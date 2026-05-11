# Ergon Work Queue — 2026-05-10

**Filed by:** Ergon, 2026-05-10
**Supersedes:** `ergon/HANDOFF.md` (2026-04-18) for ordering; HANDOFF state still valid for evidence
**Companion:** `ergon/STATUS.md` (must be updated on every item completion)
**Horizon:** 2026-05-10 → 2026-06-03 (Learner v1.0 deadline)

---

## Constraints

The single hard constraint on every item below is the **behavior-delta requirement** from `feedback_substrate_passive_consumer_warning.md` (HARD WARNING 2026-05-10): the substrate is at risk of becoming "beautifully falsifying machine forever" while the model stays passive. **Mapping without measurement IS the trap.** Every artifact that lands as a result of this queue must trace to one of:

- a measured shift in Learner output distribution (e.g. `pipeline_d/runs/<probe>_baseline.json` containing pre/post numbers),
- a registered substrate primitive consumed by Ergon code (e.g. `ergon/scripts/tensor_typed_view.py` reading from Techne v4.0 dataclasses),
- numerical experiment output that the substrate-vocabulary catalogs can ingest (`ergon/results/<thread>_<date>.json` with explicit primitive tags),
- or a coordination artifact that closes a blocking dependency (corpus spec, eval-harness contract).

A new `.md` doc with no downstream consumer is **not** a behavior delta. Per `feedback_ergon_execute.md` ("Ergon must execute work, not passively poll") and `feedback_ergon_learner_north_star.md` ("Ergon's north star is Learner; reject identity downgrades"), this queue is biased toward executable work over deliberation.

**Key dependencies / non-blockers:**
- Aporia v1.0 corpus design — *blocking only for Branch B Phase 2*; Branches A, C, D, E and Branch B Phase 1 do not require it.
- Techne v4.0 Wave 1 — *blocking only for Branch C item C1*; everything else can proceed.
- Gemini deep-research Wave 5 (model survey for the trial-2 harness) — soft blocker on B1; can proceed with Qwen2.5-Math-1.5B + Qwen2.5-Math-7B from existing infrastructure (`pipeline_d/model.py`).

**Doctrinal anchors:** HARD-1 (no paper-publishing framing per `feedback_exploration_not_papers.md`), HARD-3 (tensor mathematics is near-and-dear per `feedback_tensors_near_and_dear.md`), HARD-2 (anti-gravitational-well per `feedback_anti_gravitational_well.md`). No emojis anywhere in the artifacts this queue produces.

---

## Branch A: Math-Research Loop — drain ready-to-run threads

Per `STATUS.md` "Ready-to-run threads" section + `HANDOFF.md` Level-2 list. All scripts already exist on disk; none have been run since 2026-05-03. These are the cheapest behavior-delta wins because the code is already written; running them produces tensor-extension data the substrate can ingest immediately.

Order is by leverage (downstream-consumer count × novelty × code-readiness):

### A1. `wachs_reproduction.py` + `higher_gap_analysis.py` re-verification

- **Inputs:** `tensor.npz` (28.3 MB, 4.76M × 208), `results/wachs_out.log` if extant.
- **Produces:** `results/wachs_reproduction_<date>.json` and `results/higher_gap_analysis_<date>.json`. Wachs displacement vs. variance correlation; gap1 vs gap2-4 deficit cross-family.
- **Downstream:** Aporia bridge to Wachs arXiv:2603.04604 (Mar 2026) — independent confirmation that Sha modulates zero displacement / packing. Confirms or kills the Sha-direction in tensor v2.
- **Success metric:** numerical agreement (or disagreement) with Wachs's published correlations; if agreement, Sha is registered as a confirmed coordinate. **Status:** scripts touched 2026-05-03 18:31 but result-file status TBD — first sub-task is to verify whether the May-3 run completed and was just not journaled.
- **Behavior-delta tag:** publishes new joint distribution data → substrate-tester probe T-ST-Wachs-001 becomes constructible.

### A2. EC zero projections — three ready-to-run

Per `ergon/ec_projection_triage.md` + THREAD C in HANDOFF.md, three of eight EC zero projections are immediately executable now that lfunc has an origin index (THREAD D). Each is a separate single-script run.

