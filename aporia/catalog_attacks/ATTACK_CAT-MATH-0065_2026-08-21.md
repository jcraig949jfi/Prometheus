# ATTACK CAT-MATH-0065 — maximal prime gaps vs ln^2 p (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P53) | Grounding: AA-062 (Cramer's model refuted strictly;
Granville frame 2e^-gamma = 1.122919; true limsup OPEN) | Code: attack_0065_gaps.py |
Data: attack_0065_results.json

## Pre-stated readings
REVIEWER-REPRODUCED (max in-range ratio 0.7395, p>=100 cutoff) + TREND-DESCRIPTIVE /
REVIEWER-MISMATCH (resolve first).

## Result
- Max g(p)/ln^2 p with p>=100: 0.739500 at p=20,831,323, gap=210 — reviewer REPRODUCED
  first run, and both endpoint conventions (left/right normalization) coincide at 4dp.
- 25 record (maximal) gaps to 1e8, matching the classical table (113/14, 1327/34,
  31397/72, 370261/112, 2010733/148, 20831323/210, ..., 47326693/220) — instrument check.
- Per-decade max ratio: 0.6264, 0.6576, 0.6715, 0.6813, 0.7026, 0.7395 — monotone slow
  climb, everywhere far below the Granville constant 1.1229.

## Reading: TREND-DESCRIPTIVE (as the correction mandates)
The curve is CONSISTENT with a slowly growing normalized-gap envelope approaching the
Granville frame from below; a limsup conjecture admits no in-range verdict in either
direction and none is issued. Direction discipline (reviewer's fix): larger ratios would
SUPPORT the >=2e^-gamma frame; nothing here challenges or confirms anything asymptotic.

## NOT claimed
No statement about the true limsup, about Cramer vs Granville, or about gap growth beyond
1e8. The monotone decade climb is 6 points of an extreme-value statistic — extrapolating
it would be the ORDER-STATISTIC SCALING trap by construction.

## Trace-vector record
problem_id: CAT-MATH-0065 | tier_probe: extreme-value descriptive | answer_correct: n/a
domain_constraints_detected: [limsup-not-in-range-falsifiable, small-p-cutoff-necessity, endpoint-convention-coincidence]
operations_used: [sieve-gap-extraction, record-table-cross-check, per-decade-envelope, reviewer-reproduction-first-run]
kill_pattern: none | repair_available: n/a
confidence_calibration: exact reviewer match + classical record-table match
residue: for extreme-value attacks the RECORD TABLE is the natural instrument check — it is discrete, classical, and any sieve error corrupts it loudly
