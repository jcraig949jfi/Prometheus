"""NULL_BOOT@v1 reference implementation.

Stratified bootstrap-with-replacement null. Preserves stratifier
marginal; tests sample-variance stability of the statistic. Family
member in gen_02 null-family.

Spec: harmonia/memory/symbols/NULL_BOOT.md (v1, promoted 2026-04-20).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
import pandas as pd


def _default_statistic(data: pd.DataFrame) -> float:
    return float(np.mean(data["value"].values))


def boot_null(
    data: pd.DataFrame,
    stratifier: str = "conductor",
    n_bins: int = 10,
    n_boot: int = 1000,
    seed: int = 20260420,
    statistic: Optional[Callable[[pd.DataFrame], float]] = None,
) -> dict:
    """NULL_BOOT@v1.

    Stratified bootstrap resample: for each draw, resample rows with
    replacement *within each stratum*, preserving stratum cardinality.
    """
    if statistic is None:
        statistic = _default_statistic

    if stratifier not in data.columns:
        raise ValueError(f"stratifier column '{stratifier}' missing from data")

    rng = np.random.default_rng(seed)

    try:
        deciles = pd.qcut(
            data[stratifier], q=n_bins, labels=False, duplicates="drop"
        )
    except ValueError:
        deciles = pd.Categorical(data[stratifier]).codes
    n_strata_used = int(pd.Series(deciles).nunique())

    observed = float(statistic(data))

    stratum_sizes = pd.Series(deciles).value_counts(normalize=True)
    max_share = float(stratum_sizes.max())
    degenerate_warning = None
    if max_share > 0.20:
        degenerate_warning = (
            f"Dominant stratum holds {max_share:.1%} of data — "
            "Pattern 26 flags stratifiers where >20% concentrates; "
            "consider a different confound."
        )

    # Pre-compute per-stratum row index lists for fast resampling.
    deciles_arr = (
        deciles.to_numpy() if hasattr(deciles, "to_numpy") else np.asarray(deciles)
    )
    strata_idx = {d: np.where(deciles_arr == d)[0] for d in np.unique(deciles_arr)}

    null_vals = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        pieces = []
        for d, idx in strata_idx.items():
            resampled = rng.choice(idx, size=len(idx), replace=True)
            pieces.append(resampled)
        all_idx = np.concatenate(pieces)
        draw = data.iloc[all_idx]
        null_vals[i] = float(statistic(draw))

    null_mean = float(np.mean(null_vals))
    null_std = float(np.std(null_vals, ddof=1)) if n_boot > 1 else 0.0
    null_p99 = float(np.percentile(null_vals, 99))

    if null_std < 1e-12:
        z_score = float("inf") if observed != null_mean else 0.0
    else:
        z_score = (observed - null_mean) / null_std

    verdict = "DURABLE" if abs(z_score) >= 3.0 else "COLLAPSES"

    out = {
        "null_mean": null_mean,
        "null_std": null_std,
        "null_p99": null_p99,
        "observed": observed,
        "z_score": round(float(z_score), 2),
        "verdict": verdict,
        "n_strata_used": n_strata_used,
        "stratifier": stratifier,
        "n_bins": n_bins,
        "n_boot": n_boot,
        "seed": seed,
    }
    if degenerate_warning is not None:
        out["degeneracy_warning"] = degenerate_warning
    return out
