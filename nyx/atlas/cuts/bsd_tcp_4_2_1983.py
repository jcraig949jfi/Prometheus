"""Cut: bsd-tcp-4.2-1983 (ancestry-aware, Stage A COARSE; SOURCE_READ on M3; second of the 2026-09-17 NOT_CUT order).
Read in full: tcp_timer.c (197 lines), tcp_timer.h (99), tcp_output.c (332), tcp_var.h (80). Read in part: tcp_input.c
480-700 (ACK processing, RTT update, window update, delayed ACK) plus the grep of every srtt/wnd line. Not read: tcp_input.c
1-479 and 700-933 (state machine, reassembly, options), tcp_subr.c, tcp_usrreq.c, tcp_debug.c. Nothing ran (SOURCE_ONLY).

The record's entry point is comparative: the same files at BSD-4_3_Tahoe carry cwnd/ssthresh; here they do not. The cut
records the ABSENCE as anatomy (what regulates the send rate in this body) rather than as a missing organ.
"""
from nyx.atlas.author import Cut

T = "vault:bsd-tcp-4.2-1983/upstream/tcp_timer.c"
TH = "vault:bsd-tcp-4.2-1983/upstream/tcp_timer.h"
O = "vault:bsd-tcp-4.2-1983/upstream/tcp_output.c"
I = "vault:bsd-tcp-4.2-1983/upstream/tcp_input.c"
c = Cut("bsd-tcp-4.2-1983", mode="ANCESTRY_AWARE",
        inspected=["tcp_timer.c, tcp_timer.h, tcp_output.c, tcp_var.h (all)", "tcp_input.c 480-700 (ACK / RTT / window / delayed-ack) and grep of srtt/wnd lines"],
        evidence=[("SOURCE_READ", T), ("SOURCE_READ", TH), ("SOURCE_READ", O), ("SOURCE_READ", I + ":480-700"), ("SOURCE_READ", "vault:bsd-tcp-4.2-1983/upstream/tcp_var.h")],
        note="the send rate in this body is bounded by exactly two things: the peer's advertised window and the retransmit timer. There is no state that reads loss as a signal about the network; "
             "loss only lengthens the timer. Every mechanism below is a timer, a smoother, or a threshold on the window")

srtt = c.organ("exponentially_smoothed_rtt_from_one_timed_segment_at_a_time", human_name="t_rtt / t_rtseq / t_srtt (tcp_input.c 485-492; tcp_output.c timing)", status="ACCEPTED",
    mechanism="at most one segment is timed at a time: when a new segment is sent and nothing is being timed, t_rtt=1 and t_rtseq = its first sequence number; the slow timer increments t_rtt every 500 ms; "
              "when an ACK covers t_rtseq the sample t_rtt is folded in as srtt = alpha*srtt + (1-alpha)*rtt with alpha=0.9 (first sample sets srtt directly); the sample is in 500 ms ticks",
    input="ACK sequence numbers; the 500 ms tick", output="t_srtt (float)", state="t_rtt, t_rtseq, t_srtt", update="one sample per round trip at most",
    assumptions=["a retransmitted segment is never timed (the timer is started only on new data; but a sample taken across a retransmission is NOT excluded here: t_rtt keeps counting through a REXMT and the ACK for the retransmitted data still satisfies SEQ_GT(ack, t_rtseq)) -- the Karn problem is present by reading",
                 "500 ms resolution; the first sample is trusted fully"],
    fitness_value_in_ancestor="the only measurement the sender makes of the network; it sets every timer", failure_landscape="by reading: no variance term, so a bursty path produces spurious timeouts at beta=2; ambiguous samples after retransmission bias srtt low; no measurement",
    human_prior="alpha=0.9, beta=2.0 (tcp_timer.h: 'conservative')", evidence_ref=I + ":485-492; " + O + ":263-268; " + TH + ":74-90", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="the three t_rtt fields and the two sites that read them",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "DELAYED_CLOSED_LOOP", "memory": "SUMMARY_STATISTIC",
              "stochasticity": "ENVIRONMENT_RANDOM", "hidden_state": "ESTIMATES", "uncertainty": "POINT", "temporal_horizon": "WINDOW"})

