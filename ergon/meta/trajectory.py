"""
Trajectory geometry layer.

For each optimizer run we record the full path (subsampled to ~100 steps).
This module computes scalar metrics and a DTW-based distance matrix for
failure-mode clustering.

Scalar features per trajectory:
  path_length       -- sum of step distances
  path_curvature    -- mean turn angle between consecutive segments (radians)
  grad_norm_decay   -- fitted exponent alpha in ||grad||_t ~ t^{-alpha}
  stall_fraction    -- fraction of iterations with step size below threshold
  final_value       -- f at end
  final_basin       -- discretized basin ID (nearest to a known minimum)

DTW distance matrix (for clustering):
  computed on the gradient-norm sequence ||grad(x_t)|| over iterations.
  Preserves the TEMPORAL NARRATIVE of convergence, unlike scalar features
  alone.

Clustering:
  hierarchical (scipy linkage 'average') on DTW distance matrix, producing
  failure-mode labels.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform


# ---------- trajectory record -----------------------------------------------

@dataclass
class Trajectory:
    """Record of one optimizer run on one landscape."""
    optimizer: str
    positions: np.ndarray       # (T, d), subsampled
    values: np.ndarray          # (T,)
    grad_norms: np.ndarray      # (T,)
    iters_to_eps: int           # iterations to reach epsilon-optimal or -1
    total_iters: int
    final_x: np.ndarray
    final_value: float
    final_basin: int = -1       # assigned post-hoc by nearest-minimum lookup


# ---------- scalar features --------------------------------------------------

def path_length(positions: np.ndarray) -> float:
    if len(positions) < 2:
        return 0.0
    d = np.diff(positions, axis=0)
    return float(np.linalg.norm(d, axis=1).sum())


def path_curvature(positions: np.ndarray) -> float:
    """Mean turn angle (radians) between consecutive segments."""
    if len(positions) < 3:
        return 0.0
    d = np.diff(positions, axis=0)
    norms = np.linalg.norm(d, axis=1) + 1e-12
    u = d / norms[:, None]
    # Dot product between consecutive unit vectors
    dots = np.clip(np.sum(u[:-1] * u[1:], axis=1), -1.0, 1.0)
    angles = np.arccos(dots)
    return float(angles.mean())


def grad_norm_decay(grad_norms: np.ndarray) -> float:
    """Fit ||grad||_t ~ t^{-alpha}. Returns alpha (higher = faster decay)."""
    if len(grad_norms) < 5:
        return 0.0
    g = np.asarray(grad_norms, dtype=float)
    g = np.where(g <= 0, 1e-12, g)
    t = np.arange(1, len(g) + 1)
    # Simple log-log OLS
    log_t = np.log(t)
    log_g = np.log(g)
    # alpha = -slope of log_g vs log_t
    slope, _ = np.polyfit(log_t, log_g, 1)
    return float(-slope)


def stall_fraction(positions: np.ndarray, threshold: float = 1e-3) -> float:
    if len(positions) < 2:
        return 0.0
    d = np.diff(positions, axis=0)
    step_sizes = np.linalg.norm(d, axis=1)
    return float((step_sizes < threshold).mean())


def featurize(traj: Trajectory) -> dict:
    return {
        "optimizer": traj.optimizer,
        "path_length": path_length(traj.positions),
        "path_curvature": path_curvature(traj.positions),
        "grad_norm_decay": grad_norm_decay(traj.grad_norms),
        "stall_fraction": stall_fraction(traj.positions),
        "final_value": traj.final_value,
        "final_basin": traj.final_basin,
        "iters_to_eps": traj.iters_to_eps,
        "total_iters": traj.total_iters,
    }


# ---------- DTW on gradient-norm sequences ----------------------------------

def dtw_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Dynamic Time Warping distance between two 1D sequences.

    Pure numpy implementation; O(|a|*|b|) time, O(min(|a|,|b|)) extra memory
    via rolling rows.
    """
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return float("inf")
    # Work with log-scale to make the distance more meaningful for decaying
    # sequences; adds a small offset to avoid log(0).
    la = np.log(np.asarray(a, dtype=float) + 1e-12)
    lb = np.log(np.asarray(b, dtype=float) + 1e-12)

    # Rolling-row DP
    INF = float("inf")
    prev = np.full(m + 1, INF); prev[0] = 0.0
    for i in range(1, n + 1):
        cur = np.full(m + 1, INF)
        cur[0] = INF
        for j in range(1, m + 1):
            cost = (la[i - 1] - lb[j - 1]) ** 2
            cur[j] = cost + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    # Normalize by path length (roughly n + m)
    return float(prev[m] ** 0.5 / (n + m))


def dtw_pairwise_matrix(trajs: List[Trajectory]) -> np.ndarray:
    """Pairwise DTW distance on gradient-norm sequences."""
    n = len(trajs)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            D[i, j] = D[j, i] = dtw_distance(trajs[i].grad_norms, trajs[j].grad_norms)
    return D


def cluster_trajectories(trajs: List[Trajectory], n_clusters: int = 4) -> np.ndarray:
    """Hierarchical clustering on DTW distance. Returns (n,) label array."""
    if len(trajs) <= 1:
        return np.zeros(len(trajs), dtype=int)
    D = dtw_pairwise_matrix(trajs)
    condensed = squareform(D, checks=False)
    Z = linkage(condensed, method='average')
    labels = fcluster(Z, t=n_clusters, criterion='maxclust')
    return labels - 1


# ---------- basin assignment (post-hoc) -------------------------------------

def assign_final_basin(
    traj: Trajectory,
    minima: list,
    tol_frac: float = 0.05,
    box_scale: float = 4.0,
) -> int:
    """Assign traj.final_x to the nearest known minimum; return basin ID or -1."""
    if not minima:
        return -1
    centers = np.array([m[0] for m in minima])
    dists = np.linalg.norm(centers - traj.final_x, axis=1)
    best = int(dists.argmin())
    if dists[best] <= tol_frac * box_scale:
        return best
    return -1
