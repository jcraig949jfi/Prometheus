# Finding: the search budget is declared, not enforced

**Found:** 2026-08-25, in the MDE pilot, before A0 was scored.
**Severity:** invalidates the `UNRESOLVED_WITHIN_BUDGET` class as currently built.
**Status:** recorded, not patched. A0 ran as frozen.

## What happened

Both of the MDE pilot's two failures were `UNRESOLVED_WITHIN_BUDGET` items, and
neither was a reasoning failure. The assessors simply enumerated the entire
stated domain, straight past the 200,000 search budget:

- `MDE_PILOT-0004` swept `[1, 504120]` and reported the counterexample at
  n = 230631.
- `MDE_PILOT-0009` swept `[1, 337343]` and explicitly noted in its own record
  that `max_search_size 337343 exceeds the 200000 cap`.

They disclosed the overrun honestly. Nothing stopped them, because nothing could:
`BUDGET_SEARCH_SIZE` lives in a prompt, and a prompt is not a sandbox. Half a
million Collatz stopping times is under a second of CPU.

## Why this breaks the class

`UNRESOLVED_WITHIN_BUDGET` was constructed on the premise that the generator
enumerates under a budget the player does not have. That premise is false as
implemented. The generator's advantage was never real; it was merely requested.

So the class does not measure what it was built to measure. It does not test
whether an agent distinguishes "I could not decide this" from "true" or "false".
It tests whether an agent chooses to obey an unenforced limit — a compliance
measurement wearing a calibration measurement's clothes.

## The second, subtler problem

Scoring these items as wrong is itself questionable.

`MDE_PILOT-0009` returned `TRUE_BUT_INVALID_ARGUMENT`. The item's sealed record
says `truth_status: TRUE` and `argument_validity: INCOMPLETE` — the argument
generalises from a short sweep to a domain 80x larger. The assessor identified
the true conclusion *and* the unjustified generalisation, and named the right
step. Under the oracle's disposition map that scores as an error, because the
class asserts `UNRESOLVED`.

An assessor is being marked wrong for producing a more informative and equally
correct answer. That is a defect in the class definition, not in the assessor.

## What was NOT done

The class was not patched, the disposition map was not changed, and the item
was not rescored. A0 was already frozen (`FREEZE_A0.json`), and adjusting a
scoring rule after seeing which items it punishes is precisely the manoeuvre the
preregistration exists to prevent. The A0 report therefore carries the
preregistered number as primary and reports this class separately.

## What would fix it

Ordered by cost, not preference:

1. **A metered verifier.** Assessors call a harness-provided routine that counts
   evaluations and refuses past the cap, instead of writing their own loop. This
   is the only option that makes the budget real. It also makes verifier-call
   counting objective rather than self-reported, which fixes a second weakness:
   every count in A0 is an honour-system number, and the seats visibly disagreed
   about whether a JSON-parse check counts.
2. **Domains no laptop can sweep.** Push N past what brute force reaches. The
   generator then needs structure the player lacks, which is hard to arrange in
   elementary mathematics — the same wall that made this class carried by
   opaque iterated maps in the first place.
3. **Retire the class for the alpha.** Fold these items into
   `FALSE_BUT_HARD_WITHIN_BUDGET` and accept that alpha measures cost, not
   calibration. Cheapest, and honest, but it gives up the one class that tested
   whether an agent knows what it does not know.

Option 1 is the real fix and is the natural next milestone after A0.
