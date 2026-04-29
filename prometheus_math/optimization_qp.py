"""prometheus_math.optimization_qp — Quadratic programming wrappers.

Standard QP formulation:

    minimize    (1/2) x^T P x + q^T x
    subject to  G x <= h           (linear inequality)
                A x  = b           (linear equality)
                lb <= x <= ub      (box bounds, optional)

Convexity requires P to be positive semidefinite (P >= 0). The wrappers
in this module enforce a symmetric P (warning if not, then symmetrize)
and accept a small `psd_tol` for numerical PSD checking.

Backends
--------
- ``cvxpy`` (default): canonical convex modeller; routes to OSQP, ECOS,
  SCS, CLARABEL depending on what's installed. High accuracy but
  somewhat slower for very small QPs.
- ``scipy``: uses ``scipy.optimize.minimize(method='SLSQP')`` with explicit
  Jacobians. Faster on tiny problems but lower precision (~1e-6 vs ~1e-8
  for cvxpy/OSQP). SLSQP can struggle with rank-deficient Hessians and is
  not a true convex solver — for production convex QPs prefer cvxpy.

Solver-vs-tolerance tradeoffs
-----------------------------
- cvxpy/OSQP: relative tolerance ~1e-6 by default; very robust on convex
  problems; can polish to ~1e-9. Slow startup (~50 ms compile time).
- cvxpy/CLARABEL: comparable to OSQP, often more accurate for
  ill-conditioned P.
- scipy/SLSQP: accuracy depends on `ftol` (default 1e-6); not designed
  for QP — convergence on degenerate or rank-deficient P is fragile.

Public API
----------
- ``solve_qp(P, q, G, h, A, b, lb, ub, solver='cvxpy', verbose=False)``
- ``solve_box_qp(P, q, lb, ub, solver='cvxpy')``
- ``solve_constrained_least_squares(A, b, G, h, A_eq, b_eq, lb, ub,
  solver='cvxpy')``
- ``solve_quantile_regression(X, y, tau=0.5, solver='cvxpy')``
- ``solve_lasso_qp(X, y, alpha=1.0, solver='cvxpy')``

All return a dict with at minimum::

    {x: ndarray | None,
     optimal_value: float | None,
     status: 'optimal' | 'infeasible' | 'unbounded' | 'unknown' | ...,
     solver_used: str,
     n_iter: int | None}
"""
from __future__ import annotations

from typing import Optional

import warnings

import numpy as np

from .registry import is_available


