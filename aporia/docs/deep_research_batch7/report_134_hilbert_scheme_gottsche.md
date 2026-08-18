# Deep Research Report #134: Hilbert Scheme Göttsche Generating Function — Euler Characteristic Sequences for Hilb^n(K3)

**Target Agent:** Ergon
**Date:** 2026-04-23
**Budget:** ~4 CPU-hours

## 1. Problem Statement

Göttsche (1990) gives closed-form generating function for topological Euler characteristics of Hilbert schemes of points on a smooth projective surface S:

    Σ_{n≥0} χ(Hilb^n(S)) q^n = ∏_{m≥1} 1/(1 − q^m)^{χ(S)}

For S = K3 with χ(K3) = 24:

    Σ_{n≥0} χ(Hilb^n(K3)) q^n = ∏_{m≥1} 1/(1 − q^m)^{24} = q/Δ(τ)

where Δ(τ) is modular discriminant (weight 12 cusp form). Exact η-product: η^{-24} up to normalization. **Verification task:** compute χ(Hilb^n(K3)) for n=1..50, confirm match with η^{-24} coefficients, characterize residuals under null battery.

Pure arithmetic verification: fetch OEIS A006922, generate η-product coefficients via power series, diff at arbitrary precision. Ergon's core competence.

## 2. Literature

- **Göttsche (1990)** Math. Ann. 286: original formula; proof via Weil conjectures + stratification by partition type.
- **Cheah (1996)** J. Alg. Geom. 5: generalizes to higher-dim schemes, motivic refinement. Whether K3 specialness is coincidence of χ=24 or deeper.
- **Nakajima (1997)** Ann. Math. 145: Heisenberg algebra action on ⊕_n H*(Hilb^n(S)); representation-theoretic derivation. η-product origin as Fock space character.
- **Göttsche–Soergel (1993):** Poincaré polynomial refinement.
- **OEIS A006922:** coefficients of 1/η^{24}; equivalently τ(n+1) via Ramanujan cusp form relationship up to sign.

## 3. Data Sources

- **LMFDB:** no direct Hilb^n(K3). Modular form records for Δ (level 1, weight 12) give τ(n) indirectly via η^{24} = Δ.
- **OEIS:** A006922 (Göttsche K3), A000594 (Ramanujan τ), A008653 / A027364 (partition-weighted Euler char generating functions).
- **Independent compute:** expand ∏(1−q^m)^{-24} to order 50 via Python `sympy.series` or direct convolution; cross-check A006922.

## 4. Test Design

1. **Generate predictions:** coefficients c_n of ∏_{m=1}^{60}(1−q^m)^{-24} truncated at q^{50}. Exact integer arithmetic.
2. **Fetch OEIS A006922:** first 50 terms.
3. **Equality check:** c_n == A006922(n) for n=1..50. Any mismatch falsifies Göttsche as stated or reveals indexing convention bug.
4. **Cross-check via τ:** q · η^{-24}(τ) = 1/Δ(τ); verify c_n · τ-relation via convolution identity: f(q) · Σ τ(n) q^n = 1. Testable to n=50.
5. **Null battery:**
   - Permutation null on OEIS sequence (expected 0/1000 matches).
   - Prime detrend: regress log(c_n) against n, π(n), Ω(n); residuals structureless.
   - Alternative surfaces: Enriques χ=12, P² χ=3. Each matches own Göttsche form, not K3's.
6. **Asymptotic:** Hardy-Ramanujan c_n ~ (2π)^{13}/(√2 · Γ(12)) · n^{-27/4} · exp(4π√n). Fit log c_n → a√n + b log n + c; a ≈ 12.566, b ≈ -6.75.

## 5. Falsification

Falsified if any:
- c_n ≠ A006922(n) for 1 ≤ n ≤ 50 after convention-alignment.
- Convolution identity with τ(n) fails.
- Permutation null produces spurious matches > 0.1%.
- Hardy-Ramanujan exponent deviates > 5% from 4π after n ≥ 20.

35-year-old theorem with multiple independent proofs; falsification most plausibly indicates data-pipeline bug (OEIS version skew, sympy truncation). Log as infrastructure issue, not mathematical.

## 6. Budget

- Power series to q^{50} with 24th power: ~30 CPU-s sympy, < 1s FLINT.
- OEIS fetch + diff: < 1 min.
- Null battery (5 alt surfaces × 1000 perms): ~2 CPU-hr.
- Asymptotic fit + residual: ~30 min.
- Writeup + registration: ~1 CPU-hr.
- **Total: ~4 CPU-hr.**

## 7. Expected Outcome

**Primary:** exact match for all n=1..50. Calibration test, not discovery. Value:
1. Confirms Aporia η-product handling before applying to Göttsche–Nakajima for non-K3 hyperkähler, Noether–Lefschetz.
2. Clean "truth anchor" in Megethos space — K3 Hilb^n as known-modular benchmark for prime-detrending.
3. Wires Heisenberg-algebra correspondence (Nakajima) into Ergon concept graph for Techne operator-category work.

**Secondary (unlikely):** 24-factorization failure = infrastructure discovery; investigate before any new claim elsewhere.

Register result in null_protocol as PATTERN_GOTTSCHE_K3_VERIFIED, anchor level 1.

**Word count: 747**