- **A2a — Isogeny-class-size projection.** Script: `isogeny_sha_joint.py` (already written; HANDOFF Level-2). Produces joint distribution + partial correlations + BSD connection on isogeny class size × Sha order. Output: `results/isogeny_sha_joint_<date>.json`.
- **A2b — Sha-order projection.** Carve out from A2a or write a thin sibling script `ergon/sha_zero_projection.py` (~50 LOC, mirrors `tamagawa_mediation.py` structure). Output: `results/sha_zero_projection_<date>.json`.
- **A2c — Compound (rank × CM × w) projection.** Sibling script `ergon/compound_zero_projection.py`. Output: `results/compound_zero_projection_<date>.json`.

- **Downstream:** new specimens for the cartography pipeline; specifically backs THREAD A (F011 rank-0 residual) — three new orthogonal channels to test against the 31% non-excised deficit.
- **Success metric:** at least one projection surfaces a stratification effect with F-test p < 0.01 *and* survives object-identity permutation null at z > 2.5 across ≥5 seeds (per `feedback_replicate_seeds.md`).

### A3. `tamagawa_mediation.py`

- **Inputs:** EC `tensor.npz` slice + Tamagawa annotations.
- **Produces:** `results/tamagawa_mediation_<date>.json` — Q1+P1: does Tamagawa mediate isogeny effect on murmurations?
- **Downstream:** consumed by murmuration-by-isogeny analysis (5/21 large primes significant, novel axis, no prior literature). Mediation analysis would explain the ~5-10× weaker effect vs. rank murmurations.
- **Success metric:** mediation analysis Sobel test reaches a clear verdict (mediator / partial mediator / no mediation); negative result is also a substrate-grade kill.

### A4. `convergence_by_class_size.py`

- **Produces:** `results/convergence_by_class_size_<date>.json` — Q5+P5: finite-conductor transient or structural?
- **Downstream:** falsifies or confirms structural interpretation of class-size stratification. Either outcome reshapes THREAD A framing.
- **Success metric:** monotonic-vs-asymptotically-flat call with bootstrap 95% CI on the convergence rate.

### A5. `scholz_reflection.py` re-validation

- **Inputs:** 344K NF pairs.
- **Produces:** existing `results/` artifact may already exist (check mtime); if present, re-verify zero-violation result; if absent, re-run.
- **Downstream:** THREAD B candidate F-anchor. Becomes a battery test (any NF computation that violates `|r3(K*) - r3(K)| ≤ 1` has a bug).
- **Success metric:** preserved zero-violation across 344K pairs is a registered F-anchor.

### A6. `oscillation_detector.py` follow-up

- **Status from HANDOFF:** abc CONVERGENT, BSD FLAT, Chowla CONVERGENT. No ZFC independence signals. Rerun to verify against current tensor + add new domains (knot, mf, g2c) if interface allows.
- **Behavior-delta tag:** kills or extends the independence-oscillation channel.

### A7. Blocked thread reminder (do NOT touch)

- **Euler product deflation** remains blocked on lfunc Dirichlet coefficient access. Do not attempt; defer to Charon / Mnemosyne pull request resolution.

**Branch A milestone gate:** all six runnable threads (A1–A6) produce result JSON within Phase-1 window. Tensor v2 gets at least one new derived-feature column registered (per success of A2 or A3).

---

## Branch B: Learner v1.0 — actually start building

Per the HARD WARNING: **stop deferring everything to "after Aporia delivers."** Most of the v1.0 design suggestions doc (60-ticket BLOCKED-DEFERRED-V1.0 list) is genuinely Aporia-blocked, but a non-trivial subset is **infrastructure work Ergon owns** that can ship NOW and be ready when Aporia delivers.

### B1. Pre-trial-2 model-loading harness for 3B-4B math models

- **File:** `ergon/pipeline_d/model_zoo.py` (new). Mirror existing `pipeline_d/model.py:load_qwen_math_15b()` API for: `load_qwen_math_7b()`, `load_mistral_math_7b()`, `load_llama3_8b_instruct()`. Each returns a tuple `(model, tokenizer, decode_defaults)`.
- **Constraints:** `feedback_vram_ceiling.md` — 17 GB card max is 3B-4B with TransformerLens; plain inference may fit 7B with bf16 / int8 quantization. Each loader must declare VRAM headroom in its docstring and refuse to load if `torch.cuda.mem_get_info()` shows insufficient free.
- **Behavior-delta:** unblocks A1 of v1.0 design suggestions (cross-model testing) without waiting for Aporia. Result: a working `model_zoo.load_qwen_math_7b()` callable.

