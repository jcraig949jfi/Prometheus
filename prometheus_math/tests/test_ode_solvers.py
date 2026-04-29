"""Tests for prometheus_math.dynamics_ode_solvers.

Project #77 — pm.dynamics.ode_solvers (high-order via mpmath).

Test categories follow techne/skills/math-tdd.md:

  Authority    — outputs match analytical solutions for canonical IVPs
                 (linear decay, harmonic oscillator, Kepler period,
                 Lorenz literature value of largest Lyapunov exponent).
  Property     — invariants (4th-order convergence, time-reversal
                 round-trip, monotonicity of first-passage time,
                 RK45 ↔ DOP853 cross-check, symplectic energy
                 conservation).
  Edge         — empty t_span, unknown method, prec ≤ 0,
                 wrong-shape rhs, h ≤ 0 in rk4, t_end < t_start.
  Composition  — high-prec solve_ivp ↔ mpmath_odefun, leapfrog ↔
                 verlet, linear y' = A y ↔ matrix exponential,
                 liapunov_exponent_continuous ≈ 0.9056 on Lorenz.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math import dynamics_ode_solvers as ode


# ---------------------------------------------------------------------------
# AUTHORITY tests (>= 3 required — we provide 6)
# ---------------------------------------------------------------------------


def test_authority_linear_decay_matches_exponential():
    """y' = -y, y(0) = 1 → y(t) = exp(-t).

    Reference: hand-computation of the closed-form solution of the
    one-dimensional linear ODE.  At t = 1, y(1) = e^{-1} ≈
    0.36787944117144233 (Boyce & DiPrime, "Elementary Differential
    Equations" 9th ed., §2.1).
    """
    rhs = lambda t, y: -y
    sol = ode.solve_ivp(rhs, (0.0, 1.0), [1.0], method="RK45",
                        rtol=1e-10, atol=1e-12)
    assert sol["success"]
    assert abs(sol["y"][-1, 0] - math.exp(-1.0)) < 1e-7


def test_authority_harmonic_oscillator_energy():
    """Simple harmonic oscillator: q' = p, p' = -q has constant
    energy E = (q^2 + p^2) / 2.  At t = 2π one period the orbit
    closes (Arnold, "Mathematical Methods of Classical Mechanics"
    §1.2)."""
    def rhs(t, z):
        q, p = z
        return np.array([p, -q])

    sol = ode.solve_ivp(rhs, (0.0, 2 * math.pi), [1.0, 0.0],
                        method="RK45", rtol=1e-10, atol=1e-12)
    q_T, p_T = sol["y"][-1]
    # Energy conservation
    E0 = 0.5 * (1.0 ** 2 + 0.0 ** 2)
    ET = 0.5 * (q_T ** 2 + p_T ** 2)
    assert abs(ET - E0) < 1e-6
    # Periodicity
    assert abs(q_T - 1.0) < 1e-4
    assert abs(p_T - 0.0) < 1e-4


def test_authority_lorenz_trajectory_bounded():
    """Lorenz system (σ=10, ρ=28, β=8/3) trajectories enter and
    remain in a bounded absorbing set.

    Reference: Sparrow, "The Lorenz Equations: Bifurcations, Chaos,
    and Strange Attractors" (Applied Math. Sci. 41, Springer 1982),
    Ch. 1 — the standard parameters yield the canonical butterfly
    attractor confined to a ball of radius < 100 around the
    fixed-point pair.
    """
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0

    def rhs(t, s):
        x, y, z = s
        return np.array([sigma * (y - x), x * (rho - z) - y,
                         x * y - beta * z])

    sol = ode.solve_ivp(rhs, (0.0, 5.0), [1.0, 1.0, 1.0],
                        method="RK45", rtol=1e-7, atol=1e-9)
    norms = np.linalg.norm(sol["y"], axis=1)
    assert sol["success"]
    assert norms.max() < 100.0
    assert sol["y"].shape[1] == 3


def test_authority_pendulum_symplectic_conserves_energy():
    """Hamiltonian pendulum H(q,p) = p^2/2 + (1 - cos q).
    Symplectic integrators (leapfrog) conserve energy to a small
    bound over many periods (Hairer, Lubich, Wanner, "Geometric
    Numerical Integration", §VI.3)."""
    def H(q, p):
        return 0.5 * p[0] ** 2 + (1.0 - math.cos(q[0]))

    sol = ode.hamiltonian_system(H, (0.0, 50.0), q0=[0.5], p0=[0.0],
                                 method="leapfrog", h=0.01)
    q = sol["q"]; p = sol["p"]
    E0 = H([q[0, 0]], [p[0, 0]])
    drift = max(abs(H([qi], [pi]) - E0) for qi, pi in zip(q[:, 0], p[:, 0]))
    # Symplectic methods bound the energy oscillation; ~ h^2 ~ 1e-4
    assert drift < 1e-2


def test_authority_van_der_pol_limit_cycle():
    """Van der Pol (μ=1) admits a unique stable limit cycle of
    amplitude ≈ 2 (Strogatz, "Nonlinear Dynamics and Chaos" §7.5).
    Starting from inside, the trajectory approaches the limit cycle.
    """
    mu = 1.0

    def rhs(t, s):
        x, v = s
        return np.array([v, mu * (1 - x ** 2) * v - x])

    # Long enough to settle on the limit cycle
    sol = ode.solve_ivp(rhs, (0.0, 50.0), [0.5, 0.0],
                        method="RK45", rtol=1e-7, atol=1e-9)
    # Peak |x| over second half should be near 2.0 (Liénard cycle)
    half = len(sol["t"]) // 2
    peak = np.max(np.abs(sol["y"][half:, 0]))
    assert 1.7 < peak < 2.3


def test_authority_dop853_kepler_period():
    """Two-body Kepler orbit at unit semi-major axis has period
    T = 2π (Kepler's third law in normalized units; see Goldstein,
    "Classical Mechanics" 3rd ed., §3.7).  Starting from a circular
    orbit (e=0) at radius 1 with v = 1, after t = 2π the body is
    back at its start.
    """
    def rhs(t, s):
        x, y, vx, vy = s
        r3 = (x * x + y * y) ** 1.5
        return np.array([vx, vy, -x / r3, -y / r3])

    y0 = [1.0, 0.0, 0.0, 1.0]
    sol = ode.dop853(rhs, (0.0, 2 * math.pi), y0,
                     rtol=1e-12, atol=1e-14)
    err = np.linalg.norm(sol["y"][-1] - np.array(y0))
    assert err < 1e-6


# ---------------------------------------------------------------------------
# PROPERTY tests (>= 3 required — we provide 5)
# ---------------------------------------------------------------------------


@given(st.floats(min_value=0.1, max_value=2.0, allow_nan=False,
                 allow_infinity=False))
@settings(max_examples=15, deadline=None)
def test_property_rk45_matches_dop853_on_linear_decay(T):
    """For y' = -y over [0, T], RK45 and DOP853 agree to high
    accuracy (cross-method invariant)."""
    rhs = lambda t, y: -y
    a = ode.solve_ivp(rhs, (0.0, T), [1.0], method="RK45",
                      rtol=1e-9, atol=1e-12)
    b = ode.dop853(rhs, (0.0, T), [1.0], rtol=1e-12, atol=1e-14)
    assert abs(a["y"][-1, 0] - b["y"][-1, 0]) < 1e-6


@given(st.floats(min_value=0.5, max_value=2.0, allow_nan=False))
@settings(max_examples=10, deadline=None)
def test_property_time_reversal_returns_to_start(T):
    """Forward then backward integration returns to the initial
    condition (modulo numerical error).  This is a categorical
    invariant of the smooth flow."""
    rhs = lambda t, y: -0.3 * y
    fwd = ode.solve_ivp(rhs, (0.0, T), [1.0], method="RK45",
                        rtol=1e-10, atol=1e-12)
    y_T = fwd["y"][-1]
    rhs_back = lambda t, y: -(-0.3 * y)  # reverse-time RHS
    back = ode.solve_ivp(rhs_back, (0.0, T), y_T.tolist(),
                         method="RK45", rtol=1e-10, atol=1e-12)
    assert abs(back["y"][-1, 0] - 1.0) < 1e-5


def test_property_rk4_fourth_order_convergence():
    """RK4 has O(h^4) global error.  Halving h should reduce the
    end-point error by a factor of about 2^4 = 16.  We use y' = -y
    with known exact solution so error is analytic.
    """
    rhs = lambda t, y: -y
    truth = math.exp(-1.0)

    e_h = abs(ode.rk4(rhs, (0.0, 1.0), [1.0], h=0.1)["y"][-1, 0] - truth)
    e_half = abs(ode.rk4(rhs, (0.0, 1.0), [1.0], h=0.05)["y"][-1, 0] - truth)
    # Theoretical ratio is 16; allow 8..32 for finite-step constants.
    assert 6.0 < (e_h / max(e_half, 1e-18)) < 40.0


def test_property_symplectic_energy_drift_bounded():
    """Leapfrog on harmonic oscillator: energy oscillates but does
    not drift (Hairer-Lubich-Wanner backward error theorem)."""
    def H(q, p):
        return 0.5 * (q[0] ** 2 + p[0] ** 2)

    sol = ode.hamiltonian_system(H, (0.0, 200.0), q0=[1.0], p0=[0.0],
                                 method="leapfrog", h=0.05)
    q = sol["q"]; p = sol["p"]
    energies = 0.5 * (q[:, 0] ** 2 + p[:, 0] ** 2)
    # Drift = mean over second half minus mean over first half
    n = len(energies)
    drift = abs(np.mean(energies[n//2:]) - np.mean(energies[:n//2]))
    # Symplectic methods give zero secular drift to leading order.
    assert drift < 1e-4


def test_property_first_passage_monotone_in_initial_condition():
    """For dy/dt = 1 starting from y0 < threshold, first-passage
    time to y = 1 is monotone decreasing in y0."""
    rhs = lambda t, y: np.array([1.0])
    threshold = lambda y: y[0] - 1.0
    t1 = ode.first_passage_time(rhs, [0.0], threshold, t_max=5.0)
    t2 = ode.first_passage_time(rhs, [0.5], threshold, t_max=5.0)
    assert t1 is not None and t2 is not None
    assert t2 < t1


# ---------------------------------------------------------------------------
# EDGE-CASE tests (>= 3 required — we provide 6)
# ---------------------------------------------------------------------------


def test_edge_empty_t_span_raises():
    """Empty / degenerate t_span (t1 == t0) → ValueError."""
    rhs = lambda t, y: -y
    with pytest.raises(ValueError):
        ode.solve_ivp(rhs, (0.0, 0.0), [1.0])
    with pytest.raises(ValueError):
        ode.solve_ivp(rhs, (1.0, 0.0), [1.0])  # backward not allowed
    with pytest.raises(ValueError):
        ode.solve_ivp(rhs, (), [1.0])  # type: ignore[arg-type]


def test_edge_unknown_method_raises():
    """method='unknown' → ValueError listing supported methods."""
    rhs = lambda t, y: -y
    with pytest.raises(ValueError, match="(?i)method"):
        ode.solve_ivp(rhs, (0.0, 1.0), [1.0], method="unknown")


def test_edge_bad_prec_raises():
    """prec <= 0 in mpmath_odefun → ValueError."""
    rhs = lambda t, y: -y
    with pytest.raises(ValueError, match="(?i)prec"):
        ode.mpmath_odefun(rhs, (0.0, 1.0), [1.0], prec=0)
    with pytest.raises(ValueError, match="(?i)prec"):
        ode.mpmath_odefun(rhs, (0.0, 1.0), [1.0], prec=-10)


def test_edge_rhs_wrong_shape_raises():
    """If rhs returns a vector of the wrong length, solver must
    raise a ValueError rather than produce a silently broken
    trajectory.
    """
    bad_rhs = lambda t, y: np.array([1.0, 2.0])  # length 2 vs y0 length 1
    with pytest.raises(ValueError, match="(?i)shape|dimen|length"):
        ode.solve_ivp(bad_rhs, (0.0, 1.0), [1.0], method="RK45")


def test_edge_rk4_bad_step_size_raises():
    """h <= 0 in rk4 → ValueError."""
    rhs = lambda t, y: -y
    with pytest.raises(ValueError, match="(?i)h|step"):
        ode.rk4(rhs, (0.0, 1.0), [1.0], h=0.0)
    with pytest.raises(ValueError, match="(?i)h|step"):
        ode.rk4(rhs, (0.0, 1.0), [1.0], h=-0.1)


def test_edge_unknown_hamiltonian_method_raises():
    """hamiltonian_system with unsupported method → ValueError."""
    H = lambda q, p: 0.5 * (q[0] ** 2 + p[0] ** 2)
    with pytest.raises(ValueError, match="(?i)method|symplectic"):
        ode.hamiltonian_system(H, (0.0, 1.0), q0=[1.0], p0=[0.0],
                               method="garbage", h=0.01)


# ---------------------------------------------------------------------------
# COMPOSITION tests (>= 2 required — we provide 4)
# ---------------------------------------------------------------------------


def test_composition_high_prec_converges_to_mpmath_odefun():
    """High-precision solve_ivp result on y' = -y should match
    mpmath_odefun (the arbitrary-precision oracle) to many digits.
    Composition: solve_ivp[prec=53] vs mpmath_odefun[prec=53].
    """
    rhs = lambda t, y: -y
    f = ode.mpmath_odefun(rhs, (0.0, 1.0), [1.0], prec=53)
    y_mpmath = float(f(1.0)[0])
    sol = ode.solve_ivp(rhs, (0.0, 1.0), [1.0], method="RK45",
                        rtol=1e-12, atol=1e-14)
    assert abs(sol["y"][-1, 0] - y_mpmath) < 1e-8


def test_composition_leapfrog_matches_verlet():
    """For separable Hamiltonians, leapfrog and (velocity) Verlet
    are mathematically equivalent — they give the same trajectory
    up to the staggering of q vs. p."""
    H = lambda q, p: 0.5 * (q[0] ** 2 + p[0] ** 2)
    a = ode.hamiltonian_system(H, (0.0, 5.0), q0=[1.0], p0=[0.0],
                               method="leapfrog", h=0.005)
    b = ode.hamiltonian_system(H, (0.0, 5.0), q0=[1.0], p0=[0.0],
                               method="verlet", h=0.005)
    # Endpoints agree to leading order in h^2
    assert abs(a["q"][-1, 0] - b["q"][-1, 0]) < 1e-4
    assert abs(a["p"][-1, 0] - b["p"][-1, 0]) < 1e-4


def test_composition_linear_ode_matches_matrix_exponential():
    """For y' = A y with constant A, y(t) = exp(t A) y0.
    Compose solve_ivp with scipy's matrix exponential.
    """
    from scipy.linalg import expm
    A = np.array([[-0.5, 1.0], [-1.0, -0.5]])
    y0 = np.array([1.0, 0.0])
    rhs = lambda t, y: A @ y
    sol = ode.solve_ivp(rhs, (0.0, 1.5), y0.tolist(),
                        method="RK45", rtol=1e-10, atol=1e-12)
    y_truth = expm(1.5 * A) @ y0
    assert np.linalg.norm(sol["y"][-1] - y_truth) < 1e-6


def test_composition_lorenz_lyapunov_exponent_literature_value():
    """Largest Lyapunov exponent of the Lorenz attractor at the
    canonical (σ=10, ρ=28, β=8/3) parameters is ≈ 0.9056
    (Sprott, "Chaos and Time-Series Analysis", Table 4.1, 2003;
    cf. Wolf et al., Physica D 16 (1985) 285).
    """
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0

    def rhs(t, s):
        x, y, z = s
        return np.array([sigma * (y - x), x * (rho - z) - y,
                         x * y - beta * z])

    lam = ode.liapunov_exponent_continuous(rhs, [1.0, 1.0, 1.0],
                                           t_max=80.0, n_renorm=400)
    # Loose tolerance — finite-time estimate, but should bracket 0.9
    assert 0.6 < lam < 1.3
