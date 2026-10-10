# THESEUS-49 preregistration -- causal release swap

Currency: 2026-10-10. Committed before any swap is scored.
Code: theseus/synth/release_swap.py (new), probe_store.py, task_system.py, task_comp.py;
hashes in CODE_HASHES.txt.

## Why

48 (1e3f4d8d4) located the no-law generalisation deficit at RELEASE. Among store-intact
solvers at V 8, law-on solvers release more often: RD .216 [.132, .301]. 69% of failing
no-law solvers hold the cue but do not release it. About 60% of essential collision-generated
laws write the sensor channel. If those laws ARE the better release machinery, transplanting
one into a store-intact, release-failing no-law solver should rescue release. A coupling-
scrambled copy of the same rule should rescue less.

## Design (python -m theseus.synth.release_swap --tag release_swap_2026-10-10 --workers 4)

Recipients: every no-law solver of 48 with J_store >= .6 and J_release < .6 at V8 k8 (79
expected).

Donor laws: every essential (task_comp knockout) 'law:'-provenance rule with dst 0 in
law-on solvers of the SAME seed that release at V 8 (J_release >= .6).

Per recipient, 3 donor laws (seeded rng 20261012, sorted pools). Each is tested two ways:

| variant | appended as the recipient's last rule |
|---|---|
| SWAP | the donor law (sources taken mod the recipient's C; dst 0) |
| CTRL | the same rule with its per-source gains sign-flipped and permuted (rng 20261013) |

Outcome: J at V 8, k 8, sensor readout, task seed 0, 400/400.

## Primary

H-SWAP: per recipient, mean J over its 3 donors, SWAP > CTRL. One-sided Wilcoxon signed-rank.
SUPPORTED iff p < .05 and the median paired difference > 0; NOT SUPPORTED iff the mean paired
difference <= 0; else INDETERMINATE.

## Secondary

- S1 rescue: recipients with J >= .6 for at least one donor, SWAP vs CTRL. Exact McNemar,
  one-sided, alpha .05.
- S2 SWAP vs the recipient's own J_release (baseline): mean change and the rescue share.
- S3 CTRL vs baseline (does any extra sensor-writing react help?).
- S4 the store is not destroyed: J_store is not re-measured here (cost); stated as a limit.

## Predictions

| id | prediction | p |
|---|---|---|
| W1 | H-SWAP SUPPORTED | 0.55 |
| W2 | SWAP rescue share >= 25% of recipients | 0.45 |
| W3 | CTRL raises mean J above baseline by >= .05 | 0.5 |
| W4 | S1 SUPPORTED | 0.5 |

## Compute

79 recipients x 3 donors x 2 variants = ~474 J evaluations at V8 k8 (~3 s each): ~0.5
CPU-hour (MWO R2 cap 16).
