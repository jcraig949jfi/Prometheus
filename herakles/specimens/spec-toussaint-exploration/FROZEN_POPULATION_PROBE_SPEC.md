# FROZEN_POPULATION_PROBE_SPEC

**Frozen 2026-09-03, before any execution.** Required by the HC-T01 execution
directive, sha256 `83b6e197b52f441b007cd2a0585be504661f57d97f4730a9cb4e99bb4494d91e`,
section 2. Nothing in this file may be changed after the first confirmatory run.

## Why the generation-zero null is not enough

The generation-zero mechanical null measures the direct effect of the operator
parameter on one population, the common initial one. It cannot detect the case
the experiment exists to test: that the mechanical effect of `beta` is itself a
function of the representation the population has evolved. If evolution changes
the genotype structure, the same operator applied later may induce a different
phenotype distribution, and a generation-zero null is blind to that.

## The probe

At each preregistered checkpoint `t`, for the population `P_t` of the run:

1. Take a deep copy of the population. The run continues from the original.
2. Apply no selection, no reproduction, no replacement.
3. For each probe setting `b` in {`beta_on`, `beta_off`}, and for each of the
   `lambda = 100` individuals, draw `S = 2000` independent offspring using the
   historical variation operator with `beta = b` and the run's own `alpha`.
4. Compute the detector statistics from those samples.
5. Discard every sampled offspring. Nothing enters the population, nothing
   affects fitness, nothing advances the generation counter.

The probe uses its own random stream, seeded independently of the evolution
stream, so that probing cannot perturb the evolutionary trajectory.

## Non-interference requirement, and how it is tested

**A run executed with probing must be bit-identical to the same run executed
without probing.** This is checked directly in X2 of the execution sequence, by
running each shakedown seed twice, once with probing and once without, and
comparing the full per-generation fitness and genome-length series. Any
difference fails the shakedown and blocks execution.

## Probe settings, frozen

    beta_on   = 0.1     the primary historical enabled value
    beta_off  = 0.0     the historical ablated value
    alpha     = the run's own alpha, 0.03 or 0.06, never varied by the probe

The probe never changes `alpha`. Only the second-type mutation rate is switched,
because that is the historical ablation.

## PRIMARY PROBE OPERATOR, frozen

    beta_probe = beta_on = 0.1

Adopted from the directive's stated candidate, for the directive's stated
reason: both populations are then exposed to exactly the same variation
operator at measurement time, so any detector difference reflects the
populations rather than the immediate fact of being measured under different
operators.

`beta_probe = beta_off = 0.0` is reported as a secondary same-probe contrast.
It is not the primary, and it cannot be swapped in afterwards.

## Detector statistics computed at every probe

All are computed from the same `S = 2000` samples per individual, then averaged
over the 100 individuals of the frozen population. The population mean is the
per-checkpoint value; the run is the unit of analysis.

  1. `neutral_degree` -- fraction of sampled offspring whose phenotype is
     identical to the parent's phenotype.
  2. `modular_degree` -- Toussaint's statistic. For each sample, form the
     variation mask over the 25 phenotype positions, meaning the positions at
     which the offspring phenotype differs from the parent phenotype. The
     modular degree is the sum over `k = 1..4` of the probability that, given a
     variation at position `i`, there is also a variation at
     `(i + 5k) mod 25`, averaged over `i` in `0..24`.
  3. `mi_total` -- mean over all `i < j` of the normalised mutual information
     `I'_ij = 2 I_ij / (H_i + H_j)` between phenotype positions `i` and `j`
     across the sample.
  4. `mi_aligned` -- the same mean restricted to pairs with
     `(j - i) mod 5 == 0`.
  5. `mi_unaligned` -- the same mean over the remaining pairs.
  6. `avgfit` -- mean fitness of the sampled offspring. **Positive control
     only.** Never the primary precedence statistic.
  7. `genome_length`, `operator_count`, `operator_usage` -- genotype
     descriptors, reported for context, not detector statistics.

`mi_aligned` and `mi_unaligned` exist to separate "the representation has
modules" from "the representation has modules aligned to the target's period".
That distinction is the difference between a structural consequence of having
operators at all and an evolved property, and Toussaint's own record shows the
distinction is real: four of his ten runs in one cell produced misaligned
modules such as `bcdea` and `deabc` rather than `abcde`.

## PRIMARY DETECTOR STATISTIC, frozen

    modular_degree

Chosen because it is Toussaint's own statistic, because it measures the
structure the mechanism is claimed to create rather than a generic amount of
variation, and because it cannot be confused with a fitness reading.

Secondary, reported always, never substituted for the primary:
`neutral_degree`, `mi_aligned`, `mi_total`.

## DENOMINATOR AND STATISTIC DEFINITIONS, frozen

- Phenotype length is fixed at 25 for the statistics. A sampled offspring whose
  developed phenotype is shorter or longer than 25 is compared position-wise
  over `0..24`, with absent positions counted as differing from the parent.
  The denominator for every probability above is always the full 2000 samples,
  never the subset that happened to vary.
- For the modular degree, the conditional probability at position `i` uses as
  its denominator the number of samples that varied at `i`. If no sample varied
  at position `i`, that position contributes 0 to the sum and is still counted
  in the average over `i`. This convention is recorded because the alternative,
  dropping such positions, would inflate the statistic exactly in the
  low-variation regime where the ablated arm lives.
- Mutual information uses the 8-symbol alphabet plus one extra bin for "absent",
  so 9 bins per position, with the plug-in estimator over the 2000 samples.
  The plug-in estimator is biased upward on sparse histograms. That bias is the
  same for both arms at equal sample count, and the difference-in-differences
  removes it to first order, but it is why `mi_total` is secondary and the
  modular degree is primary.

## CHECKPOINT CADENCE, frozen

    generations 0, 5, 10, 15, 20, 30, 40, 50, 65, 80, 100, 125, 150, 175, 200,
                250, 300, 350, 400, 500, 600, 700, 800, 900, 1000

25 checkpoints. Dense early because the historical record puts the
representational reorganisation of Experiment 1 before generation 200, sparse
later because the historical record says all measures merely fluctuate after
that. The cadence is fixed for all arms and all runs.

## What the probe does not do

It does not measure a counterfactual evolutionary trajectory. It measures what
the variation operator would do to this population now. Any claim about what
the population would have become is outside what this probe supports.
