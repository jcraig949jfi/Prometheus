"""NULL_PLAIN@v1 reference implementation.

Plain unrestricted label-permutation null — the baseline coarse lens.
Preserves only the shuffled-column marginal; destroys pairings and all
stratification. Family member in gen_02 null-family.

Spec: harmonia/memory/symbols/NULL_PLAIN.md (v1, promoted 2026-04-20).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
import pandas as pd


def _default_statistic(data: pd.DataFrame) -> float:
    return float(np.mean(data["value"].values))


def plain_null(
    data: pd.DataFrame,
    n_perms: int = 300,
    seed: int = 20260420,
    statistic: Optional[Callable[[pd.DataFrame], float]] = None,
    shuffle_col: str = "value",
) -> dict:
    """NULL_PLAIN@v1.

    Parameters
    ----------
    data : DataFrame containing at minimum `shuffle_col`.
    n_perms : number of permutations (default 300 per v1 pin).
    seed : RNG seed (default 20260420 per v1 pin).
    statistic : callable(data) -> float. Default: mean(data['value']).
    shuffle_col : column permuted globally. Default "value".

    Returns
    -------
    dict with null_mean, null_std, null_p99, observed, z_score, verdict,
    n_perms, seed.
    """
    if statistic is None:
        statistic = _default_statistic

    if shuffle_col not in data.columns:
        raise ValueError(f"shuffle_col '{shuffle_col}' missing from data")

    rng = np.random.default_rng(seed)
    observed = float(statistic(data))

    null_vals = np.empty(n_perms, dtype=np.float64)
    for i in range(n_perms):
        shuffled = data.copy()
        shuffled[shuffle_col] = rng.permutation(shuffled[shuffle_col].values)
        null_vals[i] = float(statistic(shuffled))

    null_mean = float(np.mean(null_vals))
    null_std = float(np.std(null_vals, ddof=1)) if n_perms > 1 else 0.0
    null_p99 = float(np.percentile(null_vals, 99))

    if null_std < 1e-12:
        z_score = float("inf") if observed != null_mean else 0.0
    else:
        z_score = (observed - null_mean) / null_std

    verdict = "DURABLE" if abs(z_score) >= 3.0 else "COLLAPSES"

    return {
        "null_mean": null_mean,
        "null_std": null_std,
        "null_p99": null_p99,
        "observed": observed,
        "z_score": round(float(z_score), 2),
        "verdict": verdict,
        "n_perms": n_perms,
        "seed": seed,
    }
