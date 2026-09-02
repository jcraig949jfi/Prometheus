# PROPOSAL V2-T05 (arm)

## Hypothesis

A pre-registered, statistically observable failure signature — measured minimum detectable effect (MDE) exceeding the theoretical maximum effect a treatment could modulate (Δ_max) — reliably predicts experimental doom across problem families when applied prospectively as an early-abort criterion, with false-positive rate ≤ 0.10 (Type I error) and true-positive detection of doomed attempts ≥ 0.80 (power).

## Motivating evidence

- **Ergon Gen-1A discovery (2026-08-31, section 7)**: In a memory retention policy experiment with n=5 lineages, power analysis computed MDE = 10.1 percentage points at 80% power. Prior work established that the maximum content-adaptedness effect any policy could modulate is 6.7 pp. MDE > Δ_max *before execution* signaled that no result could discriminate policies from measurement noise. The experiment was redesigned to n=30 (MDE = 1.9 pp, now viable) and zero lineages were wasted.

- **Theoretical basis**: Retention policy effects are bounded by the gap between the best achievable performance on incumbent policy versus the shuffled-memory baseline, constrained by existing architecture. If the study's power analysis predicts a minimum detectable effect larger than this structural bound, statistical power cannot support discrimination, making the experiment doom-sealed.

- **Operational cost averted**: Detecting the signature prospectively (Phase 0) prevented running a full experimental campaign that would have published a null indistinguishable from "no effect" when the real defect was design power, not treatment quality.

- **Transferability question**: Does this signature generalize beyond within-lineage paired designs? Can it flag doomed attempts in cross-domain experiments (Aporia transfer studies, Ludus game-world adaptations, cross-substrate circuit discovery)?

## Prospective predictions

1. **Primary (predictive validity)**: Across a frozen roster of 8–12 pre-planned experiments in neighboring problem families (Aporia/substrate-D5, Ludus/transfer, Charon/validation), prospective application of the MDE-exceeds-Δ_max signature identifies ≥ 80% of experiments that (a) run to completion and (b) produce statistically non-significant results with confidence intervals consistent with "measurement error prevents detection," while keeping false-positive rate on viable experiments ≤ 10%.

2. **Mechanism signature**: Experiments identified as doomed will show: (i) actual observed MDE matches preregistered prediction within ±15%; (ii) treatment effect confidence intervals centered near zero, entirely within ±1 SE of the preregistered Δ_max; (iii) no post-hoc reframing (e.g., "detected smaller effect; success at reduced scale") that retroactively changes doom into discovery.

3. **Negative case (falsifier)**: If an experiment flagged by the signature produces a large, unexpected treatment effect (|effect| > 2 SE above Δ_max), the signature has failed as a predictive tool on that problem family. Post-hoc analysis must isolate which assumption was violated: theoretical bound error, design specification drift, or misspecified variance.

4. **Cross-family stability**: The signature's sensitivity and specificity must not differ by more than 2-fold across identified problem families (e.g., if it catches 80% of doom in one family but only 35% in another, the signature is not generalizable without domain-specific recalibration).

## Experiment

**Phase 0 (prospective audit and signature application, pre-freeze):**

1. **Candidate identification**: Enumerate 8–12 candidate experiments in problem families with documented architectural connection to Ergon Gen-1A (defined as one relational hop: Aporia D-5 transfer work, Ludus inter-world transfer, Charon validation suites). Each candidate requires (a) preregistered effect model; (b) explicit theoretical bounds on treatment effect; (c) committed statistical analysis plan (primary test, α level).

2. **Prospective power analysis**: For each candidate, before any outcome inspection:
   - Derive Δ_max from prior published contrasts, preregistered architectural bounds, or explicit theoretical arguments. Document the source.
   - Compute MDE at 80% power given preregistered sample size, design, and primary test.
   - Preregister comparison: classify as VIABLE (MDE < 0.5 × Δ_max) or FLAGGED (MDE ≥ 0.5 × Δ_max).
   - Freeze classification before running any experiment.

3. **Experiment roster classification**:
   - **VIABLE**: MDE < 0.5 × Δ_max. Proceed normally.
   - **FLAGGED**: MDE ≥ 0.5 × Δ_max. Marked as doomed but runs to completion (arm remains blind; no early stopping).
   - **REDESIGNED**: Initially flagged but investigators increase sample size or reduce noise before freeze. Document redesign rationale and treat as separate arm.

