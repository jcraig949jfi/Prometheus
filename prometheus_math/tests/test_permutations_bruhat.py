"""Tests for prometheus_math.combinatorics_permutations.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: classical small cases of Bruhat, reduced words for S_3
  longest element, pattern counts, RSK shapes.
- Property: length = inv, identity is min, w_0 is max, Bruhat is
  reflexive/antisymmetric, weak_right subseteq Bruhat, all reduced
  words have same length.
- Edge: empty / singleton permutations, identity reduced word, n=0
  longest, mismatched sizes, malformed pattern.
- Composition: cover_relations consistency with bruhat_le, Bruhat
  interval [e, w_0] = S_n (size n!), |Av(123) in S_n| = Catalan(n),
  rsk_shape on n-perm sums to n.

References cited in test docstrings.
"""
from __future__ import annotations

from math import factorial
from itertools import permutations as _itp

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.combinatorics_permutations import (
    inversions,
    num_inversions,
    reduced_words,
    any_reduced_word,
    bruhat_le,
    weak_left_le,
    weak_right_le,
    bruhat_interval,
    cover_relations,
    longest_element,
    permutation_pattern_count,
    is_pattern_avoiding,
    rsk_shape,
    bruhat_distance,
)


# ---------------------------------------------------------------------------
# Helpers / strategies
# ---------------------------------------------------------------------------


def _all_perms(n: int):
    if n == 0:
        return [()]
    return [tuple(p) for p in _itp(range(1, n + 1))]


def _perms_of_n_strategy(n: int):
    return st.sampled_from(_all_perms(n))


# Catalan numbers (1, 1, 2, 5, 14, 42, 132, ...).
def _catalan(n: int) -> int:
    from math import comb

    return comb(2 * n, n) // (n + 1)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_inversions_s2_transposition():
    """The unique non-identity element of S_2 has 1 inversion.

    Reference: Bjorner-Brenti, "Combinatorics of Coxeter Groups"
    (2005), Section 1.5: in S_n, the inversion count equals the
    Coxeter length. For (2, 1) the only inversion pair (i, j) with
    i < j and w(i) > w(j) is (0, 1).
    """
    assert inversions((2, 1)) == [(0, 1)]


def test_num_inversions_longest_element_s4():
    """l(w_0) = n(n-1)/2 in S_n; for n=4 this is 6.

    Reference: Bjorner-Brenti (2005), Proposition 2.3.1: w_0 has
    length n(n-1)/2 and is the unique maximum in Bruhat order.
    """
    assert num_inversions(longest_element(4)) == 6


def test_reduced_words_s3_longest_element():
    """w_0 = (3, 2, 1) in S_3 has exactly the two reduced words
    [1, 2, 1] and [2, 1, 2].

    Reference: Bjorner-Brenti (2005), Example 1.5.2; equivalent to
    the braid relation s_1 s_2 s_1 = s_2 s_1 s_2 in S_3.
    """
    rws = sorted(reduced_words((3, 2, 1)))
    assert rws == [[1, 2, 1], [2, 1, 2]]


def test_bruhat_le_identity_to_longest_s3():
    """Identity (1, 2, 3) <= (3, 2, 1) in Bruhat order.

    Reference: Bjorner-Brenti (2005), Proposition 2.3.1: identity is
    the unique Bruhat-minimum, w_0 the unique maximum.
    """
    assert bruhat_le((1, 2, 3), (3, 2, 1)) is True


def test_bruhat_le_incomparable_pair_s3():
    """(2, 1, 3) and (1, 3, 2) are incomparable in S_3 Bruhat order.

    Both have length 1 (single inversions {(0,1)} and {(1,2)}). They
    are at the same rank but not equal, hence incomparable.
    Reference: Bjorner-Brenti (2005), Section 2.1, the Bruhat order
    on S_3 (Hasse diagram: identity, two atoms, two coatoms, w_0).
    """
    assert bruhat_le((2, 1, 3), (1, 3, 2)) is False
    assert bruhat_le((1, 3, 2), (2, 1, 3)) is False


