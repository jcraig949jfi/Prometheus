# Deep Research Report #156: Selmer Scheme Rank Distribution at LMFDB Scale

**Target Agent:** Charon
**Date:** 2026-04-25
**Front:** Selmer / Bhargava-Shankar

## 1. Problem Statement

For an elliptic curve E/Q and integer n ≥ 1, the n-Selmer group Sel_n(E/Q) sits in the exact sequence 0 → E(Q)/nE(Q) → Sel_n(E/Q) → Sha(E/Q)[n] → 0. Its F_p-rank (for n = p prime) is the dominant invariant controlling rank-bounding via descent. Bhargava-Shankar (2010+) prove that the average size of Sel_n(E/Q) over E ordered by height is exactly σ(n) = sum of divisors of n for n ∈ {2, 3, 5}, matching a heuristic that predicts rk Sel_p has finite expectation (p+1)/p above the Mordell-Weil floor. Bhargava-Kane-Lenstra-Poonen-Rains (BKLPR, 2015) refine this from average to **full distribution**: rk Sel_p − rk E(Q) is distributed as the cokernel rank of a random alternating Z_p-pairing, an explicit measure on non-negative integers.

**Empirical question.** Does the LMFDB `ec_curves` catalogue (~3.6M E/Q with conductor ≤ 500K) reproduce the BKLPR distribution for n ∈ {2, 3, 4, 5, 7}, both globally and under conductor stratification? Any structural deviation is a "missing rank" void in Aporia's atlas.

## 2. Literature

- **Bhargava-Shankar (2015) Annals 181:** average 2-Selmer = 3, average rank ≤ 7/6.
- **Bhargava-Shankar (2015) Annals 181 II:** average 3-Selmer = 4.
- **Bhargava-Skinner-Zhang (2014):** ≥66% of E/Q satisfy BSD with rank ≤ 1.
- **BKLPR (2015) Camb. J. Math. 3:** full conjectural distribution of Sel_p; arithmetic side of Cohen-Lenstra-style heuristic via random alternating matrices.
- **Bhargava-Klagsbrun-Lemke Oliver-Shnidman (2017):** average 4-Selmer in quadratic twist families = 7.
- **Bhargava-Klagsbrun-Lemke Oliver-Shnidman (2019):** average 5-Selmer = 6, matching σ(5).
- **Poonen-Rains (2012):** original alternating-pairing heuristic for Sel_p; precursor to BKLPR full distribution.

## 3. LMFDB Data

- **`ec_curves`:** ~3.6M E/Q rows. Columns: `lmfdb_label`, `conductor`, `rank` (Mordell-Weil), `analytic_rank`, `sha` (analytic Sha order), `torsion_order`, `torsion_structure`, `2-selmer_rank` (where present), `regulator`, `ainvs`.
- **`ec_padic`:** p-adic L-function and p-adic Selmer data for small p (p ≤ 7), partial coverage.
- **`ec_iwasawa`:** lambda/mu invariants — useful as cross-check on Sel_p structure for p of good ordinary reduction.
- **mwrank** binary (Cremona) for direct 2-descent; **Sage** `EllipticCurve.selmer_rank(p)` for p ∈ {3, 5, 7} via isogeny + Cassels-Tate when applicable.

Direct n-Selmer is stored only for n = 2 across the full catalogue; for n ∈ {3, 4, 5, 7} we draw a stratified random sample of ~10K curves and recompute.

## 4. Test Design

**Step 1.** Pull `ec_curves` 2-Selmer column for full 3.6M; bin by conductor decade (10^1, 10^2, …, 10^5).

**Step 2.** Stratified random sample 10K curves per conductor decade; compute Sel_n via Sage for n ∈ {3, 4, 5, 7}. For n = 4, factor through 2-isogeny descent (BKLOS 2017 method). For n = 7, restrict to E with rational 7-isogeny when feasible; else use 7-descent over Q(E[7]).

**Step 3.** Empirical distribution P_emp(rk Sel_n = r) per decade and globally.

**Step 4.** BKLPR predicted distribution: for prime p, P(rk Sel_p − rk_MW = 2u) = (∏_{k≥1}(1 − p^{1−2k})) · p^{−u(u+r_0)} / ∏_{k=1}^u (p^k − 1)(p^{k+r_0} − 1), where r_0 = rk E(Q) baseline; collapse to Sel_p marginal by integrating over rk_MW prior (use empirical rank distribution from `ec_curves.rank`).

**Step 5.** Two-sample chi-square + Kolmogorov on rank histograms; record per-decade residuals.

**Null:** randomize rank assignment (permute `selmer_rank` column over conductor-bin); BKLPR fit must vanish (chi-square z drops below 2).

## 5. Falsification

- **Confirms:** all 5 distributions within 5% L1 of BKLPR per decade → first LMFDB-scale validation.
- **Publishable deviation:** any (n, decade) with > 5% structural offset (consistent across resamples, surviving null) → "missing rank" void; candidate Aporia anchor.
- **Strong kill of method:** null shuffling reproduces BKLPR fit → conductor binning is the only signal; report as artifact.

## 6. Budget

~8 hours. Postgres aggregation of 2-Selmer column (~30 min). Sage selmer_rank on 50K curves total across n ∈ {3,4,5,7} at ~3-15 sec/curve depending on n (~6h, parallel 8-core). Distribution fit + plotting + writeup (~2h).

## 7. Expected Outcome

Prior: Sel_2, Sel_3, Sel_5 match BKLPR at < 2% L1 globally — these are theorem-backed averages and the full distribution is a strong conjecture. Sel_4 and Sel_7 are open at this scale; Sel_7 in particular has never been measured on > 10^4 curves. Conductor-stratified deviations would reveal a height-dependent correction to BKLPR analogous to the Park-Poonen-Voight-Wood lower-order term in rank statistics. **Aporia connection:** Selmer rank distribution is a foundational arithmetic-statistics channel — any conductor stratum where empirical Sel_n understates BKLPR is a "missing rank" void, marking a region of LMFDB where rank computation or Sha order is systematically truncated. These voids feed Charon's anomaly queue and Harmonia's modularity cross-checks.

**Word count: 768**
