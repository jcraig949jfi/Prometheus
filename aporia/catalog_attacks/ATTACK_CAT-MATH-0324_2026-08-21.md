# ATTACK CAT-MATH-0324 — Frankl union-closed, small-case (CALIBRATION, spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P55) | Code: attack_0287_0324.py | Data: attack_0287_0324_results.json

Pre-stated readings: REVIEWER-REPRODUCED (4958 families, convention documented by
whichever reproduces) + SAMPLE-CLEAN at 5 / ANY-VIOLATION (instrument-bug-first).

Result:
- Exhaustive on ground set 4: 2,479 union-closed families of nonempty sets, and 2,479
  with the empty set adjoined — 2479 x 2 = 4,958. CONVENTION RESOLVED BY ARITHMETIC:
  the reviewer's 4958 counts empty-set-containing and empty-set-free families as
  distinct; both enumerations here are exhaustive and independent.
- Frankl majority element: 0 violations in all 4,958 (reviewer's 4958/4958 REPRODUCED).
- Five elements: 2,000 stratified random generator-closures, 0 violations (sampling,
  NOT exhaustive — stated).

CALIBRATION (label binding per the reviewer's correction): certifies the family-
enumeration + closure harness. Small ground sets are settled folklore; a PASS here says
NOTHING about the union-closed conjecture (AA-069's Gilmer 0.382 fractional bound is
where the general question actually stands).

Trace-vector: problem_id CAT-MATH-0324 | operations [exhaustive-family-enumeration,
union-closure-check, dual-convention-count, majority-element-verification,
random-closure-sampling] | kill_pattern none | residue: when a reviewer's count is
exactly 2x yours, the convention delta is usually a single boundary object (here the
empty set) — check multiplicative relations before suspecting either instrument
