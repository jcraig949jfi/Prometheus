# v1.0 Design Suggestions — Next Steps Tracker

**Filed by:** Ergon, 2026-05-09
**Inputs:** 12-fire loop arc 2026-05-07 → 2026-05-09 (`_session_close_2026-05-07_to_2026-05-09_full_arc.md`); 12 pre-registered hypotheses across `single_fact_decomposition_ablation.md` and `tester_findings_consolidated.md`; standing Aporia coordination ticket `T-2026-05-07-ergon-to-aporia-format-mode-anchors`
**Status:** Suggestions doc. NOT v1.0 design itself. Surfaces what the v1.0 design phase should address; James reviews + chooses scope.

This document is organized as **(A) user's tracked items** + **(B) Ergon's additional suggestions** + **(C) sequencing & priority** + **(D) open questions for James**.

---

## A. User-tracked items (5)

### A1. Testing against other models

**Goal:** determine whether v0.5's failure modes (Pattern 9 format-mode-leak, BS catalog, fire-variable variance, etc.) are **Qwen2.5-Math-1.5B-specific** or **model-class-general.**

**Concrete approach:**
- Hold the probe set constant: Charon's confirmed BS catalog (BS-001 Cohen + BS-003 Helfgott + BS-004 Faltings + BS-005 McKay + BS-006 Margulis) + the 6 PA-001 → PA-006 ablation probes + a sample of the 60-ticket deferred backlog (e.g., 20 stratified by Pattern 1/3/6/9).
- Hold decode params constant: greedy + `repetition_penalty=1.05` + `max_new_tokens=192`.
- Comparison axis (model):
  - **Qwen2.5-Math-1.5B-Instruct** (current v0.5 baseline; with LoRA off — see A2)
  - **Qwen2.5-Math-7B-Instruct** (if VRAM permits per `feedback_vram_ceiling.md`; 17GB card max is 3B-4B, so 7B may OOM with TransformerLens but should work for plain inference)
  - **Mistral-7B-Math** (different family, same scale; or whichever 3B-7B math model is on HuggingFace)
  - **Llama-3-8B-Instruct** (general-purpose, not math-specialized — control)
  - Optional: a frontier API model (Sonnet 4.6 or GPT-4o) on a *small subset* — to set ceiling reference
- Per-(model, probe, mode, seed=5) measurements (per §5b.8 multi-seed requirement).

**What it answers:**
- Is Pattern 9 format-mode-leak a **Qwen-pretraining-corpus artifact** (Qwen-only) or a **general failure mode** (all models)?
- Is the BS catalog **Qwen-specific** (model has weak prior on Cohen/Faltings/etc.) or **model-class-general** (all sub-7B models miss these)?
- Does **model size** matter? Qwen-1.5B vs Qwen-7B should reveal scale effects on Pattern 9 sub-classes 9.A/9.B and Pattern 6 abbreviation-loop.
- Does **math specialization** help? Compare Qwen-Math vs general Llama on attribution probes.

**Cross-reference to existing findings:**
- §5b.7 cross-pattern rep_penalty orthogonality — re-test whether other models also have decode-time-resistant Pattern 6/9/1.B sub-classes
- §5b.11 5-tier recoverability scale — does the tier distribution differ across models?
- §5b.12 fire-variable tier — is tier-stability higher for larger models?

**Implementation owner:** Ergon (pipeline_d/) once v1.0 design opens.
**Estimated scope:** ~1 week for inference runs across 4 models on ~50 probes × 2 modes × 5 seeds = 2000 inferences; analysis + writeup ~3 days.

---

### A2. Testing model WITH vs WITHOUT LoRA

**Goal:** **causally isolate what the v0.5 LoRA does.** Currently `ergon/pipeline_d/model.py:load_qwen_math_15b(use_lora=True, rank=8)` is the default; we've never run the same probe set with `use_lora=False` to compare.

**Concrete approach:**
- Same probe set as A1 (BS catalog + PA-001..006 + deferred-backlog sample).
- Same decode params.
- **Single axis: `use_lora=True` vs `use_lora=False`** on the same Qwen2.5-Math-1.5B base.
- Per-(probe, mode, lora_state, seed=5) measurements.

