#!/usr/bin/env python3

from raw_packet.Utils.base import Base
from raw_packet.Utils.network import RawIPv4, RawUDP, RawEthernet
from argparse import ArgumentParser
from random import randint
from getmac import get_mac_address
from time import sleep
from socket import socket, AF_PACKET, SOCK_RAW

Base = Base()
Base.check_platform()
Base.check_user()

current_network_interface = None

src_mac_address = None
src_ip_address = None
src_port = None

dst_mac_address = None
dst_ip_address = None
dst_port = None

data = None


def sender():
    SOCK = socket(AF_PACKET, SOCK_RAW)
    SOCK.bind((current_network_interface, 0))

    ip = RawIPv4()
    udp = RawUDP()
    eth = RawEthernet()

    payload = bytes(data, encoding="utf8")
    payload_len = len(data)
    udp_header = udp.make_header_with_ipv4_checksum(src_ip_address, dst_ip_address, src_port,
                                                    dst_port, payload_len, payload)
    ip_header = ip.make_header(src_ip_address, dst_ip_address, payload_len, len(udp_header), 17)
    eth_header = eth.make_header(src_mac_address, dst_mac_address, 2048)
    udp_packet = eth_header + ip_header + udp_header + payload

    i = 0
    while True:
        SOCK.send(udp_packet)
        sleep(1)
        i = i + 1
        print("send {} packet!".format(i))

    SOCK.close()


if __name__ == "__main__":
    parser = ArgumentParser(description='TCP packets sender')
    parser.add_argument('-i', '--interface', type=str, help='Set interface name for send TCP packets')
    parser.add_argument('-m', '--src_mac', type=str, help='Set src mac address (not required)', default=None)
    parser.add_argument('-a', '--src_ip', type=str, help='Set src ip address (not required)', default=None)
    parser.add_argument('-p', '--src_port', type=int, help='Set src port (not required)', default=None)
    parser.add_argument('-M', '--target_mac', type=str, help='Set dst mac address (not required)', default=None)
    parser.add_argument('-A', '--target_ip', type=str, required=True, help='Set target IP address')
    parser.add_argument('-P', '--target_port', type=int, required=True, help='Set target port')
    parser.add_argument('-d', '--data', type=str, help='Set TCP payload data (default="GET / HTTP/1.1\\r\\n\\r\\n")',
                        default="GET / HTTP/1.0\r\n\r\n")

    args = parser.parse_args()

    if args.interface is None:
        current_network_interface = Base.network_interface_selection()
    else:
        current_network_interface = args.interface

    if args.src_mac is None:
        src_mac_address = Base.get_interface_mac_address(current_network_interface)
    else:
        src_mac_address = args.src_mac

    if args.src_ip is None:
        src_ip_address = Base.get_interface_ip_address(current_network_interface)
    else:
        src_ip_address = args.src_ip

    if args.src_port is None:
        src_port = randint(1024, 65535)
    else:
        src_port = args.src_port

    dst_ip_address = args.target_ip

    if args.target_mac is None:
        dst_mac_address = get_mac_address(current_network_interface, dst_ip_address)

    dst_port = args.target_port

    data = args.data

    print(Base.c_info + "Interface: " + current_network_interface)
    print(Base.c_info + "Src MAC:   " + src_mac_address)
    print(Base.c_info + "Src IP:    " + src_ip_address)
    print(Base.c_info + "Src PORT:  " + str(src_port))
    print(Base.c_info + "Dst MAC:   " + dst_mac_address)
    print(Base.c_info + "Dst IP:    " + dst_ip_address)
    print(Base.c_info + "Dst PORT:  " + str(dst_port))

    sender()
