#  -*- coding: utf-8 -*-

import socket
import struct
from multiprocessing import Process
from multiprocessing import Queue as pQueue
from threading import Thread
from queue import Queue as tQueue
import time
import numpy as np

#----------------------------------------------------------------------
def parse_header(packet_dict, data):
    header_format = ">HHHHH"
    head_len = struct.calcsize(header_format)
    if (len(data) < head_len):
        packet_dict["Global count"]["status"] = False
        packet_dict["Global count"]["errors"] += 1

        packet_dict["Readout count"]["status"] = False
        packet_dict["Readout count"]["errors"] += 1

        packet_dict["Type"]["status"] = False
        packet_dict["Type"]["errors"] += 1

        packet_dict["Readout length"]["status"] = False
        packet_dict["Readout length"]["errors"] += 1

        packet_dict["Reserved"]["status"] = False
        packet_dict["Reserved"]["errors"] += 1
        return 0
    unpacked_header = struct.unpack(header_format, data[0:head_len])
    packet_dict["Global count"]["value"] = unpacked_header[0]
    readout_type_str = "0x{:04X}".format(unpacked_header[1])
    packet_dict["Type"]["value"] = readout_type_str
    if (readout_type_str == "0x2222" or readout_type_str == "0x1111"):
        packet_dict["Type"]["status"] = True
    else:
        packet_dict["Type"]["status"] = False
        packet_dict["Type"]["errors"] += 1

    packet_dict["Readout length"]["value"] = unpacked_header[2]
    if (unpacked_header[2] != len(data) - 2):
        packet_dict["Readout length"]["status"] = False
        packet_dict["Readout length"]["errors"] += 1
    packet_dict["Readout count"]["value"] = unpacked_header[3]
    packet_dict["Reserved"]["value"] = unpacked_header[4]
    return head_len

#----------------------------------------------------------------------
def parse_idle(packet_dict, data, start):
    idle_format = ">II"
    idle_length = struct.calcsize(idle_format)
    if (len(data[start:]) < idle_length):
        packet_dict["Idle TS int"]["status"] = False
        packet_dict["Idle TS int"]["errors"] += 1

        packet_dict["Idle TS frac"]["status"] = False
        packet_dict["Idle TS frac"]["errors"] += 1
    unpacked_idle = struct.unpack(idle_format, data[start:start + idle_length])
    packet_dict["Idle TS frac"]["value"] = unpacked_idle[1]
    #idle_head_str = "0x{:08X}".format(unpacked_idle[0])
    packet_dict["Idle TS int"]["value"] = unpacked_idle[0]
#    if (idle_head_str != "0x33334444"):
#        packet_dict["Idle header"]["status"] = False
#        packet_dict["Idle header"]["errors"] += 1
    return start + idle_length

#----------------------------------------------------------------------
def parse_data(packet_dict, data, start):
    m_head_format = ">HHHHII"
    m_head_length = struct.calcsize(m_head_format)
    m_offset = start
    ctr = 0
    while (len(data) - m_offset > m_head_length + 4 and data[m_offset:m_offset + 2] == bytes([0xab, 0xcd])):
        packet_dict["Data modules"]["value"] += 1
        ctr += 1
        unpacked_m_head = struct.unpack(m_head_format, data[m_offset:m_offset + m_head_length])
        stats_dict = {}
        prefix = "M{}".format(ctr)
        magic_string = "0x{:04X}".format(unpacked_m_head[0])
        if (magic_string != "0xABCD"):
            packet_dict["Data modules"]["errors"] += 1
            packet_dict["Data modules"]["status"] = False
        stats_dict[prefix + " magic"] = magic_string
        stats_dict[prefix + " length"] = unpacked_m_head[1]
        stats_dict[prefix + " channel"] = unpacked_m_head[2]
        stats_dict[prefix + " fragment"] = unpacked_m_head[3]
        stats_dict[prefix + " TS int"] = unpacked_m_head[4]
        stats_dict[prefix + " TS frac"] = unpacked_m_head[5]
        samples = (unpacked_m_head[1] - 20) // 2
        if (samples <= 0):
            packet_dict["Data modules"]["errors"] += 1
            packet_dict["Data modules"]["status"] = False
            break
        stats_dict[prefix + " samples"] = samples

        data_start = m_offset + m_head_length
        data_stop = m_offset + m_head_length + samples * 2

        if (data_start >= len(data) or data_stop + 4>= len(data)):
            packet_dict["Data modules"]["errors"] += 1
            packet_dict["Data modules"]["status"] = False
            break
        sample_data = np.fromstring(data[data_start:data_stop], dtype = np.dtype(">H"))
        stats_dict["data"] = sample_data
        trailer_data = data[data_stop:data_stop + 4]
        if (len(trailer_data) != 4):
            packet_dict["Data modules"]["errors"] += 1
            packet_dict["Data modules"]["status"] = False
            break
        trailer_string = "0x{:04X}".format(struct.unpack(">I", trailer_data)[0])
        if (trailer_string != "0xBEEFCAFE"):
            packet_dict["Data modules"]["errors"] += 1
            packet_dict["Data modules"]["status"] = False
        stats_dict[prefix + " trailer"] = trailer_string
        m_offset = m_offset + m_head_length + samples * 2 + 4
        packet_dict["data"].append(stats_dict)
    return m_offset

