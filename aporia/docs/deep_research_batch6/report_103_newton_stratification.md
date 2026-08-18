# Deep Research Report #103: Newton Stratification Empirical Density

**Target Agent:** Harmonia
**Date:** 2026-04-23
**Status:** Proposed
**Budget:** ~1 day

## 1. Problem Statement

For an abelian variety A/F_q of dimension g, the **Newton polygon** N(A) is the lower convex hull of (i, v_q(a_i)) where ∏(1 − α_j T) = Σ a_i T^i is the Frobenius characteristic polynomial and v_q is q-adic valuation. Slopes lie in [0,1] with symmetric multiplicities λ ↔ 1−λ.

**g=1:** Ordinary (0,1) and supersingular (1/2,1/2). Deuring density ~(p−1)/24 for supersingular.

**g=2:** Four strata poset:
- Ordinary: (0,0,1,1), dim 3
- p-rank 1: (0,1/2,1/2,1), dim 2
- Supersingular: (1/2,1/2,1/2,1/2), dim 1
- Superspecial: dim 0

For Jacobians of g2c embedded in A_2, densities match Oort codimension predictions modulo Torelli correction.

## 2. Literature

- **Dieudonné (1955):** Dieudonné modules; Newton polygon = isogeny invariant.
- **Manin (1963):** symmetric Newton polygons realizability.
- **Oort (1999)** "A stratification of a moduli space of abelian varieties": Newton stratification on A_g ⊗ F_p.
- **Oort (2001):** foliations; central leaves.
- **Chai-Oort (2011):** irreducibility of non-supersingular strata.
- **Viehmann (2013):** affine Deligne-Lusztig varieties.
- **Achter-Pries (2008):** supersingular locus density in M_g; Torelli correction matters.

## 3. LMFDB Data Extraction

**g=1:** `ec_curvedata.aplist` for p ≤ 100. Supersingular iff a_p ≡ 0 (mod p). Slopes:
- v_p(a_p) = 0 → (0,1).
- v_p(a_p) ≥ 1 → (1/2,1/2).

**g=2:** Need L-polynomial coefficients a_1, a_2 at p. Char poly: T^4 − a_1 T^3 + a_2 T^2 − p a_1 T + p^2. Slopes from (v_p(a_1), v_p(a_2)):
- v_p(a_1) = 0: ordinary (0,0,1,1).
- v_p(a_1) ≥ 1, v_p(a_2) = 0: p-rank 1 (0,1/2,1/2,1).
- v_p(a_1) ≥ 1, v_p(a_2) ≥ 1: supersingular (1/2)^4.

## 4. Test Design

**Primes:** p ∈ {5, 7, 11, 13, 17}.

**Samples:** 10^4 curves per family per p:
- g=1: random sample with gcd(cond, p) = 1.
- g=2: random sample with good reduction at p.

**Procedure:**
1. Extract a_p (g=1) or (a_1, a_2) (g=2).
2. Compute p-adic valuations.
3. Bin into strata.
4. Compare to Oort prediction.

**Oort prediction (g=2, asymptotic):**
- Ordinary: 1 − O(1/p)
- p-rank 1: O(1/p)
- Supersingular: O(1/p^3)

**Null:** random symmetric polygons weighted by codimension; Deuring mass formula for g=1.

## 5. Falsification

Reject if observed stratum density deviates > 3σ under binomial σ = √(ρ(1−ρ)/N), N=10^4.

**Specific kills:**
- g=1 supersingular at p=11: Deuring ≈ 0.083; kill if observed < 0.065 or > 0.10 after conductor-weighting.
- g=2 p-rank 1 at p=7: predict ~0.143; kill if < 0.10 or > 0.18.
- g=2 supersingular at p=5: predict ~0.008; kill if > 0.02.

**Confounds:**
- Torelli: Jacobians ⊊ A_g; Achter-Pries correction (factor ~2).
- Conductor bias: LMFDB conductor-complete only to cutoff; restrict cond < 10^4 (g=1), < 10^6 (g=2).
- Isogeny double-counting: dedupe by isogeny class.

## 6. Budget

~1 day: 2h SQL extraction, 3h valuation + binning, 2h null/Oort comparison, 1h writeup.

## 7. Expected Outcome

First **empirical Newton stratification census** at LMFDB scale. Baseline: g=1 matches Deuring mass formula within binomial noise; g=2 matches Oort with Torelli correction. Surprise would be stratum-crossing curves or systematic p-rank 1 deficit/excess — either LMFDB data issue (valuable) or Torelli correction beyond Achter-Pries (more valuable, feeds Chai-Oort foliation densities).

Handoff: Harmonia receives SQL + stratum-binning; output feeds Charon tensor as new coordinate `newton_stratum_p5..p17` for cross-domain coupling against rank, regulator, Sato-Tate.

**Word count: 798**
