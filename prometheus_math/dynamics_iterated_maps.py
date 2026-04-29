"""prometheus_math.dynamics_iterated_maps — classical iterated maps.

Project #76 from techne/PROJECT_BACKLOG_1000.md (Tier 2).

This module provides the canonical 1-D and 2-D iterated maps that
underpin a large fraction of low-dimensional dynamical-systems
research (see Strogatz, "Nonlinear Dynamics and Chaos", chs. 10-12,
or Devaney, "An Introduction to Chaotic Dynamical Systems").

Public API:

  Maps (raw orbits):
    - logistic_map(r, x_init, n_iter, transient=0)
    - tent_map(x_init, n_iter, transient=0)
    - sine_map(r, x_init, n_iter, transient=0)
    - henon_map(a, b, x0_init, y0_init, n_iter, transient=0)

  Diagnostics:
    - lyapunov_exponent(map_fn, x_init, params, n_iter, transient)
    - bifurcation_diagram(map_fn, param_range, n_params, x_init,
                          n_iter, transient)
    - find_periodic_orbits(map_fn, params, period, x_range, tol)
    - feigenbaum_constant_estimate(map_fn, params_range)

References:

- Devaney, R.L., "An Introduction to Chaotic Dynamical Systems"
  (2nd ed., 1989).  Logistic / tent maps, conjugacy.
- Strogatz, S.H., "Nonlinear Dynamics and Chaos" (2nd ed., 2014).
  Bifurcation diagrams, Feigenbaum's δ, Hénon attractor.
- Hénon, M., "A two-dimensional mapping with a strange attractor",
  Comm. Math. Phys. 50 (1976) 69-77.
- Feigenbaum, M.J., "Quantitative universality for a class of
  nonlinear transformations", J. Stat. Phys. 19 (1978) 25-52.
"""

from __future__ import annotations

from typing import Callable, Mapping, Optional, Sequence, Tuple

import math

import numpy as np


__all__ = [
    "logistic_map",
    "tent_map",
    "sine_map",
    "henon_map",
    "lyapunov_exponent",
    "bifurcation_diagram",
    "find_periodic_orbits",
    "feigenbaum_constant_estimate",
    "logistic_step",
    "tent_step",
    "sine_step",
    "logistic_derivative",
    "tent_derivative",
    "sine_derivative",
]


# ---------------------------------------------------------------------------
# Single-step functions and analytic derivatives.  Useful for chaining
# (e.g. find_periodic_orbits applies these k times).
# ---------------------------------------------------------------------------


def logistic_step(x: float, r: float) -> float:
    """f(x) = r x (1 - x).  Maps [0,1] -> [0,1] when r in [0,4]."""
    return r * x * (1.0 - x)


def logistic_derivative(x: float, r: float) -> float:
    """f'(x) = r (1 - 2x)."""
    return r * (1.0 - 2.0 * x)


def tent_step(x: float, _params=None) -> float:
    """Symmetric tent map on [0,1].

    f(x) = 2x          if x < 0.5
         = 2(1 - x)    otherwise.
    """
    return 2.0 * x if x < 0.5 else 2.0 * (1.0 - x)


def tent_derivative(x: float, _params=None) -> float:
    """f'(x) = +2 on (0, 0.5), -2 on (0.5, 1).  At x=0.5 we return +2
    by convention (Lebesgue-measure zero set)."""
    return 2.0 if x < 0.5 else -2.0


def sine_step(x: float, r: float) -> float:
    """f(x) = r sin(pi x).  Conjugate to logistic on [0, 1]."""
    return r * math.sin(math.pi * x)


def sine_derivative(x: float, r: float) -> float:
    """f'(x) = r pi cos(pi x)."""
    return r * math.pi * math.cos(math.pi * x)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _check_n_iter(n_iter: int, transient: int) -> None:
    if n_iter < 0:
        raise ValueError(f"n_iter must be >= 0, got {n_iter}")
    if transient < 0:
        raise ValueError(f"transient must be >= 0, got {transient}")


def _check_unit_interval(name: str, x: float) -> None:
    if not (0.0 <= x <= 1.0):
        raise ValueError(
            f"{name} must lie in [0, 1] for this map; got {x}"
        )


# ---------------------------------------------------------------------------
# Logistic map
# ---------------------------------------------------------------------------