#----------------------------------------------------------------------
def parse_filler_and_trailer(packet_dict, data, start):
    if (len(data[start:]) < 4):
        packet_dict["Trailer"]["status"] = False
        packet_dict["Trailer"]["errors"] += 1
        packet_dict["Trailer"]["value"] = ""
        return
    packet_dict["Trailer"]["value"] = "0x{:04X}".format(struct.unpack(">I", data[-4:])[0])
    if (packet_dict["Trailer"]["value"] != "0xFEEDF00D"):
        packet_dict["Trailer"]["status"] = False
        packet_dict["Trailer"]["errors"] += 1

    packet_dict["Filler ok"]["value"] = "YES"
    for i in range(start, len(data) - 4):
        if (data[i] != 85): #"U" or 0x55
            packet_dict["Filler ok"]["status"] = False
            packet_dict["Filler ok"]["errors"] += 1
            packet_dict["Filler ok"]["value"] = "0x{:02X}".format(data[i])
            break
    packet_dict["Filler size"]["value"] = len(data) - 4 - start
    if (packet_dict["Filler size"]["value"] < 0):
        packet_dict["Filler size"]["status"] = False
        packet_dict["Filler size"]["errors"] += 1

class PacketCheck():
    packet_dict = {"Nr of packets": {"value": 0, "status": True, "errors": 0},
                   "Packet length": {"value": 0, "status": True, "errors": 0},
                   "Global count": {"value": 0, "status": True, "errors": 0},
                   "Type": {"value": 0, "status": True, "errors": 0},
                   "Readout count": {"value": 0, "status": True, "errors": 0},
                   "Readout length": {"value": 0, "status": True, "errors": 0},
                   "Reserved": {"value": 0, "status": True, "errors": 0},
                   "Data modules": {"value": 0, "status": True, "errors": 0},
                   "Idle TS int": {"value": 0, "status": True, "errors": 0},
                   "Idle TS frac": {"value": 0, "status": True, "errors": 0},
                   "data": [],
                   "Filler size": {"value": "", "status": True, "errors": 0},
                   "Filler ok": {"value": "", "status": True, "errors": 0},
                   "Trailer": {"value": "", "status": True, "errors": 0}}
    nr_of_packets = 0
    def analyse(self, data):
        self.packet_dict["data"] = []
        for key in self.packet_dict:
            if (key != "data" and key != "Data modules"):
                self.packet_dict[key]["status"] = True
                self.packet_dict[key]["value"] = ""
        self.nr_of_packets += 1
        self.packet_dict["Nr of packets"]["value"] = self.nr_of_packets
        self.packet_dict["Packet length"]["value"] = len(data)
        self.packet_dict["Data modules"]["status"] = True
        byte_pos = parse_header(self.packet_dict, data)

        if (self.packet_dict["Type"]["value"] == "0x1111"):
            byte_pos = parse_data(self.packet_dict, data, byte_pos)
        elif (self.packet_dict["Type"]["value"] == "0x2222"):
            byte_pos = parse_idle(self.packet_dict, data, byte_pos)

        parse_filler_and_trailer(self.packet_dict, data, byte_pos)
        return self.packet_dict

#----------------------------------------------------------------------
def thread_function(udp_port, data_out, commands_in):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", udp_port))
    s.settimeout(0.5)
    post_packet = False
    analyser = PacketCheck()
    while (True):
        while (not commands_in.empty()):
            cmd = commands_in.get()
            if (cmd == "post_packet"):
                post_packet = True
            elif (cmd == "exit"):
                return
        try:
            packet = s.recv(16384)
        except socket.timeout:
            continue

        packet_dict = analyser.analyse(packet)

        if (post_packet):
            data_out.put(packet_dict)
            post_packet = False
    print("Exiting thread")

########################################################################
class DataAnalyser():
    #----------------------------------------------------------------------
    def __init__(self, udp_port, use_thread = False):
        if (use_thread):
            self.data_queue = tQueue()
            self.to_thread = tQueue()
            self.thread = Thread(None, target=thread_function, args=(udp_port, self.data_queue, self.to_thread))
        else:
            self.data_queue = pQueue()
            self.to_thread = pQueue()
            self.thread = Process(target=thread_function, args=(udp_port, self.data_queue, self.to_thread))
        self.thread.start()

    #----------------------------------------------------------------------
    def __del__(self):
        self.to_thread.put("exit")
        self.thread.join(timeout = 1)

    #----------------------------------------------------------------------
    def get_packet(self):
        if (self.data_queue.empty()):
            return None
        return self.data_queue.get()

    #----------------------------------------------------------------------
    def request_packet(self):
        self.to_thread.put("post_packet")

if __name__ == "__main__":
    print("Start")
    da = DataAnalyser(65535, use_thread=True)
    for i in range(5):
        time.sleep(1)
        data = da.get_packet()
        if (data == None):
            print("No data")
        else:
            print("Time stamp: " + str(data["data"]["time_stamp"]))
    print("Stopping Thread")
    del da
    print("Im done")

