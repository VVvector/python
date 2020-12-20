# -*- coding:utf-8 -*-
import socketserver
import sys


def udp_echo_process(server, data, client):
    print("process: {}, {}, {}".format(server, data, client))


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        udp_echo_process(self.request[1], self.request[0], self.client_address)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def main():
    HOST, PORT = "192.168.3.122", 30000
    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
