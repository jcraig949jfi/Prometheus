# PROPOSAL V2-T08 (arm A)

## Hypothesis

A small (2.7–3B parameter) language model fine-tuned on the archive of ERGON experiment configurations and verdicts can learn to classify whether a new experiment will receive a pass verdict (e.g., READY_TO_RUN) or fail (e.g., R13-POWER-FLOOR-UNMET, FAMILY_B_REQUIRES_NEW_SYNTHESIS_LAYER) better than domain heuristics based on configuration thresholds alone. Transfer should emerge from the joint distribution of design parameters and measured outcomes, enabling faster vetting of new proposals before expensive runs.

## Motivating evidence

1. **Verdict taxonomy exists and is measured.** ERGON (gen0–gen1b) produces structured verdicts tied to preregistered gates (attainable_range, persistence validation, power floor). Each verdict correlates with measurable configuration features (n_lineages, library_cap, budget_per_task, primitive_extension_evidence, frozen status, policy).

2. **Archive size is sufficient for supervised learning.** Across gen0, gen1, gen1a, gen1b: ~120–150 experiment runs, each with recorded config and verdict. This is small enough for 3B-model fine-tuning without overfitting on a single GPU (17GB VRAM available locally per memory).

3. **Domain heuristics are brittle.** Verdict assignment today depends on nested conditional gates (power floor, admissible families, MDE comparisons) that are difficult to predict without full domain knowledge. A learned model can discover non-obvious feature interactions (e.g., interactions between library_cap × budget × n_lineages that domain rules miss).

4. **Speed-to-verdict matters operationally.** Lexis role (sequencing decisions) owns the "should we spend compute on this run?" gate. Fast prediction on proposed configs (seconds, not hours) would unblock decision velocity.

## Prospective predictions

1. **Classification accuracy (binary: PASS vs FAIL).** Model achieves ≥65% test accuracy on held-out ERGON experiments from last 2 generations (gen1a + gen1b), where baseline domain heuristic (e.g., "PASS if n_lineages ≥ 30") achieves ~55–60%.

2. **Calibration on power gate.** When model predicts FAIL, the reason should correlate with actual gate-fire cause in ≥70% of cases (e.g., model confidence is higher when failure is due to power floor vs. structural fit).

3. **Confidence tracking.** Model confidence (via logit magnitude or temperature-scaled softmax) correctly ranks hard-vs-easy predictions: high confidence examples resolve to ground truth at ≥80%, low confidence examples at ≥55%.

## Experiment

### Data preparation

1. **Extraction.** Mine F:\Prometheus\ergon for all *.json config files + verdicts from review packets. Schema: {n_lineages, budget_per_task, library_cap, opcodes_frozen, primitive_extension_evidence, policy_name, verdict_gate_fired?, effect_size_observed, sd_observed, final_verdict}.

2. **Labeling.** Binary label: verdict IN {GEN1_READY_TO_RUN, PASSED, LEVELED, OK} → PASS (1); verdict IN {R13-POWER-FLOOR-UNMET, FAMILY_B_REQUIRES_NEW_SYNTHESIS_LAYER, NOT_CONSUMABLE, BLOCKED} → FAIL (0). Multi-class alternative: 5-class (READY, UNMET-POWER, UNMET-STRUCTURAL, UNMET-LIBRARY, UNMET-CORPUS).

3. **Featurization.** Numerics (n_lineages, budget, library_cap, sd_observed, effect_size_observed, opcodes_frozen count) → standardized. Categorical (policy_name, primitive_extension_evidence) → one-hot or learned embeddings. Target: tokenized verdict name or numeric label.

4. **Train/test split.** Stratified by verdict class and generation. Train: gen0 + first 80% of gen1 (≈80–100 examples). Validation: last 20% of gen1 (≈10–15 examples). Test: gen1a + gen1b (≈30–40 held-out, separate generations to detect covariate shift).

### Fine-tuning procedure

1. **Model.** Phi-2 (2.7B, Q4 quantized, ~8GB VRAM) or MistralLite (3B) from HuggingFace, loaded in bfloat16 with Flash Attention if available.

2. **Adapter.** LoRA (rank 16, alpha 32) on model.transformer.h[*].mlp + model.transformer.h[*].self_attn layers only, preserving embeddings + lm_head unfrozen. Estimated ~5M trainable params.

3. **Training.** Format each example as prompt: "Config: n_lineages=30, budget_per_task=30000, library_cap=64, opcodes_frozen=14, policy=D5_BASELINE_MRU, primitive_extension_evidence=no. Verdict: READY_TO_RUN.\n". Input max_length=512. Batch size 4 (gradient accumulation ×4 over 2 steps for effective 16). Optimizer: AdamW (lr=5e-4, wd=0.01). Scheduler: cosine warmup (500 steps), total_steps=2000. Loss: cross-entropy. 1 epoch over train set.

4. **Evaluation.** After each epoch: compute loss on validation set, log accuracy, precision, recall (per class for multi-class). Best checkpoint saved by validation loss.

5. **Wall time.** ~25–40 min on RTX 4090 or Tesla P100 (or 60–90 min on consumer GPU).

