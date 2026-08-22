"""Rand index — cycle 045, Track 1 (the 20% slice).

Reference: Rand, W. M. (1971). "Objective Criteria for the Evaluation of Clustering Methods."
Journal of the American Statistical Association 66(336):846-850.

    RI = (a + d) / C(n, 2)

where `a` = pairs together in both partitions and `d` = pairs separated in both. Tests written
before the implementation, all four categories, per the math-tdd skill.

This is the uncorrected ancestor of cycle 043's `adjusted_rand`, and having both is what makes the
chance correction legible: Hubert & Arabie's whole point was that RI is inflated and does not
approach 0 for independent clusterings. Tested here directly rather than taken on faith.
"""
from __future__ import annotations

import pathlib
import sys
from math import comb

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.partition import (  # noqa: E402
    PartitionError, induced_partition, variation_of_information,
)
from prometheus_math.rand_index import RAND_1971, rand_index  # noqa: E402


def _from_labels(labels):
    labels = list(labels)
    return induced_partition(range(len(labels)), lambda i: labels[i])


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_identical_partitions_score_one():
    """RI = 1 for identical clusterings: every pair is either together in both or apart in both,
    so a + d = C(n,2). Hand-check n = 6, three blocks of two: a = 3, d = 12, C(6,2) = 15."""
    p = _from_labels([0, 0, 1, 1, 2, 2])
    assert rand_index(p, p, 6) == pytest.approx(1.0, abs=1e-12)


def test_authority_worked_example_by_hand():
    """Fully hand-computed, n = 6. X = {0,1,2}{3,4,5}, Y = {0,1}{2,3}{4,5}.

        a (together in both)  = C(2,2) + C(2,2) = 2
        together in X         = C(3,2)*2 = 6
        together in Y         = C(2,2)*3 = 3
        d (apart in both)     = C(6,2) - 6 - 3 + a = 15 - 6 - 3 + 2 = 8
        RI = (2 + 8) / 15 = 10/15 = 0.6666...
    """
    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    assert rand_index(x, y, 6) == pytest.approx(10.0 / 15.0, abs=1e-12)


