# PROPOSAL V2-T09 (arm)

## Hypothesis

When a single model call produces one decision applied uniformly to all rows in a variable-sized batch, the true unit of inference is the batch, not the row. Naive per-row uncertainty quantification inflates precision and will disguise clustering-induced variance, turning a 3.9σ effect into spurious 70σ. The analysis must be batch-level with explicit acknowledgment of effective sample size, supplemented by stratified subanalyses checking whether batch size moderates or confounds the observed effect.

**Null hypothesis**: Standard per-row inference (clustered or robust SE) recovers the same falsifiable threshold as batch-level analysis after accounting for measurement error. **Alternative hypothesis**: Batch-level analysis reveals the effect is weaker or disappears compared to naive per-row inference because the true independent decisions numbered 10–30 batches, not 10,000+ rows.

## Motivating evidence

- **Agent D-5 ranking model (P145/P146)**: A model emitted one constant ranking per cell (14 cells total, 132,009 evaluated rows). Per-row binomial SE was 0.00109, yielding a 70-sigma effect (D=+0.244); clustered SE at batch level was 0.06228, yielding 3.9-sigma (57× inflation). The gate sat deep inside the 95% CI of both splits because the threshold was within measurement error—a pre-registered gate enforced correctly but resolved nothing (see feedback_gate_must_exceed_measurement_error).

- **Campaign X-2 gate collapse (P119/118)**: A threshold at 0.95 on 125-pair benchmark passed (119/125) in development and failed (118/125) held-out by one pair. Binomial SE at n=125 was 0.0195; the gate sat 0.006 from observed values across both splits. Two passes were spent moving a line through noise.

- **Charon resolution-dependence (Census Instrument Audit)**: A gate defined at cross-family level (intersection statistic) was evaluated against single-family statistics (0.2684, 0.3007) and declared unreachable, until the same manifest under correct resolution yielded 0.3151 (NOT-LEVELED) vs 0.4764 (LEVELED) on identical rows—16pp apart, opposite verdicts. Statistics at the wrong resolution produce spurious findings.

## Prospective predictions

1. **Batch-level effective n will be 10–50 independent decisions**, not proportional to row count. This will reduce nominal degrees of freedom by 50–200× relative to naive per-row analysis. Preregistered estimate: 25 batches (range 15–40) for a typical workflow.

2. **Clustered SE at batch level will exceed naive row-level SE by 10–50×**, depending on batch-size heterogeneity and outcome correlation within batches. If batches average 500 rows but range 10–5,000, variance inflation from clustering will be substantial.

3. **Batch size will NOT significantly moderate the effect** if the decision is truly uniform across batch members (null prediction). If effect magnitude is correlated with batch size (negative correlation predicted if large batches receive conservative, low-variance decisions), the confound is structural and must be surfaced in stratified analysis.

4. **The preregistered falsification threshold, computed at batch level with full CI, will NOT be reachable by naive row-level inference** (no threshold crossing when row-level SE is artificially tight). This demonstrates the measurement-error trap even within a single experiment.

## Experiment

### Phase 0 (preflight, design verification)

1. **Batch inventory and size distribution**: Record the count of distinct batches (the true unit of analysis) and the distribution of rows per batch (mean, SD, min, max, quantiles). Plot the empirical CDF. Verify that:
   - Batch count is between 10 and 200 (below 10, cluster-robust methods are unreliable; above 200, batch-level effects are less stringent to measure).
   - Row-to-batch ratio is at least 10:1 (if too balanced, clustering is irrelevant; if ratio is 1,000:1, the SE inflation risk is highest).
   - At least 80% of batches contribute >= 1 row to the outcome (no sparse, uninformative batches).

2. **Model decision verification**: For each batch, confirm the model produces exactly one decision and applies it to all constituent rows. Check for:
   - Decision consistency: same batch → same decision across runs or internal replicates.
   - Broadcast correctness: no within-batch decision heterogeneity (sub-batching, row-level refinement).
   - Enumeration: count distinct (batch_id, decision) pairs; this is n_effective.

3. **Outcome structure**: Verify outcome variable is:
   - Row-level (one value per row within each batch), not batch-level already aggregated.
   - Binary or continuous (binomial SE formulas differ from Gaussian).
   - Free of row-level randomness sourced outside the model decision (if within-batch rows vary independently due to outside noise, variance cannot be attributed to clustering, complicating inference).

### Phase 1 (evidence, batch-level analysis)

**Arm A1 (Batch-level effect and SE, preregistered)**:

