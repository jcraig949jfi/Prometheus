# Report #96: Jacobian of Genus-3 Hyperelliptic Curves — Empirical Statistics and USp(6) Comparison

**Target agent:** Ergon
**Date:** 2026-04-23

## 1. Precise Problem Statement

First empirical statistics of L-function coefficients for Jacobians of genus-3 hyperelliptic curves `y^2 = f(x)` (deg f ∈ {7,8}) over Q, at a scale uncorrupted by LMFDB selection bias (no systematic g=3 hyperelliptic table). The Jacobian `J = Jac(C)` is a 3-dim abelian variety; its L-function has analytic conductor of degree 6. Katz–Sarnak predicts that over a natural family ordered by conductor, normalized traces `a_p / (2 sqrt(p))` populate USp(6) Haar measure, with low-lying zero statistics matching the symplectic ensemble. This report specifies a 10K-curve experiment.

## 2. Literature Context

- **Katz–Sarnak (1999)** *Random Matrices, Frobenius Eigenvalues, and Monodromy* — USp(2g) symmetry for Jacobian families.
- **Shanks/Birch heuristics** — Sato–Tate for genus-g → USp(2g).
- **Harvey–Sutherland (2014, 2016)** — `smalljac` and `hypellfrob` average-polynomial-time point counting, ~O(p^{1/2+o(1)}) per prime.
- **Kedlaya–Sutherland (2009)** — Sato–Tate groups for abelian surfaces; g=3 classification by Fité–Kedlaya–Rotger–Sutherland (2012).
- **Rubinstein (2001), Miller (2008)** — 1-level density methodology for symplectic families.

## 3. Computational Test Design

**Curve sample.** 10,000 g=3 hyperelliptic curves via random `f(x)` degree 7, integer coefficients uniform in [-H, H], H chosen so discriminant is squarefree (reject ~40%). Enforce generic endomorphism ring by discriminant genericity. Compute conductor via Magma or Pari `hyperellcharpoly`.

**a_p computation.** Per curve, `a_p = p^3 + 1 - #C(F_p) − (Jacobian Euler factor contribution)` via Harvey–Sutherland `smalljac` for p ∈ [5, 2^14]. Normalize `theta_p = a_p / (2 sqrt(p) · 3)` (trace of 6×6 unitary symplectic matrix).

**Statistics.**
- Sato–Tate moments: E[tr^k] for k = 1..8.
- 1-level density: first 5 zeros per curve via approximate functional equation + `lcalc`; compare to symplectic kernel `1 − sin(2πx)/(2πx)`.
- Distribution of `a_p/p^{3/2}` vs USp(6) Weyl integration measure.

**Null comparisons.** Dirac 0 (trivial), N(0,1) (SO(3)), USp(4) (wrong dim), GL(6) unitary.

## 4. Falsification Criteria

USp(6) rejected if any of:
- E[tr^2] deviates from **1** by > 3σ (σ ≈ 0.03 at N=10K).
- E[tr^4] deviates from **3** by > 3σ.
- E[tr^6] deviates from **15** by > 3σ.
- 1-level density at origin shows SO(even) suppression or SO(odd) enhancement.
- KS distance empirical θ_p vs USp(6) Haar > 0.03.

Subtler falsification: if family fractures into detectable sub-components (extra endomorphisms correlated with coefficient parity), report discrete Sato–Tate groups per FKRS.

## 5. Expected Outcome

Theoretical USp(6) trace moments (Weyl integration on Sp(6)):
- E[tr] = 0, E[tr^2] = 1, E[tr^3] = 0, E[tr^4] = 3, E[tr^5] = 0, E[tr^6] = 15.

Expect empirical moments within 3σ. 1-level density matches symplectic. Deviations localized to reduction types (e.g., Jacobian isogenous to E × A_2) flag Sato–Tate substructure for Charon cross-check against FKRS classification.

## 6. Budget

- **Compute:** ~40 CPU-hours on Skullport (smalljac single-threaded; 16-core parallel → ~2.5 wallclock hours). Zero GPU.
- **Storage:** ~80 MB (10K curves × ~1600 primes × 5 bytes).
- **Wallclock:** 3 hours generation + 30 min analysis.
- **Risk:** ~5% reducible Jacobians (split into E × J_2); flag and analyze separately.
- **Deliverable:** `ergon/results/g3_hyperelliptic_usp6.json` with moments, KS distances, density data.

**Word count: 737**
