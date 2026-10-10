# THESEUS-46 verdict: redundant vs one-point solvers' generalisation (prereg roles/Theseus/prereg/2026-10-09_redundancy_generalise/, b56e96d48)

Re-analysis of the 45 rows (TABLE.jsonl). The prereg and scorer were pushed before the
contrast was computed.
Command: PYTHONPATH=. python theseus/synth/redund_score.py (REDUND_SUMMARY.json).
Definitions: REDUNDANT = no single essential rule (n_essential 0); ONE-POINT = n_essential >= 1.
Strata: arm x seed (6).

## Primaries

H-REDUND-ALPHA (solves V8 k8):

| stratum | redundant | one-point |
|---|---|---|
| law-on seed 1 | 43/46 | 34/45 |
| law-on seed 2 | 29/34 | 30/44 |
| law-on seed 3 | 26/33 | 32/42 |
| no-law seed 1 | 11/16 | 24/36 |
| no-law seed 2 | 9/21 | 29/45 |
| no-law seed 3 | 12/19 | 27/43 |

CMH one-sided p .125; RD_MH .051 [-.037, .138]. INDETERMINATE.

H-REDUND-DELAY (solves V4 k20):

| stratum | redundant | one-point |
|---|---|---|
| law-on seed 1 | 44/46 | 32/45 |
| law-on seed 2 | 32/34 | 32/44 |
| law-on seed 3 | 26/33 | 34/42 |
| no-law seed 1 | 13/16 | 25/36 |
| no-law seed 2 | 12/21 | 31/45 |
| no-law seed 3 | 11/19 | 37/43 |

CMH one-sided p .103; RD_MH .053 [-.032, .137]. INDETERMINATE.

## Descriptive: the per-arm split (an interaction, not preregistered as a test)

| arm | V8 k8 RD_MH | V4 k20 RD_MH |
|---|---|---|
| law-on | .130 [.024, .235], p .006 | .154 [.050, .258], p .001 |
| no-law | -.073 [-.227, .081] | -.106 [-.252, .041] |

## Reading
- Redundancy predicts generalisation only when the redundant paths are built in a law-bearing
  ecology. There, redundant solvers generalise 13-15 points more often than one-point ones.
- In the no-law ecology, redundant solvers (multiple copies of human-derived or
  mutation-edited relay rules) generalise no better, or worse.
- Pooled over both arms, the two effects cancel to an INDETERMINATE primary.

With 45, the most consistent account so far: collision-generated laws let the ecology build
several partially independent store/release paths. That multiplicity, not any one law rule,
is what survives a larger alphabet or a longer delay.

This account is post hoc on the per-arm split. It would need its own preregistered test,
for example an arm x redundancy interaction on a fresh seed or a fresh variant, before it is
stated as a finding.

## Predictions

| id | prediction | outcome |
|---|---|---|
| D1 | H-REDUND-ALPHA SUPPORTED, p .55 | WRONG (INDETERMINATE) |
| D2 | H-REDUND-DELAY SUPPORTED, p .5 | WRONG (INDETERMINATE) |
| D3 | positive RD in both arms for V8 k8 | WRONG (no-law -.073) |

All three go in the ledger as one row.

## Annotation 2026-10-09 (THESEUS-47)
The per-arm redundancy split did not replicate on fresh seed 20261011. V8 k8 RD: law-on
+.046, no-law +.071; interaction z -.17 (theseus/runs/interact_s4_2026-10-09/VERDICT.md).
The "multiplicity of law-built paths" account in the Reading above is withdrawn.
The law-built generalisation advantage itself replicated: V8 k8 85% vs 27%, p 5e-12.
