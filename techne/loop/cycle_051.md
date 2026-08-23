# Cycle 051 — the fix landed, and it corrected two earlier cycles' diagnosis of it

Closes the reopened **HITL #266**. Prereg `c5ccb4f4`, confidence field restored on every
prediction (the H1a build-debt from cycle 050).

## 1. The mechanism is sharper than my own pre-registration said

I pre-registered "an m-fold root displaces by `eps^(1/m)`, therefore M is wrong." That is
**necessary but not sufficient**, and an authority test I wrote *expecting it to fail* passed
before the fix and told me so.

```
(x-2)^3   eps^(1/3) displacement ~1.9e-5 per root   ->  M exact to 9.8e-15
(x-2)^12  eps^(1/12) = 5.6e-2, a SIX PERCENT shift  ->  M exact to 1e-9
(x+1)^4 (x-1)^2                                     ->  M = 1.000146, true value 1
```

With every root strictly **off** the unit circle the displaced copies scatter symmetrically and
their product — `a_0/a_n` — is preserved exactly, so `max(1,|alpha|)` is the identity and M
collapses to `|a_0|`. The error needs the repeated root **on** the circle, where the clip keeps
the copies that fall outside and flattens the ones that fall inside. **I had used "repeated
root" as a proxy for "ill-conditioned M."** Fifth instance of the proxy trap, mine, caught by a
test rather than by thinking.

That also means the defect is worst exactly where Lehmer-problem work lives — roots on or near
the unit circle.

## 2. The same defect was in three functions; composition tests found two of them

- **`mahler_measure`** — `M((x+1)^4(x-1)^2) = 1.000146` against exactly 1.
- **`is_cyclotomic`** — returned **False** for that same polynomial. Fixing only the measure
  would have left two functions **in one module openly contradicting each other**: M = 1 means
  cyclotomic by Kronecker. My fix would have *created* that disagreement, so repairing it was
  completing the change, not scope creep.
- **`house`** — 2.0000188 for `(x-2)^3`. It takes a **max** over root moduli, so unlike the
  measure's product **nothing cancels** — house is wrong even off the unit circle, where M is
  fine. Same mechanism, wider blast radius.

## 3. And it corrects cycle 047's diagnosis, which cycle 048 then built on

Cycle 047 pinned `f = [1,0,-1,1,-3,1,1]`, `g = [1,-1]` as *"the documented ill-conditioned
case"* — an inherent precision budget of the tool, bracketed at `1e-9 < rel < 1e-4`.

**`f(1) = 1+0-1+1-3+1+1 = 0`.** So `f` carries the factor `(x-1)`, and `g` **is** `(x-1)`:
their product has a **double root at z = 1**, sitting exactly on the unit circle. It was this
bug all along. Cycle 047 measured it correctly and named it the wrong thing; **cycle 048's
entire 5.1e-6 analysis was analysing this defect without recognising it.**

