# Ergon Learner v0.5 — Design + Task List

**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Date:** 2026-05-05
**Status:** Design freeze for v0.5 phase. Supersedes the question-cycle doc. Pending Aporia review (and Techne sign-off on the boundary-layer schema in Task W3.2).
**Predecessors:**
- `pivot/ergon_learner_proposal_v8.md` (MVP design freeze that produced the current engine)
- `pivot/ergon_learner_v0.5_state_and_questions_2026-05-05.md` (state + open-question cycle that produced this design)
- `feedback_ergon_learner_north_star.md` (directional call: north star is Learner; reject identity-downgrade framings)
- `roles/Ergon/AVAILABLE_ARTIFACTS_2026-05-05.md` (Aporia's artifact-availability handoff; six artifacts triaged into v0.5 — see §3.4 and §5 W1.7 / W1.8 / W2.7 / W3.7)

---

## 0. TL;DR

Ergon v0.5 is **Learner v0.5 — first tire-kick.** The pipeline runs end-to-end with a small math model from HuggingFace (Qwen2.5-Math-1.5B-Instruct) LoRA-fine-tuned on substrate output. Whether the model learns anything useful on the first tire-kick is a separate question from whether the pipeline exists; both outcomes are informative and both are Learner-march progress.

The substrate hardening, KillVector telemetry, T0-T4 confidence tiers, baseline gauntlet, and corpus transfer rung that ChatGPT and Gemini both flagged as essential all survive — but as **infrastructure for the Learner march**, not as a terminal "Foundry" identity. ChatGPT's Foundry reframe is rejected per James's directional call. Diagnostic capabilities (provenance leakage classifier, near-miss atlas) are built inside Ergon for now; they may fork into a separate tool later if another agent demonstrably depends on them.

The 6-week sprint culminates in a go/no-go decision on whether v0.5's tire-kick justifies a real v1.0 training run with curated corpus + multi-arm LoRA + held-out evaluation.

---

## 1. What this doc supersedes / what it builds on

### Supersedes (within the v0.5 phase)

- **`ergon_learner_v0.5_state_and_questions_2026-05-05.md` §6.5 (path-decision).** That doc proposed `D → A`. After the review cycle (ChatGPT + Gemini, 2026-05-05) and James's directional call, the path is **A′ + Pipeline-D + Diagnostic-C in parallel, culminating in a tire-kick LoRA run**. See §3 below.
- **The "Substrate-Grade Near-Miss Foundry" identity reframe** (proposed by ChatGPT). Rejected. Ergon stays Learner; substrate hardening is the path, not the destination.

### Builds on / leaves intact

- **All of v8 §§1-3, 5.1-5.6, 6.1, 6.3-6.4, 7-15.** These are unchanged.
- **The MVP engine** (`ergon/learner/`) as it exists at commit `ca681ab4`. v0.5 modifies, does not rewrite.
- **Techne's substrate primitives** (`sigma_kernel/`, `prometheus_math/discovery_pipeline.py`, `kill_vector.py`, `kill_vector_navigator.py`, the six cross-domain envs). v0.5 consumes these; does not modify them. Schema changes go through Techne.
- **The promotion ledger** (`ergon/learner/promotion_ledger.py`) and existing iter28+iter31 ledgers. v0.5 augments with KillVector telemetry; does not invalidate.

---

## 2. Identity decision

**Ergon v0.5 = Learner v0.5 — first tire-kick.**

The north star is a trained model that predicts productive search moves. RL and full LoRA-evolution loops are v1.0+. v0.5 is the first complete pass through the pipeline:

**HF small math model → LoRA fine-tune → substrate output reproduction → falsification on held-out → calibrated decision on whether to scale.**

Why "tire-kick": the corpus on hand is too small / contaminated / single-domain to train a serious capability classifier. But waiting until the corpus is perfect to build the training pipeline means missing the API-restriction window. v0.5 builds the pipeline + runs it on whatever clean data we have (synthetic + 17-entry boundary layer + small curated near-miss set), produces a measurable outcome, and decides v1.0's scope from that data.

---

## 3. Path decision (synthesis from review cycle)

### Three workstreams, parallel, with strict scopes

#### Workstream **A′** — Strict minimum substrate-grade engine (Weeks 1-3)

Cuts from §6.5's original Path A:
- **No** OBSTRUCTION_SHAPE in MSGE (it lives in W5 as a transfer experiment, not as a substrate primitive)
- **No** Redis/agora integration in MSGE (deferred to v1.0; v0.5 ships agora-lite stubs only — single Redis stream for promoted near-misses + speculative claims, no live cross-agent flow)
- **No** counterfactual logging (v8 Change 9; deferred)
- **No** anti_prior KL+descriptor enforcement (v8 Change 5; deferred)
- **No** trivial-pattern temporal signatures (v8 Change 7; deferred)

Survives:
1. Kill `MVPSubstrateEvaluator` in `engine.py`. Route every operator class through `BindEvalKernelV2` end-to-end.
2. Native KillVector consumption: descriptor's axis 1 (canonicalizer subclass) augmented with one derived axis (`dominant_failure_family ∈ {null, triviality, simpler_model, crossval, catalog, stability}`); KillVector itself stays as **telemetry** (ranking within cells + lineage analysis), not full archive-axis replacement.
3. Real `stability.py` — input jitter ε=0.001 × 100 trials + half-precision recompute. Wired to `BindEvalKernelV2` for high-magnitude buckets only (≥3).
4. **T0-T4 confidence tiers** (per ChatGPT Q9 / Gemini Q9 convergence):

   | Tier | Evidence | Treatment |
   |------|----------|-----------|
   | T0 | 1 seed, no perturbation stability | Scratchpad only |
   | T1 | 1 seed + perturbation stable | Speculative |
   | T2 | 2/3 seeds OR same cluster under two regimes | Candidate |
   | T3 | 3/3 seeds + independent evaluator/corpus check | Robust |
   | T4 | T3 + external/catalog/formal confirmation | Promotable |

   Cross-seed validation runs **async on separate worker** (Gemini's framing). Engine stays fast + stochastic; tier assignment happens out-of-band.

5. **Re-validate Trial 2's 47σ result under KillVector-ranked fitness.** The original Trial 2 used cell-fill-only fitness; switching the within-cell ranking to KillVector margins may invalidate the structural ≥1.5× uniform finding. Mandatory re-run before declaring MSGE substrate-grade.

#### Workstream **A′-Aporia** — Aporia artifact integration (Weeks 1-2, parallel to A′ core)

Five small, high-leverage additions from Aporia's 2026-05-05 artifact handoff (`roles/Ergon/AVAILABLE_ARTIFACTS_2026-05-05.md`). All low-cost, no critical-path impact:

1. **W1.7 — Per-domain π₀ in reward function.** Aporia's "highest-leverage single move." Wire `charon/diagnostics/per_domain_pi0.json` into reward weighting so PROMOTE confidence is calibrated per domain (Lehmer 0.999 → 1000:1 prior odds; genus2 0.669 → 2:1). Same PROMOTE in genus2 vs Lehmer carries ~500× different posterior weight; without π₀ weighting, cross-corpus transfer measurements (W5.3) are uninterpretable.
2. **W1.8 — Per-class hit-rate weighting in scheduler.** `ergon/learner/diagnostics/per_class_hit_rates.json` was generated this morning. Current `OperatorScheduler` enforces minimum shares but doesn't weight by empirical hit rate. Augment so scheduler combines minimum-share floor + hit-rate-proportional allocation above the floor.
3. **W3.7 — Pre-filter training data via surviving_claim_morphology.** Run the 17-entry boundary layer + synthetic env data through `charon/diagnostics/surviving_claim_morphology.json`'s 4-class classifier (productive morphology / battery blind spot / thin-data artifact / template overfitting); filter records flagged as battery blind spot or template overfitting before LoRA training. Reduces R14 (tire-kick learns trivial heuristic).
4. **W2.7 (scoped spike) — equivalence_preserving operator class.** Aporia: "the most undervalued of the three [missing operator classes] — grounds mutation in real math instead of syntactic perturbation." v0.5 ships ONE instance (isogeny-on-elliptic-curve, the cheapest math-grounded mutation we can pull from existing arsenal); full operator class (Reidemeister moves, Hecke operators, twists) deferred to v1.0.
5. **W2.6 (extended) — three new KillVector components for v0.5.** Per Techne sign-off (2026-05-05 review), substrate v2.2 §7 ships **8 new KillVector components** (relativizes / naturalizes / local_global_gap / requires_unproven_conjecture / asymptotic_only / small_case_artifact / asymmetric_effort / interpretive_slack), all backwards-compatible. Of these, three are directly v0.5-relevant and Ergon wires them now: **`interpretive_slack`** (AM/Eurisko 1984; productivity attributable to generous parsing — directly bears on R14 trivial-heuristic risk), **`small_case_artifact`** (works for small N, fails at scale — also R14 mitigation), **`requires_unproven_conjecture`** (claim conditionally depends on RH/BSD/ABC — relevant to A149 and BSD work). The other five ship from substrate-side as v2.2 lands; Ergon consumes when convenient.

6. **W4.0 — synthetic-null tire-kick gate (NEW, commit-blocking).** Per Techne 2026-05-05 review + substrate v2.2 §12 Build Gate 5 ("null-before-claim"). The Day-4 lesson applied to Ergon's own training: train Qwen2.5-Math-1.5B + LoRA on a **label-shuffled** version of the 17-entry boundary layer + synthetic env. If shuffled-label accuracy is statistically distinguishable from chance, the tire-kick is measuring memorization, not learned structure. Commit-blocking — W4.1 / W4.2 cannot ship without W4.0 passing.

7. **Substrate-contract discipline — pre/post falsification view separation.** Per Techne v2.2 §6.3 P5 NearMissCorpus contract: training input MUST come from `pre_falsification_view` (object features + canonical_form + raw_invariants computed BEFORE any falsifier touches the object). `post_falsification_view` (KillVector / EvidenceField deltas / triangulation path) is explanation-only, loaded with explicit `--allow-post-falsification` flag, logged as potential leakage event. W3.2 / W3.3 / W4.x all enforce this discipline.

Hard cap: per Aporia §5 (citing QD literature consensus — Mouret-Clune, Cully-Demiris, Vassiliades CVT-MAP-Elites, AURORA), **descriptor stays at 6 axes** unless we switch to CVT-MAP-Elites. W1.5 takes us to exactly 6; no further axis additions in v0.5. See R19.

#### Workstream **A′-Techne-coord** — Substrate v2.2 contract integration (Weeks 1-3, dependency-driven)

Per Techne 2026-05-05 review of this design doc. Substrate v2.2 (`pivot/substrate_v2_proposal_2026-05-05.md`) ships ~17-19 days of substrate work in tier order; Ergon's substrate-touching tasks gate on the relevant Techne tier deliverables. **Coordination, not blocking** — Ergon's substrate-independent tasks run Day 1 in parallel with Techne's substrate work.

**Techne's commitments to Ergon (extracted from 2026-05-05 review):**

| Substrate deliverable | Effort | Unblocks |
|----------------------|--------|----------|
| Pre-Tier-0 0a (DISCOVERY_CANDIDATE → CLAIM) | ~1 day | Cross-domain candidates routed through kernel discipline |
| Pre-Tier-0 0b (telemetry: `elapsed_seconds` + `oracle_calls`) | ~1 day | EvidenceField.computational_friction populated; W5.3 cross-corpus comparison becomes interpretable |
| Tier 0 P0 CoordinateChart for Lehmer (deg14 ±5 palindromic) | ~2 days (prioritized) | W3.2 (17-entry fixture needs `coordinate_chart_id`) |
| Tier 0 P0 CoordinateChart for A149 + OBSTRUCTION_SHAPE | ~included in above | W5.1 (OBSTRUCTION loader); W5.3 cross-corpus chart alignment |
| Tier 1 P3 MethodSpec schema | ~0.5 days | W3.2 schema can adopt structured form Day 1 |
| KillVector v2 (+8 components, prioritize 3 v0.5-relevant) | ~included in v2.2 §7 | W1.4 / W1.5 |
| Lehmer brute-force on deg12 ±5 (held-out fixture) | already queued | W3.2 held-out validation |

**Ergon's coordination commitments back to Techne:**
- Adopt P5 NearMissCorpus schema for W3.2 / W3.3 / W3.7 / W4.x (retire Ergon's prior §7.2 schema proposal)
- Enforce pre/post-falsification view separation in W4 (W4.0 commit-blocking gate)
- Block W3.2 on Lehmer chart registration; W5.1 on A149 + OBSTRUCTION_SHAPE registration (or stub with `chart_status: provisional`)
- Adopt structured `method_spec` + `stability_pass` objects (not bool / single-string) wherever schema touches them
- Reweight W6.3 RL formulation: EvidenceField axes primary, substrate-PASS as tiebreaker (per v2.2 §8 control-plane vs data-plane lock-in)

**Techne's two follow-up commitments (accepted 2026-05-05 round 2):**
1. **Early P5 interface stub on Day 1-2 of joint sprint** (instead of end-of-Tier-2 / Day 13). Stub = schema + loader API + anti-leakage flag enforcement + placeholder emitter from existing promotion_ledger. Real triangulation-aware emission lands Day 13, replacing stub via same code path. **Collapses Ergon's blocked-on-substrate window from ~13 days to ~3-4 days for the parts that matter.** Pipeline-D scaffolds against the interface from Day 1.
2. **Temporary `canonicalizer_observed_distribution` instrumentation in Pre-Tier-0 0a** (R21 mitigation, path b). Logs the canonicalizer subclass used per claim without changing engine behavior. Lets W1.6 Trial-2 re-validation proceed without serializing on P0 landing. Real hot-swap-aware CanonicalizationProtocol lands Day 3-4 with P0.

**Canonical joint timeline:** see `pivot/techne_ergon_joint_sprint_2026-05-05.md` (filed 2026-05-05). The §5 parallelization plan in this doc is superseded by the joint sprint table.

#### Workstream **Pipeline-D** — Training pipeline infrastructure (Weeks 1-4)

Build the end-to-end LoRA training pipeline now, on whatever clean data is available. Per `feedback_ergon_learner_north_star.md`, the pipeline is build-now even if data is placeholder.

**Model selection: Qwen2.5-Math-1.5B-Instruct.**

Rationale:
- Math-specialized inductive bias (right starting point for substrate-output reproduction).
- 1.5B fits comfortably under the 3-4B VRAM ceiling (`feedback_vram_ceiling.md`).
- Modern instruction-tuned base; reasoning-friendly tokenizer.
- Below Rhea's proven 1.7B ceiling for LoRA work (`project_rhea.md`).
- HF-downloadable; no proprietary dependency.

**Backup model: Qwen2.5-Math-7B-Instruct + Unsloth 4-bit quantization.** Only if 1.5B underfits visibly on the held-out set in W4. Unsloth was already specified in v8 Change 10.

**Training framing for tire-kick: substrate-verdict reproduction.** Input: serialized predicate (genome's leaf-level callable composition + arg bindings + target_predicate string) + minimal corpus context (5-10 example records). Output: predicted KillVector (12-component continuous regression) OR predicted substrate-PASS probability.

This is the simplest possible tire-kick: train a small math model to do what the falsification battery does. If it works on the clean datasets in W3, the LoRA path can absorb substrate output. That's all v0.5 has to prove.

**v1.0 framings deferred:** mutation prediction (sequence-to-sequence); operator-class recommendation given target predicate; RL on substrate-verdict reward.

#### Workstream **Diagnostic-C** — Clean-data sources (Weeks 2-4)

Two clean (i.e., contamination-free per Aporia's flag) data sources for the tire-kick:

1. **Synthetic ground-truth env.** A clean env where the true latent rule is known and continuous (analog of Techne's `modal_collapse_synthetic` but designed as a training source, not just a diagnostic). Used to test transfer pressure: does the LoRA-tuned model recover the rule under disguise?
2. **The 17-entry Lehmer boundary layer** (Techne sprint Day 5 output, Path C). Already has 4-class labels (post-invariance-fold: 2). Held-out fixture: re-run `lehmer_brute_force` on a different finite slice (deg12 ±5 palindromic, or deg14 ±3 palindromic — Techne's queued items); classifier passes if it maintains $k=2$ silhouette ≥ 0.7 on the held-out slice.

Aporia's contamination flag applies to capability training on the contaminated A149 corpus. The synthetic env and the 17-entry boundary layer are **not** contaminated, so they're fair game for tire-kick training. **This needs Aporia sign-off in W2.** See §7.

---

## 4. v0.5 acceptance criteria (6-week kill criterion)

Per ChatGPT's framing (rephrased for Learner march): v0.5 must demonstrate **at least 2 of 4** of the following, or Ergon's primary path gets reduced and the project re-scoped:

1. **Cross-corpus lift (W5):** Structural / KillVector-guided search beats structured uniform by ≥2× on robust near-miss yield across A149 + OBSTRUCTION_SHAPE.
2. **KillVector monotonicity (W2-W3):** Selected operator classes show statistically stable directional movement toward lower failure margins on held-out region keys.
3. **Robustness stratification works (W1-W2):** T3 (3/3-seed) claims are meaningfully more likely to survive cross-evaluator or cross-corpus checks than T1 (1/3-seed) claims.
4. **Pipeline + tire-kick deliver measurable signal (W4):** LoRA-tuned Qwen2.5-Math-1.5B on clean data produces ≥1 of: (a) above-baseline accuracy on substrate-verdict prediction on held-out 17-entry slice; (b) measurable behavior change vs base model on synthetic env recovery; (c) clean failure mode that names what data is needed for v1.0 (e.g., "17 entries is too few; v1.0 needs ≥1K curated near-miss pairs").

**The fourth criterion is intentionally weak** — even a "measurable failure that names what we need next" counts. The point is to *learn from the tire-kick*, not to ship a useful model on round 1. ChatGPT and Gemini converge on "no 184M classifier yet"; this acceptance criterion respects that bar.

---

## 5. Detailed task list (week-by-week)

Each task carries: **subject**, **deliverable** (concrete artifact), **success condition** (measurable), **owner** (Ergon unless flagged), **blocked-by** (if dependent).

### Week 1 — Substrate-grade hardening (A′ core)

| ID | Task | Deliverable | Success condition | Blocked by |
|----|------|-------------|-------------------|------------|
| W1.1 | Quarantine `MVPSubstrateEvaluator` | Engine raises `EvaluatorNotWiredError` if stub is requested at run time; flag --use-stub gates legacy paths | All trial scripts updated; CI green | — |
| W1.2 | Route all operator classes through `BindEvalKernelV2` | Each operator's `evaluate()` calls `BindEvalKernelV2` (not the stub); regression tests cover 5 classes × 1 minimal env | 5/5 operators evaluate end-to-end on a 100-episode smoke run with no stub fallback | W1.1 |
| W1.3 | Implement real `stability.py` (v0.5 simple form) | `perturbation_stability_check` runs input jitter ε=0.001 × 100 trials + half-precision recompute against `BindEvalKernelV2` for buckets ≥3. **Plans migration to v2.2 P2 structured object** (`{stability_mean, stability_variance, perturbation_family, worst_case_flip_rate, k_used}`) when Techne ships P2; do NOT binary-encode as single field | High-magnitude bucket records in promotion ledger carry `stability_pass` (stub-structured), with field shape ready for v2.2 expansion; tests cover pass / fail / borderline | W1.2 |
| W1.4 | Wire native KillVector logging | `EpisodeResult` carries full `KillVector`; `delta_kill_vector` computed per mutation | All ledger records since W1.4 carry KillVector; legacy records remain readable via `kill_vector_from_legacy` | W1.2 |
| W1.5 | Add `dominant_failure_family` derived descriptor axis | `descriptor.py` extended with axis 6; archive cell space stays bounded (~6× current = ~30K cells max) | Audit shows new axis fills ≥3 of 6 buckets in 1K-episode run; no axis concentration >70% | W1.4 |
| W1.6 | Re-validate Trial 2's 47σ under KillVector-ranked fitness | New trial script `trial_2_killvector_revalidation.py` reruns the 5-seed × 1K-episode protocol with KillVector-ranked within-cell fitness | Result tabulated; structural-vs-uniform multiplier reported (whatever it is — pass or fail is informative) | W1.4, W1.5 |
| W1.7 | Wire per-domain π₀ into reward function with CI propagation (Aporia artifact 1; Techne smaller concern #7) | `reward.py` augmented with `compute_reward_with_pi0(components, weights, domain)` reading `charon/diagnostics/per_domain_pi0.json`; **propagate per-domain CI** (genus2 0.669 has wide CI vs Lehmer 0.999 tight); reward weighting carries CI bounds, not just point estimate, so low-data domains don't amplify noise into the gradient; engine passes domain context through | All new ledger records carry `pi0_weighted_reward` field with `pi0_ci_lower` / `pi0_ci_upper`; cross-corpus comparisons in W5.3 use π₀-CI-conditioned rate ratios | — (Day 1 parallel start) |
| W1.8 | Per-class hit-rate weighting in scheduler (Aporia artifact 2) | `scheduler.py` augmented to read `ergon/learner/diagnostics/per_class_hit_rates.json`; allocation = min-share floor + hit-rate-proportional above floor | Smoke run shows hit-rate weighting active; minimum-share floors still respected; documentation note on hot-swap if hit rates drift | — (Day 1 parallel start) |

### Week 2 — Confidence tiers + KillVector telemetry primitives + Aporia sign-off

| ID | Task | Deliverable | Success condition | Blocked by |
|----|------|-------------|-------------------|------------|
| W2.1 | Implement T0-T4 tier assignment | `confidence.py` module with `assign_tier(claim, seeds_seen, perturbation_pass, cross_evaluator_pass)`; tier written to ledger | 100% of new ledger records carry tier; tier distribution audit run on existing iter28+iter31 ledgers | W1.4 |
| W2.2 | Build async cross-seed worker | `tools/cross_seed_worker.py` reads `agora:speculative` (file-backed for v0.5; Redis stub), runs 3-seed re-evaluation, writes tier-promotion records | Worker upgrades a known T1 example to T2 or T3 in <5 min; engine never blocks on it | W2.1 |
| W2.3 | Lineage replay tool | `tools/lineage_replay.py` reconstructs genome ancestry from content_hash + parent_hash chain; emits per-mutation `delta_kill_vector` and `delta_descriptor_cell` | Replay one of the 5 robust A149 clusters end-to-end; identify causal mutation subsequence | W1.4, W2.1 |
| W2.4 | KillVector trajectory dashboard | `tools/killvector_trajectory.py` aggregates per-operator-family `E[delta_kill_vector]` across logged lineages | Per operator class, signed ratio of "moves toward zero vector" vs "moves away" reported; baseline established for W4 monotonicity check | W2.3 |
| W2.5 | **Aporia sign-off:** synthetic env + 17-entry boundary layer cleared as non-contaminated for tire-kick training | Aporia's written confirmation appended to this doc as §7.1 | Yes/no decision recorded; if no, fall-back data source named | — (Aporia, blocking W4) |
| W2.6 | **Techne sign-off (received 2026-05-05; APPROVED with expansion):** 17-entry boundary layer schema + 3 v0.5-relevant KillVector components | Schema approved with 4 additions (`coordinate_chart_id`, structured `method_spec`, structured `stability_pass`, optional `exclusion_certificate_ref`); Techne adds 8 KillVector components to substrate v2.2, of which Ergon wires 3 for v0.5: `interpretive_slack` + `small_case_artifact` + `requires_unproven_conjecture` | Schema in §7.2 superseded by v2.2-aligned form; W1.4 / W1.5 enumerate the 3 new components plus reserve names for the other 5 | DONE |
| W2.7 | equivalence_preserving operator class — scoped spike (Aporia artifact 4) | New `ergon/learner/operators/equivalence_preserving.py` with ONE instance: isogeny-on-elliptic-curve mutation (uses `prometheus_math` arsenal isogeny callable). Full class (Reidemeister, Hecke, twists) deferred to v1.0 | Operator generates 100 child genomes from 10 EC parents without crash; mutations preserve EC isomorphism class invariants per arsenal `equivalence_class` tag | — (parallel; uses existing arsenal) |

### Week 3 — Diagnostic-C clean-data sources + Pipeline-D infrastructure scaffold

| ID | Task | Deliverable | Success condition | Blocked by |
|----|------|-------------|-------------------|------------|
| W3.1 | Build synthetic ground-truth env | `ergon/diagnostic_c/synthetic_env.py` — clean env with known latent rule (linear / polynomial regression with structured noise); generates train/held-out splits | 1K train + 200 held-out generated; ground truth recoverable by lstsq on clean data | — |
| W3.2 | Materialize 17-entry boundary layer training fixture (substrate v2.2-aligned) | `ergon/pipeline_d/boundary_layer_fixture.py` exports the 17 entries from `prometheus_math/_lehmer_brute_force_path_b.py` results in the **v2.2-aligned schema** (§7.2 below): adds `coordinate_chart_id`, structured `method_spec` (engine + strategy + precision_dps + independence_class + drift_channel), structured `stability_pass` object (not bool), optional `exclusion_certificate_ref`. **Emits separate `pre_falsification_view` and `post_falsification_view` to different file paths per v2.2 §6.3 P5 contract.** | All 17 entries serialized in both views; held-out fixture from `lehmer_brute_force` on deg12 ±5 generated (Techne queued + prioritized); pre/post views in distinct file paths | W2.6 (DONE) + Techne Tier 0 P0 Lehmer chart registration (~2 days) |
| W3.3 | Pipeline-D scaffold — data loader | `ergon/pipeline_d/data_loader.py` reads schema-conformant JSONL; produces HuggingFace `Dataset`; supports train/eval splits | Loader passes 17-entry fixture + synthetic env data through HF `Trainer` API smoke test (no actual training) | W3.1, W3.2 |
| W3.4 | Pipeline-D scaffold — model loader (Qwen2.5-Math-1.5B-Instruct) | `ergon/pipeline_d/model.py` downloads + loads Qwen2.5-Math-1.5B-Instruct via `transformers`; configures LoRA via `peft` (rank 8 default, target modules q_proj+v_proj per Rhea precedent) | Base model loads without OOM on RTX 5060 Ti; LoRA adapter attaches; trainable param count <2% of total | — |
| W3.5 | Pipeline-D scaffold — eval harness | `ergon/pipeline_d/eval.py` runs base + LoRA model on held-out fixture; reports per-class accuracy + confusion matrix + KillVector regression MSE | Base model eval runs end-to-end on 17-entry held-out; baseline numbers logged | W3.3, W3.4 |
| W3.6 | Pipeline-D scaffold — training loop | `ergon/pipeline_d/train.py` uses Unsloth + `peft` + `trl.SFTTrainer`; max 50 epochs; early stopping on held-out loss | Smoke training run (1 epoch, 17 entries) completes without crash; training loss decreases | W3.3, W3.4, W3.5 |
| W3.7 | Pre-filter training data via surviving_claim_morphology (Aporia artifact 3) — with closed-loop disclosure | `ergon/pipeline_d/data_filter.py` runs the 17-entry boundary layer + synthetic env outputs through `charon/diagnostics/surviving_claim_morphology.json`'s 4-class classifier; drops records flagged as `battery_blind_spot` or `template_overfitting`. **Per Techne smaller-concern #5: closed-loop bias disclosure** — Charon's classifier is itself trained on substrate verdicts; filtering before LoRA training means Ergon learns a constrained subset of substrate-blessed records. Mitigation: (a) per-class drop counts logged (already in spec); (b) **W4.1 runs both filtered AND unfiltered control** so we can measure the bias the filter introduces | Filter applied to W3.2 + W3.1 outputs; per-class drop counts logged; INDETERMINATE retained with metadata flag; unfiltered control corpus preserved alongside filtered for W4.1 comparison | W3.1, W3.2 |

### Week 4 — First tire-kick LoRA run

| ID | Task | Deliverable | Success condition | Blocked by |
|----|------|-------------|-------------------|------------|
| **W4.0** | **Synthetic-null tire-kick gate (COMMIT-BLOCKING per substrate v2.2 §12 Build Gate 5)** | `pipeline_d/runs/null_gate_*/` — train Qwen2.5-Math-1.5B + LoRA on **label-shuffled** version of 17-entry + synthetic env. Day-4-lesson applied to Ergon's own training: if Learner shows above-chance accuracy on shuffled labels, tire-kick is memorization | Shuffled-label held-out accuracy is **statistically indistinguishable from chance** (chi-square or permutation test, p > 0.10). If gate fails: W4.1/W4.2 BLOCKED until tire-kick design is revised | W3.6, W2.5 |
| W4.1 | Tire-kick run #1: Qwen2.5-Math-1.5B + LoRA on 17-entry boundary layer (**pre-view only**; filtered vs unfiltered comparison) | `pipeline_d/runs/tire_kick_1_filtered/` + `pipeline_d/runs/tire_kick_1_unfiltered/` — two parallel runs: morphology-filtered training data and unfiltered control. **Training input is `pre_falsification_view` only** (object features + canonical_form + raw_invariants); post-view loaded only with `--allow-post-falsification` flag. Example-records in prompt context are pre-view samples | Training completes both runs; held-out accuracy reported for both; pass/fail/inconclusive verdict with morphology-filter bias measured | W3.6, W2.5, **W4.0** |
| W4.2 | Tire-kick run #2: Qwen2.5-Math-1.5B + LoRA on synthetic env (**pre-view only**) | `pipeline_d/runs/tire_kick_2/` — same structure as W4.1; training input restricted to `pre_falsification_view` per v2.2 P5 contract | Held-out recovery rate on synthetic latent rule reported; compared to base-model zero-shot | W3.6, W2.5, **W4.0** |
| W4.3 | Tire-kick run #3 (conditional): Qwen2.5-Math-1.5B + LoRA on combined 17-entry + synthetic | If tire-kick #1 underfits, combine datasets + retrain | If run, deliverable mirrors W4.1/W4.2 | W4.1, W4.2 |
| W4.4 | Backup tire-kick (conditional): Qwen2.5-Math-7B + Unsloth 4-bit | Triggered only if 1.5B underfits visibly on both tire-kicks | Same deliverable pattern; flagged as escalation | W4.1, W4.2 |
| W4.5 | KillVector monotonicity check (criterion 2) | Aggregate per-operator `E[delta_kill_vector]` across W2-W4 ledgers; statistical test for monotonic trend | Pass/fail + p-value reported per operator class | W2.4 |
| W4.6 | Robustness stratification check (criterion 3) | Compare T3 vs T1 claims on cross-evaluator pass rate using existing iter28+iter31 ledgers + W1-W4 new records | Stratification effect size + significance test reported | W2.1 |

### Week 5 — Cross-corpus transfer rung

| ID | Task | Deliverable | Success condition | Blocked by |
|----|------|-------------|-------------------|------------|
| W5.1 | Build OBSTRUCTION_SHAPE corpus loader (chart-aware) | `ergon/learner/corpora/obstruction_shape.py` reads Techne's OBSTRUCTION env data; objects carry `coordinate_chart_id` referencing Techne's registered A149 + OBSTRUCTION_SHAPE charts (Tier 0 P0). If Techne charts haven't shipped by W5.1 start, stub with `chart_status: "provisional"` and re-bind on real registration | Loader integrates with engine; smoke run of 100 episodes completes; objects carry chart_id (real or provisional) | W1.2, **Techne Tier 0 P0 A149 + OBSTRUCTION_SHAPE chart registration (or provisional stub)** |
| W5.2 | Run engine on OBSTRUCTION_SHAPE with v0.5 settings | `trial_4_obstruction_shape.py` — 5K episodes × 3 seeds × 2 weight regimes (u05_canonical + u30_broad) | Promotion ledger generated; cluster-recurrence analysis run (per `stability_analysis.py`) | W5.1, W2.1 |
| W5.3 | Cross-corpus transfer measurement (criterion 1) | `tools/cross_corpus_transfer.py` compares structural-vs-uniform robust-near-miss yield on A149 + OBSTRUCTION_SHAPE; computes lift ratio | Lift ratio + 95% CI reported per corpus | W5.2 |
| W5.4 | LoRA generalization probe (optional, conditional on W4 success) | Run W4.1's LoRA-tuned model on OBSTRUCTION_SHAPE-derived predicates (zero-shot) | Held-out accuracy on OBSTRUCTION_SHAPE substrate-verdict reported | W4.1, W5.2 |

### Parallelization plan

The 6-week serial timeline assumed sequential work. With parallel sub-agents, the calendar collapses to roughly **3-4 weeks**, bounded by the substrate-hardening critical path.

**Day-1 parallel starts (zero upstream dependencies):**

| Task | Workstream | Cost |
|------|------------|------|
| W1.1 | A′ engine entry | small |
| W1.7 | Aporia π₀ wiring | 1-2 hrs |
| W1.8 | Aporia hit-rate scheduler | 2-3 hrs |
| W2.7 | equivalence_preserving operator spike | 1-2 days |
| W3.1 | Synthetic ground-truth env | 1-2 days |
| W3.4 | Qwen2.5-Math-1.5B model loader scaffold | 2-3 days |
| W2.5 | Aporia sign-off ping | external (async) |
| W2.6 | Techne sign-off ping | external (async) |

**Workstream parallelism:**

```
A′-core         : W1.1 → W1.2 → W1.4 ─┬→ W1.5 → W1.6
                                       ├→ W2.1 → W2.2
                                       ├→ W2.3 → W2.4
                                       └→ W1.3
A′-Aporia       : W1.7 (Day 1) || W1.8 (Day 1) || W2.7 (Day 1)
Pipeline-D      : W3.4 (Day 1) || W3.1 (Day 1) || W2.6 → W3.2 → W3.7 → W3.3 → W3.5 → W3.6
Transfer        : W1.1 → W1.2 → W5.1 → W5.2 → W5.3
Sign-offs       : W2.5 (Aporia) || W2.6 (Techne)  [external, async]

All converge at: W4 (tire-kick) → W6.1 (evidence) → W6.5 (decision)
```

**Critical path** (longest dependency chain):

`W1.1 → W1.2 → W1.4 → W2.1 → W2.3 → W2.4 → W4.5 → W6.1 → W6.5`

Nine sequentially-dependent tasks. At ~2-3 days/task focused, ≈ **18-27 calendar days = 3-4 weeks**.

**Forced serialization points (can't parallelize past these):**

1. **W4 tire-kick** needs W3.6 (pipeline ready) + W2.5 (Aporia sign-off). Aporia delay = tire-kick delay regardless of build parallelism.
2. **W6.1 evidence dossier** needs W4.5 + W4.6 + W5.3. All three can run parallel during W4-W5; W6.1 waits for slowest.
3. **W6.5 go/no-go** needs W6.2 + W6.3. These can run parallel during W6 but the decision call is the merge point.

**Sub-agent allocation recommendation:**

| Sub-agent role | Owns |
|----------------|------|
| **Substrate-A′-core** | W1.1 → W1.2 → W1.3 / W1.4 → W1.5 → W1.6 → W2.1 → W2.2 / W2.3 → W2.4 |
| **Aporia integration** | W1.7 + W1.8 + W2.7 (all Day 1, all small) |
| **Pipeline-D** (recommend WSL2 worktree) | W3.4 + W3.1 (Day 1) + W3.3 / W3.5 / W3.6 (post W3.2) |
| **Synthetic env** | W3.1 if Pipeline-D agent is busy; otherwise bundles with Pipeline-D |
| **Transfer** | W5.1 / W5.2 / W5.3 (after W1.2 + W2.1) |
| **Orchestrator (me)** | Integration, W1.6 Trial 2 re-validation, W4 tire-kick runs, W6 evidence + decision |

**Compressed timeline:**

| Week | Parallel deliverables |
|------|----------------------|
| **Day 1-2** | W1.1, W1.7, W1.8, W2.7 spike start, W3.1 start, W3.4 start, sign-off pings sent |
| **Week 1** | W1.2 → W1.4 done; W1.7 + W1.8 done; W3.4 + W3.1 done; sign-offs in flight; W2.7 spike complete |
| **Week 2** | W2.1 → W2.4 done; W3.6 done (if Techne signed off by Day 5); W3.7 done; W5.1 begins |
| **Week 3** | W4.1 / W4.2 tire-kick runs; W5.2 OBSTRUCTION run; W4.5 / W4.6 acceptance checks |
| **Week 4** | W5.3 cross-corpus measurement; W6.1 evidence dossier; W6.2 / W6.3 v1.0 drafts; W6.5 decision |

### Week 6 — Decision report + v1.0 readiness

| ID | Task | Deliverable | Success condition | Blocked by |
|----|------|-------------|-------------------|------------|
| W6.1 | Compile v0.5 evidence dossier | `pivot/ergon_learner_v0.5_results_2026-MM-DD.md` — all 4 acceptance-criterion outcomes + tire-kick results + dashboard snapshots | Document filed; all numbers traceable to underlying ledgers / runs | W4.5, W4.6, W5.3 |
| W6.2 | v1.0 design proposal — corpus expansion plan | `pivot/ergon_learner_v1.0_corpus_design_2026-MM-DD.md` — what data is needed, in what volume, for what training framings | Plan addresses Aporia's contamination flag; quantifies record-count target | W6.1 |
| W6.3 | v1.0 design proposal — RL framing (control-plane / data-plane separated) | `pivot/ergon_learner_v1.0_rl_framing_2026-MM-DD.md` — RL formulation: state = (genome, corpus context); action = mutation; **reward weighting per Techne smaller-concern #6 + v2.2 §8 control-plane/data-plane lock-in: EvidenceField axis improvement is PRIMARY signal (data-plane); substrate-PASS is TIEBREAKER only (control-plane).** This avoids the residual-gaming attractor v8 §11.6 names as the bear case | Draft ready for next review cycle; reward formulation explicitly cites v2.2 §8 architectural lock-in | W6.1 |
| W6.4 | Stoa post — v0.5 outcome announcement | `stoa/discussions/2026-MM-DD-ergon-v0.5-results.md` — public-facing summary with calibration discipline applied (no overclaim) | Post filed; cited by Aporia / Techne in their next sprint plans | W6.1 |
| W6.5 | Go/no-go decision call with James | Decision record: scale to v1.0, fork diagnostic capabilities, or downgrade Ergon scope | Decision recorded in this doc as §10 | W6.1, W6.2, W6.3 |

---

## 6. Risk register additions (beyond v8 R1-R13)

**R14: Tire-kick LoRA learns trivial heuristic.** Severity: Medium. Likelihood: High.

The 17-entry boundary layer + synthetic env are small. A LoRA fine-tune may converge on memorization or trivial heuristic (e.g., "polynomial degree → class") that doesn't reflect substrate structure. *Mitigation*: held-out fixture from a different finite slice (W3.2); zero-shot evaluation on OBSTRUCTION_SHAPE (W5.4) as out-of-distribution check.

**R15: Pipeline-D engineering eats budget.** Severity: High. Likelihood: Medium.

LoRA + Unsloth + HuggingFace + peft + trl integration on Windows + RTX 5060 Ti has many unknown engineering surfaces. Budget could overrun. *Mitigation*: W3.4-W3.6 are scoped as scaffold; if integration takes >5 days, delay W4 by 1 week; if still blocked, escalate to WSL2 (per Rhea's stack).

**R16: Aporia rejects synthetic env + 17-entry as non-contaminated.** Severity: High. Likelihood: Low.

If Aporia's review flags either source as still-contaminated, W4 has no clean training data. *Mitigation*: ask Aporia in W2 (W2.5); if flagged, fall back to synthetic-only or escalate to "build a fresh clean corpus" (which extends timeline by 2+ weeks).

**R17: KillVector consumption invalidates iter28+iter31 ledgers.** Severity: Medium. Likelihood: Medium.

Reconstructed KillVectors from legacy records may be lower-confidence than freshly logged ones. *Mitigation*: mark all reconstructed entries with `kill_vector_provenance: "legacy_reconstructed"` (per Techne's caveat-as-metadata discipline); cross-seed worker treats reconstructed entries as T0/T1 only.

**R18: Trial 2 re-validation under KillVector-ranked fitness fails.** Severity: High. Likelihood: Low-Medium.

If structural-vs-uniform multiplier collapses below 1.5× under the new fitness function, MSGE is not substrate-grade as designed. *Mitigation*: this is informative either way (and is exactly the kind of recalibration the substrate is supposed to do). If it fails, the right move is to treat it as a v0.5 finding, file a Stoa post, and use the data to inform either a fitness-function redesign or a return to cell-fill-only fitness with documented limitations.

**R19: Descriptor axis cap exceeded.** Severity: Medium. Likelihood: Low (with discipline).

QD literature (Mouret-Clune; Cully-Demiris; Vassiliades CVT-MAP-Elites; AURORA) consensus: 2-6 hand-designed axes is the supported range; CVT-MAP-Elites or autoencoded descriptors needed above 6. v0.5's W1.5 takes us to exactly 6 (canonicalizer + DAG entropy + output type + magnitude + canonical-form distance + dominant_failure_family). *Mitigation*: hard cap at 6 axes for the rest of v0.5. Any future axis (Bourbaki tag, KillVector projection beyond `dominant_failure_family`, etc.) requires switching to CVT-MAP-Elites first. Surface this constraint in v1.0 design (W6.2 / W6.3).

**R20: Techne substrate v2.2 slips → Pipeline-D blocked.** Severity: High. Likelihood: Medium.

Ergon's Pipeline-D (W3.2 / W5.1 / W4.x) has hard dependencies on Techne's Tier 0 P0 CoordinateChart registration (~2 days), KillVector v2 (+8 components), and P5 NearMissCorpus emission. Techne's substrate v2.2 is ~17-19 days of work; if any tier slips, Ergon's downstream tasks block. *Mitigation*: (a) Ergon's Day-1 substrate-independent tasks (W1.1, W1.2, W1.7, W1.8, W2.7, W3.4, W3.1) maintain forward progress; (b) provisional-stub fallback for W5.1 chart_id (Techne approved); (c) frequent sync between Techne and Ergon at tier-handoff boundaries. If Techne's Tier 0 isn't ready by end of Ergon Week 1, escalate to James for re-sequencing.

**R21: variety_fingerprint hot-swap fires before W1.5 ships.** Severity: Medium. Likelihood: High (Techne flagged 52% concentration on seed=42 / 1K eps — approaching the 70% hot-swap threshold).

Ergon's session journal shows axis 1 (canonicalizer subclass) skewing toward `variety_fingerprint`. v0.5 W1.5 adds a 6th axis (`dominant_failure_family`) but doesn't address axis-1 concentration. If hot-swap fires mid-sprint, archive cells re-bin and existing iter28+iter31 ledgers become harder to compare. *Mitigation*: (a) accept that Techne's CanonicalizationProtocol with `decidability_status` flags (Aporia Study 17, integrated in v2.2 §6.1 P0) will eventually replace the fixed enum; (b) for v0.5, do NOT trigger hot-swap on existing data — accept the concentration as a known limitation, document in W6.1 evidence dossier, plan hot-swap as a v1.0 migration with explicit re-binning of legacy ledgers.

---

## 7. Open items requiring sign-off

### 7.1 Aporia sign-off (W2.5, blocking W4)

**Question:** Are the synthetic ground-truth env (W3.1) and the 17-entry Lehmer boundary layer (W3.2) cleared as non-contaminated data sources for tire-kick LoRA training, given the sharpened gating constraint from `roles/Ergon/AVAILABLE_ARTIFACTS_2026-05-05.md`?

**Aporia's sharpened framing (2026-05-05):** the prior "≥20K records" gate is superseded by:

> The substrate is **data-rich but trace-poor**. Existing ~2K-record corpus IS training-grade for predicate-search within A149. NOT training-grade for cross-domain generalization (records are mathematical objects, not training pairs). **Defer cross-domain Ergon training until ≥100 per-claim kill records exist in ≥2 domains.**

This is the new gating constraint. v0.5's tire-kick is intra-A149 + synthetic + boundary-layer — all single-domain or contamination-free; cross-domain training is correctly deferred to v1.0 / v2.0.

**What Aporia needs to confirm:**
1. Synthetic env design (per W3.1) doesn't reproduce the modal-class recovery pathology that contaminated A149.
2. The 17-entry boundary layer's Techne-curation discipline (Path C clustering, 4-class invariance-fold, silhouette 0.87) is sufficient cleanliness for capability training under the sharpened gate.
3. Held-out fixture from a different finite slice (W3.2) is acceptable as falsification of overfit.
4. The W5.3 cross-corpus transfer experiment (engine-level only, no LoRA training across corpora) does NOT trip the sharpened gate, since LoRA training in v0.5 stays single-domain (W4.1 / W4.2 / W4.3 / W4.4 are all on synthetic + 17-entry).
5. Pre-filtering via `surviving_claim_morphology` (W3.7) is sufficient additional discipline given Aporia's flag that 100 of 103 kill records are A149-only and most cross-domain morphology classifies INDETERMINATE.

**If Aporia rejects:** fall-back is escalation to a pure synthetic corpus generated by Diagnostic-C with no boundary-layer mixing. v0.5 timeline extends by 1 week.

### 7.2 Techne sign-off (W2.6) — APPROVED 2026-05-05 with 4 schema additions

**Outcome (received from Techne 2026-05-05 review):** Original schema is substrate-derivable; approved with 4 additions to align with substrate v2.2 contracts. Held-out fixture generation via `lehmer_brute_force` on deg12 ±5 is queued + prioritized.

**Final schema (v2.2-aligned, pre-falsification view):**

```yaml
# pre_falsification_view (primary Learner training input — emitted to separate file path)
# All fields computed BEFORE any falsifier touches the object

# --- substrate v2.2 contract fields (additions per Techne approval) ---
coordinate_chart_id: str             # P0 reference — required for ExclusionCertificate alignment
                                     # e.g. "lehmer_deg14_palindromic_pm5_v1"
method_spec:                         # structured per v2.2 §6.2 P3 (replaces flat factor_list_strategy)
  engine: str                        # "mpmath"
  strategy: enum["direct", "factor_first"]
  precision_dps: int
  independence_class: str            # e.g. "mpmath_polynomial_factorization"
  drift_channel:
    intensional_hash: str            # code-derivation hash
    behavioural_hash: str            # I/O-fingerprint hash
stability_pass:                      # structured object per v2.2 P2 (NOT bool)
  stability_mean: float
  stability_variance: float
  perturbation_family: str           # e.g. "numeric_margin"
  worst_case_flip_rate: float
  k_used: int                        # 10 (diagnostic) / 50 (candidate) / 200 (promotion-grade)
exclusion_certificate_ref: str | None  # if part of deg14 ±5 ExclusionCertificate

# --- raw invariants (Lehmer-specific; per Q-E2 Ergon answer) ---
poly_coefficients: list[int]         # ±5 deg-14 reciprocal palindromic
mahler_measure_dps30: float
mahler_measure_dps60: float
mahler_measure_dps100: float
height: int
lead_coefficient: int
palindromicity_check: bool
n_irreducible_factors: int
cyclotomic_factor_indices: list[int]  # which Φ_n appear
cyclotomic_factor_powers: list[int]   # k in Φ_n^k
non_cyclotomic_factor_present: bool
non_cyclotomic_factor_mahler: float | None
catalog_match_type: enum["direct", "composite", "all_cyclotomic", "miss"]
boundary_layer_silhouette: float
reflection_pair_partner_hash: str | None  # x → -x invariance fold

# Label (target) — 4-class, foldable to 2 under invariance
class: enum["standard_quad_factor", "high_degree_reflection_pair",
            "phi_4_singleton", "lehmer_x_phi_n_k_composite"]
class_post_fold: enum["cyclotomic_noise", "lehmer_composite"]
```

```yaml
# post_falsification_view (gated, explanation/calibration only — emitted to SEPARATE file path)
# Loader requires explicit --allow-post-falsification flag; load logged as potential leakage event
kill_vector:                         # 12 + 8 = 20 components per v2.2 §7
  ...
evidence_field:                      # per v2.2 §6.2 P1
  distance_to_target: ...
  battery_survival_depth: ...
  verification_depth: ...
  exclusion_distance: ...            # populated only if ExclusionCertificate exists
  assumption_load: ...
  computational_friction: ...        # populated by Techne Pre-Tier-0 0b telemetry
  axis_confidence: dict
triangulation_path: ...
caveats: list
```

**What Techne approved (verbatim from 2026-05-05 review):**
> Schema is substrate-derivable as written; needed extensions to match v2.2... The factor_list_strategy you have is correct but lives inside method_spec.strategy in v2.2. Held-out fixture from lehmer_brute_force on deg12 ±5 is supported by the bug-fixed brute-force code; that's a queued Techne item already and I'll prioritize it for your W3.2 unblock.

**Status:** Schema FROZEN for v0.5. W3.2 fixture writer adopts this exact form.

---

## 8. What survives unchanged from v8

For external reviewers reading this v0.5 doc in isolation: the following from v8 are unchanged and remain canonical:

- §1 market context (Silver $1B framing)
- §2 background sections 2.1-2.9
- §3 architectural summary (seven operator classes, agreement-weighted reward formula structure, five-counts diagnostic, defensive surface against residual-gaming attractor)
- §3.5.2-3.5.3 (coverage-pressure cell selection; periodic prior detox)
- §3.5.4 minimum proposal-share enforcement (≥5% per non-prior class)
- §3.6 null-world baselines
- §3.7 Mathlib comparison class
- §5.1-5.2 base model + three task adapters with structural decoupling
- §5.4-5.6 adversarial cycles + self-play loop + training data rings
- §6.1, 6.3, 6.4 action space + 7 mutation operator classes + feature representation
- §11 (the does-not-claim list)
- §11.5 Techne meta-loop
- §11.6 residual-gaming attractor as bear case + defensive surface
- §13 Silver-ingestion (three substrate-ingestible fragments)
- §14 20-year position
- §15 first principle ("truth stays harder to satisfy than generation is to produce")

v0.5 modifies: §4 (replaces v8's Trial 1/1.5/2/3 with W1-W6 task list), §5.3 (reward weights stay at MVP for v0.5), §6.2 (descriptor adds `dominant_failure_family`), §10 (replaces v8's three-base ablation with single-model Qwen2.5-Math-1.5B tire-kick).

v0.5 defers (to v1.0+): counterfactual logging, anti_prior KL+descriptor enforcement, trivial-pattern temporal signatures, three-base ablation, full external_llm operator with API rotation, complete agora integration.

---

## 9. v0.5 one-sentence summary

v0.5 is the Learner's first complete pass through the pipeline — substrate-grade engine hardening (kill the stub evaluator, route through BindEvalKernelV2, native KillVector telemetry, real stability check, T0-T4 confidence tiers running async, descriptor extended with `dominant_failure_family`, Trial 2 re-validated under KillVector-ranked fitness, baseline gauntlet built) running in parallel with end-to-end LoRA training pipeline construction (Qwen2.5-Math-1.5B-Instruct via Unsloth + peft + trl, training-data scaffold, eval harness) culminating in a tire-kick training run on clean data sources (synthetic ground-truth env + 17-entry Lehmer boundary layer, both Aporia-cleared and Techne-curated) plus one cross-corpus transfer experiment on OBSTRUCTION_SHAPE — six weeks total, four acceptance criteria of which two must hit, identity stays Learner per James's directional call (Foundry reframe rejected; diagnostic capabilities built inside Ergon for now), and the sprint culminates in a go/no-go decision on whether v1.0 (full corpus + RL framing + LoRA-evolution loop) is justified by what v0.5 measured.

---

## 10. Decision record (W6.5; to be filled)

*[To be completed at end of v0.5 sprint per W6.5.]*

— Ergon, on behalf of the Prometheus agent ensemble
