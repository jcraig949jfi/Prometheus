"""Stability descriptor: how much does the TT approximation drift under
small perturbations of the input tensor?

Procedure: add Gaussian noise scaled to relative magnitude `noise_level`,
recompute TT-SVD at the same rank profile, measure the L2 distance between
the two approximations relative to the unperturbed approximation.

Interpretation:
  drift << noise_level: TT compression is robust (the structure being captured
    is genuinely there).
  drift ~~ noise_level: linear stability (proportional to perturbation).
  drift >> noise_level: fragile compression (small input changes produce large
    representation changes — characteristic of approximations that latch onto
    coincidental SVD alignments rather than structure).

This is a per-(function, rank) measurement. Cheap enough to compute on every
Pareto-front elite at the end of a run.
"""
from __future__ import annotations
import numpy as np

from ..tt.core import TTDecomposition, tt_svd, relative_l2_error


def stability_under_perturbation(dense: np.ndarray, ranks: tuple[int, ...],
                                 noise_level: float = 1e-3, n_trials: int = 3,
                                 seed: int = 20260424) -> dict:
    rng = np.random.default_rng(seed)
    base_tt = tt_svd(dense, max_ranks=ranks)
    base_recon = base_tt.reconstruct()
    base_error = relative_l2_error(dense, base_recon)

    base_norm = float(np.linalg.norm(base_recon))
    sigma = noise_level * float(np.linalg.norm(dense)) / np.sqrt(dense.size)

    drifts: list[float] = []
    for _ in range(n_trials):
        noise = rng.standard_normal(dense.shape) * sigma
        perturbed = dense + noise
        pert_tt = tt_svd(perturbed, max_ranks=ranks)
        pert_recon = pert_tt.reconstruct()
        if base_norm == 0:
            drifts.append(0.0)
        else:
            drifts.append(float(np.linalg.norm(pert_recon - base_recon) / base_norm))

    mean_drift = float(np.mean(drifts))
    return {
        "noise_level": noise_level,
        "n_trials": n_trials,
        "base_error": float(base_error),
        "drifts": drifts,
        "mean_drift": mean_drift,
        "max_drift": float(np.max(drifts)),
        "stability_ratio": float(noise_level / max(mean_drift, 1e-15)),
        # > 1 => robust (drift < noise); ~ 1 => linear; < 1 => fragile (amplifies noise)
    }
