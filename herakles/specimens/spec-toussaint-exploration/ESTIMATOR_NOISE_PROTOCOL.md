# ESTIMATOR_NOISE_PROTOCOL

**Frozen 2026-09-03, before any execution.** Required by the HC-T01 execution
directive section 16.

## Why this exists

Toussaint reported no uncertainty of any kind for the 2000-sample detector, in
any figure, in any paper, ever. Experiment 1 is a single run. There is
therefore no historical noise floor to inherit, and every threshold in HC-T01
would otherwise be chosen without reference to its own standard error. This
programme has already burned two passes that way and once set a gate above the
maximum attainable value.

## Protocol

At a fixed frozen population `P`, holding the population and the probe setting
constant and varying only the detector's own random stream:

1. Run the detector `R = 20` times with 20 independent detector seeds.
2. For each statistic, record the 20 population-mean values.
3. Report the mean, the standard deviation, and the standard error
   `sd / sqrt(R)` of the population mean.

**The reported noise floor for a statistic is the standard deviation across
detector seeds of the population-mean value at the historical sample count of
2000.** That is the quantity a single historical measurement would have had,
and it is the quantity every HC-T01 effect is compared against.

## Where the protocol is applied

    N1  common initial population, generation 0, both probe settings
    N2  an evolved beta_on population at generation 500
    N3  an evolved beta_off population at generation 500

N2 and N3 are required because estimator noise is not constant across
populations. A converged, low-variation population and a structurally diverse
one do not have the same sampling variance, and a noise floor measured only at
generation zero would understate the noise exactly where the interesting
comparison lives.

## Sample-count sweep, diagnostic only

At the same three populations, run the detector at
`S in {125, 250, 500, 1000, 2000, 4000, 8000}`, 20 seeds each, and report the
standard deviation of each statistic as a function of `S`.

This answers a question about the historical instrument that Toussaint never
asked: was 2000 samples adequate for the statistics he reported? The answer is
a finding about the instrument regardless of the missing-cell outcome.

**The sweep is diagnostic and may not be used to select an operating point.**
HC-T01 runs at `S = 2000`, the historical value, and only at that value.
Directive section 16 is explicit: do not increase samples until the historical
detector gives the desired result. A modernised estimator is a later
experiment, not this one.

## The gate

For each primary quantity `H(t)` and `E(t)`, compute

    resolvability = |observed effect| / noise_floor

where `noise_floor` is the standard deviation across detector seeds of the
population-mean statistic, taken at the population type most relevant to the
comparison, and reported explicitly.

    resolvability < 1     the historical instrument cannot see this effect
    1 <= resolvability < 2  marginal; reported as such, never as a positive
    resolvability >= 2    resolvable by the historical instrument

If the primary effects are not resolvable at the historical sample count, the
verdict is `HC_T01_HISTORICAL_DETECTOR_INADEQUATE` and kill condition K9 fires.
That is a real result about the 2003 instrument and it is reported as one, not
worked around.

## Separating estimator noise from run-to-run variance

Two variance components must not be confused:

- **Estimator noise**: same population, different detector seed. Measured by
  this protocol.
- **Run-to-run variance**: different evolutionary replicate. Measured across
  the 30 run pairs and used for the confidence intervals and permutation tests
  in `OPERATOR_HISTORY_DID_SPEC.md`.

Run-level inference uses run-to-run variance. The estimator noise floor is a
separate, additional gate: an effect must both survive run-level inference and
exceed the noise floor. Passing only one of the two is reported as marginal.
