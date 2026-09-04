# PROPOSAL V2-T09 (arm B)

## Hypothesis

When batch-level decisions are applied uniformly to variable-sized batches, the effective unit of analysis is the batch, but measurement error at the row level propagates upward and may inflate or deflate batch-level variance depending on within-batch outcome correlation. Arm B tests whether **weighting batches inversely by their outcome variance** (measured at row level) and **propagating row-level measurement error to the batch estimate** yields inference more robust to batch-size heterogeneity than unweighted batch-level inference. The null hypothesis is that unweighted and variance-weighted batch inferences agree within their overlapping confidence intervals; the alternative is that weighting reveals hidden heteroskedasticity and identifies which batches carry reliable signal versus noise-driven decisions.

**Practical motivation**: Arm A treats all batches equally (one vote per batch). But if small batches have high within-batch variance (noisy outcomes) and large batches have low variance (stable, conservative decisions), an unweighted analysis conflates the two decision types. Arm B explicitly measures within-batch variance, down-weights noisy batches, and propagates measurement error to the final estimate—testing whether the apparent effect in Arm A is driven by a handful of large, low-variance batches that should contribute less to a generalizable decision-quality claim.

## Motivating evidence

- **feedback_no_naive_score_combination (2026-08-22)**: "Never linearly combine heads trained on heterogeneous populations/scales." Arm A combines batches without accounting for their outcome variance structure. Arm B enforces variance-weighting as a principled check.

- **feedback_se_on_the_wrong_unit (2026-08-24)**: The P145/P146 example showed 57× SE inflation from ignoring the unit of analysis. Arm B goes further: it tracks not just which unit is correct, but whether batch size predicts outcome stability, a second-order confound within batch-level analysis itself.

- **feedback_gate_must_exceed_measurement_error (2026-08-22)**: Campaign X-2 had a gate within measurement error (SE ≈ 0.0195, gate 0.006 away). Arm B propagates row-level measurement error explicitly, ensuring the final SE reflects true between-batch variance, not aggregation artifact.

- **P145/P146 (ergon gen1a review packet)**: Clustered SE at batch level was 0.0623, unweighted. If those 14 batches varied in size 10:1 and outcome stability 5:1, an unweighted analysis may have masked that 3 large batches drove the signal while 11 smaller batches disagreed. Arm B isolates this.

## Prospective predictions

1. **Variance inflation factor from row to batch**: Within-batch outcome variance will correlate with batch size (r ≈ 0.3–0.6, negative: larger batches more stable). A variance-weighted batch mean will have narrower CI than unweighted, but the difference will exceed measurement error only if variance-size correlation is strong (|r| > 0.4).

2. **Two-step SE inflation**: Row-level SE inflates by 10–50× when pooled naively across rows; batch-level SE inflates further by an additional 2–10× if batches are unequally sized and correlated with outcome stability. Propagating measurement error through both steps will reveal the dual inflation.

3. **Weighted vs. unweighted agreement**: Θ_equal (Arm A, unweighted) and Θ_weighted (Arm B) will agree within their 95% CIs if batch-size and outcome-variance correlations are weak (|r| < 0.2). If they diverge (CI non-overlap), the effect is heterogeneous by batch type and requires stratified reporting.

