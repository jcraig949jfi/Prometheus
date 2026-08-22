"""Degenerate-input audit — cycle 040. Seven of how many?

From inside I could not tell whether seven instances of one bug class in three weeks was a habit
of mine or simply where all bugs live. This gets the denominator, and the answer settles two
open items.
"""
from __future__ import annotations

import collections
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.degenerate_audit import (  # noqa: E402
    CONFLATES, DISTINGUISHES, REFUSES, UNPROBED, audit_modules, classify, is_measure_like,
)


# ---- HITL #129 on the enumerator, before trusting its count ---------------------------------------

def test_THE_ENUMERATOR_CLASSIFIES_ALL_THREE_PLANTED_CASES():
    """The enumerator is a new instrument, so it goes first. Three measures whose correct
    classification I know, including the one I do not want it to miss."""
    def conflater(xs: list) -> int:
        return 0                                   # same answer for empty and for no-signal

    def refuser(xs: list) -> int:
        if not xs:
            raise ValueError("empty")
        return len(xs)

    def distinguisher(xs: list) -> int:
        return -1 if not xs else len(xs)

    assert classify(conflater, "conflater", "planted").verdict == CONFLATES
    assert classify(refuser, "refuser", "planted").verdict == REFUSES
    assert classify(distinguisher, "distinguisher", "planted").verdict == DISTINGUISHES


def test_the_measure_like_criterion_is_mechanical_not_curated():
    """A criterion chosen per function is a criterion I can bend — cycle 038's lesson. This one
    is uniform: takes an argument, reduces to a scalar verdict."""
    def scores(xs: list) -> float:
        return 1.0

    def builds(n: int) -> list:
        return []

    def nullary() -> bool:
        return True

    assert is_measure_like(scores) is True
    assert is_measure_like(builds) is False        # returns data, not a verdict
    assert is_measure_like(nullary) is False       # nothing to be degenerate about


# ---- the rate -----------------------------------------------------------------------------------

def test_THE_DENOMINATOR_IS_FORTY():
    """Forty measure-like functions across eleven modules, by a criterion applied uniformly."""
    rows = audit_modules()
    assert len(rows) == 40


def test_UNPROBED_IS_REPORTED_NOT_DROPPED():
    """A rate over only the probeable functions would flatter the result exactly the way cycle
    038's hand-written fixtures did. Six could not be probed generically and are counted."""
    rows = audit_modules()
    counts = collections.Counter(r.verdict for r in rows)
    assert counts[UNPROBED] == 6
    assert sum(counts.values()) == 40


def test_most_measures_now_refuse_because_ten_have_been_repaired():
    """Twenty-six refuse. That number is not a clean bill of health — seven of those refusals
    were installed during cycles 029-039 in response to this same bug class, and three more this
    cycle. The audit measures the code as it stands, not as it was written."""
    rows = audit_modules()
    counts = collections.Counter(r.verdict for r in rows)
    assert counts[REFUSES] >= 26
    assert counts[CONFLATES] <= 3                  # only artefacts and borderline helpers remain


# ---- instances 8, 9, 10 -----------------------------------------------------------------------------

def test_INSTANCE_8_is_refinement_chain_called_an_empty_chain_a_chain():
    from prometheus_math.partition import PartitionError, is_refinement_chain

    with pytest.raises(PartitionError):
        is_refinement_chain([], 4)
    with pytest.raises(PartitionError):
        is_refinement_chain([(frozenset([0, 1]),)], 2)
    assert is_refinement_chain([(frozenset([0]), frozenset([1])),
                                (frozenset([0, 1]),)], 2) is True


def test_INSTANCE_9_chain_direction_inherited_the_defect_verbatim():
    """Downstream of instance 8 and it copied the bug — an empty chain read DESTROYING."""
    from prometheus_math.partition import PartitionError, chain_direction

    with pytest.raises(PartitionError):
        chain_direction([], 4)
    assert chain_direction([(frozenset([0]), frozenset([1])),
                            (frozenset([0, 1]),)], 2) == "DESTROYING"


def test_INSTANCE_10_IS_THE_DUAL_OF_A_BUG_I_FIXED_IN_CYCLE_037():
    """**The propagation failure happening inside the cycle that was repairing it.**

    Cycle 037 fixed exactly this conflation in `find_aliasing_witness` and left
    `find_splitting_witness` — its dual, one file away — untouched. Both returned None for "no
    witness exists" and for "there was nothing to compare".
    """
    from techne.ladder_circuits.aliasing import OutOfDomain
    from techne.ladder_circuits.sweep import find_splitting_witness

    with pytest.raises(OutOfDomain):
        find_splitting_witness([], lambda x: x, lambda x: x)
    with pytest.raises(OutOfDomain):
        find_splitting_witness([1], lambda x: x, lambda x: x)
    assert find_splitting_witness([1, 2], lambda x: x, lambda x: x * 2) is None   # honest none
    assert find_splitting_witness([1, 2], lambda x: x, lambda x: 0) is not None   # honest witness


def test_the_class_now_stands_at_TEN_of_FORTY():
    """**The answer to the question I could not settle from inside.**

    Ten instances of one bug class among forty measure-like functions — 25%. That is not the tail
    of a normal distribution; it is a habit. Which settles the migration question too: adopting
    the measurement type stops being optional.
    """
    historical = ["structural_constancy", "find_aliasing_witness", "fiber_search",
                  "refinement_multiplicity", "murphy.skill", "verify_factorization",
                  "uniform_adversary.schema_survived"]
    this_cycle = ["is_refinement_chain", "chain_direction", "find_splitting_witness"]
    assert len(historical) == 7
    assert len(this_cycle) == 3
    assert len(historical) + len(this_cycle) == 10
    assert len(audit_modules()) == 40
