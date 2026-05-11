# Layer 5 — Composition rules (grammar)

Composition rules are the **grammar** that gates how Layer-1 primitives legally assemble into larger artifacts. Each rule states the precondition primitives, the output primitive, the applicable Layer-2 attacks that exercise the rule, and the literature confirmation. Composition rules with **two or more independent literature confirmations** in a single batch are promoted from "speculation" to "load-bearing substrate architecture" — they become required primitive interactions, not optional. The seed batch surfaced **two confirmed compositions**, both promoted in v0.1.0. Five additional candidates are documented as future-confirmed-pending.

---

## Confirmed compositions (load-bearing, v0.1.0)

### Rule 1 — `Tier-B × Tier-D composition`

- **Status:** **CONFIRMED twice in batch**; load-bearing for any future tensor-substrate work.
- **Precondition primitives:**
  - One Tier-B `BorderRankWitness` (or sub-type — `LimitWitness`, `CactusRankWitness`, etc).
  - One Tier-D distributional certificate (`PhaseTransitionThreshold` triple, or `GenericityAlmostEverywhereCert`, or `RandomTensorConcentrationCert`).
  - When `GenericityAlmostEverywhereCert` is the Tier-D side AND explicit exception lists exist: a `MeasureZeroExceptionAnnotation` is REQUIRED.
- **Output primitive:** A composite "distributional border-rank statement" — substrate-canonical handle that downstream attacks treat as a single load-bearing artifact rather than two independent witnesses.
- **Applicable attacks:** `P29_BorderApolarity`, `P31_SecantVarietyGeometry`, `P03_ExhaustiveComputation` for AOP / CO-V identifiability work.
- **Literature confirmation (TWICE):**
  1. T#73 (substrate-tester fire #43 closure): `BorderRankWitness × PhaseTransitionThreshold` — tensor-PCA threshold composes with border-rank existence statements. Triple `PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert`.
  2. T#40 (substrate-tester fire #45 closure): `BorderRankWitness × GenericityAlmostEverywhereCert + MeasureZeroExceptionAnnotation` for AOP / CO-V identifiability with explicit exception list `(6,2,9), (4,3,8), (3,5,9)`.
- **Substrate enforcement:** substrate-tester rejects any Tier-D distributional claim that is *implicitly* about a border-rank stratum without an explicit Tier-B handle, and vice versa. The composition is mandatory at the registration layer, not optional decoration.
- **Source:** T#73, T#40; synthesis §3.7 first bullet, §6 fire #45 row.

### Rule 2 — `Tier-B × Tier-E composition`

- **Status:** **CONFIRMED** by the entire T#92 cluster; load-bearing prerequisite for any GCT-style work.
- **Precondition primitives:**
  - One Tier-B `OrbitClosureNonMembershipWitness` (or `BorderComplexitySeparator`, or `EquivariantComplexityCertificate`).
  - One Tier-E `RepresentationTheoreticInvariant` (concretely instantiated by `KroneckerInvariant`, `PartitionObject`, or `Structured-Equivalence-Class`).
- **Output primitive:** `GCTObstructionCertificate` (composite Tier-B/E mandatory).
- **Applicable attacks:** `P22_RepresentationTheoreticPlethystic`; the queued `P_CANDIDATE_MultiplicityObstructionSynthesis`.
- **Literature confirmation:** T#92 entire cluster — BIP 2019 J.AMS (occurrence-obstruction killer, requires Tier-E character data to even state the claim); Dörfler–Ikenmeyer–Panova ICALP 2019 (multiplicity > occurrence, requires Tier-E multiplicity computation); Implementing GCT STOC 2020 arXiv:1911.03990 (only known constructive obstruction route, requires Tier-E representation manipulation throughout).
- **Substrate enforcement:** substrate-tester **refuses to load** a `GCTObstructionCertificate` ticket without an upstream `RepresentationTheoreticInvariant` registration. T#95 primitive bundle (`KroneckerInvariant`, `PartitionObject`) is a hard prerequisite for any T#92 work. **This is the highest-leverage cross-tier coupling in the seed batch** (synthesis §3.7).
- **Source:** T#92; synthesis §3.7 second bullet, §3.2 `GCTObstructionCertificate`.

