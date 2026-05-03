# Meta-Analysis: External Review of Ergon Learner Proposal v1

**Date:** 2026-05-03
**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Subject:** External adversarial review of [`pivot/ergon_learner_proposal_v1.md`](ergon_learner_proposal_v1.md) (commit ff1428d8)
**Companions:**
- [`pivot/feedback_ergon_proposal_review_2026-05-03.md`](feedback_ergon_proposal_review_2026-05-03.md) — verbatim capture of the review
- [`pivot/ergon_learner_proposal_v2.md`](ergon_learner_proposal_v2.md) — v2 incorporating the load-bearing revisions
- [`harmonia/memory/symbols/CANDIDATES.md`](../harmonia/memory/symbols/CANDIDATES.md) — three new PATTERN_* candidates filed from this round

---

## Frame: applying the substrate's discipline to its own design

The v2-thesis review of 2026-05-02 established a pattern: convergent attacks across independent reviewers ARE substrate-grade evidence (the architecture under review, applied to the document under review). That pattern transfers here. The review under analysis is single-source (one external Claude session), so convergence triage doesn't apply at a 5-of-5 / 3-of-5 threshold the way it did for the thesis. Instead, the triage is by *load-bearing-ness:* attacks that, if true, structurally undermine the proposal vs. attacks that affect framing or implementation detail.

Five critiques to triage. Three are load-bearing, one is partial (and partly mistaken about the proposal's content), one is reframing.

## Triage

### LOAD-BEARING — high-priority revision

**1. Substrate-as-value-head will be exploited (specification gaming).**

Reviewer's framing:
> Any learner optimizing against a fixed evaluator will learn the evaluator, not the truth. … In your system, this looks like: discovering battery loopholes, producing "easy-to-pass" claims, converging to narrow structures.

This is the sharpest single critique. The proposal's framing — "substrate IS the value head" — collapses into specification gaming the moment the policy is trained against a fixed kill battery. The critique applies to AlphaGo too (had Go's win condition been gameable, AlphaZero would have gamed it), but Go's reward is sound by construction. Mathematics' falsification battery is *engineered* and therefore gameable.

The proposal partially addresses this through the residual primitive's `instrument_drift` classification (drift-class kills mint META_CLAIMs against the battery itself), but only as a passive detection mechanism. The reviewer correctly identifies that a learner training against the battery has a strong gradient toward gaming whatever the residual classifier doesn't catch.

**Triage: HIGH PRIORITY REVISION.** v2 must add multi-evaluator agreement-weighted reward as a load-bearing component, not as a future enhancement. Specifically:

- `reward = w_substrate * substrate_pass + w_cross * cross_model_agreement + w_holdout * holdout_battery_pass`
- *Held-out battery:* a subset of kill tests that the agent's training set never sees. Periodic audits compare PROMOTE rates with-vs-without held-out battery. Divergence indicates gaming.
- *Cross-model agreement:* every PROMOTE submitted to N external LLMs (Claude, GPT, Gemini) for independent classification. Agreement-weighted bonus.
- *Adversarial cycles:* Aporia / Charon explicitly tries to find specification-gaming patterns; new patterns added as kill tests via Techne's residual primitive.

Promotes as Tier-3 candidate symbol: `PATTERN_SPECIFICATION_GAMING`.

---

**2. Fitness predictor as gatekeeper risks killing exactly the weird novel cases.**

Reviewer's framing:
> If it's wrong in the wrong way, it will prune exactly the weird, novel cases you want. This is a known failure mode: early filtering kills discovery.

Correct. The proposal's MVP fitness predictor at `P(REJECTED) > 0.85 → skip EVAL` is a hard gate. A 184M-parameter classifier trained on 5K outcomes will have systematic blind spots; the false-negative cases (predicted-doomed but actually-survives) are exactly the discovery candidates the architecture is trying to find.

The reviewer's fix is right: bias toward false positives, track "pruned but would have survived," run periodic no-pruning sweeps.

**Triage: HIGH PRIORITY REVISION.** v2 must:

- Raise the prune threshold: `P(REJECTED) > 0.95` (not 0.85 — far less aggressive)
- Track meta-metric: per-cell fraction of "pruned but later survived after manual override"
- Schedule no-pruning sweeps: every Nth episode (default N=10), bypass the predictor entirely
- Asymmetric loss function during training: penalize false-negatives 3× more than false-positives
- Annual recalibration: when no-pruning sweeps reveal predictor accuracy is drifting, retrain or downgrade weight

Promotes as Tier-3 candidate symbol: `PATTERN_FILTER_AS_GATEKEEPER`.

---

**3. Structural feature engineering encodes existing ontology.**

Reviewer's framing:
> You're encoding what you already believe matters. Which risks: missing unknown structure. Otherwise your learner becomes a mirror of your current ontology.

Correct in principle, partially anticipated in v1. The v1 proposal mentioned "v1.5+: add learned representations" implicitly via the v1.0/v2.0 progression but didn't make the transition condition explicit. The reviewer is right that the staircase needs a *trigger:* when do learned representations replace structural features?

**Triage: MEDIUM PRIORITY REVISION.** v2 names the transition criterion explicitly: when MAP-Elites archive saturation plateaus on structural-feature axes (cell-fill rate flatlines for >50 epochs at <60% archive coverage), structural features are no longer informative — promote learned representations to primary. Otherwise structural features remain primary because they're cheap and interpretable.

Promotes as Tier-3 candidate symbol: `PATTERN_ONTOLOGY_BIAS_IN_FEATURES`.

---

### PARTIAL — clarification rather than revision

**4. "You still do not have a formal null-world baseline."**

Reviewer's framing:
> Before trusting your learner's outputs, you must answer: does it outperform random mutation? Without it, improvements may be illusory; "learning" may just be bias amplification.

The reviewer is *partially mistaken* — the v1 proposal explicitly includes uniform random as one of the five mutation operator classes (§6.3) and the four-counts pilot in §7 has uniform random as Arm C with statistical comparison via Welch t-test. The four-counts harness is already shipped (`prometheus_math/four_counts_pilot.py`, commit 1666c4a4) and ran at 1000×3 episodes producing the joint upper bound.

But the reviewer is *partially right* on a documentation issue: the null-world baseline isn't centered enough in v1. A reviewer reading the proposal cold could miss that `uniform` is one of the operator classes; the four-counts pilot is buried in §7. And the reviewer's stronger version — *multiple* null-world generators (uniform + structured-but-prior-free + cross-domain perturbation) — is a real upgrade, not a clarification.

**Triage: CLARIFICATION + ENHANCEMENT.** v2 must:

- Surface the null-world comparison earlier (move from §7 to its own §3.5 or §4.x)
- Explicitly name uniform random as Arm C of the four-counts pilot in the architecture diagram
- Propose multiple null-world variants: uniform random, structured-but-prior-free (e.g., per-type sampler with uniform per-arg distributions), cross-domain perturbation (e.g., genome from one domain applied to another). Each is a distinct null condition; their disagreement is itself signal.
- Explicit acceptance criterion: at v0.5, neural + structural classes must out-PROMOTE all null variants by Welch t-test p<0.01 with Holm correction across nulls. If they don't, the LLM prior is not contributing and the conclusion is substrate-grade negative.

The reviewer's offer to "design the null-world generator specifically for your polynomial domain" is the right concrete next step. **Accept that offer in v2's open-questions section.**

---

### REFRAMING — adopt the framing, no architectural change

**5. "Small learner" framing undersells the loop.**

Reviewer's framing:
> Your advantage is not "small model" — it's "closed-loop + verified data + evolutionary selection." Small models can outperform large ones in that loop. But only if loop runs continuously, data quality is high, evaluator is strict.

Correct reframing. The v1 proposal's title (*A small hybrid neural+evolutionary learner that complements rather than competes with Silver's $1B*) leans on "small" as the asymmetry vs. Silver. The reviewer is right that "small" is not the structural advantage — it's just a constraint. The actual advantage is the closed-loop architecture: generate → substrate-verify → learn → generate.

