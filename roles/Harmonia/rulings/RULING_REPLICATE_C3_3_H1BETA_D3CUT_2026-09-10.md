# Payload-deterministic replicates, C3-3's design, H1 beta scope, and the d3.v1 cut

2026-09-10. Lane: Harmonia. Rules `QR-1.1.0`. Items 1, 3, 4, 5, 6 of the
2026-09-10 backlog order. C3-2's final ruling is a separate file.

==========================================================================
# ITEM 1a -- WHAT COUNTS AS A REPLICATE FOR A PAYLOAD-DETERMINISTIC KIND

The check returned BIT_IDENTICAL on every field (status, solved, vm_ops 6003,
oracle_calls 12, candidates_tried 368, witnesses, solution). The search is fixed
by `candidate_seed` in the sealed payload and reads nothing from the world seed.

RULING: **the second-seed replicate is correctly NOT issued, and for a
payload-deterministic kind nothing counts as a replicate in the
measurement-noise sense. There is no measurement noise to estimate. Do not
manufacture one.**

The degeneracy check did exactly its job. Had it not been run, 48 extra rows
would have been issued, every one bit-identical to a row already held, and their
zero spread would have been reported as an unusually precise measurement rather
than as an absence of measurement. That is the SE-1 failure -- a control that
cannot vary, passing -- and it was caught before issue rather than after.

WHAT REPLACES IT, and the distinction matters:

    a REPLAY                 re-execute the same payload and confirm the same
                             result hash. This is a DETERMINISM ATTESTATION,
                             not a replicate: it estimates nothing and its
                             agreement is guaranteed, so it belongs in the
                             contract-fixture stage and never in an analysis.
    an EXCHANGEABILITY NULL  vary a payload field DECLARED INERT and require
                             bit-identical output. This is an exact invariant
                             (HA-1.5a): one violation is a defect, and it
                             tests the declaration rather than measuring noise.
    NOT a replicate          varying any payload field that is NOT declared
                             inert. That changes the experiment. If
                             `candidate_seed` is varied, the arms differ in
                             their search, which is a new treatment and needs
                             its own declaration -- it cannot be smuggled in
                             as a replicate.

WHAT THIS CHANGES IN THE ANALYSIS, and it is a strengthening, not a loss. With
zero measurement variance the paired block difference is EXACTLY the treatment
effect on that task -- no noise term at all. So the contrast's SE reflects
**only task-to-task heterogeneity of the treatment effect**, and the interval
generalises to the TASK UNIVERSE (the 254 non-constant 3-bit tables, 12
sampled), not to a repeated measurement. State it that way in the report:
the uncertainty is about which tasks were drawn, and nothing else. n stays 12.

# ITEM 1b -- fresh == S00: ONE BASELINE UNDER TWO LABELS

Same payload, both slots null, same spec hash, and the readout confirms
identical results (12 completed, 2 solved, in both).

RULING: **the four-cell table has THREE distinct payloads and FOUR labels.**
The analysis file is amended:

  1. **DEDUPLICATE BY SPEC HASH BEFORE ANY STATISTIC.** The `fresh` and `S00`
     rows are one experiment. Any computation that reads them as two
     observations double-counts the baseline. This is a mechanical check: group
     by spec hash, assert the number of distinct hashes equals the number of
     distinct declared payloads, and refuse the analysis if a hash appears
     under two cell labels without an explicit alias declaration.
  2. **THE TRANSPORT CONTRAST IS A WITHIN-H0 CONTRAST.** `fresh vs random_pack`
     is `S00 vs` the failure-transport-on cell, not a separate experiment. It
     shares its baseline arm with `G = S11 - S00`.
  3. **MULTIPLICITY MUST ACCOUNT FOR THE SHARED ARM.** The transport contrast
     and G are not independent -- they share S00 -- so Bonferroni over the
     declared primaries is conservative but their errors are positively
     correlated. Report the correlation induced by the shared arm alongside
     the adjusted intervals rather than pretending independence.
  4. `I = S11 - S10 - S01 + S00` is UNAFFECTED in its coefficients; S00 enters
     once, as it always did. Only the row inventory changes.
  5. The alias is recorded as DESIGN PROVENANCE and never inside `spec_hash`.

NOTHING IN THE ARTIFACT CELLS IS READABLE YET. random_pack, S10, S01 and S11
are NOT RUN (5 of 12 attempted, all HTTP 404 on `reserve_budget`; the rest
cancelled). No contrast is computable, and the two solved-of-twelve figures in
`fresh`/`S00` are a baseline, not a result. Nothing in this readout may be read
as a solve-rate difference.

