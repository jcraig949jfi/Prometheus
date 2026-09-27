# Ananke spikes 2026-09-27 -- LOG (all Attempts kept, including failures)

Plan: SPIKES_2026-09-27_PLAN.md @ 8e081dcb1. Host: M1 GPU, free at 19:08Z.

A1 S-M2 first run FAILED (script bug, not data): numpy advanced indexing
   ms[:, bi, an, :, 0] put the batch axis first, so the decoder got [LM]
   instead of [B]. Fixed to ms[..., 0][:, bi, an, :]. No result was read
   before the fix.
Deviation D1: the plan's "slot_roll -1" cannot be built (packets cannot be
   delivered before they were sent). Replaced by +1 and +2 delays, noted
   before the run.
A2 S-M2 ran (298 s): out/s_m2.json. Fresh champions regenerated
   BIT-IDENTICALLY from stored search seeds (held acc equal to 1e-12).
A3 S-M3 ran (25 s): out/s_m3.json.
A4 S-F ran: out/s_f.json.

ADDENDUM (before running; exploratory, not in the plan): S-M2b gap sweep.
   S-F showed that M2's cue-bearing deliveries to the actuator happen only
   at lags -2..0: the bit leaves and comes back just before the readout.
   Question (prior-art item 2): tuned echo or open-ended recirculation?
   Evaluate the frozen specimen and the 3 fresh SIGNAL champions at gap in
   {4, 6, 8, 10, 12, 16, 24} (other env dials as trained), 64 worlds, ns
   0x5E2.
   Prediction: TUNED ECHO. Accuracy peaks at the trained gap 8 (+-1 or 2,
   from the +1-delay tolerance) and falls toward chance at gap >= 12 and at
   gap 4. If it holds high out to gap 24: open-ended recirculation.
   Decision: "tuned" if acc(gap 16) lo99 < 0.60 in >= 3 of 4 champions;
   "open-ended" if acc(gap 16) lo99 >= 0.75 in >= 3 of 4; else "mixed".
A5 S-M2b ran: out/s_m2b.json. Fresh genomes are cached in
   out/champions_m2.json (the C1b rows never stored them: an
   instrumentation gap, see backlog T-INS-3).

RESULTS vs PLAN PREDICTIONS (pair mean [lo99]; per-trial accuracy, 12 trials)
S-M2, 4 champions (specimen 4ab2ba01; fresh1-3 regenerated bit-identically):
  D1 swap_inflight      FLIP in 4/4 (0.13-0.15)              pred FLIP        HELD
  D2 swap_sitestate     NO-EFFECT 4/4                        pred NO-EFFECT   HELD
  D3 swap_payload_only  FLIP 4/4                             pred FLIP        HELD
  D4 swap_counts_only   NO-EFFECT 4/4                        pred NO-EFFECT   HELD
  D5/D6 one component   the code component FLIPS, the other has no effect:
                        pay1 in specimen, fresh2, fresh3; pay0 in fresh1
                                                             pred pay1        HELD 3/4
  D7a delay +1          NO-EFFECT 4/4                        pred CHANCE/sm.  LOST (tolerant)
  D7b delay +2          CHANCE 3/4 (0.75-0.81), NO-EFFECT 1/4
  D8 recipient_roll     NO-EFFECT 3/4, CHANCE 1/4 (0.80)     pred CHANCE      LOST
  D9 swap_w_only        NO-EFFECT 4/4                        pred NO-EFFECT   HELD
  Decoders (fit on half the pairs, scored on the other half): sign of the
  code component's in-flight sum = 1.00 [1.00], p .0005, in 4/4.
  Restricted to packets addressed to the actuator = 0.96-0.98. Counts,
  count-to-actuator and arrival lag = chance.
S-M3 (0a23398f, f6b623cd):
  E1 r differs between mirror partners: 0.0% at every tick   pred < 5%  HELD
     r changes: 2.1%/tick in trial 0, then 0; every site ends on rule 0
  E2 freeze_rule after 2 trials: identical to normal          pred +-.05 HELD
  E2b freeze from tick 1: 0.635 / 0.646 vs 0.674 / 0.673 (small)
  E3 swap_r mid-delta: NO-EFFECT                              pred NO-EFF HELD
  E4 reset_r to r0 mid-delta: 0.645 / 0.628 (small, not chance) pred CHANCE LOST
  E5 freeze from the start: 0.53 / 0.54; attempted emissions 43.9k -> 11.1k
     (SETRULE enables transport)                              pred change HELD
  swap_inflight mid-delta: FLIP (0.33 / 0.33). The cue rides in flight.
S-F cue-arrival profile at the actuator, from single-cue twins (share of
cue-bearing deliveries from cue onset to readout at lag 0):
  M3 0a23398f 1.00, f6b623cd 1.00 (C1 window coverage 0%)     pred ~1.0  HELD
  RELAY 0.08 / 0.31 / 0.00 / 0.27                             pred < .30 LOST for 31cd2a8a (0.31)
  MAJ D cells 0.07 / 0.07; M2 0.20 (arrivals only at lags -2..0)
S-M2b gap sweep: peak at the trained gap 6-8, gap 10 partial, gap >= 12
  at chance in 4/4. acc(gap 16) lo99 < 0.60 in 4/4 -> TUNED    pred TUNED HELD
Genome decompilation (read-only), M2 specimen: EMIT is constant (every
  awake site emits every tick); PAY0 := SENSE; PAY1 := IN0_0 (a received
  component-0 value is re-emitted on component 1); S0 := IN0_0 + IN0_1
  (readout = what arrived this tick). The cue makes a two-stage pipeline
  round trip, and the payload index works as a hop-stage tag.
Wall: about 12 min of GPU in total. No other seat's compute was seen.

ADDENDUM 2 (before running; exploratory): S-CT carrier table over the 12
C1 D-wave adjudicated cells (4 HOLD, 4 RELAY, 4 MAJ incl. the two M3).
Swaps at mid-interval (HOLD: C1b t_m; RELAY/MAJ: t0 + delta//2):
inflight, sitestate, payload-only, counts-only, delay +1, w only. ns 0x5E3.
Predictions: HOLD latches: sitestate FLIP, inflight NO-EFFECT. RELAY and
MAJ: inflight FLIP, payload-only FLIP, counts-only NO-EFFECT, sitestate
NO-EFFECT. No cell carries the bit in counts (timing-only codes absent:
T-TM-1 prior = none).

ADDENDUM 3 (before running): joint swap on MAJ 4781b0a1 (inflight CHANCE and sitestate CHANCE, S-CT). Prediction: swapping inflight+sitestate together FLIPS -> the bit is JOINTLY carried (T-DM-2 candidate). Also the same at t0+1 and t0+3 to see where the split moves.
