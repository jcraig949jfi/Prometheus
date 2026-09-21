# DRAFT AMENDMENT 2 to the frozen Campaign 1 preregistration: substrate eligibility of the local engine

DRAFT. NOT APPLIED. Dated 2026-09-21, written before any Campaign 1 data
exists. The operator's directive of 2026-09-21 requires that the engine's
status relative to the FROZEN substrate-selection rule be "explicitly
resolved" rather than "smuggled in as implementation"; this file states
the problem and the options and changes nothing by itself.

## READ FIRST: a blocker that outranks the question this file asks

Engine v0's improver is INERT. Across 10 seeds, every generation-8
artifact was byte-identical to the base image (`distinct_artifacts: 1`,
`identical_to_base_image: 10`), because the development distribution
contains only the three families the base already solves at 1.00. So
Campaign 1 on engine v0 would extract the base image, transplant the base
image, and measure a null by construction, at ANY lineage count.

The eligibility question below therefore does not need answering today.
It is logged now, pre-data, because the fix (giving the development
distribution headroom) changes the task mix, and the seat will not touch
that mix without the operator seeing this file first -- moving the task
distribution is exactly the move the frozen rule polices, and it must not
happen as a side effect of a bug fix.

## The frozen rule

"The fastest measured model whose frozen starting accuracy on the
Campaign 1 task distribution lies between 15% and 70%", applied to
benchmarked SERVED VARIANTS (checkpoint + quantisation + runtime +
inference settings) with economics from the frozen benchmark bundle.

## Why the local engine does not simply fall under it

1. It is not a served variant: there is no checkpoint, quantisation or
   inference setting, and the benchmark harness measures a model server.
2. Its starting accuracy is not a graded quantity. A deterministic code
   worker either has a family's solver or does not, so accuracy is a step
   function of the base image's coverage. MEASURED TODAY: base image
   0.75 on the uniform four-family mix (arith 1.00, sortkey 1.00, strops
   1.00, numtheory 0.00); positive control 1.00.
3. 0.75 is outside the 15-70% window. The seat will NOT adjust the task
   mix to move it inside: the operator's rule forbids tuning the
   distribution to force eligibility, and doing so after measuring would
   be exactly that.
4. Economics is not the binding constraint: ~0.40 s per 8-generation
   lineage, ~9,000 lineages/hour/core, so 64 lineages costs seconds.

## Options (the operator's choice)

A. AMEND the eligibility criterion for a non-model substrate, replacing
   the accuracy window with the two properties the window exists to
   guarantee:
     HEADROOM     the fraction of the Campaign 1 distribution the base
                  image cannot solve is >= 25% (today: 25%, one family
                  of four), so improvement is possible; and the base is
                  above the floor on the rest, so the assay is not
                  measuring noise;
     SENSITIVITY  a hand-written positive control lifts a fresh recipient
                  by at least delta (today: +0.25, far above delta = 3
                  points).
   Declared before any Campaign 1 data; the four families and the base
   image are already frozen and hashed.
B. KEEP the window and require the engine's distribution to satisfy it.
   This means choosing a distribution with more unsolved families -- a
   pre-data choice, but one the seat declines to make unilaterally
   because it is indistinguishable in form from tuning for eligibility.
C. DECLINE the engine as a Campaign 1 substrate. It remains a mechanics
   testbed (membrane, receipts, escrow, reset) and Campaign 1 waits for a
   benchmarked served variant from Nestor and Archaeon.

## The seat's lean and its reason

A, with B available if the operator prefers the window kept literal.
Reason: the window is a proxy for headroom and sensitivity, both of
which are measurable directly here, and the engine's advantages (offline,
seedable, byte-exact artifacts, provable resets, escrow beneath the
improver) attack the failure modes Campaign 1 exists to exclude. Against
A: a 25%-headroom substrate concentrates the entire experiment on ONE
missing family, so a Campaign 1 positive would be a narrow claim -- "an
artifact conferring one capability transfers" -- and the report must say
so. But note what the blocker above does to this argument: the ONE family
with headroom is the same family the improver cannot reach, so "25%
headroom" and "the improver is inert" are two faces of one design fault.
Fixing the second requires putting numtheory (or another unsolved family)
into the development distribution, which changes the base image's
starting accuracy on that distribution -- and that is precisely the
number the window governs. The two questions are coupled, and the seat
will not resolve either unilaterally.

A concrete proposal for when the operator answers: add a family the base
CANNOT solve to both the development and evaluation distributions,
declare the resulting starting accuracy pre-data whatever it turns out to
be, and let the eligibility criterion be headroom + sensitivity (option
A) rather than a window designed for graded model accuracy. The seat
would commit to that mix BEFORE measuring it, in a dated amendment, with
the measurement published whether or not it lands in 15-70%.
