"""Tests for prometheus_math.algebraic_geometry_hilbert.

Test categories (math-tdd skill):
- Authority: results vs textbook references (Cox-Little-O'Shea,
  Eisenbud) and hand-computed values.
- Property: invariants that hold across many ideals (Hypothesis).
- Edge: trivial / degenerate / pathological ideals.
- Composition: chain across krull_dimension / degree / genus / HP.

Backend: SymPy fallback. Tests skip cleanly if SymPy is unavailable
(it should always be: SymPy is a hard dependency of prometheus_math).
"""
from __future__ import annotations

import pytest

sympy = pytest.importorskip("sympy")
from sympy import symbols, Poly, Rational, sympify  # noqa: E402

from prometheus_math.algebraic_geometry_hilbert import (  # noqa: E402
    hilbert_polynomial,
    hilbert_series,
    krull_dimension,
    degree_of_variety,
    arithmetic_genus,
    is_zero_dimensional,
    groebner_basis,
)


x, y, z, w = symbols("x y z w")


# ---------------------------------------------------------------------------
# AUTHORITY tests
# ---------------------------------------------------------------------------

def test_authority_maximal_ideal_origin():
    """Reference: ``k[x, y] / (x, y) = k`` (a one-dimensional k-vector
    space, only the constants survive).

    Cox-Little-O'Shea, *Ideals, Varieties and Algorithms*, Ch.9 §3,
    Example 5: the affine Hilbert polynomial of the maximal ideal at
    the origin is the constant ``1``.
    """
    hp = hilbert_polynomial([x, y], [x, y])
    assert hp == Poly(1, symbols("t"))
    assert krull_dimension([x, y], [x, y]) == 0
    assert degree_of_variety([x, y], [x, y]) == 1


def test_authority_fat_point_at_origin():
    """Reference: ``k[x, y] / (x^2, xy, y^2) = span{1, x, y}`` (a
    three-dimensional k-vector space).

    Hand-computed: a Groebner basis is ``{x^2, xy, y^2}`` itself; the
    standard monomials are ``1, x, y`` (the only mons not divisible by
    a leading mon of the GB). Affine HP = constant 3 once d >= 1.
    """
    hp = hilbert_polynomial([x**2, x*y, y**2], [x, y])
    assert hp == Poly(3, symbols("t"))
    assert krull_dimension([x**2, x*y, y**2], [x, y]) == 0
    assert degree_of_variety([x**2, x*y, y**2], [x, y]) == 3
    assert is_zero_dimensional([x**2, x*y, y**2], [x, y])


def test_authority_projective_conic():
    """Reference: smooth projective conic ``V(xz - y^2) ⊂ P^2`` has
    graded Hilbert polynomial ``HP(t) = 2t + 1`` (degree 2, genus 0).

    Cox-Little-O'Shea, *Using Algebraic Geometry*, Ch.6 Ex.4.5:
    a degree-d hypersurface in P^n has HP(t) = (degree d
    plane-curve-type formula). For a plane conic d=2, n=2:
    HP(t) = (n choose 1) t + (1 - genus) = 2t + 1.
    """
    t = symbols("t")
    hp = hilbert_polynomial([x*z - y**2], [x, y, z], graded=True)
    assert hp == Poly(2*t + 1, t)
    assert arithmetic_genus([x*z - y**2], [x, y, z]) == 0


def test_authority_plane_cubic_elliptic_curve():
    """Reference: a smooth plane cubic in P^2 is an elliptic curve;
    its (arithmetic) genus is 1.

    Hartshorne, *Algebraic Geometry*, Ex. I.7.2: a smooth degree-d
    plane curve has genus ``(d-1)(d-2)/2``. For d=3: genus 1.

    Graded HP of V(F_3) ⊂ P^2 is ``3t - g + 1 = 3t``.
    """
    t = symbols("t")
    hp = hilbert_polynomial([x**3 + y**3 + z**3], [x, y, z], graded=True)
    assert hp == Poly(3 * t, t)
    assert arithmetic_genus([x**3 + y**3 + z**3], [x, y, z]) == 1


