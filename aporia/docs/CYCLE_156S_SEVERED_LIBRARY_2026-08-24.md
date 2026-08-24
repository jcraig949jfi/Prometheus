# CYCLE 156-S — Apollo v2 severed Hephaestus's library, and it is still there

The load-bearing joint was never "can Hephaestus mint a type-compatible primitive." It is that
**Apollo v1's instruction set and Hephaestus's primitive library are the same 25 functions**, and the
v2 blackboard rewrite dropped all of them.

    Apollo v1 PRIMITIVE_CATALOG (apollo/archive/v1/src/genome.py) : 25
    Hephaestus forge_primitives (agents/hephaestus/src/...)       : 25
    INTERSECTION                                                  : 25
    in v1 but NOT in forge                                        : NONE

Not similar. Identical.

## Three of the four unsolved categories already have a primitive

    all_but_n          -> all_but_n            def all_but_n(total, n): return total - n
    temporal_ordering  -> temporal_order
    consistency_check  -> check_transitivity / solve_constraints
    vacuous_truth      -> NO MATCH

At 155-S I reported that **no operator in the 27-op registry computes an arithmetic difference**, and
called `all_but_n` a genuine capability gap. That was true of *Apollo v2's registry*. It is false of
the program: the operation exists, is three lines, and has existed since v1.

## Why this invalidates the authorised experiment

The proposed first coupling was: give Hephaestus the failure evidence for `all_but_n`, let it mint a
primitive, hand the artifact to Apollo, measure ΔE.

**Hephaestus would not synthesize anything.** It would retrieve `all_but_n` from its own library.
ΔE would move by the predicted +4.17%, the winning pipelines would contain the primitive, and
provenance would check out — every acceptance criterion satisfied by an event that is **not vocabulary
synthesis under failure pressure**. It is reconnection of a severed dependency.

That is the `temporal_ordering` counterfeit one level up, and it would have been much harder to spot
after the fact than before.

## The corrected experimental ladder, with intervention classes fixed in advance

Using the operator's own decomposition — ΔE = ΔE_parse + ΔE_reason + ΔE_routing + ΔE_other — with
one class added that the evidence forces:

**1. ΔE_port — `all_but_n`.** Adapt an existing, already-tested forge primitive to the blackboard
type signature. Cheap, and it tests the *coupling machinery* end to end: type adaptation, guard
composition, enumeration, provenance. Predicted +4.17%. **Labelled PORT. It is not evidence of
synthesis and must never be reported as such.** This is the correct first experiment because it
exercises every mechanical part of the loop while claiming nothing about acquisition.

**2. ΔE_reason — `vacuous_truth`.** The *only* unsolved category with **no corresponding forge
primitive**. It is therefore the only place where Hephaestus must actually synthesize rather than
retrieve. **This inverts my 155-S recommendation**, which argued against `vacuous_truth` on the
grounds that its implementation risks encoding the answer pattern. That risk is real and now has to
be managed rather than avoided, because it is the only honest synthesis target available.

**3. ΔE_parse — `temporal_ordering`.** The deliberately-bad positive control already identified.
Note it *also* has a forge primitive (`temporal_order`), so it is doubly contaminated as a
demonstration and doubly useful as a control.

## The negative control this makes available

Port a forge primitive for an **already-solved** category — `check_transitivity`, where `transitivity`
already scores 10/10. **ΔE must be exactly 0.**

If it is not zero, then adding *any* op to the pool moves the ceiling, which would mean the assay is
measuring search dynamics rather than expressivity, and every ΔE reported so far is suspect. This is
cheap, it runs on existing artifacts, and it should gate the whole ladder.

A second, stronger variant: add a **type-compatible no-op**. Under a genuinely exhaustive enumeration
over the pool, a semantically null operator cannot raise the maximum. Any movement is a search-budget
artifact.

## The salvage reading

This is the charter's shape, exactly: **two assets whose coupling was severed by an architecture
rewrite, where the claim that justified the original coupling is irrelevant to the reconnection.**
Apollo v1 died as an approach. Hephaestus's library did not die with it. Apollo v2 is better in every
respect except that it lost 25 working operations, and 15 of its 20 unsolved tasks correspond to
three of them.

Nothing here required believing anything about v1.

## Self-identified weaknesses

- The name-level match is exact, but I have **not** verified the *implementations* are identical
  between `genome.py` and `forge_primitives.py` — only that the names and arities line up. A shared
  vocabulary with divergent semantics would change the port cost.
- Whether `all_but_n(total, n)` can be adapted to the blackboard `BlackboardState -> BlackboardState`
  signature is **untested**. The forge primitives are typed functions over values; blackboard ops are
  state transformers. That adapter is the real port cost and it is unmeasured.
- `consistency_check` maps to `check_transitivity`/`solve_constraints` by my reading of what the
  category requires, not by execution. Weaker than the `all_but_n` and `temporal_order` matches,
  which are name-exact to the category.
- I have still not executed `synth` (30) or `cross_tier` (20); the 100/120 accounting remains
  Apollo's for 50 of 120 tasks.

## Falsifier

Implementations diverging between v1 and the forge despite matching names; `all_but_n` proving
un-adaptable to the state-transformer signature without effectively rewriting it (in which case the
port *is* a mint and the classification changes); or the `check_transitivity` negative control
returning ΔE ≠ 0, which would invalidate the assay.

## Terminal

**CYCLE 156-S: EXPERIMENT CORRECTED BEFORE IT RAN.** The authorised first coupling would have
produced a counterfeit positive. The corrected ladder is port → negative control → synthesis, with
`vacuous_truth` now the only honest synthesis target and `all_but_n` demoted to a mechanical
end-to-end test of the loop.
