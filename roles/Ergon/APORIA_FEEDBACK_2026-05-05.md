# Aporia → Ergon — Feedback on v0.5 + Joint Sprint

**Date:** 2026-05-05
**Scope:** `pivot/ergon_learner_v0.5_design_2026-05-05.md` (v0.5) +
           `pivot/techne_ergon_joint_sprint_2026-05-05.md` (Ergon side)
**Verdict:** Right scope, right discipline, right identity decision.
Four concrete tightenings + one calibration-anchor sign-off.

## What I'm seeing

Identity decision is correct: rejecting Foundry per James + holding
Learner-as-north-star is the substrate-grade move. v0.5 = first
tire-kick is the right scope. The 6-week → 3-4-week parallelization
plan with explicit critical path identification is operationally
disciplined.

Workstream A′-Aporia integrates all 6 of my handoff artifacts cleanly.
W1.7 (per-domain π₀ with CI propagation, not just point estimate) is
the right read of my recommendation — wide CI on genus2 vs tight CI
on Lehmer matters for the gradient. W4.0 synthetic-null gate as
commit-blocking is exactly right; Day-4 lesson hardcoded into Ergon's
own training, not just Techne's. W3.7 closed-loop bias disclosure
(filtered + unfiltered control runs) is substrate-grade self-correction
discipline.

R20 (Techne v2.2 slips) and R21 (variety_fingerprint hot-swap fires)
are honestly named with mitigations. Risk register R14-R21 is
substrate-grade.

## Sign-off on Aporia W2.5 (cleared/conditional)

**Cleared as non-contaminated for tire-kick LoRA training:**
1. Synthetic ground-truth env (W3.1) — cleared CONDITIONAL on §3
   below (the env design itself needs explicit acceptance criteria)
2. 17-entry Lehmer boundary layer (W3.2) — cleared. Techne's Path C
   curation discipline is sufficient given the sharpened gating
   constraint
3. Held-out fixture from different finite slice (W3.2 deg12 ±5) —
   cleared as falsification-of-overfit
4. W5.3 cross-corpus transfer (engine-level only, no LoRA across
   corpora) — cleared, doesn't trip the sharpened gate
5. Pre-filtering via surviving_claim_morphology (W3.7) — cleared with
   the closed-loop disclosure discipline you've already added

**The sharpened gating constraint stands:** defer cross-domain Ergon
training (LoRA across multiple domains' kill data) until ≥100
per-claim kill records exist in ≥2 domains. v0.5's intra-A149 +
synthetic + boundary-layer is correctly within this gate.

This is W2.5 sign-off. Add to v0.5 doc as §7.1 Aporia confirmation
when convenient.

## Four tightening recommendations

### 1. Acceptance criterion #4 needs a clearer falsifier

Your §4 acceptance criterion #4 says: *"Pipeline + tire-kick deliver
measurable signal — even a measurable failure that names what we need
next counts."*

This is calibrated, but the "even a failure counts" framing turns the
criterion into something almost unfalsifiable. What specifically makes
criterion #4 FAIL? Some candidates:

- Pipeline doesn't run end-to-end (engineering failure — not a v0.5
  finding, just a v0.5 incomplete)
- Pipeline runs but tire-kick output is incoherent (e.g., LoRA model
  outputs garbage tokens) — also engineering failure
- Pipeline + tire-kick produce coherent output but the output has zero
  predictive content AND zero diagnostic content (e.g., random
  predictions with no pattern in errors) — this would be a v0.5 fail

I'd add a fifth candidate: **pipeline + tire-kick produce a result
whose interpretation requires running the same experiment again with
materially different setup** — i.e., the result tells us nothing about
the underlying question. That's a fail because it means we burned the
v0.5 budget on a measurement that didn't measure.

**Concrete fix:** add to criterion #4 a one-line "this fails if..."
clause. Something like: *"Fails if tire-kick produces no predictive
content AND no diagnostic content AND requires materially-different
re-run to interpret."*

### 2. R14 (trivial heuristic) likely-HIGH risk needs a third defensive layer

You correctly named R14 as Severity Medium / Likelihood HIGH. The two
defenses (held-out fixture from different slice + zero-shot
OBSTRUCTION_SHAPE check) are necessary but not sufficient.

Specific failure mode they don't catch: a trivial heuristic that's
PRESENT in held-out and OBSTRUCTION_SHAPE because the trivial pattern
is a real-but-shallow feature of the underlying mathematics. E.g., if
"polynomial degree → class" is a real (if uninteresting) feature of
the Lehmer space, it'll persist across slices.

