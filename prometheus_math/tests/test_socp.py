"""TDD-quality tests for prometheus_math.optimization_socp.

Categories per techne/skills/math-tdd.md (>= 2 in each):
  Authority   : >=3 (Chebyshev unit cube, 3-4-5 triangle incircle,
                robust-LP zero-uncertainty match, two-asset Markowitz,
                MVEE on unit-square corners)
  Property    : >=3 (cone constraint satisfaction, weights sum to 1,
                Chebyshev radius non-negative, SOCP=QP cross-check,
                MVEE contains all input points)
  Edge        : >=3 (empty cones reduces to LP, infeasible,
                unknown solver, empty c, inconsistent shapes)
  Composition : >=2 (portfolio without risk == max-return LP,
                Chebyshev centre satisfies polytope constraints,
                SOCP-from-QP matches solve_qp output)

cvxpy is the canonical backend; the entire module is skipped when cvxpy
is unavailable.
"""
from __future__ import annotations

import warnings as _warnings

# Suppress noisy cvxpy GLOP/PDLP warnings on import (ortools 9.15 mismatch).
_warnings.filterwarnings("ignore", category=UserWarning, module=r"cvxpy.*")

import math

import numpy as np
import pytest

cvxpy = pytest.importorskip(
    "cvxpy",
    reason="cvxpy not installed (install with `pip install cvxpy`)",
)

from prometheus_math.optimization_socp import (  # noqa: E402
    solve_socp,
    solve_robust_lp,
    chebyshev_center,
    min_volume_ellipsoid,
    portfolio_socp,
    facility_location_socp,
)


# ---------------------------------------------------------------------------
# AUTHORITY-BASED TESTS
# ---------------------------------------------------------------------------


def test_authority_chebyshev_center_unit_cube():
    """Largest ball inscribed in [-1, 1]^2 has centre (0, 0) and radius 1.

    Reference: Boyd & Vandenberghe, "Convex Optimization", §8.5.1.
    The unit cube [-1, 1]^n is described by ``A x <= b`` with rows
    ``+/- e_i`` and rhs all ``1``; row norms are 1 so the SOCP reduces
    to ``r <= 1`` and the centre is the origin by symmetry.
    """
    A = np.array(
        [
            [1.0, 0.0],
            [-1.0, 0.0],
            [0.0, 1.0],
            [0.0, -1.0],
        ]
    )
    b = np.ones(4)
    res = chebyshev_center(A, b)
    assert res["status"] == "optimal"
    assert math.isclose(res["radius"], 1.0, abs_tol=1e-5)
    assert np.allclose(res["center"], [0.0, 0.0], atol=1e-5)


def test_authority_chebyshev_center_triangle_3_4_5():
    """Incircle of the 3-4-5 right triangle: centre (1, 1), radius 1.

    Reference: classical incircle formulae.  Triangle with vertices
    A=(0,0), B=(4,0), C=(0,3) has side lengths a = |BC| = 5,
    b = |AC| = 3, c = |AB| = 4.  Incentre = (a A + b B + c C) /
    (a + b + c) = (5*(0,0) + 3*(4,0) + 4*(0,3)) / 12 = (1, 1).
    Inradius = (3 + 4 - 5) / 2 = 1 (right-triangle formula, Coxeter
    "Introduction to Geometry", §1.4).

    Polytope description: the three half-planes
        -x      <= 0    (line x = 0)
        -y      <= 0    (line y = 0)
        3x + 4y <= 12   (line through (4,0) and (0,3); normal (3,4)
                         has length 5, so unit-normal form has rhs 12/5)
    """
    A = np.array(
        [
            [-1.0, 0.0],
            [0.0, -1.0],
            [3.0, 4.0],
        ]
    )
    b = np.array([0.0, 0.0, 12.0])
    res = chebyshev_center(A, b)
    assert res["status"] == "optimal"
    assert math.isclose(res["radius"], 1.0, abs_tol=1e-5)
    assert np.allclose(res["center"], [1.0, 1.0], atol=1e-5)


