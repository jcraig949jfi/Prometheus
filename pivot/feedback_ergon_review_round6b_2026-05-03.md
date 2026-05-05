---
captured: 2026-05-03 (round 6, reviewer B — deeper of the two)
captured_by: Ergon (Claude Opus 4.7, 1M context, on M1)
reviewer: Second external reviewer, identity unstated; numbered-section structure with embedded subsection numbering matching round-2 / round-4 style; significantly deeper analytical engagement than round-6 reviewer A; closes with simulation offer
target_under_review: pivot/ergon_learner_v7_final.md (commit 9cafeb35)
status: VERBATIM CAPTURE for substrate ingestion
---

# Verbatim review of `ergon_learner_v7_final.md` — round 6, reviewer B

This file captures the second round-6 reviewer's review of v7 verbatim. The reviewer surfaces three new architectural-operational concerns: adversarial optimization probe needed before Trial 2; Trial 2 success criteria miscalibrated; the 10× residual-vs-PROMOTE hypothesis is brittle. Plus operational sharpenings on trivial-pattern detector, cross-model evaluator, anti_prior enforcement, magnitude axis, and counterfactual logging. Plus a new R11 (false gradient lock-in) missing from v7's risk register.

This depth is between round 5 (purely operational) and rounds 3-4 (architectural failure modes the architecture creates by its own corrections). It's "architectural-operational" — refining the operational specs in ways that catch new failure modes the operational specs alone create.

Triage in companion file `meta_analysis_ergon_round6_2026-05-03.md`. v8 in `pivot/ergon_learner_proposal_v8.md`.

---

This is one of the rare cases where the design is coherent end-to-end, but that also makes the remaining risks sharper—because if it fails, it will fail on a small number of very specific load-bearing assumptions rather than general sloppiness.

I'll focus on pressure-testing those assumptions, not rehashing what already works.

## 1. The Core Bet: Residuals as a Dense Gradient

Everything still hinges on one claim:

> Signal-class residuals are dense, predictive, and harder to game than PROMOTE.

You've now done the right thing by:
- making it falsifiable (Trial 1 + Trial 3),
- tiering w_R,
- adding adversarial structured-noise.

But here's the uncomfortable truth:

> You are testing classification accuracy, not optimization stability

A classifier can:
- pass Trial 1 (low FP on synthetic noise),
- and still be exploitable under optimization pressure.

Why? Because:
- Trial 1 = i.i.d. evaluation
- Training = adversarial distribution shift

What's missing: You don't yet simulate closed-loop adversarial optimization against the classifier.

### Concrete addition (high priority)

Add a micro-loop adversarial probe before Trial 2:
- Freeze residual classifier
- Run a tiny optimizer (even random search + hill climbing)
- Objective: maximize "signal-class confidence" without passing battery

Measure:
- how quickly it finds exploits
- whether outputs look like your synthetic structured noise or something new

If it finds exploits in <500 iterations, your current defenses are insufficient even if Trial 1 passes.

## 2. Trial 2 Success Criteria Are Slightly Miscalibrated

> "≥60% of cells filled across all 5 axes"

This is too optimistic for 1K episodes with:
- 5,000 cells
- sparse reward
- no neural guidance

You're implicitly expecting high entropy exploration from weak operators.

Likely outcome: You'll get misleading failure signals (false negatives)

### Suggested adjustment

Split the metric:
- Primary: relative improvement vs uniform baseline
- Secondary: absolute fill (but with lower bar, e.g. 20–30%)

What you actually care about is: *Does structure outperform noise?* not *Did we fill the archive?*

## 3. The "≥10× residual vs PROMOTE" Hypothesis (Q19)

This is directionally right but too brittle as a hard threshold.

Why?
- PROMOTE is not just sparse—it's *policy-dependent sparse*
- Early system = underpowered → artificially low PROMOTE
- Later system = better proposals → PROMOTE rises

So your ratio can collapse even if the system is improving.

### Better framing

Track:
- residual density (absolute)
- PROMOTE density (absolute)
- correlation: residual → eventual PROMOTE

The key question is: *Do residuals predict promotions?*

Not: *Are they 10× more frequent?*

## 4. The Trivial-Pattern Detector Is Underspecified (and Risky)

Right now it's framed as: 4 initial signatures + expected 5–30% trigger rate

That's fine as a start, but the deeper issue: You don't yet distinguish:
- benign triviality (early-stage scaffolding)
- vs pathological attractors

If the detector is too aggressive: → you kill the only gradients available at MVP scale
If too weak: → you get gravitational wells

### Missing piece

You need *temporal analysis*, not just pattern matching.

