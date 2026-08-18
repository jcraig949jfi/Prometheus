# Deep Research Report #127: Higher L-function Moments for Rank-0 EC Families

**Target Agent:** Charon
**Date:** 2026-04-23
**Topic:** Extending Conrey-Keating-Snaith moment conjectures to M_6, M_8

## 1. Problem Statement

CKS philosophy: moments of L-functions at central point, averaged over natural families, match moments of characteristic polynomials of random matrices from family's symmetry group. For rank-0 EC ordered by conductor, family has **orthogonal symmetry** (SO(even) for even functional-equation sign). Moment conjecture:

    M_k(X) := (1/|F(X)|) Σ_{E ∈ F(X), r_E=0} L(E,1)^k ~ a_k g_k (log X)^{k(k-1)/2}

where g_k is the matrix-integral factor (Keating-Snaith), a_k arithmetic factor (Euler product).

- **M_2, M_4:** Rubinstein (2001) numerical agreement within 1-3% at moderate conductor.
- **M_6:** conjectural. g_6 = 11! / ∏_{j=0}^5 (2j+1)! times orthogonal correction; full CKS (2005).
- **M_8:** conjectural. Numerically untested at LMFDB scale; Hughes-Young (2010) orthogonal refinement.

**Test:** compute M_6, M_8 over 10^5 rank-0 EC in LMFDB; compare to CKS prediction with symmetry-matched RMT null.

## 2. Literature

- **Conrey-Keating-Snaith (2000)** "Integral moments of L-functions": full moment conjecture including lower-order terms via recipe.
- **Conrey-Keating-Snaith (2005)** "Moments of zeta and L-functions": general families, orthogonal/symplectic/unitary cases.
- **Rubinstein (2001)** PhD thesis: first numerical M_2, M_4 for quadratic twist and conductor-ordered EC.
- **Hughes-Young (2010)** "Twisted fourth moment of Riemann zeta": orthogonal moment machinery applicable here.
- **Conrey-Farmer-Keating-Rubinstein-Snaith (2005):** Dirichlet series recipe for arithmetic factor.
- **Bui-Keating (2023):** recent progress on thin-family moments.

## 3. LMFDB Data Inventory

Via devmirror:
- `ec_curvedata`: ~3.8M curves, filter `rank = 0`.
- `special_value` or `lfunctions.central_value`: L(E,1) ~20 digits.
- Target: ~10^5 rank-0 curves, conductor N ≤ 10^6, binned log-conductor windows [X, 2X] with X ∈ {10^3, 10^4, 10^5} for scaling.
- Sign from `root_number` column; restrict w=+1 for rank-0 consistency.

## 4. Test Design

**Step 1 — Moment computation.** For each conductor bin B_X = [X, 2X]:
- Empirical M̂_k(X) = |B_X|^{-1} Σ_{E ∈ B_X} L(E,1)^k for k ∈ {2,4,6,8}.
- Validate against M_2, M_4 (Rubinstein baseline) before trusting M_6, M_8.

**Step 2 — CKS prediction.** Compute a_k g_k (log X)^{k(k-1)/2}:
- g_k orthogonal-SO(even): closed form from Keating-Snaith matrix integral.
- a_k: Euler product over primes p ≤ 10^4 with local factors from a_p column.

**Step 3 — Bootstrap.** Resample within each bin 1000×; 95% CI on M̂_k. Report M̂_k / CKS(X) with confidence band.

**Step 4 — Symmetry-matched RMT null.** 500 SO(2N) characteristic polynomials with N ~ log X / 2; compute moments; compare to bin-level prediction. Key: **orthogonal** null, not unitary — unitary would be wrong-symmetry control.

**Step 5 — Scaling law.** Regress log M̂_k on log log X; slope should equal k(k-1)/2. Deviation > 3σ flags failure.

## 5. Falsification Criteria

- **Pass:** |M̂_k / CKS(X) − 1| < 0.1 across all 3 bins for k=6,8; scaling exponent matches k(k-1)/2 within bootstrap CI.
- **Soft fail:** M_6 passes, M_8 deviates — finite-N effect in tail; report as data point.
- **Hard fail:** both M_6, M_8 miss > 3σ — either CKS arithmetic factor wrong, or orthogonal symmetry assumption fails (family is union of symmetry types).
- **Null check:** unitary RMT null must fail (confirms detecting orthogonal structure, not generic heavy-tail).

Apply standard battery: permutation null + prime detrending.

## 6. Budget

- Query 10^5 rows + a_p for p ≤ 10^4: ~5 min.
- Moment computation (vectorized): ~30 min.
- Bootstrap (1000 × 3 bins × 4 moments): ~2 CPU-hr.
- RMT null generation (500 SO(2N) samples): ~4 CPU-hr.
- Analysis + battery: ~1.5 CPU-hr.
- **Total: ~8 CPU-hr**, overnight on either machine.

## 7. Expected Outcome

Most likely: M_6 agrees within 5-10%, M_8 deviates 15-25% due to finite-conductor tail (large-L(E,1) curves dominate high moments — known "realization speed" problem). **First LMFDB-scale test of M_6/M_8** for EC; probes whether CKS arithmetic factor extrapolates correctly.

Side product: L(E,1)-tail curves driving M_8 are sparse sleeper candidates with outsized moment contribution. Feeds silent-islands catalog.

If CKS fails cleanly, deviation pattern (sign, scaling) diagnoses which ingredient is wrong: orthogonal assumption, arithmetic factor, lower-order terms. Each publishable.

**Word count: 758**
