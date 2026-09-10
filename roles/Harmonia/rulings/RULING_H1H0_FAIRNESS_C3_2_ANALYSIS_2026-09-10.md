# signature_v0 fairness, C3-2's pre-declared analysis, H0 phase-2 sizing, D3's upper fires

2026-09-10. Lane: Harmonia. Rules `QR-1.1.0`. Nothing outside my lane modified;
no campaign retuned, no arm licensed.

==========================================================================
# ITEM 2 -- signature_v0: THE FEATURE IS FAIR; THE COMPARISON IS INERT

## 2a. FAIR, as a feature, with two conditions

RULING: **FAIR**. `licensed_metadata(tt)` computes four flags -- popcount
bucket, permutation-symmetric, self-dual, monotone -- from the target's TRUTH
TABLE, which IS the task specification the solver is given. No oracle call, no
solution, no program, no target-family provenance, no information about which
source tasks were built to help. It is recorded on every task and readable by
every arm.

That is exactly the design's own criterion: "a declared structural signature of
task specification visible equally to all arms; it cannot use hidden target
labels or target-family provenance to recognize answers." A function of the
specification cannot leak the answer, because the specification is not the
answer -- the answer is a PROGRAM, and no flag here is a function of any
program.

TWO CONDITIONS, both mechanical:
  (i)  the four flags must have been declared BEFORE phase-1 outcomes were
       visible. A feature chosen after seeing which sources helped is selection
       on the outcome, whatever it is computed from. Checkable in git: the
       commit introducing `licensed_metadata` must predate the phase-1 receipt.
  (ii) the baseline's EQUAL ACCESS must be recorded, not merely permitted. The
       fresh arm's equal allowance (`seed_probe_count = K_PACK`) is in the
       payload; keep it there.

## 2b. AND IT DOES NOT MATTER AT THIS SCOPE. THE MEASURED FACT DECIDES.

The de-duplicated pool of distinct witness inputs is **4**. `K_PACK` is **4**.
Confirmed in the phase-2 receipt: `k_pack: 4` and `"shortfall": 0` on every one
of the ten packs -- four requested, four available, zero short.

THEREFORE EVERY PACK IS THE SAME SET. A retrieval policy that must choose 4
distinct items from a pool of exactly 4 has nothing to choose. `signature_v0`
and `random_compatible` deliver IDENTICAL CONTENT and differ only in ORDER.

CONSEQUENCE, and this is the ruling that matters: at this scope a
relevant-versus-random comparison **is not a relevance comparison**. It is an
ORDER comparison on an identical input set. Reporting it as evidence about
relevance would be a claim inflation of the same shape as an intervention that
was never applied -- the policy is inert with respect to content BY
CONSTRUCTION, and no fairness ruling on the feature can change that.

RULING ON THE SCOPE FACT: **run the alpha as designed, and report it as a
finding about scope**, with the comparison RELABELLED as order-only. Do NOT set
`RELEVANCE_LICENSED`. The alpha stays TRANSPORT-ONLY -- which is what the code
already encodes and the design already permits, but now for a stronger reason
than the one on offer: not "no fair relevance feature exists yet", but
**no selection is possible at this scope**.

An order effect is still a real, reportable observation: CEGIS consumes
counterexamples in sequence, so order can change rounds-to-match. Report it
under its own name.

## 2c. WHEN RELEVANCE BECOMES TESTABLE -- a quantitative re-scope condition

Packs differ in content only when |pool| > K. For them to differ
SUBSTANTIALLY -- expected overlap at or below half -- requires |pool| >= 2K.
At K=4 that is |pool| >= 8.

