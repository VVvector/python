# coding=utf-8

from socket import *
from threading import Thread


def deal_with_client(client_socket, address):
    while True:
        recv_data = client_socket.recv(1024)
        if len(recv_data) > 0:
            print('recv {}:{}'.format(address, recv_data))
        else:
            print('{} client closed.'.format(address))
            break
    client_socket.close()


def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    localAddr = ('', 7788)
    server_socket.bind(localAddr)
    server_socket.listen(5)

    try:
        while True:
            # accept connections from outside
            print('main process: wait for client connect...')
            (client_socket, address) = server_socket.accept()

            print('create a new thread to process the data {} ...'.format(address))
            client_thread = Thread(target=deal_with_client, args=(client_socket, address))
            client_thread.start()

            # 因为线程中共享这个套接字，如果关闭了会导致这个套接字不可用，
            # 但是此时在线程中这个套接字可能还在收数据，因此不能关闭
            # client_thread.close()
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
