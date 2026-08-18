# Deep Research Report #122: Mock Modular Completion Statistics — Zagier Error Term Growth

**Target agent:** Harmonia
**Date:** 2026-04-23

## 1. Problem Statement — Shadow Growth Law

A mock modular form f of weight k is holomorphic part of a harmonic Maass form F = f + f*, where completion f* is determined by a cusp form g of weight 2−k via

    f*(τ) = (i/√(2π))^(k−1) ∫_{−τ̄}^{i∞} g(−z̄) / (−i(z+τ))^k dz

Shadow ξ_k(F) = 2i y^k ∂F/∂τ̄ = g governs modular defect of f.

**Empirical scaling law:**
    log |f*(τ_0)| ~ α·k + β·log N + γ

at fixed test point τ_0 (e.g. τ_0 = i/√N), across 500 mock forms of varying weight k ∈ {1/2, 3/2, 2, 5/2, 3, 7/2, ...} and level N. Hypothesis: Zagier's error term grows **polynomially in level at fixed weight, exponentially in weight at fixed level**, with level-weight cross-term driven by Petersson norm of shadow g.

## 2. Literature

- **Zwegers (2002)** Utrecht thesis: completion of Ramanujan's mock thetas; shadow yields genuine modular transformation.
- **Zagier (2007)** *Ramanujan's mock theta functions and their applications*, Séminaire Bourbaki 986: explicit error-term growth for order-5 and order-7 mocks.
- **Bruinier–Funke (2004)** Duke Math. J. 125: foundational operator theory for ξ_k and harmonic Maass space H_k.
- **Bringmann–Ono (2006)** Invent. Math. 165: first asymptotics for mock theta coefficients.
- **Bringmann–Ono (2010)** Ann. Math. 171: extends completion framework; shadow bounds for Andrews-Dyson-Hickerson.
- **Duke–Imamoğlu–Tóth (2011), Folsom–Ono–Rhoades (2013):** quantum modular forms; boundary behavior ↔ shadow growth.

## 3. LMFDB Data Availability

LMFDB harmonic-Maass / mock-modular coverage **sparse**: `mf_hecke_cc`, `mf_newforms` hold holomorphic cusps (shadows g), not mock partners. Strategy:

- Pull weight 2−k cusp forms g from `mf_newforms` where 2−k ∈ {3/2, 1/2, 0, −1/2, ...} — weight-1/2 and -3/2 load-bearing.
- Reconstruct f* numerically via Eichler-integral definition using g's q-expansion.
- Cross-reference Bringmann–Ono q-series tables (supplementary to 2010 Annals; also in Ono's *Web of Modularity* CBMS 102).

Expected: ~500 mock forms with weights ∈ [1/2, 7/2] and N ≤ 500, dominated by weight-1/2 Zwegers family and weight-3/2 Hurwitz-class-number family.

## 4. Test Design

1. For each mock f with shadow g of weight w' = 2−k, level N:
   - Compute f*(τ_0) at τ_0 = i/√N via truncated Eichler integral (50 terms of g's q-expansion to 10^{-8}).
   - Record (k, N, log|f*|, ||g||_Pet, dim S_{w'}(N)).
2. Fit OLS: log|f*| = α·k + β·log N + δ·log||g||_Pet + γ; bootstrap CIs.
3. **Prime-detrend first**: residualize against log N prime factorization before claiming weight effect.
4. **Mean-spacing normalize** gap-like sub-statistics.
5. **Permutation null** on (k, N) with 1000 shuffles.
6. **Replicate across 5 τ_0 seeds** τ_0 ∈ {i/√N, 2i/√N, (1+i)/(2√N), ...} to rule out point artifacts.

## 5. Falsification

Any one triggers abandonment:
- |α| < 2σ after prime detrend → weight effect is prime contamination.
- Permutation p > 0.05 for joint (α, β) significance.
- Bootstrap CI for β crosses zero across ≥ 2 of 5 τ_0 seeds.
- Residual variance > 80% of total → no law, just noise.

## 6. Budget

~8 CPU-hr:
- 2h catalog + Eichler integration (500 × 50 terms × 5 seeds ≈ 125K evals @ ~50ms).
- 1h prime detrend + fit.
- 2h permutation null (1000 × 5 seeds).
- 1h bootstrap CI.
- 2h writeup + battery.

## 7. Expected Outcome

Prior: shadow growth dominated by Petersson norm of g; δ absorbs most variance; α, β small after controlling for ||g||_Pet. If α survives at ≥ 3σ independent of ||g||_Pet, that's genuine Zagier-error scaling — Harmonia battery pass worth pursuing. Base rate on novel findings surviving full battery: ~4/96 per feedback_false_profundity; calibrate accordingly.

**Word count: 748**
