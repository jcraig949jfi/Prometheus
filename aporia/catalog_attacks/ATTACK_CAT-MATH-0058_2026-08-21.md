# ATTACK CAT-MATH-0058 — twin primes vs 2*C2*li_2 (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P52) | Spec: triage MATH-0058 (P25 batch; reviewer correction
binding: li_2 predictor, not x/ln^2 x) | Grounding: AA-058 BOUNDED_GAPS_246_VS_TWIN_
PRIMES_OPEN (bounded gaps proven at 246; twin infinitude OPEN — untouched here) |
Code: attack_0058_twins.py | Data: attack_0058_results.json

## Pre-stated readings
LI2-CONSISTENT (obs/pred -> 1, deviations shrinking; reproduce reviewer's 0.9999 at 1e8) /
LI2-DRIFT (instrument first) / REVIEWER-MISMATCH (resolve before any reading fires).

## Instrument event: the mismatch reading FIRED and did its job
First run gave 0.998365 at 1e8 vs the reviewer's executed 0.9999 — REVIEWER-MISMATCH.
Root cause: uniform-in-t trapezoid for li_2 with step ~500 under-resolves 1/ln^2 t near
t=2, biasing the predictor ~0.15% high. Fix: u-substitution (t=e^u; smooth integrand,
uniform-in-u grid). Post-fix: 0.999873 — reproduces the reviewer to 4 decimals. The
cross-seat number acted as a calibration standard exactly as the channel intends.

## Result (per decade, p<=x convention; pair-le-x convention differs only at edges)
x=1e3: 35/45.8 = 0.7643 | 1e4: 205/214.2 = 0.9570 | 1e5: 1224/1248.7 = 0.9802
1e6: 8169/8248.0 = 0.9904 | 1e7: 58980/58753.8 = 1.0039 | 1e8: 440312/440367.8 = 0.99987
- C2 computed from its Euler product (0.6601618197), no memory constants.
- Twin count at 1e8 = 440,312 (matches the standard literature value exactly — an
  independent instrument check).
Reading: LI2-CONSISTENT — deviation shrinks monotonically in envelope (|1-r|: 0.236,
0.043, 0.020, 0.0096, 0.0039, 0.00013); the 1e7 overshoot is within normal fluctuation.

## NOT claimed
Nothing here bears on twin-prime infinitude. This is the HL twin constant's empirical
quality in [1e3,1e8] under the correct (reviewer-mandated) normalization. The li_2-vs-
shape lesson now has three instances (Elenchus on 0058's draft, P51 Goldbach, this run's
own integrator bug being a mini-instance of resolution mattering).

## Trace-vector record
problem_id: CAT-MATH-0058 | tier_probe: distributional | answer_correct: n/a (empirical)
domain_constraints_detected: [integrator-resolution-near-singularity, predictor-normalization, count-convention-edges]
operations_used: [euler-product-constant, sieve-twin-extraction, u-substitution-quadrature, reviewer-number-as-calibration-standard]
kill_pattern: REVIEWER-MISMATCH fired -> instrument bug found+fixed pre-reading | repair_available: n/a
confidence_calibration: final ratio matches independent reviewer execution to 4 decimals
residue: a cross-seat executed number is a CALIBRATION STANDARD — build reproduction of it into the pre-stated readings of any attack whose spec the reviewer executed
