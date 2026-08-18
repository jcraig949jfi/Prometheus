# Report 79: Unitary +ρ Despite Zero Katz-Sarnak 2-Point Correction

**For:** Harmonia  **Date:** 2026-04-23  **Axis:** F011 / 3b

## 1. Problem Statement

Under Katz-Sarnak (KS) heuristics, a family F of L-functions is assigned a symmetry type G ∈ {U, O±, USp}, and the 2-point correlation of low-lying zeros, in the scaling limit N → ∞, satisfies

R_2(G; x) = 1 − (sin πx / πx)² + ε_G · K(x),

with ε_G · K the family-averaged correction: positive for O±, zero for U, negative for USp (Katz-Sarnak 1999, §3.3; Conrey-Snaith 2007). The observed empirical correlation is Spearman(nbp, local-gap-variance deficit at 24-gap window) ≈ +1.000 per-curve for both the complex Dirichlet sample (n=40K) and the real-quadratic Dirichlet sub-sample (n=3898). The mystery: U has **zero** family-average correction, yet the per-curve ρ is saturated at +1, identical in magnitude and sign to the O-class curves.

## 2. Literature Anchors

- **Katz-Sarnak 1999** (Bull. AMS 36, "Zeroes of zeta functions and symmetry"), §3.3: pair-correlation kernels for classical compact groups; U(N) has universal GUE 2-point and no family-level KS correction.
- **Iwaniec-Luo-Sarnak 2000** ("Low lying zeros of families of L-functions", Publ. IHÉS 91): 1-level densities for GL(2) families; U-type families (primitive Dirichlet) appear with support-restricted test functions.
- **Rubinstein 2001** (Duke Math. J. 109, "Low-lying zeros of L-functions and random matrix theory"): numerical verification of KS for Dirichlet; finite-conductor deviations are O(1/log C).
- **Conrey-Farmer-Keating-Rubinstein-Snaith 2005** (Proc. LMS 91, "Integral moments of L-functions"): CFKRS recipe yields lower-order, prime-dependent terms for U-family moments nonzero at finite conductor, feeding into 2-point statistics as arithmetic corrections distinct from the KS kernel.
- **Shin-Templier 2016** (Invent. Math. 203): universality of symmetry type for very general families; per-element fluctuation is controlled by an arithmetic factor a_F(p).

Key insight: the KS kernel ε_G · K is a **family-mean** correction. Per-L-function deviations are governed by the CFKRS arithmetic factor, which is nonzero even for U.

## 3. Candidate Hypotheses and Discriminators

**(i) Finite-N wash-out.** LMFDB Dirichlet conductors are bounded (C ≲ 10⁴–10⁵); the O(1/log C) Rubinstein correction could masquerade as a U-family 2-point effect.
 - *Test:* stratify n=40K by conductor into ≥5 bins, recompute ρ in each. Monotone decay with C confirms finite-N.
 - *Falsifier:* ρ stays ≈+1 across all conductor bins → not finite-N.

**(ii) Higher-order correlations.** U has nonzero 3- and 4-point connected correlators (Mehta 2004, Random Matrices, Ch. 5-6). A 3-point contribution to local-gap-variance deficit could couple to nbp per-curve even when 2-point averages to zero.
 - *Test:* Spearman(nbp, 3-point correlation deficit at 24-gap). |ρ_3| > 0.5 ⟹ higher-order is a live driver.
 - *Falsifier:* ρ_3 ≈ 0 while ρ_2 = +1 → mechanism is NOT higher-order RMT.

**(iii) Conductor-ordering artifact.** LMFDB Dirichlet is conductor-ordered. Both nbp (rises with C) and local-gap-variance deficit (depends on truncation depth × zero density × log C) rise monotonically with C. A spurious ρ = +1 could arise from co-monotonicity with C alone.
 - *Test:* partial Spearman ρ(nbp, deficit | C), or resample within fixed C-bins.
 - *Falsifier:* partial ρ → 0 → we were measuring conductor-correlation, not symmetry-class signal.

**(iv) Mechanism is Euler-factor simplification, not 2-point.** "nbp" counts primes dividing the conductor where the local Euler factor degenerates (L_p(s) = 1 for p | N). Each bad prime removes an oscillatory term from the explicit formula, mechanically reducing local gap variance — independent of KS symmetry type. The O/Sp sign match would then be coincidence driven by direction of monotonicity (more bad primes ⟹ less oscillation ⟹ deficit increases), which points the same way for O, U, and Sp-like Dirichlet subfamilies.
 - *Test:* Spearman(Ω(N), deficit) on a NON-L-function surrogate — CUE zeros with artificial "bad-prime" tagging. Persistence without symmetry class confirms (iv).
 - *Reframing:* deficit ≈ α − β · Σ_{p | N} f(p), independent of ε_G.
 - *Falsifier:* surrogate shows ρ ≈ 0 but real data shows +1 → symmetry-class content is real.

## 4. Recommended Priority

**Run (iii) first** — partial Spearman is trivial and addresses the most mundane alternative. If (iii) survives, run (iv) next: it is the deepest reframing and would realign the F011 claim from "2-point correlation structure tracks nbp" to "Euler-factor simplification tracks nbp; the KS sign match is a direction-of-monotonicity coincidence for O and Sp." Hypothesis (i) is secondary because Rubinstein's bound is weaker than the observed effect size. Hypothesis (ii) is the most interesting IF (iii) and (iv) are ruled out.

## 5. Connection to F011 Axis 3b

Axis 3b asserts per-curve arithmetic (nbp) couples to KS 2-point structure in a sign-matched way. The U anomaly is the **critical falsifier**: if U shows +ρ for reason (iv), the O/Sp sign-match is numerology and Axis 3b collapses into a weaker, more honest claim about Euler-product depletion. This is the same class of kill as Harmonia Attack 4 on NF backbone (see `feedback_permutation_null.md`): a partial-correlation null dissolves the apparent symmetry-class signal. Recommend NOT publishing F011 Axis 3b until tests (iii) and (iv) are executed.

**Word count: 780**
