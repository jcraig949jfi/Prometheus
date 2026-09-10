# Tracks A/B/E: three local corrections, and D3's live output adjudicated

2026-09-10. Lane: Harmonia. Rules `QR-1.1.0` (amends `QR-1.0.0`), fixtures
`AF-1.0.0`, protocol `H4-ADAPTIVE-1.0.0`. Code:
`roles/Harmonia/qualification/h0h5/`,
`roles/Harmonia/science/d3_live_corpus_calibration.py`.

--------------------------------------------------------------------------
## ITEM 1 -- H0 SIZING AMENDED. QR-1.0.0 -> QR-1.1.0

RULE TEXT. The variance of any four-cell contrast is `c' Sigma c`. Every
ratio, mine and Appendix A's, is that formula evaluated at a particular
Sigma, and no ratio may be quoted without the Sigma it came from. Each lane
estimates Sigma EMPIRICALLY on the disjoint pilot (`sigma_from_blocks`) and
reports both contrasts' variability SEPARATELY (`se_ratio_report`).

ASSUMPTIONS STATED. `SE(I)/SE(G) = sqrt(2)` holds when (a) the four cells have
EQUAL marginal variances and (b) the within-block correlation is EXCHANGEABLE.
My QR-1.0.0 wording said "for any rho", which is true inside that structure and
false outside it. Verified both ways:

    exchangeable, equal marginals 0.005079
        rho = 0.0, 0.3, 0.7        SE(I)/SE(G) = 1.4142  (Archaeon confirmed)

    equal marginals 0.005079, NON-exchangeable (one nonzero correlation)
        corr(S11,S00) = 0.0000     1.4142
        corr(S11,S00) = 0.3000     1.8127
        corr(S11,S00) = 0.5714     2.4494   <- sqrt(6) = 2.4495

Appendix A is right in its domain and so is my sqrt(2); the universal wording
was mine and is withdrawn. What survives unchanged is the DIRECTION and the
reason it matters: under every structure examined the interaction is the less
precise of the two, so H0's stronger claim is the harder one to resolve, and
sizing on G will leave I inconclusive.

G IS A JOINT-TREATMENT CONTRAST, NOT A MARGINAL MAIN EFFECT. In a 2x2,
`G = (marginal main 1) + (marginal main 2) + I` -- the both-on-versus-both-off
path through the design. Calling it a main effect silently attributes the
interaction to it. Measured at Sigma exchangeable(0.005079, 0.3):

    Var(G  joint treatment)      0.0071106
    Var(M1 marginal main)        0.0035553      exactly half
    Var(I  interaction)          0.0142212

The marginal main effects are `C_M1` and `C_M2` and are separate analyses if
wanted. `h0_estimands` now returns the contrast named
`G_joint_treatment_S11_minus_S00`, so the name carries the meaning.

LICENSES: sizing H0 from a pilot-estimated Sigma. DOES NOT LICENSE: quoting
sqrt(2), sqrt(6) or any ratio as a general fact; reporting G as a main effect.

--------------------------------------------------------------------------
## ITEM 2 -- PRECISION, POWER AND MEANINGFUL EFFECT ARE THREE QUANTITIES

RULE TEXT. `required_blocks()` is renamed `blocks_for_interval_clearance()`;
the old name is kept as an alias with a docstring saying what it actually
computes. It assumes the point estimate lands exactly on the assumed effect,
so it answers "how wide is the interval", not "how often would a run reach a
verdict". `blocks_for_power()` is added and SIMULATES the actual decision rule,
multiplicity and contrast, because interval clearance is not a standard test
and no closed form applies to it.

    sd 0.10, threshold 0.05, true effect 0.15, two primaries

        interval clearance (what the old name computed)    9 blocks
        power 0.50                                         8 blocks  (0.53)
        power 0.80                                        12 blocks  (0.81)