4. **Freeze decision packet**: Before Phase 1, record for each experiment: (a) Δ_max derivation with citations; (b) MDE computation sheet; (c) design specifications; (d) preregistered stopping rule and primary test specification.

**Phase 1 (execution with outcome blinding):**

1. Run each experiment according to preregistered protocol. Experimenters blind to doom classification.

2. For each completed experiment, record: (a) primary test statistic and p-value; (b) effect size (point estimate + 90% CI); (c) whether CI overlaps preregistered Δ_max; (d) comparison to MDE prediction.

3. Measure signature performance:
   - For each FLAGGED experiment: did the observed effect fall within ±1 SE of zero (consistent with "measurement prevented detection") or exceed it (signature failed)?
   - For each VIABLE experiment: did it produce significant result (success) or coherent non-significant result (correct viability judgment)?

**Phase 2 (validation and falsification):**

1. **Contingency table**: Create 2×2 cross-tabulation (Signature: {Viable, Flagged} × Outcome: {Significant p < α, Non-significant CI includes zero}). Compute sensitivity (% truly non-significant experiments correctly flagged), specificity (% significant experiments not flagged).

2. **Falsifier audit**: For any FLAGGED experiment with |effect| > 2 SE above Δ_max, conduct post-hoc analysis to identify assumption violation: Was Δ_max underestimated? Did design hide heterogeneity? Was statistical test misspecified?

3. **Cross-family consistency stratification**: Repeat contingency table analysis stratified by problem family. Test whether sensitivity/specificity ratios differ by > 2-fold across families.

## Controls

- **Null classifier baseline**: Randomly classify experiments as doomed/viable at the same rate as true signature. True signature must exceed this by ≥ 15 percentage points (sensitivity + specificity, unweighted).

- **Trivial threshold control**: Any experiment with MDE < 0.2 × Δ_max is automatically viable (requires no insight). Measure signature value only in the range [0.3 × Δ_max, 1.0 × Δ_max] where signal and noise genuinely overlap.

- **Within-family replication**: Include at least two independent experiments per problem family (e.g., two retention-policy studies with different search cores) to test consistency of signature predictions within a single domain.

- **Reframing audit**: After Phase 2, examine each FLAGGED experiment's final interpretation. If investigators changed claimed effect size, primary endpoint, or success criterion post-outcome, flag as REFRAMING_ATTEMPTED and report frequency.

## Confound defenses

- **Preregistration window leakage**: An independent analyst (not experiment PI) conducts Phase 0 power analysis without outcome data access. Δ_max derivations audited by external reviewer. Timestamp and analyst signature embedded in frozen decision packet.

- **Retroactive theory revision**: Δ_max is preregistered WITH EXPLICIT ANCHORS (specific prior contrasts, published effect sizes, architectural diagrams). Post-hoc derivation revisions are recorded separately as correction events, not retroactive re-justification.

- **Measurement variance underestimation**: If actual observed noise exceeds preregistered assumption, MDE is underestimated and experiments appear more viable than they are. Defense: variance assumptions taken from COMMITTED STATISTICAL PLANS, never data-estimated. Actual observed/preregistered variance ratios are reported as model-specification findings.

- **Δ_max derivation craft variability**: Different investigators may use conflicting priors to derive bounds. Defense: Δ_max derivations scored by independent adjudicator on explicit criteria (grounded in published results? avoids unfalsifiable ranges?). Inter-rater reliability on Δ_max coding measured; disagreements hand-adjudicated with documented reasoning.

- **Missed alternative doom modes**: Some experiments may fail for reasons outside the MDE-mediated class (model misspecification, oracle leakage, selection bias). Defense: At end of Phase 2, any VIABLE experiment failing dramatically is audited for alternative failure modes. Signature explicitly claims to catch only power-analysis doom, not all doom.

## Preregistered falsifiers (numeric thresholds)

- **F1 (signature discriminance)**: Sensitivity ≥ 0.65 (% of truly non-significant experiments flagged) AND specificity ≥ 0.85 (% of significant experiments marked viable). If either missed: SIGNATURE_LACKS_DISCRIMINANCE. Study fails.

- **F2 (viable category reliability)**: Among VIABLE experiments completing, non-significant rate must not exceed 0.30. If exceeded: VIABLE_CATEGORY_UNRELIABLE (too many marginal designs admitted).

- **F3 (cross-family generalization)**: Sensitivity and specificity must not differ by > 2-fold across identified problem families. If a family shows 0.80 sensitivity and another shows 0.35: FAMILY_SPECIFIC_SIGNATURE_ONLY. Signature not generalizable.

