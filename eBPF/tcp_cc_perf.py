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
#include <net/tcp.h>

// define output data structure in C
struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
    u32 func_id;
    u32 output[11];
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

//workaround: avoid the compile error!!!
static inline u32 trace_tcp_packet_in_flight(struct tcp_sock *tp)
{
    u32 tcp_left_out = tp->sacked_out + tp->lost_out;
    u32 tcp_packets_in_flight = tp->packets_out - tcp_left_out + tp->retrans_out;

    return tcp_packets_in_flight;
}

#if 0
int kprobe__tcp_v4_rcv(struct pt_regs *ctx, struct sk_buff *skb)
{
    struct data_t data = {};
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.func_id = 0;
    data.output[0] = 0;
    data.output[1] = 0;
    data.output[2] = 0;
    data.output[3] = 0;
    data.output[4] = 0;
    data.output[5] = 0;
    data.output[6] = 0;
    data.output[7] = 0;
    data.output[8] = 0;
    data.output[9] = 0;
    data.output[10] = skb->len;

    events.perf_submit(ctx, &data, sizeof(data));
    
    return 0;
}
#endif

int kprobe__tcp_v4_do_rcv(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    struct data_t data = {};
    struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));;
    struct tcp_sock *tp = tcp_sk(sk);

    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)sk;
    u16 sport = sock->inet_sport;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;

    if (ntohs(dport) == 5201) {
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.func_id = 1;
        data.output[0] = saddr;
        data.output[1] = ntohs(sport);
        data.output[2] = daddr;
        data.output[3] = ntohs(dport);
        data.output[4] = tp->snd_cwnd;
        data.output[5] = tp->snd_ssthresh;
        data.output[6] = tp->rcv_wnd;

        data.output[7] = tcb->ack_seq;
        data.output[8] = 0;
        data.output[9] = 0;
        data.output[10] = 0;

        events.perf_submit(ctx, &data, sizeof(data));
    }
    
    return 0;
}

bool kprobe__tcp_add_backlog(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    struct data_t data = {};
    struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));;
    struct tcp_sock *tp = tcp_sk(sk);

    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)sk;
    u16 sport = sock->inet_sport;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;

    if (ntohs(dport) == 5201) {
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.func_id = 2;
        data.output[0] = saddr;
        data.output[1] = ntohs(sport);
        data.output[2] = daddr;
        data.output[3] = ntohs(dport);
        data.output[4] = tp->snd_cwnd;
        data.output[5] = tp->snd_ssthresh;
        data.output[6] = tp->rcv_wnd;

        data.output[7] = tcb->ack_seq;
        data.output[8] = 0;
        data.output[9] = 0;
        data.output[10] = 0;

        events.perf_submit(ctx, &data, sizeof(data));
    }
    
    return 1;
}

void kprobe__tcp_rcv_established(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    struct data_t data = {};
    struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));;
    struct tcp_sock *tp = tcp_sk(sk);

    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)sk;
    u16 sport = sock->inet_sport;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;

    if (ntohs(dport) == 5201) {
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.func_id = 3;
        data.output[0] = saddr;
        data.output[1] = ntohs(sport);
        data.output[2] = daddr;
        data.output[3] = ntohs(dport);
        data.output[4] = tp->snd_cwnd;
        data.output[5] = tp->snd_ssthresh;
        data.output[6] = tp->rcv_wnd;

        data.output[7] = tcb->ack_seq;
        data.output[8] = 0;
        data.output[9] = 0;
        data.output[10] = 0;

        events.perf_submit(ctx, &data, sizeof(data));
    }
}

