# CAMPAIGN F — one pass, TERMINAL: **F3 MOSTLY-ATOMIC**. And the OEIS line closes here.

## What this campaign tested, and what it did not

The decisive check — *is any candidate relation actually unknown to mathematics* — cannot be run by
this loop. Campaign F ran the closest machine-executable proxy: does a candidate `op(A) = B`
**factor** through a third corpus sequence, i.e. does there exist `C` with `op1(A) = C` and
`op2(C) = B`, both exact over ≥ 20 terms, under the full 12-operator family?

A factoring relation is **implied by two simpler ones**. It is not atomic and is correspondingly
less likely to be interesting in its own right.

**This is a factorisation test, not a novelty test.** A composition can still be unnoticed. It gives
a triage ordering — atomic relations first — not a verdict on novelty. Scoped before the number
existed.

## Result

    non-trivial core:  568 records over 268 targets   (trivial-class operators excluded per Campaign V)
    factoring:          48 / 268  =  P = 0.1791   ->  F3 MOSTLY-ATOMIC
    ATOMIC:            220 targets

**Partition verified by enumeration:** 1,001 points over [0,1], coverage F3 200 · F2 400 · F1 401,
boundaries `0.199→F3`, `0.200→F2`, `0.599→F2`, `0.600→F1`. Census — the 0.20/0.60 cuts are
**materiality judgements**. Null check: nothing factors → P = 0 → F3; everything factors → P = 1 → F1.

**The margin is uncomfortable and I am not going to hide it.** P = 0.1791 sits **6 targets** from the
F2 boundary — 54 of 268 would have been 0.2015 and fired MIXED. Granularity is 1/268 = 0.0037, so the
distance is ~5.6 granularity units: resolvable, but this is the kind of margin my own gate-design
doctrine exists to flag. The branch is reported as fired, with its closeness attached.

## 220 atomic candidates

`aporia/search/CANDIDATES_ATOMIC.jsonl` — relations reached by a non-trivial operator, stated in
neither partner's title nor formula field, with a target neglected under all-source connectivity, and
**with no two-step chain through any of 266,122 corpus sequences under twelve operators.**

## The OEIS line closes here

**Tally, five campaigns and seven passes (P128–P134):**

    campaigns          S, T, U, V, F        terminal states   ADVANCE · ADVANCE · SURVIVES · KEEP · MOSTLY-ATOMIC
    sweep              230,694 sources x 12 operators, exact, seconds per run
    population         28,830 neglected sequences (all-source definition)
    ESTABLISHED        the method: exact operator search over a neglected population,
                       positive-controlled per operator, cheap and reproducible
    CANDIDATE          220 atomic non-trivial relations
    UNCHECKED          whether any is unknown to mathematics

**Has machine work hit diminishing returns? Yes, and this pass is where it happened.** Campaign F was
the last genuinely *different* check available. Everything remaining is either a rerun on axes
already tested three times — title, formula, population — or requires reading mathematics, which is
the one thing this loop cannot do. A sixth campaign would be motion.

## What would make the 220 actionable

**For James, in order of leverage:**

1. **Read twenty.** Sorted by exact term count, the top of `CANDIDATES_ATOMIC.jsonl` is where a
   specialist eye is worth most. Twenty rows would establish the base rate of "obvious" and settle
   whether the remaining 200 deserve time. That single number is worth more than any further sweep.
2. **OEIS comment and example fields** would close the last audit gap. Titles, formulas, programs and
   cross-references are on disk; comments are not. A relation stated in a comment still counts as
   unstated in every number above.
3. **The reviewer seat** — 23 reviews, 0 dispositions, ~50 passes. Five campaigns of self-adjudication
   with no external check remains the largest standing weakness in this line and in the loop.

## What the loop should do next, and it is not this

Not another operator family, not another audit, not the X-line. The loop's own decision-yield audit
found process improving while science stayed flat, and the cause was optimising past a success
criterion instead of applying it. That pattern would repeat here. The next campaign should come from
a different question entirely — and choosing it is the next allocation pass's job, not this one's.

## Campaign F TERMINAL: F3 MOSTLY-ATOMIC — the OEIS line closes
