# Preregistration: counterfeit gauntlet for the recursive-sagacity criterion

Reviewer: FABLE-5.1 (seat Dionysus). Written 2026-10-01, before the
registered run. Committed with gauntlet.py and before any receipt exists.

## What is being tested

The review charter asks me to try to fool the combined criterion of
"Recursive Sagacity Observatory v0.1", section 19:

- functional savings: later acquisition is cheaper because earlier
  development built reusable machinery;
- V -> U -> S causal nesting: developed V causally improves the
  construction of fresh U, which improves fresh S;
- developmental provenance: the effect traces through machinery that takes
  part in future developmental writes, not through carried task content;

using the section's own protocol (develop on A; reset task content; let V_A
construct fresh U_B on B; freeze U_B; reset task state; test on fresh C;
lesion V; sham lesion; rescue; cross V and U donors; irrelevant-history
donors; repeat on fresh D and E). Step 13, reconstruction in another
substrate, is not run.

## The organisms (all designed, none found by search)

| name | inherited | what develops | what I expect |
|---|---|---|---|
| STATIC | three learning procedures in a fixed order | nothing | FAIL (fire test: savings) |
| MATURATION | the same | after ANY experience the order is rewritten to one fixed inherited order | FAIL (fire test: irrelevant-history control) |
| GEARBOX | the same three procedures | a move-to-front list: the procedure that worked moves to the front | PASS v0.1 |
| BUILDER | six primitive operations and a fixed constructor; no procedures | a library of templates that worked; the constructor tries the library, then compositions of library items, then primitives | PASS v0.1 |

How I map the criterion's letters onto them, stated so it can be contested:
S is the state a procedure fits within one task (a constant, a pair of
constants, or a table). U is the procedure chosen for a family and then
frozen. V is the part that chooses or builds U: the fixed rule plus its
developed state (the list, or the library).

## The world

Prediction of a hidden function on the integers modulo 17, with feedback,
12 trials per task. Cost is the number of errors. Family types: SHIFT
(x + c), SCALE (a x), AFFINE (a x + c), TABLE (arbitrary), SQR, CUB.

## Fixed in advance

- Code: gauntlet.py at this commit (its hash goes on the receipt).
- Parameters: 24 independent replicates per arm; 50 test tasks per
  replicate; a replicate is GOOD at 3.5 errors per task or fewer, BAD at
  6.0 or more; an arm is GOOD or BAD if at least 22 of 24 replicates are;
  otherwise INDETERMINATE. A procedure is accepted during construction if
  it makes 4 errors or fewer on one task. Construction budgets: GEARBOX 1
  task, BUILDER 4 tasks.
- Seeds: the registered base is 2026100121. It has not been run.
- Expected verdicts (the EXPECTED table in the code):

      v0.1 criterion    STATIC FAIL, MATURATION FAIL,
                        GEARBOX PASS (targets SHIFT and SCALE),
                        BUILDER PASS (target AFFINE)
      added checks      GEARBOX -> SELECTION_AMONG_INHERITED
                        BUILDER -> CONSTRUCTION_AT_FIXED_DEPTH

- The v0.1 verdict is PASS only if all of these hold: naive BAD and intact
  GOOD (savings); lesion BAD, sham GOOD, rescue GOOD, V donor GOOD, U donor
  GOOD, lesioned-line U BAD (nesting); at least one developmental write to
  V, at least one read of V during construction, and irrelevant history
  BAD (provenance); the same pattern on fresh families D and E. Any
  INDETERMINATE arm makes the verdict INDETERMINATE.

## The three added checks

1. Out-of-library gain. Does experience help on a family whose efficient
   procedure was not inherited as a unit (AFFINE)?
2. Knockout of the inherited part. Remove the inherited procedure
   (GEARBOX) or the inherited composition operator (BUILDER) and ask
   whether the gain survives.
3. Count. Over a long, varied history, is any accepted procedure absent
   from what was inherited as a unit?

Classification rule, fixed here: no out-of-library gain and nothing new
accepted is SELECTION_AMONG_INHERITED. Out-of-library gain, something new
accepted, and no gain once the inherited operator is removed is
CONSTRUCTION_AT_FIXED_DEPTH. Neither check can return "recursion": no
organism here can add a level or modify its own constructor, and I have no
designed positive for that. That gap is reported, not hidden.

## Design run, disclosed

I ran the code once on design seeds (base 11, `--design`, nothing
written). Every arm came out as expected, 24 of 24 replicates in each. I
changed no parameter after that run. So the registered run is a
confirmation on fresh seeds of something I have already seen once.

## What I will and will not say

- If GEARBOX passes: "the v0.1 criterion as written is satisfied by
  algorithm selection with a move-to-front memory". I will not say the
  authors intended to accept it. The design says a conventional system that
  passes should be reported, and I am reporting one.
- If any verdict differs from the table: the receipt is kept as GATE FAILED
  and the review says my counterfeit claim failed.
- Independence: one author, one host, designed organisms. In my own
  package's terms this is level I1 and a C0 observation about a criterion.
