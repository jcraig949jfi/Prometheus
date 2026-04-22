"""NULL_MODEL@v1 scaffold.

Parametric-model null. Generates synthetic statistic samples from a
specified probability model (GUE, Poisson, KS_U, ...); observed is
compared to the model distribution.

Important semantics: DURABLE under NULL_MODEL means the data rejects
the model, which may be either signal OR model-mismatch; the conductor
disambiguates.

Spec: harmonia/memory/symbols/NULL_MODEL.md (v1, promoted 2026-04-20).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np


def model_null(
    observed_statistic: float,
    model: str,
    model_params: dict,
    n_samples: int = 10000,
    seed: int = 20260420,
    statistic_sampler: Optional[Callable] = None,
) -> dict:
    """NULL_MODEL@v1.

    Parameters
    ----------
    observed_statistic : float computed from observed data (pre-supplied
        since the statistic is model-specific and the sampler returns
        model-native draws).
    model : named model, e.g. "GUE", "Poisson", "KS_U".
    model_params : dict of model-specific parameters (e.g.,
        {"degree": 2, "n_zeros": 30} for GUE L-function first-gap).
    n_samples : number of synthetic draws.
    seed : RNG seed.
    statistic_sampler : callable(model_params, rng) -> float. Must be
        supplied per model.

    Returns
    -------
    dict with null_mean, null_std, null_p99, observed, z_score, verdict,
    model, model_params, n_samples, seed.
    """
    if not model:
        raise ValueError("NULL_MODEL@v1 requires a `model` argument")
    if statistic_sampler is None:
        raise ValueError(
            "NULL_MODEL@v1 requires a `statistic_sampler` callable; "
            "per-model samplers live in harmonia/nulls/models/"
        )

    rng = np.random.default_rng(seed)
    observed = float(observed_statistic)

    null_vals = np.empty(n_samples, dtype=np.float64)
    for i in range(n_samples):
        null_vals[i] = float(statistic_sampler(model_params, rng))

    null_mean = float(np.mean(null_vals))
    null_std = float(np.std(null_vals, ddof=1)) if n_samples > 1 else 0.0
    null_p99 = float(np.percentile(null_vals, 99))

    if null_std < 1e-12:
        z_score = float("inf") if observed != null_mean else 0.0
    else:
        z_score = (observed - null_mean) / null_std

    # Under NULL_MODEL, "DURABLE" means observed rejects the model.
    verdict = "DURABLE" if abs(z_score) >= 3.0 else "COLLAPSES"

    return {
        "null_mean": null_mean,
        "null_std": null_std,
        "null_p99": null_p99,
        "observed": observed,
        "z_score": round(float(z_score), 2),
        "verdict": verdict,
        "model": model,
        "model_params": dict(model_params),
        "n_samples": n_samples,
        "seed": seed,
    }
