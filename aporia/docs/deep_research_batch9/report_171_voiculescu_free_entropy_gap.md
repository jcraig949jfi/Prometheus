# Deep Research Report #171: Voiculescu Free Entropy Gap

**Target Agent:** Harmonia
**Date:** 2026-04-26
**Front:** Operator algebras (Batch 9 Tier 3)
**Predecessor:** Batch 1 #3 (Connes Embedding Problem)

## 1. Problem Statement

For an n-tuple (X_1,...,X_n) of self-adjoint elements in a tracial von Neumann algebra (M, τ), Voiculescu's **free entropy** is

  χ(X_1,...,X_n) = lim sup_{N→∞} (1/N²) log Vol(Γ_R(X_1,...,X_n; N, k, ε)) + (n/2) log N,

where Γ_R is the set of microstates — n-tuples (A_1,...,A_n) ∈ M_N(C)^n_{sa} with operator norm ≤ R whose mixed moments of length ≤ k approximate τ(X_{i_1}...X_{i_k}) within ε. The **maximum** χ_max(R) is achieved exactly when (X_1,...,X_n) is free semicircular of radius R; here χ takes the explicit Voiculescu value (n/2) log(2πeR²/4).

**Voiculescu's open question (the "free entropy gap"):** does there exist ε > 0 such that no n-tuple in any tracial von Neumann algebra has free entropy strictly inside (χ_max − ε, χ_max)? Equivalently, is χ_max an *isolated* point of the χ-spectrum, analogous to spectral gaps for von Neumann entropy and Pinsker-type inequalities? A positive gap would constrain the structural region adjacent to free-semicircular models and would have consequences for non-Γ classification, L²-Betti numbers, and free Stein dimension.

## 2. Literature

- **Voiculescu (1994, 1996, 1998, 2002):** the free entropy series; definition, additivity for free families, semi-continuity defects, microstates vs. non-microstates approaches.
- **Connes-Shlyakhtenko (2005):** L² rigidity and free entropy dimension δ★; ties χ to first L²-Betti number.
- **Jung (2007):** microstates uniqueness; if χ(X) = χ_max then (X) is free semicircular — pointwise rigidity, but no quantitative ε.
- **Hayes (2018):** free Stein dimension; provides a related quantity that often agrees with δ★ and is computable.
- **Ji-Natarajan-Vidick-Wright-Yuen (2020):** MIP*=RE collapses Connes Embedding; reshapes the microstate landscape — non-Connes-embeddable algebras have χ = −∞ trivially, so the gap question lives entirely inside the Connes-embeddable slab.

## 3. Computational Handle

Free entropy is not directly computable, but the **gap** question is testable via Monte Carlo over microstate spaces:

- (a) Sample tracial von Neumann algebras with explicit moment data: free groups F_n, surface group ℤ²★ℤ, finite-group vN algebras (S_5, A_6, dihedral), q-Gaussian deformations for q ∈ (-1,1), and Voiculescu's free Poisson.
- (b) For each, generate large-N microstates by GUE/Haar sampling and rejection on moment constraints.
- (c) Estimate (1/N²) log Vol via importance sampling or replica-style volume ratios at N = 50, 100, 200; extrapolate.
- (d) Histogram χ̂ across the ~50 algebras and inspect the upper edge.

## 4. Test Design

**Step 1.** Curate ~50 candidate tracial vN algebras, n ∈ {2, 3, 4}: free groups F_n; free products of finite groups (ℤ/p ★ ℤ/q); group vN algebras of small hyperbolic / surface groups; q-Gaussians on a 5-point q grid; finite-dim direct sums as controls (χ = −∞).

**Step 2.** For each, compute target moments τ(X_{i_1}...X_{i_k}) up to k = 8 from group/free-product combinatorics.

**Step 3.** Microstate Monte Carlo at N ∈ {50, 100, 200}: sample (A_1,...,A_n) GUE-distributed, weight by Gaussian-kernel match to target moments at tolerance ε; estimate log-volume via ratio with reference free-semicircular weight. Normalize by N².

**Step 4.** Plot histogram of χ̂ − χ_max across the 50 algebras. Look for a forbidden band (-ε, 0).

**Step 5.** Structural stratification: classify which algebras land near the edge by L²-Betti number, free Stein dimension (Hayes), and amenability.

## 5. Falsification

- **Empirical gap:** clear bimodality with a forbidden band of width ≥ 0.05 → numerical support for Voiculescu's gap conjecture; flag the algebras nearest the edge for analytic follow-up.
- **Continuous distribution to χ_max:** density of χ̂ on (χ_max − ε, χ_max) for arbitrarily small ε → counterevidence; identify the saturating sequence.
- **Edge saturators:** specific non-semicircular algebras within < 0.01 of χ_max with isolation > ε from the bulk → publishable as candidate near-extremal examples.
- **Null:** finite-dimensional controls must return χ̂ → −∞ as N grows; failure invalidates the volume estimator.

## 6. Budget

Harmonia ~1 day. NumPy + SciPy Monte Carlo, no external solvers. Matrix-MC code ~3 h; parallel runs across ~50 algebras at three N values ~3 h compute on workstation GPU (or CPU pool); distribution analysis and stratification ~1 h; writeup ~1 h.

## 7. Expected Outcome

First empirical map of Voiculescu free entropy near its maximum across ~50 tracial von Neumann algebras. Adds the first dense **structural-region** data points to the operator-algebra slab of the unified tensor — currently almost empty per `project_silent_islands` (operator algebras isolated). Whether the histogram shows a gap or not, the result is a calibrated χ-distance against which future tracial samples can be placed; cross-link target is the spectral-gap literature for II_1 factors (property (T), non-Γ, strong solidity), where any algebra found near the edge becomes a candidate for joint analysis with Hayes's free Stein dimension. Per `feedback_tensor_first`, the histogram itself — not the conjecture verdict — is the deliverable.

**Word count: 798**
