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
        packet_dict["Global counter"]["status"] = False
        packet_dict["Global counter"]["errors"] += 1

        packet_dict["Readout counter"]["status"] = False
        packet_dict["Readout counter"]["errors"] += 1

        packet_dict["Readout type"]["status"] = False
        packet_dict["Readout type"]["errors"] += 1

        packet_dict["Readout length"]["status"] = False
        packet_dict["Readout length"]["errors"] += 1

        packet_dict["Readout reserved"]["status"] = False
        packet_dict["Readout reserved"]["errors"] += 1
        return 0
    unpacked_header = struct.unpack(header_format, data[0:head_len])
    packet_dict["Global counter"]["value"] = unpacked_header[0]
    readout_type_str = "0x{:04X}".format(unpacked_header[1])
    packet_dict["Readout type"]["value"] = readout_type_str
    if (readout_type_str == "0x2222" or readout_type_str == "0x1111"):
        packet_dict["Readout type"]["status"] = True
    else:
        packet_dict["Readout type"]["status"] = False
        packet_dict["Readout type"]["errors"] += 1

    packet_dict["Readout length"]["value"] = unpacked_header[2]
    packet_dict["Readout counter"]["value"] = unpacked_header[3]
    packet_dict["Readout reserved"]["value"] = unpacked_header[4]
    return head_len

#----------------------------------------------------------------------
def parse_idle(packet_dict, data, start):
    idle_format = ">II"
    idle_length = struct.calcsize(idle_format)
    if (len(data[start:]) < idle_length):
        packet_dict["Idle header"]["status"] = False
        packet_dict["Idle header"]["errors"] += 1

        packet_dict["Idle timestamp"]["status"] = False
        packet_dict["Idle timestamp"]["errors"] += 1
    unpacked_idle = struct.unpack(idle_format, data[start:start + idle_length])
    packet_dict["Idle timestamp"]["value"] = unpacked_idle[1]
    idle_head_str = "0x{:08X}".format(unpacked_idle[0])
    packet_dict["Idle header"]["value"] = idle_head_str
    if (idle_head_str != "0x33334444"):
        packet_dict["Idle header"]["status"] = False
        packet_dict["Idle header"]["errors"] += 1
    return start + idle_length

#----------------------------------------------------------------------
def parse_data(packet_dict, data, start):
    m_head_format = ">HHHHI"
    m_head_length = struct.calcsize(m_head_format)
    m_offset = start
    ctr = 0
    while (len(data) - m_offset > m_head_length + 4 and data[m_offset:m_offset + 2] == bytes([0xab, 0xcd])):
        ctr += 1
        unpacked_m_head = struct.unpack(m_head_format, data[m_offset:m_offset + m_head_length])
        stats_dict = {}
        prefix = "M{}".format(ctr)
        stats_dict[prefix + " timestamp"] = unpacked_m_head[4]
        samples = (unpacked_m_head[1] - 3) * 2
        stats_dict[prefix + " samples"] = samples
        stats_dict[prefix + " channel"] = unpacked_m_head[2]

        sample_data = np.fromstring(data[m_offset + m_head_length:m_offset + m_head_length + samples * 2], dtype = np.dtype(">H"))
        stats_dict["data"] = sample_data
        stats_dict[prefix + " trailer"] = "0x{:04X}".format(struct.unpack(">I", data[m_offset + m_head_length + samples * 2:m_offset + m_head_length + samples * 2+4])[0])
        m_offset = m_offset + m_head_length + samples * 2 + 4
        packet_dict["data"].append(stats_dict)
    return m_offset

#----------------------------------------------------------------------
def parse_filler_and_trailer(packet_dict, data, start):
    if (len(data[start:]) < 4):
        packet_dict["0xFEEDF00D"]["status"] = False
        packet_dict["0xFEEDF00D"]["errors"] += 1
        packet_dict["0xFEEDF00D"]["value"] = ""
        return
    packet_dict["0xFEEDF00D"]["value"] = "0x{:04X}".format(struct.unpack(">I", data[-4:])[0])
    if (packet_dict["0xFEEDF00D"]["value"] != "0xFEEDF00D"):
        packet_dict["0xFEEDF00D"]["status"] = False
        packet_dict["0xFEEDF00D"]["errors"] += 1

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

#----------------------------------------------------------------------
def thread_function(udp_port, data_out, commands_in):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", udp_port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_NO_CHECK)
    s.settimeout(0.5)
    post_packet = False
    packet_dict = {"Nr of packets": {"value": 0, "status": True, "errors": 0},
                   "Packet length": {"value": 0, "status": True, "errors": 0},
                   "Global counter": {"value": 0, "status": True, "errors": 0},
                   "Readout type": {"value": 0, "status": True, "errors": 0},
                   "Readout counter": {"value": 0, "status": True, "errors": 0},
                   "Readout length": {"value": 0, "status": True, "errors": 0},
                   "Readout reserved": {"value": 0, "status": True, "errors": 0},
                   "Idle header": {"value": 0, "status": True, "errors": 0},
                   "Idle timestamp": {"value": 0, "status": True, "errors": 0},
                   "data": [],
                   "Filler size": {"value": "", "status": True, "errors": 0},
                   "Filler ok": {"value": "", "status": True, "errors": 0},
                   "0xFEEDF00D": {"value": "", "status": True, "errors": 0}}

    nr_of_packets = 0
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

        packet_dict["data"] = []
        for key in packet_dict:
            if (key != "data"):
                packet_dict[key]["status"] = True
                packet_dict[key]["value"] = ""
        nr_of_packets += 1
        packet_dict["Nr of packets"]["value"] = nr_of_packets
        packet_dict["Packet length"]["value"] = len(packet)
        byte_pos = parse_header(packet_dict, packet)

        if (packet_dict["Readout type"]["value"] == "0x1111"):
            byte_pos = parse_data(packet_dict, packet, byte_pos)
        elif (packet_dict["Readout type"]["value"] == "0x2222"):
            byte_pos = parse_idle(packet_dict, packet, byte_pos)

        parse_filler_and_trailer(packet_dict, packet, byte_pos)

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

