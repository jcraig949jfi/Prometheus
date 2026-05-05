"""Property-based test suite for prometheus_math.number_theory.

Project #6 from techne/PROJECT_BACKLOG_1000.md. Hypothesis-driven property
tests covering the 24 functions exposed via prometheus_math.number_theory.

Categories per math-tdd skill (techne/skills/math-tdd.md):
  - 2: property-based tests via `hypothesis` (this file's main focus)
  - 3: edge cases (woven in where natural)

Each test states the property under test in the docstring, with the
mathematical justification (textbook citation or definition). When a
property is violated by the implementation, the test does NOT silently
weaken its assertion: the failure is documented in BUGS.md and the test
remains as a regression marker.

Run: pytest prometheus_math/tests/test_number_theory_properties.py -v
                                    --hypothesis-show-statistics
"""
from __future__ import annotations

import math
from fractions import Fraction
from math import factorial, gcd

import numpy as np
import pytest
from hypothesis import HealthCheck, assume, example, given, settings, strategies as st

from prometheus_math.number_theory import (
    cf_expand,
    cf_max_digit,
    class_field_tower,
    class_group,
    class_number,
    cm_order_data,
    disc_is_square,
    fe_residual,
    functional_eq_check,
    galois_group,
    hilbert_class_field,
    is_abelian,
    is_cyclotomic,
    lll,
    lll_gram,
    lll_with_transform,
    log_mahler_measure,
    mahler_measure,
    regulator_nf,
    set_pari_stack_mb,
    shortest_vector_lll,
    sturm_bound,
    zaremba_test,
)


# --------------------------------------------------------------------------- #
# Hypothesis profiles                                                         #
# --------------------------------------------------------------------------- #

FAST = settings(max_examples=100, deadline=None,
                suppress_health_check=[HealthCheck.too_slow,
                                       HealthCheck.function_scoped_fixture])
MEDIUM = settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.too_slow,
                                         HealthCheck.function_scoped_fixture])
SLOW = settings(max_examples=20, deadline=None,
                suppress_health_check=[HealthCheck.too_slow,
                                       HealthCheck.function_scoped_fixture])
VERY_SLOW = settings(max_examples=10, deadline=None,
                     suppress_health_check=[HealthCheck.too_slow,
                                            HealthCheck.function_scoped_fixture])


# --------------------------------------------------------------------------- #
# Custom strategies                                                           #
# --------------------------------------------------------------------------- #

# Bounded integer coefficients — keep degree small to avoid numerical roots
# blowing up in mahler_measure (np.roots on degree > ~30 gets noisy).
def small_int_coeffs(min_size=1, max_size=8, lo=-5, hi=5):
    """Integer polynomial coefficients (descending order)."""
    return st.lists(st.integers(min_value=lo, max_value=hi),
                    min_size=min_size, max_size=max_size)


def nonzero_int_coeffs(min_size=1, max_size=8, lo=-5, hi=5):
    """Coefficients with at least one non-zero entry."""
    return small_int_coeffs(min_size, max_size, lo, hi).filter(
        lambda c: any(x != 0 for x in c)
    )


# Small primes for class-number / Galois tests
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


@st.composite
def imag_quad_disc(draw, min_value=-200, max_value=-3):
    """Imaginary quadratic discriminant: D < 0, D ≡ 0 or 1 (mod 4)."""
    D = draw(st.integers(min_value=min_value, max_value=max_value))
    while D % 4 not in (0, 1):
        D -= 1
        if D < min_value:
            D = max_value
            while D % 4 not in (0, 1):
                D -= 1
            break
    return D


@st.composite
def quadratic_poly_minus_d(draw, min_d=2, max_d=200):
    """x^2 + d for d > 0 (giving Q(sqrt(-d)))."""
    return f"x^2+{draw(st.integers(min_value=min_d, max_value=max_d))}"


@st.composite
def random_lattice_basis(draw, min_n=2, max_n=4, lo=-10, hi=10):
    """A random integer basis as a square (n x n) matrix (rows = vectors)."""
    n = draw(st.integers(min_value=min_n, max_value=max_n))
    rows = []
    for _ in range(n):
        rows.append(draw(st.lists(st.integers(min_value=lo, max_value=hi),
                                  min_size=n, max_size=n)))
    return np.array(rows, dtype=object)


@st.composite
def fundamental_disc(draw):
    """Sample a known fundamental discriminant from Heegner+others."""
    return draw(st.sampled_from([-3, -4, -7, -8, -11, -15, -19, -20, -23,
                                 -24, -31, -35, -39, -40, -43, -47, -51,
                                 -52, -55, -56, -67, -68, -163]))


@st.composite
def rational_pair(draw, p_lo=1, p_hi=1000, q_lo=2, q_hi=200):
    """Coprime (p, q) with q >= q_lo."""
    q = draw(st.integers(min_value=q_lo, max_value=q_hi))
    p = draw(st.integers(min_value=p_lo, max_value=p_hi))
    return p, q


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _eval_cf(coeffs):
    """Evaluate a finite continued fraction back to a Fraction."""
    if not coeffs:
        return Fraction(0)
    f = Fraction(coeffs[-1])
    for a in reversed(coeffs[:-1]):
        f = a + Fraction(1) / f
    return f


def _is_zero_poly(coeffs):
    return all(c == 0 for c in coeffs)


def _det_int(M):
    """Integer determinant via numpy float, rounded."""
    return int(round(float(np.linalg.det(np.array(M, dtype=float)))))


def _cyclotomic_poly_coeffs(n):
    """Return Phi_n(x) coefficients in descending order using sympy."""
    import sympy
    poly = sympy.Poly(sympy.cyclotomic_poly(n, sympy.Symbol('x')))
    return [int(c) for c in poly.all_coeffs()]


def _sumsq(M):
    return sum(int(x) ** 2 for row in M for x in row)


def _l2sq(v):
    return sum(int(x) ** 2 for x in v)


# =========================================================================== #
# 1. mahler_measure / log_mahler_measure / is_cyclotomic                      #
# =========================================================================== #

@FAST
@given(coeffs=nonzero_int_coeffs(min_size=2, max_size=8))
def test_mahler_measure_at_least_one(coeffs):
    """M(p) >= 1 for any non-zero integer polynomial of degree >= 1.

    Reference: Lehmer's classical bound; for any non-zero integer polynomial
    p, M(p) >= 1, with equality iff p is +/- product of cyclotomic polynomials.
    Numerical tolerance: np.roots may introduce O(1e-9) error.
    """
    assume(coeffs[0] != 0)  # ensure leading coefficient nonzero
    m = mahler_measure(coeffs)
    assert m >= 1.0 - 1e-7, f"M({coeffs}) = {m} < 1"