__all__ = [
    "solve_qp",
    "solve_box_qp",
    "solve_constrained_least_squares",
    "solve_quantile_regression",
    "solve_lasso_qp",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_KNOWN_SOLVERS = {"cvxpy", "scipy"}


def _check_solver(solver: str) -> str:
    if solver not in _KNOWN_SOLVERS:
        raise ValueError(
            f"Unknown solver {solver!r}; choose from {sorted(_KNOWN_SOLVERS)}"
        )
    if solver == "cvxpy" and not is_available("cvxpy"):
        raise ImportError(
            "cvxpy is not installed; install with `pip install cvxpy` or "
            "pass solver='scipy' for the SLSQP fallback (lower precision, "
            "see module docstring)."
        )
    if solver == "scipy" and not is_available("scipy"):
        raise ImportError("scipy is not installed; install with `pip install scipy`.")
    return solver


def _validate_P(P: np.ndarray, psd_tol: float = 1e-8) -> np.ndarray:
    """Return a symmetrized copy of P. Raise on non-PSD or wrong shape."""
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError(f"P must be a square 2-D array; got shape {P.shape}")
    sym_err = np.max(np.abs(P - P.T)) if P.size else 0.0
    if sym_err > 1e-8:
        warnings.warn(
            f"P is not symmetric (max |P - P.T| = {sym_err:.2e}); symmetrizing.",
            RuntimeWarning,
            stacklevel=3,
        )
    P = 0.5 * (P + P.T)
    if P.size:
        # Eigenvalues of symmetric matrix are real.
        eigvals = np.linalg.eigvalsh(P)
        if eigvals.min() < -psd_tol * max(1.0, abs(eigvals.max())):
            raise ValueError(
                f"P is not positive semidefinite; min eigenvalue = "
                f"{eigvals.min():.3e} (psd_tol={psd_tol})."
            )
    return P


def _coerce_vec(v, name, n) -> Optional[np.ndarray]:
    if v is None:
        return None
    arr = np.asarray(v, dtype=float).ravel()
    if arr.size != n:
        raise ValueError(f"{name}: expected length {n}, got {arr.size}")
    return arr


def _coerce_mat(M, name, n) -> Optional[np.ndarray]:
    if M is None:
        return None
    arr = np.asarray(M, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2 or arr.shape[1] != n:
        raise ValueError(
            f"{name}: expected shape (m, {n}); got {arr.shape}"
        )
    return arr


def _empty_result(solver: str) -> dict:
    return {
        "x": np.empty(0, dtype=float),
        "optimal_value": 0.0,
        "status": "optimal",
        "solver_used": solver,
        "n_iter": 0,
    }


# ---------------------------------------------------------------------------
# Core: solve_qp
# ---------------------------------------------------------------------------


def solve_qp(
    P,
    q,
    G=None,
    h=None,
    A=None,
    b=None,
    lb=None,
    ub=None,
    solver: str = "cvxpy",
    verbose: bool = False,
) -> dict:
    """Solve a (convex) quadratic program.

    Minimise ``(1/2) x^T P x + q^T x`` subject to ``G x <= h``,
    ``A x = b``, and optional box bounds ``lb <= x <= ub``.

    Parameters
    ----------
    P : (n, n) array_like
        Symmetric positive-semidefinite Hessian. Non-symmetric input is
        symmetrised with a warning. Strict non-PSD (eigenvalue below
        ``-psd_tol``) raises ``ValueError``.
    q : (n,) array_like
        Linear coefficient.
    G, h : optional (m, n), (m,) array_like
        Linear inequality ``G x <= h``.
    A, b : optional (p, n), (p,) array_like
        Linear equality ``A x = b``.
    lb, ub : optional (n,) array_like
        Box bounds. ``None`` entries treated as +/-inf.
    solver : {'cvxpy', 'scipy'}
        See module docstring for tradeoffs.
    verbose : bool
        Forwarded to the underlying solver.

    Returns
    -------
    dict with keys ``x``, ``optimal_value``, ``status``, ``solver_used``,
    ``n_iter``. ``x`` is an ``np.ndarray`` (or ``None`` if infeasible).

    Notes
    -----
    For ``n == 0`` (empty variable) the trivial result ``x = []``,
    ``optimal_value = 0`` is returned.
    """
    _check_solver(solver)
    P = np.asarray(P, dtype=float)
    if P.size == 0 and P.shape == (0, 0):
        return _empty_result(solver)
    P = _validate_P(P)
    n = P.shape[0]
    q = _coerce_vec(q, "q", n)
    if q is None:
        q = np.zeros(n)
    G = _coerce_mat(G, "G", n) if G is not None else None
    h = _coerce_vec(h, "h", G.shape[0]) if G is not None else None
    if (G is None) != (h is None):
        raise ValueError("G and h must both be provided or both None.")
    A_eq = _coerce_mat(A, "A", n) if A is not None else None
    b_eq = _coerce_vec(b, "b", A_eq.shape[0]) if A_eq is not None else None
    if (A_eq is None) != (b_eq is None):
        raise ValueError("A and b must both be provided or both None.")
    lb = _coerce_vec(lb, "lb", n)
    ub = _coerce_vec(ub, "ub", n)
    if lb is not None and ub is not None:
        if np.any(lb > ub + 1e-12):
            raise ValueError("Inconsistent box bounds: lb > ub somewhere.")

    if solver == "cvxpy":
        return _qp_cvxpy(P, q, G, h, A_eq, b_eq, lb, ub, verbose)
    return _qp_scipy(P, q, G, h, A_eq, b_eq, lb, ub, verbose)


def _qp_cvxpy(P, q, G, h, A_eq, b_eq, lb, ub, verbose) -> dict:
    import cvxpy as cp

    n = P.shape[0]
    x = cp.Variable(n)
    # cvxpy's quad_form requires PSD (it checks). We've already validated.
    objective = cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(P)) + q @ x)
    cons = []
    if G is not None:
        cons.append(G @ x <= h)
    if A_eq is not None:
        cons.append(A_eq @ x == b_eq)
    if lb is not None:
        mask = np.isfinite(lb)
        if mask.any():
            cons.append(x[mask] >= lb[mask])
    if ub is not None:
        mask = np.isfinite(ub)
        if mask.any():
            cons.append(x[mask] <= ub[mask])
    prob = cp.Problem(objective, cons)
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
    if status in ("optimal", "optimal_inaccurate"):
        x_val = np.asarray(x.value, dtype=float)
        val = float(prob.value)
    else:
        x_val = None
        val = None
    n_iter = None
    try:
        stats = prob.solver_stats
        if stats is not None and stats.num_iters is not None:
            n_iter = int(stats.num_iters)
    except Exception:
        pass
    return {
        "x": x_val,
        "optimal_value": val,
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": n_iter,
    }


