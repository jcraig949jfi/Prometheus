# Substrate Primitives v2 — Status & Proposed Roadmap

**Date:** 2026-05-05 (revised; see §0 for revision history)
**Version:** v2.2 (post-ChatGPT/Gemini convergent revisions + Aporia artifact batch integration)
**Author:** Techne (mathematical toolsmith + substrate owner)
**Audience:** James (project lead); Aporia, Charon, Ergon (Prometheus pillars); ChatGPT, Gemini, Claude, Grok, DeepSeek (external review)
**Purpose:** Single self-contained document describing where the substrate primitives initiative currently stands at the end of the 2026-05-01 → 2026-05-05 sprint, and proposing a concrete v2 roadmap. Written to be reviewable by readers without prior context on Project Prometheus.
**Status:** Pre-build. Two external reviews integrated (ChatGPT, Gemini). Aporia artifact batch integrated. Awaiting Charon, Ergon, Claude, Grok, DeepSeek.

---

## 0. Revision history

| Version | Date | Changes |
|---|---|---|
| v1.0 | 2026-05-05 morning | Initial proposal — six primitives (P1–P6), three tiers, 15 reviewer questions. |
| v2.1 | 2026-05-05 afternoon | ChatGPT + Gemini convergent revisions: split EvidenceField from PolicyField; added P0 CoordinateChart; renamed ExclusionZone → ExclusionCertificate; deferred bridge_proximity; added assumption_load + computational_friction axes; structured MethodSpec with independence_class; multi-view leakage-safe NearMissCorpus; tightened TriangulationProtocol independence requirements; reframed mental model. *(Drafted in conversation; not in this doc until v2.2.)* |
| v2.2 | 2026-05-05 evening | Aporia artifact batch integration (`roles/Techne/AVAILABLE_ARTIFACTS_2026-05-05.md`): Pre-Tier-0 work added (cartography handles 1+2, TRACE preservation audit); P0 CoordinateChart now uses Study 17's `CanonicalizationProtocol` interface with decidability flags; +7 KillVector components from Study 02; architectural lock-in of control-plane vs data-plane (proof primitives via BIND/EVAL only); REWRITE/EQUIV opcodes added as parallel kernel-track; intensional vs behavioural drift channel folded into MethodSpec; Charon G4/G6 coordination noted. **All v2.1 changes are reflected in v2.2.** |
| v2.3 | 2026-05-05 late | Aporia tightening pass (`roles/Techne/APORIA_FEEDBACK_2026-05-05.md`): added `triangulation_history` field to ExclusionCertificate (prevents future certificates from inheriting `complete` strength without earned triangulation); committed schema decision for KillVector +8 component overlap (option b: independent flags with explicit MI reporting in §7.1); added §13 convergence-bias check applying my own Q-C5 warning to v2.2 design (the discipline is identifying, not necessarily changing). |

---

## 1. Executive summary

The Prometheus substrate is a typed, append-only ledger that records mathematical-discovery experiments along with the falsification probes that killed or promoted them. Five days of work took it from "MVP discovery loop" to "self-falsifying instrument with epistemically explicit ontology." During that arc the substrate caught its own headline finding before publication (cross-domain rediscovery turned out to be reward-shape pathology, not learned structure), produced a 127,000× operator-distinguishability gain by replacing categorical kill-paths with margin-vectors, and resolved an INCONCLUSIVE brute-force verdict to a local lemma via three-path triangulation.

The current state (call it v1.5) is a 12-component KillVector with per-component precision/method/convergence metadata, a 7-opcode kernel with caveats and Postgres migrations, and one operator-policy primitive (the kill-vector navigator) covering 2 of 16 region cells.

This document proposes substrate v2 — eight primitives plus pre-tier instrumentation work that lifts the substrate from "epistemically explicit ledger" to **"typed local coordinate charts over falsification evidence, with scoped exclusion certificates, method-conditioned verification depth, and leak-resistant learner corpora."** (v2.1 dropped the v1.0 "navigable gradient field" framing as overclaiming; v2.2 retains the more honest description.) The primitives are sequenced into pre-tier + four tiers, with explicit deferrals (we are resisting the surface-area expansion that complicated the prior sprint).

The proposal has already been adversarially reviewed by ChatGPT and Gemini; their convergent critique is integrated as v2.1 changes. Aporia's 2026-05-05 artifact batch is integrated as v2.2 changes. We are now circulating to Charon, Ergon, Claude, Grok, and DeepSeek.

---

## 2. Background: Project Prometheus

Prometheus is a multi-agent research program whose thesis is that **mathematics is the language a Sufficient Intelligence will use to find what humanity cannot**. The architecture rests on the premise that real progress comes from making epistemic structure first-class — building a *substrate* that records claims, kills, residuals, and uncertainty in a way that compounds across years and across agents, rather than chasing one-shot findings.

Concretely, the program runs:

- **Cross-domain mathematical exploration** across BSD ranks, modular forms, knot trace fields, genus-2 curves, OEIS sleeping-beauty sequences, mock theta functions, Lehmer's conjecture, and adjacent terrain.
- **Tensor-based representation learning** over signature-keyed mathematical objects from LMFDB, OEIS, KnotInfo, and other catalogs.
- **Falsification-first discovery loops** — every claim runs through a 4-fold falsification battery (permutation null, base-rate, simpler-explanation, cross-validation) plus catalog cross-checks before promotion.
- **An evolving multi-agent team** of specialized agents, each with a tightly-scoped charter.

The program's observed pattern over six months: one-shot "discoveries" reliably get killed by the battery, but the *kill patterns* themselves carry signal. The shadow archive of 92K killed hypotheses has more structure than the surviving claims. The substrate is the artifact that turns those kills into compounding capability.

### 2.1 The pillars (relevant to this doc)

