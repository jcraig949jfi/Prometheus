# Layer 1 — Primitives (nouns)

Primitives are the **structured mathematical objects** that substrate agents produce, register, serialize across handoffs, and submit to substrate-tester probes. Each primitive has a tier, a parent class, an explicit sub-type list, and a declaration of which other tiers it can legally compose with (see `composition_rules.md` for the grammar). The 5-tier hierarchy in v0.1.0 is: **Tier A++** (TensorNetwork-level), **Tier B** (ConstructiveExistenceWitness), **Tier C** (SecantVarietyEquation), **Tier D** (distributional certificate), **Tier E** (RepresentationTheoreticInvariant), plus **outside-tier** entries that do not yet fit cleanly. Each entry below cites the T#XX report(s) and synthesis section(s) that seeded it.

---

## Tier A++ — TensorNetwork-level

### `TensorNetwork`

- **Tier:** A++ (foundational)
- **Parent:** none (root primitive at A++)
- **Sub-types:** `MPS`, `MPO`, `PEPS`, `MERA`, `ContractionTree`, `LineGraph`. Sub-type list is non-exhaustive in v0.1.0; future batches will expand.
- **Composition eligibility:** consumed by virtually all Tier-B, Tier-C, Tier-D primitives that operate on tensors-as-networks rather than tensors-as-monolithic-arrays. Produces a substrate-canonical handle that downstream primitives reference.
- **Description:** A registered network of contracted tensor nodes with edge bond dimensions, contraction-order metadata, and topology metadata (line-graph treewidth, planarity, sparsity). THE foundational HARD-3 primitive — without it, T#84's NP-hardness result (Markov–Shi 2008) and the cotengra / opt_einsum production stack cannot be substrate-expressed at all. Recommended *first* registration in any contract-change window.
- **Source:** T#84 (`report_T84_optimal_contraction.md`); synthesis §3.1, §8 Wave 1.

### `ContractionOrderWitness`

- **Tier:** A++
- **Parent:** none (sibling to `TensorNetwork`)
- **Sub-types:** `OptimalCotengraOrder`, `LineGraphTreewidthCert`, `NetconOrder`. Three sub-tactics from T#84.
- **Composition eligibility:** consumes a `TensorNetwork`; produces a complexity-of-evaluation annotation usable by downstream Tier-D distributional bounds.
- **Description:** Records a chosen contraction order plus a certificate (treewidth-style or empirical-cost-style) of its near-optimality. The decision problem is NP-hard (Markov–Shi 2008); witnesses are heuristic-with-bounds, not exact. Substrate must encode the heuristic-vs-exact distinction in `certificate_grade`.
- **Source:** T#84; synthesis §3.1, §5 P30 sub-tactics.

### `RankZooSignature`

- **Tier:** A++
- **Parent:** none (tracking primitive on tensor nodes)
- **Sub-types:** none in v0.1.0; the signature *itself* is the primitive. May acquire sub-types in v0.2.0 as new ranks register.
- **Composition eligibility:** retrofitted onto any tensor node; consumed by all Tier-B rank-witness primitives for cross-coordinate consistency checking.
- **Description:** Tracks all distinct rank coordinates `(R, R̄, sr, cr, cr̄, R_partition, R_analytic, R_geometric, R_strength, R_slice, ...)` as a single named tuple per tensor. Each coordinate has its own `optional<Integer>` slot plus a `closure_status` annotation. Lampert–Moshkovitz Sept 2025 separation of partition-rank from analytic-rank validated the need; Buczyńska–Buczyński Jan 2026 added border cactus rank `cr̄` as a fifth invariant. **Charts that collapse these coordinates into a single "rank" field violate HARD-5 and trigger `PATTERN_RANK_PARITY_LEAK`.**
- **Source:** T#13 (`report_T13_slice_vs_analytic.md`), T#19 (`report_T19_cactus_rank.md`); synthesis §3.1, §3.2.

---

## Tier B — ConstructiveExistenceWitness

The Tier-B cluster is the densest in the seed batch. It absorbs the rank / decomposition / complexity / orbit-closure witnesses that an attack produces as concrete certificate output.

### `TensorRankWitness`

