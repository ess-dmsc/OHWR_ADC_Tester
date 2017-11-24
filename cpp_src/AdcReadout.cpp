//
//  ADC_Readout.cpp
//  ADC_Data_Receiver
//
//  Created by Jonas Nilsson on 2017-10-17.
//  Copyright © 2017 European Spallation Source. All rights reserved.
//

#include <iostream>
#include "AdcReadout.h"
#include "AdcParse.h"
#include "Socket.h"

AdcReadout::AdcReadout(std::uint16_t port, std::int32_t ConcatenateSamples) : Detector(), toProcessingQueue(100), port(port), MaxSamplesInBuffer(ConcatenateSamples) {
  for (int i = 0; i < 4; i++) {
    InternalSampleBuffer.TimeStamps[i] = {0, 0};
    FinishedSampleBuffer.TimeStamps[i] = {0, 0};
    InternalSampleBuffer.Samples[i].resize(ConcatenateSamples, 0);
    FinishedSampleBuffer.Samples[i].resize(ConcatenateSamples, 0);
  }
  std::function<void()> inputFunc = [this](){AdcReadout::inputThread();};
  Detector::AddThreadFunction(inputFunc, "input");

  std::function<void()> processingFunc = [this](){AdcReadout::processingThread();};
  Detector::AddThreadFunction(processingFunc, "processing");
  
}

void AdcReadout::inputThread() {
  Socket::Endpoint local("0.0.0.0", port);
  UDPServer mbdata(local);
  mbdata.buflen(9000);
  mbdata.setbuffers(0, 2000000);
  mbdata.printbuffers();
  mbdata.settimeout(0, 100000); // One tenth of a second
  ElementPtr DataElement;
  bool outCome;
  
  while (Detector::runThreads) {
    if (nullptr == DataElement) {
      outCome = toProcessingQueue.waitGetEmpty(DataElement, 500);
      if (not outCome) {
        continue;
      }
    }
    DataElement->Length = mbdata.receive(static_cast<void*>(DataElement->Data), DataElement->MaxLength); //Fix cast
    if (DataElement->Length > 0) {
      toProcessingQueue.tryPutData(std::move(DataElement));
    }
  }
}

void AdcReadout::processingThread() {
  ElementPtr DataElement;
  bool GotElement = false;
  std::array<int, 4> SamplesInBuffer;
  for (auto &NrOf : SamplesInBuffer) {
    NrOf = 0;
  }
  while (Detector::runThreads) {
    GotElement = toProcessingQueue.waitGetData(DataElement, 1000);
    if (GotElement) {
      std::vector<DataModule> ChannelData = parsePacket(*DataElement);
      for (auto &DataModule : ChannelData) {
        auto &CurrentChannelNr = DataModule.Channel;
        auto &CurrentNrOfSamples = SamplesInBuffer[CurrentChannelNr];
        auto &CurrentTimeStamp = InternalSampleBuffer.TimeStamps[CurrentChannelNr];
        if (0 == CurrentTimeStamp.Seconds and 0 == CurrentTimeStamp.SecondsFraction) {
          CurrentTimeStamp.Seconds = DataModule.TimeStampSeconds;
          CurrentTimeStamp.SecondsFraction = DataModule.TimeStampSecondsFrac;
        }
        auto &SamplesVector = InternalSampleBuffer.Samples[CurrentChannelNr];
        bool UpdateFinishedBuffer = false;
        int NrOfSamplesToCopy = DataModule.Data.size();
        if (MaxSamplesInBuffer - CurrentNrOfSamples < NrOfSamplesToCopy) {
          UpdateFinishedBuffer = true;
          NrOfSamplesToCopy = MaxSamplesInBuffer - CurrentNrOfSamples;
        }
        std::copy(DataModule.Data.begin(), DataModule.Data.begin() + NrOfSamplesToCopy, SamplesVector.begin() + CurrentNrOfSamples);
        CurrentNrOfSamples += NrOfSamplesToCopy;
        if (UpdateFinishedBuffer) {
          CurrentNrOfSamples = 0;
          {
            std::lock_guard<std::mutex> Guard(BufferMutex);
          FinishedSampleBuffer.TimeStamps[CurrentChannelNr] = CurrentTimeStamp;
            FinishedSampleBuffer.Samples[CurrentChannelNr] = SamplesVector;
          }
          CurrentTimeStamp.SecondsFraction = 0;
          CurrentTimeStamp.Seconds = 0;
        }
      }
      while (not toProcessingQueue.tryPutEmpty(std::move(DataElement)) and Detector::runThreads) {
        //Do nothing
      }
    }
  }
}

SampleData AdcReadout::getSamples() {
  std::lock_guard<std::mutex> Guard(BufferMutex);
  return FinishedSampleBuffer;
}
