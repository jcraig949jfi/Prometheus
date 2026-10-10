# THESEUS-40 verdict: third seed for 36/37 and the pooled 3-seed size

Prereg: roles/Theseus/prereg/2026-10-09_third_seed/PREREG.md (20a608cae).

Seed-3 runs (master seed 20261010, flags as 38):
- v0_2t0_s3_2026-10-09 (task0)
- v0_2t0nl_s3_2026-10-09 (task0 --no-law)
- v0_2tr_s3_2026-10-09 (rep)

Evals:
- comp_task_s3_law_2026-10-09: --a task0 --b no-law, 2 workers
- comp_task_s3_sel_2026-10-09: --a task0 --b rep, 4 workers. Its task0 J and KO files were
  copied from the law eval before it ran. They are deterministic and identical by
  construction; task_comp's checkpoint resumed from them.

Pooled: python -m theseus.synth.pooled (files POOLED_*.json here).

GATE (seed 3, both evals): 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Seed 3

| test | a | b | one-sided Fisher p | verdict |
|---|---|---|---|---|
| H-SEL-S3 | task0 75/100 (mean J .795) | rep 63/100 (.713) | .0461 | SUPPORTED |
| H-LAW-S3 | task0 75/100 | no-law 62/100 (.701) | .0337 | SUPPORTED |

## Pooled over 3 seeds (the quotable result)

H-SEL-POOLED (task selection vs reproducibility selection):

| seed | a | b | RD [Newcombe 95% CI] |
|---|---|---|---|
| 1 | 91 | 59 | .32 [.204, .427] |
| 2 | 78 | 63 | .15 [.024, .270] |
| 3 | 75 | 63 | .12 [-.008, .243] |

CMH z 5.33, one-sided p 4.9e-8; RD_MH .197 [.119, .274]. SUPPORTED.

H-LAW-POOLED (collision-generated laws vs none):

| seed | a | b | RD [Newcombe 95% CI] |
|---|---|---|---|
| 1 | 91 | 52 | .39 [.270, .496] |
| 2 | 78 | 66 | .12 [-.005, .240] |
| 3 | 75 | 62 | .13 [.001, .253] |

CMH z 5.73, one-sided p 5.1e-9; RD_MH .213 [.134, .293]. SUPPORTED.

## Heterogeneity

Seeds 2-3 pooled:

| effect | RD_MH [95% CI] | CMH p |
|---|---|---|
| selection | .135 [.042, .228] | .0017 |
| laws | .125 [.033, .217] | .0032 |

Seed 1's RD lies ABOVE the seeds 2-3 upper bound for both effects (.32 > .228; .39 > .217).
Seed 1 was a single-seed overestimate of both effects, by roughly 2.5-3x (ledger).

The 3-seed RD_MH is the preregistered quotable size. Because seed 1 is an outlier, the
honest statement is: "task selection adds about 13-20 points of deep solvers, and removing
the collision-generated laws removes about 12-21 points (pooled 3 seeds; seeds 2-3 alone give
the lower figure)".

## Attribution (seed 3; python -m theseus.synth.ko_prov)

Essential-rule counts 0/1/2/3/4:

| run | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| task0 | 33 | 26 | 12 | 3 | 1 |
| no-law | 19 | 25 | 17 | 1 | 0 |
| rep | 29 | 18 | 13 | 3 | 0 |

Essential-rule provenance:

| run | provenance | solvers with a law essential | law rules writing the sensor channel |
|---|---|---|---|
| task0 | law 32, G0 14, mutation edit 11, lens 6 | 28/75 | 19 |
| no-law | G0 44, mutation edit 16, lens 2 | 0 | 0 |
| rep | law 32, mutation edit 14, lens 5, G0 2 | 27/63 | 18 |

## Reading (3 seeds)
- Collision-generated laws are the commonest essential step in every law-on run, and about
  60% of them are the release into the sensor channel.
- Without laws, solvers fall back on human-derived G0 rules. On seed 3, G0 is the source of
  44 of 62 essential rules.
- Selection's gain is not a larger law-carried share: 28/75 vs 27/63 on seed 3.

## Predictions (all RIGHT)

| id | prediction | outcome |
|---|---|---|
| T1 | H-SEL-S3 supported | p .046 |
| T2 | H-LAW-S3 supported | p .034 |
| T3 | H-SEL-POOLED supported | yes |
| T4 | H-LAW-POOLED supported | yes |
| T5 | pooled selection RD in [.10, .25] | .197 |
| T6 | seed-1 selection RD above the seeds 2-3 CI | .32 > .228 |
