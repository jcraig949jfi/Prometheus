"""Test suite for prometheus_math.galois (Project #25 Phase 1).

Artin representation tools — Frobenius traces, conjugacy class identification
via factorization mod p, abelian L-function approximation.

Categories per math-tdd skill (techne/skills/math-tdd.md), 8+ tests:
  - Authority: Q(sqrt(-23)) quadratic character == Kronecker (-23/p);
               Q(zeta_5) cyclotomic split/inert behavior; permutation
               rep traces hand-checked against cycle structure.
  - Property:  |tr(Frob_p)| <= dim(rep) for irreducible unitary reps;
               sum of cycle lengths == polynomial degree;
               trivial rep trace == 1 at every good prime.
  - Edge:      ramified prime returns None; bad-poly raises ValueError;
               non-prime input raises ValueError.
  - Composition: frobenius_class output cycle type recoverable via
               cycle_type op; quadratic-character trace agrees with
               sympy's jacobi_symbol on a 50-prime sweep.

Run: pytest prometheus_math/tests/test_galois.py -v
"""
from __future__ import annotations

import math

import pytest
from sympy.functions.combinatorial.numbers import kronecker_symbol
from sympy import isprime, prime as nth_prime

from prometheus_math.galois import (
    artin_rep_from_polynomial,
    cycle_type,
    frobenius_class,
    frobenius_traces,
    artin_l_function_at_s,
)


# --------------------------------------------------------------------------- #
# Authority: Q(sqrt(-23)), the dim-1 quadratic character.                     #
# --------------------------------------------------------------------------- #


def test_authority_quadratic_character_q_sqrt_minus_23():
    """Q(sqrt(-23)) quadratic character: tr(Frob_p) = (-23/p) Kronecker.

    Reference: Neukirch, "Algebraic Number Theory", I.8 — for the unique
    non-trivial character chi of Gal(Q(sqrt(D))/Q) = Z/2, chi(Frob_p) is
    the Kronecker symbol (D/p) at unramified p (i.e. p does not divide
    disc K = -23).

    Hand-computation:
        p=3:  3 splits in Q(sqrt(-23)) iff -23 is a QR mod 3.
              -23 mod 3 = 1, which is a QR, so split, chi = +1.
        p=5:  -23 mod 5 = 2, not a QR mod 5, so inert, chi = -1.
        p=7:  -23 mod 7 = 5, not a QR mod 7, so inert, chi = -1.
    Cross-check: sympy.jacobi_symbol(-23, p) for p coprime to 23.
    """
    rep = artin_rep_from_polynomial('x^2+x+6')  # Hilbert class poly variant
    # We use x^2+x+6 because nfdisc = -23 (cleaner than x^2+23 which has
    # poldisc = -92 = -23 * 4 and adds index-2 ramification at 2).
    # Per the math-tdd skill: documented above.
    primes = [3, 5, 7, 11, 13, 17, 19, 29, 31, 37, 41, 43, 47, 53, 59]
    traces = frobenius_traces(rep, primes)
    for p in primes:
        expected = int(kronecker_symbol(-23, p))
        assert traces[p] == expected, (
            f"Frobenius trace at p={p}: got {traces[p]}, "
            f"Kronecker (-23/{p}) = {expected}"
        )


def test_authority_q_zeta_5_perm_rep_split_inert():
    """Q(zeta_5)/Q: cyclotomic, Gal = (Z/5)^* = Z/4. Permutation rep at split
    prime has 4 fixed points; at inert prime has 0 fixed points.

    Reference: Washington, "Introduction to Cyclotomic Fields", Theorem 2.13
    — p splits completely in Q(zeta_n) iff p ≡ 1 (mod n).

    Hand-check:
        p=11: 11 ≡ 1 mod 5  → split, perm-rep tr = 4.
        p=2:  2  ≡ 2 mod 5, ord(2 in (Z/5)*) = 4 → inert, tr = 0.
        p=19: 19 ≡ 4 mod 5, ord(4 in (Z/5)*) = 2 → cycle type (2,2),
              fixed points = 0, tr = 0.
    """
    rep = artin_rep_from_polynomial('polcyclo(5)', kind='permutation')
    traces = frobenius_traces(rep, [11, 31, 2, 3, 7, 19])
    # Split primes: 4 fixed points
    assert traces[11] == 4
    assert traces[31] == 4
    # Inert primes (order 4 in Z/4): 0 fixed points
    assert traces[2] == 0
    assert traces[3] == 0
    assert traces[7] == 0
    # Order-2 elements: cycle type (2,2), 0 fixed points
    assert traces[19] == 0