rto = c.organ("retransmit_timer_as_beta_times_srtt_with_tabulated_backoff_and_a_ten_strike_drop", human_name="TCPT_REXMT handling (tcp_timer.c 121-148; tcp_output.c 270-278)", status="ACCEPTED",
    mechanism="on sending with no timer running: REXMT = clamp(beta*srtt, 1 s, 30 s), shift=0; on expiry: shift++, if shift > 10 drop the connection (ETIMEDOUT); else REXMT = clamp(srtt * backoff[shift-1]) with backoff = {1.0,1.2,1.4,1.7,2.0,3.0,5.0,8.0,16.0,32.0} "
              "(or srtt << shift when the tcpexprexmtbackoff switch is on -- a compiled-in alternative, off by default); then snd_nxt = snd_una and ONE segment is (re)sent ('this only transmits one segment!'); an ACK that advances snd_una resets shift to 0 and the timer to beta*srtt",
    input="srtt, shift, the ACK stream", output="a retransmission of the oldest unacked segment; the next timeout; or a dropped connection", state="t_timer[REXMT], t_rxtshift", update="on send, on ACK, on expiry",
    assumptions=["a timeout means the segment was lost, not that the network is full (the record's failure: this is where 4.3 Tahoe reads congestion)", "the backoff table is gentle at first (1.0, 1.2, 1.4) -- the first three retransmissions come at nearly the same interval"],
    fitness_value_in_ancestor="reliability: nothing unacknowledged is ever abandoned short of ten timeouts", failure_landscape="the record's: under shared-link congestion every host's timer fires, every host resends into the queue, throughput collapses three orders of magnitude; the gentle table makes it worse than pure doubling",
    human_prior="the ten-entry table vs the exponential switch: two policies, one compiled in, one chosen at runtime by a global; the table is the default", evidence_ref=T + ":106-148; " + O + ":270-278; " + I + ":494-501", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="case TCPT_REXMT and the two timer-set sites",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "DELAYED_CLOSED_LOOP", "memory": "LAST_VALUE",
              "stochasticity": "ENVIRONMENT_RANDOM", "update_topology": "EVENT_DRIVEN", "failure_mode": "COLLAPSES", "recovery": "RETRIES", "resource_dependence": "BANDWIDTH", "competition": "CONTENDS"})

win = c.organ("send_amount_bounded_by_peer_advertised_window_only", human_name="tcp_output.c 51-57: len = MIN(sb_cc, snd_wnd + t_force) - off", status="ACCEPTED",
    mechanism="the amount eligible to send is whatever is in the socket buffer up to the peer's advertised window (snd_wnd, updated from segments that pass the wl1/wl2 freshness test, tcp_input.c 578-586), minus what is already in flight; "
              "capped per segment at t_maxseg (negotiated at SYN as min(rcv_hiwat/2, 1024)); 'sendalot' loops until the window or buffer is exhausted. No sender-side variable other than snd_wnd limits in-flight data",
    input="sb_cc, snd_wnd, snd_nxt, snd_una, t_maxseg", output="len for this segment; whether to loop", state="snd_wnd, snd_wl1, snd_wl2", update="per output call; snd_wnd per fresh window advertisement",
    assumptions=["the receiver's buffer is the only scarce resource worth modelling; the path between the hosts is not modelled at all"],
    fitness_value_in_ancestor="flow control: the receiver is never overrun", failure_landscape="a full window is dumped into the network at once at connection start and after every timeout (no slow start); with many senders on one link the shared queue overflows -- the 1986 collapse",
    human_prior="RFC 793 window semantics implemented literally; the absence of a network model is the era's prior", evidence_ref=O + ":48-58, 318-320; " + I + ":576-586", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="the len computation and the step6 window update",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC",
              "resource_dependence": "BANDWIDTH", "hidden_state": "IGNORES", "competition": "CONTENDS"})

