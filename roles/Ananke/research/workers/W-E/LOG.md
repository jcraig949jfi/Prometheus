# W-E LOG  T-RET-1

Attempt 0 (2026-09-27): read brief, COMMON_RULES, lens.py, engine.py, envs.py,
c1b_run.py, s_ct.json, s_m2.json; wrote PLAN.md + Addendum A before any run.

Attempt 1 (smoke, controls, nperm 2000, CPU 2 threads, 78 s): ret_census.py --controls.
  C-NEG hold_latch: guards G1/G2/G3/G5 pass; all pairs merge by end of trial k+1
  (0% by end of trial k, 100% by k+1); decoders 1.0 at j=0, exactly 0.5 at j>=1;
  EFFECTIVE 0 everywhere -> FORGETS, as predicted.
  C-POS integrator: never merges; paired decoder 1.0 at every lag (p = min);
  single decoder 1.0 at j=0 (latch), then 0.59-0.64 at j=1..6 (p 0.001-0.008):
  as preregistered, the primary single-world decoder sees superposed retention
  only weakly; under Holm over 112 tests (needs p < 8.9e-5) such a champion
  would NOT count as RR. Calibration fact, recorded, rule unchanged.
  Outputs renamed out/smoke_*.json.

Attempt 2 (launch): calib, controls (nperm 20000), census (16 specimens, nperm 20000)
  started as 3 background CPU processes x 2 threads. That is > 2 threads, so
  acquired lease cpu8 token 112e2591aa63 (ttl 60 min) right after launch (seconds).

Attempt 3 (full run, nperm 20000): calib (200 noise reps, nperm 2000): single
  p<.05 in 5.0%, paired 3.0%; p<.01 0.5% / 0.0% -> G6 PASS. Controls at 20000
  perms reproduce the smoke run. Census: 16/16 specimens, all guards G1 G2 G3 G5
  PASS (swap identity exact in every world), total ~12 min wall. cpu8 lease
  released (posted 755).
  Metric defect found on reading: 'merged_before_ro' counts ANY equal tick in
  [cue onset, ro_k), which includes ticks before the twins first diverge (sync
  update_period 2: a cue landing on a sleeping tick changes no state). It is
  NOT a merge-before-query measure; ignored in the report. MERGE TIME itself
  (first equal tick >= ro_k, G2 no re-divergence) is unaffected.

Attempt 4 (exploratory Addendum B): first launch crashed (numpy 2 solve needs a
  trailing [...,None] rhs); fixed and relaunched.
  Relaunched explore_hist.py ran 18/18 (16 specimens + 2 controls), ~5 min.
  D_f7e62fe3 w_sum A 0.97-0.88 at j=1..6, Holm adj p 0.0056 (post-hoc family of
  112); C-POS 0.67-0.80; others chance at j>=2. out/explore_hist*.json.

Attempt 5 (descriptive probe_trace.py): persisting twin differences at end of
  trial k+1 and k+6 are FROZEN single-element scars (identical value sets j=1 vs
  j=6): D_f7e62fe3 w 4 elems 32/32 signed; M2_fresh3 w 1 elem +-8 32/32 signed;
  D_0ad7dc00 Kp 1 elem ~216 22/22 signed; D_6a47bd68 S 1 elem 25/25 signed.

Summary (summarize.py -> out/summary.json): preregistered decision NO
  (min Holm single p at j>=2 = 0.149). Labels: 7 FORGETS, 5 DIVERGES-UNREC (4
  with paired Holm-significant signed trace), 2 MIXED (slow merge), 2 INTERFERES
  (M2 fresh2/3, unsigned). REPORT.md write was REFUSED by the harness; the full report is in W-E's final message to Ananke. No git operations performed.
