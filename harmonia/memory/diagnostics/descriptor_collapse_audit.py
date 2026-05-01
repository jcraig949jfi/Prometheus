"""Descriptor-collapse audit (substrate primitive, v0.1).

A 5-layer pipeline that detects whether a set of descriptors is collapsing
onto a lower-dimensional manifold, with built-in null discipline and
conditioning. Generalized from `exploratory/zoo/diagnostics/{correlation,
nonlinear}.py` + `exploratory/zoo/experiments/analyze_conditional_mi.py`
into a substrate-tier primitive callable from any session.

Layers
------
1. Pearson correlation matrix (linear collapse)
2. Distance correlation matrix (any-form dependence; Szekely-Rizzo-Bakirov)
3. KSG mutual information matrix (Kraskov-Stogbauer-Grassberger, k-NN)
4. Shuffled-null per pair (is observed coupling above the null distribution?)
5. Within-band conditional MI (is the residual coupling explained by a
   geometric/boundary effect, or does it persist after band-narrowing?)

Discipline
----------
- Every result dict carries a `caveats` list with KSG small-n warnings,
  Pearson-is-linear-only reminder, and the not-a-Pattern-30 disclaimer.
- The composite verdict is a falsifier, not a finding: CLEAR / BOUNDARY_
  EXPLAINED / STRUCTURAL_COUPLING_SUSPECTED.
- Cross-references the substrate's null discipline: `NULL_BSWCD@v2`
  (block-shuffle nulls), `null_protocol_v1.md` (per-claim-class nulls),
  and `pattern_30.py` (algebraic-coupling diagnostic that this audit
  does NOT replace).

Provenance: proposal at
`D:/Prometheus/harmonia/memory/protocols/descriptor_collapse_audit_proposal.md`.
"""
from __future__ import annotations

from itertools import combinations
from typing import Iterable

import numpy as np


# -----------------------------------------------------------------------------
# Layer-3 / Layer-2 primitives — verbatim from zoo, hash-equivalent behavior
# -----------------------------------------------------------------------------

def distance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Szekely-Rizzo-Bakirov distance correlation. Range [0, 1].

    Zero iff X and Y are independent (under finite-moment assumptions).
    Strictly positive under any dependence, including nonlinear.
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    n = len(x)
    if n < 2 or len(y) != n:
        return 0.0

    a = np.abs(x[:, None] - x[None, :])
    b = np.abs(y[:, None] - y[None, :])

    A = a - a.mean(axis=0, keepdims=True) - a.mean(axis=1, keepdims=True) + a.mean()
    B = b - b.mean(axis=0, keepdims=True) - b.mean(axis=1, keepdims=True) + b.mean()

    dcov2_xy = (A * B).mean()
    dvar2_x = (A * A).mean()
    dvar2_y = (B * B).mean()

    denom = np.sqrt(dvar2_x * dvar2_y)
    if denom <= 0:
        return 0.0
    return float(np.sqrt(max(0.0, dcov2_xy / denom)))


def knn_mutual_information(
    x: np.ndarray,
    y: np.ndarray,
    k: int = 3,
    *,
    rng_seed: int = 0,
) -> float:
    """KSG-1 estimator of I(X; Y), in nats.

    Reference: Kraskov, Stogbauer, Grassberger, "Estimating mutual information,"
    Phys Rev E 69, 066138 (2004).

    KSG-1 with Chebyshev distance. Small jitter is added (deterministic via
    rng_seed) to break ties from zero-variance / discrete descriptors.
    """
    from scipy.special import digamma

    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    n = len(x)
    if n < k + 1 or len(y) != n:
        return 0.0

    rng = np.random.default_rng(rng_seed)
    x_std = x.std() if x.std() > 0 else 1.0
    y_std = y.std() if y.std() > 0 else 1.0
    x = x + rng.normal(0, x_std * 1e-10, n)
    y = y + rng.normal(0, y_std * 1e-10, n)

    dx = np.abs(x[:, None] - x[None, :])
    dy = np.abs(y[:, None] - y[None, :])
    joint = np.maximum(dx, dy)
    np.fill_diagonal(joint, np.inf)

    eps_k = np.partition(joint, k, axis=1)[:, k - 1]

    n_x = (dx < eps_k[:, None]).sum(axis=1) - 1
    n_y = (dy < eps_k[:, None]).sum(axis=1) - 1
    n_x = np.maximum(n_x, 0)
    n_y = np.maximum(n_y, 0)

    mi = digamma(k) + digamma(n) - np.mean(digamma(n_x + 1) + digamma(n_y + 1))
    return float(max(0.0, mi))


# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------

def _validate_descriptors(descriptors: dict[str, np.ndarray]) -> tuple[list[str], int]:
    if not descriptors:
        raise ValueError("descriptors dict is empty")
    keys = list(descriptors)
    n = len(np.asarray(descriptors[keys[0]]).ravel())
    for k in keys:
        v = np.asarray(descriptors[k]).ravel()
        if len(v) != n:
            raise ValueError(
                f"descriptor '{k}' has length {len(v)}; expected {n} (must match other descriptors)"
            )
    if n < 3:
        raise ValueError(f"need at least 3 samples per descriptor; got {n}")
    return keys, n


def _standardize(arr: np.ndarray) -> np.ndarray:
    a = np.asarray(arr, dtype=np.float64).ravel()
    s = a.std()
    if s == 0:
        return a - a.mean()
    return (a - a.mean()) / s


# -----------------------------------------------------------------------------
# Layer 1: Pearson
# -----------------------------------------------------------------------------

def pearson_audit(
    descriptors: dict[str, np.ndarray],
    threshold: float = 0.9,
) -> dict:
    """Pairwise Pearson correlation; flag pairs with |r| >= threshold.

    Linear collapse only. Pearson ~0 does NOT imply independence — this layer
    must be paired with at least one of dCor / KSG MI.
    """
    keys, n = _validate_descriptors(descriptors)
    cols = {k: np.asarray(descriptors[k], dtype=np.float64).ravel() for k in keys}
    matrix: dict[str, float] = {}
    flagged: list[dict] = []
    for a, b in combinations(keys, 2):
        x, y = cols[a], cols[b]
        if x.std() == 0 or y.std() == 0:
            r = 0.0
        else:
            r = float(np.corrcoef(x, y)[0, 1])
        matrix[f"{a}|{b}"] = r
        if abs(r) >= threshold:
            flagged.append({"pair": [a, b], "correlation": r})
    return {
        "n_samples": n,
        "matrix": matrix,
        "flagged": flagged,
        "threshold": threshold,
    }


# -----------------------------------------------------------------------------
# Layer 2: Distance correlation
# -----------------------------------------------------------------------------

def dcor_audit(
    descriptors: dict[str, np.ndarray],
    threshold: float = 0.5,
) -> dict:
    """Pairwise distance correlation; flag pairs with dCor >= threshold.

    Standardizes inputs for numerical conditioning before computing dCor.
    """
    keys, n = _validate_descriptors(descriptors)
    matrix: dict[str, float] = {}
    flagged: list[dict] = []
    for a, b in combinations(keys, 2):
        x, y = descriptors[a], descriptors[b]
        if np.asarray(x).std() == 0 or np.asarray(y).std() == 0:
            d = 0.0
        else:
            d = distance_correlation(_standardize(x), _standardize(y))
        matrix[f"{a}|{b}"] = d
        if d >= threshold:
            flagged.append({"pair": [a, b], "distance_correlation": d})
    return {
        "n_samples": n,
        "matrix": matrix,
        "flagged": flagged,
        "threshold": threshold,
    }


# -----------------------------------------------------------------------------
# Layer 3: KSG mutual information
# -----------------------------------------------------------------------------

def ksg_mi_audit(
    descriptors: dict[str, np.ndarray],
    threshold_nats: float = 0.5,
    k: int = 3,
    *,
    rng_seed: int = 0,
) -> dict:
    """Pairwise KSG MI in nats; flag pairs with MI >= threshold_nats.

    threshold_nats=0.5 ~ 0.72 bits ~ moderate-to-tight dependence. Defaults
    inherited from zoo `nonlinear_audit`.
    """
    keys, n = _validate_descriptors(descriptors)
    matrix: dict[str, float] = {}
    flagged: list[dict] = []
    for a, b in combinations(keys, 2):
        x, y = descriptors[a], descriptors[b]
        if np.asarray(x).std() == 0 or np.asarray(y).std() == 0:
            m = 0.0
        else:
            m = knn_mutual_information(
                _standardize(x), _standardize(y), k=k, rng_seed=rng_seed
            )
        matrix[f"{a}|{b}"] = m
        if m >= threshold_nats:
            flagged.append({"pair": [a, b], "ksg_mi_nats": m})
    return {
        "n_samples": n,
        "matrix": matrix,
        "flagged": flagged,
        "threshold_nats": threshold_nats,
        "k": k,
    }


# -----------------------------------------------------------------------------
# Layer 4: Shuffled-null per pair
# -----------------------------------------------------------------------------

