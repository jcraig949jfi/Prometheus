"""NULL_FRAME@v1 scaffold.

Frame-based resample null for construction-biased samples (Class 4 per
null_protocol_v1.md). This is a scaffold: real-world use requires a
per-frame `resampler` callable that encodes the inverted bias.

Spec: harmonia/memory/symbols/NULL_FRAME.md (v1, promoted 2026-04-20).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
import pandas as pd


def frame_null(
    data: pd.DataFrame,
    frame: str,
    resampler: Callable,
    n_perms: int = 300,
    seed: int = 20260420,
    statistic: Optional[Callable] = None,
) -> dict:
    """NULL_FRAME@v1.

    Parameters
    ----------
    data : the observed construction-biased sample
    frame : named frame, e.g. "lmfdb_r4", "lmfdb_r0_d5"
    resampler : callable(frame_name, rng) -> DataFrame — generates a
        single draw from the unbiased frame.
    n_perms : number of resamples.
    seed : RNG seed.
    statistic : callable(data) -> float. Default: mean(data['value']).

    Returns
    -------
    dict with null_mean, null_std, null_p99, observed, z_score, verdict,
    frame, n_perms, seed, frame_applicability.
    """
    if not frame:
        raise ValueError("NULL_FRAME@v1 requires an explicit `frame` argument")
    if resampler is None:
        raise ValueError("NULL_FRAME@v1 requires a `resampler` callable")
    if statistic is None:
        def statistic(df: pd.DataFrame) -> float:
            return float(np.mean(df["value"].values))

    rng = np.random.default_rng(seed)
    observed = float(statistic(data))

    null_vals = np.empty(n_perms, dtype=np.float64)
    for i in range(n_perms):
        draw = resampler(frame, rng)
        null_vals[i] = float(statistic(draw))

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
        "frame": frame,
        "n_perms": n_perms,
        "seed": seed,
        "frame_applicability": "class_4",
    }
