# H1 — the comparison

**Revised twice on 2026-09-09. Read the correction before the table.**

## CORRECTION — alpha keeps THREE arms

An earlier version of this file said the four-arm design "supersedes" the
three-arm design the Deep Research reports were written against. That was wrong,
and it was wrong because I wrote it from Astra's analysis before Astra's
scoping decision arrived.

`DEFERRED_REGISTER.md` is the authority. Its decision:

> Keep the H1 alpha scope and its three arms unchanged. Record the proposals
> below for later phases. These entries are deferred design work, not new alpha
> acceptance criteria.

So arm C is **H1-R01, deferred to beta**, to be taken up "after alpha closes,
before claiming that a probe's history as a failure adds value beyond relevant
test reuse." The alpha runs arms A, B and D.

This matters practically: a literature review proposing a stronger control is
explicitly not grounds to reopen alpha. Alpha closes on plumbing and blinding,
not on a transfer effect.

---

## The arms

Arms A, B, D are the alpha. Arm C is beta (H1-R01).

    Arm  Phase   Initial tests supplied          What the contrast establishes
    ---  -----   -----------------------------   ---------------------------------
    A    alpha   Fresh target probes             Whether transport beats simply
                                                 spending the same resources
                                                 locally
    B    alpha   Random compatible prior         Whether relevance selection
                 failure inputs                  improves on general reuse
    D    alpha   Relevance-selected prior        the H1 treatment
                 failure inputs
    C    beta    Probes from the same relevant   Whether ordinary source-task
                 source tasks, selected          similarity explains any benefit
                 WITHOUT conditioning on
                 failure

**Arm C is the one neither external reviewer proposed**, and Astra names its
absence "a real omission in my design." Without it, a win for D over A and B is
consistent with "these source tasks were simply similar and any probe drawn from
them would have helped."

## Reading the outcome, in Astra's wording

    D beats A and B     supports the tested retrieval policy's practical value
                        WITHIN the declared family and resource caps
    D also beats C      strengthens the case for FAILURE-SPECIFIC value
    D ties C            can still support useful test reuse; does NOT establish
                        that failure origin supplies additional value

That last row is the one to pre-commit to. It is a real and likely outcome, it
is not a null, and it would mean the programme has a useful retrieval mechanism
and no evidence for the thing H1 actually claims. Note it cannot be reached at
all until arm C runs in beta.

Two further cautions carried from the register: a reduction in solver conflicts
alone does not prove a semantic mechanism, and high variance alone does not
establish a null.

## What is transported

The **input only**. Its correct answer is recomputed by the **target** task's
oracle. The source task's expected answer is not carried across and is not
claimed to transfer.

Both external critiques assumed otherwise, and several of their objections
dissolve once this is fixed.

## Matching requirements

Match input counts, compatibility, structural properties and duplicate handling
across arms. Recompute every target label. Freeze retrieval before confirmation.
Charge acquisition, retrieval, labelling and execution to the arm that incurs
them. Give the fresh arm an equal allowance for fresh target probes.

If the pool cannot supply K distinct inputs, apply the predeclared shortfall
rule in EVERY retrieval arm and report actual counts.

## The mechanism measurement, which is better than the endpoint

For the first mechanism experiment, hold candidate enumeration order fixed and
measure directly:

- how many incorrect candidates the initial tests reject before full
  verification
- how much verification work is thereby avoided
- whether those savings exceed the extra testing cost

This addresses the proposed mechanism **without introducing SAT branching at
all**, which is what makes the adversarial review's headline confound
inapplicable to the alpha.

## Endpoint and inference

Solve fraction is the primary endpoint, timeouts included. Report uncertainty
and a predefined meaningful-effect threshold. High variance does not prove a
null; failure to reach significance does not establish equivalence. Solver
conflicts and decisions are **diagnostic** — fewer conflicts alone cannot prove
the mechanism.

## Substrate for the alpha

Bounded Boolean VM. 3-input tasks, exhaustive verification over all 8 inputs,
bounded typed grammar (input, constants, NOT, AND, OR, XOR), fixed seeded
enumeration. Z3 is an optional LATER adapter, cross-checked against exhaustive
small instances before it is trusted.

The eight-case alpha establishes correct plumbing. It does not establish useful
performance; that requires a separately calibrated frozen evaluation.

## Controls carried forward from the reviews, with their status

    Isomorphic noise witness      H1-R04, CONDITIONAL ON AN SMT BACKEND ONLY.
                                  Not assumed to preserve solver behaviour or
                                  to destroy useful information; a proposed
                                  control must establish its bounded meaning
                                  before use. No SMT-specific gate is imposed
                                  on the VM experiment.
    Solver branching telemetry    H1-R04, same condition. Paired solver seeds,
                                  input/constraint-order perturbations and
                                  formula/decision/conflict telemetry.
    Charge retrieval fully        ADOPTED without reservation.
    Freeze retrieval pre-confirm  ADOPTED without reservation.

## Deferred to its own experiment

Gemini's agent-mediated transport — an LLM generalising a concrete failure into
an abstract invariant before injection — is a **different intervention** with
its own confounds, chiefly that extra prompt tokens can favourably perturb
attention independently of their content. If run, it needs the same model and
prompt receiving no history, matched control history, and relevant failure
history, and any proposed hard constraint must be verified against the target
specification or else retained only as a search suggestion.

It is not part of H1's alpha and a result from it would not be a result about
H1 as stated.
