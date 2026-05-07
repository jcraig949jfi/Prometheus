# Σ-substrate kernel — architecture

> **Public read note.** Primary architecture document for the Σ-kernel — the substrate runtime at the heart of Project Prometheus. Linked from the project's top-level [README](../../../README.md). v0.1 MVP shipped 2026-04-28 (7 opcodes, single-process). v2.3 substrate sprint shipped 2026-05-06 (commit `d17a2ff8`): kernel grew to 9 opcodes (+ REWRITE / EQUIV); KillVector v2 added 8 components (total 20); ExclusionCertificate, TriangulationProtocol, CoordinateChart with CanonicalizationProtocol, MethodSpec, EvidenceField, NearMissCorpus full emission all landed. See [`pivot/substrate_v2_proposal_2026-05-05.md`](../../../pivot/substrate_v2_proposal_2026-05-05.md) for the v2.3 design rationale.

**Status:** v2.3 shipped 2026-05-06 (commit `d17a2ff8`); 607 tests passing; 11 new modules; 9 kernel opcodes. Single-agent, single-process. Substrate-native runtime that mechanically enforces epistemic discipline.

**Code:** `sigma_kernel/` + `prometheus_math/` (this repo).
**Long-form design history:** [`sigma_council_synthesis.md`](sigma_council_synthesis.md) — 25 rounds of multi-model design dialogue, from "design a programming language for agentic models" through to a 13-opcode RISC, ecology dynamics, theory-space curvature, and back down to the buildable kernel.
**Symbol candidates surfaced:** [`../symbols/CANDIDATES.md`](../symbols/CANDIDATES.md) — three new Tier-3 candidates (`OBSTRUCTION_SHAPE`, `ORACLE_PROFILE`, `NULL_MODEL_FAMILY`) with anchor evidence from the kernel.

---

## What this is

The Σ-substrate kernel is a runtime for **promoted symbols** that mechanically enforces, rather than socially trusts, the disciplines Harmonia has converged on:

- **Append-only substrate**: once a symbol is promoted at version N, its definition blob is frozen forever. Bug fixes are new versions (v(N+1)), never mutations.
- **Linear capability tokens**: promotion / demotion / errata require typed one-shot capabilities; tokens are consumed by use.
- **Three-valued GATE semantics**: filter outputs are `CLEAR` / `WARN(rationale)` / `BLOCK(rationale)`, not Boolean. `BLOCK` short-circuits; `WARN` bubbles with rationale; `CLEAR` continues.
- **Falsification-first promotion**: a claim cannot be promoted unless it has been run through a kill path and the verdict is non-`BLOCK`. PROMOTE itself rechecks (defense-in-depth).
- **Content-addressed provenance**: every value carries the hashes of the symbols and inputs that produced it; RESOLVE recomputes the def_hash and rejects mismatches.

The discipline lives in the runtime, not in agent goodwill. An LLM-driven worker that tries to overwrite a promoted symbol or double-spend a capability is rejected by the kernel before the misuse is observable on the bus.

## Scope of v0.1 vs v2.3

The v0.1 kernel demonstrated mechanically-enforceable discipline. v2.3 extends with the typed substrate primitives that downstream consumers (Ergon Pipeline-D, KillEmbedding, Charon cartography) require.

| Layer | v0.1 (2026-04-28) | v2.3 (2026-05-06) |
|---|---|---|
| Opcodes | 7 (RESOLVE / CLAIM / FALSIFY / GATE / PROMOTE / ERRATA / TRACE) | 9 (above + REWRITE + EQUIV) |
| Process model | Single-agent, single-process | unchanged |
| Storage | SQLite (default) + Postgres adapter | unchanged |
| Ω oracle | One subprocess, deterministic toy | unchanged |
| Bootstrap | Hardcoded GENESIS | unchanged |
| BIND/EVAL extension | sidecar (v2 routes through CLAIM/FALSIFY/PROMOTE) | unchanged; TRACE-preservation invariant audited (see [`TRACE_PRESERVATION_AUDIT.md`](../../../sigma_kernel/TRACE_PRESERVATION_AUDIT.md)) |
| Kill outcome shape | Categorical `kill_path: str` | KillVector v2 (20 components: 12 legacy + 8 v2 from Aporia Study 02) |
| Caveat propagation | Hash-locked through TRACE | unchanged (see [migration 004](../../../sigma_kernel/migrations/004_add_caveats_to_claims.sql)) |
| Precision metadata | – | First-class on Claim ([`PRECISION_METADATA_SPEC.md`](../../../sigma_kernel/PRECISION_METADATA_SPEC.md); [migration 005](../../../sigma_kernel/migrations/005_add_precision_metadata.sql)) |
| Region scaffolding | – | CoordinateChart + CanonicalizationProtocol with `decidability_status` flag (Lehmer chart registered) |
| Method identity | flat `method: str` | Structured MethodSpec with `independence_class` + `drift_channel` (intensional + behavioural hashes) |
| Stability scoring | scalar | Per-falsifier-type adapters + tiered `k=10/50/200` + structured StabilityResult |
| Evidence aggregation | implicit | EvidenceField (6 factual axes; PolicyField separate per ChatGPT/Gemini convergence) |
| Negative-result encoding | – | ExclusionCertificate (with `triangulation_history` hard rule per Aporia 2026-05-05 feedback) |
| Triangulation discipline | manual | TriangulationProtocol (5 method classes; clustering CANNOT certify) |
| Learner contract | – | NearMissCorpus full triangulated emission ([`LEARNER_CORPUS_SPEC.md`](../../../prometheus_math/LEARNER_CORPUS_SPEC.md)) |

