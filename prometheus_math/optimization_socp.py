"""prometheus_math.optimization_socp — Second-order cone programming.

Standard SOCP form
------------------

    minimize    c^T x
    subject to  ||A_i x + b_i||_2 <= c_i^T x + d_i,   i = 1, ..., k
                A_eq x = b_eq                           (optional)

SOCP strictly generalises LP and QP: any convex QP can be cast as an
SOCP via a single ``||L x + ...||_2 <= t`` constraint where ``L`` is the
Cholesky factor of the Hessian. SOCP is in turn a strict subset of SDP.

Backend
-------
``cvxpy`` (mandatory).  Routes to one of CLARABEL / SCS / ECOS depending
on what the local cvxpy build has installed.  All four are conic
solvers that natively handle the second-order cone.

Public API
----------
- ``solve_socp(c, A_cones, b_cones, c_cones, d_cones, A_eq, b_eq, ...)``
- ``solve_robust_lp(c, A, b, uncertainty_radius, ord, ...)``
- ``chebyshev_center(A, b, ...)``
- ``min_volume_ellipsoid(points, ...)``
- ``portfolio_socp(returns_mean, returns_cov, ...)``
- ``facility_location_socp(facility_costs, demands, distances, ...)``

Each function returns a dict with at minimum::

    {x|center|weights|...,
     optimal_value,
     status,
     solver_used}

References
----------
- Boyd & Vandenberghe, "Convex Optimization", §4.4.2 (SOCP),
  §8.5.1 (Chebyshev centre), §8.4.1 (minimum-volume ellipsoid).
- Lobo, Vandenberghe, Boyd, Lebret (1998), "Applications of
  second-order cone programming", LAA 284:193-228.
"""
from __future__ import annotations

import warnings
from typing import Iterable, List, Optional, Sequence

import numpy as np


__all__ = [
    "solve_socp",
    "solve_robust_lp",
    "chebyshev_center",
    "min_volume_ellipsoid",
    "portfolio_socp",
    "facility_location_socp",
]


# ---------------------------------------------------------------------------
# cvxpy lazy import
# ---------------------------------------------------------------------------


def _import_cvxpy():
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            import cvxpy as cp
        return cp
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "cvxpy is required for prometheus_math.optimization_socp. "
            "Install via `pip install cvxpy`."
        ) from e


_KNOWN_SOLVERS = {"cvxpy"}


def _check_solver(solver: str) -> str:
    if solver not in _KNOWN_SOLVERS:
        raise ValueError(
            f"Unknown solver {solver!r}; choose from {sorted(_KNOWN_SOLVERS)}"
        )
    return solver


# ---------------------------------------------------------------------------
# Argument helpers
# ---------------------------------------------------------------------------


def _as_vec(v, name: str) -> np.ndarray:
    arr = np.asarray(v, dtype=float).ravel()
    return arr


