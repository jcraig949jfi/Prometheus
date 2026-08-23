# Cycle 050 — PRE-REGISTRATION: H1 self-calibration, measured on this loop

**Committed BEFORE extracting any prediction outcome.**
**Repairs O-1** from cycle 049's audit: Band H was never built and never withdrawn.

## Why this is the Band H move and not a substitute for it

Canon §6 defines **H1 — REFLECTIVE MODELING** as a system that *"maintains a calibrated
model of its **own failure distribution** and of other reasoners' failure distributions ...
and allocates search, verification, and delegation accordingly."*

The charter allows theory to substitute for building in the upper bands. It does not require
it. The cheapest **falsifiable** version of H1's first clause needs a reasoner with a complete,
timestamped record of pre-registered predictions and their outcomes. **This loop is that
reasoner** — 49 cycles, prereg files committed before measurement, outcomes recorded after.

The other-reasoner clause is **out of scope** and stays hypothesis: canon puts it behind the
model zoo, which has not run. Claiming H1 from the self half alone would be the same
part-for-whole error cycle 049 caught. This measures **H1a** and names H1b unbuilt.

## The measurement

Enumerate every **pre-registered prediction** in `techne/loop/` — prereg files in
`rung_notes/` plus predictions stated in cycle files *before* their measurement — and score
each as `HELD` or `FALSIFIED` against the outcome recorded in the same corpus.

## The statistic and its base rate

`p_held` = fraction of pre-registered predictions that held.

**The counter-baseline** (`feedback_counter_baseline_discriminator`): a reasoner with *no*
model of its own failure distribution predicts its own predictions will hold — `p̂ = 1.0`,
always. Calibration is only demonstrated if my **stated** confidence separates the ones that
held from the ones that didn't. A high `p_held` alone is NOT evidence of calibration; it is
equally consistent with only ever pre-registering things I already knew.

## Predictions, committed before extraction

1. `p_held` lands in **[0.55, 0.85]**. Below 0.55 I am guessing; above 0.85 I am
   pre-registering only safe bets, which is the more likely failure and the harder to see.
2. **At least 3 cycles** record a prediction falsified *in the direction of my own record
   being better than predicted* (049 had two). That asymmetry, if present, is the signal that
   I model myself pessimistically rather than accurately — a *mis*-calibration, not a virtue.
3. **I will not find a single instance** of a stated per-prediction confidence level.
   Everything is asserted flat. If so, `p_held` cannot be a calibration curve at all — only a
   hit rate — and **H1a fails on instrument grounds regardless of the number.**

## The kill test

**H1a is NOT demonstrated if prediction 3 holds.** Calibration means the confidence tracks
the outcome. A corpus of flat, unquantified assertions has no confidence axis to track, so no
value of `p_held` can rescue it. In that case the honest verdict is: *this loop pre-registers
but does not calibrate*, and the H1a build-debt is a **confidence field on every prediction**,
which is cheap and which I do not currently have.

## Self-guard

Same as cycle 049: every scored prediction must cite the file and the line that records its
outcome. A prediction I score from memory of what I meant is excluded from the count.

*— Techne, cycle 050, before extracting.*
