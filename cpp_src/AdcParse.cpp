//
//  ADC_Readout.cpp
//  ADC_Data_Receiver
//
//  Created by Jonas Nilsson on 2017-10-17.
//  Copyright © 2017 European Spallation Source. All rights reserved.
//

#include "AdcParse.h"
#include <arpa/inet.h>
#include <netinet/in.h>

HeaderInfo parseHeader(const InData &Packet) {
  HeaderInfo ReturnInfo;
  if (Packet.Length < sizeof(PacketHeader)) {
    ReturnInfo.HeaderOk = false;
    return ReturnInfo;
  }
  const PacketHeader *HeaderRaw = reinterpret_cast<const PacketHeader*>(Packet.Data);
  PacketHeader Header(*HeaderRaw);
  Header.fixEndian();
  switch (Header.PacketType) {
    case 0x1111:
      ReturnInfo.Type = PacketType::Data;
      break;
    case 0x2222:
      ReturnInfo.Type = PacketType::Idle;
      break;
    default:
      ReturnInfo.Type = PacketType::Unknown;
      ReturnInfo.HeaderOk = false;
      break;
  }
  ReturnInfo.DataStart = sizeof(PacketHeader);
  if (Packet.Length - 2 != Header.ReadoutLength) {
    ReturnInfo.HeaderOk = false;
  }
  return ReturnInfo;
}

AdcData parseData(const InData &Packet, std::uint32_t StartByte) {
  AdcData ReturnData;
  while (StartByte + sizeof(DataHeader) < Packet.Length) {
    const DataHeader *HeaderRaw = reinterpret_cast<const DataHeader*>(Packet.Data + StartByte);
    DataHeader Header(*HeaderRaw);
    Header.fixEndian();
    if (0xABCD != Header.MagicValue) {
      break;
    }
    std::uint16_t NrOfSamples = (Header.Length - 20) * 2;
    if (StartByte + sizeof(DataHeader) + NrOfSamples * sizeof(std::uint16_t) + 4> Packet.Length) {
      ReturnData.DataOk = false;
      break;
    }
    DataModule CurrentDataModule;
    CurrentDataModule.Data.resize(NrOfSamples);
    CurrentDataModule.Channel = Header.Channel;
    CurrentDataModule.TimeStampSeconds = Header.TimeStampSeconds;
    CurrentDataModule.TimeStampSecondsFrac = Header.TimeStampSecondsFrac;
    const std::uint16_t *ElementPointer = reinterpret_cast<const std::uint16_t*>(Packet.Data + StartByte + sizeof(DataHeader));
    for (int i = 0; i < NrOfSamples; ++i) {
      CurrentDataModule.Data[i] = ntohs(ElementPointer[i]);
    }
    StartByte += sizeof(DataHeader) + NrOfSamples * sizeof(std::uint16_t);
    const std::uint32_t *TrailerPointer = reinterpret_cast<const std::uint32_t*>(Packet.Data + StartByte);
    if (ntohl(*TrailerPointer) != 0xBEEFCAFE) {
      ReturnData.DataOk = false;
      break;
    }
    StartByte += 4;
    ReturnData.Modules.emplace_back(CurrentDataModule);
  }
  ReturnData.FillerStart = StartByte;
  return ReturnData;
}

TrailerInfo parseTrailer(const InData &Packet, std::uint32_t StartByte) {
  TrailerInfo ReturnInfo;
  const std::uint8_t *FillerPointer = reinterpret_cast<const std::uint8_t*>(Packet.Data + StartByte);
  for (int i = 0; i < Packet.Length - StartByte - 4; i++) {
    if (FillerPointer[i] != 0x55) {
      ReturnInfo.TrailerOk = false;
      return ReturnInfo;
    }
    ++ReturnInfo.FillerBytes;
  }
  const std::uint32_t *TrailerPointer = reinterpret_cast<const std::uint32_t*>(Packet.Data + StartByte + ReturnInfo.FillerBytes);
  if (ntohl(*TrailerPointer) != 0xFEEDF00D) {
    ReturnInfo.TrailerOk = false;
  }
  return ReturnInfo;
}

std::vector<DataModule> parsePacket(const InData &Packet) {
  HeaderInfo Header = parseHeader(Packet);
  std::vector<DataModule> ReturnData;
  if (not Header.HeaderOk) {
    return ReturnData;
  }
  AdcData Data;
  if (PacketType::Data == Header.Type) {
    Data = parseData(Packet, Header.DataStart);
    if (not Data.DataOk) {
      return ReturnData;
    }
    TrailerInfo Trailer = parseTrailer(Packet, Data.FillerStart);
    if (not Trailer.TrailerOk) {
      return ReturnData;
    }
  }
  return Data.Modules;
}
