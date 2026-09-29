# W-A LOG (echo interval of the M2 HOLD specimen)

Every attempt, including bugs and failed runs. Times are local (2026-09-27).

## A0 reading (no runs)
- Read brief, COMMON_RULES, engine._tick/_emit, lens, envs (HOLD builder),
  topology (ring offsets [-3,-2,-1,1,2,3]), physics, spikes s_m2/s_m2b/s_f,
  C1B_SUMMARY arms for M2 fresh champions, SYNTHESIS s2 (the "tuned two-stage
  echo" hypothesis), thread T-M2-2.
- Noted before any run: C1b arm shuffle_time (delay := U[1, LM-1]) did NOT
  hurt fresh1-3 (0.84/0.86/0.85 vs normal 0.82/0.87/0.86). So exact latency
  values are not what is tuned; the latency DISTRIBUTION's support is the
  candidate.

## A1 decompile.py (CPU, seconds)
- Decompiled all 4 genomes with engine field reduction. All four reduce to:
  actuator emits SENSE on comp c; every site relays IN_c (x scale) on c';
  S0 := IN_c' (overwritten every wake); EMIT always > 0. Scales: specimen 1,
  fresh1 >>4 (c=1, c'=0), fresh2 >>2, fresh3 1. No recirculation (c' is never
  relayed). Specimen also writes RVAL=-1 every wake to table index
  (-7168 mod 6)=2 = offset -1: w[2] 16 -> 0 in 16 wakes. That kills every
  hop-1 round trip (a->a-1 blocked; a+1->a blocked).
- Details in PLAN.md s2.

## A2 echo_model.py written (reduced particle model, no fitted parameters)
- First version hard-coded route index 2; generalized to (-7168) mod R
  before any prediction was computed (needed for the radius-2 condition).

## A3 predict_all.py (CPU, numpy, 26 min wall; slower than estimated)
- 50 (condition, champion) curves x 15 gaps x {sat, nosat}, 4000 worlds each.
- Calibration glance (NOT a test; S-M2b even gaps were known): model base
  curves match specimen and fresh1 within ~0.03 at every even gap; fresh2
  and fresh3 are measured ~0.05 lower at gap 4-6 and ~0.07 higher at gap 10,
  i.e. shifted later than the uniform-routing model. Likely their
  data-dependent routing writes (fresh3: a's w[offset -3] += 8 when SENSE>0)
  favour long hops. Not corrected (would be post-hoc); logged as expected
  misfit.
- sha256 frozen in PLAN s6.

## A4 engine sweeps started (run_engine.py, CPU 2 threads, background)
- ~85 s per (condition, champion) curve of 15 gaps. Base results (first 4
  curves) arrived; evaluation deferred to evaluate.py after all 50.
- cpu8 lease acquired token 6ace865c9e22 (ttl 75 min) to run a second
  2-thread process (impulse kernel, A5) alongside the sweep.

## A5 kernel_engine.py (CPU, ~1 min) -> out/kernel_engine.json
- Engine-measured normalized echo kernel (read wake - cue wake):
  specimen {8:.68, 10:.21, 12:.12}, model {8:.63, 10:.25, 12:.13}, TV .05 HOLDS
    (zero mass at RT 4 and 6 in the engine too: routing cut confirmed)
  fresh1 {4:.13, 6:.13, 8:.52, 10:.13, 12:.10}, model {.08,.17,.50,.17,.08}, TV .07 HOLDS
  fresh2 {4:.03, 6:.08, 8:.37, 10:.32, 12:.15, >12: .06}, TV .27 (expected contaminated)
  fresh3 {4:.07, 6:.07, 8:.41, 10:.28, 12:.16}, TV .20
- fresh2/3 carry echo mass shifted to RT 10-12 = hop-3 paths. That is the
  measured cause of their later-shifted base curves (A3 note): their routing
  writes bias the tables toward offset -3 (w[0]). Mechanism the same, kernel
  weights differ. Not fixed in the frozen model.
- cpu8 lease released (token 6ace865c9e22) after A5; sweep continues on 2 threads.

## A6 engine sweeps finished (3940 s wall, 50 curves x 15 gaps, out/engine.json)

## A7 evaluate.py -> out/evaluation.json
- Bug 1 (mine): second loop over modes counted the "_gold_sat" summary key
  as a condition (KeyError 'nosat'). Fixed by skipping "_" keys; no rule
  or threshold changed.
- Gold standard (frozen rule): 46/46 non-base curves FIT (MAE <= .07) and
  INTERVAL-HOLDS, for both the primary (sat) and secondary (nosat) model
  -> PREDICTS. Max MAE 0.058 (pipe:fresh3); median ~0.02.
- P-a HOLDS (amp_dist 0: chance at all gaps >= 13; upper edge unchanged at 11).
- P-b HOLDS 4/4 (acc 7 > 8 > 9): spec .97/.87/.80, f1 .97/.85/.75,
  f2 .93/.86/.82, f3 .90/.86/.83. The trained gap 8 is NOT the best gap.
- P-c HOLDS: specimen mean acc gaps 2-5 = .55 vs fresh .62-.68;
  plastic_route 0 lifts it to .68.
- P-e HOLDS for both: pipeline edit moves interval (6,11)->(8,12) specimen,
  (4,11)->(6,13) fresh3; peak 7 -> 9.
- P-f HOLDS: canon:specimen is IDENTICAL to base:4ab2ba01 at every gap
  (all 3 numbers); canon:uniform is identical to pr0:4ab2ba01 and pr0:fresh3
  and within .004 MAE of base:fresh1.
- Peak (argmax) disagreements exist where curves are bimodal (lb0, lb2,
  lh2, up1, up3 for fresh2/3); argmax was not a frozen criterion.

## A8 null_check.py (POST-HOC, labelled): discriminating power
- Null predictor "the champion's base curve, unchanged" passes the same
  rule on 12/44 non-base curves (the conditions where the interval should
  not move: pr0 for fresh, ad0, j2, ...). The model passes 44/44 of these.

## A9 REPORT.md
- The agent harness refused to create REPORT.md (subagent report-file
  policy). Not circumvented. The full report text was returned in the
  final message to Ananke for filing at workers/W-A/REPORT.md.
- No leases held at end (cpu8 released after A5; GPU never used).
