# IQ-NULL — RESULT: ADVANCE. The assay survives, and the reason it could have failed is real.

Preregistration `aporia/iq/PREREG_IQ_NULL_2026-08-25.md`, committed **de27e115 before any
measurement**. `null_noop` itself was frozen one commit earlier still (28761a6f), so it could
not be tuned to the result. Evaluator hash re-checked at run time and matched. Raw ledger:
`aporia/iq/RESULT_IQ_NULL.json`.

---

## HEADLINE

    ΔE(null_noop)             = 0.000000   EXACTLY
    ΔE(op_check_transitivity) = 0.000000   EXACTLY

Both nulls read zero. **The expressivity assay measures expressivity, not search dynamics,**
and IQ-PORT-1's ΔE_port = +0.0416667 stands as a ΔE over a max rather than being suspended.

## The mechanism that could have broken it — and did fire

The preregistration named a specific way this step could fail, before it was measured:
**the enumeration grammar keys on DECLARED writes, not on runtime behaviour.** Confirmed:

    N1  null_noop footprint over all 120 tasks              0 tasks. It changes nothing.
    N2  entity_counter UNREACHABLE in the enumeration over C   TRUE
    N3  null_noop CHANGES the reachable operator set           TRUE — it unlocks entity_counter
    N4  ΔE(null_noop)                                          0.000000

**N3 is true.** An operator that writes nothing at runtime, but *declares* a write, genuinely
enlarged the enumerable program space. The assay was exposed to exactly the confound the prereg
named — and the newly-reachable region tops out at **0.7333**, a full 0.1000 *below* the 0.8333
ceiling. So the unlock is real and the gain is zero. That is a much stronger result than a null
that was never at risk.

Scope, declared rather than implied: 56,880 evaluations. Region A = the ceiling body plus
`{null_noop, entity_counter}`, ≤24 orderings × 36 tails. Region B = **all 1,471 subsets**
containing both, plus up to 4 of the 14 other transformers, ≤8 orderings × 36 tails. Every
subset in that range is visited; nothing is sampled. **Not covered:** subsets with 5+ extra
transformers that are not supersets of the ceiling body.

## Three of the 27 registered operators are structurally dead

Measured by a fixpoint over declared reads and writes — the enumerator's own validity rule
lifted to a closure, not a grep:

    entity_counter        reads [names, relations, quantities]   — `quantities` has no producer
    evidence_updater      reads [hypotheses, evidence, probabilities] — `hypotheses`, `probabilities` have none
    distribution_reducer  reads [probabilities, evidence]        — `probabilities` has none

**None of the three can appear in any valid ordering over C.** They are precisely the three
operators `blackboard_ops_v2.py` was written to create, in the 2026-05-25 rewrite that
reviewers convergently demanded: *"Rewritten in this module: evidence_updater, entity_counter,
distribution_reducer."* The rewrite landed; the slots that would feed it never got producers.

Consequence for the standing qualifier, which must now change wording:

> O1's "nothing in 1,737,000 type-correct pipelines beats 0.8333" was computed over an
> **effective pool of 12 transformers, not 15**. Three of the 15 were dead on arrival, and the
> O1 preregistration and findings do not mention it.

This is not a defect in the O1 result — it is a *sharpening* of it, and it is a concrete,
cheap, non-widening candidate for a later rung: giving `probabilities`/`hypotheses` a producer
would resurrect two more operators without adding a single new capability claim.

## The second null, and a vacuous reading caught

`op_check_transitivity` ports `fp.check_transitivity` (Warshall closure) into
`transitive_closure`, an exact declared-type match (`dict_str_set_str`), targeting
`transitivity` — already 10/10. ΔE = 0.000000 over 9,396 evaluations of orderings containing
it. **A port into an already-solved category buys nothing, as it must not.**

**The first run's footprint reading for this op was VACUOUS and is reported as such.** It was
computed as a set-difference of "tasks touched by [parse, op]" minus "tasks touched by
[parse]". The prefix already touches those tasks, so the difference was empty *by
construction*, and N6 — "the footprint contains no currently-unsolved task" — passed without
being able to fail. `LOOP_APORIA.md` P138: *a threshold outside the attainable range is a
non-measurement wearing a test's clothes.*

Replaced with a **differential** footprint that runs the prefix with and without the op and
diffs the states. Corrected reading:

    footprint 25 tasks:  canary:transitivity 10  ·  synth:nth_ranked 15
    overlap with the 20 unsolved tasks: 0

N6 now holds substantively, and the harness asserts `len(footprint) > 0` before reading it, so
the vacuous form cannot recur silently. The ΔE numbers were never affected — they come from
the enumeration, not the footprint.

## What this does and does not license

- IQ-PORT-1's +0.0416667 **stands** as a ΔE over a max. Not suspended.
- The assay is validated **as an assay**, over the 12-transformer effective pool and its
  grammar. Nothing here says ΔE deserves promotion to an abstraction *selector* — that is
  SELECTOR's question and remains open. Microscope, not yet compass.
- Two nulls at exactly zero is two data points. A null that reads zero because the instrument
  is insensitive would look identical; the N3 unlock is the reason to believe otherwise, since
  it shows the instrument's reachable space genuinely moved and the score did not follow.

## Ladder position

IQ-PORT-1 **ADVANCE** · IQ-NULL **ADVANCE**. Next by the ladder is SYNTH-1 — **but its target
has been measured to be unmeasurable** (`FINDINGS_IQ_PORT_1_2026-08-25.md`: a fixed-prefix
"Yes" scorer takes canary `vacuous_truth` 5/5). The next constructive step is therefore
**TRANSFER-1's frozen G-heldout generator**, built and frozen before any mint exists. The
ladder's step order is not being rewritten; the instrument for step 3 does not exist yet and
step 4 builds it.
