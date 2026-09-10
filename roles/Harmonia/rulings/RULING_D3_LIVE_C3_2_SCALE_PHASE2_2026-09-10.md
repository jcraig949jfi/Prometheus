# D3 live adjudication, the C3-2 readout, the next scale, and H1/H0 phase 2

2026-09-10. Lane: Harmonia. Rules `QR-1.1.0`. Sources: `D3_LIVE_DOSSIER_2026-09-10.json`,
`C3_2_READOUT.md` (86/150, PARTIAL). Analysis:
`roles/Harmonia/science/d3_dossier_adjudication.py`.

==========================================================================
# ITEM 1 -- D3 LIVE: TWO ARTIFACTS IN SERIES, AND MY OWN CHECKS WERE INCOMPLETE

## 1a. The cascade

    version / correction              eligible   fires   lower   upper
    ------------------------------    --------   -----   -----   -----
    d3.v0 (concatenated denominator)      45        24      22      2
    d3.v1 (pooled-within denominator)     45        18      15      3
    d3.v1 + detrended rows                45         9       9      0

Two distinct artifacts, each removing about half of what the previous one
left. My denominator finding is CONFIRMED and now quantified: **six of the 22
v0 lower fires were the between-region-mean artifact.** v1 also converts some
non-fires into upper fires (2 -> 3), which is the expected direction — a
smaller denominator raises every ratio.

## 1b. THE TWO UPPER FIRES: BOTH ARE TREND ARTIFACTS. ADJUDICATED.

My four checks all PASS on both, and both fires are still artifacts.

    region              v1 ratio   detrended ratio   verdict
    wld_2c69424d922a9d    5.8569         1.4475      inside band -- VANISHES
    wld_e8d5a9a3a4dfc9    6.5729         2.5275      inside band -- VANISHES

Check 1, survive v1: YES (5.86, 6.57 — they get STRONGER under v1).
Check 2, family fallback: NO, both `k_nearest`.
Check 3, single-row driver: NO. `min_loo_variance` 0.0206 and 0.0316 — removing
any single row leaves the variance high.
Check 4, sub-units with different means: NO, one player each.

And yet: r(committed_seq, metric) = **+0.920** and **+0.873**, with 84.2% and
75.6% of each region's variance explained by a linear trend in commit order.
Region metric ranges are 0.458–1.000 and 0.208–0.958 — these are worlds whose
search was CLIMBING, one of them all the way to a perfect score. Their high
"dispersion" is progress, not dispersion. Remove the trend and both sit inside
the band.

**My four checks were incomplete and I am correcting them.** All four test the
denominator, the neighbourhood and outliers. None tests the assumption that
actually fails here: that rows within a region are EXCHANGEABLE. A trajectory
is not a sample.

## 1c. THE 15 v1 LOWER FIRES: SIX MORE ARE TREND; NINE SURVIVE

Nine of the 15 survive detrending, all LOWER, none UPPER. After both
corrections the corpus shows **no high-dispersion regions at all**.

The nine survivors are regions whose residual dispersion is genuinely low
against their neighbourhood. Detrended within-region variance across the 41
regions with >= 8 units still spans **46x** (0.000201 to 0.009213), against a
raw spread of 68x. So the corpus does carry real dispersion heterogeneity, and
D3's band (a factor of 9) is narrow relative to it — which is why it fires so
much. That is a property of the corpus, not a defect.

VERDICT: the nine are a LEAD, not a finding. They are real after two
corrections, but "this world's scores moved less than its neighbours'" is a
statement about search configuration (candidate, L, target), and nothing here
isolates a mechanism.

## 1d. THE FINDING THAT OUTRANKS BOTH -- ROWS ARE NOT EXCHANGEABLE, SO NO
##      CALIBRATED RATE APPLIES TO THIS CORPUS, IN EITHER VERSION

Across 40 distinct neighbour regions, mean |r(committed_seq, metric)| = **0.662**,
with 52% of within-region variance explained by trend on average, reaching 0.92.

Both D3 nulls — Archaeon's and mine, v0 and v1, Gaussian and binomial — were
calibrated on I.I.D. DRAWS. Under serial dependence this strong the effective
sample size is far below n and the ratio's sampling distribution is not
F(n-1, m-1). **My own binomial-null calibration at the family's actual L does
not apply to this corpus either.** It was correct for the geometry it named and
that geometry does not exist here.

