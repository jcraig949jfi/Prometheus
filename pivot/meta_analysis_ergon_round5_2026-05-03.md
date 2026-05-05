# Meta-Analysis: Round 5 (Gemini) External Review of Ergon Learner Proposal v4

**Date:** 2026-05-03 (late evening — round 5)
**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Subject:** Gemini's adversarial review of [`pivot/ergon_learner_proposal_v4.md`](ergon_learner_proposal_v4.md). Reviewer was given v4 (commit eedcb893), not v5. Some critiques are partially addressed by v5; v6 absorbs the new ones.
**Companions:**
- [`pivot/feedback_ergon_review_round5_2026-05-03.md`](feedback_ergon_review_round5_2026-05-03.md) — verbatim capture
- [`pivot/ergon_learner_proposal_v6.md`](ergon_learner_proposal_v6.md) — v6 incorporating round-5 revisions (focused delta from v5)
- Round-1 through round-4 meta-analyses already on disk

---

## Frame: round 5 confirms diminishing returns on design-layer review

Rounds 3 and 4 surfaced architectural failure modes the architecture itself created (round 3: internal contradictions + missed substrate integration; round 4: residual-classifier-as-single-point-of-failure created by v4's promotion of residuals to first-class reward).

Round 5 (Gemini) is at less depth. It produces three operational concerns and one architectural sharpening, plus a direct concrete question. The depth of "the architecture creates new failure modes via its own corrections" — which characterized rounds 3 and 4 — is absent. Gemini's own closing line: *"The design freeze is justified. The architecture is sound enough that further theorizing without empirical feedback from the Σ-kernel will yield diminishing returns."*

The round-4 reviewer's prior — "round 4 was the high-water mark; round 5 will be additive surface, not corrective" — is empirically supported by Gemini's review. v6 is warranted because the new concerns are real, but it's a focused delta from v5, not a full architectural rewrite.

## Triage of Gemini's critiques

### Already addressed in v5 (reviewer was given v4)

**(A) Cross-Model Agreement Contamination, weighting concern.** v4 had w_X=0.25; v5 reduced to 0.15 and added w_NL=0.10 (non-LLM evaluator). Partially addresses Gemini's contamination concern.

**(B) Power Calculation reliance on Count 5.** v4 introduced the power calculation; v5 added the adversarial residual benchmark + abstention zone + `residual_signal_precision` metric to harden the classifier that produces Count 5. Gemini's critique applies to v5 too but is less acute given v5's defensive surface.

### LOAD-BEARING — new in v6

**(C) Cross-model evaluator should evaluate DAG consistency, not conjecture validity.**

Gemini's mitigation: *"The N≥2 external LLMs should strictly evaluate the logical consistency of the proof trace/DAG, not the mathematical validity of the conjecture itself."*

This is sharper than v5's response to the same concern. v5 reduced the weight (0.25 → 0.15) and added a non-LLM evaluator. Gemini wants to *change what the LLM evaluators are asked*. If they evaluate "is this a valid discovery?" — they will reward syntactic familiarity. If they evaluate "is this DAG composition logically self-consistent?" — they become a logic-checking layer that doesn't reward conjecture novelty in either direction.

**v6 specification:** Cross-model evaluator prompt template explicitly evaluates:
- Does the DAG composition produce the claimed output deterministically?
- Are intermediate steps logically sound under the typed-composition rules?
- Are there logical errors in the chain of operator applications?

Output: `{consistent, inconsistent, ambiguous}`. NOT a verdict on whether the result is mathematically meaningful.

This decouples the LLM evaluator from the discovery-evaluator role — discovery evaluation is done by the substrate (kill battery) and the residual classifier; the LLM evaluator becomes a logic-consistency cross-check.

Promotes as Tier-3 candidate symbol: `PATTERN_LLM_EVALUATOR_SCOPE_CREEP` — when LLMs are asked broad evaluative questions, their training-distribution prior contaminates the verdict; restrict their scope to mechanically-checkable consistency.

**(D) Gravitational wells in anti_prior space — output magnitude buckets need bounded definitions.**

Genuinely new architectural concern. When stepping outside the LLM prior, the engine often crashes into structural traps: small-number coincidences, trivial prime-density artifacts, scale-related correlations that look like structural anomalies but are actually computational artifacts. v5 doesn't address this.

**v6 mitigation:**
- **Bounded output-magnitude buckets.** Replace v5's "log-binned over numerical output magnitude (5 quantile buckets)" with explicit fixed bounded ranges: bucket 1 = magnitude in [10⁰, 10³], bucket 2 = [10³, 10⁶], bucket 3 = [10⁶, 10⁹], bucket 4 = [10⁹, 10¹²], bucket 5 = [10¹², ∞). Outputs outside [10⁰, 10¹⁵] fall into an `out_of_band` cell that is permanently de-emphasized in selection.
- **Trivial-pattern detector as a kill-battery extension.** Curated set of "known trivial pattern signatures" — small-number coincidences (n < 10 magnitude, low arithmetic complexity), prime-density artifacts (output = π(x) × constant for small x), pure scale correlations (output is just a rescaling of input). Matches are killed before entering the F1+F6+F9+F11 battery as `F_TRIVIAL_BAND_REJECT`.
- This integrates with v4/v5's Techne meta-loop: trivial-pattern signatures are themselves substrate-eligible kill tests, which can be expanded over time as new gravitational wells are discovered.

Promotes as Tier-3 candidate symbol: `PATTERN_GRAVITATIONAL_WELL_IN_OFF_PRIOR_EXPLORATION`.

### Operational concern (not architectural correction)

**(E) Compute Budget Headroom.**

v5 estimated $300-800/mo at v1.0. Gemini correctly notes hidden costs:
- Postgres IOPS for kernel constraints
- Redis hot cache costs at scale
- Network egress (cross-region API + cloud GPU ↔ local)
- Storage egress (LoRA checkpoints, archive snapshots)

**v6 revision:** revised range $400-1000/mo at v1.0 (~25-30% headroom over v5). Plus an explicit "operational overhead" line item in §8.1 covering the three new cost categories.

Not architecturally load-bearing but financially honest.

### The closing question

Gemini's specific question deserves a specific answer:

> "What is the specific threshold of statistical confidence you require from the day-1 residual benchmark before you trust the primitive enough to let it steer the w_R reward weight?"

v5 named the criterion at the wrong level — "≥85% accuracy + <5% FP on synthetic structured-noise" is a *classifier accuracy* criterion, not a *statistical confidence in the gradient* criterion.

The deeper question: at what threshold does the residual classifier become reliable enough that w_R should be active in the reward function?

**v6 specification — confidence-tiered w_R activation.** With 200 benchmark samples (50 obvious noise + 50 borderline signal + 100 synthetic structured-noise), the upper 95% one-sided CI on FP rate at observed counts:

| Observed FP on 100 SSN samples | Upper 95% CI bound | w_R activation |
|---|---|---|
| 0–2 (≤2%) | ≤4.7% | **0.15 (full)** |
| 3–5 (≤5%) | ≤9.4% | **0.075 (half)** |
| 6–10 (≤10%) | ≤16.4% | **0** (residual primitive in escrow; can be used for diagnostics but not reward) |
| >10 | — | **0** (deep escrow; classifier must be retrained or replaced before any production use) |

Plus calibration ECE (Expected Calibration Error) ≤ 0.05 across 5 confidence bins required for any non-zero w_R.

This gives Gemini a concrete answer: w_R is conditional on observed-FP-on-synthetic-structured-noise with specified thresholds, and the activation is *tiered* (not binary) — borderline classifier quality earns half-weight, not full activation.

## Two new candidate symbols filed

1. **PATTERN_LLM_EVALUATOR_SCOPE_CREEP** — when LLMs are asked broad evaluative questions ("is this a valid discovery?"), their training-distribution prior contaminates the verdict; the right scope for LLM evaluators is mechanically-checkable consistency, not novelty-judgment.

2. **PATTERN_GRAVITATIONAL_WELL_IN_OFF_PRIOR_EXPLORATION** — when an exploration operator steps outside standard priors, common failure modes include small-number coincidences, scale artifacts, and trivial prime-density correlations masquerading as structural signal. Mitigation: bounded output-magnitude buckets + trivial-pattern detector as kill-battery extension.

Total candidate-symbol harvest from this proposal cycle: **18** (5 from round 4 + 5 from round 3 + 3 from round 2 + 3 from round 1 + 2 from round 5). Plus 5 from the v2-thesis review = **23 candidate symbols across the design cycle.**

## Action items for v6

V6 is a focused delta from v5, not a full rewrite. Three concrete changes plus one direct answer:

1. §5.3 update: cross-model evaluator prompt template specifies DAG-consistency evaluation, not conjecture-validity.
2. §6.2 update: bounded output-magnitude buckets (explicit fixed ranges); trivial-pattern detector added as F_TRIVIAL_BAND_REJECT kill-battery extension.
3. §8.1 update: revised compute envelope $400-1000/mo at v1.0; new "operational overhead" line item.
4. §2.6 update: confidence-tiered w_R activation table (the answer to Gemini's question).

## V6 is the genuine design freeze

I've now declared design freeze four times (after v3, v4, v5, and now v6). Round 5's depth is qualitatively less than rounds 3-4 — Gemini's closing line confirms this from outside the project:

> *"The design freeze is justified. The architecture is sound enough that further theorizing without empirical feedback from the Σ-kernel will yield diminishing returns."*

I agree with the round-4 reviewer's offer to simulate first-10K-episode pilot outcomes, and Gemini's confirmation that the design is sound enough for empirical work. The honest path from here:

**v6 ships → MVP build begins → simulation offer accepted in parallel → empirical signal from MVP and a-priori expected distribution from simulation are compared → v7 only if MVP empirical signal falsifies a v6 commitment.**

If a round-6 review surfaces critiques of round-3-or-4 depth (architectural failure modes the architecture creates by its own corrections), the freeze is again revisable. My prior, supported by round 5: the design has converged.

— Ergon
