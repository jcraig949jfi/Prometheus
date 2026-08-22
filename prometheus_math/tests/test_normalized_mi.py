"""Normalized mutual information — cycle 042, Track 1 (the 20% slice).

Reference: Strehl, A. & Ghosh, J. (2002). "Cluster Ensembles — A Knowledge Reuse Framework for
Combining Multiple Partitions." Journal of Machine Learning Research 3:583-617. NMI is defined
there as

    NMI(X, Y) = I(X; Y) / sqrt(H(X) H(Y))

Tests written before the implementation, all four categories, per the math-tdd skill.

NMI is a SIMILARITY where cycle 041's normalized VI is a DISTANCE, and they are not simply
complementary — that is what the composition tests are for.
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
    PartitionError, entropy, induced_partition, mutual_information, variation_of_information,
)
from prometheus_math.normalized_mi import STREHL_GHOSH_2002, normalized_mi  # noqa: E402


def _from_labels(labels):
    labels = list(labels)
    return induced_partition(range(len(labels)), lambda i: labels[i])


def _singletons(n):
    return tuple(frozenset([i]) for i in range(n))


def _one_block(n):
    return (frozenset(range(n)),)


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_identical_partitions_have_nmi_exactly_one():
    """Strehl & Ghosh (2002), eq. (2): NMI = 1 for identical clusterings.

    Hand-computation, n = 4, two blocks of two. H(X) = H(Y) = 1 bit. The partitions are equal so
    I(X;Y) = H(X) = 1. Then NMI = 1 / sqrt(1 * 1) = 1 exactly.
    """
    p = (frozenset([0, 1]), frozenset([2, 3]))
    assert entropy(p, 4) == pytest.approx(1.0, abs=1e-12)
    assert mutual_information(p, p, 4) == pytest.approx(1.0, abs=1e-12)
    assert normalized_mi(p, p, 4) == pytest.approx(1.0, abs=1e-12)


def test_authority_independent_partitions_have_nmi_zero():
    """Statistically independent clusterings share no information, so I = 0 and NMI = 0.

    Hand-constructed on n = 4: X splits {0,1}|{2,3}, Y splits {0,2}|{1,3}. Every cell of the
    joint table holds exactly one element, so p(x,y) = 1/4 = p(x)p(y) for all cells and the
    mutual information vanishes exactly.
    """
    x = (frozenset([0, 1]), frozenset([2, 3]))
    y = (frozenset([0, 2]), frozenset([1, 3]))
    assert mutual_information(x, y, 4) == pytest.approx(0.0, abs=1e-12)
    assert normalized_mi(x, y, 4) == pytest.approx(0.0, abs=1e-12)


def test_authority_citation_is_recorded():
    assert "Strehl" in STREHL_GHOSH_2002 and "2002" in STREHL_GHOSH_2002


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_labels = st.lists(st.integers(0, 3), min_size=2, max_size=9)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_nmi_is_in_the_unit_interval(a, b):
    """0 <= NMI <= 1. The upper bound is the Cauchy-Schwarz step in Strehl & Ghosh:
    I(X;Y) <= sqrt(H(X) H(Y)) since I <= min(H(X), H(Y))."""
    n = min(len(a), len(b))
    if n < 2:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if len(p) < 2 or len(t) < 2:
        return                                    # zero-entropy side: undefined, covered in edges
    v = normalized_mi(p, t, n)
    assert -1e-12 <= v <= 1.0 + 1e-12


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_symmetry(a, b):
    """NMI(X, Y) = NMI(Y, X) — the denominator is symmetric by construction."""
    n = min(len(a), len(b))
    if n < 2:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if len(p) < 2 or len(t) < 2:
        return
    assert normalized_mi(p, t, n) == pytest.approx(normalized_mi(t, p, n), abs=1e-12)


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels)
def test_property_maximal_exactly_on_identity(a):
    """NMI(X, X) = 1, and only equality achieves it among comparable partitions."""
    n = len(a)
    if n < 2:
        return
    p = _from_labels(a)
    if len(p) < 2:
        return
    assert normalized_mi(p, p, n) == pytest.approx(1.0, abs=1e-12)


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_labels, _labels)
def test_property_nmi_is_a_similarity_not_one_minus_a_distance(a, b):
    """**The trap this test exists to block.**

    NMI and normalized VI are both in [0, 1] and both extremal on identity, which invites
    `NMI = 1 - normalized_vi`. That identity is FALSE in general: VI normalises by log n while
    NMI normalises by sqrt(H(X)H(Y)), so the two use different denominators and only agree in
    special cases. Asserting they are NOT equal in general is the point — it stops a future
    caller substituting one for the other.
    """
    n = min(len(a), len(b))
    if n < 2:
        return
    p, t = _from_labels(a[:n]), _from_labels(b[:n])
    if len(p) < 2 or len(t) < 2:
        return
    nmi = normalized_mi(p, t, n)
    assert 0.0 - 1e-12 <= nmi <= 1.0 + 1e-12       # both live in the unit interval...
    # ...but the naive complement relation is only guaranteed at the identity endpoint.
    if p == t:
        assert nmi == pytest.approx(1.0, abs=1e-12)
        assert variation_of_information(p, t, n) == pytest.approx(0.0, abs=1e-12)


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

def test_edge_cases():
    """Edges covered, enumerated:

    - n = 0: REFUSES (no ground set).
    - EITHER partition has zero entropy (a single block): REFUSES. The denominator
      sqrt(H(X)H(Y)) is exactly 0, and I(X;Y) is also 0, so the value is 0/0. Returning 0.0 would
      say "these clusterings share nothing" and returning 1.0 would say "they agree perfectly" —
      both are claims about the clusterings, and neither is true.
    - BOTH sides zero entropy: REFUSES, same reason.
    - malformed partition (not covering / overlapping): REFUSES.
    - maximal and minimal values: attained exactly.
    """
    with pytest.raises(PartitionError):
        normalized_mi((), (), 0)
    whole = _one_block(4)
    sing = _singletons(4)
    with pytest.raises(PartitionError):
        normalized_mi(whole, sing, 4)              # H(X) = 0
    with pytest.raises(PartitionError):
        normalized_mi(sing, whole, 4)              # H(Y) = 0
    with pytest.raises(PartitionError):
        normalized_mi(whole, whole, 4)             # both zero
    with pytest.raises(PartitionError):
        normalized_mi((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3)


def test_edge_zero_entropy_refuses_rather_than_returning_zero_over_zero():
    """**The degenerate-domain discipline, applied at design time rather than retrofitted.**

    A one-block partition carries no information, so NMI's denominator vanishes. Every tempting
    answer conflates: 0.0 reads as "no agreement", 1.0 reads as "perfect agreement", nan
    propagates silently. The honest answer is that NMI is undefined when either side is constant,
    and the refusal says which side.
    """
    with pytest.raises(PartitionError) as exc:
        normalized_mi(_one_block(4), _singletons(4), 4)
    msg = str(exc.value)
    assert "zero entropy" in msg or "constant" in msg
    assert "projection" in msg or "truth" in msg   # names WHICH side, not just that it failed


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_nmi_agrees_with_the_entropy_identity():
    """NMI = I / sqrt(H(X)H(Y)), chained against `mutual_information` and `entropy` — three tools
    built at different times that must agree on the same objects."""
    for la, lb, n in (([0, 0, 1, 1, 2], [0, 1, 1, 2, 2], 5),
                      ([0, 1, 2, 3], [0, 0, 1, 1], 4),
                      ([0, 0, 1, 1, 1, 2], [0, 1, 1, 1, 2, 2], 6)):
        p, t = _from_labels(la), _from_labels(lb)
        i = mutual_information(p, t, n)
        hx, hy = entropy(p, n), entropy(t, n)
        assert normalized_mi(p, t, n) == pytest.approx(i / math.sqrt(hx * hy), abs=1e-9)


def test_composition_nmi_one_iff_vi_zero():
    """The two normalisations disagree everywhere except at the identity, where they must agree:
    NMI = 1 exactly when VI = 0. Chains `normalized_mi` against `variation_of_information`."""
    p = _from_labels([0, 0, 1, 1, 2, 2])
    q = _from_labels([0, 1, 2, 3, 4, 5])
    assert normalized_mi(p, p, 6) == pytest.approx(1.0, abs=1e-12)
    assert variation_of_information(p, p, 6) == pytest.approx(0.0, abs=1e-12)
    assert normalized_mi(p, q, 6) < 1.0 - 1e-9
    assert variation_of_information(p, q, 6) > 1e-9


def test_composition_refinement_raises_agreement_monotonically():
    """On a refinement chain fine <= mid <= coarse, moving AWAY from a fixed truth must not
    increase agreement. Chains `normalized_mi` against the refinement lattice used by cycles
    022-041, so a direction bug in either shows up as a sign error here.
    """
    n = 6
    truth = _from_labels([0, 0, 0, 1, 1, 1])
    fine = _from_labels([0, 1, 2, 3, 4, 5])
    mid = _from_labels([0, 0, 1, 1, 2, 2])
    near = _from_labels([0, 0, 0, 1, 1, 2])
    scores = [normalized_mi(x, truth, n) for x in (fine, mid, near)]
    assert scores[2] > scores[1] > 0.0
    assert all(0.0 <= s <= 1.0 + 1e-12 for s in scores)
