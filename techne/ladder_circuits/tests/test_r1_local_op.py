"""R1 straw-man acceptance suite — capability AND kill tests both enforced.

R1 must PASS R0's kill test (renames, fresh coefficients: capability) and FAIL upward probes
(no rule / needs chaining: enforced abstention). Traps 5-7 from the rung notes encoded.
"""
from __future__ import annotations

import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r1_local_op import (  # noqa: E402
    R1LocalOpCircuit,
    linear_root_rule,
)

x, y, p = sp.symbols("x y p")


def circuit() -> R1LocalOpCircuit:
    c = R1LocalOpCircuit()
    c.give_rule(linear_root_rule())
    return c


# ---- capability: survives everything that kills R0 ----------------------------------------

def test_applies_rule_to_trained_shape():
    assert circuit().answer(3 * x + 7) == sp.Rational(-7, 3)


def test_survives_rename_and_fresh_coefficients_R0_kill_passes():
    c = circuit()
    assert c.answer(3 * y + 7) == sp.Rational(-7, 3)      # rename
    assert c.answer(5 * x + 2) == sp.Rational(-2, 5)      # fresh coefficients
    assert c.answer(-11 * y + 4) == sp.Rational(4, 11)    # signs


def test_trap5_exact_far_outside_any_training_hull():
    """Rule application is exact at coefficients no interpolator saw: 10^9-scale and exact
    rationals. An answer-function overfit (trap 5) fails here; rule application cannot."""
    c = circuit()
    assert c.answer(10**9 * x + 3) == sp.Rational(-3, 10**9)
    assert c.answer(sp.Rational(2, 7) * x - sp.Rational(5, 3)) == sp.Rational(35, 6)


def test_determinism():
    c = circuit()
    assert c.answer(5 * x + 2) == c.answer(5 * x + 2)


# ---- kill tests, enforced as tests --------------------------------------------------------

def test_KILL_abstains_without_a_rule_for_the_structure():
    assert circuit().answer(x**2 - 4) is None
    assert circuit().answer(sp.sin(x) - 1) is None


def test_KILL_guard_refuses_illegal_instance_rather_than_erroring():
    """0*x + 7 'matches' the linear shape but has no root: the guard must abstain — legality
    is part of the operation (trap 6 scored separately from answers)."""
    assert circuit().answer(sp.Integer(0) * x + 7) is None
    assert circuit().answer(sp.Integer(7)) is None


def test_KILL_abstains_when_rule_would_need_symbolic_coefficient_reasoning():
    """p*x + 3 with symbolic p needs a case split (p=0?) — that is constraint maintenance
    (R3 territory), so the R1 circuit must abstain, not answer -3/p."""
    assert circuit().answer(p * x + 3) is None


def test_trap7_ac_near_miss_does_not_overreach():
    """a*x^2 + b AC-matches sloppy flattenings of the linear template. The wild-match must
    not treat x**2 as the variable slot."""
    assert circuit().answer(3 * x**2 + 7) is None
    assert circuit().answer(3 * x * y + 7) is None
