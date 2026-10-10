# THESEUS-46 preregistration -- do REDUNDANT solvers generalise better?

Currency: 2026-10-09. Committed before the contrast below is computed.

Disclosure: the data already exist. theseus/runs/generalise_2026-10-09/TABLE.jsonl (45,
524d35156) holds, per solver, n_essential and J at V4 k20 and V8 k8. 45 examined arm (law vs
no-law) and law-essential presence. The relation between n_essential and generalisation has
NOT been computed or inspected. This prereg freezes the test before it is.

## Why

Across 36/38/40, selection and generated laws raise the share of solvers with no single
essential rule (redundant, multi-path store/release). 45 found the generalisation advantage
of law-bearing ecologies is NOT carried by an essential law rule; law-essential solvers
generalise slightly worse than redundant law-on ones. If redundancy is what generalises, the
REDUNDANT vs ONE-POINT contrast should hold within each arm.

## Test

Population: the 424 solvers of 45.
- REDUNDANT: n_essential == 0.
- ONE-POINT: n_essential >= 1.
Strata: arm (law-on, no-law) x seed (1, 2, 3) = 6 strata.

H-REDUND-ALPHA: share solving V8 k8 (J >= .6), REDUNDANT > ONE-POINT. One-sided CMH over the 6
strata, alpha .025.
H-REDUND-DELAY: the same for V4 k20, alpha .025.
Each is SUPPORTED iff CMH p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED iff
RD_MH <= 0; else INDETERMINATE.

Descriptive: per-arm RDs, and the RD within the law-on arm only.

Command: PYTHONPATH=. python theseus/synth/redund_score.py (committed with this prereg).

## Predictions

| id | prediction | p |
|---|---|---|
| D1 | H-REDUND-ALPHA SUPPORTED | 0.55 |
| D2 | H-REDUND-DELAY SUPPORTED | 0.5 |
| D3 | the RD is positive in both arms for V8 k8 | 0.6 |

## Compute

None: a re-analysis of committed rows.
