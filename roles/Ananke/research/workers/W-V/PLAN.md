# W-V PLAN (E-ANANKE-W-V, T-INS-18, successor of T-INS-16, thr-8c7342a7d513, MWO-0004)

Frozen 2026-09-30 ~06:59Z, BEFORE any champion run. Thresholds are not changed after results.
Context read before this plan (per brief): W-T REPORT RESULTS/DISAGREEMENTS, W-P REPORT
RESULTS/DISAGREEMENTS, W-R PLAN head, code of W-R fork.py/specs.py, W-S probe.py/analyze.py, W-T wt.py,
posthoc_maj.py. Also decompiled the 4781b0a1 genome myself (LOG A1).

## Question
Per-sensor carrier census of MAJ champion 4781b0a1 (sync update_period 2, 5 sensors): whose in-flight
traffic to the readout carries the bit, and is the readout a majority over sensors or a subset rule?

## s1 Instrument
- Carrier unit = the in-flight packets EMITTED BY sensor j (sense_idx[:, j]) and ADDRESSED TO the readout
  site a (read_idx[:, 0]), all slots, all channels, both payload components, sums AND counts.
- Identification (deviation from the brief wording "twin-world packet log", stated here): exact EMITTER
  TAGGING instead of the cue-flip log. TagWorld(World) re-runs the engine's own _emit with the want mask
  restricted to one emitter group into scratch mailboxes (index_add is linear, draws are hashed per
  (world, site, tick, copy) so they are unchanged); the real Msum/Mcnt are written by the unchanged
  engine _emit. Groups: sensor 0..4 and "rest" (all other sites). Tag slot t mod LM is cleared at each
  emission (the engine delivers and clears that slot at the start of the tick; delays >= 1).
  Checks (must pass before any census; test_wv.py):
    T1 TagWorld trace and full state digest == World (bit-identical).
    T2 sum over groups of tag sums/counts == Msum/Mcnt[:, b, a] exactly, every tick.
    T3 swap of the empty sensor set == normal run (bit-identical traces).
    T4 plants: swap of all 5 sensors == W-S flight_a swap (all in-flight to the readout), bit-identical
       (in the plants only sensors emit).
- Swap of sensor set J for world b in an arm block, applied after tick t0+o (lens convention):
  Msum[:, b, a] += T_J(partner) - T_J(b), same for Mcnt, using the base run's tags at that tick (an arm
  world equals the base run until its only swap). Mirror partners share sensor and readout positions.
- Runner: W-R fork_single structure (bit-identical to lens_swap.run_arms per W-R KA-F): one normal
  base run (TagWorld) of M worlds; for trial k fork after tick t0+o_min, tile, apply each arm's swap
  after t0+o, run to trial k's readout. SINGLE-trial arms, trials 1..11.
- Arms per offset: single {j} (5), complement all-but-j (5), ALL5 (all sensors), FLA (W-S flight_a:
  every in-flight packet to the readout, any emitter) = 12 arms.
- Champion: 4781b0a1 via W-R specs.load; worlds assays.world_seeds(0x650, 128) (64 mirror pairs);
  offsets o in {2, 4, 6, 8, 10, 12, 14} (ro_off 16). Pd = 19 is odd, so every offset has both update-clock
  phases q = (t0+o) mod 2 across trials (W-R).

## s2 Statistics
- Eligible pair-trial: trial in 1..11, scored, BOTH partners normal-correct (frozen census convention).
- follow(world, arm) = 1 if sign(arm readout S0) == sign(partner's normal S0), else 0 (a 0 readout counts
  0). Pair-trial follow = mean of its two worlds. Effect e_J = mean over eligible pair-trials.
- 99% CIs: pair bootstrap (resample the 64 mirror pairs with all their trials), 2000 draws, seed 0.
- Strata: primary unit = (offset, phase q) with q = (t0+o) mod 2; secondary = pooled over q per offset.
  A stratum needs >= 20 eligible pair-trials (MIN_ELIGIBLE), else UNDEFINED.
- Descriptors: E = e_ALL5; r_j = e_j / E; r_cj = e_{all-but-j} / E; share s_j = e_j / sum_i e_i;
  additivity A = sum_j e_j / E; F = e_FLA (reference).
