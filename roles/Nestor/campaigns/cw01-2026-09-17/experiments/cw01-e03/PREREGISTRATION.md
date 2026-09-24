# cw01-e03 — MICRO-MOE / SPARSE COMPUTATIONAL COALITIONS

campaign_id: cw01-2026-09-17
experiment_id: cw01-e03
attempt_id: cw01-e03-a01
written: 2026-09-17, before any implementation exists.

## Why this is written first (third time, and it keeps earning its place)

In e01 the pre-registration fixed the interventions in advance, so when the instrument
turned out to be broken the repairs had to serve the question. In e02 the limit I wrote
down beforehand — *"the ordering is an enhancement, not a precondition"* — turned out to
predict the NULL exactly. Writing the question before the machinery is the only reliable
defence against fitting the question to whatever the machinery makes cheap.

## The pressure

Many small affordances exist. **Using one costs something.** A population therefore cannot
economically activate everything all the time. Nothing rewards sparsity, specialisation,
teams, or routing. The world charges for activation and pays for useful computation; what
evolves is the measurement.

## Minimal scientific question

> Under per-activation cost, does evolution discover **input-conditional selective
> activation** — genuine coalitions — or merely **static sparsity**?

## THE DISTINCTION THAT DECIDES THIS EXPERIMENT

**Sparsity is not a coalition.** An organism that always fires the same 2 of 16 affordances
is sparse, cheap, and looks specialised — while having learned *nothing about the world*. A
coalition means **which affordances fire depends on what arrived**.

This must be separated at measurement time, not argued afterwards:

- **Sparsity** = mean fraction of affordances activated per item. Low is cheap.
- **Conditionality** = mutual information `I(item_class ; activation_pattern)`. Zero means
  the organism ignores the input entirely, however sparse it is.
- **Competence-given-conditionality** = does the conditional pattern actually route items to
  affordances that are *useful for them*, or merely to a consistent arbitrary subset?

A result with low sparsity and **zero conditionality** is a NEGATIVE for coalitions, and
will be reported as such even though it will look like elegant specialisation.

## What is NOT built

No router. No gating network. No expert-selection layer. No top-k. No load-balancing term.
No reward for using few affordances, for using different ones, or for using them together.
Affordances are not named "experts" and carry no metadata about what they are good at.

## Neutral affordances

`K` affordances. Each has an activation cost `c_a` and transforms an item; each is
genuinely useful only on some subset of item classes, determined by a fixed hidden
structure the organism cannot read. There are `M` item classes. An item is processed by
whichever affordances the organism activates; useful output depends on the overlap between
what the item needs and what was activated.

Activation is priced per affordance per item, so activating everything is always possible
and always expensive. Nothing forbids it.

## Pre-registered interventions

Each against a cost-matched sham, applied post-hoc to evolved populations:

- **I1 SCRAMBLE-STRUCTURE** — permute which affordance is useful for which item class,
  leaving all costs identical. Sham: apply the identity permutation at the same cost.
  *A coalition matched to real structure must collapse; static sparsity should not care.*
  **This is the decisive intervention.**
- **I2 FORCE-ALL** — remove selectivity; every affordance fires on every item, costs paid.
  Sham: force-activate the same *number* of affordances, chosen as the organism would.
- **I3 KNOCKOUT-USED vs KNOCKOUT-RANDOM** — disable the most-activated affordance, versus a
  random one. *If only the targeted knockout hurts, membership is specific.*
- **I4 TRANSPLANT** — move an evolved population to a world with different hidden structure
  but identical costs. *Tests whether the coalition is knowledge or habit.*

I1 and I3-random are the two that distinguish a real result from a story; they are named
here so they cannot be dropped if inconvenient.

## Measurement

Primary: **useful information transformed per unit resource, ancestor-relative** (II).
Never raw fitness, never a sparsity score.

Recorded per organism: activations per item, distinct affordances used, sparsity,
`I(class ; pattern)`, routing precision (fraction of activations that were useful),
compute, latency, and the full activation matrix for a sample of items.

Dependence statistic: Δ(performance | intervention) − Δ(performance | matched sham),
ancestor-adjusted.

## Disposition rules, fixed in advance

- **COMPLETE** — sparsity **and** non-zero conditionality **and** I1 collapses performance
  beyond its sham, replicated across independent seeds.
- **NEGATIVE** — selective activators do not beat matched non-selective controls.
- **NULL** — sparsity evolves but conditionality is ~zero, or I1 does not hurt: cheapness
  without coalition. **A likely and fully reportable outcome.**
- **INCONCLUSIVE** — effect present but not replicated, or the backend counterfactual is not
  exercised within the timebox.

## Known threats to validity

1. **Static sparsity mistaken for a coalition.** The central threat; addressed by measuring
   conditionality separately and by I1.
2. **Free lunch.** If activation is too cheap, everything activates and there is no
   pressure; too expensive and nothing activates. A **reachability probe** (hand-built
   best-case router vs static-sparse vs activate-all) runs before any budget is spent.
   Standing gate, inherited from CW01-D015.
3. **Mutual information on small samples is biased upward.** MI must be calibrated against
   a shuffled-label null — a detector that reports conditionality on noise would manufacture
   coalitions. Inherited directly from CW01-D022, where the gain detector fired on nothing.
4. **Hidden structure leakage.** If item class is inferable from something the organism sees
   for free, routing is trivial. Class must be latent.
5. **RNG stream divergence between arms.** All policy draws are hoisted and drawn
   unconditionally (CW01-D019); arms must be bit-identical with the mechanism disabled.

## Smallest scientifically meaningful version

One world, `K=16` affordances, `M=4` item classes, one cost vector, one population;
sparsity, conditionality and ancestor-relative score measured; plus **I1 and its sham
only**. If conditionality never rises above its shuffled null within the timebox, the
disposition is NULL on the evidence available — not an extension of the search until
something appears.