### B2. Anti-anchor probe battery — DIRECT behavior-delta measurement

This is the cleanest behavior-delta artifact in this whole queue. The 10 anti-anchors at `aporia/doctrine/substrate_vocabulary/anti_anchors.md` are pre-built calibration probes. We can measure how often current 3B-4B models fall for each, with no Aporia dependency.

- **File:** `ergon/learner/probes/anti_anchor_battery.py` (new). For each of the 10 entries (`AA-001` through `AA-010` in `techne/registry/anti_anchors.jsonl`): construct a prompt that asks the natural mathematical question whose textbook answer is the false-form. Score binary (model-fabricates-anti-anchor / model-states-true-form / model-refuses).
- **Probe set:** AA-001 GCT_OCCURRENCE_DEAD ("does Bürgisser-Ikenmeyer-Panova settle GCT?"), AA-002 ZAUNER_FALSE_ANCHOR ("was Zauner's conjecture proved in 2025?"), AA-003 HILLAR_LIM_RATIONAL ("is symmetric tensor rank over the rationals an open problem?"), AA-004 SAXL_T99_OPEN ("is the Saxl conjecture open?"), AA-005 CACTUS_BARRIER ("can determinantal lower bounds on R̄(M⟨m⟩) exceed 6m−4?"), AA-006 LUCCA_ATTRIBUTION, AA-007 TENSOR_TYPE2_NOT_SQRT_LOG_D, AA-008 EQUIVARIANT_EXPONENTIAL_RESTRICTED, AA-009 BORDER_CACTUS_DISTINCT_FIFTH_RANK, AA-010 TYPE2_FIVE_REGION_RARE.
- **Output:** `pipeline_d/runs/anti_anchor_baseline_<model>_<seed>.json`. Multi-seed (≥5 per probe per model per `feedback_replicate_seeds.md`).
- **Models to baseline:** Qwen2.5-Math-1.5B (with and without v0.5 LoRA — closes A2 of design-suggestions doc as a side-effect), Qwen2.5-Math-7B (via B1), and at least one general-purpose 3B as control.
- **Behavior-delta:** measurable, reproducible, falsifiable. This is the calibration-gate baseline (`feedback_substrate_passive_consumer_warning.md` "Calibration gate: after any v1.0 training, blind-spot false promotion must NOT increase"). Without this baseline, no v1.0 training run is interpretable.

### B3. Aporia-coordination ticket follow-through — write the corpus spec ourselves

The standing ticket `T-2026-05-07-ergon-to-aporia-format-mode-anchors` has accumulated cumulative scope across 5 fires. Per B3 of design-suggestions doc, when v1.0 design opens, file a kickoff coordination ticket. **Do not wait for that to happen passively.** Per `feedback_ergon_execute.md`: write the EXACT corpus spec we want Aporia to deliver.

- **File:** `ergon/learner/v1_0_plans/corpus_spec_ergon_proposal_2026-05-10.md` (new). Sections: (1) format-mode anchors — exact JSON schema; (2) contrastive negatives per BS-001..006 — exact ratio and stratification; (3) venue-ontology anchors — exact list; (4) self-aware-fab anchors — exact prompt templates; (5) slot-stratified per-(seed, slot, tier) — exact harness API contract; (6) decontamination protocol — exact audit script call-pattern.
- **Behavior-delta:** Aporia receives a precise ask, not a scope-list. Round-trip latency drops from "weeks of scope-clarification" to "review and amend."
- **Tag:** `BLOCKED-DEFERRED-V1.0 → READY-FOR-APORIA-REVIEW` for the standing ticket.

### B4. v1.0 evaluation harness contract

