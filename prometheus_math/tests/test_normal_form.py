"""Tests for ``prometheus_math.algebraic_geometry_normal_form``.

Covers the math-tdd four-category gate:

- Authority (5+): hand-computed reductions cited inline (e.g.,
  ``x^3 + 2x^2 + 1`` mod ``x^2+1``), Cox--Little--O'Shea Example
  2.7.2 for ``reduced_groebner``.
- Property (5+): uniqueness, idempotence, linearity, ideal-membership
  iff zero remainder, ``g_i in I`` for all generators.
- Edge (5+): zero polynomial, empty basis, constant ideal, empty ring,
  variables outside the ring.
- Composition (4+): ``is_in_ideal == (NF == 0)``, certificate
  reconstruction recovers ``f``, NF after ``reduced_groebner``,
  zero-dim quotient-ring representation.
"""
from __future__ import annotations

import pytest
import sympy
from hypothesis import given, settings, strategies as st
from sympy import Poly, symbols

from prometheus_math.algebraic_geometry_normal_form import (
    canonical_form,
    ideal_membership_certificate,
    is_in_ideal,
    normal_form,
    reduce_polynomial_step,
    reduced_groebner,
)

x, y, z = symbols("x y z")


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------

def test_authority_xy_in_ideal_x_y_reduces_to_zero():
    """``NF(xy, [x, y]) == 0`` because ``xy = y*x + 0`` and ``LT(xy)``
    is divisible by ``x``.

    Hand-computation: ``xy`` has leading term ``x*y``, divisible by
    ``LT(x) = x``; multiplier ``y``; ``xy - y*x = 0``. Reference: Cox,
    Little, O'Shea, *Ideals, Varieties, and Algorithms* 4e, §2.3.
    """
    r = normal_form(x * y, [x, y], [x, y])
    assert r.is_zero


def test_authority_unit_circle_xsquare_plus_ysquare():
    """In ``Q[x,y] / (x^2+y^2-1)``, ``NF(x^2+y^2) == 1``.

    Hand-computation: ``x^2+y^2 = 1*(x^2+y^2-1) + 1``. Reference:
    parameterising the unit circle (textbook AG example).
    """
    r = normal_form(x**2 + y**2, [x**2 + y**2 - 1], [x, y])
    assert r.as_expr() == 1


def test_authority_unit_circle_xsquare_alone():
    """``NF(x^2, [x^2+y^2-1]) == 1 - y^2``.

    Hand-computation: ``x^2 = 1*(x^2+y^2-1) + (1 - y^2)``; the
    multiplier is ``1`` (lex order, leading term ``x^2``).
    """
    r = normal_form(x**2, [x**2 + y**2 - 1], [x, y])
    assert (r.as_expr() - (1 - y**2)).expand() == 0


def test_authority_x3_2x2_1_mod_x2_plus_1():
    """``f = x^3 + 2x^2 + 1 mod (x^2+1)``: hand-computed remainder ``-x - 1``,
    so ``f`` is **not** in the ideal ``(x^2+1)``.

    Hand-computation:
        x^3 + 2x^2 + 1 = x*(x^2+1) - x + 2x^2 + 1
                      = x*(x^2+1) + 2*(x^2+1) - x - 2 + 1
                      = (x+2)*(x^2+1) - x - 1.
    So the cofactor is ``x+2`` and the remainder is ``-x-1``.
    """
    r = normal_form(x**3 + 2*x**2 + 1, [x**2 + 1], [x])
    assert (r.as_expr() - (-x - 1)).expand() == 0
    assert not is_in_ideal(x**3 + 2*x**2 + 1, [x**2 + 1], [x])


def test_authority_cox_little_oshea_example_lex_groebner():
    """Reduced lex Groebner basis of ``<x^2-y, xy-z, y^2-z^2>`` matches
    SymPy's :func:`groebner` output.

    Reference: Cox, Little, O'Shea Ch. 2 §7 Example 2 / Lazard staircase
    computation. We cross-check against an independent SymPy call.
    """
    G = reduced_groebner([x**2 - y, x*y - z, y**2 - z**2], [x, y, z])
    expected = list(sympy.groebner([x**2 - y, x*y - z, y**2 - z**2], x, y, z, order="lex", polys=True))
    assert [g.as_expr() for g in G] == [g.as_expr() for g in expected]
    # Non-trivial: contains a univariate-in-z generator (the
    # elimination ideal). For this system, that's ``z^4 - z^2``.
    z_only = [g for g in G if g.as_expr().free_symbols == {z}]
    assert len(z_only) >= 1


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------