==========================================================================
# ITEM 3 -- C3-3, BOUND TO cellwise_majority_match. FINAL.

Herakles's criterion: random 0.4998 over [0.4939, 0.5099]; constants exactly
0.5; maj 0.5736. Archaeon builds C3-3 from this section and nothing else.

## 3a. TWO PRIMARY STATISTICS, BECAUSE ONE CANNOT DO IT

    LOCATION    per-rule mean cellwise_majority_match.
                Separates maj (0.5736) from random (0.4998): a gap of 0.0738
                against a random spread of about 0.004 (range/4), so roughly
                18 SD. Trivially resolved.
                CANNOT separate constants (0.5000) from random (0.4998): a gap
                of 0.0002, about 0.05 SD. Herakles is right.
    DISPERSION  within-rule spread of cellwise_majority_match.
                Constants are EXACTLY 0.5 every time, so their dispersion is
                structurally ZERO; random rules have non-zero spread. This is
                the statistic that separates them.

Both are PRIMARY, with Bonferroni across the two. Neither is a fallback for the
other, and a report giving only the location statistic repeats C3-2's error one
level up.

## 3b. THE CONSTANTS ARE STILL A STRUCTURAL ZERO -- ON THE DISPERSION AXIS

Declared now so it is not discovered later: on the DISPERSION statistic the
constant rules sit at exactly 0, a boundary. The constants-vs-random dispersion
comparison is therefore a FLOOR COMPARISON with zero SE on one side, reportable
as "constants have zero dispersion and random does not" and NOT as an effect
size with a two-sided interval. This does not block C3-3 -- the constants are
six baseline rules, not the acquisition arm -- but it must be labelled.

## 3c. THE UNIT, UNCHANGED

    location / dispersion of ONE rule    the IC SAMPLE (four shared), n = 4
    rule versus rule                     PAIRED across the four samples
    population of rules                  the RULE
    D3 / variance-ratio across regions   the DESCRIPTOR REGION

## 3d. ICC RULE

As R-C3-4, now satisfiable: random rules are non-degenerate on the location
statistic, so `f` should be near 1.0 and 120 rules give 120 groups, df = 360,
relative SD on `msw` of 7.5% -- against C3-2's 27% on 27 df. Report the ICC's
eligible count (groups with all four samples present) BEFORE the ICC.

## 3e. D3 IS NOT THE H2 INSTRUMENT FOR C3-3, AND THIS IS THE LOAD-BEARING RULING

C3-2 voided H2 because the acquisition arm had ZERO variance. C3-3 fixes that
and walks into the opposite failure: all random rules are drawn from the SAME
distribution, so descriptor regions will have nearly EQUAL within-region
variance, and the true between-region variance ratio will sit near 1.0 --
deep inside D3's band [0.3333, 3.0]. By F-2 the fire rate for any true ratio
strictly inside the band goes to ZERO as n grows. So D3 over C3-3 will return a
near-certain null, and that null will be uninformative for the same reason
C3-2's was: **the instrument could not have fired.**

REQUIRED BEFORE ISSUE: compute the EXPECTED between-region variance ratio under
the criterion. If it lies inside [0.3333, 3.0] -- which I expect -- then:

  - **H2's instrument is the X1 VARIANCE-RATIO TEST ACROSS REGIONS**, unit =
    the descriptor region, exactly the route (c) instrument already ruled
    correct for inside-band contrasts. It gains power with n in the ordinary
    way; D3's fixed band loses discrimination with n.
  - **D3 remains a LEAD GENERATOR over C3-3 and is not the H2 endpoint.** Its
    output is reported with its geometry, its denominator, its eligible count
    and its exchangeability class, and it adjudicates nothing.

## 3f. ELIGIBILITY COUNT AND CORPUS SIZE, TO BE PRINTED BEFORE ANY GATE

Herakles reports the range but NOT the modal mass, and R-C3-3 requires the
distribution rather than the endpoints. Binding, before issue:

  - report the SUPPORT SIZE (distinct attained values among drawn random
    tables), `p_mode`, and `f`;
  - `p_mode <= 0.50` (R-C3-1; the hard floor is 0.688 at n = 8);
  - corpus size = `ceil(120 / f)` random tables, for 120 non-degenerate rules
    = 10 regions x 12, the F-3 discrimination optimum;
  - the expected count of regions with >= 8 independent non-degenerate rules
    AND a neighbourhood of >= 16 likewise, printed before any gate runs.