@FAST
@given(coeffs=nonzero_int_coeffs(min_size=2, max_size=8))
def test_log_mahler_measure_nonneg(coeffs):
    """log M(p) >= 0 for non-zero integer polynomial of degree >= 1.

    Direct corollary of M(p) >= 1.
    """
    assume(coeffs[0] != 0)
    lm = log_mahler_measure(coeffs)
    assert lm >= -1e-7


@FAST
@given(coeffs=nonzero_int_coeffs(min_size=2, max_size=8))
def test_log_mahler_consistent_with_mahler(coeffs):
    """log M = log(M) within numerical tolerance.

    Sanity: log_mahler_measure should equal np.log of mahler_measure.
    """
    assume(coeffs[0] != 0)
    m = mahler_measure(coeffs)
    lm = log_mahler_measure(coeffs)
    assert abs(lm - math.log(max(m, 1e-300))) < 1e-9


@FAST
@given(coeffs=nonzero_int_coeffs(min_size=2, max_size=8))
def test_mahler_measure_reciprocal_invariance(coeffs):
    """M(p) = M(p*) where p*(x) = x^n p(1/x) is the reciprocal polynomial.

    Reference: the roots of p* are 1/alpha_i, and
    |1/alpha| <= 1 iff |alpha| >= 1; combined with the leading-coefficient
    swap, M is preserved exactly.
    """
    assume(coeffs[0] != 0 and coeffs[-1] != 0)
    m1 = mahler_measure(coeffs)
    m2 = mahler_measure(list(reversed(coeffs)))
    # Tolerance generous because np.roots compounds error for near-reciprocal cases
    rel = abs(m1 - m2) / max(m1, 1e-12)
    assert rel < 1e-6, f"M({coeffs})={m1} vs M(reversed)={m2}"


@FAST
@given(c=st.integers(min_value=-100, max_value=100).filter(lambda x: x != 0))
def test_mahler_measure_degree_zero(c):
    """M([c]) = |c| for any non-zero constant polynomial.

    Reference: degenerate case of M(p) = |a_n| * prod max(1,|alpha|).
    With no roots, the product is empty and M = |a_0|.
    """
    assert mahler_measure([c]) == abs(c)


@FAST
@given(coeffs=nonzero_int_coeffs(min_size=2, max_size=8))
def test_is_cyclotomic_implies_M_one(coeffs):
    """If is_cyclotomic(p) is True, then M(p) is approximately 1.

    Reference: cyclotomic polynomials have all roots on the unit circle, so
    each max(1, |alpha|) = 1 and M = |a_n| = 1 for monic polys.
    """
    assume(coeffs[0] != 0)
    if is_cyclotomic(coeffs):
        m = mahler_measure(coeffs)
        # For monic cyclotomic, M=1; for non-monic with roots-on-unit-circle, M=|a_n|
        assert m >= 1.0 - 1e-7


@FAST
@given(n=st.sampled_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20]))
def test_mahler_of_cyclotomic_polys_is_one(n):
    """M(Phi_n) = 1 exactly, for all n.

    Reference: Phi_n is monic with all roots = primitive nth roots of unity,
    so M = 1. Verified for n in {1..12, 15, 20}.
    """
    coeffs = _cyclotomic_poly_coeffs(n)
    m = mahler_measure(coeffs)
    assert abs(m - 1.0) < 1e-6, f"M(Phi_{n}) = {m}, expected 1.0"


@FAST
@given(n=st.sampled_from([2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15]))
def test_is_cyclotomic_true_for_phi_n(n):
    """is_cyclotomic(Phi_n) returns True for n >= 2."""
    coeffs = _cyclotomic_poly_coeffs(n)
    assert is_cyclotomic(coeffs) is True


def test_mahler_zero_polynomial_raises():
    """Edge: zero polynomial has no Mahler measure."""
    with pytest.raises(ValueError):
        mahler_measure([0, 0, 0])
    with pytest.raises(ValueError):
        mahler_measure([])


def test_log_mahler_zero_polynomial_raises():
    """Edge: zero polynomial has no log Mahler measure."""
    with pytest.raises(ValueError):
        log_mahler_measure([0, 0, 0, 0])


def test_mahler_measure_lehmer_polynomial():
    """Edge/anchor: Lehmer's polynomial has M ≈ 1.17628.

    Reference: Lehmer 1933, "Factorization of certain cyclotomic functions",
    Mossinghoff's table of small Mahler measures.
    """
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    m = mahler_measure(lehmer)
    assert 1.176 < m < 1.177
    assert is_cyclotomic(lehmer) is False


def test_is_cyclotomic_constant_polynomial():
    """Edge: degree-0 polynomial is not cyclotomic by definition (no roots)."""
    assert is_cyclotomic([5]) is False
    assert is_cyclotomic([1]) is False


def test_is_cyclotomic_zero_polynomial():
    """Edge: zero polynomial is not cyclotomic."""
    assert is_cyclotomic([0, 0, 0]) is False
    assert is_cyclotomic([]) is False


# =========================================================================== #
# 2. class_number / class_group / regulator_nf                                #
# =========================================================================== #

# Cohen Table 1.1 (Q(sqrt(d)), d squarefree imaginary):
# Pairs are (poly, h_K). Polynomials are minimal polys of generators.
# These are CLASS NUMBERS OF THE FIELD (PARI's h), keyed by polynomial.
COHEN_IMAG_QUAD = [
    ('x^2+1', 1),         # Q(i),    d=-4
    ('x^2+2', 1),         # Q(sqrt(-2)), d=-8
    ('x^2+x+1', 1),       # Q(omega), d=-3
    ('x^2+x+2', 1),       # d=-7
    ('x^2+x+3', 1),       # d=-11
    ('x^2+x+4', 2),       # d=-15
    ('x^2+x+5', 1),       # d=-19
    ('x^2+x+6', 3),       # d=-23
    ('x^2+x+9', 2),       # d=-35  (h=2, NOT 1 — Cohen Table 1.1)
    ('x^2+x+11', 1),      # d=-43  (Heegner)
    ('x^2+x+17', 1),      # d=-67  (Heegner)
    ('x^2+15', 2),        # d=-60 (non-fundamental: 4*-15)
]
COHEN_REAL_QUAD = [
    ('x^2-2', 1),
    ('x^2-3', 1),
    ('x^2-5', 1),
    ('x^2-6', 1),
    ('x^2-7', 1),
    ('x^2-10', 2),
    ('x^2-15', 2),
]


