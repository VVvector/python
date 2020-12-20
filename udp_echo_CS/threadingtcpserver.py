# -*- coding:utf-8 -*-
from socketserver import *
import threading


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        while 1:
            self.data = self.request.recv(1024).strip()
            cur_thread = threading.current_thread()
            print('cur_thread.name:', cur_thread.name)

            if self.data == 'bye':
                print('client exit {}'.format(self.client_address[0]))
                break
            print('client{}:{} - {}'.format(self.client_address[0], self.client_address[1], self.data.decode()))

            self.request.sendall(self.data.upper())


if __name__ == '__main__':
    print('listening...')
    server = ThreadingTCPServer(('127.0.0.1', 9977), MyTCPHandler)
    server.serve_forever()