def test_authority_citation_is_recorded():
    assert "Rand" in RAND_1971 and "1971" in RAND_1971


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_labels = st.lists(st.integers(0, 3), min_size=3, max_size=9)


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_in_unit_interval(a, b):
    """0 <= RI <= 1: it is a proportion of agreeing pairs."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    assert -1e-12 <= rand_index(p, t, n) <= 1.0 + 1e-12


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_symmetry(a, b):
    """RI(X, Y) = RI(Y, X) — 'together in both' and 'apart in both' are symmetric predicates."""
    n = min(len(a), len(b))
    if n < 3:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    assert rand_index(p, t, n) == pytest.approx(rand_index(t, p, n), abs=1e-12)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels)
def test_property_identity_is_one(a):
    n = len(a)
    if n < 3:
        return
    p = _from_labels(a)
    assert rand_index(p, p, n) == pytest.approx(1.0, abs=1e-12)


def test_property_RI_IS_INFLATED_which_is_why_ARI_exists():
    """**Hubert & Arabie's motivation, demonstrated rather than asserted.**

    RI does not approach 0 for unrelated clusterings — it is dominated by the `d` term, since most
    pairs are apart in both partitions once there are several blocks. On a deliberately
    below-chance pairing, RI stays high while ARI goes negative. A caller who reads RI as
    "fraction correct" will call an anti-correlated projection a good one.
    """
    from prometheus_math.adjusted_rand import adjusted_rand

    x = _from_labels([0, 0, 1, 1, 2, 2])
    y = _from_labels([0, 1, 2, 0, 1, 2])
    ri, ari = rand_index(x, y, 6), adjusted_rand(x, y, 6)
    assert ri > 0.5, f"RI should stay inflated on a below-chance pairing, got {ri}"
    assert ari < 0.0, f"ARI should be negative on the same input, got {ari}"


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

def test_edge_cases():
    """Edges covered, enumerated:

    - n < 2: REFUSES. C(n,2) = 0, so the denominator is zero and RI would be 0/0.
    - malformed partitions (not covering / overlapping): REFUSES.
    - all-singletons vs all-singletons: RI = 1 legitimately and does NOT refuse — unlike
      `adjusted_rand` and `fowlkes_mallows`, which are 0/0 there. That difference is the point of
      keeping the uncorrected index.
    """
    with pytest.raises(PartitionError):
        rand_index((), (), 0)
    with pytest.raises(PartitionError):
        rand_index((frozenset([0]),), (frozenset([0]),), 1)
    with pytest.raises(PartitionError):
        rand_index((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3)


def test_edge_all_singletons_is_DEFINED_here_though_ARI_and_FM_refuse():
    """**The same input, three indices, two refusals and one honest answer.**

    Two all-singleton partitions: every pair is apart in both, so `a = 0`, `d = C(n,2)` and
    RI = 1 exactly — well-defined and correct. `adjusted_rand` and `fowlkes_mallows` are both 0/0
    on this input and refuse. Pinning all three together stops a future caller assuming the family
    shares a domain.
    """
    from prometheus_math.adjusted_rand import adjusted_rand
    from prometheus_math.fowlkes_mallows import fowlkes_mallows

    singles = tuple(frozenset([i]) for i in range(4))
    assert rand_index(singles, singles, 4) == pytest.approx(1.0, abs=1e-12)
    with pytest.raises(PartitionError):
        adjusted_rand(singles, singles, 4)
    with pytest.raises(PartitionError):
        fowlkes_mallows(singles, singles, 4)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_agrees_with_the_pair_count_identity():
    """RI recomputed independently from the contingency table: (a + d) / C(n,2)."""
    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    n = 6
    a = sum(comb(len(bx & by), 2) for bx in x for by in y)
    tx = sum(comb(len(bx), 2) for bx in x)
    ty = sum(comb(len(by), 2) for by in y)
    d = comb(n, 2) - tx - ty + a
    assert rand_index(x, y, n) == pytest.approx((a + d) / comb(n, 2), abs=1e-12)


def test_composition_one_iff_vi_zero():
    """RI = 1 exactly when VI = 0 — a pair-counting index and an information-theoretic one must
    agree on the identity endpoint."""
    p = _from_labels([0, 0, 1, 1, 2, 2])
    q = _from_labels([0, 0, 0, 1, 1, 1])
    assert rand_index(p, p, 6) == pytest.approx(1.0, abs=1e-12)
    assert variation_of_information(p, p, 6) == pytest.approx(0.0, abs=1e-12)
    assert rand_index(p, q, 6) < 1.0 - 1e-9
    assert variation_of_information(p, q, 6) > 1e-9


def test_composition_ari_is_the_chance_corrected_form_of_this_index():
    """ARI = (RI - E[RI]) / (max - E[RI]) with everything expressed in pair counts. Recomputing
    ARI *from* RI and checking it against `adjusted_rand` chains the two implementations, so a
    normalisation error in either shows up here."""
    from prometheus_math.adjusted_rand import adjusted_rand

    x = _from_labels([0, 0, 0, 1, 1, 1])
    y = _from_labels([0, 0, 1, 1, 2, 2])
    n = 6
    a = sum(comb(len(bx & by), 2) for bx in x for by in y)
    tx = sum(comb(len(bx), 2) for bx in x)
    ty = sum(comb(len(by), 2) for by in y)
    expected = tx * ty / comb(n, 2)
    ari_from_counts = (a - expected) / ((tx + ty) / 2 - expected)
    assert adjusted_rand(x, y, n) == pytest.approx(ari_from_counts, abs=1e-12)
    assert rand_index(x, y, n) > adjusted_rand(x, y, n)      # uncorrected is the larger number
