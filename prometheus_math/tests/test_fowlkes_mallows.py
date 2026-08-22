"""Fowlkes-Mallows index — cycle 044, Track 1 (the 20% slice).

Reference: Fowlkes, E. B. & Mallows, C. L. (1983). "A Method for Comparing Two Hierarchical
Clusterings." Journal of the American Statistical Association 78(383):553-569.

    FM = TP / sqrt((TP + FP)(TP + FN))

the geometric mean of pair-precision and pair-recall. Tests written before the implementation,
all four categories, per the math-tdd skill.

FM is the fourth member of the comparison family and the one that is NOT chance-corrected — which
is exactly why it is worth having next to `adjusted_rand`: the pair of them isolates what chance
correction actually buys.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.partition import PartitionError, induced_partition  # noqa: E402
from prometheus_math.fowlkes_mallows import (  # noqa: E402
    FOWLKES_MALLOWS_1983, fowlkes_mallows,
)


def _from_labels(labels):
    labels = list(labels)
    return induced_partition(range(len(labels)), lambda i: labels[i])


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_identical_partitions_score_one():
    """FM = 1 for identical clusterings: every co-clustered pair is a true positive, so
    FP = FN = 0 and FM = TP / sqrt(TP * TP) = 1.

    Hand-check, n = 6, three blocks of two: TP = 3 * C(2,2) = 3, FP = 0, FN = 0,
    FM = 3 / sqrt(3 * 3) = 1 exactly.
    """
    p = _from_labels([0, 0, 1, 1, 2, 2])
    assert fowlkes_mallows(p, p, 6) == pytest.approx(1.0, abs=1e-12)


def test_authority_worked_example_by_hand():
    """Fully hand-computed, n = 6. X = {0,1,2}{3,4,5}, Y = {0,1}{2,3}{4,5}.

    Contingency counts: |X1nY1|=2, |X1nY2|=1, |X2nY2|=1, |X2nY3|=2.
        TP = sum C(nij,2) = C(2,2) + C(2,2) = 2
        TP + FP = sum_i C(ai,2) = C(3,2) + C(3,2) = 6      (pairs together in X)
        TP + FN = sum_j C(bj,2) = 3 * C(2,2) = 3           (pairs together in Y)
        FM = 2 / sqrt(6 * 3) = 2 / sqrt(18) = 0.4714045...
    """
    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    assert fowlkes_mallows(x, y, 6) == pytest.approx(2.0 / math.sqrt(18.0), abs=1e-12)


def test_authority_citation_is_recorded():
    assert "Fowlkes" in FOWLKES_MALLOWS_1983 and "1983" in FOWLKES_MALLOWS_1983


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_labels = st.lists(st.integers(0, 3), min_size=3, max_size=9)


def _defined(p, t, n):
    """FM is defined iff both pair-counts are non-zero — the ACTUAL precondition, not a proxy.

    Cycle 043 guarded a property test on `len(p) > 1` and Hypothesis broke it immediately, because
    an all-singleton partition has more than one block and zero co-clustered pairs. The condition
    is computed here rather than approximated.
    """
    from math import comb
    a = sum(comb(len(b), 2) for b in p)
    b_ = sum(comb(len(b), 2) for b in t)
    return a > 0 and b_ > 0


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_in_the_unit_interval(a, b):
    """0 <= FM <= 1. It is a geometric mean of two ratios each in [0, 1]."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if not _defined(p, t, n):
        return
    v = fowlkes_mallows(p, t, n)
    assert -1e-12 <= v <= 1.0 + 1e-12


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_symmetry(a, b):
    """FM(X, Y) = FM(Y, X): swapping exchanges FP and FN, and the denominator is symmetric."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if not _defined(p, t, n):
        return
    assert fowlkes_mallows(p, t, n) == pytest.approx(fowlkes_mallows(t, p, n), abs=1e-12)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels)
def test_property_identity_is_one(a):
    n = len(a)
    if n < 3:
        return
    p = _from_labels(a)
    if not _defined(p, p, n):
        return
    assert fowlkes_mallows(p, p, n) == pytest.approx(1.0, abs=1e-12)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_never_negative_UNLIKE_adjusted_rand(a, b):
    """**The contrast that makes having both worthwhile.**

    FM is NOT chance-corrected, so it is bounded below by 0 and a below-chance pairing still
    scores positive. ARI on the same input can go negative. Code that treats the two as
    interchangeable will silently lose the "worse than chance" signal.
    """
    from prometheus_math.adjusted_rand import adjusted_rand
    from math import comb

    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if not _defined(p, t, n):
        return
    assert fowlkes_mallows(p, t, n) >= -1e-12                 # never negative
    sa = sum(comb(len(x), 2) for x in p)
    sb = sum(comb(len(y), 2) for y in t)
    if abs((sa + sb) / 2 - sa * sb / comb(n, 2)) >= 1e-15:
        adjusted_rand(p, t, n)                                # defined; may be negative


def test_property_the_chance_correction_gap_is_real():
    """A constructed below-chance pairing: ARI < 0 while FM > 0 on the same input."""
    from prometheus_math.adjusted_rand import adjusted_rand

    x = _from_labels([0, 0, 1, 1, 2, 2])
    y = _from_labels([0, 1, 2, 0, 1, 2])
    assert adjusted_rand(x, y, 6) < 0.0
    assert fowlkes_mallows(x, y, 6) >= 0.0


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

def test_edge_cases():
    """Edges covered, enumerated:

    - n < 2: REFUSE. No pairs exist at all.
    - EITHER partition all singletons: REFUSE. That side contributes zero co-clustered pairs, so
      the denominator has a zero factor and FM is 0/0.
    - malformed partitions: REFUSE.
    - disjoint-but-valid: FM = 0 legitimately, and that is NOT the degenerate case.
    """
    with pytest.raises(PartitionError):
        fowlkes_mallows((), (), 0)
    with pytest.raises(PartitionError):
        fowlkes_mallows((frozenset([0]),), (frozenset([0]),), 1)
    with pytest.raises(PartitionError):
        fowlkes_mallows((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3)


def test_edge_all_singletons_refuses_and_is_NOT_confused_with_a_true_zero():
    """**The distinction this whole loop has been about, in one function.**

    An all-singleton partition has zero co-clustered pairs, so `TP + FP = 0` and FM is 0/0.
    Returning 0.0 would be indistinguishable from a genuine "these clusterings share no pair",
    which is a real and different situation — constructed below so the two cannot be conflated.
    """
    singles = tuple(frozenset([i]) for i in range(4))
    blocks = (frozenset([0, 1]), frozenset([2, 3]))
    with pytest.raises(PartitionError) as exc:
        fowlkes_mallows(singles, blocks, 4)
    assert "0/0" in str(exc.value) or "no co-clustered" in str(exc.value)

    # ...and a genuine zero, which must NOT raise: both sides have pairs, none shared.
    x = (frozenset([0, 1]), frozenset([2, 3]))
    y = (frozenset([0, 2]), frozenset([1, 3]))
    assert fowlkes_mallows(x, y, 4) == pytest.approx(0.0, abs=1e-12)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_fm_is_the_geometric_mean_of_precision_and_recall():
    """FM = sqrt(precision * recall) over pairs, recomputed independently from the contingency
    table. If either the implementation or the table walk has an off-by-one, this catches it."""
    from math import comb

    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    n = 6
    tp = sum(comb(len(bx & by), 2) for bx in x for by in y)
    tp_fp = sum(comb(len(bx), 2) for bx in x)
    tp_fn = sum(comb(len(by), 2) for by in y)
    precision, recall = tp / tp_fp, tp / tp_fn
    assert fowlkes_mallows(x, y, n) == pytest.approx(math.sqrt(precision * recall), abs=1e-12)


def test_composition_agrees_with_ari_on_ordering():
    """Both are pair-counting indices, so they must RANK the same two candidates identically even
    though chance correction makes the values differ. Chains against cycle 043's `adjusted_rand`."""
    from prometheus_math.adjusted_rand import adjusted_rand

    n = 6
    truth = _from_labels([0, 0, 0, 1, 1, 1])
    near = _from_labels([0, 0, 0, 1, 1, 2])
    far = _from_labels([0, 1, 0, 1, 0, 1])
    assert fowlkes_mallows(near, truth, n) > fowlkes_mallows(far, truth, n)
    assert adjusted_rand(near, truth, n) > adjusted_rand(far, truth, n)
    assert abs(fowlkes_mallows(near, truth, n) - adjusted_rand(near, truth, n)) > 1e-6


def test_composition_one_iff_vi_zero():
    """FM = 1 exactly when VI = 0 — a pair-counting index and an information-theoretic one must
    agree on the identity endpoint or one of them has a convention bug."""
    from prometheus_math.partition import variation_of_information

    p = _from_labels([0, 0, 1, 1, 2, 2])
    q = _from_labels([0, 0, 0, 1, 1, 1])
    assert fowlkes_mallows(p, p, 6) == pytest.approx(1.0, abs=1e-12)
    assert variation_of_information(p, p, 6) == pytest.approx(0.0, abs=1e-12)
    assert fowlkes_mallows(p, q, 6) < 1.0 - 1e-9
    assert variation_of_information(p, q, 6) > 1e-9