- **Tier:** B (parent class — sibling to `BorderRankWitness`)
- **Parent:** `ConstructiveExistenceWitness` (abstract Tier-B root)
- **Sub-types:** v0.1.1 leaves the sub-type tree shallow on purpose. The first registered sub-types are expected to be `DirectSumAdditivitySafeZoneWitness` (the AA-013 / Rupniewski 2024 safe-zone certificate for `R ≤ 7` over `ℂ`) and `ExactRankCertificate` (witness that a specific decomposition achieves `R(T) = r` rather than just upper-bounding `R̄(T)`). Both register through the Techne v4.0 Wave 2 contract-change window.
- **Composition eligibility:** Tier-B × Tier-D (pairs naturally with `GenericityAlmostEverywhereCert` for "almost every tensor has rank `r`" statements over given fields); Tier-B × Tier-E via `RankZooSignature` (HARD-5: must register `R` slot distinctly from `R̄` slot in the signature tuple).
- **Description:** Witness that a tensor `T` has **ordinary tensor rank** `R(T) = r` (or `≤ r` / `≥ r` per certificate grade). Distinct from `BorderRankWitness` by definitional locus: `TensorRankWitness` certifies membership in the rank-`r` locus itself (the constructible set of tensors decomposable as a sum of `r` rank-1 terms), whereas `BorderRankWitness` certifies membership in the Zariski / topological **closure** of that locus. **Do not substitute one for the other unless an explicit theorem or reduction bridges `R` and `R̄` in the scoped setting** — strict separations are pervasive (Schönhage 1981 border-rank additivity failure; the entire matmul-exponent literature; Lampert–Moshkovitz 2025 partition-rank vs analytic-rank separation).
- **Empirical motivation (load-bearing):** AA-013 in `anti_anchors.md` records the HARD-5 routing-correction caught by Aporia's 2026-05-13 Gemini Deep Research pilot (DR-001, Rupniewski 2024 LAA Vol 698, DOI 10.1016/j.laa.2024.06.016). Strassen's direct-sum additivity strictly holds for **exact tensor rank `R` over `ℂ` when both tensors satisfy `R ≤ 7`** — NOT for border rank `R̄`, where additivity fails earlier per Schönhage 1981. The first version of AA-013's prompt-author routing destination named `BorderRankWitness` as the consumer; a primary-source check on Rupniewski 2024 surfaced that the result is about `R`, not `R̄`. The catch happened at a routing-decision layer one above code or citation (see `feedback_generic_to_specific_audit.md` four-layer audit pattern).
- **Consumer hook (substrate-tester / Learner-Tester):** the routing correction is durable only if it can be exercised as a fixture. The named fixtures are:
  - **Substrate-tester probe:** `prometheus_math/tests/substrate_tester/test_aa_013_tensor_rank_vs_border_rank_separation.py` — given a Tier-B witness annotated `cert_type=DirectSumAdditivitySafeZoneWitness`, refuses to register the witness if `rank_invariant ∈ {border_rank, R_bar}` and accepts only if `rank_invariant == ordinary_rank`. Sentinel-violation on a substitution attempt fires `PATTERN_RANK_PARITY_LEAK` (see `attacks.md`).
  - **Learner-Tester routing smoke test:** `ergon/learner/fixtures/smoke_tests/aa_013_tensor_rank_routing.json` — given a corpus input matching the AA-013 true_form, the Learner's witness-routing head must select `TensorRankWitness`, NOT `BorderRankWitness`. Required to pass before any LoRA / supervised-routing checkpoint can claim AA-013 coverage.