At the interval-clearance n the real power is about 0.53 -- the old name
promised the third row and delivered the first. My H0-H5 sizing table is
therefore a PRECISION table and is relabelled as one; every number in it
stands, the column heading was wrong.

THE THREE, kept distinct and never substituted:

    MEANINGFUL EFFECT   a scientific and resource decision. Fixable BEFORE a
                        pilot. NOT a function of the observed noise.
    PRECISION           interval half-width at a given n. Arithmetic.
    POWER               P(conclusive verdict) under an assumed truth. Needs
                        the actual contrasts, multiplicity and decision rule.

AND THE RULE THAT MATTERS MOST. If the budget cannot resolve the fixed
meaningful effect, REPORT THE LIMITATION or version a revised question. Never
redefine the threshold to match the noise. My own ITEM 2 in the H0-H5 ruling
said "freeze the threshold from the pilot's observed SD", and read literally
that is threshold-fitting. Corrected: the pilot's SD sizes the BLOCKS; the
threshold is set on scientific grounds and, if it proves unaffordable, that is
a reported limitation, not a number to move.

If confirmation POWER is promised anywhere, the promised probability must be
stated and `blocks_for_power` must validate the sizing for the actual
contrasts.

--------------------------------------------------------------------------
## ITEM 3 -- THE ELIGIBILITY GATE IS SCOPED TO CONFIRMATORY INFERENCE

RULE TEXT. `LanePlan.purpose` is `CONFIRMATORY` or `DIAGNOSTIC`. HA-1.6's
minimum-attainable-p gate applies to CONFIRMATORY plans only. A diagnostic run
-- a two-seed instrument alpha, a plumbing check, a contract fixture -- makes
no inferential claim, so a gate about the attainability of a p-value does not
apply to it and must not block it. Demonstrated:

    two-seed DIAGNOSTIC     ACCEPTED  (gate not applied; min attainable p
                                       0.5000 recorded, not enforced)
    two-seed CONFIRMATORY   REFUSED   (ineligible by HA-1.6)

This is a correction to my own over-reach: HA-1.6 was written against three
confirmatory designs and I stated it without a scope. Diagnostic alphas proceed
while confirmation sizing is repaired.

DOES NOT LICENSE: quoting a diagnostic run as evidence for or against an
effect. It is an instrument check and is labelled one.

--------------------------------------------------------------------------
## ITEM 7 + 8 -- D3 ON THE LIVE CORPUS IS A DENOMINATOR ARTIFACT
##                (this is the substantive finding of the pass)

BINOMIAL-NULL CALIBRATION AT THE FAMILY'S ACTUAL L, as the frozen design in
c9910be21 s2c required. The campaign's arms are `arm-a` L=24 and `arm-b` L=28
(`archaeon/producer/campaign.py`), generator Binomial(L,1/2)/L, no planted
effect, 20,000 draws per cell.

    FLOOR geometry (n=8, pool=32)      L=24  0.0790 (SE 0.0019)
                                       L=28  0.0795 (SE 0.0019)
                                       Gaussian reference        0.0833

    The binomial null sits about 0.004 below the Gaussian tail at the floor.
    The approximation error is small and does not change any floor decision.
    The binomial-null item is CLOSED.

    REALISED geometry (n=40, k=4)      L=24  0.00005
                                       L=28  0.00000

So a pure null at the corpus's own median geometry fires essentially never --
the band-concentration result at the actual L. THE OBSERVED 30/77 = 0.390 IS
NOWHERE NEAR A NULL RATE, and small-sample noise is not a candidate explanation
in either direction.

THE MECHANISM. `d3_variance_anomaly.py` builds its baseline as

    pool = [x.metric for o in nb for x in by_region[o]]
    v_nb = variance(pool)

-- the variance of the CONCATENATED neighbours. By the variance decomposition
that quantity is `within-region variance + BETWEEN-region variance`. The
numerator is a single region's within variance. So whenever neighbouring
regions differ in MEAN, the denominator is inflated and every ratio is pushed
DOWN. The campaign authors exactly such differences: `_bits(seed_root, length)`
gives each world its own deterministic candidate, so region means differ by
construction.

