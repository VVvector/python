#!/usr/bin/python
#
# tcp_cc	Trace TCP IPv4 tcp_slow_start and tcp_cong_avoid_ai().
#		For Linux, uses BCC, eBPF. Embedded C.

from __future__ import print_function
from bcc import BPF
import time
import os

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <net/inet_connection_sock.h>
#include <bcc/proto.h>
#include <linux/tcp.h>

// define output data structure in C
struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
    u32 function;
    u32 output[9];
};
BPF_PERF_OUTPUT(events);

/* BIC TCP Parameters */
struct bictcp {
    u32	cnt;		/* increase cwnd by 1 after ACKs */
    u32	last_max_cwnd;	/* last maximum snd_cwnd */
    u32	last_cwnd;	/* the last snd_cwnd */
    u32	last_time;	/* time when updated last_cwnd */
    u32	epoch_start;	/* beginning of an epoch */

#define ACK_RATIO_SHIFT	4
    u32	delayed_ack;	/* estimate the ratio of Packets/ACKs << 4 */
};


static inline unsigned int tcp_left_out(const struct tcp_sock *tp)
{
    return tp->sacked_out + tp->lost_out;
}

static inline unsigned int tcp_packets_in_flight(const struct tcp_sock *tp)
{
    return tp->packets_out - tcp_left_out(tp) + tp->retrans_out;
}

int kprobe__tcp_ack(struct pt_regs *ctx, struct sock *sk, const struct sk_buff *skb, int flag)
{
    struct data_t data = {};
    struct tcp_sock *tp = tcp_sk(sk);
    
    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;

    if (ntohs(dport) == 5201) {
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.function = 1;
        data.output[0] = saddr;
        data.output[1] = daddr;
        data.output[2] = ntohs(dport);
        data.output[3] = tp->snd_cwnd;
        data.output[4] = tp->snd_ssthresh;
        data.output[5] = tp->rcv_wnd;
        data.output[6] = flag;
        data.output[7] = 0;
        data.output[8] = 0;	
    
        events.perf_submit(ctx, &data, sizeof(data));
    }
    
    return 0;
}

u32 kprobe__tcp_slow_start(struct pt_regs *ctx, struct tcp_sock *tp)
{
    struct data_t data = {};
    struct bictcp *ca = (void *)tp->inet_conn.icsk_ca_priv;
    struct sock *skp = (struct sock *)tp;
    
    u32 in_flight = tcp_packets_in_flight(tp);
    u32 saddr = skp->__sk_common.skc_rcv_saddr;
    u32 daddr = skp->__sk_common.skc_daddr;
    u16 dport = skp->__sk_common.skc_dport;
    
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.function = 2;
    data.output[0] = saddr;
    data.output[1] = daddr;
    data.output[2] = ntohs(dport);
    data.output[3] = tp->snd_cwnd;
    data.output[4] = tp->snd_ssthresh;
    data.output[5] = tp->rcv_wnd;
    data.output[6] = in_flight;
    data.output[7] = tp->snd_cwnd_cnt;
    data.output[8] = ca->cnt;	
    
    events.perf_submit(ctx, &data, sizeof(data));
    
    return 0;
};

void kprobe__tcp_cong_avoid_ai(struct pt_regs *ctx, struct tcp_sock *tp)
{
    struct data_t data = {};
    struct bictcp *ca = (void *)tp->inet_conn.icsk_ca_priv;
    struct sock *skp = (struct sock *)tp;
    u32 in_flight = tcp_packets_in_flight(tp);
    
    u32 saddr = skp->__sk_common.skc_rcv_saddr;
    u32 daddr = skp->__sk_common.skc_daddr;
    u16 dport = skp->__sk_common.skc_dport;
    
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.function = 3;
    data.output[0] = saddr;
    data.output[1] = daddr;
    data.output[2] = ntohs(dport);
    data.output[3] = tp->snd_cwnd;
    data.output[4] = tp->snd_ssthresh;
    data.output[5] = tp->rcv_wnd;
    data.output[6] = in_flight;
    data.output[7] = tp->snd_cwnd_cnt;
    data.output[8] = ca->cnt;	
    
    events.perf_submit(ctx, &data, sizeof(data));
};

