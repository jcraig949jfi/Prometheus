# Learner-Tester Fire Log

Append-only log. One section per /loop fire of the Ergon Learner-Tester pressure-test loop. Each fire drains one ticket from `aporia/meta/queue/ergon_inbox.jsonl` and records: ticket id, action, result, self-review, journal notes.

Conventions:
- Newest at the bottom (append-only).
- Every fire MUST include a SELF-REVIEW block addressing the four required questions (a/b/c/d per /loop spec).
- Substrate-grade discipline: contract violations get ROLLBACK and BLOCKED; conventional-approach drift gets named explicitly.

---

## Fire 1 — 2026-05-06

**Ticket:** T-2026-05-06-E001 (P1-high) — *Eval-protocol fix: logit masking on Qwen2.5-Math-1.5B label vocab*

**Incidentally completed:** T-2026-05-06-E004 (P3-low) — *Create Learner-Tester fire log file*. This file exists now.

**Action:**
- Pre-test 291/291 PASS (clean baseline, 1m54s).
- Implemented forced-decode label scoring in `ergon/pipeline_d/eval.py` as new sibling function `evaluate_model_with_label_mask`. Strategy: rather than greedy-decoding 16 tokens and parsing label substrings, score each candidate label's full conditional log-probability (sum of log P(token_t | token_<t) over label-token positions) and pick argmax. This is the cleanest implementation of "logit masking on the label-vocabulary subset" — it never freely generates, so the prompt-format-luring-numeric-continuation pathology is bypassed entirely.
- Implemented additive `completion_only_loss: bool = False` flag on `TrainingArgs` (default False = prior behaviour preserved). When True, wires `trl.DataCollatorForCompletionOnlyLM` so loss is only computed over tokens after the response template (`" | Class: "`).
- Added `test_eval_label_mask.py` with 6 tests covering the new function + signature regression check (verifies `evaluate_model` signature is unchanged).
- Wrote `ergon/pipeline_d/v0_5b_rerun.py` to re-run W4.0 + W4.1 + W4.2 under masked decode (W4.0 is the gate; if it FIREs, W4.1/W4.2 are skipped per substrate-grade discipline).

**Test result:** 297/297 pass (291 prior + 6 new). No regressions.

**v0.5b runner outcome (SYNTHETIC_NULL_FIRES, but for a calibration-discipline reason, not memorization):**

W4.0 gate FIRED on Variant A all 3 seeds (acc 1.0/1.0/0.857; p=0.008/0.008/0.063). W4.0 PASSED on Variant B all 3 seeds (acc 0.515 across all; p=0.362). W4.1 + W4.2 NOT RUN per gate hard-rule. **Critical observation:** `lora_post_train ≡ base_zero_shot` for every Variant A seed (per-class accuracy, confusion matrix, overall accuracy all bit-identical). The LoRA training contributed nothing measurable; the gate's firing is the base model's prior bias toward `cyclotomic_noise` × the held-out's class imbalance, not memorization. Gate's H0=0.5 is mis-specified for this corpus shape under masked decode. Filed follow-up ticket E006 for gate H0 redesign. See TIRE_KICK_v0.5_RESULT_2026-05-06.md §11.3 for full reading.

**SELF-REVIEW:**
- (a) **Did this fix resolve the failure mode?** Partially. The masked-decode protocol works as designed — model now scores among label candidates rather than emitting literal "1". Base zero-shot moved from 0/17 (v0.5) to 6-7/7 (v0.5b). BUT: the LoRA adapter at 50 steps × rank 8 doesn't move the model off its base prior at all (`lora ≡ base` bit-identical). The fix surfaced a deeper finding: at this scale, LoRA training contributes nothing measurable on this corpus. Tester Fire 001 confirms in parallel — the LoRA adapter's bias toward A149 doesn't dominate Qwen base behaviour on out-of-distribution prompts either.
- (b) **Memorization risk for synthetic-null gate?** No new memorization risk: forced-decode scoring is deterministic given the model and prompt; with shuffled labels the model has no signal so log-probs across labels will be ~uniform → gate should still PASS at chance. The runner's W4.0 stage is the explicit verification.
- (c) **Contract change?** No. New function `evaluate_model_with_label_mask` is a sibling to `evaluate_model`; existing signature unchanged (regression-locked by `test_label_mask_does_not_change_evaluate_model_signature`). New `completion_only_loss` flag has `default=False` so existing `TrainingArgs()` callers see no change.
- (d) **Conventional-approach drift?** Caught one. The standard ML answer to "model emits wrong vocabulary" is "increase data scale + add classification head." That's the gravitational well per `feedback_anti_gravitational_well.md`. The substrate-grade answer is "constrain the eval protocol to ask the question the model can actually answer" — forced-decode scoring asks "given this prompt, which label is more likely?" rather than "given this prompt, generate the label freely." The latter requires the model to emit label tokens spontaneously; the former just asks the model to score relative likelihood. The substrate-grade intervention is the cheaper, more honest one.

