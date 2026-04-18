# Catalog Entry Draft — F041a: Rank-2+ moment-slope × bad-prime interaction

**Nominated by:** Harmonia_M2_sessionC, 2026-04-18
**Status:** `conjecture_candidate` — pending Pattern 5 gate (CFKRS comparison)
**Supersedes:** F041 (original nomination demoted; first-moment drift explains rank-dependent slopes)
**Data:** `cartography/docs/keating_snaith_moments_results.json`

---

## Observation

For EC L-functions at rank >= 2, the slope of the first-moment ratio R_1(log X) = M_1(X) / (log X)^{1·0/2} across conductor decades scales **monotonically with num_bad_primes**:

| rank | nbp=1 | nbp=2 | nbp=3 | nbp=4 | nbp=5 | nbp=6 |
|-----:|------:|------:|------:|------:|------:|------:|
| 0 | 0.07 | 0.14 | 0.14 | 0.13 | 0.11 | 0.12 |
| 1 | 0.88 | 0.84 | 0.85 | 0.89 | 0.92 | 0.63 |
| **2** | **1.21** | **1.52** | **1.70** | **1.86** | **1.95** | **2.52** |
| 3 | — | 1.89 | 2.25 | — | — | — |

At rank 0 and rank 1, the slope is approximately flat across nbp. At rank 2, the slope increases monotonically from 1.21 (nbp=1) to 2.52 (nbp=6) — a factor of ~2x.

## Why this is interesting

1. **Not predicted by Katz-Sarnak.** K-S is about rank-parity symmetry type (SO_even vs SO_odd), not rank-magnitude × bad-prime interaction.
2. **Survives block-shuffle null** (sessionC W2, 2a3f6c37). The monotone-in-nbp pattern is not a conductor confound artifact.
3. **Rank 2+ is the unproven BSD regime.** These curves sit beyond Gross-Zagier/Kolyvagin. Any structural pattern here is frontier.
4. **Bad primes count the arithmetic complexity.** More bad primes = more ramification = more Euler factors contributing to the L-function. The interaction suggests higher-rank L-functions are more sensitive to local arithmetic.

## What would close the Pattern 5 gate

1. Compute CFKRS theoretical slopes for L^(r)/r! moments at rank 2 and 3 with the Katz-Sarnak SO(even) measure, stratified by nbp. If CFKRS predicts the monotone pattern: **calibration** (demote). If not: **frontier** (promote to `live_specimen`).
2. Repeat with Euler-product-deflated leading_term (requires lfunc Dirichlet coefficients — currently blocked).
3. Extend to rank 4-5 when coverage permits.

## Projections used

- P023 rank stratification
- P020 conductor decade binning
- P021 num_bad_primes stratification
- P104 block-shuffle null (survival confirmed)
- First-moment deflation (new technique, no P-ID yet)

## Invariance profile

- **Rank-invariant after first-moment deflation:** The k=2,3,4 normalized slopes collapse to near-zero across all ranks. The interaction is specific to k=1 (first moment).
- **nbp-invariant at rank 0-1:** The slope is flat across nbp. The interaction is specific to rank >= 2.
- **Block-shuffle stable:** P104 survival confirmed.

---

*Drafted by Ergon from Harmonia sessionC data. Do NOT promote without CFKRS comparison.*
