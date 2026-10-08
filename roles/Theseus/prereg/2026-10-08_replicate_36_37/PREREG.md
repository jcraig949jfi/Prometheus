# THESEUS-38 preregistration -- fresh-seed replication of 36 (task selection) and 37 (laws needed)

Currency: 2026-10-08. Committed before any of the three runs.

## Why

36 (47498bbe0) and 37 (5ceae43b4) are the campaign's strongest results and both rest on one
master seed (20260930): task selection raises deep solvers of the composition-necessary task
59 -> 91/100, and removing the collision-generated laws drops them to 52/100. Single-seed
results shrank before (35); replicate before building on them.

## Design (master seed 20261009, otherwise identical to 36/37)

Common flags: PYTHONHASHSEED=0 --master-seed 20261009 --g0-readers --cond-ops --aligned-binding
--ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3 --elite-protect-k 150
--seed-select 1.5 --workers 4
  S2-TASK0      --quality task0           tag v0_2t0_s2_2026-10-08
  S2-TASK0-NOLAW --quality task0 --no-law  tag v0_2t0nl_s2_2026-10-08
  S2-REP        --quality rep             tag v0_2tr_s2_2026-10-08
Evals (task_comp, gate inside):
  H-SEL-SOLVE-S2:  --a v0_2t0_s2 --b v0_2tr_s2   (tag comp_task_s2_sel_2026-10-08)
  H-LAW-NEEDED-S2: --a v0_2t0_s2 --b v0_2t0nl_s2 (tag comp_task_s2_law_2026-10-08)

## Decision rule (each, as in 36/37)

GATE as 36. SUPPORTED iff one-sided Fisher p < .05 for (a) solver share > (b); NOT SUPPORTED
iff (a) share <= (b) share; else INDETERMINATE. The pair is REPLICATED iff both are SUPPORTED.

## Predictions

M1 H-SEL-SOLVE-S2 SUPPORTED.       p = 0.75
M2 H-LAW-NEEDED-S2 SUPPORTED.      p = 0.7
M3 both SUPPORTED (replicated).    p = 0.55

Compute: three ecology-only runs with task0/rep quality (~45 min each, 4 workers) + two evals
(~40 min each, checkpointed); ~9 CPU-hours (MWO R2 per-item cap 16).
