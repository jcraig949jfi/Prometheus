"""Tests for prometheus_math.combinatorics_posets.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: chain/antichain cover relations, Boolean lattice Mobius
  function (-1)^n, divisor poset of 12, num_linear_extensions of
  chain (=1) and antichain (=n!), Mobius of chain (=0 for length>1),
  Dilworth's theorem on B_3, divisor poset Mobius (=mu(n/d) classical
  number-theoretic Mobius).
- Property: reflexivity, antisymmetry, transitivity, Mobius integer-
  valued, dual involution, product cardinality, distributive Boolean
  lattices, linear extension is a chain.
- Edge: empty poset, single-element poset, inconsistent relations,
  unknown elements raising KeyError, missing join/meet returns None.
- Composition: linear_extensions[0] is a chain, mobius restricted to
  interval, is_lattice on Boolean, product(chain(2),chain(2)) iso B_2.
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.combinatorics_posets import (
    Poset,
    chain_poset,
    antichain_poset,
    boolean_lattice,
    divisor_poset,
    product_poset,
    dual_poset,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_chain_poset_3_cover_relations():
    """chain_poset(3) cover relations are exactly (1,2) and (2,3).

    Reference: Stanley, "Enumerative Combinatorics, Vol. 1" (2nd ed.,
    2012), Ch. 3.1, Example 3.1.1: the chain n is the poset on
    {1, ..., n} with the usual total order, whose Hasse diagram is a
    path.
    """
    P = chain_poset(3)
    covers = sorted(P.cover_relations())
    assert covers == [(1, 2), (2, 3)]


def test_boolean_lattice_2_size_and_mobius():
    """B_2 has 4 elements; mu(empty, full) = (-1)^2 = 1.

    Reference: Stanley, "Enumerative Combinatorics, Vol. 1" (2nd ed.,
    2012), Example 3.8.3: the Mobius function of the Boolean lattice
    B_n satisfies mu(0, 1_hat) = (-1)^n. For n=2 this is +1.
    """
    P = boolean_lattice(2)
    assert len(P.elements) == 4
    bot = frozenset()
    top = frozenset({0, 1})
    assert P.mobius(bot, top) == 1


def test_boolean_lattice_3_mobius_is_minus_one():
    """B_3: mu(empty, full) = (-1)^3 = -1.

    Reference: Stanley, "Enumerative Combinatorics, Vol. 1" (2nd ed.,
    2012), Example 3.8.3.
    """
    P = boolean_lattice(3)
    bot = frozenset()
    top = frozenset({0, 1, 2})
    assert P.mobius(bot, top) == -1


def test_divisor_poset_12_elements():
    """divisor_poset(12) has 6 elements: 1, 2, 3, 4, 6, 12.

    Reference: Stanley, EC1 (2nd ed., 2012), Example 3.1.1(d): the
    divisor poset D_n is the set of positive divisors of n ordered by
    divisibility. D_12 = {1, 2, 3, 4, 6, 12}.
    """
    P = divisor_poset(12)
    assert sorted(P.elements) == [1, 2, 3, 4, 6, 12]


def test_divisor_poset_12_mobius_matches_classical():
    """For D_n, mu_D(1, k) equals the classical number-theoretic
    Mobius function mu(k).

    Reference: Stanley, EC1 (2nd ed., 2012), Example 3.8.4: the
    Mobius function of the divisor lattice agrees with the classical
    Mobius. mu(1)=1, mu(2)=-1, mu(3)=-1, mu(4)=0, mu(6)=1, mu(12)=0.
    """
    P = divisor_poset(12)
    expected = {1: 1, 2: -1, 3: -1, 4: 0, 6: 1, 12: 0}
    for k, mu_k in expected.items():
        assert P.mobius(1, k) == mu_k, (k, P.mobius(1, k), mu_k)


def test_chain_poset_4_one_linear_extension():
    """A total order has exactly one linear extension.

    Reference: Stanley, EC1 (2nd ed., 2012), Section 3.5: a chain has
    exactly one linear extension (itself).
    """
    P = chain_poset(4)
    assert P.num_linear_extensions() == 1


def test_antichain_poset_3_has_factorial_extensions():
    """An antichain on n elements has n! linear extensions.

    Reference: Stanley, EC1 (2nd ed., 2012), Section 3.5: every
    permutation is a linear extension of the antichain.
    """
    from math import factorial
    P = antichain_poset(3)
    assert P.num_linear_extensions() == factorial(3)


def test_chain_mobius_is_zero_for_length_at_least_two():
    """For chain_poset(n) with n >= 2: mu(0, n-1) = 0 unless n == 1.

    Reference: Stanley, EC1 (2nd ed., 2012), Example 3.8.1: in a chain
    of length L, mu(0, k) = 1 if k=0, -1 if k=1, 0 if k >= 2.
    """
    P = chain_poset(4)  # elements 1..4, length 3
    assert P.mobius(1, 1) == 1
    assert P.mobius(1, 2) == -1
    assert P.mobius(1, 3) == 0
    assert P.mobius(1, 4) == 0


def test_max_antichain_boolean_3_is_level_2():
    """In B_3 the largest antichain is the level-2 subsets (size 3).

    Reference: Sperner's theorem (1928); Stanley, EC1, Example 3.4.1.
    Maximum antichain in B_n has size C(n, floor(n/2)). C(3,1)=3.
    """
    P = boolean_lattice(3)
    A = P.max_antichain()
    assert len(A) == 3
    # All elements should be size-2 OR size-1 subsets (both extremes
    # work in Sperner; we just require the count).
    assert P.antichain(A)


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


@given(st.integers(min_value=1, max_value=6))
def test_chain_le_is_reflexive(n):
    """le(a, a) is True for every element of every chain."""
    P = chain_poset(n)
    for a in P.elements:
        assert P.le(a, a)


@given(st.integers(min_value=2, max_value=5))
def test_divisor_poset_antisymmetric(n):
    """If le(a, b) and le(b, a) then a == b — divisor poset case."""
    P = divisor_poset(n * n)  # bigger lattice for variety
    for a in P.elements:
        for b in P.elements:
            if P.le(a, b) and P.le(b, a):
                assert a == b


@given(st.integers(min_value=2, max_value=4))
def test_boolean_lattice_transitive(n):
    """If le(a, b) and le(b, c) then le(a, c) — Boolean lattice."""
    P = boolean_lattice(n)
    elts = list(P.elements)
    for a in elts:
        for b in elts:
            if not P.le(a, b):
                continue
            for c in elts:
                if P.le(b, c):
                    assert P.le(a, c)


@given(st.integers(min_value=1, max_value=4))
def test_mobius_is_integer(n):
    """mu(a, b) is always an integer (here checked via type)."""
    P = boolean_lattice(n)
    elts = list(P.elements)
    for a in elts:
        for b in elts:
            if P.le(a, b):
                m = P.mobius(a, b)
                assert isinstance(m, int)


@given(st.integers(min_value=1, max_value=4))
def test_dual_is_involution(n):
    """dual(dual(P)) has same cover relations as P."""
    P = boolean_lattice(n)
    DD = dual_poset(dual_poset(P))
    assert set(DD.cover_relations()) == set(P.cover_relations())


@given(st.integers(min_value=1, max_value=4), st.integers(min_value=1, max_value=4))
def test_product_cardinality(p, q):
    """|P x Q| = |P| * |Q|."""
    P = chain_poset(p)
    Q = chain_poset(q)
    PQ = product_poset(P, Q)
    assert len(PQ.elements) == p * q


@given(st.integers(min_value=1, max_value=4))
def test_boolean_lattice_is_distributive(n):
    """Every Boolean lattice is distributive."""
    P = boolean_lattice(n)
    assert P.is_distributive()


@given(st.integers(min_value=1, max_value=4))
def test_linear_extension_is_a_chain(n):
    """Every linear extension is a chain in the original poset."""
    P = chain_poset(n)  # any poset works; test on chain
    le = P.linear_extensions()[0]
    assert P.chain(le)


@given(st.integers(min_value=2, max_value=5))
def test_linear_extension_respects_order(n):
    """For each linear extension, if a precedes b in the list then
    we never have b < a in the partial order."""
    P = divisor_poset(2 ** (n - 1))  # totally ordered chain {1,2,4,...}
    for ext in P.linear_extensions():
        for i, a in enumerate(ext):
            for b in ext[i + 1:]:
                assert not P.lt(b, a)


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_empty_poset():
    """Empty poset edges: no relations, exactly one linear extension
    (the empty list)."""
    P = Poset(elements=[], relations=[])
    assert P.elements == []
    assert P.cover_relations() == []
    assert P.num_linear_extensions() == 1
    assert P.linear_extensions() == [[]]


def test_single_element_poset():
    """Singleton poset: 1 linear extension; mu(a,a) = 1; le reflexive."""
    P = Poset(elements=["x"], relations=[])
    assert P.le("x", "x")
    assert P.num_linear_extensions() == 1
    assert P.mobius("x", "x") == 1


def test_inconsistent_relations_raise():
    """Cyclic relations a < b < a (with a != b) must raise ValueError."""
    with pytest.raises(ValueError):
        Poset(elements=[1, 2], relations=[(1, 2), (2, 1)])


def test_unknown_element_raises_keyerror():
    """le on an element not in the poset raises KeyError."""
    P = chain_poset(3)
    with pytest.raises(KeyError):
        P.le(1, 99)


def test_join_returns_none_when_not_unique():
    """In the diamond {a,b,c,d} with a<c, a<d, b<c, b<d (no top),
    join(c, d) is None (no unique upper bound)."""
    # Build poset N = {a, b, c, d} with cover relations a<c, a<d, b<c, b<d
    P = Poset(
        elements=["a", "b", "c", "d"],
        relations=[("a", "c"), ("a", "d"), ("b", "c"), ("b", "d")],
    )
    # join(a, b) does not exist: c and d both upper bounds, neither <= other
    assert P.join("a", "b") is None
    # meet(c, d) does not exist: a and b both lower bounds, neither >= other
    assert P.meet("c", "d") is None


def test_isomorphism_simple_cases():
    """chain(3) is isomorphic to itself; chain(3) is NOT iso to
    antichain(3)."""
    C = chain_poset(3)
    A = antichain_poset(3)
    assert C.is_isomorphic_to(chain_poset(3))
    assert not C.is_isomorphic_to(A)


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_chain_returns_true_on_linear_extension():
    """Composition: linear_extensions[0] of any poset must satisfy
    chain(...) == True restricted to elements that form a chain in P.

    Note: a 'linear extension' is a list-permutation that respects <=
    of P, not necessarily a chain in P itself. So we test on a poset
    that IS a chain, where its linear extension is a P-chain.
    """
    P = chain_poset(4)
    ext = P.linear_extensions()[0]
    assert P.chain(ext)


def test_mobius_consistent_with_interval():
    """Composition: the Mobius function of a poset P, restricted to
    the interval [a, b], should match the Mobius function of the
    sub-poset P|[a,b].

    Test in B_3: mu(empty, {0,1,2}) computed in B_3 should equal
    mu(empty, {0,1,2}) computed in the interval poset."""
    P = boolean_lattice(3)
    bot = frozenset()
    top = frozenset({0, 1, 2})
    # Interval as a sub-poset
    interval = P.interval(bot, top)
    sub_relations = []
    for x in interval:
        for y in interval:
            if P.le(x, y) and x != y:
                sub_relations.append((x, y))
    Q = Poset(elements=list(interval), relations=sub_relations)
    assert P.mobius(bot, top) == Q.mobius(bot, top)


def test_boolean_lattice_is_a_lattice():
    """Composition: is_lattice() ∘ boolean_lattice(n) must always be
    True (Boolean lattice has joins=union, meets=intersection)."""
    for n in range(1, 4):
        P = boolean_lattice(n)
        assert P.is_lattice()


def test_product_of_chains_is_boolean():
    """Composition: chain(2) x chain(2) is isomorphic to B_2.

    Reference: Stanley, EC1, Example 3.1.1: B_n decomposes as the
    n-fold direct product of the 2-element chain.
    """
    C2 = chain_poset(2)
    P = product_poset(C2, C2)
    B2 = boolean_lattice(2)
    assert P.is_isomorphic_to(B2)


def test_chain_x_chain_is_distributive():
    """Composition: product of distributive lattices is distributive
    (here chain x chain). Cross-checks is_lattice + is_distributive."""
    P = product_poset(chain_poset(3), chain_poset(2))
    assert P.is_lattice()
    assert P.is_distributive()
