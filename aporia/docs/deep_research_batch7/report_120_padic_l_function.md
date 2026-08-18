# Deep Research Report #120: p-adic L-function at LMFDB Scale

**Target Agent:** Charon
**Topic:** Mazur-Tate-Teitelbaum zeros across 10^4 ordinary elliptic curves
**Date:** 2026-04-23

## 1. Problem Statement

p-adic BSD (MTT formulation): for E/Q with good or multiplicative ordinary reduction at p, the p-adic L-function L_p(E, s) satisfies

    ord_{s=1} L_p(E, s) = rank E(Q) + δ_E(p)

where δ_E(p) = 1 if E has split multiplicative at p (exceptional zero) and 0 otherwise. Any deviation — order exceeding this prediction — would be a genuine extra zero beyond MTT or p-adic BSD failure. At LMFDB scale (~10^4 curves, multiple primes), empirical frequency of such deviations is not catalogued.

**Q:** does MTT hold exactly as stated across a representative sweep, or are there systematic exceptional phenomena the theory hasn't absorbed?

## 2. Literature

- **Mazur-Tate-Teitelbaum (1986):** original L_p(E, s) via modular symbols; p-adic BSD including exceptional zero at split multiplicative. L-invariant L(E, p).
- **Greenberg-Stevens (1993):** proved exceptional zero conjecture L_p'(E, 1) = L(E, p) · (L(E,1)/Ω_E) for split multiplicative, rank 0.
- **Kato (2004):** p-adic zeta element; one divisibility in main conjecture for ordinary E; ord_{s=1} L_p ≥ rank + δ under mild hypotheses.
- **Skinner-Urban (2014):** reverse divisibility for most ordinary; closes Iwasawa main conjecture; exact MTT prediction broadly.
- **Pollack-Stevens (2011, 2013):** overconvergent modular symbols algorithm — practical L_p(E, s) engine; feeds LMFDB `ec_iwasawa`.

Theoretical prediction nearly proven; LMFDB-scale test calibrates residual cases.

## 3. LMFDB Data

`ec_iwasawa` (Postgres mirror):
- `lmfdb_label`, `p`
- `reduction_type` (ordinary good / split mult / nonsplit mult / supersingular / additive)
- `lambda_invariant`, `mu_invariant`
- `L_p_values` (truncated expansion at s=1)
- Join `ec_curvedata` for rank, conductor, torsion.

Primes p ∈ {3, 5, 7} well-populated. Filter `reduction_type IN ('ordinary', 'split_multiplicative')` and p ∤ N for good reduction → ~10^4-10^5 (curve, p) pairs in 11 ≤ N ≤ 10^7.

## 4. Test Design

**Sample:** 10K ordinary (curve, p) pairs stratified log_10(N) ∈ [1, 7], ~uniform per decade, ranks 0-3 natural frequencies + oversample rank ≥ 2.

**Measurement:** predicted order r_MTT = rank + δ_E(p). Empirical r_emp from `lambda_invariant` (when positive) or first non-zero coefficient of L_p expansion in `L_p_values`. Agreement requires r_emp = r_MTT.

**Strata:**
- Good ordinary, rank 0 (r_MTT = 0; sensitive to trivial zero anomalies).
- Good ordinary, rank 1 (r_MTT = 1).
- Split mult, rank 0 (r_MTT = 1, exceptional zero — Greenberg-Stevens).
- Split mult, rank ≥ 1 (r_MTT = rank + 1).
- Rank ≥ 2 across all reduction types (least tested).

**Null:** random pairing r_MTT ↔ r_emp within conductor bins; MTT agreement vs chance.

## 5. Falsification

Falsified if any:
- Good-ordinary curve r_emp > rank with no split-mult explanation (genuine extra zero).
- Rank-0 good-ordinary r_emp ≥ 1 (L-invariant pathology outside theory).
- Systematic bias: > 1% disagreement in any stratum above Monte Carlo noise (expect ≪ 0.1% per Skinner-Urban).
- Conductor-dependent drift: disagreement rising with log N.

Mandatory: permutation null over 1000 shuffles; sampling replicated across 5 seeds.

## 6. Budget

- SQL extraction + join: 30 min.
- Parse L_p_values + extract r_emp (10K pairs): ~2 CPU-hr.
- Stratified analysis + permutation (5 × 1000 shuffles): ~2 CPU-hr.
- Sage `E.padic_lseries(p).series()` verification on 200 random: ~1.5 CPU-hr.
- **Total: ~6 CPU-hours.** Zero API cost.

## 7. Expected Outcome

Most likely: > 99.9% MTT agreement, confirms Skinner-Urban theoretical coverage empirically. Value: calibration — establishes Charon battery's baseline for a "solved" p-adic prediction, against which novel p-adic claims (e.g., `project_padic_symmetry_signal` r=0.339) can be benchmarked. Secondary: residual disagreements flag curves where IMC hypotheses fail (p | #E(F_p)_tors, non-squarefree at p) — clean exceptional-case list.

If disagreement > 0.1% in any stratum → genuine anomaly, Aporia escalation. Per assume-wrong doctrine, expect confirmation + sharpen null, not new ground.

**Word count: 798**
