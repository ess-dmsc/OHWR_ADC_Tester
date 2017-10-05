#  -*- coding: utf-8 -*-

import socket
import time
import random
import copy

pkt1 = bytearray.fromhex("0019222200160000000033334444029f1f5afeedf00d")
pkt2 = bytearray.fromhex("001a222200160000000033334444029f18d2feedf00d")
pkt3 = bytearray.fromhex("001b222200160000000033334444029f1246feedf00d")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_list = []
    for i in range(2):
        in_file = open("test2_pkt" + str(i + 1) + ".txt")
        in_data = in_file.read()
        data_list.append(bytearray.fromhex(in_data))
    pkt_ctr = 0
    while (True):
        used_data = copy.deepcopy(data_list[pkt_ctr])
        # if (random.random() > 0.9):
        #     used_data[-1] = 0
        sent = sock.sendto(used_data, ('localhost', 65535))
        pkt_ctr += 1
        if (pkt_ctr == len(data_list)):
            pkt_ctr = 0
        time.sleep(1)

if __name__ == "__main__":
    main()
    