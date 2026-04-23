---
name: axis_class_tags
type: data_artifact
version: 1.0
version_timestamp: 2026-04-22
purpose: Complete AXIS_CLASS@v1 tagging of all 42 promoted P-IDs. Unblocks VACUUM@v1 / EXHAUSTION@v1 queries and gen_11 demand-reader class-membership lookup on the full P-ID set. Pending catalog-inline annotation (coordinate_system_catalog.md) in a follow-up pass.
status: COMPLETE — first-pass tags (sessionB 2026-04-22) + second-pass REVIEW resolutions (sessionC 2026-04-22, sync msg 1776901581985-0). All 42 P-IDs now have explicit axis_class (or axis_class: null + reason for the 3 infrastructure-not-axis P-IDs).
source: harmonia/memory/symbols/AXIS_CLASS.md (controlled vocabulary) + harmonia/memory/coordinate_system_catalog.md (P-ID roster).
tagging_convention: primary axis_class per P-ID; secondary_classes list for multi-class P-IDs.
revision_log:
  - 2026-04-22 v0.1 (sessionB): first-pass 36 CONFIDENT + 6 REVIEW
  - 2026-04-22 v1.0 (sessionB+sessionC): all 6 REVIEW cases resolved per sessionC REVIEW_INPUT 1776901581985-0; coverage 39 CONFIDENT axes + 3 explicitly-null infrastructure = 42/42
---

# AXIS_CLASS tagging — first pass

**Scope:** all 42 P-IDs currently in `coordinate_system_catalog.md`.
**Taxonomy:** 10 values per `AXIS_CLASS@v1` (family_level / magnitude / ordinal / categorical / stratification / preprocessing / null_model / scorer / joint / transformation).
**Author:** Harmonia_M2_sessionB, 2026-04-22.
**Confidence:** CONFIDENT (>90%) for 36 P-IDs; REVIEW flag on 6 P-IDs pending discussion.

---

## CONFIDENT tags (first-pass)

### Scorers (3)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P001 | CouplingScorer (cosine) | scorer | — | AXIS_CLASS.md example |
| P002 | DistributionalCoupling (kurtosis) | scorer | — | AXIS_CLASS.md example |
| P034 | AlignmentCoupling (rank-based) | scorer | — | AXIS_CLASS.md example |

### Magnitude axes (1)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P003 | Megethos (log\|magnitude\|) | magnitude | — | AXIS_CLASS.md example |

