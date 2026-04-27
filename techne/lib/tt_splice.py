"""TOOL_TT_SPLICE - cross-region TT bond-rank compatibility analyzer.

The public entry point is ``tt_splice_compatibility``. It loads two NPZ-backed
tensors, optionally removes leading-axis log-prime-density structure, computes
independent and joint TT-SVD bond ranks, and calibrates the observed splice
score against a permutation null.

Forged: 2026-04-26 | Tier: 1 | REQ-027
Backends: numpy + scipy.linalg.svd. TensorLy is optional; this module keeps a
hand-rolled SVD cascade so the result is stable across tensorly API changes.
"""
from __future__ import annotations

from pathlib import Path
import math
import warnings

import numpy as np
from scipy.linalg import svd


PATTERN_WARNING = (
    "PATTERN_PRIME_GRAVITATIONAL_OVERFIT: prime_detrend=False leaves TT "
    "bond-rank claims vulnerable to prime-density structure."
)

_ENERGY = 0.995
_EPS = 1e-12


def _load_npz_tensor(path: Path) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    with np.load(path, allow_pickle=False) as data:
        if "data" in data.files:
            arr = data["data"]
        else:
            arrays = [name for name in data.files if getattr(data[name], "ndim", 0) >= 2]
            if not arrays:
                raise ValueError(f"{path} contains no numeric array with ndim >= 2")
            arr = data[arrays[0]]
    arr = np.asarray(arr, dtype=float)
    if arr.ndim < 2:
        raise ValueError(f"{path} tensor must have ndim >= 2, got shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{path} contains NaN or infinite values")
    return arr


def _effective_rank_from_singular_values(s: np.ndarray, energy: float = _ENERGY) -> int:
    if s.size == 0:
        return 0
    power = s * s
    total = float(power.sum())
    if total <= _EPS:
        return 0
    return int(np.searchsorted(np.cumsum(power) / total, energy) + 1)


def _unfolding(tensor: np.ndarray, split_axis: int) -> np.ndarray:
    left = int(np.prod(tensor.shape[:split_axis], dtype=np.int64))
    right = int(np.prod(tensor.shape[split_axis:], dtype=np.int64))
    return tensor.reshape(left, right)


def _tt_bond_ranks(tensor: np.ndarray) -> list[int]:
    ranks: list[int] = []
    for split_axis in range(1, tensor.ndim):
        mat = _unfolding(tensor, split_axis)
        s = svd(mat, compute_uv=False, check_finite=False)
        ranks.append(_effective_rank_from_singular_values(s))
    return ranks


def _leading_subspace(mat: np.ndarray, rank: int) -> np.ndarray:
    if rank <= 0:
        return np.zeros((mat.shape[1], 0))
    _, _, vh = svd(mat, full_matrices=False, check_finite=False)
    r = min(rank, vh.shape[0])
    return vh[:r].T


def _subspace_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape[1] == 0 and b.shape[1] == 0:
        return 1.0
    if a.shape[1] == 0 or b.shape[1] == 0:
        return 0.0
    overlap = svd(a.T @ b, compute_uv=False, check_finite=False)
    denom = math.sqrt(a.shape[1] * b.shape[1])
    return float(np.clip(np.linalg.norm(overlap) / max(denom, _EPS), 0.0, 1.0))