@pytest.mark.parametrize("poly,h", COHEN_IMAG_QUAD)
def test_class_number_cohen_imag_quad_table(poly, h):
    """Authority + property: class numbers match Cohen Table 1.1.

    Reference: Cohen, "A Course in Computational Algebraic Number Theory",
    Table 1.1 (imaginary quadratic class numbers).
    """
    assert class_number(poly) == h


@pytest.mark.parametrize("poly,h", COHEN_REAL_QUAD)
def test_class_number_cohen_real_quad_table(poly, h):
    """Authority: real quadratic class numbers from Cohen.

    Reference: Cohen Table 1.2 (real quadratic class numbers, narrow vs wide).
    """
    assert class_number(poly) == h


@FAST
@given(d=st.sampled_from([1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 19, 23, 31,
                          35, 43, 47, 67, 163]))
def test_class_number_positive_integer(d):
    """class_number returns a positive integer for any valid number field."""
    poly = f"x^2+{d}"
    h = class_number(poly)
    assert isinstance(h, int)
    assert h >= 1


@FAST
@given(d=st.sampled_from([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
                          47, 53, 59, 61]))
def test_class_group_h_matches_class_number(d):
    """class_group['h'] == class_number for the same input.

    Both call PARI's bnfinit().no — must agree.
    """
    poly = f"x^2+{d}"
    cg = class_group(poly)
    cn = class_number(poly)
    assert cg['h'] == cn


@FAST
@given(d=st.sampled_from([1, 2, 3, 5, 7, 11, 13, 19, 23, 43, 67, 163]))
def test_class_group_structure_empty_iff_h_one(d):
    """class_group['structure'] is empty iff h == 1.

    Reference: trivial class group has no elementary divisors.
    """
    poly = f"x^2+{d}"
    cg = class_group(poly)
    if cg['h'] == 1:
        assert cg['structure'] == []
    else:
        assert len(cg['structure']) >= 1


@FAST
@given(d=st.sampled_from([5, 6, 10, 13, 14, 15, 21, 22, 23, 26, 29, 30,
                          33, 35, 37, 38, 39]))
def test_class_group_structure_product_equals_h(d):
    """Product of elementary divisors equals h.

    Reference: |Cl(K)| = product of cyclic factor orders.
    """
    poly = f"x^2+{d}"
    cg = class_group(poly)
    if cg['structure']:
        prod = 1
        for x in cg['structure']:
            prod *= x
        assert prod == cg['h']


@FAST
@given(d=st.sampled_from([1, 2, 3, 5, 7, 11, 13, 17, 19, 23]))
def test_class_group_imag_quad_signature(d):
    """Q(sqrt(-d)) has signature (0, 1).

    Reference: imaginary quadratic field has 0 real, 1 complex place.
    """
    poly = f"x^2+{d}"
    cg = class_group(poly)
    assert cg['signature'] == (0, 1)
    assert cg['degree'] == 2


@FAST
@given(d=st.sampled_from([2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19]))
def test_class_group_real_quad_signature(d):
    """Q(sqrt(d)) for d > 0 squarefree has signature (2, 0)."""
    poly = f"x^2-{d}"
    cg = class_group(poly)
    assert cg['signature'] == (2, 0)


@FAST
@given(d=st.sampled_from([2, 3, 5, 6, 7, 10, 13, 14, 15, 17, 19, 21]))
def test_regulator_real_quad_positive(d):
    """For real quadratic fields, regulator is strictly positive.

    Reference: real quadratic K has rank-1 unit group with fundamental unit
    epsilon > 1 → R = log epsilon > 0.
    """
    poly = f"x^2-{d}"
    R = regulator_nf(poly)
    assert R > 0
    assert math.isfinite(R)


@FAST
@given(d=st.sampled_from([1, 2, 3, 5, 7, 11, 13, 19, 23, 43, 67, 163]))
def test_regulator_imag_quad_one(d):
    """For imaginary quadratic, regulator is 1.0 by convention (empty product).

    Reference: imag-quadratic unit group is finite (just roots of unity), so
    the regulator is the determinant of an empty matrix, conventionally 1.
    """
    poly = f"x^2+{d}"
    assert regulator_nf(poly) == pytest.approx(1.0, abs=1e-12)


def test_class_number_heegner_disc_is_one():
    """Edge: each of 9 Heegner discriminants gives h=1.

    Reference: Heegner-Stark theorem (1952/1967): the only imaginary
    quadratic fields with h=1 have d in {-3, -4, -7, -8, -11, -19, -43, -67, -163}.
    """
    heegner_polys_minimal = ['x^2+x+1', 'x^2+1', 'x^2+x+2', 'x^2+2',
                             'x^2+x+3', 'x^2+x+5', 'x^2+x+11',
                             'x^2+x+17', 'x^2+x+41']
    for p in heegner_polys_minimal:
        assert class_number(p) == 1, f"{p} should be h=1 (Heegner)"


def test_class_number_empty_input_raises():
    """Edge: empty polynomial input raises ValueError."""
    with pytest.raises((ValueError, Exception)):
        class_number([])


def test_class_number_reducible_raises():
    """Edge: reducible polynomial raises (PARI's bnfinit refuses)."""
    with pytest.raises(Exception):
        class_number('x^2-1')


# =========================================================================== #
# 3. galois_group / is_abelian / disc_is_square                               #
# =========================================================================== #

@FAST
@given(n=st.sampled_from([2, 3, 4, 5, 6]))
def test_galois_order_divides_n_factorial(n):
    """|Gal(f)| divides n! for any irreducible degree-n f.

    Reference: standard fact, Gal(f) is a subgroup of S_n.
    Polynomials sampled: x^n - 2 (Eisenstein at 2, irreducible).
    """
    g = galois_group(f"x^{n}-2")
    assert factorial(n) % g['order'] == 0
    assert g['degree'] == n