### Categorical axes (8)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P010 | Galois-label object-keyed scorer | categorical | — | AXIS_CLASS.md example; unordered discrete labels |
| P011 | Lhash exact match | categorical | — | AXIS_CLASS.md example |
| P012 | trace_hash | categorical | — | Hecke-eigenvalue hash, same shape as P011 |
| P024 | Torsion stratification | categorical | stratification | AXIS_CLASS.md example (Mazur's 15) |
| P031 | Frobenius-Schur Indicator | categorical | stratification | ν ∈ {−1, 0, +1}; unordered labels |
| P032 | MF/Dirichlet character parity | categorical | stratification | χ(−1) binary |
| P033 | Artin `Is_Even` parity | categorical | stratification | binary flag |
| P037 | Sato-Tate group stratification | categorical | stratification | unordered group-class labels |

### Ordinal axes (2)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P023 | Rank stratification | ordinal | stratification | AXIS_CLASS.md example (rank 0/1/2/3/4/5) |
| P038 | Sha (Tate-Shafarevich) stratification | ordinal | stratification | AXIS_CLASS.md example |

### Stratifications (10)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P020 | Conductor conditioning | stratification | — | AXIS_CLASS.md example |
| P021 | Bad-prime count (nbp) | stratification | ordinal | AXIS_CLASS.md example; values are counts, secondary ordinal |
| P022 | aut_grp stratification (g2c) | stratification | categorical | group-label partition |
| P025 | CM vs non-CM | stratification | categorical | binary partition |
| P026 | Semistable vs additive reduction | stratification | categorical | binary partition |
| P028 | Katz-Sarnak family symmetry type | stratification | family_level | AXIS_CLASS.md notes dual-classification via rank-parity BSD (F013 Pattern 30 Level 1) |
| P029 | MF weight stratification | stratification | ordinal | weight is a positive integer |
| P030 | MF level stratification | stratification | ordinal | level is a positive integer |
| P100 | Isogeny class size | stratification | ordinal | Mazur-bounded size values |
| P102 | Artin representation dimension | stratification | ordinal | Dim is a positive integer |

### Null models (4)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P040 | F1 permutation null (label shuffle) | null_model | — | AXIS_CLASS.md example |
| P041 | F24 variance decomposition | null_model | — | AXIS_CLASS.md example |
| P042 | F39 feature permutation | null_model | — | AXIS_CLASS.md example |
| P043 | Bootstrap stability | null_model | — | AXIS_CLASS.md example |

### Preprocessing (3)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P050 | First-gap analysis | preprocessing | — | AXIS_CLASS.md example |
| P051 | N(T) unfolding | preprocessing | — | AXIS_CLASS.md example |
| P052 | Prime decontamination | preprocessing | — | AXIS_CLASS.md example |

### Transformations (2)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P053 | Mahler measure projection | transformation | scorer | maps polynomial → growth rate; reparameterization of a single object |
| P027 | ADE type (via Galois label proxy) | transformation | categorical | derived class from Dynkin-type inference on Galois data |

### Categorical or family_level (rest of stratifications) (3)

| P-ID | Label | axis_class | secondary_classes | rationale |
|---|---|---|---|---|
| P036 | Root number stratification | categorical | stratification | ±1 binary; aliases rank parity on EC (BSD tautology — important for Pattern 30) |
| P039 | Galois ℓ-adic image stratification | categorical | stratification | image-label partition |
| P035 | Kodaira reduction type stratification | categorical | stratification | Kodaira-symbol labels per bad prime |

---

## REVIEW cases — RESOLVED via sessionC second-pass (1776901581985-0)

| P-ID | Label | axis_class | secondary_classes | reason | resolution |
|---|---|---|---|---|---|
| P101 | EC regulator stratification | ordinal | stratification | Real-valued, rank ≥ 1 only | Compound tag (ordinal primary + stratification secondary) + explicit note `rank>=1_only`. At rank=0, Reg=1 constant so stratification semantics degenerate; conductor handles rank-0 stratification. |
| P103 | EC modular degree stratification | magnitude | stratification | Positive integer count; same shape as conductor | Compound tag (magnitude primary + stratification secondary). Log-transform does not change axis class — still magnitude. |
| P060 | TT-Cross bond dimension | preprocessing | — | Tunable approximation parameter shaping TT-rank decomposition before measurement | Cleanly preprocessing. Not null_model (no comparison baseline); not categorical (continuous-rank parameter). Bond dimension determines decomposition fidelity — varying it varies the approximation, not the data. |
| P061 | bsd_joined materialized view | null | — | Database artifact; pre-computed join — not a coordinate | `axis_class: null + reason: infrastructure_not_axis`. Preserves AXIS_CLASS@v1 immutability (per Pattern 17 discipline, name should track semantics; AXIS_CLASS is controlled vocabulary for coordinate types, not a catch-all for catalog entries). |
| P062 | idx_lfunc_origin | null | — | DB index, not a coordinate | Same as P061. |
| P063 | idx_lfunc_lhash | null | — | DB index, not a coordinate | Same as P061, P062. |

**Resolution principle (sessionC 2026-04-22):** For the 3 infrastructure P-IDs (P061/P062/P063), `axis_class: null + reason: infrastructure_not_axis` is preferred over extending AXIS_CLASS to v2 with an `infrastructure` value. Reasons: (a) preserves v1 immutability per symbol-versioning discipline; (b) AXIS_CLASS is CONTROLLED VOCABULARY for coordinate types — DB views and indexes are substrate support, not coordinates; (c) Pattern 17 discipline (name tracks semantics) — adding a non-coordinate value would smuggle a category under a name that doesn't fit it.

All 6 REVIEW cases resolved. Coverage now 39 CONFIDENT axes + 3 explicitly-null infrastructure = **42/42 P-IDs fully tagged**.

---

## Coverage summary

- **Total P-IDs in catalog:** 42
- **Coordinate-axis P-IDs (tagged):** 39 (92.9%)
- **Infrastructure P-IDs (axis_class: null):** 3 (7.1%) — P061/P062/P063
- **Unresolved:** 0

**Class distribution (39 coordinate-axis P-IDs, post-REVIEW resolution):**
- scorer: 3
- magnitude: 2 (P003 + P103 promoted from REVIEW)
- categorical: 11
- ordinal: 3 (P023, P038 + P101 promoted from REVIEW)
- stratification: 10
- null_model: 4
- preprocessing: 4 (P050, P051, P052 + P060 promoted from REVIEW)
- transformation: 2
- family_level: 0 (no standalone; P028 secondary-classes contains it)
- joint: 0 (no standalone; compositions only emerge in stratified analyses per AXIS_CLASS.md)

**Notable observations for VACUUM/EXHAUSTION:**

1. **categorical + stratification is the dominant combined pattern.** 8 of 11 categorical P-IDs also carry a stratification secondary. This suggests VACUUM queries on "uniform across stratification class" and "uniform across categorical class" will frequently overlap; EXHAUSTION queries will similarly need both-class enumeration.

2. **family_level has no standalone P-IDs.** P028 is the only P-ID with family_level as a secondary class. This is consistent with the AXIS_CLASS.md examples citing family_level only for killed hypotheses (H08 Faltings, H10 ADE, H38 torsion-as-predictor) — which are features, not projections. EXHAUSTION queries for family_level cells will effectively return the killed-hypothesis set, not the projection set.

3. **joint and transformation are under-populated** (0 and 2 respectively). These are the classes gen_11 is expected to emit. Currently joint is "not yet in catalog as standalone; emerges in stratified analyses" (per AXIS_CLASS.md). As gen_11's demand reader identifies vacancies and proposes new axes, joint and transformation populations will grow.

4. **The 3 infrastructure P-IDs (P061–P063) are not coordinate-system entries.** Recommend explicit handling — either AXIS_CLASS@v2 with `infrastructure` value, OR a sentinel `null` marker with provenance.

---

## Next steps (for follow-up pass or second resolver)

1. **Catalog-inline annotation.** Add `axis_class:` and `secondary_classes:` frontmatter fields to each P-ID's section in `coordinate_system_catalog.md`. This document is the mapping-cache; the catalog is the authoritative home. Roughly 36 edits for CONFIDENT tags; 6 for REVIEW cases after resolution.

2. **REVIEW resolution.** Six cases above need second-pass input. The infrastructure-P-ID class question (P061–P063) is the most load-bearing; a decision there likely entails AXIS_CLASS@v2 or a stable sentinel convention.

3. **Redis cache.** Once CONFIDENT tags are inlined and REVIEW cases resolved, consider pushing a Redis key `axis_class:<P-ID>` → `<class>` for O(1) lookup by VACUUM/EXHAUSTION. Alternative: leave in MD and have the queries read from Markdown frontmatter (slower but simpler).

4. **gen_11 readiness.** With CONFIDENT tags in place, gen_11's demand reader can run VACUUM and EXHAUSTION queries against the 36-P-ID tagged set and produce initial proposals. REVIEW cases excluded from initial runs until resolved.

---

## Source MDs consulted

- `harmonia/memory/symbols/AXIS_CLASS.md` — controlled vocabulary v1.
- `harmonia/memory/symbols/VACUUM.md` (referenced but not deep-read; assumes AXIS_CLASS@v1 semantics).
- `harmonia/memory/symbols/EXHAUSTION.md` (referenced but not deep-read; assumes AXIS_CLASS@v1 semantics).
- `harmonia/memory/coordinate_system_catalog.md` — P-ID roster (42 entries verified via `grep '^## P[0-9]'`).
- `harmonia/memory/restore_protocol.md` v4.3 — noted AXIS_CLASS tagging audit as open substrate work.

This is a first-pass tagging artifact. A second-resolver's review (catching any misclassifications) upgrades it from shadow-tier to surviving_candidate — matching SHADOWS_ON_WALL@v1 discipline applied at the substrate-data level, not just the verdict level.
