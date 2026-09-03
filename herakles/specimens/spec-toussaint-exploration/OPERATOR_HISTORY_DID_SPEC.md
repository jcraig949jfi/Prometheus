# OPERATOR_HISTORY_DID_SPEC

**Frozen 2026-09-03, before any execution.** Required by the HC-T01 execution
directive sections 3, 4, 5, 7, 19 and 20.

## Notation

`D(P, b)` is the detector applied to frozen population `P` under probe setting
`b`, as defined in `FROZEN_POPULATION_PROBE_SPEC.md`. `P_on,t` is the
population at generation `t` of a run whose evolutionary history had
`beta = 0.1`. `P_off,t` is the population at generation `t` of a run whose
history had `beta = 0`. Both are at the same `alpha`.

## The three quantities, and what each is worth

### O1, the mechanical contrast

    M(P, t) = D(P_t, beta_on) - D(P_t, beta_off)

Computed within a single run, on a single frozen population. `M(P_0)` at
generation zero is the direct mechanical operator effect on the common initial
population. **This is calibration. It is not a result.** It is expected to be
non-zero and a non-zero value proves only that turning the knob turns the knob.

### O2, the same-probe evolutionary-history contrast

    H(t) = D(P_on,t, beta_probe) - D(P_off,t, beta_probe)

with `beta_probe = 0.1` frozen. Both populations meet the identical variation
operator at measurement time. Any difference is a difference between the
populations, not between the measurements. **This is the first non-tautological
quantity.**

### O3, the difference-in-differences interaction

    E(t) = [D(P_on,t, beta_on) - D(P_on,t, beta_off)]
         - [D(P_off,t, beta_on) - D(P_off,t, beta_off)]
         = M(P_on, t) - M(P_off, t)

`E(t)` asks whether the mechanical effect of the operator has itself become
history-dependent. It is the operator-by-representation interaction.

**`E(0) = 0` exactly, up to estimator noise, and this is the baseline.** At
generation zero both arms are the identical common initial population, a single
egg-cell symbol with no operators, so the two bracketed terms are estimates of
the same quantity. Any systematic departure of `E(t)` from zero as `t` grows is
evidence that evolution has changed the machine.

This is a strong feature of the design and it should be stated plainly: the
null for the interaction is not modelled or assumed, it is measured on the same
apparatus at generation zero, in the same units, with the same estimator noise.

## Pairing rule for O2 and O3

Runs are paired by `(alpha, replicate index, seed family)`. Replicate `r` of the
`beta = 0.1` arm is paired with replicate `r` of the `beta = 0` arm at the same
`alpha`, and both are initialised from the same common initial population and
the same base seed. The two runs diverge only because of `beta`.

Pairing is fixed before execution. It reduces between-run variance without any
post-hoc matching, and it makes `H(t)` and `E(t)` per-run quantities rather
than differences of arm means.

## UNIT OF ANALYSIS AND RUN-LEVEL INFERENCE, frozen

**The unit is the run, or for paired quantities the run pair.** Never the
generation, individual, offspring sample, or phenotype position.

For each checkpoint `t`:

- `H_r(t)` and `E_r(t)` are computed once per run pair `r`.
- Across the `n` run pairs in a cell, report the mean, the standard deviation,
  and a 95 percent confidence interval from the t distribution on `n - 1`
  degrees of freedom.
- The significance test is a **two-sided paired permutation test** on the run
  pairs: the sign of each pair's value is flipped uniformly at random,
  `10,000` permutations, and the p-value is the fraction of permuted means at
  least as extreme as the observed. The permutation is over run pairs, which is
  the exchangeable unit, not over generations or individuals.
- No test is performed on within-run repeated measurements as if independent.
- The family of 25 checkpoints is handled by reporting the whole trajectory
  with its confidence band, and by preregistering **two** checkpoints as the
  primary inferential moments, with Holm correction across those two only:

      t_primary_early = 100
      t_primary_late  = 500

  Chosen because the historical record places representational reorganisation
  before generation 200 and stable fluctuation after it. Every other checkpoint
  is descriptive.

## Sample sizes, frozen

    primary grid       n = 30 run pairs per alpha level
                       2 alpha levels, 2 beta arms, 120 runs
    historical echo    the first 10 pairs of each cell reproduce the historical
                       n = 10 and are reported separately, so that a reviewer
                       can see what Toussaint's own replication would have
                       supported

## Effect-size reporting

Every reported difference carries, alongside the confidence interval, the ratio
of the effect to the estimator's own noise from
`ESTIMATOR_NOISE_PROTOCOL.md`. A difference smaller than the estimator noise is
reported as not resolvable by the historical instrument, whatever its p-value.

## Decision rules, frozen

    T1 SUPPORTED     H(t) differs from zero at t_primary_early or
                     t_primary_late, after Holm correction, AND the effect
                     exceeds the estimator noise floor
    T1 NOT SUPPORTED otherwise

    INTERACTION      E(t) differs from its generation-zero value at either
                     primary checkpoint, after Holm correction, AND exceeds the
                     estimator noise floor

    K2 FIRES         the full trajectory of H(t) and E(t) is within the
                     generation-zero mechanical baseline plus noise at all
                     checkpoints
    K3 FIRES         H(t) is indistinguishable from zero at both primary
                     checkpoints
    K4 FIRES         E(t) is indistinguishable from E(0) at both primary
                     checkpoints
    K5 FIRES         differences exist but are within the estimator noise floor

## What a non-zero E(t) does and does not license

It licenses: the same variation operator, applied to populations that differ
only in their history under that operator, produces measurably different
distributions of one-step reachable phenotypes.

It does not license: any claim that the difference is adaptive, that it caused
the acquisition difference, or that it constitutes a general capacity. The
causal chain to acquisition is T3, and T3 requires the acquisition results as
well, analysed at run level, with the ablation arm showing suppression of both.

## Sign

No sign is predicted for `H(t)` or `E(t)`. A representation with operators
could plausibly show higher modular degree, because a single mutation in an
operator propagates to several phenotype positions, or lower neutral degree,
because such a mutation is more likely to be non-neutral. Both directions are
admissible and neither is preferred.