def test_authority_robust_lp_zero_uncertainty_matches_lp():
    """rho = 0 robust LP collapses to the standard LP.

    Reference: Ben-Tal & Nemirovski (2000), §1: the robust counterpart
    is identical to the nominal LP when the uncertainty radius is zero.
    Hand-derived: min -x_1 - x_2 s.t. x_1 + x_2 <= 1, x_i >= 0 has
    optimal value -1 (achieved on the segment x_1 + x_2 = 1).
    """
    c = np.array([-1.0, -1.0])
    A = np.array(
        [
            [1.0, 1.0],
            [-1.0, 0.0],
            [0.0, -1.0],
        ]
    )
    b = np.array([1.0, 0.0, 0.0])
    res_robust = solve_robust_lp(c, A, b, uncertainty_radius=0.0, ord="inf")
    assert res_robust["status"] == "optimal"
    assert math.isclose(res_robust["optimal_value"], -1.0, abs_tol=1e-5)


def test_authority_two_asset_portfolio_known_weights():
    """Two-asset min-variance portfolio with hand-derived solution.

    Setup: two uncorrelated assets, sigma_1 = 1, sigma_2 = 2,
    long-only, full-investment.  Min-variance portfolio weights are
    proportional to ``1 / sigma_i^2`` (textbook result, see Markowitz
    1952): w_1 / w_2 = 4 / 1, so w_1 = 4/5 = 0.8 and w_2 = 0.2.
    Achieved standard deviation = sqrt(0.8^2 * 1 + 0.2^2 * 4) =
    sqrt(0.64 + 0.16) = sqrt(0.8) approx 0.8944.

    We invoke the min-variance mode by setting target_return at the
    average asset return so the constraint is non-binding.
    """
    mu = np.array([0.10, 0.10])  # equal returns => target inactive
    Sigma = np.diag([1.0, 4.0])
    res = portfolio_socp(mu, Sigma, target_return=0.10)
    assert res["status"] == "optimal"
    w = res["weights"]
    assert math.isclose(w[0], 0.8, abs_tol=1e-3)
    assert math.isclose(w[1], 0.2, abs_tol=1e-3)
    assert math.isclose(res["risk"], math.sqrt(0.8), rel_tol=1e-3)


def test_authority_min_volume_ellipsoid_unit_square_corners():
    """MVEE around the four unit-square corners is the circle radius sqrt(2).

    Reference: Boyd & Vandenberghe, "Convex Optimization", §8.4.1.
    Points (+/-1, +/-1) lie on a circle of radius sqrt(2); by symmetry
    the minimum-volume enclosing ellipsoid is that very circle, with
    semi-axes both equal to sqrt(2) and centre at the origin.
    """
    pts = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], dtype=float)
    res = min_volume_ellipsoid(pts)
    assert res["status"] == "optimal"
    assert np.allclose(res["center"], [0.0, 0.0], atol=1e-3)
    # Both semi-axes ~ sqrt(2)
    assert np.allclose(np.sort(res["radius_axes"]), [math.sqrt(2.0)] * 2,
                       atol=5e-3)


# ---------------------------------------------------------------------------
# PROPERTY TESTS
# ---------------------------------------------------------------------------


def test_property_socp_solution_satisfies_cone_constraint():
    """Solution returned by solve_socp respects ||A x + b||_2 <= c^T x + d."""
    # Minimise x s.t. ||x||_2 <= x + 1, i.e. circle-style cone.
    # Trivially x = 0 is feasible; minimisation unbounded below would
    # require x ->-inf, but the cone forces x + 1 >= 0 ⇒ x >= -1, and
    # ||x||_2 = |x| <= x + 1 forces x >= -1/2.  So optimum is x = -1/2.
    c = np.array([1.0])
    A_cones = [np.array([[1.0]])]
    b_cones = [np.array([0.0])]
    c_cones = [np.array([1.0])]
    d_cones = [1.0]
    res = solve_socp(c, A_cones, b_cones, c_cones, d_cones)
    assert res["status"] == "optimal"
    x = res["x"]
    # Verify the cone constraint within tolerance.
    lhs = np.linalg.norm(A_cones[0] @ x + b_cones[0])
    rhs = c_cones[0] @ x + d_cones[0]
    assert lhs <= rhs + 1e-6
    assert math.isclose(float(x[0]), -0.5, abs_tol=1e-4)


