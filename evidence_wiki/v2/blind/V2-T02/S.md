# PROPOSAL V2-T02 (arm)

## Hypothesis
A record sanitizer with a curated known-bad-patterns list can be validated for production corpus admission use by establishing: (1) the patterns exist at measurable frequency in the target archive, (2) each pattern's detection rule has both positive and negative fixtures confirming sensitivity and specificity, (3) rejection thresholds sit within the data's attainable range, and (4) the sanitizer's decision eligibility is demonstrated against a baseline.

## Motivating evidence
- **Verify signature exists before controls (feedback_verify_signature_exists_before_controls, 08-18):** Controls against bias protect only aimed instruments. Aporia designed anti-bias validation for a `kind` field that did not exist in the target archive—0 occurrences in 35.4M corpus records—making the instrument vacuous before data touched. A mis-aimed instrument returns only the expected answer. Structural zero (patterns don't exist) must be pre-committed as a distinct reading.
- **Gate must be shown reachable (feedback_gate_must_be_shown_reachable, 08-23):** A preregistered Jaccard cut at 0.14 sat above the max attainable value (0.1364) over actual data, preventing the gate from firing on any input. A threshold outside the statistic's range is not a test; it is a predetermined outcome wearing test's clothes. Compute the attainable range on actual data before reading any null.
- **Verdict without rows is assertion (feedback_verdict_without_rows_is_an_assertion, 08-23):** Two verdicts had their raw ledgers destroyed and untracked. Rows ship in the same commit as the verdict. A sanitizer's decision is portable capability only when tied to the record ledger that prompted it.
- **Gate must exceed measurement error (feedback_gate_must_exceed_measurement_error, 08-22):** A threshold closer to observed value than its own SE is not a gate. Report the CI beside the verdict before choosing thresholds. A sanitizer gate moving at the noise floor cannot reliably distinguish signal.

## Prospective predictions
1. **Baseline existence:** The curated bad-patterns list matches ≥1 record in the target training corpus (≥5 total, ≥0.01% of rows). Prediction: ≥1 match. If 0, test returns VACUOUS and design proceeds to structural-zero protocol.
2. **Per-pattern sensitivity:** For each of K patterns with ≥10 known-positive fixtures, sanitizer detection rate ≥95% (CI lower bound ≥90%). Prediction: sensitivity metric survives CI gate before production admission.
3. **Per-pattern specificity:** For each pattern, false-positive rate on N_good ≥10,000 held-out good records ≤0.1% (CI upper bound ≤0.2%). Prediction: FPR survives its own CI gate.
4. **Threshold attainability:** For each rejection rule (e.g., confidence threshold, pattern-count cutoff), the observed max value in the sample exceeds the preregistered threshold by ≥2× measurement error. If not, gate is reported as non-reachable and the rule is reclassified.
5. **Eligibility:** Sanitizer rejection decision on a held-out test set differs from baseline by ≥5 records (minimum detectable effect). Baseline = (a) human review verdict, or (b) prior filter version, or (c) admitting all records. Prediction: sanitizer adds measurable signal beyond baseline.
6. **Component independence:** Rejection decisions on records triggering multiple patterns agree with per-pattern verdicts in ≥98% of cases (no hidden rule interactions). Prediction: pattern decisions compose as expected.

## Experiment
**Phase A: Baseline census and pattern inventory**
- Query target training corpus: count records matching each pattern in the curated bad-patterns list.
- Stratify by pattern; report: (pattern_id, match_count, proportion, confidence_interval).
- If any pattern has 0 matches in the target corpus, flag as VACUOUS and pre-commit a structural-zero reading before proceeding.
- Enumerate all positive fixtures (records already known bad by external authority—human review, prior filter, domain expert judgment) for each pattern. Record source and date of judgment.

**Phase B: Per-pattern calibration**
- For each pattern P with ≥10 known-positive fixtures:
  - Construct fixture set: F_pos (≥10 records with known bad status) and F_neg (≥1,000 held-out good records, stratified).
  - Run sanitizer detection rule on F_pos; compute sensitivity = TP/(TP+FN) with binomial CI (Wilson, 95%).
  - Run sanitizer detection rule on F_neg; compute specificity = TN/(TN+FP) with binomial CI (95%).
  - Gate: Sensitivity CI lower bound ≥90% AND Specificity CI lower bound ≥99.8% (rejecting ≤0.1% of good records).
  - Record: (pattern_id, TP, FN, sensitivity_est, sensitivity_CI, FP, TN, specificity_est, specificity_CI, pass/fail).
- Patterns failing calibration gates are flagged for re-tuning or retirement.

**Phase C: Threshold attainability**
- For each pattern, measure the attainable range of the rejection statistic on the full training corpus:
  - Compute: min_val, max_val, median, SD, 99th percentile of the test statistic.
  - For preregistered thresholds (e.g., confidence > 0.85, pattern count ≥2), verify:
    - Threshold sits strictly within [min_val, max_val].
    - Threshold − median ≥ 2× SD (threshold exceeds noise floor by Cohen's d ≥ 0.5 equivalent).
  - If threshold violates these, reclassify as non-reachable; report VACUOUS for that rule.

**Phase D: Eligibility and baseline contrast**
- Randomly split training corpus into development (80%) and held-out test (20%), stratified by known-bad status.
- Establish baseline decision on test set:
  - Option 1 (preferred): Human expert review of a 200-record random sample; compute proportions of rejections.
  - Option 2: Prior sanitizer version or known-good filter; record rejection rate and pattern of coverage.
  - Option 3 (fallback): Uniform admit-all baseline; sanitizer must reject ≥5 records to demonstrate signal.
- Apply final sanitizer (all calibrated patterns, attainable thresholds) to test set.
- Compute: sanitizer rejection rate, agreement with baseline on agreed-bad records (precision on manual rejects), disagreement rate (new rejects vs. baseline).
- Gate: Test-set disagreement ≥5 records OR sanitizer precision on manual rejects ≥95%.
- Ledger: Record every test-set decision triple (record_id, baseline_decision, sanitizer_decision, patterns_matched).

**Phase E: Component composition and interaction test**
- On the test set, isolate records matching 2+ patterns.
- Compute per-pattern verdict independently for each pattern's rejection criteria.
- Compare: single-pattern verdict vs. multi-pattern verdict; flag any record where per-pattern union differs from composite decision (rule interaction detected).
- Gate: ≤2% interaction rate (≤1 interaction per 50 records with multi-pattern matches).

## Controls
1. **Baseline control (Phase D):** Human or prior-method baseline captures domain knowledge absent from pattern list; sanitizer must exceed it or admit it adds no signal.
2. **Negative fixture control (Phase B):** 1,000+ held-out good records test false-positive rate under realistic conditions; prevents overfitting to pattern triggers.
3. **Stratified split (Phase D):** Development/test stratification by known-bad status prevents optimism bias; test set remains blind during calibration.
4. **Attainability control (Phase C):** Measuring max statistic on actual data before reading any rejection rate prevents threshold-above-ceiling defect; gate must be *reachable*.
5. **Per-component calibration (Phase B):** Each pattern validated independently before composition; catches interactions in Phase E rather than conflating them.
6. **Ledger attachment (Phase D):** Every rejection decision logged with record ID, patterns matched, and decision path; rows ship with verdict; enables post-hoc audit and seam-sufficiency check.

## Confound defenses
1. **Temporal drift in pattern frequency:** Baseline census (Phase A) captures pattern prevalence at validation time; annotate with collection date. If production corpus collected under different regime, revalidate on representative recent sample.
2. **Selection bias in fixture sets:** Positive fixtures sourced from external review (human, prior filter) rather than pattern-discovery process; negative fixtures ≥1,000 and stratified by domain to represent good-record diversity; fixtures recorded with source and date.
3. **Threshold cherry-picking:** Thresholds preregistered before Phase C attainability check; any threshold adjusted post-check is revalidated on a held-out replication corpus before admission.
4. **Hidden rule interactions:** Phase E composition test detects multi-pattern agreement failures; any interaction ≥2% flags a confound requiring investigation (e.g., one pattern's match biases another's features).
5. **Measurement error masquerading as signal:** Gate thresholds must exceed 2× SD; confidence intervals reported for all proportions (sensitivity, specificity, baseline agreement) to distinguish noise from effect.

## Preregistered falsifiers (numeric thresholds)
1. **Pattern existence (Phase A, VACUOUS gate):** If target corpus has 0 matches for a pattern, that pattern fails admission; test continues with remaining patterns.
2. **Sensitivity gate (Phase B):** Sensitivity CI lower bound <90% for any calibrated pattern → pattern fails; requires re-tuning or retirement.
3. **Specificity gate (Phase B):** False-positive rate (FPR) exceeds 0.1% (CI upper bound >0.2%) → pattern fails.
4. **Threshold attainability (Phase C):** Threshold sat above max(test_statistic) or below min(test_statistic) → rule reclassified as VACUOUS; OR threshold within 2× SD of median → rule reclassified as noise-floor, decision eligibility lost.
5. **Eligibility gate (Phase D):** Sanitizer rejection rate equals baseline rate (≤2 records difference) OR precision on manual rejects <95% → sanitizer adds no decision signal, admission refused.
6. **Composition gate (Phase E):** Multi-pattern interaction rate >2% → confound detected, sanitizer design requires revision before production.

## Stopping rule
- **Hard stop (do not admit sanitizer):** Any pattern fails phases B, C, or E; OR Phase D eligibility gate fails; OR Phase A reveals zero pattern matches AND no structural-zero protocol pre-committed.
- **Early stop allowed:** After Phase A census, if <5 patterns have ≥10 known-positive fixtures, development stops; baseline patterns alone may be sufficient (report separately).
- **Conditional stop (Phase D):** If agreement with baseline is high (>98%), sanitizer may pass with lower test-set disagreement (≥2 records instead of ≥5) but must be marked as "high-recall baseline redundancy" in production metadata.

## Expected failure modes
1. **No bad-pattern matches in target corpus:** Baseline census finds 0 occurrences for all patterns → VACUOUS reading; indicates known-bad list is domain-mismatched or corpus lacks those failure modes.
2. **Insufficient fixtures:** <10 positive examples for a pattern → pattern cannot be calibrated to CI standards; pattern retired from list or external fixtures sourced.
3. **High false-positive rate:** FPR >1% on good records → pattern rule is too sensitive, misses context; requires domain re-specification or retired.
4. **Threshold unreachable:** Preregistered threshold sat outside attainable range or at noise floor → indicates misspecification before data; threshold reclassified VACUOUS.
5. **Perfect agreement with baseline:** Sanitizer rejects exactly the records baseline rejects; if baseline is human review on full corpus, sanitizer adds no efficiency; if baseline is prior filter, sanitizer may be redundant (report separately).
6. **Multi-pattern rule interactions:** Composition changes verdicts >2% → patterns are not independent; interaction model required before production use.
7. **Temporal instability:** Revalidation on new corpus chunk shows pattern prevalence or performance ≥2 SD different → patterns drift over time; requires periodic re-calibration gates.

## Compute estimate
- **Phase A (census):** 1 full corpus scan (assume 1-10M records); pattern-matching on each record. Estimate: 10-30 GPU-hours or equivalent for regex/embedding-similarity matching.
- **Phase B (calibration):** 10-30 patterns × (10 fixtures + 1,000 negatives) = ~30K sensitivity/specificity evaluations. Estimate: 1-2 hours CPU.
- **Phase C (attainability):** 1 full corpus scan with statistic computation per pattern. Estimate: 5-15 GPU-hours (if statistics require embedding recomputation).
- **Phase D (test set baseline + contrast):** 200-record manual review (if human baseline chosen); sanitizer evaluation on 20% test set (~200K-1M records). Estimate: 40-80 person-hours (review) + 1-2 GPU-hours (sanitizer run).
- **Phase E (composition test):** Analysis of records with 2+ pattern matches (~10-100 records expected). Estimate: 0.1-0.5 GPU-hours.
- **Total:** ~40-130 person-hours (mainly Phase D review) + 20-50 GPU-hours.

## Prior evidence that materially changed this design (or 'none found')
**feedback_verify_signature_exists_before_controls (08-18):** Directly motivated Phase A baseline census as a structural precondition before any other testing; mandated structural-zero reading and VACUOUS classification to prevent mis-aimed instrument detection.

**feedback_gate_must_be_shown_reachable (08-23):** Directly motivated Phase C attainability check and the 2× SD threshold gate; ensures rejection decision is eligible to change on actual data.

**feedback_verdict_without_rows_is_an_assertion (08-23):** Motivated mandatory ledger attachment in Phase D; every rejection decision recorded with record ID, patterns, and path to ensure rows ship with verdict.

**feedback_gate_must_exceed_measurement_error (08-22):** Motivated confidence interval reporting for sensitivity, specificity, and agreement metrics; thresholds must not sit at noise floor.

## Unresolved uncertainty
1. **Fixture source validation:** Who is the external authority (human reviewer, prior filter, domain expert) that provides known-bad records? Credibility of baseline is not independently audited.
2. **Pattern interaction model:** If Phase E detects >2% interactions, what model of composition is correct? (AND, OR, weighted majority, learned combination?) Specification does not pre-commit.
3. **Temporal generalization:** Does sanitizer performance hold on corpus collected under different conditions (e.g., different data collection team, different tool versions)? Phase D test set is static; drift detection requires separate monitoring protocol.
4. **False negative cost asymmetry:** Specification weighs false positives (Type I, rejecting good records) but does not explicitly cost false negatives (Type II, missing bad records). Production decision may favor different sensitivity/specificity tradeoff.
5. **Bad-pattern list maintenance:** Who updates the known-bad patterns list? What is the update cadence? A static list risks obsoletion. Specification does not include update protocol.

