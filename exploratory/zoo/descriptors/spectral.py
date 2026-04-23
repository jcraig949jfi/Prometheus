"""Spectral decay descriptor: per-function intrinsic compressibility.

For a tensor T of shape (n_1, ..., n_d), the unfolding matrix at bond k has
shape (prod n_1..n_k, prod n_{k+1}..n_d). Its singular value spectrum
governs how well TT can compress at that bond.

We fit log(sigma_i) ~ c - alpha * log(i) on the top-K normalized singular
values at the middle bond and report alpha. Higher alpha = faster decay
= more compressible. alpha = 0 means flat spectrum (no compressibility);
alpha = inf would mean the second value is zero (rank-1 exact).

This is a function-level descriptor — it does not change as TT ranks evolve.
It is the intrinsic axis against which approximation-level descriptors
(rank, error) get interpreted.
"""
from __future__ import annotations
import numpy as np


def _middle_bond(d: int) -> int:
    return max(0, d // 2 - 1)  # index of bond after which we split


def spectral_decay(dense: np.ndarray, bond: int | None = None,
                   n_top: int = 16, noise_floor: float = 1e-12) -> dict:
    """Fit alpha in log(sigma_i / sigma_1) ~ -alpha * log(i) on the top n_top
    normalized singular values of the unfolding at `bond`.

    Returns dict with: alpha, fit_r2, sigma_top (length min(n_top, rank)), bond,
    n_kept_for_fit, note (set when fit short-circuits).
    """
    d = dense.ndim
    if bond is None:
        bond = _middle_bond(d)
    shape = dense.shape
    left_size = int(np.prod(shape[: bond + 1]))
    right_size = int(np.prod(shape[bond + 1:]))
    M = dense.reshape(left_size, right_size)
    sigmas = np.linalg.svd(M, compute_uv=False)

    n_keep = min(n_top, len(sigmas))
    sigma_top = sigmas[:n_keep]
    if sigma_top[0] < noise_floor:
        return {"alpha": 0.0, "sigma_top": [float(s) for s in sigma_top],
                "fit_r2": None, "bond": int(bond),
                "n_kept_for_fit": 0, "note": "zero spectrum"}

    sigma_norm = sigma_top / sigma_top[0]
    log_idx = np.log(np.arange(1, n_keep + 1))

    mask = sigma_norm >= noise_floor
    if mask.sum() < 3:
        return {"alpha": float("inf"), "sigma_top": [float(s) for s in sigma_top],
                "fit_r2": None, "bond": int(bond),
                "n_kept_for_fit": int(mask.sum()),
                "note": "spectrum collapses to noise floor too quickly (super-fast decay)"}

    log_sigma = np.log(np.clip(sigma_norm[mask], noise_floor, None))
    A = np.column_stack([np.ones(mask.sum()), -log_idx[mask]])
    sol, *_ = np.linalg.lstsq(A, log_sigma, rcond=None)
    c, alpha = sol
    pred = A @ sol
    ss_res = float(np.sum((log_sigma - pred) ** 2))
    ss_tot = float(np.sum((log_sigma - np.mean(log_sigma)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else 1.0

    return {
        "alpha": float(alpha),
        "sigma_top": [float(s) for s in sigma_top],
        "fit_r2": r2,
        "bond": int(bond),
        "n_kept_for_fit": int(mask.sum()),
        "note": None,
    }
