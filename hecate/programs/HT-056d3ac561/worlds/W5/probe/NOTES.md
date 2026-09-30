# HT-056d3ac561 / W5 -- probe round 3 implementation notes

Prompt: hecate/programs/_prompts/probe_impl_v3.md (sha256 a34a8c61...1685),
{TID} = HT-056d3ac561, {W} = W5. Written BEFORE any run.
Read: the two PREREGs, spec.json, controls.py, ATTAINABILITY.json,
DESIGN_NOTES.md (and, incidentally, attain.py / revisions.json in the same
world directory, to see how the frozen clause values were computed).
Nothing frozen is edited; everything is written in probe/.

## Arms (world.py)

world.py IMPORTS controls.py and uses its constants, make_data,
run_filter, latency, fa_flag, mse_unchanged, oracle_fn, twin_fn, nis_fn
and calibrate_nis unchanged. controls.main() is NOT called (it would
overwrite the frozen control_rows.jsonl); its per-seed loop is reproduced
line for line, writing to probe/rows.jsonl instead.

Per evaluation seed s in [0,1,2,3,4] (200 runs each, the spec's seeds):
  rng = default_rng(s); x, z, chg, x0 = make_data(rng, 200)   (same as controls)
  POSITIVE_CONTROL  run_filter(oracle_fn(chg))
  NULL_TWIN         run_filter(twin_fn(default_rng(10000+s), 200))
  REFERENCE_NIS     run_filter(nis_fn(h_NIS))        -- the spec's CONTROL arm
  NO_REOPEN         run_filter(no-op)                -- F3 reference
  CHEAT             latencies 0, fa 0 (as controls.py)
  TREATMENT         run_filter(mr_fn(...)) on the same x, z, x0
The order of RNG draws per seed is identical to controls.py, so the
control arms must reproduce the frozen rows exactly.

h_NIS = controls.calibrate_nis() (seed 999, 1000 no-jump runs).
h_MR  calibrated on the SAME calibration data (make_data(default_rng(999),
1000, jump=False)), treatment statistic with alarms disabled: 0.95 quantile
over runs of max over components and even t in [50, 300) of S_j.

## Treatment (M3 reopening, M8 stride relation as alarm)

Implemented as a reopen_fn passed to controls.run_filter (same code path as
every other arm). It carries the stride-2 filter in a closure:
  - stride-2 filter: initial estimate x0 (same as stride-1), P2 = P_ss at t=0;
    updates only at even t >= 2 with P2m = P2 + 2Q, same R, measurement z_t.
  - at even t: tentative stride-1 update (from run_filter's e, S) and
    tentative stride-2 update; d_j = xhat1_j - xhat2_j (both posterior at t),
    z_j = d_j / sqrt(max(P2_jj - P1_jj, 1e-8)); z_j^2 appended to component
    j's window of the last 10 even steps; S_j = window sum.
  - alarm on j iff window full (10 entries since start/last clear) and
    S_j > h_MR and t >= 50. On alarm the stride-2 update at t is redone
    with P2m_jj += RHO on alarmed components, the mask is returned so that
    run_filter adds RHO to the stride-1 Pm_jj before its update at t, and
    the alarmed components' windows are cleared.
  - odd t: stride-2 idle, no statistic, no alarm.

## Ambiguities and readings chosen (no threshold changed)

A1 Reopen timing. The spec says reopening happens "before the update at
   the chosen step" and DESIGN_NOTES A3 says both filters are reopened "at
   the same step". Reading: the alarm at even t is computed from tentative
   posterior updates at t (z_t is available, so this is causal); if it
   fires, both filters' updates at t are performed with the reopened
   variance. The reopening step recorded for the false-alarm flag is t.
A2 Window fullness. Mirroring controls.nis_fn (the frozen control's code
   path), an alarm requires a full window (10 even-step entries since the
   last clear). At t >= 50 without a prior alarm the window is always full
   (entries from t = 2), so this only matters after a clear.
A3 Stride-2 initial estimate: x0 (the stride-1 initial estimate), P = P_ss,
   per the spec ("same initial P_ss"). Before t = 2 it has made no update.
A4 Latency, false-alarm flag, secondary MSE: controls.latency / fa_flag /
   mse_unchanged unchanged (band 0.5 J, 10 consecutive steps, cap 290;
   FA = any reopening at a step in [50, 300)).
A5 The CONTROL arm is REFERENCE_NIS. S3 and F1 use the REFERENCE_NIS rows
   rerun here (not the frozen numbers), which must reproduce 18.0.

## Evaluation (evaluate.py)

1. Recompute S1-S3 on the rerun POSITIVE_CONTROL, NULL_TWIN, CHEAT arms
   (S3 ratio to rerun REFERENCE_NIS); compare attainable / discriminating
   / cheat-detected status with ATTAINABILITY.json; any status difference
   -> INSTRUMENT_FAIL (reproducibility), stop. Value differences and the
   REFERENCE_NIS = 18.0 reproduction are also checked (the frozen S3 text
   requires it) and a mismatch there is also INSTRUMENT_FAIL.
2. positive_control_detected = POSITIVE meets S1-S3; cheat_detected = CHEAT
   meets S1-S3; either false -> INSTRUMENT_FAIL.
3. null_twin_meets_success (all of S1-S3) -> CONFOUNDED.
4. TREATMENT meets all of S1-S3 and none of F1-F3 -> SIGNAL; otherwise NULL.

## Seeds

Evaluation 0-4 (200 runs each, 1000 pooled); calibration 999 (1000 runs);
null-twin draws 10000 + seed. BLAS threads pinned to 1.
Budget: <= 10 CPU core-minutes; expected < 1.

## Post-run diagnostic (added after the single run; no parameter changed, no rerun of world.py)

h_MR = 114.3 (h_NIS = 223.97, reproduces frozen). A chi2_10 window would give
a far lower threshold, so the normalization was checked for a bug on 300
no-jump calibration-seed runs (read-only, nothing written): mean z_j^2 = 0.976
(normalization by P2 - P1 is correct), but lag-1 correlation of z_j^2 across
even steps = 0.97. Both filters have gain ~0.01-0.02, so their disagreement
moves on a ~100-step time scale; the 10-even-step window sum is ~10 z^2 of
one draw, its null tail is heavy, and the calibrated threshold is high. After
the jump the MR alarm fires in 79.8% of runs with median delay 82 steps,
so the treatment barely beats never reopening (75 vs 78). This is a property
of the frozen statistic, not an implementation defect.