Measured, same null, sweeping the between-region mean SD (within-region SD at
L=24 is 0.1021):

    between_sd   fire rate   lower   upper   lower fraction
    ----------   ---------   -----   -----   --------------
       0.000       0.00005       1       0        1.000
       0.040       0.00040       8       0        1.000
       0.080       0.02430     486       0        1.000
       0.100       0.07885    1577       0        1.000
       0.150       0.32835    6567       0        1.000
       0.200       0.56805   11361       0        1.000

    observed on the live corpus    0.390                    0.933 (28 of 30)

Every single simulated fire is LOWER, at every level. A between-region mean SD
near 0.16 reproduces the observed rate, and the observed 28-of-30 lower
fraction is the fingerprint of this mechanism and of nothing else.

THE CONTROL THAT PROVES IT IS THE DENOMINATOR. Replace the concatenation with
the df-weighted POOLED WITHIN-REGION variance of the neighbours and rerun the
identical data:

    between_sd    0.000   0.040   0.080   0.150   0.200
    fire rate   0.00005 0.00005 0.00005 0.00005 0.00005

Completely immune. The entire signal is the baseline construction.

ADJUDICATION. D3's 30 fires / 77 eligible with 28 LOWER is NOT detector output
about the corpus's dispersion. It is a structural downward bias in d3.v0's
baseline, driven by authored between-region mean differences. It is neither
"small-sample noise" nor evidence of local variance structure, and Archaeon was
right to withdraw the interpretation -- though the reason is different from the
one on offer.

WHAT IS NOT EXPLAINED. The 2 of 30 UPPER fires. The bias model predicts zero
upper fires and the corpus produced two. That residue is the only part of the
live output not accounted for here, and it is a thing to look at, not a claim.

THE FIX IS d3.v1 AND NOT MINE. Comparing a region's within variance against the
POOLED WITHIN variance of its neighbours is the standard estimator and is
immune, as shown. It changes the detector's firing logic, so it is a new
version requiring its own qualification; d3.v0's admission is unaffected and
its band remains a phase boundary (F-2).

DOES NOT LICENSE: any statement about the live corpus's dispersion structure
from d3.v0 output while the baseline contains the between-region component.

--------------------------------------------------------------------------
## ITEM 4 -- TRACK B: C3's PAIRED / CLUSTERED ANALYSIS, DECLARED BEFORE ISSUE

