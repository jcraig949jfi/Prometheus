# THESEUS-41 preregistration -- SYN injection WITHOUT task selection

Currency: 2026-10-09. Committed before either run.
Code: unchanged (run_v0 --inject, task_comp, inject_attr); hashes in CODE_HASHES.txt.

## Why

39 found that re-injected SYN concepts raise deep solver share over matched non-solving
matter under TASK selection (85 vs 72, one seed; second seed in 42). That leaves open whether
the matter is useful on its own, or only when a task-selecting ecology keeps and recombines
it. Under reproducibility selection the task is invisible to the search. Any S > M
difference would then come from inheritance alone (children copying SYN rules), not from
selection keeping solvers.

## Design (master seed 20261009; flags as 38 S2-REP plus --inject)

Common: PYTHONHASHSEED=0 --quality rep --master-seed 20261009 --g0-readers --cond-ops
--aligned-binding --ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5

| arm | inject file | tag |
|---|---|---|
| REP-S | theseus/archive/inject_S_v0_2t0_2026-10-08.jsonl | v0_2tr_s2_injS_2026-10-09 |
| REP-M | theseus/archive/inject_M_v0_2t0_2026-10-08.jsonl | v0_2tr_s2_injM_2026-10-09 |

N (descriptive): 38 S2-REP v0_2tr_s2_2026-10-08, 63/100 solvers.

Eval: python -m theseus.synth.task_comp --tag comp_task_syn_rep_2026-10-09
--a v0_2tr_s2_injS_2026-10-09 --b v0_2tr_s2_injM_2026-10-09.

## Decision rule

Primary H-SYN-REP: D solver share REP-S > REP-M. Gate as 36. SUPPORTED iff one-sided
Fisher p < .05; NOT SUPPORTED iff the REP-S share <= the REP-M share; else INDETERMINATE.

## Descriptive
- 39-style attribution:
  - verbatim injected essential rules (inject_attr)
  - redundant-solver counts
  - the in-run injected-ancestry share of D children; under rep quality the run has no task
    J, so this is computed from entity ancestry, not from collisions.task_J
- The REP-S minus REP-M RD, set beside 39's task0 RD .13.

## Predictions

| id | prediction | p |
|---|---|---|
| U1 | REP-S share > REP-M share (direction) | 0.65 |
| U2 | H-SYN-REP SUPPORTED | 0.4 |
| U3 | the REP RD is smaller than the task0 RD of 39 (.13) | 0.55 |
| U4 | REP-S has more solvers whose every essential part is a verbatim SYN rule than REP-M | 0.7 |

## Compute

Two ecology runs (~25-45 min) + one eval (~40 min): ~6 CPU-hours (MWO R2 cap 16).
Day-2 running total: ~30 of 48.
