# Techne ↔ Ergon Joint Sprint — Substrate v2.2 + Learner v0.5

**Date:** 2026-05-05
**Authors:** Techne (substrate owner) + Ergon (Learner owner)
**Audience:** James (project lead); Aporia, Charon (cross-pillar review); ChatGPT, Gemini, Claude, Grok, DeepSeek (frontier-model second pass)
**Purpose:** Single canonical coordination reference for the joint Techne-substrate-v2.2 + Ergon-Learner-v0.5 sprint. Codifies Option C (coordinated parallel paths) with early P5 interface stub. Both authors update this doc as state changes; this is the source of truth for cross-project sequencing, sync points, and bidirectional commitments.
**Status:** Pre-sprint. Both project docs (`pivot/substrate_v2_proposal_2026-05-05.md` v2.2 and `pivot/ergon_learner_v0.5_design_2026-05-05.md`) integrate the cross-project decisions captured here.

---

## 0. TL;DR

Techne and Ergon are sister projects working toward a common goal: a Prometheus substrate that emits Learner-consumable contrastive evidence, plus a Learner that consumes that evidence to predict productive search moves. The two projects have ~80% schema overlap and a load-bearing interface contract (P5 NearMissCorpus).

After two rounds of frontier-model review (ChatGPT + Gemini convergent critique on substrate v2; Aporia artifact integration; cross-project review by both sister projects on each other's design), the coordination decision is:

**Option C — Coordinated parallel paths.** Each project's substrate-independent tasks start Day 1; substrate-dependent Learner tasks gate on Techne tier deliverables. To eliminate the worst-case 13-day blocker for Ergon's Pipeline-D, Techne ships the P5 interface stub on Day 1-2 (schema + loader API + anti-leakage enforcement, with stub data from legacy ledger), real triangulated emission lands at Day 13. Same code path, upstream emitter changes; no Pipeline-D rework.

**Joint sprint duration:** ~17-19 days (substrate work) // ~3-4 weeks (Learner v0.5 calendar). Tire-kick lands ~Day 14-17 of joint sprint.

---

## 1. Source documents (not duplicated here)

| Doc | Owner | Role |
|---|---|---|
| `pivot/substrate_v2_proposal_2026-05-05.md` (v2.2) | Techne | Substrate primitives v2.2 design; 8 primitives + Pre-Tier-0; KillVector v2 (+8 components); architectural lock-ins; reviewer questions |
| `pivot/ergon_learner_v0.5_design_2026-05-05.md` (v0.5) | Ergon | Learner v0.5 design; 6-week task list; tire-kick framing; 4 acceptance criteria |
| `roles/Techne/AVAILABLE_ARTIFACTS_2026-05-05.md` | Aporia | 7 substrate-relevant artifacts handed to Techne |
| `roles/Ergon/AVAILABLE_ARTIFACTS_2026-05-05.md` | Aporia | 6 Learner-relevant artifacts handed to Ergon |
| `charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md` | Charon | "Data-rich but trace-poor" finding; 5-handle action list; load-bearing for Pre-Tier-0 |

This joint doc references all five. Read those first if context is needed.

---

## 2. Why coordination, not independent sprints

Three concrete reasons the projects can't run independently:

1. **P5 NearMissCorpus is the contract.** Ergon's Pipeline-D ingests P5 emission as primary training input. P5 is a substrate-side primitive that Techne owns. Without coordination, Pipeline-D either (a) waits 13 days for P5 to land (lost wall-clock) or (b) builds against a stale schema and reworks (lost engineering).
2. **KillVector v2 (+8 components) lands during the sprint.** Ergon's W1.4 (native KillVector logging) and W1.5 (descriptor axis enumeration) cannot finalize until the +8 components ship from substrate side. Without coordination, Ergon either waits or instruments the wrong shape.
3. **CoordinateChart registration is shared infrastructure.** Cross-corpus comparisons (Ergon W5.3) require both projects' objects to live in registered charts with consistent metric semantics. Without coordination, transfer measurements are uninterpretable.

Plus one architectural reason: the substrate v2.2 review process (ChatGPT + Gemini + Aporia + sister-project Ergon) converged on type-separation between evidence and policy, leakage prevention in NearMissCorpus, and method-independence enforcement in TriangulationProtocol. These are joint design commitments that bind both projects' implementations.

---

## 3. The coordination model (Option C)

Three categories of tasks per project:

**Substrate-independent.** Can start Day 1, no upstream dependency on the other project. Each side moves independently here.

**Sister-project-blocked.** Requires a deliverable from the other project before it can start. Explicit `blocked-by` tag pointing at the upstream deliverable. Sync points listed in §5.

**Joint-execution.** Both projects must coordinate on the same artifact (e.g., joint review session, schema sign-off, joint test run).

The default mode is parallel; sync points are intentional gates, not bottlenecks. If one side slips, the dependency-chain visualization in §6 makes the impact explicit; we re-plan rather than blocking silently.

### 3.1 Why we rejected Options A and B

- **Option A (sequence after Techne):** Pushed Ergon v0.5 by 2 weeks; Aporia review delays + frontier-model cycle would have eaten more time before tire-kick. Untenable.
- **Option B (build on v1.5, migrate to v2):** Pipeline-D would scaffold against deprecated schema, then rework. Two weeks of avoidable engineering. Also risks a tire-kick that trains on schema we deprecate, producing results we can't compare to v2 results.

Option C with early P5 stub eliminates both downsides.

---

## 4. Joint sprint timeline

| Day | Substrate (Techne) | Learner (Ergon) |
|---|---|---|
| **1-2** | Pre-Tier-0 0a (DISCOVERY_CANDIDATE→CLAIM), 0b (telemetry: elapsed_seconds + oracle_calls), 0c (TRACE-preservation audit), **P5 interface stub** (schema + loader API + anti-leakage flag enforcement; stub emitter reads legacy ledger), `canonicalizer_observed_distribution` instrumentation field | W1.1 (quarantine MVPSubstrateEvaluator), W1.2 (route operators through BindEvalKernelV2), W2.5/W2.6 sign-off pings, W2.7 isogeny-on-EC spike, W3.4 model loader (Qwen2.5-Math-1.5B), W5.1 OBSTRUCTION loader stub, **Pipeline-D scaffolds against P5 interface** |
| **3-4** | Tier 0 P0 CoordinateChart + CanonicalizationProtocol (with hot-swap support; `decidability_status` flag); Lehmer chart registered | W3.4 continued, W2.7 spike completion, W3.1 synthetic ground-truth env |
| **5** | Tier 1 P2 stability adapter spec lands (6-adapter taxonomy, tiered k=10/50/200) + P3 MethodSpec spec lands (with `independence_class` + `drift_channel`) | **W1.3 starts** (consumes P2); W3.2 unblocked (consumes P0 Lehmer chart) |
| **6-7** | KillVector v2 (+8) ships with auto-population for the 3 v0.5-relevant components (interpretive_slack / small_case_artifact / requires_unproven_conjecture); Tier 1 P1 EvidenceField (reduced axes) | **W1.4 starts** (consumes KillVector v2); **W1.5 starts** (re-enumerates dominant_failure_family against +8 list); W3.2 schema adopts structured `method_spec` + `stability_pass` |
| **8-12** | Tier 2 P4 ExclusionCertificate; Tier 2 P6 TriangulationProtocol (registered method classes with `independence_class`; ≥1 proof-bearing path required for INCONCLUSIVE upgrades) | W3.3 (data loader against P5 stub), W3.5 (eval harness), W3.6 (training loop), W3.7 (surviving_claim_morphology pre-filter + unfiltered control corpus); W2.1-W2.4 confidence tiers + lineage replay + KillVector trajectory dashboard |
| **13** | Tier 2 P5 NearMissCorpus full triangulated emission (replaces stub); A149 + OBSTRUCTION_SHAPE charts registered (with Charon coord) | Pipeline-D switches from stub data to real emission; **W4.0 synthetic-null tire-kick condition** (label-shuffled training as commit-blocking gate per substrate v2.2 §12 Build Gate 5) |
| **14-17** | Tier 3 rollout — cross-domain envs (BSD/MF/knots/g2c/mock theta) emit KillVector v2 + EvidenceField; navigator coverage 2/16 → ≥12/16 (reported as observed policy table, not manifold chart) | **W4.1/W4.2/W4.3/W4.4 tire-kick LoRA runs** on `pre_falsification_view` only (post-view loaded only with `--allow-post-falsification` flag); W5.2 OBSTRUCTION engine run |
| **17-19** | Charon coordination on G4 (F-gate orthogonality MI audit) + G6 (Lehmer ExclusionZone topology, now ExclusionCertificate); v2.2 review-response doc filed | W4.5/W4.6 acceptance checks; W5.3 cross-corpus transfer measurement; W5.4 LoRA generalization probe; **W6.1-W6.5 evidence dossier + decision** |

---

## 5. Sync points (explicit handoffs)

Each sync point is a moment where one project hands a deliverable to the other and the receiving side unblocks specific tasks. Sync points are scheduled, not opportunistic — both sides commit to the day.

| # | Day | From → To | Deliverable | Unblocks |
|---|---|---|---|---|
| **S1** | Day 2 | Techne → Ergon | P5 interface stub published (`prometheus_math/learner_corpus_interface.py` + spec doc) | Ergon W3.3 scaffolding |
| **S2** | Day 2 | Techne → Ergon | Pre-Tier-0 0a (DISCOVERY_CANDIDATE→CLAIM) routes Ergon's engine emissions into kernel discipline | Ergon's substrate-grade hardening (W1.x) gets typed-record outputs |
| **S3** | Day 2 | Techne → Ergon | Pre-Tier-0 0b (telemetry instrumentation) populates `elapsed_seconds` + `oracle_calls` on cross-domain pilots | Ergon W5.3 cross-corpus comparison becomes interpretable |
| **S4** | Day 2 | Techne → Ergon | `canonicalizer_observed_distribution` instrumentation logs canonicalizer used per claim | Ergon W1.6 Trial-2 re-validation runs safely (R21 hot-swap mitigation) |
| **S5** | Day 4 | Techne → Ergon | P0 CoordinateChart registered for Lehmer (deg14 ±5 palindromic); CanonicalizationProtocol with hot-swap support live | Ergon W3.2 fixture materialization (with `coordinate_chart_id`) |
| **S6** | Day 5 | Techne → Ergon | P2 stability adapter spec + P3 MethodSpec spec | Ergon W1.3 (stability adapters) and W3.2 schema (structured `method_spec`) |
| **S7** | Day 6-7 | Techne → Ergon | KillVector v2 (+8) ships; 3 v0.5-relevant components auto-populate from existing pipelines | Ergon W1.4 (native KillVector logging), W1.5 (axis re-enumeration) |
| **S8** | Day 13 | Techne → Ergon | P5 NearMissCorpus real triangulated emission (replaces stub); A149 + OBSTRUCTION_SHAPE charts registered | Ergon Pipeline-D upgrades from stub data; W4 tire-kick can run on real corpus |
| **S9** | Day 1-3 | Ergon → Techne | Per-domain raw-invariant feature lists (Lehmer pinned in Q-E2; OBSTRUCTION_SHAPE deferred to Charon coord) | Techne P5 spec finalizes per-domain content of `pre_falsification_view` |
| **S10** | Day 5 | Ergon → Techne | W3.2 schema final form (with `coordinate_chart_id`, structured `method_spec`, structured `stability_pass`, optional `exclusion_certificate_ref`) | Techne uses it as the canonical Lehmer raw-invariant set in P5 spec |
| **S11** | Day 7 | Ergon → Techne | W2.6 sign-off complete (Techne touch points: 17-entry schema + interpretive_slack + KillVector v2 (+8) acceptance + MethodSpec.drift_channel) | Techne KillVector v2 spec doc finalized with cross-project sign-off |
| **S12** | Day 13-14 | Ergon → Techne | Pipeline-D scaffold's stub-to-real migration validation (does same code path produce expected delta when upstream emitter changes?) | Substrate confirms P5 contract is consumable; v2.2 success criterion (≥1 contrastive corpus that Ergon trains on end-to-end) gets measured |
| **S13** | Day 14-17 | Joint | W4.0 synthetic-null tire-kick result (label-shuffled training) — does the model "learn" something on shuffled labels? | If pass: tire-kick is measuring memorization; if fail: tire-kick result is interpretable. Either way, gates W4.1+ interpretation per v2.2 Build Gate 5 |
| **S14** | Day 17-19 | Joint | W6.1 evidence dossier + W6.5 go/no-go decision; cross-referenced with substrate v2.2 success criteria | Both projects file `pivot/substrate_v2_review_responses_2026-05-XX.md` and `pivot/ergon_learner_v0.5_results_2026-05-XX.md` |

---

## 6. Bidirectional commitments

### 6.1 Techne → Ergon (substrate-side commitments)

| # | Commitment | Day | Status |
|---|---|---|---|
| T1 | P5 interface stub (schema + loader API + anti-leakage enforcement; stub from legacy ledger) | 1-2 | committed |
| T2 | Pre-Tier-0 0a + 0b + 0c (DISCOVERY_CANDIDATE→CLAIM, telemetry, TRACE audit) | 1-2 | committed |
| T3 | `canonicalizer_observed_distribution` instrumentation (R21 mitigation) | 1-2 | committed |
| T4 | P0 CoordinateChart with CanonicalizationProtocol + hot-swap support | 3-4 | committed |
| T5 | Lehmer chart registered (deg14 ±5 palindromic) | 3-4 | committed |
| T6 | P2 stability adapter spec (6-adapter taxonomy, tiered k) | 5 | committed |
| T7 | P3 MethodSpec spec (structured, with `independence_class` + `drift_channel`) | 5 | committed |
| T8 | KillVector v2 (+8 components); 3 v0.5-relevant auto-populated from existing pipelines | 6-7 | committed |
| T9 | P1 EvidenceField (reduced axes; `assumption_load` + `computational_friction` populated; `bridge_proximity` deferred) | 6-7 | committed |
| T10 | Tier 2 P4 ExclusionCertificate, P6 TriangulationProtocol, P5 full emission (in this order) | 8-13 | committed |
| T11 | A149 + OBSTRUCTION_SHAPE chart registration (with Charon coord) | 13 | conditional on Charon |
| T12 | Lehmer brute-force on deg12 ±5 (Ergon W3.2 held-out fixture) | 1-3 | committed |
| T13 | Tier 3 cross-domain rollout (envs emit KillVector v2 + EvidenceField) | 14-17 | committed |

### 6.2 Ergon → Techne (Learner-side commitments)

| # | Commitment | Day | Status |
|---|---|---|---|
| E1 | Pin per-domain raw-invariant feature lists (Lehmer first, OBSTRUCTION_SHAPE pending Charon) | 1-3 | committed |
| E2 | W3.2 schema final form (with structured fields per substrate v2.2) | 5 | committed |
| E3 | W2.6 sign-off response (Techne touch points: schema + interpretive_slack + KillVector v2 (+8) + MethodSpec.drift_channel) | 7 | committed |
| E4 | Pipeline-D scaffolds against P5 interface (not against legacy promotion_ledger) | 1-7 | committed |
| E5 | Train on `pre_falsification_view` only; explicit `--allow-post-falsification` flag for opt-in | 14+ | committed |
| E6 | W4.0 synthetic-null condition (label-shuffled training) as commit-blocking gate | 13-14 | committed |
| E7 | W3.7 surviving_claim_morphology pre-filter + unfiltered control corpus for one tire-kick comparison | 8-12 | committed |
| E8 | W6.3 RL framing reweighted: EvidenceField axes primary, substrate-PASS as tiebreaker | post-sprint | committed |
| E9 | W1.7 π₀ wiring propagates per-domain CI, not just point estimate | 1-3 | committed |
| E10 | Stub-to-real migration validation at Day 13-14 (S12) — confirms P5 contract is consumable | 13-14 | committed |
| E11 | W6.1 evidence dossier cross-references substrate v2.2 success criteria | 17-19 | committed |

### 6.3 Joint commitments (both projects own)

| # | Commitment | Day |
|---|---|---|
| J1 | Update this doc as state changes; both authors commit edits with `[joint-coord]` prefix | continuous |
| J2 | Surface sync-point slips immediately, not at end-of-week | continuous |
| J3 | Joint frontier-model review submission (this doc + both v2.2 / v0.5 docs as a bundle) | end of sprint |
| J4 | Joint sister-project review of opposite project's evidence dossier before W6.5 decision | 17-19 |
| J5 | **Mid-sprint pulse-check** (added per Aporia 2026-05-05): 30-min sync between Techne and Ergon, agora-streamed. Each side reports: what's on track, what's slipping, what's surfaced that wasn't in the original plan. Strategic fix for silent drift accumulation; the synthesis-debt pattern from Techne's 5-day sprint is the canonical cautionary example (9 results docs accumulated without a post-mortem). | 8-10 |

---

## 7. Dependency-chain visualization

```
Pre-Tier-0 (Days 1-2) ────────────────────────────────────┐
  ├─ 0a DISCOVERY_CANDIDATE→CLAIM ──┐                     │
  ├─ 0b telemetry instrumentation ──┤                     │
  ├─ 0c TRACE audit ────────────────┤                     │
  ├─ P5 interface stub ─────────────┼──→ Ergon W3.3       │
  └─ canonicalizer_obs_dist ────────┴──→ Ergon W1.6 safe  │
                                                           │
Tier 0 (Days 3-4) ─────────────────────────────────────────┤
  └─ P0 CoordinateChart + Lehmer ──→ Ergon W3.2          │
                                                           │
Tier 1 (Days 5-7) ─────────────────────────────────────────┤
  ├─ P3 MethodSpec spec ───────────→ Ergon W3.2 schema   │
  ├─ P2 stability adapters spec ───→ Ergon W1.3          │
  ├─ KillVector v2 (+8) ───────────→ Ergon W1.4 / W1.5   │
  └─ P1 EvidenceField (reduced) ───→ Ergon W2.4 dashboard│
                                                           │
Tier 2 (Days 8-13) ────────────────────────────────────────┤
  ├─ P4 ExclusionCertificate ──┐                          │
  ├─ P6 TriangulationProtocol ─┤                          │
  └─ P5 real emission ─────────┴──→ Ergon Pipeline-D real│
                                                           │
                                ┌──────────────────────────┘
                                ▼
                     Joint (Days 14-19)
                     ├─ W4.0 synthetic null ─ commit-blocking gate
                     ├─ W4.1-W4.4 tire-kick LoRA runs
                     ├─ W5.3 cross-corpus measurement
                     ├─ W6.1 evidence dossier
                     └─ W6.5 go/no-go decision
```

**Critical-path identifications:**

- **Substrate critical path:** Pre-Tier-0 → P0 → P3+P2+P1 → P4+P6+P5 → Tier 3. ~17-19 days serial.
- **Learner critical path:** W1.1 → W1.2 → W1.4 → W2.1 → W2.3 → W2.4 → W4.5 → W6.1 → W6.5. With Option C, Learner critical path runs concurrent with substrate critical path; total joint duration bounded by substrate critical path + ~5 days for tire-kick + decision.
- **Joint critical path:** the longer of the two, plus the tire-kick + decision phase. ~17-19 days substrate work and ~4 weeks Learner calendar; tire-kick is the merge point.

---

## 8. Joint risks (affect both projects)

| ID | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| **JR1** | P5 interface stub slips past Day 2 | High | Low | Ergon Pipeline-D scaffolding pivots to legacy promotion_ledger temporarily; rework scoped to ~1 day |
| **JR2** | KillVector v2 (+8) schema changes mid-sprint after Ergon W1.4 | High | Low | Auto-populate the 3 v0.5-relevant components only; other 5 emit `not_applicable` with structured reason — schema-stable |
| **JR3** | variety_fingerprint hot-swap fires before P0 lands (Ergon's R21) | Medium | Medium | T3 (`canonicalizer_observed_distribution` instrumentation) ships Day 1-2; logs canonicalizer per claim without changing logic; P0 lands Day 3-4 with proper hot-swap support |
| **JR4** | Aporia rejects Ergon's data sources as contaminated (Ergon's R16) | High | Low | Ergon W2.5 sign-off ping Day 1; if rejected, fall-back to pure synthetic corpus + 1-week extension |
| **JR5** | Charon's A149 + OBSTRUCTION_SHAPE chart specs aren't ready by Day 13 | Medium | Medium | Substrate ships placeholder charts with `chart_status: provisional`; Ergon W5.1 stubs against placeholder; re-bind on real registration |
| **JR6** | Tire-kick fails W4.0 synthetic-null condition (model "learns" on shuffled labels) | Medium | Medium | This is informative — substrate v2.2 §12 Build Gate 5 considers this an instrument-positive outcome; W6.1 dossier reports as expected failure mode rather than blocker |
| **JR7** | Pipeline-D engineering eats budget on Windows + RTX 5060 Ti (Ergon's R15) | High | Medium | Escalate to WSL2 if integration takes >5 days; substrate side unaffected |
| **JR8** | Cross-project schema drift mid-sprint (one side updates without notifying) | Medium | Low | This doc is the source of truth; both authors commit changes with `[joint-coord]` prefix; sister-project review of any deviation within 24h |

### 8.1 Day 1-2 slip priority order (added 2026-05-05 per Aporia review)

Day 1-2 has substantial parallel work on both sides (T1-T4 substrate + 8+ Ergon tasks). If something slips, the priority order for what gets cut:

**Substrate side (Techne):**
1. **MUST NOT cut:** P5 interface stub (T1) — Pipeline-D scaffolding depends on it; cutting cascades to E4 and S1
2. **MUST NOT cut:** Pre-Tier-0 0a + canonicalizer_observed_distribution (T2 + T3) — substrate discipline + R21 mitigation
3. **CAN cut/defer:** Pre-Tier-0 0c TRACE-preservation audit — ~1-hour investigation; can shift to Day 5+ without blocking anything
4. **CAN cut/defer:** telemetry instrumentation 0b — only blocks W5.3 interpretability, not Pipeline-D scaffolding; recoverable on Day 3-4

**Learner side (Ergon):**
1. **MUST NOT cut:** W2.5 + W2.6 sign-off pings — external blockers; even if everything else slips, send these Day 1
2. **MUST NOT cut:** W1.1 (quarantine MVPSubstrateEvaluator) — substrate discipline; small task; gates W1.2 and rest of A′
3. **CAN cut/defer:** W2.7 isogeny spike — nominal for v0.5 (per Aporia: "useful but not load-bearing"); can defer to Week 2
4. **CAN cut/defer:** W3.4 model loader — Pipeline-D's critical path doesn't need it on Day 1; can shift to Day 3-4 alongside Techne P0
5. **CAN cut/defer:** W5.1 OBSTRUCTION loader stub — only matters when W5.x kicks off in Week 4-5; Day 1 start is convenience not necessity

**Joint:**
- If both sides slip Day 1-2 simultaneously, escalate to James for re-sequencing rather than absorbing silently
- Sync point S1 (Day 2: P5 interface stub) is the firmest deliverable — both sides plan around it landing on time

---

## 9. Decision and escalation rules

**Within-project decisions:** each project owns its design space (substrate primitives for Techne; Learner architecture and training for Ergon). Sister-project review for awareness, not approval, unless the decision affects the joint contract (P5, KillVector v2, CoordinateChart, MethodSpec).

**Cross-project decisions:** require sign-off from both authors. Updates to this doc require both authors' acknowledgment via commit.

**Escalation to James:** required for (a) any change to the joint timeline beyond ±2 days, (b) any deviation from architectural lock-ins in substrate v2.2 §8, (c) any decision to drop or substantially scope-reduce a sync-point deliverable, (d) any joint risk transitioning from Likelihood-Low to Likelihood-Medium-or-High.

**Escalation to Aporia:** required for (a) sign-off on data-source contamination (Ergon W2.5), (b) integration of new artifacts mid-sprint that affect either project, (c) any pre/post-falsification view boundary question that's ambiguous.

**Escalation to Charon:** required for (a) chart registration for A149 + OBSTRUCTION_SHAPE (T11), (b) G4/G6 coordination, (c) any dispute about whether a measurement is calibration discipline or substrate-level finding.

**Frontier-model second-pass review:** triggered when this doc + substrate v2.2 + Learner v0.5 reach a stable joint state, not before. Bundle submission for efficiency (Claude / Grok / DeepSeek receive all three docs together).

---

## 10. Update protocol

Both authors update this doc continuously during the sprint. Conventions:

- Commit changes with `[joint-coord]` prefix in commit message.
- Use the change log (§11) to record material updates.
- If a sync point slips, update §5 immediately AND post to the agora stream (`agora:joint_sprint`).
- If a commitment in §6 changes status (committed → at-risk → slipped → recovered), update the status column AND log the change in §11.
- Architectural decisions logged in this doc supersede the same decisions in either project's individual doc; if the individual docs and this doc disagree, this doc wins.

End-of-sprint: file the joint review-response doc as `pivot/techne_ergon_joint_sprint_results_2026-05-XX.md` cross-referencing both project's individual outcome docs.

---

## 11. Change log

| Date | Author | Change |
|---|---|---|
| 2026-05-05 | Techne | Initial draft. Codifies Option C with early P5 stub. Captures bidirectional commitments T1-T13 and E1-E11. Schedules sync points S1-S14. Joint risk register JR1-JR8. |
| 2026-05-05 | Techne | [joint-coord] Added J5 mid-sprint pulse-check (Day 8-10) per Aporia feedback (`roles/Techne/APORIA_FEEDBACK_2026-05-05.md`); strategic fix for silent drift accumulation. |
| 2026-05-05 | Techne | [joint-coord] **Pre-Tier-0 SHIPPED.** T1 (P5 NearMissCorpus interface stub: `prometheus_math/learner_corpus.py` + `LEARNER_CORPUS_SPEC.md`, 23 tests pass), T2 0a (DISCOVERY_CANDIDATE→CLAIM promotion adapter: `prometheus_math/discovery_promotion.py`, 19 tests pass — domain-agnostic; supports Lehmer/BSD/OEIS/etc; SHADOW_CATALOG default; auto-caveats from precision_metadata; PROMOTE provenance scrapes candidate_id correctly), T2 0b (telemetry instrumentation across 6 cross-domain envs: bsd_rank/modular_form/knot_trace_field/genus2/oeis_sleeping/mock_theta — `info["elapsed_seconds"]` + `info["oracle_calls"]`, 6 new tests, 122/122 targeted pass), T2 0c (TRACE-preservation audit: `sigma_kernel/TRACE_PRESERVATION_AUDIT.md` — invariant HOLDS; documented as substrate-grade property; one follow-up flagged for Tier 1 about BIND/EVAL caveats), T3 (`canonicalizer_observed_distribution` instrumentation: `prometheus_math/canonicalizer_observability.py` — R21 hot-swap mitigation, 19 tests pass). Total: 183 new tests pass + 55 kernel regression tests pass + 0 regressions. Sister-project sync points S1–S4 all unblocked for Ergon. |
| 2026-05-06 | Techne | [joint-coord] **Tier 0 + Tier 1 partial SHIPPED in parallel.** T4+T5 P0 CoordinateChart + CanonicalizationProtocol (`sigma_kernel/coordinate_chart.py` + `sigma_kernel/coordinate_charts/lehmer.py`, 30 tests pass — `LEHMER_DEG14_PM5_PALINDROMIC` registered at import time; chart_id `"lehmer:deg14:pm5:palindromic"`; L2 metric over canonicalized half-vector with x→-x reflection equivalence; hot_swap_pending integration via canonicalizer_observability; sync point S5 unblocks Ergon W3.2). T7 P3 MethodSpec (`sigma_kernel/method_spec.py`, 35 tests pass — structured `(engine, strategy, precision_dps, version, parameters, fallback_chain, independence_class, drift_channel)`; 13-value IndependenceClass enum; intensional + behavioural hashes for triangulation independence per Aporia Study 15; `from_string()`/`to_string()` legacy compat; sync point S6 unblocks W3.2 schema). T9 P1 EvidenceField (`prometheus_math/evidence_field.py`, 39 tests pass — 6 factual axes with axis_type {metric, ordinal, vector, …}; PolicyField split per ChatGPT/Gemini convergence; `bridge_proximity` deferred per architectural lock-in; `assumption_load` ChatGPT v2.3 addition; `computational_friction` Gemini v2.3 addition). All landed via parallel agents per Aporia urgency. Total Tier 0/1 so far: 104 new tests + 0 regressions. |
| 2026-05-06 | Techne | [joint-coord] **Watch-1 kernel-foundation feasibility pass complete (research-only).** Doc filed at `pivot/sigma_kernel_logical_foundation_feasibility_2026-05-06.md`. **Verdict: PARTIAL.** CoC + native falsification records subsumes the epistemic layer cleanly (RESOLVE, CLAIM, FALSIFY, GATE, TRACE, REWRITE, EQUIV — 7 of 11) but not the operational layer (ERRATA defeasible reasoning, BIND host-callable, EVAL cost contract — 3 resist; PROMOTE needs QTT/LTT for linear caps). Recommendation: option (c) hybrid kernel ↔ CoC translation layer for v3.0; v2.2 imperative VM ships unchanged per Decision 3 scope. ~8,660 words. Aporia owns watchlist maintenance for Watch-1 status update. |
| 2026-05-06 | Techne | [joint-coord] **Tier 2 dispatched in parallel** (Agent E P4 ExclusionCertificate + Agent F P6 TriangulationProtocol) alongside in-flight Agent C (KillVector v2 + P2 stability adapters). Three Tier 2 implementations + KillVector v2 running concurrently. Once all land, I'll wire P5 NearMissCorpus full emission (replacing the Day 1-2 stub) per joint sprint S8/T10. |
| 2026-05-06 | Techne | [joint-coord] **Tier 1 + Tier 2 + Parallel-kernel SHIPPED.** T6+T8 KillVector v2 (`prometheus_math/kill_vector.py` + 60 new tests) — +8 components from Aporia Study 02 appended (relativizes / naturalizes / local_global_gap / requires_unproven_conjecture / asymptotic_only / small_case_artifact / asymmetric_effort / interpretive_slack); coalescing_failure_signature_caveat at 3+ co-occurring; pairwise MI estimator with Laplace smoothing; PRE_FALSIFICATION_DERIVABLE classification per Ergon Q-E5. P2 stability adapters (`prometheus_math/stability_adapters.py`) — 6-adapter taxonomy + tiered k=10/50/200 + structured StabilityResult. T10 P4 ExclusionCertificate (`sigma_kernel/exclusion_certificate.py` + Lehmer prototype, 34 tests) — Aporia v2.3 hard rule enforced (strength=COMPLETE requires non-empty triangulation_history); deg14 ±5 palindromic Lehmer cert auto-registers at import. T10 P6 TriangulationProtocol (`sigma_kernel/triangulation_protocol.py`, 34 tests) — clustering CANNOT certify; ≥1 proof-bearing path required for INCONCLUSIVE upgrades; INDEPENDENCE_TO_METHOD_CLASS registry. T10 P5 NearMissCorpus FULL emission (`prometheus_math/learner_corpus.py::emit_from_substrate`, 14 new tests) — schema v2.3 (no longer stub); integrates ALL upstream primitives (P0 chart_id, P3 method_spec, P4 exclusion_cert_ref, P6 triangulation_path, P1 evidence_field, KillVector v2); anti-trivial-separability triple generation drawn from same-region neighborhood per Gemini; canonical splits (train/val_same_region/val_heldout_region/val_heldout_method/val_later_time/synthetic_null) with deterministic seed; synthetic-null pack via label-shuffle. Parallel kernel REWRITE+EQUIV opcodes (`sigma_kernel/sigma_kernel.py` extended, 20 new tests) — feasibility-pass-validated; mint as regular Symbols; provenance scrapes endpoint hashes; no schema migration needed. **417 v2.3 tests passing across substrate, 0 regressions in pre-existing kernel/KV suite.** Sister-project sync point S8 (P5 full emission) DELIVERED. Only Agent H (Tier 3 cross-domain env rollout) still in flight. |
| 2026-05-06 | Techne | [joint-coord] **SUBSTRATE v2.3 SPRINT COMPLETE.** T13 Tier 3 cross-domain rollout shipped — 6 envs (bsd_rank/modular_form/knot_trace_field/genus2/oeis_sleeping/mock_theta) now emit `info["kill_vector"]` (KillVector v2 dict) + `info["evidence_field"]` (EvidenceField dict) per step. Shared helper `prometheus_math/_tier3_evidence.py`. EvidenceField.exclusion_distance NULL with explanatory reason for cross-domain envs (anti-fake-topology — only Lehmer chart registered; A149/OBSTRUCTION_SHAPE pending Charon coord per T11). 30 new tests + 122 pre-existing = 152/152 passing across env suites. **Final v2.3 regression: 607 tests passing in 53s, 0 regressions.** All bidirectional commitments T1–T13 SHIPPED. All 14 sync points S1–S14 unblocked or delivered. Joint sprint deliverable: substrate v2.3 ready for Ergon Pipeline-D real-data consumption (sync point S12 stub-to-real validation now possible). |
| 2026-05-05 | Ergon | **Acknowledgment + sign-off.** All E1-E11 commitments confirmed as written. All sync points S1-S14 accepted. Joint risk register JR1-JR8 accepted. R20 (Techne substrate slip) and R21 (variety_fingerprint hot-swap) from Ergon v0.5 design doc are subsumed by JR1+JR3 in this joint doc. Two clarifications: (a) E7 unfiltered-control corpus is implemented in W3.7 task description (not a separate task); (b) the v0.5 design doc's parallelization plan (its §5) is now superseded by §4 of this joint doc — the v0.5 doc references this doc as canonical. |
| (TBD) | Both | Sprint daily updates begin Day 1. |

---

## 12. References

- `pivot/substrate_v2_proposal_2026-05-05.md` (v2.2)
- `pivot/ergon_learner_v0.5_design_2026-05-05.md` (v0.5)
- `roles/Techne/AVAILABLE_ARTIFACTS_2026-05-05.md` (Aporia → Techne handoff)
- `roles/Ergon/AVAILABLE_ARTIFACTS_2026-05-05.md` (Aporia → Ergon handoff)
- `roles/Techne/CHARTER.md` (substrate mandate, 2026-05-05)
- `roles/Techne/RESPONSIBILITIES.md` (substrate + calibration discipline)
- `roles/Techne/SPRINT_2026-05-01_to_2026-05-05.md` (5-day sprint summary that justified v2)
- `charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md` (data-rich-but-trace-poor finding)
- `charon/diagnostics/MATHLIB4_PARETO_REPORT.md` (control-plane vs data-plane empirical validation)
- `aporia/meta/studies/2026-05-05/` (Studies 02, 12, 15, 17, 19 — substrate-relevant findings)

---

*Two forges, one sprint. The substrate forge produces the language truth lives in; the Learner forge produces the model that predicts where to look next. The handoff between them is P5 NearMissCorpus, the schema where evidence becomes training signal. Both forges run continuously and coordinate explicitly.*

*— Techne + Ergon, 2026-05-05*
