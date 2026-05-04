"""prometheus_math.cost_model_profiler — empirical cost calibration.

Profiles arsenal ops at multiple input sizes, fits a complexity curve to
the wall-time-vs-size data, and emits a structured cost model that can
be written back into ``prometheus_math._metadata_table`` as a
``calibrated_cost`` field. The existing ``cost`` dict is left intact so
no downstream consumer breaks.

Hardware on which the canonical 2026-05-04 calibration was run:

- Host: Skullport (M1)
- CPU: AMD Ryzen 7 5700X3D (AMD64 Family 25 Model 97 Stepping 2)
- OS: Windows 11 (Windows-10-10.0.26200-SP0)
- Python: 3.11.9 (CPython, MSVC 1938 / x64)
- mpmath default dps = 15
- Wall-time clock: ``time.perf_counter`` (best available monotonic)

Cost models are *one-machine snapshots*. They drift with:

- mpmath / FLINT / scipy / cypari minor-version bumps
- CPU thermal state (laptop vs desktop, sustained vs burst)
- Concurrent load on the host
- ``OMP_NUM_THREADS`` / ``MKL_NUM_THREADS`` / ``CYPARI_PARI_THREADS``

Recalibration cadence: monthly, OR on perceived drift in production
(when the substrate's cost-aware scheduler rejects too many BIND/EVAL
candidates because their declared budgets blow out).

Standalone usage::

    python -m prometheus_math.cost_model_profiler --top-50 \\
        --output prometheus_math/cost_calibration_2026_05_04.json
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import platform
import statistics
import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Sizing strategies — map a callable_ref + base args to a sequence of
# (size_label, args_tuple, kwargs) probes covering at least 3 sizes.
# ---------------------------------------------------------------------------

# Each entry maps callable_ref -> (size_param_name, [list of arg-builders]).
# The arg-builder returns ([positional], {kwargs}) for a given size hint.
ProbeBuilder = Callable[[int], Tuple[List[Any], Dict[str, Any]]]

# Default size grid: small / medium / large.
DEFAULT_SIZES: Tuple[int, ...] = (4, 8, 16)

# Per-op sizing recipes. Keys are callable_refs; values are (sizes, builder).
PROBES: Dict[str, Tuple[Sequence[int], ProbeBuilder]] = {}


def _register_probe(ref: str, sizes: Sequence[int], builder: ProbeBuilder) -> None:
    PROBES[ref] = (tuple(sizes), builder)


# --- numerics_special — mostly cheap mpmath wrappers; size = dps. --------

def _dilog_probe(size: int):
    # size is irrelevant for scalar dilog beyond mpmath's internal series;
    # vary the argument's distance from singularity instead.
    z = 1.0 - 1.0 / size if size > 1 else 0.5
    return [z], {}


_register_probe(
    "prometheus_math.numerics_special_dilogarithm:dilogarithm",
    (4, 16, 64),
    _dilog_probe,
)
_register_probe(
    "prometheus_math.numerics_special_dilogarithm:polylogarithm",
    (2, 5, 10),
    lambda n: ([n, 0.5], {}),
)
_register_probe(
    "prometheus_math.numerics_special_dilogarithm:bloch_wigner_dilog",
    (1, 2, 4),
    lambda n: ([0.5 + 0.1 * n * 1j], {}),
)
_register_probe(
    "prometheus_math.numerics_special_dilogarithm:clausen",
    (1, 2, 4),
    lambda n: ([0.5 * n], {}),
)
_register_probe(
    "prometheus_math.numerics_special_hurwitz:hurwitz_zeta",
    (2, 4, 8),
    lambda n: ([float(n), 1.0], {}),
)
_register_probe(
    "prometheus_math.numerics_special_hurwitz:polygamma",
    (0, 2, 4),
    lambda n: ([n, 1.5], {}),
)
_register_probe(
    "prometheus_math.numerics_special_theta:theta_null_value",
    (1, 2, 3),
    lambda n: ([3, 0.1 * n + 0.1], {}),
)
_register_probe(
    "prometheus_math.numerics_special_theta:jacobi_theta",
    (1, 2, 3),
    lambda n: ([3, 0.0, 0.1 * n + 0.1], {}),
)
_register_probe(
    "prometheus_math.numerics_special_eta:eta",
    (1, 2, 4),
    lambda n: ([1.0j * n], {}),
)
_register_probe(
    "prometheus_math.numerics_special_eta:j_invariant",
    (1, 2, 4),
    lambda n: ([1.0j * n], {}),
)
_register_probe(
    "prometheus_math.numerics_special_eta:eta_quotient",
    (1, 2, 4),
    lambda n: ([{1: 2, 2: -2}, 1.0j * n], {}),
)
_register_probe(
    "prometheus_math.numerics_special_q_pochhammer:euler_function",
    (1, 2, 4),
    lambda n: ([0.1 * n + 0.1], {}),
)
_register_probe(
    "prometheus_math.numerics_special_q_pochhammer:dedekind_eta",
    (1, 2, 4),
    lambda n: ([1.0j * n], {}),
)
_register_probe(
    "prometheus_math.numerics_special_q_pochhammer:q_pochhammer",
    (1, 2, 4),
    lambda n: ([0.5, 0.1 * n + 0.1], {}),
)


# --- combinatorics — partition / Young tableaux. -------------------------

_register_probe(
    "prometheus_math.combinatorics_partitions:num_partitions",
    (10, 30, 80),
    lambda n: ([n], {}),
)
_register_probe(
    "prometheus_math.combinatorics_partitions:partitions_of",
    (5, 8, 12),
    lambda n: ([n], {}),
)
_register_probe(
    "prometheus_math.combinatorics_partitions:conjugate",
    (5, 10, 20),
    lambda n: ([list(range(n, 0, -1))], {}),
)
_register_probe(
    "prometheus_math.combinatorics_partitions:num_standard_young_tableaux",
    (3, 5, 8),
    lambda n: ([list(range(n, 0, -1))], {}),
)
_register_probe(
    "prometheus_math.combinatorics_partitions:rsk",
    (4, 8, 16),
    lambda n: ([list(range(n))], {}),
)
_register_probe(
    "prometheus_math.combinatorics_partitions:hook_length_array",
    (5, 10, 20),
    lambda n: ([list(range(n, 0, -1))], {}),
)


# --- numerics — flint / mpmath / bernoulli / zeta. -----------------------

_register_probe(
    "prometheus_math.numerics:flint_factor",
    (4, 8, 16),
    lambda n: ([[1] + [0] * (n - 1) + [-1]], {}),
)
_register_probe(
    "prometheus_math.numerics:flint_polmodp",
    (4, 8, 16),
    lambda n: ([list(range(1, n + 1)), 7], {}),
)
_register_probe(
    "prometheus_math.numerics:flint_matmul_modp",
    (4, 8, 16),
    lambda n: (
        [[[1] * n for _ in range(n)], [[1] * n for _ in range(n)], 7],
        {},
    ),
)
_register_probe(
    "prometheus_math.numerics:mpdft",
    (4, 8, 16),
    lambda n: ([[1.0 if i % 2 == 0 else 0.0 for i in range(n)]], {}),
)
_register_probe(
    "prometheus_math.numerics:mpfft",
    (4, 8, 16),
    lambda n: ([[1.0 if i % 2 == 0 else 0.0 for i in range(n)]], {}),
)
_register_probe(
    "prometheus_math.numerics:bernoulli",
    (4, 10, 20),
    lambda n: ([n], {}),
)
_register_probe(
    "prometheus_math.numerics:zeta",
    (2, 4, 8),
    lambda n: ([float(n)], {}),
)


# --- geometry — convex hull / voronoi / delaunay. ------------------------

def _points2d(n: int) -> List[Tuple[float, float]]:
    pts = []
    for i in range(n):
        # deterministic "random" points
        x = ((i * 2654435761) % 10000) / 10000.0
        y = ((i * 40503) % 10000) / 10000.0
        pts.append((x, y))
    return pts


_register_probe(
    "prometheus_math.geometry_convex_hull:convex_hull",
    (8, 32, 128),
    lambda n: ([_points2d(n)], {}),
)
_register_probe(
    "prometheus_math.geometry_voronoi:voronoi_diagram",
    (8, 32, 128),
    lambda n: ([_points2d(n)], {}),
)
_register_probe(
    "prometheus_math.geometry_delaunay:delaunay_triangulation",
    (8, 32, 128),
    lambda n: ([_points2d(n)], {}),
)
def _simplex_pts(d: int) -> List[Tuple[float, ...]]:
    # Build a d-simplex (d+1 affinely-independent points in d-space).
    pts = [tuple(0.0 for _ in range(d))]
    for i in range(d):
        v = [0.0] * d
        v[i] = 1.0 + 0.01 * i  # break degeneracies
        pts.append(tuple(v))
    return pts


_register_probe(
    "prometheus_math.geometry_delaunay:circumcenter",
    (2, 3, 4),
    lambda n: ([_simplex_pts(n)], {}),
)


# --- dynamics — iterated maps. -------------------------------------------

_register_probe(
    "prometheus_math.dynamics_iterated_maps:logistic_map",
    (50, 200, 800),
    lambda n: ([3.7, 0.5], {"n_iter": n, "transient": n // 4}),
)
_register_probe(
    "prometheus_math.dynamics_iterated_maps:tent_map",
    (50, 200, 800),
    lambda n: ([0.6], {"n_iter": n, "transient": n // 4}),
)


# --- research_lehmer — Salem / reciprocal / degree-profile. --------------

def _lehmer_poly(n: int) -> List[int]:
    # Reciprocal polynomial of degree n; pads Lehmer's classic to n.
    base = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    if n <= len(base):
        return base[:n + 1] if n + 1 <= len(base) else base
    pad = (n + 1 - len(base)) // 2
    return [1] * pad + base + [1] * (n + 1 - len(base) - pad)


_register_probe(
    "prometheus_math.research.lehmer:identify_salem_class",
    (4, 10, 20),
    lambda n: ([_lehmer_poly(n)], {}),
)
_register_probe(
    "prometheus_math.research.lehmer:is_reciprocal",
    (4, 10, 20),
    lambda n: ([_lehmer_poly(n)], {}),
)


# --- research_lehmer / techne.lib — Mahler / cyclotomic. -----------------

_register_probe(
    "techne.lib.mahler_measure:mahler_measure",
    (10, 20, 40),
    lambda n: ([_lehmer_poly(n)], {}),
)
_register_probe(
    "techne.lib.mahler_measure:log_mahler_measure",
    (10, 20, 40),
    lambda n: ([_lehmer_poly(n)], {}),
)
_register_probe(
    "techne.lib.mahler_measure:is_cyclotomic",
    (4, 8, 16),
    lambda n: ([[1] + [0] * (n - 1) + [-1]], {}),
)


# --- techne.lib — continued fractions, sturm, smith normal form. ---------

_register_probe(
    "techne.lib.cf_expansion:cf_expand",
    (1, 4, 16),
    lambda n: ([22 * n + 7, 7], {}),
)
_register_probe(
    "techne.lib.cf_expansion:cf_max_digit",
    (1, 4, 16),
    lambda n: ([22 * n + 7, 7], {}),
)
_register_probe(
    "techne.lib.cf_expansion:zaremba_test",
    (8, 25, 80),
    lambda n: ([n], {}),
)
_register_probe(
    "techne.lib.cf_expansion:sturm_bound",
    (4, 12, 30),
    lambda n: ([n, 11], {}),
)


def _hnf_matrix(n: int) -> List[List[int]]:
    # Construct a small invertible integer matrix sized n x n.
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        M[i][i] = i + 2
        if i + 1 < n:
            M[i][i + 1] = 1
        if i > 0:
            M[i][i - 1] = -1
    return M


_register_probe(
    "techne.lib.smith_normal_form:smith_normal_form",
    (3, 5, 8),
    lambda n: ([_hnf_matrix(n)], {}),
)
_register_probe(
    "techne.lib.smith_normal_form:invariant_factors",
    (3, 5, 8),
    lambda n: ([_hnf_matrix(n)], {}),
)
_register_probe(
    "techne.lib.smith_normal_form:abelian_group_structure",
    (3, 5, 8),
    lambda n: ([_hnf_matrix(n)], {}),
)


# --- techne.lib — number fields, LLL. ------------------------------------

_register_probe(
    "techne.lib.lll_reduction:lll",
    (3, 5, 8),
    lambda n: ([_hnf_matrix(n)], {}),
)
_register_probe(
    "techne.lib.lll_reduction:shortest_vector_lll",
    (3, 5, 8),
    lambda n: ([_hnf_matrix(n)], {}),
)


# --- techne.lib — elliptic curves (BSD chain). ---------------------------

# Five canonical curves of varying conductor.
_EC_CURVES: List[List[int]] = [
    [0, -1, 1, -10, -20],   # 11.a1, conductor 11, rank 0
    [0, 0, 1, -1, 0],       # 37.a1, conductor 37, rank 1
    [1, -1, 1, -7820, -263580],  # 5077.a1, rank 3
]


_register_probe(
    "techne.lib.regulator:regulator",
    (0, 1, 2),
    lambda n: ([_EC_CURVES[n]], {}),
)
_register_probe(
    "techne.lib.conductor:conductor",
    (0, 1, 2),
    lambda n: ([_EC_CURVES[n]], {}),
)
_register_probe(
    "techne.lib.conductor:bad_primes",
    (0, 1, 2),
    lambda n: ([_EC_CURVES[n]], {}),
)
_register_probe(
    "techne.lib.root_number:root_number",
    (0, 1, 2),
    lambda n: ([_EC_CURVES[n]], {}),
)
_register_probe(
    "techne.lib.faltings_height:faltings_height",
    (0, 1, 2),
    lambda n: ([_EC_CURVES[n]], {}),
)


# ---------------------------------------------------------------------------
# Top-50 hot-path priority list. The substrate routes BIND/EVAL through
# these in every CLAIM lifecycle (F1-F12 falsifiers, Mahler pilots, BSD
# audits, modular forms, etc.).
# ---------------------------------------------------------------------------

TOP_50_HOT_PATH: List[str] = [
    # F-falsifier-class (Mahler / reciprocity / cyclotomic checks).
    "techne.lib.mahler_measure:mahler_measure",
    "techne.lib.mahler_measure:log_mahler_measure",
    "techne.lib.mahler_measure:is_cyclotomic",
    "prometheus_math.research.lehmer:identify_salem_class",
    "prometheus_math.research.lehmer:is_reciprocal",
    # Number-field core.
    "techne.lib.cf_expansion:cf_expand",
    "techne.lib.cf_expansion:cf_max_digit",
    "techne.lib.cf_expansion:sturm_bound",
    "techne.lib.smith_normal_form:smith_normal_form",
    "techne.lib.smith_normal_form:invariant_factors",
    "techne.lib.smith_normal_form:abelian_group_structure",
    "techne.lib.lll_reduction:lll",
    "techne.lib.lll_reduction:shortest_vector_lll",
    # Numerics — flint + mpmath core.
    "prometheus_math.numerics:flint_factor",
    "prometheus_math.numerics:flint_polmodp",
    "prometheus_math.numerics:flint_matmul_modp",
    "prometheus_math.numerics:mpdft",
    "prometheus_math.numerics:mpfft",
    "prometheus_math.numerics:bernoulli",
    "prometheus_math.numerics:zeta",
    # numerics_special — modular form scaffolding.
    "prometheus_math.numerics_special_dilogarithm:dilogarithm",
    "prometheus_math.numerics_special_dilogarithm:polylogarithm",
    "prometheus_math.numerics_special_dilogarithm:bloch_wigner_dilog",
    "prometheus_math.numerics_special_dilogarithm:clausen",
    "prometheus_math.numerics_special_hurwitz:hurwitz_zeta",
    "prometheus_math.numerics_special_hurwitz:polygamma",
    "prometheus_math.numerics_special_theta:theta_null_value",
    "prometheus_math.numerics_special_theta:jacobi_theta",
    "prometheus_math.numerics_special_eta:eta",
    "prometheus_math.numerics_special_eta:j_invariant",
    "prometheus_math.numerics_special_eta:eta_quotient",
    "prometheus_math.numerics_special_q_pochhammer:euler_function",
    "prometheus_math.numerics_special_q_pochhammer:dedekind_eta",
    "prometheus_math.numerics_special_q_pochhammer:q_pochhammer",
    # Combinatorics.
    "prometheus_math.combinatorics_partitions:num_partitions",
    "prometheus_math.combinatorics_partitions:partitions_of",
    "prometheus_math.combinatorics_partitions:conjugate",
    "prometheus_math.combinatorics_partitions:num_standard_young_tableaux",
    "prometheus_math.combinatorics_partitions:rsk",
    "prometheus_math.combinatorics_partitions:hook_length_array",
    # Geometry.
    "prometheus_math.geometry_convex_hull:convex_hull",
    "prometheus_math.geometry_voronoi:voronoi_diagram",
    "prometheus_math.geometry_delaunay:delaunay_triangulation",
    "prometheus_math.geometry_delaunay:circumcenter",
    # Elliptic-curve BSD audit chain.
    "techne.lib.conductor:conductor",
    "techne.lib.conductor:bad_primes",
    "techne.lib.root_number:root_number",
    "techne.lib.faltings_height:faltings_height",
    # Dynamics.
    "prometheus_math.dynamics_iterated_maps:logistic_map",
    "prometheus_math.dynamics_iterated_maps:tent_map",
]


# ---------------------------------------------------------------------------
# Profiler core.
# ---------------------------------------------------------------------------


@dataclass
class Profile:
    """Result of profiling a single op at multiple sizes."""

    callable_ref: str
    sizes: List[int] = field(default_factory=list)
    times_us: List[float] = field(default_factory=list)  # median wall, microseconds
    n_repeats: int = 0
    fitted_complexity: str = "unknown"
    fitted_coefficient_us: float = 0.0
    fitted_r2: float = 0.0
    declared_max_seconds: float = 0.0
    p95_max_seconds: float = 0.0
    ratio_declared_over_p95: float = 0.0
    in_band: bool = False  # True iff ratio in [2, 50] (the existing test target)
    calibration_failed: bool = False
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "callable_ref": self.callable_ref,
            "sizes": self.sizes,
            "times_us": self.times_us,
            "n_repeats": self.n_repeats,
            "fitted_complexity": self.fitted_complexity,
            "fitted_coefficient_us": self.fitted_coefficient_us,
            "fitted_r2": self.fitted_r2,
            "declared_max_seconds": self.declared_max_seconds,
            "p95_max_seconds": self.p95_max_seconds,
            "ratio_declared_over_p95": self.ratio_declared_over_p95,
            "in_band": self.in_band,
            "calibration_failed": self.calibration_failed,
            "error": self.error,
        }


def _resolve_callable(ref: str) -> Callable:
    """Resolve ``module:qualname`` into a callable (mirrors arsenal_meta)."""
    if ":" not in ref:
        raise ValueError(f"bad ref {ref!r}")
    modpath, qualname = ref.split(":", 1)
    mod = importlib.import_module(modpath)
    obj: Any = mod
    for part in qualname.split("."):
        obj = getattr(obj, part)
    if not callable(obj):
        raise TypeError(f"{ref!r} resolves to non-callable")
    return obj


def _measure(fn: Callable, args: List[Any], kwargs: Dict[str, Any],
             n_repeats: int = 7, max_total_seconds: float = 5.0) -> List[float]:
    """Measure wall time of fn(*args, **kwargs) up to ``n_repeats`` times.

    Stops early if the cumulative wall budget exceeds ``max_total_seconds``
    so unbounded-growth ops don't hang the harness.
    """
    times = []
    t_start = time.perf_counter()
    for _ in range(n_repeats):
        if time.perf_counter() - t_start > max_total_seconds:
            break
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)
    return times


def _fit_complexity(sizes: Sequence[int], times_us: Sequence[float]) -> Tuple[str, float, float]:
    """Fit log-log linear regression to sizes vs times; return (class, coef_us, R^2).

    Returns one of {"O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)",
    "O(n^3)", "O(2^n)", "unknown"} based on the fitted exponent. The
    coefficient is in microseconds at n = 1.
    """
    if not sizes or not times_us or len(sizes) != len(times_us):
        return "unknown", 0.0, 0.0
    if len(sizes) < 2:
        # Single point: report O(1) with the observed time as the coefficient.
        return "O(1)", float(times_us[0]) if times_us else 0.0, 0.0

    # Filter pathological zeros.
    pairs = [(s, t) for s, t in zip(sizes, times_us)
             if s > 0 and t > 0 and not math.isnan(t)]
    if len(pairs) < 2:
        return "O(1)", float(times_us[0]) if times_us else 0.0, 0.0

    log_n = [math.log(s) for s, _ in pairs]
    log_t = [math.log(t) for _, t in pairs]
    n = len(log_n)
    mean_x = sum(log_n) / n
    mean_y = sum(log_t) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_n, log_t))
    den = sum((x - mean_x) ** 2 for x in log_n)
    if den < 1e-30:
        return "O(1)", math.exp(mean_y), 0.0
    slope = num / den
    intercept = mean_y - slope * mean_x

    # R^2
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(log_n, log_t))
    ss_tot = sum((y - mean_y) ** 2 for y in log_t)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-30 else 1.0

    coef_us = math.exp(intercept)

    # Bucket the exponent.
    if slope < 0.2:
        cls = "O(1)"
    elif slope < 0.6:
        cls = "O(log n)"
    elif slope < 1.3:
        cls = "O(n)"
    elif slope < 1.7:
        cls = "O(n log n)"
    elif slope < 2.3:
        cls = "O(n^2)"
    elif slope < 3.3:
        cls = "O(n^3)"
    else:
        cls = "O(2^n)"

    return cls, coef_us, r2


def profile_op(callable_ref: str, declared_max_seconds: float = 0.0,
               n_repeats: int = 7) -> Profile:
    """Profile a single op across the registered probe sizes.

    Returns a ``Profile`` that captures fit + ratio metrics. Catches all
    exceptions and records them in ``Profile.error`` with
    ``calibration_failed=True``.
    """
    p = Profile(callable_ref=callable_ref,
                declared_max_seconds=declared_max_seconds,
                n_repeats=n_repeats)
    try:
        fn = _resolve_callable(callable_ref)
    except Exception as e:
        p.calibration_failed = True
        p.error = f"resolve: {type(e).__name__}: {e}"
        return p

    if callable_ref not in PROBES:
        p.calibration_failed = True
        p.error = "no probe builder registered"
        return p

    sizes, builder = PROBES[callable_ref]
    p.sizes = list(sizes)

    medians_us: List[float] = []
    all_times_s: List[float] = []
    for size in sizes:
        try:
            args, kwargs = builder(size)
        except Exception as e:
            p.calibration_failed = True
            p.error = f"builder(size={size}): {type(e).__name__}: {e}"
            return p
        try:
            ts = _measure(fn, args, kwargs, n_repeats=n_repeats)
        except Exception as e:
            p.calibration_failed = True
            p.error = f"measure(size={size}): {type(e).__name__}: {e}"
            # Record what we have so far; bail out.
            return p
        if not ts:
            medians_us.append(0.0)
            continue
        med = statistics.median(ts)
        medians_us.append(med * 1e6)
        all_times_s.extend(ts)

    p.times_us = medians_us
    if all_times_s:
        all_times_s.sort()
        idx = min(int(len(all_times_s) * 0.95), len(all_times_s) - 1)
        p.p95_max_seconds = all_times_s[idx]
    p.fitted_complexity, p.fitted_coefficient_us, p.fitted_r2 = _fit_complexity(
        sizes, medians_us)
    if declared_max_seconds > 0 and p.p95_max_seconds > 0:
        p.ratio_declared_over_p95 = declared_max_seconds / max(p.p95_max_seconds, 1e-6)
        p.in_band = 0.5 <= p.ratio_declared_over_p95 / 5.0 <= 2.0  # see report
        # Looser test-suite band:
        p.in_band = 2.0 <= p.ratio_declared_over_p95 <= 50.0
    return p


def hardware_profile() -> Dict[str, str]:
    """Capture host info so calibration is reproducible/auditable."""
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "wall_clock": "time.perf_counter (monotonic)",
    }


def calibrated_cost_payload(profile: Profile) -> Dict[str, Any]:
    """Convert a Profile into the structured ``calibrated_cost`` payload
    that goes into ``ArsenalMeta.cost`` (additive — does not replace the
    existing ``max_seconds`` / ``max_memory_mb`` keys).

    The semantics differ from ``max_seconds``:

    - ``max_seconds`` is a *safety budget ceiling* (declared >=2x actual,
      <=50x actual) used by the substrate's BIND/EVAL guard rails.
    - ``calibrated_cost`` is an *empirical scheduling estimate*: the
      complexity class plus the coefficient at n=1, calibrated on
      Skullport / Windows 11 / Python 3.11 on 2026-05-04.
    """
    return {
        "complexity": profile.fitted_complexity,
        "coefficient_us": round(profile.fitted_coefficient_us, 4),
        "fit_r2": round(profile.fitted_r2, 4),
        "p95_seconds": round(profile.p95_max_seconds, 6),
        "median_at_smallest_us": round(profile.times_us[0], 4) if profile.times_us else 0.0,
        "median_at_largest_us": round(profile.times_us[-1], 4) if profile.times_us else 0.0,
        "calibrated_2026_05_04": True,
        "in_band": profile.in_band,
        "host": "Skullport / Windows 11 / Python 3.11.9 / AMD Ryzen 7 5700X3D",
    }


def predict_us(calibrated_cost: Dict[str, Any], size: int) -> float:
    """Predict op cost in microseconds at a given input size, using the
    structured ``calibrated_cost`` payload. Returns 0.0 if the payload is
    malformed or absent.
    """
    if not calibrated_cost:
        return 0.0
    cls = calibrated_cost.get("complexity", "unknown")
    coef = float(calibrated_cost.get("coefficient_us", 0.0))
    if size <= 0 or coef <= 0:
        return coef
    if cls == "O(1)":
        return coef
    if cls == "O(log n)":
        return coef * (1.0 + math.log(max(size, 1)))
    if cls == "O(n)":
        return coef * size
    if cls == "O(n log n)":
        return coef * size * (1.0 + math.log(max(size, 1)))
    if cls == "O(n^2)":
        return coef * size * size
    if cls == "O(n^3)":
        return coef * size * size * size
    if cls == "O(2^n)":
        return coef * (2.0 ** min(size, 30))  # cap to avoid overflow
    return coef


def profile_top_50(declared_costs: Dict[str, float],
                   n_repeats: int = 7) -> Dict[str, Profile]:
    """Profile the canonical top-50 hot-path ops in order. Returns a
    ``{callable_ref: Profile}`` dict. Skips ops missing from
    ``ARSENAL_REGISTRY``.
    """
    out: Dict[str, Profile] = {}
    for ref in TOP_50_HOT_PATH:
        decl = float(declared_costs.get(ref, 0.0))
        out[ref] = profile_op(ref, declared_max_seconds=decl, n_repeats=n_repeats)
    return out


def build_report(profiles: Dict[str, Profile]) -> Dict[str, Any]:
    """Aggregate a per-op profile dict into a JSON-serialisable report."""
    profiled = [p for p in profiles.values() if not p.calibration_failed]
    failed = [p for p in profiles.values() if p.calibration_failed]
    in_band = [p for p in profiled if p.in_band]
    out_of_band = [p for p in profiled
                   if not p.in_band and p.declared_max_seconds > 0
                   and p.p95_max_seconds > 0]
    out_of_band_sorted = sorted(
        out_of_band,
        key=lambda p: max(
            p.ratio_declared_over_p95, 1.0 / max(p.ratio_declared_over_p95, 1e-9)
        ),
        reverse=True,
    )
    return {
        "hardware": hardware_profile(),
        "n_profiled": len(profiles),
        "n_calibrated": len(profiled),
        "n_failed": len(failed),
        "n_in_band_2x_to_50x": len(in_band),
        "n_out_of_band": len(out_of_band),
        "worst_skewed_top5": [p.to_dict() for p in out_of_band_sorted[:5]],
        "profiles": {ref: p.to_dict() for ref, p in profiles.items()},
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-50", action="store_true",
                        help="Profile the curated top-50 hot-path ops")
    parser.add_argument("--output", type=str, default="cost_calibration.json",
                        help="JSON output path")
    parser.add_argument("--n-repeats", type=int, default=7,
                        help="Wall-time repeats per (op, size) cell")
    args = parser.parse_args()

    # Defer import so --help works even if registry breaks.
    from prometheus_math.arsenal_meta import ARSENAL_REGISTRY

    declared = {ref: meta.cost.get("max_seconds", 0.0)
                for ref, meta in ARSENAL_REGISTRY.items()}

    if args.top_50:
        profiles = profile_top_50(declared, n_repeats=args.n_repeats)
    else:
        profiles = {ref: profile_op(ref, declared.get(ref, 0.0),
                                    n_repeats=args.n_repeats)
                    for ref in PROBES if ref in ARSENAL_REGISTRY}

    report = build_report(profiles)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"profiled {report['n_profiled']} ops; "
          f"calibrated {report['n_calibrated']}, "
          f"in_band={report['n_in_band_2x_to_50x']}, "
          f"failed={report['n_failed']}")
    print(f"report -> {args.output}")
    return 0


if __name__ == "__main__":
    # Allow `python prometheus_math/cost_model_profiler.py` from the repo
    # root by adding the parent directory to sys.path.
    import os
    _here = os.path.dirname(os.path.abspath(__file__))
    _parent = os.path.dirname(_here)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    try:
        raise SystemExit(_cli())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