def test_pattern_count_3142_contains_one_132():
    """w = (3, 1, 4, 2) contains exactly one 132-pattern.

    Hand-computation: the only length-3 subsequence with relative
    order 1, 3, 2 is positions (1, 2, 3) -> values (1, 4, 2), which
    rank-relabels to (1, 3, 2). All other 3-subsets do not match.
    Reference: Bona, "Combinatorics of Permutations" (2nd ed. 2012),
    Sec. 4.2.
    """
    assert permutation_pattern_count((3, 1, 4, 2), (1, 3, 2)) == 1


def test_rsk_shape_3142_is_partition_of_4():
    """RSK shape of (3, 1, 4, 2) is a partition of 4. By direct
    computation, P = [[1, 2], [3, 4]] (or similar) so shape = (2, 2).

    Hand-computation: insert 3 -> [[3]]; insert 1 -> bumps 3 down,
    so P = [[1], [3]]; insert 4 -> [[1, 4], [3]]; insert 2 -> bumps
    4 down to row 2 (where 2 < 3 so 2 bumps 3 down to row 3? actually
    row 2 has [3] so 2 < 3, 2 bumps 3 to row 3): final P =
    [[1, 2], [3, 4]] with shape (2, 2). Reference: Sagan (2001),
    Sec. 3.5.
    """
    shape = rsk_shape((3, 1, 4, 2))
    assert shape == (2, 2)
    assert sum(shape) == 4


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


@given(_perms_of_n_strategy(4))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=24)
def test_property_length_equals_reduced_word_length(w):
    """l(w) = inv(w) = length of any reduced word.

    Reference: Bjorner-Brenti (2005), Prop. 1.5.2.
    """
    assert num_inversions(w) == len(any_reduced_word(w))


@given(_perms_of_n_strategy(4))
@settings(max_examples=24)
def test_property_identity_below_everything(w):
    """In Bruhat order, identity is below every w.

    Reference: Bjorner-Brenti (2005), Prop. 2.3.1.
    """
    n = len(w)
    e = tuple(range(1, n + 1))
    assert bruhat_le(e, w) is True


@given(_perms_of_n_strategy(4))
@settings(max_examples=24)
def test_property_below_longest(w):
    """Every w in S_n satisfies w <= w_0 in Bruhat.

    Reference: Bjorner-Brenti (2005), Prop. 2.3.1.
    """
    assert bruhat_le(w, longest_element(len(w))) is True


@given(_perms_of_n_strategy(4))
@settings(max_examples=24)
def test_property_bruhat_reflexive(w):
    """bruhat_le(w, w) is True (reflexive)."""
    assert bruhat_le(w, w) is True


@given(_perms_of_n_strategy(3), _perms_of_n_strategy(3))
@settings(max_examples=36)
def test_property_bruhat_antisymmetric(w, v):
    """bruhat_le(w, v) and bruhat_le(v, w) imply w == v."""
    if bruhat_le(w, v) and bruhat_le(v, w):
        assert w == v


@given(_perms_of_n_strategy(3), _perms_of_n_strategy(3))
@settings(max_examples=36)
def test_property_weak_right_subseteq_bruhat(w, v):
    """Right weak order is a refinement of Bruhat order.

    Reference: Bjorner-Brenti (2005), Prop. 3.1.3.
    """
    if weak_right_le(w, v):
        assert bruhat_le(w, v)


@given(_perms_of_n_strategy(4))
@settings(max_examples=20)
def test_property_all_reduced_words_same_length(w):
    """Every reduced word for w has length l(w)."""
    L = num_inversions(w)
    for rw in reduced_words(w):
        assert len(rw) == L


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_edge_inversions_empty():
    """Empty permutation has no inversions."""
    assert inversions(()) == []


def test_edge_inversions_singleton():
    """Singleton permutation has no inversions."""
    assert inversions((1,)) == []


def test_edge_reduced_words_identity_s3():
    """Identity in S_3 has the empty word as its unique reduced word."""
    assert reduced_words((1, 2, 3)) == [[]]


