# THESEUS-39 verdict: SYN re-injection (prereg roles/Theseus/prereg/2026-10-09_syn_reinject/, 0e93f7ac7)

Runs: PYTHONHASHSEED=0, master seed 20261009, flags as in THESEUS-38 S2-TASK0, plus:
- INJ-S v0_2t0_s2_injS_2026-10-09: --inject inject_S (the 20 admitted SYN concepts; 20/20 viable at injection)
- INJ-M v0_2t0_s2_injM_2026-10-09: --inject inject_M (20 matched non-solvers, J .20-.47; 20/20 viable)
- N (descriptive): v0_2t0_s2_2026-10-08, already evaluated in comp_task_s2_sel_2026-10-08

Eval: python -m theseus.synth.task_comp --tag comp_task_syn_2026-10-09
--a v0_2t0_s2_injS_2026-10-09 --b v0_2t0_s2_injM_2026-10-09 --workers 4.

GATE: 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Primary: H-SYN-SOLVE
D solvers (J >= .6), 100 viable DEEP+VERY_DEEP children per run:
- INJ-S 85/100 (mean J .865)
- INJ-M 72/100 (mean J .781)
- one-sided Fisher p .0190; RD .13, Newcombe 95% CI [.016, .241]

VERDICT: SUPPORTED, on one seed. Re-injected compressed concepts raise the rate at which deep
descendants solve the composition-necessary task, relative to equally deep, same-lineage,
non-solving matter. Nothing broader is claimed.

Single-seed caveat: this is the first and only seed. The two previous headline effects shrank
by half or more on replication (38), so the size here is unconfirmed. It would need a second
seed before it is quoted (frontier: THESEUS-42).

## Secondary
- S1 INJ-S vs N (78/100): one-sided p .137. Not distinguishable. Confounded by lane timing
  (see the prereg), descriptive only.
- S2 INJ-M vs N: 72 vs 78, two-sided p .414. Adding deep non-solving matter did not
  measurably change the rate.
- S3 in-run (200/200 episodes, every viable DEEP+VERY_DEEP child):

  | run | solvers | first D solver |
  |---|---|---|
  | INJ-S | 312/378 (83%) | gen 1 |
  | INJ-M | 282/364 (77%) | gen 1 |

  Every in-run solver in both arms has an injected ancestor: 312/312 and 282/282.
  The un-injected run N first has DEEP children at gen 6.
- S4 attribution (knockouts on every solver; python -m theseus.synth.inject_attr / ko_prov).

  Essential-rule counts 0/1/2/3/4:

  | run | 0 | 1 | 2 | 3 | 4 |
  |---|---|---|---|---|---|
  | INJ-S | 47 | 30 | 8 | 0 | 0 |
  | INJ-M | 37 | 22 | 10 | 1 | 2 |

  Redundant solvers (no single essential rule): INJ-S 47/85 (55%), INJ-M 37/72 (51%).

  Essential rules copied VERBATIM from an injected genome:

  | run | copied | of which laws | solvers with any essential copy | all essential parts copied |
  |---|---|---|---|---|
  | INJ-S | 16/46 | 12 | 15/38 | 12 |
  | INJ-M | 14/53 | 5 | 12/35 | 3 |

  Essential-rule provenance:
  - INJ-S: law 31, mutation edit 12, lens 2, G0 1 (18 law rules write the sensor channel)
  - INJ-M: law 35, mutation edit 10, G0 5, lens 3 (17 write the sensor channel)

## Reading
The SYN arm's advantage has two visible sources:
1. Inherited working parts. In 12 SYN-arm solvers every essential part is a verbatim copy of
   a SYN concept rule, mostly a collision-generated law. That happens in 3 control-arm
   solvers.
2. More redundant solutions: 47 vs 37 solvers with no single essential rule.

Most solvers in both arms still rest on laws generated afresh in the new run. The concept's
law is re-used, not required.

Part R (theseus/runs/syn_repro_v0_2t0_2026-10-08/NOTE.md, f90c6986f): on the task the SYN
concepts are indistinguishable from, or worse than, a hand-written store+release program. So
what is being re-used is a self-generated implementation of a known function.

## Predictions

| id | prediction | outcome |
|---|---|---|
| P1 | INJ-S >= .85 | .85, RIGHT (at the boundary) |
| P2 | H-SYN-SOLVE SUPPORTED | RIGHT |
| P3 | INJ-M within 68-88 | 72, RIGHT |
| P4 | first in-run D solver earlier in INJ-S | WRONG: both gen 1 (ledger) |
| P5 | R2 >= 10/20 reproduced or partial | 16, RIGHT |
| P6 | R1 <= 5/20 reproduced | 2, RIGHT |

## Annotation 2026-10-09 (THESEUS-42)
The "inherited working parts" source in the Reading (12 vs 3 all-copied solvers) did not
replicate on seed 20261010: 11 vs 12 (theseus/runs/comp_task_syn_s3_2026-10-09/VERDICT.md).
The rate advantage replicates in direction only (79 vs 74). Pooled over 2 seeds:
RD_MH .090 [.007, .173], CMH p .016. Quote the pooled figure, not the 13 points above.
