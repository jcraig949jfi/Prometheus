# THESEUS-49 verdict: causal release swap (prereg roles/Theseus/prereg/2026-10-10_release_swap/, 12b5f1ac4)

Commands:
- python -m theseus.synth.release_swap --tag release_swap_2026-10-10 --workers 4
- scoring: PYTHONPATH=. python theseus/synth/release_swap_score.py (SUMMARY.json)

Recipients: 79 store-intact, release-failing no-law solvers (48).
Donor pools: essential sensor-writing laws from releasing law-on solvers, per seed
18 / 17 / 16 / 9. 3 donors per recipient; 474 evaluations at V8 k8.

## Primary: H-SWAP (per-recipient mean J over 3 donors)

| | SWAP (donor law) | CTRL (gains sign-flipped and permuted) |
|---|---|---|
| mean J | .445 | .425 |

Mean paired difference +.019; median 0.000. One-sided Wilcoxon p .0500.
VERDICT: INDETERMINATE. p is not < .05, and the median difference is not > 0.

## Secondary

S1 rescue (J >= .6 with at least one donor):

| | SWAP | CTRL |
|---|---|---|
| recipients rescued | 31/79 (39%) | 26/79 (33%) |
| single (recipient, donor) evaluations rescued | 51/237 | 42/237 |

Discordant recipients: 8 rescued by SWAP only, 3 by CTRL only. Exact McNemar one-sided
p .113. Not supported.

S2/S3 against the recipients' own release (baseline mean J .325):
- SWAP mean change +.120
- CTRL mean change +.101

S4: the store was not re-measured after the transplant (as preregistered).

## Reading

Appending a single k-ary sensor-writing coupling from the storage channels rescues release
in about a third of release-failing no-law solvers. The donor law's EXACT gains add little
beyond a sign-flipped, permuted copy of the same rule: +.019 mean, 8 vs 3 discordant
rescues. Both are suggestive and neither is significant.

So the release machinery that law-bearing ecologies supply is carried mostly by the FORM of
a generated law (a multi-source "react" from storage channels into the sensor channel), not
by its specific learned coefficients.
- This fits 45 (an essential law's identity does not predict generalisation) and 48 (the
  deficit is at release).
- The no-law op set has no rule of this form. Without collision-generated laws, react rules
  arise only from G0 compiles and mutation, and rarely as a multi-source write into the
  sensor channel.
- Testable next (not run): count multi-source sensor-writing react rules per solver by arm,
  and test it as the predictor of V 8 release.

Limits:
- One task family; appended (not substituted) rules; no store re-measurement.
- CTRL keeps the sources and amplitude, so it is a weak control for "law form": it removes
  only the coefficients' arrangement.

## Predictions

| id | prediction | outcome |
|---|---|---|
| W1 | H-SWAP SUPPORTED | WRONG (INDETERMINATE, p .0500): ledger |
| W2 | SWAP rescue >= 25% | 39%, RIGHT |
| W3 | CTRL raises J >= .05 over baseline | +.101, RIGHT |
| W4 | S1 SUPPORTED | WRONG (p .113): ledger |

## Annotation 2026-10-10 (THESEUS-50)
The reading above ("carried mostly by the FORM of a generated law, a multi-source react") is
corrected. A single-source cut of the same donor law rescues MORE: mean J .500, 37/79 rescued,
vs .425 / 26 for the multi-source scrambled copy (theseus/runs/release_form_2026-10-10/VERDICT.md).
What rescues release is a direct storage -> sensor coupling. Law-bearing ecologies supply one
almost universally (93% vs 19% of solvers).
