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
