# E1 — RESULT: INSTRUMENT FAILURE, NOT A NULL

Run date 2026-09-04. Executed fully as frozen against
`E1_PREREGISTRATION_v2.md` (sha256 4d03d8753248a130ba360b4f7feddad0f5db4194e7cd9a38181cfef70e941ebf).
Raw: `e1_results.json`. Diagnostic: `e1_diagnostic_matching.py`.

## Outcome

All 8 arms returned `INSUFFICIENT_MATCHES`, `n_pairs = 0`.

    arm                          n_pairs   min_required
    --------------------------   -------   ------------
    E1A match P*                       0             30
    E1B match P* and G                 0             30
    C0 within-history                  0             30
    C1 replicate, same targets         0             30
    C3 degenerate linear               0             30
    sigma sweep 0.01/0.05/0.2          0             30

Per prereg section 5, an arm below 30 pairs **is not interpreted**. This is
therefore NOT a null, NOT evidence for K2, and NOT a bounded negative result.
No exchangeability test was ever evaluated. Runtime was 196 s rather than the
projected ~20 min precisely because every arm aborted before the permutation
stage.

## Measured cause — two independent defects

Measured on a full 2000-generation lineage pair (not inspected, measured):

    TAU_MATCH declared                 0.2000   (= 0.05 * sqrt(16))
    per-trait |P| mean / max           4.174 / 6.437
    ||P*|| mean                       17.483
    within-history  min pairwise       0.1528
    within-history  median NN          0.3765
    within-history  pairs <= TAU          22    (< 30 required)
    cross-history   min distance      27.1252
    cross-history   median NN         28.3322
    cross-history   pairs <= TAU           0

### DEFECT 1 — tolerance specified in the wrong units (scale error)

The prereg fixed an ABSOLUTE tolerance `0.05*sqrt(N)` as though the adult
phenotype were O(1), i.e. on the scale of a tanh output. It is not. The Watson
map has fixed point

    0.2 * P = tanh(B.P)   =>   P = 5 * tanh(B.P)

so per-trait phenotype is O(5) and `||P*|| ~ 17.5`. The declared tolerance is
~135x tighter than the smallest attainable cross-history distance. The gate
could not fire on any input.

This is the SAME error class already recorded in memory as
`feedback_gate_must_be_shown_reachable`, in the inverse direction: there a cut
sat above the maximum attainable, here it sits below the minimum attainable.
Both make the decision ineligible to change. The attainable range must be
computed BEFORE the threshold is frozen.

### DEFECT 2 — zero common support (design error, the serious one)

Loosening the tolerance would NOT rescue this experiment.

`make_targets` builds treatment A on trait indices {0,1,4,5,8,9,12,13} and
treatment B on the complement {2,3,6,7,10,11,14,15}. The supports are DISJOINT,
so the targets are exactly orthogonal, and saturating selection drives the two
populations to different corners of phenotype space.

    cross-history minimum distance / within-history median NN  =  72x

There is no region of phenotype space occupied by both treatments. E1 requires
conditioning on a MATCHED adult phenotype; that conditioning set is empty by
construction. A tolerance wide enough to admit pairs (>= 27) would be ~70x
wider than the entire within-population dispersion, so the resulting "matched"
pairs would differ more from each other than any two organisms within a
treatment, and C0's matching-error floor would dominate the statistic
completely.

## The design tension I failed to notice

A same-probe counterfactual needs treatments that

  1. differ in the GENERATOR (otherwise there is no history effect to find), and
  2. OVERLAP in the OBSERVABLE being conditioned on (otherwise there is nothing
     to match).

I designed the targets to maximise (1). That drove (2) to exactly zero. The two
requirements are in direct tension and the preregistration never stated a
positivity/overlap requirement, so nothing checked it.

## Status

    E1 as preregistered  ..... CANNOT BE EXECUTED on this substrate
    K2                   ..... UNCHANGED: not killed, not confirmed
    Escalation to E2     ..... NOT LICENSED (requires a positive E1)
    Packet section 5     ..... still the open experiment

## What v3 would need (PROPOSED, NOT RUN, NOT FROZEN)

1. Scale-relative tolerance: a fraction of the within-population phenotype
   dispersion, with the attainable distance distribution measured and reported
   BEFORE the threshold is fixed.
2. Overlapping treatments: histories that differ in the CORRELATION STRUCTURE
   of targets while sharing marginal target directions, so P* distributions
   overlap while B diverges. Overlap must be a preregistered, checked gate.
3. A positivity precondition: report the size of the common-support region as
   a first-class measured quantity; if it is empty, say so and stop, rather
   than reading zero matches as zero effect.

No v3 parameters are chosen here. Retuning after seeing a failure is exactly
what the freeze exists to prevent; v3 requires its own preregistration and
external review.
