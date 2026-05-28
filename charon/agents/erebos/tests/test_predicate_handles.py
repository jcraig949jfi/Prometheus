"""Synthetic-control tests for predicate_handles.

Per Erebos v3 Phase 0 ITER-25. Validates the MahlerPolynomialHandle
(fully implemented), SmtFormulaHandle (basic), and the deferred
Lean/SymPy/Sage stubs. Critical regression: the cyclotomic-extension
detector that ITER-10 caught inline in G18 is now a structural
property of the handle.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators._predicate_handles import (
    M_COMPARISON_EPSILON,
    LeanTermHandle,
    MahlerPolynomialHandle,
    SageObjectHandle,
    SmtFormulaHandle,
    SymPyExpressionHandle,
)


# ---------------------------------------------------------------------
# MahlerPolynomialHandle — palindromic detection
# ---------------------------------------------------------------------

def test_mahler_handle_lehmer_polynomial_is_palindromic():
    """Lehmer's degree-10 polynomial: [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]"""
    h = MahlerPolynomialHandle(
        coeffs=(1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1),
        mahler_measure=1.1762808182599176,
        degree=10,
        salem_class=True,
    )
    assert h.is_palindromic is True
    assert h.is_anti_palindromic is False


def test_mahler_handle_non_palindromic():
    h = MahlerPolynomialHandle(
        coeffs=(1, 2, 3, 4, 5),
        mahler_measure=2.0,
        degree=4,
    )
    assert h.is_palindromic is False


def test_mahler_handle_anti_palindromic_detected():
    """Anti-palindromic = coeffs == [-c for c in reversed(coeffs)]."""
    h = MahlerPolynomialHandle(
        coeffs=(1, 2, 0, -2, -1),  # reversed = (-1, -2, 0, 2, 1) = -1 * coeffs
        mahler_measure=1.5,
        degree=4,
    )
    assert h.is_anti_palindromic is True


# ---------------------------------------------------------------------
# Cyclotomic-extension detector (ITER-10 G18 regression)
# ---------------------------------------------------------------------

M_LEHMER = 1.1762808182599176
M_LEHMER_X_PHI_16 = 1.1762808182599174  # 2 ULPs apart from Lehmer's M


def test_mahler_handle_lehmer_x_phi_16_is_cyclotomic_extension_of_lehmer():
    """The ITER-10 G18 false-positive scenario: Lehmer × Φ_16 has
    the same Mahler measure as Lehmer (within ULPs) but higher
    degree. Locks in that the handle's structural detector catches
    this."""
    lehmer = MahlerPolynomialHandle(
        coeffs=(1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1),
        mahler_measure=M_LEHMER,
        degree=10,
        salem_class=True,
    )
    lehmer_x_phi_16 = MahlerPolynomialHandle(
        coeffs=(1, 1, 0, -1, -1, -1, -1, -1, 1, 2, 1, -1, -1, -1, -1, -1, 0, 1, 1),
        mahler_measure=M_LEHMER_X_PHI_16,
        degree=18,
    )
    assert lehmer_x_phi_16.is_cyclotomic_extension_of(lehmer) is True


def test_mahler_handle_distinct_polynomial_not_cyclotomic_extension():
    """Same degree but different M — not an extension."""
    p1 = MahlerPolynomialHandle(
        coeffs=(1, 0, 1), mahler_measure=1.20, degree=2
    )
    p2 = MahlerPolynomialHandle(
        coeffs=(1, 1, 1), mahler_measure=1.50, degree=2
    )
    assert p1.is_cyclotomic_extension_of(p2) is False


def test_mahler_handle_lower_degree_not_cyclotomic_extension():
    """is_cyclotomic_extension_of requires self.degree > other.degree."""
    low = MahlerPolynomialHandle(
        coeffs=(1,), mahler_measure=1.176, degree=1
    )
    high = MahlerPolynomialHandle(
        coeffs=(1, 1), mahler_measure=1.176, degree=2
    )
    assert low.is_cyclotomic_extension_of(high) is False


# ---------------------------------------------------------------------
# Symmetry operators
# ---------------------------------------------------------------------

def test_mahler_handle_x_flip_negates_odd_indices():
    h = MahlerPolynomialHandle(
        coeffs=(1, 2, 3, 4, 5),
        mahler_measure=1.5,
        degree=4,
    )
    flipped = h.x_flip()
    assert flipped.coeffs == (1, -2, 3, -4, 5)
    # Mahler measure preserved
    assert flipped.mahler_measure == h.mahler_measure


def test_mahler_handle_x_flip_idempotent_under_double_application():
    h = MahlerPolynomialHandle(
        coeffs=(3, -7, 2, 9, -1),
        mahler_measure=2.0,
        degree=4,
    )
    twice = h.x_flip().x_flip()
    assert twice.coeffs == h.coeffs


