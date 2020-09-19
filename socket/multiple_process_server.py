# coding=utf-8
from socket import *
from multiprocessing import *


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

            print('create a new process to process the data {} ...'.format(address))
            client_process = Process(target=deal_with_client, args=(client_socket, address))
            client_process.start()

            # 因为已经向子进程中copy了一份（引用），并且父进程中这个套接字也没有用处了，所以关闭了。
            client_socket.close()
    finally:
        # 当为所有的客户端服务完之后再进行关闭，表示不再接收新的客户端的链接
        server_socket.close()


if __name__ == '__main__':
    main()
