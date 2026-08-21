# ATTACK CAT-MATH-0057 — binary Goldbach (pure-compute, spec ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P51) | Spec: aporia/mathematics/triage.jsonl MATH-0057 (P25 batch,
disposition sound) | Grounding: AA-057 TERNARY_VS_BINARY_GOLDBACH_BOUNDARY (ternary proven,
binary OPEN, verified ~4e18 Oliveira e Silva-Herzog-Pardi — reviewer-confirmed) |
Code: attack_0057_goldbach.py | Data: attack_0057_results.json

## Pre-stated readings (committed before compute)
R1: ALL-DECOMPOSE / FAILURE-FOUND (instrument audit first, never a claim).
R2: HL-CONSISTENT / HL-DRIFT / HL-STRUCTURED-DEVIATION.

## Instrument discipline
- C2 COMPUTED from its Euler product over primes to 1e7: 0.6601618197 (not a memory number).
- Calibration: r(10)=2, r(100)=6, r(1000)=28 — sieve implementation vs independent sympy
  brute force, 3/3 agree.
- One instrument bug caught by its own guard pre-result: n=4 (partner is the EVEN prime 2)
  survived the odd-partner loop and tripped the >20000 abort — fixed at initialization,
  rerun clean. Filed here because the guard working is part of the result's credibility.

## Part A — decomposition sweep (the consistency check)
All 49,999,999 evens in [4, 1e8] decompose: undecomposed = 0. Max SMALLEST odd partner
in range = 1093. Runtime 7.4s (vectorized smallest-partner elimination).
Reading: R1 = ALL-DECOMPOSE. This is CONSISTENCY-IN-RANGE, ~10 orders below the published
verification frontier; it contributes nothing to the conjecture's status and is framed as
an instrument certification for Part B. (The max-partner value 1093 is reported as a
statistic; that it coincides with a Wieferich prime is NOISE and no claim attaches —
numerical-coincidence discipline.)

## Part B — Hardy-Littlewood distributional test (the real product)
1,190 stratified evens across [1e3, 1e8], r(n) = #{p<=n/2 : p, n-p prime} vs
C2 * prod_{p|n,p>2}((p-1)/(p-2)) * S(n), under BOTH conventions (convention-flip
discipline):

- S = J(n) = int_2^{n-2} dt/(ln t ln(n-t)) (numerical): median obs/(C2*sg*J/2) per
  half-decade: 1.881, 1.937, 1.959, 1.977, 1.987, 1.988, 1.990, 1.990, 1.990, 1.989.
  FLAT at 2.00 from 10^5 up — the factor-2 identifies the CONVENTION: the unordered
  count satisfies r(n) ~= C2 * sg * J(n), i.e. obs/(C2*sg*J) = 0.994-0.995, stable to
  +-0.001 across 2.5 decades. The residual -0.5% is finite-size (small-prime edge terms),
  shrinking slowly.
- S = n/ln^2 n (the spec's shape form): median ratio drifts 1.309 -> 1.127 with no
  plateau in range — the SAME lesson Elenchus taught on 0058 (x/ln^2 x under-integrates;
  li-type predictors converge, shape forms drift for any feasible range).

Reading: R2 = HL-CONSISTENT under the integral predictor (flat, tight, convention
identified empirically); the shape-form drift is EXPECTED normalization behavior, not an
HL deviation. No factorization-structured residual beyond the singular series was
detected at this sample size.

## NOT claimed
Nothing here bears on binary Goldbach's truth. Part A is a range consistency check far
inside the verified frontier. Part B says the mirror of reality in [1e3,1e8] matches the
HL singular-series prediction to ~0.5% under the correct normalization — a statement
about the PREDICTION's empirical quality, not the conjecture's status.

## Residue (method, consumable)
1. The 0058 li-lesson GENERALIZES: for any HL-family count, compare against the integral
   predictor; shape forms n/ln^k n produce phantom drift at every feasible range.
2. Convention-flip on the ordered/unordered factor resolves itself empirically in one
   run — build the ambiguity INTO the instrument instead of adjudicating from memory.
3. Max-smallest-partner (1093 at 1e8) is a cheap byproduct curve worth accumulating at
   higher ranges if this attack ever scales — it tracks the effective difficulty of
   greedy decomposition.

## Trace-vector record
problem_id: CAT-MATH-0057 | tier_probe: consistency+distributional | answer_correct: n/a (empirical attack)
domain_constraints_detected: [ordered-unordered-convention-ambiguity, shape-vs-integral-normalization, even-prime-edge-case]
operations_used: [euler-product-constant-derivation, vectorized-partner-elimination, dual-implementation-calibration, convention-flip, stratified-sampling]
kill_pattern: none fired (one guard-caught instrument bug, fixed pre-result) | repair_available: n/a
confidence_calibration: Part B integral-ratio stability +-0.001 over 2.5 decades; claims scoped to range
residue: li-generalization + built-in convention-flip (both above)
