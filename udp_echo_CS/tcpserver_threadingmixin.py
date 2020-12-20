# -*- coding:utf-8 -*-

from socketserver import TCPServer, StreamRequestHandler, ThreadingMixIn
import time

class MyThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass

class MyHandler(StreamRequestHandler):
    def handle(self):
        addr = self.request.getpeername()
        print('来自客户端：', addr)
        print('from address:', self.client_address)
        data = self.rfile.readline().strip()
        print('*' * 10)
        print(type(data))
        print(data.decode())
        # if data.decode()=='bye' or not data:
        #    break
        time.sleep(0.1)
        if data:
            self.wfile.write('服务器回复的消息'.encode('utf-8'))


if __name__ == '__main__':
    sever = MyThreadingTCPServer(('127.0.0.1', 9966), MyHandler)

    sever.serve_forever()
