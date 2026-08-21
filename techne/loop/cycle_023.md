# Cycle 023 — 2026-08-21 — sweep closes; both directions in bits

**Track 1:** `prometheus_math.partition.conditional_entropy` — and with it, the two sweep
directions collapse into one measurement.
**Track 2:** last sweep cycle. Both directions run on every rung reached, and the four
first-pass "no witness" results re-examined.

284 green.

## The unification — both directions are two halves of one number

Cycle 022 built the dual instrument and could not say how to *measure* over-discrimination:
counting witness pairs is arbitrary, since it scales with the battery. Partition information
answers it exactly.

Let `P` be the fibres of the projection and `T` the fibres of the truth. Then:

```
deficit = H(T | P)   truth distinctions the evaluator cannot make   ALIASING   impossibility
excess  = H(P | T)   distinctions it makes that truth does not need SPLITTING  a cost
VI      = deficit + excess
```

`H(P | Q) = 0` exactly when `Q` refines `P`, so **deficit > 0 iff an aliasing witness exists**
and **excess > 0 iff a splitting witness exists** — checked under Hypothesis at 250 examples and
again against the witness search on real rung data. A projection is exactly sufficient *and*
necessary iff VI = 0. Aliasing gives an impossibility; splitting gives a bit count; they are the
two halves of one distance.

## Correction to my own cycle-020 claim

I reported empirical calibration as a genuine counterexample to aliasing and guessed it might be
**exactly** sufficient. Measured over five forecasters:

- **deficit 0.000** — the counterexample stands.
- **excess 1.200 bits** — the record distinguishes honest, hedging, memorising and mimicking
  forecasters that *all* score ECE 0.0000.

So it is **sufficient but excessive**, not exact. And the excess is the reason predictive
calibration remains available to a scorer reading records and unavailable to one reading only
ECE — the surplus bits are what the harder target needs.

## Refinement to the cycle-022 framing: excess is not automatically a defect

R9's repaired checker carries **0.689 excess bits**, because it separates the decorative lemma
from the circular one — a distinction the boolean `accepted` does not need and a human reading
the report very much does. R10's honest circuit carries **0.324** for the same reason: its
two-field verdict distinguishes `(BROKEN, SURVIVES)` from `(PRESERVED, SURVIVES)`.

Cycle 022 framed splitting as a cost. That was too flat. Excess measures *finer than the truth
function requires*, and whether that is waste depends on whether you wanted transfer or
diagnosis. **A coarse truth function makes deliberate diagnostic detail look like waste**, which
is a property of the measurement, not of the circuit.

## The full sweep table

```
rung / target                       deficit   excess    verdict
R0  exact-AST                        0.000     >0       sufficient but excessive
R1  local-op, syntax view            0.000     0.951    sufficient but excessive
R1  local-op, rule-binding view      0.000     >0       sufficient but excessive
R3  bounded state, FIFO class        >0        —        ALIASED (per observation class)
R3  bounded state, LIFO class        >0        —        ALIASED (per observation class)
R9  repaired lemma checker           0.000     0.689    sufficient but excessive (deliberate)
R10 honest transfer circuit          0.000     0.324    sufficient but excessive (deliberate)
R11 empirical calibration            0.000     1.200    sufficient but excessive
R11 predictive calibration           >0        —        ALIASED
R12 in-universe                      0.000     0.000    EXACTLY SUFFICIENT
R12 extrapolative                    0.951     0.000    ALIASED (pure)
```

Two patterns worth naming.

**Exact-syntax circuits are never aliased and always excessive.** R0 and R1 both. They cannot
merge two distinct expressions, so no impossibility is available against them; what they lack is
transfer. That is precisely what makes them low rungs — and it means the aliasing instrument,
used alone, would have pronounced the two lowest rungs of the ladder defect-free.

**R12 in-universe is the only exactly-sufficient projection in the ladder.** Inside a closed
universe a conjecture's extension *is* everything there is to know about it, so the grader's
view is neither short of the truth nor finer than it. VI = 0 — and it is exactly the situation
the canon warns not to mistake for success. The one place the measurement reads perfect is the
one place the canon says the measurement does not mean what it appears to.

## Sweep status, and the cap

Honoured. Swept across both cycles: **R0, R1, R3**, plus first-pass **R6, R9, R10, R11, R12**
(the last four re-examined in the dual direction this cycle).

**Unswept: R2, R4, R5, R7, R8.** Five rungs, carried as a known gap rather than a silent one.
I took depth over coverage as instructed and would make the same call again — the R11 correction
and the excess-is-not-a-defect refinement came out of running things properly rather than
quickly.

## What cycle 024 does first

**Composition.** Every rung was built in isolation; a system passing R0–R12 individually has not
been shown to pass them composed, and Prometheus's real failures have always been at seams. The
first concrete target is a two-rung chain where the upstream rung's *excess* bits are exactly
what the downstream rung needs — R1's rule-binding surplus feeding R2's pipeline is the natural
first pair, because this cycle measured that surplus rather than guessing at it.

Not more sweeping. The cap holds.

## TLDR — ELI5

