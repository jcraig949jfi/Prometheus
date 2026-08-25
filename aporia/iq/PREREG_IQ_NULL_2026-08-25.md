# PREREGISTRATION — IQ-NULL

**Assay validity. This gates everything downstream, including IQ-PORT-1's own
ΔE = +0.0416667.** Written 2026-08-25 after IQ-PORT-1 committed at `28761a6f`, before
any IQ-NULL measurement is taken. Same frozen evaluator:
`10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae`.

Doctrine §8: *"type-compatible no-op + already-solved-category port. Both ΔE exactly 0.
Non-zero means the assay measures search dynamics rather than expressivity and every ΔE so
far is suspect."*

---

## The two null interventions

    null_noop              reads problem_text, writes quantities, DOES NOTHING at runtime.
                           Already written and frozen in aporia/iq/port_ops.py at 28761a6f,
                           before this preregistration — deliberately, so it cannot be tuned
                           to the result.
    op_check_transitivity  PORT of fp.check_transitivity (forge_primitives.py:68), a
                           Warshall closure. reads relations, writes transitive_closure —
                           an exact match for the declared slot type dict_str_set_str.
                           Targets `transitivity`, which is ALREADY 10/10.

## The risk this step actually probes, named before measuring

Writing `null_noop` for IQ-PORT-1 surfaced something I did not anticipate and have not yet
measured: **the enumeration grammar keys on DECLARED writes, not on runtime behaviour.**
An operator is enumerable iff every slot it reads has been written by an earlier operator's
*declaration*. IQ-PORT-1 measured that **no operator in C writes `quantities`**.

`entity_counter` declares `reads = [names, relations, quantities]`. If that audit is right,
`entity_counter` **cannot appear in any valid ordering over C at all** — it is dead in the
enumerated space, and the 1,737,000-pipeline O1 result never contained it.

`null_noop` declares `writes = [quantities]` while writing nothing. It therefore **unlocks
`entity_counter` into the enumerable space without changing any runtime state.** If any
pipeline in that newly-reachable region beats 0.8333, then ΔE of a literal no-op is
positive, and E is measuring declared-type reachability rather than expressivity.

That is the honest statement of what could go wrong, and it is the reason this step is not
a formality.

## Predicted readings

    N1  null_noop footprint over all 120 tasks = 0 tasks. No state changes anywhere.
    N2  entity_counter is UNREACHABLE in the enumeration grammar over C.
        Predicted set of unreachable ops in C is computed and reported, not asserted.
    N3  adding null_noop CHANGES the reachable operator set — entity_counter becomes
        enumerable. I expect this to be true and it is not, by itself, a failure.
    N4  ΔE(null_noop) = 0.000000 EXACTLY, despite N3.
    N5  ΔE(op_check_transitivity) = 0.000000 EXACTLY.
    N6  op_check_transitivity's footprint contains no task that is currently unsolved.

**N4 is the risky one and I am not confident in it.** N3 supplies a concrete mechanism by
which it could fail. Stating that here rather than after the fact is the point of a prereg.

## How ΔE is obtained for a null — different from IQ-PORT-1, and stronger

IQ-PORT-1 used exhibited-lower-bound ∧ footprint-upper-bound. For `null_noop` the footprint
bound is decisive if N1 holds: **an operator that alters no state on any task cannot change
the behaviour of any pipeline containing it**, so ΔE ≤ 0/120 = 0 and ΔE ≥ 0 trivially.

**But that argument is only valid if reachability is held fixed, and N3 says it is not.**
So the bound alone is insufficient and the newly-unlocked region must be searched directly:

> Enumerate every valid ordering over subsets drawn from the previously-unreachable
> operators plus `null_noop`, closed with every scorer tail used by O1, and report the
> maximum accuracy attained. ΔE(null_noop) = max(0, that maximum − 0.8333).

This is tractable precisely because the unreachable set is small. **If it is not small, the
run reports the size and PARKs rather than sampling a prefix of it.**

For `op_check_transitivity`, the same two-part treatment: footprint, plus a bounded
enumeration over orderings that contain it.

## Terminal states — exactly one, and they partition

    ADVANCE   N1 and N4 and N5 all hold. The assay measures expressivity. IQ-PORT-1's
              ΔE stands. Next rung: TRANSFER-1's generator (see below).
    REDESIGN  N4 or N5 fails. E is contaminated by declared-type reachability. IQ-PORT-1's
              +0.0416667 is SUSPENDED, not retracted, pending a corrected assay in which
              reachability is held fixed across the C / C∪{p} comparison.
    PARK      the unreachable set is too large to enumerate exhaustively at this budget.

Note the asymmetry, which is deliberate: a REDESIGN here does **not** retract IQ-PORT-1's
measurement — the exhibited pipeline and its knockouts are direct observations and survive.
What a REDESIGN kills is the interpretation of that number as a *ΔE over a max*.

## Ladder consequence already fixed by IQ-PORT-1, restated so it is not lost

canary `vacuous_truth` cannot discriminate a synthesised operator from a constant (a
fixed-prefix "Yes" scorer takes 5/5). **SYNTH-1's reading has no valid instrument.**
Whatever IQ-NULL returns, the next constructive step is TRANSFER-1's frozen G-heldout
generator, not the mint.
