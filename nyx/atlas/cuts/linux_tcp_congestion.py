"""Cut: linux-tcp-congestion (ancestry-aware, Stage A COARSE; SOURCE_READ tcp_cubic.c in full and tcp_bbr.c
functions 479-1035 plus the state struct 81-128; the bbr_get_info / register boilerplate 1106-1202 skimmed only).

The record holds TWO whole systems in one body (CUBIC 2008 and BBR 2016). They share a plant they do not contain
(the kernel TCP core: loss detection, rate sampling, pacing, slow start, additive increase) and are cut as two
subsystems of one fossil. Organ ids are prefixed cubic./bbr. so the composition graph never mixes them by accident.
Evidence refs are host-independent: vault:<fossil>/upstream/<file>:<lines>.
"""
from nyx.atlas.author import Cut

CU = "vault:linux-tcp-congestion/upstream/tcp_cubic.c"
BB = "vault:linux-tcp-congestion/upstream/tcp_bbr.c"
c = Cut("linux-tcp-congestion", mode="ANCESTRY_AWARE",
        inspected=["tcp_cubic.c (all 557 lines)", "tcp_bbr.c 81-128 state, 244-320 pacing, 359-552 cwnd, 553-608 cycle, 634-758 lt sampling, 760-1035 model"],
        evidence=[("SOURCE_READ", CU), ("SOURCE_READ", BB)],
        note="two controllers for one plant the fossil does not contain; SOURCE_ONLY, nothing ran; every organ below is a sensor, a filter, an estimator or an actuator setter, and the actuator itself (pacing, cwnd enforcement) is kernel core")

# ----------------------------------------------------------------------------------------------- CUBIC subsystem
cub = c.organ("cubic", human_name="CUBIC congestion control (module)", status="CANDIDATE",
    human_interpretation="grow the congestion window as a cubic function of time since the last loss, so growth is fast far from the last maximum and flat near it, independent of RTT",
    mechanism="a per-connection block (struct bictcp, 86-105) updated from three kernel callbacks: cong_avoid (per ACK, grows cwnd), ssthresh (on loss, shrinks and remembers), acked (per RTT sample, slow-start exit); the subsystem below is the set of mechanisms those callbacks are made of",
    input="ACK count, current cwnd, jiffies, RTT samples, loss events (from kernel core)", output="ca->cnt (ACKs per +1 cwnd), snd_ssthresh, last_max_cwnd", state="struct bictcp: 19 fields", update="event-driven per ACK / per loss",
    assumptions=["loss is the congestion signal", "cwnd < 1M packets (overflow note 262-264)"], interface="struct tcp_congestion_ops (476-499)", dependencies=["kernel: tcp_slow_start, tcp_cong_avoid_ai, tcp_is_cwnd_limited, jiffies"],
    fitness_value_in_ancestor="Linux default since 2.6.19 (record ANCESTRY)", evidence_ref=CU + ":86-105,476-499", confidence="HIGH",
    portability="UNKNOWN", compatibility="NO", utility="UNKNOWN", source_boundary="tcp_cubic.c minus register/unregister/BPF boilerplate",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "feedback": "DELAYED_CLOSED_LOOP", "stochasticity": "ENVIRONMENT_RANDOM", "update_topology": "EVENT_DRIVEN"})