def _qp_scipy(P, q, G, h, A_eq, b_eq, lb, ub, verbose) -> dict:
    from scipy.optimize import minimize

    n = P.shape[0]

    def f(x):
        return 0.5 * x @ P @ x + q @ x

    def grad(x):
        return P @ x + q

    constraints = []
    if G is not None:
        constraints.append(
            {"type": "ineq", "fun": lambda x, G=G, h=h: h - G @ x,
             "jac": lambda x, G=G: -G}
        )
    if A_eq is not None:
        constraints.append(
            {"type": "eq", "fun": lambda x, A=A_eq, b=b_eq: A @ x - b,
             "jac": lambda x, A=A_eq: A}
        )
    bounds = None
    if lb is not None or ub is not None:
        lb_arr = lb if lb is not None else np.full(n, -np.inf)
        ub_arr = ub if ub is not None else np.full(n, np.inf)
        bounds = list(zip(
            [None if not np.isfinite(v) else float(v) for v in lb_arr],
            [None if not np.isfinite(v) else float(v) for v in ub_arr],
        ))
    x0 = np.zeros(n)
    if bounds is not None:
        # Project x0 into box.
        for i, (lo, hi) in enumerate(bounds):
            if lo is not None and x0[i] < lo:
                x0[i] = lo
            if hi is not None and x0[i] > hi:
                x0[i] = hi
    res = minimize(
        f, x0, jac=grad, method="SLSQP",
        constraints=constraints if constraints else (),
        bounds=bounds,
        options={"disp": verbose, "maxiter": 200, "ftol": 1e-9},
    )
    success = bool(res.success)
    status = "optimal" if success else (str(res.message) or "unknown")
    return {
        "x": np.asarray(res.x, dtype=float) if success else None,
        "optimal_value": float(res.fun) if success else None,
        "status": status if success else status,
        "solver_used": "scipy",
        "n_iter": int(getattr(res, "nit", 0) or 0),
    }


# ---------------------------------------------------------------------------
# Specialised wrappers
# ---------------------------------------------------------------------------


def solve_box_qp(P, q, lb, ub, solver: str = "cvxpy") -> dict:
    """Box-constrained QP: ``min (1/2) x^T P x + q^T x`` s.t. ``lb <= x <= ub``.

    Convenience wrapper around :func:`solve_qp` with no general
    inequality / equality constraints.
    """
    return solve_qp(P, q, lb=lb, ub=ub, solver=solver)