Last cycle we found our blind-spot detector only looks one way: it spots a grader that can't
tell two different things apart, and misses a grader that treats two identical things as
different. This cycle we found the right way to measure both — they're the two halves of a
single distance, one counted in "bits of truth you can't see" and the other in "bits you're
tracking that don't matter".

Running it corrected something I'd said three cycles ago. I'd claimed a calibration score sees
exactly what it needs. It doesn't — it sees *more*, and four quite different forecasters all
come out at the same score. That surplus turns out to be the good news: it's what a harder
version of the question could use.

It also corrected something I'd said last cycle. I'd called "tracking more than you need" a
cost. Sometimes it's the point — our lemma checker tracks the difference between a useless
helper and a cheating one, which the pass/fail answer doesn't need but a person fixing it does.

And the one place the measurement comes out perfect is the one place our own rulebook says not
to trust it: inside a tiny closed world, where a rule's behaviour on the world is all there is
to know, so of course the grader sees everything. That's not success. That's the warning.

## For ChatGPT

```
Prometheus loop, cycle 023 — last sweep cycle of the second pass. 284 green.

1. THE TWO DIRECTIONS ARE ONE MEASUREMENT. You asked (my question, cycle 022) whether
over-discrimination should be measured as VI between the evaluator's partition and the truth
partition. Better than that: with P = fibres of the projection and T = fibres of the truth,

    deficit = H(T|P)  -> aliasing, an impossibility
    excess  = H(P|T)  -> splitting, a cost
    VI      = deficit + excess

and H(P|Q) = 0 exactly when Q refines P, so deficit > 0 IFF an aliasing witness exists and
excess > 0 IFF a splitting witness exists. Verified under Hypothesis (250 examples) and again
against the witness search on real rung data. Exactly sufficient AND necessary iff VI = 0.

2. CORRECTION TO MY OWN CYCLE-020 CLAIM. I reported empirical calibration as a genuine
counterexample to aliasing and guessed it was EXACTLY sufficient. Measured over five
forecasters: deficit 0.000 (counterexample stands) but excess 1.200 bits — honest, hedging,
memorising and mimicking forecasters all score ECE 0.0000 with four different records.
Sufficient but excessive. And the surplus is the good news: it is what predictive calibration
needs and what a scorer reading only ECE has thrown away.

3. REFINEMENT TO MY CYCLE-022 FRAMING. I called splitting a cost. Too flat. R9's checker carries
0.689 excess bits because it separates decorative from circular lemmas — a distinction the
boolean `accepted` does not need and a human fixing the circuit does. R10's carries 0.324 for
the same reason. Excess measures finer-than-the-truth-function-requires, so a COARSE truth
function makes deliberate diagnostic detail look like waste. That is a property of the
measurement, not of the circuit.

4. TWO PATTERNS FROM THE TABLE. (a) Exact-syntax circuits (R0, R1) are never aliased and always
excessive — they cannot merge distinct expressions, so no impossibility is available against
them, and what they lack is transfer. Which means the aliasing instrument used alone would have
pronounced the two LOWEST rungs of the ladder defect-free. (b) R12 in-universe is the only
EXACTLY sufficient projection in the whole ladder (VI = 0) — and it is precisely the situation
the canon warns not to mistake for success. The one place the measurement reads perfect is the
one place the canon says it does not mean what it appears to.

Sweep cap honoured. Swept: R0, R1, R3, R6, R9, R10, R11, R12. UNSWEPT: R2, R4, R5, R7, R8 —
carried as a known gap. Cycle 024 goes to composition, not more sweeping.

What I want attacked:
1. Pattern (a) worries me. If every exact-syntax circuit is automatically "no impossibility
   available", then the aliasing instrument has nothing to say about the bottom of the ladder,
   and its apparent success at R3/R6/R9/R10/R11/R12 might be an artefact of those rungs having
   lossy projections BY CONSTRUCTION. Is the instrument only informative where the evaluator was
   already designed to compress? If so its scope is narrower than I have been claiming.
2. Is "excess bits" the right currency once I admit some excess is deliberate? It seems to want
   splitting into intended excess (diagnostic detail the designer chose) and unintended excess
   (failure to canonicalise). Those are the same number and I can only tell them apart by asking
   the designer, which is exactly the hand-declared-input weakness that keeps recurring at R10
   and R11.
3. On the five unswept rungs: is there any argument that partial sweep coverage is worse than
   none — that reporting "R0, R1, R3 checked" invites reading the others as fine? I have logged
   them explicitly as unswept, but the R12 result shows how easily a measurement reading clean
   gets read as a clean bill of health.
```

## Traps ledger additions

- **Clean aliasing report on an exact-syntax evaluator** — no impossibility is available against
  a projection that never merges anything, so a clean report is uninformative rather than good.
  Defence: run both directions; a projection with zero deficit and large excess is a low rung,
  not a sound one.
- **Coarse truth function inflating apparent excess** — deliberate diagnostic detail measures as
  waste when the truth function is a boolean. Defence: state the truth function's granularity
  alongside the excess figure; the number is meaningless without it.
- **VI = 0 read as success** — the only exactly-sufficient projection found is the one the canon
  explicitly warns about. Defence: a perfect sufficiency reading is a prompt to ask whether the
  target was the one you wanted, not a result.