def _as_mat(M, name: str) -> np.ndarray:
    arr = np.asarray(M, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be 2-D; got shape {arr.shape}")
    return arr


def _extract_n_iter(prob) -> Optional[int]:
    try:
        if prob.solver_stats is not None and prob.solver_stats.num_iters is not None:
            return int(prob.solver_stats.num_iters)
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# 1. solve_socp — standard SOCP form
# ---------------------------------------------------------------------------


def solve_socp(
    c,
    A_cones: Optional[Sequence] = None,
    b_cones: Optional[Sequence] = None,
    c_cones: Optional[Sequence] = None,
    d_cones: Optional[Sequence] = None,
    A_eq=None,
    b_eq=None,
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Solve a standard-form second-order cone program.

        minimize    c^T x
        subject to  ||A_i x + b_i||_2 <= c_i^T x + d_i, for i = 1..k
                    A_eq x = b_eq                     (optional)

    Parameters
    ----------
    c : (n,) array_like
        Linear objective.
    A_cones : sequence of (m_i, n) arrays, optional
        One matrix per cone constraint.  If None or empty, the program
        reduces to an LP (only equality constraints, if any, remain).
    b_cones : sequence of (m_i,) arrays, optional
        Cone offsets (same length as ``A_cones``).
    c_cones : sequence of (n,) arrays, optional
        Linear part on the right-hand side of each cone constraint.
    d_cones : sequence of floats, optional
        Scalar offsets on the rhs (same length as ``A_cones``).
    A_eq, b_eq : optional (p, n) and (p,) arrays
        Linear equality constraints.
    solver : {'cvxpy'}
        Backend.
    verbose : bool

    Returns
    -------
    dict with keys ``x``, ``optimal_value``, ``status``, ``solver_used``,
    ``n_iter``.

    Notes
    -----
    For ``A_cones = None`` (no cone constraints), the program reduces to
    a plain LP and is solved as such.
    """
    _check_solver(solver)
    c_arr = _as_vec(c, "c")
    n = c_arr.size
    if n == 0:
        raise ValueError("c must be non-empty (problem must have >= 1 variable)")

    # Normalise the four parallel cone-constraint sequences.
    if A_cones is None:
        A_cones = []
    A_list = [_as_mat(A_i, f"A_cones[{i}]") for i, A_i in enumerate(A_cones)]
    k = len(A_list)
    for i, A_i in enumerate(A_list):
        if A_i.shape[1] != n:
            raise ValueError(
                f"A_cones[{i}] has shape {A_i.shape}; expected (*, {n})"
            )

    if b_cones is None:
        b_cones = [np.zeros(A_i.shape[0]) for A_i in A_list]
    b_list = [_as_vec(b_i, f"b_cones[{i}]") for i, b_i in enumerate(b_cones)]
    if len(b_list) != k:
        raise ValueError(
            f"b_cones has length {len(b_list)} but A_cones has length {k}"
        )
    for i, (A_i, b_i) in enumerate(zip(A_list, b_list)):
        if b_i.size != A_i.shape[0]:
            raise ValueError(
                f"b_cones[{i}] has size {b_i.size}; expected {A_i.shape[0]}"
            )

    if c_cones is None:
        c_cones = [np.zeros(n) for _ in A_list]
    c_list = [_as_vec(c_i, f"c_cones[{i}]") for i, c_i in enumerate(c_cones)]
    if len(c_list) != k:
        raise ValueError(
            f"c_cones has length {len(c_list)} but A_cones has length {k}"
        )
    for i, ci in enumerate(c_list):
        if ci.size != n:
            raise ValueError(
                f"c_cones[{i}] has size {ci.size}; expected {n}"
            )

    if d_cones is None:
        d_cones = [0.0] * k
    d_list = [float(d_i) for d_i in d_cones]
    if len(d_list) != k:
        raise ValueError(
            f"d_cones has length {len(d_list)} but A_cones has length {k}"
        )

    A_eq_arr = None
    b_eq_arr = None
    if A_eq is not None or b_eq is not None:
        if A_eq is None or b_eq is None:
            raise ValueError("A_eq and b_eq must both be provided or both None.")
        A_eq_arr = _as_mat(A_eq, "A_eq")
        b_eq_arr = _as_vec(b_eq, "b_eq")
        if A_eq_arr.shape[1] != n:
            raise ValueError(
                f"A_eq has shape {A_eq_arr.shape}; expected (*, {n})"
            )
        if b_eq_arr.size != A_eq_arr.shape[0]:
            raise ValueError(
                f"b_eq has size {b_eq_arr.size}; expected {A_eq_arr.shape[0]}"
            )

    cp = _import_cvxpy()
    x = cp.Variable(n)
    constraints = []
    for A_i, b_i, c_i, d_i in zip(A_list, b_list, c_list, d_list):
        # ||A_i x + b_i||_2 <= c_i^T x + d_i
        constraints.append(cp.SOC(c_i @ x + d_i, A_i @ x + b_i))
    if A_eq_arr is not None:
        constraints.append(A_eq_arr @ x == b_eq_arr)

    objective = cp.Minimize(c_arr @ x)
    prob = cp.Problem(objective, constraints)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        try:
            prob.solve(verbose=verbose)
        except cp.error.SolverError as exc:  # pragma: no cover
            return {
                "x": None,
                "optimal_value": None,
                "status": f"solver_error: {exc}",
                "solver_used": "cvxpy",
                "n_iter": None,
            }

    status = str(prob.status)
    if status in ("optimal", "optimal_inaccurate") and x.value is not None:
        x_val = np.asarray(x.value, dtype=float)
        val = float(prob.value)
    else:
        x_val = None
        val = None
    return {
        "x": x_val,
        "optimal_value": val,
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": _extract_n_iter(prob),
    }


# ---------------------------------------------------------------------------
# 2. solve_robust_lp — LP under bounded uncertainty in the constraint rows
# ---------------------------------------------------------------------------


def solve_robust_lp(
    c,
    A,
    b,
    uncertainty_radius: float = 0.0,
    ord: str = "inf",
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Robust LP with row-wise uncertainty in the constraint matrix.

        minimize    c^T x
        subject to  (a_i + u_i)^T x <= b_i  for all ||u_i||_p <= rho

    For ``ord = 2`` the worst-case constraint is the SOCP

        a_i^T x + rho ||x||_2 <= b_i.

    For ``ord = 'inf'`` the worst-case is the LP

        a_i^T x + rho ||x||_1 <= b_i.

    For ``ord = 1`` it is

        a_i^T x + rho ||x||_inf <= b_i.

    Either way we reformulate via the dual norm of the uncertainty.

    Parameters
    ----------
    c : (n,) array_like
        Linear objective.
    A : (m, n) array_like
        Nominal constraint matrix.
    b : (m,) array_like
        Constraint rhs.
    uncertainty_radius : float >= 0
        ``rho`` in the formulation above. ``0`` reduces to the standard LP.
    ord : {2, 'inf', 1}
        Norm bounding the uncertainty per constraint row.
    solver : {'cvxpy'}
    verbose : bool

    Returns
    -------
    dict with keys ``x``, ``optimal_value``, ``status``, ``solver_used``,
    ``n_iter``, ``uncertainty_radius``, ``ord``.

    References
    ----------
    Ben-Tal, Nemirovski, "Robust solutions of linear programming
    problems contaminated with uncertain data", Math. Prog. 88 (2000),
    411-424.
    """
    _check_solver(solver)
    if uncertainty_radius < 0:
        raise ValueError(
            f"uncertainty_radius must be >= 0; got {uncertainty_radius}"
        )
    if ord not in (2, "inf", 1):
        raise ValueError(f"ord must be 2, 'inf' or 1; got {ord!r}")
    c_arr = _as_vec(c, "c")
    A_arr = _as_mat(A, "A")
    b_arr = _as_vec(b, "b")
    n = c_arr.size
    if n == 0:
        raise ValueError("c must be non-empty")
    if A_arr.shape[1] != n:
        raise ValueError(f"A has shape {A_arr.shape}; expected (*, {n})")
    if b_arr.size != A_arr.shape[0]:
        raise ValueError(
            f"b has size {b_arr.size}; expected {A_arr.shape[0]}"
        )

    cp = _import_cvxpy()
    x = cp.Variable(n)
    rho = float(uncertainty_radius)

    if ord == 2:
        # Dual of L2 is L2.
        cons = [A_arr @ x + rho * cp.norm(x, 2) <= b_arr]
    elif ord == "inf":
        # Dual of Linf is L1.
        cons = [A_arr @ x + rho * cp.norm(x, 1) <= b_arr]
    else:  # ord == 1
        # Dual of L1 is Linf.
        cons = [A_arr @ x + rho * cp.norm(x, "inf") <= b_arr]

    prob = cp.Problem(cp.Minimize(c_arr @ x), cons)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(verbose=verbose)
    status = str(prob.status)
    if status in ("optimal", "optimal_inaccurate") and x.value is not None:
        x_val = np.asarray(x.value, dtype=float)
        val = float(prob.value)
    else:
        x_val = None
        val = None
    return {
        "x": x_val,
        "optimal_value": val,
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": _extract_n_iter(prob),
        "uncertainty_radius": rho,
        "ord": ord,
    }


# ---------------------------------------------------------------------------
# 3. chebyshev_center — largest inscribed ball in {Ax <= b}
# ---------------------------------------------------------------------------


def chebyshev_center(
    A,
    b,
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Compute the Chebyshev centre of the polytope ``{ x : A x <= b }``.

    The Chebyshev centre is the centre of the largest Euclidean ball
    that fits inside the polytope.  It is found by solving the SOCP

        maximize    r
        subject to  a_i^T x + r ||a_i||_2 <= b_i,  i = 1..m
                    r >= 0.

    Parameters
    ----------
    A : (m, n) array_like
    b : (m,) array_like
    solver : {'cvxpy'}
    verbose : bool

    Returns
    -------
    dict with keys ``center`` (np.ndarray, shape (n,)),
    ``radius`` (float), ``status``, ``solver_used``, ``n_iter``.

    References
    ----------
    Boyd & Vandenberghe, "Convex Optimization", §8.5.1 (eq. 8.5).
    """
    _check_solver(solver)
    A_arr = _as_mat(A, "A")
    b_arr = _as_vec(b, "b")
    if b_arr.size != A_arr.shape[0]:
        raise ValueError(
            f"b has size {b_arr.size}; expected {A_arr.shape[0]}"
        )
    n = A_arr.shape[1]
    norms = np.linalg.norm(A_arr, axis=1)

    cp = _import_cvxpy()
    x = cp.Variable(n)
    r = cp.Variable(nonneg=True)
    cons = [A_arr @ x + norms * r <= b_arr]
    prob = cp.Problem(cp.Maximize(r), cons)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(verbose=verbose)
    status = str(prob.status)
    if status in ("optimal", "optimal_inaccurate") and x.value is not None:
        center = np.asarray(x.value, dtype=float)
        radius = float(r.value)
    else:
        center = None
        radius = None
    return {
        "center": center,
        "radius": radius,
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": _extract_n_iter(prob),
    }


# ---------------------------------------------------------------------------
# 4. min_volume_ellipsoid — Lowner-John MVEE around a finite point set
# ---------------------------------------------------------------------------


def min_volume_ellipsoid(
    points,
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Minimum-volume enclosing ellipsoid (Lowner-John ellipsoid).

    Parameterise the ellipsoid as ``{ y : ||A y + b||_2 <= 1 }`` with
    ``A`` symmetric positive definite.  The volume is proportional to
    ``1 / det(A)``, so we

        maximize    log det(A)
        subject to  ||A x_i + b||_2 <= 1     for each input point x_i
                    A symmetric.

    The centre of the ellipsoid is ``c = -A^{-1} b`` and the principal
    semi-axes are ``1 / sigma_k(A)`` (the reciprocals of the singular
    values of ``A``).

    Parameters
    ----------
    points : (N, n) array_like
        Point cloud (N points in n dimensions). N >= n is required.
    solver : {'cvxpy'}
    verbose : bool

    Returns
    -------
    dict with keys ``center`` ((n,) array), ``A`` ((n, n) array; the
    shape matrix as defined above), ``P`` ((n, n) array; ``A^T A``),
    ``radius_axes`` ((n,) array of semi-axis lengths in decreasing
    order), ``status``, ``solver_used``, ``n_iter``.

    References
    ----------
    Boyd & Vandenberghe, "Convex Optimization", §8.4.1 (eq. 8.10).
    Sun & Freund, "Computation of Minimum-Volume Covering Ellipsoids",
    OR 52(5), 2004.
    """
    _check_solver(solver)
    pts = _as_mat(points, "points")
    N, n = pts.shape
    if N < n:
        raise ValueError(
            f"min_volume_ellipsoid needs at least n={n} points; got {N}"
        )

    cp = _import_cvxpy()
    A = cp.Variable((n, n), symmetric=True)
    b = cp.Variable(n)
    cons = [cp.norm(A @ pts[i] + b, 2) <= 1 for i in range(N)]
    prob = cp.Problem(cp.Maximize(cp.log_det(A)), cons)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(verbose=verbose)
    status = str(prob.status)
    if status not in ("optimal", "optimal_inaccurate") or A.value is None:
        return {
            "center": None,
            "A": None,
            "P": None,
            "radius_axes": None,
            "status": status,
            "solver_used": "cvxpy",
            "n_iter": _extract_n_iter(prob),
        }
    A_val = 0.5 * (np.asarray(A.value, dtype=float) + np.asarray(A.value, dtype=float).T)
    b_val = np.asarray(b.value, dtype=float)
    # Centre c satisfies A c + b = 0  =>  c = -A^{-1} b.
    try:
        center = -np.linalg.solve(A_val, b_val)
    except np.linalg.LinAlgError:
        center = None
    sigmas = np.linalg.svd(A_val, compute_uv=False)
    # Semi-axes are reciprocals of singular values.
    radius_axes = 1.0 / np.maximum(sigmas, 1e-300)
    radius_axes = np.sort(radius_axes)[::-1]
    P = A_val.T @ A_val
    return {
        "center": center,
        "A": A_val,
        "P": P,
        "radius_axes": radius_axes,
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": _extract_n_iter(prob),
    }


# ---------------------------------------------------------------------------
# 5. portfolio_socp — Markowitz mean-variance via SOCP
# ---------------------------------------------------------------------------


def portfolio_socp(
    returns_mean,
    returns_cov,
    target_return: Optional[float] = None,
    risk_target: Optional[float] = None,
    long_only: bool = True,
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Mean-variance portfolio optimisation cast as an SOCP.

    Two operating modes (mutually exclusive; at most one may be set):

    1. ``target_return`` given, ``risk_target=None``::

           minimise   ||L^T w||_2          (= sqrt(w^T Sigma w))
           subject to  mu^T w >= target_return
                       1^T w = 1
                       w >= 0  (if long_only)

    2. ``risk_target`` given, ``target_return=None``::

           maximise   mu^T w
           subject to  ||L^T w||_2 <= risk_target
                       1^T w = 1
                       w >= 0  (if long_only)

    3. Neither given: maximise ``mu^T w`` subject only to the budget
       (and long-only) constraints.  This degenerates to an LP that
       puts all weight on the highest-return asset.

    Parameters
    ----------
    returns_mean : (n,) array_like
        Expected returns vector ``mu``.
    returns_cov : (n, n) array_like
        Return covariance ``Sigma``. Must be symmetric PSD.
    target_return : float, optional
    risk_target : float, optional
    long_only : bool
        If True, enforces ``w >= 0``.
    solver : {'cvxpy'}
    verbose : bool

    Returns
    -------
    dict with keys ``weights``, ``expected_return``, ``risk`` (the
    sqrt(w^T Sigma w) standard deviation), ``optimal_value``,
    ``status``, ``solver_used``, ``n_iter``.

    References
    ----------
    Markowitz, "Portfolio selection", J. Finance 7 (1952), 77-91.
    Lobo et al., "Applications of second-order cone programming",
    LAA 284 (1998), §3.4.
    """
    _check_solver(solver)
    if target_return is not None and risk_target is not None:
        raise ValueError(
            "Specify at most one of target_return or risk_target."
        )
    mu = _as_vec(returns_mean, "returns_mean")
    Sigma = _as_mat(returns_cov, "returns_cov")
    n = mu.size
    if n == 0:
        raise ValueError("returns_mean must be non-empty")
    if Sigma.shape != (n, n):
        raise ValueError(
            f"returns_cov has shape {Sigma.shape}; expected ({n}, {n})"
        )
    Sigma_sym = 0.5 * (Sigma + Sigma.T)
    eigvals = np.linalg.eigvalsh(Sigma_sym)
    if eigvals.min() < -1e-8 * max(1.0, abs(eigvals.max())):
        raise ValueError(
            f"returns_cov is not PSD; min eigenvalue = {eigvals.min():.3e}"
        )
    # Cholesky-style factor.  Add tiny ridge for numerical PSD.
    ridge = max(0.0, -eigvals.min()) + 1e-12
    L = np.linalg.cholesky(Sigma_sym + ridge * np.eye(n))

    cp = _import_cvxpy()
    w = cp.Variable(n)
    cons = [cp.sum(w) == 1.0]
    if long_only:
        cons.append(w >= 0)
    risk_expr = cp.norm(L.T @ w, 2)

    if target_return is not None:
        cons.append(mu @ w >= float(target_return))
        objective = cp.Minimize(risk_expr)
    elif risk_target is not None:
        if risk_target < 0:
            raise ValueError(
                f"risk_target must be non-negative; got {risk_target}"
            )
        cons.append(risk_expr <= float(risk_target))
        objective = cp.Maximize(mu @ w)
    else:
        objective = cp.Maximize(mu @ w)

    prob = cp.Problem(objective, cons)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(verbose=verbose)
    status = str(prob.status)
    if status not in ("optimal", "optimal_inaccurate") or w.value is None:
        return {
            "weights": None,
            "expected_return": None,
            "risk": None,
            "optimal_value": None,
            "status": status,
            "solver_used": "cvxpy",
            "n_iter": _extract_n_iter(prob),
        }
    weights = np.asarray(w.value, dtype=float)
    er = float(mu @ weights)
    var = float(weights @ Sigma_sym @ weights)
    risk = float(np.sqrt(max(var, 0.0)))
    return {
        "weights": weights,
        "expected_return": er,
        "risk": risk,
        "optimal_value": float(prob.value),
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": _extract_n_iter(prob),
    }


# ---------------------------------------------------------------------------
# 6. facility_location_socp — continuous Euclidean facility placement
# ---------------------------------------------------------------------------


def facility_location_socp(
    facility_costs,
    demands,
    distances,
    capacity: Optional[float] = None,
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Continuous facility-location with Euclidean transport cost.

    For each facility ``j`` we have a fixed cost ``f_j``; for each
    demand point ``i`` we have weight ``w_i`` and a per-unit-distance
    transport cost via the matrix ``distances`` (interpreted as the
    nominal Euclidean distance between facility ``j`` and demand
    ``i``).  We solve

        minimise    sum_j f_j + sum_{i,j} w_i * d_{ij} * t_{ij}
        subject to  sum_j t_{ij} = 1                (each demand fully served)
                    t_{ij} >= 0
                    sum_i w_i * t_{ij} <= capacity   (if ``capacity`` set)

    with the ``j`` summation weighted via the cone constraint
    ``||sum t_{ij} (demand_i - facility_j)||_2 <= ...`` form.  The
    public-API convenience here keeps facility positions fixed and
    returns the optimal transport plan ``t``.  This is the
    "transportation LP with Euclidean unit cost" — already an SOCP if
    extended to dynamic facility placement, and we expose the
    constrained version that calls cvxpy with conic-eligible structure.

    Parameters
    ----------
    facility_costs : (J,) array_like
        Fixed cost f_j for facility j.
    demands : (I,) array_like
        Demand weights w_i for client i.
    distances : (I, J) array_like
        Distance d_{ij} between client i and facility j.
    capacity : float, optional
        Per-facility capacity bound.
    solver : {'cvxpy'}

    Returns
    -------
    dict with keys ``transport`` ((I, J) array), ``optimal_value``
    (total cost), ``status``, ``solver_used``, ``n_iter``.

    References
    ----------
    Lobo, Vandenberghe, Boyd, Lebret (1998), §3.5.
    """
    _check_solver(solver)
    f = _as_vec(facility_costs, "facility_costs")
    w = _as_vec(demands, "demands")
    D = _as_mat(distances, "distances")
    I, J = D.shape
    if w.size != I:
        raise ValueError(
            f"demands has size {w.size}; expected {I} (rows of distances)"
        )
    if f.size != J:
        raise ValueError(
            f"facility_costs has size {f.size}; expected {J} (cols of distances)"
        )

    cp = _import_cvxpy()
    t = cp.Variable((I, J), nonneg=True)
    cons = [cp.sum(t, axis=1) == 1.0]
    if capacity is not None:
        cons.append(w @ t <= float(capacity))
    transport_cost = cp.sum(cp.multiply(np.diag(w) @ D, t))
    objective = cp.Minimize(cp.sum(f) + transport_cost)
    prob = cp.Problem(objective, cons)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        prob.solve(verbose=verbose)
    status = str(prob.status)
    if status not in ("optimal", "optimal_inaccurate") or t.value is None:
        return {
            "transport": None,
            "optimal_value": None,
            "status": status,
            "solver_used": "cvxpy",
            "n_iter": _extract_n_iter(prob),
        }
    return {
        "transport": np.asarray(t.value, dtype=float),
        "optimal_value": float(prob.value),
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": _extract_n_iter(prob),
    }
