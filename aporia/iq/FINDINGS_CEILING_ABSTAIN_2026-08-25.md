# CEILING-UNDER-ABSTAIN — ADVANCE. The guessing is real, widespread, and inert.

Preregistration `aporia/iq/PREREG_CEILING_ABSTAIN_2026-08-25.md` committed **7a0e5b6d, before
any code existed**. `C` never edited; all variants harness-side.
Ledger: `aporia/iq/RESULT_CEILING_ABSTAIN.json`.

---

## Headline

    ceiling organism   0.833333 -> 0.833333      tasks lost: 0
    ported pipeline    0.875000 -> 0.875000      tasks lost: 0
    dE_port            +0.041667 in BOTH regimes — unchanged

**No task the ceiling organism wins is won by a guess.** Lexis's proven 0.8333 (`fcdc91af`)
stands as a capability number, and IQ-PORT-1's ΔE_port needs no regime qualifier after all.

**My preregistered C1 was FALSIFIED.** I predicted the ceiling would fall, on the reasoning that
`select_nth__g` guesses and is a member of the organism. It does guess — and it never has to,
on any task the organism wins.

## C4 — the last unresolved scorer, resolved. It is 9 of 10, not 8.

`score_by_extreme_number__g` was reported UNRESOLVED by SCORER-FIX because no probe fired its
guard. Resolved here: with `extreme_number='777 a'` the guard fires and it **emits
`candidates[0]`**. So the inventory is:

    GUESS candidates[0]   9 of 10 scorers
    abstain               1 of 10  (score_by_comparison__g)

The pathology is close to universal in this substrate — and, on this battery, entirely inert.

## The instrument bug I shipped and caught, in full

The first discriminator was **wrong**, and it produced a confident false verdict:

    v1 (removal):  emit == candidates[0]?  remove that candidate, re-run.
                   If it emits the new position 0, call it a fall-through.

    v1 RESULT:     ceiling 0.833333 -> 0.633333, 24 tasks lost,
                   verdict REDESIGN_PROVEN_CEILING_IS_PARTLY_GUESSING

**That reading was an artifact of the test.** Removing a *genuinely matched* candidate leaves
nothing to match, so the original falls through **by construction** and v1 misclassifies every
real match at position 0 as a guess.

Caught by execution, on the tell that 24 ≈ 25% of the 100 won tasks:

    lost tasks whose correct answer sits at candidate index 0:  24 / 24
    base rate of index-0 answers across the battery:            35 / 120 = 0.2917

    v2 (rotation): run the original, then run it on a ROTATED candidate list.
                   A genuine match tracks the VALUE and emits the same string from a new
                   position. A fall-through tracks POSITION. Nothing is removed, so a real
                   match is never destroyed by the probe.

    v2 RESULT:     ceiling unchanged, 0 tasks lost.

Had I not run that check, this document would be announcing that Lexis's proven ceiling is 24
tasks of luck. **The failure mode was a probe that perturbs the very thing it is measuring** —
and the give-away was a number suspiciously close to the base rate of the confound.

## Non-inertness — because my own verdict rule warned about it

I preregistered the null output: *an inert wrapper would leave the ceiling unchanged and read
ADVANCE, indistinguishable from a genuine no-dependence result.* With v2 losing **zero** tasks on
both pipelines, there is no positive evidence inside the main measurement that the wrapper does
anything at all. So a positive control was required and run:

    TRANSFER-1 mutants on NONDEGENERATE, plain pool -> rotation-wrapped pool
      M1_plus        0.1366 -> 0.0000
      M3_swapped     0.1366 -> 0.0000
      M6_half_total  0.1268 -> 0.0000

The wrapper reproduces SCORER-FIX's hand-written abstain variant exactly. **It is non-inert, so
the unchanged ceiling is a reading and not a no-op.**

## What this settles, and what it does not

**Settled.** For the known ceiling organism and the ported pipeline, on this 120-task battery,
removing every `candidates[0]` fall-through costs nothing. The scorers that win tasks win them
by matching values, not by position. ΔE_port = +0.041667 survives in both regimes.

**Not settled, and stated as scope rather than discovered later.** This rung scored **two
programs**, not a ceiling over all programs. Whether the *maximum over all type-correct
compositions* changes under abstention would require re-running Lexis's joint product BFS with
the wrapped pool. It is untouched here. The direction is still bounded — abstention can only
lose tasks — so the true abstain-regime ceiling is **≤ 0.8333**, and this result shows the known
optimum is still attainable, which pins it at exactly 0.8333 for that organism.

**Where the guessing does bite:** wrong rules. That is precisely the TRANSFER-1 finding — the
mutants collected a 1-in-4 floor — and it is why the pathology matters for *measurement* even
though it is inert for *capability* here. A substrate that pays wrong rules but not right ones
inflates every mutation battery run against it without moving a single headline.

## Scope

- Two programs, one battery, single seed, no intervals. Nothing dropped: all 120 tasks scored
  under both pools; exceptions count as wrong.
- The v2 wrapper is behavioural — it never reads the scorers' source — so it applies uniformly to
  all nine guessers without nine bespoke reimplementations.
- `C` untouched; the entire rung is reversible by not passing the variant pool.
