"""Subspace-angle stability cross-check.

An independent gauge-invariant probe: at each bond k, the left-unfolding
subspace U_k (top r_k left singular vectors of the unfolding matrix) is
a gauge-invariant object — it is the projector onto the dominant subspace
at that bond. A perturbation delta induces a subspace U_k' at the same
rank, and the principal angle between U_k and U_k' measures how much the
dominant structure shifted.

If reconstruction-based stability and subspace-angle stability rank the
same elites similarly, we have cross-metric agreement. If they disagree,
the "stability" descriptor is carrying at least two distinct phenomena
and we should not treat it as a single axis.

Principal angle theta between two k-dim subspaces with orthonormal bases
U, V is given by arccos of the smallest singular value of U^T V. We use
sin(theta) = sqrt(1 - min_sv^2) as the distance (range [0, 1]).

Gauge invariance: the subspace itself is gauge-invariant (gauge acts on
the right, not on the left unfoldings); the principal angle is therefore
gauge-invariant as well.
"""
from __future__ import annotations
import numpy as np


def _left_unfolding_subspace(dense: np.ndarray, bond: int, rank: int) -> np.ndarray:
    """Top-`rank` left singular vectors of the bond-k unfolding."""
    d = dense.ndim
    shape = dense.shape
    left_size = int(np.prod(shape[: bond + 1]))
    right_size = int(np.prod(shape[bond + 1:]))
    M = dense.reshape(left_size, right_size)
    U, _, _ = np.linalg.svd(M, full_matrices=False)
    r = min(rank, U.shape[1])
    return U[:, :r]


def _principal_sin(U: np.ndarray, V: np.ndarray) -> float:
    """sin of the largest principal angle between column spans of U and V.

    Returns a value in [0, 1]: 0 = subspaces agree exactly, 1 = orthogonal.
    """
    if U.shape[1] == 0 or V.shape[1] == 0:
        return 1.0
    # Align by projection SVD
    M = U.T @ V
    svals = np.linalg.svd(M, compute_uv=False)
    s_min = float(np.clip(np.min(svals), 0.0, 1.0))
    return float(np.sqrt(max(0.0, 1.0 - s_min ** 2)))


def subspace_stability(dense: np.ndarray, ranks: tuple[int, ...],
                       noise_level: float = 1e-3, n_trials: int = 3,
                       seed: int = 20260424) -> dict:
    rng = np.random.default_rng(seed)
    d = dense.ndim
    t_norm = float(np.linalg.norm(dense))
    sigma = noise_level * t_norm / np.sqrt(dense.size)

    # Base subspaces at each internal bond (d - 1 bonds)
    base_subspaces = [
        _left_unfolding_subspace(dense, bond=k, rank=ranks[k])
        for k in range(d - 1)
    ]

    angles_per_trial: list[list[float]] = []
    for _ in range(n_trials):
        delta = rng.standard_normal(dense.shape) * sigma
        perturbed = dense + delta
        pert_subspaces = [
            _left_unfolding_subspace(perturbed, bond=k, rank=ranks[k])
            for k in range(d - 1)
        ]
        angles = [
            _principal_sin(base_subspaces[k], pert_subspaces[k])
            for k in range(d - 1)
        ]
        angles_per_trial.append(angles)

    angles_arr = np.array(angles_per_trial)  # (n_trials, d-1)
    mean_angle_per_bond = angles_arr.mean(axis=0).tolist()
    max_angle = float(angles_arr.max())
    mean_angle = float(angles_arr.mean())

    return {
        "metric_type": "principal_subspace_angle_sin",
        "gauge_invariant": True,
        "noise_level": noise_level,
        "n_trials": n_trials,
        "mean_angle_per_bond": [float(x) for x in mean_angle_per_bond],
        "mean_angle": mean_angle,
        "max_angle": max_angle,
        "log_subspace_stability": float(np.log10(max(noise_level / max(mean_angle, 1e-15), 1e-15))),
    }
