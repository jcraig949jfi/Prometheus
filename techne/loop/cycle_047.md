## HITL #78 — latent, unchanged. `['P1','P1']`, no P3/P4. Not reopened. **Arsenal red: 29** (26 dependency artifacts; #242 still unruled, nothing installed).

# Cycle 047 — the drift is not structural, and a four-role function was silently wrong

**First cycle to complete detect → intervene → measure on code another role depends on.**

## The scoping move — the drift, answered with a number

Block 042–046's finding was that "real substrate + actionable intervention" had quietly become
"*my* substrate". So: repo-wide enumeration, 12,543 files across 40 non-mine directories, no claim
attached.

```
79 files across 7 roles import my code
   charon 41 · ergon 19 · aporia 7 · scripts 4 · sigma_kernel 4 · harmonia 3 · theseus 1

by DISTINCT CONSUMER-ROLE count
   4  techne.lib.mahler_measure.mahler_measure   [charon, harmonia, scripts, sigma_kernel]
   2  prometheus_math.arsenal_meta.ARSENAL_REGISTRY
   2  prometheus_math.discovery_pipeline.DiscoveryPipeline
```

**The drift was not structural.** It was a target-selection habit, and there was a four-role
callable sitting there the whole time.

## What was already true, and what wasn't

`mahler_measure` had tests for constants (`[5] → 5.0`), one cyclotomic, and shift-invariance.
**No test compared it against a published Mahler measure of a non-trivial polynomial.** Four roles
depended on that.

Pre-registered (`rung_notes/MAHLER_CROSS_ROLE_PREREG.md`, committed `9c1f5c26`) with two
deliberately opposed predictions.

**Prediction 1 — the mathematics is correct: HELD, 8/8.**

```
Lehmer x^10+x^9-x^7-...+x+1   got 1.1762808182599187   published 1.176280818259917
golden ratio x^2-x-1          got 1.6180339887498945   phi = 1.618033988749895
x-2 -> 2.0 · 2x-1 -> 2.0 · Phi_1 -> 1.0 · Phi_5 -> 1.0 · Phi_4 -> 1.0 · (x-2)(x-3) -> 6.0
```

**Prediction 2 — a degenerate input is mishandled: FAILED.** Every pre-registered domain case —
empty list, all zeros, single zero, float zero — **refused correctly** with an informative message,
and leading-zero padding was handled right. My expectation that the locally recurrent defect class
would be present here was simply wrong, which is worth as much as a hit: it is evidence the class
is not everywhere, sharpening cycle 044's retirement of the class hypothesis.

## Two real defects, neither of which I predicted

### 1. A complex constant lost its imaginary part

A `ComplexWarning` surfaced *while the authority suite ran* — not from my declared domain set,
which passed clean. `mahler_measure` casts input to `complex128` on entry, so complex coefficients
are in-domain by construction, but the degree-0 branch computed `abs(float(coeffs[0]))`, and
`float(complex)` **discards the imaginary part**:

```
M(3+4j)  returned 3.0   correct 5.0
M(1j)    returned 0.0   correct 1.0
```

The second is the severe one. **A measure of zero for a non-zero polynomial — and 0.0 is exactly
the value the zero-polynomial guard higher up exists to make unreachable.** A sentinel colliding
with a legitimate return, the same shape as cycle 046's knot volume. The degree-≥1 branch of the
*same function* already used `abs(coeffs[0])` correctly, so the function disagreed with itself
about how to read one coefficient — the "two readers, one right" shape of HITL #78, inside a single
function this time.

Fixed: modulus first, then cast. Four parametrised cases pin it, plus one asserting a non-zero
polynomial can never measure zero.

### 2. A precision budget nobody had measured

My own new multiplicativity property test then failed under Hypothesis on
`f=[1,0,-1,1,-3,1,1], g=[1,-1]`. **I did not assume it was my test.** High precision (mpmath, 50
dps) refereed: the implementation matches `M(f)` to **1.4e-10**, and the entire discrepancy lives
in the product — where `np.roots` displaces a root by 1.9e-6, and mpmath's own `polyroots` fails to
converge at all.

```
generic x generic     deg 2    rel err 1.2e-15
generic x generic     deg 4    rel err 2.4e-16
Lehmer x (x-2)        deg 11   rel err 1.9e-15    roots EXACTLY on the circle
(x-2) x Phi_4         deg 3    rel err 1.3e-15
f x Phi_5             deg 10   rel err 2.2e-09
f x (x-1)             deg 7    rel err 5.1e-06    <- worst found
```

**My first hypothesis was wrong.** I assumed roots *on* the unit circle drove the error —
Lehmer×(x−2) has them and is fine at 1.9e-15. The driver is how far root-finding **displaces** a
root; `max(1, |root|)` turns displacement straight into a spurious factor.

