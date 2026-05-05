"""Stability descriptor — formal, gauge-invariant.

For a tensor T with TT approximation \\hat{T}(T) at rank profile r, define

    S(T, r, eps) := eps / E_delta[ || \\hat{T}(T + delta) - \\hat{T}(T) ||_F / || \\hat{T}(T) ||_F ]

where delta ~ N(0, sigma^2 I) with sigma chosen so E[||delta||_F] = eps * ||T||_F,
i.e. sigma = eps * ||T||_F / sqrt(|T|).

Gauge invariance. TT representations are non-unique up to bond-wise gauge:
G_k -> G_k A, G_{k+1} -> A^{-1} G_{k+1} leaves the represented tensor fixed.
Because S is defined on the reconstruction norm (not on the cores), S is
invariant under any gauge choice made inside tt_svd.

Interpretation.
  S > 1  : drift < noise => robust compression (structure is real)
  S ~ 1  : linear stability (drift proportional to noise)
  S < 1  : fragile compression (noise amplified by representation; the
           approximation is latched onto coincidental SVD alignment)

Implementation returns drifts per trial so the caller can audit the
distribution (a single mean can hide heavy-tailed instability).
"""
from __future__ import annotations
import numpy as np

from ..tt.core import tt_svd, relative_l2_error


def _stable_norm(x: np.ndarray) -> float:
    return float(np.linalg.norm(x))


def stability_under_perturbation(dense: np.ndarray, ranks: tuple[int, ...],
                                 noise_level: float = 1e-3, n_trials: int = 3,
                                 seed: int = 20260424) -> dict:
    """Compute S(T, r, eps) with n_trials realizations of delta.

    All distances are measured on the reconstructed tensors, making S
    gauge-invariant by construction.
    """
    rng = np.random.default_rng(seed)
    base_tt = tt_svd(dense, max_ranks=ranks)
    base_recon = base_tt.reconstruct()
    base_error = relative_l2_error(dense, base_recon)

    t_norm = _stable_norm(dense)
    sigma = noise_level * t_norm / np.sqrt(dense.size)
    base_recon_norm = _stable_norm(base_recon)

    drifts: list[float] = []
    for _ in range(n_trials):
        delta = rng.standard_normal(dense.shape) * sigma
        perturbed = dense + delta
        pert_tt = tt_svd(perturbed, max_ranks=ranks)
        pert_recon = pert_tt.reconstruct()
        if base_recon_norm == 0:
            drifts.append(0.0)
        else:
            drifts.append(_stable_norm(pert_recon - base_recon) / base_recon_norm)

    mean_drift = float(np.mean(drifts))
    median_drift = float(np.median(drifts))
    return {
        "metric_type": "reconstruction_frobenius",
        "gauge_invariant": True,
        "noise_level": noise_level,
        "n_trials": n_trials,
        "base_error": float(base_error),
        "drifts": [float(d) for d in drifts],
        "mean_drift": mean_drift,
        "median_drift": median_drift,
        "max_drift": float(np.max(drifts)),
        "stability_ratio": float(noise_level / max(mean_drift, 1e-15)),
        "log_stability_ratio": float(np.log10(max(noise_level / max(mean_drift, 1e-15), 1e-15))),
    }
