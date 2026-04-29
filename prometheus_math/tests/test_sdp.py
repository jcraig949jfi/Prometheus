"""Tests for prometheus_math.optimization_sdp.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: Lovasz theta on classic graphs (K_n, C_5, empty), MAX-CUT
  SDP bound on K_3 / K_5, hand-computed 2x2 SDP.
- Property: PSD output, status set, Lovasz sandwich, symmetric C
  invariance, trivial PSD-objective optimum.
- Edge: empty constraints, n=0, infeasible, non-symmetric C, missing
  solver.
- Composition: Lovasz sandwich theorem (theta + max_cut SDP), full
  matrix completion recovers input, primal-dual agreement.
"""
from __future__ import annotations

# Suppress noisy cvxpy GLOP/PDLP warnings on import (ortools 9.15 mismatch).
import warnings as _warnings
_warnings.filterwarnings("ignore", category=UserWarning, module=r"cvxpy.*")

import numpy as np
import pytest

# Skip the whole module if cvxpy is unavailable.
cvxpy = pytest.importorskip("cvxpy")

from prometheus_math.optimization_sdp import (  # noqa: E402
    solve_sdp,
    solve_sdp_dual,
    sdp_relaxation_max_cut,
    lovasz_theta,
    matrix_completion_sdp,
    solve_lmi,
)


# Skip an individual test if SCS specifically is missing.
_HAS_SCS = "SCS" in cvxpy.installed_solvers()
_SCS_REASON = "SCS solver not installed in this cvxpy build"


# ---------------------------------------------------------------------------
# Authority tests (cite published references)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_lovasz_theta_complete_graph_K5():
    """theta(K_n) = 1.

    Reference: Lovasz, "On the Shannon capacity of a graph", IEEE Trans.
    Inf. Theory, 1979, Theorem 8 (theta of complete graph). Also
    Knuth, "The sandwich theorem", Electronic J. Combinatorics 1
    (1994), eq. (24).
    """
    n = 5
    A = np.ones((n, n), dtype=float) - np.eye(n)
    val = lovasz_theta(A)
    assert abs(val - 1.0) < 1e-3


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_lovasz_theta_pentagon_C5():
    """theta(C_5) = sqrt(5) (Lovasz' classic result).

    Reference: Lovasz (1979), Theorem 13. Settled the Shannon-capacity
    of the pentagon at sqrt(5).
    """
    n = 5
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        A[i, (i + 1) % n] = 1.0
        A[(i + 1) % n, i] = 1.0
    val = lovasz_theta(A)
    assert abs(val - np.sqrt(5.0)) < 1e-3


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_lovasz_theta_empty_graph_equals_n():
    """theta(empty graph on n vertices) = n.

    Reference: Knuth (1994), eq. (3): for the edgeless graph on n
    vertices, alpha = chi-bar = theta = n. Both sandwich bounds collapse.
    """
    for n in (1, 3, 6):
        A = np.zeros((n, n), dtype=float)
        val = lovasz_theta(A)
        assert abs(val - n) < 1e-3


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_max_cut_sdp_triangle_K3():
    """MAX-CUT SDP on K_3 returns SDP bound 9/4 = 2.25 (= 3 * (1 - cos(2pi/3))/2 = 3 * 0.75 = 2.25).

    Reference: Goemans-Williamson, "Improved approximation algorithms
    for maximum cut and satisfiability problems using semidefinite
    programming", JACM 42(6), 1995. For K_3 the SDP relaxation is
    9/4 = 2.25 (combinatorial max cut is 2; SDP overshoots).
    """
    A = np.ones((3, 3)) - np.eye(3)
    res = sdp_relaxation_max_cut(A)
    # The SDP optimum equals (1/4) sum_{i<j} A_ij (1 - X_ij) where X_ii = 1.
    # For K_3 that's 9/4 = 2.25.
    assert abs(res["value"] - 2.25) < 1e-2


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_max_cut_sdp_K5_upper_bounds_max_cut():
    """SDP relaxation on K_5 is >= integer MAX-CUT (= 6).

    Reference: Goemans-Williamson (1995). Integer MAX-CUT of K_5 is 6
    (split into 2-3 partition; 2*3=6 edges across). SDP is a valid
    upper bound, so SDP >= 6.
    """
    n = 5
    A = np.ones((n, n)) - np.eye(n)
    res = sdp_relaxation_max_cut(A)
    assert res["value"] >= 6.0 - 1e-2


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_solve_sdp_tiny_2x2_handcomputed():
    """Hand-computed 2x2 SDP.

    Problem: min Tr(C X) s.t. X_11 + X_22 = 2, X >= 0.
    With C = diag(1, 2), Tr(C X) = X_11 + 2 X_22.  Subject to
    X_11 + X_22 = 2 and X >= 0 (PSD).  The minimum picks X_22 = 0,
    X_11 = 2, giving Tr(C X) = 2.

    Hand computation: PSD with diagonal sum 2 and zero second diagonal
    forces X = diag(2, 0); off-diagonals must be 0 (2x2 PSD with one
    zero diagonal entry).  Optimal value = 2.
    """
    C = np.diag([1.0, 2.0])
    A_eq = [np.eye(2)]   # Tr(I X) = 2 -> X_11 + X_22 = 2
    b_eq = [2.0]
    res = solve_sdp(C, A_eq, b_eq, n=2)
    assert res["status"] in ("optimal", "optimal_inaccurate")
    assert abs(res["optimal_value"] - 2.0) < 1e-3


