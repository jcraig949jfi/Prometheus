# Cycle 052 — the inherent-limits sweep: #298 answered AFFIRMATIVELY

Prereg `5d326dbb`, committed before grepping. **Kill test did not fire** — a `SUSPECT` was
found, and unlike prediction 4 expected, it was **confirmed as a real defect inside the cycle**.

## Predictions

| # | prediction | confidence | outcome |
|---|---|---|---|
| 1 | >= 8 limit claims exist | moderate | **FALSIFIED — 22 hits, but only ~6 are genuine limit CLAIMS** |
| 2 | >= 1 `SUSPECT` | moderate-to-high | **HELD** |
| 3 | `UNGROUNDED` > `GROUNDED` | low-to-moderate | **FALSIFIED — the opposite** |
| 4 | no `SUSPECT` confirmed as a bug this cycle | moderate | **FALSIFIED — confirmed in one measurement** |

Prediction 1 is scored FALSIFIED on the honest reading: the grep returned 22 lines, but most
are ordinary caveats ("caller is expected to check", "HEURISTIC, not a real catalog query")
rather than claims that a limit is *inherent*. Counting grep hits would have let me claim a
hit; counting actual claims does not.

## The confirmed defect — `lehmer_brute_force._verify_mahler_mpmath`

**The claim** (`lehmer_brute_force.py:924`, `lehmer_path_a.py:12`):
> *"Without high-precision certification we cannot decide H5 vs H2 cleanly"* — 17 of 43 band
> entries carry `verification_failed=True` because `mpmath.polyroots` at dps=30 returned NaN,
> and the run is marked **INCONCLUSIVE** as a result.

**Why it is `SUSPECT`, not `GROUNDED`:** the verifier escalates precision three times
(dps 15/30/60, extraprec 50/100/200, maxsteps 300/600/1000) and **never factors**. Yet
`lehmer_path_a.py`'s own docstring names the mechanism exactly:

> *"by **factoring the polynomial first** so that `polyroots` only has to handle each
> irreducible factor in isolation (rather than fighting **clustered repeated unit-circle
> roots** in the unfactored deg-14 polynomial)"*

**The witness, measured this cycle** — Lehmer × (x+1)², degree 12, double root at −1 on the
unit circle, true M = M(Lehmer) = 1.1762808182599176:

```
escalation ladder, no factoring   ->  nan
squarefree factoring first        ->  1.1762808182599176   (exact)
```

**More precision does not fix a clustered repeated root; factoring does.** The NaNs are not a
precision limit — they are the eps^(1/m) family of defects this loop has now chased through
`mahler_measure`, `is_cyclotomic`, `house`, and the batch path.

**Consequence.** Those NaNs are what produce `INCONCLUSIVE`. A verdict of "we cannot decide
H5 vs H2" was written as an epistemic limit of the search and is at least partly an artifact
of an unfactored verifier. Path A exists as a *workaround* for a defect that could have been
fixed in the verifier — and Path A knew the mechanism, in writing, at the time.

**Not fixed this cycle.** `lehmer_brute_force` is a substrate module whose verdicts are
published; changing its verifier changes historical INCONCLUSIVE verdicts and needs its own
prereg and blast-radius pass. Queued, not smuggled (cycle 045's rule).

## The `GROUNDED` majority — prediction 3 falsified in the good direction

The TDD-forged modules cite theorems and bound their claims correctly. `adjusted_rand.py`'s
refusal to clamp below-chance scores, `calibration.py`'s Brier skill baseline,
`catalog_consistency.py`'s *"we cannot verify what's NOT in any catalog"* — all correct
statements about genuine epistemic limits, all citing the reason. `techne/lib/lll_reduction.py`
labels a real cypari behaviour. The one **UNGROUNDED** hit is
`tier_1_claim_runner.py:766`'s bare *"fundamental limitation"* comment, which is about a paper's
content rather than a tool's accuracy.

**The class is not endemic.** But it is not empty either, and the one instance it does contain
was load-bearing for a published verdict.

## What makes the difference, stated as a rule

Both cycle 047's claim and this one share a shape: **a limit asserted from a witness whose
structure was never factored.** The grounded claims all name *why* — a theorem, a missing
population, a library's documented behaviour. The suspect ones name only *that it happened*.

**Rule: a limit claim must state the mechanism, not just the observation.** "polyroots returned
NaN" is an observation. "polyroots cannot resolve clustered repeated roots at any precision" is
a mechanism — and the moment you can state it, you can also test whether factoring removes it.

*— Techne, cycle 052.*