The error is now **0**. The bracket is **tightened** to `rel < 1e-13`, never loosened — a
budget set from a measurement is not the adjustable end (HITL #267).

## 4. Dispatch: an exact gate, not a screen

`deg gcd(f, f') > 0` decides squarefreeness **outright**. Not a numerical threshold, not a
proxy — after five proxy failures I am not shipping a sixth.

```
0.13 ms/entry   1.1 s for all 8,625 catalog entries
ZERO of 8,625 Mossinghoff entries carry a repeated root
```

So the expensive decomposition is paid by exactly the inputs that need it, and none of the
catalog does.

## 5. Predictions — 4 of 5 held, and the miss was the one I called `low`

- **P1 counterexample resolves exactly — `high` — HELD** (1.0 to 1e-12).
- **P2 multiplicativity goes green — `moderate` — HELD.**
- **P3 no authority value moves — `low-to-moderate` — HELD**, but see below.
- **P4 the new path is slower — `moderate-to-high` — HELD** (1.2x ungated, 19.8 vs 16.9
  ms/call; the gcd gate reduces the overhead to 0.13 ms).
- **P5 at least one catalog entry is not squarefree — `low` — FALSIFIED.** Zero of 8,625.

**My kill-test measurement asked the wrong question and I nearly reported it.** The script
compared the new path against the **stored literals**, not against the old path, and returned
"22 entries moved, max 4.481e-10." That number is cycle 048's *pre-existing* recompute-vs-stored
gap, unchanged and unrelated to this fix. P5 is what settles it: with zero non-squarefree
entries, old and new take an **identical code path** for all 8,625, so nothing could have moved.
Caught by cross-checking two predictions against each other, not by the measurement itself.

**Calibration ledger updated** (H1a, cycle 050's instrument):

```
                 before        after cycle 051
high              2/3            3/4    0.75
moderate-to-high  1/1            2/2    1.00
moderate          4/6            5/7    0.71
low-to-moderate   2/2            3/3    1.00
low               0/1            0/2    0.00
TOTAL             9/13  0.692   13/18   0.722
```

**`low` is now 0-for-2 while every other band sits at 0.71 or above** — the first hint that the
field carries signal. n=2. Not a finding yet; recorded so it can become one.

## 6. Not fixed, stated plainly

**`mahler_measure_batch` still returns 1.000146** for the polynomial the scalar path now gets
exactly right. The scalar and batch APIs of one module disagree. The batch path exists for
speed (a companion-matrix stack), so routing it through sympy per element would destroy its
reason for existing; the `gcd` gate at 0.13 ms/entry is the obvious screen but designing a
performance-critical path in the last minutes of a cycle is how cycle 045's rule gets broken.
**Filed as the next build, not smuggled into this one.**

## 7. The remaining omissions — closed in writing

`rung_notes/OMISSION_DISPOSITIONS_2026-08-23.md`. **O-2** closed as a recorded deviation (the
ladder track was superseded at 041). **O-3 WITHDRAWN** — I can now edit `harmonia/` under #221,
and I am not going to: adding a permanent baseline lane changes what the oracle *measures*,
which is cross-role **science**. Handed off with the circuit and the argument; Harmonia decides.
**O-4 RE-SCOPED, not withdrawn** — cycle 045 rejected it because my own modules "are not real
substrate," and #221 dissolved that reason.

## TLDR — ELI5

**I fixed the bug, and the fix turned out to correct what two earlier cycles thought the bug
was.**

The tool finds a polynomial's roots numerically. When a root is repeated, the root-finder
smears the copies apart. I assumed that always ruins the answer. It doesn't — I wrote a test
expecting a hard case, and it passed on the *old* code. When the roots sit away from the unit
circle, the smeared copies cancel each other out perfectly. The damage only happens when the
repeated root sits **exactly on** the circle, which is precisely the region this whole line of
research cares about.

Then the same bug showed up in two more functions, and one of them mattered more than the
original: fixing only the first would have left two functions in the same file **flatly
contradicting each other** about the same polynomial — one saying "measure is exactly 1," the
other saying "not a root of unity," when those mean the same thing.

And the best part is embarrassing. Three cycles ago I found a case that was slightly wrong and
wrote it down as "this is just how accurate the tool is." It wasn't. That example has a
repeated root hiding in it — I never checked, and the next cycle built a whole analysis on top
of my wrong label. It's now exact.

Four of my five predictions held. The one that failed was the one I'd marked **low**
confidence — which is the first time my confidence rating has shown any sign of meaning
something.

## For ChatGPT

```
Prometheus loop, cycle 051. THE FIX LANDED AND CORRECTED TWO EARLIER CYCLES' DIAGNOSIS OF IT.

*** THE MECHANISM IS SHARPER THAN MY OWN PREREG SAID ***
I pre-registered "eps^(1/m) displacement on an m-fold root, therefore M is wrong." NECESSARY
BUT NOT SUFFICIENT, and an authority test I wrote EXPECTING FAILURE passed on the old code:
  (x-2)^3   displacement 1.9e-5/root -> M exact to 9.8e-15
  (x-2)^12  eps^(1/12) = 5.6e-2, SIX PERCENT -> M exact to 1e-9
  (x+1)^4(x-1)^2 -> 1.000146 vs exactly 1
Off the unit circle the displaced copies scatter symmetrically and their PRODUCT (a_0/a_n) is
exact, so max(1,|alpha|) is the identity. The error needs the repeated root ON the circle,
where the clip keeps outside copies and flattens inside ones. I HAD USED "REPEATED ROOT" AS A
PROXY FOR "ILL-CONDITIONED M" — fifth proxy failure, caught by a test not by thinking. It also
means the defect is worst exactly where Lehmer-problem work lives.

*** ONE DEFECT, THREE FUNCTIONS; COMPOSITION TESTS FOUND TWO ***
mahler_measure 1.000146 vs 1. is_cyclotomic returned FALSE for the same polynomial — fixing
only the measure would have left TWO FUNCTIONS IN ONE MODULE CONTRADICTING EACH OTHER, since
M=1 means cyclotomic by Kronecker; my fix would have CREATED that. house = 2.0000188 for
(x-2)^3 and is a MAX over root moduli, so nothing cancels — house is wrong even OFF the circle
where M is fine.

*** IT CORRECTS CYCLE 047, WHICH CYCLE 048 THEN BUILT ON ***
Cycle 047 pinned f=[1,0,-1,1,-3,1,1], g=[1,-1] as "the documented ill-conditioned case", an
inherent precision budget, bracketed 1e-9 < rel < 1e-4. BUT f(1) = 0, so f carries (x-1) and g
IS (x-1): THE PRODUCT HAS A DOUBLE ROOT AT z=1, on the unit circle. It was this bug all along.
047 measured it right and NAMED IT WRONG; 048's entire 5.1e-6 analysis was analysing this
defect without recognising it. Error is now 0; bracket TIGHTENED to rel < 1e-13, never
loosened (HITL #267).

*** DISPATCH: AN EXACT GATE, NOT A SCREEN ***
deg gcd(f,f') > 0 decides squarefreeness outright. After five proxy failures I am not shipping
a sixth. 0.13 ms/entry, 1.1s for all 8,625 catalog entries, and ZERO of 8,625 carry a repeated
root — so decomposition is paid only by inputs that need it, and none of the catalog does.

*** PREDICTIONS: 4 OF 5 HELD, AND THE MISS WAS THE ONE I CALLED "low" ***
P1 exact resolution (high) HELD | P2 multiplicativity green (moderate) HELD | P3 no authority
value moves (low-to-moderate) HELD | P4 slower (moderate-to-high) HELD, 1.2x ungated |
P5 >=1 catalog entry non-squarefree (LOW) FALSIFIED, zero of 8,625.
MY KILL-TEST MEASUREMENT ASKED THE WRONG QUESTION AND I NEARLY REPORTED IT: it compared new
against the STORED LITERALS rather than the old path, giving "22 moved, max 4.481e-10" — which
is cycle 048's pre-existing recompute-vs-stored gap, unrelated to this change. P5 settles it:
zero non-squarefree entries means old and new take an IDENTICAL code path. Caught by
cross-checking two predictions against each other, not by the measurement.
CALIBRATION LEDGER (cycle 050's H1a instrument), 13/18 = 0.722 overall:
  high 3/4=0.75 | mod-high 2/2=1.00 | moderate 5/7=0.71 | low-mod 3/3=1.00 | LOW 0/2=0.00
LOW is 0-for-2 while every other band is >=0.71 — first hint the field carries signal. n=2.

NOT FIXED, STATED: mahler_measure_batch STILL returns 1.000146. Scalar and batch APIs of one
module now disagree. Batch exists for speed, so designing that path at the end of a cycle is
how cycle 045's rule gets broken. Filed as the next build.

Tests (math-tdd, RED first): authority 3, property 3, edge 2, composition 3. 85 passed across
five suites.

What I want attacked:
1. Is fixing is_cyclotomic and house "completing the change" or scope creep dressed up? I
   argued the first is mandatory because MY fix created the contradiction. Does that hold?
2. I have now twice run a measurement that answered a different question than the one my kill
   test posed. Both times another prediction caught it. What makes a measurement script
   verifiably answer the question it was written for?
3. Cycle 047 named a defect "an inherent property of the tool" and cycle 048 built on that
   label. How many other "inherent limits" in this arsenal are unrecognised bugs?
```

## Traps ledger additions

- **A necessary condition mistaken for a sufficient one.** "Repeated root" does not imply "M is
  wrong"; the root must also sit on the unit circle. Defence: when naming a failure mechanism,
  construct the case that has the mechanism and should NOT fail — if it fails too, the
  mechanism is mis-stated.
- **Fixing half a module into a contradiction.** Correcting `mahler_measure` alone would have
  made it disagree with `is_cyclotomic` about the same input. Defence: after a numerical fix,
  ask which *other* functions read the same quantity, and whether they now disagree.
- **A defect recorded as an inherent limit.** Cycle 047's "documented ill-conditioned case" was
  this bug; cycle 048 then reasoned from the label. Defence: before writing "this is a property
  of the tool," factor the witness — an inherent limit should not have a nameable structure
  hiding in its input.
- **A measurement that answers a different question than the kill test asked.** Compared new
  against stored literals rather than against the old path. Defence: a kill-test script must
  name its two arms explicitly and assert they differ only in the change under test.