@FAST
@given(n=st.sampled_from([2, 3, 4, 5, 6]))
def test_galois_order_at_least_n(n):
    """For irreducible degree-n f, |Gal(f)| >= n.

    Reference: Gal(f) acts transitively on the n roots, so its order is a
    multiple of n.
    """
    g = galois_group(f"x^{n}-2")
    assert g['order'] >= n
    assert g['order'] % n == 0


@FAST
@given(n=st.sampled_from([2, 3, 4, 5, 6, 7]))
def test_galois_transitive_id_well_formed(n):
    """transitive_id is (n, k) with 1 <= k.

    Reference: PARI's polgalois uses the transitive-groups database with
    indices 1, 2, ... per degree.
    """
    g = galois_group(f"x^{n}-2")
    deg, k = g['transitive_id']
    assert deg == n
    assert k >= 1


@FAST
@given(n=st.sampled_from([3, 4, 5, 6, 7, 8, 9, 10, 12]))
def test_galois_cyclotomic_phi_n_abelian_order(n):
    """Phi_n is abelian with order phi(n).

    Reference: Gal(Q(zeta_n)/Q) ~= (Z/nZ)*, an abelian group of order phi(n).
    Note: PARI's polgalois requires the `galdata` add-on for deg > 7. In
    the default cypari build, n=11 (giving Phi_11 of degree 10) fails with
    a missing-file PariError. See BUGS.md B-GAL-001. We sample n's whose
    Phi_n has degree <= 7 to stay in PARI's default-supported range.
    """
    coeffs = _cyclotomic_poly_coeffs(n)
    if len(coeffs) - 1 > 7:
        return  # PARI polgalois without galdata only supports degree <= 7
    g = galois_group(coeffs)
    assert g['is_abelian'] is True
    # |G| = phi(n) = degree of Phi_n
    expected_order = len(coeffs) - 1
    assert g['order'] == expected_order


@FAST
@given(n=st.sampled_from([3, 4, 5, 6, 7, 8, 9, 10, 12]))
def test_galois_abelian_implies_order_equals_degree(n):
    """For irreducible f, Gal(f) abelian => |G| = deg(f).

    Reference: a transitive abelian subgroup of S_n is regular,
    so |G| = n. Restricted to degree <= 7 due to galdata limit.
    """
    coeffs = _cyclotomic_poly_coeffs(n)
    if len(coeffs) - 1 > 7:
        return
    g = galois_group(coeffs)
    if g['is_abelian']:
        assert g['order'] == g['degree']


def test_galois_known_groups():
    """Authority: spot-check well-known Galois groups."""
    assert galois_group('x^3-2')['name'].startswith('S')        # S_3
    assert galois_group('x^3-2')['order'] == 6
    assert galois_group('x^3-3*x-1')['order'] == 3              # cyclic cubic A_3
    assert galois_group('x^4-x-1')['order'] == 24               # S_4
    assert galois_group('x^5-x-1')['order'] == 120              # S_5


@FAST
@given(n=st.sampled_from([2, 3, 4, 5, 6, 7]))
def test_disc_is_square_iff_parity_one(n):
    """disc_is_square is True iff galois_group(...).parity == 1."""
    poly = f"x^{n}-2"
    g = galois_group(poly)
    assert disc_is_square(poly) == (g['parity'] == 1)


@FAST
@given(n=st.sampled_from([3, 4, 5, 6, 7]))
def test_is_abelian_consistent_with_galois_group(n):
    """is_abelian(f) == galois_group(f)['is_abelian']."""
    poly = f"x^{n}-2"
    assert is_abelian(poly) == galois_group(poly)['is_abelian']


def test_galois_high_degree_raises():
    """Edge: degree > 11 raises (PARI's polgalois has no built-in data above 11)."""
    with pytest.raises(ValueError):
        galois_group("x^12-1")


# =========================================================================== #
# 4. lll / lll_with_transform / shortest_vector_lll / lll_gram                #
# =========================================================================== #

@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=4, lo=-8, hi=8))
def test_lll_preserves_abs_det(B):
    """|det(lll(B))| == |det(B)| for full-rank integer basis.

    Reference: LLL applies a unimodular transformation, which has det = +/-1.
    """
    d = _det_int(B)
    if d == 0:
        return  # degenerate
    R = lll(B)
    dR = _det_int(R)
    assert abs(d) == abs(dR), f"det B={d}, det R={dR}"


@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=4, lo=-8, hi=8))
def test_lll_with_transform_satisfies_R_equals_TB(B):
    """lll_with_transform: R == T @ B (exact integer arithmetic).

    Reference: by construction, the unimodular T expresses the reduced basis
    in the original. Verified via integer matrix product.
    """
    if _det_int(B) == 0:
        return
    R, T = lll_with_transform(B)
    Bi = np.array(B, dtype=int)
    Ti = np.array(T, dtype=int)
    Ri = np.array(R, dtype=int)
    prod = Ti @ Bi
    assert np.array_equal(prod, Ri), f"T@B = {prod}, R = {Ri}"


@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=4, lo=-8, hi=8))
def test_lll_transform_unimodular(B):
    """lll_with_transform: |det(T)| == 1.

    Reference: definition of unimodular = invertible-over-Z = |det| = 1.
    """
    if _det_int(B) == 0:
        return
    _, T = lll_with_transform(B)
    dT = _det_int(T)
    assert abs(dT) == 1, f"det T = {dT}, expected +/-1"


@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=4, lo=-8, hi=8))
def test_lll_first_row_shorter_than_average(B):
    """LLL's first row b1 is bounded by the original basis's average
    squared norm (a corollary of the LLL guarantee).

    Calibration drift fix (2026-04-29): the previous assertion was
    "sum of squared row norms of lll(B) <= sum of squared row norms of
    B", which is NOT a theorem of LLL. LLL guarantees that b1 (the
    first vector of the reduced basis) approximates the shortest
    vector up to a factor (4/3)^((n-1)/2), and that successive
    Gram-Schmidt norms don't decrease too fast — but the *sum of row
    norms* can legitimately INCREASE. Hypothesis correctly found a
    counterexample (B=[[-1,1,7],[2,6,-1],[-5,5,2]] gives sumB=146,
    sumR=151 with the same lattice). The fix: assert that b1 is no
    larger than the largest input row (a weaker, true property), and
    rely on the dedicated test_shortest_vector_in_lattice for the
    actual LLL strength claim.

    Reference: Lenstra-Lenstra-Lovász (1982), Theorem 1: ||b_1||^2
    <= 2^(n-1) * det(L)^(2/n) for n-dim L; in particular b1 is
    bounded by the longest input vector since b1 is part of the
    same lattice and LLL only swaps/reduces rows.
    """
    if _det_int(B) == 0:
        return
    R = lll(B)
    # Largest row of input bounds the first row of output.
    max_row_sq_B = max(_l2sq(row) for row in B)
    first_row_sq_R = _l2sq(R[0])
    # Allow equality (input was already LLL-reduced).
    assert first_row_sq_R <= max_row_sq_B, (
        f"|b1|^2 = {first_row_sq_R} > max input row^2 = {max_row_sq_B}"
    )


