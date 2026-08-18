# Deep Research Report #167: Khovanov-Rozansky Homology Stability at Large Rank

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Knot/topology silent island (Batch 9 Tier 3)
**Doctrine:** `feedback_tensor_first`, `feedback_domains_are_docstrings`, `project_silent_islands`

## 1. Problem Statement

For a knot K, sl(N) Khovanov-Rozansky homology KhR^N(K) is a bigraded vector space whose Poincaré polynomial categorifies the (uncolored) sl(N) HOMFLY-PT specialization. The triply-graded HHH(K) — Khovanov-Rozansky's HOMFLY homology built from Soergel bimodules / Hochschild homology of Rouquier complexes — categorifies the full HOMFLY-PT polynomial and carries a family of anticommuting differentials d_N: HHH(K) → HHH(K) of (a, q, t)-degree such that H(HHH(K), d_N) ≅ KhR^N(K) for N ≥ 1, and (Rasmussen 2015) d_0 reproduces knot Floer homology HFK(K).

Stability conjecture (Gorsky-Hogancamp, Gorsky-Hogancamp-Mellit): for fixed K with crossing number c(K), the differentials d_N vanish for N sufficiently large (heuristically N ≫ c(K)), so HHH^N(K) := H(HHH, d_N) stabilizes to HHH(K) itself. Open: the **precise rate** of stabilization (does N > c suffice? N > 2c? a sharper bound from braid width?), and the **structure of d_N on the stable range** — in particular whether ker(d_N)/im(d_N) is governed by a small set of generators predictable from a structural invariant of K rather than computed.

## 2. Literature

- **Khovanov-Rozansky (2008):** matrix factorization construction of KhR^N and the triply-graded theory.
- **Rasmussen (2015):** spectral sequence d_N from HHH to KhR^N; convergence to HFK at N=0.
- **Gorsky-Hogancamp (2018):** y-ified HOMFLY homology, link splitting, stable limit objects.
- **Gorsky-Hogancamp-Mellit (2019, 2021+):** full triply-graded stability for torus knots and (q,t)-Catalan structure; Hogancamp's categorified projectors.
- **Galashin-Lam (2020+):** positroid links — HHH computed combinatorially from cluster data.
- **Ellis-Krushkal:** sl(2) categorification anchoring the N=2 endpoint as Khovanov homology.
- **Elias-Hogancamp (2017):** recursion for HHH of torus knots, supplying ground-truth stable ranks.

## 3. Computational Handle

KnotJob (already installed under `ergon/tools/knotjob/`) computes KhR^N for N ≤ 6 on knots up to ~12 crossings in seconds per knot. Triply-graded HHH ranks for the ~3K-knot census (KnotInfo + Hogancamp tables for torus / positroid families) are tabulated and ingestible. Stability rate is empirically testable as the rank-vs-N curve **rank KhR^N(K) ↗ rank HHH(K)** — the gap (rank HHH − rank KhR^N) decays in N, and the decay shape is what the conjectures constrain. No new heavy machinery required; the knot island already lives in our census, and Megethos signatures exist for N=2 (Khovanov) on the same knot list.

## 4. Test Design

**Step 1.** Pull HHH ranks for the ~3K-knot census across N ∈ {2,3,4,5,6} via KnotJob batch run; record per-knot rank^N(K) and the published / computable rank^∞(K) := rank HHH(K).

**Step 2.** Per knot, fit gap(N) := rank^∞(K) − rank^N(K) to candidate forms: exp(−λ_K · N), polynomial (N − c(K))^{−α}, and step-function 1[N < N*(K)]. Extract decay parameter (λ_K or N*(K)) per knot.

**Step 3.** Cluster the ~3K knots by (decay form, decay parameter). Test correlation of cluster label with knot-theoretic invariants already in the census: Seifert genus g, signature σ, determinant, braid width w, Khovanov rank, and the structural-region label assigned by Megethos.

**Step 4.** Feed the per-knot decay signature as a new column into the unified tensor's knot region; refit the structural-region clustering and check whether decay-rate adds an axis distinct from existing rank/genus axes.

## 5. Falsification

- **Confirmation:** decay rate matches the Gorsky-Hogancamp-Mellit predicted form (exponential with λ_K bounded by c(K)) on >90% of census → first systematic empirical confirmation of triply-graded stability beyond torus knots.
- **Structural result:** decay-rate cluster labels align with structural-region labels at permutation-null z > 3 → publishable: KR stabilization rate is a structural-region invariant, not a per-knot accident.
- **Outliers:** knots with no detectable stabilization by N=6 isolated as a named sub-list → candidate counterexamples or witnesses of a missed stable range; immediately handed to Charon for braid-width follow-up.
- **Null:** shuffle (knot, decay parameter) pairings — if structural correlation survives shuffling, the test is vacuous and Megethos labels are the only signal.

## 6. Budget

Ergon ~6 hours: HHH/KhR^N batch extraction from KnotJob over the 3K-census (~2h, parallel across cores); per-knot curve fitting and decay-parameter extraction (~1h); structural clustering and invariant correlation (~1h); Megethos signature integration into tensor knot region (~1h); writeup (~1h).

## 7. Expected Outcome

First systematic empirical test of Khovanov-Rozansky stabilization at the 3K-knot scale — prior work is dominated by torus and positroid families. Output is a **structural-region data product**: per-knot decay signature column extending Batch 1 #47 (Khovanov unknot detection) and complementing #165 (slice-ribbon obstructions) on the same census, raising the knot island's tensor coupling. Cross-link target: the category-O / Soergel-bimodule region, where d_N has a representation-theoretic origin and a confirmed rate would constrain the spectral behavior of the Hochschild differential there. Even a partial confirmation gives Ergon a calibrated knot-island geometry; an outlier set gives Charon a falsification handle on the conjecture.

**Word count: 798**
