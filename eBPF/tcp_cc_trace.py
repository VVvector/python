#!/usr/bin/python
#
# tcp_cc	Trace TCP IPv4 tcp_slow_start and tcp_cong_avoid_ai().
#		For Linux, uses BCC, eBPF. Embedded C.

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <net/inet_connection_sock.h>
#include <bcc/proto.h>
#include <linux/tcp.h>


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

u32 kprobe__tcp_slow_start(struct pt_regs *ctx, struct tcp_sock *tp)
{
	struct bictcp *ca = (void *)tp->inet_conn.icsk_ca_priv;
	struct sock *skp = (struct sock *)tp;

	u32 in_flight = tcp_packets_in_flight(tp);
	u32 saddr = skp->__sk_common.skc_rcv_saddr;
	u32 daddr = skp->__sk_common.skc_daddr;
	u16 dport = skp->__sk_common.skc_dport;

	bpf_trace_printk("tcp_cc ss_s %x %x %d", saddr, daddr, ntohs(dport));
	bpf_trace_printk("tcp_cc ss_1 %d %d %d", tp->snd_cwnd, tp->snd_ssthresh, tp->rcv_wnd);
	bpf_trace_printk("tcp_cc ss_e %d %d %d", in_flight, tp->snd_cwnd_cnt, ca->cnt);

	return 0;
};

void kprobe__tcp_cong_avoid_ai(struct pt_regs *ctx, struct tcp_sock *tp)
{
	struct bictcp *ca = (void *)tp->inet_conn.icsk_ca_priv;
	struct sock *skp = (struct sock *)tp;
	u32 in_flight = tcp_packets_in_flight(tp);

	u32 saddr = skp->__sk_common.skc_rcv_saddr;
	u32 daddr = skp->__sk_common.skc_daddr;
	u16 dport = skp->__sk_common.skc_dport;

	bpf_trace_printk("tcp_cc ca_s %x %x %d", saddr, daddr, ntohs(dport));
	bpf_trace_printk("tcp_cc ca_1 %d %d %d", tp->snd_cwnd, tp->snd_ssthresh, tp->rcv_wnd);
	bpf_trace_printk("tcp_cc ca_e %d %d %d", in_flight, tp->snd_cwnd_cnt, ca->cnt);
};

void kprobe__bictcp_state(struct pt_regs *ctx, struct sock *sk, u8 new_state)
{
	struct tcp_sock *tp = tcp_sk(sk);

	u32 saddr = sk->__sk_common.skc_rcv_saddr;
	u32 daddr = sk->__sk_common.skc_daddr;
	u16 dport = sk->__sk_common.skc_dport;

	bpf_trace_printk("tcp_cc sta_s %x %x %d", saddr, daddr, ntohs(dport));
	bpf_trace_printk("tcp_cc sta_1 %d %d %d", tp->snd_cwnd, tp->snd_ssthresh, tp->rcv_wnd);
	bpf_trace_printk("tcp_cc sta_e %d 0 0", new_state);
};

