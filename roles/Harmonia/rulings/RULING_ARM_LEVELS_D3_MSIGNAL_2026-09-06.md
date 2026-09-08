# Harmonia ruling: arm binding, analysis levels, D3 admission, M-SIGNAL

Date: 2026-09-06. Lane: Harmonia (audit/qualification). No code outside my lane
was modified. Measurements below are reproducible from the commands given.

## 1. ARM RULING -- CONFIRMED, with two binding conditions

The operator's three-way split is correct and I confirm it:

    execution parameters      -> sealed execution spec (spec_hash)
    family + arm assignment   -> separately sealed experimental design
    execution <-> design link -> audit envelope, preserved in PEW

It is right for a specific reason: it separates what must be IDENTICAL across
arms (the execution) from what must DIFFER (the assignment). The A/B same-hash
acceptance test is the load-bearing part -- it proves the arms differ only in
label, which is what makes an arm contrast interpretable at all.

CONDITION 1 -- ORDERING, NOT JUST SEALING. Sealing the design proves it was not
edited; it does not prove it existed before the outcomes. The design seal must
carry an ordering proof against the execution (committed_seq or equivalent), or
post-hoc assignment is indistinguishable from pre-registered assignment. A hash
proves immutability, not precedence.

CONDITION 2 -- THE LINK MUST BE A RELATION, NOT TEXT. I measured that
family_members refuses member_kind "family" (422), so a design-to-execution
chain recorded only inside a manifest string is sealed but NOT traversable. If
the audit envelope carries the binding as freeform text, PEW preserves it but no
consumer can follow it mechanically. Daedalus owns whether this becomes a
first-class relation; without it, "PEW preserves the binding" is true and not
sufficient.

## 2. THE THREE LEVELS -- 32 obs / 8 worlds / 2 families

Asked before any power calculation, which is the correct order.

    SELECTED    the 8 worlds. They are the 2x2x2 factor grid, chosen by design.
                Deliberate coverage, not sampling.
    RANDOMIZED  whatever level ARM ASSIGNMENT happens at. Must be declared
                explicitly; it is the only level at which a causal contrast
                exists.
    ANALYZED    must equal the randomized level or be coarser. NEVER finer.

THE HARD FINDING: 2 FAMILIES IS NOT n=2. Two families are two CONDITIONS, not
two replicates. If arm is assigned AT THE FAMILY LEVEL there is exactly one
assignment per arm and no contrast is estimable -- not underpowered, not
estimable. If that is the current design it must change before any power
calculation is meaningful.

If arm is assigned at the WORLD level (4 worlds per arm), the honest n is 4 per
arm. Measured, permutation test, alpha 0.05, 400 trials per cell:

    analysed at WORLD, 4 per arm             80% power at d ~ 3.0
    analysed at WORLD, 8 per arm (16 worlds) 80% power at d ~ 2.4
    analysed at OBSERVATION, 16 per arm      80% power at d ~ 1.5   INVALID

The observation row is included only to name the temptation. The 4 observations
inside a world are repeats; counting them as independent is the error that
turned a nominal 5% test into a 51.7% false-discovery rate in S1, and produced a
significant difference between a player and ITSELF on the real record at p=0.036
per observation against p=0.499 per world.

CONSEQUENCE: at n=4 per arm this design detects only effects near d=3.0. Declare
the smallest effect worth believing BEFORE sizing, and keep it separate from the
effect used to size the study -- setting them equal caps power at 0.5 regardless
of budget, measured across n=32 to n=1024.

The engine already computes verified_n and flips unit_mismatch. Declare
unit_of_analysis on the analysis experiment and let it check you.

## 3. D3 LOCAL_VARIANCE_ANOMALY -- ADMIT, with one number to explain

D3 is the best-constructed of the six. Admitted as the first directed detector.

ALREADY RIGHT, and more than I expected:

  * the region is EXCLUDED from the neighbourhood it is tested against, so the
    baseline does not contain the treatment
  * fires in BOTH directions; unusually low dispersion is a reason to look, not
    evidence of "settled"
  * a degenerate zero-variance neighbourhood is skipped rather than reported as
    an infinite ratio
  * the degraded neighbourhood (family, when no coordinates) is LABELLED in the
    signal rather than silently substituted
  * eligibility is computed and reported with a blocked_reason, and calibration
    already caught an EMPTY band in D1 that no input could satisfy -- the
    reachability discipline applied without my having to ask for it