What stayed deliberately out of scope at v2.3: the long-synthesis layers (DISTILL, STABILIZE, COMPOSE, FORK, JOIN, ADJUDICATE, OBJECT, REFUTE, CONSTRAIN, CALIBRATE), multi-agent quorum, swarm coordination, full Ω ecology, theory-space curvature with `χ`-field. Most are conditional on the curvature experiment producing predictive signal.

## The 9 opcodes

| Op | Semantics |
|----|-----------|
| `RESOLVE(name, version) → Symbol` | Fetch by `(name, version)`. Recompute def_hash; reject on mismatch (`IntegrityError`). |
| `CLAIM(target, hypothesis, evidence, kill_path, tier=Conjecture) → Claim` | Allocate provisional claim. Born at lowest tier unless overridden. |
| `FALSIFY(claim, seed) → VerdictResult` | Dispatch claim + kill_path to the Ω oracle subprocess; bind verdict to claim. Fails closed: any oracle error becomes a BLOCK with rationale. |
| `GATE(verdict) → flow` | `BLOCK` raises `BlockedError`; `WARN` prints rationale and returns `"WARN"`; `CLEAR` returns `"CLEAR"`. |
| `PROMOTE(claim, capability) → Symbol` | Atomic transaction: verify cap unconsumed, verify claim has non-BLOCK verdict, consume cap, append symbol, update claim status. Fails-and-rolls-back as a unit. |
| `ERRATA(prior_name, prior_version, corrected_def, fault, cap) → Symbol` | Promote v(N+1) with `errata_correcting` backref to vN. vN stays immutable in the substrate as historical record. |
| `TRACE(symbol) → ProvenanceGraph` | Recursive walk of the dependency hashes. Cycle-safe via visited set. Hashes that don't resolve are tagged `external`. Caveats and precision_metadata propagate through the walk. |
| `REWRITE(src_expr, tgt_expr, rewrite_rule_id, invariants_preserved, cap, rationale) → Symbol` | **v2.3.** Mint a Symbol that records `src_expr → tgt_expr` via a named rule, preserving named invariants. Provenance includes both endpoint def_hashes + the rewrite_rule_id (scraped to provenance via PROMOTE-style hex extraction). Tier defaults to `WorkingTheory` (provisional until verified). |
| `EQUIV(expr_a, expr_b, equivalence_class_id, witness, cap, rationale) → Symbol` | **v2.3.** Mint a Symbol asserting `expr_a ≡ expr_b` under a named equivalence relation, supported by a typed witness (`proof_ref` / `finite_check` / `equiv_chain`). Provenance includes both endpoint def_hashes + witness's referenced hashes. Tier defaults to `WorkingTheory`. |

