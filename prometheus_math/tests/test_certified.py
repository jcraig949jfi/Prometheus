"""TDD suite for prometheus_math.certified — ball-arithmetic certified evaluation (Arb/FLINT 3).

Written FIRST, per the math-tdd skill. The module wraps python-flint's arb type into a
CertifiedValue whose radius is a *guaranteed* enclosure — the upgrade over `precision_dps`
bookkeeping is that the error bound is certified by Arb's ball arithmetic, not requested.

Four categories: authority (OEIS digit sequences + mpmath cross-tool), property (Hypothesis),
edge, composition (π²/6 = ζ(2) chain across two operations).
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.certified import (  # noqa: E402
    CertifiedValue,
    certified_const,
    certified_zeta,
    KNOWN_CONSTANTS,
)

import mpmath  # noqa: E402


# ------------------------------------------------------------------ authority

def test_pi_against_oeis_a000796():
    """π to 30 digits, from OEIS A000796 (decimal expansion of Pi).

    Reference: OEIS A000796 digits 3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,6,4,3,3,8,3,2,7,9...
    i.e. π = 3.14159265358979323846264338327... The certified ball at 30 dps must CONTAIN this
    value and have radius below 1e-29.
    """
    with mpmath.workdps(45):
        ref = mpmath.mpf("3.14159265358979323846264338327950288")
    v = certified_const("pi", dps=30)
    assert v.contains(ref)
    assert v.radius < 1e-29


def test_e_against_oeis_a001113():
    """e to 25 digits, from OEIS A001113: 2.718281828459045235360287...

    Reference: OEIS A001113 (decimal expansion of e), 40 digits — MORE digits than the ball's
    25 dps, so the reference's own truncation error (~1e-39) is far below the ball radius.
    (First draft used a 27-digit truncation and the certified ball CORRECTLY excluded it:
    a truncated expansion is not the value. Lesson recorded.)
    """
    with mpmath.workdps(55):
        ref = mpmath.mpf("2.718281828459045235360287471352662497757")
    v = certified_const("e", dps=25)
    assert v.contains(ref)
    assert v.radius < 1e-24


def test_zeta3_against_oeis_a002117():
    """ζ(3) (Apéry's constant) to 20 digits, from OEIS A002117: 1.202056903159594285399...

    Reference: OEIS A002117 (decimal expansion of zeta(3)), 37 digits >> the ball's 20 dps.
    """
    with mpmath.workdps(50):
        ref = mpmath.mpf("1.202056903159594285399738161511449991")
    v = certified_zeta(3, dps=20)
    assert v.contains(ref)
    assert v.radius < 1e-19


def test_zeta_cross_checked_against_mpmath_second_tool():
    """Cross-tool check (skill rubric score-3 authority): Arb's certified ζ must contain
    mpmath's independently computed value at several real points.

    Reference: mpmath.zeta at dps 40 (independent implementation: Euler–Maclaurin/Borwein,
    not Arb).
    """
    with mpmath.workdps(40):
        for s in (2, 3, 5, 7.5, 11):
            ref = mpmath.zeta(mpmath.mpf(s))
            v = certified_zeta(s, dps=30)
            assert v.contains(ref), f"zeta({s}): ball {v} excludes mpmath {ref}"


# ------------------------------------------------------------------ property (Hypothesis)

@given(st.sampled_from(sorted(KNOWN_CONSTANTS)), st.integers(min_value=5, max_value=200))
@settings(max_examples=60, deadline=None)
def test_ball_contains_own_midpoint_and_has_positive_finite_radius(name, dps):
    """A certified ball always contains its own midpoint; radius is finite and >= 0."""
    v = certified_const(name, dps=dps)
    assert v.contains(v.midpoint)
    assert 0 <= v.radius < math.inf


@given(st.sampled_from(sorted(KNOWN_CONSTANTS)))
@settings(max_examples=20, deadline=None)
def test_radius_shrinks_monotonically_with_requested_dps(name):
    """More requested precision never yields a WIDER certified ball (radius non-increasing
    across dps 10 -> 40 -> 160)."""
    r10 = certified_const(name, dps=10).radius
    r40 = certified_const(name, dps=40).radius
    r160 = certified_const(name, dps=160).radius
    assert r40 <= r10
    assert r160 <= r40
    assert r160 < r10  # and strictly shrinks over a 16x dps span


@given(st.floats(min_value=1.5, max_value=50, allow_nan=False), st.integers(20, 60))
@settings(max_examples=40, deadline=None)
def test_zeta_ball_contains_mpmath_value_generic_s(s, dps):
    """Property: for arbitrary real s in (1.5, 50], the certified ball contains the
    second-tool value. Includes large-scale inputs per the skill's anti-pattern list."""
    with mpmath.workdps(dps + 10):
        ref = mpmath.zeta(mpmath.mpf(s))
    assert certified_zeta(s, dps=dps).contains(ref)


@given(st.integers(min_value=5, max_value=120))
@settings(max_examples=30, deadline=None)
def test_interval_addition_encloses_sum(dps):
    """Ball arithmetic composes: (π + e) ball must contain π_ref + e_ref."""
    with mpmath.workdps(150):
        ref = mpmath.pi + mpmath.e
    v = certified_const("pi", dps=dps) + certified_const("e", dps=dps)
    assert v.contains(ref)


def test_decisively_nonzero_is_trichotomous_not_optimistic():
    """decisively_nonzero() must return True only when 0 is EXCLUDED from the ball;
    a ball straddling zero returns False (indeterminate is not a yes)."""
    v = certified_const("pi", dps=20)
    assert v.decisively_nonzero() is True
    straddling = CertifiedValue(mid_str="0.0", rad_str="0.001", dps=20)
    assert straddling.decisively_nonzero() is False


# ------------------------------------------------------------------ edge

def test_edge_cases():
    """Edges covered:
    - unknown constant name: ValueError with the name in the message
    - dps <= 0: ValueError
    - zeta at the pole s=1: ValueError (not a NaN ball)
    - zeta just above the pole (s=1+1e-6): finite certified ball (precision boundary)
    - pathological scale: dps=5000 still returns a certified ball with tiny radius
    """
    with pytest.raises(ValueError, match="unknown constant"):
        certified_const("feigenbaum_wrong_name", dps=10)
    with pytest.raises(ValueError, match="dps"):
        certified_const("pi", dps=0)
    with pytest.raises(ValueError, match="pole"):
        certified_zeta(1, dps=10)
    near_pole = certified_zeta(1 + 1e-6, dps=30)
    assert near_pole.radius < math.inf and near_pole.midpoint > 1e5
    huge = certified_const("pi", dps=5000)
    assert huge.radius < mpmath.mpf(10) ** (-4990)


# ------------------------------------------------------------------ composition

def test_composition_pi_squared_over_six_equals_zeta_two():
    """Basel chain across TWO operations: certified_const('pi')**2 / 6 and certified_zeta(2)
    are certified balls for the same real number, so they must OVERLAP at every dps.

    This is the module's own consistency proof: constants pipeline and zeta pipeline meet.
    """
    for dps in (15, 30, 60):
        lhs = (certified_const("pi", dps=dps) ** 2) / 6
        rhs = certified_zeta(2, dps=dps)
        assert lhs.overlaps(rhs), f"π²/6 and ζ(2) balls disjoint at dps={dps}"


def test_composition_certified_beats_float_at_boundary():
    """The reason this module exists: a certified comparison is trichotomous where floats lie.

    ζ(2) − π²/6 is exactly 0; the certified difference ball must CONTAIN 0 (never decisively
    nonzero), while the naive float difference is a nonzero garbage value.
    """
    diff = certified_zeta(2, dps=40) - (certified_const("pi", dps=40) ** 2) / 6
    assert diff.contains(0)
    assert diff.decisively_nonzero() is False
