# THESEUS-47 preregistration -- arm x redundancy interaction on generalisation, fresh seed

Currency: 2026-10-09. Committed before either run.
Code: theseus/synth/interact_score.py (new), generalise.py (job), task_comp.py, run_v0.py;
hashes in CODE_HASHES.txt.

## Why

46 (post hoc per-arm split, 5340b85cb): among selected-task solvers, redundant solvers (no
single essential rule) generalise better than one-point solvers in law-bearing ecologies,
and not in no-law ecologies.

| arm | V8 k8 RD | V4 k20 RD |
|---|---|---|
| law-on | +.130 | +.154 |
| no-law | -.073 | -.106 |

The ledger rule (2026-10-09, D1-D3): when arms differ in kind, preregister the interaction.
This is that test, on data not yet generated.

## Design (master seed 20261011; flags as 40)

Common: PYTHONHASHSEED=0 --quality task0 --master-seed 20261011 --g0-readers --cond-ops
--aligned-binding --ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5 --workers 2

| arm | flags | tag |
|---|---|---|
| S4-TASK0 | (common flags) | v0_2t0_s4_2026-10-09 |
| S4-NOLAW | + --no-law | v0_2t0nl_s4_2026-10-09 |

Commands:
- eval: python -m theseus.synth.task_comp --tag comp_task_s4_law_2026-10-09
  --a v0_2t0_s4_2026-10-09 --b v0_2t0nl_s4_2026-10-09 (gate inside; J + knockouts)
- score: python -m theseus.synth.interact_score --tag interact_s4_2026-10-09
  --evaldir theseus/runs/comp_task_s4_law_2026-10-09 --law v0_2t0_s4_2026-10-09
  --nolaw v0_2t0nl_s4_2026-10-09

## Primary

H-INTERACT: for solving V8 k8 among selected-task solvers,
(RD redundant-minus-one-point in law-on) - (the same RD in no-law) > 0.
Wald z, one-sided. SUPPORTED iff p < .05; NOT SUPPORTED iff the difference <= 0; else
INDETERMINATE. GATE as 36 (from the eval) must pass.

## Secondary

- S1 the same interaction at V4 k20.
- S2 the law-on redundancy RD > 0 at V8 k8, one-sided Fisher.
- S3 replication of 37/40 on seed 4: S4-TASK0 solver share > S4-NOLAW, one-sided Fisher.
- S4 replication of 45 H-ALPHA on seed 4: among solvers, law-on solve V8 k8 more often than
  no-law, one-sided Fisher.

## Predictions

| id | prediction | p |
|---|---|---|
| I1 | H-INTERACT SUPPORTED | 0.4 (post hoc pattern, winner's curse expected) |
| I2 | the interaction difference > 0 (direction) | 0.65 |
| I3 | S3 laws > no-law supported | 0.55 |
| I4 | S4 law-on solvers generalise to V8 k8 more often | 0.6 |

## Compute

Two ecology runs (~30 min x 2 workers each, in parallel) + eval (~45 min) + scoring
(~150 solvers x 6 scorings, ~1 CPU-h): ~8 CPU-hours (MWO R2 cap 16).