def _shape_pair(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if a.shape == b.shape:
        return a, b
    common = tuple(min(sa, sb) for sa, sb in zip(a.shape, b.shape))
    if len(a.shape) != len(b.shape) or any(dim < 2 for dim in common):
        raise ValueError(f"tensor shapes are not splice-compatible: {a.shape} vs {b.shape}")
    slices = tuple(slice(0, dim) for dim in common)
    return a[slices], b[slices]


def _prime_density_residual(n: int) -> np.ndarray:
    if n <= 1:
        return np.zeros(n, dtype=float)
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False
    for p in range(2, int(math.sqrt(n)) + 1):
        if is_prime[p]:
            is_prime[p * p:n + 1:p] = False
    idx = np.arange(1, n + 1, dtype=float)
    observed = np.cumsum(is_prime[1:].astype(float)) / idx
    expected = 1.0 / np.maximum(np.log(idx + 1.0), _EPS)
    residual = observed - expected
    residual = np.sign(residual) * np.log1p(np.abs(residual))
    residual -= residual.mean()
    std = residual.std()
    if std > _EPS:
        residual /= std
    return residual


def _prime_magnitude(tensor: np.ndarray, residual: np.ndarray) -> dict:
    rows = tensor.reshape(tensor.shape[0], -1)
    row_signal = rows.mean(axis=1)
    corr = 0.0
    if residual.std() > _EPS and row_signal.std() > _EPS:
        corr = float(np.corrcoef(residual, row_signal)[0, 1])
    beta = float(np.dot(residual, row_signal) / max(np.dot(residual, residual), _EPS))
    return {
        "fro_norm": float(np.linalg.norm(tensor)),
        "leading_axis_prime_corr": corr,
        "leading_axis_prime_beta": beta,
    }


def _detrend_prime(tensor: np.ndarray, residual: np.ndarray) -> np.ndarray:
    rows = tensor.reshape(tensor.shape[0], -1)
    design = np.column_stack([np.ones(tensor.shape[0]), residual])
    coeffs, *_ = np.linalg.lstsq(design, rows, rcond=None)
    fitted_prime = np.outer(residual, coeffs[1])
    return (rows - fitted_prime).reshape(tensor.shape)


def _joint_tensor(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.concatenate([a, b], axis=0)


def _rank_excess_score(independent_a: list[int], independent_b: list[int], joint: list[int]) -> float:
    scores = []
    for ra, rb, rj in zip(independent_a, independent_b, joint):
        geom = math.sqrt(max(ra, 0) * max(rb, 0))
        if geom <= _EPS:
            scores.append(1.0 if rj == 0 else 0.0)
        else:
            scores.append(float(np.clip(geom / max(rj, _EPS), 0.0, 1.0)))
    return float(np.mean(scores)) if scores else 1.0


def _splice_score(a: np.ndarray, b: np.ndarray) -> tuple[float, list[int], dict]:
    ranks_a = _tt_bond_ranks(a)
    ranks_b = _tt_bond_ranks(b)
    joint = _tt_bond_ranks(_joint_tensor(a, b))

    subspace_scores = []
    for split_axis, (ra, rb) in enumerate(zip(ranks_a, ranks_b), start=1):
        ma = _unfolding(a, split_axis)
        mb = _unfolding(b, split_axis)
        target_rank = max(1, min(ra, rb))
        subspace_scores.append(_subspace_similarity(
            _leading_subspace(ma, target_rank),
            _leading_subspace(mb, target_rank),
        ))

    subspace_score = float(np.mean(subspace_scores)) if subspace_scores else 1.0
    rank_score = _rank_excess_score(ranks_a, ranks_b, joint)
    score = float(np.clip(subspace_score * rank_score, 0.0, 1.0))
    detail = {
        "independent_bond_ranks_a": ranks_a,
        "independent_bond_ranks_b": ranks_b,
        "rank_compression_score": rank_score,
        "subspace_alignment_score": subspace_score,
    }
    return score, joint, detail


def _operators_from_score(score: float, ranks: list[int]) -> list[str]:
    operators: list[str] = []
    if score >= 0.95:
        operators.append("IDENTITY_SELF_SPLICE")
    if score >= 0.7:
        operators.append("LOW_RANK_SHARED_FACTOR")
    if ranks and min(ranks) <= 2:
        operators.append("RANK_2_BOND")
    if score < 0.2:
        operators.append("NO_STABLE_OPERATOR")
    return operators


def tt_splice_compatibility(
    region_a_npz: Path,
    region_b_npz: Path,
    prime_detrend: bool = True,
    null_perms: int = 300,
    seed: int = 20260417,
) -> dict:
    """Measure TT splice compatibility between two NPZ-backed region tensors."""
    if null_perms < 0:
        raise ValueError("null_perms must be non-negative")

    region_a, region_b = _shape_pair(_load_npz_tensor(region_a_npz), _load_npz_tensor(region_b_npz))
    residual = _prime_density_residual(region_a.shape[0])

    pre = {
        "region_a": _prime_magnitude(region_a, residual),
        "region_b": _prime_magnitude(region_b, residual),
    }

    if prime_detrend:
        work_a = _detrend_prime(region_a, residual)
        work_b = _detrend_prime(region_b, residual)
    else:
        warnings.warn(PATTERN_WARNING, RuntimeWarning, stacklevel=2)
        work_a = region_a.copy()
        work_b = region_b.copy()

    post = {
        "region_a": _prime_magnitude(work_a, residual),
        "region_b": _prime_magnitude(work_b, residual),
    }

    if np.allclose(work_a, work_b, rtol=1e-10, atol=1e-10):
        _, bond_ranks, detail = _splice_score(work_a, work_b)
        observed = 1.0
        detail["identity_splice"] = True
    else:
        observed, bond_ranks, detail = _splice_score(work_a, work_b)
        detail["identity_splice"] = False

    rng = np.random.default_rng(seed)
    null_scores: list[float] = []
    for _ in range(null_perms):
        permuted = work_b[rng.permutation(work_b.shape[0])]
        score, _, _ = _splice_score(work_a, permuted)
        null_scores.append(score)

    if null_scores:
        null_arr = np.asarray(null_scores, dtype=float)
        p_value = float((np.count_nonzero(null_arr >= observed) + 1) / (len(null_arr) + 1))
        null_summary = {
            "mean": float(null_arr.mean()),
            "std": float(null_arr.std()),
            "max": float(null_arr.max()),
        }
    else:
        p_value = float("nan")
        null_summary = {"mean": float("nan"), "std": float("nan"), "max": float("nan")}

    audit = {
        "prime_detrend_applied": bool(prime_detrend),
        "pre_detrend_magnitudes": pre,
        "post_detrend_magnitudes": post,
        "null_perms_run": int(null_perms),
        "null_seed": int(seed),
        "null_p_value": p_value,
        "null_score_summary": null_summary,
        **detail,
    }

    return {
        "bond_ranks": [int(r) for r in bond_ranks],
        "compatibility_score": observed,
        "bridge_operators": _operators_from_score(observed, bond_ranks),
        "audit": audit,
    }


__all__ = ["tt_splice_compatibility", "PATTERN_WARNING"]