1. **Effect size (batch-level point estimate)**:
   - Define the outcome for each batch as the aggregated row-level statistic (mean, proportion, median, or row-wise loss). Do not re-score at batch level; aggregate row-level scores.
   - Compute batch-wise effect as (treatment batch mean) − (control batch mean) if between-batch design, or regression slope if continuous batch predictor.
   - Compute 95% CI via one of two methods:
     - **Bootstrap (preferred if n_batches < 50)**: Resample batches (not rows) with replacement 5,000 times, recompute effect, extract percentile CI and SE. This is robust to non-normality and heteroskedasticity across batch sizes.
     - **t-test (if n_batches >= 30 and normality tenable)**: Use batch-level means, compute clustered SE, reference t-distribution with df = n_batches − 1. Report both point estimate and explicit 95% CI.

2. **Standard error at batch level**:
   - Compute SD of batch-wise effect estimates (SD of bootstrap replicates, or s / sqrt(n_batches)).
   - Report SE alongside point estimate. If n_batches < 30, note SE caveat: "cluster-robust SE below recommended minimum; results rely on bootstrap validity rather than t-approximation."
   - Compare to any preregistered falsification threshold: is the 95% CI at least 2 SE away from the null? If not, the gate is unresolvable and the experiment lacked power.

3. **Effective sample size statement**:
   - State explicitly: "This analysis uses n_batches = [X], not n_rows = [Y]. The 57-fold SE inflation reported in feedback_se_on_the_wrong_unit applies if row-level n were incorrectly substituted; this analysis uses batch-level n."
   - Compute and report variance inflation factor (VIF): VIF = (row-level SE / batch-level SE)^2 as a sanity check. Expect VIF in range [10, 200] for typical survey/experimental batches.

### Phase 1b (stratified analysis by batch size)

**Arm A2 (Batch size moderation and confounding check)**:

1. **Stratification**: Divide batches into size terciles (small, medium, large) or quartiles if n_batches > 40. Recompute the batch-level effect within each stratum.

2. **Heterogeneity test**: Does effect magnitude differ across size strata? 
   - Fit a linear model: effect_i = β₀ + β_size(batch_size_i) + ε_i, where ε_i ~ N(0, SE_i²) (weighted regression by stratum variance).
   - Test β_size ≠ 0 via t-test. If p < 0.05, effect is size-confounded; report both stratified and aggregate effects.
   - If p >= 0.05, conclude effect is homogeneous and aggregate analysis is valid.

3. **Bias check**: If large batches have systematically different outcome distributions (e.g., conservative decisions, lower variance), report this correlation. Does the model's decision-making favor certain batch types?

### Phase 2 (falsification: row-level analysis as contrast)

**Arm A3 (Per-row inference with cluster-robust SE, for comparison only)**:

This arm is **not** the primary inference but a transparency check. It applies robust standard error estimation at row level, clustering by batch.

