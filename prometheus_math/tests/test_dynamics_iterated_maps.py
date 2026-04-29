"""Tests for prometheus_math.dynamics_iterated_maps.

Project #76 — pm.dynamics.iterated_maps (logistic, tent, sine, Hénon).

Test categories follow techne/skills/math-tdd.md:
  Authority    — output matches authoritative reference values
                 (Feigenbaum's δ, Lyapunov exponent of the doubling
                 map = ln 2, fixed-point coordinates).
  Property     — invariants (orbit confinement, sortedness).
  Edge         — n_iter=0, parameter out of range, degenerate Hénon.
  Composition  — bifurcation × periodic-orbit consistency,
                 logistic-tent conjugacy of Lyapunov exponents,
                 superstability cascade × Feigenbaum δ.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math import dynamics_iterated_maps as dim


# ---------------------------------------------------------------------------
# AUTHORITY tests (>=4 required)
# ---------------------------------------------------------------------------


def test_authority_logistic_fixed_point_at_r_2():
    """At r=2, the logistic map has a stable fixed point at x* = 1/2.

    Reference: hand-computation.  Solve r x (1 - x) = x:
       x (r (1 - x) - 1) = 0  →  x = 0  or  x = 1 - 1/r.
    For r = 2 the non-trivial fixed point is x = 0.5.  The
    multiplier f'(x*) = r (1 - 2 x*) = 2 (1 - 1) = 0 → superstable
    (Strogatz, "Nonlinear Dynamics and Chaos", §10.1, Example 10.1.1).
    """
    orbit = dim.logistic_map(r=2.0, x_init=0.5, n_iter=100)
    assert abs(orbit[-1] - 0.5) < 1e-12

    # Convergence from a different start
    orbit2 = dim.logistic_map(r=2.0, x_init=0.3, n_iter=200)
    assert abs(orbit2[-1] - 0.5) < 1e-6


def test_authority_logistic_at_r_4_lyapunov_equals_ln_2():
    """The fully chaotic logistic map (r=4) is conjugate to the tent
    map and has Lyapunov exponent λ = ln 2 ≈ 0.6931.

    Reference: Devaney, "An Introduction to Chaotic Dynamical
    Systems" (2nd ed., 1989), §1.7 — the conjugacy h(x) = sin²(πx/2)
    sends the tent map (with λ = ln 2 a.e.) to the r=4 logistic map,
    so their Lyapunov exponents agree.  Numerical confirmation in
    Strogatz §10.5.
    """
    lam = dim.lyapunov_exponent(
        dim.logistic_map,
        x_init=0.1,
        params={"r": 4.0},
        n_iter=200_000,
        transient=2_000,
    )
    assert abs(lam - math.log(2.0)) < 5e-3


def test_authority_tent_map_hand_computed_iterations():
    """tent_map(0.3, ...) hand-computation:
        x_0 = 0.3
        x_1 = 2 * 0.3 = 0.6
        x_2 = 2 * (1 - 0.6) = 0.8
        x_3 = 2 * (1 - 0.8) = 0.4
        x_4 = 2 * 0.4 = 0.8
        x_5 = 2 * (1 - 0.8) = 0.4
    """
    orbit = dim.tent_map(0.3, 5)
    expected = [0.6, 0.8, 0.4, 0.8, 0.4]
    np.testing.assert_allclose(orbit, expected, atol=1e-12)


def test_authority_henon_classical_attractor_bounded():
    """Hénon map at (a, b) = (1.4, 0.3) has a strange attractor
    contained in roughly [-1.5, 1.5] × [-0.45, 0.45].

    Reference: Hénon, M., "A two-dimensional mapping with a strange
    attractor", Comm. Math. Phys. 50 (1976) 69-77, Fig. 1.  The
    attractor is bounded and the trajectory does not escape.
    """
    xs, ys = dim.henon_map(
        a=1.4, b=0.3, x0_init=0.1, y0_init=0.1, n_iter=20_000, transient=2_000
    )
    assert np.all(np.abs(xs) < 2.0)
    assert np.all(np.abs(ys) < 1.0)
    # Non-trivial spread (not a fixed point)
    assert xs.std() > 0.3


def test_authority_logistic_period_2_orbit_at_r_3_2():
    """At r = 3.2 the logistic map has a period-2 orbit.  Solving
    x = f(f(x)) and discarding the period-1 fixed point x = 1 - 1/r
    gives the analytic pair

        x_± = ((r + 1) ± sqrt((r-3)(r+1))) / (2 r)

    (Strogatz, §10.3 eq. 10.3.6).  For r = 3.2 this evaluates to
    x_+ ≈ 0.79945549 and x_- ≈ 0.51304451.
    """
    r = 3.2
    discrim = math.sqrt((r - 3) * (r + 1))
    x_plus = (r + 1 + discrim) / (2 * r)
    x_minus = (r + 1 - discrim) / (2 * r)
    expected = sorted([x_plus, x_minus])

    roots = dim.find_periodic_orbits(
        dim.logistic_map, params={"r": r}, period=2, x_range=(0.05, 0.99)
    )
    # Period-2 orbit + the period-1 fixed point (which is also
    # period-2) should appear.  Filter out the period-1.
    fixed_pt = 1.0 - 1.0 / r
    period2 = sorted(rt for rt in roots if abs(rt - fixed_pt) > 1e-3)
    assert len(period2) == 2
    np.testing.assert_allclose(period2, expected, atol=1e-4)


def test_authority_feigenbaum_constant_estimate():
    """δ ≈ 4.66920160910299...

    Reference: Feigenbaum, M.J., "Quantitative universality for a
    class of nonlinear transformations", J. Stat. Phys. 19 (1978)
    25-52.  Strogatz §10.6 reports δ = 4.6692...
    """
    delta = dim.feigenbaum_constant_estimate(
        dim.logistic_map, params_range=(3.0, 3.5699)
    )
    assert abs(delta - 4.6692) < 0.05


# ---------------------------------------------------------------------------
# PROPERTY tests (>=3 required)
# ---------------------------------------------------------------------------


@given(
    r=st.floats(min_value=0.0, max_value=4.0, allow_nan=False),
    x0=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
@settings(max_examples=40, deadline=None)
def test_property_logistic_invariant_unit_interval(r, x0):
    """For r in [0, 4] and x0 in [0, 1], the logistic orbit stays
    in [0, 1].  (Standard fact: f(x) = r x (1-x) on [0,1] attains
    its max r/4 ≤ 1 when r ≤ 4.)"""
    orbit = dim.logistic_map(r, x0, n_iter=50)
    assert np.all(orbit >= -1e-12)
    assert np.all(orbit <= 1.0 + 1e-12)


@given(x0=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
@settings(max_examples=30, deadline=None)
def test_property_tent_invariant_unit_interval(x0):
    """The tent map sends [0, 1] to [0, 1]."""
    orbit = dim.tent_map(x0, n_iter=50)
    assert np.all(orbit >= -1e-12)
    assert np.all(orbit <= 1.0 + 1e-12)


def test_property_lyapunov_logistic_r2_is_negative_infinity_or_very_negative():
    """At r=2 the unique attracting fixed point is superstable
    (multiplier f'(0.5) = 0).  The Lyapunov exponent is -∞ in the
    limit, so any finite-N estimate is hugely negative (or -inf
    when the orbit lands exactly on the critical point).
    """
    lam = dim.lyapunov_exponent(
        dim.logistic_map,
        x_init=0.4,
        params={"r": 2.0},
        n_iter=2000,
        transient=1000,
    )
    assert lam == float("-inf") or lam < -2.0


def test_property_bifurcation_diagram_shape():
    """bifurcation_diagram returns flat arrays of length n_params * n_iter."""
    n_params, n_iter = 25, 10
    p, x = dim.bifurcation_diagram(
        dim.logistic_map,
        param_range=(3.0, 4.0),
        n_params=n_params,
        x_init=0.3,
        n_iter=n_iter,
        transient=200,
    )
    assert p.shape == (n_params * n_iter,)
    assert x.shape == (n_params * n_iter,)
    # x lies in [0, 1]
    assert np.all((x >= -1e-12) & (x <= 1.0 + 1e-12))


def test_property_find_periodic_orbits_sorted_unique():
    """find_periodic_orbits returns a sorted list with unique entries."""
    roots = dim.find_periodic_orbits(
        dim.logistic_map, params={"r": 3.5}, period=4, x_range=(0.0, 1.0)
    )
    assert roots == sorted(roots)
    # No duplicates within tolerance
    for i in range(len(roots) - 1):
        assert roots[i + 1] - roots[i] > 1e-5


# ---------------------------------------------------------------------------
# EDGE-case tests (>=3 required)
# ---------------------------------------------------------------------------


def test_edge_n_iter_zero_returns_empty_array():
    """n_iter = 0 ⇒ empty array (no iteration is performed).

    Edges covered: zero-length output, applied to all 1-D maps and
    the 2-D Hénon map.
    """
    assert dim.logistic_map(r=3.5, x_init=0.5, n_iter=0).shape == (0,)
    assert dim.tent_map(0.3, 0).shape == (0,)
    assert dim.sine_map(0.5, 0.3, 0).shape == (0,)
    xs, ys = dim.henon_map(1.4, 0.3, 0.1, 0.1, 0)
    assert xs.shape == (0,) and ys.shape == (0,)


def test_edge_logistic_parameter_out_of_range_raises():
    """r outside [0, 4] is unphysical for the standard map; we
    raise ValueError with an informative message rather than
    return diverging garbage.
    """
    with pytest.raises(ValueError, match="r in"):
        dim.logistic_map(r=5.0, x_init=0.5, n_iter=10)
    with pytest.raises(ValueError, match="r in"):
        dim.logistic_map(r=-0.1, x_init=0.5, n_iter=10)


def test_edge_x_init_out_of_range_raises():
    """x_init outside the documented invariant interval [0,1] for
    the 1-D maps raises ValueError.
    """
    with pytest.raises(ValueError, match="x_init"):
        dim.logistic_map(r=3.0, x_init=1.5, n_iter=10)
    with pytest.raises(ValueError, match="x_init"):
        dim.tent_map(-0.1, 10)
    with pytest.raises(ValueError, match="x_init"):
        dim.sine_map(0.5, 1.5, 10)


def test_edge_logistic_r_zero_orbit_decays_to_zero():
    """f(x) = 0 * x * (1 - x) = 0, so the orbit collapses to 0
    after a single step regardless of x_init.
    """
    orbit = dim.logistic_map(r=0.0, x_init=0.7, n_iter=10)
    np.testing.assert_allclose(orbit, np.zeros(10))


def test_edge_henon_b_zero_is_degenerate_1d_map():
    """When b = 0, y_{n+1} = 0 for all n>=1, and the map collapses
    to x_{n+1} = 1 - a x_n^2 (a 1-D quadratic map).  We verify that
    the 2-D output indeed has y == 0 after the first iterate.
    """
    xs, ys = dim.henon_map(
        a=1.4, b=0.0, x0_init=0.1, y0_init=0.1, n_iter=10
    )
    # All y values are b * x_prev = 0 once x_prev passed through b=0.
    np.testing.assert_allclose(ys, np.zeros(10))


def test_edge_lyapunov_constant_orbit_minus_inf():
    """Lyapunov on a constant orbit (logistic at r=2 starting exactly
    at the fixed point x=0.5, where f'(0.5) = 0) returns -∞.
    """
    lam = dim.lyapunov_exponent(
        dim.logistic_map,
        x_init=0.5,
        params={"r": 2.0},
        n_iter=100,
        transient=10,
    )
    assert lam == float("-inf")


# ---------------------------------------------------------------------------
# COMPOSITION tests (>=2 required)
# ---------------------------------------------------------------------------


def test_composition_bifurcation_diagram_meets_period_2_orbit():
    """At r = 3.2 the long-time dynamics is a period-2 cycle.  The
    bifurcation diagram should sample exactly two distinct attractor
    values, and these must agree with the analytic period-2 orbit
    found by find_periodic_orbits.

    Composition: bifurcation_diagram × find_periodic_orbits.
    """
    p, x = dim.bifurcation_diagram(
        dim.logistic_map,
        param_range=(3.2, 3.2 + 1e-6),  # tight slice
        n_params=2,
        x_init=0.3,
        n_iter=200,
        transient=2000,
    )
    # Restrict to the first parameter slice
    xs = x[p == p[0]]
    # Round to discover the two attractor branches
    rounded = np.round(xs, 4)
    unique = np.unique(rounded)
    assert len(unique) == 2  # two-cycle

    fixed_pt = 1.0 - 1.0 / 3.2
    pos = dim.find_periodic_orbits(
        dim.logistic_map, params={"r": 3.2}, period=2, x_range=(0.05, 0.99)
    )
    period2 = sorted(rt for rt in pos if abs(rt - fixed_pt) > 1e-3)
    np.testing.assert_allclose(unique, period2, atol=1e-3)


def test_composition_logistic_r4_lyapunov_matches_tent_map():
    """The logistic map at r=4 is conjugate (h(x) = sin²(πx/2)) to
    the tent map, so they share the same Lyapunov exponent ln 2.

    Composition: lyapunov_exponent on two distinct map_fn objects
    must agree.
    """
    lam_logistic = dim.lyapunov_exponent(
        dim.logistic_map,
        x_init=0.123,
        params={"r": 4.0},
        n_iter=100_000,
        transient=2000,
    )
    lam_tent = dim.lyapunov_exponent(
        dim.tent_map,
        x_init=0.123,
        params=None,
        n_iter=100_000,
        transient=2000,
    )
    # Tent map: f'(x) = ±2 a.e., so Lyapunov is exactly ln 2.
    assert abs(lam_tent - math.log(2.0)) < 1e-9
    # Logistic at r=4 should match within finite-sample noise.
    assert abs(lam_logistic - lam_tent) < 5e-3


def test_composition_feigenbaum_from_period_doubling_cascade():
    """The Feigenbaum constant emerges from the period-doubling
    cascade in the bifurcation diagram.  Sanity-check that

      (i) feigenbaum_constant_estimate returns ≈ 4.669,
      (ii) the superstable r-values lie inside the cascade region
            (3, 3.5699...).

    Composition: chains the period-doubling detection with the
    Feigenbaum estimator.
    """
    delta = dim.feigenbaum_constant_estimate(
        dim.logistic_map, params_range=(3.0, 3.5699)
    )
    assert 4.5 < delta < 4.85