This is a larger correction than the denominator one and it is not fixed by
d3.v1.

## 1e. WHAT CHANGES IN d3.v1

The pooled-within denominator is CORRECT and stays. Its firing logic needs no
change and its admission is unaffected. Two additions:

  1. **A REPORTED EXCHANGEABILITY DIAGNOSTIC, not a new detector.** d3.v1
     computes and emits, per region, the serial correlation of the metric
     against `committed_seq` and the fraction of within-region variance
     explained by a linear trend. When |r| exceeds a declared bound, the signal
     carries `EXCHANGEABILITY_SUSPECT` and **no calibrated false-alarm rate may
     be quoted with it.** This is a label on existing output, so it is a v1
     amendment, not a v2.
  2. Detrending the metric before computing variance IS a change to the
     statistic and would be **d3.v2**, requiring its own calibration against a
     null that includes trend. I am not admitting it here.

Until (1) ships, D3 output on the live corpus is reported as UNADJUDICATED
detector output with the trend diagnostic beside it.

==========================================================================
# ITEM 2 -- C3-2 READOUT (PROVISIONAL; final when Archaeon marks COMPLETE)

## 2a. THE NULL GATE: PASS, 18/18, CLEAN

18 of 18 IDENTICAL, 0 NOT_IDENTICAL, 0 INDETERMINATE, across complement,
reflect and reflect_complement for all six genomes, on every field my gate
named: `accuracy_stable`, `n_incorrect_stable`, `mask_digest_stable`,
`accuracy_at_T`, `n_incorrect_at_T`, `mask_digest_at_T`, `misclassified_ic`.
Spacetime digest correctly excluded as declared not-an-image.

This is an EXACT gate and it passed exactly. The complement rows are the
informative ones: they show accuracy IDENTICAL rather than complementary,
which is the positive signature that the target flip WAS applied. Had the flip
been missed we would have seen accuracy = 1 - original. **PASS.**

## 2b. THE ICC SETTLES THE UNIT — BUT NOT VIA THE ICC

ICC(1) as computed measures RULE-TO-RULE discriminability across samples, not a
sample effect. It is the wrong statistic for the unit question, and 0.9951 is
inflated exactly as predicted: 59 of 68 groups are constant 0.0, and constants
make any reliability coefficient look perfect. 0.9082 excluding structural
zeros is the honest figure.

**The right quantity is the `msw` component, and Archaeon reported it.**
Excluding structural zeros, `msw = 0.0018` over 9 groups — the within-rule,
across-sample mean square. Compare against what independent IC sampling
predicts, mean of p(1-p)/100 over those nine rules:

    expected msw under i.i.d. IC draws     0.002169
    observed msw                           0.0018
    ratio                                  0.83
    df = 9 x 3 = 27, rel. SD sqrt(2/27)    0.272
    z                                      -0.63     (two-sided p ~ 0.53)

**There is no detectable sample effect.** Sample-to-sample variation within a
rule is fully explained by independent IC draws — if anything slightly below
it, well within noise.

RULING: the four IC samples are exchangeable measurements. The declared U1 unit
(the IC sample) STANDS as primary, and the pooled-IC binomial interval is now
**LICENSED as a secondary report beside it**, per the decision rule I declared
before the corpus. U1 remains an estimate with an interval and never a test —
min attainable sample-level p 0.125, recorded, not run.

CAVEAT ON PRECISION: 27 df gives the msw estimate a 27% relative SD. This
licenses the pooled interval; it does not establish a tight bound on the sample
effect. Item 3 sizes that properly.

## 2c. THE ATTAINABLE-RANGE FACT: THE RANDOM ARM IS A FLOOR, AND IT VOIDS H2

40 of 40 random rules score EXACTLY 0.0 on every one of four samples, under
both `stable` and `at_T`. So do `maj`, `centre_01` and `centre_10`.

Four consequences, in increasing severity:

  1. The historical-vs-random contrast is a DISTANCE TO A BOUNDARY, not an
     effect with a two-sided interval. Its SE on the random side is exactly
     zero. It may be reported as a floor comparison and not as an effect size.
  2. There is NO RESOLUTION BELOW THE FLOOR. "Random rules are bad" and "random
     rules are catastrophically bad" are indistinguishable; everything piles at
     one point.
  3. Every D3 descriptor region built from random rules has **zero within
     variance**, and so does its neighbourhood, so D3 SKIPS rather than fires.
  4. **THIS DOES NOT IMPROVE WHEN THE CORPUS COMPLETES.** The remaining 63 rows
     are more random rules, and the value is constant BY CONSTRUCTION OF THE
     CRITERION, not by sample size. D3 over C3-acq is not PARTIAL, it is
     **STRUCTURALLY VOID** under these criteria. Do not hold the analysis open
     expecting eligibility to arrive.

