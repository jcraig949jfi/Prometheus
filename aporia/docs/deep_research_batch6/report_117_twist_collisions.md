# Deep Research Report #117: Twist Family Collisions in Discriminant-Matched EC Selection

**Target agent:** Charon
**Date:** 2026-04-23
**Topic:** Quadratic twist family collisions at high conductor — finite-size selection bias audit for F011 and Batch 5

## 1. Problem Statement

Every E/Q sits in a twist orbit {E^d : d ∈ Q^× / (Q^×)²}. Members share j-invariant but have conductors N(E^d) scaling with d² · rad(d)-dependent factors; discriminants Δ(E^d) = d^6 Δ(E) up to minimalization. Filtering by |Δ| or N thresholds may sample **multiple twists of the same j-class** — pseudo-replicates inflating apparent couplings.

F011 and several Batch 5 findings correlated discriminant-derived features against rank/regulator at log cond > 10. If high-conductor tail is enriched in twist-collision clusters, effective df are overstated and z-scores biased upward. Selection-geometry confounder distinct from prime-atmosphere.

## 2. Literature

- **Goldfeld (1979):** density conjecture for ranks in quadratic twist families; 50/50 rank-parity heuristic dominates high-d statistics.
- **Heath-Brown (1994, 2004):** 2-Selmer in twist families; explicit collision control via squarefree d. #{d : |d| < X, N(E^d) < Y} ≪ X^{1/2} Y^{1/3} for fixed E.
- **Rubinstein (2001):** L-value statistics in twist families, empirical to |d| ≤ 10^8; documents finite-size artifacts.
- **Bhargava–Skinner–Zhang (2014):** positive proportion rank-0 and rank-1; orbit counts estimate expected collision multiplicity per conductor bin.

Null under uniform squarefree-d sampling: collision multiplicity in log-conductor bin width 0.1 scales as O(log N), not O(N^ε).

## 3. LMFDB Data

Primary:
- `ec_curvedata` — `lmfdb_label`, `conductor`, `disc`, `jinv`, `ainvs`, `rank`, `regulator`, `torsion`
- `ec_twists` — `twist_class_label`, `minimal_twist_disc`
- `ec_iwasawa` — independent p-adic cross-check

Query (via Mnemosyne): curves with log_10 N ∈ [10, 12], group by `jinv` mod Q^{×12} (j-class within twist orbit), count orbit reps per 0.1-width log N bin.

Size: ~400K curves in target window.

## 4. Test Design

**Step A — Collision rate.**
For each bin [10.0, 10.1), ..., [12.9, 13.0):
1. Count distinct j-classes J_b.
2. Count total curves C_b.
3. Collision multiplicity μ_b = C_b / J_b.
4. Null μ_b^null from squarefree-d sampling (Heath-Brown, calibrated on low-bin where collisions provably rare).

**Step B — F011 sensitivity audit.**
Re-run F011 correlation under three resampling regimes:
1. Full data (reproduce original z).
2. One-per-j-class (minimal-|d| twist only).
3. Cluster bootstrap over j-classes (1000 iterations).

Correct z-score is regime 3. If regime 1 ≫ regime 3, F011 is collision artifact.

**Step C — Batch 5 crosswalk.**
Apply cluster bootstrap to Batch 5 findings using discriminant-matched cohorts. Flag any whose z drops below 2.0 under clustering.

## 5. Falsification

"F011 confounded by twist collisions" is **falsified** if:
- μ_b ≤ 1.3 across all high-conductor bins, AND
- cluster-bootstrap z for F011 within 10% of naive z.

**Confirmed** if:
- μ_b > 2 in any bin with log N > 10.5, OR
- cluster-bootstrap z drops > 30% vs naive z.

Intermediate (10-30% z reduction): partial confounding; corrected z replaces original.

## 6. Budget

- SQL aggregation over ec_curvedata: ~20 min.
- F011 re-compute under 3 regimes: ~2 CPU-hr (bootstrap dominates).
- Batch 5 crosswalk (~6 findings): ~4 CPU-hr.
- Plots + writeup: ~1.5 CPU-hr.
- **Total: ~8 CPU-hr**, single overnight on Charon.

## 7. Expected Outcome

**Audit, not discovery.** Outputs:
- Collision multiplicity curve μ_b vs log N — calibration asset for every future EC correlation study.
- Revised z-scores for F011 and Batch 5 with cluster-aware error bars.
- Likely ≥1 finding drops below significance (assume-wrong prior + null-battery kill rate). Survival under cluster-bootstrap materially strengthens F011 — removes one of three unaudited confounders (prime atmosphere, Selmer parity, twist collision).

Artifacts: collision multiplicity table, three z-score columns per finding, recommendation: add `TWIST_COLLISION` precondition to Charon's battery if confirmed.

**Word count: 748**