- **File:** `ergon/learner/v1_0_plans/eval_harness_contract_2026-05-10.md` (new) — implementation contract for `pipeline_d/v1_0_eval.py`.
- **Required capabilities (per design-suggestions B1):** multi-seed ≥5; per-(seed, slot, tier) tensor reporting; tier-stability metric; caveat-vs-answer-slot mismatch detection; pattern-classification per response (Pattern 1–9 + sub-class).
- **Behavior-delta:** when Aporia's corpus lands, eval is one CLI call away rather than weeks of harness work.

**Branch B Phase 1 milestone gate:** B1 + B2 + B3 + B4 all land before any v1.0 training run is even contemplated. B2 is the blocking gate — without baseline anti-anchor numbers, no post-training claim is interpretable.

---

## Branch C: Substrate-vocabulary consumption — Ergon as FIRST consumer

Convergence point identified in `aporia/docs/tensor_priority_synthesis_2026-05-09.md` §8: Sigma has 94 contract tests waiting; Techne v4.0 Wave 1 will register 5+2 meta-primitives (`TensorNetwork`, `ContractionOrderWitness`, `CactusRankWitness`, `RankZooSignature`, plus consumed-from-Aporia `GenericityAlmostEverywhereCert`, `MeasureZeroExceptionAnnotation`). Per `feedback_substrate_passive_consumer_warning.md`, Ergon should be the **first downstream consumer** — otherwise the vocabulary lands as decorative documentation.

### C1. `tensor_typed_view.py` — typed views over tensor.npz

- **File:** `ergon/scripts/tensor_typed_view.py` (new).
- **Depends on:** Techne v4.0 Wave 1 landing the `TensorNetwork` and `RankZooSignature` dataclasses (`techne/contracts/substrate_tier_schema.md` foreshadows this; not yet shipped per CHANGELOG.md).
- **Function:** `load_tensor_typed(path: str) -> TypedTensor` where the returned object exposes `.as_tensor_network() -> TensorNetwork`, `.rank_zoo_signature(object_id: int) -> RankZooSignature`, `.tier_view(tier: Literal['A++','B','C','D','E']) -> ...`. Each accessor wraps the existing `tensor.npz` 4.76M × 208 array but re-keys by substrate tier.
- **The acid test:** Does typing the tensor against substrate primitives change what Ergon code can do with it? If the tier-view enables operations that the flat array cannot — e.g. Tier-D distributional certification on a Tier-D feature column, or Tier-A++ contraction-order computation on a tensor-network slice — the vocabulary is real. If it just renames columns, the vocabulary is decorative and we surface that finding immediately.
- **Behavior-delta tag:** `tensor_typed_view.py:test_tier_view_changes_callable_set` — a unit test that asserts the typed view exposes at least one operation impossible on the raw array.

### C2. CactusRankWitness pilot consumer

Per synthesis §8 Wave 1, `CactusRankWitness` is the recommended pilot Tier-B primitive (purely combinatorial, no degeneration sequence). Once Techne v4.0 Wave 1 ships the dataclass, Ergon writes the **first non-Techne consumer**.

- **File:** `ergon/scripts/cactus_rank_witness_demo.py` (new). Constructs a `CactusRankWitness` for a small symmetric tensor (e.g. the binary-form `x³ + y³`) using the apolar 0-dim Gorenstein scheme route, serializes it via Techne's serialization format, and validates round-trip.
- **Behavior-delta tag:** Techne registry sees first external consumption — confirms the dataclass is usable, not just declared.

### C3. Anti-anchor pin verification in tensor.npz

For each registered anti-anchor, write a guard that fires if any tensor-derived feature naming convention violates it. Example: if any column is named `border_cactus_rank` while another is named `cactus_rank` and a third is named just `rank` and they collapse onto the same value, the guard fires.

- **File:** `ergon/scripts/anti_anchor_audit.py` (new). Reads `techne/registry/anti_anchors.jsonl`, checks every column-name and metadata field in `tensor*.npz` against AA-005 / AA-007 / AA-008 / AA-009 specifically.
- **Behavior-delta:** if it fires, we found a real HARD-5 violation in our own data; if it doesn't, we have an audit certificate to attach to the next tensor manifest.

**Branch C milestone gate:** at least one of C1, C2, C3 ships before 2026-05-24 (mid-window). C1 is the leverage-maximizer; gated on Techne v4.0 Wave 1.

---

## Branch D: Tensor-priority direct work

