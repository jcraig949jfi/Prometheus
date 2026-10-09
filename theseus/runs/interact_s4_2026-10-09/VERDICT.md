# THESEUS-47 verdict: arm x redundancy interaction on generalisation, fresh seed (prereg roles/Theseus/prereg/2026-10-09_interaction/, acb9bda6c)

Runs: PYTHONHASHSEED=0, master seed 20261011, flags as 40, --workers 2 each:
- S4-TASK0 v0_2t0_s4_2026-10-09
- S4-NOLAW v0_2t0nl_s4_2026-10-09 (--no-law)

Eval: python -m theseus.synth.task_comp --tag comp_task_s4_law_2026-10-09 (gate inside).
Score: python -m theseus.synth.interact_score --tag interact_s4_2026-10-09 ... --workers 4
(SUMMARY.json, TABLE.jsonl; 135 solvers).

GATE: 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Primary: H-INTERACT (V8 k8)

| arm | redundant | one-point | RD (se) |
|---|---|---|---|
| law-on | 27/31 | 33/40 | +.046 (.085) |
| no-law | 6/19 | 11/45 | +.071 (.124) |

Difference -.025; Wald z -.17, one-sided p .57.
VERDICT: NOT SUPPORTED. The difference is <= 0, and the 46 pattern does not replicate.

## Secondary

S1 (V4 k20):

| arm | redundant | one-point | RD |
|---|---|---|---|
| law-on | 25/31 | 36/40 | -.094 |
| no-law | 9/19 | 26/45 | -.104 |

Interaction z .07. Not supported.

S2: law-on redundancy RD at V8 k8 is +.046 (Fisher p .42). Not supported.

S3 (37/40 on seed 4): S4-TASK0 71/100 vs S4-NOLAW 64/100 solvers, one-sided Fisher p .18.
Not supported on this seed. Pooled over 4 seeds this is descriptive: the 40 pooled verdict
stands on 3 seeds as preregistered. RD_MH .178 [.110, .245], CMH p 2.3e-8.

S4 (45 H-ALPHA on seed 4): among solvers, the share solving V8 k8 is law-on 60/71 (.85) vs
no-law 17/64 (.27), one-sided Fisher p 4.8e-12. SUPPORTED, larger than on seeds 1-3.
- At V4 k20: 61/71 vs 35/64, p 5.9e-5.

## Reading
- Law-built solvers' generalisation advantage replicates strongly on a fourth seed,
  especially on the alphabet axis (85% vs 27%).
- The candidate explanation from 46 does not replicate. On fresh data, redundancy predicts
  generalisation in neither arm, and there is no arm x redundancy interaction. The
  per-arm split in 46 was a post-hoc pattern of the kind this campaign has repeatedly seen
  shrink.
- What generalises is a property of solvers from law-bearing ecologies. It is carried neither
  by a single essential law (45 H-LAWESS) nor by redundancy (47).
- The next candidate is the form of the store/release implementation itself, for example a
  graded k-ary coupling vs a thresholded relay. That needs its own preregistered test.

46's reading is annotated.

## Predictions

| id | prediction | outcome |
|---|---|---|
| I1 | H-INTERACT SUPPORTED, p .4 | did not occur |
| I2 | interaction direction > 0 | WRONG (-.025): ledger |
| I3 | S3 laws > no-law on seed 4 | WRONG (p .18): ledger |
| I4 | S4 law-on solvers generalise to V8 k8 more often | RIGHT (p 5e-12) |