def shuffled_null_pair(
    x: np.ndarray,
    y: np.ndarray,
    *,
    n_shuffles: int = 100,
    subsample: int | None = 150,
    k_mi: int = 3,
    rng_seed: int = 99,
) -> dict:
    """Empirical null distribution of MI and dCor by permuting y against
    fixed x. Returns observed values, null summary, z-scores, and p-values.

    `subsample` caps n at this size for KSG tractability (KSG cost is O(n^2)).
    Pass None to skip subsampling.

    p-value is one-sided: P(null >= observed). Below 0.05 is the working
    floor; combine with effect size, not as a sole gate.
    """
    rng = np.random.default_rng(rng_seed)
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    n = len(x)
    if subsample is not None and n > subsample:
        idx = rng.choice(n, size=subsample, replace=False)
        x, y = x[idx], y[idx]

    xn = _standardize(x)
    yn = _standardize(y)

    mi_obs = knn_mutual_information(xn, yn, k=k_mi, rng_seed=rng_seed)
    dc_obs = distance_correlation(xn, yn)

    mi_null = np.empty(n_shuffles)
    dc_null = np.empty(n_shuffles)
    for i in range(n_shuffles):
        perm = rng.permutation(len(yn))
        ys = yn[perm]
        mi_null[i] = knn_mutual_information(xn, ys, k=k_mi, rng_seed=rng_seed + 1 + i)
        dc_null[i] = distance_correlation(xn, ys)

    def _p(null_arr: np.ndarray, obs: float) -> float:
        return float((null_arr >= obs).mean())

    def _z(null_arr: np.ndarray, obs: float) -> float:
        sd = float(null_arr.std())
        if sd <= 1e-12:
            return float("inf") if obs > null_arr.mean() else 0.0
        return float((obs - null_arr.mean()) / sd)

    return {
        "n_subsample": int(len(xn)),
        "n_shuffles": int(n_shuffles),
        "mi_observed": float(mi_obs),
        "mi_null_mean": float(mi_null.mean()),
        "mi_null_std": float(mi_null.std()),
        "mi_null_p95": float(np.percentile(mi_null, 95)),
        "mi_null_p99": float(np.percentile(mi_null, 99)),
        "mi_z": _z(mi_null, mi_obs),
        "mi_p_value": _p(mi_null, mi_obs),
        "dcor_observed": float(dc_obs),
        "dcor_null_mean": float(dc_null.mean()),
        "dcor_null_p95": float(np.percentile(dc_null, 95)),
        "dcor_z": _z(dc_null, dc_obs),
        "dcor_p_value": _p(dc_null, dc_obs),
    }


# -----------------------------------------------------------------------------
# Layer 5: Within-band conditional MI
# -----------------------------------------------------------------------------