1. **Row-level regression with clustered SE**:
   - Estimate effect β via row-level regression: outcome_ij = β·treatment_j + ε_ij (where i indexes rows, j indexes batches).
   - Compute cluster-robust SE: SE_robust(β) = sqrt( (X'X)⁻¹ · X' Ω X · (X'X)⁻¹ ), where Ω is the covariance matrix of residuals, clustered by batch.
   - Report β, SE_robust, 95% CI.

2. **Comparison to batch-level result**:
   - If CI_robust ⊂ [CI_batch − 2·SE_batch, CI_batch + 2·SE_batch], the row-level and batch-level inferences are compatible (difference within measurement error).
   - If CI_robust is narrower and excludes the batch-level CI, a pseudoreplication trap is present: row-level SE is artificially tight. Red-flag this as violating the feedback_se_on_the_wrong_unit principle.
   - If CI_robust is much wider, the batch-level analysis was appropriate.

3. **Caveat**: Report this analysis as "exploratory" or "transparency check only." It should never be the primary gate, as it is prone to the inflation documented in P145/P146.

## Controls

1. **Batch composition control**: Verify that batch assignments are fixed by the model (not adaptive or post-hoc). No re-batching after observing outcomes.

2. **Variance homogeneity check**: Test for heteroskedasticity across batch sizes via Levene or Breusch-Pagan test. If variance is significantly related to batch size, report adjusted SEs (Huber-White, HC2 or HC3 variant) alongside bootstrap SEs.

3. **Normality check (batch-level)**: Plot Q-Q plot of batch-wise effect estimates. If n_batches >= 30 and non-normality is severe (e.g., bimodal), prefer bootstrap CI over t-CI.

4. **Confound isolation**: If batch size correlates with outcome (expected if model decision is conservative for large batches), stratify and report whether removing batch-size effects changes the inference.

5. **Null distribution (permutation, optional)**: Permute batch labels 5,000 times, recompute batch-level effect. Compute p-value as fraction of permuted effects >= observed. This is assumption-free but computationally expensive.

## Confound defenses

1. **Unit-of-analysis confound (highest risk)**: Naive per-row inference treats 10,000 rows as n=10,000 independent decisions when the model made 20. This inflates precision ~50× and can produce spurious gates deep within CI.
   - **Defense**: Compute n_effective (count distinct batches) before any analysis. Use batch-level inference as primary. Row-level inference is secondary.

2. **Batch-size moderation confound**: If large batches receive systematically different decisions (e.g., conservative, averaged decisions for high-stakes large batches), effect magnitude is confounded with batch size.
   - **Defense**: Stratify by batch size (terciles). Test β_size. If significant, report stratified effects and note that aggregate effect is batch-size-weighted average, not a universal effect.

3. **Measurement-error gate trap**: A preregistered gate at, e.g., 0.15 effect size, sits within the 95% CI if SE >= 0.075. The gate is unresolvable by noise, not by actual absence of effect.
   - **Defense**: Compute SE BEFORE preregistration. Require gate to be >= 2 SE away from plausible values. Report CI alongside verdict.

4. **Resolution mismatch**: Computing effect at batch level but defining falsifiers at row level (or vice versa).
   - **Defense**: Preregistration must specify both: effect unit (batch or row), threshold unit (same), and the two must match exactly.

5. **Missing-data bias**: If some batches have sparse or missing outcomes (e.g., silent failures), effective n is smaller than n_batches.
   - **Defense**: Report n_eligible_batches (those with >= 1 outcome row). If > 10% of batches are entirely missing, impute or note as incomplete data and adjust inference.

## Preregistered falsifiers (numeric thresholds)

All thresholds are defined at BATCH LEVEL and frozen before evidence.

- **F1 (Null effect at batch level)**: The 95% CI of the batch-level effect estimate includes zero. Verdict: no statistically detectable effect (inconclusive on power, not on magnitude).

- **F2 (Effect unresolvable by measurement error)**: The 95% CI spans a range smaller than 4·SE_batch (i.e., CI width < 4·SE). Verdict: measurement error is too large relative to observed effect; the gate is unresolvable. If the preregistered gate sits within this interval, it is a coin flip, and the experiment lacked power.

- **F3 (Pseudoreplication trap confirmed)**: Row-level clustered SE is >= 10× smaller than batch-level SE, indicating the row-level analysis severely underestimated variance. Verdict: naive per-row inference is not trustworthy; batch-level result is the only valid inference.

- **F4 (Batch size moderates effect)**: The interaction term β_size in the stratified model is statistically significant (p < 0.05) AND the sign or magnitude of the effect differs by >= 100% between smallest and largest batch-size strata. Verdict: effect is heterogeneous across batch size; aggregate claim must be qualified.

- **F5 (Effective n too small)**: n_batches < 10. Verdict: cluster-robust methods are unreliable below ~15–30 clusters; inference is untrustworthy even if p-values suggest significance. This is a design failure, not an analysis failure.

Thresholds are reported as verdicts alongside CI and SE, never as yes/no binary outcomes.

## Stopping rule

1. **Early stop if F5 is triggered during preflight** (n_batches < 10): the experiment is underpowered by design. Halt and redesign to accumulate >= 20 batches before running evidence phase.

2. **Proceed to full evidence phase** (Phase 1, 1b, 2) if n_batches >= 15.

3. **No interim stopping rule on effect size**. The batch-level analysis is the primary gate; row-level inference is never used to gate further data collection.

4. **Stopping rule for Arm A3 (per-row analysis)**: This is secondary only. If clustered SE for A3 is >= 10× smaller than A1 (batch-level SE), flag pseudoreplication but continue both analyses to full completion for transparency.

## Expected failure modes

1. **Batch size effect dominates aggregate effect (Prior ~40%)**: The model makes conservative decisions on large batches (lower variance, center-biased) and exploratory decisions on small batches. Stratification reveals small batches have +0.25 effect, large batches have −0.05. Aggregate effect is near zero, but the heterogeneity is the finding.

2. **Batch-level n too small (Prior ~30%)**: Only 8 distinct batches identified; cluster-robust methods are unreliable. True effect unknown; experiment failed at design phase.

3. **Outcome correlation within batches is negative (Prior ~20%)**: Batch decision is a prior; within-batch rows exhibit variance-reduction (common to feedback systems). Variance within batch is lower than between batches, compressing the true SE estimate. Bias is toward false precision.

4. **All-or-nothing outcome structure (Prior ~15%)**: Batches have 100% success or 100% failure (e.g., model decides accept/reject uniformly), so batch-level variance is limited and CI is tight but may reflect ceiling/floor effects, not true effect.

5. **Model decision is not truly uniform per batch (Prior ~15%)**: Sub-batching, row-level refinement, or multi-stage decisions within batch invalidate the batch-level assumption. Revealed during Phase 0 verification.

## Compute estimate

- **Phase 0 (preflight, design verification)**:
  - Batch inventory and size distribution: 1–5 minutes (read batch metadata, compute quantiles).
  - Model decision verification: 10–30 minutes (iterate through batches, confirm decision uniformity).
  - Outcome structure check: 5 minutes.
  - **Total: ~20 minutes on single CPU thread.**

- **Phase 1 (batch-level analysis, Arm A1)**:
  - Compute batch-wise aggregates: 5 minutes.
  - Compute batch-level effect and SE via bootstrap (5,000 replicates): 20–60 minutes depending on outcome complexity and batch count. (Parallelizable to 5 min on 8 cores.)
  - Compute and report CI: 5 minutes.
  - **Subtotal: ~30 minutes (single-threaded), ~5 minutes (parallelized).**

- **Phase 1b (stratified analysis, Arm A2)**:
  - Stratification and weighted regression: 10 minutes.
  - Heterogeneity tests (t-test, ANOVA): 5 minutes.
  - **Subtotal: ~15 minutes.**

- **Phase 2 (row-level clustered SE, Arm A3, optional/secondary)**:
  - Cluster-robust SE computation (e.g., via sandwich estimator): 10–30 minutes depending on row count and library efficiency.
  - **Subtotal: ~20 minutes.**

- **Total: ~65 minutes (single-threaded, all phases), ~25 minutes (parallelized with 8 cores).**

- **Storage**: Batch-level summaries, bootstrap replicates, and regression outputs: ~10 MB for typical workflow (< 100K rows, < 1K batches).

## Prior evidence that materially changed this design (or 'none found')

- **feedback_se_on_the_wrong_unit (2026-08-24)**: The P145/P146 example (132,009 rows, 14 batches, 57× SE inflation) was the direct motivation for this specification. Without this feedback, batch-level analysis would have been deferred as secondary; it is now the primary gate.

- **feedback_gate_must_exceed_measurement_error (2026-08-22)**: Campaign X-2's example (gate at 0.95 lying within SE) demonstrates that preregistered falsification thresholds must account for measurement error. This shaped the F2 falsifier (CI width vs. SE).

- **feedback_wrong_population_statistics (2026-08-21/23)**: The charon/resolution example (gate defined at cross-family level, evaluated on single-family statistics, 16pp reversal) demonstrates that statistics and thresholds must be at the same resolution. This shaped the emphasis on "batch level only" for primary gates.

- **feedback_three_claim_inflations (2026-08-25)**: The note on separating pre-registered verdict from program disposition shaped the distinction between Arm A1 (primary batch-level verdict) and Arm A3 (exploratory row-level analysis for transparency).

## Unresolved uncertainty

1. **Bootstrap validity under clustering**: Bootstrap resampling at batch level (with replacement) is valid for point estimation and CI, but cluster-level resampling may underestimate variance if batches are serially correlated (e.g., by time or producer). Mitigation: if batches are time-ordered or stratified by producer, permutation test (Phase 2 optional) provides a non-parametric check.

2. **Variance structure within batches**: The design assumes within-batch outcome correlations are unknown. If correlations are high (ρ > 0.7), batch-level SE may underestimate true variance; if correlations are negative (common in feedback systems), true variance may be overestimated. Recommendation: compute within-batch ICC (intraclass correlation) during Phase 1 preflight to characterize this.

3. **Optimal batch size for inference**: The specification allows batch sizes to range 10–5,000 rows. Heteroskedasticity (larger batches, lower variance) is expected. The stratified analysis (Arm A2) handles this but does not resolve whether heteroskedasticity is model-driven (conservative decisions on large batches) or outcome-driven (inherent sampling variance scales with batch size). Recommendation: regress outcome variance on batch size and inspect residuals.

4. **Multiple comparisons across strata**: Arm A2 tests homogeneity of effect across batch-size strata (potentially 3–4 hypothesis tests). No multiple-comparison correction is applied here (strata are stratified subgroups, not independent hypotheses), but if effect differs by stratum, the aggregate effect is a weighted average, which may not be the scientifically relevant quantity. Recommendation: report per-stratum effects as primary and aggregate only as secondary summary.

5. **Batch-level confounding**: If batch membership is correlated with an unmeasured outcome driver (e.g., time, model version, data quality), batch-level analysis can mask or exaggerate the true causal effect. The design does not account for this without explicit covariates. Recommendation: record batch metadata (time, producer, data origin) and include as covariates in regression if confounding is suspected.