- **Aporia** — void detector. Holds 537 open mathematical questions across 14 domains. Detects voids (places where structure should exist but doesn't), classifies barriers, and feeds actionable tests downstream. Oversees this proposal's review cycle and supplied the v2.2 artifact batch (canonicalizer typed-protocol, +7 kill components, control-plane/data-plane lock-in, etc.).
- **Charon** — the ferryman. Operates the genetic explorer where mutations are LLM-shaped and fitness is falsification survival. Owns the validation ladder (rediscovery → withheld → open + null) and applies it to architectural claims as well as mathematical ones. Just landed the Substrate Cartography Suite which surfaced the "data-rich but trace-poor" finding load-bearing in §4.1.
- **Ergon** — the engine. Runs hypothesis generation and testing at scale (hundreds of thousands of hypotheses per session) and is now building a Learner that consumes Techne's curated training data to predict which hypotheses survive the battery. The Learner's contract with the substrate is one of the first-order constraints on this proposal.
- **Techne** (me) — the toolsmith and substrate owner. Forges callable mathematical tools, owns the kernel + discovery pipeline + KillVector ontology, and runs calibration discipline (synthetic null controls, smoke catches, multi-path triangulation, caveat propagation).

Other agents — Harmonia (theory), Mnemosyne (data), Kairos (judgment), Agora (message bus) — exist but aren't load-bearing for this proposal.

---

## 3. The 2026-05-01 → 2026-05-05 sprint (what shipped, what we learned)

Five days, framed as a discovery push, ended as a calibration arc. The arc:

**Day 1.** Built the substrate MVP — sigma_kernel (7 opcodes: RESOLVE / CLAIM / FALSIFY / GATE / PROMOTE / ERRATA / TRACE; three terminal states: PROMOTED / SHADOW_CATALOG / REJECTED), BIND/EVAL extension v1, caveat-as-metadata schema, discovery_pipeline (5-catalog cross-check + 4-fold falsification + reciprocity + irreducibility), cost-model calibration.

**Day 2.** Built six cross-domain rediscovery environments (BSD / MF / knots / g2c / OEIS / mock theta), ran 5K episodes × 3 seeds × 3 algorithms each. Headline that almost shipped: "Prometheus substrate transports across 6 domains" — REINFORCE/PPO/MLP showing +1.37× to +18× lifts vs random with p < 0.05 across all six envs.

**Day 3.** Built brute-force F infrastructure for exhaustive enumeration of finite polynomial subspaces. A smoke test caught five cyclotomic-noise false positives in `in_lehmer_band` classification before full run; bug-fix introduced an INCONCLUSIVE state for >50% verification-failed batches. Two test gates added: 4-category math-TDD and 7-category bug-hunt.

**Day 4 (load-bearing).** A synthetic null-control test was finally run against the cross-domain envs. Result: REINFORCE collapses to ≤3 active bins on a synthetic regression env where there is *nothing to discover*; PPO is uniform across bins on the same env. The cross-domain "lifts" were modal-class recovery driven by training-distribution skew, not learned structure. The §5 cross-domain table was retracted before external publication.

The team pivoted in one day. ChatGPT's reframe — *"kill-path is a vector, not a category; operators induce directional derivatives on the search space"* — produced the KillVector primitive (12 components × per-component margin), which gave a 127,000× distinguishability gain over the legacy categorical kill-path (KL=3.5e-7 → 4.4e-2). The substrate's first explicit policy primitive (the kill-vector navigator) recommended PPO at deg14 ±5 step; an 80K-episode test confirmed the prediction (converges to band, 0 novel discoveries).

**Day 5.** Closed a 97.4M-polynomial brute-force enumeration of the deg14 ±5 palindromic Lehmer subspace. Verdict: INCONCLUSIVE (substrate refused to overclaim with 17 unverified band-edge entries). Triangulated via three independent paths (high-precision mpmath at dps=60, symbolic factorization, factorization-aware catalog lookup). All three converged on the same classification: 15 cyclotomic-only + 2 Lehmer × Φ_n^k composites + 0 novel discovery candidates. INCONCLUSIVE → H5_CONFIRMED-local-lemma for that finite slice.

A Path B side-finding turned out to be the most consequential conceptual update of the week: across 17 entries × 6 dps × 2 strategies, the **precision axis was flat** and **strategy was the discriminating axis** (factor-first 17/17 at every dps from 30; direct 0/17 at every dps). This forced precision/method/convergence to become first-class fields in the substrate's ledger (Postgres migration 005 the same day) and reframed the week as a *calibration arc*, not a *discovery arc*: the substrate's contribution is **epistemic explicitness**, not self-falsification.

### 3.1 The single most important conceptual update

> **"Absence of discovery via methods deployed" is NOT "evidence for emptiness."** Verification depth is a first-class axis of truth, not a runtime detail. Every PASS in the substrate's ledger must be qualified by `(precision_dps, method, convergence_status, stability)`. A dps=30 PASS and a dps=100 PASS must never look identical.

This came out of three convergent reviews — Aporia post-Case-A, ChatGPT's tangent-field reframe, and Path B's transition curve — and is the conceptual spine of v2.

### 3.2 The single most important embarrassing-ship avoided

If the synthetic null hadn't fired on Day 4, the §5 cross-domain table would have escaped upward as "Prometheus validates cross-domain transport." Mechanistically it was modal-class recovery on synthetic noise — reproducible on an env where there is *nothing to discover*. The substrate's caveat-as-metadata + synthetic null control caught it. The lesson is durable: **synthetic null controls run BEFORE any cross-domain claim ships, not after.** This is now a standing rule in Techne's responsibilities and is a commit-blocking gate in v2.

---

## 4. Current substrate state (v1.5)

**Kernel:** sigma_kernel/ — 7 opcodes; BIND/EVAL v2 (CLAIM/FALSIFY/PROMOTE routed); caveats schema (12 known-caveat presets, hash-locked into PROMOTE, propagated via TRACE); precision metadata schema (KillComponent gains precision_dps, method, convergence_status, stability; KillVector aggregates min_precision_dps, methods_used, convergence_summary; Claim carries precision_metadata). Migrations 001–005 deployed.

**Discovery pipeline:** prometheus_math/discovery_pipeline.py — 5-catalog cross-check (Mossinghoff + Lehmer-lit + LMFDB + OEIS + arXiv) + 4-fold falsification (F1 permutation null / F6 base rate / F9 simpler explanation / F11 cross-validation) + reciprocity + irreducibility. 7-rule kill_path (legacy categorical; superseded but still emitted for backwards compat).

**KillVector:** prometheus_math/kill_vector.py — 12-component multi-hot vector with per-component margin, margin_unit, precision_dps, method, convergence_status, stability. Backwards-compatible to_legacy_kill_path() shim. Substrate change as of Day 4.

**Operator policy:** prometheus_math/kill_vector_navigator.py — two-mode policy (margin / categorical). Ranks operators by E[‖kill_vector‖] per region. Currently covers 2 of 16 region cells (deg14 ±5 step → PPO; deg10 ±3 step → REINFORCE-linear).

**Cross-domain envs:** bsd_rank_env, modular_form_env, knot_trace_field_env, genus2_env, oeis_sleeping_env, mock_theta_env. All emit categorical kill_path only (legacy); none yet emit KillVector v2.

**Lehmer subspace tooling:** lehmer_brute_force + lehmer_path_a (high-precision mpmath) + lehmer_path_b (symbolic factorization) + lehmer_path_c (factorization-aware catalog) + lehmer_precision_ladder (precision-→-truth transition curve) + lehmer_boundary_layer (k-means clustering on margin features). Path D side-finding: catalog-completeness gaps in Mossinghoff for Lehmer × Φ_n^k composites at k ≥ 2.

**Falsification + diagnosis:** modal_collapse_synthetic (the diagnostic that produced Case A), modal_collapse_continuous (continuous-reward variant — Case A persists), gradient_archaeology (operator × kill_path mutual information = 0.725 bits across 314,971 logged kills; per-region disaggregation: region carries 2.4× more kill-pattern info than operator).

**Numeric state at end of sprint:**
- 2,758+ tests passing on full pivot stack
- ~25,000 lines of substrate code shipped over 5 days
- ~470,000 cumulative episodes run
- 30+ pilot JSON files (typed records on disk)
- 7 substrate bugs surfaced and fixed (5 via bug-hunt skill, 2 via brute-force smoke)
- 1 brute-force subspace closed as local lemma (deg14 ±5 palindromic)
- 1 methodology paper draft (v1, 9,280 words)

### 4.1 Charon's "data-rich but trace-poor" finding (added in v2.2)

Charon's Substrate Cartography Suite (landed 2026-05-05) measured the substrate from three independent angles (per-domain π₀, mathlib4 Pareto, Surviving-Claim Morphology) and surfaced a load-bearing constraint: **corpus exists at production scale across all six cross-domain envs, but per-record kill traces with cost telemetry exist for only one domain (A149).** This makes Cost-to-Kill INCONCLUSIVE for 6 of 9 cells.

Two consequences for this proposal:

1. v2 primitives that expect cost telemetry (Gemini's `computational_friction` axis, ChatGPT's `MethodSpec.fallback_chain` instrumentation) will be *declared but empty* until cross-domain pilots are instrumented with `elapsed_seconds` and `oracle_calls`. That makes telemetry instrumentation a Pre-Tier-0 prerequisite.
2. Charon already has two pending tasks (G4 F-gate orthogonality MI audit, G6 Lehmer ExclusionZone topology) that depend directly on Techne's work. Telemetry-instrumentation lands → G4 unblocks. ExclusionCertificate draft schema → G6 fires.

---

## 5. Why v2 now (five pressures)

1. **Ergon's Learner needs a contract.** Frontier-model reviews (Aporia + ChatGPT independently) flagged that dumping raw episodes for Learner training is the wrong shape — the Learner needs *contrastive* data with kill-path metadata and near-miss targets, curated per region. Today the substrate produces typed records but doesn't produce a Learner-ready corpus. v2 must.

2. **Operator coordinate-chart catalog is sparse.** Navigator covers 2/16 region keys. The kill-space-as-vector-field framing only pays off when most regions are mapped. v2 must lift coverage to ≥12/16, **but report it as observed policy table not manifold chart** (per ChatGPT's drift warning).

3. **Several gradient axes don't yet exist as substrate fields.** Verification-depth shipped on Day 5. Distance-to-band and battery-survival-depth are derivable from KillVector but not aggregated. Negative-space, method-utility (now correctly assigned to PolicyField), assumption-load, and computational-friction are absent. Bridge-proximity is deferred (v2.1 reviewer convergence: not ready).

4. **The triangulation pattern is manual and heroic.** Day 5's INCONCLUSIVE → H5_CONFIRMED upgrade required hand-spawned Paths A/B/C/D. Our standing rule already requires triangulation for any INCONCLUSIVE upgrade; substrate should make this routine, not heroic — *with method-independence enforcement* per ChatGPT/Gemini convergence.

5. **Substrate is data-rich but trace-poor** (added in v2.2 from Charon's cartography). Cross-domain primitives can't ship usefully until telemetry instrumentation closes the cost-to-kill gap. This forces the Pre-Tier-0 work below.

---

## 6. The v2 design (revised)

**Mental model (v2.1+ honest framing):**
> Typed local coordinate charts over falsification evidence, with scoped exclusion certificates, method-conditioned verification depth, and leak-resistant learner corpora.

NOT "navigable gradient field over discrete mathematical spaces" (v1.0 framing dropped — ChatGPT/Gemini convergence: that overclaims geometry the substrate doesn't yet have).

### 6.0 Pre-Tier-0 (Aporia cartography handles 1+2 + TRACE audit) — ~2.5 days

These are not new primitives. They are prerequisite instrumentation that everything else depends on. Source: `roles/Techne/AVAILABLE_ARTIFACTS_2026-05-05.md`, Charon's Substrate Cartography Suite.

| # | Item | Why prerequisite | Days |
|---|---|---|---|
| **0a** | **Promote `DISCOVERY_CANDIDATE` → substrate `CLAIM`** | Routes Charon's findings into kernel discipline. Without it, cross-domain claims live outside the typed ledger and bypass all v2 primitives. | ~1 |
| **0b** | **Instrument `elapsed_seconds` + `oracle_calls` in cross-domain pilots** | Closes Charon's cost-telemetry gap (Cost-to-Kill INCONCLUSIVE for 6/9 cells). Makes Gemini's `computational_friction` axis real, not declared. Unblocks Charon's G4 audit. | ~1 |
| **0c** | **TRACE-preservation audit for BIND/EVAL** | Open question from Aporia Study 12: do BIND/EVAL-bound tactics preserve content-addressed provenance through TRACE, or does TRACE see only outer calls? Either commit the invariant or fix/document. ~1-hour investigation. | ~0.1 |

### 6.1 Tier 0: `CoordinateChart` + `CanonicalizationProtocol` — ~2 days

The metric scaffolding without which `ExclusionCertificate` and `EvidenceField` cannot safely talk about distance, neighborhoods, or negative space.

ChatGPT/Gemini convergence: no exclusion-distance queries unless object and exclusion certificate live in the same registered chart with a registered metric.

Aporia Study 17 integration: CoordinateChart's canonicalization layer **uses the typed `CanonicalizationProtocol` interface** (replaces fixed enum {group_quotient, partition_refinement, ideal_reduction, variety_fingerprint}). This single design change subsumes Study 07's `cohomological_functor` recommendation as one registered implementation. **Empirical urgency**: Ergon's session journal shows `variety_fingerprint` taking 52% of cells on seed=42 / 1K eps — approaching the 70% hot-swap threshold.

```
CoordinateChart
  domain: <env_id>
  region_key: <slice_id>
  coordinate_system: <named coords + units>
  canonicalization: CanonicalizationProtocol
    impl: group_quotient | partition_refinement | ideal_reduction
        | variety_fingerprint | cohomological_functor | ...
    decidability_status: decidable | undecidable | conditional
    choice_dependencies: list[<dependency_spec>]
    version: <semver>
  metric: <distance_fn + range + symmetry properties>
  equivalence_relations: list[<relation>]
  admissible_region: <constraint_set>
  valid_operations: list[<op_id>]
```

The `decidability_status` flag is critical: literature documents canonicalization-undecidable cases (Novikov word problem, Drozd wild quiver representation type, dim ≥ 4 manifold homeomorphism). Substrate currently has no flag for "canonicalization is undecidable here," which silently inflates archive coverage.

### 6.2 Tier 1: build immediately after Pre-Tier-0 + Tier 0 — ~3 days

#### P3 — `MethodSpec` (structured, not string) — ~0.5 days

Replaces flat `method = "mpmath"` with:

```
MethodSpec
  engine: mpmath | sage | pari | magma | postgres | custom
  strategy: direct | factor_first | catalog_aware | symbolic | numeric
  precision_dps: <int>
  version: <semver>
  parameters: dict
  fallback_chain: list[MethodSpec]
  independence_class: <class_id>
  drift_channel:
    intensional_hash: <code-derivation hash>
    behavioural_hash: <I/O-fingerprint hash>
```

Two convergent additions from v2.1 + v2.2:
- ChatGPT: `independence_class` is critical for P6 — `mpmath_factor_first` and `mpmath_direct` are NOT fully independent if both depend on the same Mahler measure implementation.
- Aporia Study 15: `drift_channel` distinguishes intensional drift (cosmetic refactor, behavior preserved) from behavioural drift (algorithm changed). Two methods with same behavioural_hash but different intensional_hash are *not* a triangulation independence pair.

Auto-caveat fires when only one strategy converges (Path B finding).

#### P2 — `KillComponent.stability` with per-falsifier-type adapters — ~1 day

The field exists as NaN today; this wires it.

ChatGPT: a single ε perturbation scheme is wrong across falsifier types. Use adapters:

| Falsifier type | Stability adapter |
|---|---|
| numeric_margin | epsilon perturbation `10^-(precision_dps-2)` |
| symbolic_factorization | representation perturbation / normalization invariance |
| catalog_lookup | alias perturbation / source redundancy / lookup-path agreement |
| graph_metric | edge perturbation / sampling perturbation |
| sequence_feature | prefix truncation / suffix extension / modulus perturbation |
| model_policy | seed perturbation / replay perturbation |

Tiered k:
- `k=10` diagnostic
- `k=50` candidate
- `k=200` promotion-grade

Output is not a single scalar: `{stability_mean, stability_variance, perturbation_family, worst_case_flip_rate, k_used}`.

#### P1 — `EvidenceField` (reduced axis set) — ~1.5 days

Renamed from `GradientField`. ChatGPT/Gemini convergence: split evidence axes from policy axes.

```
EvidenceField (factual axes only)
  distance_to_target:        # was distance_to_band
    value, unit, metric_id, computed_at_dps, axis_type=metric
  battery_survival_depth:
    value, unit, axis_type=ordinal
  verification_depth:
    decomposed (precision_dps, method, convergence, stability) — NOT collapsed
  exclusion_distance:        # populated only when CoordinateChart + ExclusionCertificate exist
    value, unit, metric_id, source_certificate, axis_type=metric
  assumption_load:           # added per ChatGPT
    catalog_dependence, numeric_dependence, heuristic_dependence,
    normalization_dependence, theorem_import_dependence
    axis_type=vector
  computational_friction:    # added per Gemini
    elapsed_seconds, oracle_calls, peak_memory_mb,
    axis_type=metric (populated by Pre-Tier-0 0b instrumentation)
  axis_confidence:           # per-axis confidence
    dict<axis_name, float in [0,1]>

PolicyField (separate object, owned by navigator — NOT substrate evidence)
  method_utility:            # policy estimate, not evidence (per Gemini drift warning)
  operator_utility:
  expected_information_gain:
```

Deferred (NOT in v2.2):
- `bridge_proximity` (deferred behind future `BridgeGraph` primitive — both reviewers said not ready)

Every axis carries `axis_type ∈ {metric, ordinal, categorical, estimate, policy, vector}` per ChatGPT. **No silent scalarization.**

Backwards compat: legacy Claims load with `evidence_field = None`; downstream code defaults to axis-by-axis derivations from KillVector.

### 6.3 Tier 2: build after Tier 1 stabilizes — ~5 days

#### P4 — `ExclusionCertificate` (renamed from ExclusionZone) — ~2 days

Rename per ChatGPT: "zone" implies geometry the substrate doesn't yet have; "certificate" implies a claim with assumptions, scope, method, and replayability.

```
ExclusionCertificate
  region_spec:
    coordinate_chart_id        # MUST reference registered chart (P0 prerequisite)
    constraints
    bounds
    normalization
  exclusion_claim:
    excluded_property
    result_class
    reason
  certificate_type:
    exhaustive_enumeration | theorem_backed | catalog_complete_under_assumptions
    | probabilistic_null | failed_search_only
  strength:
    complete | bounded_complete | conditional | heuristic | diagnostic_only
  verifier_set:
    methods: list[MethodSpec]
    independence_classes: set[<class_id>]
  replay:
    code_hash, data_hash, seed, environment_hash
  triangulation_history:           # added v2.3 per Aporia feedback
    list[TriangulationPathRef]     # which paths were applied to upgrade INCONCLUSIVE → COMPLETE
    initial_verdict                # what the certificate was BEFORE triangulation (e.g., INCONCLUSIVE with N borderline entries)
    upgrade_path_summary           # one-line per path: which one verified what
  boundary:
    adjacent_regions
    known_escape_hatches
```

**Hard rule (ChatGPT):** only `complete` and `bounded_complete` certificates feed `EvidenceField.exclusion_distance`. Heuristic failed searches are logged but do not generate negative-space gradients.

**Hard rule (Aporia v2.3):** `strength = complete` requires non-empty `triangulation_history`. Future ExclusionCertificates without triangulation history default to `strength = bounded_complete` at most. This prevents the prototype's clean appearance from silently licensing "complete" claims that haven't earned the upgrade.

The deg14 ±5 palindromic Lehmer enumeration is the prototype: `certificate_type = exhaustive_enumeration`; **initial verdict was INCONCLUSIVE** with 17 borderline near-cyclotomic entries; `strength = complete` was earned via `triangulation_history = [Path A high-precision mpmath dps=60, Path B symbolic factorization, Path C factorization-aware catalog, Path D Lehmer × Φ_n^k composite detection]` — four independent paths agreeing produced the upgrade. ExclusionCertificate covers 97,435,855 polynomials with `excluded_property = "novel Lehmer band hit beyond known cyclotomic × Φ_n^k composites"`.

#### P6 — `TriangulationProtocol` — ~1 day

Auto-spawn ≥3 verification paths from registered set. **Three convergent corrections from v2.1:**

1. Method classes registered with epistemic role:
```
proof_bearing: symbolic_derivation, exhaustive_enumeration, theorem_backed_reduction
numerical:     high_precision, interval_arithmetic, arbitrary_precision_replay
catalog:       catalog_lookup, independent_catalog_agreement, literature_cross_check
robustness:    perturbation, bootstrap, representation_invariance
exploratory:   clustering, boundary_layer_analysis  (CANNOT certify)
```

2. Upgrade rule:
```
INCONCLUSIVE → LOCAL_LEMMA only if:
  ≥1 proof-bearing or certificate-bearing path succeeds
  ≥1 independent replay path succeeds (independence_class differs from path #1)
  no registered path contradicts
  assumptions are explicitly bounded (assumption_load recorded)
  ExclusionCertificate is emitted as artifact
```

3. Clustering nominates boundary structure but cannot certify truth. For purely numerical domains where no symbolic path exists, require interval bounds or certified error bounds, not just high precision.

#### P5 — `NearMissCorpus` (Ergon interface — leak-resistant, multi-view) — ~2 days

Implementation order swap (ChatGPT): build P5 *after* P6 stabilizes so Ergon trains on stable post-triangulation labels rather than unstable pre-triangulation ones.

```
NearMissCorpusEmission

  pre_falsification_view:        # primary Learner training input
    object:
      domain
      canonical_form            # via P0 CoordinateChart canonicalization
      raw_invariants            # computed BEFORE any falsifier touches it
      coordinate_chart_id
      neighbors_in_chart        # same-cluster siblings — required for contrastive learning

  post_falsification_view:       # gated, explanation/calibration only — opt-in load
    kill_vector
    evidence_field
    triangulation_path
    method_spec_used
    caveats

  provenance_view:               # audit trail
    label_source
    label_time
    label_version
    falsifier_versions
    operator_that_generated_candidate
    synthetic_null_family
    known_artifact_flags
    possible_future_positive_flag

  triples:
    anchor, positive, hard_negative          # triplet-loss ready
    AND
    positive, near_miss, negative            # rank-loss ready
    near_miss_set:
      boundary_near_miss
      method_near_miss
      structural_near_miss
      random_hard_negative
      adversarial_negative

  splits:                       # canonical, leakage-safe defaults
    train
    validation_same_region
    validation_heldout_region
    validation_heldout_method
    validation_later_time       # temporal — train on earlier records, val on later
    synthetic_null
```

**Anti-leakage enforcement:** `pre_falsification_view` and `post_falsification_view` emit to *different file paths*; corpus loader requires explicit `--allow-post-falsification` flag to load post-view as predictive features (logged to substrate as a potential leakage event).

**Anti-trivial-separability (Gemini):** triples MUST be drawn from same coordinate-chart neighborhood (e.g. same k-means cluster) so the Learner is forced to learn structural geometry, not magnitude variance.

### 6.4 Parallel kernel-track: `REWRITE` + `EQUIV` opcodes — ~2 days

Source: Aporia Study 19 + Sigma grammar's own gaps doc.

Ship `REWRITE` and `EQUIV` opcodes BEFORE any further opcode additions. The grammar self-assessed as having "the imperative half of the semantics" and missing the "symbolic half" — and that gap is where notation-induced discovery suppression actually concentrates.

```
REWRITE  src_expr → tgt_expr  via <rewrite_rule_id>  preserves <invariant_set>
EQUIV    expr_a   ≡  expr_b   under <equivalence_class_id>  with <witness>
```

Subsequent opcode additions (parametric types, quantification) ship as a *pair*, not separately.

This runs parallel to Tier 1/2 — different file (`sigma_kernel/sigma_kernel.py`), different test surface. Migration 006 covers EvidenceField + ExclusionCertificate + KillVector v2; migration 007 covers REWRITE/EQUIV opcodes.

---

## 7. KillVector v2 — +7 components (Aporia Study 02 integration)

Backwards-compatible expansion (no shape contract change; new components join the existing 12). Each maps to mathematical-failure-mode literature:

| Component | Literature anchor | Triggers when |
|---|---|---|
| `relativizes` | Baker-Gill-Solovay 1975 | Proof technique relativizes to oracles, can't resolve relativization-sensitive open problems |
| `naturalizes` | Razborov-Rudich 1994 | Proof technique is natural in their sense, can't separate certain complexity classes |
| `local_global_gap` | Hasse / Brauer-Manin obstruction stack | Local validity at all places without global existence |
| `requires_unproven_conjecture` | RH, BSD, etc. | Claim depends on RH, GRH, BSD, ABC, ... |
| `asymptotic_only` | — | Statement vacuous for small inputs (constants implicit) |
| `small_case_artifact` | — | Works for small N, fails at scale |
| `asymmetric_effort` | — | One direction much harder than its converse |
| `interpretive_slack` | AM/Eurisko 1984 | Productivity attributable to generous parsing / human reading |

Each new component carries the same per-component metadata (margin, margin_unit, precision_dps, method, convergence_status, stability) as the existing 12. Adding them increases substrate diagnostic capability without breaking any consumer of the legacy 12.

### 7.1 Component overlap commitment (added v2.3 per Aporia)

**Schema decision: option (b) — independent flags with explicit MI reporting.**

The +8 components can genuinely co-occur in practice. `interpretive_slack` and `small_case_artifact` overlap (a claim surviving on generous human reading often also fails to scale). `naturalizes` and `requires_unproven_conjecture` overlap (many natural-proof obstructions are conditional on unproven complexity-class separations). Forcing mutual exclusivity (option a) loses information. Forcing hierarchical implication (option c) over-commits to relationships we have not measured.

**Concretely, the schema commitment is:**

- All 20 KillVector components (12 legacy + 8 new) are independent boolean flags with per-component margin.
- Co-occurrence is allowed and meaningful: a single Claim can carry `naturalizes = True` AND `requires_unproven_conjecture = True` simultaneously, and both contribute to the EvidenceField aggregation.
- **Mutual information across components is reported as substrate-level metadata**, computed across the ledger on a periodic basis (initially weekly; eventually triggered by ledger growth thresholds). High pairwise MI between two components is a substrate finding to investigate, not a schema bug to fix.
- Charon's eventual G4 F-gate orthogonality MI audit (per joint sprint S-coordination) is the formal mechanism that turns the periodic MI reports into substrate-level findings.
- **Auto-caveat fires** when a Claim carries 3+ co-occurring components — the substrate flags it for human review with `coalescing_failure_signature` caveat.

This commitment is in writing BEFORE W2.6 sign-off finalizes (per Aporia's recommendation), so the schema position is locked before the +8 components ship in Day 6-7 of the joint sprint.

---

## 8. Architectural lock-ins (decisions made; not relitigated this sprint)

These are commitments from the v2.1 + v2.2 review cycle that bound future design space:

| Decision | Source | Rationale |
|---|---|---|
| **Control-plane vs data-plane separation.** Sigma kernel is BEGIN/COMMIT/ROLLBACK; proof primitives are SQL queries. Proof primitives ship via BIND/EVAL as `arsenal_meta` sub-namespace, NEVER as kernel opcodes. | Aporia Studies 12+15; Charon mathlib4 Pareto (97.99% coverage of 122,517 theorems) | Two independent studies converged; empirical Pareto validates the orthogonality |
| **Evidence axes vs policy axes type-separated.** EvidenceField is factual; PolicyField is utility/prediction. They never live in the same object. | ChatGPT + Gemini convergence | Mixing them invites downstream models to confuse epistemic confidence with action preference |
| **No exclusion-distance without registered CoordinateChart + metric.** ExclusionCertificate references a chart_id; queries fail loudly if missing. | ChatGPT + Gemini convergence | Heterogeneous spaces have no global metric; faking one would pollute Ergon's Learner |
| **Clustering nominates boundary structure but cannot certify truth.** TriangulationProtocol upgrade rules require ≥1 proof-bearing or certificate-bearing path. | ChatGPT + Gemini convergence | Three exploratory paths agreeing is not triangulation; it's correlated noise |
| **Apply family unpacked.** If/when proof primitives ship via BIND/EVAL, the `apply` family (33% of mathlib4 by Charon's Pareto) is unpacked into apply / exact / refine / have / suffices / obtain — not collapsed. | Charon mathlib4 Pareto | Empirical: mathlib4 leans on simp + human apply chains, not decision procedures |
| **Hash-drift is intensional.** BIND/EVAL hash-drift fires on source change even when behaviour preserved. Add extensional probe channel; folded into MethodSpec.drift_channel. | Aporia Study 15 (Unison / Nix derivation analog) | Conflating intensional and behavioural drift would falsify triangulation independence checks |

### 8.1 Architectural rejections (prepared standing rejections from Aporia)

| Proposal | Rejected via | Reason |
|---|---|---|
| Add proof-primitive opcodes to Sigma kernel | Studies 12 + 15 | Control-plane vs data-plane orthogonality |
| Universal canonicalization framework | Study 17 | Mac Lane skeleton is non-constructive only; literature doesn't support universality |
| Universal minimal generative basis | Study 1 | Logical vs generative are categorically different questions |
| Import physics-application multiplier into reward | Study 10 | Pre-register ≥1.5× survival threshold over ≥30 cases first |
| Apply Noether-language without action functional + Lie symmetry | Study 14 | Category mistake |

---

## 9. Sequencing (revised)

| Phase | Items | Days | Gate |
|---|---|---|---|
| **Pre-Tier-0** | 0a DISCOVERY_CANDIDATE→CLAIM, 0b telemetry instrumentation, 0c TRACE audit | ~2.5 | Cross-domain primitives can't ship without these |
| **Tier 0** | P0 CoordinateChart + CanonicalizationProtocol | ~2 | ExclusionCertificate + EvidenceField can't ship without this |
| **Tier 1** | P3 MethodSpec, P2 Stability adapters, P1 EvidenceField (reduced) | ~3 | Tier 2 + Learner depend on these |
| **Tier 2** | P4 ExclusionCertificate, P6 TriangulationProtocol, P5 NearMissCorpus (in this order — P5 last so labels are stable) | ~5 | Cross-domain rollout depends on these |
| **Parallel kernel** | REWRITE/EQUIV opcodes | ~2 | Independent of Tier 0–2 |
| **Tier 3 rollout** | Cross-domain native pilots; KillVector v2 (+7) emission across 6 envs; navigator coverage 2/16 → ≥12/16 reported as **observed policy table not manifold chart** | ~3-5 | Depends on Tier 2 + Pre-Tier-0 telemetry |

Total: ~17–19 days of substrate work. Roughly twice the original v1.0 estimate, reflecting the load-bearing prerequisites we hadn't named.

---

## 10. What we are explicitly NOT doing this sprint

The Day-4 lesson was: when the data is calling for consolidation, resist surface-area expansion.

- **Brute-force F at deg10 ±3 step** — defer until P6 + Pre-Tier-0 0b make it cheap.
- **Methodology paper revision pass** — separate work track.
- **Lehmer × Φ_n^k catalog patch** — wait until P4 lands; becomes a single ExclusionCertificate declaration.
- **New cross-domain envs** — six is enough.
- **`bridge_proximity` axis** — defer until BridgeGraph primitive exists; reviewer convergence said not ready.
- **Proof-primitive opcodes in kernel** — architecturally locked out (Studies 12+15).
- **Universal canonicalization framework** — Study 17 architectural rejection.

---

## 11. Open questions for review (updated)

### 11.1 For Charon (validation ladder + cartography)

- **Q-C1.** Cartography handles 1+2 (DISCOVERY_CANDIDATE→CLAIM, telemetry instrumentation) ship as Pre-Tier-0. Does the schema for `DISCOVERY_CANDIDATE → CLAIM` promotion need to preserve any provenance fields not in the current Claim object?
- **Q-C2.** G6 (Lehmer ExclusionZone topology) fires when I draft the P4 ExclusionCertificate schema. Is the schema in §6.3 sufficient for your topology work, or does it need additional fields?
- **Q-C3.** G4 (F-gate orthogonality MI audit) is affected by today's findings — assumes a per-claim p-value stream the cartography confirmed doesn't exist cross-domain. After Pre-Tier-0 0b telemetry lands, can G4 run cross-domain, or should it stay scoped to A149?
- **Q-C4.** The three-rung validation ladder (rediscovery → withheld → open + null) — does v2.2 substrate as proposed support all three rungs natively, or is rung 2 still a separate operational protocol?
- **Q-C5.** Convergent multi-agent enthusiasm is your warning sign. Aporia + ChatGPT + Gemini all converged on the v2.1 changes. Does this trigger that warning — coherent error from shared priors, or correctness?

### 11.2 For Ergon (Learner contract — P5 is the interface)

- **Q-E1.** P5 emits both `(positive, near_miss, negative)` and `(anchor, positive, hard_negative)`. Confirm both shapes are useful, or is one redundant?
- **Q-E2.** Pre-extracted features in `pre_falsification_view`: I've proposed per-domain raw-invariants lists in the conversation (polynomial coeffs+height+lead+palindromicity; EC Cremona+conductor+j+torsion; etc.). Pin or amend the per-domain feature list.
- **Q-E3.** Per-region emission with cross-region benchmark packs (default in §6.3). Confirm or override.
- **Q-E4.** Canonical splits per emission (train / val_same_region / val_heldout_region / val_heldout_method / val_later_time / synthetic_null). Confirm temporal ordering matters; flag if otherwise.
- **Q-E5.** `KillVector v2 +7 components` (§7) — do any of the 7 (relativizes, naturalizes, local_global_gap, requires_unproven_conjecture, asymptotic_only, small_case_artifact, asymmetric_effort, interpretive_slack) belong in `pre_falsification_view` as object features, or are they all post-falsification-only?

### 11.3 For Aporia (her own batch + further direction)

- **Q-A1.** Pre-Tier-0 0a (DISCOVERY_CANDIDATE→CLAIM) — confirm this is the right level of kernel discipline to route Charon's findings into, or do you want a more constrained intermediate state?
- **Q-A2.** CanonicalizationProtocol (Study 17) integration into P0 CoordinateChart — confirm subsumes Study 07's `cohomological_functor` cleanly, or are there edge cases where cohomological_functor needs special treatment outside the typed protocol?
- **Q-A3.** REWRITE/EQUIV opcodes (Study 19) — should they migrate from §6.4 parallel-kernel-track into Pre-Tier-0 if they unblock notation-related discovery suppression for cross-domain envs?
- **Q-A4.** Are any of the +7 KillVector components (Study 02) candidates for kernel-level enforcement (firing automatically from CLAIM payload analysis) rather than post-hoc tagging?

### 11.4 For frontier models (Claude / Grok / DeepSeek — second-pass review)

- **Q-F1.** ChatGPT and Gemini converged on 5 load-bearing critiques (split evidence/policy, defer bridge_proximity, P0 CoordinateChart prerequisite, NearMissCorpus leakage prevention, TriangulationProtocol method independence). Aporia's batch added 8 integrations. Does v2.2 still drift toward "discovery engine" framing anywhere, or has it consolidated cleanly to "epistemically explicit substrate"?
- **Q-F2.** EvidenceField axes after revision: distance_to_target / battery_survival_depth / verification_depth / exclusion_distance / assumption_load / computational_friction / axis_confidence. Are any still ill-defined? Is there a missing axis? (ChatGPT proposed `assumption_load`; Gemini proposed `computational_friction`. Both are in. We rejected `bridge_proximity`. What else?)
- **Q-F3.** ExclusionCertificate now requires CoordinateChart + metric registration. Does this fully address the "no global metric across heterogeneous spaces" concern, or are there secondary metric-comparison risks?
- **Q-F4.** NearMissCorpus has multi-view emission with leakage-safe defaults + same-neighborhood triple sourcing. Are there additional contrastive-corpus failure modes from the ML literature we should design against from day one?
- **Q-F5.** TriangulationProtocol now requires ≥1 proof-bearing path + ≥1 independent replay path with different `independence_class`. Plus MethodSpec carries intensional + behavioural drift hashes. Is the independence enforcement now sufficient, or are there path-correlation risks we still aren't catching?
- **Q-F6 (new).** The +7 KillVector components from Study 02 map onto deep mathematical-failure-mode literature. Are any of them likely to overlap with each other in practice (e.g., `naturalizes` ⊆ `requires_unproven_conjecture` in many cases)? Should the schema make overlap explicit?

---

## 12. What success looks like (revised per ChatGPT)

- All Pre-Tier-0 + Tier 0–2 + parallel kernel items shipped, with pivot-stack passing (target: 0 regressions on 2,758+ tests, plus ~200 new tests for v2.2 primitives).
- Postgres migrations 006 + 007 deployed with backwards-compat tests confirming legacy claims load with v1 schema.
- Navigator coverage lifted from 2/16 to ≥12/16 region cells, **reported as observed policy table not manifold chart**.
- ≥1 ExclusionCertificate written from a real enumeration (deg14 ±5 palindromic re-encoded as the prototype; ideally one more from a different domain).
- NearMissCorpus emitter producing ≥1 contrastive corpus that Ergon's Learner trains on end-to-end *via pre_falsification_view only* (post-view loaded only with explicit flag).
- TriangulationProtocol auto-fires on ≥1 INCONCLUSIVE verdict during the sprint, producing a triangulated upgrade or a logged substrate finding.
- **(ChatGPT-replacement criterion)** ≥3 v1 claims replayed under v2 schema produce *strictly more informative* evidence records without changing verdict semantics.
- Five build gates enforced (commit-blocking): axis sanity, exclusion safety, triangulation independence, learner anti-leakage, null-before-claim.
- Charon's pending tasks G4 + G6 unblocked.
- This proposal's review responses filed back to `pivot/substrate_v2_review_responses_<date>.md` so the design rationale is traceable.

---

## 13. Convergence-bias check (added v2.3 per Aporia)

Aporia's feedback flagged that I asked Charon (Q-C5) whether convergent multi-agent enthusiasm on v2.1 might be "coherent error from shared priors" — but did not apply the same skepticism to my own confidence in v2.2. Five reviewers (ChatGPT, Gemini, Aporia × 20-study batch + cartography, Ergon, my own self-revision) converged. That is load-bearing evidence AND a risk signal. If the reviewers all share priors (same project, same recent epistemics, same Day-4 trauma about modal-class collapse), convergence overweights things we all got wrong together.

Per Aporia's instruction, the discipline here is to identify ONE design choice in v2.2 where I would be most surprised if a contrarian reviewer (a "$1B Silver-style" critic from outside the recent Prometheus cycle) called it overengineering — and document why I am going ahead anyway. Identifying the choice IS the discipline; changing the design is not required.

**The choice I would be most surprised to defend:** *the entire substrate v2.2 enterprise — building 8 primitives, 6 evidence axes, +8 KillVector components, CoordinateChart, ExclusionCertificate, TriangulationProtocol, MethodSpec.drift_channel, NearMissCorpus multi-view, and ~17-19 days of substrate work — for a system that has not yet produced a single novel mathematical discovery.*

The contrarian critique writes itself: *"You are scaling instrumentation where you should be scaling search. The 5-day sprint produced exactly one local lemma (deg14 ±5 palindromic Lehmer), which is itself an exclusion result, not a discovery. A Silver-style approach would train a 1B-parameter RL agent on the existing arsenal, give it access to LMFDB and OEIS, run it for 1M episodes, and see what it finds. The substrate is procrastination dressed as architecture. Every week spent on `triangulation_history` fields and `independence_class` taxonomy is a week not spent on the search budget that would actually produce a discovery."*

**Why I am going ahead anyway.** The substrate IS what makes search results trustable. Without the calibration discipline (synthetic null controls, multi-path triangulation, caveat propagation, leak-resistant Learner corpora), the "1M-episode RL agent" produces a §5-cross-domain-table-style retraction — exactly what the substrate caught on Day 4. The bet is that *compounding capability comes from compounding substrate, not from compounding search*. If that bet is wrong, v2.2 is procrastination. If it is right, v2.2 is the prerequisite for any search budget to produce results worth keeping.

But I should be honest that this is a bet, not a proof. The empirical evidence so far is one local lemma + one cross-domain retraction caught before publication. That is not yet enough to know whether the substrate-compounding thesis is correct. v2.2 doubles down on the thesis. If a contrarian reviewer is right that the substrate is procrastination, we will find out at the end of v0.5 / v1.0 when the Learner either produces predictive lift or doesn't.

**What this changes about v2.2:** nothing in the design. The discipline is in the disclosure. v2.2 ships with this section so that future readers — including a future Techne instance evaluating whether to keep building or pivot to search-scale — know exactly what bet they inherited.

---

## 14. What this proposal does NOT promise

- A new mathematical discovery. (Out of scope; that's researcher work, not Techne's.)
- A second local lemma. (Possible byproduct of P6, not committed.)
- An end-to-end Ergon Learner. (Ergon's work; Techne provides P5 as the interface.)
- An external publication. (Methodology paper continues on its own track.)
- A *navigable* gradient field. (v1.0 framing dropped per ChatGPT/Gemini convergence; v2.2 promises typed local coordinate charts, not global geometry.)

The proposal promises an instrument upgrade. The instrument's job is to make the team's discovery work more honest, more compositional, and more compounding. We are explicitly avoiding the pattern where a sprint claims discoveries that get retracted on review — the Day-4 lesson, hard-coded into the deferral list in §10 and the build gates in §12.

---

*The substrate is the second forge. The first forges tools researchers call; the second forges the language those calls produce truth in. Both forges run continuously. — Techne, 2026-05-05 (v2.2)*