I set the property tolerance to the **measured** budget rather than a guessed one, and pinned the
characterisation in its own test — well-conditioned products asserted at 1e-13, the known bad case
bracketed. Loosening without measuring would have been weakening a contract to make an instrument
pass.

**Why the four consuming roles should care:** Lehmer's constant is 1.17628…, and searches for a
smaller measure work at fine resolution. **A 5e-6 error is far larger than the gaps such a search
resolves**, so a candidate could be mis-ranked. That is a property of the tool, not a bug, and it
was invisible until something checked.

## Postcondition, by name-diff

```
046   28 failed / 3474 passed
047   29 failed / 3518 passed
NEW   test_mahler_authority::test_property_MULTIPLICATIVITY   (my own, now resolved)
GONE  none
```

The one new failure was **my own new test**, and it is now green after the tolerance was measured
rather than assumed. Nothing else moved. The 26 dependency artifacts are untouched — #242 unruled,
nothing installed.

## Track 1 — `prometheus_math.polynomial_length` (Mahler 1960)

20 tests, RED first, four categories. The cheap L1 height, and the screen for the expensive one.

- **Authority**: `L(Lehmer) = 9` counted by hand; small cases.
- **Property**: dominates its largest coefficient; subadditive under addition; submultiplicative
  under multiplication; invariant under leading-zero padding.
- **Edge**: the zero polynomial **refuses**, deliberately matching `mahler_measure`'s domain rather
  than returning the arithmetically-defensible `0.0` — *a screen whose domain is wider than the
  thing it screens passes inputs the expensive step then rejects*. Also pins that complex
  coefficients use the modulus, because its companion had exactly that bug hours earlier.
- **Composition**: **Mahler's two-sided bound `M(f) ≤ L(f) ≤ 2^deg · M(f)`** against
  `mahler_measure` — chained against a function validated against published values the same day.

## TLDR — ELI5

Last block ended with an uncomfortable finding: I'd been fixing my own code and calling it real
work, because the code that actually matters belongs to other people and I'm not allowed to touch
it. So this cycle I checked whether that was really true.

It wasn't. Seven other parts of the project import my code, in 79 files. And one function —
Mahler measure, a number-theory calculation — is used by **four** of them. I own it, so I can fix
it. Nobody had ever checked it against the published textbook values.

The headline number was fine: it gets Lehmer's famous polynomial right to fifteen decimal places.

But two things were wrong that I hadn't predicted.

**One:** feed it a complex number and it threw away half of it. For one input it returned *zero* —
and zero is the answer it uses to mean "you gave me nothing", which it refuses elsewhere. The same
function was reading the same number two different ways in two different branches.

**Two:** my own new test then failed, and I nearly assumed my test was wrong. It wasn't obvious.
I checked with 50-digit arithmetic and found the function is accurate to about one part in
10¹⁵ normally — but on certain awkward polynomials it drops to one part in 10⁵. That matters,
because the whole point of this number in this project is hunting for values just barely above
1.17628, and an error that size is bigger than the gaps being hunted.

So I measured the error properly and wrote the measurement down, instead of quietly relaxing my
test until it passed.

## For ChatGPT

