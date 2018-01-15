//
//  ADC_Readout.hpp
//  ADC_Data_Receiver
//
//  Created by Jonas Nilsson on 2017-10-17.
//  Copyright © 2017 European Spallation Source. All rights reserved.
//

#pragma once

#include <mutex>
#include <array>
#include <cstdint>
#include "Detector.h"
#include "CircularBuffer.h"
#include "AdcBufferElements.h"

struct TimeStamp {
  std::uint32_t Seconds;
  std::uint32_t SecondsFraction;
};

struct SampleData {
  std::array<TimeStamp, 4> TimeStamps;
  std::array<std::vector<std::uint16_t>, 4> Samples;
};

class AdcReadout : public Detector {
public:
  AdcReadout(std::uint16_t port, std::int32_t ConcatenateSamples = 0);
  AdcReadout(const AdcReadout&) = delete;
  AdcReadout(const AdcReadout&&) = delete;
  ~AdcReadout() = default;
  virtual void inputThread();
  virtual void processingThread();
  SampleData getSamples();
protected:
  using ElementPtr = SpscBuffer::ElementPtr<InData>;
  using Queue = SpscBuffer::CircularBuffer<InData>;
  Queue toProcessingQueue;
  std::uint16_t port;
  std::mutex BufferMutex;
  int MaxSamplesInBuffer;
  SampleData InternalSampleBuffer;;
  SampleData FinishedSampleBuffer;
};

//class ADC_Readout_Factory : public DetectorFactory {
//public:
//  std::shared_ptr<Detector> create(void *args) {
//    return std::shared_ptr<Detector>(new ADC_Readout(args));
//  }
//};

