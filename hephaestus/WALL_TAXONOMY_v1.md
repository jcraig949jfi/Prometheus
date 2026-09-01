# Wall taxonomy v1 — preregistered mechanism families (Addendum 4, Q4)

**Frozen 2026-09-01, before specimen 3.** The purpose is to make a negative result legible:
*"No OPERATOR gap was found across the preregistered families F under frozen basis
A2-GENERIC-v1 and depth/budget Y"* is a finding; *"we tried N walls"* is not.

Every wall that enters the funnel is assigned to exactly one family **at preregistration**, from
the wall's *probe description*, before its closure test runs. The family is recorded in the packet
(`CLOSURE_TEST.family`). A family counts as *covered* once at least one wall in it has a completed
gauntlet with a recorded `CLOSURE_MARGIN`.

| # | Family | What the target mapping is over | Covered by |
|---|---|---|---|
| F1 | **Scalar predicate** | a fixed small tuple of scalars → bool/int | — |
| F2 | **Quantified predicate** | (quantifier, domain cardinalities/counts) → bool | MINT-0001 vacuous_truth — margin **A1** |
| F3 | **Relational / global invariant** | a finite relation or graph → bool (acyclicity, connectivity, functionality…) | MINT-0004 consistency_check — margin **A2_ONLY** |
| F4 | **Recursive / transitive property** | closure or fixpoint of a relation → set/relation | — (MINT-0004's witness uses the closure but its target is F3) |
| F5 | **Stateful / temporal property** | a sequence of states or events → bool/value depending on order and history | — |
| F6 | **Constructive transformation** | input structure → output structure (not a verdict) | — |
| F7 | **New state / memory** | a mapping that cannot be computed from the visible state without an auxiliary store or unbounded recursion | — |

Rules:
- Assign the family from the probe, not from the implementation you later find.
- One wall per family is enough to *cover*; heterogeneity beats count.
- If every family closes at margin ≤ A2 under A2-GENERIC-v1 and depth 3, the Forge's premise —
  that Prometheus's observed walls include missing primitive reasoning operators — comes under
  review as the finding, per the operator's ruling.
- Changing the family list is a versioned intervention (v2), reported against all prior assignments.

**Specimen 3 (to be assigned at preregistration, from its probe):** Aporia Q045 "unreachable class".
