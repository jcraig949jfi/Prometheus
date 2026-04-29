"""prometheus_math.optimization_sdp — semidefinite programming via cvxpy.

Wraps cvxpy with researcher-friendly entry points for the most common
SDP problem forms:

    solve_sdp                primal: min <C, X>  s.t.  <A_eq, X> = b_eq,
                                                       <A_ineq, X> <= b_ineq,
                                                       X >> 0
    solve_sdp_dual           dual:   max b^T y    s.t. C - sum_i y_i A_i >> 0
    sdp_relaxation_max_cut   Goemans-Williamson SDP for MAX-CUT
    lovasz_theta             Lovasz theta function of a graph
    matrix_completion_sdp    nuclear-norm-style PSD matrix completion
    solve_lmi                min c^T x s.t. sum_i x_i A_i  <<  B

Backend: cvxpy.  Default solver = SCS (open-source, ships with cvxpy).
Other solvers (CVXOPT, MOSEK) used if explicitly requested and installed.

Notes
-----
On systems with newer ortools (>= 9.15) cvxpy emits noisy warnings while
importing GLOP / PDLP — those LP-only solvers are unavailable but the
SDP solvers (SCS, CVXOPT, etc.) import cleanly.  This module suppresses
those warnings on first use.
"""
from __future__ import annotations

import warnings
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# cvxpy lazy import (suppress ortools-version warnings)
# ---------------------------------------------------------------------------


def _import_cvxpy():
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            import cvxpy as cp
        return cp
    except ImportError as e:  # pragma: no cover - exercised only without cvxpy
        raise ImportError(
            "cvxpy is required for prometheus_math.optimization_sdp. "
            "Install via `pip install cvxpy`."
        ) from e


def _validate_solver(cp, solver: str) -> str:
    """Return the cvxpy solver string after validating availability."""
    avail = cp.installed_solvers()
    if solver not in avail:
        raise ValueError(
            f"Solver {solver!r} is not available in this cvxpy build. "
            f"Installed solvers: {avail}.  "
            f"For SDP, SCS is the standard open-source default."
        )
    return solver


# ---------------------------------------------------------------------------
# Argument helpers
# ---------------------------------------------------------------------------


