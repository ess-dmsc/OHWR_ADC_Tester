//
//  ADC_Readout.hpp
//  ADC_Data_Receiver
//
//  Created by Jonas Nilsson on 2017-10-17.
//  Copyright © 2017 European Spallation Source. All rights reserved.
//

#pragma once

#include <vector>
#include <netinet/in.h>
#include <cstdint>
#include "AdcBufferElements.h"

struct DataModule {
  std::uint32_t TimeStampSeconds;
  std::uint32_t TimeStampSecondsFrac;
  std::uint16_t Channel;
  std::vector<std::uint16_t> Data;
};

struct AdcData {
  bool DataOk = true;
  std::vector<DataModule> Modules;
  std::int32_t FillerStart = 0;
};

enum class PacketType {Idle, Data, Unknown};

struct HeaderInfo {
  bool HeaderOk = true;
  PacketType Type = PacketType::Unknown;
  std::int32_t DataStart = 0;
};

struct TrailerInfo {
  bool TrailerOk = true;
  std::uint32_t FillerBytes = 0;
};

#pragma pack(push, 2)
struct PacketHeader {
  std::uint16_t PacketType;
  std::uint16_t ReadoutLength;
  std::uint16_t RedoutCount;
  std::uint16_t Reserved;
  std::uint32_t Seconds;
  std::uint32_t SecondsFrac;
  void fixEndian() {
    PacketType = ntohs(PacketType);
    ReadoutLength = ntohs(ReadoutLength);
    RedoutCount = ntohs(RedoutCount);
    Seconds = ntohl(Seconds);
    SecondsFrac = ntohl(SecondsFrac);
  }
};

struct DataHeader {
  std::uint16_t MagicValue;
  std::uint16_t Length;
  std::uint16_t Channel;
  std::uint16_t Fragment;
  std::uint32_t TimeStampSeconds;
  std::uint32_t TimeStampSecondsFrac;
  void fixEndian() {
    MagicValue = ntohs(MagicValue);
    Length = ntohs(Length);
    Channel = ntohs(Channel);
    Fragment = ntohs(Fragment);
    TimeStampSeconds = ntohl(TimeStampSeconds);
    TimeStampSecondsFrac = ntohl(TimeStampSecondsFrac);
  }
};

struct IdleHeader {
  std::uint32_t TimeStampSeconds;
  std::uint32_t TimeStampSecondsFrac;
  void fixEndian() {
    TimeStampSeconds = ntohl(TimeStampSeconds);
    TimeStampSecondsFrac = ntohl(TimeStampSecondsFrac);
  }
};
#pragma pack(pop)

std::vector<DataModule> parsePacket(const InData &Packet);
AdcData parseData(const InData &Packet, std::uint32_t StartByte);
HeaderInfo parseHeader(const InData &Packet);
TrailerInfo parseTrailer(const InData &Packet, std::uint32_t StartByte);

