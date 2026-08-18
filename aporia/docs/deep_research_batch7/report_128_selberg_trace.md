# Deep Research Report #128: Selberg Trace Formula Empirics — PSL(2,Z) Laplace Spectrum

**Target Agent:** Ergon
**Date:** 2026-04-23
**Topic:** Low-lying zero statistics for Laplace spectrum on Γ\H, Γ = PSL(2,Z)

## 1. Problem Statement

Γ = PSL(2,Z) acts on upper half-plane H by Möbius. Γ\H is non-compact hyperbolic of volume π/3 with single cusp. Hyperbolic Laplacian Δ = −y²(∂²_x + ∂²_y) has:

- **Continuous spectrum:** [1/4, ∞) from Eisenstein E(z, 1/2 + it).
- **Discrete spectrum:** λ_j = 1/4 + r_j² with r_j > 0, corresponding to Maass cusp forms φ_j.

Selberg trace formula relates Σ over r_j to Σ over conjugacy classes in Γ (hyperbolic = closed geodesics, elliptic = fixed points, identity, parabolic = cusp).

**Q:** do low-lying r_j obey GUE pair-correlation, and does trace formula balance numerically to 4-6 digits at 10^4 eigenvalues?

## 2. Literature

- **Selberg (1956)** J. Indian Math. Soc. 20: original trace formula; heuristic that eigenvalues behave like zeta zeros.
- **Cartier–Hejhal (1970s)** Hejhal's *Selberg Trace Formula* (Springer LNM 548, 1001): first computations r_1 ≈ 9.533695, r_2 ≈ 12.173008.
- **Phillips–Sarnak (1985)** Invent. Math. 80: generic deformations destroy cusp forms; PSL(2,Z) non-generic (arithmetic).
- **Bogomolny–Leyvraz–Schmit / Bolte (1990s):** arithmetic quantum chaos — despite classical chaos, PSL(2,Z) spectrum is Poisson-like, not GUE, due to exponential degeneracy from Hecke operators.
- **Booker–Strömbergsson–Venkatesh (2006)** IMRN: rigorous certification of first ~2000 eigenvalues via Hejhal + interval arithmetic.
- **Then (2005, 2012):** computed 10^6+ eigenvalues; confirmed Poisson spacings, cubic moment of Hecke eigenvalues.

## 3. LMFDB Data

`maass_forms` (~20K rows for level 1):
- `spectral_parameter` (r_j, 50-digit low-lying, ~10-digit high)
- `level` (filter level=1 for PSL(2,Z))
- `symmetry` (even/odd under z → −z̄)
- `coefficients` (first ~1000 Hecke a_p)
- `atkin_lehner_eigenvalues` (trivial at level 1)

`maass_forms WHERE level=1 ORDER BY spectral_parameter LIMIT 10000`. Cross-check first 10 against Hejhal Vol. II Table 1.

## 4. Test Design

**Stage A — Pair correlation (2 CPU-hr):**
Load r_1,...,r_{10^4}. Unfold via Weyl: N(r) ~ r²/12 − (2r/π) log(r/e) + O(1). Unfolded spacings s_j = N(r_{j+1}) − N(r_j). Histogram R_2(s) on [0, 3]. **Prediction:** Poisson (e^{−s}), not GUE.

**Stage B — Trace formula consistency (3 CPU-hr):**
Test function h(r) = exp(−r²/T²) with T ∈ {5, 10, 20, 50}:
- Spectral: Σ_{j: r_j < 5T} h(r_j).
- Geometric: identity (vol·h-integral/4π) + hyperbolic (Σ over closed geodesics, lengths ℓ(γ), class-number-weighted per Sarnak) + elliptic (orders 2, 3 from i and ρ) + parabolic (Eisenstein scattering φ'/φ integral).

Closed geodesic lengths from indefinite binary quadratic forms disc D > 0; ℓ = 2 log ε_D where ε_D is fundamental unit. Use LMFDB `nf_fundamental_units` for real quadratic up to D ≤ 10^5.

**Stage C — Hecke degeneracy probe (1 CPU-hr):**
For each r_j, verify Ramanujan |a_p(φ_j)| ≤ 2. Sato–Tate moments Σ a_p²/p ~ log log X.

## 5. Falsification

- Trace residual |spectral − geometric| / |spectral| > 10^{-3} at T=10 after geodesics ℓ < 5T. Sarnak bound gives 10^{-6} achievable.
- Pair correlation χ² vs Poisson p < 0.01 → contradicts arithmetic quantum chaos; re-examine unfolding.
- Ramanujan violation |a_p| > 2 + 10^{-8} for certified eigenvalue → contradicts Kim–Sarnak.
- Weyl count N(R) deviates > O(R / log R) from asymptotic.

**Charon battery:** permutation null on Hecke-spectral coupling; prime-detrended residuals.

## 6. Budget

- Data pull: 15 min.
- Stage A: 2 CPU-hr.
- Stage B: 3 CPU-hr (geodesic enumeration dominates; cache ε_D lookups).
- Stage C: 1 CPU-hr.
- **Total: ~6 CPU-hr**, single machine.

## 7. Expected Outcome

Most likely: trace formula balances to 4-5 digits; pair correlation Poisson with χ² confirming arithmetic quantum chaos. **Calibration anchor**, not discovery — confirms Ergon pipeline reproduces Then (2012). Establishes PSL(2,Z) as clean baseline before probing non-arithmetic Γ (Hecke triangle groups) where GUE should appear.

Interesting if: residuals at T=20 show structure correlated with low-lying zeta zeros (Montgomery analog). Echoes zeros-are-spectrum heuristic; run against permutation null before claiming.

Dead if: LMFDB `maass_forms` has < 500 certified at level 1 — fall back to Hejhal Vol. II tables.

**Word count: 798**