def _ensure_2d_array(M, name: str) -> np.ndarray:
    arr = np.asarray(M, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2-D matrix; got shape {arr.shape}")
    return arr


def _symmetrize(M: np.ndarray) -> np.ndarray:
    return 0.5 * (M + M.T)


def _check_n(n) -> int:
    if not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError(f"n must be a positive integer; got {n!r}")
    return int(n)


def _normalize_constraints(
    A_list: Optional[Iterable], b_list: Optional[Iterable], n: int, name: str
) -> Tuple[List[np.ndarray], List[float]]:
    if A_list is None:
        A_list = []
    if b_list is None:
        b_list = []
    A_arrs: List[np.ndarray] = []
    for k, A_k in enumerate(A_list):
        A_arr = _ensure_2d_array(A_k, f"{name}[{k}]")
        if A_arr.shape != (n, n):
            raise ValueError(
                f"{name}[{k}] has shape {A_arr.shape}, expected ({n}, {n})")
        A_arrs.append(_symmetrize(A_arr))
    b_arrs: List[float] = [float(x) for x in b_list]
    if len(A_arrs) != len(b_arrs):
        raise ValueError(
            f"length mismatch: {len(A_arrs)} {name} matrices vs "
            f"{len(b_arrs)} rhs values")
    return A_arrs, b_arrs


# ---------------------------------------------------------------------------
# 1. Primal standard-form SDP
# ---------------------------------------------------------------------------


def solve_sdp(
    C,
    A_eq: Optional[Sequence] = None,
    b_eq: Optional[Sequence] = None,
    A_ineq: Optional[Sequence] = None,
    b_ineq: Optional[Sequence] = None,
    n: Optional[int] = None,
    solver: str = "SCS",
    verbose: bool = False,
) -> dict:
    """Solve the primal standard-form SDP:

        minimize    <C, X>
        subject to  <A_eq[i],  X> = b_eq[i],
                    <A_ineq[j], X> <= b_ineq[j],
                    X is symmetric positive semidefinite (n x n).

    where <A, X> = trace(A^T X).

    Parameters
    ----------
    C        : (n, n) symmetric cost matrix.  Non-symmetric C is symmetrized
               with a UserWarning (Tr(C X) = Tr(((C+C^T)/2) X) for symmetric X).
    A_eq, b_eq : equality constraint matrices and rhs (length m).
    A_ineq, b_ineq : inequality constraint matrices and rhs.
    n        : explicit dimension; if None, inferred from C.shape.
    solver   : 'SCS' (default), 'CVXOPT', 'MOSEK', etc.  See cvxpy.installed_solvers().
    verbose  : passed through to cvxpy.

    Returns
    -------
    dict with keys: X (np.ndarray (n,n)), optimal_value (float|None),
                    status (str), solver_used (str), n_iter (int|None).

    References
    ----------
    Vandenberghe & Boyd, "Semidefinite Programming", SIAM Review 1996.
    """
    cp = _import_cvxpy()
    if n is None:
        C_arr = _ensure_2d_array(C, "C")
        n = C_arr.shape[0]
    n = _check_n(n)
    C_arr = _ensure_2d_array(C, "C")
    if C_arr.shape != (n, n):
        raise ValueError(f"C has shape {C_arr.shape}, expected ({n}, {n})")
    if not np.allclose(C_arr, C_arr.T, atol=1e-10):
        warnings.warn(
            "C is not symmetric; symmetrizing as (C + C^T) / 2 "
            "(Tr(C X) is invariant under this symmetrization for symmetric X).",
            UserWarning,
            stacklevel=2,
        )
    C_sym = _symmetrize(C_arr)

    A_eqs, b_eqs = _normalize_constraints(A_eq, b_eq, n, "A_eq")
    A_ineqs, b_ineqs = _normalize_constraints(A_ineq, b_ineq, n, "A_ineq")

    solver = _validate_solver(cp, solver)

    X = cp.Variable((n, n), symmetric=True)
    constraints = [X >> 0]
    for A_k, b_k in zip(A_eqs, b_eqs):
        constraints.append(cp.trace(A_k @ X) == b_k)
    for A_k, b_k in zip(A_ineqs, b_ineqs):
        constraints.append(cp.trace(A_k @ X) <= b_k)

    objective = cp.Minimize(cp.trace(C_sym @ X))
    prob = cp.Problem(objective, constraints)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        try:
            prob.solve(solver=solver, verbose=verbose)
        except cp.error.SolverError as e:
            return {
                "X": None,
                "optimal_value": None,
                "status": "solver_error",
                "solver_used": solver,
                "n_iter": None,
                "error": str(e),
            }

    X_val = None
    if X.value is not None:
        X_val = _symmetrize(np.asarray(X.value, dtype=float))

    n_iter = None
    try:
        n_iter = int(prob.solver_stats.num_iters) if prob.solver_stats else None
    except Exception:
        n_iter = None

    return {
        "X": X_val,
        "optimal_value": (
            float(prob.value) if prob.value is not None and np.isfinite(prob.value) else None
        ),
        "status": str(prob.status),
        "solver_used": solver,
        "n_iter": n_iter,
    }


# ---------------------------------------------------------------------------
# 2. Dual standard-form SDP
# ---------------------------------------------------------------------------


def solve_sdp_dual(
    C,
    A: Sequence,
    b: Sequence,
    n: Optional[int] = None,
    solver: str = "SCS",
    verbose: bool = False,
) -> dict:
    """Solve the dual SDP:

        maximize    b^T y
        subject to  C - sum_i y_i A_i  >>  0   (PSD)

    Parameters
    ----------
    C : (n, n) symmetric matrix.
    A : list of m matrices each (n, n).
    b : length-m vector.

    Returns
    -------
    {y, optimal_value, status, solver_used}.

    References
    ----------
    Vandenberghe & Boyd 1996, Section 1 (primal-dual SDP pair).
    """
    cp = _import_cvxpy()
    if n is None:
        C_arr = _ensure_2d_array(C, "C")
        n = C_arr.shape[0]
    n = _check_n(n)
    C_arr = _symmetrize(_ensure_2d_array(C, "C"))
    A_arrs, b_arrs = _normalize_constraints(A, b, n, "A")
    m = len(A_arrs)
    solver = _validate_solver(cp, solver)

    y = cp.Variable(m) if m > 0 else None

    if m == 0:
        # No dual variables: feasibility is C >> 0 with objective 0.
        eigs = np.linalg.eigvalsh(C_arr)
        if eigs.min() >= -1e-10:
            return {
                "y": np.zeros(0),
                "optimal_value": 0.0,
                "status": "optimal",
                "solver_used": solver,
            }
        return {
            "y": None,
            "optimal_value": None,
            "status": "infeasible",
            "solver_used": solver,
        }

    slack = C_arr - sum(y[i] * A_arrs[i] for i in range(m))
    constraints = [slack >> 0]
    objective = cp.Maximize(b_arrs @ y)
    prob = cp.Problem(objective, constraints)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        try:
            prob.solve(solver=solver, verbose=verbose)
        except cp.error.SolverError as e:
            return {
                "y": None,
                "optimal_value": None,
                "status": "solver_error",
                "solver_used": solver,
                "error": str(e),
            }

    y_val = None
    if y is not None and y.value is not None:
        y_val = np.asarray(y.value, dtype=float)
    return {
        "y": y_val,
        "optimal_value": (
            float(prob.value) if prob.value is not None and np.isfinite(prob.value) else None
        ),
        "status": str(prob.status),
        "solver_used": solver,
    }


# ---------------------------------------------------------------------------
# 3. MAX-CUT SDP relaxation
# ---------------------------------------------------------------------------


def sdp_relaxation_max_cut(adjacency_matrix, solver: str = "SCS",
                           verbose: bool = False) -> dict:
    """Goemans-Williamson SDP relaxation of MAX-CUT.

        maximize    (1/4) sum_{i<j} A_{ij} (1 - X_{ij})
        subject to  X_{ii} = 1, X >> 0.

    Parameters
    ----------
    adjacency_matrix : (n, n) symmetric non-negative weights.

    Returns
    -------
    {value (SDP optimum, upper bound on MAX-CUT),
     X    (Gram matrix, n x n),
     cut_lower_bound (Goemans-Williamson 0.87856 guarantee).

    References
    ----------
    Goemans & Williamson, JACM 42(6), 1995.
    """
    cp = _import_cvxpy()
    A = _ensure_2d_array(adjacency_matrix, "adjacency_matrix")
    if A.shape[0] != A.shape[1]:
        raise ValueError(f"adjacency_matrix must be square; got {A.shape}")
    n = A.shape[0]
    if n == 0:
        raise ValueError("adjacency_matrix must have n >= 1 vertices")
    A = _symmetrize(A)
    solver = _validate_solver(cp, solver)

    X = cp.Variable((n, n), symmetric=True)
    constraints = [X >> 0, cp.diag(X) == 1]
    # Weighted edge contributions (laplacian-like):
    # cut_value = (1/4) sum_{i,j} A_{ij} (1 - X_{ij})  (factor 1/2 for ordered
    # pairs absorbed by counting each edge twice through (i,j) and (j,i)).
    # Use (1/4) sum_ij A_ij (1 - X_ij) since A is symmetric and that double-counts.
    # That matches the standard normalization: equals sum_{i<j} A_ij (1 - X_ij)/2.
    expr = 0.25 * cp.sum(cp.multiply(A, 1 - X))
    objective = cp.Maximize(expr)
    prob = cp.Problem(objective, constraints)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(solver=solver, verbose=verbose)

    X_val = None
    if X.value is not None:
        X_val = _symmetrize(np.asarray(X.value, dtype=float))
    val = float(prob.value) if prob.value is not None and np.isfinite(prob.value) else None
    cut_lb = 0.87856 * val if val is not None else None
    return {
        "value": val,
        "X": X_val,
        "cut_lower_bound": cut_lb,
        "status": str(prob.status),
        "solver_used": solver,
    }


# ---------------------------------------------------------------------------
# 4. Lovasz theta function
# ---------------------------------------------------------------------------


def lovasz_theta(adjacency_matrix, solver: str = "SCS",
                 verbose: bool = False) -> float:
    """Compute Lovasz' theta function theta(G).

    Formulation (one of several equivalent SDPs):

        maximize    sum_ij X_ij
        subject to  trace(X) = 1,
                    X_ij = 0  for every edge (i, j) in G,
                    X >> 0.

    Reference: Lovasz, "On the Shannon capacity of a graph", IEEE Trans.
    Inf. Theory IT-25 (1979).  Also Knuth (1994), eq. (24).

    Parameters
    ----------
    adjacency_matrix : symmetric 0/1 matrix; positive off-diagonal entries
        flag edges.  Diagonal entries are ignored.

    Returns
    -------
    float theta(G).
    """
    cp = _import_cvxpy()
    A = _ensure_2d_array(adjacency_matrix, "adjacency_matrix")
    if A.shape[0] != A.shape[1]:
        raise ValueError(f"adjacency_matrix must be square; got {A.shape}")
    n = A.shape[0]
    if n == 0:
        raise ValueError("Graph must have at least one vertex")
    solver = _validate_solver(cp, solver)

    X = cp.Variable((n, n), symmetric=True)
    constraints = [X >> 0, cp.trace(X) == 1]
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] != 0 or A[j, i] != 0:
                constraints.append(X[i, j] == 0)

    objective = cp.Maximize(cp.sum(X))
    prob = cp.Problem(objective, constraints)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(solver=solver, verbose=verbose)

    if prob.value is None or not np.isfinite(prob.value):
        raise RuntimeError(
            f"Lovasz theta SDP did not solve to optimum (status={prob.status})")
    return float(prob.value)