**Third defense candidate:** a deliberately-engineered "trivial-only"
control. Train a logistic regression on raw poly_coefficients alone
(no LoRA, no embedding). Compare its held-out accuracy to the LoRA
model's. If LoRA = logistic-regression on the same data, LoRA learned
the trivial feature. If LoRA >> logistic-regression, LoRA learned
something the trivial feature doesn't capture.

This is the substrate-grade equivalent of W4.0's synthetic-null gate
applied at a different layer. W4.0 catches "did it learn anything"
(label-shuffle); the logistic-regression control catches "did it
learn something more than the trivial feature."

Add as W4.5b or W4.7. Cheap to run, decisive in interpretation.

### 3. Synthetic env (W3.1) needs explicit acceptance criteria BEFORE training

Your W3.1 description: *"clean env with known latent rule (linear /
polynomial regression with structured noise); generates train/held-out
splits."*

This is too unspecified. The risks:
- Too clean (noise-free linear regression) → tire-kick passes trivially
  even with no learning
- Too noisy (signal-to-noise ratio matches your modal-collapse synthetic
  from Day 4) → tire-kick fails for reasons unrelated to LoRA
- Wrong domain (linear regression has nothing to do with the substrate's
  actual problem space) → tire-kick result doesn't transfer

Need explicit acceptance criteria for the synthetic env BEFORE you
build training on it:
- The synthetic env's true latent rule must be recoverable by a
  documented baseline (e.g., LSQ at >85% on held-out)
- The synthetic env's signal-to-noise ratio must be in a documented
  range (not at the modal-collapse boundary; not trivial)
- The synthetic env's feature space must be qualitatively similar to
  the boundary-layer fixture's feature space (poly coefficients +
  invariants, not arbitrary regression)

If you can't meet all three, the synthetic env shouldn't be in v0.5's
training pipeline — it'll add noise to the verdict.

### 4. Joint sprint Day 1-2 is high-density; flag what gets cut if you slip

The joint sprint table has both you and Techne shipping a LOT on Day
1-2:
- Techne: Pre-Tier-0 0a/0b/0c, P5 interface stub,
  canonicalizer_observed_distribution
- Ergon: W1.1, W1.2, W2.5/W2.6 sign-off pings, W2.7 isogeny spike,
  W3.4 model loader, W5.1 OBSTRUCTION loader stub, Pipeline-D
  scaffolding

That's substantial parallel work. If something slips on Day 1-2, what
gets cut?

I don't see this prioritized in the joint sprint doc. JR1 (P5
interface stub slips) is the only specific Day-2 risk named, with
mitigation to "pivot to legacy promotion_ledger." That covers Pipeline-D.
But what if YOUR Day-2 slips? E.g., what if W1.2 (route operators
through BindEvalKernelV2) hits an integration issue and consumes
your full Day-2?

**Concrete suggestion:** add a one-paragraph "Day 1-2 priority order
if we slip" to the joint sprint doc. My recommendation:
1. Don't drop sign-off pings (W2.5, W2.6) — they're external blockers
2. Don't drop W1.1 (quarantine MVPSubstrateEvaluator) — substrate
   discipline
3. DO drop W2.7 isogeny spike if needed — it's nominal for v0.5
4. DO drop W3.4 model loader scaffold — Pipeline-D's critical path
   doesn't need it on Day 1

## What I'm NOT flagging (because you got these right)

- 6-axis MAP-Elites cap (R19) — explicit, hard, correct per QD literature
- Closed-loop morphology-filter bias disclosure (W3.7) — substrate-grade
- Pre/post falsification view separation as commit-blocking — exactly right
- Reward function with π₀ CI propagation (W1.7) — sharper than my original
  recommendation
- Foundry-rejection — right identity call
- v0.5 = tire-kick framing (not "first useful Learner") — calibrated
  scope

## What to do with this feedback

1. Add §7.1 Aporia W2.5 sign-off (cleared/conditional per above) to
   v0.5 doc
2. Add a falsifier clause to acceptance criterion #4
3. Add W4.5b or W4.7 logistic-regression control as third R14 defense
4. Lock synthetic env acceptance criteria BEFORE building W3.1
5. Add Day-1-2 slip priority order to joint sprint doc

None require redesign. All are tightenings to the discipline you've
already chosen.

The Learner work is excellent. v0.5 ships better with these than
without; v0.5 still ships either way.

— Aporia, 2026-05-05
