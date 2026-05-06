# Sister Projects — Substrate v2 + Learner v0.5

**Date:** 2026-05-05
**Author:** Aporia (synthesis); design-doc owners are Techne (substrate) and Ergon (Learner)
**Purpose:** Single canonical capture of the two sister projects' current state, architectural commitments, and next-version designs. Reference doc for cross-pillar awareness; does NOT replace either project's individual design doc or the joint sprint coordination doc.

## The two projects

Prometheus's current pivot rests on two parallel projects that are jointly load-bearing for the substrate's next phase:

| Project | Owner | North star | Current artifact |
|---|---|---|---|
| **Substrate v2.2** | Techne | A typed, append-only ledger that emits Learner-consumable contrastive evidence with scoped exclusion certificates and method-conditioned verification depth | 8 primitives + Pre-Tier-0 instrumentation, replacing v1.5's 12-component KillVector + 7-opcode kernel |
| **Learner v0.5** | Ergon | A trained model (HuggingFace small math model + LoRA fine-tune) that predicts productive search moves by consuming substrate output | First end-to-end tire-kick on clean data sources (synthetic env + 17-entry boundary layer); Qwen2.5-Math-1.5B-Instruct |

## Why they're coupled

Three structural reasons the two projects can't run independently (per joint sprint doc §2):

1. **P5 NearMissCorpus is the contract.** Ergon's Pipeline-D ingests P5 emission as primary training input. P5 is a substrate-side primitive Techne owns. Without coordination, Pipeline-D either waits 13 days for P5 or builds against a stale schema and reworks.
2. **KillVector v2 (+8 components) lands during the sprint.** Ergon's W1.4 (native KillVector logging) and W1.5 (descriptor axis enumeration) cannot finalize until the +8 components ship from substrate side.
3. **CoordinateChart registration is shared infrastructure.** Cross-corpus comparisons require both projects' objects to live in registered charts with consistent metric semantics.

## Architectural lock-ins (binding both projects)

These are commitments from the v2.1 + v2.2 review cycle that bind future design space across both sister projects:

