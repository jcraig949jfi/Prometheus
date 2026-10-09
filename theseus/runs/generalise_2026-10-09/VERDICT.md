# THESEUS-45 verdict: why law-built solvers generalise (prereg roles/Theseus/prereg/2026-10-09_generalise/, 970399844)

Commands:
- python -m theseus.synth.generalise --tag generalise_2026-10-09 --workers 2
- scoring: PYTHONPATH=. python theseus/synth/generalise_score.py (SUMMARY.json)

Population: every selected-task solver of the law-on (task0) and no-law runs, seeds 1-3:

| arm | seed 1 | seed 2 | seed 3 | total |
|---|---|---|---|---|
| law-on | 91 | 78 | 75 | 244 |
| no-law | 52 | 66 | 62 | 180 |

## Primaries (CMH over seeds, alpha .025 each)

H-DELAY: solves V4 k20 (alphabet fixed, delay 8 -> 20).

| seed | law-on | no-law |
|---|---|---|
| 1 | 76/91 | 38/52 |
| 2 | 64/78 | 43/66 |
| 3 | 60/75 | 48/62 |

CMH z 2.45, one-sided p .0072; RD_MH .101 [.018, .183]. SUPPORTED.

H-ALPHA: solves V8 k8 (delay fixed, alphabet 4 -> 8).

| seed | law-on | no-law |
|---|---|---|
| 1 | 77/91 | 35/52 |
| 2 | 59/78 | 38/66 |
| 3 | 58/75 | 39/62 |

CMH z 3.76, one-sided p 8.5e-5; RD_MH .166 [.075, .257]. SUPPORTED.

Secondary H-LAWESS: within law-on solvers, those with an essential collision-generated law vs
those without one, solving V4 k20.

| seed | essential law | no essential law |
|---|---|---|
| 1 | 25/34 | 51/57 |
| 2 | 26/32 | 38/46 |
| 3 | 23/28 | 37/47 |

CMH one-sided p .85; RD_MH -.053 [-.153, .048]. NOT SUPPORTED (the direction is reversed).

## Descriptive

Mean J by delay k (V4):

| arm | k 4 | k 8 | k 12 | k 16 | k 20 |
|---|---|---|---|---|---|
| law-on | .996 | .982 | .930 | .884 | .856 |
| no-law | .997 | .970 | .886 | .820 | .767 |

Mean J at V8 k8: law-on .827, no-law .685.

Cross-tab of the two axes:

| arm | both | delay only | alphabet only | neither |
|---|---|---|---|---|
| law-on | 178 (73%) | 22 | 16 | 28 |
| no-law | 101 (56%) | 28 | 11 | 40 |

Law arity (distinct sources) of essential laws, law-essential solvers:

| outcome at k20 | n | mean | arity 2 | arity 3 | other |
|---|---|---|---|---|---|
| pass | 74 | 2.42 | 44 | 29 | arity 4: 1 |
| fail | 20 | 2.25 | 14 | 4 | arity 1: 1, arity 4: 1 |

## Reading
- Law-built solvers are more robust on both axes. The larger gap is the ALPHABET axis (8
  symbols at the same delay: RD .166), not the delay axis (RD .101).
- Distinguishing more cue values through the store/release path is where no-law solutions
  break most.
- The advantage is a property of solvers from law-bearing ECOLOGIES. Inside those ecologies,
  it is not carried by an essential law rule: solvers whose essential step is a law
  generalise no better than redundant solvers with no single essential rule (RD -.05).
- Consistent with the redundancy readings of 36/38/40: law-bearing ecologies produce more
  redundant, multi-path store/release solutions, and multi-path solutions survive harder
  settings.
- The arity of the essential law differs little between generalising and failing solvers
  (2.42 vs 2.25; 3-source laws 29/74 vs 4/20, descriptive).

## Predictions

| id | prediction | outcome |
|---|---|---|
| G1 | H-DELAY SUPPORTED | RIGHT |
| G2 | H-ALPHA SUPPORTED | RIGHT |
| G3 | delay RD > alphabet RD | WRONG (.101 < .166): ledger |
| G4 | H-LAWESS SUPPORTED (p .45) | did not occur; the direction is reversed |
