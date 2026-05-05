"""Conditional-MI + shuffled-null analysis on the existing Phase 4 dump.

Two questions, both answered without running new MAP-Elites:

(1) Is the observed MI(log_params, rank_entropy) significantly above the
    shuffled null? Construct an empirical null by shuffling rank_entropy
    against fixed log_params 100 times and computing MI on each shuffle.
    Report observed MI as percentile of the null distribution.

(2) Is the residual MI driven by the §4.2 geometric boundary (high-entropy
    profiles cannot have low params), or by structure beyond the boundary?
    Partition pooled history by log_params bands and compute per-band MI.
    If within-band MI drops to baseline ~ 0, the boundary explains all
    observed coupling. If within-band MI persists, there is structural
    coupling beyond geometry.

Both tests use KSG k-NN MI (k=3) with 150-point subsampling for tractability.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

from zoo.diagnostics.nonlinear import knn_mutual_information, distance_correlation


HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE.parent / "results"


def _load_latest(prefix: str) -> tuple[dict, str]:
    candidates = sorted(RESULTS_DIR.glob(f"{prefix}_*.json"))
    if not candidates:
        raise SystemExit(f"No {prefix}_*.json found.")
    with candidates[-1].open("r") as f:
        return json.load(f), candidates[-1].name


def _extract(payload: dict, label: str) -> tuple[np.ndarray, np.ndarray]:
    pool = payload["pooled_history_per_function"][label]
    lp = np.array([float(np.log10(max(1, e["n_params"]))) for e in pool])
    re = np.array([float((e["extras"] or {}).get("rank_entropy", 0.0)) for e in pool])
    return lp, re


def shuffled_null(lp: np.ndarray, re: np.ndarray, n_shuffles: int = 100,
                   subsample: int = 150, seed: int = 99) -> dict:
    """Empirical MI null distribution by shuffling rank_entropy."""
    rng = np.random.default_rng(seed)
    n = len(lp)
    if n > subsample:
        idx = rng.choice(n, size=subsample, replace=False)
        lp, re = lp[idx], re[idx]
    # Standardize
    lp_n = (lp - lp.mean()) / max(lp.std(), 1e-12)
    re_n = (re - re.mean()) / max(re.std(), 1e-12)
    # Observed
    mi_obs = knn_mutual_information(lp_n, re_n, k=3)
    dc_obs = distance_correlation(lp_n, re_n)
    # Null distribution
    mi_null = []
    dc_null = []
    for _ in range(n_shuffles):
        perm = rng.permutation(len(re_n))
        re_shuf = re_n[perm]
        mi_null.append(knn_mutual_information(lp_n, re_shuf, k=3))
        dc_null.append(distance_correlation(lp_n, re_shuf))
    mi_null = np.array(mi_null)
    dc_null = np.array(dc_null)
    return {
        "n_subsample": int(len(lp)),
        "n_shuffles": int(n_shuffles),
        "mi_observed": float(mi_obs),
        "mi_null_mean": float(mi_null.mean()),
        "mi_null_std": float(mi_null.std()),
        "mi_null_p95": float(np.percentile(mi_null, 95)),
        "mi_null_p99": float(np.percentile(mi_null, 99)),
        "mi_null_max": float(mi_null.max()),
        "mi_z_vs_null": float((mi_obs - mi_null.mean()) / max(mi_null.std(), 1e-12)),
        "mi_p_value": float((mi_null >= mi_obs).mean()),
        "dcor_observed": float(dc_obs),
        "dcor_null_mean": float(dc_null.mean()),
        "dcor_null_p95": float(np.percentile(dc_null, 95)),
        "dcor_p_value": float((dc_null >= dc_obs).mean()),
    }


def conditional_mi(lp: np.ndarray, re: np.ndarray, n_bands: int = 4,
                   k: int = 3) -> dict:
    """MI(rank_entropy, log_params) within log_params bands.

    If the global MI is driven entirely by the geometric boundary, splitting
    log_params into bands narrows its range within each band; the residual
    MI within bands measures structure beyond the boundary.

    Caveat: small bands have low n; KSG becomes biased. We report bands
    with n >= 20 only and note the small-sample limitation.
    """
    quantiles = np.linspace(0, 1, n_bands + 1)
    edges = np.quantile(lp, quantiles)
    bands = []
    for b in range(n_bands):
        lo, hi = edges[b], edges[b + 1]
        if b == n_bands - 1:
            mask = (lp >= lo) & (lp <= hi)
        else:
            mask = (lp >= lo) & (lp < hi)
        n_in = int(mask.sum())
        if n_in < 20:
            bands.append({
                "band": b, "lp_range": [float(lo), float(hi)],
                "n_in_band": n_in, "mi_within_band": None,
                "note": "n < 20; skipped",
            })
            continue
        lp_b = lp[mask]
        re_b = re[mask]
        if lp_b.std() == 0 or re_b.std() == 0:
            mi = 0.0
            dc = 0.0
        else:
            lp_b_n = (lp_b - lp_b.mean()) / lp_b.std()
            re_b_n = (re_b - re_b.mean()) / re_b.std()
            mi = knn_mutual_information(lp_b_n, re_b_n, k=k)
            dc = distance_correlation(lp_b_n, re_b_n)
        bands.append({
            "band": b,
            "lp_range": [float(lo), float(hi)],
            "n_in_band": n_in,
            "log_params_std_in_band": float(lp_b.std()),
            "rank_entropy_std_in_band": float(re_b.std()),
            "mi_within_band": float(mi),
            "dcor_within_band": float(dc),
        })
    valid = [b for b in bands if b.get("mi_within_band") is not None]
    avg_mi = float(np.mean([b["mi_within_band"] for b in valid])) if valid else None
    return {
        "n_bands_requested": n_bands,
        "n_bands_valid": len(valid),
        "bands": bands,
        "mean_within_band_mi": avg_mi,
    }


def main() -> int:
    t0 = time.time()
    payload, fname = _load_latest("phase4")
    print(f"Reading {fname}\n")

    targets = ["pairwise_tanh", "runge_dim", "heat_smoothed"]
    results: dict[str, dict] = {}

    for label in targets:
        print(f"=== {label} ===")
        lp, re = _extract(payload, label)
        print(f"  pooled n = {len(lp)}")

        # Shuffled null (Test 1)
        null = shuffled_null(lp, re, n_shuffles=100, subsample=150, seed=99)
        print(f"  Test 1 — shuffled null:")
        print(f"    MI observed:     {null['mi_observed']:.3f} nats")
        print(f"    MI null mean:    {null['mi_null_mean']:.3f}")
        print(f"    MI null p95:     {null['mi_null_p95']:.3f}")
        print(f"    MI null p99:     {null['mi_null_p99']:.3f}")
        print(f"    MI z vs null:    {null['mi_z_vs_null']:.1f} sigma")
        print(f"    MI p-value:      {null['mi_p_value']:.3f}")
        print(f"    dCor observed:   {null['dcor_observed']:.3f}  null_mean={null['dcor_null_mean']:.3f}")

        # Conditional MI (Test 2)
        cond = conditional_mi(lp, re, n_bands=4)
        print(f"  Test 2 — conditional MI within log_params bands:")
        print(f"    n_bands_valid = {cond['n_bands_valid']}")
        for b in cond["bands"]:
            if b.get("mi_within_band") is None:
                print(f"    band {b['band']} {b['lp_range']}: n={b['n_in_band']} skipped ({b.get('note')})")
            else:
                print(f"    band {b['band']} {b['lp_range']}: n={b['n_in_band']} "
                      f"MI={b['mi_within_band']:.3f}  dCor={b['dcor_within_band']:.3f}")
        print(f"    mean within-band MI: {cond['mean_within_band_mi']}")

        # Verdict
        boundary_explains = (
            cond["mean_within_band_mi"] is not None
            and cond["mean_within_band_mi"] < 0.3
        )
        coupling_significant = null["mi_p_value"] < 0.05
        results[label] = {
            "shuffled_null": null,
            "conditional_mi": cond,
            "boundary_explains_residual": boundary_explains,
            "coupling_significantly_above_null": coupling_significant,
        }
        print(f"  VERDICT:")
        print(f"    Coupling above shuffled null:    {coupling_significant}")
        print(f"    Boundary explains residual MI:   {boundary_explains}")
        print()

    out_path = RESULTS_DIR / f"phase4_analysis_{time.strftime('%Y%m%dT%H%M%S')}.json"
    out_path.write_text(json.dumps({
        "source_dump": fname,
        "results": results,
    }, indent=2, default=str))
    print(f"Dumped {out_path}")
    print(f"Elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
