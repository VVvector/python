#!/usr/bin/python
from __future__ import print_function
from bcc import BPF
import time
import os
import sys
import argparse


class EBPFInfo:
    bpf_text = None
    bpf_file = None
    bpf = None
    start = 0
    stats_file = None
    stats_file_handle = None
    check_times = 0

    def load_bpf_file(self, source_file):
        self.bpf_file = source_file
        self.bpf = BPF(src_file=self.bpf_file)

    def load_bpf_txt(self, source_text):
        self.bpf_text = source_text
        self.bpf = BPF(text=self.bpf_text)

ebpf_info = EBPFInfo()


def inet_ntoa(addr):
    dq = ''
    for i in range(0, 4):
        dq = dq + str(addr & 0xff)
        if (i != 3):
            dq = dq + '.'
        addr = addr >> 8
    return dq


def save_ebpf_stats(stats_content):
    global ebpf_info
    ebpf_info.stats_file_handle.writelines(stats_content)

    if ebpf_info.check_times > 10000:
        ebpf_info.check_times = 0
        # 100M bytes
        if os.path.getsize(ebpf_info.stats_file) > 100000000:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            rename = "{}.{}".format(os.path.basename(ebpf_info.stats_file), timestamp)
            rename_file = os.path.join(os.path.dirname(ebpf_info.stats_file), rename)
            ebpf_info.stats_file_handle.close()
            os.rename(ebpf_info.stats_file, rename_file)
            ebpf_info.stats_file_handle = open(ebpf_info.stats_file, "w", encoding='UTF-8')


# process event
def ring_buffer_poll(ctx, data, size):
    global ebpf_info

    event = ebpf_info.bpf["buffer"].event(data)

    if ebpf_info.start == 0:
        ebpf_info.start = event.ts
    time_s = (float(event.ts - ebpf_info.start)) / 1000000000

    stats_content = "{:<16} {:<4} {:<16} {:<6} f{:<2} - {:<16}:{:<6} -> {:<16}:{:<6} - {:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}".format(
        time_s, event.cpu, event.comm.decode('utf-8'), event.pid,
        event.func_id,
        inet_ntoa(event.data[0]), event.data[1], inet_ntoa(event.data[2]), event.data[3],
        event.data[4], event.data[5], event.data[6], event.data[7],
        event.data[8], event.data[9], event.data[10])

    # print(stats_content)
    save_ebpf_stats("{}\n".format(stats_content))


def ebpf_ring_buffer_show():
    global ebpf_info
    print("ebpf tracing start...")
    print("== ctrl-c to exit ==")
    header = "{:<16} {:<4} {:<16} {:<6} f{:<2} - {:<16}:{:<6} -> {:<16}:{:<6} - {:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}".format(
            "time/s", "cpu", "comm", "pid",
            "id",
            "v0", "v1", "v2", "v3", "v4", "v5",
            "v6", "v7", "v8", "v9", "v10")
    print(header)


    try:
        ebpf_info.stats_file_handle = open(ebpf_info.stats_file, "w", encoding='UTF-8')
        ebpf_info.stats_file_handle.writelines("{}\n".format(header))

        ebpf_info.bpf["buffer"].open_ring_buffer(ring_buffer_poll)
        while 1:
            ebpf_info.bpf.ring_buffer_poll()
            # or ebpf_info.b.ring_buffer_consume()
            time.sleep(0.1)
    except:
        ebpf_info.stats_file_handle.close()
        sys.exit()


def main():
    parser = argparse.ArgumentParser(description="This is a ebpf ring program")
    parser.add_argument('-f', '--file', required=True, help='tracing C file name')
    args = parser.parse_args()
    print(args)

    global ebpf_info
    ebpf_info.load_bpf_file(args.file)

    # init ebpf stats file
    dir = os.path.abspath(os.path.dirname(__file__))
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    dir_name = "{}-{}".format("bcc_tracing", timestamp)
    dir = os.path.join(dir, dir_name)
    os.mkdir(dir)

    ebpf_info.stats_file = os.path.join(dir, "bcc_tracing.log")
    print(ebpf_info.stats_file)
    ebpf_ring_buffer_show()


if __name__ == '__main__':
    main()