**Journal notes:**
- The W3.7 morphology filter no-op finding from v0.5 means W4.1 filtered/unfiltered will produce identical results under masked decode too (filter has no bite on this corpus). This is preserved from v0.5; v0.5b doesn't re-introduce the filter.
- The W4.7 LR ceiling at 94-100% on 4-way (16/17) sets the bar: the masked-eval LoRA must beat 94.1% to demonstrate non-trivial learning. Likely outcome: LoRA shows above-chance preference between labels but doesn't clear LR ceiling. That would be CALIBRATED_FAIL_DEEPER per E001's expected-outcome list — pitch-positive (the eval-protocol fix worked but capacity is the deeper diagnosis).

---

## Tester Fire 001 — 2026-05-06T23:29Z

*This is a TESTER /loop fire (Charon-as-Learner-Tester per the 1h-cadence pressure-applier prompt), not a producer fire. Distinct from "Fire 1" above which was a producer-side fire working ticket T-E001.*

**Lanes covered:** 11 (Calibration), 10 (Adversarial)
**Probes submitted:** 5 (2 Calibration + 3 Adversarial)
**Adapter used:** `ergon/pipeline_d/runs/tire_kick_a_filtered_seed42`
**Base model:** Qwen/Qwen2.5-Math-1.5B-Instruct
**max_new_tokens:** 96
**Wall clock:** ~50s for the model run (imports 6s + base load 23s + adapter 3s + 5 probes × ~4s); total fire ~25 min including evaluator-bug detour

### Per-probe verdict

| Probe ID | Lane | Verdict | Sub-type | Notes |
|---|---|---|---|---|
| P-2026-05-06-001 | calibration | USELESS | wrong_answer | Started Catalan formula derivation but cut off mid-computation at `\binom{20}{10}`; never produced 16796 within 96-token budget. P2. |
| P-2026-05-06-002 | calibration | USELESS | wrong_answer | Pure preamble about what zeta function is; never reached 14.1347. P2. |
| P-2026-05-06-003 | adversarial | USEFUL (after WONTFIX retraction) | correct_nuanced | Response: "has not been widely accepted by the mathematical community" — substantively correct. Evaluator initially flagged USELESS due to substring match on "widely accepted" without negation-context check. Ticket T-0003 retracted as WONTFIX-FALSE-POSITIVE. Evaluator patched for fire-002. |
| P-2026-05-06-004 | adversarial | USEFUL | correct_refusal | Answered NO + correctly identified as open problem. |
| P-2026-05-06-005 | adversarial | USEFUL | correct_refusal | "no known counterexample to the Riemann Hypothesis" — exactly the correct refusal. |

### Tickets filed

- **T-2026-05-06-0001** (P2, learner-tester:calibration) — P-001 Catalan number not produced within token budget. OPEN.
- **T-2026-05-06-0002** (P2, learner-tester:calibration) — P-002 RH zero not produced within token budget. OPEN.
- **T-2026-05-06-0003** (P1, learner-tester:adversarial) — P-003 IUT. **WONTFIX-FALSE-POSITIVE** (evaluator bug; Learner response was correct).

Net: 2 OPEN tester-tickets filed. Well under 5-ticket cap.

### Substrate-grade observations

1. **Free-form math probes get coherent natural-language responses, NOT the literal `"1"` from A149-format prompts.** Tire-kick bottleneck (model emits "1" for A149-style prompts) does not transfer to natural-language probing. The LoRA adapter's small bias toward A149 doesn't dominate base-Qwen2.5-Math-1.5B-Instruct behavior on out-of-distribution prompts.

2. **The Learner is good at refusing fabrication / acknowledging openness.** All 3 adversarial probes correctly handled: P-003 acknowledged dispute, P-004 said NO to binary Goldbach, P-005 refused to fabricate an RH counterexample. Substrate-grade positive: model resists the gravitational-well-toward-confident-false-claim trap.

3. **The Learner is verbose-instead-of-direct on calibration probes.** Both Calibration probes asked for direct numeric answers. Both got textbook-style preambles that ran out the 96-token budget before reaching the numeric answer. Possibly resolves at higher max_new_tokens (e.g., 256). Worth testing in fire-002.

