#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import socket
import argparse
import signal
import time

from struct import pack_into
from struct import unpack_from
from sys import argv

socketStop = False
TestGenSN = 0
TestRespSN = 0
TestRespReplyFailureCount = 0
UDPEchoConfig_PacketsSend_count = 0
UDPEchoConfig_BytesSend_count = 0
UDPEchoConfig_PacketsResponse_count = 0
UDPEchoConfig_BytesResponse_count = 0
SucessfulEchoCnt = 0

RoundTripPacketLoss = 0
SentPacketLoss = 0
ReceivePacketLoss = 0


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of str


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of bytes


def print_stat(isplus):
    if isplus:
        print('RoundTripPacketLoss={}'.format(RoundTripPacketLoss))
        print('SentPacketLoss={}'.format(SentPacketLoss))
        print('ReceivePacketLoss={}'.format(ReceivePacketLoss))


def sigint_handler(signum, frame):
    global socketStop
    socketStop = True
    print('exit signal')


def sendEchoReq(args):
    global TestGenSN
    global TestRespSN
    global RoundTripPacketLoss
    global SentPacketLoss
    global ReceivePacketLoss
    global SucessfulEchoCnt
    global TestRespReplyFailureCount

    maxSize = 2048
    minSize = 20

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('connect to server:{} {}'.format(args.ip, args.port))

    data_buf = bytearray(maxSize + 1)
    sock.settimeout(3)
    t = 0

    data_len = len(args.data)

    if not args.plus:
        print('Send Echo Request {} to {}({}) bytes of data.'.format(args.data, data_len, data_len))
    else:
        print('Send Echo Request {} to {}({}) bytes of data.'.format(args.data, data_len, data_len + 20))

    while t < args.times:
        t += 1
        TestGenSN += 1

        if socketStop:
            print('exists')
            sock.close()
            return

        if not args.plus:
            # print 'send msg: ',data
            sendTime = time.time() * 1000
            sock.sendto(args.data, (args.ip, args.port))
            try:
                nbytes, serv = sock.recvfrom_into(data_buf, maxSize)
                recvTime = time.time() * 1000
                print('Reply from {}: bytes={} time={}ms'.format(serv, nbytes, recvTime - sendTime))
            except Exception as err:
                print('No reply from {}: bytes={}'.format(serv, nbytes))

        else:
            # UDP Echo plus
            # pack the data - big-endian
            pack_into('>I', data_buf, 0, TestGenSN)
            send_data = to_bytes(args.data)
            str_fmt = '>{}s'.format(data_len)
            pack_into(str_fmt, data_buf, 20, send_data)
            send_data_len = data_len + 20
            sendTime = time.time() * 1000
            sock.sendto(data_buf[:send_data_len], (args.ip, args.port))
            try:
                nbytes, serv = sock.recvfrom_into(data_buf, maxSize)
                recvTime = time.time() * 1000

                if nbytes == send_data_len:
                    RevSN, TestRespSN, RecvTimeStamp, ReplyTimeStamp, TestRespReplyFailureCount = unpack_from('>IIIII',
                                                                                                              data_buf)
                    # check sequence
                    if RevSN != TestGenSN:
                        print('No reply from {}: seq={}'.format(args.ip, TestGenSN))
                    else:
                        SucessfulEchoCnt += 1
                        EffectiveRTD = int(recvTime * 1000) - int(sendTime * 1000) - (ReplyTimeStamp - RecvTimeStamp)
                        print('Reply from {}: seq={} bytes={} rtd={}us'.format(serv, RevSN, nbytes, EffectiveRTD))
                else:
                    print(
                        'Reply from {}: seq={} bytes={} time={}ms'.format(serv, TestGenSN, nbytes, recvTime - sendTime))
            except Exception as err:
                print('No Reply from {}: seq={}. {}'.format(args.ip, TestGenSN, err))

            pass

        time.sleep(1)

    if args.plus:
        RoundTripPacketLoss = TestGenSN - SucessfulEchoCnt
        SentPacketLoss = TestGenSN - (TestRespSN - TestRespReplyFailureCount)
        ReceivePacketLoss = RoundTripPacketLoss - SentPacketLoss

    sock.sendto(to_bytes('END'), (args.ip, args.port))
    sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UDP Echo Plus Client')
    parser.add_argument('-v', '--version', action='version', version='v1.0')
    parser.add_argument('-i', '--ip', required=True, type=str,
                        help='UDP Echo Plus server IP')
    parser.add_argument('-p', '--port', required=True, type=int,
                        help='UDP Echo Plus server Port')
    parser.add_argument('-u', '--plus', action="store_true",
                        help='Enable UDP Echo Plus')
    parser.add_argument('-d', '--data', default='Hello,world!', type=str,
                        help='package data')
    parser.add_argument('-t', '--times', default=4, type=int,
                        help='times of echo request')

    args = parser.parse_args(argv[1:])

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    sendEchoReq(args)
    print_stat(args.plus)