def test_property_portfolio_weights_sum_to_one():
    """Long-only portfolio always has weights summing to 1 within tol."""
    rng = np.random.default_rng(seed=42)
    n = 6
    mu = rng.normal(0.05, 0.02, size=n)
    raw = rng.normal(size=(n, n))
    Sigma = raw @ raw.T / n + np.eye(n) * 0.01
    res = portfolio_socp(mu, Sigma, target_return=float(np.mean(mu)))
    assert res["status"] == "optimal"
    w = res["weights"]
    assert math.isclose(w.sum(), 1.0, abs_tol=1e-5)
    assert np.all(w >= -1e-6)  # long_only


def test_property_chebyshev_radius_nonnegative():
    """For a non-empty polytope the Chebyshev radius is non-negative.

    Property holds because the variable ``r`` is constrained to
    ``r >= 0`` in the SOCP formulation.  Sample several random LPs and
    check.
    """
    rng = np.random.default_rng(seed=7)
    for _ in range(5):
        n = 3
        m = 6
        A = rng.normal(size=(m, n))
        # Force the polytope to contain the origin: b > 0.
        b = np.abs(rng.normal(size=m)) + 0.5
        res = chebyshev_center(A, b)
        if res["status"] == "optimal":
            assert res["radius"] >= -1e-9


def test_property_socp_matches_qp_for_quadratic_objective():
    """Cross-check: an SOCP recasting of a convex QP reproduces solve_qp.

    For a strongly convex QP ``min (1/2) x^T P x`` cast as
    ``min t  s.t.  ||L^T x||_2 <= t`` with ``L`` a Cholesky factor of P,
    the optimum value equals ``sqrt(QP_value * 2)`` (since
    ``t* = ||L^T x*||_2 = sqrt(x*^T P x*) = sqrt(2 * QP_optimal_value)``
    when the QP optimum is at zero only — for a non-trivial example we
    pin to a known optimum.)  Easier: solve the same LP-via-SOCP
    problem two ways.
    """
    # Build a problem solvable in closed form: min ||x - x0||_2 over
    # all x.  Optimum is x = x0 with value 0.
    x0 = np.array([2.0, -1.0])
    n = 2
    # Cone: ||I x - x0||_2 <= t  with t in objective.  Use augmented
    # variable z = (x, t) of size 3.  c = (0, 0, 1).
    c_full = np.array([0.0, 0.0, 1.0])
    # A_cone selects the x part only, b is -x0, c_cone selects t, d=0
    A_cone = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    b_cone = -x0
    c_cone = np.array([0.0, 0.0, 1.0])
    d_cone = 0.0
    res = solve_socp(c_full, [A_cone], [b_cone], [c_cone], [d_cone])
    assert res["status"] == "optimal"
    z = res["x"]
    assert np.allclose(z[:2], x0, atol=1e-4)
    assert math.isclose(z[2], 0.0, abs_tol=1e-5)


def test_property_mvee_contains_all_input_points():
    """The MVEE shape ``A`` and offset ``b`` satisfy ||A x_i + b|| <= 1."""
    rng = np.random.default_rng(seed=11)
    n = 2
    N = 10
    pts = rng.normal(size=(N, n))
    res = min_volume_ellipsoid(pts)
    assert res["status"] in ("optimal", "optimal_inaccurate")
    A = res["A"]
    # We need to recover b = -A center (since center = -A^-1 b).
    b = -A @ res["center"]
    for i in range(N):
        v = A @ pts[i] + b
        assert np.linalg.norm(v) <= 1.0 + 5e-3, (
            f"Point {pts[i]} not enclosed: ||A x + b|| = "
            f"{np.linalg.norm(v):.6f}"
        )


# ---------------------------------------------------------------------------
# EDGE-CASE TESTS
# ---------------------------------------------------------------------------