swa = c.organ("sender_silly_window_avoidance_by_three_thresholds", human_name="tcp_output.c 70-80", status="ACCEPTED",
    mechanism="with data available but no SYN/RST/FIN/URG, send only if: the segment is a full t_maxseg, or it empties the send buffer, or 4*len >= snd_wnd (at least a quarter of the window), or t_force; otherwise wait for more data or a bigger window",
    input="len, snd_wnd, sb_cc, t_maxseg, t_force", output="send / defer", state="none", update="per output call",
    assumptions=["small segments are the waste to avoid (header overhead), not queue occupancy"], fitness_value_in_ancestor="prevents the sender half of the silly-window syndrome (Clark 1982)",
    failure_landscape="UNKNOWN by run", evidence_ref=O + ":70-80", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the if (len) block",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

rwa = c.organ("receiver_window_advertisement_with_quarter_buffer_floor_and_35_percent_update_trigger", human_name="tcp_output.c 91-96, 215-219, 302-304", status="ACCEPTED",
    mechanism="the advertised window is the free receive-buffer space, but advertised as 0 if below a quarter of the buffer (receiver silly window avoidance); a segment is sent solely to update the window when the newly available space is >= 35% of the buffer; rcv_adv remembers the largest edge advertised",
    input="sbspace(so_rcv), sb_hiwat, rcv_adv, rcv_nxt", output="ti_win; a window-update send decision", state="rcv_adv", update="per output call",
    assumptions=["window updates are unreliable (no ACK for an ACK), so the peer's persist timer covers the loss (the comment block at tcp_output.c 99-116)"], fitness_value_in_ancestor="the receiver half of SWS avoidance; fewer window-update segments",
    failure_landscape="UNKNOWN by run", evidence_ref=O + ":91-96, 215-219, 302-304", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the three sites naming rcv_adv / sb_hiwat",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC"})

pers = c.organ("persist_timer_probing_a_zero_window_with_a_forced_byte_and_its_own_backoff", human_name="tcp_setpersist / TCPT_PERSIST (tcp_output.c 118-125, 322-332; tcp_timer.c 149-156)", status="ACCEPTED",
    mechanism="when the peer's window is zero, data is queued, and no retransmit is pending: start PERSIST = clamp((beta*srtt) << shift, 5 s, 30 s), shift++ (wrapping at 10); on expiry force one byte out (t_force=1: the byte is allowed past the window) and re-arm; a nonzero window update clears the timer",
    input="snd_wnd == 0, sb_cc, the two timers", output="a one-byte probe segment; the next probe time", state="t_timer[PERSIST], t_rxtshift (shared with REXMT)", update="on window close, on expiry, on window open",
    assumptions=["the peer will answer a byte outside its window with a fresh window; the two timers are mutually exclusive (panic if both set: tcp_setpersist)"],
    fitness_value_in_ancestor="deadlock avoidance: a lost window update cannot freeze the connection", failure_landscape="by reading: t_rxtshift is shared between persist and retransmit backoff, so a persist episode's shift leaks into the next retransmit interval unless reset (it is reset at 119 on entering persist, and by an advancing ACK)",
    evidence_ref=O + ":118-125, 322-332; " + T + ":149-156", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="tcp_setpersist and case TCPT_PERSIST",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "DELAYED_CLOSED_LOOP", "stochasticity": "DETERMINISTIC",
              "update_topology": "EVENT_DRIVEN", "failure_mode": "STALLS", "recovery": "RETRIES"})

keep = c.organ("keepalive_by_a_deliberately_out_of_window_segment_with_an_idle_drop", human_name="TCPT_KEEP (tcp_timer.c 158-181)", status="ACCEPTED",
    mechanism="every 45 s of idleness (if SO_KEEPALIVE): send <SEQ=snd_una-1, ACK=rcv_nxt-1> -- both numbers lie so that the peer must respond -- and drop the connection after 8*45 s idle; a connection not yet established is dropped at the first expiry",
    input="t_idle (incremented per 500 ms tick, reset on receipt)", output="a probe or a drop", state="t_idle, t_timer[KEEP]", update="per expiry",
    assumptions=["the protocol spec obliges a response to an out-of-window segment"], fitness_value_in_ancestor="dead-peer detection with no protocol extension", failure_landscape="UNKNOWN by run",
    evidence_ref=T + ":158-185", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="case TCPT_KEEP",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "failure_mode": "STALLS"})

