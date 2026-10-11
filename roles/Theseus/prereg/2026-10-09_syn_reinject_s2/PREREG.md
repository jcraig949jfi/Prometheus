# THESEUS-42 preregistration -- second seed for SYN re-injection (39)

Currency: 2026-10-09. Committed before either run.
Code: unchanged from 39 (run_v0 --inject, task_comp, pooled, inject_attr); hashes in CODE_HASHES.txt.

## Why

39 is SUPPORTED on one seed: INJ-S 85 vs INJ-M 72, p .019, RD .13 [.016, .241]. Both
previous headline effects shrank two to three times on a second seed (38). Before the re-use
result is quoted, it needs a second seed and a pooled estimate.

## Design (master seed 20261010; the same injection sets as 39)

Common: PYTHONHASHSEED=0 --quality task0 --master-seed 20261010 --g0-readers --cond-ops
--aligned-binding --ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5 --workers 4

| arm | inject file | tag |
|---|---|---|
| INJ-S | theseus/archive/inject_S_v0_2t0_2026-10-08.jsonl | v0_2t0_s3_injS_2026-10-09 |
| INJ-M | theseus/archive/inject_M_v0_2t0_2026-10-08.jsonl | v0_2t0_s3_injM_2026-10-09 |

N (descriptive): THESEUS-40 S3-TASK0 v0_2t0_s3_2026-10-09.

Commands:
- eval: python -m theseus.synth.task_comp --tag comp_task_syn_s3_2026-10-09
  --a v0_2t0_s3_injS_2026-10-09 --b v0_2t0_s3_injM_2026-10-09 --workers 4
- pooled: python -m theseus.synth.pooled with
  --pair theseus/runs/comp_task_syn_2026-10-09:v0_2t0_s2_injS_2026-10-09:v0_2t0_s2_injM_2026-10-09
  --pair theseus/runs/comp_task_syn_s3_2026-10-09:v0_2t0_s3_injS_2026-10-09:v0_2t0_s3_injM_2026-10-09

## Decision rules

Seed 20261010 (H-SYN-SOLVE-S3), as 39: GATE as 36. SUPPORTED iff one-sided Fisher p < .05;
NOT SUPPORTED iff the INJ-S share <= the INJ-M share; else INDETERMINATE.

Pooled (H-SYN-POOLED; this is the quotable result): SUPPORTED iff the one-sided CMH
p < .05 over the 2 strata AND the RD_MH 95% CI lower bound > 0. NOT SUPPORTED iff
RD_MH <= 0; else INDETERMINATE.

Descriptive, as 39 S3/S4: the in-run solver table, verbatim-copied essential rules, and
redundant-solver counts.

## Predictions

| id | prediction | p |
|---|---|---|
| Q1 | H-SYN-SOLVE-S3 SUPPORTED | 0.35 |
| Q2 | INJ-S share > INJ-M share on seed 3 (direction only) | 0.7 |
| Q3 | H-SYN-POOLED SUPPORTED | 0.55 |
| Q4 | SYN-arm solvers whose every essential part is a verbatim injected rule outnumber M-arm ones again | 0.7 |

## Compute

Two ecology runs (~25-45 min x 4 workers) + one eval (~40 min): ~6 CPU-hours (MWO R2 cap 16).
