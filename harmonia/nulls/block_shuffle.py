"""NULL_BSWCD@v1 reference implementation.

Block-Shuffle Within <Stratifier> Decile null. The promoted symbol's
pinned defaults are (n_bins=10, n_perms=300, seed=20260417) with
stratifier=conductor. This module implements the operator so every
future audit can call it identically.

Spec: harmonia/memory/symbols/NULL_BSWCD.md (v1, promoted 2026-04-18).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
import pandas as pd


def _default_statistic(data: pd.DataFrame) -> float:
    """Default statistic: mean of `value`. Override for real audits."""
    return float(np.mean(data["value"].values))


def bswcd_null(
    data: pd.DataFrame,
    stratifier: str = "conductor",
    n_bins: int = 10,
    n_perms: int = 300,
    seed: int = 20260417,
    statistic: Optional[Callable[[pd.DataFrame], float]] = None,
    shuffle_col: str = "value",
) -> dict:
    """NULL_BSWCD@v1.

    Parameters
    ----------
    data : DataFrame with the stratifier column and a shuffle column.
    stratifier : name of the column to decile-bin (e.g., "conductor",
        "rank", "num_bad_primes", "torsion_order"). If the column is
        already integer-coded and discrete, pass `n_bins` as the number
        of distinct classes; bin boundaries are computed from the
        stratifier's quantiles.
    n_bins : number of strata (default 10 per v1 pin).
    n_perms : number of permutations (default 300 per v1 pin).
    seed : RNG seed (default 20260417 per v1 pin).
    statistic : callable(data) -> float. Computed on observed + every
        shuffled dataset. Defaults to `mean(data['value'])` but should
        be set to the audit-specific statistic (slope, R^2, etc.).
    shuffle_col : column permuted within each stratum. Default "value".

    Returns
    -------
    dict with:
        null_mean, null_std, null_p99  (4 sig figs meaningful)
        observed                       (the statistic on the original)
        z_score                        (2 decimal places meaningful)
        verdict                        ("DURABLE" or "COLLAPSES")
        n_strata_used                  (after duplicates='drop')
        stratifier, n_bins, n_perms, seed  (echoed for audit trail)
    """
    if statistic is None:
        statistic = _default_statistic

    rng = np.random.default_rng(seed)

    if stratifier not in data.columns:
        raise ValueError(f"stratifier column '{stratifier}' missing from data")
    if shuffle_col not in data.columns:
        raise ValueError(f"shuffle_col '{shuffle_col}' missing from data")

    # qcut with duplicates='drop' silently reduces n_bins if the
    # stratifier has too many ties. Track the actual stratum count.
    try:
        deciles = pd.qcut(
            data[stratifier], q=n_bins, labels=False, duplicates="drop"
        )
    except ValueError:
        # Fall back to categorical stratification (already-discrete column)
        deciles = pd.Categorical(data[stratifier]).codes
    n_strata_used = int(pd.Series(deciles).nunique())

    observed = float(statistic(data))

    # Degeneracy guard: warn if any stratum dominates (Pattern 26).
    stratum_sizes = pd.Series(deciles).value_counts(normalize=True)
    max_share = float(stratum_sizes.max())
    degenerate_warning = None
    if max_share > 0.20:
        degenerate_warning = (
            f"Dominant stratum holds {max_share:.1%} of data — "
            "Pattern 26 flags stratifiers where >20% concentrates; "
            "consider a different confound."
        )

    null_vals = np.empty(n_perms, dtype=np.float64)
    for i in range(n_perms):
        shuffled = data.copy()
        vals = shuffled[shuffle_col].values.copy()
        for d in np.unique(deciles):
            mask = (deciles == d).to_numpy() if hasattr(deciles, "to_numpy") else (deciles == d)
            idx = np.where(mask)[0]
            vals[idx] = rng.permutation(vals[idx])
        shuffled[shuffle_col] = vals
        null_vals[i] = float(statistic(shuffled))

    null_mean = float(np.mean(null_vals))
    null_std = float(np.std(null_vals, ddof=1)) if n_perms > 1 else 0.0
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
        "n_perms": n_perms,
        "seed": seed,
    }
    if degenerate_warning is not None:
        out["degeneracy_warning"] = degenerate_warning
    return out


def bswcd_signature(
    feature_id: str,
    projection_ids: list,
    result: dict,
    n_samples: int,
    dataset_spec: str,
    commit: str,
    worker: str,
    timestamp: str,
    effect_size: Optional[float] = None,
) -> dict:
    """Build a SIGNATURE@v1 dict from a bswcd_null result.

    The null_spec string is in the standard NULL_BSWCD@v1[...] form
    so reproducibility_hash has deterministic input.
    """
    import hashlib
    import json

    null_spec = (
        f"NULL_BSWCD@v1[stratifier={result['stratifier']},"
        f"n_bins={result['n_bins']},"
        f"n_perms={result['n_perms']},"
        f"seed={result['seed']}]"
    )

    sig = {
        "feature_id": feature_id,
        "projection_ids": projection_ids,
        "null_spec": null_spec,
        "dataset_spec": dataset_spec,
        "n_samples": int(n_samples),
        "effect_size": float(effect_size) if effect_size is not None else float(result["observed"]),
        "z_score": float(result["z_score"]),
        "precision": {
            "effect_size": "4 sig figs",
            "z_score": "2 decimal places",
            "n_samples": "exact",
        },
        "commit": commit,
        "worker": worker,
        "timestamp": timestamp,
    }
    hashable = json.dumps(
        {k: sig[k] for k in sorted(sig) if k != "reproducibility_hash"},
        sort_keys=True,
        default=str,
    )
    sig["reproducibility_hash"] = hashlib.sha256(hashable.encode()).hexdigest()
    sig["bswcd_full_result"] = result
    return sig