- **Source:** AA-013 (this file's sibling registry); Rupniewski 2024 LAA Vol 698 (DOI 10.1016/j.laa.2024.06.016); first announced arXiv:2209.11040. Substrate-shaped pipeline pilot 2026-05-13.

### `BorderRankWitness`

- **Tier:** B (parent class — sibling to `TensorRankWitness`)
- **Parent:** `ConstructiveExistenceWitness` (abstract Tier-B root)
- **Sub-types:** `DecompositionCertificate`, `DegenerationWitness`, `LimitWitness`, `CactusRankWitness`, `WaringRankWitness`, `BorderCactusWitness`. (Plus the cross-cutting sub-primitives `DualityCheck`, `PrecisionFloorCertificate`, `ReshapingCertificate`, `MeasureZeroExceptionAnnotation` listed below.)
- **Composition eligibility:** Tier-B × Tier-D (confirmed twice — see `composition_rules.md`); Tier-B × Tier-E (confirmed via T#92 `GCTObstructionCertificate`).
- **Description:** Witness that a tensor `T` lies in (or outside) the **Zariski / topological closure** of the rank-`r` locus inside the ambient tensor space — i.e. certifies a statement about border rank `R̄(T)`, not ordinary rank `R(T)`. Encodes the witness type, the certificate-grade (exact / numerical-certified / numerical-heuristic), the duality-check status, and the precision floor. Parent for the entire border-rank cluster. **Sibling to `TensorRankWitness`; the two are NOT interchangeable** (border-rank additivity fails earlier per Schönhage 1981, and the closure-vs-locus distinction is foundational — see AA-013 and the sibling primitive's empirical-motivation block).
- **Source:** T#34 (`report_T34_borderrank_membership.md`); synthesis §3.2.

### `LimitWitness`

- **Tier:** B (sub-type of `BorderRankWitness`)
- **Parent:** `BorderRankWitness`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** stand-alone (no degeneration sequence required); composes with Tier-D `GenericityAlmostEverywhereCert` for ill-posedness regimes.
- **Description:** Witnesses de Silva–Lim 2008 ill-posedness — the "best rank-r approximation does not exist" phenomenon. Distinct from `DegenerationWitness` because it does not require an explicit degeneration sequence; the failure of a minimum to be attained is itself the witness.
- **Source:** T#43 (`report_T43_best_rank_r_existence.md`); synthesis §3.2.

### `ComputationalComplexityCertificate`

- **Tier:** B (sub-type of `BorderRankWitness`; cross-cutting)
- **Parent:** `BorderRankWitness` (sub-type by tagging existence claim with complexity class)
- **Sub-types:** `NPHardClass`, `ExistsRHardClass`, `UndecidableClass`. (`∃ℝ` is the canonical class for border-rank decision per T#34.)
- **Composition eligibility:** annotates any Tier-B existence claim; composes with `GCTObstructionCertificate` to gate construction at PH-hardness regimes.
- **Description:** Tags an existence claim with its complexity-of-construction class (NP-hard / `∃ℝ`-hard / undecidable / etc). Critical because two witnesses of the *same* mathematical statement can have radically different construction complexity (e.g. tensor rank decision is NP-hard; border-rank decision is `∃ℝ`-hard; symmetric-rank-over-`ℚ` decision was settled NP-hard by Shitov 2016 — supersedes the catalog "open" claim).
- **Source:** T#56 (`report_T56_symmetric_rank_nphard.md`); synthesis §3.2.

### `CactusRankWitness`

- **Tier:** B (sub-type of `BorderRankWitness`)
- **Parent:** `BorderRankWitness`
- **Sub-types:** `BorderCactusWitness` (sub-sub-type, Buczyńska–Buczyński Jan 2026).
- **Composition eligibility:** composes with `RankZooSignature` for full-coordinate registration; pairs with a separate `BorderRankWitness` to certify strict gap `cr < R̄`.
- **Description:** Witness for cactus rank `cr(T)` via an explicit saturated 0-dim Gorenstein apolar scheme. Strictly *easier* to construct than a full `BorderRankWitness` (purely combinatorial — no degeneration sequence, no NP-hardness reduction). Strictly *less informative* (lower bound on `R̄`, not exact decision). Underlies the **cactus barrier** `6m − 4` on determinantal lower bounds for `R̄(M⟨m⟩)` (Buczyński Feb 2026, arXiv:2602.11309) — see `anti_anchors.md` entry 5. Recommended **pilot** for the Tier-B contract-change window.
- **Source:** T#19 (`report_T19_cactus_rank.md`); synthesis §3.2, §8 Wave 1.

### `BorderCactusWitness`

- **Tier:** B (sub-sub-type of `CactusRankWitness`)
- **Parent:** `CactusRankWitness`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** as `CactusRankWitness`; additionally requires Cox-ring multihomogeneous-ideal infrastructure on toric ambients.
- **Description:** Border-apolarity extension to cactus varieties via Cox-ring multihomogeneous ideals (Buczyńska–Buczyński Jan 2026, arXiv:2601.19558). Border cactus rank `cr̄` is the **fifth distinct rank invariant** alongside `R, R̄, sr, cr` — never collapse (HARD-5 / anti-anchor 9).
- **Source:** T#19; synthesis §3.2.

### `WaringRankWitness`

- **Tier:** B (sub-type of `BorderRankWitness`)
- **Parent:** `BorderRankWitness`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** consumes `DefectivityCertificate.fat_point_witness` (Tier-C, T#26); shares Lie-theoretic infrastructure with `GCTObstructionCertificate`.
- **Description:** Symmetric specialization of `BorderRankWitness` for Waring rank of symmetric tensors / forms. T#22 has the only known exact value `R_W(perm_3) = 16` (Shitov 2021); `n ≥ 4` is OPEN. **det/perm tooling-asymmetry is itself substrate signal** (synthesis §1): permanent-side literature is markedly thinner than determinant-side, which is a HARD-3 / HARD-6 surface.
- **Source:** T#22 (`report_T22_waring_permanent.md`); synthesis §3.2.

### `OrbitClosureNonMembershipWitness`

- **Tier:** B
- **Parent:** `ConstructiveExistenceWitness`
- **Sub-types:** consumed as base of `GCTObstructionCertificate` composite.
- **Composition eligibility:** Tier-B × Tier-E mandatory (composite).
- **Description:** Witness that a polynomial `p` does NOT lie in the orbit-closure `\overline{G \cdot q}` of another polynomial `q` under a group action `G`. Geometric content of GCT-style separations. Distinct from `BorderRankWitness` (which is membership in a *secant* variety, not orbit-closure of a single polynomial).
- **Source:** T#92 (`report_T92_gct_vp_vs_vnp.md`); synthesis §3.2.

### `GCTObstructionCertificate`

- **Tier:** B + E composite (mandatory composite)
- **Parent:** `OrbitClosureNonMembershipWitness` (Tier-B base) + `RepresentationTheoreticInvariant` (Tier-E upstream)
- **Sub-types:** `OccurrenceObstruction` (**KILLED** by BIP 2019 — see `anti_anchors.md` entry 1), `MultiplicityObstruction`, `VanishingIdealObstruction`, `OutsideOrbitObstruction`, `EquivariantObstruction` (restricted-model only).
- **Composition eligibility:** REQUIRES upstream `RepresentationTheoreticInvariant` (Tier-E from T#95). Substrate-tester refuses to load a `GCTObstructionCertificate` ticket without an upstream T#95 registration. Highest-leverage cross-tier coupling in the seed batch.
- **Description:** Composite certificate for GCT-style obstructions. Five sub-types, each tagged with which complexity coordinate (`dc / \underline{dc} / L / B / dc_{equiv}`) it separates. Substrate must reject any agent attempt to construct an `OccurrenceObstruction` for `(det_m, padded_perm_{n,m}, m=poly(n))` as a sentinel-violation.
- **Source:** T#92; synthesis §3.2, §3.7.

### `BorderComplexitySeparator`

- **Tier:** B
- **Parent:** `ConstructiveExistenceWitness`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** sibling to `BorderRankWitness`; explicit HARD-5 separator from T#34's primitive.
- **Description:** Operates on `\underline{dc}` (border determinantal complexity) rather than `\underline{R}` (border tensor rank). Same homotopy-limit machinery as `BorderRankWitness`; distinct semantics. Collapsing the two violates HARD-5 / fires `PATTERN_RANK_PARITY_LEAK`.
- **Source:** T#92; synthesis §3.2.

### `EquivariantComplexityCertificate`

- **Tier:** B (restricted-model)
- **Parent:** `ComputationalComplexityCertificate`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** carries mandatory `restricted_to: SymmetryGroup` annotation; substrate WARNs on any unrestricted-extrapolation use.
- **Description:** Lower-bound certificate that holds only under a specified symmetry restriction (e.g. Landsberg–Ressayre 2017's exponential lower bound on `dc(perm)` under `(S_n × S_n) ⋉ (D_n × D_n)` equivariance). The restriction is severe; the analogous unrestricted statement is open. Anti-anchor 8 in `anti_anchors.md` pins this distinction.
- **Source:** T#92 (Landsberg–Ressayre 2017); synthesis §3.2, §4 entry 8.

### `DualityCheck`

- **Tier:** B (cross-cutting sub-primitive)
- **Parent:** none (annotation on Tier-B witnesses)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** annotates any `BorderRankWitness` family.
- **Description:** Verifies that the dual / transposed / re-shaped variant of a tensor produces a consistent rank witness. Cross-cutting because rank invariants must respect tensor-symmetry transforms.
- **Source:** T#34; synthesis §3.2.

### `PrecisionFloorCertificate`

- **Tier:** B (cross-cutting)
- **Parent:** none (annotation on numerical witnesses)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** mandatory annotation on any `certificate_grade ∈ {NUMERICAL_CERTIFIED, NUMERICAL_HEURISTIC}` witness.
- **Description:** Records the numerical precision regime under which a witness was constructed. Without this, numerical false-NEGATIVES from precision exhaustion are indistinguishable from genuine non-existence.
- **Source:** T#34; synthesis §3.2.

### `ReshapingCertificate`

- **Tier:** B (cross-cutting)
- **Parent:** none (annotation on Tier-B witnesses)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** annotates AOP / CO-V identifiability claims.
- **Description:** Documents the specific tensor-reshaping (mode-merge, partial-flatten, etc) used to produce an identifiability witness. AOP / CO-V identifiability holds with explicit exception list `(6,2,9), (4,3,8), (3,5,9)`; reshaping discipline is required to track which exceptions apply.
- **Source:** T#40 (`report_T40_cp_identifiability.md`); synthesis §3.2.

### `MeasureZeroExceptionAnnotation`

- **Tier:** B (cross-cutting)
- **Parent:** none (annotation on Tier-B + Tier-D composite witnesses)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** REQUIRED on any Tier-B witness paired with Tier-D `GenericityAlmostEverywhereCert` to call out finite explicit exception lists.
- **Description:** Records the measure-zero exception set explicitly when a generic-identifiability claim is paired with explicit known exceptions (e.g. AOP / CO-V `(6,2,9), (4,3,8), (3,5,9)`). The composition `GenericityAlmostEverywhereCert + MeasureZeroExceptionAnnotation` is one of the two confirmed cross-tier composition patterns (T#40 fire #45).
- **Source:** T#40; synthesis §3.2, §3.7.

---

## Tier C — SecantVarietyEquation

### `DefectivityCertificate`

- **Tier:** C
- **Parent:** `SecantVarietyEquation`
- **Sub-types:** `SegreVeroneseDefectivity` (closed for `d_i ≥ 3`, ABGO 2024).
- **Composition eligibility:** `fat_point_witness` consumed by `WaringRankWitness`.
- **Description:** Certifies defectivity (or non-defectivity) of a secant variety — i.e. whether the dimension drops below the expected secant-dimension count. ABGO 2024 (arXiv:2406.20057) closed the Segre–Veronese classification for `d_i ≥ 3`. The defective stratum is precisely where rank-zoo gaps live (`PATTERN_BASE_RATE_NEGLECT` fires on generic-stratum spot-checks).
- **Source:** T#26 (`report_T26_defective_segre_veronese.md`); synthesis §3.3.

### `MomentPolytope`

- **Tier:** C (companion)
- **Parent:** `SecantVarietyEquation` (companion structure)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** companion to `DefectivityCertificate`; supplies symplectic-geometric data for stratification.
- **Description:** Records the moment polytope of a tensor / form under a torus action. Companion structure to defectivity certification; supplies polytope-combinatorial data that downstream attacks (e.g. P22 plethystic) consume.
- **Source:** T#26; synthesis §3.3.

---

## Tier D — Distributional certificate

### `PhaseTransitionThreshold`

- **Tier:** D
- **Parent:** none (Tier-D root)
- **Sub-types:** none in v0.1.0; usually appears as triple with `AlgorithmThresholdCert` + `GenericityAlmostEverywhereCert`.
- **Composition eligibility:** Tier-B × Tier-D mandatory pairing (substrate-tester fire #43; T#73).
- **Description:** Records a sharp threshold (typically signal-to-noise ratio) at which a recovery / decoding / decomposition problem transitions from infeasible to feasible. Tensor-PCA threshold (T#73) is the canonical seed.
- **Source:** T#73 (`report_T73_tensor_pca_threshold.md`); synthesis §3.4.

### `AlgorithmThresholdCert`

- **Tier:** D
- **Parent:** none
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** sibling to `PhaseTransitionThreshold`; pairs with a specific algorithm to certify it achieves the threshold.
- **Description:** Certifies that a *specific* algorithm achieves (or fails to achieve) a phase-transition threshold. Distinct from the threshold itself, which is statistical / information-theoretic.
- **Source:** T#73; synthesis §3.4.

### `GenericityAlmostEverywhereCert`

- **Tier:** D
- **Parent:** none
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** Tier-B × Tier-D mandatory pairing (substrate-tester fire #45; T#40). REQUIRES `MeasureZeroExceptionAnnotation` when paired with explicit exception lists.
- **Description:** Certifies that a property holds on a Zariski-open / measure-1 / generic stratum, leaving a measure-zero exception set. Without paired Tier-B witnesses for the explicit exception cases, generic claims silently elide the boundary phenomena where the substrate's interesting math actually lives.
- **Source:** T#73, T#40; synthesis §3.4, §3.7.

### `RandomTensorConcentrationCert`

- **Tier:** D
- **Parent:** none (sister to T#73 triple)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** stand-alone Tier-D; composes with `BorderRankWitness` for distributional border-rank statements.
- **Description:** Records `(order_r, dim_d, p_norm, n_summands, upper_bound_exponent, upper_bound_polylog, lower_bound_exponent, regime ∈ {matrix_r2, p_geq_2r, p_lt_2r, p_eq_infty}, status, source_anchor, proposer, technique, MC estimate fields)`. BGJLR STOC 2025 resolved Lucca's Conjecture 16 for `p ≥ 2r`; `p < 2r` open behind a *volumetric barrier* (P25 sub-tactic). Tensor type-2 constant is `d^{1/2−1/p}` polylog, NOT the matrix `√log d` (anti-anchor 7).
- **Source:** T#72 (`report_T72_type2_constant.md`); synthesis §3.4.

### `AlgebraicNaturalProofsBarrier`

- **Tier:** D (meta-warning)
- **Parent:** none
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** fires on candidate `GCTObstructionCertificate` constructions to apply the Forbes–Shpilka–Volk barrier check.
- **Description:** Tier-D meta-warning that fires when a candidate obstruction is itself a circuit-lower-bound. Forbes–Shpilka–Volk + Grochow–Kumar–Saks–Saraf 2017 give first evidence of an algebraic natural-proofs barrier (succinct hitting sets imply equations-of-circuit-classes lower bounds). Complicates GCT obstruction-construction.
- **Source:** T#92; synthesis §3.4.

---

## Tier E — RepresentationTheoreticInvariant

### `RepresentationTheoreticInvariant`

- **Tier:** E (parent class)
- **Parent:** none (Tier-E root, shared between T#92 and T#95)
- **Sub-types:** `KroneckerInvariant`, `PartitionObject`, `Structured-Equivalence-Class`. Plus number-field-provenance variants `RayClassFieldFiducial` and `StarkUnitWitness` from T#85.
- **Composition eligibility:** prerequisite for `GCTObstructionCertificate` (Tier-B × Tier-E mandatory composite).
- **Description:** Parent class for all representation-theoretic invariants the substrate manipulates: Schur functions, Kronecker coefficients, plethysm coefficients, character data. Saxl conjecture (T#99) **remains OPEN** as of 2026-05-11 — anti-anchor AA-004 pins the forward-false-anchor risk that LLM training data may memorize the withdrawn Lee 2025 arXiv:2512.15035 abstract as proof. Luo-Sellke 2017 proved only the fourth-power relaxation; 2022 follow-on tightened to the cube. (Updated 2026-05-11 per Wave 1 anti-anchor verification.)
- **Source:** T#95 (`report_T95_kronecker_positivity.md`); synthesis §3.5.

### `KroneckerInvariant`

- **Tier:** E (sub-type)
- **Parent:** `RepresentationTheoreticInvariant`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** consumed by `GCTObstructionCertificate.MultiplicityObstruction`.
- **Description:** Specific Kronecker-coefficient data and positivity certificates. Kronecker positivity is NP-hard (Ikenmeyer–Mulmuley–Walter 2017 — falsified Mulmuley's PH1 conjecture); Ikenmeyer–Pak–Panova 2024 IMRN gives PH-hardness for `S_n`-character positivity.
- **Source:** T#95; synthesis §3.5.

### `PartitionObject`

- **Tier:** E (sub-type)
- **Parent:** `RepresentationTheoreticInvariant`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** consumed by `KroneckerInvariant` and `GCTObstructionCertificate`.
- **Description:** Partition / Young-diagram object with all standard combinatorial annotations (staircase indicator, hook-length data, etc). The Lee 2025 staircase-minimality argument (withdrawn 3 days after posting) was intended as a `PartitionObject`-centric proof of Saxl's conjecture; the technique itself remains an interesting `PartitionObject` operation but has no known successful application. (Updated 2026-05-11 per Wave 1 anti-anchor verification.)
- **Source:** T#95; synthesis §3.5.

### `Structured-Equivalence-Class`

- **Tier:** E (meta-primitive)
- **Parent:** `RepresentationTheoreticInvariant`
- **Sub-types:** unifies `OrbitWitness` + `HomotopyWitness` + `ArityGradedOperationFamily` (three legacy primitives folded into one meta-class).
- **Composition eligibility:** root of the SLOCC entanglement-class machinery; composes with `GCTObstructionCertificate.OutsideOrbitObstruction`.
- **Description:** Meta-primitive unifying orbit, homotopy, and arity-graded-operation-family witnesses for SLOCC entanglement classification. Backed by 2025 AME-at-`n=5` result (T#79). Reflects deeper architecture: equivalence-class structure is one thing, the tier just enumerates its facets.
- **Source:** T#79 (`report_T79_slocc_entanglement.md`); synthesis §3.5.

---

## Outside the 5-tier model

These primitives surfaced cleanly from the seed batch but do not yet fit any of the five tiers. They are documented here to avoid forcing a bad fit; v0.2.0 may grow a sixth tier or absorb them into existing tiers.

### `AsymptoticSpectrumMonotone`

- **Tier:** outside-tier (candidate "Tier-F" or extension of A++)
- **Parent:** none
- **Sub-types:** Strassen monoid elements: `tensor_rank`, `slice_rank`, `support_functional`, `quantum_functional`. CHNVZ 2024 polynomial characterization adds new spectrum elements.
- **Composition eligibility:** used by attacks on `ω` (T#1) and asymptotic spectrum machinery generally.
- **Description:** Spectrum element of Strassen's asymptotic spectrum of tensors. Each element is a `≤_∼`-monotone map from tensors to non-negative reals. CHNVZ 2024 (arXiv:2411.15789) gives the first polynomial characterization of spectrum elements — a paradigm event.
- **Source:** T#1 (`report_T1_matrix_multiplication_exponent.md`), T#28 (`report_T28_asymptotic_spectrum.md`); synthesis §3.6.

### `RayClassFieldFiducial`

- **Tier:** outside-tier (number-field provenance; conditional anchor)
- **Parent:** `RepresentationTheoreticInvariant` (extension)
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** required by AFK 2025's conditional Zauner construction; carries mandatory `conditional_on: [stark_conjectures, shintani_faddeev_modularity]` annotation.
- **Description:** Tags a SIC-POVM construction with its underlying ray-class-field of a real-quadratic field. Conditional on Stark conjectures + Shintani–Faddeev modularity. **Anti-anchor 2:** "Zauner proved 2025" is FALSE; AFK 2025 is conditional, not unconditional.
- **Source:** T#85 (`report_T85_zauner_sicpovm.md`); synthesis §3.6, §4 entry 2.

### `StarkUnitWitness`

- **Tier:** outside-tier (number-field provenance; conditional anchor)
- **Parent:** `RayClassFieldFiducial`
- **Sub-types:** none in v0.1.0.
- **Composition eligibility:** consumed by `RayClassFieldFiducial`; required for AFK 2025 reconstruction.
- **Description:** Witness for a Stark unit in the relevant ray-class-field. Conditional on the Stark conjectures. Honest substrate-tester probes must reject any "Stark unit verified" claim that does not annotate the conditionality.
- **Source:** T#85; synthesis §3.6.

---

## TODO for future batches

Open slots flagged for amendment in subsequent contract-change windows:

- **Knot / 3-manifold tier.** `feedback_silent_islands.md` flags knots as one of the four silent islands; expected to seed a Tier-A++-equivalent for braid-word / knot-diagram primitives.
- **Number-field tier.** T#85 surfaced two number-field primitives (`RayClassFieldFiducial`, `StarkUnitWitness`) that may grow into a sixth tier as Charon and aporia push deeper into LMFDB territory.
- **Knot-PCA / random-knot distributional tier.** T#73's `RandomTensorConcentrationCert` is the first Tier-D entry; future batches will populate.
- **Sub-types of `RankZooSignature`.** Currently flat; v0.2.0 may sub-type by tensor symmetry class (general / symmetric / partially-symmetric / skew-symmetric).
- **Resolution of P32 paradigm collisions.** The P32 slot in `attacks.md` has five candidates colliding (T#1, T#56, T#85, T#92, T#95); when resolved, one new attack will register as the canonical P32, and others will get P33+ slots that may surface new primitive-bundle dependencies.
