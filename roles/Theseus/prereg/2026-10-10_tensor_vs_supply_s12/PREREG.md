# THESEUS-52 preregistration -- tensor vs supply on seeds 1 and 2; pooled 4-seed verdict

Currency: 2026-10-10. Committed before either run.
Code: unchanged from 51 (collide random_law_gains, run_v0, task_comp, pooled, rg_release);
hashes in CODE_HASHES.txt.

## Why

51 (536a30ddb), 2 seeds:
- H-TENSOR NOT SUPPORTED (RD -.005)
- H-SUPPLY SUPPORTED (RD .105 [.012, .198])

That makes the concept tensor's learned gains doing no detectable work in the campaign's main
capability result. That is the charter's central object, so it needs more than 2 seeds.
Seeds 1 and 2 already have LAW and NOLAW runs (36/37/38).

## Design

RANDLAW runs: PYTHONHASHSEED=0 --quality task0 --random-law-gains --g0-readers --cond-ops
--aligned-binding --ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5 --workers 2

| seed | RANDLAW (new) | LAW (existing) | NOLAW (existing) |
|---|---|---|---|
| 1, default (20260930) | v0_2t0rg_2026-10-10 | v0_2t0_2026-10-08 | v0_2t0nl_2026-10-08 |
| 2, --master-seed 20261009 | v0_2t0rg_s2_2026-10-10 | v0_2t0_s2_2026-10-08 | v0_2t0nl_s2_2026-10-08 |

Evals: task_comp comp_task_s{1,2}_rg_2026-10-10 --a RANDLAW --b NOLAW (gate inside). The LAW
and NOLAW J/KO rows (deterministic) are copied from comp_task_law_2026-10-08 and
comp_task_s2_law_2026-10-08 first.

## Primaries (one-sided CMH over the 4 strata, seeds 1-4, with 51's rows; alpha .025 each)

| hypothesis | contrast |
|---|---|
| H-TENSOR-4 | LAW > RANDLAW |
| H-SUPPLY-4 | RANDLAW > NOLAW |

Each is SUPPORTED iff p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED iff RD_MH <= 0;
else INDETERMINATE.

Secondary (descriptive): seeds 1-2 alone; the V8 k8 release among RANDLAW solvers (rg_release)
vs LAW/NOLAW (48 rows).

## Predictions

| id | prediction | p |
|---|---|---|
| U1 | H-TENSOR-4 SUPPORTED | 0.25 |
| U2 | H-SUPPLY-4 SUPPORTED | 0.75 |
| U3 | the seed-1 RANDLAW solver share is >= 80 (seed 1 LAW was 91) | 0.5 |

## Compute

Two ecology runs (~45-60 min x 2 workers, in parallel) + two evals + V8 release scoring:
~9 CPU-hours. Day-3 total so far ~10 of 48.