ct = c.organ("cubic.window_target_from_time_since_last_loss", parent=cub, human_name="the cubic function W(t) = C(t-K)^3 + Wmax", status="ACCEPTED",
    human_interpretation="window growth that is concave up to the old maximum and convex beyond it",
    mechanism="at the start of an epoch (first call after a loss) record origin = Wmax and K = cbrt((Wmax - cwnd) * cube_factor); every jiffy compute t = time since epoch + delay_min, target = origin +/- c*(t-K)^3/rtt; convert the target into cnt = cwnd / (target - cwnd) ACKs per increment (or 100*cwnd if at/above target); clamp the first epoch to cnt<=20 and every epoch to cnt>=2",
    input="cwnd, acked, jiffies, delay_min, last_max_cwnd", output="ca->cnt", state="epoch_start, bic_K, bic_origin_point, last_cwnd, last_time",
    update="at most once per jiffy (223-228); epoch restarts when epoch_start==0 (set by ssthresh)", assumptions=["time, not ACK clock, drives growth (RTT-fairness by design)", "fixed-point cube root (cubic_root 167-212) is exact enough"],
    fitness_value_in_ancestor="fast recovery of lost throughput on high-BDP paths plus a plateau at the last known ceiling", failure_landscape="UNKNOWN -- not run; the code's own note: overflow above 1M packets",
    evidence_ref=CU + ":214-297,167-212", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bictcp_update up to the tcp_friendliness label",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "feedback": "DELAYED_CLOSED_LOOP", "memory": "LAST_VALUE", "temporal_horizon": "EPISODE", "stochasticity": "DETERMINISTIC"})

wm = c.organ("cubic.remembered_maximum_with_fast_convergence_decay", parent=cub, human_name="Wmax memory / fast convergence / multiplicative decrease", status="ACCEPTED",
    human_interpretation="on loss, cut the window to beta*cwnd and remember where the loss happened; if the loss came BELOW the previous remembered maximum, remember a point below the current one so a newer flow can claim share",
    mechanism="ssthresh callback: epoch_start=0 (forces a new epoch); if cwnd < last_max_cwnd and fast_convergence then last_max_cwnd = cwnd*(1+beta)/2 else last_max_cwnd = cwnd; return max(cwnd*beta/1024, 2) with beta=717",
    input="cwnd at loss, previous last_max_cwnd", output="new ssthresh, last_max_cwnd", state="last_max_cwnd", update="per loss event",
    assumptions=["a loss below the last max means the bottleneck shrank or a competitor arrived"], fitness_value_in_ancestor="convergence time between flows (the name)",
    evidence_ref=CU + ":340-357", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="cubictcp_recalc_ssthresh",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "update_topology": "EVENT_DRIVEN", "stochasticity": "DETERMINISTIC"})

