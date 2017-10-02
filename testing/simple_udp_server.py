#  -*- coding: utf-8 -*-

import socket
import time

pkt1 = bytearray.fromhex("0019222200160000000033334444029f1f5afeedf00d")
pkt2 = bytearray.fromhex("001a222200160000000033334444029f18d2feedf00d")
pkt3 = bytearray.fromhex("001b222200160000000033334444029f1246feedf00d")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 12345)
    sock.bind(server_address)
    data_list = [pkt1, pkt2, pkt3]
    for i in range(5):
        in_file = open("test_pkt" + str(i + 1) + ".txt")
        in_data = in_file.read()
        data_list.append(bytearray.fromhex(in_data))
    pkt_ctr = 0
    while (True):
        sent = sock.sendto(data_list[pkt_ctr], ('localhost', 65535))
        pkt_ctr += 1
        if (pkt_ctr == len(data_list)):
            pkt_ctr = 0
        time.sleep(1)

if __name__ == "__main__":
    main()
    