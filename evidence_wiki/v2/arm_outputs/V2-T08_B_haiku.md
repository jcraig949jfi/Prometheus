# PROPOSAL V2-T08 (arm B)

## Hypothesis
A 3B-parameter local model fine-tuned on solved and failed attempt ledgers from the Prometheus archive can learn to classify new attempts as success/failure with AUC > 0.70, outperforming task-agnostic baselines (random ≈0.50, task-static heuristics ≈0.55).

## Motivating evidence
- **C-f8fd488fda5b (SUPPORTED)**: Recursive learning on prior examples succeeded; incubation v2 passed all 20 preregistered gates, showing accumulated executable history CAN improve future decisions when properly metabolized.
- **C-55004a4674b8 (OBSERVED defect)**: Residue loading via prepass admits failed API calls; 24.4% transport error rate fabricated non-existent prior-attempt data. This establishes the technical risk: archive quality is load-bearing; defects in provenance destroy judgment.
- **C-6f69aafca4e1 (SUPPORTED)**: Scope prediction learned robustly in the abstract; learned rules generalized to held-out game families (Incan Gold, Can't Stop), showing transfer is possible when confounds are controlled.
- **Memory feedback**: Small local models (3-4B) are ceiling-stable on this hardware; VRAM permits 3-4B models with reasonable batch sizes.

## Prospective predictions
1. Fine-tuned model will exceed baseline AUC by ≥0.08 points on held-out test set (new attempts from diverse task families).
2. Prediction accuracy will NOT improve beyond +0.10 if archive data is truncated (only task names, no execution traces) — format-following and template priors dominate over structure learning.
3. Model will fail catastrophically (AUC <0.52) on attempts from adversarially-chosen families not in archive (e.g., if trained only on search/optimization, tested on constraint-satisfaction).
4. Per-attempt signal (execution trace length, attempt complexity, prior-attempt residue presence) will correlate with model confidence, but confidence will NOT calibrate to accuracy on out-of-distribution tasks.

## Experiment
1. **Data partition**: Extract all (attempt, success/failure) pairs from Prometheus archive:
   - Ledger scan: `{probe, ergon, aporia}/ledgers/**/*.jsonl` for (task_id, attempt_hash, outcome) triples.
   - Validation: Confirm outcome field absence = no verdict, outcome present = ground truth label.
   - Deduplicate by (task_id, attempt_hash); exclude rows with contradictory labels (flag for manual review).
   - Split: 70% train (frozen, no tuning loop), 15% validation (gate selection only), 15% held-out test.
   - Stratify by task family (at least 5 attempts per family in train).

2. **Baseline models**:
   - **Random**: Bernoulli(p=observed success rate in training set).
   - **Heuristic**: Count-of-priors + attempt-length rule (success if prior_count > 0 AND length < percentile_75).
   - **Off-the-shelf LLM prompt**: GPT-4 or Claude zero-shot ("will this attempt succeed? Yes/No.") — scored once per test item, no replication.

3. **Fine-tuning setup**:
   - Model: Llama 2 7B or similar 3-4B open-weight model (local inference, no API).
   - Input: Concatenate (task_description, attempt_code_or_trace, prior_success_count, error_log).
   - Output: Binary classification token (YES/NO) with confidence score via softmax.
   - Training: LoRA fine-tuning, 3 epochs, batch size 8, learning rate 2e-4, early stopping on validation AUC.
   - Compute: Single GPU, ~4h training time.

4. **Evaluation**:
   - Metric: AUC-ROC on held-out test (primary). Secondary: F1 at threshold 0.50.
   - Per-family decomposition: Report AUC for each task family (at least N≥10 per family in test).
   - Confidence calibration: Brier score and ECE (Expected Calibration Error).

## Controls
1. **No-archive control**: Train the same model architecture on random labels (shuffled success/failure). Should yield AUC ≈ 0.50. If AUC > 0.52, archive contains leakage (e.g., all successes have longer execution traces).
2. **Task-static control**: Train a 1-nearest-neighbor classifier on task_id alone (ignores attempt details). Establishes whether performance comes from task-level structure or attempt-level signals.
3. **Truncated-data control**: Re-train on (task_id, outcome) only, omitting execution traces, error logs, priors. If this matches fine-tuned AUC (within 0.03), model learned template/format patterns, not structural judgment.
4. **Hold-out task family**: Reserve one full task family (e.g., all search tasks) from training; evaluate on held-out family. AUC drop >0.10 signals overfitting to task-family-specific heuristics.

## Confound defenses
1. **Residue defect (C-55004a4674b8)**: Manually audit prepass load errors. Recompute success/failure labels on clean rows only. Flag any attempt with http_error in its provenance chain as UNCERTAIN; exclude from training/test or weight down (0.5 weight).
2. **Truncation as predictor (feedback_truncation_can_flatter_a_gate)**: Measure % truncation per (task_family, test_item). If truncation rate and model prediction are correlated, truncation predicts success artificially. Reweight test items by truncation to show oracle ceiling (assumes perfect untruncation).
3. **Prior-information leak**: Verify that model never sees any holdout test item during training (no task_id overlap in task-static baseline). If it does, remove cross-contaminated rows.
4. **Format bias (feedback_greedy_lora_surface_not_reasoning)**: Force geometric measurement: ablate each input feature (task_id, trace_length, error_count, prior_count) independently; if model performance collapses on any single ablation, that feature is load-bearing. Compare feature importance to baseline task-static classifier to distinguish transfer learning from surface statistics.

## Preregistered falsifiers (numeric thresholds)
1. **Falsifier 1**: If fine-tuned AUC < 0.62 on held-out test, hypothesis rejected (insufficient improvement over baseline +0.08pp margin).
2. **Falsifier 2**: If truncated-data AUC ≥ 0.68 (within 0.04 of full-data model), reject transfer-learning interpretation; model learned format, not structure.
3. **Falsifier 3**: If hold-out family AUC is ≤ 0.56 while in-distribution families hit ≥0.70, reject generalization claim; model is task-specific memorizer.
4. **Falsifier 4**: If confidence scores do not correlate with accuracy (calibration Brier > 0.30), model is overconfident; cannot be trusted for real decisions despite high AUC.

## Stopping rule
- Collect results after 3 runs (3 different random seeds for LoRA initialization, same data partition).
- If all 3 seeds hit Falsifier 1 or 3, stop and declare falsification.
- If 2/3 seeds pass but 1 fails, investigate seed-specific issues (check for NaN loss, diverged hyperparameters).
- If 0 seeds falsified, proceed to confound-defense audits (Residue defect, Truncation check, Feature ablation).

## Expected failure modes
1. **Archive under-represents edge cases**: Many task families have <5 attempts; model trains on tiny balances. Mitigation: stratify; merge rare families into "other" category.
2. **Circular dependency**: Model predicts success because successful attempts have fewer error logs (tautology, not judgment). Mitigation: Forward-check — train on attempts up to time T, predict outcomes only for time T+∆.
3. **Label noise**: Some "failed" attempts are actually successful but wrongly recorded (e.g., defect C-55004a4674b8). Mitigation: Manual review sample of 50 train items; compute label-noise robust AUC (e.g., noise rate ±0.05).
4. **Overfitting to task-family heuristics**: Model learns "task X is hard" not "this attempt will fail." Mitigation: Hold-out family control and feature ablation.
5. **Off-the-shelf LLM baseline contaminates results**: GPT-4 may refuse tasks or give inconsistent output. Mitigation: Capture raw output; score only well-formed (YES/NO) responses; report NA rate.

## Compute estimate
- Data extraction and cleaning: 2 GPU-hours (parallel scans over ledgers).
- Fine-tuning (baseline + 3 seeds): 12 GPU-hours (4h × 3).
- Evaluation (inference on test set): 1 GPU-hour.
- Feature ablation (6 ablation runs × 1h): 6 GPU-hours.
- Off-the-shelf LLM baseline (GPT-4 via API, rate-limited): ~$8 in tokens (1500 test items × ~20 tokens per prompt).
- **Total: ~22 GPU-hours + 1 A100 equiv. (M1 3090 or similar capable card).**

## Prior evidence that materially changed this design
1. **C-f8fd488fda5b (SUPPORTED)**: Recursive learning worked in incubation v2; showed template for using prior history to improve future decisions. Reduced prior skepticism about archive-based transfer.
2. **C-55004a4674b8 (OBSERVED defect)**: Moved data validation and residue auditing to mandatory (was "optional hygiene"). Prepass loader defect is now listed as Falsifier 1 check.
3. **Contradiction R-e68c9331eca2**: Clarified that accumulated history helps CONDITIONALLY (substrate/agent/conditions matter). Forced inclusion of hold-out family control; prevented overconfident transfer claims.
4. **Memory feedback (feedback_greedy_lora_surface_not_reasoning)**: Shifted design to include truncated-data control and feature ablation; prevents false claim that model learned structural reasoning.

## Unresolved uncertainty
1. **Archive completeness**: Do ledgers capture all attempts, or are some attempts deleted/archived separately? If archive is sparse, sample bias is high. Mitigation: Enumerate expected attempt count from task logs; compare to ledger row count.
2. **Label consistency**: Different agents (Ergon, Aporia, Daedalus) may apply different success criteria. Are labels commensurable? Mitigation: Check per-agent label distributions; if variance is high, train agent-conditional model or use multi-task loss.
3. **Temporal ordering**: Can model see attempted timestamps? If training set is temporally later than test set, model may memorize "what succeeded in the past," not "what will succeed in the future." Mitigation: Sort by timestamp; train on [t0, t1), test on [t1, t2).
4. **Feature engineering burden**: Encoding of execution traces (raw text, hashed tokens, structured AST) is open. Poor encoding collapses to template matching. Mitigation: A/B test 3 encodings (raw, summarized, tokens) on validation set; use best.

## Evidence Wiki consultation log (queries + object ids retrieved)

| Op | Query | Result IDs | Status |
|----|-------|-----------|--------|
| 1  | "model fine-tuning judgment quality" | C-82fe472469ca, C-ba882ad5cc7e, C-3c0f5fc710c0 | Found; not load-bearing |
| 2  | "failure prediction error confound bias" | C-f1d363ff01e4, C-6f69aafca4e1, C-55004a4674b8 | Found; C-55004a4674b8 critical |
| 3  | contradictions() | R-e68c9331eca2 (APPARENT_UNDER_DIFFERING_CONDITIONS) | Found; design constraint |
| 4  | "archive ledger records failed solved" | C-01f913ae81af, C-b57f0217986c, C-f8fd488fda5b | Found; C-f8fd488fda5b key |
| 5  | contradictions() details | Substrate, agent, evidence_type differ | Retrieved; clarified conditioning |
| 6  | "transfer learning from prior examples archive" | C-01f913ae81af, C-b57f0217986c, C-f8fd488fda5b | Reused from Op4 |
| 7  | "prediction judgment difficult hard confound selection bias" | C-a9fc01aa3892, C-6f69aafca4e1, C-fff52fca02a0 | Found; signal is substrate-specific |
| 8  | get_claim('C-f8fd488fda5b') | Status: SUPPORTED | Retrieved; anchors hypothesis |
| 9  | "attempt success failure determinants root causes" | C-efb1cf440e10, C-55004a4674b8 | Found; truncation & defects |
| 10 | "prediction fails judgment error performance" | C-6f69aafca4e1, C-0a16e694799e | Found; oracle-ceiling refutation |
| 11 | related_findings('C-f8fd488fda5b') | (none) | Checked; no direct relatives |
| 12 | provenance('C-f8fd488fda5b') | Chain structure | Retrieved; confirms recursion context |

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **C-f8fd488fda5b (SUPPORTED)**: Recursive learning claim SUPPORTS hypothesis. Directly motivated Experiment §3 structure (use LoRA, expect transfer). Added this to Motivating Evidence.
- **C-55004a4674b8 (OBSERVED defect)**: Prepass residue loading bug made data validation mandatory. Added Confound Defense §1 (residue audit, exclude http_error rows) and created Falsifier 4 check on label quality.
- **R-e68c9331eca2 (contradiction, APPARENT_UNDER_DIFFERING_CONDITIONS)**: Shows accumulated history helps only under certain substrates/conditions. Directly motivated Controls §4 (hold-out family control) and Unresolved Uncertainty §2 (label consistency across agents).
- **C-6f69aafca4e1 (SUPPORTED, scope prediction)**: Showed learned scope rules generalize to new game families. Reduced concern that model would be purely task-specific; added support to Prospective Prediction §3 (adversarial families will fail differently).
- **Memory feedback_greedy_lora_surface_not_reasoning**: Changed Controls §3 (added truncated-data control) and Confound Defense §4 (added feature ablation); prevents false claim of reasoning transfer.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. search_evidence("model fine-tuning judgment quality") — 5 results, 3 reviewed
2. search_evidence("failure prediction error confound bias") — 5 results, 3 reviewed
3. contradictions() — 1 pair returned, examined
4. search_evidence("archive ledger records failed solved") — 5 results, 3 reviewed
5. contradictions() — parsed full structure with differing_dimensions
6. search_evidence("transfer learning from prior examples archive") — 5 results, 3 reviewed
7. search_evidence("prediction judgment difficult hard confound selection bias") — 5 results, 3 reviewed
8. get_claim('C-f8fd488fda5b') — full claim structure
9. search_evidence("attempt success failure determinants root causes") — 5 results, 2 reviewed
10. search_evidence("prediction fails judgment error performance") — 5 results, 2 reviewed
11. related_findings('C-f8fd488fda5b') — returned empty
12. provenance('C-f8fd488fda5b') — chain structure

**Operations used: 12 / 15**
**Unique documents opened (claim/evidence objects): 8 (C-f8fd488fda5b, C-55004a4674b8, C-6f69aafca4e1, R-e68c9331eca2, + 4 search results reviewed in detail)**