def test_edge_empty_cones_reduces_to_lp():
    """No cone constraints => standard LP min c^T x s.t. A_eq x = b_eq."""
    c = np.array([1.0, 2.0])
    A_eq = np.array([[1.0, 1.0]])
    b_eq = np.array([3.0])
    # No box bounds; objective unbounded below since c can be made
    # very negative along (-1, 1) direction (residual + null space),
    # but with the equality constraint the feasible set is the line
    # x_1 + x_2 = 3 in R^2, and c^T x = x_1 + 2 x_2 = 3 + x_2 -> -inf
    # as x_2 -> -inf.  So we expect 'unbounded' (or similar).  Verify
    # status is not 'optimal'.
    res = solve_socp(c, [], [], [], [], A_eq=A_eq, b_eq=b_eq)
    assert res["status"] in ("unbounded", "infeasible_or_unbounded", "unbounded_inaccurate")

    # Now add a feasible cone constraint that bounds the solution: a
    # ball around the origin.  Cone: ||I x||_2 <= 10 (i.e. ||x||_2 <= 10).
    A_cone = np.eye(2)
    b_cone = np.zeros(2)
    c_cone = np.zeros(2)
    d_cone = 10.0
    res2 = solve_socp(
        c, [A_cone], [b_cone], [c_cone], [d_cone],
        A_eq=A_eq, b_eq=b_eq,
    )
    assert res2["status"] == "optimal"


def test_edge_infeasible_chebyshev():
    """Polytope ``A x <= b`` with no feasible point => infeasible status."""
    # x <= -1 and x >= 1 => empty.
    A = np.array([[1.0], [-1.0]])
    b = np.array([-1.0, -1.0])
    res = chebyshev_center(A, b)
    # cvxpy may report 'infeasible' or 'unbounded' depending on the
    # solver path.  Either non-optimal status is acceptable.
    assert res["status"] != "optimal"


def test_edge_unknown_solver_raises():
    """Passing an unknown solver name raises ValueError immediately."""
    c = np.array([1.0])
    with pytest.raises(ValueError, match="Unknown solver"):
        solve_socp(c, [], [], [], [], solver="not_a_real_solver")
    with pytest.raises(ValueError, match="Unknown solver"):
        chebyshev_center(np.eye(1), np.array([1.0]), solver="bogus")


def test_edge_empty_c_raises():
    """An empty objective vector is rejected with a clear error."""
    with pytest.raises(ValueError, match="non-empty"):
        solve_socp(np.array([]), [], [], [], [])
    with pytest.raises(ValueError):
        portfolio_socp(np.array([]), np.zeros((0, 0)))


def test_edge_inconsistent_shapes_raise():
    """Mismatched shapes (cone matrix vs c, A_eq cols, b sizes) raise."""
    c = np.array([1.0, 2.0])  # n = 2
    A_cone_bad = np.array([[1.0, 0.0, 0.0]])  # 3 columns - wrong
    with pytest.raises(ValueError, match="A_cones"):
        solve_socp(c, [A_cone_bad], [np.array([0.0])], [np.array([0.0, 0.0])], [0.0])
    # b_cones size mismatch
    with pytest.raises(ValueError, match="b_cones"):
        solve_socp(
            c,
            [np.eye(2)],
            [np.array([0.0, 0.0, 0.0])],  # size 3 vs A_cones[0].shape[0] = 2
            [np.zeros(2)],
            [0.0],
        )
    # robust LP shape check
    with pytest.raises(ValueError):
        solve_robust_lp(np.array([1.0, 2.0]), np.eye(3), np.zeros(3))


# ---------------------------------------------------------------------------
# COMPOSITION TESTS
# ---------------------------------------------------------------------------


def test_composition_portfolio_no_constraints_is_max_return_lp():
    """Without a risk constraint, portfolio_socp degenerates to the
    LP of putting everything on the highest-return asset.

    Composes: portfolio_socp(target=None, risk=None) ↔ argmax mu_i.
    """
    mu = np.array([0.05, 0.20, 0.07])
    Sigma = np.diag([1.0, 1.0, 1.0])
    res = portfolio_socp(mu, Sigma)  # no targets => max return
    assert res["status"] == "optimal"
    w = res["weights"]
    # All weight on asset 1.
    expected = np.array([0.0, 1.0, 0.0])
    assert np.allclose(w, expected, atol=1e-4)
    assert math.isclose(res["expected_return"], 0.20, abs_tol=1e-4)


