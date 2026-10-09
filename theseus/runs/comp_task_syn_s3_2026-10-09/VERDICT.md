# THESEUS-42 verdict: second seed for SYN re-injection (prereg roles/Theseus/prereg/2026-10-09_syn_reinject_s2/, 12b9b0076)

Runs: PYTHONHASHSEED=0, base seed 20261010, flags as THESEUS-40 S3-TASK0, run with
--workers 2 each, side by side.

| arm | tag | injected | viable |
|---|---|---|---|
| INJ-S | v0_2t0_s3_injS_2026-10-09 | inject_S (20 SYN) | 20/20 |
| INJ-M | v0_2t0_s3_injM_2026-10-09 | inject_M (20 matched non-solvers) | 20/20 |

Eval: python -m theseus.synth.task_comp --tag comp_task_syn_s3_2026-10-09
--a v0_2t0_s3_injS_2026-10-09 --b v0_2t0_s3_injM_2026-10-09 --workers 4.

GATE: 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Seed 3: H-SYN-SOLVE-S3
D solvers (J >= .6), 100 viable DEEP+VERY_DEEP children per run:

| run | solvers | mean J |
|---|---|---|
| INJ-S | 79/100 | .821 |
| INJ-M | 74/100 | .780 |
| N (S3-TASK0, descriptive) | 75/100 | .795 |

INJ-S vs INJ-M: one-sided Fisher p .252; RD .05 [-.068, .166].
VERDICT: INDETERMINATE. The direction is positive; the seed alone does not establish it.

## Pooled over 2 seeds: H-SYN-POOLED (the quotable result)

| seed | INJ-S | INJ-M | RD [95% CI] |
|---|---|---|---|
| 20261009 (39) | 85 | 72 | .13 [.016, .241] |
| 20261010 (42) | 79 | 74 | .05 [-.068, .166] |

CMH z 2.15, one-sided p .0158; RD_MH .090 [.007, .173].
VERDICT: SUPPORTED, narrowly: the CI lower bound is .007. Re-injected SYN concepts raise deep
solver share over matched, same-lineage, non-solving deep matter by about 9 points (CI
0.7-17), pooled over 2 seeds.

As with every effect in this campaign, the first seed's size (13) halved on the second (5).
This one is now close to the floor of detectability at n = 100 per arm.

## Descriptive (seed 3)

In-run (200/200 episodes):

| run | D children | solvers | first solver gen | solvers with an injected ancestor |
|---|---|---|---|---|
| INJ-S | 381 | 297 | 1 | all |
| INJ-M | 391 | 282 | 1 | all |

Essential-rule counts 0/1/2/4:

| run | 0 | 1 | 2 | 4 |
|---|---|---|---|---|
| INJ-S | 42 | 24 | 11 | 2 |
| INJ-M | 37 | 25 | 12 | 0 |

Redundant solvers (no single essential rule): 42 vs 37, as in 39 (47 vs 37).

Verbatim injected essential rules (inject_attr):

| run | copied | of which laws | solvers with any essential copy | all essential parts copied |
|---|---|---|---|---|
| INJ-S | 18/54 | 13 | 15/37 | 11 |
| INJ-M | 17/49 | 14 | 13/37 | 12 |

Essential-rule provenance:
- INJ-S: law 37, mutation edit 12, G0 5
- INJ-M: law 41, mutation edit 4, lens 3, G0 1

## Correction to the 39 reading (annotation, not an edit of 39's verdict)

39 read the SYN advantage partly as "inherited working parts": 12 vs 3 solvers whose every
essential part was a verbatim injected rule. On seed 3 that difference vanishes (11 vs 12).
Laws copied verbatim from the matched NON-solving genomes become essential just as often.
They are useful parts that their source genome did not use for the task.

What replicates across both seeds is the small rate advantage and more redundant solutions
in the SYN arm (47 vs 37; 42 vs 37). Inheritance of the specific SYN-solving parts does not.

## Predictions

| id | prediction | outcome |
|---|---|---|
| Q1 | H-SYN-SOLVE-S3 supported (p .35) | did not occur: INDETERMINATE, in line with the stated probability |
| Q2 | direction S > M | RIGHT |
| Q3 | H-SYN-POOLED supported | RIGHT |
| Q4 | more all-copied solvers in S than M | WRONG (11 vs 12): ledger |
