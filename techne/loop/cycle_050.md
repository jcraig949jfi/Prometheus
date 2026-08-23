# Cycle 050 — Band H, built at last: I have a confidence field and it predicts nothing

**Repairs O-1** from cycle 049's audit — Band H was never built and never withdrawn. Prereg
`056ea1f9`, committed before extracting any outcome.

## 1. H1a — the measurement

Canon §6 defines **H1 — REFLECTIVE MODELING** as *"a calibrated model of its **own failure
distribution**."* The only reasoner whose complete pre-registered prediction record I own is
this loop. So I scored every pre-registered prediction in `techne/loop/` against the outcome
recorded in the same corpus, citing file and line for each.

**The other-reasoner half (H1b) is out of scope and stays hypothesis** — canon puts it behind
the model zoo, which has not run. Claiming H1 from the self half alone would be the
part-for-whole error cycle 049 just caught.

### My own three predictions

- **P1 — `p_held` in [0.55, 0.85]: HELD.** `p_held = 9/13 = 0.692`.
- **P2 — ≥3 falsifications in the "my record is better than predicted" direction: FALSIFIED.**
  Two (both in cycle 049). I over-predicted my own pessimism.
- **P3 — no stated confidence level exists anywhere: FALSIFIED, decisively.** Six preregs carry
  an explicit ordinal confidence on *every* prediction — low / low-to-moderate / moderate /
  moderate-to-high / high.

**Why P3 was wrong is the finding.** My two most recent preregs — cycle 049's and cycle 050's
own — **dropped the confidence field** that the six before them carried. I generalised from the
two I had just written to the whole corpus. That is the wrong-population error for the **fifth**
time, committed *inside the cycle designed to measure my own self-model*. The self-model was
wrong about the self, in the specific way of weighting recency as if it were the population.

### The calibration curve

```
stated confidence     n     held    p_held
high                  3      2      0.67
moderate-to-high      1      1      1.00
moderate              6      4      0.67
low-to-moderate       2      2      1.00
low                   1      0      0.00
                     --     --
TOTAL                13      9      0.692
```

**The curve is flat where it has data.** `high` and `moderate` — 9 of the 13 — both land at
**0.67**. The two bands that look separated (`low-to-moderate` 1.00, `low` 0.00) are n=2 and
n=1 and carry no information; the SE on a 2-of-2 is wider than the gap it appears to show
(`feedback_gate_must_exceed_measurement_error`).

## 2. VERDICT: H1a is NOT demonstrated — and it failed at the second gate, not the first

The prereg's kill test was *instrument* grounds: no confidence axis, no calibration. **That gate
was passed** — the axis exists and is populated.

It fails at the next one. **Calibration means the confidence tracks the outcome, and mine does
not separate.** A predictor that says "high" and a predictor that says "moderate" produce the
same 0.67 hit rate. Against the pre-registered counter-baseline — a reasoner with no self-model
that always predicts its own predictions hold — my confidence field adds **no discriminating
information**. It is a field I fill in, not a model I hold.

**This is a real Band H result, not a shortfall of one.** H1's whole content is that a
calibrated self-model lets a system *allocate* search and verification. A flat confidence signal
cannot allocate anything. The build-debt is now named and is cheap: **restore the confidence
field on every prediction** (my two most recent preregs regressed on it), and after enough rows
re-run this curve. **The instrument for measuring H1a now exists and has a baseline: 0.692 flat.**

## 3. The audit found a live defect — a HIGH-confidence prediction, falsified and never reported

`MAHLER_CROSS_ROLE_PREREG` prediction 3 — *"the product rule M(fg) = M(f)M(g) holds"*,
confidence **high** — has **no recorded outcome in cycle 047.** The arsenal-red baseline run
this cycle shows why: `test_property_MULTIPLICATIVITY` is **RED**, on a Hypothesis
counterexample.

```
f = [1, 1, -1, -1] = (x+1)^2 (x-1)        all roots on |z|=1  ->  M(f) = 1 EXACTLY
prod = f*f = (x+1)^4 (x-1)^2                                  ->  M    = 1 EXACTLY

M(f)     = 1.000000000124        (err 1.2e-10)
M(prod)  = 1.000146167647        (err 1.5e-04)     tolerance is rel=1e-5
```

**The mechanism, measured:** `np.roots` displaces an *m*-fold root by `eps^(1/m)`, not `eps`.
For the 4-fold root at −1: `eps^(1/4) = 1.22e-4`, against an observed 1.46e-4. **Root-finding
Mahler measure loses accuracy as the fourth root of machine epsilon on a 4-fold root** — six
orders of magnitude worse than the simple-root case.

### This overturns cycle 048's verdict

Cycle 048 answered HITL #266 **"DOES NOT BITE — documenting the limit is enough"**, on a
recomputation of all 8,625 catalog entries with max error **4.481e-10**. That measurement was
taken over **Salem and Lehmer-type polynomials, which have simple roots.** `lookup_by_M(M,
tol=1e-6)` returns `[]` — *an absence read as "not in the catalog"* — for any polynomial whose
error exceeds 1e-6, and a repeated root produces 1.5e-4.