int kprobe__tcp_ack(struct pt_regs *ctx, struct sock *sk, const struct sk_buff *skb, int flag)
{
    struct data_t data = {};
    struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));
    struct tcp_sock *tp = tcp_sk(sk);

    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)sk;
    u16 sport = sock->inet_sport;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;

    if (ntohs(dport) == 5201) {
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.func_id = 4;
        data.output[0] = saddr;
        data.output[1] = ntohs(sport);
        data.output[2] = daddr;
        data.output[3] = ntohs(dport);
        data.output[4] = tp->snd_cwnd;
        data.output[5] = tp->snd_ssthresh;
        data.output[6] = tp->rcv_wnd;

        data.output[7] = tcb->ack_seq;
        data.output[8] = flag;
        data.output[9] = 0;
        data.output[10] = 0;

        events.perf_submit(ctx, &data, sizeof(data));
    }

    return 0;
}

void kprobe_tcp_fastretrans_alert(struct pt_regs *ctx, struct sock *sk, const u32 prior_snd_una,
				  int num_dupack, int *ack_flag, int *rexmit)
{
    struct data_t data = {};
    struct inet_connection_sock *icsk = inet_csk(sk);
    struct tcp_sock *tp = tcp_sk(sk);

    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)sk;
    u16 sport = sock->inet_sport;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;
    u8 ca_state = *(u8 *)((u64)&tp->inet_conn.icsk_retransmits - 1);

    if (ntohs(dport) == 5201) {
        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.func_id = 5;
        data.output[0] = saddr;
        data.output[1] = ntohs(sport);
        data.output[2] = daddr;
        data.output[3] = ntohs(dport);
        data.output[4] = tp->snd_cwnd;
        data.output[5] = tp->snd_ssthresh;
        data.output[6] = tp->rcv_wnd;

        data.output[7] = num_dupack;
        data.output[8] = ca_state;
        data.output[9] = 0;
        data.output[10] = 0;

        events.perf_submit(ctx, &data, sizeof(data));
    }
}

u32 kprobe__tcp_slow_start(struct pt_regs *ctx, struct tcp_sock *tp, u32 acked)
{
    struct data_t data = {};
    struct bictcp *ca = (void *)tp->inet_conn.icsk_ca_priv;
    struct sock *skp = (struct sock *)tp;

    u32 in_flight = trace_tcp_packet_in_flight(tp);
    u32 saddr = skp->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)skp;
    u16 sport = sock->inet_sport;
    u32 daddr = skp->__sk_common.skc_daddr;
    u16 dport = skp->__sk_common.skc_dport;

    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.func_id = 6;
    data.output[0] = saddr;
    data.output[1] = ntohs(sport);
    data.output[2] = daddr;
    data.output[3] = ntohs(dport);
    data.output[4] = tp->snd_cwnd;
    data.output[5] = tp->snd_ssthresh;
    data.output[6] = tp->rcv_wnd;

    data.output[7] = in_flight;
    data.output[8] = tp->snd_cwnd_cnt;
    data.output[9] = acked;
    data.output[10] = 0;

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
};

void kprobe__tcp_cong_avoid_ai(struct pt_regs *ctx, struct tcp_sock *tp, u32 w, u32 acked)
{
    struct data_t data = {};
    struct bictcp *ca = (void *)tp->inet_conn.icsk_ca_priv;
    struct sock *skp = (struct sock *)tp;
    u32 in_flight = trace_tcp_packet_in_flight(tp);

    u32 saddr = skp->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)skp;
    u16 sport = sock->inet_sport;
    u32 daddr = skp->__sk_common.skc_daddr;
    u16 dport = skp->__sk_common.skc_dport;

    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.func_id = 7;
    data.output[0] = saddr;
    data.output[1] = ntohs(sport);
    data.output[2] = daddr;
    data.output[3] = ntohs(dport);
    data.output[4] = tp->snd_cwnd;
    data.output[5] = tp->snd_ssthresh;
    data.output[6] = tp->rcv_wnd;

    data.output[7] = in_flight;
    data.output[8] = tp->snd_cwnd_cnt;
    data.output[9] = ca->cnt;
    data.output[10] = acked;

    events.perf_submit(ctx, &data, sizeof(data));
};

