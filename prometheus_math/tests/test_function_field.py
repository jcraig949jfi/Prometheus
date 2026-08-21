"""TDD suite for prometheus_math.function_field — the four required categories.

Authority / property / edge / composition, per the math-tdd skill.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import sympy as sp
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.function_field import (  # noqa: E402
    SeparabilityError, inseparability_witness, is_separable,
)

x = sp.Symbol("x")


# ---- 1. authority ------------------------------------------------------------------------

def test_x_p_minus_1_is_inseparable_over_F_p_and_separable_over_Q():
    """Reference: Lang, *Algebra* 3rd ed., Ch. V §4 (and Ch. V §6 on p-th powers).

    In characteristic p the freshman's dream gives x^p - 1 = (x - 1)^p, a single root of
    multiplicity p, so gcd(f, f') = f. Over ℚ, x^p - 1 has p distinct p-th roots of unity.
    Hand-check for p = 5: f' = 5x^4 = 0 in F_5, and gcd(f, 0) = f, degree 5 > 0.
    """
    assert is_separable(x ** 5 - 1, char=0) is True
    assert is_separable(x ** 5 - 1, char=5) is False
    assert is_separable(x ** 5 - 1, char=3) is True        # 3 does not divide 5


def test_artin_schreier_polynomial_is_separable_in_its_own_characteristic():
    """Reference: Lang, *Algebra*, Ch. VI §6 (Artin–Schreier extensions). x^p - x - 1 has
    derivative p·x^(p-1) - 1 = -1 in characteristic p, a non-zero constant, so gcd(f, f') = 1
    and the polynomial is separable — the standard degree-p separable example in char p.
    """
    for p in (2, 3, 5, 7):
        assert is_separable(x ** p - x - 1, char=p) is True


def test_repeated_factor_is_reported_as_the_witness():
    """(x - 1)^2 (x - 2): gcd with the derivative is (x - 1) up to units, hand-verified."""
    w = inseparability_witness((x - 1) ** 2 * (x - 2), char=0)
    assert w is not None and sp.Poly(w, x).degree() == 1
    assert sp.simplify(w.subs(x, 1)) == 0


# ---- 2. property (Hypothesis) ---------------------------------------------------------------

@settings(max_examples=60, deadline=None)
@given(st.integers(min_value=1, max_value=6), st.sampled_from([2, 3, 5, 7]))
def test_p_th_power_of_any_polynomial_is_inseparable_in_characteristic_p(k, p):
    """Invariant: f(x)^p has derivative 0 in char p for any non-constant f, hence is never
    separable. Uses f = x + k so the base is non-constant for every k."""
    f = (x + k) ** p
    assert is_separable(f, char=p) is False
    assert inseparability_witness(f, char=p) is not None


@settings(max_examples=60, deadline=None)
@given(st.integers(min_value=2, max_value=9))
def test_distinct_linear_factors_are_always_separable_over_Q(n):
    """Invariant: a product of n distinct linear factors has n distinct roots."""
    f = sp.prod([x - i for i in range(n)])
    assert is_separable(f, char=0) is True
    assert inseparability_witness(f, char=0) is None


@settings(max_examples=40, deadline=None)
@given(st.sampled_from([2, 3, 5, 7]), st.integers(min_value=1, max_value=4))
def test_witness_and_boolean_never_disagree(p, k):
    """Compatibility invariant across the two entry points: exactly one of them fires."""
    for f in (x ** p - 1, x ** p - x - 1, (x + k) ** 2, x ** k + 1):
        sep = is_separable(f, char=p)
        assert sep == (inseparability_witness(f, char=p) is None)


# ---- 3. edge cases ---------------------------------------------------------------------------

def test_separability_edges():
    """Edges covered:
    - zero polynomial: SeparabilityError (no roots to be distinct)
    - constant polynomial: SeparabilityError (degree 0, root condition undefined)
    - negative characteristic: SeparabilityError
    - non-prime positive characteristic (char 4, 6): SeparabilityError, since F_4 is not ℤ/4
      and sympy's `modulus` would silently work in a non-field
    - boundary characteristic 2, the smallest prime, where f' loses the most information
    - degree exactly 1: separable, the smallest non-trivial case
    """
    with pytest.raises(SeparabilityError):
        is_separable(sp.Integer(0), char=5)
    with pytest.raises(SeparabilityError):
        is_separable(sp.Integer(7), char=5)
    with pytest.raises(SeparabilityError):
        is_separable(x ** 2 - 1, char=-3)
    for bad in (4, 6, 9):
        with pytest.raises(SeparabilityError):
            is_separable(x ** 2 - 1, char=bad)
    assert is_separable(x ** 2 + x + 1, char=2) is True     # roots in F_4, distinct
    assert is_separable(x ** 2 - 1, char=2) is False        # (x+1)^2 in char 2
    assert is_separable(x - 3, char=7) is True              # degree 1


def test_pathological_degree_is_handled():
    """Pathological scale: degree 200 in char 2, where naive root-finding would be hopeless but
    the gcd criterion is cheap."""
    assert is_separable(x ** 200 - 1, char=2) is False
    assert is_separable(x ** 201 - x - 1, char=3) is True


# ---- 4. composition --------------------------------------------------------------------------

def test_composes_with_the_canon_R10_transfer_circuit():
    """The primitive must agree with the R10 circuit's independent probe of the same fact —
    two code paths (this gcd criterion vs. the circuit's own sympy call) for one claim."""
    from techne.ladder_circuits.canon_r10_analogy import (
        W_F3, W_F5, W_Z, _p_x5_minus_1_separable,
    )
    for world in (W_Z, W_F5, W_F3):
        holds, _witness = _p_x5_minus_1_separable(world)
        assert holds == is_separable(x ** 5 - 1, char=world.char)


def test_composes_with_factorization_multiplicity():
    """Chain: separability must agree with sympy's factorisation multiplicities — a polynomial
    is separable iff every irreducible factor appears exactly once."""
    for f, char in ((x ** 5 - 1, 5), (x ** 5 - 1, 0), ((x - 1) ** 2 * (x - 2), 0),
                    (x ** 3 - x - 1, 3)):
        poly = sp.Poly(f, x) if char == 0 else sp.Poly(f, x, modulus=char)
        multiplicities = [m for _fac, m in poly.factor_list()[1]]
        assert is_separable(f, char=char) == all(m == 1 for m in multiplicities)
