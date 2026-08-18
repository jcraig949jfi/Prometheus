# Deep Research Report #146: Perfectoid / Prismatic Site Empirical Cohomology

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** perfectoid / prismatic
**Sister reports:** #103 (de Rham Newton), #141 (crystalline Newton)

## 1. Problem Statement

Bhatt-Scholze prismatic cohomology Hⁱ_Δ(X/Z_p) is the freshest unifying object in p-adic Hodge theory: a single Z_p-module that specializes (by base change along distinguished prisms) to de Rham, crystalline, and étale cohomology. The Hodge-Tate comparison predicts an isomorphism

  Hⁿ_Δ(X) ⊗_{Z_p} B_HT  ≃  ⊕_{i+j=n} Hⁱ(X, Ωʲ)(−j)

after tensoring with the Hodge-Tate period ring. **Empirical question:** at LMFDB scale, do prismatic dimensions of small varieties (E/F_p, K3 reductions, abelian surface reductions) match the Hodge-Tate decomposition predicted from their de Rham / crystalline data? Where the comparison fails, the variety is "non-Hodge-Tate" — a candidate **void cell** in Aporia's bridge atlas, parallel to the Newton-above-Hodge anomalies tracked in #103 and #141.

## 2. Literature

- **Scholze (2011, PhD thesis):** perfectoid spaces; tilting equivalence char 0 ↔ char p.
- **Bhatt-Scholze (2019, "Prisms and prismatic cohomology"):** the breakthrough — a single site interpolating crystalline and étale.
- **Bhatt-Morrow-Scholze (2018, "Integral p-adic Hodge theory"):** A_inf-cohomology, Z_p[1/p]-integral comparison, the technical bridge to crystalline/de Rham.
- **Bhatt (2018, Eilenberg / Arizona Winter School lectures):** computational backbone for what dimensions to expect.
- **Cesnavicius-Scholze (2019, "Purity for flat cohomology"):** prismatic locality and descent — needed to localize tests at single primes.

## 3. LMFDB Data

- `ec_curves`: E/Q with reduction data per prime; columns `j_invariant`, `disc`, `bad_primes`, `ap` (used to back out Frobenius slopes mod p).
- `ec_padic`: per-curve p-adic L-series and `slopes` where computed.
- `g2c_curves`: genus-2 Jacobians; `disc`, `bad_primes`, `slopes` (Newton polygon slopes of Frob on H¹_crys), `euler_factors`.
- `av_fq_search`: abelian varieties over F_q with explicit Newton polygon and Hodge polygon columns — direct ground truth for the Hodge-Tate test.
- For prismatic computation: Sage-experimental `prismatic` package (Bhatt-Lurie scripts); fallback is to derive H¹_Δ ⊗ B_HT dimensions from the Bhatt-Morrow-Scholze comparison applied to crystalline output of `padic_lseries`.

## 4. Test Design

**Step 1.** Sample ~100 elliptic curves from `ec_curves` with good reduction at each p ∈ {3, 5, 7, 11, 13} (exclude `bad_primes` ∋ p). Reject CM curves to a separate stratum.

**Step 2.** For each (E, p):
- (a) **Crystalline dim** of H¹: 2; verify via `slopes` having two entries summing to 1 (ordinary: {0,1}; supersingular: {1/2, 1/2}).
- (b) **De Rham dim** of H¹: 2 (always, genus 1).
- (c) **Prismatic dim** of H¹_Δ: call Sage `prismatic.H(E, p, 1)` if installed; else compute via BMS comparison from (a) and check rank of the predicted Z_p-module.
- (d) **Hodge-Tate decomposition test:** verify H¹_Δ ⊗ B_HT splits as H⁰(Ω¹) ⊕ H¹(O)(−1), each rank 1.

**Step 3.** Repeat for ~50 g2c reductions at p ∈ {3, 5, 7}, dim H¹ = 4, expected HT decomposition 2+2.

**Step 4.** Record a per-cell **HT residual**: rank deficit, slope mismatch, or comparison-map non-isomorphism flag.

**Step 5.** Null: random assignment of slope multiset drawn from the empirical distribution at fixed p; recompute fraction of "HT-consistent" cells. Real signal must beat null by ≥ 5σ.

**Metrics:** fraction of cells where Hodge-Tate decomposition holds; stratification by ordinary vs supersingular vs CM; conductor-class residuals.

## 5. Falsification

- **Expected (null result):** Hodge-Tate decomposition holds in all 150 cells — confirms BMS comparison empirically at LMFDB scale; calibrates the testbed.
- **Strong finding:** any cell where prismatic rank ≠ Hodge sum, or comparison map fails to be an isomorphism, is a publishable **non-HT lift candidate** — direct void in Aporia's atlas.
- **Weak finding:** systematic failure on supersingular reductions only → suggests Sage prismatic package mishandles slope-1/2 case; report as data-correction.
- **Null sanity:** shuffled slope multiset must produce mostly inconsistent cells; if shuffled null also passes, the test is vacuous and the slope data is too coarse.

## 6. Budget

~1 day. Sage prismatic experimental install + crystalline cross-check via `padic_lseries` (~3h). 100 EC × 5 primes + 50 g2c × 3 primes = 650 cells, each cell <1s once Sage warm (~2h compute). Stratified plotting and null shuffle (~2h). Writeup (~1h).

## 7. Expected Outcome

Measure the Hodge-Tate decomposition pass rate on 150 reductions; identify any non-HT cells. The expected outcome is a calibrated null — HT comparison holding across the sample, confirming BMS at LMFDB scale and validating Sage's experimental prismatic backend. The high-value outcome is one or more **non-HT cells**: a small variety whose prismatic cohomology fails the predicted decomposition is a fresh void marker, directly feedable to Aporia's bridge-atlas. This report is the third leg of an integrated p-adic Hodge testbed: #103 supplies de Rham Newton data, #141 supplies crystalline Newton data, and #146 supplies the prismatic unification. Together they triangulate the same void from three independent cohomological angles, and disagreement between the three is itself a discovery signal.

**Word count: 748**