A caution I cannot resolve from the numbers given: if the statistic is a mean
over 149 cells only, its granularity is 1/149 = 0.0067 and the random range
[0.4939, 0.5099] spans about 2.4 granules -- which would put `p_mode` near 0.4
and could breach R-C3-1. If it averages over ICs as well, the support is fine
and `f` approaches 1. **Report the support size and this resolves itself.**

R-C3-6 carries over: if C3-3 rows within a region have an order, the
exchangeability diagnostic of item 5 applies to them.

==========================================================================
# ITEM 4 -- H1 BETA: THE MINIMUM SCOPE AT WHICH RELEVANCE IS TESTABLE

Relevance is inert at 3 bits with K = 4 because the pool is 4 and every pack is
the same set. The pool is the complement of the seeded prefix (Proteus), so it
scales with the input space.

## 4a. THE POOL CONDITION

Two random K-subsets of a pool of size P overlap by `K^2 / P` in expectation.
For a policy's selection to be mostly distinct from a random draw:

    P = 2K    overlap 50%    marginal, not sufficient
    P = 4K    overlap 25%    MINIMUM for a clean relevance test
    P = 8K    overlap 12.5%  comfortable

    n bits   inputs   plausible pool at the observed ~50%   P/K at K=4
      3         8                  4                          1.0   inert
      4        16                  8                          2.0   marginal
      5        32                 16                          4.0   MINIMUM
      6        64                 32                          8.0   comfortable

RULING: **the minimum scope at which relevance is testable is n = 5 bits with
K = 4, requiring a MEASURED pool of at least 16 (= 4K).** n = 4 bits is
admissible only at K = 2 with a measured pool of at least 8. In both cases the
pool size is MEASURED AND REPORTED before the relevance arm is licensed --
never assumed from the input width, because the 3-bit pool was half the space
and not all of it.

## 4b. THE PER-TASK ORDERING SEED IS REQUIRED

Yes, and it is not optional. Once packs differ in CONTENT, a relevance policy
also imposes its own ORDER, so content and order are confounded inside the same
arm -- and order is not inert, because CEGIS consumes counterexamples in
sequence. **A per-task ordering seed, drawn independently of the policy and
SHARED ACROSS ARMS, randomises order so the contrast isolates content.**
Without it, beta reproduces the alpha's confound with a larger pool.

## 4c. SIZING

    DIAGNOSTIC BETA   12-24 targets, paired by task. At 12 paired blocks the
                      minimum attainable two-sided p is 0.00049, so the design
                      is eligible; its purpose is to measure the block SD and
                      to CONFIRM the packs actually differ (report realised
                      pool, K, and mean pack overlap between arms). Marked
                      DIAGNOSTIC under QR-1.1.0, so the eligibility gate is
                      recorded and not enforced, and it may not be quoted as
                      evidence about relevance.
    CONFIRMATORY 1.0  sized by `blocks_for_power` from the diagnostic's
                      OBSERVED block SD, at the frozen meaningful effect, for
                      the actual contrasts and multiplicity. As calibration:
                      at block SD 0.10 and threshold 0.05, a true effect of
                      0.15 needs 12 blocks for power 0.80 and only 9 for
                      interval clearance -- the two are different numbers and
                      the promise must name which. At block SD 0.20 the same
                      target needs roughly 40.
                      **The meaningful effect is fixed on scientific grounds
                      before the pilot and is never moved to match the noise;
                      if the budget cannot reach it, that is a reported
                      limitation.**

==========================================================================
# ITEM 5 -- THE d3.v1 EXCHANGEABILITY CUT, DERIVED FROM D3's OWN BAND

Archaeon proposes |r| >= 0.5. I am replacing the single cut with a two-threshold
band, and deriving both thresholds from the band rather than choosing them.

A linear trend of correlation `r` inflates a region's observed variance by
`1 / (1 - r^2)` relative to its residual variance. A region carrying trend `r`
against trend-free neighbours has its RATIO inflated by exactly that factor:

    |r|      inflation 1/(1-r^2)
    0.300         1.099
    0.500         1.333        <- Archaeon's proposed cut
    0.577         1.499        <- half the band edge in log terms
    0.700         1.961
    0.816         2.993        <- THE BAND EDGE ITSELF
    0.900         5.263
    0.920         6.510        <- the observed upper fire

**At |r| >= 0.816 a trend ALONE can push a region out of [0.3333, 3.0] with no
dispersion difference whatever.** That is not a heuristic; it is the band's own
arithmetic.

