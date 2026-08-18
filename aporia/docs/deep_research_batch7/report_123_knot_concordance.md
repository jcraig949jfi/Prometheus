# Deep Research Report #123: Knot Concordance Rank Empirics — Smooth vs Topological Slice Genus

**Target Agent:** Ergon
**Domain:** Knot Concordance / Low-Dimensional Topology
**Date:** 2026-04-23
**Feeds:** Silent-Island Knot Cluster

## 1. Problem Statement

Every knot K in S^3 bounds a smoothly embedded surface in B^4 of minimal genus g_4^s(K) and a locally flat topologically embedded surface of minimal genus g_4^t(K). Inequality g_4^t(K) ≤ g_4^s(K) is forced by smoothing. The **concordance gap** Δ(K) := g_4^s(K) − g_4^t(K) measures failure of topological category to detect smooth obstructions — purest empirical fingerprint of exotic 4-manifold phenomena visible at the knot level.

For 10^4 prime knots (crossing ≤ 15), catalog Δ(K) and test whether distribution matches Hedden-Livingston-Ruberman (2010) on density of topologically slice but smoothly non-slice.

## 2. Literature

- **Freedman (1982):** knots with trivial Alexander polynomial are topologically slice (g_4^t = 0). Infinite supply of Δ > 0 candidates when g_4^s > 0.
- **Rasmussen (2004):** s-invariant from Khovanov; |s(K)|/2 ≤ g_4^s(K); often sharp. Reproves Milnor without gauge theory.
- **Hedden-Livingston-Ruberman (2010):** infinite families of topologically slice with unbounded smooth 4-genus; positive-density within Whitehead doubles.
- **Sarkar (2021):** refines Rasmussen via equivariant Khovanov; sharpness at c = 13-15.
- **Piccirillo (2020):** Conway knot topologically slice but not smoothly — settles 50-year problem.

## 3. Data Source

LMFDB knot coverage **sparse**. Primary: **KnotInfo** (Livingston-Moore):
- Crossing ≤ 13: 2,978 knots with g_4^s, g_4^t fully tabulated.
- Crossing 14-15: ~8,000 additional with partial invariants (s, τ, Casson-Gordon).
- Alexander polys, σ, det, genus-3 Seifert data.

Mirror to Postgres via Mnemosyne; request `knotinfo_15x`.

## 4. Test Design

1. Ingest KnotInfo → `team_research.knots_concordance` (K, crossing, s, τ, g_4^s, g_4^t, Alex, σ).
2. **g_4^s bound** via Rasmussen: g_4^s ≥ |s|/2. SnapPy + KnotJob for uncomputed s. Upper bound via band-unknotting.
3. **g_4^t bound** via Casson-Gordon on 2-fold branched cover; τ from Heegaard Floer as secondary. For Alexander-trivial, Freedman forces g_4^t = 0.
4. **Gap Δ(K) = g_4^s − g_4^t**; histogram stratified by crossing.
5. **Null:** random Seifert matrix ensemble preserving det distribution.
6. **Falsification target:** HLR predicts Δ ≥ 1 density ~O(1/c) at crossing c among Alexander-trivial. If O(1/c²) or flat, refuted.

## 5. Falsification

- **K1:** Rasmussen saturates > 98% at c ≤ 13 → Δ dominated by known sharp cases; no signal.
- **K2:** Casson-Gordon and τ give identical g_4^t across sample → redundant; one channel, not two.
- **K3:** Δ across seeds (permuting Seifert null) z < 2 → seed-artifact.
- **K4:** Permutation null on (crossing, Δ) mandatory.

## 6. Budget

- Ingest + schema: 15 min.
- Rasmussen s (KnotJob, ~10^4 knots): ~3 CPU-hr.
- Casson-Gordon (Sage on branched covers): ~2 CPU-hr.
- Histogram + null + 5 seeds: ~1 CPU-hr.
- **Total: ~6 CPU-hours**, M1+M2 parallel.

## 7. Expected Outcome

**(A) HLR confirmed:** Δ ≥ 1 density O(1/c) among Alexander-trivial → positive quantitative result feeding Knot cluster in silent-island tensor. "Knot concordance gap law."
**(B) HLR refuted:** different scaling → publishable kill; Knot cluster gains null-anchor for battery calibration.
**(C) Gap sparse/bimodal:** outliers at Conway-like crossings only → exotic phenomena rare and localized; sharpens Piccirillo to density statement.

**Feeds silent-island Knot cluster:** (g_4^s, g_4^t) pair becomes new tensor column; enables cross-island tests with genus-2 Rosetta bridge. Slice genus is literally a 4-genus; genus-2 curves are universal 4D bridge. Expected ρ ≈ 0.15-0.25 against genus-2 rank column if exotic universal, ≈ 0 if accidental.

**No discovery claim before Harmonia Attack 4 permutation null.**

**Word count: 762**