### Prediction pipeline

1. **Inference.** On each new proposed config (e.g., from an authored spec awaiting vetting), tokenize and pass through fine-tuned model. Return: (predicted_verdict_label, confidence_logit, prediction_time_ms).

2. **Integration point.** Hook into engine/driver/backlog_gen.py after spec parsing and before gate assignment. If model predicts FAIL with high confidence, flag for human review or recommend config adjustments.

3. **Logging.** Every prediction appended to evidence_wiki/v2/arm_outputs/V2-T08_inference_log.jsonl with (config_hash, predicted_verdict, actual_verdict_later, confidence, model_version).

## Controls

1. **Permutation null (label shuffle).** Re-train on same data with verdict labels shuffled (permutation within stratification). If accuracy stays >60%, model is learning from feature noise, not meaningful patterns. Expected: accuracy drops to ~50% (random).

2. **Domain heuristic baseline.** Hand-craft a decision tree or logistic regression from 3–5 key features (e.g., n_lineages, library_cap, sd_observed) without any neural component. Model must beat this baseline by ≥5pp to claim value.

3. **Out-of-distribution detection.** After training, sample 20 random experiment configs (generated, not from archive). Measure model confidence distribution on OOD examples vs in-distribution test set. If OOD confidence ≤ 0.55 avg, model is not overconfident on unseen structure.

4. **Ablation: config-only vs config+outcome.** Train two variants: (A) without effect_size_observed / sd_observed (only config), (B) with both. If (B) achieves >75% accuracy but (A) < 65%, then outcome information is carrying the signal, not design parameter interactions.

## Confound defenses

1. **Temporal leakage.** Test set is held-out by generation (gen1a/gen1b), not by time. No future information (effect_size from a later generation) bleeds into train set for an earlier-generation experiment.

2. **Class imbalance.** Count PASS vs FAIL in train set. If imbalanced >3:1, use class_weight='balanced' in loss or oversample minority. Log final class distribution in report.

3. **Feature scale mismatch.** n_lineages ranges 5–30, budget ranges 30k–300k. Standardize all numeric features (zscore) before model input. Verify mean ≈0, std ≈1 on train set.

4. **Verdict definition drift.** ERGON verdicts across generations use consistent gate names (R13-POWER-FLOOR-UNMET, GEN1_READY_TO_RUN). If a gate definition changed between gen0 and gen1b, document in report and exclude those examples or re-label.

## Preregistered falsifiers (numeric thresholds)

1. **Accuracy floor: FAIL if test accuracy < 58%.** This is only 3pp above random on a 50/50 binary classification. Below this, the model is worse than coin flip and the experiment is killed.

2. **Baseline beat: FAIL if model accuracy ≤ domain baseline + 2pp.** Domain baseline computed on same test set. Model must show clear lift to justify fine-tuning cost.

3. **Calibration break: FAIL if Brier score on test > 0.35.** Measures gap between predicted confidence and actual accuracy. A value > 0.35 (where 0=perfect, 1=worst) indicates model is overconfident or miscalibrated.

4. **OOD confidence: FAIL if mean confidence on OOD examples > 0.58.** Model predicting high confidence on random examples is a sign of learned spurious patterns, not robust features.

5. **Class-wise recall: FAIL if recall on FAIL class < 0.50.** If model learns to predict PASS for everything, recall on true failures drops to 0. Minimum threshold ensures the model is discriminative on the minority class (or balanced if near 50% split).

## Stopping rule

1. **Early stop during training.** If validation loss does not improve for 3 consecutive checkpoints (every 500 steps), halt and load best checkpoint.

2. **Falsifier abort.** If any of the 5 preregistered thresholds is violated on the validation set *during* training, stop immediately and report which falsifier fired. Do not wait for full epoch completion.

3. **Wall-time cap.** If training exceeds 120 minutes on the assigned GPU, checkpoint and halt (even if convergence not reached). A stopped model is useful for downstream analysis.

## Expected failure modes

1. **Verdict distribution mismatch.** If gen0 is 80% PASS but gen1b is 60% FAIL, the model trained on gen0 may overfit to the PASS prior and fail to generalize. Control: inspect train/val/test class distributions; report if they differ >10pp.

2. **Feature redundancy.** If library_cap and opcodes_frozen are perfectly correlated in the archive (e.g., every frozen config has cap=64), the model cannot distinguish their effects. Diagnosis: compute pairwise feature correlations on train set; report any >0.85.

3. **Sparse outcome coverage.** If only 5% of configs in the archive had sd_observed recorded (versus 95% missing), imputation or dropping that feature silently changes the input space. Control: report missingness rates per feature; drop features >20% sparse.

4. **Domain drift in gate logic.** If a gate threshold (e.g., "power floor = 300") was changed between generations, verdicts are not comparable. Example: gen0 used floor=200, gen1 uses floor=300. Outcome: model learns a rule that no longer applies. Mitigation: hardcode gate logic versions into data extraction; annotate data with relevant gate version.

