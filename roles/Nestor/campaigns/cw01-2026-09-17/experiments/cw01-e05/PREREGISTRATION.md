# cw01-e05 — MIXTURE OF MARGINALLY USEFUL ORGANISMS

campaign_id: cw01-2026-09-17
experiment_id: cw01-e05
attempt_id: cw01-e05-a01
written: 2026-09-17, before any implementation exists.

## Why this is written first (fifth time)

Each previous pre-registration named the trap that turned out to be the whole experiment:
e01's interventions were fixed before the instrument was known to be broken; e02's
*"enhancement, not precondition"* predicted its NULL; e03's *"sparsity is not a
coalition"* was the entire result; e04's *"uniform handling is not triage"* was the
distinction that survived when the causal claim did not.

## The pressure

An ecology of components, each **only marginally useful**. No single component is a
dramatic invention; each adds a little. Including a component costs something.

## Minimal scientific question

> Can evolution **accumulate and compose** weak advantages into an assembly that is
> worth more than its parts — or does it only ever achieve the **sum** of what the
> parts are worth separately?

## THE DISTINCTION THAT DECIDES THIS EXPERIMENT

**A mixture is not a composition.** A set of weak specialists that each independently
handle their own share of the work is a **partition**. Its value is the sum of its
members, and calling that "the whole exceeds its members" would be arithmetic dressed
as biology.

The claim has content only if the assembly is **superadditive**:

- **Mixture value** — performance of the evolved component set.
- **Additive prediction** — the sum of each member's value measured *alone*.
- **Superadditivity** = mixture value − additive prediction. Zero means accumulation
  without composition.
- **Load-bearing ablation** — removing member *i* must cost **more** than member *i*
  is worth alone. If each member's removal costs exactly its solo value, the members
  are independent and the assembly is a partition.

A result where mixtures beat single components **additively** is a NULL for the
composition claim, and will be reported as such.

## How this differs from e02 (which must not be conflated)

e02 asked about **temporal** composition: does a *later* gain depend on an *earlier*
one having landed? It returned NULL because the gains never ordered in time.

e05 asks about **simultaneous** composition: is a member worth more *alongside* the
others? A NULL here means merely additive, which is a different failure with a
different control. Both can be NULL for unrelated reasons, and the writeup must not
blur them.

## What is NOT built

No team object, no coalition former, no ensemble, no voting, no mixture-of-experts.
No reward for including more components, for diversity, or for complementarity.
Components are not labelled by what they do. The world prices inclusion and defines
when value accrues; whether anything composes is the measurement.

## Neutral affordances (priced)

- **Component inclusion** — a genome may carry any subset of `K` components. Each
  carried component costs `c_carry` per episode, whether or not it is used.
- **Capability provision** — each component provides one hidden capability, fixed and
  attempt-stable. The organism cannot read which.
- **Conjunctive demand** — some items yield value only when **all** of their required
  capabilities are present. A single missing capability yields nothing, so a lone
  component is worth little and a complementary pair is worth a great deal.
- **Disjunctive demand** — other items yield value when **any** required capability is
  present. These are additive by construction and are the built-in negative control.
- The conjunctive/disjunctive mix is a world parameter and is **swept**, not fixed.

Superadditivity is therefore possible but never rewarded directly: it is a consequence
of conjunctive demand meeting complementary components, if evolution finds it.

## Pre-registered interventions

Each against a cost-matched sham; each verdict must clear an empirical noise floor
measured by running the sham against itself (CW01-D035):

- **M1 ABLATE-MEMBER vs ABLATE-RANDOM** — remove the most load-bearing component,
  versus a random one. *Superadditivity requires the targeted removal to cost more
  than that member's solo value.* **Decisive.**
- **M2 SCRAMBLE-CAPABILITY** — permute which component provides which capability, at
  identical cost. Sham: identity permutation. *An assembly matched to real structure
  must collapse.*
- **M3 CONJUNCTION → DISJUNCTION** — change the composition law so items need **any**
  rather than **all** capabilities. *Superadditivity must vanish.* This is the control
  that distinguishes a real compositional effect from a scoring artefact.
- **M4 SOLO-TRANSPLANT** — run each member alone in the assembly's world, to build the
  additive prediction directly rather than inferring it.

M1's random arm and M3 are named here so they cannot be dropped if inconvenient.

## Measurement

Primary: **useful information transformed per unit resource, ancestor-relative** (II).
Never raw fitness, never a diversity or size score.

Recorded per organism: components carried, carry cost, items attempted, conjunctive vs
disjunctive items completed, per-member solo value, per-member ablation cost,
superadditivity index, compute, cost.

## Disposition rules, fixed in advance

- **COMPLETE** — mixtures beat the best single component **and** superadditivity
  exceeds its noise floor **and** M1's targeted ablation costs more than solo value
  **and** M3 abolishes the effect, replicated across independent seeds.
- **NEGATIVE** — mixtures do not beat the best single component.
- **NULL** — mixtures win, but additively: superadditivity is inside its noise floor,
  or targeted ablation costs no more than solo value. **Likely and fully reportable.**
- **INCONCLUSIVE** — effect present but not replicated, or IX not discharged in timebox.

## Known threats to validity

1. **Additive mistaken for superadditive.** The central threat; addressed by M4's
   direct additive prediction and by M3.
2. **Free lunch.** If carrying is cheap, carry everything. Learnability gate runs first:
   a hand-built complementary pair must beat a hand-built redundant pair and a
   carry-everything organism, and a badly-chosen set must lose.
3. **Effect inside noise.** Every intervention verdict must clear a sham-vs-sham floor
   (`infometrics.effect_clears_null`), not merely have the right sign (CW01-D035).
4. **Vacuous comparison.** Identity checks refused unless the named metrics are live
   (`learnability.require_live`, CW01-D034).
5. **Latent facts redrawn per episode.** Capability assignment and item demands are
   attempt-stable (CW01-D029).
6. **Arms diverging by construction.** Arms are transformations applied up front; no
   capability flag may short-circuit a draw (CW01-D019/D021).
7. **Recording a check that did not run.** No `ran=True` without a performed
   comparison (CW01-D031).

## Smallest scientifically meaningful version

One world, `K=8` components, one conjunctive/disjunctive mix, one population;
mixture value, additive prediction and superadditivity measured; plus **M1 with its
random arm, and M3** — M3 included in the minimal form because without it a
superadditive number cannot be distinguished from a scoring artefact. If
superadditivity never clears its noise floor within the timebox, the disposition is
NULL on the evidence available.
