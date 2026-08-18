# Deep Research Report #133: Hypergeometric Motives L-function Empirics — Rodriguez-Villegas HGM Sato-Tate Scan

**Target Agent:** Charon
**Date:** 2026-04-23

## 1. Problem Statement

Hypergeometric motives (HGMs) are Q-motives indexed by pairs of disjoint multisets (α, β) of positive integers with equal sum. Each HGM carries an L-function L(s, H(α, β) | t) depending on rational parameter t; Euler factors computable via finite hypergeometric sums (Greene, McCarthy, Beukers-Cohen-Mellit). Sato-Tate distributions should match one of Serre's compact subgroups of the motivic Galois group (USp(2g), SU(2)×SU(2), N(SO(2)), ...), determined by Hodge structure and endomorphism algebra.

**Q:** across 10^3 HGMs in LMFDB, do empirical Sato-Tate moments (m_1,...,m_4) cluster at predicted symmetry-type values; where they deviate, does deviation correlate with any Charon tensor feature (rank signatures, p-adic valuations, Hodge vectors)?

Instrument-mode test: HGMs are a domain Charon hasn't pulled through its battery. If cross-family compression law is genuine, HGM gap statistics should compress at predicted type boundaries without HGM-specific tuning.

## 2. Literature

- **Rodriguez-Villegas (2007)** "Hypergeometric families of Calabi-Yau manifolds": original HGM construction from hypergeometric data, p-adic trace formula.
- **Beukers-Cohen-Mellit (2015)** "Finite hypergeometric functions" PAMQ: proved equivalence of three definitions; algorithmic Euler factor formula (LMFDB/Magma).
- **Watkins (2020)** "Hypergeometric motives" preprint: implementation details, conductor bounds, degree ≤ 6 census underlying `hgm_motives`.
- **Fité-Kedlaya-Rotger-Sutherland (2012):** Sato-Tate groups for abelian surfaces — 52-group classification HGMs embed into at low degree.
- **Roberts-Rodriguez-Villegas (2022):** "Hypergeometric supercongruences" — mod-p^r refinements; relevant if Charon p-adic channel fires.

## 3. LMFDB Data

Table `hgm_motives`. Columns:
- `label` (e.g., `A2.2_B1.1.1.1_t1.2`)
- `A`, `B` (α, β multisets)
- `t` (specialization, rational)
- `degree`, `weight`, `hodge`
- `cond`, `sig`, `famhodge`
- `ap` arrays or recompute via BCM for p up to B = 10^4
- `st_group` when tagged

Cross-ref: `hgm_families` for family-level symmetry predictions.

## 4. Test Design

**Sample:** 1K HGMs stratified across degree 2-6 and weight 0-3 (drop Galois-conjugate duplicates of t).

**Pipeline:**
1. Pull (label, A, B, t, degree, weight, hodge, cond, predicted st_group) for 1K rows.
2. Compute/fetch normalized Frobenius a_p / p^{w/2} for p ∈ [5, 10^4], p ∤ cond · (numer(t) · denom(t) · denom(t−1)).
3. Moments m_k = (1/N) Σ (a_p/p^{w/2})^k for k ∈ 1..8.
4. Theoretical moments for predicted Sato-Tate group (FKRS tables, Serre NX/56).
5. KS / χ² of empirical CDF vs Haar pushforward on [−2g, 2g].
6. **Charon battery:** feed normalized a_p gaps through frozen v10 battery — does gap-compression law fire at degree boundaries where endomorphism algebra jumps?
7. Permutation null: shuffle (label, st_group) 10^3 times.
8. Prime detrend: strip sorted-prime scaling from gaps before any coupling claim.

## 5. Falsification

Falsified if any:
- KS p > 0.05 on > 30% at predicted st_group → distributions don't match (LMFDB tags wrong or BCM implementation wrong).
- Battery gap-compression z indistinguishable from permutation null (|z| < 2 after Holm across degree bins).
- Moment deviations (m_2 − predicted) show no correlation with Hodge vector entries (Spearman |ρ| < 0.1, n=1000).
- Replication across 5 seeds fails — any headline signal not surviving all 5 seeds is killed.

Pre-registered kill: if degree-2 HGMs (EC in disguise for many (A,B)) don't reproduce known USp(2) / N(U(1)) split at expected ratios → **entire pipeline bugged**; discard higher-degree results.

## 6. Budget

- LMFDB pull + BCM Euler factors: ~4 CPU-hr (PARI `hgmeulerfactor` rate-limiter; parallel 8 cores).
- Moment + KS + battery: ~2 CPU-hr.
- Permutation null (10^3 × 5 seeds): ~2 CPU-hr.
- **Total: ~8 CPU-hr** single machine, no GPU.

## 7. Expected Outcome

**60%:** HGM gap statistics follow predicted ST types with no compression anomaly → HGMs "well-behaved" in same universality class Charon mapped via EC/g2/MF. Calibration win, not discovery.

**25% discovery:** compression law fires at endomorphism-algebra jumps NOT predicted by st_group tag — HGMs with CM-like substructure LMFDB hasn't labeled. Charon's first HGM-native leads.

**15% kill:** moments don't match predictions — BCM implementation drift or subtle normalization bug. Every kill strengthens battery.

Instrument-mode: no oracle prediction, just point frozen battery at new island and read the dial.

**Word count: 798**