---

## Candidate compositions (future-confirmed-pending)

The seed batch surfaced five additional plausible compositions that received only **single-report** confirmation. They are documented here so future batches that independently confirm them can promote them to load-bearing without re-discovering the structure. Promotion criterion: a second independent batch report exhibits the same composition pattern.

### Candidate 3 — `Tier-A++ × Tier-D composition` (TensorNetwork × distributional)

- **Status:** candidate; one confirmation.
- **Precondition primitives:** `TensorNetwork` + `ContractionOrderWitness` (Tier-A++); a Tier-D distributional certificate over contraction cost (e.g. expected cost under random ordering, or worst-case treewidth-distribution bound).
- **Output primitive:** distributional contraction-cost statement; a Tier-A++ × Tier-D composite that gates downstream Tier-B work on networked tensors.
- **Applicable attacks:** `P03_ExhaustiveComputation` (cotengra / line-graph treewidth / netcon sub-tactics); P30 in the contraction-order sense.
- **Single-report confirmation:** T#84 (`report_T84_optimal_contraction.md`) cotengra / opt_einsum production stack — the distributional cost analysis is implicit in the heuristic-vs-exact certificate-grade. Promotion blocked on second independent batch confirming distributional tier explicitly registers.
- **Rationale for tracking:** without this composition, the heuristic-cost contraction-order results cannot be substrate-expressed without false-precision (i.e. reporting a heuristic cost as if it were exact).
- **Source:** T#84; synthesis §3.1, §5 P30 sub-tactics.

### Candidate 4 — `Tier-B × Tier-C composition` (BorderRank × Defectivity)

- **Status:** candidate; cross-cited but not jointly confirmed in a single fire.
- **Precondition primitives:** `BorderRankWitness` (or `WaringRankWitness` sub-type) + `DefectivityCertificate` (Tier-C, e.g. Segre–Veronese).
- **Output primitive:** "border-rank witness on the defective stratum" — pinpoints exactly which secant-defective configurations realize strict rank-zoo gaps.
- **Applicable attacks:** `P09_DimensionCounting` chained into `P29_BorderApolarity`.
- **Single-report cross-citation:** T#22 `WaringRankWitness` consumes `DefectivityCertificate.fat_point_witness` from T#26. The cross-tier reference exists in the primitive declaration but the Tier-C side has not been independently exercised by a separate fire.
- **Rationale for tracking:** the defective stratum is precisely where rank-zoo gaps live (`PATTERN_BASE_RATE_NEGLECT`); formalizing this composition would let substrate-tester probe gap-detection at the right stratum automatically.
- **Source:** T#22, T#26; synthesis §3.2 (WaringRankWitness consumption), §3.3 (DefectivityCertificate).

### Candidate 5 — `Tier-B × Tier-B composition` (cross-coordinate gap-witness)

- **Status:** candidate; pattern recurs but not promoted.
- **Precondition primitives:** Two distinct Tier-B witnesses on the **same tensor** but for **different rank coordinates** — e.g. `CactusRankWitness(F, r₁)` paired with a `BorderRankWitness(F, r₂)` where `r₁ < r₂`.
- **Output primitive:** a **strict-gap witness** — substrate-grade certification that two rank coordinates are NOT equal on `F`. Higher-leverage than either sole witness because it constructively realizes the rank-zoo separation.
- **Applicable attacks:** `P29_BorderApolarity` for the cactus side; `P31_SecantVarietyGeometry` for the border-rank side; jointly under `P25_PivotalNegativeResult` when the gap is a pivotal counterexample (e.g. wild forms).
- **Single-batch evidence:** T#19 explicitly documents the composition rule `CactusRankWitness(F, r) ∧ R̄(F) > r ⇒ STRICT GAP cr < R̄`; T#43 (de Silva–Lim wild-form witnesses) is a recurring source. Has not yet recurred in a non-cactus context — recurrence in a different rank-pair would promote.
- **Rationale for tracking:** strict-gap witnesses are the substrate's unique deliverable on rank-zoo phenomena. Without a registered composition rule, agents serialize them as two independent witnesses and the gap claim becomes implicit (`PATTERN_RANK_PARITY_LEAK` risk).
- **Source:** T#19; synthesis §3.2 composition rules section.

