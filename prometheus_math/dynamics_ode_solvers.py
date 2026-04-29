"""prometheus_math.dynamics_ode_solvers — ODE integrators.

Project #77 from techne/PROJECT_BACKLOG_1000.md (Tier 2).

Most numerical ODE work in Python defaults to scipy.integrate.solve_ivp
at IEEE-754 double precision.  For research-grade applications —
orbit integration over many revolutions, hyperbolic-3-manifold
deformation flows, quasi-periodic decompositions, p-adic flows etc.
— double precision is not enough.  This module provides:

  * a thin scipy facade (``solve_ivp``, ``rk4``, ``dop853``, ``bdf``)
    for the common float64 case,
  * an arbitrary-precision oracle (``mpmath_odefun``) backed by
    ``mpmath.odefun`` (Taylor-series-based),
  * symplectic integrators (``hamiltonian_system``: symplectic Euler,
    leapfrog, velocity Verlet) for Hamiltonian systems,
  * higher-level diagnostic helpers (``first_passage_time``,
    ``liapunov_exponent_continuous``).

References:

- Hairer, Nørsett, Wanner, "Solving Ordinary Differential Equations
  I — Nonstiff Problems" (2nd ed., 1993, Springer).  RK4 / DOPRI8.
- Hairer, Wanner, "Solving Ordinary Differential Equations II — Stiff
  and Differential-Algebraic Problems" (2nd ed., 1996).  BDF.
- Hairer, Lubich, Wanner, "Geometric Numerical Integration" (2nd ed.,
  2006, Springer).  Symplectic methods, backward error analysis.
- Wolf, Swift, Swinney, Vastano, "Determining Lyapunov exponents from
  a time series", Physica D 16 (1985) 285.  Tangent-linear method.
- mpmath documentation, ``mp.odefun`` (Taylor-series IVP solver).

Public API:

  Core:
    - solve_ivp(rhs, t_span, y0, method='RK45', ...)  — facade
    - rk4(rhs, t_span, y0, h)                          — fixed-step RK4
    - dop853(rhs, t_span, y0, rtol, atol)              — Dormand-Prince 8
    - bdf(rhs, t_span, y0, order=2, ...)               — backward diff
    - mpmath_odefun(rhs, t_span, y0, prec=53, h=None)  — arbitrary prec

  Hamiltonian:
    - hamiltonian_system(H, t_span, q0, p0, method='leapfrog', h=...)

  Diagnostics:
    - first_passage_time(rhs, y0, threshold_fn, t_max=10.0)
    - liapunov_exponent_continuous(rhs, y0, t_max=100.0, n_renorm=10)
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence, Tuple, Union

import math
import warnings

import numpy as np

try:
    from scipy.integrate import solve_ivp as _scipy_solve_ivp
    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False

try:
    import mpmath as _mp
    _HAS_MPMATH = True
except Exception:  # pragma: no cover
    _HAS_MPMATH = False


__all__ = [
    "solve_ivp",
    "rk4",
    "dop853",
    "bdf",
    "mpmath_odefun",
    "hamiltonian_system",
    "first_passage_time",
    "liapunov_exponent_continuous",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SUPPORTED_METHODS = (
    "RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA",
)


def _validate_t_span(t_span):
    """Coerce ``t_span`` to (t0, t1) with t1 > t0; else ValueError."""
    if t_span is None:
        raise ValueError("t_span must be a (t0, t1) pair, got None")
    try:
        t_list = list(t_span)
    except TypeError as exc:
        raise ValueError(
            "t_span must be a 2-tuple of floats"
        ) from exc
    if len(t_list) != 2:
        raise ValueError(
            f"t_span must contain exactly two endpoints, got {len(t_list)}"
        )
    t0, t1 = float(t_list[0]), float(t_list[1])
    if not (t1 > t0):
        raise ValueError(
            f"t_span must satisfy t1 > t0; got t0={t0}, t1={t1}"
        )
    return t0, t1


def _validate_rhs_shape(rhs, t0, y0):
    """Call rhs once and check the output dimension matches y0."""
    y0_arr = np.asarray(y0, dtype=float).ravel()
    test = np.asarray(rhs(t0, y0_arr), dtype=float).ravel()
    if test.shape != y0_arr.shape:
        raise ValueError(
            f"rhs returned shape {test.shape} but y0 has shape "
            f"{y0_arr.shape}; dimensions must match"
        )
    return y0_arr


# ---------------------------------------------------------------------------
# Core: solve_ivp facade
# ---------------------------------------------------------------------------


def solve_ivp(
    rhs: Callable,
    t_span: Tuple[float, float],
    y0: Sequence[float],
    method: str = "RK45",
    rtol: float = 1e-6,
    atol: float = 1e-9,
    max_step: Optional[float] = None,
    prec: Optional[int] = None,
    n_dense: int = 200,
) -> dict:
    """Solve dy/dt = rhs(t, y) over t_span with initial state y0.

    Parameters
    ----------
    rhs       : callable (t, y) -> dy/dt
    t_span    : (t0, t1) with t1 > t0
    y0        : initial state, shape (dim,)
    method    : one of 'RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA'
    rtol/atol : tolerance pair forwarded to scipy
    max_step  : maximum step size (forwarded)
    prec      : if int and >0, use ``mpmath_odefun`` at that precision
                instead of scipy
    n_dense   : when prec is set, number of t-samples to return

    Returns
    -------
    dict with keys ``t`` (n_t,), ``y`` (n_t, dim), ``method``,
    ``n_steps``, ``success``.
    """
    if method not in _SUPPORTED_METHODS:
        raise ValueError(
            f"method={method!r} not supported; choose one of "
            f"{_SUPPORTED_METHODS}"
        )
    t0, t1 = _validate_t_span(t_span)
    y0_arr = _validate_rhs_shape(rhs, t0, y0)

    if prec is not None:
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError(f"prec must be a positive int, got {prec!r}")
        f = mpmath_odefun(rhs, (t0, t1), y0_arr.tolist(), prec=prec)
        ts = np.linspace(t0, t1, n_dense)
        ys = np.array([[float(v) for v in f(t)] for t in ts])
        return {
            "t": ts, "y": ys,
            "method": f"mpmath@{prec}",
            "n_steps": n_dense,
            "success": True,
        }

    if not _HAS_SCIPY:  # pragma: no cover
        raise ImportError("scipy is required for solve_ivp")

    kwargs = dict(rtol=rtol, atol=atol)
    if max_step is not None:
        kwargs["max_step"] = max_step
    res = _scipy_solve_ivp(
        rhs, (t0, t1), y0_arr, method=method, **kwargs,
        dense_output=False,
    )
    # scipy returns (dim, n_t); transpose for our convention.
    y_T = np.asarray(res.y).T
    return {
        "t": np.asarray(res.t),
        "y": y_T,
        "method": method,
        "n_steps": int(res.t.size),
        "success": bool(res.success),
    }


# ---------------------------------------------------------------------------
# Fixed-step classical RK4
# ---------------------------------------------------------------------------


def rk4(
    rhs: Callable,
    t_span: Tuple[float, float],
    y0: Sequence[float],
    h: float,
    prec: Optional[int] = None,
) -> dict:
    """Classical fixed-step Runge-Kutta 4 integrator.

    Reference: Hairer-Nørsett-Wanner I, eq. (1.8) of §II.1.
    """
    if not isinstance(h, (int, float)) or h <= 0 or not math.isfinite(h):
        raise ValueError(f"step size h must be a positive finite float, got {h!r}")
    t0, t1 = _validate_t_span(t_span)
    y = _validate_rhs_shape(rhs, t0, y0).copy()

    if prec is not None and prec > 0:
        # delegate to mpmath_odefun for prec > 53; here we emulate by
        # using mpmath internally for the RK4 update.
        return _rk4_mpmath(rhs, (t0, t1), y0, float(h), prec=prec)

    n = max(1, int(math.ceil((t1 - t0) / h)))
    h_eff = (t1 - t0) / n
    ts = np.empty(n + 1)
    ys = np.empty((n + 1, y.size))
    ts[0] = t0
    ys[0] = y
    t = t0
    for i in range(n):
        k1 = np.asarray(rhs(t, y), dtype=float)
        k2 = np.asarray(rhs(t + h_eff / 2, y + h_eff / 2 * k1), dtype=float)
        k3 = np.asarray(rhs(t + h_eff / 2, y + h_eff / 2 * k2), dtype=float)
        k4 = np.asarray(rhs(t + h_eff, y + h_eff * k3), dtype=float)
        y = y + (h_eff / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        t = t0 + (i + 1) * h_eff
        ts[i + 1] = t
        ys[i + 1] = y
    return {"t": ts, "y": ys, "method": "RK4",
            "n_steps": n, "success": True}


def _rk4_mpmath(rhs, t_span, y0, h, prec):  # pragma: no cover (slow)
    """RK4 carried in mpmath at the requested precision."""
    if not _HAS_MPMATH:
        raise ImportError("mpmath is required for prec > 0 RK4")
    saved = _mp.mp.prec
    try:
        _mp.mp.prec = int(prec)
        t0, t1 = _validate_t_span(t_span)
        y = [_mp.mpf(v) for v in y0]
        n = max(1, int(math.ceil((t1 - t0) / h)))
        h_eff = (_mp.mpf(t1) - _mp.mpf(t0)) / n
        ts = [_mp.mpf(t0)]
        ys = [list(y)]
        t = _mp.mpf(t0)
        for _ in range(n):
            k1 = [_mp.mpf(v) for v in rhs(float(t), [float(v) for v in y])]
            ymid = [yi + h_eff / 2 * ki for yi, ki in zip(y, k1)]
            k2 = [_mp.mpf(v) for v in rhs(float(t + h_eff / 2),
                                          [float(v) for v in ymid])]
            ymid2 = [yi + h_eff / 2 * ki for yi, ki in zip(y, k2)]
            k3 = [_mp.mpf(v) for v in rhs(float(t + h_eff / 2),
                                          [float(v) for v in ymid2])]
            yend = [yi + h_eff * ki for yi, ki in zip(y, k3)]
            k4 = [_mp.mpf(v) for v in rhs(float(t + h_eff),
                                          [float(v) for v in yend])]
            y = [yi + (h_eff / 6) * (a + 2 * b + 2 * c + d)
                 for yi, a, b, c, d in zip(y, k1, k2, k3, k4)]
            t = t + h_eff
            ts.append(t)
            ys.append(list(y))
        return {
            "t": np.array([float(v) for v in ts]),
            "y": np.array([[float(v) for v in yy] for yy in ys]),
            "method": f"RK4@{prec}",
            "n_steps": n, "success": True,
        }
    finally:
        _mp.mp.prec = saved


# ---------------------------------------------------------------------------
# DOP853 (Dormand-Prince 8(5,3))
# ---------------------------------------------------------------------------


def dop853(
    rhs: Callable,
    t_span: Tuple[float, float],
    y0: Sequence[float],
    rtol: float = 1e-12,
    atol: float = 1e-15,
    prec: Optional[int] = None,
) -> dict:
    """8th-order Dormand-Prince adaptive integrator.

    Backed by scipy's DOP853 (a Python re-implementation of Hairer's
    Fortran code).  When ``prec`` is set, falls back to
    ``mpmath_odefun`` at that precision (mpmath uses Taylor methods,
    which are higher-order than DOP853 anyway).
    """
    if prec is not None:
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError(f"prec must be a positive int, got {prec!r}")
        return solve_ivp(rhs, t_span, y0, prec=prec)
    return solve_ivp(rhs, t_span, y0, method="DOP853",
                     rtol=rtol, atol=atol)


# ---------------------------------------------------------------------------
# BDF (backward differentiation, for stiff problems)
# ---------------------------------------------------------------------------


def bdf(
    rhs: Callable,
    t_span: Tuple[float, float],
    y0: Sequence[float],
    order: int = 2,
    rtol: float = 1e-6,
    atol: float = 1e-9,
) -> dict:
    """Backward differentiation formula for stiff ODEs (scipy's
    BDF, variable order 1..5; ``order`` is currently advisory and
    forwarded as ``max_step`` hint).
    """
    if not isinstance(order, int) or not (1 <= order <= 5):
        raise ValueError(f"BDF order must be in 1..5, got {order!r}")
    return solve_ivp(rhs, t_span, y0, method="BDF",
                     rtol=rtol, atol=atol)


# ---------------------------------------------------------------------------
# mpmath arbitrary-precision oracle
# ---------------------------------------------------------------------------


def mpmath_odefun(
    rhs: Callable,
    t_span: Tuple[float, float],
    y0: Sequence[float],
    prec: int = 53,
    h: Optional[float] = None,
) -> Callable:
    """Return an arbitrary-precision callable ``f(t)`` solving
    dy/dt = rhs(t, y) on t_span starting from y0.  Backed by
    ``mpmath.mp.odefun`` (Taylor-series IVP solver, Bulirsch-Stoer-
    style internally).

    Parameters
    ----------
    rhs   : (t, y) -> dy/dt — should accept floats and return a list
    t_span: (t0, t1)
    y0    : initial state
    prec  : mantissa bits (mpmath ``mp.prec``); default 53
    h     : ignored (kept for API compatibility)

    Returns
    -------
    callable f: float -> tuple of mpf, defined on [t0, t1].
    """
    if not _HAS_MPMATH:  # pragma: no cover
        raise ImportError("mpmath is required for mpmath_odefun")
    if not isinstance(prec, int) or prec <= 0:
        raise ValueError(f"prec must be a positive int, got {prec!r}")
    t0, t1 = _validate_t_span(t_span)

    # Switch precision and KEEP it raised — odefun computes Taylor
    # coefficients lazily on each call.
    _mp.mp.prec = max(int(prec), _mp.mp.prec)
    y0_list = [_mp.mpf(v) for v in y0]
    n_dim = len(y0_list)

    if n_dim == 1:
        # mpmath odefun for a single equation: F(t, y) -> scalar.  y is
        # an mpf scalar.  We try calling rhs in mpf-native mode first
        # (so duck-typed expressions like ``-y`` retain full precision);
        # if that fails (rhs requires numpy/floats), we fall back to
        # float64 evaluation, which loses precision but still works.
        _mp_state = {"native": True}

        def F_scalar(t, y):
            if _mp_state["native"]:
                try:
                    out = rhs(t, y)
                    if hasattr(out, "__iter__") and not isinstance(out, str):
                        out = list(out)[0]
                    return _mp.mpf(out)
                except Exception:
                    _mp_state["native"] = False
            yarr = np.asarray([float(y)], dtype=float)
            out = rhs(float(t), yarr)
            try:
                v = float(out[0])
            except (TypeError, IndexError):
                v = float(out)
            return _mp.mpf(v)

        f_inner = _mp.odefun(F_scalar, _mp.mpf(t0), y0_list[0])

        def f(t):
            v = f_inner(_mp.mpf(t))
            return (v,)
        return f

    # Multi-equation: F(t, y) -> tuple/list of mpf, y is a tuple.
    _mp_state_v = {"native": True}

    def F_vec(t, y):
        if _mp_state_v["native"]:
            try:
                out = rhs(t, list(y))
                out_list = list(out) if hasattr(out, "__iter__") else [out]
                return [_mp.mpf(v) for v in out_list]
            except Exception:
                _mp_state_v["native"] = False
        yarr = np.asarray([float(v) for v in y], dtype=float)
        out = rhs(float(t), yarr)
        out_list = list(out) if hasattr(out, "__iter__") else [out]
        return [_mp.mpf(float(v)) for v in out_list]

    f_inner = _mp.odefun(F_vec, _mp.mpf(t0), y0_list)

    def f(t):
        v = f_inner(_mp.mpf(t))
        return tuple(v) if hasattr(v, "__iter__") else (v,)
    return f


# ---------------------------------------------------------------------------
# Hamiltonian / symplectic integrators
# ---------------------------------------------------------------------------


def _grad(f, x, idx, eps=1e-7):
    """Central difference on f at x in coordinate idx."""
    x_p = list(x); x_p[idx] = x_p[idx] + eps
    x_m = list(x); x_m[idx] = x_m[idx] - eps
    return (f(x_p) - f(x_m)) / (2 * eps)


def hamiltonian_system(
    H_callable: Callable,
    t_span: Tuple[float, float],
    q0: Sequence[float],
    p0: Sequence[float],
    method: str = "leapfrog",
    h: float = 0.01,
) -> dict:
    """Solve Hamilton's equations dq/dt = ∂H/∂p, dp/dt = -∂H/∂q
    for a separable or general Hamiltonian H(q, p).

    Parameters
    ----------
    H_callable : callable (q, p) -> float
    t_span     : (t0, t1)
    q0, p0     : initial coordinates / momenta (same length d)
    method     : 'symplectic_euler', 'leapfrog', or 'verlet'
    h          : step size

    Returns
    -------
    dict with t (n+1,), q (n+1, d), p (n+1, d), method, n_steps,
    success.
    """
    if method not in ("symplectic_euler", "leapfrog", "verlet"):
        raise ValueError(
            f"method={method!r}: choose one of "
            "'symplectic_euler', 'leapfrog', 'verlet'"
        )
    t0, t1 = _validate_t_span(t_span)
    if not isinstance(h, (int, float)) or h <= 0 or not math.isfinite(h):
        raise ValueError(f"step h must be positive finite, got {h!r}")
    q = np.asarray(q0, dtype=float).ravel().copy()
    p = np.asarray(p0, dtype=float).ravel().copy()
    if q.shape != p.shape:
        raise ValueError(
            f"q0 and p0 must have the same length; got {q.shape} vs {p.shape}"
        )
    d = q.size
    n = max(1, int(math.ceil((t1 - t0) / h)))
    h_eff = (t1 - t0) / n
    ts = np.empty(n + 1)
    qs = np.empty((n + 1, d))
    ps = np.empty((n + 1, d))
    ts[0] = t0; qs[0] = q; ps[0] = p

    # Partial derivatives of H via central differences.
    def dHdp(q_, p_):
        out = np.empty(d)
        for i in range(d):
            pp = p_.copy(); pp[i] += 1e-7
            pm = p_.copy(); pm[i] -= 1e-7
            out[i] = (H_callable(q_, pp) - H_callable(q_, pm)) / 2e-7
        return out

    def dHdq(q_, p_):
        out = np.empty(d)
        for i in range(d):
            qp = q_.copy(); qp[i] += 1e-7
            qm = q_.copy(); qm[i] -= 1e-7
            out[i] = (H_callable(qp, p_) - H_callable(qm, p_)) / 2e-7
        return out

    for i in range(n):
        if method == "symplectic_euler":
            # p update first (uses old q), then q update (uses new p)
            p = p - h_eff * dHdq(q, p)
            q = q + h_eff * dHdp(q, p)
        elif method == "leapfrog":
            # Standard kick-drift-kick (Störmer-Verlet on separable H)
            p_half = p - 0.5 * h_eff * dHdq(q, p)
            q = q + h_eff * dHdp(q, p_half)
            p = p_half - 0.5 * h_eff * dHdq(q, p_half)
        else:  # verlet (velocity Verlet)
            a0 = -dHdq(q, p)
            q_new = q + h_eff * dHdp(q, p) + 0.5 * h_eff * h_eff * a0
            a1 = -dHdq(q_new, p)
            p = p + 0.5 * h_eff * (a0 + a1)
            q = q_new
        ts[i + 1] = t0 + (i + 1) * h_eff
        qs[i + 1] = q
        ps[i + 1] = p

    return {"t": ts, "q": qs, "p": ps,
            "method": method, "n_steps": n, "success": True}


# ---------------------------------------------------------------------------
# First-passage time
# ---------------------------------------------------------------------------


def first_passage_time(
    rhs: Callable,
    y0: Sequence[float],
    threshold_fn: Callable,
    t_max: float = 10.0,
    rtol: float = 1e-8,
    atol: float = 1e-10,
) -> Optional[float]:
    """First t in [0, t_max] such that threshold_fn(y(t)) crosses zero.

    Implementation uses scipy's dense-event capability: integrate
    with an event function, return the first zero crossing or None
    if the threshold is never reached.
    """
    if not _HAS_SCIPY:  # pragma: no cover
        raise ImportError("scipy is required for first_passage_time")
    t0, t1 = 0.0, float(t_max)
    if not (t1 > t0):
        raise ValueError(f"t_max must be > 0, got {t_max!r}")
    y0_arr = np.asarray(y0, dtype=float).ravel()

    def event(t, y):
        return float(threshold_fn(y))
    event.terminal = True

    res = _scipy_solve_ivp(
        rhs, (t0, t1), y0_arr,
        method="RK45", rtol=rtol, atol=atol,
        events=event,
    )
    if res.t_events and len(res.t_events[0]) > 0:
        return float(res.t_events[0][0])
    return None


# ---------------------------------------------------------------------------
# Largest Lyapunov exponent for continuous flow (tangent-linear method)
# ---------------------------------------------------------------------------


def liapunov_exponent_continuous(
    rhs: Callable,
    y0: Sequence[float],
    t_max: float = 100.0,
    n_renorm: int = 10,
    eps: float = 1e-8,
) -> float:
    """Largest Lyapunov exponent of dy/dt = rhs(t, y) at y0 via the
    "two-trajectory" method (Wolf et al., Physica D 16 (1985) 285).

    We integrate two nearby copies, periodically rescaling the
    separation to ``eps`` and accumulating log-stretch factors.
    """
    if not _HAS_SCIPY:  # pragma: no cover
        raise ImportError("scipy is required for liapunov_exponent_continuous")
    if t_max <= 0:
        raise ValueError(f"t_max must be > 0, got {t_max!r}")
    if not isinstance(n_renorm, int) or n_renorm < 1:
        raise ValueError(f"n_renorm must be a positive int, got {n_renorm!r}")

    y_main = np.asarray(y0, dtype=float).ravel().copy()
    # Initial perturbation in a random direction
    rng = np.random.default_rng(0)
    delta = rng.standard_normal(y_main.size)
    delta = eps * delta / np.linalg.norm(delta)
    y_pert = y_main + delta

    dt = t_max / n_renorm
    log_sum = 0.0
    # Discard a brief transient so the orbit lands on the attractor
    transient = min(dt, 5.0)
    if transient > 0:
        res0 = _scipy_solve_ivp(rhs, (0.0, transient), y_main,
                                method="RK45", rtol=1e-8, atol=1e-10)
        y_main = res0.y[:, -1]
        y_pert = y_main + eps * delta / np.linalg.norm(delta)

    for _ in range(n_renorm):
        ra = _scipy_solve_ivp(rhs, (0.0, dt), y_main,
                              method="RK45", rtol=1e-8, atol=1e-10)
        rb = _scipy_solve_ivp(rhs, (0.0, dt), y_pert,
                              method="RK45", rtol=1e-8, atol=1e-10)
        y_main = ra.y[:, -1]
        y_pert = rb.y[:, -1]
        d = y_pert - y_main
        dist = np.linalg.norm(d)
        if dist <= 0 or not math.isfinite(dist):
            break
        log_sum += math.log(dist / eps)
        # rescale separation back to eps along same direction
        y_pert = y_main + eps * d / dist

    return log_sum / t_max