void kprobe__bictcp_state(struct pt_regs *ctx, struct sock *sk, u8 new_state)
{
    struct data_t data = {};
    struct tcp_sock *tp = tcp_sk(sk);

    u32 saddr = sk->__sk_common.skc_rcv_saddr;
    struct inet_sock *sock = (struct inet_sock *)sk;
    u16 sport = sock->inet_sport;
    u32 daddr = sk->__sk_common.skc_daddr;
    u16 dport = sk->__sk_common.skc_dport;

    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.func_id = 8;
    data.output[0] = saddr;
    data.output[1] = ntohs(sport);
    data.output[2] = daddr;
    data.output[3] = ntohs(dport);
    data.output[4] = tp->snd_cwnd;
    data.output[5] = tp->snd_ssthresh;
    data.output[6] = tp->rcv_wnd;

    data.output[7] = new_state;
    data.output[8] = 0;
    data.output[9] = 0;
    data.output[10] = 0;	

    events.perf_submit(ctx, &data, sizeof(data));
};

void kprobe__bictcp_cong_avoid(struct pt_regs *ctx, struct sock *sk, u32 ack, u32 acked)
{
    struct data_t data = {};
    struct tcp_sock *tp = tcp_sk(sk);

    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct inet_sock *sock = (struct inet_sock *)sk;
        u16 sport = sock->inet_sport;
        u32 saddr = sk->__sk_common.skc_rcv_saddr;
        u32 daddr = sk->__sk_common.skc_daddr;

        u8 in_slow_start = tp->snd_cwnd < tp->snd_ssthresh;
        u8 ss_cwnd_limit = tp->snd_cwnd < 2 * tp->max_packets_out;
        u8 is_cwnd_limited = *(u8 *)((u64)&tp->tlp_high_seq - 1);
        u8 ca_state = *(u8 *)((u64)&tp->inet_conn.icsk_retransmits - 1);

        data.pid = bpf_get_current_pid_tgid();
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        data.func_id = 9;
        data.output[0] = saddr;
        data.output[1] = ntohs(sport);
        data.output[2] = daddr;
        data.output[3] = ntohs(dport);
        data.output[4] = tp->snd_cwnd;
        data.output[5] = tp->snd_ssthresh;
        data.output[6] = tp->rcv_wnd;

        data.output[7] = ca_state;
        data.output[8] = in_slow_start;
        data.output[9] = ss_cwnd_limit;
        data.output[10] = is_cwnd_limited;

        events.perf_submit(ctx, &data, sizeof(data));
    }
}
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

    stats_content = "{:<16} {:<16} {:<6} f{:<2} - {:<16}:{:<6} -> {:<16}:{:<6} - {:<8} {:<12} {:<8} {:<12} {:<8} {:<8} {:<8}".format(
        time_s, event.comm.decode(), event.pid,
        event.func_id,
        inet_ntoa(event.output[0]), event.output[1], inet_ntoa(event.output[2]), event.output[3],
        event.output[4], event.output[5], event.output[6], event.output[7],
        event.output[8], event.output[9], event.output[10])

    #print(stats_content)
    save_ebpf_stats("{}\n".format(stats_content))


def ebpf_perf_buffer_show():
    global ebpf_info
    print("tcp cc trace")
    print("{:<16} {:<16} {:<6} {:<2} - {:<16}:{:<6} -> {:<16}:{:<6} - {:<8} {:<12} {:<8} {:<12} {:<8} {:<8} {:<8}".format(
        "time_s", "comm", "pid",
        "func",
        "v0", "v1", "v2","v3", "v4", "v5",
        "v6", "v7", "v8", "v9", "v10"))

    try:
        ebpf_info.stats_file_handle = open(ebpf_info.stats_file, "w", encoding='UTF-8')
        ebpf_info.b["events"].open_perf_buffer(evt_poll_perf_data, page_cnt=1024)
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