# ---------------------------------------------------------------------------
# Property tests (invariants)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_solve_sdp_returns_psd_matrix():
    """X returned by solve_sdp is positive semidefinite (eigvals >= 0)."""
    rng = np.random.default_rng(0)
    n = 4
    C = np.eye(n) + 0.1 * rng.standard_normal((n, n))
    C = (C + C.T) / 2  # symmetrize
    A_eq = [np.eye(n)]
    b_eq = [1.0]
    res = solve_sdp(C, A_eq, b_eq, n=n)
    X = res["X"]
    eigs = np.linalg.eigvalsh((X + X.T) / 2)
    assert eigs.min() > -1e-6  # PSD up to solver tolerance


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_solve_sdp_status_set():
    """status is one of the documented strings."""
    C = np.eye(2)
    A_eq = [np.eye(2)]
    b_eq = [1.0]
    res = solve_sdp(C, A_eq, b_eq, n=2)
    assert res["status"] in {
        "optimal", "optimal_inaccurate",
        "infeasible", "unbounded", "solver_error",
        "infeasible_inaccurate", "unbounded_inaccurate",
    }


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_lovasz_sandwich_property():
    """alpha(G) <= theta(G) <= chi(complement(G)). We check theta in [1, n].

    Reference: Knuth (1994), the sandwich theorem (sandwich bounds the
    theta function between independence number and chromatic number of
    the complement).  Both extremes are >= 1 and <= n on any graph,
    so theta in [1, n].
    """
    rng = np.random.default_rng(1)
    n = 6
    # Random sparse graph
    A = (rng.random((n, n)) < 0.3).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    val = lovasz_theta(A)
    assert 1.0 - 1e-3 <= val <= float(n) + 1e-3


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_solve_sdp_symmetric_C_solution_symmetric():
    """When C is symmetric, X solution is symmetric to numerical tol."""
    n = 3
    C = np.array([[1.0, 0.5, 0.0],
                  [0.5, 2.0, 0.1],
                  [0.0, 0.1, 1.5]])
    A_eq = [np.eye(n)]
    b_eq = [1.0]
    res = solve_sdp(C, A_eq, b_eq, n=n)
    X = res["X"]
    assert np.allclose(X, X.T, atol=1e-5)


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_solve_sdp_psd_objective_no_constraints_optimum_zero():
    """For trivial SDP (no equality/inequality constraints, C >> 0,
    plus X >= 0), optimal X = 0 and value = 0.

    With C strictly PSD and only X >= 0, min Tr(C X) = 0 at X = 0.
    """
    C = np.eye(3) * 2.0  # 2 I, strictly PSD
    res = solve_sdp(C, A_eq=[], b_eq=[], n=3)
    assert res["status"] in ("optimal", "optimal_inaccurate")
    assert abs(res["optimal_value"]) < 1e-4
    assert np.linalg.norm(res["X"]) < 1e-3


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_n_zero_raises():
    """n = 0 must raise ValueError."""
    with pytest.raises(ValueError):
        solve_sdp(np.zeros((0, 0)), [], [], n=0)


