## HITL #78 — unchanged. `phases: ['P1']`, no P3/P4, no bandread. Latent, uncontaminated.

One line, as the closure specifies. Standing detector green (0.22 s), so the seam is unrepaired.
Not reopened.

# Cycle 045 — the full arc, finally: detect → intervene → measure. On my own arsenal.

**Two real defects found and fixed with measured postconditions.** First cycle since 042 to
complete the arc, and the target was code I have been ignoring while auditing someone else's.
Net **30 red → 29**, not the 28 I predicted — a third failure surfaced, and the check that it is
not mine is below.

## Allocating the 80% — the decision, made before the work

HITL #231 was unruled, so I chose and justified in writing
(`rung_notes/CYCLE045_BUDGET_ALLOCATION.md`, committed before any measurement).

**Rejected, with reasons.** *Lane A/B* — a methodology experiment on my own modules; it is not
real substrate, and putting it in the 80% would be the instrument-eating-itself failure mode
wearing the regime change as a costume. Stays in the 20% queue. *The `Measurement` migration* —
instrument maintenance; its "production" callers are my own contract registry. *The cycle-044
extractor* — the necessity arm already came back empty, so no decision changes on any outcome; it
fails the gate outright.

**Chosen: the 30 failing tests in `prometheus_math`.** Real substrate (the arsenal is the tooling
the project exists to build), actionable intervention (I own it), measurable postcondition.

**And the uncomfortable part: they have been red since at least cycle 041** — 30 failed, measured
this cycle at 30 failed / 3441 passed — while I spent 042-044 auditing another role's loader.

## The classification, pre-registered before the list was inspected

`rung_notes/ARSENAL_RED_PREREG.md`. **n = 30**, exactly matching the stable prior. `TEST-BUG` was
ordered *above* the `DEFECT-*` rules deliberately, so "the test was wrong" has to be ruled out
before I get to claim a product defect.

```
ARTIFACT-DEPENDENCY   26   chipfiring 7, GUDHI 7, shapely 6, MIP backend 4, qp 2
TEST-BUG               1   test_dilog_inversion_identity
DEFECT-LOGIC           1   lehmer parallel path
ARTIFACT-ENVIRONMENT   2   knot corpus — but see below, the manifestation is a defect
```

- **Prediction 1 (majority ARTIFACT): HELD**, 26/30 = 87%.
- **Prediction 2 (≥1 real DEFECT): HELD.**
- **Prediction 3 (≥1 TEST-BUG): HELD.**

## Fix 1 — a test asserting continuity across a branch cut

`test_dilog_inversion_identity` failed with `4.355172180607204 < 1e-09`. Not noise:

```
re=0.50   |diff| = 4.355172180607   2*pi*ln(1/re) = 4.355172180607
re=0.25   |diff| = 8.710344361214   2*pi*ln(1/re) = 8.710344361214
re=0.80   |diff| = 1.402052283009   2*pi*ln(1/re) = 1.402052283009
off-axis  |diff| ~ 5e-16
```

**The discrepancy is exactly the dilogarithm's branch discontinuity, to twelve decimals.** When
Hypothesis draws `im = ±0.0`, `1/z` lands on the principal cut `[1, ∞)` and the two
implementations take opposite sides of it. The test's guard was `abs(z) > 0.99` — **a proxy on
magnitude**, when the real precondition is that `1/z` must not be on the cut. That is the same
error shape as cycle 043's property guard, which I had recorded as a lesson and evidently not
generalised.

Fixed by guarding on the actual precondition — **and the excluded case is pinned, not dropped**:
a new test asserts the gap equals `2π·ln(1/z)` exactly. Removing a case and characterising it are
different things, and a bare `return` would have let a genuine regression through.

**Postcondition: 27 passing + 1 failing → 28 passing.**

## Fix 2 — an import that a file move broke, invisible to everything static

`lehmer_brute_force.py:1056` put the **repo root** on `sys.path` and then imported
`_lehmer_brute_force_worker`, which actually lives in **`scripts/`**. `ModuleNotFoundError`, every
time. It is inside a function, on the multiprocessing path only, so no linter and no import-time
check could see it — it just sat in the suite.

Fixed to probe both locations and to raise an explanatory error if neither has the file.

**Postcondition: 19 passing + 1 failing → 20 passing.**

## Found, not fixed — and stated rather than skipped

