"""Decomposition lineage: the Pattern-30 analog for the function zoo.

Two failure modes this catches:

(1) Pairwise algebraic coupling: two functions whose dense tensors are
    nearly collinear. Their archive entries are not independent — the
    map's apparent "two regions" is one region observed twice.

(2) Span coupling: a target function lies in the linear span of a candidate
    basis. Archive entries are not independent in a higher-dimensional sense.
    Mirrors F043's failure mode (BSD identity rearrangement) — there the
    coupling was algebraic-definitional; here it is linear-decompositional.

The infrastructure is in place even when current zoo members are unrelated;
adding a new function calls into the same check before it joins the run.
"""
from __future__ import annotations
import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a.ravel(), b.ravel()) / (na * nb))


def pairwise_function_correlations(samples: dict[str, np.ndarray],
                                   threshold: float = 0.9) -> dict:
    """Cosine similarity between flattened function tensors. Pairs with
    |cos| > threshold are flagged as algebraically coupled.
    """
    labels = list(samples.keys())
    matrix: dict[str, float] = {}
    flags: list[dict] = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            c = cosine(samples[a], samples[b])
            matrix[f"{a}|{b}"] = c
            if abs(c) > threshold:
                flags.append({
                    "pair": [a, b],
                    "cosine": c,
                    "verdict": "ALGEBRAICALLY_COUPLED",
                    "implication": "archive entries for these are not independent",
                })
    return {"matrix": matrix, "flags": flags, "threshold": threshold}


def residual_decomposition(target: np.ndarray, basis: dict[str, np.ndarray],
                           r2_threshold: float = 0.95) -> dict:
    """Solve target ~ sum_j alpha_j * basis_j via least squares. If R^2 above
    threshold, target is in the basis span and any archive measurement on
    target is structurally derivable from measurements on the basis."""
    if not basis:
        return {"r_squared": 0.0, "coeffs": {}, "in_span": False, "verdict": "NO_BASIS"}
    labels = list(basis.keys())
    B = np.column_stack([basis[k].ravel() for k in labels])
    t = target.ravel()
    coeffs, *_ = np.linalg.lstsq(B, t, rcond=None)
    pred = B @ coeffs
    res = t - pred
    res_norm = float(np.linalg.norm(res))
    t_norm = float(np.linalg.norm(t))
    r2 = float(1.0 - (res_norm / t_norm) ** 2) if t_norm > 0 else 1.0
    in_span = r2 >= r2_threshold
    return {
        "r_squared": r2,
        "coeffs": {k: float(c) for k, c in zip(labels, coeffs)},
        "residual_norm": res_norm,
        "target_norm": t_norm,
        "in_span": in_span,
        "verdict": "IN_BASIS_SPAN" if in_span else "INDEPENDENT",
        "r2_threshold": r2_threshold,
    }


def lineage_audit(samples: dict[str, np.ndarray], frontier_labels: list[str],
                  cosine_threshold: float = 0.9, r2_threshold: float = 0.95) -> dict:
    """Two-stage check: pairwise cosine + residual span for each frontier
    function against the calibration basis."""
    pairwise = pairwise_function_correlations(samples, threshold=cosine_threshold)
    basis_labels = [k for k in samples if k not in frontier_labels]
    basis = {k: samples[k] for k in basis_labels}
    span_results = {}
    for label in frontier_labels:
        if label not in samples:
            continue
        span_results[label] = residual_decomposition(
            samples[label], basis, r2_threshold=r2_threshold,
        )
    return {
        "pairwise": pairwise,
        "frontier_in_calibration_basis": span_results,
        "any_coupled": (
            len(pairwise["flags"]) > 0
            or any(v.get("in_span") for v in span_results.values())
        ),
    }