REWRITE and EQUIV mint regular Symbols (with version bumping per the kernel's standard pattern); their distinguishing structure lives in `def_blob`. No schema migration needed for these opcodes (see [migration 006](../../../sigma_kernel/migrations/006_add_rewrite_equiv_opcodes.sql) — explicit no-op documenting the design choice).

Macros (not separate opcodes): REFUTE = CLAIM + FALSIFY + PROMOTE on incumbent; AWAIT is implicit in FALSIFY (synchronous in v0.1); OBJECT = COMMIT with `objection_window` parameter (deferred — needs the multi-agent layer).

## State machine

```
⟨ I, σ, γ, μ ⟩
```

| Component | Holds |
|---|---|
| **I** | Instruction pointer (implicit in Python control flow for v0.1) |
| **σ** | Immutable substrate hypergraph (SQLite) |
| **γ** | Local epistemic registers (Python objects in the agent's process) |
| **μ** | Protocol / swarm state (empty in v0.1; placeholder for the multi-agent layer) |

Note: per the synthesis Round 18, `Φ` (search policy capability) is *not* in the machine state. It lives entirely in branch context when the FORK/USING construct lands. v0.1 has no FORK, so this is purely forward-compatibility.

## Storage

Dual-backend behind a unified adapter API:

| Backend | When | How |
|---|---|---|
| `"sqlite"` (default) | Zero-infra demos, per-script isolated state, outside readers cloning the repo | Local SQLite file via `sqlite3` |
| `"postgres"` | Cross-session symbol visibility, Mnemosyne-managed substrate, multi-process linearity | `prometheus_fire`'s `sigma` schema via `thesauros.prometheus_data.pool.get_fire()` |

Three tables, identical structure across both backends:

- `symbols(name, version, def_hash, def_blob, provenance, tier, created_at)` — PRIMARY KEY `(name, version)`; INDEX on `def_hash`. Append-only by UNIQUE constraint.
- `claims(id, target_name, hypothesis, evidence, kill_path, target_tier, status, verdict_*, caveats, precision_metadata)` — claim lifecycle persisted for replay/audit. `caveats` (migration 004) and `precision_metadata` (migration 005) are JSON-encoded TEXT fields with NULL defaults; legacy claims missing these fields continue to load.
- `capabilities(cap_id, cap_type, consumed)` — `spent_caps` semantics; double-spend rejected by reading `consumed=1` before update.

The kernel writes SQL with `?` placeholders and unqualified table names. The Postgres adapter rewrites `?` → `%s` and prepends `sigma.` at execute time. SQL stays single-source.

**Postgres provisioning:** Mnemosyne applies migrations in order: 001 (sigma schema) → 002 (bind_eval tables) → 003 (residual tables) → 004 (caveats column) → 005 (precision_metadata column) → 006 (REWRITE/EQUIV no-op; documents the design choice). All idempotent (`CREATE SCHEMA IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`).

**Failure modes** (Postgres backend, all caught at adapter `__init__`):
- DB unreachable → `ConnectionError` mentioning `~/.prometheus/db.toml`
- Schema not provisioned → `ConnectionError` naming the migration file
- User lacks privileges → `ConnectionError` listing the required GRANTs

**Future migration to harmonia Redis substrate:** each `(name, version)` row maps to `symbols:<NAME>:v<N>:def`; capabilities map to `symbols:caps:<cap_id>`. The kernel API is storage-agnostic by design — adding a third adapter is the same shape of work as the Postgres one.

## v2.3 typed substrate primitives

These primitives extend the kernel's epistemic ledger from "categorical kill outcome + flat method string" to "20-component KillVector + structured MethodSpec + 6-axis EvidenceField + scoped ExclusionCertificate + auto-triangulated INCONCLUSIVE upgrades + leak-resistant Learner emission." Each lives in a new module; none modifies existing kernel opcodes.

### KillVector v2 — 20 components

`prometheus_math/kill_vector.py`. 12 legacy components (out_of_band, reciprocity, irreducibility, 5 catalog entries, F1/F6/F9/F11) + 8 v2 components from Aporia Study 02 (mathematical-failure-mode literature):

- `relativizes` (Baker-Gill-Solovay 1975)
- `naturalizes` (Razborov-Rudich 1994)
- `local_global_gap` (Hasse / Brauer-Manin obstruction)
- `requires_unproven_conjecture` (RH / BSD / ABC etc.)
- `asymptotic_only` (vacuous for small inputs)
- `small_case_artifact` (works for small N, fails at scale)
- `asymmetric_effort` (one direction much harder than its converse)
- `interpretive_slack` (AM/Eurisko 1984; productivity attributable to generous parsing / human reading)

Each component carries `(triggered, margin, margin_unit, metadata, precision_dps, method, convergence_status, stability, stability_pass)`. Backwards-compat: legacy 12-component readers continue to work; `KillVector.to_legacy_kill_path()` derives the categorical view. Component overlap is allowed and meaningful (per substrate v2.3 §7.1 — schema decision option (b): independent flags + explicit MI reporting + auto-caveat at 3+ co-occurring via `KillVector.coalescing_failure_signature_caveat()`). See [`KILL_VECTOR_SPEC.md`](../../../prometheus_math/KILL_VECTOR_SPEC.md).

### CoordinateChart + CanonicalizationProtocol

`sigma_kernel/coordinate_chart.py`. Per substrate v2.3 §6.1 P0 + Aporia Study 17. The metric scaffolding without which `ExclusionCertificate.exclusion_distance` and `EvidenceField.exclusion_distance` cannot safely talk about distance, neighborhoods, or negative space. Per ChatGPT/Gemini convergence: no exclusion-distance queries unless object and certificate live in the same registered chart with a registered metric.

`CanonicalizationProtocol` is a typed interface (`impl`, `decidability_status ∈ {decidable / undecidable / conditional}`, `choice_dependencies`, `version`, optional `canonicalize` callable). Subsumes earlier `cohomological_functor` proposal as one registered impl. Module-level `ChartRegistry` (singleton `DEFAULT_REGISTRY`) maps `(domain, region_key) ↔ chart_id`. Lehmer chart `lehmer:deg14:pm5:palindromic` registers at import (`sigma_kernel/coordinate_charts/lehmer.py`) with L2 metric over canonicalized half-vector and `x → -x` reflection equivalence. Hot-swap-aware via integration with [`canonicalizer_observability`](../../../prometheus_math/canonicalizer_observability.py).

### MethodSpec

`sigma_kernel/method_spec.py`. Per substrate v2.3 §6.2 P3. Replaces flat `method: str` with structured `(engine, strategy, precision_dps, version, parameters, fallback_chain, independence_class, drift_channel)`.

`IndependenceClass` is a 13-value enum (mpmath_polynomial_factorization / sympy_symbolic_factorization / pari_number_field / sage_elliptic_curve / numpy_linear_algebra / mahler_lookup_catalog / lmfdb_catalog / oeis_catalog / literature_cross_check / perturbation_robustness / clustering_boundary / mpmath_numerical_root_finding / unknown). Two MethodSpecs in the same independence class are NOT independent for triangulation purposes.

`DriftChannel` (per Aporia Study 15) carries `(intensional_hash, behavioural_hash)`: code-derivation hash vs I/O-fingerprint hash. Two methods with same behavioural_hash but different intensional_hash are NOT a triangulation independence pair (cosmetic refactor doesn't add independence).

Backwards-compat: `MethodSpec.from_string("mpmath_factor_first")` parses legacy strings; `to_string()` round-trips for legacy consumers.

### Stability adapters

`prometheus_math/stability_adapters.py`. Per substrate v2.3 §6.2 P2. The previously-NaN `KillComponent.stability` field is now wired with per-falsifier-type adapters:

| Falsifier type | Stability adapter |
|---|---|
| `numeric_margin` | epsilon perturbation `10^-(precision_dps-2)` |
| `symbolic_factorization` | representation perturbation / normalization invariance |
| `catalog_lookup` | alias perturbation / source redundancy / lookup-path agreement |
| `graph_metric` | edge perturbation / sampling perturbation |
| `sequence_feature` | prefix truncation / suffix extension / modulus perturbation |
| `model_policy` | seed perturbation / replay perturbation |

Tiered `k`: `DIAGNOSTIC=10`, `CANDIDATE=50`, `PROMOTION_GRADE=200`. Output is structured `StabilityResult(stability_mean, stability_variance, perturbation_family, worst_case_flip_rate, k_used, falsifier_type)`, NOT a single scalar. Legacy `KillComponent.stability` scalar still readable; new `KillComponent.stability_pass` carries the structured result.

### EvidenceField (factual axes only) — split from PolicyField

`prometheus_math/evidence_field.py`. Per substrate v2.3 §6.2 P1. ChatGPT/Gemini convergent critique: evidence axes (factual) and policy axes (utility/prediction) must be type-separated; mixing them invites downstream models to confuse epistemic confidence with action preference.

Six factual axes:

- `distance_to_target` (metric) — derived from KillComponent.margin
- `battery_survival_depth` (ordinal — counts of categorical falsifiers; NOT continuous)
- `verification_depth` (vector — `(precision_dps, methods_used, convergence_summary, stability_aggregate)`; NEVER collapsed to scalar)
- `exclusion_distance` (metric — populated only when CoordinateChart + ExclusionCertificate both registered; NULL with `reason_unpopulated` otherwise; anti-fake-topology discipline)
- `assumption_load` (vector — `(catalog_dependence, numeric_dependence, heuristic_dependence, normalization_dependence, theorem_import_dependence)`; ChatGPT v2.3 addition)
- `computational_friction` (metric — `(elapsed_seconds, oracle_calls, peak_memory_mb)`; Gemini v2.3 addition; populated by Pre-Tier-0 0b telemetry)

Each axis carries `axis_type ∈ {metric, ordinal, categorical, estimate, vector}` per ChatGPT — no silent scalarization. `PolicyField` (separate object, owned by the navigator) carries `method_utility / operator_utility / expected_information_gain` — never colocated with EvidenceField.

`bridge_proximity` is **deferred** behind a future BridgeGraph primitive (reviewer convergence: not ready).

### ExclusionCertificate

`sigma_kernel/exclusion_certificate.py`. Per substrate v2.3 §6.3 P4. Renamed from "ExclusionZone" per ChatGPT — "certificate" implies a claim with scope, assumptions, and replayability; "zone" implied geometry the substrate doesn't yet have.

Schema includes `region_spec` (referencing a registered CoordinateChart), `exclusion_claim`, `certificate_type ∈ {exhaustive_enumeration / theorem_backed / catalog_complete_under_assumptions / probabilistic_null / failed_search_only}`, `strength ∈ {complete / bounded_complete / conditional / heuristic / diagnostic_only}`, `verifier_set` (with `independence_classes`), `replay` (code/data/seed/environment hashes), `triangulation_history` (per Aporia v2.3 hard rule), and `boundary` (adjacent regions + known escape hatches).

**Hard rule (Aporia 2026-05-05):** `strength = complete` requires non-empty `triangulation_history`. Future certificates without earned triangulation default to `bounded_complete` at most. Only `complete` and `bounded_complete` certificates feed `EvidenceField.exclusion_distance` (heuristic / failed-search certificates are logged but do not generate negative-space gradients).

The deg-14 ±5 palindromic Lehmer brute-force enumeration is the prototype: 97,435,855 polynomials enumerated; initial verdict INCONCLUSIVE with 17 borderline near-cyclotomic entries; strength `complete` earned via four triangulation paths (high-precision mpmath, symbolic factorization, factorization-aware catalog, Lehmer × Φ_n^k composite detection). Auto-registers at import (`sigma_kernel/exclusion_certificates/lehmer_deg14.py`).

### TriangulationProtocol

`sigma_kernel/triangulation_protocol.py`. Per substrate v2.3 §6.3 P6. Five registered method classes with epistemic role:

- **proof_bearing** — symbolic_derivation, exhaustive_enumeration, theorem_backed_reduction
- **numerical** — high_precision, interval_arithmetic, arbitrary_precision_replay
- **catalog** — catalog_lookup, independent_catalog_agreement, literature_cross_check
- **robustness** — perturbation, bootstrap, representation_invariance
- **exploratory** — clustering, boundary_layer_analysis (CANNOT certify per hard rule)

Upgrade rule: INCONCLUSIVE → LOCAL_LEMMA only if (a) ≥1 proof-bearing path verified, (b) ≥1 independent replay path verified with different `independence_class`, (c) no path contradicts. Clustering nominates boundary structure but cannot certify truth (per ChatGPT/Gemini convergence — three exploratory paths agreeing is correlated noise, not triangulation).

### NearMissCorpus (P5 full triangulated emission — Ergon Learner contract)

`prometheus_math/learner_corpus.py` + [`LEARNER_CORPUS_SPEC.md`](../../../prometheus_math/LEARNER_CORPUS_SPEC.md). Per substrate v2.3 §6.3 P5. Multi-view emission: `pre_falsification_view` (object features + canonical_form + raw_invariants + coordinate_chart_id; the Learner's primary training input) + `post_falsification_view` (KillVector / EvidenceField / triangulation_path / method_spec / caveats / exclusion_certificate_ref; gated for explanation/calibration only) + `provenance_view` (audit trail).

Anti-leakage discipline (load-bearing per ChatGPT + Gemini): pre and post views write to separate file paths; `LearnerCorpusLoader.load_post_view()` requires explicit `allow_post_falsification=True` keyword + `caller_id` + `purpose` (all keyword-only); every post-view load is logged to `_post_view_load_events.jsonl` for substrate-side leakage audit.

Anti-trivial-separability (Gemini): triples drawn from same coordinate-chart neighborhood. Both rank-loss `(positive, near_miss, negative)` and triplet-loss `(anchor, positive, hard_negative)` shapes emitted (per Ergon Q-E1 confirmation).

Canonical splits: `train` / `validation_same_region` / `validation_heldout_region` / `validation_heldout_method` / `validation_later_time` / `synthetic_null`. Synthetic-null pack via label-shuffle for the substrate's standing null-before-claim build gate.

`emit_from_substrate()` is the real (Day-13-shipped) emission; `stub_emit_from_legacy_ledger()` continues to exist for callers built against the Day-1-2 stub.

## What v0.1 demonstrates (preserved as historical anchor)

Three runnable scripts in `sigma_kernel/`:

1. **`demo.py`** — six-scenario walkthrough that exercises every opcode at least once. Demonstrates: CLEAR + PROMOTE; WARN + PROMOTE with bubble; BLOCK + GATE raise + PROMOTE refusal even if GATE skipped (defense-in-depth); double-spend rejected; overwrite rejected; ERRATA producing v2 while v1 stays immutable; recursive TRACE.

2. **`curvature_experiment.py`** — holonomy-defect probe across three real cartography data sources. Ingests `battery_runs.jsonl` (5-transform), `asymptotic_deviations.jsonl` (2-transform short-vs-long), `battery_sweep_v2.jsonl` (kill-test agreement matrix). Computes pairwise commutator defects per finding. Compares ranking to random / magnitude / n_transforms baselines. **First end-to-end measurement of representation-defect signal on actual Prometheus substrate findings.**

3. **`a149_obstruction.py`** — concrete forward-path use of the OBSTRUCTION_SHAPE candidate. Five OEIS sequences (A149074, A149081, A149082, A149089, A149090) emerged from the curvature experiment as the cross-source cluster (highest defect in Source B AND unanimous-killed in Source C). All five are 5-step lattice walks confined to N³ with structural signature `{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}`. The signature predicts unanimous-kill on the F1+F6+F9+F11 battery at **5/5 = 100% within the A149* family vs 1/54 = 1.9% on non-matches** (54x predictive lift). The script promotes `boundary_dominated_octant_walk_obstruction@v1` through the full kernel discipline (CLAIM → FALSIFY → GATE → PROMOTE).

## Symbol candidates surfaced

Three new entries in [`../symbols/CANDIDATES.md`](../symbols/CANDIDATES.md) (Tier 3):

| Symbol | Anchor evidence | Forward-path use |
|---|---|---|
| `OBSTRUCTION_SHAPE` | Three anchors; one promoted-and-validated through the kernel (`boundary_dominated_octant_walk_obstruction@v1`), two retrospective | ✓ Live (a149_obstruction.py) |
| `ORACLE_PROFILE` | Two anchors: `omega_oracle.py@v1` (kernel) + F20 implicit oracle (cartography battery) | Pending — needs a multi-oracle scenario |
| `NULL_MODEL_FAMILY` | Three anchors: F1+F13+F14 kill-tests, F20 by_transform set, NULL_BSWCD@v2 stratifier instances | Pending — needs curvature_experiment refactored to consume typed family |

`OBSTRUCTION_SHAPE` is the closest to v1 promotion — has three anchors and live forward-path use through the kernel. With one cross-family validation (e.g., on A148xxx octant walks) it'd hit the joint-promotion threshold.

## Where this sits relative to the long synthesis

The 25-round design synthesis (`sigma_council_synthesis.md`) explored a much richer architecture:

- 5-to-7-layer stack (Constitution / Ecology / ISA / Swarm / Substrate / Δ₁ / Δ₂)
- 13-to-14-opcode RISC including DISTILL with three outputs (O, Φ, Δ) and CONSTRAIN
- Triadic ecology (Constructors / Breakers / Translators) with Lotka-Volterra dynamics
- Theory-space curvature (`χ`-field) and PROMOTE_THEORY with triple-witness (compression + transport + curvature)
- Ten soundness theorems (I-X) plus candidates XI-XIV

Most of that is **conditional** on the curvature experiment producing predictive signal that beats baselines (Round 25 specified this; Rounds 23/24 framed it as the falsifiability bar). The kernel v0.1 is structured so the conditional layers can grow on top: every additional opcode is one method per opcode plus one row of demo. v2.3 added two opcodes (REWRITE + EQUIV) following exactly that pattern. Adding swarm coordination is sharing a SQLite path across processes (the linear-capability discipline already holds across processes via `spent_caps`).

A v3.0 design pass is queued (Watch-1 in [`pivot/external_review_watchlist_2026-05-05.md`](../../../pivot/external_review_watchlist_2026-05-05.md)) to consider a hybrid kernel ↔ Calculus-of-Constructions translation layer for the substrate's epistemic content. The feasibility doc at [`pivot/sigma_kernel_logical_foundation_feasibility_2026-05-06.md`](../../../pivot/sigma_kernel_logical_foundation_feasibility_2026-05-06.md) found PARTIAL subsumption: 7 of the 11 v2.3 constructs (RESOLVE / CLAIM / FALSIFY / GATE / TRACE / REWRITE / EQUIV) subsume cleanly into CoC + native falsification records; ERRATA / BIND / EVAL resist (defeasible reasoning, host-callable hash, cost contract). v2.2 imperative VM ships unchanged; v3.0 may adopt hybrid.

The architecture-from-Round-19 line worth keeping:

> *Σ-VM is a microkernel for mathematical civilization. Registers hold pointers, hashes, and obstructions. The math happens in user space.*

v2.3 expands the microkernel surface from 7 opcodes to 9 and adds the typed primitives (CoordinateChart, MethodSpec, EvidenceField, ExclusionCertificate, TriangulationProtocol, NearMissCorpus) the user-space math relies on. The "user space" math currently runs in `omega_oracle.py` as a deterministic stub plus six cross-domain envs (BSD ranks, modular forms, knot trace fields, genus-2 curves, OEIS sleeping-beauty sequences, mock theta functions) that emit KillVector v2 + EvidenceField via Tier 3 rollout. Real Ω invocations will shell out to Python / Sage / Lean sandboxes that return signed result blobs.

## Contract-change window 2026-05-07 — locked changes

The 2026-05-07 contract-change window (`aporia/meta/pressure_appliers/CONTRACT_CHANGE_WINDOW_TECHNE_2026-05-07.md`) authorized a small, focused batch of contract changes after the substrate-tester surfaced silent-degradation patterns that the regular contract-locked loop could not address. The new locked contracts:

### Contract change #1 — `prometheus_math.learner_corpus.get_raw_invariant_keys` (ST003 + T018)

Was: returned `("__unregistered__",)` sentinel tuple on unregistered domain.
Now: raises `KeyError(f"unregistered domain {domain!r}; registered: ...")`. Substrate discipline is loud-fail-on-typo; silent-sentinel masked typo'd domain inputs that propagated downstream as all-None `raw_invariants` in NearMissCorpus emission.

Backwards-compat note: callers wanting Optional-style behavior can wrap with `RAW_INVARIANTS_PER_DOMAIN.get(domain)` directly (the registry is a public module attribute).

### Contract change #2 — `sigma_kernel.triangulation_protocol.method_class_for_independence_class` (T018 sister-of-ST003)

Was: returned `MethodClass.EXPLORATORY` for any unregistered IC string.
Now: raises `KeyError(f"unregistered independence_class {key!r}; registered: ...")`. `INDEPENDENCE_TO_METHOD_CLASS` now contains all 13 `IndependenceClass` enum values explicitly (including `unknown` → `EXPLORATORY` as the explicit cannot-certify opt-in). Truly unregistered method strings raise; the `UNKNOWN` enum value is the explicit-typed way to opt into cannot-certify semantics.

Migration: 2 existing tests updated; `evaluate()` and other internal callers continue to work because they were using registered IC values.

### Contract change #3 — `sigma_kernel.exclusion_certificate.CertificateCollisionError` (T020)

Added: a new exception class `CertificateCollisionError(CertificateRegistrationError)`. The registry's duplicate-id detection (already in place) now raises the more-specific subclass, allowing callers to distinguish "duplicate certificate_id" from the umbrella "registration error" cases (which also includes "missing chart"). Existing callers catching `CertificateRegistrationError` continue to work unchanged (subclass relationship).

### Documented-as-safe — `CanonicalizationProtocol.decidability_status` defaults (T021)

Audit confirmed: field is required; `__post_init__` raises `ValueError` on invalid values; missing field raises `TypeError` at construction. No silent default. No hardening needed. Audit doc at `prometheus_math/DECIDABILITY_STATUS_AUDIT.md`.

### Audit-deferred — KillVector v2 multi-precision (T029)

`KillComponent.margin` is `Optional[float]` (IEEE 754 double). Sufficient for current discovery-pipeline domains (Lehmer, BSD, modular forms in their typical ranges); INSUFFICIENT for the HARD-4 hunt regions (Maass forms with 50+ digit Hecke eigenvalues, p-adic L-function values with native O(p^N) precision, motivic periods with conjectural high-precision identities). Audit doc at `prometheus_math/MULTIPRECISION_AUDIT.md` recommends Option B (additive `margin_high_precision` sister field) for a future contract-change window. No code change in this window.

### Tier 3 — capability-gap encodings (operator-portability primitive + 6 design docs)

Per HARD-5 (refinement, 2026-04-26): "the discovery worth promoting is the operator's signature pattern across regions, not the bridge story we tell about it." Tier 3 of this contract-change window ships substrate-grade encodings for under-explored regions, all anchored on (object, operator-output) pairs and operator-derived structural partitions — discipline labels live in `notes` fields, NEVER in chart coordinates.

**T030 — Operator-portability primitive (SHIPPED — `sigma_kernel/operator_portability.py`).** New module + tests. Defines `OperatorPortabilityCertificate(operator_id, source_chart_id, target_chart_id, transfer_method, evidence_pre, evidence_post, equivalence_relation, verdict, rationale, replay)` with content-addressed `certificate_id` and a registry mirroring the ExclusionCertificate pattern. The substrate now has a typed encoding for "operator X transports from region A to region B with evidence Y." Worked example: Mahler-measure operator across the deg14 ±5 (Day-5) and deg12 ±5 (Fire #8 W3.2 fixture) Lehmer charts. Design doc: `harmonia/memory/architecture/operator_portability_GAP.md`. 26 tests pass.

**T023 — Maass form Hecke eigenvalue (SHIPPED — `prometheus_math/encodings/maass_form_hecke.py`).** New module via the more-general `OperatorOutputSequence` primitive. The substrate-grade primitive for any "object that produces a sequence of values under a parameterized operator" — Maass forms are one instance (operator = Hecke at prime p; index = primes); modular form q-expansion coefficients and L-function values at integer arguments are sister instances. String-encoded high-precision values (mpmath.mpf serialization) sidestep the float-precision contract gap from T029. Design doc: `prometheus_math/encodings/maass_form_hecke_GAP.md`. 12 tests pass.

**T024-T028 — design docs only (deferred to next contract-change window):**
- `prometheus_math/encodings/tropical_curve_GAP.md` (T024) — `LatticePolytope` + `ValuationTag` primitives for tropical curves
- `prometheus_math/encodings/padic_l_function_GAP.md` (T025) — `PadicValue` + `PadicLFunctionValue` (depends on T029 multi-precision)
- `prometheus_math/encodings/galois_cohomology_GAP.md` (T026) — `Cocycle` + `GroupActionContext`
- `prometheus_math/encodings/large_cardinal_consistency_GAP.md` (T027) — `FormalTheory` + `ConsistencyRelation`
- `prometheus_math/encodings/motivic_period_GAP.md` (T028) — `TranscendentalValue` + `ConjecturalIdentity` (depends on T029 multi-precision)

All 5 deferred designs follow the same pattern: substrate-grade primitive name, dataclass shape, CoordinateChart placement, worked encoding example, deferred-implementation note. Implementation can ship under a future contract-change window without breaking the v2.3 contracts.

---

## Open frontiers (next sessions)

1. **A149 + OBSTRUCTION_SHAPE chart registration** — pending Charon coordination per joint sprint commitment T11. Lehmer chart is the v2.3 prototype; the 5 cross-domain envs use `provisional:<domain>` chart_ids until charts land.
2. **Cross-family validation of A149* obstruction.** Run `a149_obstruction.py` against A148xxx octant walks. If the structural signature transfers, the obstruction generalizes; if not, it's family-specific (still useful as a typed substrate symbol, but narrower).
3. **Resolve the A149499 anti-anchor** (`neg_x=3` case unanimously killed despite not matching strict signature). Sister-obstruction draft or strict-signature refinement.
4. **Cartography Source A scaling.** Currently only 3 findings have `by_transform` data. The script that produces them is `cartography/shared/scripts/battery_v2.py`. Running it over more findings would generate the corpus needed for Round 25's full experiment design.
5. **Redis migration.** The kernel API is storage-agnostic; swapping SQLite → Redis is mechanical. Required for cross-session symbol visibility in the harmonia substrate.
6. **Promotion of OBSTRUCTION_SHAPE@v1 to harmonia.** Needs agora SYMBOL_PROPOSED post + Harmonia-session second-reference. Drafts ready in [`../symbols/agora_drafts_20260429.md`](../symbols/agora_drafts_20260429.md).
7. **KillEmbedding implementation** (Day 13-17 of joint sprint). Schema seed at [`pivot/killembedding_design_seed_2026-05-06.md`](../../../pivot/killembedding_design_seed_2026-05-06.md); cross-review window open Days 5-12; substrate-side prep checklist at [`pivot/killembedding_implementation_prep_2026-05-06.md`](../../../pivot/killembedding_implementation_prep_2026-05-06.md). Trains a low-dimensional embedding from KillVector v2 + MethodSpec + EvidenceField, with commit-blocking synthetic-null guard. Adoption gates on the synthetic-null result.
8. **Watch-1 v3.0 design pass** — hybrid kernel ↔ CoC translation per the feasibility doc.

## What this is NOT

- Not a replacement for the harmonia substrate. It's a *kernel*; harmonia is the substrate above the kernel.
- Not a production system. The Ω oracle is a deterministic toy. Real evaluators must supply their own subprocesses.
- Not a multi-agent system. v2.3 is single-process; cross-process linearity exists for capabilities but the swarm-coordination opcodes (FORK/JOIN/ADJUDICATE/OBJECT) are deferred.
- Not a validation of the long synthesis's most ambitious claims (theory-space curvature, paradigm-shift optimization, etc.). Those depend on experimental work that v2.3 enables but does not run.
- **Not a navigable global metric topology.** Per ChatGPT/Gemini convergence: the substrate provides typed local coordinate charts (Lehmer registered) over falsification evidence; metric queries fail loudly when no chart is registered. Anti-fake-topology is the v2.3 architectural lock-in.

## Reading order for new agents joining this work

1. This file (`sigma_kernel.md`) — what is, how to use, where it sits.
2. [`../../sigma_kernel/README.md`](../../../sigma_kernel/README.md) — clone-and-run instructions.
3. [`../symbols/CANDIDATES.md`](../symbols/CANDIDATES.md) — the three new symbol candidates surfaced by the kernel work, with full anchor evidence.
4. [`pivot/substrate_v2_proposal_2026-05-05.md`](../../../pivot/substrate_v2_proposal_2026-05-05.md) — v2.3 design rationale (8 primitives + Pre-Tier-0 + four tiers + architectural lock-ins).
5. [`pivot/techne_ergon_joint_sprint_2026-05-05.md`](../../../pivot/techne_ergon_joint_sprint_2026-05-05.md) — sister-project coordination doc for the v2.3 sprint + KillEmbedding cross-review.
6. [`sigma_council_synthesis.md`](sigma_council_synthesis.md) — full 25-round design history. Long. Read only if you need the architectural rationale.
