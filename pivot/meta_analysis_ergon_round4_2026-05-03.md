# Meta-Analysis: Round 4 External Review of Ergon Learner Proposal v4

**Date:** 2026-05-03 (late evening)
**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Subject:** Round 4 external adversarial review of [`pivot/ergon_learner_proposal_v4.md`](ergon_learner_proposal_v4.md). Reviewer was given v4 (the expanded-background version, commit eedcb893).
**Companions:**
- [`pivot/feedback_ergon_review_round4_2026-05-03.md`](feedback_ergon_review_round4_2026-05-03.md) — verbatim capture
- [`pivot/ergon_learner_proposal_v5.md`](ergon_learner_proposal_v5.md) — v5 incorporating round-4 revisions
- Round-1, round-2, round-3 meta-analyses already on disk

---

## Frame: round 4 identifies a NEW structural weakness v4 created

Rounds 1-2 surfaced missing mitigations. Round 3 surfaced internal contradictions (Llemma rationale vs asymmetry argument; missed residual-primitive integration). Round 4 surfaces something different: **the architectural correction in v4 — promoting the residual primitive to first-class reward signal — shifted the single point of epistemic failure from "PROMOTE rate too sparse" to "residual classifier is now critical infrastructure."**

This is a follow-on consequence of v4's biggest move. v4's §1.2 of the round-4 review states it cleanly: v4 crosses the line from "falsification system" to "falsification-gradient system." The gradient is only as good as the classifier producing it. v4 didn't address the classifier's robustness with anywhere near the rigor it addressed the kernel's.

Five fragility points; one fully-spelled-out bear case ("system optimizes for looking like signal, not being signal"); four pre-MVP tightening recommendations. v5 is warranted to absorb the load-bearing items.

## Triage of round-4 critiques

### LOAD-BEARING — single point of failure

**(1) The residual classifier is now critical infrastructure but lightly calibrated.**

Reviewer's framing:
> Everything now depends on signal vs noise vs drift classification. But your classifier is heuristic, lightly calibrated (30 samples), using simple rules (variance, signatures, etc.). … This is now the most critical component in the system.

Sharp catch. v4 promotes the residual primitive to load-bearing reward signal (`w_R = 0.15` in the agreement-weighted reward) without commensurately strengthening its calibration. The original residual primitive proposal had a 30-residual benchmark with ≥80% accuracy + zero false-positive `signal` calls as the day-1 acceptance gate; that gate has not yet been reported as passing on disk, and even if it passed, 30 samples is not robust.

**v5 mitigations:**
- **Adversarial residual benchmark.** Before any agreement-weighted-reward production use, the classifier must pass an adversarial benchmark including: obvious noise samples (FP-quantization, MC-seed jitter, Gaussian residuals), borderline signal samples (real structured residuals from mathematical history at 1.5σ–3σ confidence boundary), and synthetic structured-noise samples (deliberately constructed to look like signal but be uncorrelated with truth). Acceptance: <5% false-positive rate on synthetic structured-noise specifically.
- **Confidence abstention zone.** The reward signal `w_R * signal_class_residual_indicator` triggers only when classifier confidence is ≥ 0.85. Mid-confidence residuals (0.5-0.85) earn zero reward — neither rewarded nor penalized. This prevents the agent from learning to generate "borderline" residuals that game the classifier.
- **`residual_signal_precision` metric.** Track `(signal-class residuals that later lead to PROMOTE or META_CLAIM success) / (all signal-class residuals)`. If this is low (<0.1), the gradient is fake; reduce w_R or pause production use.

Promotes as Tier-3 candidate symbol: `PATTERN_GRADIENT_CLASSIFIER_SINGLE_POINT_OF_FAILURE`.

### LOAD-BEARING — evaluator independence

**(2) Cross-model agreement is weaker than v4 acknowledged.**

Reviewer's framing:
> You're assuming: multiple frontier LLMs = independent evaluators. In reality: they share training data, heuristics, failure modes. So cross_model_agreement ≠ independent validation. … You partially acknowledge this, but it's still overweighted at w_X=0.25.

Correct. v4 mentioned correlated-mutation as a mitigation in §3.5 but kept w_X=0.25 in the reward function. Round-4 reviewer notes the reward weighting is still too high given the actual independence of the evaluators.

