# Toussaint and Watson: is there a common object?

## STATUS WARNING

**The Toussaint primary source was NOT recovered** (source ledger, N2 — OpenAlex search returned
unrelated works). Everything below about Toussaint is RECALLED and is **not evidence**. HC-T01
owns that lineage. This document exists to state the question precisely, not to answer it.

One RECOVERED anchor: S1 cites "Toussaint & von Seelen 2007" among the works establishing that
developmental biases "can, in principle, be shaped by past selection" — so the two lineages are
connected in Watson's own reference frame.

## The two mechanisms as stated

    Toussaint (RECALLED)
        variation operator / representation changes
            -> the distribution of offspring around a parent changes
            -> exploration is redirected

    Watson (RECOVERED)
        selection history modifies the interaction matrix W
            -> the developmental map from genotype to phenotype changes
            -> the distribution of phenotypes reachable by mutation changes

## The candidate common object

Both, if the RECALLED description of Toussaint is right, modify the same downstream quantity:

    Q( next phenotype | current genotype, variation operator, developmental map )

They modify it at **different points in the pipeline**:

| lineage | what is modified | what stays fixed |
|---|---|---|
| Toussaint (RECALLED) | the variation operator / the encoding it acts on | the map from encoded state to phenotype |
| Watson (RECOVERED) | the genotype→phenotype map `W` | the mutation operator on `G` |

DERIVED: these are **plausibly two routes to the same object, not the same route**. Watson holds
mutation fixed and moves the map; Toussaint moves the operator. If both are projections of `Q`,
then the unifying claim is not that they are the same mechanism but that **`Q` is the thing
Prometheus should be measuring**, and the mechanisms are alternative handles on it.

## When the unification is legitimate — and when it is not

Legitimate if, and only if:

1. Both can be written as changing a *distribution over next states*, with the same support.
2. The composition order does not matter for what is being claimed — otherwise `Q` hides the
   fact that operator-change and map-change interact.
3. Neither mechanism requires state not present in `Q` (e.g. a history term that makes the
   process non-Markov in `Q`).

Condition 3 is where I expect the unification to fail, and it deserves stating: Watson's `W`
carries accumulated history. If two systems with the *same* current `Q` but *different* `W`
behave differently under further selection, then `Q` is an incomplete state description and the
unification is premature. **That is exactly the same-probe question** — see
`FUTURE_CONE_ANALYSIS.md`.

## Verdict

    UNVERIFIED. The common object is a well-posed candidate, not a result.

Do not adopt `Q` into canonical Prometheus language on this document. It earns adoption only if
(a) the Toussaint source is recovered and the RECALLED description survives, and (b) the
same-probe test distinguishes or fails to distinguish `Q` from `W`.
