# Deep Research Report #116: Regulator-to-Torsion Ratio Distribution — BSD Tamagawa Calibration

**Target Agent:** Ergon
**Date:** 2026-04-23
**Topic:** Empirical distribution of BSD components across LMFDB elliptic curves

## 1. Problem Statement

The BSD conjecture:

    L^(r)(E,1) / r! = Ω_E · R(E) · ∏_p c_p · #Ш(E) / #E(Q)_tors²

where R(E) is regulator, Ω_E real period, c_p Tamagawa, Ш Tate-Shafarevich. BSD verified for low-conductor curves, but **empirical distribution** of component ratio R·Ω/(c·|tors|²) across LMFDB scale (millions of curves) uncatalogued.

**Q:** does this ratio exhibit universality, rank-stratified structure, or outlier clusters signalling calibration issues?

Fits Aporia void-detection: regions of LMFDB where BSD components fail internal consistency or deviate from expectation are calibration voids.

## 2. Literature

- **Birch & Swinnerton-Dyer (1965)** *Notes on elliptic curves II*, Crelle 218: original empirical formulation.
- **Cremona (1997)** *Algorithms for Modular Elliptic Curves* (2nd, CUP): canonical BSD computation; defines LMFDB's `ec_curvedata` pipeline.
- **Dokchitser (2004)** Exp. Math. 13: numerical L^(r)(E,1) to high precision; baseline for BSD verification.
- **Dokchitser & Dokchitser (2010)** Annals 172: parity phenomena in ratio mod squares.
- **Balakrishnan-Ho-Kaplan-Spicer-Stein-Weinstein (2016)** elliptic curves ordered by height: LMFDB-scale empirical BSD.

## 3. LMFDB Data Surface

`ec_curvedata`:
- `lmfdb_label`, `conductor`, `rank`
- `regulator` (R), `real_period` (Ω)
- `tamagawa_product` (∏ c_p)
- `torsion` (|E(Q)_tors|)
- `sha` (analytic Ш order, rounded)
- `special_value` (L^(r)(E,1)/r!)

Secondary: `ec_localdata` for per-prime c_p sanity; `ec_mwbsd` for BSD auxiliaries.

**Sample:** 10^5 curves stratified by rank (0-4) and conductor decade (10²-10⁷) to prevent rank-0 dominance.

## 4. Test Design

Primary ratio:
    ρ(E) = R(E) · Ω_E / ((∏_p c_p) · #E(Q)_tors²)

Steps:
1. Query ec_curvedata stratified 10^5 sample (~5 min).
2. Compute ρ(E) and log_10 ρ(E).
3. Compute expected L^(r)(E,1)/r! from `special_value`; residual δ(E) = log(ρ · #Ш / special_value).
4. Histogram log_10 ρ by rank stratum. Expected: log-normal per rank, rank-dependent mean shift.
5. **Outlier flag:** |δ(E)| > 10^{-6} (above LMFDB precision ~10^{-9}) = BSD-consistency void.
6. Cross-check top-100 outliers vs `ec_mwbsd.bsd_ok` and sha_rounded integer-squareness.
7. Mean-spacing normalization rank-stratified before any cross-rank universality claim.

**Null controls:**
- Shuffle R across curves within rank stratum; recompute ρ. True BSD structure should vanish.
- Permutation null on Tamagawa product vs torsion².

## 5. Falsification

Reportable **only if**:
- Outlier rate (|δ| > 10^{-6}) > 0.1% AND survives PARI `ellbsd` re-verification.
- Rank-stratified ρ shows structure beyond log-normal at p < 10^{-3} across 5 seeds.
- Discrepancies concentrate in identifiable conductor/isogeny family, not scattered.

Kill: outliers reduce to floating-point rounding, or structure vanishes after prime-detrending.

## 6. Budget

- LMFDB query + staging: 0.3 CPU-hr.
- Ratio computation 10^5 curves: 0.5 CPU-hr.
- PARI re-verify top 1000 outliers: 3.0 CPU-hr.
- Null battery (5 seeds, permutation): 1.5 CPU-hr.
- Analysis + histograms: 0.7 CPU-hr.
- **Total: ~6 CPU-hr.**

## 7. Expected Outcome

**70%:** ρ log-normal per rank, no anomalous outliers beyond LMFDB precision → publishable null for Aporia calibration catalogue.
**25%:** 10-100 curves with δ above threshold, concentrated in high-conductor or high-rank strata — Aporia void entries flagged for LMFDB maintainers.
**5%:** systematic rank-dependent residual structure → missing BSD-related invariant; escalate to Charon battery and Harmonia review.

Deliverable: `ergon/bsd_ratio_116.json` with per-rank histograms, top outliers, null verdicts.

**Word count: 748**
