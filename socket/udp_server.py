# coding=utf-8
import socket
import sys

def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('192.168.3.140', 10000)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    while True:
        print('waiting to receive message')
        data, address = sock.recvfrom(4096)

        print('received {} bytes from {}'.format(len(data), address))
        print("data: {}".format(data.decode()))


if __name__ == '__main__':
    main()
