"""Adjusted Rand index — cycle 043, Track 1 (the 20% slice).

Reference: Hubert, L. & Arabie, P. (1985). "Comparing partitions." Journal of Classification
2(1):193-218. The chance-corrected form of Rand (1971):

    ARI = (RI - E[RI]) / (max RI - E[RI])

Tests written before the implementation, all four categories, per the math-tdd skill.

ARI completes a trio with cycle 041's normalized VI (a metric) and cycle 042's NMI (an
information-theoretic similarity). ARI is a PAIR-COUNTING similarity, corrected for chance, and it
can go NEGATIVE — which none of the other two can. That is the property worth having and the one
most likely to be assumed away.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.partition import (  # noqa: E402
    PartitionError, induced_partition, variation_of_information,
)
from prometheus_math.adjusted_rand import HUBERT_ARABIE_1985, adjusted_rand  # noqa: E402


def _from_labels(labels):
    labels = list(labels)
    return induced_partition(range(len(labels)), lambda i: labels[i])


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_identical_partitions_score_exactly_one():
    """Hubert & Arabie (1985): ARI = 1 for identical partitions.

    Hand-computation, n = 6, three blocks of two. Each block contributes C(2,2) = 1 agreeing
    pair, so index = 3. Both marginals are the same, so expected = 3 * 3 / C(6,2) = 9/15 = 0.6
    and max = (3 + 3)/2 = 3. ARI = (3 - 0.6) / (3 - 0.6) = 1 exactly.
    """
    p = _from_labels([0, 0, 1, 1, 2, 2])
    assert adjusted_rand(p, p, 6) == pytest.approx(1.0, abs=1e-12)


def test_authority_worked_example_by_hand():
    """A fully hand-computed non-trivial case, n = 6.

    X = {0,1,2}{3,4,5}, Y = {0,1}{2,3}{4,5}. Contingency table counts:
        |X1 n Y1| = 2, |X1 n Y2| = 1, |X1 n Y3| = 0
        |X2 n Y1| = 0, |X2 n Y2| = 1, |X2 n Y3| = 2
    index      = sum C(nij,2) = C(2,2) + C(2,2) = 1 + 1 = 2
    sum_a      = C(3,2) + C(3,2) = 3 + 3 = 6
    sum_b      = C(2,2) * 3 = 3
    expected   = 6 * 3 / C(6,2) = 18 / 15 = 1.2
    max        = (6 + 3) / 2 = 4.5
    ARI        = (2 - 1.2) / (4.5 - 1.2) = 0.8 / 3.3 = 0.242424...
    """
    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    assert adjusted_rand(x, y, 6) == pytest.approx(0.8 / 3.3, abs=1e-12)


def test_authority_citation_is_recorded():
    assert "Hubert" in HUBERT_ARABIE_1985 and "1985" in HUBERT_ARABIE_1985


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_labels = st.lists(st.integers(0, 3), min_size=3, max_size=9)


def _nondegenerate(p, t, n):
    """ARI is defined iff its correction denominator `max - expected` is non-zero.

    **Guard on the actual condition, not a proxy.** The first version of this helper tested
    `len(p) > 1 and len(t) > 1`, which passes for two all-singleton partitions — and those are
    degenerate, because every pair disagrees by construction and max == expected. Hypothesis found
    it immediately with `a=[0,1,2]`. The implementation was correct to refuse; the guard was
    measuring the wrong thing.
    """
    from math import comb
    sum_a = sum(comb(len(bx), 2) for bx in p)
    sum_b = sum(comb(len(by), 2) for by in t)
    expected = sum_a * sum_b / comb(n, 2)
    return abs((sum_a + sum_b) / 2 - expected) >= 1e-15


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_bounded_above_by_one(a, b):
    """ARI <= 1 always, with equality only at identity."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if not _nondegenerate(p, t, n):
        return
    assert adjusted_rand(p, t, n) <= 1.0 + 1e-12


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_symmetry(a, b):
    """ARI(X, Y) = ARI(Y, X). Both the index and its correction are symmetric."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if not _nondegenerate(p, t, n):
        return
    assert adjusted_rand(p, t, n) == pytest.approx(adjusted_rand(t, p, n), abs=1e-12)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels)
def test_property_identity_is_exactly_one(a):
    n = len(a)
    if n < 3:
        return
    p = _from_labels(a)
    if not _nondegenerate(p, p, n):
        return
    assert adjusted_rand(p, p, n) == pytest.approx(1.0, abs=1e-12)


def test_property_CAN_GO_NEGATIVE_and_that_is_the_point():
    """**Chance correction means ARI is NOT bounded below by zero.**

    A pairing that agrees LESS than chance scores negative. Every naive "similarity in [0,1]"
    assumption breaks here, and code that clamps to zero silently destroys the distinction
    between "no better than chance" and "actively anti-correlated". Constructed rather than
    searched for, so the test cannot quietly stop exercising the case.
    """
    x = _from_labels([0, 0, 1, 1, 2, 2])
    y = _from_labels([0, 1, 2, 0, 1, 2])
    v = adjusted_rand(x, y, 6)
    assert v < 0.0, f"expected a below-chance pairing to score negative, got {v}"


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

def test_edge_cases():
    """Edges covered, enumerated:

    - n = 0 and n = 1: REFUSE. There are no pairs to count; C(n,2) = 0.
    - BOTH partitions trivial in the same way (both one block, or both all singletons): REFUSE.
      max == expected exactly, so ARI is 0/0.
    - malformed partitions (not covering / overlapping): REFUSE.
    - the negative case: permitted, not clamped.
    """
    with pytest.raises(PartitionError):
        adjusted_rand((), (), 0)
    with pytest.raises(PartitionError):
        adjusted_rand((frozenset([0]),), (frozenset([0]),), 1)
    with pytest.raises(PartitionError):
        adjusted_rand((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3)


def test_edge_the_degenerate_denominator_refuses_rather_than_returning_zero_over_zero():
    """**The 0/0 that this family of indices is notorious for.**

    When both partitions are the single block, every pair agrees trivially: index == expected ==
    max, so the ratio is 0/0. The same happens when both are all singletons. Returning 0.0 would
    say "no better than chance" and 1.0 would say "identical" — and the two partitions ARE
    identical, which makes 1.0 the more seductive wrong answer. It is still wrong, because it is
    produced by division by zero rather than by measuring agreement.

    The refusal names the situation so a caller can pick a different index.
    """
    whole = (frozenset(range(4)),)
    singles = tuple(frozenset([i]) for i in range(4))
    for p, t in ((whole, whole), (singles, singles)):
        with pytest.raises(PartitionError) as exc:
            adjusted_rand(p, t, 4)
        assert "0/0" in str(exc.value) or "degenerate" in str(exc.value).lower()


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_ari_one_iff_vi_zero():
    """ARI = 1 exactly when VI = 0. Two independently built comparison tools — pair-counting and
    information-theoretic — must agree on the identity endpoint."""
    p = _from_labels([0, 0, 1, 1, 2, 2])
    q = _from_labels([0, 1, 2, 3, 4, 5])
    assert adjusted_rand(p, p, 6) == pytest.approx(1.0, abs=1e-12)
    assert variation_of_information(p, p, 6) == pytest.approx(0.0, abs=1e-12)
    assert adjusted_rand(p, q, 6) < 1.0 - 1e-9
    assert variation_of_information(p, q, 6) > 1e-9


def test_composition_agrees_with_nmi_on_ordering_but_not_on_value():
    """**Two indices, same ranking, different numbers — tested so neither is substituted for the
    other.**

    Chains `adjusted_rand` against cycle 042's `normalized_mi`. Both should rank a near-correct
    projection above a badly wrong one, and both should be < 1 for either; but the VALUES must
    not be assumed equal, because one counts pairs and the other counts bits.
    """
    from prometheus_math.normalized_mi import normalized_mi

    n = 6
    truth = _from_labels([0, 0, 0, 1, 1, 1])
    near = _from_labels([0, 0, 0, 1, 1, 2])
    far = _from_labels([0, 1, 0, 1, 0, 1])
    ari_near, ari_far = adjusted_rand(near, truth, n), adjusted_rand(far, truth, n)
    nmi_near, nmi_far = normalized_mi(near, truth, n), normalized_mi(far, truth, n)
    assert ari_near > ari_far                       # same ordering...
    assert nmi_near > nmi_far
    assert abs(ari_near - nmi_near) > 1e-6          # ...different values


def test_composition_pair_counts_reconcile_with_the_contingency_table():
    """The index term recomputed independently from the contingency table must match what the
    implementation used. Chains `adjusted_rand` against `induced_partition`'s block structure —
    if either has an off-by-one in pair counting, this is where it shows.
    """
    from math import comb

    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    n = 6
    index = sum(comb(len(bx & by), 2) for bx in x for by in y)
    sum_a = sum(comb(len(bx), 2) for bx in x)
    sum_b = sum(comb(len(by), 2) for by in y)
    expected = sum_a * sum_b / comb(n, 2)
    maximum = (sum_a + sum_b) / 2
    assert adjusted_rand(x, y, n) == pytest.approx(
        (index - expected) / (maximum - expected), abs=1e-12)