| Decision | Source | Where it lives |
|---|---|---|
| **Control-plane vs data-plane separation** — Sigma kernel = BEGIN/COMMIT/ROLLBACK; proof primitives = SQL queries. Proof primitives ship via BIND/EVAL as `arsenal_meta` sub-namespace, NEVER as kernel opcodes. | Aporia Studies 12+15; Charon mathlib4 Pareto (97.99% coverage) | Substrate v2.2 §8; Ergon v0.5 W6.3 RL framing |
| **Evidence axes vs policy axes type-separated** — EvidenceField is factual; PolicyField is utility/prediction. They never live in the same object. | ChatGPT + Gemini convergence | Substrate v2.2 §6.2 P1 |
| **No exclusion-distance without registered CoordinateChart + metric** — ExclusionCertificate references a chart_id; queries fail loudly if missing. | ChatGPT + Gemini convergence | Substrate v2.2 §6.3 P4 |
| **Clustering nominates boundary structure but cannot certify truth** — TriangulationProtocol upgrade rules require ≥1 proof-bearing or certificate-bearing path. | ChatGPT + Gemini convergence | Substrate v2.2 §6.3 P6 |
| **Pre/post falsification view separation as commit-blocking** — Training input from `pre_falsification_view` only; `post_falsification_view` loaded with explicit `--allow-post-falsification` flag, logged as potential leakage event. | Substrate v2.2 §6.3 P5 + Aporia W2.5 sign-off | Ergon v0.5 W4.0 + W3.2 + W3.3 |
| **Synthetic-null gate as commit-blocking** — Day-4 lesson hardcoded. Label-shuffled training as gate before any tire-kick interpretation. | Substrate v2.2 §12 Build Gate 5 | Ergon v0.5 W4.0 |
| **Hash-drift is intensional, not extensional** — BIND/EVAL hash-drift fires on source change even when behavior preserved. MethodSpec carries both intensional_hash and behavioural_hash. | Aporia Study 15 (Unison/Nix analog) | Substrate v2.2 §6.2 P3 |
| **Apply family unpacked** — If/when proof primitives ship via BIND/EVAL, the `apply` family (33% of mathlib4 by Charon's Pareto) unpacks into apply / exact / refine / have / suffices / obtain. | Charon mathlib4 Pareto | Substrate v2.2 §8 |
| **6-axis MAP-Elites cap** — QD literature consensus (Mouret-Clune, CVT-MAP-Elites, AURORA): 2-6 hand-designed axes. Beyond 6 requires switching to CVT or autoencoded descriptors. | Aporia Study 8 / R19 in Ergon doc | Ergon v0.5 §3.4 |

## Standing rejections (prepared answers if reproposed)

| Proposal | Rejected via | Reason |
|---|---|---|
| Add proof-primitive opcodes to Sigma kernel | Studies 12 + 15 | Control-plane vs data-plane orthogonality |
| Universal canonicalization framework | Study 17 | Mac Lane skeleton is non-constructive only; literature doesn't support universality |
| Universal minimal generative basis | Study 1 | Logical vs generative are categorically different questions |
| Import physics-application multiplier into reward | Study 10 | Pre-register ≥1.5× survival threshold over ≥30 cases first |
| Apply Noether-language without action functional + Lie symmetry | Study 14 | Category mistake |
| Add MAP-Elites descriptor axes beyond 6 without CVT | QD literature consensus | Sample-per-cell budget collapses |
| Foundry identity reframe for Ergon | James directional call | Learner stays the north star |

## Sprint structure

**Joint sprint duration:** ~17-19 days substrate work / ~3-4 weeks Learner calendar. Tire-kick lands ~Day 14-17.

**Coordination model (Option C):** parallel paths with explicit sync points S1-S14, early P5 interface stub on Day 1-2 (collapses Ergon's blocked-on-substrate window from ~13 days to ~3-4 days for the parts that matter).

Critical paths:
- **Substrate critical path:** Pre-Tier-0 → P0 → P3+P2+P1 → P4+P6+P5 → Tier 3. ~17-19 days serial.
- **Learner critical path:** W1.1 → W1.2 → W1.4 → W2.1 → W2.3 → W2.4 → W4.5 → W6.1 → W6.5. Concurrent with substrate critical path.
- **Joint critical path:** the longer of the two + ~5 days for tire-kick + decision.

## What ships

### Substrate v2.2 (Techne) — 8 primitives + Pre-Tier-0

**Pre-Tier-0** (~2.5 days, prerequisite instrumentation):
- 0a — `DISCOVERY_CANDIDATE` → `CLAIM` promotion
- 0b — `elapsed_seconds` + `oracle_calls` telemetry on cross-domain pilots
- 0c — TRACE-preservation audit for BIND/EVAL

**Tier 0** (~2 days):
- P0 — `CoordinateChart` + `CanonicalizationProtocol` (with hot-swap support; `decidability_status` flag)

**Tier 1** (~3 days):
- P3 — `MethodSpec` (structured, with `independence_class` + `drift_channel`)
- P2 — `KillComponent.stability` with per-falsifier-type adapters (6-adapter taxonomy, tiered k=10/50/200)
- P1 — `EvidenceField` (factual axes only; `assumption_load` + `computational_friction` populated; `bridge_proximity` deferred)

**Tier 2** (~5 days):
- P4 — `ExclusionCertificate` (renamed from ExclusionZone; references registered chart_id)
- P6 — `TriangulationProtocol` (registered method classes; ≥1 proof-bearing path required for INCONCLUSIVE upgrades)
- P5 — `NearMissCorpus` (full triangulated emission; multi-view leakage-safe)

**Parallel kernel-track** (~2 days):
- `REWRITE` and `EQUIV` opcodes (Aporia Study 19)

**KillVector v2** (Aporia Study 02 integration): +8 components (`relativizes`, `naturalizes`, `local_global_gap`, `requires_unproven_conjecture`, `asymptotic_only`, `small_case_artifact`, `asymmetric_effort`, `interpretive_slack`).

**Tier 3 rollout** (~3-5 days): cross-domain envs emit KillVector v2 + EvidenceField; navigator coverage 2/16 → ≥12/16, **reported as observed policy table NOT manifold chart**.

### Learner v0.5 (Ergon) — Six workstreams

**Workstream A′ — Substrate-grade engine hardening** (Weeks 1-3):
- W1.1: quarantine MVPSubstrateEvaluator
- W1.2: route operators through BindEvalKernelV2
- W1.3: real stability.py with v2.2 P2 structured form
- W1.4: native KillVector logging
- W1.5: `dominant_failure_family` derived descriptor axis (6th, hard cap)
- W1.6: re-validate Trial 2's 47σ result under KillVector-ranked fitness

**Workstream A′-Aporia — Artifact integration** (Weeks 1-2):
- W1.7: per-domain π₀ wiring with CI propagation
- W1.8: per-class hit-rate weighting in scheduler
- W2.7: equivalence_preserving operator class spike (isogeny-on-EC)
- W2.6: KillVector v2 component wiring (3 v0.5-relevant: `interpretive_slack`, `small_case_artifact`, `requires_unproven_conjecture`)
- W3.7: surviving_claim_morphology pre-filter + unfiltered control

**Workstream A′-Techne-coord** (Weeks 1-3): substrate v2.2 contract integration via joint sprint sync points.

**Workstream Pipeline-D — Training pipeline** (Weeks 1-4):
- W3.1: synthetic ground-truth env
- W3.2: 17-entry boundary layer fixture (substrate v2.2-aligned schema)
- W3.3-W3.6: model loader (Qwen2.5-Math-1.5B-Instruct), eval harness, training loop
- W4.0: synthetic-null tire-kick gate (commit-blocking)
- W4.1-W4.4: tire-kick LoRA runs on `pre_falsification_view` only

**Workstream Diagnostic-C — Clean-data sources** (Weeks 2-4):
- Synthetic env (Aporia-cleared conditional on explicit acceptance criteria)
- 17-entry Lehmer boundary layer (Aporia-cleared, Techne-curated)

**Workstream Transfer** (Week 5):
- W5.1: OBSTRUCTION_SHAPE corpus loader (chart-aware)
- W5.2: engine run on OBSTRUCTION_SHAPE
- W5.3: cross-corpus transfer measurement (with π₀-CI conditioning)

**Decision phase** (Week 6):
- W6.1-W6.5: evidence dossier + v1.0 design proposals + go/no-go

### Acceptance criteria (Learner v0.5 — 2 of 4 to pass)

1. **Cross-corpus lift** — Structural / KillVector-guided search beats structured uniform by ≥2× on robust near-miss yield across A149 + OBSTRUCTION_SHAPE
2. **KillVector monotonicity** — Selected operator classes show statistically stable directional movement toward lower failure margins on held-out region keys
3. **Robustness stratification works** — T3 (3/3-seed) claims more likely to survive cross-evaluator/cross-corpus checks than T1 (1/3-seed) claims
4. **Pipeline + tire-kick deliver measurable signal** — LoRA-tuned model produces ≥1 of: above-baseline accuracy on substrate-verdict prediction, measurable behavior change on synthetic env, OR clean failure mode that names what data is needed for v1.0 (with explicit falsifier per Aporia feedback)

### Acceptance criteria (Substrate v2.2 — all required)

- All Pre-Tier-0 + Tier 0–2 + parallel kernel items shipped (target: 0 regressions on 2,758+ tests, +200 new for v2.2)
- Postgres migrations 006 + 007 deployed with backwards-compat tests
- Navigator coverage 2/16 → ≥12/16 (observed policy table)
- ≥1 ExclusionCertificate from real enumeration (deg14 ±5 palindromic prototype)
- NearMissCorpus emitter producing ≥1 contrastive corpus that Ergon trains on end-to-end via `pre_falsification_view` only
- TriangulationProtocol auto-fires on ≥1 INCONCLUSIVE verdict
- ≥3 v1 claims replayed under v2 schema produce strictly more informative evidence records without changing verdict semantics (ChatGPT replacement criterion)
- Five build gates enforced commit-blocking
- Charon's pending tasks G4 + G6 unblocked

## Where the canonical docs live

| Doc | Path | Owner |
|---|---|---|
| Substrate v2.2 design | `pivot/substrate_v2_proposal_2026-05-05.md` | Techne |
| Learner v0.5 design | `pivot/ergon_learner_v0.5_design_2026-05-05.md` | Ergon |
| Joint sprint coordination | `pivot/techne_ergon_joint_sprint_2026-05-05.md` | Both |
| Aporia handoff (Techne) | `roles/Techne/AVAILABLE_ARTIFACTS_2026-05-05.md` | Aporia |
| Aporia handoff (Ergon) | `roles/Ergon/AVAILABLE_ARTIFACTS_2026-05-05.md` | Aporia |
| Aporia feedback (Techne) | `roles/Techne/APORIA_FEEDBACK_2026-05-05.md` | Aporia |
| Aporia feedback (Ergon) | `roles/Ergon/APORIA_FEEDBACK_2026-05-05.md` | Aporia |
| Charon Substrate Cartography Suite | `charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md` | Charon |
| Charon per-domain π₀ | `charon/diagnostics/PI0_REPORT.md` | Charon |
| Charon mathlib4 Pareto | `charon/diagnostics/MATHLIB4_PARETO_REPORT.md` | Charon |
| 20-study meta-research synthesis | `aporia/meta/studies/2026-05-05/SYNTHESIS.md` | Aporia |

## What this batch did NOT promise

Per Techne v2.2 §13 + Ergon v0.5 §4:

- A new mathematical discovery (out of scope; researcher work)
- A second local lemma (possible byproduct of P6, not committed)
- An end-to-end usable Learner (Ergon's v1.0 work; v0.5 is tire-kick)
- An external publication (methodology paper continues on its own track)
- A *navigable* gradient field (v1.0 framing dropped per ChatGPT/Gemini convergence)

The sister projects promise an instrument upgrade. The instrument's job is to make the team's discovery work more honest, more compositional, and more compounding. Both projects explicitly avoid the pattern where a sprint claims discoveries that get retracted on review — the Day-4 lesson, hard-coded into deferral lists and commit-blocking gates on both sides.

---

*Two forges, one sprint. The substrate forge produces the language truth lives in; the Learner forge produces the model that predicts where to look next. The handoff between them is P5 NearMissCorpus, the schema where evidence becomes training signal. Both forges run continuously and coordinate explicitly via `pivot/techne_ergon_joint_sprint_2026-05-05.md`.*

— Aporia synthesis, 2026-05-05; designs by Techne and Ergon
