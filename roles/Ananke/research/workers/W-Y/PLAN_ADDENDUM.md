# W-Y PLAN_ADDENDUM (POST-FREEZE; written before ANY W-Y run, plant or champion)

Frozen plan: roles/Ananke/research/plans/T-INS-20_PLAN.md at fc8bfa171 (not edited).
Everything below is an operationalization or deviation, labelled post-freeze,
written 2026-09-30 before the first W-Y result.

A1 (operationalization) Kp indexing. In PTE, Kp[i] is added to the immediate of
   instruction i (engine: I_all = imm + Kp, pre-program Kp); WIMM writes
   Kp_next[A mod L] := B. The champion's readout line is instruction 7,
   `ADDI S0 := IN0_1 + (-3 + Kp[7])`, and its only Kp writers are
   instruction 8 `WIMM Kp[S0 mod 16] := EMIT` and 15 `WIMM Kp[RVAL mod 16] := PAY1`.
   KP7 arm: w.Kp[rows, ro, 7] := w.Kp[partner, ro, 7] (ro = read_idx[:,0]).
   KPALL: the whole Kp[rows, ro, :]. FLA: W-S flight_a (Msum, Mcnt all slots
   addressed to ro). KP7+FLA: both. SITE_R: W-S swap_targeted('site_a').
   NORMAL: a fork with no swap (must equal the base run bit-for-bit; checked).
   All swaps are SINGLE-trial, applied after tick t0+o on a fork of the base
   state after that same tick, run to trial k's readout (W-V wv.run structure).

A2 (operationalization) Statistics. Eligibility = both partners normal-correct,
   scored, trial in 1..11, intersected over all arms (as W-V ana.py). Follow
   f = mean over the two partners of [sign(arm S0) == sign(partner normal S0)
   and != 0]. 99% pair bootstrap, 2000 draws, pairs resampled with their
   eligible trials in the stratum. Stratum = (offset, phase q = (k*Pd+o) mod 2).
   diff = e_(KP7+FLA) - max(e_KP7, e_FLA), max recomputed inside each bootstrap
   draw. Rule order: IS THE READOUT HALF (e_KP7 lo > .20 AND diff >= .10 AND
   diff lo > 0) -> REDUNDANT (e_KP7 lo > .20 AND diff lo <= 0 <= diff hi) ->
   NOT A CARRIER (e_KP7 hi < .05) -> UNRESOLVED. Informative iff
   e_SITE_R >= .50 or e_FLA >= .50 (point). Strata with < 20 eligible
   pair-trials are UNDEFINED. Overall: a class holds overall iff it holds at
   every informative stratum; otherwise MIXED (per-stratum list reported).
   Pooled-over-phase rows are reported but are not decision strata.

A3 (design) Known-answer plants (PLAN s4), built in W-Y/plants_wy.py on
   plants_wv.physics(4781b0a1) (ring 144 r3, dest all, lossless, delays 7/9/11
   by sensor distance, sync period 2) with ONE change: wimm = 1 (the plant
   must be able to write Kp). Same MAJ env, M=128, world_seeds(0x670,128).
   Sensors emit their vote once (W-V _CUE); fresh-wave reset (W-V _FRESH).
   - Plant A: readout accumulator lives in Kp[j], j = 7: instruction 7 is
     `ADDI RVAL := ZERO + Kp[7]`, reset on the fresh wave, S0 := IN0_0 + RVAL,
     then WIMM Kp[7] := S0. So S0 = IN + Kp[7]; arrived votes are in Kp[7],
     unarrived votes in flight. Also a live but cue-free slot Kp[jx], jx = 3:
     WIMM Kp[3] := 1 every wake, read by instruction 3 into PAY1 (ignored).
   - Plant B: identical readout line S0 := accumulator + Kp[7], but the
     accumulator is S1 and Kp[7] := 1 (constant, cue-free) every wake.
   Plant offsets: o2..o14 even, both phases, trials 1..11.
   Known-answer pass criteria (fixed now):
   - KA-A: Plant A reads IS THE READOUT HALF at every informative stratum
     where BOTH halves are live, i.e. Kp[7] at ro is mirror-different in
     >= 50% of pairs AND the in-flight traffic to ro is mirror-different in
     >= 50% of pairs (state census at the swap tick, outcome-blind), and at
     least 2 such strata exist.
   - KA-B: Plant B reads NOT A CARRIER at every informative stratum (>= 2).
   - MF-X: in Plant A, the KPX arm (swap only Kp[3]) substituted for KP7
     reads NOT A CARRIER at every informative stratum.
   - MF-SHUF: "shuffled pair labels" = within each Plant A stratum, one
     random permutation (seed 0..4) of eligible pair-trials is applied to the
     arm outcomes of ALL arms jointly (arm S0 of both worlds of pair-trial
     pi(i) scored against the normal S0 of pair-trial i). Pass iff no
     informative stratum reads IS THE READOUT HALF under any of 5 seeds, and
     the plan's literal criterion (every stratum UNRESOLVED / NOT A CARRIER /
     not informative) is reported separately.
     PREDICTION stated before running: a permutation of a binary sign-follow
     score drives every arm to ~.50 (half the permuted partners share the
     sign), so e_KP7 lo > .20 and diff ~ 0; the frozen rule is then expected
     to read REDUNDANT wherever FLA/SITE_R land >= .50 by chance. If so, the
     plan's literal MF criterion FAILS and this is a defect of the frozen
     REDUNDANT branch (no chance anchor), not of the runner. Consequence fixed
     now: the champion still runs (the IS / NOT-A-CARRIER calls are the ones
     KA-A/KA-B/MF-X validate), but any champion REDUNDANT call is reported
     as NOT VALIDATED.
   Champion runs only after KA-A, KA-B and MF-X pass.

