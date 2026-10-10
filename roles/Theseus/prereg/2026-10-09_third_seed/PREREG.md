# THESEUS-40 preregistration -- third master seed for 36/37 and a pooled 3-seed size

Currency: 2026-10-09. Committed before any of the three runs.
Code: theseus/synth/pooled.py (new), task_comp.py, run_v0.py; blob hashes in CODE_HASHES.txt.

## Why

Both headline effects shrank on the second seed: selection went from +32 to +15 points and
laws from +39 to +12. The 37-S2 test was just under the threshold (p .041). Two seeds cannot
separate a real size from a lucky first seed. A third seed and a pooled stratified estimate
give the size that may be quoted. Seeds 1-2 pooled now (computed with pooled.py while
writing this prereg, before any seed-3 run): selection RD_MH .235 [.139, .331], laws
RD_MH .255 [.156, .354].

## Design (master seed 20261010; otherwise identical to 38)

Common flags: PYTHONHASHSEED=0 --master-seed 20261010 --g0-readers --cond-ops --aligned-binding
--ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3 --elite-protect-k 150
--seed-select 1.5 --workers 4

| arm | flags | tag |
|---|---|---|
| S3-TASK0 | --quality task0 | v0_2t0_s3_2026-10-09 |
| S3-TASK0-NOLAW | --quality task0 --no-law | v0_2t0nl_s3_2026-10-09 |
| S3-REP | --quality rep | v0_2tr_s3_2026-10-09 |

Evals (task_comp, gate inside):
- comp_task_s3_sel_2026-10-09: --a S3-TASK0 --b S3-REP
- comp_task_s3_law_2026-10-09: --a S3-TASK0 --b S3-TASK0-NOLAW

Pooled: python -m theseus.synth.pooled with the three seed strata (1: comp_task_2026-10-08 /
comp_task_law_2026-10-08; 2: the s2 dirs; 3: the s3 dirs).

## Decision rules

Per seed 3 (as 36/37/38): the gate as 36. SUPPORTED iff one-sided Fisher p < .05; NOT
SUPPORTED iff a share <= b share; else INDETERMINATE.

Pooled, the quotable result:
- H-SEL-POOLED (task0 vs rep) and H-LAW-POOLED (task0 vs no-law) are each SUPPORTED iff the
  one-sided CMH p < .01 over the 3 strata AND the RD_MH 95% CI lower bound > 0. NOT
  SUPPORTED iff RD_MH <= 0; else INDETERMINATE.
- The size quoted from here on is RD_MH with its 95% CI, never a single seed's difference.

Heterogeneity: report the per-seed RDs with Newcombe CIs. If the seed-1 RD lies outside the
pooled CI of seeds 2-3, record it in the ledger as a single-seed overestimate.

## Predictions

| id | prediction | p |
|---|---|---|
| T1 | S3 H-SEL SUPPORTED | 0.55 |
| T2 | S3 H-LAW SUPPORTED | 0.5 |
| T3 | H-SEL-POOLED SUPPORTED | 0.85 |
| T4 | H-LAW-POOLED SUPPORTED | 0.8 |
| T5 | pooled selection RD_MH in [.10, .25] | 0.6 |
| T6 | the seed-1 selection RD (.32) lies above the seeds 2-3 pooled CI upper bound (single-seed overestimate) | 0.5 |

## Compute

Three ecology runs (~50 min x 4 workers) + two evals (~40 min each): ~12 CPU-hours. That is
within the MWO R2 per-item cap of 16. Day-2 total including 39 is ~22 of the 48/day cap.