def logistic_map(
    r: float,
    x_init: float,
    n_iter: int,
    transient: int = 0,
) -> np.ndarray:
    """Iterate the logistic map x_{n+1} = r x_n (1 - x_n).

    Parameters
    ----------
    r : float
        Bifurcation parameter in [0, 4]. Outside this range, orbits
        starting in [0, 1] generally escape to infinity; ValueError.
    x_init : float
        Initial condition in [0, 1].
    n_iter : int
        Number of points to return after the transient.
    transient : int
        Number of leading iterations to drop.

    Returns
    -------
    np.ndarray of shape (n_iter,)
        The orbit x_{transient}, x_{transient+1}, ..., x_{transient+n_iter-1}.

    Notes
    -----
    For n_iter == 0, returns an empty array (no iteration is done,
    not even the transient).  This is the documented edge case.
    """
    _check_n_iter(n_iter, transient)
    if not (0.0 <= r <= 4.0):
        raise ValueError(
            f"logistic_map requires r in [0, 4]; got r={r}. "
            "Outside this range, orbits in [0,1] generally escape."
        )
    _check_unit_interval("x_init", x_init)
    if n_iter == 0:
        return np.empty(0, dtype=float)

    x = float(x_init)
    for _ in range(transient):
        x = r * x * (1.0 - x)

    out = np.empty(n_iter, dtype=float)
    for i in range(n_iter):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


# ---------------------------------------------------------------------------
# Tent map
# ---------------------------------------------------------------------------


def tent_map(
    x_init: float,
    n_iter: int,
    transient: int = 0,
) -> np.ndarray:
    """Iterate the symmetric tent map.

    f(x) = 2x          for x in [0, 0.5)
         = 2(1 - x)    for x in [0.5, 1].

    Parameters
    ----------
    x_init : float
        Initial condition in [0, 1].
    n_iter, transient : int
        Same conventions as ``logistic_map``.
    """
    _check_n_iter(n_iter, transient)
    _check_unit_interval("x_init", x_init)
    if n_iter == 0:
        return np.empty(0, dtype=float)

    x = float(x_init)
    for _ in range(transient):
        x = 2.0 * x if x < 0.5 else 2.0 * (1.0 - x)

    out = np.empty(n_iter, dtype=float)
    for i in range(n_iter):
        x = 2.0 * x if x < 0.5 else 2.0 * (1.0 - x)
        out[i] = x
    return out


# ---------------------------------------------------------------------------
# Sine map
# ---------------------------------------------------------------------------


def sine_map(
    r: float,
    x_init: float,
    n_iter: int,
    transient: int = 0,
) -> np.ndarray:
    """Iterate the sine map x_{n+1} = r sin(pi x_n).

    For r in [0, 1], the unit interval is invariant.  Outside [0, 1]
    we still allow the call (orbits may visit a wider range), but
    we restrict r to [0, 1] for conjugacy with the logistic map.
    """
    _check_n_iter(n_iter, transient)
    if not (0.0 <= r <= 1.0):
        raise ValueError(
            f"sine_map requires r in [0, 1]; got r={r}."
        )
    _check_unit_interval("x_init", x_init)
    if n_iter == 0:
        return np.empty(0, dtype=float)

    x = float(x_init)
    for _ in range(transient):
        x = r * math.sin(math.pi * x)

    out = np.empty(n_iter, dtype=float)
    for i in range(n_iter):
        x = r * math.sin(math.pi * x)
        out[i] = x
    return out


# ---------------------------------------------------------------------------
# Hénon map (2-D)
# ---------------------------------------------------------------------------


