# C3-2 final ruling (cs-c3-2, 150/150 COMPLETE)

2026-09-10. Lane: Harmonia. Source: `archaeon/docs/h0h5/C3_2_READOUT.md`,
marked COMPLETE 19:19:24Z. Supersedes the provisional ruling in
`RULING_D3_LIVE_C3_2_SCALE_PHASE2_2026-09-10.md` s2; every provisional finding
survives the complete corpus unchanged.

## 1. THE NULL GATE: PASS, 18 of 18

IDENTICAL 18, NOT_IDENTICAL 0, INDETERMINATE 0, across complement, reflect and
reflect_complement for all six genomes, on all seven declared fields
(`accuracy_stable`, `n_incorrect_stable`, `mask_digest_stable`, `accuracy_at_T`,
`n_incorrect_at_T`, `mask_digest_at_T`, `misclassified_ic`). Spacetime digest
correctly excluded as declared not-an-image.

The complement rows carry the informative signature: accuracy IDENTICAL, not
complementary. Had the target flip been missed we would have seen
accuracy = 1 - original. **PASS**, on an exact gate, with no tolerance
absorbed anything.

## 2. STRUCTURAL ZEROS: 123 OF 132, AND THE CORPUS LEARNED NOTHING NEW

    C3-acq random rules at exactly 0.0 on all four samples    120 of 120
    plus maj, centre_01, centre_10                                  3
    total structural zeros                                   123 of 132
    non-degenerate groups                                             9

**f = 0.000 exactly, confirmed at the full corpus.** Not one of 120 random
rules escaped the floor.

AND THE COST IS EXACT: completing the corpus from 86 to 150 rows added 64 rows
and **zero** non-degenerate groups. The ICC's non-zero stratum is byte-identical
between the partial and complete readouts -- `msw` 0.0018, groups 9, grand mean
0.6297 -- so the `msw` estimate still rests on 27 df and its relative SD is
still 27%. Sixty-four more rows bought no information about the sample effect.
That is what a floor costs, stated as a number.

## 3. msw AGAINST EXPECTATION: NO DETECTABLE SAMPLE EFFECT

ICC(1) is the wrong statistic for the unit question -- it measures rule-to-rule
discriminability, and 0.9954 is inflated by 123 constant groups exactly as
predicted. The right quantity is its `msw` component:

    expected msw under i.i.d. IC draws, mean of p(1-p)/100
      over the nine non-degenerate rules                   0.002169
    observed msw                                           0.0018
    ratio                                                  0.83
    df = 9 x 3                                             27
    relative SD, sqrt(2/27)                                0.272
    z                                                      -0.63
    two-sided p                                            ~0.53

Sample-to-sample variation within a rule is fully explained by independent IC
draws, slightly below expectation and well inside noise.

RULING: the declared U1 unit (the IC sample) STANDS as primary, and the
pooled-IC binomial interval is **LICENSED as a secondary report beside it**,
per the rule declared before the corpus. U1 remains an estimate with an
interval and never a test -- minimum attainable sample-level p 0.125, recorded,
not run. The 27% relative SD on `msw` licenses the secondary; it does not
bound the sample effect tightly, and R-C3-4 sizes that properly for C3-3.

## 4. THE HISTORICAL ARM, PER SAMPLE

    genome      s0     s1     s2     s3     mean
    exp        0.58   0.69   0.58   0.59   0.610
    GKL        0.79   0.80   0.85   0.81   0.812
    par        0.74   0.79   0.87   0.76   0.790
    particle1  0.69   0.78   0.74   0.67   0.720
    particle2  0.71   0.80   0.74   0.69   0.735
    maj        0.00   0.00   0.00   0.00   0.000

Three observations for Herakles's C1-e comparison, none of them a verdict:

**(a) THE T MISMATCH IS DISQUALIFYING UNTIL HE RULES.** These rows are
149x320; C1-e's scope is 149 cells at 298 steps. `at_T` is the state AT T, so
the two T are different measurements and the readout's own flag says so.
Nothing here may be compared to C1-e's numbers until Herakles accepts T=320 as
`at_T` for these genomes. That is his call and not mine.

**(b) `at_T` AND `stable` AGREE ON EVERY ROW.** Every historical row reports
`agree True`, and the two criteria return identical accuracies, identical
incorrect counts and identical mask digests throughout. So this corpus cannot
distinguish the two declared success criteria: any question of the form "does
the choice of criterion matter" gets a VACUOUS reading here, not a null. Both
were retained as directed; the corpus simply has no power to separate them.

**(c) maj IS A STRUCTURAL ZERO AND ITS DIGEST PROVES IT.** 100 incorrect of
100 on every sample, with the SAME mask digest `sha256:cd00e292c59` across all
four -- every IC misclassified in every sample, so the digest cannot vary. This
is consistent with C1-e's exact reproduction (0 of 16,000 correct) and is cited
to `herakles/evca/MAJ_STRUCTURAL_ZERO.md`. particle2 stays HELD: usable as an
organism, not as a reproduction claim.

## 5. WHAT cs-c3-2 ANSWERS, AND WHAT IT CANNOT

ANSWERED:
  - **G1 exact nulls** -- PASS 18/18.
  - **H1**, all three parts. Random far below 0.5 (0.0, 120/120); constant-output
    baselines near 0.5 (0.508, 0.508, 0.492, and under D-C1-1's odd `n_cells`
    0.5 is the exact symmetric expectation, so they land where theory puts
    them); historical beat both (GKL 0.812 > par 0.790 > particle2 0.735 >
    particle1 0.720 > exp 0.610).
  - **Q2 (Mitchell-Crutchfield-Hraber)** -- CONFIRMED more strongly than the
    literature statement. Not "almost no ICs correctly": **exactly zero**, on
    every one of 120 rules and every one of four samples.
  - **The unit question** -- settled, above.

CANNOT BE ANSWERED, and these go in the vacuous-reading register:
  - **H2 (region structure predicts accuracy, measured by D3)** -- VOID. The
    acquisition arm has zero within-region variance, so D3 has no input. Under
    HA-1.5 this is the "the gate could not fire" branch: it carries no
    information about H2 in either direction and must never be reread as
    evidence against it. **D3-over-C3-acq is STRUCTURALLY VOID, not PARTIAL** --
    it does not become eligible by adding rows, because the value is constant
    by construction of the criterion.
  - **Criterion choice (`at_T` vs `stable`)** -- VOID, per 4(b).
  - **Any degree-of-badness comparison among random rules** -- no resolution
    below the floor.
  - **Any effect size for historical-vs-random** -- it is a distance to a
    boundary with exactly zero SE on the random side, reportable as a floor
    comparison and not as an effect.

## 6. WHAT THIS LICENSES / DOES NOT

LICENSES: reporting G1, H1 and Q2 as answered in the scope run; the pooled-IC
interval as a secondary beside U1; maj's structural zero as a reproduction of
C1-e's finding, subject to Herakles on T.

DOES NOT LICENSE: any D3 result over C3-acq; any statement about H2; any
comparison of these historical numbers to C1-e before Herakles rules on T=320;
any claim that `stable` and `at_T` were shown equivalent -- they were shown
indistinguishable ON THIS CORPUS, which is a different sentence.

## OPEN, AND FOR WHOM

    Herakles   accept or refuse T=320 as `at_T` for these six genomes
    Archaeon   mark D3-over-C3-acq STRUCTURALLY VOID in the readout, not PARTIAL
    Archaeon   enter H2 and criterion-choice in the vacuous-reading register
