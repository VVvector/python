#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <net/inet_connection_sock.h>
#include <bcc/proto.h>
#include <linux/tcp.h>
#include <net/tcp.h>

struct event_t {
    u32 cpu;
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];

    u32 func_id;
    u32 data[11];
};

/* Creates a ringbuf called events with 64 pages of space, shared across all CPUs */
BPF_RINGBUF_OUTPUT(buffer, 64);

static inline void trace_update_common_info(struct event_t *event)
{
    event->cpu = bpf_get_smp_processor_id();
    event->pid = bpf_get_current_pid_tgid();
    event->ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
}

static inline void trace_update_ip_info(struct sock *sk, struct event_t *event)
{
    struct inet_sock *sock = (struct inet_sock *)sk;
	u16 sport = sock->inet_sport;
    u16 dport = sk->__sk_common.skc_dport;

    bpf_probe_read_kernel(&event->data[0], sizeof(event->data[0]), &sk->__sk_common.skc_rcv_saddr);
	event->data[1] = ntohs(sport);
	bpf_probe_read_kernel(&event->data[2], sizeof(event->data[2]), &sk->__sk_common.skc_daddr);
	event->data[3] = ntohs(dport);
}


static inline u32 trace_tcp_packet_in_flight(struct tcp_sock *tp)
{
    u32 tcp_left_out = tp->sacked_out + tp->lost_out;
    u32 tcp_packets_in_flight = tp->packets_out - tcp_left_out + tp->retrans_out;
    return tcp_packets_in_flight;
}

#if 0
int kprobe__tcp_v4_rcv(struct pt_regs *ctx, struct sk_buff *skb)
{
    struct event_t event = {};

    trace_update_common_info(&event);
    event.func_id = 0;
    event.data[0] = 0;
    event.data[1] = 0;
    event.data[2] = 0;
    event.data[3] = 0;
    event.data[4] = 0;
    event.data[5] = 0;
    event.data[6] = 0;
    event.data[7] = 0;
    event.data[8] = 0;
    event.data[9] = 0;
    event.data[10] = skb->len;

    buffer.ringbuf_output(&event, sizeof(event), 0);

    return 0;
}
#endif

int kprobe__tcp_v4_do_rcv(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));
        struct tcp_sock *tp = tcp_sk(sk);
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);

        event.func_id = 1;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->rcv_wnd;
        event.data[7] = tcb->ack_seq;
        event.data[8] = 0;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
    return 0;
}
bool kprobe__tcp_add_backlog(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));
        struct tcp_sock *tp = tcp_sk(sk);
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);

        event.func_id = 2;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->rcv_wnd;
        event.data[7] = tcb->ack_seq;
        event.data[8] = 0;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
    return 1;
}
void kprobe__tcp_rcv_established(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));
        struct tcp_sock *tp = tcp_sk(sk);
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);

        event.func_id = 3;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->rcv_wnd;
        event.data[7] = tcb->ack_seq;
        event.data[8] = 0;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
}
int kprobe__tcp_ack(struct pt_regs *ctx, struct sock *sk, const struct sk_buff *skb, int flag)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        struct tcp_skb_cb *tcb = ((struct tcp_skb_cb *)&((skb)->cb[0]));
        struct tcp_sock *tp = tcp_sk(sk);
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);

        event.func_id = 4;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->rcv_wnd;
        event.data[7] = tcb->ack_seq;
        event.data[8] = flag;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
    return 0;
}
void kprobe_tcp_fastretrans_alert(struct pt_regs *ctx, struct sock *sk, const u32 prior_snd_una,
				  int num_dupack, int *ack_flag, int *rexmit)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        struct tcp_sock *tp = tcp_sk(sk);
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);

        event.func_id = 5;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->rcv_wnd;
        event.data[7] = num_dupack;
        /* ca state */
        event.data[8] = *(u8 *)((u64)&tp->inet_conn.icsk_retransmits - 1);
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
}
u32 kprobe__tcp_slow_start(struct pt_regs *ctx, struct tcp_sock *tp, u32 acked)
{
    struct event_t event = {};
    trace_update_common_info(&event);
    struct sock *sk = (struct sock *)tp;
    trace_update_ip_info(sk, &event);

    event.func_id = 6;
    event.data[4] = tp->snd_cwnd;
    event.data[5] = tp->snd_ssthresh;
    event.data[6] = tp->rcv_wnd;
    event.data[7] = trace_tcp_packet_in_flight(tp);
    event.data[8] = tp->snd_cwnd_cnt;
    event.data[9] = acked;
    event.data[10] = 0;

    buffer.ringbuf_output(&event, sizeof(event), 0);
    return 0;
};
void kprobe__tcp_cong_avoid_ai(struct pt_regs *ctx, struct tcp_sock *tp, u32 w, u32 acked)
{
    struct event_t event = {};
    trace_update_common_info(&event);
    struct sock *sk = (struct sock *)tp;
    trace_update_ip_info(sk, &event);

    event.func_id = 7;
    event.data[4] = tp->snd_cwnd;
    event.data[5] = tp->snd_ssthresh;
    event.data[6] = tp->rcv_wnd;
    event.data[7] = trace_tcp_packet_in_flight(tp);
    event.data[8] = tp->snd_cwnd_cnt;
    event.data[9] = w;
    event.data[10] = acked;

    buffer.ringbuf_output(&event, sizeof(event), 0);
};