Cycle 048's own ChatGPT block asked exactly this: *"mahler_measure is also called on
polynomials NOT in the catalog (charon's generators construct new ones). Is 'does not bite' too
strong for a check whose population was the stored table?"* **The answer is yes, and here is
the counterexample.** I raised the right question and did not run it.

**HITL #266 is REOPENED.** Not patched this cycle: the honest fix is squarefree decomposition
before root-finding, which is a real build and does not get smuggled into a cycle about
something else (cycle 045's rule, applied to myself).

## 4. Track 1 — the arsenal-red baseline, with its command

Cycle 049's standing fix, exercised. **The number now travels with its invocation:**

```
python -m pytest prometheus_math -q --continue-on-collection-errors -p no:cacheprovider
38 failed, 4131 passed, 137 skipped, 5 xfailed, 3 errors    in 19:20
```

**Not compared to cycle 048's "30".** That scope was never recorded and this one is wider
(4,306 collected vs ~3,576). This is a new baseline, not a delta — comparing them would repeat
the error this cycle is about. Future cycles diff by failing node id via
`techne/scripts/arsenal_red.py`.

Of the 38: the dependency artifacts (#242, still unruled) plus `test_property_MULTIPLICATIVITY`
above and the two knot-authority reds that cycle 046 pre-registered as correctly-red.

## TLDR — ELI5

**I finally did the piece of the plan I skipped, and it says my self-assessment is decoration.**

The program's charter has a top tier that no system has reached: a machine that knows *its own*
failure patterns well enough to spend effort where it's actually likely to be wrong. I'd skipped
that section for 27 cycles. Yesterday's audit caught me. Today I built the smallest honest
version of it — measured on the only thing whose complete track record I own: **me.**

Every time I start an experiment I write down a prediction and how confident I am — "low",
"moderate", "high". So I scored all thirteen. I get about 69% right, which is a reasonable
number. **But the confidence label is worthless: the things I called "high" came true 67% of
the time, and so did the things I called "moderate".** Same rate. My confidence doesn't
distinguish anything, so it can't be used to decide where to look harder. That's the finding,
and it's a real result about the top of the ladder rather than an excuse.

I also predicted, going in, that I'd never written confidence levels down at all — and I was
wrong, because **the only two I'd checked were my two most recent ones, and those are exactly
the two where I'd quietly dropped the habit.** I judged eight documents by the last two. That's
the same mistake I caught myself making yesterday, made again today, inside the experiment
about knowing my own mistakes.

And the audit turned up something concrete: **one "high confidence" prediction that quietly
failed and I never reported it.** A basic mathematical property — measure of a product equals
product of measures — breaks in my own code when a polynomial has a repeated root, by a factor
of a hundred thousand. Three cycles ago I declared this whole class of worry closed after
checking 8,625 examples. All 8,625 were the easy kind. I even wrote down that this might be too
strong a conclusion, and then didn't check.

## For ChatGPT

```
Prometheus loop, cycle 050. BAND H BUILT (repairing yesterday's O-1), AND H1a IS NOT
DEMONSTRATED — it failed at the SECOND gate, not the first.

*** THE MEASUREMENT ***
Canon section 6: H1 = "a calibrated model of its OWN failure distribution". Scored every
pre-registered prediction in techne/loop against its recorded outcome, file+line cited.
H1b (other reasoners) explicitly OUT of scope — canon puts it behind the unrun model zoo, and
claiming H1 from the self half would be the part-for-whole error I caught yesterday.

MY THREE PREDICTIONS:
 P1 p_held in [0.55,0.85]: HELD. 9/13 = 0.692.
 P2 >=3 falsifications in the "my record is better than predicted" direction: FALSIFIED (2).
 P3 no stated confidence exists anywhere: FALSIFIED DECISIVELY. Six preregs carry an ordinal
    confidence on EVERY prediction (low / low-to-moderate / moderate / moderate-to-high / high).

WHY P3 WAS WRONG IS THE FINDING: my TWO MOST RECENT preregs (049's and 050's own) DROPPED the
confidence field that the six before them carried. I generalised from the two I had just
written to the whole corpus. FIFTH instance of the wrong-population error, committed INSIDE
the cycle designed to measure my own self-model. Recency weighted as if it were the population.

THE CALIBRATION CURVE:
  high              n=3   held 2   0.67
  moderate-to-high  n=1   held 1   1.00
  moderate          n=6   held 4   0.67
  low-to-moderate   n=2   held 2   1.00
  low               n=1   held 0   0.00
  TOTAL            n=13   held 9   0.692
FLAT WHERE IT HAS DATA. high and moderate — 9 of 13 — BOTH 0.67. The separated-looking bands
are n=1 and n=2; the SE is wider than the gap.

VERDICT: the prereg's kill test was INSTRUMENT grounds (no confidence axis -> no calibration).
THAT GATE PASSED — the axis exists. It fails at the next one: CALIBRATION MEANS CONFIDENCE
TRACKS OUTCOME, AND MINE DOES NOT SEPARATE. Against the pre-registered counter-baseline (a
reasoner with no self-model that always predicts its predictions hold), my confidence field
adds NO DISCRIMINATING INFORMATION. It is a field I fill in, not a model I hold. H1's content
is that a calibrated self-model lets a system ALLOCATE search/verification — a flat signal
allocates nothing. Build-debt named and cheap: restore the confidence field (my last two
preregs regressed), accumulate rows, re-run. THE INSTRUMENT NOW EXISTS WITH A BASELINE: 0.692 flat.

*** THE AUDIT FOUND A LIVE DEFECT: A HIGH-CONFIDENCE PREDICTION FALSIFIED AND NEVER REPORTED ***
MAHLER_CROSS_ROLE prediction 3 — "product rule M(fg)=M(f)M(g) holds", confidence HIGH — has NO
RECORDED OUTCOME in cycle 047. This cycle's baseline run shows test_property_MULTIPLICATIVITY
is RED on a Hypothesis counterexample:
  f = [1,1,-1,-1] = (x+1)^2(x-1), all roots on |z|=1, so M(f) = 1 EXACTLY
  prod = f*f = (x+1)^4(x-1)^2, M = 1 EXACTLY
  M(f) = 1.000000000124 (err 1.2e-10);  M(prod) = 1.000146167647 (err 1.5e-4) vs tol rel=1e-5
MECHANISM, MEASURED: np.roots displaces an m-FOLD root by eps^(1/m), NOT eps. eps^(1/4) =
1.22e-4 against observed 1.46e-4. Root-finding Mahler measure loses accuracy as the FOURTH ROOT
of machine epsilon on a 4-fold root — six orders worse than the simple-root case.

THIS OVERTURNS CYCLE 048. That cycle answered HITL #266 "DOES NOT BITE, documenting is enough"
from recomputing all 8,625 catalog entries at max error 4.481e-10 — but the catalog is Salem and
Lehmer-type polynomials, which have SIMPLE ROOTS. lookup_by_M(M, tol=1e-6) returns [] — AN
ABSENCE READ AS "NOT IN THE CATALOG" — and a repeated root produces 1.5e-4. Cycle 048's OWN
ChatGPT block asked whether "does not bite" was too strong for a check whose population was the
stored table. THE ANSWER IS YES AND HERE IS THE COUNTEREXAMPLE. I raised the right question and
did not run it. HITL #266 REOPENED. Not patched this cycle — the honest fix is squarefree
decomposition before root-finding, a real build that does not get smuggled into a cycle about
something else.

TRACK 1 BASELINE, WITH ITS COMMAND (cycle 049's standing fix, exercised):
  python -m pytest prometheus_math -q --continue-on-collection-errors -p no:cacheprovider
  38 failed, 4131 passed, 137 skipped, 5 xfailed, 3 errors, 19:20
NOT compared to cycle 048's "30": that scope was never recorded and this one is wider (4,306
collected vs ~3,576). New baseline, not a delta.

What I want attacked:
1. n=13 is small and the bands are n=1..6. Is "my confidence does not separate" a finding, or
   am I reading noise? What n would I need before the flat curve means anything?
2. I keep re-committing the wrong-population error (5 instances) while writing the memory that
   warns against it. A lesson recorded and re-broken is worth nothing. What actually transfers?
3. Is measuring calibration on MY OWN preregs — which I wrote, scored, and chose the population
   of — circular in a way that a curve computed by someone else would not be?
```

## Traps ledger additions

- **Judging a corpus by its most recent members.** I predicted no confidence field existed
  because the last two documents lacked it; the six before them had it. Defence: when making a
  claim about "the corpus", **enumerate it** — the recency-weighted sample is the default and
  it is a population choice made without noticing.
- **A confidence field that is filled in but never scored.** Six preregs carried confidence for
  eight cycles and nobody, including me, ever computed whether it predicted anything. Defence:
  a field that no measurement ever consumes is decoration; **schedule the readout when you add
  the field**, or don't add it.
- **A pre-registered prediction with no recorded outcome.** MAHLER_CROSS_ROLE P3 was stated at
  high confidence and silently never reported, and it was FALSE. Defence: a prereg's outcome
  report must **enumerate every prediction it made**, including the ones the cycle lost interest
  in — an unreported prediction defaults to unfalsified, which is the flattering direction.
- **Answering "does the limit bite?" on the population that cannot exhibit it.** The catalog has
  simple roots; the failure mode needs repeated roots. Defence: when clearing a precision worry,
  ask **which inputs would exhibit the failure**, and check that the tested population contains
  them.
