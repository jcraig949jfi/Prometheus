"""Smoke tests for Fire #5 active generators: A4 symbolic regression, E3 OEIS mining."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.a4_symbolic_regression import (
    A4SymbolicRegressionGenerator,
    _polyfit_r2,
    _poly_eval,
)
from theseus.generators.e3_oeis_mining import (
    E3OEISMiningGenerator,
    _prop_monotonic_increasing,
    _prop_strictly_positive,
    _prop_alternating_sign,
    _prop_exponential_growth_consistent,
)


def test_polyfit_r2_linear_perfect():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [2.0, 4.0, 6.0, 8.0, 10.0]  # y = 2x
    coeffs, r2 = _polyfit_r2(xs, ys, 1)
    assert abs(r2 - 1.0) < 1e-6
    assert abs(coeffs[0] - 2.0) < 1e-6


def test_polyfit_r2_noise_low():
    xs = list(range(20))
    ys = [42 + 0.1 * (-1 if i % 2 == 0 else 1) for i in range(20)]  # noise around 42
    coeffs, r2 = _polyfit_r2([float(x) for x in xs], ys, 1)
    # Mostly constant → linear fit has low R²
    assert r2 < 0.3


def test_polyfit_r2_quadratic_fit():
    xs = [float(i) for i in range(-5, 6)]
    ys = [x * x for x in xs]
    coeffs, r2 = _polyfit_r2(xs, ys, 2)
    assert abs(r2 - 1.0) < 1e-6


def test_a4_emits_symbolic_regression_record():
    g = A4SymbolicRegressionGenerator(batch_id="t", seed=0, sample_size=15)
    r = g.next()
    assert r is not None
    assert r.generator_id == "a4"
    p = r.claim_payload
    assert "best_r2" in p and "best_degree" in p
    assert "best_coeffs" in p
    assert p["best_degree"] in (1, 2, 3)
    assert "A4_SYMREG" in r.canonical_claim_text


def test_prop_monotonic_correct():
    assert _prop_monotonic_increasing([1, 2, 3, 5])[0] is True
    assert _prop_monotonic_increasing([1, 3, 2, 5])[0] is False


def test_prop_strictly_positive_correct():
    assert _prop_strictly_positive([1, 2, 3])[0] is True
    assert _prop_strictly_positive([0, 1, 2])[0] is False
    assert _prop_strictly_positive([-1, 1, 2])[0] is False


def test_prop_alternating_sign_correct():
    assert _prop_alternating_sign([1, -2, 3, -4, 5])[0] is True
    assert _prop_alternating_sign([1, 2, 3])[0] is False


def test_prop_exponential_growth_consistent_on_fibonacci():
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    holds, _ = _prop_exponential_growth_consistent(fib)
    assert holds  # Fibonacci's log-ratios converge


def test_e3_emits_oeis_record():
    g = E3OEISMiningGenerator(batch_id="t", seed=0)
    if not g._entries:
        pytest.skip("OEIS local dump empty")
    r = g.next()
    assert r is not None
    assert r.generator_id == "e3"
    assert "a_number" in r.claim_payload
    assert "property" in r.claim_payload
    assert "E3_OEIS" in r.canonical_claim_text


def test_a4_e3_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "a4" in actives
    assert "e3" in actives
