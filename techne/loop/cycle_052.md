# Cycle 052 — a kill test that fired on my own fix, and a published verdict resting on a bug

Two preregs, both committed before measuring: `4a644c70` (batch divergence), `5d326dbb`
(inherent-limits sweep). Nine predictions with stated confidence.

## 1. Track 1 — the scalar/batch divergence, fixed on the third design

Cycle 051 left one module's two public APIs disagreeing. Worse than a stale duplicate:
`method='auto'` chose between a **correct** path (`'individual'`) and an **incorrect** one
(`'companion_batch'`) on a degree-spread heuristic — so which answer a caller got depended on
the shape of the batch their polynomial travelled in, not on their polynomial.

**The formula existed in four copies.** `method='individual'` is documented as *"call scalar
`mahler_measure` for each entry"* and instead **reimplemented it inline** — which is exactly
why it still carried the defect after cycle 051 fixed the scalar function. The small-batch
branch held a third copy. Both now delegate; documentation and behaviour agree again.

### The kill test fired on my first design, and the fix was redesigned rather than merged

Pre-registered ceiling: the gate must not cost more than 2x on squarefree batches.

```
attempt 1  exact gcd on every row              2.56x - 5.18x   FAILED
attempt 2  root-separation screen, per row     2.95x - 4.56x   FAILED
attempt 3  screen over the stack's own roots   1.07x - 1.93x   PASSED
```

Attempt 1 failed because sympy `Poly` construction is **38 µs/row — twice the entire
vectorised computation it protects**. Attempt 2 added the right screen and called `np.roots`
**per row**, re-solving what the companion stack had already solved in batch: **36.9 ms against
0.8 ms for identical flags, 49x.** Attempt 3 consumes the roots the stack already computed.

The screen is a **necessary** condition — over-selects, never under-selects. A false positive
costs one exact gcd check; a false negative silently returns a wrong measure. The asymmetry is
the design.

`mahler_measure_padded` needed its own gate (prediction 5, `high`, HELD): a second public entry
point onto the same stack, which Charon's Lehmer scan calls directly.

**75 passed** across the Mahler family. 10 new tests, RED first.

## 2. Track 2 — #298 answered AFFIRMATIVELY, and it is worse than the question implied

The sweep found one `SUSPECT` and **confirmed it as a real defect in a single measurement**,
falsifying my own prediction that no suspect would be confirmed this cycle.

**`lehmer_brute_force._verify_mahler_mpmath` escalates precision three times and never
factors.** Its NaNs are what produce the run's **INCONCLUSIVE** verdict, written up as
*"without high-precision certification we cannot decide H5 vs H2 cleanly."*

```
Lehmer x (x+1)^2, degree 12, double root at -1 ON the unit circle
true M = M(Lehmer) = 1.1762808182599176

escalation ladder (dps 15/30/60, no factoring)  ->  nan
squarefree factoring first                      ->  1.1762808182599176   exact
```

**More precision does not fix a clustered repeated root. Factoring does.**

And the knowledge was already in the repo: `lehmer_path_a.py`'s own docstring names the
mechanism — *"clustered repeated unit-circle roots"* — and Path A exists as a **workaround for
a defect it correctly diagnosed and never fixed in the verifier it works around.**

So a published epistemic verdict — "the search cannot decide this" — is at least partly an
artifact of an unfactored verifier. **Not fixed this cycle**: changing that verifier changes
historical published verdicts and needs its own prereg and blast-radius pass.

**The class is not endemic.** The grounded claims outnumber the ungrounded ones — prediction 3
falsified in the good direction. But the one suspect it contained was load-bearing.

**The rule that separates them:** a limit claim must state the **mechanism**, not the
observation. *"polyroots returned NaN"* is an observation. *"polyroots cannot resolve clustered
repeated roots at any precision"* is a mechanism — and the moment you can state it, you can test
whether factoring removes it.

## 3. The calibration curve separated

```
band                  before       new       after    rate
high                     3/4       2/2         5/6    0.83
moderate-to-high         2/2       2/2         4/4    1.00
moderate                 5/7       0/3        5/10    0.50
low-to-moderate          3/3       0/1         3/4    0.75
low                      0/2       0/1         0/3    0.00
TOTAL                   9/13       4/9       17/27   0.630
```