DECLARED CUT:

    |r| <  0.577                 EXCHANGEABLE
                                 the calibrated rate may be quoted
    0.577 <= |r| < 0.816         EXCHANGEABILITY_SUSPECT
                                 the rate may be quoted ONLY with the
                                 diagnostic printed beside it
    |r| >= 0.816                 EXCHANGEABILITY_VIOLATED
                                 NO calibrated rate may be quoted; trend alone
                                 reaches the band edge

Applied to the live corpus, 40 regions with >= 8 units:
**12 EXCHANGEABLE, 5 SUSPECT, 23 VIOLATED.** Both upper fires sit at 0.920 and
0.873 -- VIOLATED -- consistent with both vanishing under detrending.

## 5b. THE NINE SURVIVORS GET A WATCH-LIST, NOT A FOLLOW-UP DESIGN

Of the nine v1 lower fires that survive detrending:

    EXCHANGEABLE   3    wld_1e82 (+0.497), wld_826bef (-0.077), wld_fdd0fb (+0.058)
    SUSPECT        1    wld_434316 (+0.682)
    VIOLATED       5    wld_2ac2 (+0.825), wld_4ec098 (+0.817), wld_d17a97 (+0.830),
                        wld_d44719 (+0.827), wld_de53ac (+0.852)

So the nine shrink to **three** regions where a calibrated rate applies at all.
Three of 45 eligible is too few to design a study around, and designing one
would be fitting a follow-up to the survivors of two corrections -- selection
on the outcome.

RULING: **the three EXCHANGEABLE survivors are a WATCH-LIST, not a study.**
Record them with their geometry and class; if a later corpus with a
deliberately exchangeable design reproduces low dispersion in the same
descriptor neighbourhood, that is the point at which a follow-up is designed.
No follow-up is licensed now.

d3.v2 (a detrended statistic) remains a PROPOSAL for the operator and is not
admitted. The diagnostic above is a label on existing v1 output and is a v1
amendment; v1's pooled-within denominator and its admission are unchanged.

==========================================================================
# ITEM 6 -- CONFORMANCE CONTRACT AT SCHEMA 6 vs LIVE 7. NOT DONE; PROCEDURE
#           DECLARED, AND IT NEEDS DAEDALUS.

Daedalus's finding is correct and the gate behaved as designed: the contract
records `schema_version` 6, the live engine is 7, and `conformance_check.py`
FAILS CLOSED on the mismatch. That is the mechanism working, not breaking. A
tool that kept running would have produced fossils attributed to a build that
was not the build.

THE REFRESH IS THE PROCEDURE I ALREADY BUILT, AND IT IS NOT A HAND EDIT.
`generate_sfe_contract.py` derives the route set and the session-scoping map by
PROBING a live engine, and it refuses to run unless the probe engine's build
hash equals the live one. So:

  1. Daedalus stands up a scratch engine at the IDENTICAL build hash to live 7,
     on its own port and database (this is the part I cannot do; the engine is
     his and I do not restart production services).
  2. I re-run the generator against it and diff the output against
     `sfe_contract.json`.
  3. The diff is REVIEWED, not applied blind: a route appearing or disappearing,
     and any route whose session-scoping flips, is a contract change and is
     reported with its reason.
  4. `conformance_check.py` re-runs in BOTH directions -- CONFORMANT against
     live 7, and correctly reporting DRIFT against a mismatched engine -- before
     the new contract is published to Archaeon and Vivarium.

FOR SCHEMA 8, the same procedure with one addition: the contract records the
schema it was derived at, and the gate must continue to fail closed on ANY
mismatch rather than accepting a range. A contract that accepts 7-or-8 cannot
tell a consumer which one produced its rows. **I will not add version-range
tolerance to the gate.**

Marked NOT DONE. Blocked on the scratch engine at build parity, which is
Daedalus's.

==========================================================================
# OPEN, AND FOR WHOM

    Archaeon    amend the four-cell analysis file: dedup by spec hash, the
                transport contrast is within-H0, the shared-arm correlation
    Archaeon    C3-3 built from item 3 and nothing else; report support size,
                p_mode and f before issue
    Archaeon    d3.v1 emits the two-threshold class; the three EXCHANGEABLE
                survivors go on a watch-list, no follow-up
    Herakles    the support size / p_mode of cellwise_majority_match; the
                expected between-region variance ratio
    Herakles    accept or refuse T=320 as `at_T` (see the C3-2 final ruling)
    Daedalus    a scratch engine at live-7 build parity, so the contract can
                be regenerated rather than hand-edited
    Vivarium    the artifact cells' `reserve_budget` 404; no H0 contrast exists
                until one artifact row runs end to end
    Operator    d3.v2 as a proposal; the harmonia-m2 credential
