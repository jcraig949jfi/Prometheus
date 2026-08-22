"""Normalized variation of information — cycle 041, Track 1.

Reference throughout: Marina Meila, "Comparing clusterings — an information based distance",
Journal of Multivariate Analysis 98 (2007) 873-895.

Written before the implementation, all four categories, per the math-tdd skill.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.partition import (  # noqa: E402
    PartitionError, conditional_entropy, entropy, induced_partition, refines,
    variation_of_information,
)
from prometheus_math.normalized_vi import (  # noqa: E402
    MEILA_2007, normalized_vi, vi_upper_bound,
)


def _from_labels(labels):
    """`induced_partition` takes (items, key) and returns blocks of INDICES, so a label list
    becomes a partition via the identity lookup."""
    labels = list(labels)
    return induced_partition(range(len(labels)), lambda i: labels[i])


def _singletons(n):
    return tuple(frozenset([i]) for i in range(n))


def _one_block(n):
    return (frozenset(range(n)),)


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_vi_between_the_lattice_extremes_is_log_n():
    """Meila (2007), Section 4: VI is bounded by log n, and the bound is ATTAINED by the two
    extremes of the refinement lattice.

    Hand-computation for n = 4, in bits. The all-singletons partition has four equiprobable
    blocks, so H = log2(4) = 2. The one-block partition has H = 0. They share no information,
    so I = 0. Then VI = H(P) + H(T) - 2I = 2 + 0 - 0 = 2 = log2(4). Normalised by log2(n) = 2,
    the distance is exactly 1.0 -- the maximum.
    """
    for n in (2, 4, 8, 16):
        vi = variation_of_information(_singletons(n), _one_block(n), n)
        assert vi == pytest.approx(math.log2(n), abs=1e-12)
        assert normalized_vi(_singletons(n), _one_block(n), n) == pytest.approx(1.0, abs=1e-12)


def test_authority_upper_bound_matches_meila_and_the_citation_is_recorded():
    """Meila (2007) gives VI(C, C') <= log n for any two clusterings of n points."""
    assert "Meila" in MEILA_2007 and "2007" in MEILA_2007
    for n in (1, 2, 5, 10, 64):
        assert vi_upper_bound(n) == pytest.approx(math.log2(n), abs=1e-12)


def test_authority_identical_clusterings_are_at_distance_zero():
    """Meila (2007), Property 1: VI(C, C) = 0. A metric's identity of indiscernibles."""
    p = (frozenset([0, 1]), frozenset([2]), frozenset([3, 4]))
    assert variation_of_information(p, p, 5) == pytest.approx(0.0, abs=1e-12)
    assert normalized_vi(p, p, 5) == pytest.approx(0.0, abs=1e-12)


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_labels = st.lists(st.integers(0, 3), min_size=2, max_size=9)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_normalized_vi_is_in_the_unit_interval(a, b):
    """Meila's bound, normalised: 0 <= VI / log n <= 1 for every pair of clusterings."""
    n = min(len(a), len(b))
    if n < 2:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    d = normalized_vi(p, t, n)
    assert -1e-12 <= d <= 1.0 + 1e-12


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_symmetry(a, b):
    """Meila (2007), Property 2: VI is symmetric. A distance that is not would not be one."""
    n = min(len(a), len(b))
    if n < 2:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    assert normalized_vi(p, t, n) == pytest.approx(normalized_vi(t, p, n), abs=1e-12)


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels, _labels)
def test_property_triangle_inequality(a, b, c):
    """**Meila (2007), Property 3 — VI is a TRUE METRIC on the space of clusterings.**

    This is the property that makes it worth having: it licenses talking about the DISTANCE
    between two projections rather than merely their disagreement. Normalisation by a constant
    (log n, with n fixed across the three) preserves it.
    """
    n = min(len(a), len(b), len(c))
    if n < 2:
        return
    p, q, r = (_from_labels(x[:n]) for x in (a, b, c))
    assert (normalized_vi(p, r, n)
            <= normalized_vi(p, q, n) + normalized_vi(q, r, n) + 1e-9)


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels)
def test_property_zero_exactly_on_identity(a):
    """VI(P, T) == 0 iff P == T -- the other half of identity of indiscernibles."""
    n = len(a)
    if n < 2:
        return
    p = _from_labels(a)
    assert normalized_vi(p, p, n) == pytest.approx(0.0, abs=1e-12)
    if len(p) > 1:
        assert normalized_vi(p, _one_block(n), n) > 1e-12


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