rf = c.organ("cubic.shadow_aimd_estimate_as_growth_floor", parent=ct, human_name="TCP friendliness", status="ACCEPTED",
    human_interpretation="never grow slower than standard TCP would",
    mechanism="a second window (tcp_cwnd) is advanced by one for every cwnd*3*(1-beta)/(1+beta)... ACKs (delta = cwnd*beta_scale>>3, 300-306) in parallel with the cubic target; if the shadow window is ahead of the real one, cap cnt at cwnd/(tcp_cwnd - cwnd) so the real window catches up at the shadow's rate",
    input="ack_cnt, cwnd", output="a bound on ca->cnt", state="tcp_cwnd, ack_cnt", update="per bictcp_update call", assumptions=["the AIMD rate formula in the paper is what the shadow implements"],
    fitness_value_in_ancestor="fairness against Reno flows on low-BDP paths where the cubic function is slower than AIMD", evidence_ref=CU + ":297-318", confidence="HIGH",
    portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the tcp_friendliness block",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "SUMMARY_STATISTIC", "competition": "CONTENDS"})

mn = c.organ("cubic.running_minimum_of_rtt_samples", parent=cub, human_name="delay_min", status="ACCEPTED",
    mechanism="every valid RTT sample (rtt_us >= 0, not within 1 s after a loss epoch start) lowers delay_min if smaller; delay_min is never raised except by reset on TCP_CA_Loss; delay_min is added to t in the cubic function and is the baseline for both HyStart detectors",
    input="rtt_us per ACK", output="delay_min (usec)", state="delay_min", update="per ACK", assumptions=["the smallest RTT ever seen is the propagation delay"],
    failure_landscape="UNKNOWN by run; by reading: a route change to a longer path is never learned until a loss resets (contrast bbr.windowed_minimum_of_rtt which expires after 10 s)",
    evidence_ref=CU + ":448-474,107-111", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="cubictcp_acked lines 457-467 + bictcp_reset",
    coverage={"input_topology": "STREAM", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "SUMMARY_STATISTIC", "temporal_horizon": "UNBOUNDED", "hidden_state": "ESTIMATES"})

hy = c.organ("cubic.slow_start_exit_by_ack_train_length_or_delay_rise", parent=cub, human_name="HyStart", status="ACCEPTED",
    human_interpretation="leave exponential growth before the first loss, when the path shows signs of queueing",
    mechanism="two detectors OR'd per RTT round, active only in slow start and above cwnd 16: (train) if consecutive ACKs arrive within 2 ms of each other and the train has lasted longer than delay_min (+ a TSO cushion, halved without pacing) since round start, found=1; (delay) the minimum of the first 8+ RTT samples in the round exceeds delay_min + clamp(delay_min/8, 4 ms, 16 ms), found=1; either sets ssthresh = cwnd, which ends slow start in the kernel core",
    input="ACK arrival times, RTT samples, delay_min, cwnd, snd_una vs end_seq (round boundary)", output="snd_ssthresh (once), found flag", state="round_start, end_seq, last_ack, curr_rtt, sample_cnt, found",
    update="per ACK; round reset when snd_una passes end_seq", assumptions=["ACK spacing reflects bottleneck spacing (defeated by ACK compression/aggregation, hence hystart_ack_delay 375-384)"],
    fitness_value_in_ancestor="fewer slow-start overshoot losses on large-BDP paths", failure_landscape="UNKNOWN by run; by reading: pacing and TSO change the ACK train timing (the two cushions 375-384, 405-407 are patches for that)",
    evidence_ref=CU + ":118-128,375-446,468-473", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="hystart_update + bictcp_hystart_reset + hystart_ack_delay",
    coverage={"input_topology": "STREAM", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "WINDOW", "temporal_horizon": "WINDOW", "hidden_state": "ESTIMATES"})

# ------------------------------------------------------------------------------------------------- BBR subsystem
bbr = c.organ("bbr", human_name="BBR congestion control (module)", status="CANDIDATE",
    human_interpretation="pace at the estimated bottleneck bandwidth and keep inflight near bandwidth*min_rtt, instead of reacting to loss",
    mechanism="one callback per ACK (bbr_main 1026-1035): update a model from the kernel's rate_sample (bw filter, ack aggregation, gain cycle, startup plateau, drain, min_rtt/probe_rtt, gains), then set pacing rate = bw*pacing_gain and cwnd from bw*min_rtt*cwnd_gain",
    input="rate_sample {delivered, interval_us, rtt_us, losses, is_app_limited, prior_in_flight, acked_sacked, is_ack_delayed}", output="sk_pacing_rate, snd_cwnd, snd_ssthresh (entering DRAIN)", state="struct bbr (89-128): ~30 fields",
    update="per ACK", assumptions=["delivery rate and RTT samples exist (kernel rate sampling, 2016+)", "the sender can pace"], interface="struct tcp_congestion_ops with cong_control (1156-1170)",
    dependencies=["kernel: tcp_rate sampling, sk_pacing_rate, lib/win_minmax.c, tcp_packets_in_flight"], fitness_value_in_ancestor="Google's production sender (record ANCESTRY); throughput under bufferbloat and policers",
    evidence_ref=BB + ":89-128,1015-1035,1156-1170", confidence="HIGH", portability="UNKNOWN", compatibility="NO", utility="UNKNOWN", source_boundary="tcp_bbr.c minus get_info/register/BPF",
    coverage={"input_topology": "EVENT", "output_topology": "VECTOR", "feedback": "DELAYED_CLOSED_LOOP", "stochasticity": "SEEDED_RANDOM", "update_topology": "EVENT_DRIVEN", "hidden_state": "ESTIMATES"})

bw = c.organ("bbr.windowed_maximum_of_delivery_rate_samples", parent=bbr, human_name="max_bw filter (BtlBw estimate)", status="ACCEPTED",
    mechanism="per ACK, bw = delivered/interval_us from the rate sample; samples flagged app-limited are dropped unless they exceed the current max; the max over the last 10 packet-timed rounds is kept by a 3-slot windowed min/max filter (kernel lib, not in the body); round boundaries are detected by prior_delivered passing next_rtt_delivered",
    input="rate_sample.delivered, interval_us, is_app_limited, prior_delivered", output="bbr_max_bw()", state="struct minmax bw (3 samples), rtt_cnt, next_rtt_delivered, round_start",
    update="per ACK; window advances per round", assumptions=["the largest recent delivery rate is the bottleneck rate", "the window (10 rounds) is longer than the gain cycle (8 phases) so the probe's high sample survives"],
    dependencies=["lib/win_minmax.c minmax_running_max -- NOT in the fossil"], fitness_value_in_ancestor="the numerator of everything: pacing rate and BDP", failure_landscape="UNKNOWN by run; by reading: an ack-aggregated sample can exceed the true rate (hence the extra_acked organ)",
    evidence_ref=BB + ":760-815,215-231", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_update_bw minus the lt_bw_sampling call",
    coverage={"input_topology": "STREAM", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "WINDOW", "temporal_horizon": "WINDOW", "hidden_state": "ESTIMATES"})

mr = c.organ("bbr.windowed_minimum_of_rtt_with_forced_low_inflight_probe", parent=bbr, human_name="min_rtt filter + PROBE_RTT", status="ACCEPTED",
    mechanism="min_rtt_us takes any smaller RTT sample; if 10 s pass with no new minimum the filter is 'expired' and (a) the next non-delayed sample replaces it, (b) the mode switches to PROBE_RTT: cwnd is forced down to 4 packets until inflight <= 4, then held for 200 ms plus one round, then the saved cwnd is restored and the mode reset (STARTUP if not full, else PROBE_BW)",
    input="rate_sample.rtt_us, is_ack_delayed, jiffies, packets_in_flight", output="min_rtt_us; mode changes; cwnd clamp to 4", state="min_rtt_us, min_rtt_stamp, probe_rtt_done_stamp, probe_rtt_round_done, prior_cwnd, idle_restart",
    update="per ACK; a 10 s timer implemented by timestamps", assumptions=["draining one's own queue for 200 ms reveals the propagation delay", "all BBR flows on a path will synchronise their probes (the same 10 s / 200 ms constants)"],
    fitness_value_in_ancestor="the RTT term of the BDP; also the only mechanism that lowers inflight without a loss", evidence_ref=BB + ":940-984,907-925,320-330,625-632", confidence="HIGH",
    portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_update_min_rtt + bbr_check_probe_rtt_done + bbr_save_cwnd",
    coverage={"input_topology": "STREAM", "output_topology": "MIXED", "state_amount": "CONSTANT", "memory": "WINDOW", "temporal_horizon": "WINDOW", "hidden_state": "ESTIMATES", "cooperation": "COORDINATES"})

sm = c.organ("bbr.mode_machine_with_bandwidth_plateau_detector", parent=bbr, human_name="STARTUP / DRAIN / PROBE_BW / PROBE_RTT state machine", status="ACCEPTED",
    mechanism="STARTUP paces at gain 2.885 until the max_bw filter fails to grow by 25% for 3 consecutive rounds (full_bw, full_bw_cnt); then DRAIN at gain 1/2.885 until inflight <= BDP; then PROBE_BW (gain cycle); PROBE_RTT is entered from any mode by the min_rtt organ and returns to STARTUP or PROBE_BW by full_bw_reached; each mode fixes (pacing_gain, cwnd_gain)",
    input="bbr_max_bw over rounds, inflight, round_start, app_limited flag", output="mode; pacing_gain; cwnd_gain; snd_ssthresh on entering DRAIN", state="mode (3 bits), full_bw, full_bw_cnt, full_bw_reached",
    update="per ACK, mode transitions at round boundaries", assumptions=["a rate that stops growing at 2.885x pacing means the pipe is full (not a policer, not app-limited)"],
    fitness_value_in_ancestor="startup without a loss; the transitions are where BBR's throughput/latency trade-off lives", evidence_ref=BB + ":81-86,872-905,986-1013,609-632,207-213", confidence="HIGH",
    portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_check_full_bw_reached + bbr_check_drain + bbr_update_gains + reset_*_mode",
    coverage={"input_topology": "MIXED", "output_topology": "DECISION", "state_amount": "CONSTANT", "update_topology": "EVENT_DRIVEN", "memory": "LAST_VALUE", "adaptation": "POLICY"})

gc = c.organ("bbr.eight_phase_pacing_gain_cycle_with_inflight_gated_advance", parent=sm, human_name="ProbeBW gain cycling", status="ACCEPTED",
    mechanism="pacing_gain steps through [5/4, 3/4, 1, 1, 1, 1, 1, 1]; a phase lasts at least one min_rtt of wall time; the 5/4 phase persists until inflight reaches 5/4*BDP or a loss occurs; the 3/4 phase ends early once inflight <= BDP; the starting phase index is randomised (bbr_cycle_rand=7, 616-623) so flows do not synchronise",
    input="min_rtt, inflight, losses, max_bw", output="pacing_gain (via cycle_idx)", state="cycle_idx (3 bits), cycle_mstamp", update="per ACK check; advance at phase end", assumptions=["briefly overshooting then undershooting the estimated BDP measures spare capacity and yields to newcomers"],
    fitness_value_in_ancestor="fair-share convergence among BBR flows", evidence_ref=BB + ":130-169,553-607,616-623", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_is_next_cycle_phase + bbr_advance_cycle_phase + bbr_update_cycle_phase",
    coverage={"input_topology": "MIXED", "output_topology": "SCALAR", "state_amount": "CONSTANT", "update_topology": "SWEEP", "stochasticity": "SEEDED_RANDOM", "competition": "CONTENDS"})

lt = c.organ("bbr.long_term_rate_sampling_between_loss_bursts", parent=bbr, human_name="policer detection (lt_bw)", status="ACCEPTED",
    human_interpretation="detect a token-bucket policer and pace at its long-term rate instead of cycling into it",
    mechanism="sampling starts at the first loss; an interval must span 4-16 rounds, end on a loss, and show loss rate >= 20% (50/256); the interval's delivered/elapsed is compared with the previous interval's: if within 1/8 or 4 kbps, lt_use_bw=1 and pacing_gain is pinned to 1.0 at lt_bw for up to 48 rounds, after which sampling resets and the gain cycle restarts; app-limited samples abort the interval",
    input="tp->lost, tp->delivered, delivered_mstamp, rs->losses, is_app_limited, round_start", output="lt_bw, lt_use_bw (which overrides bbr_bw and the cycle gain)", state="lt_is_sampling, lt_rtt_cnt, lt_use_bw, lt_bw, lt_last_delivered, lt_last_stamp, lt_last_lost",
    update="per ACK", assumptions=["a policer reveals itself as periodic loss bursts at a steady rate; two agreeing intervals are enough"], fitness_value_in_ancestor="throughput on policed paths (Google's stated motivation in the comments 685-686)",
    failure_landscape="UNKNOWN by run", evidence_ref=BB + ":183-193,634-758,223-231", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_lt_bw_* functions",
    coverage={"input_topology": "STREAM", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "WINDOW", "adaptation": "PARAMETER", "hidden_state": "ESTIMATES", "temporal_horizon": "WINDOW"})

ea = c.organ("bbr.windowed_maximum_of_excess_acked_beyond_expected", parent=bbr, human_name="ACK aggregation estimator (extra_acked)", status="ACCEPTED",
    mechanism="within an epoch, expected_acked = bw * elapsed; the running sum of acked packets minus expected is the excess; the epoch resets when the sum falls to or below expected; the max excess is kept in a 2-slot window that rotates every 5 rounds; the value (clamped to cwnd and to bw*100 ms) is added to the cwnd target",
    input="rs->acked_sacked, delivered_mstamp, bbr_bw", output="extra_acked (max of 2 slots)", state="ack_epoch_mstamp, ack_epoch_acked, extra_acked[2], extra_acked_win_rtts, extra_acked_win_idx", update="per ACK",
    assumptions=["ACKs arrive in batches (wifi, cellular) so cwnd must cover the silence between batches"], fitness_value_in_ancestor="throughput on aggregating links", evidence_ref=BB + ":196-202,233-242,456-477,816-870", confidence="HIGH",
    portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_update_ack_aggregation + bbr_extra_acked + bbr_ack_aggregation_cwnd",
    coverage={"input_topology": "STREAM", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "WINDOW", "hidden_state": "ESTIMATES"})

cw = c.organ("bbr.window_from_bandwidth_delay_product_with_recovery_conservation", parent=bbr, human_name="cwnd setter (BDP * gain + extras)", status="ACCEPTED",
    mechanism="target = bw * min_rtt * cwnd_gain (bdp 359-392, with a fallback to the initial window when min_rtt is unknown) + extra_acked + a quantization budget (3 TSO segments, +2 in the 3/4 phase); if the pipe is full, cwnd = min(cwnd + acked, target) else cwnd grows by acked until target; floor 4; on entering loss recovery cwnd = inflight + acked (packet conservation) and on leaving it the prior cwnd is restored; in PROBE_RTT the result is clamped to 4",
    input="bw, min_rtt, cwnd_gain, acked, losses, CA state, prior_cwnd", output="snd_cwnd", state="prior_cwnd, packet_conservation, prev_ca_state", update="per ACK",
    assumptions=["the kernel enforces cwnd; this organ only chooses it"], fitness_value_in_ancestor="bounds inflight so the pacing organ cannot fill a buffer alone", evidence_ref=BB + ":359-435,479-551", confidence="HIGH",
    portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_set_cwnd + bbr_bdp + bbr_quantization_budget + bbr_set_cwnd_to_recover_or_restore",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "recovery": "ROLLS_BACK", "update_topology": "EVENT_DRIVEN"})

pr = c.organ("bbr.pacing_rate_from_bandwidth_times_gain", parent=bbr, human_name="pacing rate setter", status="ACCEPTED",
    mechanism="rate = bw * pacing_gain * (100 - 1)% in bytes/s (244-264); the first rate before any RTT sample comes from the initial cwnd / first srtt (266-283); the rate only moves DOWN before the pipe is full unless it is higher than the current one (295-300)",
    input="bw, pacing_gain, mss, srtt", output="sk->sk_pacing_rate", state="has_seen_rtt", update="per ACK", assumptions=["the kernel's pacing (fq or internal) honours the rate"],
    fitness_value_in_ancestor="the primary actuator: BBR is rate-based, cwnd is the backstop", evidence_ref=BB + ":244-301", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="bbr_set_pacing_rate + bbr_bw_to_pacing_rate + bbr_init_pacing_rate_from_rtt",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "update_topology": "EVENT_DRIVEN"})

# ------------------------------------------------------------------------------------------------ rejected cuts
c.reject("slow start / additive increase (tcp_slow_start, tcp_cong_avoid_ai)", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY",
         evidence="tcp_cubic.c 325-338 calls tcp_slow_start and tcp_cong_avoid_ai; neither is in the body (kernel net/ipv4/tcp_cong.c); the fossil only chooses ca->cnt", note="the human name 'CUBIC' includes slow start; the executable boundary of the body does not")
c.reject("loss detection / fast recovery / RACK", reason="EFFECT_FROM_ENVIRONMENT",
         evidence="both modules receive losses as rs->losses or icsk_ca_state transitions; no line in either file detects a loss", note="a pressure source, not machinery of this fossil")
c.reject("the windowed min/max filter algorithm (minmax_running_max)", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY",
         evidence="tcp_bbr.c 813 and 233-242 call lib/win_minmax.c; the 3-slot Kathleen Nichols filter is not in the body; bbr.windowed_maximum_of_delivery_rate_samples records its USE, the mechanism itself is UNKNOWN from this fossil")
c.reject("cubic_root (fixed-point cube root)", reason="BELOW_MEANINGFUL_GRAIN",
         evidence=CU + ":167-212 -- a Newton step on a table-seeded estimate; it is arithmetic in service of cubic.window_target, with no state and no behaviour of its own")
c.reject("'CUBIC' and 'BBR' as one fossil", reason="OTHER",
         evidence="two independent modules registered separately (476-499, 1156-1170), no shared line of code; Techne's record packs them as before/after of one redesign", note="TECHNE FEEDBACK: two whole systems in one record; the atlas cuts them as two subsystems and the ancestry edge between them is intra-record")
c.reject("BPF kfunc / module registration / get_info", reason="GENERIC_LANGUAGE_MECHANICS",
         evidence=CU + ":501-557, " + BB + ":1106-1202")

# ------------------------------------------------------------------------------------------------ composition
c.edge(mn, ct, "feeds", note="delay_min added to t (259)"); c.edge(mn, hy, "feeds", note="baseline for both detectors")
c.edge(wm, ct, "feeds", note="last_max_cwnd -> origin and K at epoch start"); c.edge(wm, ct, "restores", note="epoch_start=0 forces a new epoch")
c.edge(rf, ct, "suppresses", note="caps cnt so the cubic curve is never slower than the AIMD shadow")
c.edge(hy, cub, "triggers", note="sets ssthresh = cwnd once; ends slow start in the kernel core"); c.edge("ENVIRONMENT", wm, "triggers", note="kernel loss event -> ssthresh callback")
c.edge("ENVIRONMENT", bw, "feeds", note="kernel rate_sample"); c.edge(bw, cw, "feeds"); c.edge(bw, pr, "feeds"); c.edge(bw, sm, "feeds", note="plateau detector reads max_bw per round")
c.edge(mr, cw, "feeds", note="min_rtt in the BDP"); c.edge(mr, sm, "triggers", note="PROBE_RTT entry/exit"); c.edge(mr, gc, "feeds", note="phase length = min_rtt")
c.edge(sm, gc, "gates", note="cycle runs only in PROBE_BW"); c.edge(sm, pr, "selects", note="pacing_gain by mode"); c.edge(sm, cw, "selects", note="cwnd_gain by mode; full_bw_reached switches the cwnd rule")
c.edge(gc, pr, "updates", note="pacing_gain per phase"); c.edge(lt, gc, "suppresses", note="lt_use_bw pins the gain at 1.0 and later restarts the cycle"); c.edge(lt, bw, "competes", note="bbr_bw() returns lt_bw when lt_use_bw, else max_bw (223-231)")
c.edge(ea, cw, "feeds", note="extra_acked added to target cwnd"); c.edge(bw, ea, "feeds", note="expected_acked = bw * elapsed"); c.edge("ENVIRONMENT", cw, "triggers", note="CA state transitions drive packet conservation")

# --------------------------------------------------------------------------------------------------- pressures
c.pressure("shared_bottleneck_with_loss_as_the_only_signal",
    condition="many senders share a link whose only feedback is a dropped packet, observed one round trip late; over-sending collapses everyone's useful throughput", resource_or_constraint="bottleneck capacity; one RTT of delay before any signal",
    failure_condition="congestion collapse (record: 1986)", world_punishes="sending more than the link drains for longer than the buffer hides", world_rewards="backing off on a loss and re-growing at a rate that neither idles the link nor starves neighbours",
    observable_consequence="throughput per flow, loss rate, convergence time between flows", vacuity_condition="a single sender on an uncontended link; or a link that never drops", trivial_shortcuts="send at a fixed low rate (safe, wastes the link); a world must reward utilisation AND punish loss",
    cheat_control="a sender that reads the bottleneck capacity directly from the world must reach the utilisation that the loss-signal-only sender can only approach; if it cannot, the world does not reward the capability", cost_class="CPU-scale (a queue simulator)", source_evidence="record human_failure_condition; tcp_cubic.c 340-357", purpose="PURPOSE: transmit a byte stream reliably")
c.pressure("deep_buffers_hide_congestion_from_the_loss_signal",
    condition="the bottleneck buffer holds many seconds of data, so loss arrives long after queueing delay has grown; a loss-driven sender fills the buffer and every flow's latency rises", resource_or_constraint="buffer depth >> bandwidth*propagation delay",
    failure_condition="bufferbloat: throughput fine, latency ruined", world_punishes="inflight beyond bandwidth*min_rtt", world_rewards="an estimate of the pipe (rate and floor delay) used instead of waiting for loss",
    observable_consequence="queueing delay under load; min_rtt drift", vacuity_condition="shallow buffers (loss and delay rise together)", trivial_shortcuts="a fixed low rate; a sender that never probes for more",
    cheat_control="a sender given the true bandwidth and propagation delay must show low delay at full utilisation in the world; otherwise the world's reward is not measuring the capability", cost_class="CPU-scale", source_evidence="record ANCESTRY ('then bufferbloat'); tcp_bbr.c 940-984, 359-392", purpose="PURPOSE: same")
c.pressure("periodic_loss_bursts_from_a_token_bucket_enforcer",
    condition="a middlebox admits traffic at a fixed long-term rate and drops bursts above it; a sender that probes upward is punished with a burst of loss every probe", resource_or_constraint="an external rate cap invisible except through loss timing",
    failure_condition="repeated loss bursts each probe cycle; throughput well below the cap", world_punishes="probing above the cap", world_rewards="inferring the cap from two agreeing loss-bounded intervals and holding at it",
    observable_consequence="loss rate vs sending rate shows a knee at the cap", vacuity_condition="no enforcer, or an enforcer with a bucket larger than the probe", trivial_shortcuts="a sender that halves on every loss (Reno) finds a rate below the cap but oscillates; the world must reward holding AT the cap",
    cheat_control="a sender told the cap must hold it with near-zero loss; if the world does not distinguish that from the oscillating sender, the pressure is not being measured", cost_class="CPU-scale", source_evidence="tcp_bbr.c 183-193, 634-758 and its comments", purpose="PURPOSE: same")
c.pressure("batched_acknowledgements_understate_the_pipe",
    condition="the return path delivers acknowledgements in bursts (link-layer aggregation), so per-ACK rate and delay samples misrepresent the forward path and a window sized to the true BDP idles between bursts", resource_or_constraint="feedback granularity",
    failure_condition="underutilisation despite a correct rate estimate", world_punishes="a window with no allowance for feedback silence", world_rewards="estimating the excess acked beyond the expected and provisioning for it",
    observable_consequence="throughput gap that closes when cwnd is padded", vacuity_condition="ACKs arrive one per segment", trivial_shortcuts="an unbounded cwnd (fills buffers; punished by the bufferbloat pressure)",
    cheat_control="a sender with the aggregation size given must reach full throughput", cost_class="CPU-scale", source_evidence="tcp_bbr.c 816-870 comments; tcp_cubic.c 366-384 (the same problem patched in HyStart)", purpose="PURPOSE: same")

# ----------------------------------------------------------------------------------------------------- ancestry
c.ancestry("rival_of", "linux-tcp-congestion", note="INTRA-RECORD: bbr.* rival_of cubic.* (both live Linux modules; the record packs them as before/after)")
c.ancestry("successor_of", "bsd-tcp-4.3-reno-1990", note="NewReno -> CUBIC per Techne's record of the reno fossil (superseded edge there)")

c.residue("PARTIALLY_EXPLAINED", [
    "the plant: kernel TCP core (loss detection, rate sampling, cwnd enforcement, pacing, slow start, additive increase) is outside the body; every organ here is a controller fragment whose behaviour is unobservable without it",
    "lib/win_minmax.c (the windowed filter used by bbr.max_bw and cited by BBR's design) is not in the body",
    "nothing ran: every coverage cell is READ; failure_landscape fields are UNKNOWN by run",
    "cubic_root's accuracy vs a true cube root and its effect on K: not measured",
], note="SOURCE_ONLY fossil; Stage C needs a plant (a kernel with netem, per the record) that Techne has not built")
c.save(state="COARSE")