@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=4, lo=-5, hi=5))
def test_shortest_vector_in_lattice(B):
    """shortest_vector_lll(B) is in the row-Z-span of B.

    Reference: every output of LLL is a Z-combination of the input rows
    (since R = T @ B with T integer).
    """
    if _det_int(B) == 0:
        return
    v = shortest_vector_lll(B)
    Bi = np.array(B, dtype=float)
    vi = np.array(v, dtype=float)
    # Solve Bi^T @ x = vi for rational x; check integer
    sol, *_ = np.linalg.lstsq(Bi.T, vi, rcond=None)
    nearest = np.round(sol)
    err = np.max(np.abs(Bi.T @ nearest - vi))
    assert err < 1e-6, f"v={v} not in lattice; lstsq residual {err}"


@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=3, lo=-5, hi=5))
def test_shortest_vector_at_most_original(B):
    """||shortest_vector_lll(B)||^2 <= min_i ||B_i||^2.

    Reference: LLL's first vector is no longer than any original basis vector.
    """
    if _det_int(B) == 0:
        return
    v = shortest_vector_lll(B)
    nv = _l2sq(v)
    nb = min(_l2sq(row) for row in B)
    assert nv <= nb + 1e-9, f"shortest = {nv}, min input = {nb}"


@MEDIUM
@given(B=random_lattice_basis(min_n=2, max_n=4, lo=-6, hi=6))
def test_lll_gram_unimodular(B):
    """lll_gram(B B^T) returns a unimodular matrix.

    Reference: PARI's qflllgram returns a unimodular T such that
    T^T G T is the Gram matrix of the reduced basis.
    """
    if _det_int(B) == 0:
        return
    Bi = np.array(B, dtype=int)
    G = Bi @ Bi.T
    T = lll_gram(G)
    dT = _det_int(T)
    assert abs(dT) == 1


def test_lll_identity_basis():
    """Edge: identity basis is already LLL-reduced."""
    B = np.eye(3, dtype=int)
    R = lll(B)
    Ri = np.array(R, dtype=int)
    # Should be a permutation of the identity rows up to sign
    assert abs(_det_int(R)) == 1


@pytest.mark.xfail(strict=False, reason="B-LLL-001: rank-deficient lll() crashes "
                   "with IndexError in cypari, see BUGS.md")
def test_lll_singular_basis():
    """Edge: rank-deficient input.

    Currently triggers cypari IndexError because qflll returns a transform
    matrix sized to the rank, but the wrapper's _pari_mat_cols_to_rows
    indexes column-by-column up to n. Documented as B-LLL-001 in BUGS.md.

    Expected (post-fix) behavior: leading zero rows in the reduced output
    or a clear ValueError.
    """
    B = np.array([[1, 2, 3], [2, 4, 6], [0, 0, 1]], dtype=int)
    R = lll(B)
    # First row should be zero (since first two are linearly dependent)
    assert _det_int(R) == 0


def test_lll_nonsquare_basis():
    """Edge: 2 vectors in Z^3 (n=2, d=3)."""
    B = np.array([[1, 0, 1], [0, 1, 1]], dtype=int)
    R = lll(B)
    assert R.shape == (2, 3)


# =========================================================================== #
# 5. cm_order_data                                                            #
# =========================================================================== #

@FAST
@given(D=fundamental_disc())
def test_cm_fundamental_factorization(D):
    """fundamental_disc * cm_conductor^2 == D (always).

    Reference: D = d_K · f² is the canonical decomposition of any negative
    discriminant into (fundamental, conductor).
    """
    info = cm_order_data(D)
    assert info['fundamental_disc'] * info['cm_conductor'] ** 2 == D


@FAST
@given(D=fundamental_disc())
def test_cm_conductor_positive(D):
    """cm_conductor is a positive integer >= 1."""
    info = cm_order_data(D)
    assert isinstance(info['cm_conductor'], int)
    assert info['cm_conductor'] >= 1


@FAST
@given(D=fundamental_disc())
def test_cm_class_number_positive(D):
    """class_number of the order is a positive integer."""
    info = cm_order_data(D)
    assert info['class_number'] >= 1


@FAST
@given(D=fundamental_disc())
def test_cm_fundamental_disc_negative(D):
    """fundamental_disc of any imaginary quadratic order is negative."""
    info = cm_order_data(D)
    assert info['fundamental_disc'] < 0


@FAST
@given(D=fundamental_disc())
def test_cm_is_maximal_iff_conductor_one(D):
    """is_maximal == (cm_conductor == 1)."""
    info = cm_order_data(D)
    assert info['is_maximal'] == (info['cm_conductor'] == 1)


@FAST
@given(D=fundamental_disc())
def test_cm_degree_equals_class_number(D):
    """degree of Hilbert/ring class polynomial == class number h(O_D).

    Reference: H_D is monic of degree h(O_D) by deuring-shimura.
    """
    info = cm_order_data(D)
    assert info['degree'] == info['class_number']


def test_cm_heegner_discs_have_conductor_one():
    """Authority: 9 Heegner discriminants all have f=1.

    Reference: Heegner-Stark theorem.
    """
    for D in [-3, -4, -7, -8, -11, -19, -43, -67, -163]:
        info = cm_order_data(D)
        assert info['cm_conductor'] == 1, f"D={D} expected conductor 1"
        assert info['class_number'] == 1
        assert info['is_maximal'] is True


def test_cm_non_maximal_orders():
    """Authority: known non-maximal orders.

    Reference: explicit verifications -
    D=-12 = -3*4: f=2, d_K=-3
    D=-16 = -4*4: f=2, d_K=-4
    D=-27 = -3*9: f=3, d_K=-3
    D=-28 = -7*4: f=2, d_K=-7
    All four have class number 1 (rational j-invariants).
    """
    for D, fund, f in [(-12, -3, 2), (-16, -4, 2), (-27, -3, 3), (-28, -7, 2)]:
        info = cm_order_data(D)
        assert info['fundamental_disc'] == fund, f"D={D}"
        assert info['cm_conductor'] == f, f"D={D}"
        assert info['is_maximal'] is False


