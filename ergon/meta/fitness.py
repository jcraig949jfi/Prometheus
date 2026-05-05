"""
Multi-component disagreement fitness (v2).

v1 used a single scalar: stdev(final_value across optimizers).
v2 decomposes disagreement into 4 orthogonal components:

  value_stdev          -- spread of final f values (classic, v1)
  traj_divergence      -- pairwise mean DTW distance on grad-norm sequences
  basin_entropy        -- Shannon entropy over final-basin IDs
  speed_variance       -- variance of iters-to-eps-optimal across optimizers

Two interfaces:
  - weighted_scalar: f = w1*value + w2*traj + w3*basin + w4*speed
    (default for MAP-Elites placement)
  - component_vector: returns the 4-tuple for multi-objective analysis

Also provides:
  - optimizer_ranking: order optimizers best-to-worst by final_value
  - intra_cell_variance: given a set of trajectories-per-landscape over
    multiple landscapes in the SAME MAP cell, reports how variable the
    optimizer ranking is within that cell (v2a addition — distinguishes
    "descriptors missing" from "intra-cell heterogeneity" in the
    predictive-model layer).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from ergon.meta.trajectory import Trajectory, dtw_distance


# ---------- per-landscape disagreement components ----------------------------

@dataclass
class DisagreementComponents:
    value_stdev: float
    traj_divergence: float
    basin_entropy: float
    speed_variance: float
    ranking: list           # optimizer names best-to-worst by final_value

    def as_vector(self) -> np.ndarray:
        return np.array([self.value_stdev, self.traj_divergence,
                         self.basin_entropy, self.speed_variance])


def compute_disagreement(trajs: List[Trajectory]) -> DisagreementComponents:
    """Given one list of Trajectories (one per optimizer on one landscape),
    compute the 4-component disagreement."""
    vals = np.array([t.final_value for t in trajs])
    value_stdev = float(vals.std())

    # Pairwise DTW divergence on grad-norm sequences
    n = len(trajs)
    if n >= 2:
        ds = []
        for i in range(n):
            for j in range(i + 1, n):
                ds.append(dtw_distance(trajs[i].grad_norms, trajs[j].grad_norms))
        traj_divergence = float(np.mean(ds)) if ds else 0.0
    else:
        traj_divergence = 0.0

    # Basin entropy
    basins = np.array([t.final_basin for t in trajs])
    valid = basins[basins >= 0]
    if len(valid) > 0:
        _, counts = np.unique(valid, return_counts=True)
        probs = counts / counts.sum()
        basin_entropy = float(-(probs * np.log(probs + 1e-12)).sum())
    else:
        basin_entropy = 0.0

    # Speed variance (only on optimizers that reached epsilon-optimal)
    iters = np.array([t.iters_to_eps for t in trajs if t.iters_to_eps >= 0])
    speed_variance = float(iters.var()) if len(iters) >= 2 else 0.0

    # Ranking best-to-worst by final_value
    order = np.argsort(vals)
    ranking = [trajs[i].optimizer for i in order]

    return DisagreementComponents(
        value_stdev=value_stdev,
        traj_divergence=traj_divergence,
        basin_entropy=basin_entropy,
        speed_variance=speed_variance,
        ranking=ranking,
    )


# ---------- weighted scalar --------------------------------------------------

DEFAULT_WEIGHTS = {
    "value_stdev":     1.0,
    "traj_divergence": 0.5,
    "basin_entropy":   2.0,
    "speed_variance":  0.02,  # iters^2 is large; downweight
}


def weighted_scalar(disagreement: DisagreementComponents,
                    weights: dict = None) -> float:
    w = weights or DEFAULT_WEIGHTS
    return (w["value_stdev"]     * disagreement.value_stdev +
            w["traj_divergence"] * disagreement.traj_divergence +
            w["basin_entropy"]   * disagreement.basin_entropy +
            w["speed_variance"]  * disagreement.speed_variance)


# ---------- intra-cell variance (v2a addition) -------------------------------

def intra_cell_ranking_variance(cell_rankings: List[list]) -> float:
    """Measure variability of optimizer RANKINGS (not final values) within a
    single MAP cell.

    cell_rankings: list of optimizer-name lists, one per landscape in the cell.
    Returns a normalized Kendall-tau-like disagreement score in [0, 1].
      0 = all landscapes in the cell have the same ranking.
      1 = maximum disagreement.

    Used to distinguish:
      - "model uncertainty due to MISSING DESCRIPTOR AXIS" (cells should have
        internally consistent rankings; high uncertainty = cell-scale heterogeneity
        the descriptors don't see)
      - "model uncertainty due to INTRA-CELL NOISE" (rankings vary wildly within
        one cell; descriptors ARE adequate but the landscape parameterization
        is stochastic below the cell resolution)
    """
    if len(cell_rankings) < 2:
        return 0.0
    # Flatten to rank vectors per optimizer
    optimizers = list(cell_rankings[0])
    rank_matrix = np.zeros((len(cell_rankings), len(optimizers)))
    for i, rk in enumerate(cell_rankings):
        for rank, opt in enumerate(rk):
            if opt in optimizers:
                rank_matrix[i, optimizers.index(opt)] = rank
    # Average stdev of rank across landscapes, normalized by max possible stdev
    stds = rank_matrix.std(axis=0)
    max_std = (len(optimizers) - 1) / 2.0  # crude but serviceable normalizer
    return float(stds.mean() / max_std) if max_std > 0 else 0.0
