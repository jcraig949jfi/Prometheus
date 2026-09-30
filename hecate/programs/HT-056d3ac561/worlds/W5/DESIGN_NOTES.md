# HT-056d3ac561 / W5 -- design notes (Pass 3 v2 generator)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.
Layer: implemented candidate (controls only). Nothing here is evidence about M3.

## What it tests

M3 (covariance reopening), with M8's stride relation as the oracle-free
alarm and lens L7 (recovery latency at matched false alarms) plus L1 (NIS as
the baseline every MR claim must beat). A correctly specified but
overconfident filter (gain ~0.01) meets a sparse jump (2 of 8 components,
J = 1.5). Question: does reopening only the components the stride MR flags
recover faster than isotropic reopening on a windowed-NIS alarm, with both
calibrated to 5% pre-change false alarms on a separate calibration seed?

All arms share one reopening action (P_jj += 1.0); they differ only in when
and which components. So latency differences are attributable to the alarm,
not to the size of the reopening.

## Control values (1000 pooled runs, 5 seeds)

| arm | median latency | pre-change FA |
|---|---|---|
| POSITIVE_CONTROL (oracle t_c, true components) | 2 | 0.00 |
| REFERENCE_NIS (spec control) | 18 | 0.043 |
| NULL_TWIN (random time, random 2 components) | 76 | 0.473 |
| NO_REOPEN (collapsed filter) | 78 | 0.00 |

S1 (<= 12), S2 (FA <= 0.10), S3 (ratio to NIS <= 0.60, i.e. <= 10.8 steps):
all attainable by the oracle and failed by the twin; the cheat passes all
three. Frozen.

## How it avoids the earlier failures

- W1 (INSTRUMENT_FAIL): the perturbation was invisible even to the oracle
  (oracle-RMSE AUC ~0.5). Here the oracle's effect was measured before
  freezing: latency 2 vs 78 for the collapsed filter.
- W1: the null twin's statistic blew up (mean D ~23624) because it compared
  mismatched times under one normalization. Here the twin is an action twin
  (same action count/size/sparsity), not a re-normalized statistic.
- W4: the positive control could not satisfy the spec's own clause. Here
  every clause was evaluated on the positive-control rows before freezing.
- W4: "k <= 3" was ambiguous (per cell vs pooled) and decided the class.
  Here every statistic is explicitly pooled over the 1000 runs, one number
  per clause.
- NIS is a real competitor here (18 steps, well above the oracle's 2), so
  S3 can fail. It is expected to be hard: stride disagreement may carry no
  information beyond NIS (the alternative explanation). That is the
  cleanest failure this world offers.

## Ambiguities resolved

1. "Matched false-alarm rate": both alarms calibrated to the 0.95 quantile
   of their run-level max statistic over [50, 300) on calibration seed 999
   (1000 no-jump runs, alarms off). S2 checks it held on evaluation seeds.
2. "Recovery": every changed component within 0.5 J of truth for 10
   consecutive steps; latency counted from t_c; cap 290.
3. Stride-2 filter under reopening: reopened on the same components at the
   same step as the stride-1 filter; normalization floor 1e-8 on P2 - P1.
4. CONTROL is REFERENCE_NIS; it is computed in controls.py only because S3
   is a ratio to it. The implementer reruns it in the same code path; its
   median must reproduce 18.0 or the reading is INSTRUMENT_FAIL.
5. NO_REOPEN is a diagnostic reference for F3 and the stupid explanations,
   not a clause arm.
6. Sparse attribution (the Sparse Coding role) is per-component alarm and
   reopening; its cost to unchanged components is recorded (secondary MSE)
   but is not a clause, because the random twin also leaves unchanged
   components mostly untouched and so could not be discriminating.

CPU: < 0.1 core-min per control run.