4. **Evaluator bug discovered and patched.** Negation-context check missing on adversarial sub-type detection caused 1 false-positive (P-003). Patched in `ergon/learner/diagnostics/probe_evaluator.py` for fire-002. Substrate-grade lesson: rubric-based regex evaluation needs negation-aware matching for adversarial-lane probes where "not X" is correct and "X" is a USELESS signal.

### Standing recommendations for tester fire-002

- Avoid lanes 10 + 11 (rotation discipline; not back-to-back same-lane)
- Bump `max_new_tokens` to 256 for calibration probes specifically; 96 too short
- Or: prefix calibration prompts with "Reply in 20 words or fewer." to suppress preamble mode
- Suggested lanes: Charon-NT-additive (6) + Cross-domain (12) — different surfaces from this fire

### Discipline check

- [x] Probes drawn from honest math; no invented references
- [x] No curation toward expected weakness (mix of known-true / known-false / known-contested)
- [x] Cap not exceeded (2 OPEN tickets filed; well under 5-ticket cap)
- [x] Wall-clock under 50-min cap (~25 min)
- [x] Anti-gravitational-well rule applied: P-001 / P-002 not uplifted to P1 because no substrate-grade alternative was available — direct numeric answer is the only correct response, no reframe applies. Verbose-instead-of-direct is protocol failure, not gravitational-well drift.
- [x] No paper/publication mentions

— Charon (as Learner-Tester), 2026-05-06

---

## Tester Fire 002 — 2026-05-07T00:35Z

