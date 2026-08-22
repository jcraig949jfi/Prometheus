"""Mirkin metric — cycle 046, Track 1 (the 20% slice).

Reference: Mirkin, B. G. (1996). "Mathematical Classification and Clustering." Kluwer, ch. 5;
originally Mirkin & Chernyi (1970). The unnormalised pair-counting metric

    M(X, Y) = sum_i a_i^2 + sum_j b_j^2 - 2 * sum_ij n_ij^2

Tests written before the implementation, all four categories, per the math-tdd skill.

This is the METRIC of the pair-counting family, and the reason to have it next to `rand_index`:
RI is a similarity in [0,1] with no triangle inequality, M is an unbounded true distance. The
relation `M = 2 * C(n,2) * (1 - RI)` ties them, and is asserted rather than assumed.
"""
from __future__ import annotations

import pathlib
import sys
from math import comb

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.partition import PartitionError, induced_partition  # noqa: E402
from prometheus_math.mirkin_metric import MIRKIN_1996, mirkin_distance  # noqa: E402


def _from_labels(labels):
    labels = list(labels)
    return induced_partition(range(len(labels)), lambda i: labels[i])


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_identical_partitions_are_at_distance_zero():
    """M(X, X) = 0: no pair disagrees."""
    p = _from_labels([0, 0, 1, 1, 2, 2])
    assert mirkin_distance(p, p, 6) == pytest.approx(0.0, abs=1e-12)


def test_authority_worked_example_by_hand():
    """Hand-computed, n = 6. X = {0,1,2}{3,4,5}, Y = {0,1}{2,3}{4,5}.

        sum a_i^2 = 3^2 + 3^2 = 18
        sum b_j^2 = 2^2 * 3   = 12
        sum n_ij^2 over the contingency table (2,1,0 / 0,1,2) = 4+1+0+0+1+4 = 10
        M = 18 + 12 - 2*10 = 10
    """
    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    assert mirkin_distance(x, y, 6) == pytest.approx(10.0, abs=1e-12)


def test_authority_lattice_extremes_attain_the_maximum():
    """All-singletons vs one-block, n = 4: sum a^2 = 4, sum b^2 = 16, sum n_ij^2 = 4,
    so M = 4 + 16 - 8 = 12 = 2 * C(4,2) — every pair disagrees, which is the maximum."""
    singles = tuple(frozenset([i]) for i in range(4))
    whole = (frozenset(range(4)),)
    assert mirkin_distance(singles, whole, 4) == pytest.approx(12.0, abs=1e-12)
    assert mirkin_distance(singles, whole, 4) == pytest.approx(2 * comb(4, 2), abs=1e-12)


def test_authority_citation_is_recorded():
    assert "Mirkin" in MIRKIN_1996


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_labels = st.lists(st.integers(0, 3), min_size=3, max_size=8)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_non_negative_and_bounded(a, b):
    """0 <= M <= 2*C(n,2): it counts each disagreeing pair twice."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    assert -1e-9 <= mirkin_distance(p, t, n) <= 2 * comb(n, 2) + 1e-9


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_symmetry(a, b):
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    assert mirkin_distance(p, t, n) == pytest.approx(mirkin_distance(t, p, n), abs=1e-9)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_zero_exactly_on_identity(a, b):
    """Identity of indiscernibles: M = 0 iff the partitions are equal."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if p == t:
        assert mirkin_distance(p, t, n) == pytest.approx(0.0, abs=1e-9)
    else:
        assert mirkin_distance(p, t, n) > 1e-9


@settings(max_examples=120, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels, _labels)
def test_property_TRIANGLE_INEQUALITY_which_rand_index_does_not_have(a, b, c):
    """**The property that makes this a metric and `rand_index` not one.**

    M satisfies M(p,r) <= M(p,q) + M(q,r). RI is a similarity with no such guarantee, so code that
    treats `1 - RI` as a distance can violate the triangle inequality without warning.
    """
    n = min(len(a), len(b), len(c))
    if n < 3:
        return
    p, q, r = (_from_labels(x[:n]) for x in (a, b, c))
    assert (mirkin_distance(p, r, n)
            <= mirkin_distance(p, q, n) + mirkin_distance(q, r, n) + 1e-9)


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