def solve_constrained_least_squares(
    A,
    b,
    G=None,
    h=None,
    A_eq=None,
    b_eq=None,
    lb=None,
    ub=None,
    solver: str = "cvxpy",
) -> dict:
    """Solve constrained least squares.

    Minimise ``||A x - b||^2`` subject to ``G x <= h``, ``A_eq x = b_eq``,
    ``lb <= x <= ub``. Recast as a QP with ``P = 2 A^T A`` and
    ``q = -2 A^T b``. The ``optimal_value`` returned is the QP objective
    (i.e. ``||A x - b||^2 - ||b||^2``); a ``residual_norm_sq`` key is
    added for the actual squared residual ``||A x - b||^2``.

    Without any constraints this matches ``np.linalg.lstsq`` to ~1e-8.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float).ravel()
    if A.ndim != 2:
        raise ValueError(f"A must be 2-D; got shape {A.shape}")
    if A.shape[0] != b.size:
        raise ValueError(
            f"Inconsistent shapes: A has {A.shape[0]} rows but b has {b.size}"
        )
    n = A.shape[1]
    P = 2.0 * A.T @ A
    q = -2.0 * A.T @ b
    res = solve_qp(P, q, G=G, h=h, A=A_eq, b=b_eq, lb=lb, ub=ub, solver=solver)
    if res["x"] is not None:
        x = res["x"]
        residual_sq = float(np.sum((A @ x - b) ** 2))
        res["residual_norm_sq"] = residual_sq
    else:
        res["residual_norm_sq"] = None
    return res


def solve_quantile_regression(
    X,
    y,
    tau: float = 0.5,
    solver: str = "cvxpy",
) -> dict:
    """Quantile regression at level ``tau`` (0 < tau < 1).

    Solves ``min sum_i rho_tau(y_i - X_i beta)`` where the check function
    is ``rho_tau(u) = u (tau - 1{u<0}) = tau * max(u, 0) + (1-tau)*max(-u, 0)``.

    Cast as an LP via slack variables ``u_i, v_i >= 0`` with
    ``u_i - v_i = y_i - X_i beta``, objective ``tau sum u + (1-tau) sum v``.

    For ``tau = 0.5`` (the median), this reduces to L1 / least-absolute-
    deviation regression. Although this is a linear program rather than a
    quadratic one, it is grouped here because LP/QP wrappers commonly
    sit together (as in scipy and cvxpy).

    Returns
    -------
    dict with keys ``x`` (the coefficient vector ``beta``),
    ``optimal_value`` (the achieved tilted-loss), ``status``,
    ``solver_used``, ``n_iter``.
    """
    if not (0.0 < tau < 1.0):
        raise ValueError(f"tau must lie strictly in (0, 1); got {tau}")
    _check_solver(solver)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    if X.ndim != 2 or X.shape[0] != y.size:
        raise ValueError(
            f"X has shape {X.shape}, y has size {y.size}; rows must match."
        )
    if solver != "cvxpy":
        # Provide an LP fallback via solve_qp would be wasteful — quantile
        # regression is best done in cvxpy. SLSQP through a non-smooth
        # objective is a poor fit.
        raise NotImplementedError(
            "solve_quantile_regression currently only supports solver='cvxpy'."
        )
    import cvxpy as cp

    n_samples, n_feat = X.shape
    beta = cp.Variable(n_feat)
    residuals = y - X @ beta
    # rho_tau(u) = tau * pos(u) + (1 - tau) * pos(-u)
    loss = tau * cp.sum(cp.pos(residuals)) + (1.0 - tau) * cp.sum(cp.pos(-residuals))
    prob = cp.Problem(cp.Minimize(loss))
    prob.solve()
    status = str(prob.status)
    if status in ("optimal", "optimal_inaccurate"):
        x_val = np.asarray(beta.value, dtype=float)
        val = float(prob.value)
    else:
        x_val = None
        val = None
    n_iter = None
    try:
        if prob.solver_stats is not None and prob.solver_stats.num_iters is not None:
            n_iter = int(prob.solver_stats.num_iters)
    except Exception:
        pass
    return {
        "x": x_val,
        "optimal_value": val,
        "status": status,
        "solver_used": "cvxpy",
        "n_iter": n_iter,
        "tau": tau,
    }


def solve_lasso_qp(
    X,
    y,
    alpha: float = 1.0,
    solver: str = "cvxpy",
) -> dict:
    """Lasso (L1-regularised least squares) cast as a QP via slack variables.

    Solves ``min (1/(2n)) ||X beta - y||^2 + alpha * ||beta||_1``
    by introducing ``u >= 0`` with ``-u <= beta <= u`` and replacing
    ``||beta||_1`` with ``sum(u)``. The resulting program is a QP in
    the joint variable ``[beta; u]``.

    Parameters
    ----------
    alpha : float, ``>= 0``
        Regularisation strength. ``alpha = 0`` reduces to ordinary least
        squares; large ``alpha`` shrinks all coefficients to zero.

    Returns
    -------
    dict with keys ``x`` (beta), ``optimal_value`` (the lasso objective),
    ``status``, ``solver_used``, ``n_iter``.
    """
    if alpha < 0:
        raise ValueError(f"alpha must be non-negative; got {alpha}")
    _check_solver(solver)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    if X.ndim != 2 or X.shape[0] != y.size:
        raise ValueError(
            f"X has shape {X.shape}, y has size {y.size}; rows must match."
        )
    n_samples, n_feat = X.shape
    if solver == "cvxpy":
        import cvxpy as cp

        beta = cp.Variable(n_feat)
        loss = (1.0 / (2.0 * n_samples)) * cp.sum_squares(X @ beta - y)
        objective = cp.Minimize(loss + alpha * cp.norm1(beta))
        prob = cp.Problem(objective)
        prob.solve()
        status = str(prob.status)
        if status in ("optimal", "optimal_inaccurate"):
            x_val = np.asarray(beta.value, dtype=float)
            val = float(prob.value)
        else:
            x_val = None
            val = None
        n_iter = None
        try:
            if (prob.solver_stats is not None
                    and prob.solver_stats.num_iters is not None):
                n_iter = int(prob.solver_stats.num_iters)
        except Exception:
            pass
        return {
            "x": x_val,
            "optimal_value": val,
            "status": status,
            "solver_used": "cvxpy",
            "n_iter": n_iter,
            "alpha": alpha,
        }
    # scipy fallback: build the explicit QP in z = [beta; u].
    # Variables: beta (n_feat) followed by u (n_feat), with u >= 0.
    # Objective:  (1/(2n)) ||X beta - y||^2 + alpha * sum(u)
    # Constraints: -u <= beta <= u, i.e.
    #     beta - u <= 0
    #    -beta - u <= 0
    P = np.zeros((2 * n_feat, 2 * n_feat))
    P[:n_feat, :n_feat] = (1.0 / n_samples) * (X.T @ X)  # factor of 2 absorbed by 1/(2n)
    q = np.zeros(2 * n_feat)
    q[:n_feat] = -(1.0 / n_samples) * (X.T @ y)
    q[n_feat:] = alpha
    # Add small Tikhonov to keep the problem strictly PSD for SLSQP.
    P[:n_feat, :n_feat] += 1e-12 * np.eye(n_feat)
    G_top = np.hstack([np.eye(n_feat), -np.eye(n_feat)])
    G_bot = np.hstack([-np.eye(n_feat), -np.eye(n_feat)])
    G = np.vstack([G_top, G_bot])
    h = np.zeros(2 * n_feat)
    lb = np.concatenate([np.full(n_feat, -np.inf), np.zeros(n_feat)])
    ub = np.full(2 * n_feat, np.inf)
    qp = solve_qp(P, q, G=G, h=h, lb=lb, ub=ub, solver="scipy")
    if qp["x"] is not None:
        beta_val = qp["x"][:n_feat]
        # Recompute the actual lasso objective for clarity.
        residual = X @ beta_val - y
        actual = (1.0 / (2.0 * n_samples)) * float(residual @ residual) + \
            alpha * float(np.sum(np.abs(beta_val)))
        return {
            "x": beta_val,
            "optimal_value": actual,
            "status": qp["status"],
            "solver_used": "scipy",
            "n_iter": qp["n_iter"],
            "alpha": alpha,
        }
    return {
        "x": None,
        "optimal_value": None,
        "status": qp["status"],
        "solver_used": "scipy",
        "n_iter": qp["n_iter"],
        "alpha": alpha,
    }