DECLARED NOW, ahead of the corpus, against `archaeon/producer/campaign_c3.py`:
one `seed_root`, four IC samples shared across all rules.

    C3-U1  accuracy of ONE rule          unit = the IC SAMPLE, n = 4
                                          (the operator's declaration; adopted)
    C3-U2  rule A versus rule B           PAIRED across the four shared samples
    C3-U3  a claim about the POPULATION   unit = the RULE; n = 120 for C3-acq,
           of rules                       6 for C3-hist
    D3 over C3                            one row per rule; a descriptor region
                                          needs 8 independent rules

I previously argued for the IC as the unit for U1 and the operator has
restated the IC sample. Adopted as declared, with two consequences recorded
rather than re-argued, and one measurement that settles it empirically:

  (a) at four samples a paired permutation has 2^4 = 16 sign patterns, so its
      minimum attainable two-sided p is 0.125. NO SAMPLE-LEVEL PERMUTATION TEST
      IS ELIGIBLE AT 0.05. U1 is therefore reported as an ESTIMATE WITH AN
      INTERVAL (t on 4 samples, or the exact binomial across pooled ICs
      reported beside it), never as a test.
  (b) the interval is about 1.6x wider than the IC-unit interval, so
      borderline qualification comparisons will read INDETERMINATE. That is a
      cost of the conservative choice, not an error in it.

  (c) THE MEASUREMENT THAT DECIDES IT, computable from C3 itself once issued:
      report the INTRACLASS CORRELATION of accuracy across the four IC samples.
      If ICC is indistinguishable from zero the ICs are exchangeable draws and
      the IC-unit interval is licensed as a secondary; if ICC is positive the
      sample unit is required and four samples are too few. Declaring this now
      converts a disagreement about the unit into a number the corpus supplies.

RETAINED AS DIRECTED: both success criteria (`at_T` historical, stable-family
default) and particle2's HELD label -- usable as an organism, not as a
qualification number, until the source bytes are recovered.

--------------------------------------------------------------------------
## ITEM 5 -- TRACK C: THE H5 FIXED-DECODER COMPARISON, SCOPED

RULE TEXT, all four predeclared before the comparison runs.

  1. THE ACCESS DIFFERENCE IS A CONSTRUCTION FACT, NOT A RESULT. A 12-bit
     genome under the direct decoder (low 8 bits) reaches at most 8 distinct
     neighbour rules under a single bit flip -- flips of the high 4 bits are
     silent. A permuted decoder can reach up to 12. That gap is authored by
     the encoding and is bounded ANALYTICALLY. It must be predeclared with its
     bound, and only the EXCESS over the construction bound is evidence about
     a decoder's learned quality. This is the same rule as HA-1.3's: a known
     construction curve is not an empirical exploitation result.
  2. THE ACCESSIBLE-VARIATION COUNT EXCLUDES THE PARENT'S OWN PHENOTYPE.
     Including it lets neutrality inflate the count and turns a decoder that
     changes nothing into a decoder that "accesses" its own starting point.
  3. NEUTRALITY IS A SEPARATE STATISTIC, reported alongside and never summed
     into accessible variation. They answer different questions and move in
     opposite directions.
  4. THE 224 CLASSES ARE TERMINAL-BEHAVIOUR CLASSES AT 8 STEPS ON THE 7-RING,
     AND NOTHING ELSE. Not ECA rule classes, not a general equivalence. Any
     statement using the number carries that scope in the same sentence.

--------------------------------------------------------------------------
## ITEM 6 -- NK: THE VARIANCE FORMULA IS AN ENSEMBLE EXPECTATION

RULE TEXT. `E[Var] = (1 - 2^-(k+1)) / (12 N)` is the expectation over
INDEPENDENTLY GENERATED TABLES. A realised landscape need not equal it and
usually will not. The predicted k=4/k=0 ratio of 1.9375 is an ENSEMBLE ratio,
so the test is on the ensemble means across landscapes and THE LANDSCAPE
REMAINS THE UNIT for the k contrast.

This amends my own X1 worked analysis, which listed the formula under
"predicted value" in a way that reads as a per-landscape prediction. The
analysis `nk.k_variance_ratio.v1` is otherwise unchanged: unit = landscape,
n = 6 per k, min attainable p 0.0022, eligible.

--------------------------------------------------------------------------
## OPEN, AND FOR WHOM

    Archaeon    d3.v1 with a pooled-within-region denominator, if the live
                corpus is to be read at all; d3.v0's admission is unaffected
    Archaeon    the 2 of 30 UPPER fires are unexplained by the bias model
    Archaeon    report the ICC across C3's four IC samples once issued; it
                settles the U1 unit empirically
    Lane owners Sigma estimated on each disjoint pilot before H0 sizing; and
                whether the interaction is a primary (its own sizing) or a
                declared secondary
    Lane owners if confirmation POWER is promised, state the probability
    Daedalus    F2 needs the load receipt to carry ACTUAL bytes and digest
    Vivarium    BUDGET_EXHAUSTED as a distinct termination status
    Operator    the harmonia-m2 credential
    Daedalus    F-6, an owner-preserving reissue path

Unchanged and still mine: HA-1's six rulings; X1 with route (c) as the worked
analysis; C3's three analyses registered at issue.