def test_authority_plane_quartic_genus_3():
    """Reference: a smooth plane quartic in P^2 has genus
    ``(4-1)(4-2)/2 = 3``. Graded HP = 4t - 2.

    Hartshorne, *Algebraic Geometry*, Ex. I.7.2.
    """
    t = symbols("t")
    hp = hilbert_polynomial([x**4 + y**4 + z**4], [x, y, z], graded=True)
    assert hp == Poly(4*t - 2, t)
    assert arithmetic_genus([x**4 + y**4 + z**4], [x, y, z]) == 3


def test_authority_two_points_in_P1():
    """Reference: the homogeneous ideal ``(xy)`` ⊂ k[x, y] cuts out
    two points ``[1:0]`` and ``[0:1]`` in P^1.

    Hand-computed: standard mons (under grevlex with LM = ``xy``) are
    ``1, x, y, x^2, y^2, x^3, y^3, ...`` — exactly two of each total
    degree d >= 1. So graded HP = 2 (constant), reflecting two
    projective points.
    """
    t = symbols("t")
    hp = hilbert_polynomial([x*y], [x, y], graded=True)
    assert hp == Poly(2, t)


# ---------------------------------------------------------------------------
# PROPERTY tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "gens, vs, n_vars",
    [
        ([x, y], [x, y], 2),
        ([x**2 - y], [x, y], 2),
        ([x**2 + y**2 - 1], [x, y], 2),
        ([x*z - y**2], [x, y, z], 3),
        ([x**3 + y**3 + z**3], [x, y, z], 3),
        ([x**4 + y**4 + z**4], [x, y, z], 3),
        ([x*y, y*z], [x, y, z], 3),
    ],
)
def test_property_krull_dimension_at_most_n(gens, vs, n_vars):
    """For any ideal I ⊂ k[x_1, ..., x_n], the Krull dimension of
    k[x]/I is at most n.

    Cox-Little-O'Shea, Ch.9 §3 Theorem 8.
    """
    assert krull_dimension(gens, vs) <= n_vars


@pytest.mark.parametrize(
    "gens, vs, max_d",
    [
        ([x, y], [x, y], 8),
        ([x**2, x*y, y**2], [x, y], 8),
        ([x**2 + y**2 - 1], [x, y], 10),
        ([x*z - y**2], [x, y, z], 10),
        ([x**3 - y*z], [x, y, z], 8),
    ],
)
def test_property_hilbert_function_non_negative(gens, vs, max_d):
    """The Hilbert function ``H_I(d) = dim_k (k[x]/I)_d`` is
    non-negative for every d >= 0."""
    series = hilbert_series(gens, vs, max_degree=max_d)
    assert all(h >= 0 for h in series), f"negative HF entry: {series}"


@pytest.mark.parametrize(
    "gens, vs",
    [
        ([x, y], [x, y]),
        ([x**2, x*y, y**2], [x, y]),
        ([x*y, y*z, z*x], [x, y, z]),
    ],
)
def test_property_zero_dimensional_HP_is_constant(gens, vs):
    """Zero-dimensional ideals have constant Hilbert polynomials
    (= total dimension of the quotient ring)."""
    if not is_zero_dimensional(gens, vs):
        pytest.skip("ideal is positive-dimensional")
    hp = hilbert_polynomial(gens, vs)
    assert hp.degree() <= 0, f"HP not constant: {hp}"
    val = int(sympify(hp.eval(0)))
    assert val >= 1


@pytest.mark.parametrize(
    "gens, vs",
    [
        ([x*z - y**2], [x, y, z]),
        ([x**3 + y**3 + z**3], [x, y, z]),
        ([x**4 + y**4 + z**4], [x, y, z]),
        ([x*y], [x, y]),
    ],
)
def test_property_homogeneous_ideal_HP_grade_matches_codim(gens, vs):
    """For a homogeneous principal ideal ``(F)`` ⊂ k[x_1,...,x_n] with
    F non-zero non-unit, V(F) ⊂ P^{n-1} is a hypersurface of dim n-2,
    so the GRADED HP has degree n-2."""
    hp = hilbert_polynomial(gens, vs, graded=True)
    assert hp.degree() == len(vs) - 2, (
        f"hypersurface in {len(vs)}-var ring: "
        f"expected graded HP deg {len(vs)-2}, got {hp.degree()}"
    )