**What it answers:**
- Does the v0.5 LoRA **help / hurt / no-effect** on:
  - Pattern 1 attribution-fab (BS catalog) — expectation: minimal effect; LoRA was trained on 17-entry boundary layer, not BS topics
  - Pattern 9 format-mode-leak — expectation: minimal effect (LoRA didn't see format-mode anchors)
  - PA-005 Goldbach (E007 +0.50 ON-mode improvement) — expectation: LoRA might explain part of the improvement
  - Synthetic-null gate behavior — expectation: LoRA-off should pass null gate trivially
- Is the v0.5 LoRA acting as a **soft prior** or a **hard pattern overwriter**?

**Risk / discipline:**
- Per `feedback_assume_wrong.md`: assume the v0.5 LoRA does **nothing useful** until the WITH/WITHOUT comparison shows otherwise. This is the cheapest discipline test.
- If WITH/WITHOUT comparison shows **no measurable difference**, the v0.5 LoRA is decorative — that's a substrate-grade kill that should reshape v1.0 LoRA design.

**Implementation owner:** Ergon (pipeline_d/) once v1.0 design opens.
**Estimated scope:** ~3-4 days (single model, two configurations, same probe infrastructure as A1).
**Could run in parallel with A1.**

---

### A3. Loading attack vectors / problem-solving techniques into LoRA

**Goal:** **expand the LoRA training corpus** beyond v0.5's 17-entry boundary-layer fixture to include:
- **Attack vectors** (adversarial probe shapes that surface failure modes)
- **Problem-solving techniques** (the *methods* mathematicians use, not just the *answers*)

**Concrete approach (attack vectors):**
- Source: the 60-ticket deferred backlog is itself a catalog of attack vectors. Each tester probe + the model's failure mode is an attack-vector training pair.
- Per §5b.8.1.1 BS catalog: 5+ confirmed BS topics need contrastive negative anchors (≥3-5 per BS = 15-30+ anchors).
- Per §5b.10 FM-14: ~10-15 self-aware-fab anchors (prompt elicits hedge+fab; positive answer is refusal-only).
- Per §5b.9 FM-04: 5-10 venue-ontology anchors (arXiv = preprint server, NOT university; etc.).
- Per Aporia standing coordination ticket cumulative scope: format-mode + contrastive negatives + venue-ontology + self-aware-fab + slot-stratified + per-(seed, slot, tier).
- **Total estimated v1.0 corpus size:** 100-200 anchors (vs v0.5's 17). This is a **5-10× corpus expansion**.

**Concrete approach (problem-solving techniques):**
- Catalog mathematical techniques as **first-class training units**:
  - Forcing (Cohen technique for set-theoretic independence)
  - Faltings's algebraic-geometric methods (Mordell conjecture)
  - Helfgott's circle method (ternary Goldbach)
  - Mass formula / Selberg trace
  - Probabilistic method
  - Discharging method (4-color theorem)
  - Polymath techniques
  - Iwasawa theory
  - Schemes / cohomology
- For each technique: training pairs of (problem-class → technique-name → high-level outline → key lemma → final result).
- The **technique** is a separate training axis from the **specific theorem**.

**What it answers / changes:**
- Does the model improve on Pattern 4 stating-vs-proving conflation when training pairs include technique-decomposition?
- Does the BS catalog shrink when training pairs explicitly link prover (Faltings) to technique (algebraic-geometric methods on Arakelov surfaces) to result (Mordell conjecture)?
- Does Pattern 8 arithmetic-internal-inconsistency improve when CoT-style step-by-step examples are in the corpus?

**Cross-reference:**
- §5b.8.1.1 v1.0 corpus implication: contrastive training pairs needed.
- §1 Pattern 4 hypothesis #1: chain-of-thought training was already filed in tester findings consolidated.

**Implementation owner:** Aporia (corpus design) + Ergon (LoRA ingestion). Coordination via existing standing ticket.
**Estimated scope:** corpus design ~2 weeks; LoRA training runs ~1 week per configuration; multi-seed eval ~1 week.

---

### A4. Loading "how solved problems were solved" — step-by-step process exemplars

**Goal:** **train the model on the WORKED-PROBLEM REASONING SHAPE**, not just the final answer. This addresses Pattern 4 (stating-vs-proving conflation) and Pattern 8 (arithmetic-internal-inconsistency) directly.

**Concrete approach (corpus shape):**
- For each problem in the v1.0 corpus, include 3 layers:
  1. **Statement** (the problem in plain language)
  2. **Worked solution** (full step-by-step reasoning, with explicit verification at each step)
  3. **Final boxed answer** (the bare result)
- Critically: **include verification steps** within the worked solution. Per §1 Pattern 8 hypothesis #1 (chain-of-thought verification training): "step 5: 1.207 ≈ 0.8536 — check: |1.207 - 0.8536| = 0.353, not negligible — STOP, error in chain."
- Include **failed-attempt traces** alongside successful ones, with the failure-recognition-and-recovery step shown explicitly.

**Source corpora candidates:**
- **Putnam / IMO archives** — well-documented worked solutions for competition problems
- **AoPS (Art of Problem Solving) wiki** — community worked solutions
- **MathOverflow / Math.StackExchange** — Q&A with detailed answers
- **Lean / Coq formalizations** — fully verified step-by-step proofs (highest verification quality)
- **Textbook exercise solution manuals** (with permission/license check)

**Quality stratification:**
- **Tier 1 (highest quality):** Lean/Coq formalized proofs — every step machine-verifiable.
- **Tier 2 (high quality):** AoPS/Putnam worked solutions — human-verified, expert-authored.
- **Tier 3 (variable quality):** Math SE / MathOverflow — mixed quality, needs filtering.
- v1.0 should weight Tier 1 + Tier 2 most heavily.

**Cross-reference:**
- §5b.10 FM-14 self-aware-fab — worked-solution training pairs that include "I tried X, that didn't work because Y, so I tried Z" teach the model how to USE its uncertainty signal, not just emit it as parallel hedge.
- §5b.11 slot-stratified training + §5b.12 fire-variable tier — worked-solution training touches multiple slots simultaneously (statement, technique, intermediate, final).

**Implementation owner:** Aporia (corpus curation) + Ergon (LoRA ingestion + worked-solution-format SFT).
**Estimated scope:** corpus curation ~3 weeks (the bottleneck — quality > quantity); LoRA training ~1 week.

---

### A5. Difficulty gradient — simple → extremely difficult math problems

**Goal:** **stratify the v1.0 corpus and evaluation harness by problem difficulty.** Avoid the trap where v1.0 LoRA improves on hard probes (BS catalog) but regresses on easy probes (Petersen graph chromatic-3).

**Concrete approach (difficulty tiers):**
- **Tier 0 — Trivial** (must NEVER fail post-v1.0): "What is 2+2?" / "What is the chromatic number of the Petersen graph?" / known closed-form constants
- **Tier 1 — Standard undergraduate**: Calculus, linear algebra, basic real analysis, intro number theory
- **Tier 2 — Advanced undergraduate / early graduate**: Galois theory, algebraic topology, measure theory
- **Tier 3 — Graduate qualifying-exam level**: Algebraic geometry basics, functional analysis, ODE/PDE classics
- **Tier 4 — Research / specialized**: Modular forms, deformation theory, geometric group theory, étale cohomology
- **Tier 5 — Open / frontier**: Riemann hypothesis status, BSD ranks, Langlands correspondences, recent (last 5 years) papers
- **Tier 6 — Unsolved**: Twin primes infinitude, P vs NP, Goldbach (binary), CH-dependent statements

**Per-tier evaluation harness:**
- Tier 0 + Tier 1: **regression gate** — v1.0 must achieve ≥99% on these. If v1.0 regresses on simple problems, that's a synthetic-null-gate-style failure (over-fitting to attribution corpus).
- Tier 2 + Tier 3: **uplift target** — v1.0 should show measurable improvement over v0.5 baseline.
- Tier 4 + Tier 5: **exploration target** — substrate-grade kills are expected here; the goal is that the failures are *substrate-informative* (yield new findings) not *random*.
- Tier 6: **calibration target** — v1.0 should output "I don't know" or "open problem" reliably (per §5b.10 FM-14: uncertainty-signal-propagation training).

**Cross-reference:**
- §5b.11 slot-stratified evaluation — per-tier metrics extend the per-slot metrics.
- The §5b.8 multi-seed requirement (≥3-5 seeds per probe) applies per-tier; tier-stability metric (§5b.12) becomes a per-tier metric too.

**Implementation owner:** Aporia (probe curation per tier) + Ergon (eval harness + per-tier metrics).
**Estimated scope:** probe curation ~2 weeks (overlaps with A4 corpus curation); eval harness ~1 week; multi-seed run ~1 week.

---

## B. Ergon's additional suggestions (7)

### B1. v1.0 evaluation harness specification (load-bearing prerequisite)

The §5b.8 + §5b.11 + §5b.12 findings imply a specific evaluation-harness shape. Before any v1.0 training run, the eval harness must support:
- **Multi-seed inference** (≥5 seeds per probe-mode)
- **Per-(seed, slot, tier) tensor reporting** (per §5b.12)
- **Tier-stability metric** (% seeds same-tier per probe, per §5b.12)
- **Caveat-vs-answer-slot mismatch detection** (per §5b.10 FM-14)
- **Pattern-classification per response** (which of Pattern 1-9 fired, with sub-class labels)

**Suggestion:** spec the v1.0 eval harness BEFORE corpus curation. The corpus design depends on what we can measure. ~1 week design + ~2 weeks implementation.

### B2. Synthetic-null gate v1.0 adaptation

W4.0's synthetic-null gate was designed for the v0.5 17-entry boundary-layer fixture. v1.0's 100-200 anchor corpus needs its own null gate. Open question: **can label-shuffle still detect memorization on a corpus this large?** Statistical power may differ.

**Suggestion:** before v1.0 training, run a methodology-validation experiment: generate a synthetic-null v1.0-style corpus (same shape, shuffled labels) and confirm the null gate FIRES at expected rate. If not, redesign.

### B3. Cross-pillar coordination protocol formalization

The standing Aporia coordination ticket grew its scope across 5 fires (8, 9, 10, 11, 13). Cumulative scope: format-mode + contrastive + venue-ontology + self-aware-fab + slot-stratified + BS catalog + per-(seed, slot, tier). This is a **comprehensive v1.0 corpus design input** — but needs a **formal handoff protocol** when v1.0 design phase opens.

**Suggestion:** when v1.0 design opens, file a kickoff coordination ticket that consolidates all cumulative scope-additions into a single Aporia-actionable design ask. Avoid losing context across the scope-expansion history.

### B4. LoRA hyperparameter ablation (rank, alpha, target modules)

v0.5 used `rank=8`. We have NEVER ablated rank — per `feedback_assume_wrong.md`, assume rank=8 is wrong until proven. v1.0 should include:
- Rank sweep: 4 / 8 / 16 / 32
- Alpha sweep: alpha=rank vs alpha=2×rank vs alpha=4×rank
- Target-module ablation: q_proj only vs q+v vs all linear

**Suggestion:** scope this as a sub-experiment within v1.0 (not an independent campaign). Use the smallest reliable probe set to keep compute bounded. ~1 week.

### B5. Curriculum ordering question (open from fire 7)

Fire 7 BOTH-SKIP P-056 Lefschetz observation hinted that decomposition vacuity occurs when topic-prior is absent — implies Pattern 3 corpus may need to come UPSTREAM of Pattern 1 corpus in training curriculum. **Open question, no evidence for or against.**

**Suggestion:** include curriculum-ordering as an explicit v1.0 design decision: train Pattern 3 first then Pattern 1, vs train interleaved. A/B compare. ~1 week.

### B6. Contamination protocol for v1.0 corpus

HARD-4 (calibration anchors load-bearing) implies v1.0 corpus must be **decontamination-verified**: no probe in the v1.0 evaluation set can appear in the v1.0 training corpus. Aporia signed off on v0.5 17-entry as non-contaminated (W2.5 in task list). v1.0's 100-200 anchor corpus needs the same sign-off but at higher complexity.

**Suggestion:** before v1.0 training, run `aporia/scripts/decontamination_audit.py` (or equivalent) on the v1.0 corpus against the v1.0 eval set + the BS catalog probes. Produce a contamination-free certificate.

### B7. Long-term tracking: BS catalog growth rate

The BS catalog grew 2 → 5 in one fire (fire 13). Per fire-3-saturation-prediction-failure lesson, we should NOT estimate total BS count. But we SHOULD track the catalog growth rate over time. If v1.0 LoRA + corpus is effective, we'd expect the BS catalog growth rate to **slow** post-v1.0 (model can recover more probes that were previously BS).

**Suggestion:** add a v1.0 success metric: "BS catalog growth rate (new BS confirmed per 100 tester probes) drops by ≥50% post-v1.0 vs v0.5 baseline." Falsifier: if rate doesn't drop, v1.0 corpus is missing the right anchors.

---

## C. Sequencing & priority

**Phase 1 (parallelizable, ~2 weeks):**
- A2: WITH/WITHOUT LoRA comparison (cheap, fast, high-information)
- B1: v1.0 eval harness spec
- B6: contamination protocol design

**Phase 2 (post-Phase-1, ~3-4 weeks):**
- A1: cross-model testing (reuses A2 infrastructure)
- A3 + A4 + A5: corpus curation + difficulty stratification (Aporia-led, Ergon ingests)
- B3: cross-pillar coordination kickoff

**Phase 3 (v1.0 training, ~2-3 weeks):**
- B2: synthetic-null gate v1.0 validation
- v1.0 LoRA training runs
- B4: LoRA hyperparameter ablation
- B5: curriculum ordering A/B

**Phase 4 (v1.0 evaluation, ~2 weeks):**
- Per-tier evaluation per A5
- Multi-seed evaluation per §5b.8
- BS-catalog post-v1.0 measurement (B7)
- Synthetic-null gate post-training verification

**Total estimated:** ~10-12 weeks for the full v1.0 cycle assuming no major findings derail the plan.

**Cheapest first wins (per `feedback_infrastructure.md`):**
- A2 (WITH/WITHOUT LoRA): **highest information per compute spent.** If LoRA does nothing, that's a major v1.0 design pivot.
- B1 (eval harness spec): **gates everything else.** Without it, every measurement is single-seed and unreliable.
- A1 (cross-model): **answers the "is this Qwen-specific" question** that determines whether v0.5 findings generalize.

---

## D. Open questions for James (need direction)

1. **Compute budget per phase.** Multi-seed eval across 4 models × 50 probes × 5 seeds × 2 modes = 2000 inferences just for A1. v1.0 LoRA training runs (multiple ranks, multiple curricula) could be 5-10 GPU-days. What's the budget envelope?

2. **Frontier-API ceiling reference.** Do we want a small comparison run on a frontier API (Sonnet 4.6 / GPT-4o) to set a ceiling reference for the BS catalog probes? Per `feedback_rate_limits.md` (assume APIs throttle), this needs to be a deliberately-small subset.

3. **Aporia handoff timing.** When does v1.0 design phase formally open? The standing coordination ticket has accumulated scope across 6 fires; a formal handoff would let Aporia begin corpus design. Is there a gating event (Charon round-N close, James review, etc.)?

4. **RLVF scope.** §5b.10 FM-14 metacognitive-propagation training implies RLVF (reward shaping for caveat-vs-answer-slot mismatch). Is RLVF in v1.0 scope, or v1.5+ phase?

5. **Difficulty-tier source corpus.** A4 + A5 list candidate sources (Putnam/IMO/AoPS/Lean/Coq/MathOverflow). Which sources are in-scope for v1.0? Lean/Coq formalizations are highest-quality but smallest; Math.SE is largest but variable quality.

6. **Cross-model testing scope (A1).** Which models are the priority? Qwen-1.5B vs Qwen-7B alone is ~80% of the information for ~30% of the compute. Adding Mistral-7B-Math + Llama-3-8B doubles the compute for ~20% additional information.

7. **A4 worked-solution corpus license check.** Putnam / AoPS / MathOverflow have varying licenses. Need legal/compliance check before training. This isn't an Ergon scope question — needs your call.

---

## E. What this document is NOT

- **NOT** a v1.0 design — that's the v1.0 design phase output.
- **NOT** a research paper outline (per HARD-1 no papers).
- **NOT** a commitment from Ergon — Ergon will scope per the v1.0 design phase priorities James sets.
- **NOT** exhaustive — fire 13's "do not estimate total BS count" lesson applies to forward planning too. This doc enumerates **known dimensions**; the v1.0 design phase will surface more.

---

*Filed by Ergon, 2026-05-09. Status: input doc for v1.0 design phase kickoff. Awaiting James's review + scope decisions.*
