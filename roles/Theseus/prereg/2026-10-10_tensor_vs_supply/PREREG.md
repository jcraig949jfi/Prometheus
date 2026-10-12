# THESEUS-51 preregistration -- concept-tensor content vs coupling supply

Currency: 2026-10-10. Committed before either run.
Code: collide.py (random_law_gains), run_v0.py (--random-law-gains), task_comp.py,
pooled.py, release_swap.py (J8); hashes in CODE_HASHES.txt.

Verified before this prereg: with the flag off, collide is unchanged (the flag only touches
the law's gains). With it on, a test collision differs ONLY in the law rule's per-source
gains; amp, bias, placement, sources, dst and every other rule are identical.

## Why

37/38/40 show that collision-generated k-ary laws are causally involved in capability
(pooled RD .213). 48-50 suggest a plain account: the laws SUPPLY a read-back coupling into the
sensor channel, and any such coupling, even a single-source one, rescues release. The charter's
object is the CONCEPT TENSOR: law gains come from latent factors of the parents. Is the
tensor's content doing work, or only the supply of a react coupling of that shape?

## Design (flags as 40; seeds 20261010 and 20261011)

RANDLAW runs: PYTHONHASHSEED=0 --quality task0 --random-law-gains --master-seed <seed>
--g0-readers --cond-ops --aligned-binding --ecology-only --elite-grids pca --pop-cap 300
--dark-protect-gens 3 --elite-protect-k 150 --seed-select 1.5 --workers 2

| seed | RANDLAW (new) | LAW (existing) | NOLAW (existing) |
|---|---|---|---|
| 20261010 | v0_2t0rg_s3_2026-10-10 | v0_2t0_s3_2026-10-09 | v0_2t0nl_s3_2026-10-09 |
| 20261011 | v0_2t0rg_s4_2026-10-10 | v0_2t0_s4_2026-10-09 | v0_2t0nl_s4_2026-10-09 |

Evals: python -m theseus.synth.task_comp --tag comp_task_s{3,4}_rg_2026-10-10
--a <RANDLAW> --b <NOLAW> (gate inside; J + knockouts). The LAW J rows (deterministic) are
copied into those dirs from comp_task_s{3,4}_law_* for pooling.

## Primaries (one-sided CMH over the 2 seeds, alpha .025 each)

| hypothesis | contrast (D solver share) |
|---|---|
| H-TENSOR | LAW > RANDLAW |
| H-SUPPLY | RANDLAW > NOLAW |

Each is SUPPORTED iff p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED iff RD_MH <= 0;
else INDETERMINATE. GATE as 36.

Reading rule, fixed in advance:

| H-TENSOR | H-SUPPLY | reading |
|---|---|---|
| NOT SUPPORTED or INDETERMINATE | SUPPORTED | the capability effect of laws is mostly coupling supply, not concept-tensor content |
| SUPPORTED | - | tensor content matters beyond supply |

## Secondary

- S1 generalisation among RANDLAW solvers: J at V8 k8 (release; rs.J8) vs the LAW and NOLAW
  solvers' J_release from 48. Share >= .6, pooled CMH, descriptive.
- S2 the essential-rule provenance of RANDLAW solvers (ko_prov).

## Predictions

| id | prediction | p |
|---|---|---|
| T1 | H-TENSOR SUPPORTED | 0.3 |
| T2 | H-SUPPLY SUPPORTED | 0.6 |
| T3 | RANDLAW solvers generalise to V8 k8 at >= 70% | 0.55 |

## Compute

Two ecology runs (~30 min x 2 workers each, in parallel) + two evals (~40 min) + S1 scoring
(~150 evals): ~8 CPU-hours. Day-3 total so far ~1.5 of 48.
