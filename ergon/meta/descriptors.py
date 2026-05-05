"""
Descriptors v2: minima-anchored, volume-weighted, with global ruggedness.

Five measurements per Landscape for MAP-Elites binning + analysis:

 1. n_minima                  -- count of distinct basins (hierarchical clustering)
 2. minima_avg_curvature      -- VOLUME-WEIGHTED average of trace(H(x_k*)) / d
                                 across discovered minima, weighted by basin-count
 3. minima_worst_conditioning -- max_k log10(kappa(H(x_k*)))
 4. depth_range               -- max f(x_k*) - min f(x_k*)
 5. ruggedness                -- autocorrelation length of f along random walks

Also computed (non-binned telemetry):
 - basin_entropy (legacy)
 - normalized_entropy
 - origin_curvature / origin_conditioning (for comparison to v1 artifacts)

Descriptor probe: MIXED
 - 40 L-BFGS-B multi-starts -> discover basins, endpoints, values
 - 40 pure-random samples   -> de-bias from gradient-friendly structure (global stats)
 - 10 random walks x 50 steps -> ruggedness (f-autocorrelation)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from scipy.optimize import minimize
from scipy.cluster.hierarchy import linkage, fcluster


# ---------- helpers ----------------------------------------------------------

def _minimize_to_local(landscape, x0, bounds=None, maxiter=100):
    res = minimize(
        lambda x: float(landscape.evaluate(x)),
        x0,
        jac=lambda x: landscape.grad(x),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': maxiter, 'ftol': 1e-8, 'gtol': 1e-6},
    )
    return res.x, float(res.fun), res.success


def _cluster_endpoints(final_points: np.ndarray, tol: float) -> np.ndarray:
    if len(final_points) <= 1:
        return np.zeros(len(final_points), dtype=int)
    Z = linkage(final_points, method='single', metric='euclidean')
    labels = fcluster(Z, t=tol, criterion='distance')
    return labels - 1  # zero-indexed


def _random_walk(landscape, x0, n_steps, step_size, rng):
    """Simple random walk: x_{t+1} = x_t + step_size * unit_normal.
    Returns (positions, values) arrays of length n_steps+1.
    """
    d = landscape.d
    xs = np.zeros((n_steps + 1, d))
    xs[0] = x0
    for t in range(n_steps):
        step = rng.standard_normal(d)
        step = step / (np.linalg.norm(step) + 1e-12) * step_size
        xs[t + 1] = xs[t] + step
    vs = landscape.evaluate(xs)
    return xs, np.asarray(vs, dtype=float)


def _autocorrelation_length(series: np.ndarray) -> float:
    """First lag at which autocorrelation falls below 1/e.
    Returns a float in [0, len(series)]; lower = more rugged.
    """
    s = series - series.mean()
    var = (s * s).mean()
    if var <= 0:
        return 0.0
    n = len(s)
    max_lag = min(n - 1, 25)
    for lag in range(1, max_lag + 1):
        c = (s[:-lag] * s[lag:]).mean() / var
        if c < math.exp(-1):
            return float(lag)
    return float(max_lag)


# ---------- main result ------------------------------------------------------

@dataclass
class DescriptorResult:
    # 5 primary axes (binned)
    n_minima: int
    minima_avg_curvature: float         # volume-weighted mean of trace(H(x_k*))/d
    minima_worst_conditioning: float    # max_k log10(kappa(H(x_k*)))
    depth_range: float
    ruggedness: float                   # mean autocorrelation length across walks

    # Telemetry (non-binned)
    basin_entropy: float
    normalized_entropy: float
    origin_curvature: float             # v1 metric, kept for comparison
    origin_conditioning: float          # v1 metric
    minima_curvatures: list             # per-minimum trace(H)/d
    minima_conditioning: list           # per-minimum log10(kappa)
    basin_counts: dict
    basin_weights: list                 # per-minimum normalized volume weight

    # Artifacts
    minima: list                        # list of (x, f)
    endpoints: np.ndarray
    labels: np.ndarray
    random_samples: np.ndarray          # (40, d) pure-random probe
    random_values: np.ndarray           # (40,)
    walk_values: np.ndarray             # (10, 51) gradient-independent walks


def compute_descriptors(
    landscape,
    n_starts: int = 40,
    n_random_samples: int = 40,
    n_walks: int = 10,
    walk_steps: int = 50,
    walk_step_size_frac: float = 0.2,
    box_scale: float = 4.0,
    cluster_tol_frac: float = 0.025,
    rng: Optional[np.random.Generator] = None,
) -> DescriptorResult:
    """Mixed-probe descriptor extraction.

    cluster_tol_frac: merger tolerance as a fraction of box_scale (v2a change:
    scale-aware). For box_scale=4 this is 0.1 (unchanged in 2D).
    """
    if rng is None:
        rng = np.random.default_rng()

    d = landscape.d
    bounds = [(-box_scale, box_scale)] * d
    cluster_tol = cluster_tol_frac * box_scale

    # --- 1. L-BFGS-B probe ---
    starts = rng.uniform(-box_scale, box_scale, size=(n_starts, d))
    endpoints = np.zeros_like(starts)
    values = np.zeros(n_starts)
    for i in range(n_starts):
        xf, vf, _ = _minimize_to_local(landscape, starts[i], bounds=bounds)
        endpoints[i] = xf
        values[i] = vf

    # Cluster endpoints into basins
    labels = _cluster_endpoints(endpoints, tol=cluster_tol)
    n_minima = int(labels.max() + 1) if len(labels) else 0

    # Per-basin statistics
    basin_counts = {}
    for lab in labels:
        basin_counts[int(lab)] = basin_counts.get(int(lab), 0) + 1
    total = sum(basin_counts.values())
    probs = np.array([c / total for c in basin_counts.values()])
    basin_entropy = float(-(probs * np.log(probs + 1e-12)).sum())
    norm_entropy = basin_entropy / math.log(max(2, n_minima))

    # Mean endpoint + mean value within each basin
    minima = []
    basin_weights = []
    minima_curvs = []
    minima_conds = []
    for lab in sorted(basin_counts.keys()):
        idx = np.where(labels == lab)[0]
        x_mean = endpoints[idx].mean(axis=0)
        v_mean = float(values[idx].mean())
        minima.append((x_mean, v_mean))

        weight = len(idx) / total
        basin_weights.append(weight)

        # Curvature + conditioning AT THIS MINIMUM
        H = landscape.hessian(x_mean)
        trace_h = float(np.trace(H))
        eig = np.linalg.eigvalsh(H)
        abs_eig = np.abs(eig)
        if abs_eig.min() < 1e-8:
            log_cond_k = 8.0
        else:
            log_cond_k = float(np.log10(abs_eig.max() / abs_eig.min()))
        minima_curvs.append(trace_h / d)
        minima_conds.append(log_cond_k)

    # VOLUME-WEIGHTED average curvature
    if minima_curvs:
        w = np.array(basin_weights)
        c = np.array(minima_curvs)
        minima_avg_curvature = float(np.sum(w * c))
    else:
        minima_avg_curvature = 0.0

    # WORST-CASE conditioning
    minima_worst_conditioning = float(max(minima_conds)) if minima_conds else 0.0

    # Depth range
    min_values = np.array([v for (_, v) in minima])
    depth_range = float(min_values.max() - min_values.min()) if len(min_values) >= 2 else 0.0

    # Legacy: origin-anchored (for comparison with v1)
    origin = np.zeros(d)
    H0 = landscape.hessian(origin)
    origin_curvature = float(np.trace(H0) / d)
    eig0 = np.abs(np.linalg.eigvalsh(H0))
    if eig0.min() < 1e-8:
        origin_conditioning = 8.0
    else:
        origin_conditioning = float(np.log10(eig0.max() / eig0.min()))

    # --- 2. Pure-random probe (gradient-independent) ---
    random_samples = rng.uniform(-box_scale, box_scale, size=(n_random_samples, d))
    random_values = np.asarray(landscape.evaluate(random_samples), dtype=float)

    # --- 3. Random walks for ruggedness ---
    walk_values = np.zeros((n_walks, walk_steps + 1))
    walk_step_size = walk_step_size_frac * box_scale
    walk_corr_lengths = []
    for w in range(n_walks):
        x0 = rng.uniform(-box_scale, box_scale, size=d)
        _, vs = _random_walk(landscape, x0, walk_steps, walk_step_size, rng)
        walk_values[w] = vs
        walk_corr_lengths.append(_autocorrelation_length(vs))
    ruggedness = float(np.mean(walk_corr_lengths))

    return DescriptorResult(
        n_minima=n_minima,
        minima_avg_curvature=minima_avg_curvature,
        minima_worst_conditioning=minima_worst_conditioning,
        depth_range=depth_range,
        ruggedness=ruggedness,
        basin_entropy=basin_entropy,
        normalized_entropy=norm_entropy,
        origin_curvature=origin_curvature,
        origin_conditioning=origin_conditioning,
        minima_curvatures=minima_curvs,
        minima_conditioning=minima_conds,
        basin_counts=basin_counts,
        basin_weights=basin_weights,
        minima=minima,
        endpoints=endpoints,
        labels=labels,
        random_samples=random_samples,
        random_values=random_values,
        walk_values=walk_values,
    )


# ---------- binning (5 axes, 3 bins each = 243 cells, quantile-based) -------

DESCRIPTOR_NAMES = (
    "n_minima",
    "minima_avg_curvature",
    "minima_worst_conditioning",
    "depth_range",
    "ruggedness",
)

N_BINS_PER_AXIS = 3


def _as_vector(desc: DescriptorResult) -> np.ndarray:
    return np.array([
        desc.n_minima,
        desc.minima_avg_curvature,
        desc.minima_worst_conditioning,
        desc.depth_range,
        desc.ruggedness,
    ])


def fit_quantile_edges(sample_descs: list, n_bins: int = N_BINS_PER_AXIS) -> dict:
    X = np.array([_as_vector(d) for d in sample_descs])
    qs = np.linspace(0, 1, n_bins + 1)[1:-1]
    edges = {}
    for i, name in enumerate(DESCRIPTOR_NAMES):
        edges[name] = [float(np.quantile(X[:, i], q)) for q in qs]
    return edges


def bin_index(value: float, edges: list) -> int:
    idx = 0
    for e in edges:
        if value >= e:
            idx += 1
        else:
            break
    return idx


def cell_key(desc: DescriptorResult, edges: dict) -> tuple:
    return (
        bin_index(desc.n_minima, edges["n_minima"]),
        bin_index(desc.minima_avg_curvature, edges["minima_avg_curvature"]),
        bin_index(desc.minima_worst_conditioning, edges["minima_worst_conditioning"]),
        bin_index(desc.depth_range, edges["depth_range"]),
        bin_index(desc.ruggedness, edges["ruggedness"]),
    )


# ---------- independence check ------------------------------------------------

def correlation_matrix(sample_descs: list) -> np.ndarray:
    X = np.array([_as_vector(d) for d in sample_descs])
    return np.corrcoef(X.T)


def max_offdiag(C: np.ndarray) -> float:
    n = C.shape[0]
    mask = ~np.eye(n, dtype=bool)
    return float(np.abs(C[mask]).max())
