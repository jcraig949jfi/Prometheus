"""Smoke tests for prometheus_math.algebraic_geometry.

The algebraic_geometry module wraps Singular via subprocess. Most
machines (including the current development host) do not have Singular
installed; in that case the module must:

1. Report ``installed() == False`` cleanly.
2. Raise ``ValueError`` (with a helpful "install Singular" message) on
   every operation.

When Singular *is* available, the smoke tests verify a couple of basic
computations end-to-end. They skip cleanly otherwise.
"""
from __future__ import annotations

import pytest

from prometheus_math import algebraic_geometry as ag
from prometheus_math.backends import _singular


# ---------------------------------------------------------------------------
# Always-on tests: behaviour when Singular is missing
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    ag.installed(),
    reason="Singular installed — skipping unavailability test",
)
def test_singular_unavailable_raises():
    """Every operation raises ValueError with an install hint when Singular
    is absent."""
    assert ag.installed() is False

    expected_hint = "Singular not installed"
    ops = [
        lambda: ag.groebner_basis(["x^2 - y", "y^2 - x"], ["x", "y"]),
        lambda: ag.ideal_quotient(["x*y"], ["x"], ["x", "y"]),
        lambda: ag.primary_decomposition(["x*y"], ["x", "y"]),
        lambda: ag.factorize_polynomial("x^2 - 1", ["x"]),
        lambda: ag.hilbert_series(["x^2", "y^2"], ["x", "y"]),
        lambda: ag.free_resolution(["x^2", "y^2"], ["x", "y"]),
        lambda: ag.is_radical(["x^2"], ["x"]),
    ]
    for fn in ops:
        with pytest.raises(ValueError) as excinfo:
            fn()
        assert expected_hint in str(excinfo.value), (
            f"missing install hint in error: {excinfo.value!r}"
        )


def test_install_message_mentions_path_hints():
    """The install message should reference the standard install paths
    so users know where to put the binary."""
    if ag.installed():
        pytest.skip("Singular installed — install hint not surfaced")
    with pytest.raises(ValueError) as excinfo:
        ag.groebner_basis(["x"], ["x"])
    msg = str(excinfo.value)
    assert "singular.uni-kl.de" in msg.lower() or "SageMath" in msg
    assert "PATH" in msg or "cygwin" in msg.lower()


def test_polynomial_parser_basic():
    """The Singular polynomial-output parser should handle basic
    univariate expressions even without Singular installed."""
    # 2x^2 + 3x - 5  →  [2, 3, -5]
    assert _singular.parse_polynomial("2x2+3x-5") == [2, 3, -5]
    # x^3 - x  →  [1, 0, -1, 0]
    assert _singular.parse_polynomial("x3-x") == [1, 0, -1, 0]
    # constant
    assert _singular.parse_polynomial("7") == [7]
    # garbage returns None
    assert _singular.parse_polynomial("not a poly @@@") is None


def test_singular_path_resolves_or_none():
    """``singular_path()`` always returns either a string or None;
    never raises."""
    p = _singular.singular_path()
    assert p is None or isinstance(p, str)
    # Consistency: is_installed() agrees with singular_path()
    assert _singular.is_installed() == (p is not None)


# ---------------------------------------------------------------------------
# Smoke tests: only run when Singular is available
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not ag.installed(),
    reason="Singular not installed",
)
def test_groebner_basis_smoke():
    """Compute a Groebner basis of {x^2 - y, y^2 - x} in lex order.

    The reduced lex Groebner basis of this ideal is well known:
        { x - y^2,  y^4 - y }
    (variables x > y, lex order).
    """
    gb = ag.groebner_basis(
        ["x^2 - y", "y^2 - x"],
        ["x", "y"],
        order="lp",
    )
    assert isinstance(gb, list)
    assert len(gb) >= 1
    joined = " ".join(gb).replace(" ", "")
    # Look for the y-only generator (y^4 - y) somewhere in the basis.
    assert "y4" in joined or "y^4" in joined


@pytest.mark.skipif(
    not ag.installed(),
    reason="Singular not installed",
)
def test_factor_smoke():
    """x^2 - 1 over Q factors as (x - 1)(x + 1)."""
    factors = ag.factorize_polynomial("x^2 - 1", ["x"])
    assert isinstance(factors, list)
    # Sum of multiplicities of non-constant factors should be 2
    forms = [f.replace(" ", "") for f, _ in factors]
    blob = " ".join(forms)
    assert "x-1" in blob and "x+1" in blob


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