def test_property_HP_value_equals_standard_mon_count():
    """Composition-style property: for d >= "stability degree", the
    affine HP evaluated at d equals the count of standard monomials of
    degree <= d in the original ring (when the ideal is homogeneous,
    this equals cumulative graded count)."""
    gens = [x*z - y**2]
    vs = [x, y, z]
    hp = hilbert_polynomial(gens, vs, graded=True)
    series = hilbert_series(gens, vs, max_degree=8, homogenize_if_needed=False)
    # Beyond the stability point, hp(d) == series[d]
    for d in range(2, 9):
        assert int(sympify(hp.eval(d))) == series[d], (
            f"HP({d})={hp.eval(d)} but graded HF[{d}]={series[d]}"
        )


# ---------------------------------------------------------------------------
# EDGE-CASE tests
# ---------------------------------------------------------------------------

def test_edge_zero_ideal_in_one_variable():
    """The zero ideal in k[x]: HP^a(d) = #{1, x, ..., x^d} = d+1.
    Krull dim = 1.
    """
    t = symbols("t")
    hp = hilbert_polynomial([], [x])
    assert hp == Poly(t + 1, t)
    assert krull_dimension([], [x]) == 1


def test_edge_zero_ideal_in_two_variables():
    """The zero ideal in k[x, y]: HP^a(d) = C(d+2, 2) = (d+1)(d+2)/2.
    Krull dim = 2.
    """
    t = symbols("t")
    hp = hilbert_polynomial([], [x, y])
    expected = Poly(((t + 1) * (t + 2)) / 2, t)
    assert hp == expected
    assert krull_dimension([], [x, y]) == 2


def test_edge_unit_ideal():
    """Ideal ``(1)`` is the whole ring, quotient = 0, HP is the zero
    polynomial. Krull dimension reported as -1 by convention."""
    t = symbols("t")
    hp = hilbert_polynomial([1], [x, y])
    assert hp == Poly(0, t)
    # Also via integer constant
    hp = hilbert_polynomial([sympify(7)], [x, y])
    assert hp == Poly(0, t)
    assert krull_dimension([1], [x, y]) == -1


def test_edge_single_variable_single_generator():
    """In k[x], the principal ideal ``(x^k)`` has 0-dim quotient
    (k[x]/(x^k) is k-dim k as a vector space). HP = constant k."""
    t = symbols("t")
    for k in (1, 2, 3, 5):
        hp = hilbert_polynomial([x**k], [x])
        assert hp == Poly(k, t), f"x^{k}: expected {k}, got {hp}"
        assert is_zero_dimensional([x**k], [x])


def test_edge_homogeneous_required_for_graded():
    """Asking for ``graded=True`` on a non-homogeneous ideal raises
    ValueError."""
    with pytest.raises(ValueError) as exc:
        hilbert_polynomial([x**2 + y**2 - 1], [x, y], graded=True)
    assert "homogeneous" in str(exc.value).lower()


def test_edge_arithmetic_genus_requires_homogeneous():
    """``arithmetic_genus`` is only well-defined for projective
    varieties; non-homogeneous input raises ValueError."""
    with pytest.raises(ValueError) as exc:
        arithmetic_genus([x**2 + y**2 - 1], [x, y])
    assert "homogeneous" in str(exc.value).lower()


def test_edge_empty_ring_vars_raises():
    """``ring_vars=[]`` is malformed input."""
    with pytest.raises(ValueError):
        hilbert_polynomial([], [])


def test_edge_string_inputs_accepted():
    """Generators may be passed as strings (Singular-style ``^`` for
    powers is auto-converted)."""
    hp1 = hilbert_polynomial(["x^2 + y^2 - 1"], [x, y])
    hp2 = hilbert_polynomial([x**2 + y**2 - 1], [x, y])
    assert hp1 == hp2


# ---------------------------------------------------------------------------
# COMPOSITION tests
# ---------------------------------------------------------------------------

