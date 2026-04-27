"""TAIL_VS_BULK_DECOMPOSITION - spectral tail/bulk audit operator.

``decompose_spectral`` splits a spectral signal by coordinate tail, applies a
small battery contract independently to tail-only and bulk-only components, and
reports whether both regions tell the same story.

The built-in battery is intentionally modest until a substrate-wide
``battery_apply`` callable is exposed. Contract for a future callable:

    battery(signal: np.ndarray, mask: np.ndarray, rng: np.random.Generator,
            n_perms: int) -> dict

It should return ``{'effect_size': float, 'p_value': float,
'pattern_flags': list[str]}``.

Forged: 2026-04-26 | Tier: 1 | REQ-031
"""
from __future__ import annotations

from typing import Callable

import numpy as np


BatteryCallable = Callable[[np.ndarray, np.ndarray, np.random.Generator, int], dict]


def _threshold(signal: np.ndarray, tail_threshold: float | str) -> float:
    if tail_threshold == "auto":
        return 0.95
    if isinstance(tail_threshold, str):
        raise ValueError("tail_threshold must be 'auto' or a float")
    threshold = float(tail_threshold)
    if threshold > 1.0:
        # Treat as a raw flattened index threshold for callers with explicit
        # spectral-coordinate cutoffs.
        return threshold / max(signal.size, 1)
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("tail_threshold float must be in [0, 1] or a raw positive index")
    return threshold


def _masks(signal: np.ndarray, threshold: float) -> tuple[np.ndarray, np.ndarray]:
    flat_n = signal.size
    coords = (np.arange(flat_n, dtype=float) + 0.5) / max(flat_n, 1)
    tail = coords >= threshold
    if flat_n and not np.any(tail):
        tail[-1] = True
    bulk = ~tail
    return tail.reshape(signal.shape), bulk.reshape(signal.shape)


def _default_battery(
    signal: np.ndarray,
    mask: np.ndarray,
    rng: np.random.Generator,
    n_perms: int,
) -> dict:
    values = np.asarray(signal[mask], dtype=float)
    if values.size == 0:
        return {"effect_size": 0.0, "p_value": 1.0, "pattern_flags": ["EMPTY_SEGMENT"]}

    observed = float(abs(values.mean()) / max(values.std(ddof=0), 1e-12))
    if not np.isfinite(observed):
        observed = 0.0

    if n_perms <= 0:
        p_value = float("nan")
    else:
        centered = values - values.mean()
        null = []
        for _ in range(n_perms):
            signs = rng.choice(np.array([-1.0, 1.0]), size=values.size)
            sample = centered * signs
            null.append(abs(sample.mean()) / max(sample.std(ddof=0), 1e-12))
        null_arr = np.asarray(null, dtype=float)
        p_value = float((np.count_nonzero(null_arr >= observed) + 1) / (len(null_arr) + 1))

    flags: list[str] = []
    if observed >= 1.0 and (np.isnan(p_value) or p_value <= 0.05):
        flags.append("PROMOTE_SEGMENT_SIGNAL")
    else:
        flags.append("NO_SEGMENT_SIGNAL")
    return {"effect_size": observed, "p_value": p_value, "pattern_flags": flags}


def _battery_apply(
    signal: np.ndarray,
    mask: np.ndarray,
    battery: BatteryCallable | None,
    rng: np.random.Generator,
    n_perms: int,
) -> dict:
    if battery is None:
        result = _default_battery(signal, mask, rng, n_perms)
    else:
        result = battery(signal, mask, rng, n_perms)
    return {
        "effect_size": float(result.get("effect_size", 0.0)),
        "p_value": float(result.get("p_value", 1.0)),
        "pattern_flags": list(result.get("pattern_flags", [])),
    }


def _agreement(tail_scores: dict, bulk_scores: dict) -> float:
    tail_promotes = "PROMOTE_SEGMENT_SIGNAL" in tail_scores.get("pattern_flags", [])
    bulk_promotes = "PROMOTE_SEGMENT_SIGNAL" in bulk_scores.get("pattern_flags", [])
    if tail_promotes == bulk_promotes:
        effect_gap = abs(tail_scores["effect_size"] - bulk_scores["effect_size"])
        scale = max(tail_scores["effect_size"], bulk_scores["effect_size"], 1.0)
        return float(np.clip(1.0 - effect_gap / scale, 0.0, 1.0))
    return 0.0


def decompose_spectral(
    spectral_signal: np.ndarray,
    tail_threshold: float | str = "auto",
    null_model: BatteryCallable | None = None,
    n_perms: int = 300,
    seed: int = 20260417,
) -> dict:
    """Decompose a spectral signal into coordinate-tail and bulk components."""
    signal = np.asarray(spectral_signal, dtype=float)
    if signal.size == 0:
        raise ValueError("spectral_signal must be non-empty")
    if not np.all(np.isfinite(signal)):
        raise ValueError("spectral_signal must contain only finite values")
    if n_perms < 0:
        raise ValueError("n_perms must be non-negative")

    threshold = _threshold(signal, tail_threshold)
    tail_mask, bulk_mask = _masks(signal, threshold)
    tail_signal = np.where(tail_mask, signal, 0.0)
    bulk_signal = np.where(bulk_mask, signal, 0.0)

    rng_tail = np.random.default_rng(seed)
    rng_bulk = np.random.default_rng(seed + 1)
    tail_scores = _battery_apply(signal, tail_mask, null_model, rng_tail, n_perms)
    bulk_scores = _battery_apply(signal, bulk_mask, null_model, rng_bulk, n_perms)

    return {
        "tail_signal": tail_signal,
        "bulk_signal": bulk_signal,
        "tail_battery_scores": tail_scores,
        "bulk_battery_scores": bulk_scores,
        "agreement_score": _agreement(tail_scores, bulk_scores),
        "audit": {
            "tail_threshold_used": float(threshold),
            "tail_fraction": float(np.count_nonzero(tail_mask) / signal.size),
            "bulk_fraction": float(np.count_nonzero(bulk_mask) / signal.size),
            "null_p_tail": tail_scores["p_value"],
            "null_p_bulk": bulk_scores["p_value"],
            "null_perms_run": int(n_perms),
            "null_seed": int(seed),
            "battery_contract": "callable(signal, mask, rng, n_perms) -> {effect_size, p_value, pattern_flags}",
        },
    }


__all__ = ["decompose_spectral"]
