# 09 - HARMONIA-FACING INVOCATION AND PROVENANCE

Written so the detector can be invoked without this conversation.

## What you provide

    world_adapter     an object satisfying 02_MINIMUM_WORLD_API REQUIRED set
    genotypes         an ordered sequence of genotypes to measure. For a
                      temporal test this is a lineage in order; for a
                      cross-sectional test it is a matched set.
    events            indices at which a realized phenotype change occurred.
                      MAY BE EMPTY -- the detector then reports descriptive
                      statistics only and MUST NOT claim predictive value.
    compute_ceiling   maximum neighbour evaluations. Exceeding it returns
                      NEIGHBOURHOOD_INTRACTABLE, never a subsample, unless a
                      sampling design is separately preregistered.

## What you receive

Per genotype, per neighbourhood type (sub / ins / del):

    residual_bits, support_size, effective_number,
    distinct_phenotypes, distinct_scalar_classes,
    hidden_transitions_per_scalar_class,
    bottom_fraction, duplicate_fraction,
    all eight baseline values b1-b8

Per run: a verdict from 04_NEGATIVES, plus the provenance block below.

## What constitutes DETECTOR FAILURE (not a scientific result)

    WORLD_API_INSUFFICIENT, NONDETERMINISM_DETECTED, PROJECTION_UNVERIFIED,
    NEIGHBOURHOOD_INTRACTABLE, PROJECTION_INVENTED

These are engineering outcomes. They must never be reported as evidence about
the hypothesis in either direction.

## What constitutes an INTERPRETABLE NEGATIVE

Any outcome in 04 other than the five above. The most valuable is
LATENT_VARIATION_BASELINE_EXPLAINED, especially via b6.

## Provenance that MUST be recorded

    world identity + version + seed
    genotype serialisation hash for every genotype measured
    the exact projection pi, and the world's assertion that it applies it
    determinism evidence: a repeat evaluation of at least one genotype,
        bit-compared
    the frozen denominator (VIABLE) and the frozen enumeration convention
        (uniform over sites and symbols)
    compute ceiling and whether it bound
    detector contract hash, so the measurement can be tied to frozen T_

## What must NEVER be inferred from missing fields

A missing scalar is not zero. A missing phenotype is not empty. A missing
validity flag is not "valid". A missing indel operator is not "no indels
occur". Absence is reported as absence.

## How you know the measurement corresponds to frozen T_

The run record carries the sha256 of 01_DETECTOR_CONTRACT.md. If that hash is
not the frozen one, the measurement is a variant and must be labelled as one.

## If the stack cannot support this today

It cannot -- see 07. Seams S1, S2 and S3 are blocking for a scientific run.
Calibration against candidate A and the fail-closed test against candidate C
are possible without them.
