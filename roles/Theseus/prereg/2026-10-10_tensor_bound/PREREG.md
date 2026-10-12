# THESEUS-53 preregistration -- bound the concept tensor's contribution (seeds 5 and 6)

Currency: 2026-10-10. Committed before any of the four runs.
Code: unchanged (collide random_law_gains, run_v0, task_comp, pooled, rg_release); hashes in
CODE_HASHES.txt.

## Why

52 (79649337f), 4 seeds:
- H-TENSOR-4 INDETERMINATE: RD .035 [-.023, .093]
- H-SUPPLY-4 SUPPORTED: RD .143 [.075, .210]

Whether the concept tensor's learned content contributes a small effect or none is the
charter's most important open number. Two more seeds narrow it.

## Design (flags as 40; --workers 2; PYTHONHASHSEED=0; --quality task0)

| seed | LAW (default gains) | RANDLAW (--random-law-gains) |
|---|---|---|
| 20261012 | v0_2t0_s5_2026-10-10 | v0_2t0rg_s5_2026-10-10 |
| 20261013 | v0_2t0_s6_2026-10-10 | v0_2t0rg_s6_2026-10-10 |

Evals: task_comp --tag comp_task_s{5,6}_tensor_2026-10-10 --a LAW --b RANDLAW (gate inside).

## Primary

H-TENSOR-6: LAW > RANDLAW in D solver share. One-sided CMH over seeds 1-6 (52's four
strata plus these two). SUPPORTED iff p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED
iff RD_MH <= 0; else INDETERMINATE.

BOUND (preregistered statement rule): if the 6-seed RD_MH 95% CI upper bound is < .10, the
packet states "the concept tensor's content contributes less than 10 points of deep-solver
share (95% CI)". Otherwise no bound is stated.

Secondary: seeds 5-6 alone; generalisation (V8 k8 release among solvers, rg_release), LAW vs
RANDLAW over 6 seeds, descriptive.

## Predictions

| id | prediction | p |
|---|---|---|
| V1 | H-TENSOR-6 SUPPORTED | 0.2 |
| V2 | the BOUND is stated (6-seed CI upper < .10) | 0.55 |
| V3 | seeds 5-6 RD (LAW - RANDLAW) <= .03 | 0.55 |

## Compute

Four ecology runs (~50 min x 2 workers, two at a time) + two evals + release scoring:
~14 CPU-hours. Day-3 total: ~28 + 14 = ~42 of 48.
