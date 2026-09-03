# Watson (2014) → Kouvaris (2017): the mechanism delta

Both sources RECOVERED. A mechanism comparison, not a genealogy.

## Shared substrate

A genotype seeds a developmental map whose interaction matrix is modified by past selection,
producing biased future phenotype generation.

## What Kouvaris ADDS — RECOVERED

| addition | RECOVERED basis | why it matters |
|---|---|---|
| **an unseen-environment test** | "how can natural selection favour developmental organisations that facilitate adaptive evolution in previously unseen environments?" | S1 evaluated within the family of trained targets; S3 evaluates on environments not selected for. Materially stronger protocol |
| **evolvability DEFINED as generalisation** | "equating evolvability to the way humans and machines generalise to previously-unseen situations" | converts a vague desideratum into a measurable quantity |
| **over-fitting as the named failure mode** | "conditions that alleviate over-fitting in learning systems successfully predict which biological conditions enhance evolvability" | supplies a theory of *when memory fails*, which S1 lacks |
| **noise as a control** | "training with noisy data (jittering)" ↔ "extrinsic noise in selection" | an intervention, not an observation |
| **connection cost as regularisation** | "a connection cost term ... favours connections of small values (L2) or fewer connections (L1)" ↔ "the reproduction and maintenance costs of the gene regulatory interactions" | a biological reading of a standard regulariser, and a second lever |

## What Kouvaris does NOT add — DERIVED

- **No new developmental dynamics** — the substrate is the same class of map.
- **No G4 generalisation** — unseen environments drawn from the *same structural regularity*
  remain within-distribution. Generalising to a new structural regularity is not demonstrated.
- **No recursion** — nothing makes the rule that updates `W` itself an object of selection.

## The delta in one line

> Watson 2014 shows that history is **stored** and biases future variation.
> Kouvaris 2017 shows **when that stored bias transfers and when it over-fits**, and names two
> concrete controls — noise and connection cost — imported from learning theory.

For Prometheus, S3 is the more actionable paper: it supplies the knobs. S1 supplies the object
the knobs act on.
