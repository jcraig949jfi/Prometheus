# PREREG v0 -- amendment 1 (committed before the rerun)

Currency: 2026-09-30T07:15Z.

## What happened

The first execution of the frozen v0 procedure (075e5fc21, 16 workers,
launched ~06:30Z) was STOPPED by this seat at 07:03Z during epoch 3,
generation 34 of 40, before Pass D. Cause: generation wall time went
0.02-2.6 s (epoch 0), 8-12 s (epoch 1), 13-22 s (epoch 2), then 325-540 s
(epoch 3, 32 lenses in the ecology). CPU consumed by the run at the stop:
13.0 core-hours (sum over its 19 processes), against the PREREG's
estimate of < 1 and MWO-0004 R2's 16 core-hours per item. Finishing
would have exceeded the envelope, so the run was stopped.

Diagnosis (measured after the stop): numpy uses scipy-openblas
(MAX_THREADS=24). Sixteen workers each running multithreaded BLAS on 28
logical CPUs oversubscribe once the organism matrices reach ~100
features; a single-process evaluation at the epoch-3 ecology costs
0.15-0.23 s, far below what the 330 s generations imply. This is a
resource-configuration defect of the instrument, not a property of the
procedure.

## What changes

- tyche/run_v0.py sets OMP/OPENBLAS/MKL_NUM_THREADS=1 before numpy loads
  (inherited by every worker).
- A compute guard: evolution stops early if wall x workers exceeds 2.5
  core-hours (an upper bound on its CPU). If it trips, the current
  epoch's admission step and Pass D still run, the stop is written to
  GENERATIONS.jsonl and DONE.json, and the report states the truncation.
- tyche/report.py skips that marker row.

Nothing else changes: worlds, seeds, population, operators, selection,
admission gates, Pass D, hypotheses and verdict code are as frozen at
075e5fc21. Expected cost of the rerun: about 3 core-hours, bringing this
item to about 16 core-hours in total.

## What I saw from the stopped attempt

Only: admissions per epoch 11, 10, 11 (164 admission tests), generation
timings, and the 32 admitted genomes' instruction lists and output
magnitudes while profiling (used for the timing diagnosis on P1_xor2).
I did not look at which worlds the admissions were on, at any gain, or
at any Pass A number. Its rows are kept, unscored, at
tyche/runs/v0_2026-09-30_ABORTED/ and are not evidence for H1-H6.

## Calibration

The compute estimate was wrong by more than an order of magnitude
because the global ecology's growth multiplies every organism fit and
the pilot stopped at 2 epochs; recorded in roles/Tyche/calibration/LEDGER.md.