def test_edge_longest_element_s1():
    """w_0 in S_1 is (1,)."""
    assert longest_element(1) == (1,)


def test_edge_longest_element_s0():
    """w_0 in S_0 is the empty tuple."""
    assert longest_element(0) == ()


def test_edge_bruhat_le_size_mismatch_raises():
    """Comparing permutations of different sizes raises ValueError."""
    with pytest.raises(ValueError):
        bruhat_le((1, 2, 3), (1, 2))


def test_edge_pattern_count_invalid_pattern_raises():
    """A pattern that is not a permutation of (1..k) raises ValueError."""
    with pytest.raises(ValueError):
        permutation_pattern_count((1, 2, 3), (5, 7))
    with pytest.raises(ValueError):
        permutation_pattern_count((1, 2, 3), ())


def test_edge_inversions_malformed_raises():
    """A non-permutation (e.g. duplicates) raises ValueError."""
    with pytest.raises(ValueError):
        inversions((1, 1, 2))


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_cover_relations_consistent_with_bruhat_le():
    """Every u in cover_relations(w) satisfies bruhat_le(w, u) and
    has length l(w) + 1.

    Composition test: cover_relations and bruhat_le must agree.
    Reference: Bjorner-Brenti (2005), Lemma 2.1.4.
    """
    for w in _all_perms(4):
        L = num_inversions(w)
        for u in cover_relations(w):
            assert bruhat_le(w, u) is True
            assert num_inversions(u) == L + 1


def test_composition_bruhat_interval_e_to_w0_is_full_sn():
    """[e, w_0] in Bruhat order equals all of S_n; size n!.

    Composition test: bruhat_interval, longest_element, factorial.
    Reference: Bjorner-Brenti (2005), Prop. 2.3.1.
    """
    for n in (2, 3, 4):
        e = tuple(range(1, n + 1))
        w0 = longest_element(n)
        interval = bruhat_interval(e, w0)
        assert len(interval) == factorial(n)
        assert set(interval) == set(_all_perms(n))


def test_composition_av_123_is_catalan():
    """|Av_n(123)| = C_n (Erdos-Szekeres / Knuth bijection).

    Composition test: pattern_count + is_pattern_avoiding chained on
    every permutation in S_n. Cross-checks Catalan formula.
    Reference: Knuth, "TAOCP" Vol. 1, Sec. 2.2.1, Ex. 4-5; Stanley
    EC2 Ex. 6.19.
    """
    for n in (1, 2, 3, 4, 5):
        avoiders = [w for w in _all_perms(n) if is_pattern_avoiding(w, [(1, 2, 3)])]
        assert len(avoiders) == _catalan(n), (
            f"Av_{n}(123) had size {len(avoiders)}, expected C_{n} = {_catalan(n)}"
        )


def test_composition_rsk_shape_partition_of_n():
    """For any permutation w of length n, rsk_shape(w) is a partition
    of n.

    Composition test: rsk_shape must agree with combinatorics_partitions
    invariants (weakly decreasing positive integers summing to n).
    Reference: Stanley EC2 Sec. 7.11.
    """
    for n in (1, 2, 3, 4):
        for w in _all_perms(n):
            shape = rsk_shape(w)
            assert sum(shape) == n
            assert all(p > 0 for p in shape)
            assert list(shape) == sorted(shape, reverse=True)


def test_composition_bruhat_distance_equals_length_diff():
    """When w <= v, bruhat_distance(w, v) = l(v) - l(w).

    Composition test: bruhat_distance + num_inversions consistency
    via Bruhat order being graded with rank = length.
    Reference: Bjorner-Brenti (2005), Theorem 2.2.6.
    """
    for w in _all_perms(3):
        for v in _all_perms(3):
            d = bruhat_distance(w, v)
            if bruhat_le(w, v):
                assert d == num_inversions(v) - num_inversions(w)
            elif bruhat_le(v, w):
                assert d == num_inversions(w) - num_inversions(v)
            else:
                assert d is None