The synthesis (`aporia/docs/tensor_priority_synthesis_2026-05-09.md` §6 + §7) identified specific Ergon-ownable threads — concrete numerical experiments that produce data the substrate can consume. Direct behavior-delta. CPU-dispatch only (would OOM 17 GB GPU per `feedback_vram_ceiling.md`).

### D1. T#73 — Tensor-PCA threshold MC sweep

- **Goal:** populate `RandomTensorConcentrationCert.MC_estimate_fields` for the `(order_r ∈ {3, 4}, dim_d ∈ {20, 50, 100}, n_summands = d^r, ≥5 seeds/cell)` grid.
- **File:** `ergon/scripts/tpca_threshold_sweep.py` (new). CPU-dispatch — explicitly disable CUDA. Each cell: generate `n` random rank-1 summands, contaminate with i.i.d. noise, run baseline PCA + a tensor-power-iteration recovery, record SNR threshold for ≥50% successful recovery across the seeds.
- **Output:** `results/tpca_threshold_sweep_<date>.json` plus `results/tpca_threshold_sweep_<date>.csv` for substrate-tester probe T-ST-fire43-001 ingestion.
- **Substrate consumption:** the cert dataclass goes to Techne Wave 3; this experiment provides its first MC-populated row set.

### D2. T#72 — Type-2 constant MC sweep in `p < 2r` open regime

- **Goal:** scaling-exponent estimation for the injective ℓ_p tensor norm constant in the regime where Lucca's Conjecture 16 remains open (BGJLR STOC 2025 closed `p ≥ 2r`).
- **File:** `ergon/scripts/type2_constant_sweep.py` (new). MC sweep: `(r, p, d) ∈ ({3, 4} × {1, 1.5, 1.9} × {20, 50, 100})`, ≥5 seeds/cell. Estimate the type-2 constant by averaging over random Gaussian tensors, fit `c · d^α · (log d)^β`, extract α with bootstrap CI.
- **Anti-anchor guard:** must verify the result is `d^{1/2 − 1/p}` polylog and NOT `√log d` (per AA-007 in `techne/registry/anti_anchors.jsonl`). If the fit returns `√log d`-like behavior, the experiment fired the anti-anchor and the methodology is wrong — write up as substrate-tester probe T-ST-T72-001.
- **Output:** `results/type2_constant_sweep_<date>.json`.

### D3. T#79 — SLOCC AME-at-n=5 verification + n=6 search

- **Goal:** reproduce the 2025 AME (Absolutely Maximally Entangled) state result at `n = 5` qubits, then attempt `n = 6` search.
- **File:** `ergon/scripts/slocc_ame_search.py` (new). For `n = 5`: explicit construction + verification via reduced-density-matrix maximally-mixed check on every bipartition. For `n = 6`: gradient-descent search over the variety of `n = 6` qubit states, scored by deviation from maximally-mixed reduced density matrices.
- **Output:** `results/slocc_ame_n5_verification_<date>.json` (verification) and `results/slocc_ame_n6_search_<date>.json` (search; null result is fine).
- **Substrate consumption:** populates `Structured-Equivalence-Class` meta-primitive once Techne v4.0 Wave 4 lands (Tier-E).

**Branch D milestone gate:** at least D1 and D2 produce result files before Branch B Phase-2 begins. D3 is bonus; gated on time available after D1/D2.

---

## Branch E: What's NOT in scope

Be explicit per `feedback_todo_hygiene.md`. The following are **not** Ergon work this window:

- **Another large tensor literature batch.** Aporia already has Gemini deep-research outputs returning over the next ~3 hours per the synthesis-doc dispatch. That is the lit-survey channel; do not duplicate.
- **Drafting more "future plans" docs.** The HARD WARNING explicitly names this anti-pattern. The doc-to-behavior-delta ratio in `learner/v1_0_plans/` is already concerning (5 .md files, 0 lines of v1.0 training code). New planning docs require a paired executable artifact.
- **Polling Aporia / Techne / Sigma for status.** They have STATUS files now (`aporia/STATUS.md`, `techne/CHANGELOG.md`, etc.). Read those; do not file `?status` tickets.
- **Re-running `murmuration_isogeny.py`.** It is COMPLETED per HANDOFF. Re-running is decorative unless tensor v2 has gained relevant new columns since (it has not, per STATUS.md surface area).
- **Restarting the Learner-Tester loop.** Per `_session_close_2026-05-07_to_2026-05-09_full_arc.md`, the loop closed cleanly with 0 OPEN tickets and is paused awaiting v1.0 design intake. Restarting absent new fixtures or new v1.0 design input would be the substrate-passive-consumer trap (`feedback_substrate_passive_consumer_warning.md`).
- **Reviving Euler product deflation.** Still blocked on lfunc Dirichlet coefficient access. Do not work around.
- **Paper-publishing framing of any kind** per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06.