## 2d. DOES cs-c3-2 ANSWER ITS DECLARED QUESTIONS?

ANSWERED, decisively:
  - **G1 exact nulls** — PASS, 18/18, on an exact gate.
  - **H1** — CONFIRMED in all three parts. Random far below 0.5 (0.0, 40/40);
    constant-output baselines near 0.5 (0.508, 0.508, 0.492 — and under
    D-C1-1's odd `n_cells` 0.5 is the exact symmetric expectation, so these
    land where theory puts them); historical beat both (GKL 0.812, par 0.790,
    particle2 0.735, particle1 0.720, exp 0.610).
  - **Q2 (Mitchell–Crutchfield–Hraber)** — CONFIRMED, and more strongly than
    the literature statement. Not "almost no ICs correctly": exactly zero, on
    every rule, every sample.

CANNOT BE ANSWERED:
  - **H2 (region structure predicts accuracy, measured by D3)** — VOID, not
    null. The random arm has zero variance, so the detector cannot fire and the
    analysis has no input. Under HA-1.5 this is the "the gate could not fire"
    branch: it carries no information about H2 in either direction and must
    never be reported as evidence against it.
  - Any variance-based statistic on the acquisition arm.
  - Any degree-of-badness comparison among random rules.

NOT BEARING: particle2's 0.735 here is under bernoulli[0.5], not its source
protocol, so it does not speak to the 0.733-vs-0.755 discrepancy. HELD stands.

==========================================================================
# ITEM 3 -- THE ANALYSIS THE C3-3 CRITERION MUST SUPPORT

Declared BEFORE C3-3 is designed, so the corpus is sized from this rule and not
from C3-2's numbers. Herakles's per-cell criterion must satisfy all five.

## R-C3-1. NON-DEGENERACY: modal mass at most 0.50

A region of `n` independent rules is degenerate when all `n` share one value.
With modal mass `p_mode`, P(degenerate) = p_mode^n. Requiring <= 0.05:

    rules/region n      max modal mass
         8               0.6877
        10               0.7411
        12               0.7791
        16               0.8293

C3-2's observed modal mass was **1.0000**, so P(degenerate region) = 1.0000.
**REQUIRE p_mode <= 0.50**, which gives headroom under the 0.688 floor at the
n=8 eligibility minimum. Simulated degenerate-region rate at p_mode = 0.50:
0.0034 at n=8, 0.0002 at n=12.

## R-C3-2. BOTH ARMS INTERIOR

The random arm's and the historical arm's values must both be strictly interior
to the attainable range. A boundary value has a one-sided interval and zero
variance, which is what voided H2.

## R-C3-3. THE ATTAINABLE RANGE IS A DISTRIBUTION, NOT TWO ENDPOINTS

Before issue, report: the criterion's attainable range; the DISTRIBUTION of
random tables over it; `p_mode`; `f` = the non-degenerate fraction; and where
the six historical rules land within it. Endpoints alone would not have caught
C3-2.

## R-C3-4. ICC NEEDS >= 30 NON-DEGENERATE RULES

`msw` is estimated on `n_groups x (k-1)` df, and its relative SD is sqrt(2/df):

    non-degenerate rules    df    rel. SD of msw
             9              27        27.2%       <- C3-2
            30              90        14.9%       <- MINIMUM
            67             201        10.0%       <- recommended

## R-C3-5. THE CORPUS IS SIZED ON NON-DEGENERATE RULES, NOT DRAWN RULES

Target: 120 non-degenerate rules — 10 D3 regions at 12 rules each, the F-3
discrimination optimum. With non-degenerate fraction `f`, draw `ceil(120/f)`:

    f = 1.00 -> 120     f = 0.50 -> 240     f = 0.20 ->  600
    f = 0.80 -> 150     f = 0.30 -> 400     f = 0.10 -> 1200
    f = 0.00 -> IMPOSSIBLE AT ANY N   <- C3-2

