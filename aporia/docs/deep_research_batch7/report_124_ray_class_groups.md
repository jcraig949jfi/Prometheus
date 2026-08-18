# Deep Research Report #124: Ray Class Group Structure at LMFDB Scale

**Target Agent:** Charon
**Topic:** Genus-theoretic decomposition of ray class groups across ~10^6 number fields
**Date:** 2026-04-23

## 1. Problem Statement

Ray class group Cl_m(K) generalizes class group by modulus m (finite + signature at infinite places). Its 2-torsion decomposes via **genus theory** into "ambiguous" (genus) part and "non-genus" (Rédei) part. For K = Q(√d) with t ramified primes, 2-rank of narrow class group is t−1; **4-rank** depends on Rédei symbols [d_1, d_2, d_3] — cubic-reciprocity-like invariant encoding whether d_1 is a norm from Q(√d_2, √d_3).

**Rédei reciprocity:** [d_1,d_2,d_3] = [d_2,d_1,d_3] = [d_1,d_3,d_2] (full S_3 symmetry) under compatibility. Smith's 2017 breakthrough used Rédei symbols to prove Stevenhagen's conjecture on 2^∞-class group distributions.

**Empirical Q:** do LMFDB ray class groups at scale exhibit predicted Rédei densities, and do higher-rank (non-quadratic) fields show genus-theoretic structure generalizing cleanly?

## 2. Literature

- **Rédei (1939)** "Ein neues zahlentheoretisches Symbol": triple symbol [a,b,c] and symmetry relations.
- **Scholz (1932):** reciprocity between 3-ranks of Cl(Q(√d)) and Cl(Q(√−3d)); together with Rédei determines 4-rank.
- **Gerth (1984):** 4-rank distribution P(rk_4 = k) = 2^{-k²} ∏_{j>k}(1−2^{-j})^{-1} Cohen-Lenstra-style.
- **Fouvry-Klüners (2007):** proves Gerth's for real quadratic unconditionally.
- **Smith (2017, arXiv:1702.02325):** full resolution of 2^k-class group distribution via Rédei symbol equidistribution.
- **Koymans-Pagano (2022):** Smith to imaginary quadratic; ray class groups with small modulus.

## 3. LMFDB Data

`nf_fields` (≈1.2M entries on devmirror):
- `class_group`, `narrow_class_group` invariant factors
- `disc_abs`, `disc_sign`, `ramified_primes`
- `galois_group`, `degree`, `signature`
- `regulator`, `class_number`

Quadratic: direct join. Higher degree: narrow/class gives signature contribution. Ray class with finite modulus reconstructed via PARI `bnrinit(bnf, m)` for targeted subsets. **For Rédei test, narrow-class 2-rank and 4-rank from stored invariant factors suffice.**

## 4. Test Design

**Stage A — Scan (10^6 NF, ~2 CPU-hr):**
1. Quadratic fields |disc| < 10^8 (~6×10^7; subsample 10^6 stratified by t = ω(disc)).
2. rk_2(Cl^+) and rk_4(Cl^+) from stored invariant factors.
3. Bin by t; predicted rk_2 = t−1 (Gauss) — sanity check, 100% equality.
4. Within each t-bin, empirical P(rk_4 = k) vs Gerth-Fouvry-Klüners via χ².

**Stage B — Rédei symbol density (~1.5 CPU-hr):**
1. Sample 10^5 split-prime triples (p_1, p_2, p_3) with compatible Legendre.
2. Compute [p_1, p_2, p_3] via PARI `rnfinit` + norm solver OR infer from stored 4-rank.
3. Equidistribution over {±1} (Smith predicts 1/2 each).
4. S_3 symmetry: |[p_1,p_2,p_3] − [p_2,p_1,p_3]| = 0 everywhere.

**Stage C — Higher-degree (~30 CPU-min):**
1. Cubic + quartic fields; examine 2-part of Cl^+.
2. Generalized genus rk_2 ≥ t − r − 1 holds tight?

## 5. Falsification

- **FAIL-A:** Gauss rk_2 = t−1 fails for any quadratic with complete LMFDB data → data corruption or parser bug. Hard stop.
- **FAIL-B:** Gerth-FK χ² p < 10^{-4} across t ∈ {2..6} → contradicts theorem; investigate stratification artifact.
- **FAIL-C:** Rédei symbol equidistribution deviates > 3σ on independent triples → symbol computation bug (theorem says 1/2).
- **FAIL-D:** S_3 symmetry violations above numerical noise → Rédei code bug.

Permutation null: shuffle (disc, rk_4) 1000× to confirm Gerth distribution not disc-stratified artifact.

## 6. Budget

- Stage A: 2 CPU-hr.
- Stage B: 1.5 CPU-hr.
- Stage C: 0.5 CPU-hr.
- **Total: ~4 CPU-hr.** SQL pull ~8 GB transient.

## 7. Expected Outcome

**Primary:** confirmation of Gerth-FK 4-rank distribution to χ² p > 0.05 across t-bins — **calibration milestone** establishing LMFDB ray class data consistent with proven theorems at 10^6 scale. Null-battery anchor.

**Secondary:** Rédei symbol equidistribution table → reusable Charon primitive for 2^k-class group forecasts (feeding Smith-style predictions into genus-2 Rosetta bridge). Stage C revealing unexpectedly tight/loose genus-formula for specific Galois groups (e.g., A_4 quartics) is a **sleeper lead** — Koymans-Pagano territory less-charted empirically.

**Null still useful:** adds Rédei/Gauss to null battery; raises falsification bar for future "2-part anomaly" claims.

**Word count: 793**