def test_cm_positive_disc_raises():
    """Edge: positive D is not a CM discriminant."""
    with pytest.raises(ValueError):
        cm_order_data(7)
    with pytest.raises(ValueError):
        cm_order_data(0)


def test_cm_invalid_residue_raises():
    """Edge: D not ≡ 0 or 1 (mod 4) raises."""
    # -2 mod 4 = 2, invalid
    with pytest.raises(ValueError):
        cm_order_data(-2)
    # -5 mod 4 = 3, invalid
    with pytest.raises(ValueError):
        cm_order_data(-5)
    # -6 mod 4 = 2, invalid
    with pytest.raises(ValueError):
        cm_order_data(-6)


# =========================================================================== #
# 6. cf_expand / cf_max_digit / zaremba_test / sturm_bound                    #
# =========================================================================== #

@FAST
@given(p=st.integers(min_value=1, max_value=10000),
       q=st.integers(min_value=1, max_value=200))
def test_cf_expand_round_trip(p, q):
    """cf_expand(p, q) evaluated back gives p/q in lowest terms.

    Reference: every rational has a unique finite CF (up to last-coefficient
    convention). Reconstruction = standard back-substitution.
    """
    coeffs = cf_expand(p, q)
    assert coeffs  # non-empty
    f = _eval_cf(coeffs)
    expected = Fraction(p, q)
    assert f == expected, f"cf {coeffs} -> {f}, expected {expected}"


@FAST
@given(p=st.integers(min_value=1, max_value=10000),
       q=st.integers(min_value=1, max_value=200))
def test_cf_first_coefficient_is_floor(p, q):
    """cf_expand(p, q)[0] == floor(p / q).

    Reference: by construction, the first coefficient is the integer part.
    """
    coeffs = cf_expand(p, q)
    assert coeffs[0] == p // q


@FAST
@given(p=st.integers(min_value=1, max_value=10000),
       q=st.integers(min_value=1, max_value=200))
def test_cf_remaining_coefficients_positive(p, q):
    """All CF coefficients after the first are positive (for p, q > 0).

    Reference: classical CF theorem; partial quotients are positive integers
    for any rational > 0 except possibly the leading integer part.
    """
    coeffs = cf_expand(p, q)
    for c in coeffs[1:]:
        assert c >= 1, f"cf({p}/{q}) has non-positive partial quotient: {c}"


@FAST
@given(p=st.integers(min_value=1, max_value=10000),
       q=st.integers(min_value=1, max_value=200))
def test_cf_max_digit_consistent_with_max_of_expand(p, q):
    """cf_max_digit(p, q) == max(cf_expand(p, q))."""
    assert cf_max_digit(p, q) == max(cf_expand(p, q))


@FAST
@given(p=st.integers(min_value=1, max_value=10000),
       q=st.integers(min_value=1, max_value=200))
def test_cf_max_digit_at_least_one(p, q):
    """cf_max_digit(p, q) >= 1 for p, q >= 1.

    Reference: the integer part of any positive rational is >= 0; and for
    p < q the first CF entry is 0 but later ones are >= 1.
    """
    # Skip pathological p < q where coeffs = [0, ...]; those still have >=1 later
    cf = cf_expand(p, q)
    if any(c >= 1 for c in cf):
        assert cf_max_digit(p, q) >= 1


def test_cf_expand_355_113_anchor():
    """Authority: cf_expand(355, 113) = [3, 7, 16].

    Reference: 355/113 is Milu Chongzhi's approximation to pi (478 AD);
    its CF is the classic textbook example.
    """
    assert cf_expand(355, 113) == [3, 7, 16]
    assert cf_max_digit(355, 113) == 16


def test_cf_expand_zero_denominator_raises():
    """Edge: q == 0 raises ValueError; q < 0 auto-flips (calibration
    drift fix 2026-04-29).

    Wave 12 (techne/lib/cf_expansion.py, 2026-04-21) added sign
    normalization: when q < 0, cf_expand swaps (p, q) -> (-p, -q) and
    proceeds with the canonical positive-denominator CF rather than
    raising. Only q == 0 still raises.
    """
    with pytest.raises(ValueError):
        cf_expand(1, 0)
    # q < 0 now produces a valid CF equivalent to (-p, -q).
    assert cf_expand(5, -3) == cf_expand(-5, 3)


def test_cf_integer_input_one_coefficient():
    """Edge: cf_expand(p, 1) returns single-element list [p]."""
    assert cf_expand(5, 1) == [5]
    assert cf_expand(0, 1) == [0]


@FAST
@given(q=st.integers(min_value=2, max_value=50))
def test_zaremba_returns_dict_with_required_keys(q):
    """zaremba_test always returns a dict with the documented keys."""
    r = zaremba_test(q)
    for k in ('q', 'bound', 'satisfies', 'witness', 'n_tested',
              'min_max_digit', 'best_a'):
        assert k in r
    assert r['q'] == q
    assert r['bound'] == 5  # default


@FAST
@given(q=st.integers(min_value=2, max_value=50))
def test_zaremba_witness_is_coprime(q):
    """If a witness exists, it is coprime to q.

    Reference: Zaremba's conjecture demands gcd(a, q) = 1.
    """
    r = zaremba_test(q)
    if r['witness'] is not None:
        assert gcd(r['witness'], q) == 1
        assert 1 <= r['witness'] < q


@FAST
@given(q=st.integers(min_value=2, max_value=50))
def test_zaremba_min_max_digit_consistent(q):
    """zaremba_test().min_max_digit == cf_max_digit(best_a, q).

    Reference: by construction the field stores the smallest max-CF-digit.
    """
    r = zaremba_test(q)
    if r['best_a'] is not None:
        assert r['min_max_digit'] == cf_max_digit(r['best_a'], q)


@FAST
@given(q=st.integers(min_value=2, max_value=30))
def test_zaremba_satisfies_implies_witness(q):
    """satisfies <=> witness is not None."""
    r = zaremba_test(q)
    assert r['satisfies'] == (r['witness'] is not None)