void kprobe__bictcp_cong_avoid(struct pt_regs *ctx, struct sock *sk, u32 ack, u32 acked)
{
	struct tcp_sock *tp = tcp_sk(sk);
	
	u32 saddr = sk->__sk_common.skc_rcv_saddr;
	u32 daddr = sk->__sk_common.skc_daddr;
	u16 dport = sk->__sk_common.skc_dport;

    u8 slow_start_sta = tp->snd_cwnd < tp->snd_ssthresh;
    u8 ss_limit = tp->snd_cwnd < 2 * tp->max_packets_out;
    u8 is_cwnd_limited = *(u8 *)((u64)&tp->tlp_high_seq - 1);
    u8 ca_sta = *(u8 *)((u64)&tp->inet_conn.icsk_retransmits - 1);


    if (ntohs(dport) == 5201) {
        bpf_trace_printk("tcp_cc bic_s %x %x %d", saddr, daddr, ntohs(dport));
        bpf_trace_printk("tcp_cc bic_1 %d %d %d", tp->snd_cwnd, tp->snd_ssthresh, slow_start_sta);
        bpf_trace_printk("tcp_cc bic_e %d %x %x", ss_limit, is_cwnd_limited, ca_sta);
	}
}
"""

# initialize BPF
b = BPF(text=bpf_text)

# header
print("tcp cc trace")
print("%-6s %-12s %20s %-16s %-16s %-15s %-15s %-15s %-15s %-15s %-15s %-15s" % (
"PID", "COMM", "function", "saddr", "daddr", "dport", "snd_cwnd",
"snd_ssthresh", "rcv_wnd", "in_flight", "snd_cwnd_cnt", "cnt"))


def inet_ntoa(addr):
    dq = b''
    for i in range(0, 4):
        dq = dq + str(addr & 0xff).encode()
        if (i != 3):
            dq = dq + b'.'
        addr = addr >> 8
    return dq


global pid, task
ss_list = []
ca_list = []
sta_list = []
bic_list = []


def show_ss(step, val_list, v1, v2, v3):
    tmp = [v1, v2, v3]

    if step == b"ss_s":
        val_list.clear()

    val_list.extend(tmp)

    if step == b"ss_e":
        printb(b"%-6d %-12.12s %20s %-16s %-16s %-15s %-15s %-15s %-15s %-15s %-15s %-15s" % (
            pid, task, b"ss", inet_ntoa(int(val_list[0], 16)),
            inet_ntoa(int(val_list[1], 16)), val_list[2], val_list[3], val_list[4], val_list[5], val_list[6],
            val_list[7],
            val_list[8]))


def show_ca(step, val_list, v1, v2, v3):
    tmp = [v1, v2, v3]

    if step == b"ca_s":
        val_list.clear()

    val_list.extend(tmp)

    if step == b"ca_e":
        printb(b"%-6d %-12.12s %20s %-16s %-16s %-15s %-15s %-15s %-15s %-15s %-15s %-15s" % (
            pid, task, b"ca", inet_ntoa(int(val_list[0], 16)),
            inet_ntoa(int(val_list[1], 16)), val_list[2], val_list[3], val_list[4], val_list[5], val_list[6], val_list[
                7],
            val_list[8]))


def show_sta(step, val_list, v1, v2, v3):
    tmp = [v1, v2, v3]

    if step == b"sta_s":
        val_list.clear()

    val_list.extend(tmp)

    if step == b"sta_e":
        printb(b"%-6d %-12.12s %20s %-16s %-16s %-15s %-15s %-15s %-15s %-15s %-15s %-15s" % (
            pid, task, b"sta", inet_ntoa(int(val_list[0], 16)),
            inet_ntoa(int(val_list[1], 16)), val_list[2], val_list[3], val_list[4], val_list[5], val_list[6],
            val_list[7], val_list[8]))


def show_bic(step, val_list, v1, v2, v3):
    tmp = [v1, v2, v3]

    if step == b"bic_s":
        val_list.clear()

    val_list.extend(tmp)

    if step == b"bic_e":
        printb(b"%-6d %-12.12s %20s %-16s %-16s %-15s %-15s %-15s %-15s %-15s %-15s %-15s" % (
            pid, task, b"bic", inet_ntoa(int(val_list[0], 16)),
            inet_ntoa(int(val_list[1], 16)), val_list[2], val_list[3], val_list[4], val_list[5], val_list[6],
            val_list[7], val_list[8]))


# filter and format output
while 1:
    # Read messages from kernel pipe
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        (_tag, function, v1, v2, v3) = msg.split(b" ")
    except ValueError:
        # Ignore messages from other tracers
        continue
    except KeyboardInterrupt:
        exit()

    # Ignore messages from other tracers
    if _tag.decode() != "tcp_cc":
        continue

    if b"ss" in function:
        show_ss(function, ss_list, v1, v2, v3)
    elif b"ca" in function:
        show_ca(function, ca_list, v1, v2, v3)
    elif b"sta" in function:
        show_sta(function, sta_list, v1, v2, v3)
    elif b"bic" in function:
        show_bic(function, sta_list, v1, v2, v3)
    else:
        print("error!")