- **F4 (reframing resistance)**: Post-outcome revisions of Δ_max or primary endpoint must occur in < 5% of all experiments. If exceeded: PREREGISTRATION_NOT_BINDING. Investigator flexibility undermines signature validity.

- **F5 (theory grounding)**: ≥ 95% of Δ_max derivations must cite specific quantitative evidence (published effect sizes, preregistered contrasts, architectural diagrams with labeled bounds). Armchair theory alone scores zero. If < 95% grounded: BOUND_DERIVATION_WEAK.

## Stopping rule

**Fixed-N design**: All Phase 0 experiments run to completion. No early termination of any experiment based on interim significance. Phase 0 decision packet frozen before Phase 1 begins; no post-hoc experiments added to improve signature calibration. 

If catastrophic issues discovered (outcome data leakage into Δ_max derivation, systematic bias in power analysis tool), report as PHASE_0_VALIDITY_COMPROMISED and demote results to exploratory.

## Expected failure modes

- **Signature detects noise, not doom**: In some families, MDE-exceeds-bound may conflate measurement error with true effect smallness, misclassifying hard-to-detect-but-real effects as doomed. Requires investigation of whether measurement model fits the domain.

- **Δ_max unfalsifiability**: Theoretical bounds may range widely (e.g., "library policy could improve CFR by 2% to 20%"), making Δ_max a moving target. Defense: adjudicator must reject excessively wide bounds at Phase 0 (F5 gate enforces quantitative grounding).

- **Informal post-freeze redesign**: Investigators might redesign flagged experiments after classification (increase n, reduce noise, switch endpoints) without formally reopening preregistration. Signature blamed unfairly. Defense: final executed design logged (actual n, actual noise, actual primary test); divergence from preregistration flagged and reported.

- **Family selection bias**: If chosen families share uncontrolled properties (all within-subject designs, all depend on library quality), generalization is limited. Disclosed in family description; results stratified by design class.

- **Circular Δ_max derivation**: Theoretical bounds derived from prior evidence subject to measurement error. If a prior experiment overestimated effect, Δ_max is too high and signature fails silently. Unavoidable; signature captures only power-analysis doom, not all categories of doom.

## Compute estimate

- **Phase 0** (audit + power analyses): 8–12 candidates, ~2 hours per experiment (design review, prior literature, power computation, Δ_max justification). Total: 20–24 hours, single analyst.
- **Phase 1** (execution): measured in existing experiment completion times; no additional cost.
- **Phase 2** (adjudication + validation): ~5 hours (tabulation, falsifier audit, cross-family stratification, reporting).
- **Total analyst time: ~30 hours**. No additional compute infrastructure required.

## Prior evidence that materially changed this design (or 'none found')

- **Ergon Gen-1A (2026-08-31, section 7)**: The MDE-exceeds-bound observation shifted the hypothesis from "which retention policy is best?" to "can power analysis predict doom prospectively?" Reframed the design from policy comparison to meta-experimental validation.

- **Ergon Gen-1A (2026-08-31, power table)**: Discovery that discreteness dominates heterogeneity (MDE falls sharply n=5→n=8) changed falsifier thresholds from "±20% tolerance on MDE" to "±15%, measured at medium n-range where effect matters most."

- **Gen-1A operational framing**: The cost model (38,000 evals/sec, 30 lineages costs one hour) established that sample-size adjustments are operationally cheap. This shifted expected failure modes from "experiments run underpowered" to "do investigators catch the signature early enough to redesign?" Focused design on prospective application (Phase 0) rather than post-hoc diagnosis.

## Unresolved uncertainty

- **Δ_max derivation craft**: No formal procedure exists for deriving theoretical bounds from literature. Requires domain expertise and adjudication. The V2 experiment tests whether a rubric (F5: quantitative grounding) suffices, but hand-crafted bounds may hide as much as they reveal.

- **Generalization to non-paired designs**: Gen-1A is within-lineage paired (Δ at task level, aggregated). Does signature work equally well for between-groups designs, unequal-n, or hierarchical models with random slopes? Candidate experiments may include these, offering empirical evidence.

- **Interaction with model selection**: Experiments implicitly searching over multiple models/designs and reporting the best inflate degrees of freedom, invalidating both primary test and power analysis. Whether signature remains valid under selective reporting is untested.

- **Temporal drift in problem families**: Ergon's memory-retention family under active development; assumptions may shift. Does Δ_max remain stable as the problem evolves? Long-running experiments may show temporal confounds.