def test_property_normal_form_idempotent():
    """``NF(NF(f, G), G) == NF(f, G)``."""
    G = reduced_groebner([x**2 - y, x*y - z, y**2 - z**2], [x, y, z])
    f = x**3 + 2*x*y + z**2 + 7
    r = normal_form(f, G, [x, y, z])
    rr = normal_form(r, G, [x, y, z])
    assert (r.as_expr() - rr.as_expr()).expand() == 0


def test_property_normal_form_linearity_in_quotient():
    """``NF(f + g) == NF(NF(f) + NF(g))`` mod the ideal."""
    G = reduced_groebner([x**2 - y, x*y - z], [x, y, z])
    f = x**3 + y
    g = x*y + z**2
    rf = normal_form(f, G, [x, y, z])
    rg = normal_form(g, G, [x, y, z])
    rfg = normal_form(f + g, G, [x, y, z])
    rsum = normal_form(rf.as_expr() + rg.as_expr(), G, [x, y, z])
    assert (rfg.as_expr() - rsum.as_expr()).expand() == 0


def test_property_basis_elements_are_in_ideal():
    """For every ``g_i`` in a Groebner basis ``G``, ``g_i in <G>``."""
    G = reduced_groebner([x**2 - y, x*y - z, y**2 - z**2], [x, y, z])
    for g in G:
        assert is_in_ideal(g, G, [x, y, z])
        assert normal_form(g, G, [x, y, z]).is_zero


def test_property_product_reduction_in_quotient_ring():
    """``NF(f * g) == NF(NF(f) * NF(g))`` (multiplicative compatibility
    of the canonical projection ``k[x] -> k[x]/I``).
    """
    G = reduced_groebner([x**2 + y**2 - 1], [x, y])
    f = x**3 + y
    g = x + y**2
    rf = normal_form(f, G, [x, y])
    rg = normal_form(g, G, [x, y])
    rfg = normal_form(f * g, G, [x, y])
    direct = normal_form(rf.as_expr() * rg.as_expr(), G, [x, y])
    assert (rfg.as_expr() - direct.as_expr()).expand() == 0


def test_property_uniqueness_of_normal_form():
    """``NF(f, G)`` is independent of the order in which ``G`` is
    presented, so long as ``G`` is a Groebner basis (Cox 2 §6 Cor. 2).
    """
    G = reduced_groebner([x**2 - y, x*y - z, y**2 - z**2], [x, y, z])
    f = x**3 * y + 5*z**2 + x
    r1 = normal_form(f, list(G), [x, y, z])
    r2 = normal_form(f, list(reversed(G)), [x, y, z])
    assert (r1.as_expr() - r2.as_expr()).expand() == 0


@settings(deadline=None, max_examples=15)
@given(
    a=st.integers(min_value=-5, max_value=5),
    b=st.integers(min_value=-5, max_value=5),
    c=st.integers(min_value=-5, max_value=5),
)
def test_property_hypothesis_idempotent_random(a, b, c):
    """Idempotence of ``NF`` over a random small polynomial."""
    G = [x**2 - y, x*y - z]
    f = a*x**2 + b*x*y + c*z + 1
    r = normal_form(f, G, [x, y, z])
    rr = normal_form(r, G, [x, y, z])
    assert (r.as_expr() - rr.as_expr()).expand() == 0


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_zero_polynomial():
    """``NF(0, G) == 0`` for any basis."""
    r = normal_form(0, [x**2 + y**2 - 1], [x, y])
    assert r.is_zero


def test_edge_empty_basis_returns_f():
    """``NF(f, []) == f`` (no reduction possible)."""
    r = normal_form(x**3 + 1, [], [x])
    assert (r.as_expr() - (x**3 + 1)).expand() == 0


def test_edge_constant_basis_constant_input():
    """``NF(c, [c]) == 0``; ``NF(c, [d]) == c`` when ``c, d`` distinct.

    Hand-computation: a constant ``c`` lies in ``(c)`` iff ``c`` is
    actually the same constant; otherwise ``LT(c)`` is a unit and
    reduction yields the input unchanged for ``c != d``.
    """
    # Same constant
    r1 = normal_form(7, [7], [x])
    assert r1.is_zero
    # Different non-zero constant: c=5, d=7. Both are units, so the
    # ideal is the whole ring; NF reduces to 0.
    r2 = normal_form(5, [7], [x])
    assert r2.is_zero  # Any non-zero constant generates the whole ring.