def test_composition_krull_dim_equals_HP_degree():
    """Definition (Cox-Little-O'Shea, Ch.9 §3 Thm 8): the Krull
    dimension of ``k[x]/I`` equals the degree of the affine Hilbert
    polynomial.

    Cross-verifies the krull_dimension and hilbert_polynomial code
    paths agree."""
    cases = [
        ([x, y], [x, y]),
        ([x**2, x*y, y**2], [x, y]),
        ([x**2 + y**2 - 1], [x, y]),
        ([x*z - y**2], [x, y, z]),
        ([x**3 + y**3 + z**3], [x, y, z]),
        ([], [x, y]),
    ]
    for gens, vs in cases:
        hp = hilbert_polynomial(gens, vs)
        kd = krull_dimension(gens, vs)
        if hp.is_zero:
            assert kd == -1, f"unit ideal must have kd=-1, got {kd}"
        else:
            assert hp.degree() == kd, (
                f"{gens}: HP degree {hp.degree()} != Krull dim {kd}"
            )


def test_composition_degree_equals_LC_times_factorial():
    """Definition: degree of V(I) = leading coefficient of HP times
    (Krull-dim)!"""
    import math

    cases = [
        ([x*z - y**2], [x, y, z]),  # degree 2, dim 2 (cone over conic)
        ([x**3 + y**3 + z**3], [x, y, z]),  # degree 3, dim 2
        ([x**4 + y**4 + z**4], [x, y, z]),  # degree 4, dim 2
        ([x**2 + y**2 - 1], [x, y]),   # degree 2, dim 1 (curve)
        ([x*y], [x, y]),  # degree 2, dim 1 (two lines through origin)
    ]
    for gens, vs in cases:
        hp = hilbert_polynomial(gens, vs)
        kd = krull_dimension(gens, vs)
        deg = degree_of_variety(gens, vs)
        if kd >= 0:
            lc = hp.LC()
            expected_deg = int(sympify(lc) * math.factorial(kd))
            assert deg == expected_deg, (
                f"{gens}: degree {deg} != LC*kd! = {expected_deg}"
            )


def test_composition_genus_via_HP_zero():
    """Composition: for projective curves V(F) ⊂ P^2 with smooth F of
    degree d, HP_g(t) = d*t + (1 - g), so g = 1 - HP(0).

    This re-derives :func:`arithmetic_genus` from the bare graded HP.
    """
    cases_F_d_g = [
        (x*z - y**2, 2, 0),                 # smooth conic, genus 0
        (x**3 + y**3 + z**3, 3, 1),         # smooth cubic, genus 1
        (x**4 + y**4 + z**4, 4, 3),         # smooth quartic, genus 3
    ]
    for F, d, g in cases_F_d_g:
        hp = hilbert_polynomial([F], [x, y, z], graded=True)
        # HP(0) should equal 1 - g
        hp_at_0 = int(sympify(hp.eval(0)))
        assert hp_at_0 == 1 - g, (
            f"deg-{d} curve: HP(0) = {hp_at_0} != 1 - g = {1 - g}"
        )
        # And re-derive genus via the helper
        assert arithmetic_genus([F], [x, y, z]) == g


def test_composition_zero_ideal_HP_matches_binomial():
    """Composition: for the zero ideal in k[x_1,...,x_n], the affine
    HP is the binomial polynomial C(t + n, n). This composes Krull
    dimension (= n) with the leading coefficient (= 1/n!).
    """
    import math

    for n in (1, 2, 3, 4):
        vs = symbols(f"v0:{n}")
        hp = hilbert_polynomial([], vs)
        assert hp.degree() == n
        # leading coefficient = 1 / n!
        lc = hp.LC()
        assert sympify(lc) == Rational(1, math.factorial(n))
        # Krull dim = n
        assert krull_dimension([], vs) == n


def test_composition_hilbert_series_cumulative_matches_affine_HP():
    """The cumulative sum of the (affine) hilbert_series matches
    HP_I^a(d) for d in the stable region.

    Composition: hilbert_series + hilbert_polynomial agree.
    """
    gens = [x**2 + y**2 - 1]
    vs = [x, y]
    series = hilbert_series(gens, vs, max_degree=10)
    hp = hilbert_polynomial(gens, vs)
    # series[d] for non-homogeneous = direct affine HF (NOT cumulative
    # — the homogenization gives direct counts equal to affine HF).
    for d in range(3, 11):
        assert int(sympify(hp.eval(d))) == series[d], (
            f"d={d}: HP={hp.eval(d)}, series[{d}]={series[d]}"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