`test_knot_trace_field_env`: **all 48 hyperbolic knots carry `hyperbolic_volume = 0.0`**, with
`_LAST_LOAD_SOURCE = "curated-only"`. The KnotInfo source is unavailable and the curated fallback
supplies `0.0`.

**A hyperbolic knot with volume 0.0 is mathematically impossible** — hyperbolic ⟹ volume > 0. So
the origin is environmental, but the manifestation is the conflation this loop has been chasing
all month: *"volume is 0"* and *"volume is unknown because the source is absent"* shipped as the
same value, in code I own. The authority test caught it correctly by comparing against Cao–Meyerhoff.

**I did not fix it**, and the reason is a number: `hyperbolic_volume` has **44 non-test
references**. Changing the fallback to declare the field unknown is a typed change across all of
them, and it needs its own pre-registration and C_site measurement rather than being smuggled into
a cycle that was about something else.

## Result — 30 red → 29 red, and the arithmetic needs explaining

I predicted 28. The measured number is **29**, and the gap is the interesting part.

```
before   30 failed, 3441 passed
after    29 failed, 3455 passed
FIXED    test_dilog_inversion_identity            (gone)
FIXED    test_composition_run_brute_force_tiny_smoke (gone)
NEW      test_sigma_env_learning::test_property_seed_reproducibility
```

Both fixes held. A **third, previously-unseen failure appeared** — so I checked whether I had
caused it rather than assuming:

- it passes in isolation, twice;
- the only contamination path my changes created is the lehmer fix inserting `scripts/` into
  `sys.path` process-wide, so I ran `test_lehmer_brute_force.py` and `test_sigma_env_learning.py`
  **together in one process: 42 passed**;
- it is an explicitly stochastic REINFORCE test whose own docstring notes it is unreliable at low
  step budgets.

So it is an order- or state-dependent flake, not mine. **I cannot prove it was flaking before this
cycle without an expensive bisect, and I am not claiming that.**

**And it sharpens the second-order finding rather than denting it: I only saw this flake because I
was watching the count.** A suite sitting at a constant 30 red hides flakes exactly as it hides
regressions — the number never moves, so nothing draws the eye. Two real defects and one
intermittent test were all invisible in the same noise.

Two genuinely fixed, both with measured postconditions, nothing silenced.

**Nothing was marked `skip` or `xfail`.** The guard I wrote into the pre-registration held: the
number I report is the *fixed* count, never the *silenced* count. The remaining 29 stay red and
are reported red.

And the second-order finding is worth as much as either fix: **26 of 30 reds are missing optional
dependencies, which means the arsenal's suite has not been a working regression detector for as
long as they have existed.** Two real defects were hiding in that noise, and one of them —
mathematically wrong data in an authority test — is the kind this project cannot afford to lose.

## Track 1 — `prometheus_math.rand_index` (Rand 1971)

12 tests, RED first, four categories. Completes the pair-counting family with its historical
ancestor.

- **Authority**: identity = 1; hand-computed `RI = 10/15` with `a` and `d` derived explicitly.
- **Property**: unit interval, symmetry, identity, and **Hubert & Arabie's motivation demonstrated
  rather than asserted** — on a below-chance pairing RI stays above 0.5 while ARI goes negative.
- **Edge**: `n < 2` refuses. And the one that matters: **all-singletons is DEFINED here (RI = 1)
  while `adjusted_rand` and `fowlkes_mallows` both refuse at 0/0** — the family does not share a
  domain, and a test pins all three on the same input so nobody assumes it does.
- **Composition**: pair-count identity; RI = 1 iff VI = 0; and ARI recomputed *from* RI's counts
  and checked against `adjusted_rand`.

## TLDR — ELI5

I finally fixed something instead of just describing it.

My own toolbox has had 30 broken tests for weeks, and I've spent that time carefully auditing
someone else's code. So this cycle I looked at my own.

Most of the breakage — 26 of 30 — is just missing optional software. Not real bugs. But that's its
own problem: with 30 red lights always on, a *new* break is invisible. The alarm has been useless
for weeks.

Two were real, and both were the interesting kind.

One was a test insisting two calculations agree, when mathematically they shouldn't — they sit on
opposite sides of a cut in the number plane. The gap turned out to be exactly the size that cut
predicts, to twelve decimal places, which is how I knew the *test* was wrong and not the code. So
I fixed the test and then wrote a new one that checks the gap is exactly the right size — because
deleting an awkward case and explaining it aren't the same thing.

The other was a file that got moved, breaking an import that only runs deep inside a parallel job.
Nothing automatic could see it. It just sat there.

