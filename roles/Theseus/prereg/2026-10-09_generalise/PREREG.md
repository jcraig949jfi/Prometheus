# THESEUS-45 preregistration -- why do law-built solvers generalise? Delay vs alphabet, and the essential law

Currency: 2026-10-09. Committed before any new scoring.
Code: theseus/synth/generalise.py (new), task_system.py, task_comp.py, pooled.py; hashes in
CODE_HASHES.txt.

## Why

On the held-out V8 k16 variant (43, 54557bba8), selected-task solvers transferred at
different rates:

| solvers | transfer rate |
|---|---|
| law-on (task0) | .635 pooled |
| no-law | .42 pooled; .33-.35 on seeds 2-3 |

That variant changed delay (8 -> 16) and alphabet (4 -> 8) together. Which axis breaks the
no-law solvers? And within law-on solvers, is an essential collision-generated law what
carries the generalisation?

## Population (no new ecologies)

Every selected-task solver (J >= .6 at V4 k8, the 37/38/40 law-eval rows) of the task0 and
no-law runs, seeds 1-3:

| arm | seed 1 | seed 2 | seed 3 | total |
|---|---|---|---|---|
| law-on | 91 | 78 | 75 | 244 |
| no-law | 52 | 66 | 62 | 180 |

Per solver (sensor readout, task seed 0, 400/400 episodes):
- J at V 4, k = 4, 8, 12, 16, 20 (delay axis);
- J at V 8, k 8 (alphabet axis).

Command: python -m theseus.synth.generalise --tag generalise_2026-10-09 --workers 2.

## Primaries (each one-sided CMH over the 3 seed strata, alpha .025 each, Bonferroni)

| hypothesis | outcome (among solvers) | contrast |
|---|---|---|
| H-DELAY | solves at V4 k20 (J >= .6) | law-on > no-law |
| H-ALPHA | solves at V8 k8 | law-on > no-law |

Each is SUPPORTED iff CMH p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED iff
RD_MH <= 0; else INDETERMINATE.

Secondary H-LAWESS: within law-on solvers, those with an essential collision-generated law
solve V4 k20 more often than those without one. Pooled CMH over seeds, one-sided, alpha .05.

Descriptive:
- mean J(k) curves per arm;
- the largest k with J >= .6 per solver;
- the distinct-source count of essential laws (law arity) for transferring vs non-transferring
  law-essential solvers.

## Predictions

| id | prediction | p |
|---|---|---|
| G1 | H-DELAY SUPPORTED | 0.65 |
| G2 | H-ALPHA SUPPORTED | 0.5 |
| G3 | the delay RD_MH > the alphabet RD_MH (delay is the main axis) | 0.55 |
| G4 | H-LAWESS SUPPORTED | 0.45 |

## Compute

424 solvers x 6 scorings, ~3-5 s each: ~2.5-3.5 CPU-hours (MWO R2 cap 16).
