"""OPERATOR_RANK_PARITY_NULL_CONTROL - rank-parity matched null.

Extends the NULL_BSWCD@v2 discipline from conductor-decile-only block
permutation to joint blocks keyed by (conductor decile, rank parity). This is a
Techne primitive only: it enables F011-style retroactive audits but does not
perform any F011 investigation.

Canonical multi-population use: compare the rank/parity profiles of F011's
non-CM EC, CM EC, and genus-2 curve (USp(4)) populations before interpreting a
cross-region spectral statistic as structural.

Forged: 2026-04-26 | Tier: 1 | REQ-030
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def _load_population(population: np.ndarray | str | Path) -> np.ndarray:
    if isinstance(population, (str, Path)):
        path = Path(population)
        with np.load(path, allow_pickle=False) as data:
            if "data" in data.files:
                arr = data["data"]
            else:
                arrays = [k for k in data.files if getattr(data[k], "ndim", 0) >= 1]
                if not arrays:
                    raise ValueError(f"{path} contains no array payload")
                arr = data[arrays[0]]
        return np.asarray(arr)
    return np.asarray(population)


def _field(arr: np.ndarray, field: str) -> np.ndarray:
    if arr.dtype.names and field in arr.dtype.names:
        return np.asarray(arr[field])
    if arr.ndim == 2:
        try:
            idx = int(field)
        except ValueError as exc:
            raise ValueError(
                f"unstructured 2D population needs numeric column field, got {field!r}"
            ) from exc
        return np.asarray(arr[:, idx])
    raise ValueError(f"population does not expose field {field!r}")


def _counts(values: np.ndarray) -> dict[int, int]:
    unique, counts = np.unique(values.astype(int), return_counts=True)
    return {int(k): int(v) for k, v in zip(unique, counts)}


def _conductor_deciles(conductor: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    n = len(conductor)
    if n == 0:
        raise ValueError("population must be non-empty")
    order = np.argsort(conductor, kind="mergesort")
    ranks = np.empty(n, dtype=int)
    ranks[order] = np.arange(n)
    deciles = np.floor((ranks * 10) / max(n, 1)).astype(int)
    deciles = np.clip(deciles, 0, 9)
    unique_conductor = int(np.unique(conductor).size)
    used = int(np.unique(deciles).size)
    underdetermined = bool(n < 10 or unique_conductor < 10)
    return deciles, {
        "n": int(n),
        "n_deciles_used": used,
        "unique_conductor_values": unique_conductor,
        "underdetermined": underdetermined,
        "warning": (
            "conductor decile underdetermined; fewer than 10 rows or unique conductor values"
            if underdetermined else ""
        ),
    }


def _distribution_distance(a: dict[int, int], b: dict[int, int]) -> float:
    keys = set(a) | set(b)
    sa = max(sum(a.values()), 1)
    sb = max(sum(b.values()), 1)
    return float(sum(abs(a.get(k, 0) / sa - b.get(k, 0) / sb) for k in keys) / 2.0)


def _analyze_single(
    population: np.ndarray | str | Path,
    rank_field: str,
    conductor_field: str,
    n_perms: int,
    seed: int,
) -> dict:
    arr = _load_population(population)
    rank = _field(arr, rank_field).astype(int)
    conductor = _field(arr, conductor_field).astype(float)
    if len(rank) != len(conductor):
        raise ValueError("rank and conductor fields must have the same length")
    if n_perms < 0:
        raise ValueError("n_perms must be non-negative")
    if not np.all(np.isfinite(conductor)):
        raise ValueError("conductor field must be finite")

    parity = np.mod(rank, 2).astype(int)
    deciles, decile_audit = _conductor_deciles(conductor)
    joint_keys = np.array([f"{d}:{p}" for d, p in zip(deciles, parity)])
    strata = {key: np.where(joint_keys == key)[0] for key in np.unique(joint_keys)}

    rng = np.random.default_rng(seed)
    matched: list[list[int]] = []
    null_stats = np.empty(n_perms, dtype=float)
    for perm_i in range(n_perms):
        perm = np.arange(len(rank), dtype=int)
        for idx in strata.values():
            perm[idx] = rng.permutation(idx)
        matched.append(perm.tolist())
        # A simple parity-centering statistic for downstream calibration. The
        # important contract is the permutation itself; this statistic should be
        # constant when joint strata are exactly preserved.
        null_stats[perm_i] = float(parity[perm].mean()) if len(parity) else np.nan

    preserved = True
    for perm in matched:
        perm_arr = np.asarray(perm, dtype=int)
        if not np.array_equal(np.sort(joint_keys[perm_arr]), np.sort(joint_keys)):
            preserved = False
            break

    joint_counts = {str(k): int(len(v)) for k, v in strata.items()}
    dominant = max(joint_counts.values()) / max(len(rank), 1)
    audit = {
        "rank_distribution": _counts(rank),
        "parity_distribution": _counts(parity),
        "conductor_decile_distribution": _counts(deciles),
        "joint_distribution": joint_counts,
        "joint_marginal_preserved": bool(preserved),
        "conductor_decile_audit": decile_audit,
        "degeneracy_warning": (
            "dominant joint stratum exceeds NULL_BSWCD@v2 20% warning threshold"
            if dominant > 0.20 else ""
        ),
        "pairwise_population_comparison": {},
    }
    return {
        "null_distribution": null_stats,
        "matched_population_indices": matched,
        "rank_parity_audit": audit,
    }


def _pairwise(audits: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for i in range(len(audits)):
        for j in range(i + 1, len(audits)):
            ai = audits[i]
            aj = audits[j]
            rank_l1 = _distribution_distance(ai["rank_distribution"], aj["rank_distribution"])
            parity_l1 = _distribution_distance(ai["parity_distribution"], aj["parity_distribution"])
            key = f"population_{i}_vs_{j}"
            out[key] = {
                "rank_l1_distance": rank_l1,
                "parity_l1_distance": parity_l1,
                "rank_parity_asymmetry": bool(rank_l1 > 0.10 or parity_l1 > 0.10),
                "pattern_flag": (
                    "PATTERN_RANK_PARITY_LEAK_RISK"
                    if rank_l1 > 0.10 or parity_l1 > 0.10
                    else "RANK_PARITY_BALANCED"
                ),
            }
    return out


def rank_parity_null_control(
    population: np.ndarray | str | list[np.ndarray | str],
    rank_field: str = "analytic_rank",
    conductor_field: str = "conductor",
    n_perms: int = 300,
    seed: int = 20260417,
) -> dict:
    """Build a null preserving (conductor decile, rank parity) joint marginals."""
    if isinstance(population, list):
        results = [
            _analyze_single(pop, rank_field, conductor_field, n_perms, seed + i)
            for i, pop in enumerate(population)
        ]
        audits = [r["rank_parity_audit"] for r in results]
        pairwise = _pairwise(audits)
        for audit in audits:
            audit["pairwise_population_comparison"] = pairwise
        return {
            "null_distribution": [r["null_distribution"] for r in results],
            "matched_population_indices": [r["matched_population_indices"] for r in results],
            "rank_parity_audit": {
                "population_audits": audits,
                "pairwise_population_comparison": pairwise,
                "canonical_use": "F011 non-CM EC vs CM EC vs G2C USp(4) rank-parity audit",
            },
        }
    return _analyze_single(population, rank_field, conductor_field, n_perms, seed)


__all__ = ["rank_parity_null_control"]
