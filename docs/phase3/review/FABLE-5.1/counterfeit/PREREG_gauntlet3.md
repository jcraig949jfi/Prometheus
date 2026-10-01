# Preregistration: third reading of "fresh family", under the strict protocol

Reviewer: FABLE-5.1 (seat Dionysus). Written 2026-10-01, before the
registered run. Committed with gauntlet3.py and before any receipt exists.

## Why a third gauntlet

gauntlet2.py showed a plain library learner passing the section-19 protocol
when B is a kind never met. A second read-only reviewer, arguing as the
authors of the criterion, then gave the reply they would give. Section 18
speaks of "genuinely new causal families". Read step 3 as "family B shares
no built component with history A", and the library learner fails: after a
history of other parts it gains nothing (the wrong-history arm of that very
run, 323.5 tasks against 313.5 naive). On that reading the criterion would
need one clarifying sentence and no more.

The same reviewer found, in an unregistered probe on my first gauntlet's
permissive protocol, an organism with one developed bit that passes under
that reading. This run asks the question under the strict protocol: when
history and target share no built component, does the library learner fail,
and does anything with fixed inherited machinery pass?

## What is the same as gauntlet2.py

The world, the task code, acceptance after 8 passed tasks, the quality
measure, the meaning of the six conjuncts, the quorum (HOLDS at 22 of 24,
FAILS at 12 or fewer), the strict readings of cost, content and sham.
gauntlet3.py imports gauntlet2.py unchanged and records its hash.

## What is different

- HISTORY. Step 1 is one composite family A (depth 4), built from four
  history parts. Targets B, D and E are composite kinds built from four
  other parts. A world is redrawn until no pair of history parts covers any
  target's function class. So nothing built in development is a component
  of a target. What they share is the shape of the problem: each is a pair
  of parts.
- IRRELEVANT HISTORY. One shallow family (a single part): it shares neither
  component nor shape.
- RANDOM V. A naive organism whose developed state is set at random.
- SAVINGS FACTOR. 2 where gauntlet2.py used 4, in SAVINGS, REPEAT and the
  V-donor clause. A selector's saving is bounded by the length of its
  inherited list and it must also pass 8 confirmation tasks. On design
  seeds a factor of 4 held in 22 or 23 of 24 replicates, at the edge of the
  quorum; I chose 2 so the verdict does not hang on one replicate. Section
  19 names no factor.

## Organisms and expected verdicts (the CELLS table in the code)

| cell | what it is | expected | must fail |
|---|---|---|---|
| STRATEGIST | no library; inherits 32 complete orders in which to enumerate the same 660 templates: the plain order (in use at birth), one that tries the 81 pairs of parts first, 30 decoys that try them last; one index develops (5 bits): after each success it switches to the inherited order that would have reached that success soonest | PASS | none |
| BUILDER | the library learner of gauntlet2.py, unchanged | FAIL | SAVINGS |
| STATIC | STRATEGIST that never switches | FAIL | SAVINGS |
| EAGER | STRATEGIST that switches to the pairs-first order after any experience | FAIL | PROVENANCE |

For STRATEGIST the lesion sets the index back to its value at birth; the
sham swaps two idle decoy orders; rescue and V donor take the index of a
second individual that developed on a different composite family.

The gate of this run is PASS only if every cell returns its expected
verdict and every "must fail" conjunct is among its failing conjuncts.

## Design runs, disclosed

I ran the script on design seeds (bases 43, 47, 59, 61, 73, 79; nothing
written) and changed it twice after seeing output:

1. Development was first three composite families. STRATEGIST then held
   every conjunct except LIFECYCLE, which was true in 18 of 24 replicates:
   it pays about one naive search to learn which order to use, and over
   three targets that is repaid only most of the time. Step 1 of the
   protocol says one family A, and this organism needs only one, so
   development is now one family. I report the 18 of 24 in the review.
2. The pairs-first order first listed all 144 pairs of the twelve raw
   parts. I shortened it to the 81 pairs of the nine parts with distinct
   function classes. That roughly halves the selector's cost on a target.

On the final script STRATEGIST passed on all six design bases, with every
conjunct between 22 and 24 of 24. Several sat at 22 or 23. So I expect
PASS, and an INDETERMINATE on one conjunct would not surprise me. If that
happens the gate of this run is FAILED and the review reports the counts.

BUILDER failed SAVINGS in 0 of 24 on design seeds, as the second reviewer
said it would.

The registered base is 2026100124. It has not been run.

## What I will and will not say

- If STRATEGIST passes and BUILDER fails: "tightening 'fresh' to 'no shared
  component' removes the library learner and admits a selector over
  inherited search orders that carries five bits". So no single reading of
  "fresh" makes the protocol exclude fixed inherited machinery: each of the
  three readings is passed by one of three simple organisms (a selector
  over procedures, a library learner, a selector over search orders).
- If STRATEGIST comes back INDETERMINATE: I report which conjunct and its
  count, and say the third reading resists this counterfeit at this margin.
- If BUILDER passes: the second reviewer's rebuttal is wrong on my own
  evidence, and I say so.
- Nothing about real substrates. One author, one toy world, designed
  organisms: C0 and I1 in my package's terms.