#if 0
void kprobe__bictcp_state(struct pt_regs *ctx, struct sock *sk, u8 new_state)
{
    struct data_t data = {};
    struct tcp_sock *tp = tcp_sk(sk);
    
    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;
    
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.function = 4;
    data.output[0] = saddr;
    data.output[1] = daddr;
    data.output[2] = ntohs(dport);
    data.output[3] = tp->snd_cwnd;
    data.output[4] = tp->snd_ssthresh;
    data.output[5] = tp->rcv_wnd;
    data.output[6] = new_state;
    data.output[7] = 0;
    data.output[8] = 0;	
    
    events.perf_submit(ctx, &data, sizeof(data));
};

void kprobe__bictcp_cong_avoid(struct pt_regs *ctx, struct sock *sk, u32 ack, u32 acked)
{
    struct data_t data = {};
    struct tcp_sock *tp = tcp_sk(sk);
    
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        u32 saddr = sk->__sk_common.skc_rcv_saddr;
        u32 daddr = sk->__sk_common.skc_daddr;
    
        u8 in_slow_start = tp->snd_cwnd < tp->snd_ssthresh;
        u8 ss_cwnd_limit = tp->snd_cwnd < 2 * tp->max_packets_out;
        u8 is_cwnd_limited = *(u8 *)((u64)&tp->tlp_high_seq - 1);
        u8 ca_state = *(u8 *)((u64)&tp->inet_conn.icsk_retransmits - 1);
    
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.function = 5;
        data.output[0] = saddr;
        data.output[1] = daddr;
        data.output[2] = ntohs(dport);
        
        data.output[3] = tp->snd_cwnd;
        data.output[4] = tp->snd_ssthresh;
        data.output[5] = ca_state;
        
        data.output[6] = in_slow_start;
        data.output[7] = ss_cwnd_limit;
        data.output[8] = is_cwnd_limited;
    
        events.perf_submit(ctx, &data, sizeof(data));
    }
}
#endif
"""


class EBPFInfo:
    b_text = None
    b = None
    start = 0
    stats_file = None
    stats_file_handle = None
    check_times = 0


ebpf_info = EBPFInfo()
ebpf_info.b_text = bpf_text


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
def evt_poll_perf_data(cpu, data, size):
    global ebpf_info

    event = ebpf_info.b["events"].event(data)
    if ebpf_info.start == 0:
        ebpf_info.start = event.ts
    time_s = (float(event.ts - ebpf_info.start)) / 1000000000

    stats_content = "{:<16} {:<16} {:<6} f{:<2} - {:<16} -> {:<16}:{:<6} - {:<8} {:<12} {:<8} {:<8} {:<8} {:<8}".format(
        time_s, event.comm.decode(), event.pid,
        event.function,
        inet_ntoa(event.output[0]), inet_ntoa(event.output[1]), event.output[2],
        event.output[3], event.output[4], event.output[5],
        event.output[6], event.output[7], event.output[8])

    print(stats_content)
    save_ebpf_stats("{}\n".format(stats_content))


def ebpf_perf_buffer_show():
    global ebpf_info
    print("tcp cc trace")
    print("{:<16} {:<16} {:<6} {:<2} - {:<16} -> {:<16}:{:<6} - {:<8} {:<12} {:<8} {:<8} {:<8} {:<8}".format(
        "time_s", "comm", "pid",
        "func",
        "v1", "v2", "v3",
        "v4", "v5", "v6", "v7", "v8", "v9"))

    try:
        ebpf_info.stats_file_handle = open(ebpf_info.stats_file, "w", encoding='UTF-8')
        ebpf_info.b["events"].open_perf_buffer(evt_poll_perf_data)
        while 1:
            ebpf_info.b.perf_buffer_poll()
    except:
        ebpf_info.stats_file_handle.close()


def main():
    global ebpf_info
    # initialize BPF
    b = BPF(text=ebpf_info.b_text)
    ebpf_info.b = b

    # init ebpf stats file
    dir = os.path.abspath(os.path.dirname(__file__))
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    dir_name = "{}_{}".format("bcc_tcp_cc_stats", timestamp)
    dir = os.path.join(dir, dir_name)
    os.mkdir(dir)

    ebpf_info.stats_file = os.path.join(dir, "bcc_tcp_cc.info")
    print(ebpf_info.stats_file)
    ebpf_perf_buffer_show()


if __name__ == '__main__':
    main()
