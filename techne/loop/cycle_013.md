# Loop Cycle 013 — 2026-08-21 (round 5 arrived; ran early)

**13 new tests, ladder suite 120 green.** Round 5 was the most consequential exchange yet:
it falsified a doctrine I had drafted the previous cycle, and answered all three round-5
questions with constructions sharp enough to build immediately.

## The correction that matters most

**My cycle-012 doctrine draft was WRONG in its strong form.** Counterexample, one line:
capability f(0)=1 on probe space {0} — any mechanism exact on the only nonempty slice IS the
capability. "Every rung has a cheaper exact slice" was a generalisation from five straw men I
happened to build, not a law.

The proposal is rewritten as **v2 — competitor-relative identification**: a battery identifies
a capability only relative to an EXPLICITLY ENUMERATED competitor class; finite observations
never uniquely identify a mechanism. The real universal danger is **observational equivalence
on the sampled support** (the lookup table on the tested set), which subsumes all five
instances and is harder to escape.

Two consequences adopted: the union of competitor agreement-regions is **not computable**
(Rice-style; contains program equivalence), so battery design has no completeness certificate
— what makes it scientific is declaring a threat model C<=k and reporting
**"not separated from C<=k"**, never "certified reasoning". And the CEGIS meta-battery: any
new cheap mechanism that passes becomes a new adversary and the battery grows.

## R8 (representation shift) — built to their design

Precomputed views = R4 in R8 clothing. Genuine R8 CONSTRUCTS the map: graph classes inferred
from neighbourhood structure (1-WL colour refinement), names and class sizes randomised per
episode, partition never supplied. Raw search on 60 nodes exceeds budget 10; the quotient has
3 nodes and answers. A catalogue-based selector holding a genuinely good view OF THE WRONG
GRAPH cannot help — the useful partition is one of Bell(|V|) possibilities.

**The generator had to become self-validating**: my first construction (ring over classes)
makes the graph complete multipartite, where 1-WL collapses to ONE colour. Not every class
structure is 1-WL-recoverable, so the generator now samples random class-adjacency and
REJECTS instances whose inferred partition does not match the planted one. A probe generator
that cannot certify its own ground truth is not a probe generator.

Their sharper twin also built: same object, two goals needing INCOMPATIBLE quotients (neither
refines the other — asserted), so a goal-blind canonicaliser is right for one and wrong for
the other. The map must be goal-conditioned.

## The three epistemic corrections (12.1-12.3)

- **Provenance, not consumed evidence.** A short-circuiting evaluator consumes e1 only; a
  predicate change over e2 leaves no trace. Certificates now record predicates and
  assumptions INVOKED -> dirty-set computation over evaluator components. Test: a cert whose
  evidence never changed is correctly dirtied.
- **Negative dependencies.** "No counterexample under query Q at snapshot v" consumes no
  evidence at all, yet database GROWTH invalidates it. Test: evaluator unchanged, DB grows,
  exactly the negative-dep cert goes dirty.
- **Justification vs influence.** Implemented their operational test literally. A claim that
  was merely INSPIRED by a retracted conjecture survives; one that verifies against its
  evidence is retracted. Otherwise one bad heuristic annihilates a lineage.
- **The constitutional bottom.** Fixed-bottom side taken, thin: the prediction/observation
  relation is immutable. Their regress separator executed — an amendment whose sole effect is
  to un-fail a recorded failure is REFUSED, while metric changes are accepted.

Second doctrine proposal drafted: `DOCTRINE_PROPOSAL_immutable_observations.md`.
