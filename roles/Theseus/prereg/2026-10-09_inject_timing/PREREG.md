# THESEUS-44 preregistration -- why does injected deep matter raise solvers? Lane timing vs content

Currency: 2026-10-09. Committed before either run.
Code: theseus/synth/inject_variants.py (new; the sets were built before this prereg and are
committed with it), run_v0 --inject, task_comp; hashes in CODE_HASHES.txt.

## Why

41 (descriptive, not preregistered): under reproducibility selection, both injected arms had
far more deep solvers than the un-injected run of the same base seed:

| arm | solvers /100 |
|---|---|
| REP-S | 79 |
| REP-M | 81 |
| N (un-injected rep) | 63 |

Two explanations are confounded:
- (T) lane timing: injected genomes carry generations 6-20, so the DEEP lanes open at gen 1
  instead of after ~5 generations;
- (C) content: the injected genomes carry collision-generated laws that become working parts
  (41: 15 laws among REP-M's copied essential rules).

## Design (master seed 20261009, rep quality; flags as 41)

Common: PYTHONHASHSEED=0 --quality rep --master-seed 20261009 --g0-readers --cond-ops
--aligned-binding --ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5

| arm | injection | timing | content | tag |
|---|---|---|---|---|
| REP-M0 | inject_M0: the same 20 M genomes, generation 0 | removed | kept | v0_2tr_s2_injM0_2026-10-09 |
| REP-R | inject_R: 20 random-arm genomes at the M generations | kept | removed | v0_2tr_s2_injR_2026-10-09 |
| REP-M (from 41) | inject_M | kept | kept | v0_2tr_s2_injM_2026-10-09, not re-run |

REP-R genomes: 'rand' provenance, so no collision law and no G0 rule; rule count within 1 of
the M match; J < .6.

Evals (task_comp):
- comp_task_inj_timing_2026-10-09: --a v0_2tr_s2_injM_2026-10-09 --b v0_2tr_s2_injM0_2026-10-09
- comp_task_inj_content_2026-10-09: --a v0_2tr_s2_injM_2026-10-09 --b v0_2tr_s2_injR_2026-10-09
REP-M's J rows are re-computed in each eval; they are deterministic and must equal 41's 81.

## Decision rules (gate as 36; Bonferroni, alpha .025 each)

H-TIMING: REP-M share > REP-M0 share. SUPPORTED iff one-sided Fisher p < .025; NOT
SUPPORTED iff REP-M <= REP-M0; else INDETERMINATE.
H-CONTENT: REP-M share > REP-R share; same rule.

Descriptive: each arm vs N (63/100), two-sided; verbatim injected essential rules
(inject_attr); in-run first DEEP child generation.

## Predictions

| id | prediction | p |
|---|---|---|
| Y1 | H-TIMING SUPPORTED | 0.5 |
| Y2 | H-CONTENT SUPPORTED | 0.45 |
| Y3 | REP-M0 within 10 points of N (53-73) | 0.5 |
| Y4 | REP-R > N by >= 10 points (timing alone helps) | 0.45 |

## Compute

Two ecology runs (~25-45 min) + two evals (~40 min each, REP-M rows shared by checkpoint
copy): ~7 CPU-hours (MWO R2 cap 16).
