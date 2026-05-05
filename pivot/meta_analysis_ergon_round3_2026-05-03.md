# Meta-Analysis: Round 3 External Review of Ergon Learner Proposal v3

**Date:** 2026-05-03 (evening)
**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Subject:** Round 3 external adversarial review of [`pivot/ergon_learner_proposal_v3.md`](ergon_learner_proposal_v3.md). The reviewer was given v3 (the design-freeze version, commit 82790816). This is the deepest round.
**Companions:**
- [`pivot/feedback_ergon_review_round3_2026-05-03.md`](feedback_ergon_review_round3_2026-05-03.md) — verbatim capture
- [`pivot/ergon_learner_proposal_v4.md`](ergon_learner_proposal_v4.md) — v4 incorporating the round-3 revisions
- Round-1 + round-2 meta-analyses already on disk

---

## Frame: this round is qualitatively different

Rounds 1 and 2 each surfaced three load-bearing critiques where the gap was *missing mitigation* — the architecture had a defensive surface that hadn't been named. The fix in v2 and v3 was to add new components (multi-evaluator reward, anti-prior operator, output-space MAP-Elites axes, etc.).

Round 3 is different. Six load-bearing critiques, but two of them are *internal contradictions or missed integrations* — the architecture had a flaw that was *actively hidden* by language in the doc. The fix in v4 isn't to add new components on top; it's to *correct what's already there*.

This is qualitatively sharper feedback than rounds 1–2, and it directly invalidates v3's design-freeze recommendation. v3 said: "fundamentals haven't changed since v1; mitigations have accumulated; ship MVP." Round 3 says: actually some of the fundamentals are wrong — §5.1 contradicts §3, the diagnostic ignores a primitive that just shipped, the bear case is shallower than the architecture admits.

The right response is not to apologize for v3 and freeze again. The right response is to ship v4 that actually fixes the structural seams, *then* freeze. v4 is corrective; v3 was additive.

## Triage of round-3 critiques

### LOAD-BEARING — internal contradictions (correction, not addition)

**(1) §5.1 Llemma rationale contradicts §3 asymmetry argument.**

Reviewer's framing:
> §5.1 explicitly markets Llemma-7B as "closest to Silver's training distribution" and "closest action-space inheritance to Silver's likely target distribution." This is presented as a strength — the policy inherits relevant priors — but it directly contradicts §3's claim that Ergon covers a different manifold.

Sharp catch. v3's §3 claims action-space asymmetry yields a different discovery surface, while §5.1 markets the base model on the *opposite* grounds — that it inherits Silver's likely prior. Two contradictory positions in the same document. Round 2 had named this gap (PATTERN_SHARED_PRIOR_AT_TRAINING_LAYER) and v3 added the `anti_prior` operator class to mitigate, but didn't go back and *correct §5.1's marketing language* — so the contradiction was hidden, not resolved.

**Correct framing for v4:** the prior is shared at the corpus level. Differentiation comes from action-space (typed compositions vs Lean tactics) + value head (battery survival vs Lean closure) + LoRA delta (substrate-shaped fine-tuning attractor), NOT from the base model's training distribution. Llemma is a defensible but non-load-bearing choice; the LoRA delta does the differentiation work. Worth running an ablation in v0.5 with a non-math-pretrained base (Qwen-7B or Llama-7B) to see whether the LoRA delta is more divergent from a different starting point.

**Fix in v4:** rewrite §5.1 honestly. Remove "closest to Silver's distribution" framing. Reframe as "Llemma is a starting point with a strong math-reasoning prior; the differentiation work is done by action-space + value head + LoRA delta." Add Qwen-7B and Llama-7B as v0.5 ablation candidates.

**(2) The four-counts diagnostic doesn't use the residual primitive that just shipped.**

Reviewer's framing:
> The four counts as currently specified are catalog-hit, claim-into-kernel, PROMOTE, battery-kill. There's no count for *kills with structured residual* — which is exactly what the residual primitive was designed to capture. A diagnostic that ignores the residual primitive in a system that just shipped it is a missed integration with the architecture's own most recent addition.

This is the killer line. The residual primitive landed at commit `4872bb4a` on 2026-05-03; the v3 four-counts diagnostic was written on the same day and doesn't reference it. The architecture's own most recent component is missing from its own diagnostic.

The reviewer's specific fix is correct and high-leverage: add a fifth count for `kill_with_structured_residual_passing_classifier_threshold`. Residual events should be more common than promotions by construction (residuals fire on every signal-class kill, which is a strict subset of all events). This gives the diagnostic statistical power even when PROMOTE rates are too low to resolve operator-class differentiation.