def test_authority_cubic_x3_minus_2_permutation_rep():
    """Q(zeta_3, 2^(1/3)) = splitting field of x^3 - 2, Gal = S_3.

    Reference: Lang, "Algebra", VI.6 example. Frob_p factorization
    pattern in O_K at unramified p. cycle types of Frob_p in S_3:
      identity (1,1,1) → 3 fixed pts  (tr_perm=3)
      transposition (2,1) → 1 fixed pt (tr_perm=1)
      3-cycle (3,)   → 0 fixed pts  (tr_perm=0)

    Hand-check via factormod and Dedekind's theorem:
        p=5:  cycle (2,1) — transposition (5 ≡ 2 mod 3, 2 not a cube mod 5),
              tr_perm = 1 fixed point.
        p=7:  cycle (3,) — 3-cycle (7 ≡ 1 mod 3 but 2 not a cube mod 7),
              tr_perm = 0.
        p=11: cycle (2,1) — transposition (11 ≡ 2 mod 3), tr_perm = 1.
        p=13: cycle (3,) — 2 is not a cube mod 13 (cubes={1,5,8,12}),
              tr_perm = 0.
        p=31: cycle (1,1,1) — 31 ≡ 1 mod 3 and 2 IS a cube mod 31
              (4^3=64=2 mod 31), splits completely, tr_perm = 3.
    """
    rep = artin_rep_from_polynomial('x^3-2', kind='permutation')
    traces = frobenius_traces(rep, [5, 7, 11, 13, 31])
    # transpositions (1 fixed pt)
    assert traces[5] == 1
    assert traces[11] == 1
    # 3-cycles (0 fixed pts)
    assert traces[7] == 0
    assert traces[13] == 0
    # Full split: 31 splits completely
    assert traces[31] == 3


# --------------------------------------------------------------------------- #
# Property: invariants that hold across many inputs.                          #
# --------------------------------------------------------------------------- #


def test_property_perm_rep_trace_bounded_by_degree():
    """For the permutation rep of degree n, |tr(Frob_p)| ≤ n always.

    Justification: tr_perm(g) = #{fixed points of g}, in [0, n] for any g
    in S_n. For dim-n irreducible Artin rep, the standard bound
    |chi(g)| ≤ chi(1) = n holds for ANY g (Schur).
    """
    polys = ['x^3-2', 'x^4-2', 'x^5-x-1', 'polcyclo(5)', 'polcyclo(7)']
    primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for p_str in polys:
        rep = artin_rep_from_polynomial(p_str, kind='permutation')
        n = rep['dimension']
        traces = frobenius_traces(rep, primes)
        for p, t in traces.items():
            if t is None:
                continue  # ramified
            assert 0 <= t <= n, (
                f"Permutation trace out of [0,{n}] for {p_str} at p={p}: t={t}"
            )


def test_property_cycle_type_sums_to_degree():
    """cycle_type(p, polynomial) sums to deg(polynomial) for unramified p.

    Justification: factorization mod p partitions the n roots into orbits
    under Frob_p; total length = n = deg(f). Equality fails iff p
    divides disc(f) (giving repeated factors), which we filter out.
    """
    polys_and_degs = [
        ('x^3-2', 3),
        ('x^4-2', 4),
        ('x^5-x-1', 5),
        ('polcyclo(7)', 6),
        ('x^2+x+6', 2),
    ]
    primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    for poly, deg in polys_and_degs:
        for p in primes:
            ct = cycle_type(p, poly)
            if ct is None:
                continue  # ramified
            assert sum(ct) == deg, (
                f"cycle_type({p}, {poly}) = {ct}, sum != {deg}"
            )


def test_property_trivial_rep_trace_always_one():
    """The trivial 1-d rep has tr(Frob_p) = 1 at every good prime.

    Justification: chi_trivial(g) = 1 for all g, in particular Frob_p.
    Cross-checks our handling of `kind='trivial'` against this identity.
    """
    rep = artin_rep_from_polynomial('x^3-2', kind='trivial')
    primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
    traces = frobenius_traces(rep, primes)
    for p in primes:
        if traces[p] is None:
            continue
        assert traces[p] == 1, f"trivial rep trace != 1 at p={p}: {traces[p]}"


# --------------------------------------------------------------------------- #
# Edge cases.                                                                 #
# --------------------------------------------------------------------------- #


def test_edge_ramified_prime_returns_none():
    """At p | disc(K), Frob is not well-defined as a conjugacy class
    (modulo the inertia subgroup). Convention: return None.

    Edge: x^2+x+6 has nfdisc = -23, so p=23 is ramified.
    """
    rep = artin_rep_from_polynomial('x^2+x+6')
    traces = frobenius_traces(rep, [23])
    assert traces[23] is None, f"expected None at ramified p=23, got {traces[23]}"