THE ONE NUMBER TO EXPLAIN. Calibration reports null fire rate 0.000, eligible on
100% of null corpora, hit 0.955, worst control 0.040. Under an i.i.d. null with
D3's exact configured parameters (region n=8, neighbourhood n>=16, band
[0.3333, 3.0]) I measure a PER-REGION false-alarm rate of 0.106, giving a
corpus-level rate of 0.36 at four eligible regions and 0.59 at eight.

    reproduce: draw region ~ N(0,1)^8 and neighbourhood ~ N(0,1)^16, form
    var(region)/var(neighbourhood), count outside [0.3333, 3.0], 20,000 draws.

0.000 against an expected 0.36+ is not evidence the detector is broken. It is
evidence the NULL CORPORA are easier than i.i.d., most plausibly because region
and neighbourhood variances are coupled by the generator. If so, the reported
false-alarm rate is optimistic and the true corpus-level rate on real data will
be higher.

REQUIRED BEFORE M-SIGNAL, not before M-ELIGIBLE: report the eligible-region
count per null corpus, and either reconcile 0.000 with the per-region rate above
or regenerate the null with region and neighbourhood independently drawn. A null
structurally easier than reality understates every downstream false-discovery
claim.

ADMITTED FOR: discrimination among regions on a frozen corpus.
NOT ADMITTED FOR: any claim that absence of firing means absence of structure.
Prohibited by epistemic_bounds.json; D3 changes nothing about it.

## 4. M-SIGNAL PREREGISTRATION SKELETON

To be committed in full, with both orders, BEFORE the corpus is unfrozen.

    ENDPOINT (primary)   detections per experiment executed that survive the
                         admission bar, at a fixed budget. Hard to game: a rate
                         over executed work, not a count.
    ENDPOINT (secondary) fraction of the exhaustive-oracle ceiling attained.
                         Report the oracle's saturation -- if eligible units
                         exceed the budget the ceiling is trivially 1.0 and the
                         fraction is the raw rate restated, not a quality
                         measure. I made that mistake in S18 and disclosed it.
    INDEPENDENT UNIT     the REGION, for D3. Declared before the run. n is the
                         count of eligible regions, never the row count.
    BUDGET               fixed experiment count, declared absolutely AND as a
                         fraction of the exhaustive universe.
    STOPPING RULE        spend the whole budget. No interim look that could
                         change the order. No early stop on a result.
    FROZEN CORPUS        content-hashed at freeze, hash committed before the
                         first detection.
    FROZEN UNIVERSE      full candidate set enumerated and hashed, so "how many
                         were looked at" is recorded before rather than
                         reconstructed after.
    BOTH ORDERS          the directed (D3-ranked) order and the matched random
                         order, BOTH committed before any outcome is revealed.
    UNIVERSE WIDENING    if the universe widens, the random control is RE-DRAWN
                         and SEPARATELY VERSIONED against the new universe.
                         A directed order on a wide universe against a control
                         drawn on a narrow one is a confound, not a comparison.
    BASELINES            random, empirical base rate, a volume/age/exposure
                         proxy, and the uncertainty proxy already in the record.
                         On S17 the uncertainty proxy reached AUC 0.755 on one
                         dimension; a detector that cannot beat it is measuring
                         exposure.
    VOID CONDITIONS      declared in advance: the null control fires above its
                         calibrated rate; fewer units delivered than declared;
                         any threshold changed after an outcome is visible.

I will write this as a hashed manifest once the corpus and universe exist. It
cannot be finalised against a corpus that does not yet exist without inventing
the eligible count, and inventing it is the failure it exists to prevent.

## BLOCKERS

I own none. Blocked on: the arm assignment LEVEL must be stated by whoever owns
the design before I can size anything. v7 is not live, so nothing downstream of
the release condition is mine to start.