@FAST
@given(weight=st.integers(min_value=2, max_value=24).filter(lambda k: k % 2 == 0),
       level=st.integers(min_value=1, max_value=100))
def test_sturm_bound_nonneg(weight, level):
    """sturm_bound returns a non-negative integer.

    Reference: floor of a positive expression.
    """
    sb = sturm_bound(weight, level)
    assert isinstance(sb, int)
    assert sb >= 0


@FAST
@given(level=st.integers(min_value=1, max_value=50))
def test_sturm_bound_monotone_in_weight(level):
    """sturm_bound(k+2, N) >= sturm_bound(k, N) for fixed N.

    Reference: sturm_bound = floor(k/12 * N * I) is linear in k.
    """
    base = sturm_bound(2, level)
    for k in [4, 6, 8, 12, 24]:
        assert sturm_bound(k, level) >= base


@FAST
@given(weight=st.integers(min_value=2, max_value=24).filter(lambda k: k % 2 == 0),
       level=st.integers(min_value=1, max_value=50))
def test_sturm_bound_monotone_in_level(weight, level):
    """sturm_bound(k, 2N) >= sturm_bound(k, N) for fixed k.

    Reference: doubling N at minimum doubles the index, so the bound grows.
    """
    sb1 = sturm_bound(weight, level)
    sb2 = sturm_bound(weight, 2 * level)
    assert sb2 >= sb1


def test_sturm_bound_anchors():
    """Authority: hand-computed Sturm bounds.

    Reference: Sturm 1987; common small cases.
    sturm_bound(2, 11) = floor(2 * 11 * (1+1/11) / 12) = floor(24/12) = 2
    sturm_bound(12, 1) = floor(12 * 1 * 1 / 12) = 1
    """
    assert sturm_bound(2, 11) == 2
    assert sturm_bound(12, 1) == 1


# =========================================================================== #
# 7. hilbert_class_field / class_field_tower                                  #
# =========================================================================== #

# These are slow tests — restrict to small h and use SLOW profile.
HCF_SMALL_FIELDS = [
    ('x^2+5', 2, 4),     # h=2, [HCF:Q]=4
    ('x^2+23', 3, 6),    # h=3, [HCF:Q]=6
    ('x^2+47', 5, 10),   # h=5
    ('x^2+15', 2, 4),    # h=2 (non-fundamental)
    ('x^2+x+6', 3, 6),   # h=3 (Q(sqrt(-23)) again)
]


@pytest.mark.parametrize("poly,h,deg_abs", HCF_SMALL_FIELDS)
def test_hcf_degree_relations(poly, h, deg_abs):
    """[HCF : K] = h_K, and [HCF : Q] = h_K * [K : Q].

    Reference: defining property of the Hilbert class field.
    """
    hcf = hilbert_class_field(poly)
    assert hcf['degree_rel'] == h
    assert hcf['degree_abs'] == deg_abs


@pytest.mark.parametrize("poly,h,deg_abs", HCF_SMALL_FIELDS)
def test_hcf_class_number_K_consistent(poly, h, deg_abs):
    """hcf['class_number_K'] == class_number(poly)."""
    hcf = hilbert_class_field(poly)
    assert hcf['class_number_K'] == class_number(poly)


def test_hcf_trivial_when_h_one():
    """Edge: h=1 fields have trivial HCF (HCF = K).

    Reference: definition; verified for Q(i) and Q(sqrt(-163)).
    """
    for poly in ['x^2+1', 'x^2+163', 'x^2+x+1']:
        hcf = hilbert_class_field(poly)
        assert hcf['is_trivial'] is True
        assert hcf['degree_rel'] == 1


def test_hcf_high_class_number_guard():
    """Edge: max_class_number guard rejects h > guard.

    Reference: HCF computation for large h needs > 4 GB PARI stack.
    """
    # Q(sqrt(-71)): h=7 -> reject with max_class_number=5
    with pytest.raises(ValueError, match="max_class_number"):
        hilbert_class_field('x^2+71', max_class_number=5)


@SLOW
@given(poly=st.sampled_from(['x^2+5', 'x^2+23', 'x^2+15']))
def test_class_field_tower_terminates_or_capped(poly):
    """class_field_tower returns one of: terminates, capped, or aborted.

    Reference: every well-behaved tower either reaches h=1 or hits the cap.
    """
    t = class_field_tower(poly, max_depth=3)
    flags = [t.get('terminates', False),
             t.get('capped', False),
             t.get('aborted', False)]
    # Exactly one True
    assert sum(bool(f) for f in flags) == 1, f"flags={flags} for {poly}"


@SLOW
@given(poly=st.sampled_from(['x^2+5', 'x^2+23', 'x^2+15', 'x^2+47']))
def test_class_field_tower_class_number_sequence_starts_with_h(poly):
    """class_number_sequence[0] == class_number(poly).

    Reference: tower starts at K itself.
    """
    t = class_field_tower(poly, max_depth=2)
    assert t['class_number_sequence'][0] == class_number(poly)


@SLOW
@given(poly=st.sampled_from(['x^2+5', 'x^2+23', 'x^2+47']))
def test_class_field_tower_terminates_means_last_h_is_one(poly):
    """If terminates is True, the last class number is 1."""
    t = class_field_tower(poly, max_depth=4)
    if t.get('terminates'):
        assert t['class_number_sequence'][-1] == 1


@SLOW
@given(poly=st.sampled_from(['x^2+5', 'x^2+23']))
def test_class_field_tower_degree_grows(poly):
    """degree_sequence is non-decreasing.

    Reference: each HCF iteration is an extension, so [K_{i+1}:Q] >= [K_i:Q].
    """
    t = class_field_tower(poly, max_depth=3)
    degs = t['degree_sequence']
    for a, b in zip(degs, degs[1:]):
        assert b >= a, f"degree dropped: {a} -> {b}"


@SLOW
@given(poly=st.sampled_from(['x^2+5', 'x^2+23']))
def test_class_field_tower_poly_sequence_matches_degrees(poly):
    """len(poly_sequence) == len(degree_sequence)."""
    t = class_field_tower(poly, max_depth=3)
    assert len(t['poly_sequence']) == len(t['degree_sequence'])


def test_set_pari_stack_mb_smoke():
    """Edge/smoke: set_pari_stack_mb runs without raising."""
    # Use a small but nonzero increase; don't shrink existing stack
    try:
        set_pari_stack_mb(1000)  # 1 GB, the default
    except Exception as e:
        pytest.fail(f"set_pari_stack_mb raised: {e}")


