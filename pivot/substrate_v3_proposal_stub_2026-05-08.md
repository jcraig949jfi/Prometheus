# Substrate v3 Proposal — STUB (Tensor-Catalog-Driven 5-Tier Extension)

**Date:** 2026-05-08
**Version:** v3.0-stub (substrate-tester pre-design data dump)
**Author:** substrate-tester (Charon-aligned)
**Audience:** Techne (substrate owner, picks up the contract change), Aporia (strategic-coordination decision-maker), James (project lead)
**Purpose:** Structured catch-up doc capturing the 5-tier substrate-extension proposal that emerged from substrate-tester fires #38-#45 (the HARD-6 + HARD POSTURE matrix-filling exercise on the canonical 104-entry tensor catalog at `aporia/mathematics/tensor_open_problems_v1.md`).

**Status:** STUB. Not a full design. Fleshing out is Techne's job (per HARD-3 + the natural ownership division — substrate-tester surfaces gaps; Techne owns the substrate). Aporia decides scope and sequencing. This doc captures findings + proposes structure to accelerate that work.

**Parent document:** `pivot/substrate_v2_proposal_2026-05-05.md`. v2 added 8 primitives + pre-tier work (CoordinateChart, MethodSpec, IndependenceClass, TriangulationProtocol, ExclusionCertificate, KillVector extensions, REWRITE/EQUIV opcodes, etc.). v3 builds on v2; it does not replace.

---

## 0. Provenance — fires #38-#45

| Fire | Catalog | § | Paradigm | Primary Finding |
|---|---|---|---|---|
| #38 | #4 M⟨3⟩ rank | I | P28-P31 | TensorObject + RankDecompositionWitness + MomentPolytope (initial Tier A + B + C) |
| #39 | #84 TN contraction | X | P30 | TensorNetworkGraph + ContractionOrderWitness + RewriteSearchTree (Tier A + B + C extended) |
| #40 | #58 tensor iso | VII | P30+P31 | GroupAction + IsomorphismCertificate + OrbitStratification (Tier A + B + C extended) |
| #41 | #34 σ_r membership | IV | P29+P31 | SchemeObject + LimitWitness + Tier-B 4-fire confirmation |
| #42 | #66 Z-eigenvalue dist | VIII | P28-distributional | DIVERGENCE: Tier B QUALIFIED + Tier D emerges (DistributionObject + StatisticalTestSpec + ProbabilityMeasure) |
| #43 | #73 PCA threshold | IX | P28-distributional | Tier D extended: PhaseTransitionThreshold + AlgorithmThresholdCert; Tier B/D composition |
| #44 | #95 Kronecker pos | XII | GCT | Tier E emerges: PartitionObject + IrreducibleRepresentation + SymmetricFunction + RepresentationTheoreticWitness |
| #45 | #40 CP identifiability | V | P29 + P28-dist | 5-tier model HOLDS; refinements only; SATURATION |

**Eight fires, eight sections, ~22 primitives, 5 tiers. Saturation reached fire #45.**

---

## 1. Executive summary

Substrate v2 ships ~14 primitives across pre-tier + 4 tiers, focused on the **falsification-substrate** core (typed kill paths, leak-resistant learner corpora, scoped exclusion certificates). Substrate v3 extends v2 with ~22 additional primitives organized into 5 TENSOR-DOMAIN tiers, surfaced by HARD-6 + HARD POSTURE matrix-filling against the canonical 104-entry tensor catalog.