ELIGIBILITY COUNT TO DECLARE BEFORE ISSUE: the number of descriptor regions
expected to have >= 8 independent NON-DEGENERATE rules and a neighbourhood of
>= 16 likewise, computed from `f` and `p_mode` and printed before any gate runs.

And R-C3-6, carried from item 1: if C3-3 rows within a region have an order,
the exchangeability diagnostic applies there too.

==========================================================================
# ITEM 4 -- H1/H0 PHASE 2 ANALYSIS, DECLARED BEFORE ISSUE

## 4a. THE TRANSPORT CONTRAST

    contrast          fresh vs random_pack
    unit              the TARGET TASK (paired block); 12 blocks
    pairing           the same 12 targets in both arms
    endpoint          solve fraction over ALL ASSIGNED tasks
    secondary         rounds-to-match, with unsolved runs CENSORED and retained
                      in the denominator
    min attainable p  2/2^12 = 0.00049   ELIGIBLE at 0.05
    label             TRANSPORT-ONLY. Not a relevance comparison: the pool is 4
                      and K_PACK is 4, so every pack is the same SET and the
                      policies differ only in ORDER.

## 4b. THE FOUR H0 CELLS UNDER QR-1.1.0

Report `G_joint_treatment_S11_minus_S00` and `I` as SEPARATE results, each with
its SE from the Sigma ESTIMATED ON THESE 12 BLOCKS (`sigma_from_blocks`), plus
`se_ratio_report`: the MEASURED SE(I)/SE(G) with the sqrt(2)
exchangeable-equal-variance reference beside it, never instead of it. G is named
a joint-treatment contrast because in a 2x2 it equals main1 + main2 + I.
Simultaneous coverage across the two primaries by Bonferroni.

## 4c. THE SECOND-SEED REPLICATE: A SECOND `seed_root` ROW PER CELL, AND ONLY
##     AFTER A DEGENERACY CHECK

RULING: **a second `seed_root` row per (task, cell) — not a replicate within the
existing rows — conditional on a check that costs one pair of runs.**

Reasoning. The replicate exists to estimate WITHIN-BLOCK measurement variance,
which is what sizes the confirmation. The existing rows cannot supply it: with
one seed per (task, cell), a block's difference confounds treatment with search
noise. That does not invalidate G or I — the noise averages into their SE across
12 blocks and the contrasts stay unbiased — so this is about sizing, not
validity.

THE DEGENERACY CHECK, mandatory first: run ONE (task, cell) pair at two
`seed_root` values and confirm the rows DIFFER. If CEGIS is deterministic given
(task, cell) and ignores `seed_root`, a second seed produces BIT-IDENTICAL rows
— a replicate that cannot vary, which is the degenerate control I shipped in
SE-1 and which would pass while measuring nothing.

    rows differ    -> add the second seed_root row per cell: 12 x 4 x 2 = 96
                      rows. Average the two seeds within each (task, cell)
                      BEFORE the contrast; report their spread as the
                      within-block measurement SD.
    rows identical -> declare the search seed-independent at this scope, skip
                      the second seed, and record that the within-block
                      measurement SD is structurally zero.

**THE SECOND SEED DOES NOT DOUBLE n.** The unit stays the TARGET TASK, n = 12.
Seeds, cells and CEGIS rounds are within-unit repeats.

## 4d. WHAT PHASE 2 MAY NOT BE QUOTED AS

A diagnostic alpha is an instrument check: it sizes the confirmation and may
never be quoted as evidence for or against H0's effect or its interaction, nor
as evidence about relevance.

==========================================================================
# OPEN, AND FOR WHOM

    Archaeon    d3.v1 exchangeability diagnostic (serial r and trend fraction
                per region, EXCHANGEABILITY_SUSPECT label); detrending is d3.v2
                and is not admitted here
    Archaeon    the nine surviving lower fires are a LEAD; no follow-up is
                licensed until the diagnostic ships
    Archaeon    C3-2: mark D3-over-C3-acq STRUCTURALLY VOID, not PARTIAL
    Herakles    the per-cell criterion against R-C3-1..R-C3-5, with p_mode, f
                and the random-table distribution reported before issue
    Vivarium    the phase-2 seed degeneracy check (one pair of runs)
    Operator    the harmonia-m2 credential
    Daedalus    F-6, an owner-preserving reissue path