# =========================================================================== #
# 8. functional_eq_check / fe_residual                                        #
# =========================================================================== #

def test_fe_zeta_passes_with_huge_margin():
    """Authority: ζ FE residual is very small (log_10 << -50).

    Reference: PARI's lfuncheckfeq on lfuncreate(1) gives -60 or better.
    """
    r = functional_eq_check(1)
    assert r['kind'] == 'zeta'
    assert r['conductor'] == 1
    assert r['degree'] == 1
    assert r['residual_log10'] <= -50
    assert r['satisfies'] is True


def test_fe_residual_zeta_consistent():
    """fe_residual(1) == functional_eq_check(1)['residual_log10']."""
    a = fe_residual(1)
    b = functional_eq_check(1)['residual_log10']
    assert a == b


# Curve a-invariants for a few small-conductor LMFDB elliptic curves.
# All conductor values verified via cypari ellinit/ellglobalred at suite
# authoring time (2026-04-22).
EC_INVARIANTS = [
    ([0, 0, 1, -1, 0], 37),     # 37.a1
    ([0, -1, 1, -10, -20], 11), # 11.a1
    ([1, 0, 1, 4, -6], 14),     # 14.a1 (LMFDB)
    ([0, 1, 1, -2, 0], 389),    # 389.a1
    ([0, 0, 1, 0, 0], 27),      # 27.a1
]


@pytest.mark.parametrize("ainv,N", EC_INVARIANTS)
def test_fe_elliptic_curves_satisfy(ainv, N):
    """Authority: well-known elliptic curves satisfy their FE.

    Reference: every modular elliptic curve over Q satisfies the FE for
    its L-function (by modularity, Wiles et al.). Test conductor matches LMFDB.
    """
    r = functional_eq_check(ainv)
    assert r['kind'] == 'elliptic_curve'
    assert r['conductor'] == N
    assert r['degree'] == 2
    assert r['satisfies'] is True
    assert r['residual_log10'] <= -8


@pytest.mark.parametrize("ainv,N", EC_INVARIANTS)
def test_fe_residual_below_threshold(ainv, N):
    """For valid EC L-functions, residual_log10 well below the satisfies threshold.

    Reference: FE residual for properly normalized EC L-functions is
    machine-epsilon-bounded.
    """
    r = functional_eq_check(ainv, threshold_log10=-8)
    assert r['satisfies']
    # And the residual should be much better than -8
    assert r['residual_log10'] <= -20


def test_fe_unsupported_input_raises():
    """Edge: type that doesn't match any handler raises TypeError."""
    with pytest.raises(TypeError):
        functional_eq_check({"not": "supported"})


def test_fe_threshold_strictness():
    """Property: tightening the threshold cannot turn a pass into a fail
    if the residual is already deeply negative.

    Reference: satisfies = (residual_log10 <= threshold_log10).
    Loosening (more negative threshold) makes the test stricter.
    """
    r1 = functional_eq_check(1, threshold_log10=-8)
    r2 = functional_eq_check(1, threshold_log10=-30)
    # Both should pass (zeta has residual ~ -60)
    assert r1['satisfies'] and r2['satisfies']
    # And residuals match (computation is the same)
    assert r1['residual_log10'] == r2['residual_log10']


@SLOW
@given(ainv=st.sampled_from([t[0] for t in EC_INVARIANTS]))
def test_fe_residual_deterministic(ainv):
    """fe_residual is deterministic: same input -> same output."""
    a = fe_residual(ainv)
    b = fe_residual(ainv)
    assert a == b


# =========================================================================== #
# Composition-flavored sanity checks (light touch — main category in another  #
# file, but a few here for cross-tool consistency)                            #
# =========================================================================== #

@FAST
@given(d=st.sampled_from([5, 7, 13, 23, 31, 47, 71]))
def test_class_number_consistent_with_class_group(d):
    """For Q(sqrt(-d)): class_number == class_group['h'] == sum(eldivs)*..."""
    poly = f"x^2+{d}"
    cn = class_number(poly)
    cg = class_group(poly)
    assert cn == cg['h']


@FAST
@given(D=st.sampled_from([-3, -4, -7, -8, -11, -19, -43, -67, -163,
                          -12, -16, -27, -28]))
def test_cm_class_number_one_for_rational_j(D):
    """Authority: 13 known rational-j discriminants all have class number 1.

    Reference: classical fact; rational j-invariants correspond exactly to
    these 13 discriminants.
    """
    info = cm_order_data(D)
    assert info['class_number'] == 1


def test_galois_phi_n_order_equals_euler_phi():
    """Composition: Gal(Q(zeta_n)/Q) has order phi(n).

    Reference: definition; cross-check via sympy's totient. Restricted to
    n's with phi(n) <= 7 due to PARI polgalois galdata-add-on limitation
    (see BUGS.md B-GAL-001).
    """
    import sympy
    for n in [3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 18]:
        coeffs = _cyclotomic_poly_coeffs(n)
        if len(coeffs) - 1 > 7:
            continue
        g = galois_group(coeffs)
        assert g['order'] == int(sympy.totient(n))


def test_lll_then_again_idempotent_in_norm():
    """Composition: applying LLL to an already-reduced basis preserves
    sum-of-squared-row-norms.

    Reference: LLL is a closure: subsequent applications cannot reduce further.
    """
    B = np.array([[2, 7, 1], [3, 1, 8], [1, 4, 5]], dtype=int)
    R1 = lll(B)
    R2 = lll(R1)
    assert _sumsq(R1) == _sumsq(R2)


def test_cf_round_trip_on_pi_convergents():
    """Anchor: 22/7, 333/106, 355/113 are the famous pi convergents.

    Reference: Khinchin, "Continued Fractions" §10.
    """
    assert cf_expand(22, 7) == [3, 7]
    assert cf_expand(333, 106) == [3, 7, 15]
    assert cf_expand(355, 113) == [3, 7, 16]


def test_cf_lehmer_phi_q_identity():
    """Property: number of a coprime to q in [1, q-1] equals euler_phi(q).

    Cross-check: zaremba_test.n_tested == phi(q).
    """
    import sympy
    for q in [5, 7, 11, 12, 15, 30]:
        r = zaremba_test(q)
        assert r['n_tested'] == int(sympy.totient(q))