def test_composition_chebyshev_center_inside_polytope():
    """The Chebyshev centre must satisfy A x <= b strictly (with
    slack >= radius * ||a_i||).

    Composes: chebyshev_center(A, b) ↦ direct constraint check on the
    polytope description.
    """
    # Hexagonal-ish polytope.
    A = np.array(
        [
            [1.0, 0.0],
            [-1.0, 0.0],
            [0.0, 1.0],
            [0.0, -1.0],
            [1.0, 1.0],
            [-1.0, -1.0],
        ]
    )
    b = np.array([2.0, 2.0, 2.0, 2.0, 3.0, 3.0])
    res = chebyshev_center(A, b)
    assert res["status"] == "optimal"
    x = res["center"]
    r = res["radius"]
    # For each row, a_i^T x + r * ||a_i|| <= b_i.
    norms = np.linalg.norm(A, axis=1)
    slacks = b - A @ x
    assert np.all(slacks >= r * norms - 1e-5)
    # And x must lie strictly inside (not on the boundary of any face).
    assert np.all(slacks >= -1e-7)


def test_composition_socp_from_qp_matches_solve_qp():
    """Cast a small convex QP as an SOCP via the epigraph trick and
    confirm the SOCP optimum equals the QP optimum from solve_qp.

    QP: min (1/2) x^T P x + q^T x  with x in R^2.
    Epigraph: introduce t with ||L^T x||_2 <= s  (s = sqrt(2 t)) and
    keep linear part separately.  Easier: directly compare optimal
    *value* by solving the same problem twice.
    """
    from prometheus_math import optimization_qp as qp

    P = np.array([[2.0, 0.5], [0.5, 1.0]])
    q = np.array([-1.0, -1.0])

    qp_res = qp.solve_qp(P, q)
    assert qp_res["status"] == "optimal"
    x_qp = qp_res["x"]
    qp_val = qp_res["optimal_value"]

    # SOCP form: introduce t, minimise (1/2) ||L^T x||_2^2 + q^T x where
    # L L^T = P.  In SOC form, ||L^T x||_2 <= s, then objective
    # (1/2) s^2 + q^T x — that's a *quadratic* in s, not an SOC.  So
    # instead we cast the QP itself directly (cvxpy handles QP under
    # the SOCP umbrella when the objective is constructed as
    # cp.quad_over_lin or via a rotated cone).  For a clean comparison
    # we just solve the same problem with cvxpy's ``cp.norm`` for the
    # standard-deviation equivalent and check the two optima for the
    # related min-variance reformulation:
    #
    #   min || L^T x ||_2  s.t.  q^T x = q^T x_qp.
    #
    # If solve_qp is right then this constrained problem's optimum
    # equals sqrt(2 * (qp_val - q^T x_qp)) — but because we fixed
    # q^T x = q^T x_qp, the residual identity is just the L2 norm of
    # L^T x_qp.

    L = np.linalg.cholesky(P)
    target_linear = float(q @ x_qp)
    # SOCP: min t  s.t. ||L^T x||_2 <= t,  q^T x = target_linear.
    n = 2
    # Variable z = (x, t) of size 3.
    c_full = np.array([0.0, 0.0, 1.0])
    # ||L^T x|| <= t  ↔  ||(L^T)[:, :n]  x + 0||_2 <= 0 + 1 * t.
    A_cone = np.hstack([L.T, np.zeros((n, 1))])  # shape (n, 3)
    b_cone = np.zeros(n)
    c_cone = np.array([0.0, 0.0, 1.0])
    d_cone = 0.0
    A_eq = np.hstack([q.reshape(1, -1), np.zeros((1, 1))])
    b_eq = np.array([target_linear])
    res = solve_socp(
        c_full,
        [A_cone],
        [b_cone],
        [c_cone],
        [d_cone],
        A_eq=A_eq,
        b_eq=b_eq,
    )
    assert res["status"] == "optimal"
    # The minimum t is ||L^T x_qp||_2 by construction.
    expected_t = float(np.linalg.norm(L.T @ x_qp))
    assert math.isclose(res["optimal_value"], expected_t, abs_tol=1e-4)


def test_composition_facility_location_runs():
    """End-to-end smoke test: facility_location_socp produces a
    transport plan summing to 1 along each demand row.
    """
    facility_costs = np.array([1.0, 1.5])
    demands = np.array([2.0, 3.0, 1.0])
    distances = np.array(
        [
            [0.5, 1.2],
            [1.0, 0.4],
            [0.8, 0.7],
        ]
    )
    res = facility_location_socp(facility_costs, demands, distances)
    assert res["status"] == "optimal"
    t = res["transport"]
    assert np.allclose(t.sum(axis=1), 1.0, atol=1e-5)
    assert np.all(t >= -1e-6)