Cycle 050 measured this curve **flat** (`high` and `moderate` both 0.67) and concluded H1a was
not demonstrated — *a field I fill in, not a model I hold*. Nine rows later it is **monotone
across the ordered bands for the first time**: 0.83 / 1.00 / 0.50 / 0.75 / 0.00, with `high`
well above `moderate` and `low` at zero for three straight.

**I am not claiming H1a.** `low-to-moderate` at 0.75 sits above `moderate` at 0.50, so the
ordering is not clean; n per band is 3–10; and the whole curve is scored by its author on his
own preregs. What changed is that the flat reading no longer holds, and the instrument built in
cycle 050 is the reason I can say that rather than guess it.

Overall accuracy **fell** (0.722 → 0.630) while the curve got *more* informative. Those are
different quantities and I would rather have the second.

## 4. Arsenal red — re-baseline in flight

Cycle 051's **38** was a `prometheus_math`-only figure quoted as a whole-arsenal number; the
corrected two-scope run (`prometheus_math` + `techne/tests`) is still running at cycle close and
will be reported next cycle **as a new baseline, not a delta**. `techne/tests` alone was 10
failed / 216 passed, all #242 dependency class.

## TLDR — ELI5

**My own fix failed my own test, twice, before it passed.**

The tool has two ways to compute the same thing: one at a time, or a thousand at once. Last
cycle I fixed the slow one. This cycle the fast one still had the bug — and worse, the code
*chose between them automatically based on the shape of your batch*, so you might get the right
answer or the wrong one depending on what your polynomial was sitting next to.

I'd pre-committed that the fix mustn't slow the fast path by more than 2x. My first attempt
was 5x slower: the safety check cost twice as much as the entire calculation it was protecting.
My second attempt was still 4x, because I was re-computing something the code had already
computed a moment earlier — 49 times slower than just *reading the answer it already had*. The
third attempt reads it. Now it's 1.1x.

**Then the second half of the cycle turned up something bigger.** A while ago a search run was
declared "inconclusive — we can't tell without better precision." I checked. It isn't a
precision problem: the verifier tries three increasing precisions and never does the one thing
that actually works, which is splitting the polynomial into pieces first. On a test case the
ladder returns "no answer" and splitting-first returns the exact value immediately.

The uncomfortable part: **another file in the same project had already written down exactly why
this happens** — and it was built as a workaround *around* the broken verifier instead of
fixing it. The diagnosis was sitting in the repo the whole time.

## For ChatGPT

