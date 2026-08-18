# Report 195 — Kissing Number Bounds in d = 4..10

**Aporia Problem #195** — discrete geometry, structural region of lattice space at dimension d.
**Date:** 2026-04-28. **Substrate:** Prometheus / Aporia. **Doctrine:** feedback_tensor_first, feedback_calibration_anchors_in_depth.

---

## 1. Problem Statement

The kissing number τ_d is the maximum number of non-overlapping unit balls in R^d that can simultaneously touch a fixed central unit ball. Equivalently, the maximum size of a spherical code on S^{d-1} with minimum angular distance ≥ π/3. Closed values are known only at four dimensions: τ_1 = 2 (trivial), τ_2 = 6 (hexagonal), τ_3 = 12 (Schütte–van der Waerden 1953, with a 350-year Newton–Gregory pre-history), τ_4 = 24 (Musin 2008 via SDP three-point bound on the D_4 configuration), τ_8 = 240 (Levenshtein 1979 / Odlyzko–Sloane 1979 via LP, achieved by E_8), τ_24 = 196560 (Cohn–Kumar–Miller–Radchenko–Viazovska 2017 via modular-form magic functions, achieved by Λ_24). The open dimensions in our window are d ∈ {5, 6, 7, 9, 10} with current best intervals roughly: τ_5 ∈ [40, 44], τ_6 ∈ [72, 78], τ_7 ∈ [126, 134], τ_9 ∈ [306, 364], τ_10 ∈ [500, 554]. Lower bounds come from explicit constructions (laminated lattices Λ_d, K_12); upper bounds come from semidefinite-programming relaxations of three- and four-point energy functionals.

---

## 2. Literature

- **Schütte & van der Waerden (1953)** — Settled τ_3 = 12; introduced the spherical-cap covering argument.
- **Musin (2003, 2008)** — τ_4 = 24 via Delsarte-style SDP using three-point correlations on S^3; first dimension where LP alone is insufficient.
- **Levenshtein (1979)** / **Odlyzko–Sloane (1979)** — Independent LP proofs of τ_8 = 240 and τ_24 = 196560.
- **Cohn–Elkies (2003)** — LP framework for sphere packing and kissing; established the optimization template.
- **Bachoc–Vallentin (2008)** — SDP three-point bound; improved upper bounds in d = 5..10; explicit dual feasible solutions.
- **Mittelmann–Vallentin (2010)** — Numerical SDP at scale; current published upper bounds for d ≤ 12 derive from this pipeline.
- **Cohn–Triantafillou (2022)** — Three-point semidefinite improvements via reduced symmetry; tighter slabs in d = 9, 10, 11.
- **Cohn–Kumar–Miller–Radchenko–Viazovska (2017)** — Magic-function method for d = 8, 24; conjectured to extend, but no candidate magic function is known for d ∈ {5..10}.

---

## 3. LMFDB / Corpus Data

- **Nebe–Sloane Lattice Catalogue** (catalogue.math.rwth-aachen.de) — explicit Gram matrices for D_n, E_6, E_7, E_8, K_12, Λ_d (laminated), with kissing number, automorphism order, theta series, and design strength tabulated.
- **Conway–Sloane SPLAG** Chapters 4–6 — laminated lattices Λ_5..Λ_10 (kissing numbers 40, 72, 126, 240, 272, 336), K_12 (756), Leech construction history.
- **LMFDB** has no first-class kissing-number table; lattice data must be ingested from Nebe–Sloane and cross-checked against `nf` / `gg` discriminant fields where lattice ↔ number-field bridges exist (peripheral).
- **Ergon corpus state**: no SDP solver yet wired; TOOL_SDP_RELAX (REQ-029) is unforged. Lattice ingestion would land in a new `aporia/lattices/` shard.

---

## 4. Test Design

1. **Ingest.** Pull all named lattices in d = 4..10 from Nebe–Sloane with τ ≥ 0.7·best-known-lower (so τ ≥ 28, 50, 88, 213, 350 for d = 5..10 respectively). Estimated 20–40 lattices per dimension after symmetry-orbit collapse.
2. **Direct τ computation.** Enumerate minimal vectors via Fincke–Pohst on the Gram matrix; count vectors of squared norm equal to the minimum. Ground-truth τ per lattice. Calibration anchor.
3. **Signature extraction.** For each lattice L emit `sig(L) = (τ(L), |Aut(L)|, root_system_type, design_strength_t, theta_q^4_coeff)`. Push into substrate as a signature-keyed shard.
4. **SDP upper-bound replication.** Forge TOOL_SDP_RELAX (REQ-029) wrapping Bachoc–Vallentin three-point SDP via SCS or MOSEK; replicate published upper bounds for d = 5..10 to ≤ 0.5 absolute tolerance. PATTERN_VRAM_TRUNCATION_ARTIFACT applies — three-point SDP at d = 10 has matrix blocks ≥ 8 GB; record memory ceiling and Gegenbauer-degree-truncation level explicitly.
5. **Cluster + gap-closure flag.** Project signatures into substrate's existing dimensional shards; flag any d where (a) multiple distinct lattices saturate the current lower bound (rigid construction), or (b) SDP dual slack is < 2 % (upper bound methodologically near-tight). Per PATTERN_BASE_RATE_NEGLECT: report `(n_lattices_tested_per_d, n_unique_τ_values, n_at_lower_bound)` for every claim.

---

## 5. Falsification (calibration anchors)

- **D_4 must give τ = 24** — if the enumerator returns anything else, halt and audit the Gram-matrix loader.
- **E_8 must give τ = 240** — non-negotiable; closed since 1979.
- **Λ_5 → 40, Λ_6 → 72, Λ_7 → 126, Λ_9 → 272, Λ_10 → 336, K_12 → 756** — laminated / Coxeter–Todd anchors.
- **SDP upper bounds** must reproduce Mittelmann–Vallentin tables (τ_5 ≤ 44, τ_6 ≤ 78, τ_7 ≤ 134, τ_9 ≤ 364, τ_10 ≤ 554) to within published precision; deviation > 1 indicates solver misconfiguration, not a discovery.
- **Null model** — random unit-norm point sets on S^{d-1} with greedy angular packing should land far below τ_lower; if random configs approach τ_lower, the metric is broken.

---

## 6. Budget

Ergon ~8 h wall-clock. Breakdown: 1 h ingestion + Gram-matrix normalisation, 1 h Fincke–Pohst enumeration (cheap, d ≤ 10), 4 h SDP solver forging + replication runs (dominant cost; SDP-heavy, GPU not helpful), 1 h signature emission + clustering, 1 h falsification battery + report. SDP memory ceiling at d = 10 is the binding constraint; budget assumes degree-12 Gegenbauer truncation.

---

## 7. Expected Outcome

Primary deliverable: **calibration-anchor density in d = 4..10**, where the substrate currently holds essentially no discrete-geometry anchors (per feedback_calibration_anchors_in_depth — actively under-served region). Secondary: machine-readable signatures for ~200 lattices feeding the unified tensor (per feedback_tensor_first — the tensor is the load-bearing artefact, not any single bound improvement). Tertiary, low-probability: gap-closure flag in one of d ∈ {5, 6, 7} where three-point SDP slack is reportedly tightest. Paired with Report #194 (sphere packing) this gives the substrate its first connected discrete-geometry shard. We do **not** expect to close any open kissing-number bound; claiming otherwise would violate base-rate neglect — zero open kissing bounds have been closed by automated search in the last decade.

Word count ≈ 770
