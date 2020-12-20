# -*- coding:utf-8 -*-

from socketserver import *
import time


class MyForkingTCPServer(TCPServer, ForkingMixIn):
    pass


class MyHandler(StreamRequestHandler):
    def handle(self):
        addr = self.request.getpeername()
        print('connect from :', addr)
        try:
            data = self.rfile.readline().strip()  ##客户端传的数据必须加上'\r\n'结尾
            print('data:', data)
            time.sleep(0.1)
        except:
            print('jie shou bao cuo le..')
        if data:
            self.wfile.write('this is a server message'.encode('utf-8'))


if __name__ == '__main__':
    server = MyForkingTCPServer(('127.0.0.1', 9900), MyHandler)  # 连接是接收一次，关闭一次，每次传数据都要重新建立连接
    print('server object:', server)
    server.serve_forever()
