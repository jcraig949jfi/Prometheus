# THESEUS-44 verdict: injected-matter effect -- lane timing vs law content (prereg roles/Theseus/prereg/2026-10-09_inject_timing/, f9a559e2d)

Runs: PYTHONHASHSEED=0, master seed 20261009, rep quality, flags as 41, --workers 2.

| arm | tag | first DEEP child | deep children |
|---|---|---|---|
| REP-M0 (M genomes at generation 0) | v0_2tr_s2_injM0_2026-10-09 | gen 7 | 301 |
| REP-R (random-arm genomes at the M generations) | v0_2tr_s2_injR_2026-10-09 | gen 1 | 328 |
| REP-M (from 41, not re-run) | v0_2tr_s2_injM_2026-10-09 | gen 1 | 409 |
| N (un-injected rep, 38 S2-REP) | v0_2tr_s2_2026-10-08 | gen 6 | 310 |

Evals: task_comp with tags comp_task_inj_timing_2026-10-09 (M vs M0) and
comp_task_inj_content_2026-10-09 (M vs R). REP-M re-computed: 81/100, identical to 41.

GATE (both evals): 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Primaries (alpha .025 each)

| hypothesis | contrast | one-sided Fisher p | verdict |
|---|---|---|---|
| H-TIMING | REP-M 81/100 (mean J .840) vs REP-M0 74/100 (.788) | .155 | INDETERMINATE |
| H-CONTENT | REP-M 81/100 vs REP-R 45/100 (.564) | 9.9e-8 | SUPPORTED |

## Descriptive (two-sided vs N 63/100)

| arm | solvers | vs N |
|---|---|---|
| REP-M | 81 | (41) |
| REP-M0 | 74 | p .128 |
| REP-R | 45 | p .016, BELOW N |

Essential-rule counts 0/1/2/3/4+:

| arm | 0 | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| REP-M | 28 | 30 | 20 | 3 | 0 |
| REP-M0 | 34 | 23 | 14 | 2 | 1 |
| REP-R | 8 | 15 | 13 | 7 | 2 |

Redundant solvers: REP-R 8/45 (18%) vs REP-M 28/81 (35%), REP-M0 34/74 (46%).

Essential-rule provenance:
- REP-M0: law 42, mutation edit 11, G0 8, lens 1. Verbatim injected essential rules: 7/62.
  Generation-0 injected genomes are rarely copied into deep solvers.
- REP-R: law 43, mutation edit 11, rand 10, lens 5, G0 1. Verbatim injected (rand) rules: 10/70.

## Reading
The injected-matter effect under reproducibility selection is about CONTENT, not lane timing.
- Removing the head start (M0) costs 7 points (not significant).
- Removing the content while keeping the head start (R) costs 36 points. It also puts the
  run 18 points BELOW an un-injected ecology.
- Opening the deep lanes early with lawless random matter is harmful. The early deep
  population is built from parts that are worse collision matter than the ecology's own
  G0-rooted lineages.
- Matter from a law-bearing ecology is good collision matter whether or not it solved the
  task (41: SYN 79 vs non-solver 81). What makes injected genomes useful is that they
  already carry collision-generated laws and law-built structure. Of the content variants
  tested, solving the task is not what matters.

Single seed, rep quality. The R arm differs from M in more than law content: no G0 rules,
'rand' provenance throughout. "Content" here means the whole bundle of law-bearing,
lineage-derived structure, not laws alone.

## Predictions

| id | prediction | outcome |
|---|---|---|
| Y1 | H-TIMING SUPPORTED, p .5 | WRONG (INDETERMINATE) |
| Y2 | H-CONTENT SUPPORTED | RIGHT |
| Y3 | REP-M0 within 53-73 | WRONG (74, one point above) |
| Y4 | REP-R >= N + 10 | WRONG (45, 18 below N) |

Y1, Y3 and Y4 go in the ledger as one row.
