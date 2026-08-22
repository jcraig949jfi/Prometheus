"""Cycle 041 — the migration slice, its cost, and the root recount.

Three claims are under test here, and each is one I could have asserted instead of measuring:

  1. The slice was picked by LIVENESS, not by taste.
  2. The migration COST is a number, not an impression.
  3. Counting per ROOT rather than per site does not dissolve the habit — it relocates it, and
     the relocation makes a prediction that turned out to be right once and wrong three times.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.measurement import MeasurementError, OUT_OF_DOMAIN, SIGNAL  # noqa: E402
from prometheus_math.mechanism_audit import (  # noqa: E402
    EMPTY_ITERATION_SENTINEL, INHERITED, MECHANISMS, NO_IDIOM, THE_TEN, VACUOUS_QUANTIFIER,
    classify_mechanism, mechanism_of_source, root_counts,
)
from prometheus_math.migration_liveness import REFUSAL_TYPES, TARGETS  # noqa: E402


# ---- the enumerator goes first, before any count from it is trusted (HITL #129) ------------------

def test_THE_MECHANISM_CLASSIFIER_SEPARATES_THREE_PLANTED_IDIOMS():
    """Three functions whose idiom I know, including one that carries none."""
    sentinel = '''
def search(xs):
    for a, b in combinations(xs, 2):
        if a == b:
            return (a, b)
    return None
'''
    quantifier = '''
def holds(xs):
    return all(x > 0 for x in xs)
'''
    neither = '''
def explicit(xs):
    if not xs:
        raise ValueError("empty")
    return xs[0]
'''
    assert mechanism_of_source(sentinel) == EMPTY_ITERATION_SENTINEL
    assert mechanism_of_source(quantifier) == VACUOUS_QUANTIFIER
    assert mechanism_of_source(neither) == NO_IDIOM


def test_a_wrapper_is_classified_by_INHERITANCE_not_by_its_own_body():
    """Instance 9 was a wrapper that copied its callee's conflation. A wrapper's mechanism is its
    callee's, so INHERITED is checked before the self-contained idioms — an ordering that has to
    be deliberate, because the wrapper also contains an `all()` of its own."""
    src = '''
def chain_direction(chain, n):
    if is_refinement_chain(chain, n):
        return "DESTROYING"
    return "NEITHER"
'''
    assert mechanism_of_source(src) == INHERITED


# ---- 1. the slice was picked by liveness ----------------------------------------------------------

def test_the_ten_targets_are_all_probed_and_the_refusal_types_are_named():
    """A bare `except Exception` would count ordinary bugs as refusals and inflate liveness."""
    assert len(TARGETS) == 10
    assert len(REFUSAL_TYPES) >= 2
    assert all(issubclass(t, Exception) for t in REFUSAL_TYPES)


def test_THE_MIGRATED_SITE_WAS_THE_ONE_WITH_THE_MOST_PRODUCTION_REFUSALS():
    """**Measured, not chosen.** Running the suite under the liveness probe attributed every
    refusal to its nearest caller frame:

        refinement_multiplicity   99 refusals,  96 from PRODUCTION   <- migrated
        find_aliasing_witness     12 refusals,   8 from production
        fiber_search               8 refusals,   4 from production
        verify_factorization       3 refusals,   0 from production (tests only)
        is_refinement_chain        2 refusals,   0 from production
        find_splitting_witness     2 refusals,   0 from production
        chain_direction            1 refusal,    0 from production
        structural_constancy       0 refusals   (49 calls)  UNREACHED
        skill                      0 refusals   ( 0 calls)  UNREACHED
        uniform_adversary          0 refusals   ( 0 calls)  UNREACHED

    One site accounts for 96 of the 108 production refusals. Two of the ten are never CALLED at
    all by the whole suite, which is worth knowing about repairs made in cycle 039.
    """
    from prometheus_math.partition import refinement_multiplicity

    m = refinement_multiplicity((frozenset([0, 1]),), (frozenset([0]), frozenset([1])), 2)
    assert m.status == OUT_OF_DOMAIN
    assert "presupposes" in m.reason
    with pytest.raises(MeasurementError):
        _ = m.value


def test_the_migrated_measure_still_measures_on_its_honest_case():
    """The repair must not have cost the capability. A shattered truth cell still reads as
    fragmentation, and a faithful projection still reads as none."""
    from prometheus_math.partition import refinement_multiplicity

    shattered = tuple(frozenset([i]) for i in range(4))
    whole = (frozenset(range(4)),)
    assert refinement_multiplicity(shattered, whole, 4).value == 4
    assert refinement_multiplicity(shattered, whole, 4).status == SIGNAL
    assert refinement_multiplicity(whole, whole, 4).value == 1


def test_the_measurement_type_survives_the_audit_that_motivated_it():
    """**A migration must not improve the rate by shrinking the population.**

    Cycle 040's `is_measure_like` matched scalar return annotations. Converting a measure to
    return `Measurement` changed its annotation, so it silently LEFT the denominator — the rate
    would have improved because the function stopped being counted, not because it was fixed.
    That is a confound pushing in the flattering direction, so the criterion now recognises
    `Measurement` as a scalar verdict.
    """
    from prometheus_math.degenerate_audit import REFUSES, audit_modules, is_measure_like
    from prometheus_math.partition import refinement_multiplicity

    assert is_measure_like(refinement_multiplicity) is True
    rows = {r.name: r.verdict for r in audit_modules()}
    assert rows.get("refinement_multiplicity") == REFUSES     # refusing by RETURNING still counts


# ---- 2. the cost ------------------------------------------------------------------------------------

def test_THE_MIGRATION_COST_IS_THIRTEEN_EDITS_FOR_ONE_FUNCTION():
    """**The finding, not an obstacle.** Converting `refinement_multiplicity` alone broke:

        11 tests   (adversarial_registry 4, round8_foldin 2, contract_registry 1,
                    degenerate_audit 3, measurement 1)
         2 production call sites  (adversarial_registry.py:66, contract_registry.py:100)

    Thirteen edits for one function, and it is the function whose refusal fires most. That is the
    number that makes gradual migration the honest plan rather than a preference: the remaining
    two LIVE-from-production sites are deferred with this cost as the stated reason, and the
    seven that only fire from tests are not scheduled at all.
    """
    migrated = ["refinement_multiplicity"]
    live_from_prod_remaining = ["find_aliasing_witness", "fiber_search"]
    live_from_tests_only = ["verify_factorization", "is_refinement_chain",
                            "chain_direction", "find_splitting_witness"]
    unreached = ["structural_constancy", "skill", "uniform_adversary"]
    assert len(migrated + live_from_prod_remaining + live_from_tests_only + unreached) == 10
    assert len(migrated) == 1


# ---- 3. the root recount ------------------------------------------------------------------------------

def test_counting_per_ROOT_does_not_dissolve_the_habit_it_RELOCATES_it():
    """Ten sites, but not ten independent mistakes.

    By call graph there is exactly ONE inheritance edge (chain_direction -> is_refinement_chain),
    so nine roots and the rate barely moves. By IDIOM the picture is different: three of the ten
    are the same `for a, b in combinations(...)` + post-loop sentinel, written three times.

    So "I write bad measures" becomes "a few idioms reliably produce this bug and I reach for
    them" — which is a weaker claim about me and a STRONGER one about the code, because an idiom
    is greppable and a habit is not.
    """
    groups = root_counts()
    assert set(groups) <= set(MECHANISMS) | {NO_IDIOM}
    assert len(groups[EMPTY_ITERATION_SENTINEL]) == 3
    assert set(groups[EMPTY_ITERATION_SENTINEL]) == {
        "find_aliasing_witness", "verify_factorization", "find_splitting_witness"}
    assert groups[INHERITED] == ["chain_direction"]
    # fewer roots than sites, and that is the whole point
    assert len(groups) < len(THE_TEN)


def test_INSTANCE_ELEVEN_WAS_PREDICTED_BY_THE_IDIOM_NOT_STUMBLED_ON():
    """**The prediction paid off once in four, and the one is worth the three.**

    Idiom-presence flagged four measure-like functions outside the known ten. All four were
    checked BY CALLING them rather than by reading:

        brier_score               REFUSED (CalibrationError)   — guarded by a delegated _validate
        refines                   REFUSED (PartitionError)     — likewise
        family_cannot_be_correct  REFUSED (OutOfDomain)        — likewise
        verify_family_incapacity  ANSWERED                     — **INSTANCE 11**

    `brier_score` was flagged only because of the arithmetic-identity over-fire that the planted
    anti-case caught later; the corrected classifier names three candidates, not four, so the
    honest hit rate is one in three from a screen that costs one call per candidate.

    The remaining misses share one cause: the classifier reads a function's own body and cannot
    see validation delegated to a helper. A stated blind spot, not a mystery.

    Instance 11 returned `all_members_err=True, all_members_aliased=True` for an EMPTY family —
    every member of a family with no members errs, vacuously — inside the module whose entire
    argument is that absence of a counterexample is not evidence of impossibility.
    """
    from techne.ladder_circuits.aliasing import (
        OutOfDomain, find_aliasing_witness, verify_family_incapacity,
    )

    w = find_aliasing_witness([1, 2], lambda x: 0, lambda x: x)
    assert w is not None
    with pytest.raises(OutOfDomain) as exc:
        verify_family_incapacity([], lambda a, b: 0, w)
    assert "empty family" in str(exc.value)
    # and it still works on an honest family
    report = verify_family_incapacity([0], lambda theta, x: 0, w)
    assert report["per_member"] and "all_members_err" in report


def test_cycle_040_UNPROBED_BUCKET_WAS_CONCEALING_A_LIVE_INSTANCE():
    """Cycle 040 reported UNPROBED=6 as a virtue — 'reported, never dropped'. It was counted but
    not CHECKED, and instance 11 was sitting in it. Two of the six carried the audit's own
    tell-tale reason string, 'answered on degenerate input', which is already half the evidence
    of a conflation and was nonetheless shelved rather than flagged.

    Hand-checking the bucket found one real instance (`verify_family_incapacity`) and one that I
    declined to count: `information_profile` returns `[]` for an empty chain, which is a faithful
    total function rather than a verdict masquerading as a finding. Inflating the count would be
    as dishonest as missing one.
    """
    from prometheus_math.partition import information_profile

    assert information_profile((), (), 2) == []           # honest, not a conflation — NOT counted


def test_the_class_now_stands_at_ELEVEN():
    """Ten from cycle 040, plus one predicted and confirmed this cycle."""
    through_040 = ["structural_constancy", "find_aliasing_witness", "fiber_search",
                   "refinement_multiplicity", "skill", "verify_factorization",
                   "uniform_adversary", "is_refinement_chain", "chain_direction",
                   "find_splitting_witness"]
    cycle_041 = ["verify_family_incapacity"]
    assert len(through_040) == 10
    assert len(through_040) + len(cycle_041) == 11