def test_non_symmetric_C_warns_and_symmetrizes():
    """C not symmetric: function symmetrizes (warns) rather than fail."""
    # Skewed C; we'll check that solve_sdp returns a valid result by
    # internally symmetrizing.  Edge: Tr(C X) is invariant under
    # C -> (C + C^T)/2 when X is symmetric, so symmetrizing is safe.
    C = np.array([[1.0, 1.0], [0.0, 1.0]])
    A_eq = [np.eye(2)]
    b_eq = [1.0]
    if not _HAS_SCS:
        pytest.skip(_SCS_REASON)
    with pytest.warns(UserWarning):
        res = solve_sdp(C, A_eq, b_eq, n=2)
    assert res["status"] in ("optimal", "optimal_inaccurate")


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_infeasible_status():
    """Inconsistent constraints yield infeasible status.

    Tr(I X) = 1 and Tr(I X) = 2 simultaneously is impossible.
    """
    C = np.eye(2)
    A_eq = [np.eye(2), np.eye(2)]
    b_eq = [1.0, 2.0]
    res = solve_sdp(C, A_eq, b_eq, n=2)
    assert "infeasible" in res["status"]


def test_solver_not_installed_raises():
    """Asking for a fictional solver raises ValueError with helpful msg."""
    C = np.eye(2)
    A_eq = [np.eye(2)]
    b_eq = [1.0]
    with pytest.raises(ValueError) as exc:
        solve_sdp(C, A_eq, b_eq, n=2, solver="THIS_SOLVER_DOES_NOT_EXIST")
    assert "solver" in str(exc.value).lower()


def test_lovasz_theta_n_equals_one():
    """Edge: theta(single isolated vertex) = 1."""
    if not _HAS_SCS:
        pytest.skip(_SCS_REASON)
    A = np.zeros((1, 1))
    assert abs(lovasz_theta(A) - 1.0) < 1e-3


# ---------------------------------------------------------------------------
# Composition tests (multi-tool chains)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_lovasz_sandwich_composition_K5():
    """Composition: theta(K_5) and SDP-MAX-CUT(K_5) both produced by the
    same arsenal must agree with the sandwich theorem.

    Reference: Knuth (1994). Sandwich:
        alpha(G) <= theta(G) <= chi(complement(G)).
    For K_5, alpha = 1 and chi-bar(K_5) = chi(empty_5) = 1, so theta = 1.
    Cross-check: also fall within sandwich brackets.
    """
    n = 5
    A = np.ones((n, n)) - np.eye(n)
    theta = lovasz_theta(A)
    assert 1.0 - 1e-3 <= theta <= 1.0 + 1e-3

    # SDP-MAX-CUT on K_5 should be feasible (status optimal*)
    res = sdp_relaxation_max_cut(A)
    assert res["status"] in ("optimal", "optimal_inaccurate")


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_matrix_completion_full_observation_recovers_input():
    """If we observe every entry of a PSD matrix, completion returns it."""
    n = 3
    rng = np.random.default_rng(2)
    L = rng.standard_normal((n, n))
    M = L @ L.T  # PSD ground-truth
    observed = [(i, j, M[i, j]) for i in range(n) for j in range(n)]
    res = matrix_completion_sdp(observed, n=n)
    assert res["status"] in ("optimal", "optimal_inaccurate")
    np.testing.assert_allclose(res["X"], M, atol=1e-3)


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_primal_dual_value_match():
    """Composition: primal SDP and its dual return the same optimal value
    (strong duality holds for strictly feasible SDPs, Slater's condition).

    Problem: min Tr(I X) s.t. Tr(E11 X) = 1, X >= 0.
    Primal optimum: X = E11, value = 1.  Dual optimum: y = 1, value = 1.
    """
    n = 2
    C = np.eye(n)
    E11 = np.zeros((n, n))
    E11[0, 0] = 1.0
    A = [E11]
    b = [1.0]
    primal = solve_sdp(C, A_eq=A, b_eq=b, n=n)
    dual = solve_sdp_dual(C, A=A, b=b, n=n)
    assert abs(primal["optimal_value"] - dual["optimal_value"]) < 1e-3
    assert abs(primal["optimal_value"] - 1.0) < 1e-3


@pytest.mark.skipif(not _HAS_SCS, reason=_SCS_REASON)
def test_solve_lmi_basic():
    """Composition: solve_lmi calls solve_sdp under the hood and gives
    the same answer for a hand-set scalar LMI.

    min x  s.t.  x * I >= 0.5 * I, i.e. x >= 0.5, in 1D.
    Encoded as LMI: B - sum x_i A_i >> 0 with A_1 = -I, B = -0.5 I:
        -0.5 I - x*(-I) = (x - 0.5) I  >>  0  iff  x >= 0.5.
    Optimum x = 0.5.
    """
    A_1 = -np.eye(2)
    B = -0.5 * np.eye(2)
    res = solve_lmi(matrices_A=[A_1], b=B, c=[1.0], var_dim=1)
    assert res["status"] in ("optimal", "optimal_inaccurate")
    assert abs(res["x"][0] - 0.5) < 1e-3
