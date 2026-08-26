# Next milestones, after external review (2026-08-26)

Ordering adopted from the review, with refinements noted where I disagreed.
**No live four-agent play until milestone 3 produces measurable cost headroom.**

## 0. Fingerprint control — RESOLVED, PASS

The reviewer's negative control was correct and my earlier PASS was wrong. Zero
above-chance predictability is the wrong standard, because legitimate
mathematics predicts where mistakes live. The right question is whether the
planted step can be found *without* checking the mathematics.

`fingerprint_audit.py` now runs the classifier over representations that keep
surface form and destroy content: digits masked, digits shuffled, and a skeleton
in which every word and numeral is collapsed. A positional baseline (step index
alone, no text) sits alongside them.

First run of the control: **FAIL**. The lift fully survived digit masking, and
the skeleton scored *higher* than full text — 24.2% against 17.2%, chance 9.4%.
None of the residue required arithmetic. Per-family breakdown localised it to
M4 (100%), M9 (73%) and M7 (67%) with all content destroyed. Cause: those
families targeted the only step of their shape in the derivation, so a reader
could pin the planted step by naming its *kind*. The same defect I had fixed for
congruence and instantiation, still present for inequality and identity steps,
and made worse by a 0.75 keep-probability that sometimes left a single instance.

Fixes applied, in the order the control forced them:

1. random tie-breaking in the argmax — it had been resolving ties to the first
   step, smuggling a positional prior into a text measurement;
2. two instances of every targetable kind, none dropped;
3. base and engine steps shuffled into the body — the second control run showed
   `position_only` scoring exactly what full text scored, so the entire residue
   was positional, not lexical.

Final control: full 4.7%, digits_masked 3.1%, skeleton 3.1%, position_only 6.2%,
against chance 5.4%. Every representation at or below chance. **PASS.**

Generator pilot PASS after the change; cycle simulation separation holds
(bypasses 16.67 vs 8.00, p 0.007) with the prose grep at 0%.

## 1. Metered verifier — MANDATORY before any v0.2 A0

Self-reported call counts are not an instrument. The v0.1 A0 seats openly
disagreed about whether a JSON-parse check counts, and several re-ran an
identical script purely to persist a log and counted it.

The harness owns all chargeable evaluation. Seats call:

```
evaluate(claim_id, candidate_input)     # is the proposition true at this point
symbolic_check(claim_id, expression)    # a symbolic relation about the claim
solver_query(claim_id, encoding)        # a solver call about the claim
```

**Chargeability is defined at the interface, not by inferring effort.** A call is
chargeable because it requests information *about the target claim*. Parsing
JSON is not chargeable; parsing that is itself part of the mathematical oracle
would be. This removes the judgement call the v1 seats were forced to make and
disagreed on.

Budget state is hidden except remaining credits. Past the cap the API refuses.
That is what makes `UNRESOLVED_WITHIN_BUDGET` a real class rather than a test of
whether a seat chose to obey an unenforced limit.

## 2. Navigation-shaped generator

The central diagnosis from review, and I agree: **the experiment is currently
measuring the wrong difficulty.** The seats are not struggling to determine
truth — they were unanimously correct at a median of two verifier calls. What we
want to know is whether graph state helps them choose *which falsification
operation to spend next*.

So do not harden by making the mathematics harder. That risks an ambiguous
oracle, which is worse than an easy one. Harden the **search geometry**: items
where truth stays mechanically crisp but several falsification routes exist at
wildly unequal cost. A target item admits, say:

- a 50,000-point enumeration,
- a 2,000-point boundary search,
- ~100 solver calls,
- one symbolic invariant check.

A0 spends thousands. D, reading accumulated attack structure, tries the
invariant first. *That* is navigation, and it creates cost headroom without
requiring the model to be bad at mathematics.

Each generated item records its full route menu with per-route cost in the
sealed record, so the achievable cost floor is known and the gap between what a
seat spent and what was available becomes the measurement.

## 3. v0.2 A0, under the amended objective

Registered in `PREREG_A0.md` Amendment 1: two co-primary outcomes — disposition
correctness, and verifier cost conditional on a correct disposition — with
capped EVC demoted to a secondary risk summary.

**My one substantive disagreement with the review's phrasing.** "Among correct
dispositions, D must reduce cost versus C" conditions on a post-treatment
variable, which is a collider. If D changes *which* items are answered
correctly, the two correct-sets are not comparable, and D could look cheaper by
newly solving cheap items or newly failing expensive ones. The amendment
therefore defines the cost contrast on the **intersection** — items correct
under both conditions — reports the intersection size, declares it UNPOWERED
below 20 items, and reports the two non-overlapping sets as a finding in their
own right rather than absorbing them.

Non-inferiority margin on correctness fixed at 5 percentage points, registered
before any data.

## 4. Sibling pairing on latent structure

Adopted from review: generate A/B/C/D instances from a shared hidden latent
specification — same difficulty and failure geometry, different constants,
witnesses, surface forms and hashes. That recovers most of the paired-design
variance reduction without letting D retrieve the exact A item.

**Refinement I would add:** the play pool must draw from latent structures
*disjoint from every evaluation structure*. If play and evaluation share a
latent structure, D can retrieve a played sibling's geometry — which is arguably
the transfer we want to measure, but it makes memorisation and navigation
indistinguishable. Disjointness at the latent level is what keeps them separable.

Condition-specific siblings are generated *after* condition assignment, from a
frozen latent generator.

## 5. Open-attack invention probe

Before building the epoch runner, run single Red agents with: a valid base
derivation, the rulebook, the existing defenses, **no mutation API, and no list
of attack families**. Red modifies the derivation however it likes within a
sandboxed mathematical interface.

Classify the result post hoc: KNOWN / COMPOSITION / NOVEL, by behavioural
equivalence — which defenses catch it, which semantic relation it breaks, what
transformations reproduce it. The LLM does not get to declare its own attack
novel.

**Refinement I would add:** "NOVEL" defined as "no current defense catches it"
conflates novelty with gaps in our coverage. The classification needs a
**reference battery frozen before the probe**, so novel means "not reducible to
M1–M12 by behavioural equivalence" rather than "nothing we happened to build
catches it."

This is the closest available test of the actual thesis: given an existing
defense surface, can an unconstrained agent construct a valid-looking false
derivation that bypasses it without being handed a vocabulary? The scripted
simulation cannot answer that, by construction.

## Status of the scripted cycle simulation

Kept epistemically quarantined. It shows the arena can implement adaptation when
adaptation is scripted, and that the cycle metrics can distinguish a real loop
from a fake one. It does not show that an agent can invent the thing worth
remembering.
