# Preregistration: strict gauntlet for the recursive-sagacity criterion

Reviewer: FABLE-5.1 (seat Dionysus). Written 2026-10-01, before the
registered run. Committed with gauntlet2.py and before any receipt exists.

## Why a second gauntlet

The first one (PREREG.md, RECEIPT_gauntlet.json) had a selector and a
library builder pass the section-19 protocol. A read-only accuracy reviewer
then showed, by re-running the code, that the pass leaned on four choices
the protocol leaves open, each of which I had read permissively:

1. Budget. The construction budget was cut exactly where the naive and the
   developed organism differ (1 task for the selector, 4 for the builder).
   At other budgets the verdict changed. The figures I reported were the
   quality of a procedure after a truncated construction, not the cost of
   acquiring one.
2. Fresh. "Fresh family" meant a new seed of a kind already met, for C, D
   and E in every case, and for B too in the selector's case.
3. Content. Nothing in the code carried out steps 2 and 5.
4. Sham. The sham wrote to a cell nothing reads. It could not fail.

Also: several arms were the same computation (lesion reset the organism to
its naive state; rescue and the V donor restored the identical state), and
two of the four conjuncts were never shown able to fail.

Those are faults in my test, not in the reviewer's reading. This run fixes
each one and asks the question again: does a plain library learner pass the
protocol when every open choice is read strictly?

## Strict readings, fixed here

- COST. Savings are acquisition cost: tasks consumed until an acceptable
  procedure exists, with no budget cut-off. A candidate is accepted only
  after passing 8 tasks in a row (4 errors or fewer in 12 trials each).
  Lifecycle cost counts development as well and is compared with a naive
  organism working on the targets alone.
- FRESH. B, D and E are kinds never met in development, with distinct
  function classes that no template of depth 3 or less covers. C is tested
  twice: a fresh family of B's kind, and a narrower family inside B's class
  (first constant fixed).
- CONTENT. The harness clears every declared content store at steps 2 and
  5. Rule for what counts as content: anything that refers to particular
  tasks (constants, stimulus-response pairs). A template with free
  constants refers to no task and is machinery.
- SHAM. The sham removes as many library entries as the lesion, chosen
  among entries the target does not use. A random library of equal size and
  a wrong-history library are separate donors.
- SEPARATE ARMS. The lesion removes only the entries the target uses.
  Rescue material and the V donor come from a second individual with its
  own families and order.

## The world

Functions on the integers mod 17 built from ADD(c), MUL(a), SQR, CUB, INV.
A kind is a template; a family is tasks of one kind with random constants.
Development: families of four parts (depth 2, one constant each), drawn
from nine parts with distinct function classes. Targets: compositions of
two different history parts (depth 4, two constants).

Power maps commute, so a target can have more than one decomposition. A
replicate's world is redrawn until its labels are true as statements about
function classes: exactly one ordered pair of history parts covers B; no
pair of wrong-history parts covers B; no pair from the random library
covers B. This makes "the entries B uses" and "irrelevant history" mean
what they say. It is decided from the function tables alone, before any
organism runs.

Each replicate also draws the inherited order in which an organism
enumerates primitives, so no organism is favoured by one fixed order.

## The conjuncts (function `relations` in gauntlet2.py)

For one replicate, with costs in tasks:

| conjunct | relation |
|---|---|
| SAVINGS | 4 x developed cost of B <= naive cost of B |
| LIFECYCLE | development + B + D + E, developed < B + D + E, naive |
| U_TRANSFER | frozen U on a fresh family of B's kind and on the narrower family: 3.5 errors per task or fewer; what the lesioned line builds at the intact line's cost: 6.0 or more |
| NESTING | 2 x lesion cost >= naive cost; sham cost and rescue cost <= 2 x developed cost + 4; 4 x V-donor cost <= naive cost |
| PROVENANCE | 2 x wrong-history cost >= naive cost; 2 x random-library cost >= naive cost |
| REPEAT | the SAVINGS relation on D and on E |

A conjunct HOLDS if its relation is true in at least 22 of 24 replicates,
FAILS if true in at most 12, and is INDETERMINATE otherwise. The verdict is
PASS if all six hold, FAIL if any fails, INDETERMINATE otherwise.

Step 13 (another substrate) is not run. Step 10's U cross is reduced to one
comparison, the lesioned line's product at the intact line's cost, because
once U is frozen the host plays no part.

## Organisms and expected verdicts (the CELLS table in the code)

| cell | what it is | expected | must fail |
|---|---|---|---|
| BUILDER | fixed constructor; library of procedures that worked; tries the library, pairs of library items, then every template of depth 1 to 4 | PASS | none |
| SELECTOR | inherits every part and every pair of parts as a ready list; experience reorders it | FAIL | SAVINGS |
| STATIC | BUILDER that never writes its library | FAIL | SAVINGS |
| WASTEFUL | BUILDER whose development tests every candidate on 40 tasks | FAIL | LIFECYCLE |
| HIDDEN | BUILDER with an undeclared second copy of its library | FAIL | NESTING |
| BADSHAM | BUILDER, with a "sham" that removes the entries the target uses | FAIL | NESTING |
| MATURATION | BUILDER whose library becomes an inherited list of every part after any experience | FAIL | PROVENANCE |
| MEMORISER | stores the tasks it saw, in a world that leaks the target's tasks into development | FAIL | SAVINGS; and with the content reset skipped it must show savings in at least 22 replicates |
| OFFHISTORY | BUILDER in a world whose D and E use parts absent from its history | FAIL | REPEAT |

So each of the six conjuncts except U_TRANSFER has an organism or a world
built to fail it, and the content reset has one built to pass without it.
U_TRANSFER has no dedicated fire test; SELECTOR, STATIC and MEMORISER fail
it as a side effect.

The gate of this run is PASS only if every cell returns its expected
verdict, every "must fail" conjunct is among its failing conjuncts, and the
MEMORISER check holds.

## Design runs, disclosed

I ran the script on design seeds (bases 37, 41, 53, 67, 71, 83; nothing
written) while building it, and changed it after seeing output:

1. Acceptance after one passed task let wrong templates end long searches
   early. I raised it to 3 tasks, and then to 8 when templates covering
   only part of a kind still got through in 3 of 48 replicates.
2. "Wrong history" was first any four other parts. In 3 of 24 replicates
   those parts composed into B's function class by another route (INV and
   CUB commute). I added the rule that worlds are redrawn until the labels
   are true of the function classes.
3. The MEMORISER's lookup was too weak to recognise tasks it had stored. I
   replaced it with a best-match lookup.

On the final script BUILDER passed with all six conjuncts true in 24 of 24
replicates on each of the six design bases, and every fire test failed its
conjunct. So the registered run is a confirmation on fresh seeds of what I
have already seen. The registered base is 2026100123. It has not been run.

## What I will and will not say

- If BUILDER passes: "read strictly, with costs, kinds never met, content
  resets, matched shams and separate donors, the section-19 protocol is
  passed by a plain library learner whose constructor never changes". The
  portfolio says a ruler that calls library accumulation recursive sagacity
  is insufficient, so by the package's own test the protocol needs more
  than tightening.
- If BUILDER does not pass: the strict protocol resists this counterfeit,
  the review says so, and the finding is then that section 19 needs its
  four open choices fixed and no more.
- Either way the first gauntlet's result is restated with its conditions.
- I will not say anything about real substrates. One author, one toy
  world, designed organisms: C0 and I1 in my package's terms.
