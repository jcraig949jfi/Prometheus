# Deep Research Report #153: GUE Pair Correlation for Maass Forms

**Target Agent:** Ergon
**Date:** 2026-04-25
**Front:** RMT / Maass forms
**Predecessor:** F011 EC bulk-rigidity result (k=24, +46-51% deficit)

## 1. Problem Statement

A Maass cusp form on SL_2(Z)\H has spectral parameter t_n with Laplace eigenvalue λ_n = 1/4 + t_n². Order the t_n in increasing absolute value and define the pair-correlation function

R_2(α, β) := lim_{N→∞} (1/N) #{ (n, m) : n ≠ m, α ≤ (t_n − t_m) · (log t / 2π) ≤ β }

after unfolding by the Weyl mean density. Rudnick-Sarnak (1996) show, conditionally on GRH for the relevant L-functions, that R_2 → 1 − sin²(πx)/(πx)² — the GUE limit — for any fixed test interval as N → ∞.

The empirical question is twofold. First, at finite N (LMFDB caps at ~50K forms), what is the rate of convergence to GUE? Second, does the F011 bulk-rigidity signature — a +46-51% gap-count deficit at k=24 measured on elliptic-curve L-function zeros — appear in the Maass spectrum, or is F011 an L-function-specific artifact of EC arithmetic? This is a transfer test for one of Aporia's seeded universality claims.

## 2. Literature

- **Hejhal (1976, 1983):** Selberg trace formula on the modular surface; first numerical Maass spectra and predicted small-N deviations from GUE near low-lying levels.
- **Sarnak (1990):** statistical distribution of arithmetic Laplace eigenvalues; GUE conjecture stated.
- **Rudnick-Sarnak (1996):** R_2 → GUE for principal L-functions (including Maass) under GRH; finite-N error not effectivized.
- **Luo-Sarnak (2003):** quantum unique ergodicity / mass equidistribution on SL_2(Z)\H — orthogonal observable.
- **Bogomolny-Schmit (2002):** number-theoretic billiards (rectangular + arithmetic boundary) reproduce Maass-like spectra and predict Hejhal-type oscillations in the pair correlation.
- **Iwaniec (2002, *Spectral Methods of Automorphic Forms*):** Kuznetsov / pre-trace machinery underwriting any moment-method extension.

## 3. LMFDB Data

The `maass_form` table (~50K rows on devmirror.lmfdb.xyz) carries:
- `level` — integer N for Γ_0(N).
- `weight` — 0 for cuspidal Maass.
- `nspec` — index of the spectral parameter within (level, symmetry) class.
- `spectral_parameter` — numerical t_n to 25-30 digits.
- `coefficients` — first ~1000 Hecke eigenvalues a_n (real, normalized).
- `symmetry_type` — even / odd under z → −z̄.

Restrict to `level` ∈ {1, 2, 3, 4} with `spectral_parameter` < 1000; expected ~10K survivors across both symmetry classes. Cross-reference `lfunc_lfunctions` for L(s, f) zeros where independent unfolding is needed.

## 4. Test Design

**Step 1.** Pull (level, symmetry_type, spectral_parameter) for the ~10K-row restricted set; group by (level, symmetry_type) so each spectrum is a single GOE/GUE realization.

**Step 2.** Unfold via Weyl: N(T) ~ (Vol/4π) T² − (1/π) T log T + O(T). Compute mean spacing locally; rescale t_n → x_n with mean spacing 1.

**Step 3.** Compute empirical R_2 in 10 bins on [0, 5] per (level, symmetry) stratum. Compare to GUE Dyson kernel and GOE alternative; record KS distance and integrated L² error.

**Step 4.** Gap-k statistics for k ∈ {1, 4, 8, 24}: P_k(s) := density of (k+1)-th-neighbor spacings. Compare to Wigner-Dyson β=2 surmise and GUE numerical reference. The F011 signature is a +46-51% count deficit relative to GUE in the bulk of P_24(s).

**Step 5.** 1-level density (Katz-Sarnak) over the family as a cross-validation: should match GUE symmetry type for full level 1.

**Step 6.** Permutation null per `feedback_permutation_null.md`: shuffle t_n across levels, recompute R_2 and P_24; null must not reproduce the k=24 deficit.

## 5. Falsification

- **R_2 → GUE confirmed at expected rate (~N^{-1/2}):** baseline; no surprise.
- **F011-style bulk deficit at k=24 appears in Maass:** universality crosses from EC L-functions to a non-arithmetic-curve spectrum — strong evidence the mechanism is RMT-internal, not EC-arithmetic.
- **F011 deficit absent (P_24 matches GUE within 5%):** F011 is L-function-specific or EC-specific; reframe project_charon_two_channels accordingly.
- **R_2 fails GUE at low levels in a Hejhal-predicted way but k=24 still anomalous:** structured residual — publishable as a Bogomolny-Schmit-type oscillation refinement.

## 6. Budget

~8 hours. Postgres pull ~30 min; numpy/scipy unfolding and R_2 binning ~2h; gap-k sweep ~1h; permutation null over 1000 shuffles ~3h on one core; plotting and stratified writeup ~1.5h. No GPU required.

## 7. Expected Outcome

The primary deliverable is a calibrated convergence-rate curve for R_2 on the LMFDB Maass family and a binary verdict on F011 transfer. Either result is informative: confirmation widens F011 from "EC L-function bulk rigidity" to "automorphic spectral universality"; falsification narrows F011 to an arithmetic feature of EC and re-opens the question of *which* operator is responsible. This bears directly on Aporia void-detection: Maass forms occupy a separate island from EC in the silent-islands map (`project_silent_islands.md`), and a successful F011 transfer would be the first measured bridge across that void using an RMT observable rather than an L-function functorial lift.

**Word count: 781**
