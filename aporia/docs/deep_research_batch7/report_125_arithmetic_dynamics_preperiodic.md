# Deep Research Report #125: Arithmetic Dynamics Preperiodic Density — Morton-Silverman at Scale

**Target agent:** Ergon
**Date:** 2026-04-23
**Budget:** ~1 day

## 1. Problem Statement

For morphism f: P^1 → P^1 of degree d ≥ 2 over number field K, a point P ∈ P^1(K) is **preperiodic** if forward orbit {f^n(P) : n ≥ 0} is finite. **Morton-Silverman Uniform Boundedness (1994):**

> ∃ C(d, D) such that for every number field K with [K:Q] = D and every degree-d morphism f: P^1 → P^1 over K: |PrePer(f, P^1(K))| ≤ C(d, D).

Bound depends only on degree of map and degree of field — independent of f. Generalizes Merel's EC torsion theorem (d=4 Lattès case) to arbitrary rational dynamics.

**Completely open** even for f(z) = z² + c over Q.

## 2. Literature

- **Morton-Silverman (1994)** IMRN: original statement; bounds depending on bad-reduction primes.
- **Benedetto (2007)** Crelle 608: polynomials of degree d ≥ 2 over K have |PrePer(f, K)| ≤ O(d · log d · #S_bad). Not uniform, critical partial.
- **Poonen (2012):** for z² + c over Q, conjectures |PrePer| ≤ 9; classifies portrait shapes (N-cycles N ∈ {1,2,3}).
- **Benedetto-Ghioca-Kurlberg-Tucker (2014):** averaging arguments; random f of fixed degree has preperiodic count O(1).
- **Hutz (2015):** Sage algorithms for rational preperiodic enumeration via height bounds (ĥ_f vs h_Weil).
- **Doyle-Faber-Yasufuku (2019):** Poonen extension to quadratic NF; new portraits for specific D=2.

## 3. Map Generation

LMFDB dynamics tables sparse. Generate:

- **A:** f(z) = z² + c, c ∈ Q, H(c) ≤ 50. ~2500 maps.
- **B:** f(z) = z³ + az + b, |a|,|b| ≤ 20. ~1600 maps.
- **C:** f(z) = (z² + a)/(z² + b). ~3000 maps.
- **D:** Random degree-2 Chebyshev + Lattès. ~1500 maps.
- **E:** LMFDB curated + Hutz corpus. ~1400 maps.

Target: ~10K maps.

## 4. Test Design

Per map f:
1. Canonical height: Hutz bound ĥ_f(P) ≥ h(P) − C_f; search bound for preperiodic.
2. Enumerate P ∈ P^1(Q) with h(P) ≤ C_f.
3. Iterate f up to N = 2·(degree bound) times; check cycle entry.
4. Extend to K = Q(√D) for D ∈ {−1, −2, −3, 2, 3, 5}; NF-aware height bounds.
5. Record |PrePer(f, K)|, portrait shape, cycle lengths, tree depth.

Infrastructure: Sage `DynamicalSystem`, 8-core parallel, → `ergon/dynamics_preperiodic_10k.jsonl`.

Histograms by (d, D).

**Targets:**
- **H1:** d=2, D=1: max |PrePer| ≤ 9 (Poonen).
- **H2:** d=2, D=2: max |PrePer| ≤ 15 (Doyle-Faber-Yasufuku extrapolation).
- **H3:** d=3, D=1: max |PrePer| ≤ 12 (conjectural).

## 5. Falsification

**Discovery:** map f with |PrePer| exceeding hypothesis → headline Morton-Silverman falsification.
- z² + c over Q with > 9 preperiodic → kills Poonen refined.
- Degree-3 polynomial over Q with > 12 → new publishable data.

Controls: verify canonical-height bounds tight; duplicate enumeration via PARI on 10% sample.

## 6. Budget

~1 day on 8-core:
- 4h corpus + canonical height precomputation.
- 12h enumeration over Q for 10K maps.
- 6h NF extension sweeps for 2500 quadratic polynomials.
- 2h aggregate + portrait distribution + outlier flagging.

## 7. Expected Outcome

**85%:** empirical bounds hold; histogram peaks at |PrePer| ∈ {3,5,7} for d=2/Q; Benedetto's log-d·(bad primes) scaling on average. Value: calibrates conjecture for Harmonia (modular form coupling) and Charon (spectral ↔ dynamical bridges).

**12%:** one or two near-boundary examples (|PrePer| = 9 for new c, or novel portrait). Bridge to OEIS / Poonen catalog.

**3% jackpot:** genuine bound-violator. Major result, IMRN or J. Number Theory — direct strike against uniform boundedness.

**Null:** permutation by randomizing coefficients within height shells; verify |PrePer| distributions not enumeration-order artifacts.

**Word count: 798**