**Fix in v4:** five-counts diagnostic, not four-counts. The fifth count is `signal_class_residual_kill`. All inter-arm comparisons should report both PROMOTE rate AND signal-class-residual rate.

### LOAD-BEARING — operational gaps (sharper specification)

**(3) The 0-PROMOTE baseline at 1000×3 is a power-calculation issue, not a "scale to 10K" issue.**

Reviewer's framing:
> If the underlying rate is rare (say, 10⁻⁴ or below), then 10K episodes per arm produces ≤1 PROMOTE per arm, and operator-class differentiation is undetectable at any plausible budget. … Without an estimate of where that floor sits, the four-counts pilot may be informationally null at every budget the proposal contemplates.

Correct. v3's progression assumed PROMOTE rates would become detectable at 10K. The reviewer correctly notes that's an unverified assumption. If PROMOTE rates are 10⁻⁴ or below in the Lehmer-Mahler domain, the diagnostic is informationally null at any budget the proposal contemplates.

**Fix in v4:** add a power-calculation section. Explicitly: at PROMOTE rate p, episodes-per-arm needed for Welch-significance at α=0.01, lift d, β=0.2 is approximately `n ≈ 4 * (1.96 + 0.84)² * p * (1-p) / d²`. For p=10⁻³ and d=0.5 (a 50% lift), n ≈ 31K episodes per arm. For p=10⁻⁴, n ≈ 314K per arm. Compute envelope at 10K episodes per arm only resolves operator-class differences when PROMOTE rates are ≥10⁻². The signal-class-residual count should partially solve this because residual events are denser than promotions.

**(4) The `uniform` operator class will be squeezed out under selection pressure unless minimum proposal share is enforced.**

Reviewer's framing:
> The proposal mentions `uniform` as a strawman null but doesn't commit to a minimum proposal share, which means under selection pressure for cell-fill rate, `uniform` gets squeezed out exactly when it's most needed.