def conditional_mi_pair(
    x: np.ndarray,
    y: np.ndarray,
    *,
    condition_on: np.ndarray | None = None,
    n_bands: int = 4,
    k_mi: int = 3,
    min_n_per_band: int = 20,
    rng_seed: int = 99,
) -> dict:
    """MI(x, y) within bands of a conditioning variable.

    If `condition_on` is None, bands are quantiles of x. Otherwise bands are
    quantiles of `condition_on` (the third variable).

    Within-band MI tests whether the global MI is driven entirely by a
    geometric/boundary effect (which a band restriction would attenuate)
    versus structural coupling (which persists within bands).

    Bands with n < min_n_per_band are skipped (KSG bias on small n).
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    if condition_on is None:
        cond = x.copy()
    else:
        cond = np.asarray(condition_on, dtype=np.float64).ravel()
        if len(cond) != len(x):
            raise ValueError("condition_on must match x and y in length")

    quantiles = np.linspace(0, 1, n_bands + 1)
    edges = np.quantile(cond, quantiles)
    bands: list[dict] = []
    for b in range(n_bands):
        lo, hi = edges[b], edges[b + 1]
        if b == n_bands - 1:
            mask = (cond >= lo) & (cond <= hi)
        else:
            mask = (cond >= lo) & (cond < hi)
        n_in = int(mask.sum())
        if n_in < min_n_per_band:
            bands.append({
                "band": b,
                "cond_range": [float(lo), float(hi)],
                "n_in_band": n_in,
                "mi_within_band": None,
                "dcor_within_band": None,
                "note": f"n < {min_n_per_band}; skipped (KSG small-n bias)",
            })
            continue
        x_b, y_b = x[mask], y[mask]
        if x_b.std() == 0 or y_b.std() == 0:
            mi = 0.0
            dc = 0.0
        else:
            xn = _standardize(x_b)
            yn = _standardize(y_b)
            mi = knn_mutual_information(xn, yn, k=k_mi, rng_seed=rng_seed)
            dc = distance_correlation(xn, yn)
        bands.append({
            "band": b,
            "cond_range": [float(lo), float(hi)],
            "n_in_band": n_in,
            "mi_within_band": float(mi),
            "dcor_within_band": float(dc),
        })
    valid = [b for b in bands if b["mi_within_band"] is not None]
    avg_mi = float(np.mean([b["mi_within_band"] for b in valid])) if valid else None
    return {
        "n_bands_requested": n_bands,
        "n_bands_valid": len(valid),
        "min_n_per_band": min_n_per_band,
        "bands": bands,
        "mean_within_band_mi": avg_mi,
        "conditioned_on_self": condition_on is None,
    }


# -----------------------------------------------------------------------------
# Composite audit
# -----------------------------------------------------------------------------

def descriptor_collapse_audit(
    descriptors: dict[str, np.ndarray],
    *,
    pearson_threshold: float = 0.9,
    dcor_threshold: float = 0.5,
    mi_threshold_nats: float = 0.5,
    deep_pairs: list[tuple[str, str]] | None = None,
    deep_on_flagged: bool = True,
    n_shuffles: int = 100,
    n_bands: int = 4,
    k_mi: int = 3,
    rng_seed: int = 0,
) -> dict:
    """Full 5-layer descriptor-collapse audit.

    Shallow tier (layers 1-3) runs across all pairs. Deep tier (layers 4-5)
    runs on `deep_pairs` plus all shallow-flagged pairs (if
    `deep_on_flagged`). Composite verdict labels the whole audit as
    `CLEAR`, `BOUNDARY_EXPLAINED`, or `STRUCTURAL_COUPLING_SUSPECTED`.
    """
    keys, n = _validate_descriptors(descriptors)

    layer_1 = pearson_audit(descriptors, threshold=pearson_threshold)
    layer_2 = dcor_audit(descriptors, threshold=dcor_threshold)
    layer_3 = ksg_mi_audit(
        descriptors, threshold_nats=mi_threshold_nats, k=k_mi, rng_seed=rng_seed
    )

    flagged_shallow: set[tuple[str, str]] = set()
    for f in layer_1["flagged"]:
        flagged_shallow.add(tuple(f["pair"]))
    for f in layer_2["flagged"]:
        flagged_shallow.add(tuple(f["pair"]))
    for f in layer_3["flagged"]:
        flagged_shallow.add(tuple(f["pair"]))

    deep_pairs_set: set[tuple[str, str]] = set()
    if deep_on_flagged:
        deep_pairs_set |= flagged_shallow
    if deep_pairs:
        for a, b in deep_pairs:
            if a == b or a not in keys or b not in keys:
                raise ValueError(
                    f"deep_pairs entry ({a!r}, {b!r}) refers to unknown or self-pair descriptors"
                )
            deep_pairs_set.add(tuple(sorted((a, b))))
        # canonicalize the shallow set with the same ordering for indexing
        flagged_shallow = {tuple(sorted(p)) for p in flagged_shallow}

    layer_4_5: dict[str, dict] = {}
    for a, b in sorted(deep_pairs_set):
        # ensure consistent key regardless of input order
        a2, b2 = sorted((a, b))
        x = np.asarray(descriptors[a2], dtype=np.float64).ravel()
        y = np.asarray(descriptors[b2], dtype=np.float64).ravel()
        null = shuffled_null_pair(
            x, y, n_shuffles=n_shuffles, k_mi=k_mi, rng_seed=rng_seed + 1
        )
        cond = conditional_mi_pair(
            x, y, n_bands=n_bands, k_mi=k_mi, rng_seed=rng_seed + 2
        )
        layer_4_5[f"{a2}|{b2}"] = {
            "shuffled_null": null,
            "conditional_mi": cond,
        }

    audit_summary = _composite_verdict(
        layer_1, layer_2, layer_3, layer_4_5,
        mi_threshold_nats=mi_threshold_nats,
    )

    caveats = [
        "Pearson is linear-only; pearson |r| ~ 0 does not imply independence.",
        "dCor and KSG MI thresholds are heuristic; non-zero MI does not "
        "prove non-trivial dependence at finite n, and zero MI does not prove independence.",
        "Layers 4-5 use KSG; small-band n < min_n_per_band (default 20) skipped to avoid bias.",
        "This audit does NOT diagnose Pattern 30 algebraic-identity coupling. "
        "Algebraically-coupled descriptors will register as collapsed here (the correct shallow "
        "signal), but lineage diagnosis must come from `harmonia/sweeps/pattern_30.py`.",
        "This audit is a fast falsifier; final structural claims still require "
        "block-shuffle nulls (NULL_BSWCD@v2) per null_protocol_v1.md.",
    ]

    return {
        "version": "v0.1",
        "descriptors": keys,
        "n_samples": n,
        "thresholds": {
            "pearson": pearson_threshold,
            "dcor": dcor_threshold,
            "mi_nats": mi_threshold_nats,
            "k_mi": k_mi,
        },
        "layer_1_pearson": layer_1,
        "layer_2_dcor": layer_2,
        "layer_3_ksg_mi": layer_3,
        "layer_4_5_per_pair": layer_4_5,
        "audit_summary": audit_summary,
        "caveats": caveats,
    }


def _composite_verdict(
    layer_1: dict,
    layer_2: dict,
    layer_3: dict,
    layer_4_5: dict,
    *,
    mi_threshold_nats: float,
) -> dict:
    """Combine per-layer flags into a single verdict.

    Logic:
      - No shallow flags -> CLEAR.
      - Shallow flags exist but no deep audit ran -> SHALLOW_FLAGGED_DEEP_NOT_RUN
        (caller disabled deep_on_flagged and supplied no deep_pairs;
        no evidence to downgrade or escalate).
      - Shallow flags exist and at least one shallow-flagged pair was
        evaluated at deep tier:
          * any deep finding above-null AND not boundary-explained
            -> STRUCTURAL_COUPLING_SUSPECTED.
          * else -> BOUNDARY_EXPLAINED (all evaluated deep pairs are
            either not above null OR boundary-explained).
    """
    shallow = []
    for f in layer_1["flagged"]:
        shallow.append(("pearson", tuple(f["pair"])))
    for f in layer_2["flagged"]:
        shallow.append(("dcor", tuple(f["pair"])))
    for f in layer_3["flagged"]:
        shallow.append(("ksg_mi", tuple(f["pair"])))

    if not shallow:
        return {
            "any_pair_flagged_shallow": False,
            "verdict": "CLEAR",
            "shallow_flags": [],
            "deep_findings": [],
        }

    boundary_threshold = mi_threshold_nats / 2.0
    deep_findings: list[dict] = []
    any_structural = False
    for pair_key, payload in layer_4_5.items():
        nul = payload["shuffled_null"]
        cond = payload["conditional_mi"]
        above_null = nul["mi_p_value"] < 0.05
        mean_within = cond["mean_within_band_mi"]
        boundary_explained = (
            mean_within is not None and mean_within < boundary_threshold
        )
        structural = above_null and not boundary_explained
        if structural:
            any_structural = True
        deep_findings.append({
            "pair": pair_key,
            "above_null": bool(above_null),
            "boundary_explained": bool(boundary_explained),
            "structural_coupling_suspected": bool(structural),
            "mi_p_value": nul["mi_p_value"],
            "mi_observed": nul["mi_observed"],
            "mean_within_band_mi": mean_within,
            "boundary_threshold_used": boundary_threshold,
        })

    # Self-dissent v0.1.2 fix: if shallow flags exist but no deep audit
    # ran on any of them, we have no evidence to upgrade to structural
    # OR downgrade to boundary-explained. Caller turned off the deep
    # tier for those pairs; refusing to invent a verdict.
    flagged_shallow_pairs = {tuple(sorted(p)) for (_layer, p) in shallow}
    deep_audited_pairs = {tuple(sorted(k.split("|"))) for k in layer_4_5}
    shallow_pairs_with_deep = flagged_shallow_pairs & deep_audited_pairs

    if not shallow_pairs_with_deep:
        verdict = "SHALLOW_FLAGGED_DEEP_NOT_RUN"
    elif any_structural:
        verdict = "STRUCTURAL_COUPLING_SUSPECTED"
    else:
        verdict = "BOUNDARY_EXPLAINED"

    return {
        "any_pair_flagged_shallow": True,
        "verdict": verdict,
        "shallow_flags": [
            {"layer": layer, "pair": list(pair)} for (layer, pair) in shallow
        ],
        "deep_findings": deep_findings,
    }


__all__ = [
    "descriptor_collapse_audit",
    "pearson_audit",
    "dcor_audit",
    "ksg_mi_audit",
    "shuffled_null_pair",
    "conditional_mi_pair",
    "distance_correlation",
    "knn_mutual_information",
]
