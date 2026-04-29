"""TDD-quality tests for prometheus_math.optimization_qp.

Categories per techne/skills/math-tdd.md:
  Authority   : ≥3 (hand-computed canonical QP solutions / SVM dual)
  Property    : ≥3 (constraint satisfaction, determinism, box-equiv,
                lasso shrinkage, convexity)
  Edge        : ≥3 (empty, non-symmetric P, non-PSD P, infeasible,
                empty x, unknown solver)
  Composition : ≥2 (lstsq agreement, quantile=0.5 ≈ L1 median,
                lasso recovers sparse signal)

Reference values are hand-computed via the optimality conditions of
each QP and cited in each test docstring.

cvxpy is the canonical solver here. Tests skip with a clear message
when cvxpy is unavailable. The ``scipy`` solver is exercised separately
where its lower precision is acceptable.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.registry import is_available
from prometheus_math import optimization_qp as qp


CVXPY_AVAILABLE = is_available("cvxpy")
SCIPY_AVAILABLE = is_available("scipy")

requires_cvxpy = pytest.mark.skipif(
    not CVXPY_AVAILABLE,
    reason="cvxpy not installed (install with `pip install cvxpy`)",
)
requires_scipy = pytest.mark.skipif(
    not SCIPY_AVAILABLE,
    reason="scipy not installed",
)


# ---------------------------------------------------------------------------
# AUTHORITY-BASED TESTS (hand-derived canonical solutions)
# ---------------------------------------------------------------------------


@requires_cvxpy
def test_authority_trivial_qp():
    """min (1/2) x^2  →  optimal x = 0, value = 0.

    Reference: derivative dL/dx = x = 0. Verified against textbook
    "Convex Optimization", Boyd & Vandenberghe, §4.4.
    """
    P = np.array([[1.0]])
    q = np.array([0.0])
    res = qp.solve_qp(P, q)
    assert res["status"] == "optimal"
    assert math.isclose(float(res["x"][0]), 0.0, abs_tol=1e-7)
    assert math.isclose(res["optimal_value"], 0.0, abs_tol=1e-9)


@requires_cvxpy
def test_authority_qp_with_linear_term():
    """min (1/2) x^2 - 3x  →  x* = 3, f* = -4.5.

    Reference: ∂/∂x [(1/2)x² - 3x] = x - 3 = 0 ⇒ x = 3.
    f(3) = 4.5 - 9 = -4.5. (Hand calculation.)
    """
    P = np.array([[1.0]])
    q = np.array([-3.0])
    res = qp.solve_qp(P, q)
    assert res["status"] == "optimal"
    assert math.isclose(float(res["x"][0]), 3.0, abs_tol=1e-4)
    assert math.isclose(res["optimal_value"], -4.5, abs_tol=1e-4)


@requires_cvxpy
def test_authority_constrained_qp():
    """min x^2 s.t. x >= 1  →  x* = 1, f* = 1.

    Reference: unconstrained optimum is 0, but the constraint x ≥ 1 is
    active at the boundary. KKT: x* = 1 with multiplier μ = 2 ≥ 0.
    Form as P = [[2]], q = 0, lb = [1].  (1/2)*P = [[1]] ⇒ objective
    is x², so optimal value at x=1 is 1.
    """
    P = np.array([[2.0]])
    q = np.array([0.0])
    res = qp.solve_qp(P, q, lb=[1.0])
    assert res["status"] == "optimal"
    assert math.isclose(float(res["x"][0]), 1.0, abs_tol=1e-6)
    assert math.isclose(res["optimal_value"], 1.0, abs_tol=1e-6)


@requires_cvxpy
def test_authority_2d_separable_qp():
    """min (1/2)(x² + 2y²)  →  optimal (0, 0), value = 0.

    Reference: ∂L/∂x = x = 0, ∂L/∂y = 2y = 0 ⇒ (0, 0).
    """
    P = np.diag([1.0, 2.0])
    q = np.zeros(2)
    res = qp.solve_qp(P, q)
    assert res["status"] == "optimal"
    np.testing.assert_allclose(res["x"], [0.0, 0.0], atol=1e-7)
    assert math.isclose(res["optimal_value"], 0.0, abs_tol=1e-9)


@requires_cvxpy
def test_authority_simple_svm_dual():
    """Hard-margin SVM on two linearly separable points → both are SVs.

    Two points: x_+ = (1, 0) with label +1 and x_- = (-1, 0) with label -1.
    Primal: min (1/2) ||w||² s.t. y_i (w · x_i + b) ≥ 1.
    The unique solution is w = (1, 0), b = 0, margin = 2/||w|| = 2.
    Verify by solving the primal as a QP in (w_1, w_2, b):
      P = diag(1, 1, 0), q = 0,
      G x ≤ h where rows encode -y_i (w · x_i + b) ≤ -1.
    Hand calculation: ||w||² = 1 ⇒ optimal value 1/2.
    """
    # Variables: w1, w2, b.
    P = np.diag([1.0, 1.0, 0.0])
    q = np.zeros(3)
    # Tiny ridge on b so P is strictly PSD (cvxpy allows PSD via psd_wrap).
    # We rely on psd_wrap; no ridge needed.
    # Inequality y_i (w · x_i + b) ≥ 1   ⇒   -y_i (w · x_i + b) + 1 ≤ 0
    # Point +1 at (1,0):  -(w1 + b) + 1 ≤ 0  ⇒  -w1 - b ≤ -1
    # Point -1 at (-1,0): -(-1)*(-w1 + b) + 1 ≤ 0 ⇒ -w1 + b ≤ -1
    G = np.array([
        [-1.0, 0.0, -1.0],
        [-1.0, 0.0,  1.0],
    ])
    h = np.array([-1.0, -1.0])
    res = qp.solve_qp(P, q, G=G, h=h)
    assert res["status"] == "optimal"
    w = res["x"][:2]
    b = res["x"][2]
    # Optimal w = (1, 0); b = 0 (by symmetry); ||w||² = 1.
    np.testing.assert_allclose(w, [1.0, 0.0], atol=1e-5)
    assert abs(b) < 1e-5
    assert math.isclose(res["optimal_value"], 0.5, abs_tol=1e-5)


# ---------------------------------------------------------------------------
# PROPERTY-BASED TESTS
# ---------------------------------------------------------------------------


@requires_cvxpy
def test_property_constraints_satisfied():
    """Solution must satisfy ALL constraints to within tolerance.

    Random small QPs: P = M^T M + I (PSD), random q, random G/h, A/b.
    """
    rng = np.random.default_rng(20260425)
    for trial in range(5):
        n = rng.integers(2, 6)
        M = rng.standard_normal((n, n))
        P = M.T @ M + np.eye(n)
        q = rng.standard_normal(n)
        m_ineq = rng.integers(1, 4)
        G = rng.standard_normal((m_ineq, n))
        # Generate feasible G x* <= h by picking an interior x_int.
        x_int = rng.standard_normal(n)
        h = G @ x_int + rng.uniform(0.5, 2.0, size=m_ineq)
        res = qp.solve_qp(P, q, G=G, h=h)
        assert res["status"] in ("optimal", "optimal_inaccurate"), \
            f"trial {trial}: status {res['status']}"
        x = res["x"]
        # G x <= h within tol
        slack = h - G @ x
        assert np.all(slack >= -1e-6), f"trial {trial}: violated G x <= h, slack={slack}"


@requires_cvxpy
def test_property_convex_qp_global_optimum():
    """For convex QP the local optimum equals the global optimum.

    Verify by perturbing the cvxpy solution by small random vectors and
    checking the objective never decreases below the reported value.
    """
    rng = np.random.default_rng(2026)
    n = 5
    M = rng.standard_normal((n, n))
    P = M.T @ M + np.eye(n) * 0.1
    q = rng.standard_normal(n)
    res = qp.solve_qp(P, q)
    f_star = res["optimal_value"]
    x_star = res["x"]
    for _ in range(20):
        delta = rng.standard_normal(n) * 1e-2
        x = x_star + delta
        f = 0.5 * x @ P @ x + q @ x
        assert f >= f_star - 1e-8, f"global opt violated: f={f}, f*={f_star}"


@requires_cvxpy
def test_property_deterministic():
    """Solving the same QP twice yields the same answer (within tol).

    cvxpy with a deterministic backend (OSQP/CLARABEL) gives stable output.
    """
    rng = np.random.default_rng(7)
    n = 4
    M = rng.standard_normal((n, n))
    P = M.T @ M + np.eye(n)
    q = rng.standard_normal(n)
    res1 = qp.solve_qp(P, q)
    res2 = qp.solve_qp(P, q)
    np.testing.assert_allclose(res1["x"], res2["x"], atol=1e-8)
    assert math.isclose(res1["optimal_value"], res2["optimal_value"], abs_tol=1e-8)


@requires_cvxpy
def test_property_box_qp_wide_bounds_is_unconstrained():
    """solve_box_qp with very wide bounds must match unconstrained QP.

    For min (1/2) x^T P x + q^T x with no constraints, x* = -P^{-1} q.
    With lb = -1e6, ub = 1e6 the box is inactive.
    """
    P = np.array([[2.0, 0.0], [0.0, 3.0]])
    q = np.array([-4.0, 6.0])
    # Unconstrained optimum: x = -[1/2, 1/3] * q componentwise =
    #   [4/2, -6/3] = [2, -2]
    res_box = qp.solve_box_qp(P, q, lb=[-1e6, -1e6], ub=[1e6, 1e6])
    res_un = qp.solve_qp(P, q)
    np.testing.assert_allclose(res_box["x"], [2.0, -2.0], atol=1e-5)
    np.testing.assert_allclose(res_box["x"], res_un["x"], atol=1e-5)


@requires_cvxpy
def test_property_lasso_shrinks_with_alpha():
    """Increasing alpha shrinks |beta| toward 0 for a fixed (X, y).

    Property: ||beta(alpha_1)||_1 >= ||beta(alpha_2)||_1 when alpha_1 < alpha_2.
    """
    rng = np.random.default_rng(123)
    n_samples, n_feat = 30, 6
    X = rng.standard_normal((n_samples, n_feat))
    true_beta = np.array([3.0, 0.0, -1.5, 0.0, 0.0, 2.0])
    y = X @ true_beta + 0.1 * rng.standard_normal(n_samples)

    norms = []
    for alpha in (0.001, 0.05, 0.5, 5.0):
        res = qp.solve_lasso_qp(X, y, alpha=alpha)
        assert res["x"] is not None
        norms.append(np.sum(np.abs(res["x"])))
    # Monotone non-increasing.
    for i in range(len(norms) - 1):
        assert norms[i] >= norms[i + 1] - 1e-5, \
            f"||beta||_1 should shrink: {norms}"
    # Very large alpha drives all coefficients to ~0.
    assert norms[-1] < 0.5


# ---------------------------------------------------------------------------
# EDGE-CASE TESTS
# ---------------------------------------------------------------------------


@requires_cvxpy
def test_edge_empty_constraints_is_unconstrained():
    """No G/h/A/b/lb/ub => unconstrained QP, x* = -P^{-1} q."""
    P = np.array([[4.0, 1.0], [1.0, 2.0]])
    q = np.array([1.0, -2.0])
    res = qp.solve_qp(P, q)
    expected = -np.linalg.solve(P, q)
    np.testing.assert_allclose(res["x"], expected, atol=1e-4)


def test_edge_non_symmetric_P_warns_and_symmetrises():
    """Non-symmetric P should warn and proceed with (P + P.T)/2."""
    P = np.array([[2.0, 1.0], [0.0, 2.0]])  # asymmetric
    q = np.array([0.0, 0.0])
    if not CVXPY_AVAILABLE:
        pytest.skip("cvxpy not installed")
    with pytest.warns(RuntimeWarning, match="not symmetric"):
        res = qp.solve_qp(P, q)
    assert res["status"] == "optimal"
    np.testing.assert_allclose(res["x"], [0.0, 0.0], atol=1e-7)


def test_edge_non_psd_raises():
    """P with a strictly negative eigenvalue must raise ValueError."""
    P = np.array([[1.0, 0.0], [0.0, -1.0]])
    q = np.array([0.0, 0.0])
    with pytest.raises(ValueError, match="not positive semidefinite"):
        qp.solve_qp(P, q)


@requires_cvxpy
def test_edge_infeasible():
    """G x <= h with x >= 1 AND -x >= 1 (i.e. x <= -1) is infeasible.

    Inequalities: x <= -1 (-x <= 1 doesn't capture this; use x <= -1 directly),
    plus lb = [1].  The half-spaces don't overlap → cvxpy reports
    'infeasible' (or 'infeasible_inaccurate'). x is None.
    """
    P = np.array([[1.0]])
    q = np.array([0.0])
    G = np.array([[1.0]])
    h = np.array([-1.0])  # x <= -1
    res = qp.solve_qp(P, q, G=G, h=h, lb=[1.0])  # x >= 1 and x <= -1
    assert "infeasible" in res["status"].lower()
    assert res["x"] is None


def test_edge_inconsistent_box_bounds_raises():
    """lb > ub must raise immediately."""
    P = np.array([[1.0]])
    q = np.array([0.0])
    with pytest.raises(ValueError, match="Inconsistent box bounds"):
        qp.solve_qp(P, q, lb=[2.0], ub=[1.0])


@requires_cvxpy
def test_edge_inconsistent_equalities_yields_infeasible():
    """A x = b1 AND A x = b2 (b1 != b2) → status 'infeasible'."""
    P = np.array([[1.0, 0.0], [0.0, 1.0]])
    q = np.zeros(2)
    A_eq = np.array([
        [1.0, 1.0],
        [1.0, 1.0],
    ])
    b_eq = np.array([1.0, 2.0])
    res = qp.solve_qp(P, q, A=A_eq, b=b_eq)
    assert "infeasible" in res["status"].lower() or res["x"] is None


def test_edge_empty_x():
    """n = 0 (P is 0x0) is the trivial case: x = [], value = 0."""
    P = np.zeros((0, 0))
    q = np.zeros(0)
    if not CVXPY_AVAILABLE:
        pytest.skip("cvxpy not installed")
    res = qp.solve_qp(P, q)
    assert res["status"] == "optimal"
    assert res["x"].shape == (0,)
    assert res["optimal_value"] == 0.0


def test_edge_unknown_solver_raises():
    """Unknown solver name raises ValueError."""
    P = np.array([[1.0]])
    q = np.array([0.0])
    with pytest.raises(ValueError, match="Unknown solver"):
        qp.solve_qp(P, q, solver="not-a-solver")


def test_edge_shape_mismatch_raises():
    """q with wrong length raises ValueError."""
    P = np.eye(3)
    q = np.array([1.0, 2.0])  # length 2, but P is 3x3
    if not CVXPY_AVAILABLE:
        pytest.skip("cvxpy not installed")
    with pytest.raises(ValueError, match="expected length 3"):
        qp.solve_qp(P, q)


def test_edge_quantile_invalid_tau():
    """tau outside (0, 1) must raise."""
    if not CVXPY_AVAILABLE:
        pytest.skip("cvxpy not installed")
    X = np.array([[1.0], [2.0]])
    y = np.array([1.0, 2.0])
    with pytest.raises(ValueError, match="tau"):
        qp.solve_quantile_regression(X, y, tau=0.0)
    with pytest.raises(ValueError, match="tau"):
        qp.solve_quantile_regression(X, y, tau=1.5)


# ---------------------------------------------------------------------------
# COMPOSITION TESTS
# ---------------------------------------------------------------------------


@requires_cvxpy
def test_composition_constrained_lstsq_matches_numpy():
    """Without any constraints, solve_constrained_least_squares
    must match np.linalg.lstsq.

    Composition: solve_constrained_least_squares -> solve_qp -> cvxpy,
    cross-checked against numpy.linalg.lstsq.
    """
    rng = np.random.default_rng(42)
    A = rng.standard_normal((10, 4))
    b = rng.standard_normal(10)
    res = qp.solve_constrained_least_squares(A, b)
    expected, *_ = np.linalg.lstsq(A, b, rcond=None)
    np.testing.assert_allclose(res["x"], expected, atol=1e-5)
    # residual_norm_sq should match ||A x - b||² of the lstsq solution.
    expected_resid = float(np.sum((A @ expected - b) ** 2))
    assert math.isclose(res["residual_norm_sq"], expected_resid, abs_tol=1e-5)


@requires_cvxpy
def test_composition_quantile_regression_median_matches_l1():
    """tau = 0.5 quantile regression == ordinary L1 / median regression.

    Composition: solve_quantile_regression(tau=0.5) on a univariate
    problem must approximately recover the median of (y - intercept * 1).

    Construct y_i = c + epsilon_i with epsilon symmetric → median ≈ c.
    With X = column of ones, the fitted beta is the median of y.
    """
    rng = np.random.default_rng(11)
    n = 51  # odd so true median is unique
    true_intercept = 2.5
    y = true_intercept + rng.standard_normal(n)
    X = np.ones((n, 1))
    res = qp.solve_quantile_regression(X, y, tau=0.5)
    assert res["status"] in ("optimal", "optimal_inaccurate")
    fitted = float(res["x"][0])
    median_y = float(np.median(y))
    assert math.isclose(fitted, median_y, abs_tol=1e-4), \
        f"quantile-0.5 regression {fitted} vs median {median_y}"


@requires_cvxpy
def test_composition_lasso_recovers_sparse_signal():
    """Lasso with moderate alpha on a planted-sparse problem recovers
    the true sparsity pattern (non-zero coords match true support).

    Composition: solve_lasso_qp -> cvxpy; cross-check against the
    planted ground-truth and verify the L1 solution drives the
    irrelevant features below a small threshold.
    """
    rng = np.random.default_rng(2024)
    n_samples, n_feat = 60, 10
    true_beta = np.zeros(n_feat)
    support = [1, 4, 7]
    for j in support:
        true_beta[j] = rng.choice([-2.0, 2.0])
    X = rng.standard_normal((n_samples, n_feat))
    # Standardise X for stable lasso behaviour.
    X = X / X.std(axis=0)
    y = X @ true_beta + 0.05 * rng.standard_normal(n_samples)

    res = qp.solve_lasso_qp(X, y, alpha=0.05)
    beta_hat = res["x"]
    assert beta_hat is not None
    # The true support should have |beta_hat| > 0.5 (it's around |2| - bias).
    for j in support:
        assert abs(beta_hat[j]) > 0.5, f"coord {j} not recovered: {beta_hat[j]}"
    # Off-support coords should be tiny.
    off = [j for j in range(n_feat) if j not in support]
    for j in off:
        assert abs(beta_hat[j]) < 0.4, \
            f"off-support coord {j} too large: {beta_hat[j]}"


@requires_cvxpy
def test_composition_qp_box_equals_qp_with_explicit_bounds():
    """solve_box_qp(P,q,lb,ub) must give the same answer as
    solve_qp(P,q,lb=lb,ub=ub).

    Composition test ensuring the convenience wrapper is a faithful
    forwarder.
    """
    P = np.array([[2.0, 0.5], [0.5, 1.0]])
    q = np.array([-1.0, 0.5])
    lb = [-1.0, -1.0]
    ub = [1.0, 1.0]
    r1 = qp.solve_box_qp(P, q, lb, ub)
    r2 = qp.solve_qp(P, q, lb=lb, ub=ub)
    np.testing.assert_allclose(r1["x"], r2["x"], atol=1e-7)
    assert math.isclose(r1["optimal_value"], r2["optimal_value"], abs_tol=1e-7)


# ---------------------------------------------------------------------------
# Backend coverage: scipy fallback (lower precision)
# ---------------------------------------------------------------------------


@requires_scipy
def test_scipy_fallback_simple_qp():
    """scipy SLSQP fallback solves a tiny QP to ~1e-5 precision."""
    P = np.array([[2.0, 0.0], [0.0, 2.0]])
    q = np.array([-2.0, -4.0])
    # Optimum: x = [1, 2], value = 0.5 * (1 + 4) - 2 - 8 = 2.5 - 10 = -5
    res = qp.solve_qp(P, q, solver="scipy")
    assert res["status"] == "optimal"
    np.testing.assert_allclose(res["x"], [1.0, 2.0], atol=1e-4)
    assert math.isclose(res["optimal_value"], -5.0, abs_tol=1e-4)