def test_edge_empty_ring_vars_raises():
    """Empty ``ring_vars`` is a ValueError."""
    with pytest.raises(ValueError):
        normal_form(x, [x], [])


def test_edge_extra_variable_raises():
    """A polynomial mentioning a variable absent from ``ring_vars``
    raises a ValueError (rejected by the ring coercion).
    """
    with pytest.raises(ValueError):
        normal_form(x + y, [x], [x])  # y outside the ring
    with pytest.raises(ValueError):
        normal_form(x, [x + y], [x])  # basis poly mentions y


def test_edge_certificate_for_non_member_raises():
    """``ideal_membership_certificate`` raises if ``f`` is not in the
    ideal — i.e., the certificate would be vacuous.
    """
    with pytest.raises(ValueError):
        ideal_membership_certificate(x + 1, [x**2 + 1], [x])


def test_edge_reduce_step_no_reduction_returns_zero_multiplier():
    """If no monomial of ``f`` is divisible by ``LT(g)``, the
    reduction step returns ``f`` unchanged with multiplier ``0``.
    """
    f_red, t = reduce_polynomial_step(x + 1, y, [x, y])
    assert (f_red.as_expr() - (x + 1)).expand() == 0
    assert t.is_zero


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

def test_composition_is_in_ideal_iff_nf_zero():
    """Definitional composition: ``is_in_ideal == (NF == 0)``."""
    G = reduced_groebner([x**2 - y, x*y - z, y**2 - z**2], [x, y, z])
    samples = [x*y - z, x**3 - y*x, x**2 - y, 1, x + y]
    for f in samples:
        nf = normal_form(f, G, [x, y, z])
        in_ideal = is_in_ideal(f, G, [x, y, z])
        assert in_ideal == nf.is_zero, f"mismatch on {f}: nf={nf.as_expr()}, in_ideal={in_ideal}"


def test_composition_certificate_reconstructs_f():
    """For ``f in I``, ``sum(h_i * g_i) == f`` where ``(i, h_i)`` is
    the ideal-membership certificate.
    """
    G = reduced_groebner([x**2 - y, x*y - z], [x, y, z])
    # x^3 - xy = x*(x^2 - y) is clearly in the ideal.
    f = x**3 - x*y
    cert = ideal_membership_certificate(f, G, [x, y, z])
    assert cert  # Not vacuous.
    recon = sum((h * G[i]).as_expr() for i, h in cert)
    assert (recon - f).expand() == 0


def test_composition_groebner_then_normal_form_canonicality():
    """``normal_form`` after ``reduced_groebner`` produces the
    canonical-form representative — equal polynomials in ``k[x]/I``
    yield identical normal forms.
    """
    G = reduced_groebner([x**2 - y, x*y - z], [x, y, z])
    # f and f + h*(x^2-y) for any h must reduce identically.
    f = x**3 + 7
    h = z + x
    g_in_I = h * (x**2 - y)
    rf = normal_form(f, G, [x, y, z])
    rg = normal_form(f + g_in_I, G, [x, y, z])
    assert (rf.as_expr() - rg.as_expr()).expand() == 0


def test_composition_zero_dim_quotient_ring_representation():
    """For the zero-dimensional ideal ``(x^2-1, y^2-1)``, every
    polynomial reduces to a representative of degree < 2 in each
    variable. The quotient ring ``k[x,y]/I`` has basis ``{1, x, y, xy}``.
    """
    G = reduced_groebner([x**2 - 1, y**2 - 1], [x, y])
    f = x**3 * y**3 + x**2 + y**4
    r = normal_form(f, G, [x, y])
    # Degrees in x and y must each be < 2.
    poly = Poly(r.as_expr(), x, y)
    for monom, _ in poly.terms():
        assert monom[0] < 2, f"x-degree {monom[0]} >= 2 in {r.as_expr()}"
        assert monom[1] < 2, f"y-degree {monom[1]} >= 2 in {r.as_expr()}"
    # Hand-check: x^3*y^3 -> x*y; x^2 -> 1; y^4 -> 1. So r = xy + 2.
    assert (r.as_expr() - (x*y + 2)).expand() == 0


def test_composition_canonical_form_alias():
    """``canonical_form`` is exactly ``normal_form`` (composition with
    itself via aliasing): both should give identical results.
    """
    G = reduced_groebner([x**2 + y**2 - 1], [x, y])
    f = x**4 + 3*y
    a = normal_form(f, G, [x, y])
    b = canonical_form(f, G, [x, y])
    assert (a.as_expr() - b.as_expr()).expand() == 0