def test_mahler_handle_reciprocal_reverses_coefficients():
    h = MahlerPolynomialHandle(
        coeffs=(1, 2, 3, 4, 5),
        mahler_measure=1.5,
        degree=4,
    )
    rev = h.reciprocal()
    assert rev.coeffs == (5, 4, 3, 2, 1)
    assert rev.mahler_measure == h.mahler_measure


def test_mahler_handle_palindromic_invariant_under_reciprocal():
    """Palindromic polynomials reverse to themselves."""
    h = MahlerPolynomialHandle(
        coeffs=(1, 2, 3, 2, 1),
        mahler_measure=1.5,
        degree=4,
    )
    rev = h.reciprocal()
    assert rev.coeffs == h.coeffs


# ---------------------------------------------------------------------
# evaluate() + to_string()
# ---------------------------------------------------------------------

def test_mahler_handle_evaluate_structural_equality():
    h1 = MahlerPolynomialHandle(coeffs=(1, 0, 1), mahler_measure=1.0, degree=2)
    h2 = MahlerPolynomialHandle(coeffs=(1, 0, 1), mahler_measure=1.0, degree=2)
    h3 = MahlerPolynomialHandle(coeffs=(1, 1, 1), mahler_measure=1.5, degree=2)
    assert h1.evaluate(h2) is True
    assert h1.evaluate(h3) is False


def test_mahler_handle_to_string_format():
    h = MahlerPolynomialHandle(
        coeffs=(1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1),
        mahler_measure=M_LEHMER,
        degree=10,
        salem_class=True,
    )
    s = h.to_string()
    assert "deg=10" in s
    assert "salem=1" in s
    assert "pal=1" in s


def test_mahler_handle_handle_type_field():
    h = MahlerPolynomialHandle(coeffs=(1,), mahler_measure=1.0, degree=0)
    assert h.handle_type == "mahler_polynomial"


# ---------------------------------------------------------------------
# ComposedClaim.predicate_handle field — optional, backward-compat
# ---------------------------------------------------------------------

def test_composed_claim_optional_predicate_handle_defaults_to_none():
    claim = ComposedClaim(
        plugin_id="g_test",
        composed_id="TEST-001",
        input_provenance={},
        transformation_description="t",
        output_claim_text="claim",
        falsification_route="f",
        expected_kill_pattern="kp",
        loader_feasibility_note="n",
    )
    assert claim.predicate_handle is None


def test_composed_claim_with_mahler_handle_serializes():
    h = MahlerPolynomialHandle(
        coeffs=(1, 0, 1), mahler_measure=1.0, degree=2
    )
    claim = ComposedClaim(
        plugin_id="g_test",
        composed_id="TEST-002",
        input_provenance={},
        transformation_description="t",
        output_claim_text="claim",
        falsification_route="f",
        expected_kill_pattern="kp",
        loader_feasibility_note="n",
        predicate_handle=h,
    )
    assert claim.predicate_handle is h
    assert claim.predicate_handle.handle_type == "mahler_polynomial"
    assert claim.predicate_handle.is_palindromic is True


# ---------------------------------------------------------------------
# Deferred stubs — confirm they raise the right errors
# ---------------------------------------------------------------------

def test_lean_handle_stub_raises_not_implemented():
    h = LeanTermHandle(term_ref="mathlib.test", context="ctx")
    with pytest.raises(NotImplementedError, match="Lean 4"):
        h.evaluate({})
    assert h.handle_type == "lean_term"


def test_sympy_handle_stub_raises_not_implemented():
    h = SymPyExpressionHandle(expr_repr="x**2 + 1", symbols=("x",))
    with pytest.raises(NotImplementedError, match="Phase 3"):
        h.evaluate({})
    assert h.handle_type == "sympy_expr"


def test_sage_handle_stub_raises_not_implemented():
    h = SageObjectHandle(sage_object_id="abc", sage_class="EllipticCurve")
    with pytest.raises(NotImplementedError, match="SageMath"):
        h.evaluate(None)
    assert h.handle_type == "sage_object"


def test_smt_handle_evaluate_full_impl_deferred():
    """SmtFormulaHandle.evaluate raises (either ImportError-converted-to
    -NotImplementedError if z3 missing, or NotImplementedError if z3
    present but full eval is Phase 3+)."""
    h = SmtFormulaHandle(sexpr="(> x 0)", variables=("x",))
    with pytest.raises(NotImplementedError):
        h.evaluate({"x": 5})
    assert h.handle_type == "smt_formula"


def test_smt_handle_to_string():
    h = SmtFormulaHandle(sexpr="(> x 0)", variables=("x",))
    assert "SMT" in h.to_string()
    assert "x" in h.to_string()