Correct. v3's spawning policy is `with probability p_explore = 0.3, sample under-explored cell; with probability (1-p_explore), sample fitness-weighted cell.` Operator-class selection within a cell isn't constrained — under cell-fill-rate pressure, the operator that has historically filled that cell will be re-sampled. `uniform` is by construction worst at filling specific cells (it's prior-free), so it gets squeezed out.

**Fix in v4:** explicit minimum proposal share. `uniform` ≥ 5% of all proposals; `anti_prior` ≥ 5%; `structured_null` ≥ 5%. Total non-prior-shaped operators ≥ 15% of all proposals at all times. This is a coordination constraint at the operator-class scheduler level, not at the cell-selection level.

### LOAD-BEARING — content-aware behavior descriptor

**(5) Behavior descriptor measures structure-of-proposal, not mathematical-content.**

Reviewer's framing:
> All five axes — DAG depth, width, equivalence-class entropy, cost tier, output-type signature — are properties of how the genome is *constructed*, not of what it's *doing mathematically*. … MAP-Elites maximizing diversity along these axes produces diversity-of-construction, which may or may not correlate with diversity-of-discovery.

Sharp. The reviewer is correct that v3's revised axes (DAG depth, equiv-class entropy, output-type signature, output magnitude bucket, output canonical-form distance) are partly content-aware but mostly construction-aware. Output-type signature is coarse content; output magnitude bucket is content-derived but very coarse; output canonical-form distance is content-aware but in a structural-distance sense.

**Fix in v4:** swap one structural axis (DAG depth) for a content axis: **output canonicalizer subclass tag** (group_quotient / partition_refinement / ideal_reduction / variety_fingerprint) when applied to the genome's evaluation result. This is the canonicalizer's discrete content classification of *what the output is mathematically*, not how the genome was built.

Revised v4 5-axis descriptor:
1. ~~DAG depth~~ → **Output canonicalizer subclass** (4 categories)
2. Equivalence-class entropy of the DAG (5 quantiles)
3. Output-type signature (~10 categories)
4. Output magnitude bucket (5 quantiles)
5. Output canonical-form distance (5 quantiles)

Total cells: 4 × 5 × 10 × 5 × 5 = 5,000. Slightly fewer than v3's 6,250 but with better content/construction balance.

### LOAD-BEARING — operationalization of the Silver-ingestion story

**(6) Silver-ingestion in §13 is rhetorical, not operational.**

Reviewer's framing:
> Silver's likely output is Lean-closed proofs. A Lean-closed proof has *already* been mechanically verified — there's no useful substrate-side falsification of "this theorem's Lean proof type-checks," because the Lean kernel did that. … The doc should specify what fragment of Silver's output is substrate-ingestible and what verdict the substrate can render that the Lean kernel can't.

Correct. v3's §13 is hand-waving. A Lean proof type-checking is not substrate news. Useful substrate ingestion of Silver's output requires:

- **Empirical-pattern conjectures used in the proof** — Lean proofs sometimes invoke conjectures (BSD-conditional, GRH-conditional, Selmer-rank-conditional) that the Lean kernel treats as axioms but the substrate could falsify empirically.
- **Generalizations the proof makes from specific cases** — Lean proves "for all x, P(x)" via tactic chains; the substrate could ablate P(x) on out-of-distribution x and check if it survives the empirical battery.
- **Non-formal byproducts of the proof process** — when Silver's learner explores tactic chains, intermediate goals or near-misses might be substrate-ingestible CLAIMs even when the parent proof closes via different tactics.

**Fix in v4:** §13 specifies the three substrate-ingestible fragments above, with the operational verdict the substrate renders (residual signal-class on empirical conjectures; cross-domain generalization-fail on ablated cases; near-miss CLAIMs from tactic-tree exploration). Removes the hand-waving "outputs become CLAIMs."

### POSITIONING — comparison class

**(7) Lean Mathlib is a more honest comparison than Silver alone.**

Reviewer's framing:
> Lean Mathlib in particular is a content-addressed, append-only, mechanically-verified substrate of mathematical truth — it's what the Σ-kernel would look like if the kill-test were "Lean kernel accepts." … Naming Mathlib as the comparison rather than Silver clarifies the substrate's actual niche: not "the substrate Silver needs," but "the substrate for empirical mathematical patterns that doesn't exist in Mathlib." That positioning survives any outcome of Silver's company.

This is a positioning correction, not an architectural one. Mathlib is structurally the closest existing analog to the Σ-kernel; Silver's Ineffable is the closest competitor on the *learner* side, but on the substrate side the comparison is Mathlib.

**Partial pushback:** I disagree with the reviewer's implication that Silver should be downplayed. Silver framing is the market context that motivates Prometheus's pivot urgency; Mathlib framing is the technical comparison that clarifies the substrate's niche. Both belong in the doc, with different framings. The reviewer's "Silver framing is good marketing for external readers but Lean Mathlib is the more honest comparison" is partly right and partly wrong: Silver isn't *just* marketing — he's the load-bearing reason this proposal exists at this moment. But Mathlib should be added as the technical comparison class, not replacing Silver.

**Fix in v4:** add §3.7 "Comparison class — Mathlib, AlphaProof, academic projects" alongside the existing §1 Silver context. Frame Mathlib as the substrate-side comparison and Silver as the learner-side comparison. Substrate's niche is the *empirical-pattern* manifold neither Mathlib nor Silver covers.

### LOAD-BEARING — deeper bear case

**(8) The deeper bear case: PROMOTE may be too restrictive for novel structure to fire at all, and the architecture doesn't have machinery to distinguish "engine bad" from "battery bad."**

Reviewer's framing:
> The deeper bear case is structural: the PROMOTE primitive may be too restrictive for empirical-pattern discovery to fire at all. The battery is calibrated on known truths, which by construction look like known truths. Novel structure may have a different statistical shape that the battery rejects as noise. … "calibrated negative result" is unfalsifiable — you can't tell if the engine failed or the calibration did.

This is the deepest critique in the entire review cycle. v3's bear case (neural ≈ evolutionary on PROMOTE rate) assumes PROMOTE rate is non-zero. The deeper bear case assumes PROMOTE rate is zero across all arms because the battery is miscalibrated for novel structure.

**Reviewer's proposed fix:** a meta-loop where Techne occasionally forges a *sharper* checker for high-residual kills, and the substrate audits whether the original battery should have caught what the sharper checker promotes. This connects directly to the v2-thesis anti-calibration-set commitment (PATTERN_BATTERY_CALIBRATION_BIAS, candidate from 2026-05-02) and to the residual primitive's `instrument_drift` classification.

**Fix in v4:** §12 (or new §11.5) operationalizes the meta-loop:
- High-residual kills (residual classifier confidence ≥ 0.9 for signal-class but kill happened anyway) trigger a Techne-forged sharper checker
- The sharper checker is run on a curated set of historical battery-kills with similar residual signature
- If the sharper checker promotes any of them, the original battery is flagged as `uncalibrated_for_residual_class_X`
- A `META_CLAIM` mints against the battery; promoted META_CLAIMs add new kill tests
- Calibration-bias rate (sharper-checker-promoted-but-original-battery-killed / total promotions) is a substrate-grade metric

This makes the "calibrated negative result" falsifiable. If calibration-bias rate is high, the battery is the bottleneck; if it's low and PROMOTE rate is still zero, the engine is the bottleneck.

## Five new candidate symbols filed

From round 3:

1. **PATTERN_INTERNAL_CONTRADICTION_HIDDEN_BY_LANGUAGE** — when a doc's introductory framing claims one structural property and a later operational section markets the opposite, the contradiction can be hidden behind verbal sophistication. Mitigation: cross-section consistency audits as part of doc lifecycle.

2. **PATTERN_DIAGNOSTIC_IGNORES_RECENT_PRIMITIVE** — when a substrate adds a primitive (residual classifier, etc.) and existing diagnostics aren't updated to use it, the diagnostic's signal coverage is silently incomplete. Mitigation: every new primitive triggers a "diagnostic refresh" pass across measurement docs.

3. **PATTERN_POWER_CALCULATION_DEFERRED** — projecting empirical pilots without estimating effect sizes leaves the architecture vulnerable to "the diagnostic is informationally null at every budget" failure. Mitigation: power calculation as a load-bearing section in any proposal naming a measurement plan.

4. **PATTERN_CONSTRUCTION_VS_CONTENT_DIVERSITY** — quality-diversity archives whose axes measure construction-properties (how a thing was built) rather than content-properties (what it is) maximize diversity in the wrong manifold for discovery. Mitigation: at least one content-aware axis per archive descriptor.

5. **PATTERN_UNFALSIFIABLE_NEGATIVE_RESULT** — a "calibrated negative result" framed as substrate-grade is only substrate-grade if the substrate has machinery to distinguish "engine failed" from "evaluator failed." Without the distinction machinery, the negative result is unfalsifiable. Mitigation: meta-loop with sharper checkers + calibration-bias auditing.

These complement round 1's three (PATTERN_SPECIFICATION_GAMING, PATTERN_FILTER_AS_GATEKEEPER, PATTERN_ONTOLOGY_BIAS_IN_FEATURES) and round 2's three (PATTERN_SHARED_PRIOR_AT_TRAINING_LAYER, PATTERN_BEHAVIOR_DESCRIPTOR_COLLAPSE, PATTERN_TASK_A_TASK_B_ECHO_CHAMBER), bringing the total to 11 substrate-grade candidate symbols from this proposal review cycle alone, plus the 5 from the v2-thesis review = **16 candidate symbols across the design-cycle to date.**

That ratio (11 candidates from one proposal's three review rounds) is itself a substrate-grade observation: adversarial design-layer review is highly productive of substrate-grade pattern symbols. The v2-thesis review predicted this; this cycle has empirically borne it out.

## Action items for v4

1. Rewrite §5.1 (Llemma rationale corrected; differentiation comes from action-space + value head + LoRA delta, not base model prior).
2. Five-counts diagnostic, not four-counts (add `signal_class_residual_kill` count integrating residual primitive).
3. Add power-calculation section (§7.x).
4. Minimum proposal share enforcement (`uniform` ≥ 5%, `anti_prior` ≥ 5%, `structured_null` ≥ 5%; total non-prior-shaped ≥ 15%).
5. Swap DAG depth for output canonicalizer subclass in MAP-Elites descriptor.
6. Operationalize §13 Silver-ingestion (specify three substrate-ingestible fragments).
7. Add §3.7 Mathlib comparison alongside Silver framing.
8. Operationalize §12 meta-loop (Techne forges sharper checkers; calibration-bias rate as substrate-grade metric).

## Genuine design-freeze recommendation now

Round 3's depth invalidates v3's design-freeze recommendation. v4 absorbs the corrections and operationalizations; it doesn't add new architectural surface beyond what's already there. After v4 ships:

- The internal contradictions are resolved
- The residual-primitive integration is done
- The power calculation is on the record
- The deeper bear case is operationalized via meta-loop

**v4 design freeze is justified in a way v3's wasn't.** v3 said "ship MVP based on v3"; v4 says "v4 is the corrected version; ship MVP based on v4."

If a round-4 review surfaces critiques as deep as round 3's, those will warrant v5. If round-4 surfaces only mitigations on top, the design is genuinely converged. My prior: round 3 was the high-water mark for design-layer critique; round 4 will be either pure praise or shallow additional surface. MVP is the next high-value move.

— Ergon