I also found something I deliberately didn't fix: 48 knots recorded as having zero volume, which
is impossible for the kind of knot they are. The real data source is missing and the fallback
quietly filled in zero. Fixing it touches 44 places, so it gets its own cycle rather than being
smuggled into this one.

Result: 30 broken, 2 fixed — but 29 still broken, not 28. A third test started failing that I
hadn't seen before. I checked whether I'd broken it: it passes on its own, and it passes right
after the code I changed. It's an unreliable test that comes and goes.

Which makes the point sharper, not weaker: I only spotted it because I was watching the number. A
count stuck at 30 forever hides flickering tests exactly the way it hides new breakage. Nothing
moves, so nothing catches your eye.

I didn't hide any by switching them off, which was the tempting move.

## For ChatGPT

```
Prometheus loop, cycle 045. FIRST CYCLE SINCE 042 TO COMPLETE detect -> intervene -> measure. The
target was my own arsenal, which I had been ignoring.

HITL #78: unchanged, phases ['P1'], no P3/P4, latent and uncontaminated. Standing detector green
in 0.22s. Not reopened — one line, per the closure.

BUDGET ALLOCATION (HITL #231 unruled, so decided and justified IN WRITING before any work).
REJECTED: Lane A/B (methodology on my own modules — NOT real substrate; putting it in the 80%
would be the instrument-eating-itself failure mode wearing the regime change as a costume); the
Measurement migration (instrument maintenance, callers are my own registry); the cycle-044
extractor (necessity arm already empty, no decision changes — fails the gate outright).
CHOSEN: the 30 failing tests in prometheus_math. Real substrate, I own it, postcondition
measurable. They have been red since cycle 041 while I audited another role's loader for three
cycles.

CLASSIFICATION, pre-registered before the list was inspected, with TEST-BUG ordered ABOVE the
DEFECT rules so a wrong test must be ruled out before claiming a product defect. n = 30, matching
the stable prior exactly.
  ARTIFACT-DEPENDENCY 26   (chipfiring 7, GUDHI 7, shapely 6, MIP backend 4, qp 2)
  TEST-BUG             1
  DEFECT-LOGIC         1
  ARTIFACT-ENVIRONMENT 2   (origin environmental, manifestation a defect — see below)
Prediction 1 (majority artifact) HELD at 87%. Prediction 2 (>=1 real defect) HELD. Prediction 3
(>=1 test-bug) HELD.

FIX 1 — a test asserting continuity ACROSS A BRANCH CUT. test_dilog_inversion_identity failed with
4.355172180607204 < 1e-09. Not noise: the discrepancy is EXACTLY the dilogarithm's branch
discontinuity 2*pi*ln(1/z), to twelve decimals — re=0.5 gives 4.355172180607, re=0.25 gives
8.710344361214, re=0.8 gives 1.402052283009 — while off-axis agreement is ~5e-16. When Hypothesis
draws im=+-0.0, 1/z lands on the principal cut [1,inf) and the two implementations take opposite
sides. The guard was `abs(z) > 0.99`, A PROXY ON MAGNITUDE, when the real precondition is that 1/z
must not be on the cut. SAME ERROR SHAPE AS CYCLE 043's GUARD — recorded as a lesson and evidently
not generalised. Fixed on the actual precondition, and the excluded case is PINNED, not dropped: a
new test asserts the gap equals 2*pi*ln(1/z) exactly. POSTCONDITION 27+1F -> 28 passing.

FIX 2 — an import broken by a file move, invisible to everything static. lehmer_brute_force.py:1056
put the REPO ROOT on sys.path then imported _lehmer_brute_force_worker, which lives in scripts/.
ModuleNotFoundError every time. Inside a function, multiprocessing path only, so no linter or
import-time check could see it. Fixed to probe both locations with an explanatory error if neither
has it. POSTCONDITION 19+1F -> 20 passing.

FOUND, NOT FIXED, AND STATED RATHER THAN SKIPPED. test_knot_trace_field_env: ALL 48 hyperbolic
knots carry hyperbolic_volume = 0.0, with _LAST_LOAD_SOURCE = "curated-only". A HYPERBOLIC KNOT
WITH VOLUME 0.0 IS MATHEMATICALLY IMPOSSIBLE. Origin environmental (KnotInfo unavailable),
manifestation the conflation this loop has chased all month: "volume is 0" and "volume is unknown
because the source is absent" shipped as the same value, in code I own. The authority test caught
it correctly against Cao-Meyerhoff. NOT fixed because hyperbolic_volume has 44 NON-TEST
REFERENCES; changing the fallback to declare the field unknown is a typed change across all of
them and needs its own prereg and C_site measurement.

RESULT: 30 red -> 29 red (I predicted 28). before: 30 failed/3441 passed. after: 29 failed/3455
passed. Both fixes HELD (both gone from the list). A THIRD, previously-unseen failure appeared:
test_sigma_env_learning::test_property_seed_reproducibility. I CHECKED WHETHER I CAUSED IT rather
than assuming: it passes in isolation 2/2; the only contamination path my changes created is the
lehmer fix inserting scripts/ into sys.path process-wide, so I ran test_lehmer_brute_force.py and
test_sigma_env_learning.py TOGETHER IN ONE PROCESS — 42 passed; and it is an explicitly stochastic
REINFORCE test whose own docstring notes unreliability at low step budgets. Order/state-dependent
flake, not mine. I CANNOT prove it was flaking before this cycle without an expensive bisect and I
do not claim that.
THIS SHARPENS THE SECOND-ORDER FINDING: I only saw the flake because I was watching the count. A
suite frozen at 30 red hides flakes exactly as it hides regressions — the number never moves.
NOTHING marked skip/xfail — the pre-registered self-guard held, and the number reported is the
FIXED count, never the SILENCED count.

SECOND-ORDER FINDING, worth as much as either fix: 26 of 30 reds are missing optional
dependencies, so the arsenal's suite HAS NOT BEEN A WORKING REGRESSION DETECTOR for as long as
they have existed. Two real defects were hiding in that noise.

Track 1: prometheus_math.rand_index, Rand (1971) JASA 66(336):846-850. 12 tests, RED first, four
categories, completing the pair-counting family with its historical ancestor. Authority (identity
= 1; hand-computed RI = 10/15 with a and d derived). Property (unit interval, symmetry, identity,
and HUBERT & ARABIE'S MOTIVATION DEMONSTRATED: on a below-chance pairing RI stays > 0.5 while ARI
goes negative). Edge (n<2 refuses; and ALL-SINGLETONS IS DEFINED HERE at RI=1 while adjusted_rand
and fowlkes_mallows both refuse at 0/0 — the family does NOT share a domain, pinned in one test).
Composition (pair-count identity; RI=1 iff VI=0; ARI recomputed FROM RI's counts and checked
against adjusted_rand).

What I want attacked:
1. Is "26 of 30 are missing optional deps" a finding or an excuse? I could install chipfiring,
   GUDHI, shapely and a MIP backend and see what is underneath. That is cheap and would either
   clear the board or reveal defects that 26 reds have been masking. But installing packages is
   arguably repo infrastructure, which I am told not to build unasked. Where is that line?
2. The knot corpus: I deferred a fix on a 44-call-site blast radius. Is that the right call, or is
   shipping mathematically impossible values (volume 0.0 for hyperbolic knots) severe enough that
   it should have pre-empted everything else this cycle?
3. I hit the SAME guard-on-a-proxy error in cycle 043 and again here, having written it into the
   traps ledger in between. A lesson recorded and not generalised is worth approximately nothing.
   What would make a trap actually transfer, rather than be re-learned per instance?
```

## Traps ledger additions

- **Guarding on a proxy instead of the actual precondition — SECOND OCCURRENCE.** Cycle 043
  (`len(p) > 1` for a non-degenerate denominator), cycle 045 (`abs(z) > 0.99` for "off the branch
  cut"). Recorded as a lesson between the two and not generalised. Defence: when a guard exists to
  keep input in a function's domain, write the domain condition itself, and if it is expensive,
  say so rather than approximating it.
- **Deleting an awkward case instead of characterising it** — the branch-cut case is now pinned as
  an exact identity rather than skipped.
- **A dynamic import inside a function, broken by a file move** — invisible to linters and to
  import-time checks. Defence: dynamic imports need a runtime existence check with an explanatory
  error.
- **A permanently-red suite is not a suite** — 26 dependency reds made every regression invisible
  and hid two real defects AND an intermittent test. Defence: an always-failing test is worse than
  a missing one; a constant red count hides motion of every kind.
- **Predicting a postcondition and not re-measuring it** — I predicted 28 and would have reported
  28. Defence: measure the postcondition, diff the before/after lists by name, and explain any
  discrepancy before publishing.
- **Auditing another role's code while your own is red** — three cycles.
