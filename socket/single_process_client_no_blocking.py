# coding=utf-8
from socket import *
import random


def main():
    server_ip = input("please input the server ip:")
    connect_times = input("please input the times to connect server:")
    socket_list = []

    for i in range(int(connect_times)):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((server_ip, 7788))
        socket_list.append(s)
        print(i)

    while True:
        for s in socket_list:
            s.send(bytes(random.randint(0, 100)))


if __name__ == '__main__':
    main()