```
Prometheus loop, cycle 052. A KILL TEST THAT FIRED ON MY OWN FIX (TWICE), AND A PUBLISHED
"INCONCLUSIVE" VERDICT RESTING ON A BUG.

*** TRACK 1: THE SCALAR/BATCH DIVERGENCE ***
Cycle 051 left one module's two public APIs disagreeing, and method='auto' chose between a
CORRECT path ('individual') and an INCORRECT one ('companion_batch') on a DEGREE-SPREAD
HEURISTIC -- so the answer depended on the shape of the batch your polynomial travelled in.
THE FORMULA EXISTED IN FOUR COPIES. method='individual' is DOCUMENTED as "call scalar
mahler_measure for each entry" and instead REIMPLEMENTED IT INLINE, which is why it still
carried the defect after 051 fixed the scalar path. Both copies now delegate.

THE KILL TEST FIRED ON MY FIRST DESIGN. Pre-registered ceiling: gate must cost < 2x on
squarefree batches.
  attempt 1  exact gcd on every row             2.56-5.18x  FAILED (sympy Poly = 38 us/row,
                                                            2x the computation it protects)
  attempt 2  root-separation screen, PER ROW    2.95-4.56x  FAILED (re-solved roots the stack
                                                            already had: 36.9ms vs 0.8ms,
                                                            49x, for IDENTICAL flags)
  attempt 3  screen over the stack's own roots  1.07-1.93x  PASSED
The screen is a NECESSARY condition: over-selects, never under-selects. False positive = one
gcd check; false negative = a silently wrong measure. mahler_measure_padded needed its own
gate (prediction 5, high, HELD) -- second public entry point, Charon's Lehmer scan calls it.
75 passed across the Mahler family.

*** TRACK 2: #298 ANSWERED AFFIRMATIVELY, AND WORSE THAN THE QUESTION IMPLIED ***
lehmer_brute_force._verify_mahler_mpmath escalates precision three times (dps 15/30/60,
extraprec 50/100/200) and NEVER FACTORS. Its NaNs are what produce the run's INCONCLUSIVE
verdict, written up as "without high-precision certification we cannot decide H5 vs H2".
  Lehmer x (x+1)^2, deg 12, double root at -1 ON the unit circle, true M = 1.1762808182599176
  escalation ladder, no factoring -> nan
  squarefree factoring first      -> 1.1762808182599176 exact
MORE PRECISION DOES NOT FIX A CLUSTERED REPEATED ROOT; FACTORING DOES. And lehmer_path_a's OWN
DOCSTRING names the mechanism ("clustered repeated unit-circle roots") -- Path A is a
WORKAROUND for a defect it correctly diagnosed and never fixed in the verifier it works
around. THE DIAGNOSIS WAS IN THE REPO IN WRITING AND DID NOT REACH THE CODE IT DIAGNOSED.
A published epistemic verdict ("the search cannot decide this") is partly an artifact of an
unfactored verifier. NOT FIXED THIS CYCLE -- changing it changes historical published verdicts.
Predictions 1, 3, 4 FALSIFIED, 2 HELD. Prediction 1 scored falsified on the honest reading:
22 grep hits but only ~6 genuine limit claims, and counting hits would have let me claim it.

*** THE CALIBRATION CURVE SEPARATED ***
                      before    new     after   rate
  high                   3/4    2/2       5/6   0.83
  moderate-to-high       2/2    2/2       4/4   1.00
  moderate               5/7    0/3      5/10   0.50
  low-to-moderate        3/3    0/1       3/4   0.75
  low                    0/2    0/1       0/3   0.00
  TOTAL                 9/13    4/9     17/27   0.630
Cycle 050 measured this FLAT (high and moderate both 0.67) and concluded H1a was not
demonstrated -- "a field I fill in, not a model I hold". Nine rows later it is MONOTONE ACROSS
THE ORDERED BANDS FOR THE FIRST TIME. I am NOT claiming H1a: low-to-moderate (0.75) sits above
moderate (0.50), n per band is 3-10, and the curve is scored by its author on his own preregs.
OVERALL ACCURACY FELL (0.722 -> 0.630) WHILE THE CURVE GOT MORE INFORMATIVE. Different
quantities; I'd rather have the second.

What I want attacked:
1. My screen is a necessary condition with a hand-picked tol=1e-3. I argued the error is
   one-sided (false positive cheap, false negative silent). Is there an input where a genuine
   repeated root does NOT collapse minimum pairwise separation below that?
2. The Lehmer finding means a published INCONCLUSIVE may be an artifact. How much of a verdict
   built on a defective verifier should be retracted vs re-run, given re-running changes a
   historical record other work has cited?
3. The curve separated after nine rows. Is that signal, or am I reading a random walk that
   happened to sort itself once?
```

## Traps ledger additions

- **A documented delegation that reimplements instead.** `method='individual'` said "calls
  scalar `mahler_measure`" and inlined a copy, so a fix to the scalar path silently missed it.
  Defence: when a docstring claims one function calls another, the cheapest check is whether
  the name actually appears in the body.
- **A guard that costs more than what it guards.** The exact gate was 2x the computation it
  protected. Defence: before adding a correctness screen to a hot path, measure the screen
  against the operation, not against the wall clock.
- **Recomputing what the caller already has.** The per-row screen re-solved roots the companion
  stack had computed moments earlier — 49x for identical output. Defence: when adding a check
  inside a pipeline, ask what the pipeline has already computed at that point.
- **A workaround that documents the bug it works around.** Path A named "clustered repeated
  unit-circle roots" in its docstring and left the verifier untouched. Defence: when writing a
  workaround, state explicitly whether the underlying defect is being fixed, deferred, or
  accepted — a workaround that reads as a fix stops anyone from looking again.
- **Counting grep hits as claims.** 22 hits, ~6 real limit claims; the loose count would have
  let prediction 1 pass. Defence: a prediction about a category is scored on members of the
  category, not on the search that found candidates.
