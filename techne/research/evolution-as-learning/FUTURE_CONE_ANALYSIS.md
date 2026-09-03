# Future Cone Analysis

The directive proposes a candidate term and asks whether the historical mathematics supports it.
This document argues it **partly does, and not yet enough to adopt**.

## The candidate object

    Q( next_state | current_machine, variation_operator, environment/history )

with the *future cone* being the distribution over states reachable under a defined variation
process and resource horizon.

## What the recovered mathematics licenses

RECOVERED from S1: the developmental map `P(t+1) = P(t) + tau_1 sigma(B P(t)) - tau_2 P(t)` with
`P(0) = G` means the phenotype reachable from a genotype is a deterministic function of `(G, B)`.
Mutation perturbs `G`. Therefore:

    the distribution of adult phenotypes obtainable from mutations of G
        is a function of B

and `B` is modified by past selection via the Hebbian term. **So in S1 the object exists, is
well-defined, and is provably history-dependent.** That much is not speculation.

## The distinction the directive cares about — and it is real here

    movement through state space      x_t changes
    change in the transition law      Q_t( next | x_t ) changes

S1 delivers the **second**. This is the substantive point and it is RECOVERED, not analogical:
selection does not merely move the population, it edits `B`, and `B` is a term in the generator
of future phenotypes. History modifies the generator.

## The critical unanswered question — the same-probe test

Directive §6 asks: can two systems expressing the **same current phenotype** generate **different
phenotype distributions** under identical subsequent perturbation?

**In the S1 formalism the answer is trivially yes by construction** — two organisms with
different `B` but a `G` chosen so that `P*` coincides will have different mutational
neighbourhoods. That is a property of the equations, not a finding.

**What is NOT in the recovered text is a measurement of it.** S1 does not report a controlled
experiment holding `P*` fixed and varying `B` by history, then measuring the offspring
distribution. Nor does S3. This is the missing experiment, and it is the highest-value one this
programme identifies — see `SFE_EXPERIMENT_CANDIDATES.md`, E1.

## Should `future cone` enter canonical Prometheus language?

**Not yet. DERIVED recommendation: NO.**

Three reasons:

1. **One lineage is not a unification.** The object is recovered for Watson. For Toussaint and
   MVG it rests on RECALLED descriptions of sources I could not fetch.
2. **`Q` may be an incomplete state description.** If `B` carries history that two systems with
   identical current `Q` do not share, then `Q` is not sufficient and the term would hide the
   very thing Prometheus is hunting. This is testable and untested.
3. **A term adopted before its unification is demonstrated becomes vocabulary that argues for
   its own thesis.** The cartography campaign already produced one instrument that measured its
   own vocabulary rather than the world; this is the same hazard in the theory layer.

Use it as a working label in this directory. Do not export it.

## Meta-evolvability — SPECULATIVE

The directive asks whether evolution can modify `Q` such that later modifications of `Q` become
easier. **Nothing in S1–S3 addresses this.** The Hebbian update modifies `B`; no recovered
mechanism modifies the *rule* that modifies `B`. Recursion depth in the recovered lineage is
**one**. Any Prometheus claim of meta-evolvability from this lineage would be unsupported.