Add:
- "recurrence density" of similar claims
- "novelty decay" per lineage

A trivial pattern isn't just simple—it's *repeatedly rediscovered with low variation*.

## 5. Cross-Model Evaluator (w_X) Is Still a Quiet Failure Mode

You've constrained it to: "logical consistency only"

Good—but not sufficient.

### Risk

Models share latent structural priors, even without "judgment"

So they can agree on:
- wrong but internally consistent reasoning

Your current safeguard:
- w_X = 0.15
- w_NL = 0.10

This is good weighting, but missing one check:

### Add

Track agreement vs novelty

If:
- high agreement
- low descriptor distance (axis 5)

→ likely prior-driven convergence, not real signal

## 6. Anti-Prior Operator: Good Idea, Weak Enforcement

You require ≥5% share, but:

> That doesn't guarantee meaningful divergence

Anti-prior can still:
- collapse into structured noise
- or shallow variations of prior

Strengthen it by measuring:
- KL divergence from corpus frequency stats
- descriptor displacement vs neural operator outputs

And enforce: anti_prior must occupy regions neural never reaches

Otherwise it becomes symbolic noise with a fancy name.

## 7. MAP-Elites Descriptor: Strong, But One Axis Is Fragile

Axis 4: magnitude buckets

This is good (prevents trivial small-number hacks), but:

### Risk

Magnitude correlates with:
- computational instability
- numerical noise
- false residuals

So you may unintentionally:
- reward high-magnitude artifacts

### Mitigation

Tie magnitude to: stability under perturbation

i.e., large outputs must survive:
- input jitter
- precision changes

Otherwise they shouldn't earn full credit.

## 8. Logging + Observability: This Is Actually a Strength

This is one of the most solid parts of the design.

You've avoided a common failure: building a complex system without the ability to diagnose it

### The only addition I'd suggest

Add "counterfactual logging"

For a subset of claims:
- log what would have happened under:
  - PROMOTE-only reward
  - no trivial detector
  - no w_R

This gives you: causal insight, not just metrics

## 9. RAG Decision: Correct (for now)

Your "no RAG at MVP" decision is solid.

The deeper reason (you hinted at it but didn't fully state it):

> RAG collapses the search space toward known manifolds.

Your system's value is: exploring off-manifold structure

So delaying RAG is not just simplicity—it's epistemically necessary.

## 10. MVP Timeline (Q20)

15 days is tight but plausible, with one caveat:

The hidden time sink is: debugging interaction effects between components

Not: implementing them

Realistic breakdown:
- Trial 1: fine (4 days)
- Trial 2: likely spills to 8–10 days
- Trial 3: depends on debugging → 5–7 days

So: Expect ~20–25 days unless everything works first pass (unlikely)

## 11. Biggest Missing Risk (Q22)

You listed many risks, but one is missing:

### R11: False gradient lock-in

System finds:
- a consistent but wrong signal proxy
- passes all local checks
- becomes dominant in archive

Symptoms:
- good metrics
- no real discoveries

This is *worse than failure—it's illusory success*

Mitigation:
- periodic "null environment" runs
- cross-domain validation (change problem family)
- forced archive resets for subsets

## 12. Is the Design Actually Frozen? (Q34)

You're close—but not fully.

A true freeze requires: No remaining untested foundational assumptions

You still have two:
1. Residuals are a usable gradient *under optimization*
2. MAP-Elites + your descriptor produces *meaningful diversity at this scale*

Your trials test them—but until results exist, the design isn't proven, just well-structured.

### What would justify v8?

Only one thing: Trial 1 or 3 falsifies the residual-gradient hypothesis

Anything else is implementation tuning, not design revision.

## Final Assessment

What's strong:
- Clear falsification pathways (rare and valuable)
- Layered defenses against gaming (thoughtful, not superficial)
- Proper separation of concerns (generator vs verifier vs classifier)
- Realistic cost discipline

What's fragile:
- Residual classifier under adversarial optimization
- Early-stage statistical power assumptions
- Trivial-pattern detection without temporal dynamics
- Implicit assumptions about diversity emergence

## Bottom Line

You've done something most systems like this fail to do:

> You've turned vague ideas ("residuals", "diversity", "anti-prior") into testable operational components.

Now the uncomfortable part:

> The MVP is not about proving the system works—it's about finding out which of your three core bets is wrong.

If Trial 1–3 pass cleanly, you don't just have an MVP—you have a legitimate new learning paradigm worth scaling.

If they don't, the design is still valuable—but as a map of where the idea breaks.

---

If you want, I can simulate likely outcomes of each trial (pass/fail patterns and what they imply structurally).
