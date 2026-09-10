# WP-X1: the analysis-family convention, with a worked analysis

2026-09-08. Lane: Harmonia (OWNER). Convention `analysis.v1`. Numbers reproduce
from `roles/Harmonia/science/ha1num.py`.

An ANALYSIS is a derived claim over observations that already exist. It is not
an experiment and it never re-executes anything. The engine adjudicates
executions; analyses are adjudicated here, outside executors, and a within-run
aggregate keeps whatever meaning the executor gave it.

--------------------------------------------------------------------------
## 1. THE CONVENTION -- TEN REQUIRED FIELDS

Seven come from the acceptance criteria. Three more are added because this
campaign has already been bitten by their absence; they are marked ADDED.

    1  source_refs          an ORDERED list of immutable references, each
                            (world_id, observation_id, event_seq, spec_hash).
                            NEVER a query. A query is a way of FINDING
                            sources, not a source: it returns different things
                            at different times, so an analysis identified by a
                            query is not reproducible.

    2  source_set_digest    sha256 over the canonicalised, sorted source_refs.
                            Replacing or re-versioning any source changes it;
                            originals are never touched (X1-c).

    3  analysis_version     semantic version of the analysis CODE, kept
                            separate from the data. (source_set_digest,
                            analysis_version) together identify the result.

    4  unit_of_analysis     the independent unit, DECLARED BEFORE ANY ROW IS
                            READ, plus declared_n and the explicit mapping
                            rule from source_refs to units. This is the field
                            that stops repeats inflating n (X1-d).

    5  measurement_identity <kind>.<field> with direction and range, per R3.
                            Two measurement identities are never pooled; an
                            analysis spanning them is REFUSED, not averaged
                            (X1-b).

    6  declared_null        the reference distribution, its generator, and the
                            ATTAINABLE RANGE of the statistic under it.

    7  mode                 FROZEN or EXPLORATORY. FROZEN requires the
                            manifest hash committed before the first source is
                            read. EXPLORATORY output may never be relabelled
                            FROZEN afterwards -- there is no retroactive
                            pre-registration (X1-d).

    8  eligible_count       ADDED. Computed and PRINTED before the statistic.
                            A statistic over an ineligible set is void, and
                            the count is the first thing a reader needs.

    9  min_attainable_p     ADDED (HA-1.6). The smallest p the design's own
                            lattice can produce. If it exceeds alpha the
                            analysis is INELIGIBLE and must be resized or
                            reclassified as descriptive.

   10  exclusions           ADDED. Every source_ref excluded, the rule that
                            excluded it, and the COUNT. An exclusion count is
                            part of the denominator, not housekeeping; D-16's
                            Class II count is exactly this field.

REFUSALS. declared_n greater than the independent-unit count. Two measurement
identities pooled. FROZEN mode whose manifest hash postdates its first source
read. A statistic reported without its eligible_count.

--------------------------------------------------------------------------
## 2. X1-d, DEMONSTRATED -- REPEATS DO NOT ADD UNITS, AND MORE REPEATS
##     MAKE THE NAIVE ANALYSIS WORSE, NOT NOISIER

Pure null over NK at route (c)'s geometry: k carries NO effect, landscapes
differ from one another, starts are drawn inside landscapes. Two-sided
permutation test at alpha 0.05, false positive rate over 400 trials:

    geometry                     unit = LANDSCAPE      unit = START
    -------------------------    ----------------      ------------
    6 landscapes/k,  20 starts        0.055               0.598
    6 landscapes/k, 100 starts        0.040               0.810

The landscape unit is calibrated. The start unit is not merely optimistic, it
is at 0.60 and 0.81 -- and it gets WORSE as starts are added. Collecting more
data inside the same landscapes drives the naive false-positive rate toward 1.
That is the shape of the error, and it is why field 4 is declared before the
rows are read rather than chosen after seeing them.

--------------------------------------------------------------------------
## 3. THE WORKED ANALYSIS -- ROUTE (c), THE NK k-VARIANCE RATIO

The first real analysis, stated as the worked example per the order.

    analysis_id            nk.k_variance_ratio.v1
    mode                   FROZEN -- this manifest is hashed and committed
                           before the A3 corpus is read
    question               does the ensemble variance of per-candidate score
                           differ between k=0 and k=4 NK landscapes?

    source_refs            the WP-A3 corpus at k in {0, 4}, six landscapes per
                           k, 20 starts per landscape. Enumerated and hashed
                           at freeze.
    source_set_digest      computed at freeze; recorded before the statistic
    analysis_version       1.0.0

    unit_of_analysis       THE LANDSCAPE. Not the query, not the candidate.
    declared_n             6 per k, 12 total
    mapping rule           each landscape contributes exactly ONE value: the
                           within-landscape variance of score over its 20
                           starts

    measurement_identity   nk_landscape.score, direction higher-is-better,
                           range declared with the length actually used
    statistic              mean within-landscape variance at k=4 divided by
                           the same at k=0

    declared_null          label permutation: permute the k labels across the
                           12 landscapes, recompute, two-sided
    eligible_count         12 landscapes, printed before the statistic
    min_attainable_p       2 / C(12,6) = 0.0022  -> ELIGIBLE at 0.05
    predicted value        E[Var] = (1 - 2^-(k+1)) / (12 N), so the k=4/k=0
                           ratio is 1.9375 EXACTLY, and N cancels
    exclusions             any landscape contributing zero variance, counted
    void conditions        fewer than 6 landscapes per k delivered; the
                           exchangeability null failing integer-exact
                           identity; the manifest hash postdating a source read

ONE DISCREPANCY TO RESOLVE BEFORE FREEZE, not blocking. BRANCHES WP-A3
specifies `length 24`; packet v2 s1.9 computes H2 at `N = 16`. The analysis
must declare which length it ran on. For THIS statistic it happens not to
matter -- N cancels out of the ratio, so the predicted 1.9375 is the same
either way -- but the absolute variances differ by a factor of 1.5 and H2's
predicted values are stated at N=16. Someone should reconcile the two
documents; the analysis states its own length regardless.

WHY THIS IS THE RIGHT INSTRUMENT, restated from the route (c) ruling: a
variance-ratio test across landscapes pools evidence in the ordinary way and
gains power with n, whereas D3's fixed band LOSES discrimination with n for any
ratio inside it (F-2). 1.9375 is inside D3's band. The test is eligible; the
band is not.

--------------------------------------------------------------------------
## WHAT THIS LICENSES

Any analysis carrying the ten fields may be registered and reported as an
analysis. `nk.k_variance_ratio.v1` may be frozen and committed now, before the
A3 corpus exists, because every field except the digests is knowable in advance
-- which is the point of freezing it.

## WHAT IT DOES NOT LICENSE

An analysis identified by a query. Pooling measurement identities. Any n that
exceeds the independent-unit count. Relabelling exploratory output as frozen.
Reporting a statistic without its eligible count and its minimum attainable p.

## OPEN, AND FOR WHOM

    Archaeon   reconcile NK length: BRANCHES WP-A3 says 24, packet v2 s1.9
               computes H2 at N=16
    Archaeon   the A3 corpus at six landscapes per k for k in {0, 4}; the
               analysis is frozen and waiting for it
    Harmonia   register the remaining C3 analyses once the corpus is issued
               (three units, three analyses -- see the C3 ruling)