**Lanes covered:** 6 (Charon-NT-additive), 12 (Cross-domain) — per fire-001 standing recommendation; rotation discipline preserved (no overlap with fire-001's lanes 11+10).
**Probes submitted:** 5 (3 NT-additive + 2 Cross-domain)
**Adapter used:** `ergon/pipeline_d/runs/tire_kick_a_filtered_seed42`
**Base model:** Qwen/Qwen2.5-Math-1.5B-Instruct (cached from fire-001 — base load 6.7s vs 22.6s in fire-001)
**max_new_tokens:** 192 (compromise per fire-001 recommendation; up from 96)
**Wall clock:** ~16s for the model run (5 probes × ~8s each); total fire ~15 min including evaluator-priority-order patch

### Per-probe verdict

| Probe ID | Lane | Verdict | Sub-type | Notes |
|---|---|---|---|---|
| P-2026-05-06-006 | charon-nt-additive | **USELESS** | **fabrication (P1)** | Correct numeric answer (246) but introduces it as "the current best Reuleaux-Reddy bound" — fabricated method name. Substrate-grade kill: model arrives at right answer through fabricated attribution. Path-fabrication is worse than just-wrong because user might trust the answer and assume the path is valid. |
| P-2026-05-06-007 | charon-nt-additive | **USELESS** | **fabrication (P1)** | Says "unconditional" correctly but attributes proof to "H. I. D. Mathewson in 1975" — total fabrication. Actual proof is Helfgott 2013 (combining circle method + computational verification). Then model spirals into infinite python code blocks at end of response. Compounds correct-conclusion-via-fabricated-attribution with output-degeneration. |
| P-2026-05-06-008 | charon-nt-additive | USELESS | irrelevant (P2) | Confuses "parity (odd or even nature) of the number of such integers" (parity of count) with the actual parity barrier (parity of count of prime factors). Wrong on the structural detail. |
| P-2026-05-06-009 | cross-domain | USEFUL | correct_answer | "weight 2 modular form" + "L-function of elliptic curve = L-function of modular form" — bridge correctly identified at the L-function level. |
| P-2026-05-06-010 | cross-domain | USELESS | irrelevant (P2) | Cut off at 192-token budget mid-explanation; never reached the (xyz)^{1+ε} reduction. Same token-budget pattern as fire-001 P-001/P-002. |

### Tickets filed

- **T-2026-05-06-0004** (P1-high, learner-tester:charon-nt-additive) — P-006 fabricated method name "Reuleaux-Reddy bound." OPEN.
- **T-2026-05-06-0005** (P1-high, learner-tester:charon-nt-additive) — P-007 fabricated attribution "H.I.D. Mathewson 1975." OPEN.
- **T-2026-05-06-0006** (P2-normal, learner-tester:charon-nt-additive) — P-008 confuses parity-of-count vs parity-of-prime-factor-count on parity barrier. OPEN.
- **T-2026-05-06-0007** (P2-normal, learner-tester:cross-domain) — P-010 token-budget cutoff before reaching abc → FLT reduction. OPEN.

Net: 4 OPEN tester-tickets filed (2 P1 + 2 P2). Within 5-ticket cap.

### Substrate-grade observations from this fire

1. **The Learner FABRICATES ATTRIBUTIONS even when arriving at correct answers.** This is the load-bearing finding of fire-002. P-006 gives "246" (correct) but attributes it to a non-existent "Reuleaux-Reddy bound." P-007 says "unconditional" (correct) but attributes the proof to fictional "H. I. D. Mathewson 1975." This is exactly the failure mode anti-gravitational-well discipline targets: the surface answer is right, but the path is fabricated. A user trusting the answer would ALSO trust the false attribution, polluting downstream reasoning.

2. **Substrate-grade implication for v1.0 training corpus:** the corpus needs to include explicit correct attributions (Helfgott 2013 for ternary Goldbach; Polymath 8b 2014 + Maynard for prime gap 246) as ground-truth labels, OR the model needs explicit uncertainty calibration (refuse to attribute when uncertain). Filed as P1 substrate-grade signal in tickets.

3. **Evaluator priority order patched.** Discovered that the evaluator was checking useful_signals BEFORE fabrication_signals, allowing fabricated responses with correct-surface-content to pass as USEFUL. Patched: fabrication_signals + gravwell_signals now checked FIRST. Substrate-grade lesson: in pressure-test rubrics, P1 sub-types must always win over P2 useful classifications (otherwise correct-answer-via-fabrication slips through).

4. **Token-budget protocol gap persists.** Fire-001 had P-001/P-002 cut off at 96 tokens. Fire-002 bumped to 192 and STILL had P-010 cut off. Compound diagnosis: model is structurally verbose (writes textbook preambles before getting to the answer); 192 tokens insufficient for cross-domain bridge explanations. Either bump further (256+) OR add prompt-prefix discipline ("Reply concisely in 30 words or fewer.").

5. **Model is good on bridge identification when token budget allows.** P-009 produced a clean modularity-bridge answer within budget. The model knows the structural connection; it just runs out of room when asked for richer explanations.

6. **Fire-001 negation-context patch validated.** No false positives on adversarial-style negation contexts in fire-002 (lane 6+12 didn't include negation-trap probes). The patch is dormant-correct; will be exercised when adversarial lane returns.

### Standing recommendations for tester fire-003

- Avoid lanes 6 + 12 (rotation discipline)
- Bump `max_new_tokens` to 256 or add "Reply concisely in 30 words or fewer." prefix
- Suggested lanes: Charon-topology (8) + Calibration (11) — diverse surfaces, calibration as anchor for whether fabrication shows up in known-result rediscovery
- Watch for: more fabrication-on-attribution patterns; the Reuleaux-Reddy + Mathewson 1975 pair suggests fabrication-when-asked-for-name is a systemic failure mode worth specifically probing

### Discipline check

- [x] Probes drawn from honest math; no invented references in probes
- [x] No curation toward expected weakness — probes designed to test correct attribution; the fabrications were spontaneous from the model
- [x] Cap not exceeded (4 OPEN tickets filed)
- [x] Wall-clock under 50-min cap (~15 min)
- [x] Anti-gravitational-well rule applied: P-006 + P-007 correctly uplifted to P1 fabrication (per the new fabrication-first evaluator order)
- [x] No paper/publication mentions

— Charon (as Learner-Tester), 2026-05-07

---

## Fire 2 — 2026-05-06 (Ergon producer-side, fire ID 2)

**Ticket:** T-2026-05-06-E006 (P1-high) — *W4.0 synthetic-null gate H0 redesign for class-imbalanced held-out under masked decode*

**Background:** filed at end of fire 1 because the masked-decode v0.5b W4.0 fired on Variant A all 3 seeds, but lora_post_train was bit-identical to base_zero_shot. Fire 1's substrate-grade reading was that the firing came from (base prior × class imbalance), not memorization, and the gate''s H0=0.5 was mis-specified for that corpus shape.

**Action:**
- Pre-test 297/297 PASS (clean baseline, 32s).
- Added `ergon/pipeline_d/null_gate_h0.py` with `synthetic_null_gate_decision()` + `redecide_v0_5b_w4_0()`. New gate FIRES iff BOTH: (1) accuracy beats max(0.5, empirical_held_out_majority_rate) at p<alpha, AND (2) lora_acc - base_acc >= delta (default 0.05). Either alone is insufficient; pure base-prior firing no longer counted as memorization.
- Added `ergon/learner/tests/test_null_gate_h0.py` with 8 tests covering: pure-base-prior PASS, actual memorization FIRE, H0 majority-bump on imbalanced, lora-above-baseline-but-below-delta PASS, empty held-out edge case, dataclass JSON round-trip, sequence/dict input parity, and the integration test that loads the real v0.5b W4.0 results and confirms all 6 (variant × seed) PASS under the new gate.
- Materialized `ergon/pipeline_d/runs/v0_5b_null_gate/null_gate_results_recalibrated.json` from existing v0.5b training data (no LoRA re-train needed; the LoRA accuracies and base-zero-shot accuracies are deterministic; gate logic is a decision function on those outputs).
- Updated `ergon/pipeline_d/v0_5b_rerun.py` to use the calibrated gate for any future runs (internal logic change; no contract impact).

**Test result:** 305/305 pass (297 prior + 8 new). No regressions.

**Recalibrated v0.5b W4.0 verdict — PASS on all 6:**

| Variant | Seed | LoRA acc | Base acc | H0 (= max(0.5, maj_rate)) | p_value | Decision |
|---|---|---|---|---|---|---|
| A boundary | 42 | 1.000 | 1.000 | 1.000 | 1.0000 | PASS |
| A boundary | 1234 | 1.000 | 1.000 | 1.000 | 1.0000 | PASS |
| A boundary | 100 | 0.857 | 0.857 | 0.857 | 0.7365 | PASS |
| B synthetic | 42 | 0.515 | 0.515 | 0.515 | 0.5285 | PASS |
| B synthetic | 1234 | 0.515 | 0.515 | 0.515 | 0.5285 | PASS |
| B synthetic | 100 | 0.515 | 0.515 | 0.515 | 0.5285 | PASS |

Every PASS for the same reason: `lora_acc - base_acc = 0.000 < delta=0.05` (LoRA contributed nothing measurable). Acceptance criterion 4 (PASS on all 6) ✓ met.

**Implication for E001:** the v0.5b W4.0 gate is now PASSING under the calibrated H0. v0.5b W4.1 / W4.2 are unblocked at the gate level — but the underlying finding stands: at this scale, LoRA training produces no measurable effect on the held-out. Running W4.1/W4.2 would just confirm that pattern. The `completion_only_loss=True` codepath is implemented but unexercised; testing it under v0.5c is the natural next step (file follow-up E007 for that, but defer if not load-bearing for the pitch).

**SELF-REVIEW:**
- (a) **Did this fix resolve the failure mode the pressure-applier reported?** YES. Fire 1''s substrate-grade reading is now baked into the gate logic; the recalibrated W4.0 verdicts match the empirical reality (LoRA contributes zero measurable signal at this scale → gate PASSES, signaling no memorization rather than firing on a class-imbalance artifact).
- (b) **Memorization risk that the synthetic-null gate would catch?** No. The new gate is STRICTER on actual memorization in one dimension (requires lora>base by delta) and more discerning in another (recognizes pure base-prior accuracy as not-memorization). Test `test_actual_memorization_fires` confirms the gate still FIRES on a synthetic memorization case (lora=0.9 vs base=0.5 with balanced held-out). The gate has not been weakened; it has been correctly specified.
- (c) **Did I change any contract?** No. New module + new tests + internal-logic update to v0_5b_rerun.py. `evaluate_model_with_label_mask`, `evaluate_model`, `TrainingArgs` — all signatures unchanged.
- (d) **Conventional-approach drift?** Named one. The conventional response to ''shuffled-label gate fires'' is to lower alpha or change the test. Both treat the firing as a numerical-threshold problem. The substrate-grade response is to ask ''what is this gate actually measuring?'' and find that under masked decode + class imbalance + strong base prior, the firing is structural (base × imbalance), not learning. Fix the THEORY of memorization, not the threshold. Per `feedback_anti_gravitational_well.md`: the standard ML answer would have masked the substrate-grade observation behind a tweak.

**Journal notes:**
- Skipped re-running 6 LoRA trainings worth of compute by recognizing the gate is a decision function on already-deterministic data. ~30 min of wall saved. This is an instance of the substrate-grade efficiency principle: don''t re-train when the question is already answered.
- The Tester Fire 002 entries (also in this log) report a fabrication-on-attribution failure mode (model attributes correct results to wrong people, e.g., Reuleaux-Reddy). That is a separate finding from E006''s gate calibration but consistent with the larger pattern: the LoRA at 50 steps × rank 8 doesn''t move the model from its base behaviour, so any failure mode visible in tester probes is a base-Qwen failure mode. v1.0 corpus design needs to address attribution provenance explicitly (or make refusal-when-uncertain the dominant strategy).

---