def test_edge_cases():
    """Edges covered, enumerated:

    - n = 0: REFUSES. No ground set, so "distance 0" would report agreement over nothing.
    - n = 1: DEFINED and equal to 0 — there are no pairs, so nothing can disagree, and unlike the
      normalised indices there is no denominator to vanish. A genuine value, not a 0/0.
    - malformed partitions: REFUSES.
    - maximum attained exactly at the lattice extremes.
    """
    with pytest.raises(PartitionError):
        mirkin_distance((), (), 0)
    single = (frozenset([0]),)
    assert mirkin_distance(single, single, 1) == pytest.approx(0.0, abs=1e-12)
    with pytest.raises(PartitionError):
        mirkin_distance((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3)


def test_edge_n_equals_one_is_DEFINED_here_unlike_the_normalised_indices():
    """**Same input, four indices, three refusals and one honest zero.**

    At n = 1, `normalized_vi` refuses (log2(1) = 0), `adjusted_rand` refuses (C(1,2) = 0) and
    `fowlkes_mallows` refuses (no co-clustered pairs). Mirkin is a raw count with no denominator,
    so it is simply 0. Pinning all four on one input stops a caller assuming the family shares a
    domain — the third time this loop has had to record that they do not.
    """
    from prometheus_math.adjusted_rand import adjusted_rand
    from prometheus_math.fowlkes_mallows import fowlkes_mallows
    from prometheus_math.normalized_vi import normalized_vi

    single = (frozenset([0]),)
    assert mirkin_distance(single, single, 1) == 0.0
    for fn in (normalized_vi, adjusted_rand, fowlkes_mallows):
        with pytest.raises(PartitionError):
            fn(single, single, 1)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_mirkin_is_rand_index_rescaled():
    """M = 2 * C(n,2) * (1 - RI). Chains against cycle 045's `rand_index`; a normalisation error
    in either shows up as a mismatch here."""
    from prometheus_math.rand_index import rand_index

    for la, lb, n in (([0, 0, 0, 1, 1, 1], [0, 0, 1, 1, 2, 2], 6),
                      ([0, 1, 2, 3], [0, 0, 1, 1], 4),
                      ([0, 0, 1, 1, 2], [0, 1, 1, 2, 2], 5)):
        p, t = _from_labels(la), _from_labels(lb)
        assert mirkin_distance(p, t, n) == pytest.approx(
            2 * comb(n, 2) * (1 - rand_index(p, t, n)), abs=1e-9)


def test_composition_zero_iff_vi_zero():
    """M = 0 exactly when VI = 0 — a pair-counting metric and an information-theoretic one must
    agree on the identity endpoint."""
    from prometheus_math.partition import variation_of_information

    p = _from_labels([0, 0, 1, 1, 2, 2])
    q = _from_labels([0, 0, 0, 1, 1, 1])
    assert mirkin_distance(p, p, 6) == pytest.approx(0.0, abs=1e-12)
    assert variation_of_information(p, p, 6) == pytest.approx(0.0, abs=1e-12)
    assert mirkin_distance(p, q, 6) > 1e-9
    assert variation_of_information(p, q, 6) > 1e-9


def test_composition_ranks_a_near_projection_above_a_far_one():
    """A distance must ORDER candidates the opposite way to the similarities. Chains against
    `rand_index` and `adjusted_rand` on the same three partitions."""
    from prometheus_math.adjusted_rand import adjusted_rand
    from prometheus_math.rand_index import rand_index

    n = 6
    truth = _from_labels([0, 0, 0, 1, 1, 1])
    near = _from_labels([0, 0, 0, 1, 1, 2])
    far = _from_labels([0, 1, 0, 1, 0, 1])
    assert mirkin_distance(near, truth, n) < mirkin_distance(far, truth, n)
    assert rand_index(near, truth, n) > rand_index(far, truth, n)
    assert adjusted_rand(near, truth, n) > adjusted_rand(far, truth, n)