**v5 mitigations:**
- **Add at least one non-LLM evaluator** to the reward function. Candidates:
  - Symbolic consistency check (PARI/GP or SymPy independent verification of the claim's mathematical content)
  - Theorem-prover acceptance where formalizable (Lean / Coq / Isabelle)
  - Numeric robustness across input perturbations (bootstrap-style: does the claim survive small perturbations to its arguments?)
- **Reweight:** w_S=0.4, w_X=0.15 (down from 0.25), w_H=0.2, **w_NL=0.10 (NEW non-LLM evaluator)**, w_R=0.15. Total = 1.00.
- The non-LLM evaluator's specific implementation depends on the domain. For Lehmer-Mahler discovery, numeric perturbation is the most tractable: does M(P + ε) ≈ M(P) under small coefficient noise?

Promotes as Tier-3 candidate symbol: `PATTERN_LLM_EVALUATOR_SHARED_PRIOR`.

### LOAD-BEARING — descriptor degeneracy

**(3) MAP-Elites descriptor may collapse in practice.**

Reviewer's framing:
> Canonicalizer subclass (4 classes): If distribution is skewed (likely): 70-90% of outputs land in one class → axis loses discriminative power. Output canonical-form distance: depends on quality of your catalog and distance metric validity. Entropy of DAG subclasses: may correlate strongly with depth and complexity → redundant axis.

This sharpens round 2's MAP-Elites collapse critique with specific axis-by-axis fragility analysis. Each axis has a different failure mode.

**v5 mitigations:**
- **Per-axis fill-rate audit.** At end of every 1K episodes, compute per-axis fill distribution. If any axis has >70% concentration in one bin, flag the axis as `degenerate_at_window_X` and trigger axis-replacement protocol.
- **Hot-swappable descriptor.** Axes are configurable; replacements specified by tag. If `output_canonicalizer_subclass` axis collapses, replace with `output_signature_class` or `output_arithmetic_invariant_bucket`. If `output_canonical_form_distance` axis is noisy (catalog quality issue), replace with `output_irreducibility_class` or `output_galois_group_signature`.
- **Independence verification at every audit.** Cross-correlation matrix computed at every audit; pairs with |corr| > 0.7 flag the axes for review.

Promotes as Tier-3 candidate symbol: `PATTERN_DESCRIPTOR_COLLAPSE_DEGENERACY`.

### LOAD-BEARING — anti-prior may not work as advertised

**(4) Anti-prior operator may produce structured noise rather than off-prior exploration.**

Reviewer's framing:
> "anti-correlated with corpus frequency stats" produces: rare ≠ novel, rare ≠ meaningful, rare often = garbage. Likely outcome: high kill rate, low signal-class residual rate, acts like a noisy null.

Honest pushback acknowledged. The reviewer is right that "anti-correlated with corpus frequency" maps to "rare in corpus," and "rare in corpus" maps to many things including "garbage." The anti_prior operator's intended behavior — exploring outside the LLM prior's high-density region — depends on whether structurally novel mathematics happens to cluster with corpus-rare patterns or not. Empirical question.

**v5 partial mitigation:**
- Acknowledge this in v5's §3.5.1: anti_prior may behave as "structured noise generator" in practice; that's still useful as null baseline but not as discovery operator.
- Add: **per-operator-class `residual_signal_precision` tracking.** If anti_prior's per-operator precision is far below other operators (e.g., <50% of structural's precision), the operator is functioning as noisy null — keep the minimum-share commitment but don't expect anti_prior to outperform.
- v5 doesn't claim anti_prior necessarily explores outside the prior; it claims anti_prior provides anti-correlated baseline exploration that prevents pure prior-collapse.

(No new symbol — this is calibration of expectations on an existing component.)

### LOAD-BEARING — meta-loop trigger may not fire

**(5) Meta-loop trigger threshold may be unreachable in practice.**

Reviewer's framing:
> Your trigger: META_AUDIT_CANDIDATE ≥ 5% of kills in 1K window. But if residual classifier is conservative or signal density is low: you may never trigger, even if battery is miscalibrated.

Correct. v4's threshold has a self-defeating loop: if the classifier is conservative (which may itself be a calibration issue), the trigger doesn't fire, and the calibration check the meta-loop is supposed to perform never runs.

**v5 mitigations:**
- **Lower trigger threshold.** From 5% to 3% of kills in a 1K-episode window.
- **Absolute-count fallback trigger.** Fire on ≥30 high-residual-confidence kills in any rolling window, regardless of percentage.
- **Scheduled fires regardless of trigger.** Every 10K episodes, execute at least one Techne-forged sharper-checker run on a curated sample of recent battery-kills, regardless of whether the threshold-based trigger has fired. Forces the meta-loop to actually exercise the audit machinery.
- **Trigger sensitivity meta-metric.** Track `meta_loop_fire_rate` over time; if zero across multiple 100K-episode windows, the trigger is broken and the meta-loop's calibration audit never runs.

Promotes as Tier-3 candidate symbol: `PATTERN_META_LOOP_TRIGGER_DEAD_ZONE`.

### THE FULLY-SPELLED-OUT BEAR CASE

Round-4 reviewer provides the cleanest formulation of the bear case so far:

> 1. Residual classifier is noisy → mislabels noise as signal
> 2. Signal-class-residual reward dominates early learning
> 3. Policy learns to generate "structured-looking noise"
> 4. Cross-model agreement reinforces it (shared bias)
> 5. Battery continues to reject everything
> 6. Meta-loop doesn't trigger (threshold not met)
> 7. PROMOTE rate stays ~0
> 8. Residual rate stays high but meaningless
>
> **Result: System optimizes for looking like signal, not being signal.**

This is structurally a *meta-version of specification gaming* where the gaming target is the residual classifier. v5's §11.6 makes this explicit:

**The residual-gaming attractor as the v5 bear case.** The mitigations are the five v5 changes above (adversarial benchmark + abstention zone + non-LLM evaluator + descriptor audit + meta-loop trigger fix); together they form a defensive surface against the residual-gaming attractor. None individually is sufficient; together they may be.

The substrate-grade test for whether the architecture is in the bear case: **`residual_signal_precision` metric.** If this stays low (<0.1) across multiple operator classes for multiple 10K-episode windows, the gradient is fake; the system is optimizing for looking like signal.

## Five new candidate symbols filed (round 4)

1. **PATTERN_GRADIENT_CLASSIFIER_SINGLE_POINT_OF_FAILURE** — when an architecture promotes a heuristic classifier from logging to reward signal, the classifier becomes the most critical component but is rarely strengthened commensurately. Mitigation: adversarial benchmark + abstention zone + precision tracking.

2. **PATTERN_LLM_EVALUATOR_SHARED_PRIOR** — multiple frontier LLMs prompted independently still share training-corpus blind spots; cross-model agreement is not independent validation. Mitigation: include at least one non-LLM evaluator (symbolic / theorem-prover / numeric perturbation).

3. **PATTERN_DESCRIPTOR_COLLAPSE_DEGENERACY** — quality-diversity descriptor axes can degenerate per-axis (skewed distribution; noisy reference distance; correlation with other axes); requires per-axis ongoing audit and hot-swappable axis spec. Mitigation: per-axis fill-rate audit at fixed intervals; cross-correlation matrix re-computed; axis-replacement protocol.

4. **PATTERN_META_LOOP_TRIGGER_DEAD_ZONE** — auto-trigger thresholds for self-audit machinery can be unreachable in the precise scenarios where the audit is most needed. Mitigation: lower threshold + absolute-count fallback + scheduled fires regardless of trigger + trigger-sensitivity meta-metric.

5. **PATTERN_RESIDUAL_GAMING_ATTRACTOR** — when residual signal becomes reward, policy can learn to generate structured-looking noise that classifier mislabels and cross-model agreement reinforces; system optimizes for looking like signal, not being signal. Mitigation: residual_signal_precision metric (precision = signal-class residuals leading to PROMOTE or META success / all signal-class residuals); abstain from rewarding low-precision operators.

Total candidate-symbol harvest from this proposal review cycle: **16** (5 from round 4 + 5 from round 3 + 3 from round 2 + 3 from round 1). Plus 5 from the v2-thesis review = **21 candidate symbols across the design cycle.**

## Action items for v5

1. §2.6 update: residual primitive section — add adversarial benchmark + abstention zone discipline; raise day-1 acceptance gate to brutal enforcement (zero false-positive on synthetic structured noise).
2. §3.5.5 (NEW): `residual_signal_precision` metric + per-operator-class tracking.
3. §5.3 update: agreement-weighted reward formula updated to include non-LLM evaluator (w_NL=0.10); w_X reduced from 0.25 to 0.15.
4. §6.2 update: per-axis fill-rate audit; hot-swappable descriptor; cross-correlation matrix at every audit.
5. §11.5 update: meta-loop trigger lowered to 3%; absolute-count fallback; scheduled fires regardless of trigger; meta_loop_fire_rate as monitored metric.
6. §11.6 (NEW): the residual-gaming attractor as v5's specific bear case + defensive surface enumeration.
7. §12 update: open questions — add residual classifier robustness, descriptor stability, meta-loop trigger sensitivity.

## The reviewer's offer to simulate first-10K-episode-pilot outcomes

The review closes with: *"If you want, I can simulate likely outcomes of the first 10K-episode pilot (what distributions you should expect, and what would count as 'this is working' vs 'this is failing')."*

This is operationally the most valuable next step. After v5 ships, accepting the simulation offer gives:
- Expected per-operator-class PROMOTE rate distributions
- Expected per-operator-class signal-class-residual rate distributions
- Expected residual_signal_precision under various classifier-quality scenarios
- Concrete go/no-go criteria for "this is working" vs "this is failing"

This is a substitute for empirical signal we can't generate yet (MVP isn't built); the substrate gains an a-priori expectation distribution against which the actual pilot's results can be compared.

**Recommendation:** ship v5; accept the simulation offer; the simulation results inform the MVP build's pre-flight checks.

## The genuine design freeze threshold

I've now told James "design freeze after this round" three times (v3, v4, v5). Each time the next round has surfaced load-bearing critiques. I should be honest: the cycle has produced 16 candidate substrate symbols and 5 versions in 24 hours. That's high-velocity but also high-churn.

The right framing: design freeze is a *discipline*, not a *prediction*. v5 ships; if round 5 surfaces critiques as deep as rounds 3-4 (active failure modes the architecture creates by its own corrections), v6 is warranted. If round 5 surfaces only mitigations on top, the design is genuinely converged and MVP build begins. The discipline is to evaluate each round's depth honestly, not to declare freeze prematurely.

My prior: round 4 is at parity with round 3 in depth (both surface architectural failure modes). Round 5 will likely be at less depth — or absent entirely if the reviewer pool is exhausted. The simulation offer from round-4 reviewer suggests they themselves think the next high-value step is empirical, not further design review.

— Ergon