# ---------------------------------------------------------------------------
# 5. Matrix completion via PSD constraint
# ---------------------------------------------------------------------------


def matrix_completion_sdp(
    observed_entries: Sequence[Tuple[int, int, float]],
    n: int,
    solver: str = "SCS",
    verbose: bool = False,
) -> dict:
    """Low-rank PSD matrix completion.

    Given a set of observed entries (i, j, v), find a PSD matrix X with
    minimal trace (proxy for rank) that matches the observations.

        minimize    trace(X)
        subject to  X_{ij} = v_{ij}  for all observed (i, j, v),
                    X >> 0.

    Parameters
    ----------
    observed_entries : list of (i, j, value) tuples.
    n : matrix dimension.

    Returns
    -------
    {X (n x n), optimal_value, status, solver_used}.

    References
    ----------
    Candes & Recht, "Exact matrix completion via convex optimization",
    Found. Comp. Math. 9 (2009).  Trace-norm minimization for PSD completion.
    """
    cp = _import_cvxpy()
    n = _check_n(n)
    solver = _validate_solver(cp, solver)

    X = cp.Variable((n, n), symmetric=True)
    constraints = [X >> 0]
    for (i, j, v) in observed_entries:
        if not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"observed index ({i}, {j}) out of bounds for n={n}")
        constraints.append(X[i, j] == float(v))

    objective = cp.Minimize(cp.trace(X))
    prob = cp.Problem(objective, constraints)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(solver=solver, verbose=verbose)

    X_val = None
    if X.value is not None:
        X_val = _symmetrize(np.asarray(X.value, dtype=float))
    return {
        "X": X_val,
        "optimal_value": (
            float(prob.value) if prob.value is not None and np.isfinite(prob.value) else None
        ),
        "status": str(prob.status),
        "solver_used": solver,
    }