def test_edge_cases():
    """Edges covered here, enumerated so a missing one is visible:

    - n = 0 (empty ground set): REFUSES. log2(0) is undefined, and returning 0.0 would read as
      "these two clusterings are identical" -- this cycle's whole subject.
    - n = 1 (singleton ground set): REFUSES. log2(1) = 0, so the normaliser is zero and every
      distance would divide by it. The unnormalised VI is legitimately 0 here; the NORMALISED
      one is undefined, and saying so beats returning 0.0.
    - blocks not covering the ground set: REFUSES (inherited from `_validate`).
    - overlapping blocks: REFUSES.
    - maximal distance: attained, equals 1.0 exactly, not 1.0 - epsilon.
    """
    with pytest.raises(PartitionError):
        normalized_vi((), (), 0)
    with pytest.raises(PartitionError):
        normalized_vi((frozenset([0]),), (frozenset([0]),), 1)
    with pytest.raises(PartitionError):
        normalized_vi((frozenset([0]),), (frozenset([0]), frozenset([1])), 2)
    with pytest.raises(PartitionError):
        normalized_vi((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3)
    assert normalized_vi(_singletons(8), _one_block(8), 8) == pytest.approx(1.0, abs=1e-12)


def test_edge_n_equals_one_refuses_rather_than_dividing_by_zero():
    """**Pulled out because it is the cycle-040 bug class in its natural habitat.**

    At n = 1 the normaliser log2(1) is exactly 0. The tempting implementations both conflate:
    returning 0.0 says "identical", and returning nan propagates silently. The honest answer is
    that normalised VI has no value on a one-element ground set, said out loud.
    """
    with pytest.raises(PartitionError) as exc:
        normalized_vi((frozenset([0]),), (frozenset([0]),), 1)
    assert "log2(1)" in str(exc.value) or "one element" in str(exc.value)
    # ...while the UNNORMALISED quantity is perfectly well-defined and stays available.
    assert variation_of_information((frozenset([0]),), (frozenset([0]),), 1) == pytest.approx(0.0)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_vi_is_deficit_plus_excess():
    """VI decomposes into the two conditional entropies -- Meila (2007), Eq. (3):

        VI(P, T) = H(P | T) + H(T | P)

    This chains `normalized_vi` against `conditional_entropy`, which was built independently in
    cycle 023 for the sweep directions. Two tools that were never fitted to each other must agree,
    which is what makes this worth more than a unit test.
    """
    for labels_p, labels_t, n in (([0, 0, 1, 1, 2], [0, 1, 1, 2, 2], 5),
                                  ([0, 1, 2, 3], [0, 0, 1, 1], 4),
                                  ([0, 0, 0, 1], [0, 1, 2, 3], 4)):
        p, t = _from_labels(labels_p), _from_labels(labels_t)
        deficit = conditional_entropy(t, p, n)
        excess = conditional_entropy(p, t, n)
        assert variation_of_information(p, t, n) == pytest.approx(deficit + excess, abs=1e-9)
        assert normalized_vi(p, t, n) == pytest.approx((deficit + excess) / math.log2(n), abs=1e-9)


def test_composition_on_a_refinement_chain_vi_collapses_to_one_entropy_gap():
    """When P REFINES T, one of the two conditional entropies vanishes and

        VI(P, T) = H(P | T) = H(P) - H(T)

    Chains `refines` (cycle 022), `entropy` (023) and `variation_of_information` against each
    other on the same objects. Any disagreement means one of the three has a convention bug --
    which is exactly the off-by-a-direction failure the ladder work keeps producing.
    """
    n = 6
    fine = _from_labels([0, 1, 2, 3, 4, 5])
    mid = _from_labels([0, 0, 1, 1, 2, 2])
    coarse = _from_labels([0, 0, 0, 0, 0, 0])
    for p, t in ((fine, mid), (mid, coarse), (fine, coarse)):
        assert refines(p, t, n)
        assert conditional_entropy(t, p, n) == pytest.approx(0.0, abs=1e-12)
        assert variation_of_information(p, t, n) == pytest.approx(
            entropy(p, n) - entropy(t, n), abs=1e-9)
        assert normalized_vi(p, t, n) == pytest.approx(
            (entropy(p, n) - entropy(t, n)) / math.log2(n), abs=1e-9)


def test_composition_normalisation_is_the_scale_free_comparison_it_claims_to_be():
    """**The point of normalising, tested rather than asserted.**

    The lattice-extreme distance is log n in raw bits, so a raw VI comparison between ground sets
    of different sizes reports the size, not the disagreement. Normalised, the same structural
    relationship reads the same at every n -- which is what makes cross-n comparison legitimate.
    """
    raw = [variation_of_information(_singletons(n), _one_block(n), n) for n in (4, 8, 16, 32)]
    assert len(set(round(r, 9) for r in raw)) == 4          # raw: four different numbers
    norm = [normalized_vi(_singletons(n), _one_block(n), n) for n in (4, 8, 16, 32)]
    assert all(x == pytest.approx(1.0, abs=1e-12) for x in norm)   # normalised: one number
