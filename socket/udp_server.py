# coding=utf-8
import socket
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description='UDP packets receiver')
    parser.add_argument('-A', '--target_ip', type=str, required=True, help='Set target IP address')
    parser.add_argument('-P', '--target_port', type=int, required=True, help='Set target port')
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (args.target_ip, args.target_port)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    while True:
        print('waiting to receive message')
        data, address = sock.recvfrom(4096)

        print('received {} bytes from {}'.format(len(data), address))
        print("data: {}".format(data.decode()))


if __name__ == '__main__':
    main()