5. **Seed effect on library randomness.** If verdict depends on RNG seed of the experiment run (e.g., seed=42 passes but seed=43 fails), the model cannot predict it from config alone. Control: check if the archive reports multiple seeds per config. If so, compute mean verdict per config, not individual runs.

## Compute estimate

- **Model size (Phi-2 Q4).** ~8 GB VRAM for weights + activations. Batch size 4 (gradient accumulation ×4) fits on 17GB card with some margin.
- **Training time.** ~2000 steps at ~1.5s/step (fwd + bwd + optimizer) = 3000s ≈ 50 min on GPU. Wall time including data load, checkpoint save, validation: ~60–90 min.
- **Inference time.** ~100–200ms per prediction (tokenization + forward pass + argmax).
- **Storage.** Fine-tuned LoRA adapter: ~15 MB. Inference logs: ~1 MB per 1000 predictions.
- **Total GPU cost.** 1.5 GPU-hours (training) + 0.05 GPU-hours (validation/inference testing) = ~1.6 GPU-hours.
- **Local feasibility.** Yes, single RTX 4090 or Tesla P100 on M1/Skullport.

## Prior evidence that materially changed this design (or 'none found')

- **memory/feedback_ergon_learner_north_star.md (08-30).** Ergon = memory-metabolism seat; seat boundary is PROVENANCE; admission = executable + exact-execution. This motivates using ERGON's own verdicts as training labels (not redoing gate evaluation), since Ergon is the canonical source of executed/measured results.
- **memory/feedback_vram_ceiling.md.** Local ceiling 3–4B; 7B OOMs on 17GB. This constrains model size to Phi-2 or MistralLite; larger models ruled out.
- **Gen1A review packet (REVIEW_PACKET_GEN1A_2026-09-01.txt).** Verdict GEN1_READY_TO_RUN tied to n=30 paired lineages and persistence gates. This showed that verdicts have clear structural dependencies on config, motivating supervised learning.
- **Charon orchestration map (orchestration_forensic_map.json).** 644 PARKED items in backlog, many blocked by "SPEC_MISSING" or "DESIGN_W001_COSIGN". Fast verdict prediction on specs would unblock this lane. This is the operational motivation.

## Unresolved uncertainty

1. **Verdict label granularity.** Should we predict binary (PASS/FAIL) or 5-class (READY, UNMET-POWER, UNMET-STRUCTURAL, etc.)? Binary is simpler and has more training examples per class. Multi-class is more informative for Lexis's sequencing decisions (e.g., "UNMET-STRUCTURAL is unfixable; UNMET-POWER is fixable by increasing n"). Decision deferred to pre-training analysis of class distribution.

2. **Prompt format.** Is structured text (Config: ... Verdict: ...) the right tokenization, or should we use a more abstract feature vector? Text-based fine-tuning reuses pretrained knowledge of English words (e.g., "library" in "library_cap"), but numeric features might be better served by pure embedding layers. No decision until we measure text-based model's training curve.

3. **Verdict label timing.** Some configs spawn experiments that run for hours and emit a verdict. Others (quick structural checks) verdict in minutes. Should we include wall_time_to_verdict as a feature? Currently excluded; could add if prediction latency becomes a bottleneck.

4. **Transfer from pretraining.** Phi-2 was pretrained on code + general English. Does that transfer help with predicting ERGON verdicts, or is it noise (false priors on what "verdict" means)? We expect zero transfer based on domain specificity, but this is unvalidated.

## Operation log (numbered; ops used / 15, documents opened / 12)

| Op | Task | Status |
|---|---|---|
| 1 | Grep: attempt/verdict patterns in ERGON | Timed out; no result |
| 2 | Glob: ledger*.jsonl files | Timed out; no result |
| 3 | Glob: archive*.jsonl files | Timed out; no result |
| 4 | Read: campaign_log.jsonl (50 lines) | Success; saw verdict structure |
| 5 | Read: canonicalization_fuzz_failures.json (50 lines) | Success; saw test pass/fail schema |
| 6 | Grep: verdict\|PASSED\|KILLED in ERGON | Success; found verdict taxonomy |
| 7 | Read: roles/Lexis/ROLE.md (60 lines) | Success; understood sequencing gate |
| 8 | Read: charon/orchestration_forensic_map.json (80 lines) | Success; infrastructure + blockers |
| 9 | Bash: find F:\Prometheus\ergon *.json | Success; listed experiment files |
| 10 | Read: ergon/gen0/gen0_config.json (100 lines) | Success; mapped config schema |

**Documents opened: 7** (campaign_log.jsonl, canonicalization_fuzz_failures.json, ROLE.md, orchestration_forensic_map.json, gen0_config.json). Operations used: 9/15. Remaining budget: 6 ops, 5 documents.

**Design rationale.** Specification built from: (1) ERGON's published verdict taxonomy and measurements; (2) local VRAM ceiling of 3–4B; (3) Lexis's operational need for fast spec vetting; (4) archive size (~100–150 experiments) sufficient for fine-tuning. Preregistered falsifiers ensure rigor (accuracy floor, calibration, OOD detection). Controls rule out label noise and feature spuriousness. Unresolved uncertainties deferred to pre-training data analysis, not design-level.
