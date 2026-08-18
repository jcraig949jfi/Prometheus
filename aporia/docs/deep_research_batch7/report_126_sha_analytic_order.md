# Deep Research Report #126: Tate-Shafarevich Analytic Order Distribution

**Target Agent:** Charon
**Topic:** Ш distribution across rank-0 elliptic curves at log conductor > 8
**Date:** 2026-04-23

## 1. Problem Statement

The Tate-Shafarevich group Ш(E/Q) is the obstruction to local-global for E. For rank-0 curves, BSD predicts:

    |Ш(E)|_an = L(E,1) · |E(Q)_tors|² / (R · Ω_E · ∏_p c_p)

where R=1 (trivial regulator at rank 0), Ω_E is real period, c_p Tamagawa. Delaunay heuristics predict |Ш| concentrates at squares {1, 4, 9, 16, ...} with specific Cohen-Lenstra-over-alternating-forms densities.

**Q:** does empirical |Ш| distribution across rank-0 curves with log_10(N) > 8 match Delaunay, or does high-conductor tail deviate? Prior tabulations (Cremona) dominated by low conductor. LMFDB now extends to N ~ 10^9 — new regime.

## 2. Literature Anchors

- **Delaunay (2001)** Exp. Math.: |Ш| heuristic, rank-0, ordered by conductor. Prob(|Ш|=n²) for odd n via Cohen-Lenstra product. Predicts Prob(|Ш|=1) ≈ 0.9752, Prob(|Ш|=4) ≈ 0.0200, Prob(|Ш|=9) ≈ 0.00227.
- **Delaunay (2007)** LMS Lecture Notes 341: refined including 2-part; joint with rank; E[|Ш|] conditional on rank=0.
- **Bhargava-Shankar (2015)** Annals: bounded average rank via 2-Selmer; ≥ 66% rank ≤ 1.
- **Park-Poonen-Voight-Wood (2017):** heuristic for ranks and Ш via random alternating matrices over Z_p; sharper tail.
- **Bhargava-Kane-Lenstra-Poonen-Rains (2015):** random matrix model for Selmer; underlying machinery for n²-concentration.

## 3. LMFDB Data Plan

Postgres mirror:
```sql
SELECT lmfdb_label, conductor, rank, sha_an, torsion_order,
       tamagawa_product, real_period, special_value
FROM ec_curvedata
WHERE rank = 0
  AND conductor > 100000000
  AND sha_an IS NOT NULL;
```

Yield: ~300K-1M rank-0 curves at log N > 8 (LMFDB reaches N ≤ 5×10^8 complete; partial to 10^9). Cross-check sha_an against BSD recomputation L(E,1)·tors²/(Ω·∏c) to catch stale analytic-order columns.

## 4. Test Design

**Stratification:**
- Bin 1: 10^8 < N ≤ 10^{8.5}
- Bin 2: 10^{8.5} < N ≤ 10^9
- Control: 10^6 < N ≤ 10^7 (Delaunay's original regime)

**Per bin:**
1. Empirical histogram |Ш|. Report Prob(|Ш|=k²) for k ∈ {1,2,3,4,5,7}.
2. KS-style comparison vs Delaunay CDF (square-supported).
3. Mean log|Ш|, variance; PPVW growth O(log log N).
4. Conditional: within bin, stratify by 2-Selmer rank to separate 2-part of Ш from odd part.

**Null models:**
- A: uniform over squarefree (trivial rejection baseline).
- B: Delaunay 2001 (prediction under test).
- C: PPVW 2017 (refined).

χ² on first 6 square bins + "tail" bin for |Ш| ≥ 49.

## 5. Falsification Criteria

Delaunay killed at this regime if any:
1. χ²(Delaunay) in Bin 1 or 2 gives p < 0.001 with realign.py multiple-testing across 3 bins.
2. Non-square |Ш| > 0.1% → BSD-computation bug (triage first).
3. Prob(|Ш|=1) in high-conductor bins deviates from 0.9752 by > 3σ under bootstrap (n=1000).
4. Mean log|Ш| exceeds PPVW O(log log N) envelope at > 2σ.

**Permutation null mandatory:** shuffle conductor labels within bin; recompute χ². Real signal > shuffled 99th percentile.

## 6. Budget

- Postgres pull + isogeny-dedupe: ~0.5 CPU-hr.
- sha_an verification via mwrank/PARI on 5% sample: ~2 CPU-hr.
- Histogram + χ² + bootstrap + permutation: ~1 CPU-hr.
- Cross-tab with 2-Selmer: ~0.5 CPU-hr.
- **Total: ~4 CPU-hr.** No GPU.

## 7. Expected Outcome

**60%:** Delaunay holds at log N > 8; Prob(|Ш|=1) ≈ 0.975 ± 0.002. Calibration anchor (rare positive); publishable replication.
**30%:** tail deviation — high-conductor shift toward larger |Ш|, consistent with PPVW refinement over Delaunay. First empirical tension between 2001 and 2017 heuristics at scale.
**10% kill:** non-square mass or Prob(|Ш|=1) < 0.95 → either LMFDB BSD-column bug (likely) or genuine anomaly (remote). Triage via mwrank.

Feeds Charon conditional-law registry; pairs with rank-0 L-value concentration work in v10 battery.

**Word count: 748**