def test_edge_bad_polynomial_input_raises():
    """Edge cases:
      - empty list → ValueError
      - constant poly → ValueError (no Galois extension)
      - reducible poly → ValueError (not an irreducible Artin rep)
      - linear poly → ValueError (trivial extension)
    """
    with pytest.raises(ValueError):
        artin_rep_from_polynomial([])
    with pytest.raises(ValueError):
        artin_rep_from_polynomial('5')  # constant
    with pytest.raises(ValueError):
        artin_rep_from_polynomial('x^2-1')  # reducible: (x-1)(x+1)
    with pytest.raises(ValueError):
        artin_rep_from_polynomial('x-1')   # linear


def test_edge_non_prime_input_raises():
    """frobenius_class(poly, p) must reject composite or non-prime p."""
    with pytest.raises(ValueError):
        frobenius_class('x^2+1', 4)
    with pytest.raises(ValueError):
        frobenius_class('x^2+1', 1)
    with pytest.raises(ValueError):
        frobenius_class('x^2+1', 0)
    with pytest.raises(ValueError):
        frobenius_class('x^2+1', -3)


# --------------------------------------------------------------------------- #
# Composition tests.                                                          #
# --------------------------------------------------------------------------- #


def test_composition_quadratic_character_vs_sympy_jacobi_50_primes():
    """Composition: frobenius_traces(quadratic-character rep) agrees with
    sympy.jacobi_symbol(-23, p) on the first 50 primes coprime to 23.

    Chains: artin_rep_from_polynomial → frobenius_traces → cross-check
    against an independent number-theory implementation (sympy).
    """
    rep = artin_rep_from_polynomial('x^2+x+6')  # nfdisc = -23
    primes = []
    p = 2
    while len(primes) < 50:
        if p != 23:
            primes.append(p)
        p += 1
        while not isprime(p):
            p += 1
    traces = frobenius_traces(rep, primes)
    for p in primes:
        expected = int(kronecker_symbol(-23, p))
        if expected == 0:
            assert traces[p] is None, f"p={p} divides disc, got {traces[p]}"
        else:
            assert traces[p] == expected, (
                f"p={p}: trace={traces[p]} vs Kronecker={expected}"
            )


def test_composition_cycle_type_sums_match_frobenius_class_string():
    """cycle_type(p, f) and frobenius_class(p, f) must be consistent.

    The class string is canonicalized as the cycle type joined by '+';
    parsing the string back should give the same tuple. This guards
    against drift between the two interfaces.
    """
    pairs = [('x^3-2', 5), ('x^3-2', 11), ('x^3-2', 31),
             ('x^4-2', 7), ('polcyclo(5)', 11)]
    for poly, p in pairs:
        ct = cycle_type(p, poly)
        cls_str = frobenius_class(poly, p)
        # frobenius_class returns string like "3" or "2+1" or "1+1+1"
        parts = tuple(int(s) for s in cls_str.split('+'))
        # frobenius_class is sorted descending too
        assert parts == ct, (
            f"frobenius_class({poly},{p})={cls_str!r} parsed={parts} "
            f"vs cycle_type={ct}"
        )


def test_composition_l_function_truncation_finite_at_s_2():
    """artin_l_function_at_s for the trivial rep with s=2 should
    approximate zeta(2) ≈ pi^2/6 ≈ 1.6449 as we extend the truncation.

    The trivial Artin rep has L(s, 1) = zeta(s) (Euler product over
    all primes), so this is a sanity check that our truncated Euler
    product converges to the right limit.
    """
    rep = artin_rep_from_polynomial('x^2+x+6', kind='trivial')
    val = artin_l_function_at_s(rep, 2.0, n_primes=200)
    # zeta(2) = pi^2/6 ≈ 1.6449...; truncated product over first 200
    # primes will be slightly under; allow 5% tolerance.
    target = math.pi ** 2 / 6
    assert abs(val.real - target) < 0.05 * target, (
        f"trivial-rep L(2) = {val} vs zeta(2) = {target}"
    )
    assert abs(val.imag) < 1e-9


def test_composition_artin_rep_galois_group_consistency():
    """artin_rep_from_polynomial dimension agrees with degree of poly,
    and the galois_group field matches the canonical Galois group.

    Composition with techne.lib.galois_group: ensures the rep metadata
    is consistent with our number_theory.galois_group output.
    """
    from prometheus_math.number_theory import galois_group as gg
    cases = [('x^2+x+6', 2), ('x^3-2', 3), ('polcyclo(5)', 4)]
    for poly, expected_deg in cases:
        rep = artin_rep_from_polynomial(poly)
        # base_degree always equals deg(f); 'dimension' depends on rep kind.
        assert rep['base_degree'] == expected_deg
        # For 'permutation' kind dim = deg; for n=2 default 'sign' kind dim=1.
        rep_perm = artin_rep_from_polynomial(poly, kind='permutation')
        assert rep_perm['dimension'] == expected_deg
        # Galois group order should match
        gal_g = gg(poly)
        assert rep['galois_group']['order'] == gal_g['order']