The 3-bit task has only **8 possible witness inputs in total**, and 4 were
observed. So the maximum conceivable pool at 3 bits only just reaches 2K, and
the realised pool is half of that. RELEVANCE IS NOT TESTABLE AT 3 BITS WITH
K=4, at any sample size, however fair the feature. The fix is one of:

    raise the input width   4-6 input tasks give 16-64 possible witnesses
                            (the design's own beta step)
    lower K                 K=1 or 2 makes selection possible at 3 bits, at
                            the cost of a much weaker treatment
    both

Beta must satisfy |pool| >= 2K, measured and reported, BEFORE a relevance arm
is licensed. That is a precondition, not a preference.

==========================================================================
# ITEM 3 -- C3-2: THE PRE-DECLARED ANALYSIS

Declared before the readout is written. Archaeon writes numbers to
`archaeon/docs/h0h5/C3_2_READOUT.md`; the rules below are what they are
measured against.

## 3a. THE THREE UNITS

    C3-U1  accuracy of ONE rule        unit = the IC SAMPLE, n = 4
    C3-U2  rule A versus rule B        PAIRED across the four shared samples
    C3-U3  a claim about the           unit = the RULE; n = 120 for C3-acq,
           POPULATION of rules         n = 6 for C3-hist
    D3 over C3                         one row per rule (aggregated)

Adopted as the operator declared. One unit per ANALYSIS, never one per corpus.

## 3b. U1 IS AN ESTIMATE WITH AN INTERVAL, NEVER A TEST

At four samples a paired sign-flip permutation has 2^4 = 16 patterns, so its
**minimum attainable two-sided p is 0.125**. No sample-level test is eligible
at alpha 0.05, whatever the data. U1 therefore reports a point estimate and an
interval (t on 4 sample accuracies), with the pooled-IC binomial interval
printed BESIDE it as a reference, never instead of it. No p-value is computed
at the sample level and none may be quoted.

    attainable range of a sample-level two-sided p    [0.125, 1.0]
    eligible at 0.05                                  NO -- recorded, not run

## 3c. THE ICC, WHICH SETTLES THE UNIT EMPIRICALLY

Two-way layout, rules as rows, the four shared IC samples as columns, cell
value = that rule's accuracy on that sample. Rows used: every rule in C3-acq
with all four samples present (report C3-hist's six separately; six rows do not
estimate a variance component usefully and the number is descriptive there).

    MS_sample = n_rules * sum_s (abar_s - abar)^2 / (4 - 1)
    MS_error  = sum_r sum_s (a_rs - abar_r - abar_s + abar)^2
                / ((n_rules - 1) * (4 - 1))

    ICC_sample = (MS_sample - MS_error)
                 / (MS_sample + (n_rules - 1) * MS_error)

    attainable range   [-1/(n_rules - 1), 1]
    eligible count     n_rules with all 4 samples present; printed BEFORE the
                       ICC, and the ICC is void without it

DECISION, declared now:
  ICC not distinguishable from 0 -> the four samples carry no shared effect,
      the ICs are exchangeable draws, and the pooled-IC interval is LICENSED as
      a secondary report beside U1's sample-level interval.
  ICC materially positive       -> the sample unit is REQUIRED and four samples
      are too few for any test; U1 stays an estimate and C3-U2 contrasts are
      reported with their width, not their significance.

Either way the declared U1 unit stands. The ICC decides only whether the
pooled-IC interval may appear beside it.

## 3d. D3 OVER C3: d3.v1 PRIMARY, d3.v0 BESIDE IT

One row per rule (aggregated), so repeats cannot inflate a region's n. A
descriptor region needs **8 independent rules**; at 120 rules over 10 regions
that is about 12 per region, the discrimination optimum.

Report d3.v1 (pooled-within denominator) as PRIMARY and d3.v0 BESIDE it, with
the difference between them stated. Reason: on the live bitstring corpus the
v0 concatenation denominator carries between-region variance and produced 30
fires with 28 LOWER; v1 was immune across every between-region SD tested. C3 is
a different corpus and may not show it, and reporting both is how we find out
rather than assume.

    attainable range of the ratio      (0, inf)
    band                               [0.3333, 3.0]
    eligible count                     regions with >= 8 independent rules AND
                                       a neighbourhood of >= 16; printed before
                                       any fire count
    calibrated rate                    at the REALISED geometry, with its
                                       binomial SE. A rate without its geometry
                                       and its denominator may not be quoted.

d3.v0's band remains a phase boundary: for any true ratio strictly inside it
the fire rate goes to 0 as n grows, so a zero here is not evidence of a clean
corpus.

## 3e. THE 18 NULL ROWS: AN EXACT-SYMMETRY GATE, NOT A STATISTICAL ONE

These are exact invariants (HA-1.5a). The expected answer is known with
probability 1, there is no distribution, no tolerance and no threshold. ONE
violation is a defect in the library or the transform and it HALTS the family.

**PASS requires all three fields identical**, compared as exact integers, not
floats:

    1. accuracy per IC sample, as the CORRECT COUNT out of the sample size
       (integer equality; a float comparison may absorb a one-IC difference)
    2. the incorrect COUNT per sample
    3. the incorrect-set MASK DIGEST, after applying the declared IC index
       mapping for that transform

**REFLECT.** Reflection permutes cells and preserves cell counts, so
density is invariant and the correct answer is unchanged. With the rule table
and the IC reflected together, the trajectory is the reflection of the
original. All three fields must match, the mask digest under the reflection
index mapping.

**COMPLEMENT, and the target flip.** Complementing the IC sends density rho to
1 - rho, so the TARGET FLIPS. Under D-C1-1's odd `n_cells` there are no ties,
so the flip is total and well defined. With the rule table complemented too,
the prediction flips as well -- therefore CORRECTNESS IS INVARIANT and accuracy
must be EXACTLY EQUAL, not complementary.

    DIAGNOSTIC SIGNATURE, worth stating because it is unambiguous: if the
    complement arm returns accuracy = 1 - original accuracy, the target flip
    was NOT applied. That is a specific, diagnosable implementation defect and
    must be reported as that rather than as a generic FAIL.

**INDETERMINATE** (not PASS, not FAIL):
  - the mask digest is absent or the IC index mapping for the transform was not
    recorded. Accuracy and count agreement is NECESSARY BUT NOT SUFFICIENT --
    two different incorrect SETS can share a count, so without the digest the
    invariant is unverified, not verified.
  - a row is missing, or a sample is missing for a row.
An INDETERMINATE row is not a pass and does not count toward the gate; it is
counted and reported.

    eligible count      18 rows, printed before the verdict
    attainable values   {identical, not identical} -- exact
    expected            identical, probability 1
    no p-value, no threshold, no tolerance

==========================================================================
# ITEM 4 -- H0 SIZING FOR PHASE 2 AS BUILT, UNDER QR-1.1.0

Twelve target tasks x four cells, paired by task, diagnostic alpha.

WHAT I WILL REPORT. `G_joint_treatment_S11_minus_S00` and `I`, as SEPARATE
results, each with its own SE computed from the Sigma ESTIMATED ON THIS PILOT
(`sigma_from_blocks` over the 12 paired blocks), plus `se_ratio_report`: the
MEASURED SE(I)/SE(G) with the sqrt(2) exchangeable-equal-variance reference
printed beside it, never instead of it. G is named as a JOINT-TREATMENT
contrast because in a 2x2 it equals main1 + main2 + I; it is not a marginal
main effect and will not be reported as one. Simultaneous coverage across the
two primaries is Bonferroni.

UNIT AND ELIGIBILITY. The block is the TARGET TASK, so n = 12 and the minimum
attainable two-sided paired p is 2/2^12 = 0.00049 -- eligible even under the
confirmatory gate. The two-seed structure is a DIAGNOSTIC replicate within a
block and does not multiply n; seeds, cells and CEGIS rounds are within-unit
repeats.

HA-1.6 CONFIRMATION. The two-seed diagnostic alpha PROCEEDS. `purpose =
DIAGNOSTIC` means the eligibility gate is recorded and not enforced, per the
QR-1.1.0 scoping; and at 12 blocks it would pass the gate anyway. Nothing here
waits on confirmation sizing.

WHAT IT MAY NOT BE QUOTED AS, in one line: **a diagnostic alpha is an
instrument check -- its estimates size the confirmation and may never be quoted
as evidence for or against H0's effect or its interaction.**

==========================================================================
# ITEM 5 -- WHAT I NEED FOR D3's TWO UPPER FIRES

The bias model predicts ZERO upper fires and the corpus produced two. That
residue is the only part of the 30/77 not accounted for. For each of the two
upper-firing regions I need, as rows:

    region id, family, and neighbourhood_kind for that region
      (k_nearest vs the family fallback -- a threshold tuned for k nearest
       neighbours means something different against a whole-family pool, and
       the detector already labels this)
    the region's rows: one metric value per INDEPENDENT UNIT, with the unit id
    the neighbour region ids actually used (neighbours_of), and for each,
      its rows as metric values with unit ids
    the recorded v_reg, v_nb and ratio, so I can reconcile against my recompute
    the coordinate centroid used for that region and its neighbours
    whether any region in that set still carries repeats rather than
      aggregated units

Four checks it enables, in order: recompute the ratio under d3.v1's
pooled-within denominator and see whether the fire survives; check whether the
neighbourhood is the family fallback rather than k_nearest; check for a single
outlier row driving `v_reg`; and check whether the region spans sub-units with
different means, which would put a between-component in the NUMERATOR and
produce an upper fire by the mirror of the mechanism that produces the lower
ones.

The two upper fires stay UNADJUDICATED until then. They are not a finding and
not a defect; they are the open residue.

==========================================================================
# OPEN, AND FOR WHOM

    Archaeon    the rows and fields above for the 2 upper fires
    Archaeon    confirm in git that `licensed_metadata` predates the phase-1
                receipt (fairness condition (i))
    Archaeon    C3-2 readout numbers against 3a-3e; the ICC's eligible count
                printed before the ICC
    Archaeon    beta: measure and report |pool| and K, and satisfy
                |pool| >= 2K before any relevance arm is licensed
    Operator    `RELEVANCE_LICENSED` stays FALSE on this ruling; the alpha is
                transport-only and the relevant arm stays WITHHELD
    Operator    the harmonia-m2 credential
    Daedalus    F-6, an owner-preserving reissue path