/************************************* BIC ***********************************************/
void kprobe__bictcp_state(struct pt_regs *ctx, struct sock *sk, u8 new_state)
{
	u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
		struct event_t event = {};
		trace_update_common_info(&event);
		trace_update_ip_info(sk, &event);
		struct tcp_sock *tp = tcp_sk(sk);

		event.func_id = 8;
		event.data[4] = tp->snd_cwnd;
		event.data[5] = tp->snd_ssthresh;
		event.data[6] = tp->rcv_wnd;
		event.data[7] = new_state;
		event.data[8] = 0;
		event.data[9] = 0;
		event.data[10] = 0;

		buffer.ringbuf_output(&event, sizeof(event), 0);
	}
};
void kprobe__bictcp_cong_avoid(struct pt_regs *ctx, struct sock *sk, u32 ack, u32 acked)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);
        struct tcp_sock *tp = tcp_sk(sk);

        event.func_id = 9;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->rcv_wnd;
        /* ca state */
        event.data[7] = *(u8 *)((u64)&tp->inet_conn.icsk_retransmits - 1);
        /* in slow start state */
        event.data[8] = tp->snd_cwnd < tp->snd_ssthresh;
        /* ss cwnd limit */
        event.data[9] = tp->snd_cwnd < 2 * tp->max_packets_out;
        /* is cwnd limited */
        event.data[10] =*(u8 *)((u64)&tp->tlp_high_seq - 1);

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
}
/************************************* CUBIC ***********************************************/
/************************************* TCP XMIT ***********************************************/
bool kprobe__tcp_write_xmit(struct pt_regs *ctx, struct sock *sk, unsigned int mss_now, int nonagle,
			   int push_one, gfp_t gfp)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);
        struct tcp_sock *tp = tcp_sk(sk);

        event.func_id = 10;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->packets_out;
        event.data[7] = tp->max_packets_out;
        event.data[8] = sk->sk_pacing_rate;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
    return 0;
}
void kprobe__tcp_event_new_data_sent(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);
        struct tcp_sock *tp = tcp_sk(sk);

        event.func_id = 11;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->packets_out;
        event.data[7] = tp->max_packets_out;
        event.data[8] = sk->sk_pacing_rate;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
}

void kprobe__tcp_update_pacing_rate(struct pt_regs *ctx, struct sock *sk)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);
        struct tcp_sock *tp = tcp_sk(sk);

        event.func_id = 12;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->packets_out;
        event.data[7] = tp->max_packets_out;
        event.data[8] = sk->sk_pacing_rate;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
}

void kprobe__tcp_tsq_handler(struct pt_regs *ctx, struct sock *sk)
{
    u16 dport = sk->__sk_common.skc_dport;
    if (ntohs(dport) == 5201) {
        struct event_t event = {};
        trace_update_common_info(&event);
        trace_update_ip_info(sk, &event);
        struct tcp_sock *tp = tcp_sk(sk);

        event.func_id = 10;
        event.data[4] = tp->snd_cwnd;
        event.data[5] = tp->snd_ssthresh;
        event.data[6] = tp->packets_out;
        event.data[7] = tp->max_packets_out;
        event.data[8] = sk->sk_pacing_rate;
        event.data[9] = 0;
        event.data[10] = 0;

        buffer.ringbuf_output(&event, sizeof(event), 0);
    }
}