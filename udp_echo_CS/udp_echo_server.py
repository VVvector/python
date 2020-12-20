#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import socket
import argparse
import signal
import time
import select

from struct import pack_into
from struct import unpack_from
from sys import argv

socketStop = False
TestRespSN = 0
TestRespReplyFailureCount = 0
UDPEchoConfig_PacketsReceived_count = 0
UDPEchoConfig_BytesReceived_count = 0
UDPEchoConfig_PacketsResponded_count = 0
UDPEchoConfig_BytesResponded_count = 0


def print_stat():
    print('UDPEchoConfig_PacketsReceived={}'.format(UDPEchoConfig_PacketsReceived_count))
    print('UDPEchoConfig_BytesReceived={}'.format(UDPEchoConfig_BytesReceived_count))
    print('UDPEchoConfig_PacketsResponded={}'.format(UDPEchoConfig_PacketsResponded_count))
    print('UDPEchoConfig_BytesResponded={}'.format(UDPEchoConfig_BytesResponded_count))


def sigint_handler(signum, frame):
    global socketStop
    socketStop = True
    print('exit signal')


def waitForMsgs(args):
    global socketStop
    global TestRespSN
    global TestRespReplyFailureCount
    global UDPEchoConfig_PacketsReceived_count
    global UDPEchoConfig_BytesReceived_count
    global UDPEchoConfig_PacketsResponded_count
    global UDPEchoConfig_BytesResponded_count

    maxSize = 2048
    minSize = 20

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.ip, args.port))

    data_buf = bytearray(maxSize + 1)

    while not socketStop:
        rlist, wlist, xlist = select.select([sock], [], [], 3)
        if [rlist, wlist, xlist] == [[], [], []]:
            # timeout
            continue;

        if sock != rlist[0]:
            # cannot reach here..
            continue;

        nbytes, client = sock.recvfrom_into(data_buf, maxSize)
        requestTime = int(round(time.time() * 1000000))

        # check "END" witch client sends
        if nbytes == 3:
            print("{} has existed".format(client))
            sock.close()
            return

        if (args.source != None):
            if (client[0] != args.source):
                TestRespReplyFailureCount += 1
                continue  # break

        if nbytes > minSize:
            if args.plus:
                rev_head = unpack_from('>IIIII', data_buf)
                TestRespSN += 1
                responseTime = int(round(time.time() * 1000000))
                pack_into('>IIIII', data_buf, 0, rev_head[0], TestRespSN, (requestTime & 0xFFFFFFFF),
                          (responseTime & 0xFFFFFFFF), TestRespReplyFailureCount)

                if (data_buf[nbytes] == 0):
                    print('recv UDP Echo message from client {}:{}'.format(client, data_buf[minSize:nbytes]))
                else:
                    print('recv UDP Echo data {} bytes from client {}'.format(nbytes, client))
            else:
                print('recv UDP Echo data {} bytes from client {}'.format(nbytes, client))
        else:
            print('recv UDP Echo from client {}'.format(client))

        sock.sendto(data_buf[:nbytes], client)

        UDPEchoConfig_PacketsReceived_count += 1
        UDPEchoConfig_BytesReceived_count += (nbytes + 8)
        UDPEchoConfig_PacketsResponded_count += 1
        UDPEchoConfig_BytesResponded_count += (nbytes + 8)

    if socketStop:
        print('server exists')
        sock.close()
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UDP Echo Plus Server')
    parser.add_argument('-v', '--version', action='version', version='v2.0')
    parser.add_argument('-i', '--ip', required=True, type=str,
                        help='UDP Echo Plus server IP')
    parser.add_argument('-p', '--port', required=True, type=int,
                        help='UDP Echo Plus server Port')
    parser.add_argument('-u', '--plus', action="store_true",
                        help='Enable UDP Echo Plus')
    parser.add_argument('-s', '--source', type=str,
                        help='UDP Echo Plus source IP')

    args = parser.parse_args(argv[1:])

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    waitForMsgs(args)
    print_stat()