```
Prometheus loop, cycle 047, first cycle of block 047-051. FIRST CYCLE TO COMPLETE
detect -> intervene -> measure ON CODE ANOTHER ROLE DEPENDS ON.

HITL #78 latent unchanged, not reopened. Arsenal red 29 (26 dependency artifacts; #242 unruled,
nothing installed).

THE DRIFT WAS NOT STRUCTURAL. Repo-wide scoping, 12543 files across 40 non-mine dirs, no claim:
79 files across 7 roles import my code (charon 41, ergon 19, aporia 7, scripts 4, sigma_kernel 4,
harmonia 3, theseus 1). Top callable I own by DISTINCT CONSUMER-ROLE count:
techne.lib.mahler_measure.mahler_measure at FOUR roles. It was a target-selection habit, not a
structural limit.

PRE-REGISTERED (9c1f5c26) with two opposed predictions. Prior knowledge disclosed: existing tests
covered constants, one cyclotomic and shift-invariance, but NO test compared against a published
Mahler measure of a non-trivial polynomial.

PREDICTION 1 (mathematics correct): HELD 8/8. Lehmer -> 1.1762808182599187 vs published
1.176280818259917; golden ratio, x-2, 2x-1, Phi_1, Phi_4, Phi_5, (x-2)(x-3) all correct.
PREDICTION 2 (a degenerate input mishandled): FAILED. Every pre-registered domain case refused
correctly. My expectation that the locally recurrent defect class would be present was WRONG —
evidence the class is not everywhere, sharpening cycle 044's retirement of the class hypothesis.

DEFECT 1, NOT PREDICTED, found by a ComplexWarning surfacing WHILE THE SUITE RAN (the declared
domain set passed clean). mahler_measure casts input to complex128 on entry, so complex
coefficients are in-domain, but the degree-0 branch did abs(float(coeffs[0])) and float(complex)
DISCARDS THE IMAGINARY PART:
    M(3+4j) returned 3.0  (correct 5.0)
    M(1j)   returned 0.0  (correct 1.0)
The second is severe: A ZERO MEASURE FOR A NON-ZERO POLYNOMIAL, and 0.0 is exactly the value the
zero-polynomial guard exists to make unreachable — a sentinel colliding with a legitimate return,
same shape as cycle 046's knot volume. The degree>=1 branch of the SAME FUNCTION already used
abs(coeffs[0]) correctly, so it disagreed with itself about one coefficient. Fixed, 5 tests pin it.

DEFECT 2 — A PRECISION BUDGET NOBODY HAD MEASURED. My own new multiplicativity property test then
failed under Hypothesis on f=[1,0,-1,1,-3,1,1], g=[1,-1]. I DID NOT ASSUME IT WAS MY TEST. mpmath
at 50 dps refereed: the implementation matches M(f) to 1.4e-10 and the whole discrepancy is in the
product, where np.roots displaces a root by 1.9e-6 and mpmath.polyroots itself fails to converge.
    generic x generic   deg 2   1.2e-15      Lehmer x (x-2)  deg 11  1.9e-15 (roots ON circle)
    generic x generic   deg 4   2.4e-16      f x Phi_5       deg 10  2.2e-09
    (x-2) x Phi_4       deg 3   1.3e-15      f x (x-1)       deg 7   5.1e-06  <- worst
MY FIRST HYPOTHESIS WAS WRONG: roots ON the circle do not drive it (Lehmer x (x-2) has them and is
fine). The driver is how far root-finding DISPLACES a root; max(1,|root|) converts displacement
into a spurious factor. I set the tolerance to the MEASURED budget and pinned the characterisation
in its own test (well-conditioned asserted at 1e-13, bad case bracketed) rather than loosening
until green.
WHY THE FOUR ROLES SHOULD CARE: Lehmer's constant is 1.17628... and searches for a smaller measure
work at fine resolution. A 5e-6 error is LARGER THAN THE GAPS SUCH A SEARCH RESOLVES, so a
candidate could be mis-ranked. Property of the tool, not a bug, invisible until something checked.

POSTCONDITION BY NAME-DIFF: 046 28 failed/3474 passed -> 047 29 failed/3518 passed. The single new
failure was MY OWN new test, now green after measuring the tolerance. Nothing else moved.

Track 1: prometheus_math.polynomial_length, Mahler (1960) Mathematika 7:98-100. 20 tests, RED
first, four categories. The cheap L1 height and screen for the expensive one. Authority
(L(Lehmer)=9 by hand). Property (dominates largest coefficient; subadditive; submultiplicative;
padding-invariant). Edge (the zero polynomial REFUSES, deliberately matching mahler_measure's
domain rather than returning the arithmetically-defensible 0.0 — a screen with a wider domain than
what it screens passes inputs the expensive step then rejects; complex coefficients use the
modulus, pinned because its companion had exactly that bug hours earlier). Composition (MAHLER'S
TWO-SIDED BOUND M <= L <= 2^deg * M against mahler_measure, validated against published values the
same day).

What I want attacked:
1. Defect 2 was found because a property test I wrote failed and I chased it with high-precision
   arithmetic instead of loosening. But I ALSO wrote the tolerance that failed. How much credit is
   that worth versus a lucky catch — and would a reviewer have called 1e-7 obviously wrong?
2. The 5e-6 precision limit affects searches near Lehmer's constant. I have not checked whether
   any of the four consuming roles ACTUALLY operates at that resolution. Should the next cycle
   trace that, or is documenting the limit enough?
3. Prediction 2 failed: the degenerate-domain class was NOT present in the most-used function I
   own. Combined with cycle 044's retirement of the class hypothesis, is the class now better
   described as a property of code written FAST FOR THE LOOP rather than of my code generally?
```

## Traps ledger additions

- **A function disagreeing with itself across branches** — `abs(float(z))` in the degree-0 branch,
  `abs(z)` in the degree-≥1 branch of the same function. Defence: when a function has a
  special-case branch, check it computes the *same quantity* as the general one.
- **`float(complex)` silently discarding the imaginary part** — a warning, not an error, so it
  survives every run that does not read warnings. Defence: run new authority suites with warnings
  visible; this defect was found by a warning, not an assertion.
- **Picking a tolerance without measuring the error budget** — 1e-7 was a guess; the real budget
  spans 1e-16 to 5e-6 depending on conditioning. Defence: measure the budget, then set the
  tolerance, and pin the measurement so a future loosening has to argue with data.
- **Assuming a failing property test is the test's fault** — nearly did; high-precision arithmetic
  showed the implementation right in method and located the error precisely.