dack = c.organ("delayed_acknowledgement_via_a_200ms_fast_timer_flag", human_name="TF_DELACK / tcp_fasttimo (tcp_timer.c 26-44; tcp_input.c 640-646)", status="ACCEPTED",
    mechanism="receipt of data sets TF_DELACK (unless the global tcpnodelack forces TF_ACKNOW); the fast timer (200 ms) converts every pending DELACK into ACKNOW and calls tcp_output; any output in between clears both flags, so an ACK rides on the next data segment for free",
    input="incoming data segments; the 200 ms tick", output="an ACK-only segment or a piggybacked ACK", state="the two flag bits", update="per segment and per fast tick",
    assumptions=["a reply or more data usually arrives within 200 ms"], fitness_value_in_ancestor="halves ACK traffic on request/response traffic", failure_landscape="UNKNOWN by run; the tick is not per-connection, so the delay is 0-200 ms uniformly",
    evidence_ref=T + ":26-44; " + I + ":640-646; " + O + ":313", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="tcp_fasttimo and the two flag sites",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "temporal_horizon": "WINDOW"})

tick = c.organ("countdown_timer_array_swept_by_a_global_500ms_tick", human_name="tcp_slowtimo / t_timer[4] / TCPT_RANGESET", status="ACCEPTED",
    mechanism="four short counters per connection (REXMT, PERSIST, KEEP, 2MSL); a global 500 ms routine walks every control block, decrements every nonzero counter and dispatches the expiry to tcp_timers via the user-request switch; all timer values are clamped by TCPT_RANGESET to [min,max] in ticks; the same sweep ages t_idle and t_rtt and advances the initial sequence number",
    input="the clock", output="expiry events", state="4 shorts per connection", update="every 500 ms",
    assumptions=["500 ms resolution suffices for every timer including RTT measurement"], fitness_value_in_ancestor="one mechanism, one data structure for every time-based behaviour", failure_landscape="by reading: RTT quantised to 500 ms makes srtt for LAN paths equal to 1-2 ticks, so REXMT sits at its 1 s floor",
    evidence_ref=T + ":48-93; " + TH + ":1-12, 93-99", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="tcp_slowtimo, tcp_canceltimers, the macro",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "temporal_horizon": "STEP"})