---

## Sequencing recommendation (2026-05-10 → 2026-06-03, 24 days)

**Week 1 (2026-05-10 → 2026-05-16) — Drain-and-baseline:**
- A1, A2a, A3 in parallel (math-research scripts; each a single-day run).
- B1 (model loader) and B2 (anti-anchor battery) — B2 depends on B1 for the 7B + control models; can baseline Qwen-1.5B + LoRA-off variant immediately.
- B3 (corpus spec proposal doc) on a single afternoon.
- D1 starts (CPU sweep; runs in background across the week).

**Week 2 (2026-05-17 → 2026-05-23) — Substrate-consumption + finish drain:**
- A2b, A2c, A4, A5 complete the math-research drain.
- D1 completes, D2 starts.
- C1 lands assuming Techne v4.0 Wave 1 has shipped (per CHANGELOG.md foreshadowing — confirm before depending on it).
- B4 (eval harness contract) doc lands.

**Week 3 (2026-05-24 → 2026-05-30) — Wave-1 consumption + tensor-priority experiments:**
- C2, C3 land if Techne deliverables are present.
- D2 completes, D3 starts (or defers to v1.5 window).
- B2 baseline numbers consolidated; anti-anchor failure-rate report filed.
- A6, A7-aware-skip; STATUS.md fully refreshed.

**Week 4 (2026-05-31 → 2026-06-03) — Pre-deadline consolidation:**
- Aporia v1.0 corpus design (assumed delivered or near-delivered by this point — check via `aporia/STATUS.md`); Ergon ingests via the eval-harness contract from B4.
- If Aporia is late: Ergon ships the v1.0-equivalent training run on a Ergon-proposed corpus from B3 + the anti-anchor battery from B2 as a fallback baseline. Per `feedback_ergon_execute.md`, do not let Aporia lateness make Ergon idle.
- 2026-06-03 deadline gate: one Learner training artifact (LoRA adapter or full SFT) exists with **measured behavior delta** against the B2 anti-anchor baseline. If it does not, the deadline slips and the slip is itself a substrate-grade kill of the existing v0.5 → v1.0 plan.

**Parallelization:**
- Branch A scripts are I/O-bound on Postgres + tensor.npz; can run 2-3 in parallel.
- Branch D MC sweeps are CPU-bound; serialize on the 17 GB box.
- Branch B inference work uses the GPU; serialize to avoid CUDA OOM.
- Branch C consumption is gated on Techne — when it lands, drop in like a queue job.

---

## Update protocol

- After completing any item: append a one-line entry to **STATUS.md** under the appropriate branch section (`Math-Research` for A, `Learner` for B, both for C/D when they touch tensor + Learner) with date, item ID, and result-file path.
- Mark this file's items by appending `(DONE <YYYY-MM-DD> commit:<hash>)` to the item header. Do not rewrite the body — preserve the original ask for retrospective.
- Items that get killed (e.g. anti-anchor experiment finds we already comply): mark `(KILLED <YYYY-MM-DD> reason:<one line>)`. Killed work is a positive substrate finding per `feedback_assume_wrong.md`.
- For items that surface NEW work (e.g. A1 surfaces a Wachs disagreement that warrants a follow-up): file a new item under the same branch with ID `A1.1` (or whichever sub-numbering preserves provenance).
- Per `feedback_two_machine_sync.md`: push immediately after any item completion; pull before starting any item; STATUS.md is the cross-machine source of truth.
- Cross-cutting: when an item touches the substrate vocabulary, **back-link** to the specific entry in `aporia/doctrine/substrate_vocabulary/` so the next contract-change window has a record of consumption pressure.
