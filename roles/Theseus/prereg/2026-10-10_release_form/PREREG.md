# THESEUS-50 preregistration -- is the FORM of a generated law the release machinery?

Currency: 2026-10-10. Committed before Part A counts are computed and before any Part B
evaluation.
Code: theseus/synth/release_form.py (new), release_swap.py, pooled.py; hashes in
CODE_HASHES.txt.

## Why

49 (3e4859324): appending a donor's essential release law to store-intact, release-failing
no-law solvers raised release J by +.120. A coefficient-scrambled copy raised it by +.101.
The difference was INDETERMINATE (p .0500).
Reading: the rescue comes mostly from the law's FORM, a react rule with several source
channels writing the sensor channel, not from its learned coefficients.

Two tests of that reading:
- (A) does the form predict release in naturally evolved solvers?
- (B) does removing the form (cutting the law to one source) remove the rescue?

## Part A (no new task runs)

F = number of rules with op "react", dst 0 and >= 2 distinct source channels.

H-FORM: among store-intact solvers of 48 (J_store >= .6 at V 8), solvers with F >= 1 release
(J_release >= .6) more often than solvers with F = 0. One-sided CMH over the 8 arm x seed
strata (the arm is held fixed, so this is a within-arm test); alpha .025.
SUPPORTED iff CMH p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED iff RD_MH <= 0;
else INDETERMINATE.

Descriptive: share with F >= 1 by arm, and the arm effect on release within F = 0 and within
F >= 1.

## Part B (python -m theseus.synth.release_form --tag release_form_2026-10-10 --workers 4)

Same 79 recipients and the IDENTICAL donor draws as 49.

SINGLE: the donor law cut to one source. It keeps its first non-sensor source channel (taken
mod C; channel 1 if none), amp, bias and that source's gain, and is appended as the last
rule.

H-MULTI: per recipient, mean J over its 3 donors: 49's CTRL (multi-source, coefficients
scrambled) > SINGLE. One-sided Wilcoxon signed-rank. SUPPORTED iff p < .05 and median
difference > 0; NOT SUPPORTED iff mean difference <= 0; else INDETERMINATE.

Descriptive: SWAP vs SINGLE; SINGLE vs baseline; rescue counts.

## Predictions

| id | prediction | p |
|---|---|---|
| F1 | H-FORM SUPPORTED | 0.55 |
| F2 | H-MULTI SUPPORTED | 0.5 |
| F3 | SINGLE raises mean J over baseline by < .05 | 0.45 |
| F4 | law-on solvers have F >= 1 more often than no-law solvers | 0.75 |

## Compute

Part A: none. Part B: 237 J evaluations at V8 k8, ~0.25 CPU-hour.