# ---------------------------------------------------------------------------
# 6. Generic LMI: min c^T x s.t. sum x_i A_i  <<  B
# ---------------------------------------------------------------------------


def solve_lmi(
    matrices_A: Sequence,
    b,
    c: Sequence[float],
    var_dim: int,
    solver: str = "SCS",
    verbose: bool = False,
) -> dict:
    """Solve a generic LMI program:

        minimize    c^T x
        subject to  sum_{i=1..var_dim} x_i A_i  <<  B
                  (equivalently  B - sum x_i A_i  >>  0)

    Parameters
    ----------
    matrices_A : list of var_dim symmetric (n, n) matrices.
    b : (n, n) symmetric matrix B (or any object reshaped via _ensure_2d_array).
    c : length-var_dim cost vector.
    var_dim : number of scalar variables x_i.

    Returns
    -------
    {x (np.ndarray length var_dim), optimal_value, status, solver_used}.

    References
    ----------
    Boyd, El Ghaoui, Feron, Balakrishnan, "Linear Matrix Inequalities in
    System and Control Theory", SIAM Studies in Applied Mathematics 15, 1994.
    """
    cp = _import_cvxpy()
    if var_dim is None or int(var_dim) <= 0:
        raise ValueError(f"var_dim must be a positive integer; got {var_dim!r}")
    var_dim = int(var_dim)
    if len(matrices_A) != var_dim:
        raise ValueError(
            f"len(matrices_A) ({len(matrices_A)}) must equal var_dim ({var_dim})")
    if len(c) != var_dim:
        raise ValueError(
            f"len(c) ({len(c)}) must equal var_dim ({var_dim})")
    B = _symmetrize(_ensure_2d_array(b, "b"))
    n = B.shape[0]
    A_arrs = []
    for k, A_k in enumerate(matrices_A):
        A_arr = _ensure_2d_array(A_k, f"matrices_A[{k}]")
        if A_arr.shape != (n, n):
            raise ValueError(
                f"matrices_A[{k}] has shape {A_arr.shape}, expected ({n}, {n})")
        A_arrs.append(_symmetrize(A_arr))
    solver = _validate_solver(cp, solver)

    x = cp.Variable(var_dim)
    slack = B - sum(x[i] * A_arrs[i] for i in range(var_dim))
    constraints = [slack >> 0]
    objective = cp.Minimize(np.asarray(c, dtype=float) @ x)
    prob = cp.Problem(objective, constraints)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(solver=solver, verbose=verbose)

    x_val = None
    if x.value is not None:
        x_val = np.asarray(x.value, dtype=float)
    return {
        "x": x_val,
        "optimal_value": (
            float(prob.value) if prob.value is not None and np.isfinite(prob.value) else None
        ),
        "status": str(prob.status),
        "solver_used": solver,
    }


__all__ = [
    "solve_sdp",
    "solve_sdp_dual",
    "sdp_relaxation_max_cut",
    "lovasz_theta",
    "matrix_completion_sdp",
    "solve_lmi",
]