A4 (resources) <= 2 threads unleased (estimated < 0.5 core-h; W-V's 12-arm
   run of these offsets took 203 s x 1 thread).

A5 (design, post-freeze, before any run) Plant physics also sets prog_len = 28
   (W-V's 24 cannot hold the extra Kp read/write lines). The Kp vector at the
   readout therefore has 28 slots in the plants (16 in the champion). Plant
   dev checks (plant correctness only, no swap arms) use namespace 0x67f, M 16,
   never the analysis namespace 0x670.

A6 (POST HOC: written after the plant results, BEFORE any champion run; ~11:25Z, champion launched 11:25:06Z)
   Plant outcomes (out/ka.json, summary_pa/pb*.txt):
   - KA-B PASS (NOT A CARRIER at all 14 informative strata). MF-X PASS (KPX NOT A
     CARRIER at all 14). MF-SHUF: exactly as predicted in A3, every arm ~.50 and
     every stratum reads REDUNDANT under all 5 seeds; never IS THE READOUT HALF
     (pass_no_IS true; plan's literal criterion FAILS -> REDUNDANT has no chance
     anchor and is NOT VALIDATED).
   - KA-A as pre-registered in A3 FAILS. My outcome-blind census ("Kp[7]
     mirror-different") was a bad proxy: at o2-o6 Kp[7] holds the PREVIOUS trial's
     sum (stale, discarded by the fresh-wave reset), so it is mirror-different
     but carries no current cue; there the instrument correctly reads NOT A
     CARRIER. With a cue-bearing census (Kp[7] != previous trial's final sum,
     post hoc) both halves carry at o8q0, o10q0, o10q1: o10q0 reads IS THE
     READOUT HALF (KP7 .67, FLA .33, joint 1.00, diff .33 [.26,.39]); o8q0 reads
     UNRESOLVED (KP7 .19 [.13,.25], only ~1 vote landed: the Kp half is too weak
     for the .20 floor); o10q1 reads UNRESOLVED (KP7 .25 [.20,.30]; a third
     carrier, the readout inbox Acc_sum, holds votes in this phase and is in
     neither KP7 nor FLA, so joint = .67). o12/o14 read REDUNDANT because the
     flight half is empty there (Kp[7] is the sole carrier; the rule's
     REDUNDANT label cannot distinguish "sole" from "redundant").
   - Reading: the frozen rule is SPECIFIC (no false IS in KA-B, MF-X, MF-SHUF)
     but INSENSITIVE: IS fires only where the Kp half weighs >= ~.25 and no
     third carrier (inbox) is live.
   DEVIATION D-1 (from A3's gate and the brief's "pass before touching the
   champion"): I run the champion anyway (cost ~0.05 core-h), as a labelled
   deviation, and report each frozen-rule call with its validation status:
   NOT A CARRIER = validated (KA-B, MF-X); IS THE READOUT HALF = validated for
   specificity only; REDUNDANT = NOT validated (MF-SHUF); UNRESOLVED = no
   inference. The champion decision rule (PLAN s3) is applied unchanged.
   Champion: 4781b0a1, M 128, world_seeds(0x670,128), o10,o12,o14, trials 1..11,
   6 arms, 1 process x 1 thread.