- Pivotality (majority test): votes v_i = sign(SENSE_i of trial k in world A); y = world A's normal sign
  (correct). Sensor j is PIVOTAL in the pair-trial iff exactly 3 votes equal y and v_j == y. Contrast
  D_piv = mean follow_j over (pair-trial, j) units with j pivotal - mean over non-pivotal units, pooled
  over j, same pair bootstrap.

## s3 Frozen classification (per stratum)
- INFORMATIVE iff E >= 0.50. Otherwise NOT-INFORMATIVE (in-flight sensor traffic does not decide).
- Carrier set C = { j : 99% CI low of e_j >= 0.03  OR  99% CI low of (E - e_{all-but-j}) >= 0.03 }.
- DICTATOR(j*): r_j* >= 0.70 AND r_c(j*) <= 0.30 AND for every i != j*: 99% CI high of e_i <= 0.10.
- MAJORITY: every j has 99% CI low of e_j >= 0.03 AND max_j r_j <= 0.50 AND min_j r_cj >= 0.60 AND
  D_piv >= 0.50 with 99% CI low > 0.
- else SUBSET(C) if 1 <= |C| <= 2; DISTRIBUTED-NONMAJ if |C| >= 3; REDUNDANT-JOINT if |C| = 0.
- Champion verdict: a class (ignoring the set) holding in >= 2/3 of the INFORMATIVE defined strata;
  otherwise MIXED-BY-STRATUM (listed). If no stratum is informative: NO-INFLIGHT-SENSOR-CARRIER.

## s4 Known answers (plants in W-V/plants_wv.py; built with prometheus.ananke.plants.assemble)
Physics: champion ring (144 sites, radius 3), dest_mode all, loss 0, cap 0, lat_base 5, lat_hop 2,
lat_jitter 0, sync update_period 2 (as the champion), state_dim 3, prog_len 24, no plasticity/WIMM.
MAJ env identical to the champion's (delta 16, flip_p .3). Sensors at ring distance 3,3,2,2,1 (indices
0..4, by envs._pick_at), delays 11, 9, 7; each sensor emits its cue sign once per trial on PAY0; no
relays. Readout silence counter S2 marks a new trial.
- PMAJ: readout sums all arrivals of the trial into S1 (reset on the first arrival after >= 3 silent
  wakes), S0 := S1 -> majority of 5 votes.
- PDICT: readout latches S0 := sign(first arrival wave) -> the distance-1 sensor (index 4) dictates.
- Plant offsets {2, 4, 6, 8, 12}; M = 128, ns 0x650.
- KA-MAJ: PMAJ reads MAJORITY in every informative stratum of o2-o6 (verdict MAJORITY).
- KA-DICT: PDICT reads DICTATOR(4) in every informative stratum of o2-o6 (verdict DICTATOR(4)).
- Must-fail inputs:
  MF1 PDICT: swapping a non-carrying sensor (j = 0..3): each e_j 99% CI high <= 0.05 (no effect).
  MF2 PDICT under the MAJORITY rule: must not read MAJORITY.
  MF3 PMAJ with pivot labels permuted across pair-trials (votes of another pair-trial): D_piv test fails
      (point < 0.50) so the classifier must not read MAJORITY.
  MF4 PMAJ/PDICT at o12 (all packets delivered): NOT-INFORMATIVE (E < 0.50).
- Classifier unit tests on synthetic effect tables (majority, dictator, 2-subset, redundant).

## s5 Predictions (frozen, champion)
- W1: in-flight sensor traffic is informative at >= 1 stratum (E >= .5) - W-P: payload-1 Msum is a
  carrier at every offset (jointly with S1), W-R: channel-follow at o12-14 in one phase.
- W2 (from my decompilation, LOG A1: PAY1 = MAX(IN0_1, SENSE) is rectified; S0 := IN0_1 - 3 + Kp[7]):
  the readout is NOT a majority; expect DISTRIBUTED-NONMAJ or SUBSET, with D_piv < .5.
- W3: ALL5 ~= FLA (W-T: 0 true relays), |E - F| <= .05 at every offset.

## s6 Compute and hygiene
<= 6 core-hours (stop launching at 5.5); <= 4 procs x 1 thread; Fabric lease skullport:cpu8 --as Ananke
for the champion/plant runs; PYTHONDONTWRITEBYTECODE=1; no GPU; outputs <= 3 MB; no git writes.