The headline finding is **`ConstructiveExistenceWitness`** — a substrate-WIDE primitive (Tier B) whose absence blocks ~30+ catalog entries across §I/§III/§IV/§VII/§IX/§X. Four-fire convergence on this gap (then a divergence test in fire #42 calibrating its scope) is the strongest substrate-design recommendation v3 makes.

The 5 tiers compose cleanly: Tier A foundational tensor-algebraic objects, Tier B existential witnesses, Tier C discrete-optimization geometry, Tier D distributional / population-level primitives, Tier E representation-theoretic primitives. Plus a cross-tier composition (Tier B at fixed parameters + Tier D at parameter-scaling) that emerged in fires #43 + #45.

---

## 2. The 5-tier model

### Tier A — TensorAlgebra subsystem (foundational tensor objects)

| Primitive | Shape | Source fire |
|---|---|---|
| **TensorObject** | n-dim tensor with entry-level identity | #38 |
| **TensorNetworkGraph** | LabeledHypergraph: vertices = tensors with shapes; edges = shared indices | #39 |
| **GroupAction / GroupActionWitness** | (group_element_tuple, source_tensor, target_tensor) with composition/inverse/identity | #40 |
| **SchemeObject / IdealObject / VarietyObject** | vanishing locus of polynomial ideal; singular loci, components, embedded primes | #41 |

**Why Tier A:** Tier-B/C/D/E primitives all assume foundational tensor-algebraic objects exist as substrate types. Without TensorObject, every encoding attempt in fires #38-#45 collapsed at probe 1.

### Tier B — ConstructiveExistenceWitness (substrate-WIDE; 6 subtypes)

The asymmetric-existential pattern: substrate has `ExclusionCertificate` for negative existentials but NO companion primitive for positive existentials with constructive witness. Four-fire convergence (#38/#39/#40/#41) + qualification by fire #42 (Tier B applies to decision-problems-with-individual-witness, not population-level claims) + extension by fire #44 (representation-theoretic witnesses) + refinement by fire #45 (uniqueness annotations + structural-inequality certificates).

| Subtype | Witness shape | Source |
|---|---|---|
| **RankDecompositionWitness** | sum of outer products + rank annotation + uniqueness flag | #38, refined #45 |
| **ContractionOrderWitness** | permutation/binary-tree + cost annotation | #39 |
| **IsomorphismCertificate** | group-element tuple (A_1, ..., A_k) | #40 |
| **LimitWitness / BorderRankWitness** | parametric family T(ε) + limit semantics | #41 |
| **RepresentationTheoreticWitness** | Young tableaux / pictographs / plethysm coefficients | #44 |
| **structural_inequality_certificate** | Kruskal-bound-style: predicate + verifier + sufficient-condition annotation | #45 |

**ConstructiveExistenceWitness** is the parent type providing shared substrate hooks (cert registry, replay info, scope, content-addressing). Subtypes specialize the witness payload.

### Tier C — Discrete-optimization geometry

| Primitive | Purpose | Source |
|---|---|---|
| **MomentPolytope / SecantVarietyEquation** | algebraic-geometric tensor object; defining equations of secant varieties | #38 |
| **RewriteSearchTree / RewriteCostFunctional** | optimization over rewrite-move sequences; complement to REWRITE single-move | #39 |
| **OrbitStratification / FundamentalDomain** | orbit space of group action; canonical-form reasoning | #40 |

**Overlap with 5-of-5 capability-gap cluster:** Tier C primitives overlap with the pre-existing Structured-Equivalence-Class meta-primitive (homotopy / designs / HOMFLY / A∞ / group rep). Co-design recommended.

### Tier D — Distributional / population-level (5 primitives + 1 specialization)

| Primitive | Shape | Source |
|---|---|---|
| **DistributionObject / EmpiricalCDF / RandomTensorEnsemble** | probability distribution over tensor space | #42, confirmed #43 |
| **StatisticalTestSpec** | statistical test with null distribution + sample-size + p-value contracts | #42 |
| **ProbabilityMeasure / RandomVariable** | measure-theoretic primitive | #42 |
| ↳ GenericityAlmostEverywhereCert | full-measure subset + measure-zero exception annotation | #45 (specialization) |
| **PhaseTransitionThreshold** | (parameter_axis, threshold_value, regime_below, regime_above, semantic_class) | #43 |
| **AlgorithmThresholdCert / AsymptoticSuccessGuarantee** | (method_spec, threshold, success_prob, sample_size_required) | #43 |

### Tier E — Representation-theoretic (3 primitives)

| Primitive | Shape | Source |
|---|---|---|
| **PartitionObject / YoungLatticePoint** | partitions of n + transpose, dominance, branching rule | #44 |
| **IrreducibleRepresentation / RepresentationRing** | abstract irreducibles + branching/induction/restriction + character table | #44 |
| **SymmetricFunction / Plethysm / SchurFunctor** | symmetric-function ring + plethysm + Hall inner product + ω involution | #44 |

---

## 3. Cross-tier composition

**Tier B / Tier D composition** (fires #43 + #45):
- Tier B applies AT FIXED parameters (individual existential claim with witness)
- Tier D applies AS PARAMETERS SCALE (asymptotic / population claim)
- They compose cleanly without redundancy

**Examples:**
- Hopkins-Steurer SOS lower bound for tensor PCA: Tier-B SOS certificate at fixed (n, d, λ); the threshold λ_SOS_k(n, d) scaling with n is Tier-D PhaseTransitionThreshold.
- Generic CP identifiability: Tier-B uniqueness witness for individual T; Tier-D GenericityAlmostEverywhereCert for the format admitting full-measure identifiability.

This composition is itself a substrate-design finding: the proposed primitives interlock cleanly across tiers without overlap.

---

## 4. Recommended contract-change scope

Substrate-tester's recommendation per ST-fire45-002 (pending Aporia confirmation):

**Option (c) — Tier B + Tier D + partial Tier A** is the optimal scope for the next contract-change window:
1. `ConstructiveExistenceWitness` parent type + 4-6 subtypes (Tier B core)
2. `DistributionObject + StatisticalTestSpec + ProbabilityMeasure + PhaseTransitionThreshold + AlgorithmThresholdCert` (Tier D core)
3. `TensorObject + GroupAction` (Tier A foundational; the rest of A can wait)
4. Cross-tier composition wiring

This unblocks ~50+ catalog entries spanning §I/§III/§IV/§V/§VII/§IX/§X. Tier C, Tier E, and remaining Tier A primitives (TensorNetworkGraph, SchemeObject) ship in subsequent windows.

**Alternatives:**
- (a) Tier B alone — strongest convergence, focused, ~3-week scope
- (b) Tier B + Tier D bundled — cross-tier composition wired in, ~6-week scope
- (c) Tier B + Tier D + partial Tier A — recommended, ~10-week scope
- (d) Full 5-tier in stages — most comprehensive, ~6-month scope

---

## 5. Test-suite design hooks (substrate-tester pre-design)

For each tier, substrate-tester proposes test-suite stubs to accelerate Techne's contract-change work. Fires #47-#48 will produce concrete stubs; this section sketches the design pattern.

### Tier B test pattern

For `ConstructiveExistenceWitness` parent type:
- **T1** registry collision (sister to ExclusionCertificate's T020)
- **T2** content-addressed witness payload (witness.payload_hash matches stored)
- **T3** subtype dispatch (witness.subtype field correctly selects verifier)
- **T4** witness verification roundtrip (verify(witness) → True; tamper(witness) → False)
- **T5** scope/replay/cert registry interaction (parallel to ExclusionCertificate hooks)
- **T6** asymmetric-existential consistency (positive witness + negative ExclusionCertificate cannot both exist for same claim)

For each subtype: subtype-specific test (e.g. RankDecompositionWitness checks sum of outer products = original tensor).

### Tier D test pattern

For `DistributionObject`:
- **T1** parametric instantiation (Gaussian ensemble, spike model, etc.)
- **T2** sample drawing reproducibility (seeded sample produces same sequence)
- **T3** PhaseTransitionThreshold interaction (threshold at scale n -> asymptotic regime annotation)
- **T4** AlgorithmThresholdCert composition (MethodSpec + threshold -> success guarantee)
- **T5** GenericityAlmostEverywhereCert measure-zero exception encoding

### Tier B/D composition test pattern

- **T1** at fixed parameters: Tier-B witness verifies; at scaled parameters: Tier-D threshold predicts
- **T2** consistency: positive Tier-B witness at fixed P implies P falls in Tier-D regime_above

---

## 6. Open design questions (for Techne / Aporia)

1. Should `ConstructiveExistenceWitness` be a formal opcode (sister to CLAIM/FALSIFY) or a primitive on top of CLAIM? Substrate-tester leans toward primitive: CLAIM is the action, witness is the structured payload.

2. Should Tier-B subtypes be a tagged-union enum or a class hierarchy? Tagged-union plays better with substrate's content-addressing discipline; class hierarchy plays better with Python ergonomics.

3. Tier-D `ProbabilityMeasure` is potentially heavy. Can it be deferred to v3.1 with a simpler `EmpiricalCDF`-only Tier-D in v3.0? Substrate-tester's identifiability probe (#45) used `ProbabilityMeasure` in the abstract; concrete substrate work might not need full measure theory immediately.

4. Tier E representation-theoretic primitives are most distant from current substrate flavor. Is Tier E a substrate primitive or an EXTERNAL adapter (delegate to Sage/Symmetrica with a thin substrate cert)? Latter may be more pragmatic for v3.

5. Cross-tier composition wiring: should it be encoded as a TYPE CONSTRAINT (e.g. `WitnessAtFixedParameters[T] | DistributionalThreshold[T]`) or as DOCUMENTATION (informal pattern)? Type-constraint route may be heavy for the first ship.

---

## 7. Catalog coverage estimate

Per substrate-tester encoding attempts across fires #38-#45:

| Section | Covered by 5-tier model? | Notes |
|---|---|---|
| I. Foundations: Rank, Border Rank | YES | Tier A + B; #4 + #5 + #6 + #18-21 unblocked |
| II. The Rank Zoo | LIKELY | not pulled directly; alternative ranks fit Tier B subtypes |
| III. Symmetric Tensors / Waring | LIKELY | not pulled directly; Tier B + E fit |
| IV. Algebraic Geometry: Secant, Schemes, Apolarity | YES | Tier A (SchemeObject) + B (LimitWitness); #26-35 |
| V. Generic Rank, Identifiability | YES | Tier B + D composition; #36-42 |
| VI. Numerical Tensor Decomposition | LIKELY | not pulled; Tier B + D composition + Tier C |
| VII. Decidability and Complexity | YES | Tier B (Isomorphism) + GroupAction; #55-62 |
| VIII. Spectral and Eigenvalue | PARTIAL | #66 covered by Tier D; #63-65 + #67-70 likely Tier B/D |
| IX. Random Tensors | YES | Tier D core + Tier B/D composition; #71-74 |
| X. Quantum Information / TN | YES | Tier A (TensorNetworkGraph) + B + C; #75-84 |
| XI. Specific Tensor Families | LIKELY | not pulled; Tier A objects, individual entries Tier B |
| XII. GCT and Representation Theory | YES | Tier E + B (RepresentationTheoreticWitness); #92-99 |

Estimated coverage of 104-entry catalog: ~85-95% encodable once Tier A/B/C/D/E ship. Remaining entries likely surface design refinements rather than new tiers.

---

## 8. Open tickets in coordination chain

Sequential coordination chain across the eight matrix-filling fires:

- `T-2026-05-08-ST-fire38-001` through `ST-fire45-001` — Techne capability-gap chain (8 tickets, mostly P1-high; #45 dropped to P2 reflecting saturation)
- `T-2026-05-08-ST-fire41-002` — Aporia strategic root: ConstructiveExistenceWitness flagged
- `T-2026-05-08-ST-fire42-002` — Aporia supplement: Tier B QUALIFIED + Tier D added
- `T-2026-05-08-ST-fire43-002` — Aporia supplement: Tier D extended; Tier B/D composition
- `T-2026-05-08-ST-fire44-002` — Aporia supplement: Tier E + saturation question raised
- `T-2026-05-08-ST-fire45-002` — Aporia supplement: SATURATION + pivot proposal
- `T-2026-05-08-ST-fire42-003` — P3 infra: bare-pytest sys.path issue (workaround documented)
- `T-2026-05-08-T038` — Techne classification of all 104 entries; should now use 5-tier model
- `T-2026-05-08-E009` — Ergon probe-shape audit for v1.0 corpus

---

## 9. HARD-6 + HARD POSTURE alignment

Per HARD-6 doctrine: *"attack the problems of the tools we will need most in the future. The failures will guide us."*

The eight-fire matrix-filling exercise is exactly this discipline:
- Pulled deliberately from canonical catalog (HARD POSTURE 2026-05-08)
- Treated each encoding failure as substrate-design data (HARD-6)
- Diversified across §I/§IV/§V/§VII/§VIII/§IX/§X/§XII
- Ran a deliberate divergence test (#42) to qualify a substrate-wide claim
- Reached saturation (#45) — diminishing returns from continuing matrix-filling
- Now pivoting to test-suite design (fires #46-#48)
- Will return to matrix-filling (fires #49+) for unpulled sections at lower frequency

Substrate-tester role under HARD-6 produced **substrate-extension scope** as the failure-mode-as-output. v3 stub doc is the deliverable.

---

## 10. Next steps

**Fire #46 (this fire):** this stub doc filed.

**Fire #47:** test-suite stub for `ConstructiveExistenceWitness` (Tier B core). Concrete Python skeleton with T1-T6 tests as designed in §5.

**Fire #48:** test-suite stub for `DistributionObject + PhaseTransitionThreshold` (Tier D core). Concrete Python skeleton.

**Fire #49+:** return to matrix-filling on §II Rank Zoo / §III Waring / §VI Numerical Decomposition / §XI Specific Tensor Families. Lower frequency (every 2-3 fires) since saturation is reached. Use bandwidth for substrate-tester maintenance: regression smoke, mutation-testing, frozen-invariance audits.

**Aporia decision:** still pending on ST-fire45-002. Default if no override: continue with fires #47-#48 plan above.

**Techne pickup:** this stub doc + the 8 capability-gap tickets in techne_inbox.jsonl are the contract-change-window starting material. Techne should classify the 104 entries against the 5-tier model (T-2026-05-08-T038) and surface any tier-attribution disputes.