c.reject("mbuf assembly, checksum, header template copy, option encoding (tcp_output.c 130-230)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="packet construction; no decision", note="kernel plumbing of the era")
c.reject("the connection state machine (tcp_fsm.h; tcp_input.c switch statements) and reassembly (tcp_reass)", reason="OTHER", evidence="not read this pass (tcp_input.c 1-479, 700-933); residue", note="likely GENERIC protocol mechanics, but not read so not rejected on the merits")
c.reject("'congestion control' as an absent organ", reason="OTHER", evidence="nothing in this body reads loss as a network signal; the absence is recorded on the window organ and the retransmit organ, not invented as a slot", note="the 4.3 Tahoe fossil is where the organ appears; a recurrence test across the two bodies is the natural Stage E item")
c.reject("urgent-pointer handling and out-of-band data (tcp_input.c 588-628)", reason="BELOW_MEANINGFUL_GRAIN", evidence="protocol bookkeeping with a self-described kludge; no mechanism worth an organ")

c.edge(tick, rto, "triggers"); c.edge(tick, pers, "triggers"); c.edge(tick, keep, "triggers"); c.edge(tick, srtt, "updates", note="t_rtt++ per tick"); c.edge(srtt, rto, "feeds"); c.edge(srtt, pers, "feeds")
c.edge(rto, win, "restores", note="snd_nxt = snd_una: the window is re-sent from its left edge"); c.edge(win, swa, "gates"); c.edge(rwa, win, "feeds", note="the peer's rwa is this side's snd_wnd"); c.edge(win, pers, "triggers", note="snd_wnd == 0")
c.edge(pers, rwa, "predicts", note="a probe elicits an advertisement"); c.edge(dack, rwa, "schedules"); c.edge(rto, pers, "suppresses", note="mutually exclusive timers"); c.edge(rto, srtt, "suppresses", note="no: a retransmission does NOT stop the RTT clock (read); recorded as the Karn ambiguity")

c.pressure("many_senders_share_one_bottleneck_whose_only_signal_is_loss_and_delay",
    condition="N organisms push data through one queue of bounded size; the queue drops when full; each organism sees only its own acknowledgements and their timing; goodput is rewarded, retransmissions are not",
    resource_or_constraint="bottleneck capacity C shared by N; queue length Q; per-organism feedback delayed by one round trip", failure_condition="aggregate offered load stays above C after drops begin (collapse: goodput -> 0 while the link stays busy with duplicates)",
    world_punishes="sending a full window after every timeout; treating a drop as an isolated loss", world_rewards="an organism that reduces its offered load when its own losses rise and probes upward when they stop",
    observable_consequence="aggregate goodput / C as N grows; retransmissions per delivered segment; fairness across the N", vacuity_condition="N = 1 or C >= sum of the windows (no shared queue)",
    trivial_shortcuts="a world that tells the organism C/N directly; fixed-rate senders tuned to C/N offline; a queue that never drops (infinite buffer -> latency instead of loss, a different pressure)",
    cheat_control="an organism handed the exact fair share must reach it with zero retransmissions; the ancestor's policy (window-limited, timer-only backoff) must show the collapse at some N: if the world cannot reproduce the 1986 shape with the ancestor, it is not exerting this pressure",
    cost_class="CPU-scale", source_evidence="record human_failure_condition; tcp_output.c 48-58; tcp_timer.c 121-148", purpose="PURPOSE: reliable byte stream over a shared internet (RFC 793 as implemented in 4.2BSD)")

c.pressure("a_timer_must_be_set_from_a_noisy_delayed_measurement_the_organism_takes_of_its_own_transactions",
    condition="each request is answered after a delay drawn from an unknown, drifting distribution; the organism must decide when a request is lost; deciding too early wastes capacity, too late wastes time",
    resource_or_constraint="one sample per outstanding request at most; coarse clock; no side channel", failure_condition="spurious retransmissions (timer < delay) or long stalls (timer >> delay)",
    world_punishes="both", world_rewards="an estimator that tracks the mean and the spread and a timer set from both", observable_consequence="spurious-timeout rate and stall time as the delay distribution's variance is varied",
    vacuity_condition="constant delay", trivial_shortcuts="a timer fixed at the known maximum delay; a world that reveals the delay", cheat_control="an organism given the true delay per request must show zero spurious timeouts and zero stall; the ancestor's mean-only estimator with beta=2 must show spurious timeouts once the variance exceeds the mean: if the world cannot show that difference the pressure is absent",
    cost_class="CPU-scale", source_evidence="tcp_timer.h 74-90; tcp_input.c 485-501", purpose="PURPOSE: retransmission timeout estimation (the 4.2BSD form, before Jacobson 1988)")

c.ancestry("historical_version_of", "4.3BSD Tahoe TCP (1988) adds cwnd/ssthresh/slow start (the record's lineage; bsd-tcp-4.3-tahoe-1988 is in the vault)", note="lineage per the record; the Tahoe body was not opened this pass")
c.residue("PARTIALLY_EXPLAINED", ["tcp_input.c outside 480-700 (state transitions, SYN/RST handling, reassembly, option parsing) not read", "tcp_subr.c (template, respond, drop, close) and tcp_usrreq.c not read",
                                   "the Karn ambiguity (RTT sample spanning a retransmission) is a reading-level claim: t_rtt is not cleared at TCPT_REXMT in tcp_timer.c and tcp_output.c only starts a timer on new data; not run"],
          note="the sender's rate-governing machinery is fully accounted for: window, retransmit timer, persist, SWS thresholds; the finding is what is NOT there")
c.save(state="COARSE")