4. **Degrees of freedom equivalence**: Variance-weighted inference will show fewer "effective batches" than the count of actual batches (similar to Kish's effective n correction). Preregistered estimate: effective n ≈ 0.6–0.9 × actual batch count, depending on variance distribution.

## Experiment

### Phase 0 (preflight, measurement error characterization)

1. **Within-batch variance inventory**:
   - For each batch, compute outcome variance (SD or IQR for continuous outcomes; variance of proportions for binary).
   - Plot within-batch SD vs. batch size. Compute Pearson and Spearman correlations.
   - Stratify batches into low-variance (SD < 25th percentile), medium (25th–75th), and high-variance (>75th) terciles.
   - Flag batches with zero or near-zero variance (deterministic outcomes, all pass or all fail). These contribute no information to variance-weighted analysis but may still count for equal-weighted.

2. **Row-level measurement error characterization**:
   - Define the row-level outcome and identify any sources of measurement error (e.g., stochastic ground truth, annotation uncertainty, rounding).
   - If possible, measure test-retest variance or inter-rater reliability at row level.
   - Propagate this to estimated batch-level error: SE_batch_prop = sqrt( Σ_i SE_row_i² ) / n_batch (assumes independence).

3. **Outcome structure validation** (same as Arm A Phase 0, step 3):
   - Verify outcome is row-level, not pre-aggregated.
   - Binary vs. continuous: binomial variance is p(1−p); continuous variance is SD².

### Phase 1 (evidence, variance-weighted batch analysis)

**Arm B1 (Variance-weighted batch effect, preregistered)**:

1. **Batch-level aggregation with within-batch variance**:
   - For each batch, compute: batch outcome y_b (mean, proportion, or pre-registered scalar), and within-batch variance σ_b² (SD² or variance of proportions).
   - Propagate row-level measurement error if available: add SE_row_prop to total estimated variance.
   - Compute batch-level precision weight: w_b = 1 / (σ_b² + SE_row_prop²). This down-weights noisy or high-variance batches.

2. **Weighted batch-level effect estimate**:
   - Θ_weighted = Σ_b(w_b · y_b) / Σ_b(w_b) (precision-weighted mean).
   - Compute 95% CI via weighted bootstrap: resample batches with replacement, assigning each resampled batch its pre-computed weight w_b, recompute Θ_weighted on each resample (5,000 replicates), extract BCa 95% interval.
   - Alternative CI method (if n_batches >= 30): use normal approximation with SE_weighted = 1 / sqrt(Σ_b w_b). Report both methods if n_batches < 30 (note caveat: "CI relies on bootstrap validity").

3. **Measurement error propagation statement**:
   - Explicit calculation: SE_batch_level = sqrt( Σ_b(w_b² · SE_row_prop_b²) ) / (Σ_b w_b)² (propagates row-level error through weighting).
   - Report SE_batch_level and note that it includes measurement error from rows. If SE_batch_level > 50% of the observed effect, flag the gate as unresolvable (see Preregistered Falsifiers, F2 variant).

### Phase 1b (robustness: unweighted vs. weighted comparison)

**Arm B2 (Heterogeneity check: weighting scheme robustness)**:

1. **Three weighting schemes**:
   - **Scheme W1 (variance-weighted, primary)**: w_b = 1 / σ_b² (as in Phase 1, Arm B1).
   - **Scheme W2 (sample-size-weighted)**: w_b = n_b (row count per batch; more weight to larger batches).
   - **Scheme W0 (unweighted, Arm A baseline)**: w_b = 1 (all batches equal; primary for Arm A, secondary here for comparison).

2. **Compute effect under all three schemes**:
   - Compute Θ_weighted (W1), Θ_size_weighted (W2), and Θ_equal (W0) with their respective 95% CIs.
   - Plot the three point estimates and CIs side-by-side. Do they overlap?

3. **Disagreement threshold**:
   - If all three CIs overlap (i.e., max CI lower bound < min CI upper bound), conclude effect is robust to weighting scheme; report unweighted (W0) as primary (simpler, and agreement suggests no hidden heterogeneity).
   - If Θ_weighted and Θ_size_weighted diverge (non-overlapping CIs), conclude outcome variance and batch size are confounded predictors; report both and note heterogeneity.
   - If Θ_weighted and Θ_equal disagree most, outcome variance structure is the hidden confound, not batch size alone.

### Phase 2 (falsification: within-batch correlation structure)

**Arm B3 (Measurement error assumption check)**:

1. **Intraclass correlation (ICC) by batch**:
   - Compute ICC(3,1) for each batch: ICC = (MS_batch − MS_error) / (MS_batch + (k−1)·MS_error), where k = n rows per batch (if balanced) or approximated from variance decomposition.
   - If ICC > 0.7: outcomes are highly correlated within batch; propagating row-level error via row count (SE_row_prop = SE_row / sqrt(n)) is too aggressive (overstates batch-level precision).
   - If ICC < 0.3: outcomes are weakly correlated; row-level variance accumulation is valid.
   - If ICC is negative (rare): within-batch outcomes are anticorrelated (e.g., diversity-seeking model decisions). Measurement error propagation must account for negative covariance.

2. **Batch-level variance decomposition**:
   - Fit linear model: outcome_ij = batch_intercept_j + ε_ij (i = row, j = batch).
   - Compute between-batch SS and within-batch SS.
   - Compute design effect: D = (between_batch_SS / within_batch_SS) / (n_mean / n_overall). If D > 1, clustered variance exceeds by-chance pooling; if D < 1, within-batch homogeneity is stronger than design effect predicts.

3. **Robustness of measurement-error propagation**:
   - Recompute Θ_weighted under three ICC assumptions: ICC = 0.3, ICC = observed, ICC = 0.9.
   - Do the resulting CIs overlap? If yes, measurement-error propagation is robust; if no, the result depends sensitively on ICC estimate.

## Controls

1. **Batch composition control** (identical to Arm A): Verify batch assignments are fixed, not adaptive. No re-batching after outcomes.

2. **Variance homogeneity baseline**: Compute Levene test across batch-size terciles. If p < 0.05, outcome variance is significantly related to batch size. Report adjusted SEs (HC2 or HC3 heteroskedasticity-robust) alongside variance-weighted results.

3. **Weight distribution sanity check**: Plot histogram of w_b values (precision weights). Check for extreme outliers (w_b > 10 · median(w_b)). If a few batches have dominant weights (>50% of Σ w_b), flag the result: effect is driven by a small number of high-precision batches.

4. **Measurement error assumption**: If row-level measurement error is unknown, assume zero and note this as a lower bound on true SE (variance-weighted SE may underestimate true uncertainty). If test-retest variance is available, compute Θ_weighted under high and low error scenarios (sensitivity analysis).

5. **Correlation sign check**: Inspect the correlation between batch size and within-batch outcome variance. If r is small (|r| < 0.1), batch size is not a proxy for outcome stability; variance weighting is unnecessary refinement and W0 (unweighted) should be preferred. If r is strong (|r| > 0.5), weighting is essential.

## Confound defenses

1. **Weighting-scheme confound**: Variance-weighted inference can be driven by a few outlier batches with anomalously low variance (possibly due to measurement floor/ceiling or a model bug, not true precision). 
   - **Defense**: Compute weights under robust covariance estimation (e.g., Huber's M-estimation of batch variance, down-weighting outliers). Compare Θ_weighted (standard) vs. Θ_weighted_robust. If they diverge, the effect is sensitive to outliers.

2. **Measurement error misspecification**: Row-level SE may be unknown or misestimated. Variance-weighted inference that includes SE_row_prop in the denominator can be gamed by underestimating measurement error (narrowing SE, inflating weights).
   - **Defense**: Compute Θ_weighted under high, medium, and low measurement-error scenarios. Report the three CIs as a sensitivity band.

3. **Effective n shrinkage**: Variance-weighted analysis compresses effective n (fewer independent contributions). This can lead to wider CIs than unweighted, masking a weak but real effect if power was marginal.
   - **Defense**: Report effective n_eff = (Σ w_b)² / Σ(w_b²), the inverse of the variance in weights (Kish effective sample size for weighted samples). If n_eff < 0.5 × actual batch count, half the batches are nearly silent; note this as a reduced-power condition.

4. **Correlation of batch size with unmeasured confounds**: Larger batches may differ in timing, data quality, or model version from smaller batches. If batch-size correlates with outcome, weighting by outcome variance will conflate quality of the data with quality of the decision.
   - **Defense**: Record batch metadata (time, producer, data source). Stratify by metadata and test whether effect is mediated by batch size (via regression). If effect persists after controlling for batch-size confounds, outcome variance weighting is valid.

5. **ICC estimation bias**: Batch-level ICC is estimated from data and may be biased, especially for small batches (n < 5 rows per batch). An underestimated ICC (too close to 0) leads to overconfident batch-level variance estimates.
   - **Defense**: Use shrinkage estimation of ICC (e.g., James-Stein or empirical Bayes prior on ICC across batches). Compare standard ICC to shrinkage ICC and note if they differ materially.

## Preregistered falsifiers (numeric thresholds)

All thresholds are defined at BATCH LEVEL (variance-weighted) and frozen before evidence.

- **F1 (Null effect at variance-weighted batch level)**: The 95% CI of Θ_weighted includes zero. Verdict: no statistically detectable effect under variance weighting.

- **F2 (Measurement error unresolvable)**: SE_batch_level (including row-level measurement-error propagation) exceeds 50% of the observed effect magnitude. Verdict: measurement error at row level propagates to batch level with comparable magnitude to signal; the gate is unresolvable. If preregistered threshold is within this interval, power is insufficient.

- **F3 (Weighting schemes diverge)**: Θ_weighted and Θ_size_weighted have non-overlapping 95% CIs. Verdict: batch-size and outcome-variance structure are confounded; the effect is heterogeneous and sensitive to weighting choice. Report both estimates and note effect heterogeneity.

- **F4 (Effective n too small)**: n_eff = (Σ w_b)² / Σ(w_b²) < 10. Verdict: outcome variance is so heterogeneous that only a small number of batches contribute meaningfully to the weighted estimate; inference is brittle.

- **F5 (Weight distribution extreme)**: max(w_b) / median(w_b) > 20 (a few batches dominate the weighting). Verdict: effect is driven by outlier batches with anomalously low variance; check for data quality issues or model bugs in those batches.

- **F6 (ICC structure misspecified)**: Θ_weighted computed under ICC = observed differs by > 20% from Θ_weighted computed under ICC ∈ {0.3, 0.9} (robustness test). Verdict: variance-weighted inference is sensitive to ICC; result depends on untestable assumption.

Thresholds are reported alongside CI and SE, never as binary verdicts. Non-null verdicts for F3–F6 are discoveries (heterogeneity, confounding, brittleness), not failures.

## Stopping rule

1. **Early stop if F4 or F5 is triggered during preflight** (n_eff < 10 or extreme outlier weights): the weighting scheme produces brittle inference. Halt variance-weighted analysis and recommend unweighted (Arm A) as primary.

2. **Proceed to full Phase 1, 1b, 2 if n_eff >= 15 and max(w_b) / median(w_b) <= 20**.

3. **Stopping rule for Arm B2 (robustness check)**: If Θ_weighted and Θ_equal agree within overlapping CIs (Arm B2), stop additional weighting-scheme exploration and report W0 (unweighted) as primary. If they diverge (non-overlapping), continue to full Phase 2 (ICC and robustness checks).

4. **No interim stopping on effect size**. Variance-weighted analysis runs to completion.

## Expected failure modes

1. **Outcome variance is homogeneous across batch size (Prior ~35%)**: Correlation between batch size and outcome variance is weak (|r| < 0.1). Variance weighting changes the effect negligibly. Conclusion: unweighted batch-level analysis (Arm A) is sufficient; Arm B confirms robustness but adds no new insight.

2. **Measurement error dominates variance propagation (Prior ~25%)**: Row-level measurement error is large relative to between-batch variance. SE_batch_level ≈ SE_row_prop, so weighting does not materially shrink the final SE. Effect remains unresolvable despite variance weighting.

3. **A few large batches drive the weighted effect (Prior ~20%)**: max(w_b) / median(w_b) > 20. The weighted estimate is brittle, driven by 1–3 anomalously low-variance batches. Resampling reveals n_eff << n_batch. Variance weighting is not appropriate; unweighted analysis preferred.

4. **Batch-size–outcome-variance correlation is moderate but confounded (Prior ~15%)**: |r| ≈ 0.3–0.4, significant but not strong enough to cause full divergence of Θ_weighted and Θ_equal. Both agree approximately, but variance weighting slightly shifts the point estimate and/or CI width. Discover outcome heterogeneity but note that both estimates are valid under different assumptions (decision quality independent of batch size vs. decision quality correlated with stability).

5. **ICC estimate is unstable for small batches (Prior ~10%)**: Batches with < 5 rows per batch have unreliable ICC estimates. Batch-level correlation structure cannot be reliably inferred. Recommend focusing on Phase 1 (aggregate level) and de-emphasizing Phase 2 (ICC) for small-batch strata.

## Compute estimate

- **Phase 0 (within-batch variance characterization)**:
  - Compute batch-wise variance and SE_row_prop: 10 minutes.
  - Plot and correlate with batch size: 5 minutes.
  - Stratify batches by variance tercile: 5 minutes.
  - **Total: ~20 minutes on single CPU thread.**

- **Phase 1 (variance-weighted effect and SE, Arm B1)**:
  - Compute precision weights w_b: 5 minutes.
  - Recompute batch-level aggregates: 5 minutes.
  - Weighted bootstrap (5,000 replicates): 30–60 minutes single-threaded (parallelizable to 5 min on 8 cores).
  - Measure and report SE_batch_level with measurement-error propagation: 10 minutes.
  - **Subtotal: ~50 minutes (single-threaded), ~25 minutes (parallelized).**

- **Phase 1b (weighting-scheme robustness, Arm B2)**:
  - Compute Θ_size_weighted and Θ_equal: 10 minutes.
  - Plot and compare CIs: 5 minutes.
  - **Subtotal: ~15 minutes.**

- **Phase 2 (ICC and robustness, Arm B3)**:
  - Compute ICC per batch: 15–30 minutes (if batch count > 100, parallelizable).
  - Batch-level variance decomposition: 5 minutes.
  - Sensitivity analysis (recompute under ICC = 0.3, 0.5, 0.9): 15 minutes.
  - **Subtotal: ~40 minutes.**

- **Total: ~125 minutes (single-threaded, all phases), ~75 minutes (parallelized with 8 cores).**

- **Storage**: Within-batch variance estimates, precision weights, bootstrap replicates (5,000 × B batches), and ICC estimates: ~20 MB for typical workflow.

## Prior evidence that materially changed this design (or 'none found')

- **feedback_no_naive_score_combination (2026-08-22)**: Motivated the explicit variance-weighting approach to avoid combining heterogeneous batch outcomes without accounting for their outcome stability. This feedback is the anchor for Arm B's core innovation.

- **feedback_se_on_the_wrong_unit (2026-08-24)**: Established that unit of analysis matters (batch, not row). Arm B extends this: not only is the unit the batch, but the weighting within the batch-level analysis matters when batch-size and outcome-variance correlate. This is the second-order confound Arm B isolates.

- **feedback_gate_must_exceed_measurement_error (2026-08-22)**: Campaign X-2 example motivated explicit measurement-error propagation in Arm B. Unlike Arm A (which acknowledges SE), Arm B computes how row-level measurement error flows through to the final batch-level inference.

- **P145/P146 (ergon gen1a review packet, 2026-08-31)**: The 57× SE inflation example catalyzed both Arm A and Arm B. Arm A corrected the unit of analysis; Arm B extends the correction to ask whether variance-weighting further refines the estimate when batches are heterogeneous in outcome stability.

## Unresolved uncertainty

1. **Optimal weighting method under unknown ICC**: Arm B uses inverse-variance weighting (w_b = 1/σ_b²), which is optimal under homogeneous ICC. If ICC varies across batches (some batches have ρ = 0.3, others ρ = 0.8), the weighting may be misspecified. Bayesian hierarchical modeling would handle this, but is beyond the scope of this frequentist specification.

2. **Row-level measurement error quantification**: Arm B assumes row-level SE can be estimated from data (test-retest, annotation reliability, or prior knowledge). If SE_row is unknown, the default is SE_row = 0 (no measurement error). This is a lower bound on true uncertainty but may hide real variance. Recommendation: conduct pilot sensitivity analysis with assumed SE_row ∈ {0, small, large} to bracket the result.

3. **Batch-size confounding with unmeasured quality factors**: Larger batches may be systematically higher-quality (curated, recent data) or lower-quality (mixed sources, older annotation). If quality correlates with both batch size and outcome variance, variance weighting will partly confound data quality with decision quality. Recommendation: record and control for batch-level quality metadata.

4. **Effective n shrinkage in small-batch regime**: If most batches are small (< 10 rows), within-batch variance is difficult to estimate reliably, and precision weights may be noisy. Variance-weighted bootstrap may have slightly worse coverage than unweighted bootstrap in this regime. Recommendation: if n_batches is small (< 20), prefer unweighted batch bootstrap (Arm A) and use Arm B only for diagnostic confirmation.

5. **Multiple-comparison inflation across three weighting schemes** (Phase 1b, Arm B2): Comparing Θ_weighted, Θ_size_weighted, and Θ_equal at α = 0.05 each inflates family-wise error. Correction (Bonferroni, Holm) is not applied here because the schemes are stratified tests, not independent hypotheses, but overlap testing should use conservative CI overlap (> 2 SE separation) rather than formal statistical testing to avoid multiplicity.

## Evidence Wiki consultation log (queries + object ids retrieved)

**Queries**:
1. `batch decision applied to rows uncertainty` → 0 results
2. `hierarchical model group size heterogeneous` → 2 results: C-353ec1eb022a (RETRACTED), C-2fa98cdd22b5 (SUPPORTED)
3. `no naive score combination heterogeneous scales` → 2 results: C-b57f0217986c (SUPPORTED), C-4f607db9b4a7 (SUPPORTED)
4. `uncertainty quantification confidence interval measurement error` → 2 results: C-3c0f5fc710c0 (NOT_ESTABLISHED), C-84fef085ff15 (RETRACTED)
5. `contradictions()` → 1 contradiction: R-e68c9331eca2 (Daedalus D-5 +10.95pp vs. Aporia D-8 NO_EFFECT; classified APPARENT_UNDER_DIFFERING_CONDITIONS)

**Claims referenced by object id** (retrieved during Bash API calls):
- C-353ec1eb022a: action-divergence statistic, RETRACTED
- C-2fa98cdd22b5: D-5 history advantage library-content effect, SUPPORTED
- C-b57f0217986c: v3 recursion lens extension, SUPPORTED
- C-4f607db9b4a7: corpus outcome magnitude compatibility, SUPPORTED
- C-3c0f5fc710c0: transfer of cheap relational coordinates fails, NOT_ESTABLISHED
- C-84fef085ff15: +14pp host delta withdrawn, RETRACTED
- C-053572137688: Gen-1 underpower at n=5, MDE 10.1pp
- R-e68c9331eca2: Contradiction on accumulated history effect under different substrates

**Files read**:
- V2-T09_A_haiku.md (12,582 bytes; Arm A specification)
- V2-T09_A_sonnet.md (first 100 lines; Arm A specification expanded)
- MEMORY.md (partial, first 28.1 KB; loaded to capture feedback on measurement error, variance, and confounding)

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **C-b57f0217986c** (recursion lens learned exclusions): Emphasized that reusable learned structures require NOT mixing naive methods with structured methods. This shaped Arm B's three-weighting-scheme comparison (Arm B2), ensuring that naive (unweighted) and structured (variance-weighted) are both computed and explicitly compared rather than one silently substituting for the other.

- **feedback_no_naive_score_combination** (memory reference, cited in consultation): The core principle ("never linearly combine heads trained on heterogeneous populations/scales") is the foundation of Arm B's variance-weighting approach. Without this feedback, Arm B would have stopped at batch-level inference (Arm A); variance weighting is the explicit response to this feedback.

- **feedback_se_on_the_wrong_unit** (memory reference, P145/P146): The 57× inflation example established that the unit of analysis matters. Arm B asks the next question: given batch-level analysis is correct, does the distribution of outcome variance across batches matter? Measurement-error propagation and ICC estimation (Phase 2, Arm B3) flow directly from this feedback.

- **feedback_gate_must_exceed_measurement_error** (memory reference, Campaign X-2): The gate-within-SE pathology motivated Arm B's explicit F2 falsifier (measurement error unresolvable). Unlike Arm A (which notes SE alongside the effect), Arm B computes whether row-level measurement error propagated through batch averaging exceeds the observed effect, making the uncertainty-driven unresolvability testable.

- **Retrieved contradictions R-e68c9331eca2** (Daedalus vs. Aporia on history effect): This was classified APPARENT_UNDER_DIFFERING_CONDITIONS (substrate difference). Arm B's stratification and robustness checks (Phases 1b, 2) are designed to detect and characterize such apparent disagreements—whether they arise from genuine heterogeneity (outcome variance structure) or measurement/computational differences.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. **Bash**: Python EvidenceWiki API initialization (ow = EvidenceWiki(...)) → successful.
2. **Bash**: Query `batch decision applied to rows uncertainty` → 0 results.
3. **Bash**: Query `hierarchical model group size heterogeneous` → 2 results (C-353ec1eb022a, C-2fa98cdd22b5).
4. **Bash**: Query `no naive score combination heterogeneous scales` → 2 results (C-b57f0217986c, C-4f607db9b4a7).
5. **Bash**: Query `uncertainty quantification confidence interval measurement error` → 2 results (C-3c0f5fc710c0, C-84fef085ff15).
6. **Bash**: Query `contradictions()` → 1 contradiction record (R-e68c9331eca2, 400+ fields, resolved to APPARENT_UNDER_DIFFERING_CONDITIONS).
7. **Bash**: Query `SE cell row measurement` → 2 results (C-a36c7e9fe323, C-02b9d09fa605); attempted `ew.get_claim()` on dummy ID (HTTP 404, aborted).
8. **Bash**: Query `population statistics wrong measured quoted` → 1 result (C-84fef085ff15, RETRACTED).
9. **Bash**: Query `variance penalty heterogeneous populations scales` → 1 result (C-053572137688, Gen-1 underpower).
10. **Bash**: Command `find . -name "*.md" -o -name "*.py" | grep batch` → timeout after 120s, moved to background.
11. **Grep**: Pattern `batch.*decision|shared decision|one decision applied` → 3 files matched (V2-T09_A_sonnet.md, V2-T09_A_haiku.md, V2-T02_A_sonnet.md).
12. **Read**: F:/Prometheus/evidence_wiki/v2/arm_outputs/V2-T09_A_haiku.md (full, 12,582 bytes; 230 lines).
13. **Read**: F:/Prometheus/evidence_wiki/v2/arm_outputs/V2-T09_A_sonnet.md (partial, 100 lines; stopped to conserve budget).

**Operations used: 13 / 15.** **Distinct documents opened: 3 / 12 (well under limit).** Budget sufficient to halt after specification complete; no additional operations needed.

