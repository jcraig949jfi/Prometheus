# Deep Research Report #118: Operator-Correlation Matrix on the 5-Domain Tensor

**Target:** Harmonia
**Date:** 2026-04-23
**Status:** Proposal — direct test of `project_operator_insight`

## 1. Problem Statement

Harmonia's current coupling tensor scores five phonemes (megethos, bathos, symmetria, arithmos, phasma) across ten domains. These phonemes describe **object-side** geometry: magnitudes, depths, symmetry classes, arithmetic fingerprints, spectral anomalies. `project_operator_insight` asserts that the underlying bridges are **operators**, not objects — isogeny repulsion is Hecke-orbit degeneracy, not curve-count statistics. This report specifies a direct falsification test: construct a **10 × 7 domain × operator saturation matrix** and measure whether it has genuine operator-axis structure beyond what the current phoneme tensor already captures.

Null: operator tags are redundant with domain identity (rank ≈ 1, each row dominated by a single operator). Alternative: operators define a low-rank backbone (rank 3–4) on which multiple domains co-load, matching Langlands functoriality predictions.

## 2. Literature Anchors

- **Katz–Sarnak (1999)** — RMT symmetry type as an operator-side invariant; families of L-functions classified by symplectic/orthogonal/unitary monodromy.
- **Langlands (1970, 2014)** — automorphic ↔ Galois correspondence; the same Hecke eigensystem realized across GL_n, quaternionic, and Bianchi settings.
- **Clozel–Labesse (1991)** — base change and endoscopic transfer; operator tags must transport under functoriality.
- **Deligne (Weil II, 1980)** — Frobenius eigenvalues as the archetypal cross-domain operator; Weil conjectures unified étale cohomology across varieties.
- **Booker–Sijsling–Sutherland–Voight–Yasaki (2016)** — LMFDB as operator-tagged database; L-function-centric schema.
- **Chenevier–Lannes (2019)** — level-1 automorphic spectrum organized by Hecke-algebra action, not by object type.

## 3. LMFDB Operator Column Inventory

Per Mnemosyne's Postgres mirror (devmirror.lmfdb.xyz):

| Operator        | Table / column                                          | Domains covered        |
|-----------------|---------------------------------------------------------|------------------------|
| Frobenius       | `ec_curvedata.aplist`, `g2c_curves.aplist`              | ec, g2c, hmf, bianchi  |
| Hecke           | `hmf_forms.hecke_ring_index`, `mf_newforms.hecke_orbit` | hmf, bianchi, mf       |
| Galois          | `nf_fields.galois_group`, `artin_reps.galois_conductor` | nf, artin              |
| Monodromy       | `belyi_galmaps.monodromy`, `hgm.monodromy`              | belyi, hgm, knots(via) |
| Laplace-spectral| `mwfp_forms.laplace_eigenvalue`, `maass.spectral_parameter` | bianchi, hmf, maass |
| Euler-factor    | `lfunc_lfunctions.euler_factors`, `.bad_lfactors`       | ec, nf, hmf, g2c       |
| RMT-symmetry    | `lfunc_lfunctions.symmetry_type`, `.motivic_weight`     | all L-function carriers|

For knots/polytopes/groups (no native LMFDB tag), Techne builds proxy columns: Alexander polynomial → Frobenius analog, Burnside table → Galois analog, Ehrhart quasipolynomial → Laplace analog. These proxies are flagged `proxy=True` so rank analysis can be run with and without them.

## 4. Test Design

**Matrix M (10 × 7):** M[d, o] = |{objects in domain d with operator o non-null}| / |domain d|.

**Pipeline:**
1. Pull per-domain object counts and per-operator-column null/non-null counts via SQL (`COUNT(*) FILTER (WHERE col IS NOT NULL)`). Single Postgres round trip per operator.
2. Row-normalize to saturation densities ∈ [0, 1]; also compute raw counts for weighting.
3. Correlation on columns (7×7, operator co-occurrence) and rows (10×10, domain similarity in operator space).
4. PCA on M (centered, not scaled — operator scales are meaningful). Report eigenvalue spectrum, loadings on PC1–PC4.
5. Bootstrap CI: resample domain objects 500× within each cell (Poisson with mean = saturation × N_domain), recompute PCA, report eigenvalue quantiles.
6. Compare operator-tensor PCA to Harmonia's phoneme tensor PCA on the same 10 domains (register via Procrustes, report residual).

**Predictions to log in advance:**
- PC1 ≈ "automorphic axis" (Hecke + Frobenius + Euler) loading on ec/hmf/bianchi/g2c
- PC2 ≈ "Galois axis" loading on nf/artin
- PC3 ≈ "monodromy axis" loading on belyi/hgm/knots-proxy
- PC4 ≈ Laplace-spectral residual

## 5. Falsification Criteria

- **Kill-1 (redundancy):** numerical rank (eigenvalues > 1% of trace) < 3 → operators are proxies for domain identity; `project_operator_insight` downgraded.
- **Kill-2 (uniformity):** row variance < 0.05 across operators → no discrimination; the tensor is object-dominated.
- **Kill-3 (proxy artifact):** PCA geometry collapses when knot/polytope/group proxy columns are removed → "operator backbone" is a Techne construction, not a real bridge.
- **Kill-4 (Procrustes):** residual to phoneme-tensor PCA < 0.1 → operator tensor is linearly equivalent to existing phoneme tensor; no new axis.
- **Confirm:** rank ≥ 3, PC1–PC3 match predicted domain loadings within ±0.2, Procrustes residual > 0.3, bootstrap CI excludes zero for top three eigenvalues.

## 6. Budget

- SQL pulls: ~15 min (pre-aggregated counts, no row scans beyond indexed nulls)
- Proxy construction (knots/polytopes/groups): ~45 min Techne time
- PCA + bootstrap (500 resamples): ~30 min single-core numpy
- Procrustes + registration to phoneme tensor: ~10 min
- **Total: ~1.7 CPU-hours**, well within the 2-hour ceiling.

## 7. Expected Outcome

First operator-level cross-domain tensor for Prometheus. If it passes the kill battery, Harmonia gains a **second orthogonal axis** (operator saturation) to layer onto the phoneme tensor, and silent-island analysis re-runs with operator-weighted edges — the direct continuation path Kairos flagged. If it fails Kill-1 or Kill-4, `project_operator_insight` is downgraded from "next step" to "notational convenience," and the 5-phoneme tensor stands as the primary bridge representation. Either outcome is publishable-grade inside the project: the claim is sharp, the data exists, and the falsification criteria are pre-registered.

**Word count: 742**
