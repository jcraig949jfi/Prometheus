"""Synthetic-control tests for G24 x-flip symmetry audit loader.

Validates the x -> -x flip operator + the audit's tolerance behavior
against synthetic polynomials where we can verify Mahler invariance
by hand.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders.composition_g24_lehmer_x_flip import (
    SAMPLE_SIZE,
    TOLERANCE,
    _x_flip_local,
)


# ---------------------------------------------------------------------
# _x_flip_local primitive
# ---------------------------------------------------------------------

def test_x_flip_negates_odd_coeffs():
    """x -> -x: ascending coeffs at odd indices flip sign."""
    coeffs = [1, 2, 3, 4, 5]  # 1 + 2x + 3x^2 + 4x^3 + 5x^4
    flipped = _x_flip_local(coeffs)
    # After x -> -x: 1 - 2x + 3x^2 - 4x^3 + 5x^4
    assert flipped == [1, -2, 3, -4, 5]


def test_x_flip_idempotent_squared():
    """(x -> -x) applied twice == identity."""
    coeffs = [3, -7, 2, 9, -1, 4]
    twice = _x_flip_local(_x_flip_local(coeffs))
    assert twice == coeffs


def test_x_flip_zero_coeffs_unchanged():
    coeffs = [0, 0, 0, 0]
    assert _x_flip_local(coeffs) == [0, 0, 0, 0]


def test_x_flip_single_constant():
    assert _x_flip_local([5]) == [5]


def test_x_flip_palindrome_special_case():
    """Palindromic polynomials (e.g., 1 + x^2) are self-flipped because
    odd-index coeffs are zero."""
    # 1 + 0*x + 1*x^2 has odd-index coeff = 0, so x-flip is no-op
    coeffs = [1, 0, 1]
    assert _x_flip_local(coeffs) == [1, 0, 1]


# ---------------------------------------------------------------------
# Tolerance & sample-size sanity
# ---------------------------------------------------------------------

def test_tolerance_is_in_double_precision_range():
    """Tolerance should be > ULP noise (~1e-15) and small enough to
    catch real catalog bugs (< 1e-3, the typical M-gap between
    distinct entries)."""
    assert 1e-13 < TOLERANCE < 1e-3


def test_sample_size_bounded():
    """Sample size should be at least the smallest test-meaningful
    cohort but cap to keep per-tick cost bounded."""
    assert 50 <= SAMPLE_SIZE <= 1000


# ---------------------------------------------------------------------
# End-to-end with synthetic catalog (mocked)
# ---------------------------------------------------------------------

def test_audit_passes_with_consistent_synthetic_catalog(monkeypatch):
    """If every catalog entry's stored Mahler exactly equals the
    twisted-poly Mahler (we make sure by using x -> -x invariant
    polynomials), the audit returns PROMOTED with 0 mismatches."""
    import charon.agents.stygian.loaders.composition_g24_lehmer_x_flip as g24
    import charon.agents.stygian.loaders.composition_g24_lehmer_x_flip as g24_mod

    # Palindromic synthetic polynomials: 1 + x^2 has M = 1
    # (cyclotomic-like). We exclude M = 1 via the upper_M filter,
    # so use M = 1.5 entries: polynomial p(x) = x^2 + 1.5
    # actually has M = 1.5 (root at +/- sqrt(-1.5), abs = sqrt(1.5),
    # but that's irrational not integer; actually for integer poly
    # x^2 - 2 has M = sqrt(2). Skip the math — directly mock both
    # the catalog AND the Mahler computer so the test is purely
    # about loader logic, not about polynomial arithmetic.
    def fake_loader(upper_M=2.0):
        return [
            {"degree": 2, "mahler_measure": 1.41421356, "coeffs": [-2, 0, 1]}
            for _ in range(SAMPLE_SIZE)
        ]

    def fake_mahler(coeffs):
        # Returns the catalog value exactly, regardless of input.
        # This isolates the audit's tolerance check from the actual
        # polynomial arithmetic.
        return 1.41421356

    monkeypatch.setattr(
        g24_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    import sys
    fake_module = type(sys)("techne.lib.mahler_measure_mock")
    fake_module.mahler_measure = fake_mahler
    monkeypatch.setitem(
        sys.modules, "techne.lib.mahler_measure", fake_module
    )

    result = g24.run_g24_lehmer_x_flip_audit()
    assert result["verdict"] == "PROMOTED"
    assert result["n_mismatches"] == 0


def test_audit_detects_synthetic_corruption(monkeypatch):
    """If twisted-poly Mahler differs from stored value beyond
    tolerance for any entry, audit returns REJECTED with
    symmetry_breaking."""
    import charon.agents.stygian.loaders.composition_g24_lehmer_x_flip as g24
    import charon.agents.stygian.loaders.composition_g24_lehmer_x_flip as g24_mod

    def fake_loader(upper_M=2.0):
        # 10 normal entries + 1 corrupted (twisted Mahler will differ)
        out = [
            {"degree": 2, "mahler_measure": 1.41421356, "coeffs": [-2, 0, 1]}
            for _ in range(10)
        ]
        out.append({"degree": 2, "mahler_measure": 1.5, "coeffs": [-2, 0, 1]})
        return out

    def fake_mahler(coeffs):
        # Returns a value that won't match the stored 1.5 for the
        # corrupted entry, but matches 1.41421356 for the normal ones.
        return 1.41421356

    monkeypatch.setattr(
        g24_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    import sys
    fake_module = type(sys)("techne.lib.mahler_measure_mock")
    fake_module.mahler_measure = fake_mahler
    monkeypatch.setitem(
        sys.modules, "techne.lib.mahler_measure", fake_module
    )

    result = g24.run_g24_lehmer_x_flip_audit()
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "symmetry_breaking"
    assert result["n_mismatches"] >= 1