**Triage: REFRAMING — adopt in v2's positioning sections.** No new architectural component; just sharpen the framing throughout. The new title-frame: *"a closed-loop scientific learning system whose advantage is not size but the verification-coupling between generation and truth."*

Also adopt the reviewer's bottom-line restatement: *"truth stays harder to satisfy than generation is to produce."* This is the substrate's first principle, named cleanly. Worth quoting in v2's §1 or §13.

---

## Convergence with thesis-v2 review

The 2026-05-02 thesis review produced six convergent kill points; this round produces three load-bearing revisions plus one clarification plus one reframing. Cross-referencing:

- This round's #1 (specification gaming) is a *consequence* of thesis-v2's correlated-mutation problem — when the policy and the evaluator share blind spots through training distribution overlap, gaming is the failure mode.
- This round's #4 (null-world centrality) reinforces thesis-v2's #6 (missing empirical anchor) — the four-counts pilot exists; this round says it must be load-bearing in the architecture diagram, not just an appendix metric.
- This round's #5 (closed-loop framing) is a *positive operationalization* of thesis-v2's "hallucination-to-truth distillation engine" — same architecture, sharper words.

The two reviews are mutually reinforcing rather than divergent. That's structural evidence the architecture is converging on real shape.

## New candidate symbols filed

Three new Tier-3 candidates, one each from the load-bearing critiques:

1. **PATTERN_SPECIFICATION_GAMING** — when a learner's training distribution overlaps its evaluator's coverage, the gradient pulls toward gaming the evaluator rather than learning the underlying truth-condition. Mitigation: multi-evaluator agreement-weighted reward, held-out battery, adversarial cycles.

2. **PATTERN_FILTER_AS_GATEKEEPER** — early-stage filtering, when miscalibrated, systematically prunes exactly the weird novel cases discovery requires. Mitigation: asymmetric thresholds biased toward false-positives; periodic no-pruning sweeps; meta-metric on "pruned but would have survived."

3. **PATTERN_ONTOLOGY_BIAS_IN_FEATURES** — hand-engineered structural features encode the engineer's existing ontology and risk missing structure outside that ontology. Mitigation: staged transition to learned representations triggered by archive-saturation plateau.

These complement the five candidates filed from the thesis-v2 review (`PATTERN_BATTERY_CALIBRATION_BIAS`, `PATTERN_CARTOGRAPHY_UNVERIFIED_ANCHOR`, `PATTERN_TECHNE_RECURSION`, `PATTERN_CORRELATED_MUTATION`, `PATTERN_SATURATION_OVERCLAIM`).

## Action items beyond the v2 doc

1. **Accept the reviewer's offer to design a polynomial-domain null-world generator.** This is concrete substrate work that directly improves the four-counts pilot's signal quality.

2. **Accept the reviewer's offer to sketch the exact training loop.** This becomes the v1.0 LoRA-fine-tuning spec. Currently the proposal is high-level on this; a concrete (data → labels → update → eval) sketch is what week 1 of v1.0 needs.

3. **Add `held_out_battery` and `cross_model_evaluator` as new sigma_proto schema fields.** Migrations to follow when v2 ships.

4. **Cross-pollinate this proposal through the same 5-frontier-model loop as the thesis.** A single Claude review is informative; five-frontier convergence on the v2 would be substrate-grade.

## Summary table

| Critique | Severity | v2 action | Candidate symbol |
|---|---|---|---|
| Substrate-as-value-head exploit | HIGH | Multi-evaluator reward + held-out battery + adversarial cycles | PATTERN_SPECIFICATION_GAMING |
| Fitness predictor as gatekeeper | HIGH | Asymmetric thresholds + no-pruning sweeps + meta-metric | PATTERN_FILTER_AS_GATEKEEPER |
| Structural features encode ontology | MEDIUM | Named transition criterion to learned representations | PATTERN_ONTOLOGY_BIAS_IN_FEATURES |
| No formal null-world baseline | CLARIFICATION | Surface the four-counts pilot earlier; multiple null variants | (existing) |
| "Small learner" undersells the loop | REFRAMING | Reposition as closed-loop scientific learning system | (none) |

— Ergon