def henon_map(
    a: float,
    b: float,
    x0_init: float,
    y0_init: float,
    n_iter: int,
    transient: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Iterate the 2-D Hénon map.

    x_{n+1} = 1 - a x_n^2 + y_n
    y_{n+1} = b x_n

    Classical chaotic parameters: (a, b) = (1.4, 0.3).

    Returns
    -------
    (xs, ys) : tuple of np.ndarray, each of shape (n_iter,)
    """
    _check_n_iter(n_iter, transient)
    if n_iter == 0:
        return np.empty(0, dtype=float), np.empty(0, dtype=float)

    x = float(x0_init)
    y = float(y0_init)
    for _ in range(transient):
        x_new = 1.0 - a * x * x + y
        y = b * x
        x = x_new

    xs = np.empty(n_iter, dtype=float)
    ys = np.empty(n_iter, dtype=float)
    for i in range(n_iter):
        x_new = 1.0 - a * x * x + y
        y = b * x
        x = x_new
        xs[i] = x
        ys[i] = y
    return xs, ys


# ---------------------------------------------------------------------------
# Lyapunov exponent (1-D)
# ---------------------------------------------------------------------------


# Mapping from the public map_fn callable to its analytic derivative.
# Users can pass either the canonical map_fn (logistic_map, tent_map,
# sine_map) or any 1-D callable f(x, params) -> x' together with a
# derivative (we infer for the canonical maps).
_DERIVATIVE_REGISTRY = {
    "logistic_map": logistic_derivative,
    "tent_map": tent_derivative,
    "sine_map": sine_derivative,
}


def lyapunov_exponent(
    map_fn: Callable,
    x_init: float,
    params: Optional[Mapping] = None,
    n_iter: int = 10000,
    transient: int = 1000,
) -> float:
    """Compute the maximum Lyapunov exponent of a 1-D map.

    λ = (1/N) Σ_{i=0}^{N-1} log |f'(x_i)|

    where x_i is the orbit from x_init under f, after dropping a
    transient.  Positive λ → chaos; λ <= 0 → regular orbit.

    Parameters
    ----------
    map_fn : callable
        Either one of the canonical maps in this module
        (``logistic_map``, ``tent_map``, ``sine_map``), or any
        callable matching ``logistic_map(r, x_init, n_iter, transient)``
        signature.  We use ``map_fn.__name__`` to dispatch to the
        analytic derivative.
    x_init : float
        Initial condition.
    params : Mapping or None
        Map parameters.  For the logistic / sine maps, must contain
        the key ``"r"``.  Tent map ignores params.
    n_iter : int
        Number of iterations to average over.
    transient : int
        Burn-in iterations to drop before averaging.

    Returns
    -------
    float
        Estimated Lyapunov exponent.  If the orbit visits a critical
        point (where |f'(x)| = 0) we return ``-inf``.
    """
    if n_iter <= 0:
        raise ValueError(f"n_iter must be > 0, got {n_iter}")
    if transient < 0:
        raise ValueError(f"transient must be >= 0, got {transient}")

    name = getattr(map_fn, "__name__", None)
    if name not in _DERIVATIVE_REGISTRY:
        raise ValueError(
            f"lyapunov_exponent supports the canonical 1-D maps "
            f"({list(_DERIVATIVE_REGISTRY)}); got {name}."
        )
    deriv = _DERIVATIVE_REGISTRY[name]

    if name == "tent_map":
        r_param = None
        step = lambda x: tent_step(x)  # noqa: E731
        d_step = lambda x: tent_derivative(x)  # noqa: E731
    else:
        if params is None or "r" not in params:
            raise ValueError(
                f"{name} requires params={{'r': ...}} for Lyapunov."
            )
        r_param = float(params["r"])
        if name == "logistic_map":
            step = lambda x: logistic_step(x, r_param)  # noqa: E731
            d_step = lambda x: logistic_derivative(x, r_param)  # noqa: E731
        else:  # sine_map
            step = lambda x: sine_step(x, r_param)  # noqa: E731
            d_step = lambda x: sine_derivative(x, r_param)  # noqa: E731

    x = float(x_init)
    for _ in range(transient):
        x = step(x)

    log_sum = 0.0
    for _ in range(n_iter):
        d = d_step(x)
        if d == 0.0:
            return float("-inf")
        log_sum += math.log(abs(d))
        x = step(x)

    return log_sum / n_iter


# ---------------------------------------------------------------------------
# Bifurcation diagram
# ---------------------------------------------------------------------------


def bifurcation_diagram(
    map_fn: Callable,
    param_range: Tuple[float, float],
    n_params: int,
    x_init: float,
    n_iter: int,
    transient: int = 1000,
) -> Tuple[np.ndarray, np.ndarray]:
    """Build a bifurcation diagram for a canonical 1-D map.

    For each of ``n_params`` evenly-spaced parameter values in
    ``param_range``, iterate the map after dropping ``transient``
    points and collect the next ``n_iter`` orbit points.

    Parameters
    ----------
    map_fn : callable
        ``logistic_map`` or ``sine_map``.  Tent map has no parameter
        and is not supported by this routine (its diagram is
        a horizontal band).
    param_range : (lo, hi)
    n_params : int
        Number of parameter samples.
    x_init : float
    n_iter : int
        Orbit points retained per parameter value.
    transient : int

    Returns
    -------
    params, xs : np.ndarray, np.ndarray
        Both of length ``n_params * n_iter``.  ``params[i]`` is the
        parameter at which orbit point ``xs[i]`` was sampled.
    """
    if n_params <= 0:
        raise ValueError(f"n_params must be > 0, got {n_params}")
    if n_iter <= 0:
        raise ValueError(f"n_iter must be > 0, got {n_iter}")
    if transient < 0:
        raise ValueError(f"transient must be >= 0, got {transient}")
    lo, hi = float(param_range[0]), float(param_range[1])
    if hi <= lo:
        raise ValueError(
            f"param_range must satisfy hi > lo; got ({lo}, {hi})."
        )

    name = getattr(map_fn, "__name__", None)
    if name not in ("logistic_map", "sine_map"):
        raise ValueError(
            "bifurcation_diagram supports logistic_map and sine_map."
        )

    grid = np.linspace(lo, hi, n_params)
    params_out = np.empty(n_params * n_iter, dtype=float)
    xs_out = np.empty(n_params * n_iter, dtype=float)

    for k, r in enumerate(grid):
        # logistic_map / sine_map both validate r-range; reuse them.
        orbit = map_fn(float(r), x_init, n_iter, transient=transient)
        slc = slice(k * n_iter, (k + 1) * n_iter)
        params_out[slc] = r
        xs_out[slc] = orbit

    return params_out, xs_out


# ---------------------------------------------------------------------------
# Periodic-orbit finder (1-D)
# ---------------------------------------------------------------------------


def _iterate_step(step: Callable[[float], float], x: float, k: int) -> float:
    """Apply ``step`` ``k`` times."""
    for _ in range(k):
        x = step(x)
    return x


def find_periodic_orbits(
    map_fn: Callable,
    params: Optional[Mapping],
    period: int,
    x_range: Tuple[float, float] = (0.0, 1.0),
    tol: float = 1e-6,
    n_grid: int = 2000,
) -> list:
    """Find period-``period`` orbits of a 1-D map by bracketed bisection
    on g(x) = f^period(x) - x.

    Returns a sorted list of unique fixed points of f^period that lie
    in ``x_range``.  Includes period-divisor orbits (e.g. period-1
    fixed points are also fixed points of f^2).

    Parameters
    ----------
    map_fn : callable
        ``logistic_map``, ``tent_map``, or ``sine_map``.
    params : Mapping or None
        ``{'r': ...}`` for logistic/sine; ignored for tent.
    period : int
        Search for fixed points of f^period (>= 1).
    x_range : (lo, hi)
        Initial-condition bracket.
    tol : float
        Absolute tolerance on g(x) and on collapse of duplicates.
    n_grid : int
        Number of subintervals for bracketing.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    lo, hi = float(x_range[0]), float(x_range[1])
    if hi <= lo:
        raise ValueError(
            f"x_range must satisfy hi > lo; got ({lo}, {hi})."
        )

    name = getattr(map_fn, "__name__", None)
    if name == "logistic_map":
        if params is None or "r" not in params:
            raise ValueError("logistic_map needs params={'r': ...}.")
        r = float(params["r"])
        step = lambda x: logistic_step(x, r)  # noqa: E731
    elif name == "sine_map":
        if params is None or "r" not in params:
            raise ValueError("sine_map needs params={'r': ...}.")
        r = float(params["r"])
        step = lambda x: sine_step(x, r)  # noqa: E731
    elif name == "tent_map":
        step = lambda x: tent_step(x)  # noqa: E731
    else:
        raise ValueError(
            "find_periodic_orbits supports the 1-D canonical maps."
        )

    def g(x: float) -> float:
        return _iterate_step(step, x, period) - x

    grid = np.linspace(lo, hi, n_grid + 1)
    g_vals = np.array([g(float(x)) for x in grid])

    roots: list = []
    for i in range(n_grid):
        a, b = float(grid[i]), float(grid[i + 1])
        ga, gb = float(g_vals[i]), float(g_vals[i + 1])
        if abs(ga) < tol:
            roots.append(a)
            continue
        if ga * gb < 0.0:
            # Bisection
            for _ in range(80):
                mid = 0.5 * (a + b)
                gm = g(mid)
                if abs(gm) < tol or (b - a) < tol:
                    a = b = mid
                    break
                if ga * gm < 0.0:
                    b = gm if False else b  # keep b
                    b = mid
                    gb = gm
                else:
                    a = mid
                    ga = gm
            roots.append(0.5 * (a + b))
    # last endpoint
    if abs(float(g_vals[-1])) < tol:
        roots.append(float(grid[-1]))

    # Deduplicate and sort
    if not roots:
        return []
    roots.sort()
    deduped = [roots[0]]
    for r_ in roots[1:]:
        if abs(r_ - deduped[-1]) > 10.0 * tol:
            deduped.append(r_)
    return deduped


# ---------------------------------------------------------------------------
# Feigenbaum δ estimator
# ---------------------------------------------------------------------------


def feigenbaum_constant_estimate(
    map_fn: Callable = logistic_map,
    params_range: Tuple[float, float] = (1.5, 3.5699),
    max_period: int = 32,
    grid: int = 400_000,
) -> float:
    """Estimate Feigenbaum's δ ≈ 4.66920... via the period-doubling
    cascade of the canonical 1-D map.

    Strategy: locate the parameter values R_n at which the period-2^n
    orbit becomes superstable (the orbit passes through the critical
    point x* = 0.5 for logistic / sine).  These are the roots of
    ``f^{2^n}(0.5; r) = 0.5`` that are *new* at period 2^n (not
    inherited from a lower-period superstable point).  Then

        δ_n = (R_{n-1} - R_{n-2}) / (R_n - R_{n-1})  →  δ.

    Returns the last available finite ratio δ_n; raises ValueError
    if too few values are found.
    """
    name = getattr(map_fn, "__name__", None)
    if name not in ("logistic_map", "sine_map"):
        raise ValueError(
            "feigenbaum_constant_estimate supports logistic_map / sine_map."
        )

    lo, hi = float(params_range[0]), float(params_range[1])
    rs = np.linspace(lo, hi, grid)
    x_star = 0.5
    superstable_rs: list = []

    period = 1
    consecutive_misses = 0
    while period <= max_period:
        # Vectorized scan over r: build f^period(x_star; r) - x_star.
        x = np.full_like(rs, x_star)
        if name == "logistic_map":
            for _ in range(period):
                x = rs * x * (1.0 - x)
        else:  # sine
            for _ in range(period):
                x = rs * np.sin(np.pi * x)
        diff = x - x_star
        sign = np.sign(diff)
        idx = np.where(np.diff(sign) != 0)[0]

        # We want the *new* root: the first root strictly greater than
        # the previous superstable r (with margin to skip duplicate
        # detections of a sign change clustered around an inherited
        # root).
        threshold = (
            superstable_rs[-1] + 1e-4 if superstable_rs else lo - 1.0
        )
        chosen = None
        for i in idx:
            r_l, r_r = float(rs[i]), float(rs[i + 1])
            d_l, d_r = float(diff[i]), float(diff[i + 1])
            if d_l == d_r:
                r_root = 0.5 * (r_l + r_r)
            else:
                r_root = r_l - d_l * (r_r - r_l) / (d_r - d_l)
            if r_root > threshold:
                chosen = r_root
                break
        if chosen is None:
            # No superstable r in range for this period.  Two cases:
            #  (a) we haven't entered the cascade yet (small period,
            #      lo > superstable_period_n) → keep searching higher
            #      periods.
            #  (b) we've exhausted the cascade (numerical resolution) →
            #      bail out after a couple of empty rounds.
            consecutive_misses += 1
            if consecutive_misses > 2:
                break
        else:
            superstable_rs.append(chosen)
            consecutive_misses = 0
        period *= 2

    if len(superstable_rs) < 3:
        raise ValueError(
            "Feigenbaum estimator needs >= 3 superstable points; got "
            f"{len(superstable_rs)}.  Increase grid or widen params_range."
        )

    # Form successive ratios; return the last one (best estimate).
    deltas = []
    for k in range(2, len(superstable_rs)):
        num = superstable_rs[k - 1] - superstable_rs[k - 2]
        den = superstable_rs[k] - superstable_rs[k - 1]
        if den == 0:
            continue
        deltas.append(num / den)
    if not deltas:
        raise ValueError("Could not form a finite Feigenbaum ratio.")
    return float(deltas[-1])
