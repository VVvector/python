# coding=utf-8
from socket import *

# 用来存储所有的新链接的socket
g_socket_list = []


def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    localAddr = ('', 7788)
    server_socket.bind(localAddr)

    # 可以适当修改listen中的值来看看不同的现象
    server_socket.listen(1000)

    # 将套接字设置为非堵塞
    # 设置为非堵塞后，如果accept时，恰巧没有客户端connect，那么accept会
    # 产生一个异常，所以需要try来进行处理
    server_socket.setblocking(False)

    while True:
        try:
            client_info = server_socket.accept()
        except Exception as result:
            pass
        else:
            print("new client: {}".format(client_info))
            client_info[0].setblocking(False)
            g_socket_list.append(client_info)

        # 用来存储需要删除的客户端信息
        need_delete_client_info_list = []

        for client_socket, client_address in g_socket_list:
            try:
                recv_data = client_socket.recv(1024)
                if len(recv_data) > 0:
                    print('recv {}: {}'.format(client_address, recv_data))
                else:
                    print('{} client closed'.format(client_address))
                    client_socket.close()
                    need_delete_client_info_list.append((client_socket, client_address))
            except Exception as result:
                pass

        # delete the closed client
        for client in need_delete_client_info_list:
            g_socket_list.remove(client)


if __name__ == '__main__':
    main()