### Candidate 6 — `Tier-D × Tier-D composition` (triple registration)

- **Status:** candidate; one confirmation, internally a triple.
- **Precondition primitives:** Three Tier-D certificates on the same problem: `PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert` (T#73).
- **Output primitive:** complete distributional characterization of the problem — information-theoretic threshold, algorithm-achievement gap, generic-stratum coverage.
- **Applicable attacks:** Tier-D-heavy paradigms; the triple is a one-shot deliverable from a single attack rather than a chain.
- **Single-report confirmation:** T#73 tensor-PCA threshold. The triple is intrinsic to the problem class; recurrence in a non-PCA distributional setting would promote.
- **Rationale for tracking:** the triple is treated as one unit by T#73; substrate convention should make this explicit so future Tier-D work registers all three slots automatically.
- **Source:** T#73; synthesis §3.4.

### Candidate 7 — `Tier-B × Tier-D × Tier-E composition` (full GCT depth)

- **Status:** candidate; not yet a deliverable, future-promise.
- **Precondition primitives:** `BorderComplexitySeparator` (Tier-B) + `AlgebraicNaturalProofsBarrier` (Tier-D meta-warning) + `RepresentationTheoreticInvariant` (Tier-E).
- **Output primitive:** a "GCT-with-barrier-check" composite — a `GCTObstructionCertificate` that has passed the Forbes–Shpilka–Volk algebraic-natural-proofs barrier check.
- **Applicable attacks:** `P22_RepresentationTheoreticPlethystic` chained with `P25_PivotalNegativeResult`.
- **Single-report evidence:** T#92 documents all three primitives in the same cluster; the three-way composition is the *natural* shape for a future concrete obstruction. No constructive obstruction since 2020 (queued `P_CANDIDATE_MultiplicityObstructionSynthesis` is HOLD), so the composition is unexercised. Promotion blocked on a concrete obstruction being constructed.
- **Rationale for tracking:** if any future agent constructs a candidate `GCTObstructionCertificate.MultiplicityObstruction`, the substrate must auto-route it through the algebraic-natural-proofs barrier check. Pre-registering the composition rule prevents the check from being skipped.
- **Source:** T#92; synthesis §3.4 (`AlgebraicNaturalProofsBarrier`), §3.7.

---

## TODO for future batches

- **Promote candidates 3–7** as second independent confirmations arrive. Each promotion bumps MINOR.
- **Composition under model restriction.** `EquivariantComplexityCertificate` carries a mandatory `restricted_to: SymmetryGroup` annotation; composition rules involving it should special-case the restricted-model semantics so substrate doesn't auto-promote restricted bounds to unrestricted ones (anti-anchor 8). Future contract-change window should formalize this as a meta-composition-rule.
- **Composition under conditionality.** `RayClassFieldFiducial` / `StarkUnitWitness` carry `conditional_on: [stark_conjectures, shintani_faddeev_modularity]`. Conditional-composition rules need formalization analogous to model-restriction rules.
- **Cross-tier exclusion rules.** This file documents legal compositions; v0.2.0 should add explicit ILLEGAL composition entries (e.g. "an `OccurrenceObstruction` sub-type of `GCTObstructionCertificate` against the canonical regime is ILLEGAL by anti-anchor 1; substrate-tester must reject before composition rule fires").
