# -*- coding:utf-8 -*-

from socketserver import TCPServer, StreamRequestHandler as srh
import traceback


class MyHandler(srh):
    def handle(self):
        print('client address:', self.client_address)
        try:
            print('sever recv begin...')
            dd = self.rfile.readline()  # 客户端发送一定加入\r\n结尾，否则会卡死
            print('received data is:', dd)

            self.wfile.write('server send message!!'.encode())

        except:
            traceback.print_exc()
            print('baocuo ru shang')


server = TCPServer(('127.0.0.1', 21567), MyHandler)  # 每次发送请求后自动关闭连接，不能长连接
server.serve_forever()
