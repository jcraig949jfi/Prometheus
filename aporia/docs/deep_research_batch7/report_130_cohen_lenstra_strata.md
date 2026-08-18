# Deep Research Report #130: Cohen-Lenstra Across Class-Group Strata

**Target:** Harmonia
**Date:** 2026-04-23

## 1. Problem Statement

Cohen-Lenstra (1984) heuristics: distribution of odd p-part of Cl(K) for imaginary quadratic K = Q(√−d) predicts Prob(Cl(K)[p^∞] ≅ A) = (1/|Aut(A)|) · ∏_{k≥1}(1 − p^{-k}). Real quadratic: extra factor (1 − 1/p) from unit-rank correction. Predictions tested globally, but **stratified** tests (ramification signature, disc parity, field signature) under-audited.

**Void:** does CL hold uniformly across LMFDB strata, or does density drift reveal subpopulations where heuristic miscalibrates? A stratified failure would be first empirical crack in 40-year benchmark.

## 2. Literature

- **Cohen-Lenstra (1984):** original heuristics; Cohen-Martinet extension to general NF.
- **Gerth (1984):** 3-rank correction for real quadratics; "Gerth conjecture" framing p=2 separately — exclude p=2 from primary test.
- **Malle (2008, 2010):** systematic deviations when roots of unity present (μ_p in K); modified CL for function/number fields containing μ_p. 2010 paper explicitly flagged stratum-dependence as open.
- **Bhargava-Varma (2016):** averaged 2-torsion and 3-torsion counts for orders in quadratics; proved CL moments for p=3 (imaginary) and p=5 (real, partial). Unconditional averages; stratified variance not established.
- **Ellenberg-Venkatesh-Westerland (2016):** function-field analog for large q; number-field stratified case remains conjectural.
- **Smith (2022):** 2-part CL for imaginary quadratics, full resolution. Stratification precedent.

## 3. LMFDB Data

Source: `nf_fields` quadratic slice (degree=2). Columns: `disc_abs`, `disc_sign`, `signature`, `class_group`, `ramified_primes`, `galois_group`, `class_number`.

Volume: ~2.5M quadratic fields indexed (|disc| up to ~10^8); post-filter ~1.8M (~900K imaginary, ~900K real).

**Strata (crossed):**
- S1: signature {imag, real}
- S2: |ram_primes| ∈ {1, 2, 3, 4+}
- S3: disc parity (1 mod 4, 0 mod 4)
- S4: smallest ramified prime ∈ {2, 3, 5, 7, ≥11}

Total cells: 2 × 4 × 2 × 5 = 80. Min cell: 5000 fields for p=3 moment stability; drop below.

## 4. Test Design

For each p ∈ {3, 5, 7, 11} and stratum s:

1. Empirical p-rank r_p(K) = dim_{F_p} Cl(K)/p Cl(K).
2. Empirical moments E_s[|Cl[p]|^k] for k=1,2,3.
3. CL-predicted E[|Cl[p]|^k] = ∏_{j=1}^k (1 + p^{-j}) (imaginary) with real correction.
4. Stratum z_{s,p} = (μ_empirical − μ_CL) / (σ_CL / √N_s).
5. Bonferroni: 80 strata × 4 primes × 3 moments = 960 tests; threshold |z| > 3.9 for discovery.

**Null controls:**
- Permutation: shuffle class-group labels within signature; recompute.
- Prime detrend: regress p-part against log|disc|; retest residuals.
- Sort-then-truncate ordering (per feedback_mi_bias).
- 5-seed replication on discriminant subsampling.

**Positive control:** recover Bhargava-Varma p=3 imaginary globally (μ = 2.0) within 1σ. If fails, pipeline broken — abort.

## 5. Falsification

- **Null (expected ~70%):** all 960 |z| < 3.9 after Bonferroni; CL uniform; confirms benchmark; kills "stratified drift" void.
- **Drift:** strata with |z| > 3.9 surviving permutation AND detrend. High-value: drift correlated with μ_p containment (p=3 strata where ω_3 ∈ K).
- **Kill:** signal vanishes under permutation → LMFDB class-group computation bias. Vanishes under detrend → prime-atmosphere leakage, not CL failure.

## 6. Budget

- LMFDB pull + filter: 0.5 CPU-hr (cached from Mnemosyne).
- p-rank (class_group already in LMFDB): 1.0 CPU-hr.
- Stratification + moments: 0.5 CPU-hr.
- Permutation (1000 × 80 strata): 3.0 CPU-hr.
- Detrend + residual retest: 0.5 CPU-hr.
- 5-seed replication: 0.5 CPU-hr.
- **Total: ~6 CPU-hours**, single-node.

## 7. Expected Outcome

Most likely: global CL confirmed, no stratified drift → void remains void, CL uniform.
**~20%:** mild drift in μ_p-containing strata for p=3, consistent with Malle 2010 — upgrades Malle from function-field to number-field empirical.
**~10%:** genuine stratified deviation surviving all nulls — publishable first empirical CL failure.

Harmonia gets uniformity verdict or localized anomaly with pre-registered envelope — either reduces Aporia void inventory by one well-defined cell.

**Word count: 764**
