"""Phase 5b — same as Phase 5 but with DMRG disabled.

Phase 5 revealed that DMRG (now actually running, after the multi_seed bug fix)
collapses peaked rank profiles toward each function's effective rank, masking
the diversified-seed test. Phase 5b removes DMRG to give the decisive Branch-A
test the reviewer asked for: with diversified seeds + larger rank-shift +
TT-SVD only, does the entropy axis fill and within-band MI drop toward null?
"""
from __future__ import annotations
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from zoo.functions.calibration import product_of_coords, random_gaussian, sum_of_squares
from zoo.functions.frontier import pairwise_tanh, runge_dim, heat_smoothed_paraboloid
from zoo.map_elites.grid import grid_params_entropy
from zoo.map_elites.loop import LoopConfig
from zoo.map_elites.mutation import MutationConfig
from zoo.map_elites.multi_seed import run_multi_seed
from zoo.descriptors.spectral import spectral_decay, effective_rank_at_threshold
from zoo.diagnostics.nonlinear import (
    distance_correlation, knn_mutual_information,
)


def _pooled(msr) -> dict[str, np.ndarray]:
    rows = []
    for arc in msr.archives:
        for e in arc.history:
            x = e.extras or {}
            rows.append({
                "log_params": float(np.log10(max(1, e.n_params))),
                "rank_entropy": float(x.get("rank_entropy", 0.0)),
            })
    if not rows:
        return {}
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def _within_band_mi_with_null(lp, re, n_bands=4, n_shuffles=100, seed=99, k=3):
    rng = np.random.default_rng(seed)
    edges = np.quantile(lp, np.linspace(0, 1, n_bands + 1))
    bands = []
    for b in range(n_bands):
        lo, hi = edges[b], edges[b + 1]
        mask = (lp >= lo) & (lp <= hi) if b == n_bands - 1 else (lp >= lo) & (lp < hi)
        if mask.sum() < 20:
            bands.append({"band": b, "n": int(mask.sum()), "skipped": True})
            continue
        x, y = lp[mask], re[mask]
        if x.std() == 0 or y.std() == 0:
            bands.append({"band": b, "n": int(mask.sum()), "obs_mi": 0.0,
                          "null_mean": 0.0, "obs_over_null": 0.0, "p_value": 1.0})
            continue
        xn = (x - x.mean()) / x.std()
        yn = (y - y.mean()) / y.std()
        mi_obs = knn_mutual_information(xn, yn, k=k)
        nulls = []
        for _ in range(n_shuffles):
            yp = yn[rng.permutation(len(yn))]
            nulls.append(knn_mutual_information(xn, yp, k=k))
        nulls = np.array(nulls)
        bands.append({
            "band": b, "lp_range": [float(lo), float(hi)], "n": int(mask.sum()),
            "obs_mi": float(mi_obs), "null_mean": float(nulls.mean()),
            "null_p99": float(np.percentile(nulls, 99)),
            "obs_over_null": float(mi_obs / max(nulls.mean(), 1e-12)),
            "p_value": float((nulls >= mi_obs).mean()),
        })
    return {"bands": bands}


def main() -> int:
    t0 = time.time()
    base_config = LoopConfig(
        n_generations=80,
        n_initial=12,
        max_bond=16,
        seed=0,
        als_sweeps=0,
        dmrg_sweeps=0,                # DMRG OFF — the key change vs Phase 5
        dmrg_rel_tol=1e-10,
        mutation=MutationConfig(strategy="hybrid", p_shift=0.5, shift_magnitude=4),
        seed_strategy="diversified",
    )
    grid = grid_params_entropy()
    shape = (12,) * 6
    seeds = [20260424, 20260425, 20260426, 20260427, 20260428]

    functions = [
        product_of_coords(shape=shape),
        sum_of_squares(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
        runge_dim(shape=shape),
        heat_smoothed_paraboloid(shape=shape, t=0.005),
    ]
    frontier_labels = [f.label for f in functions if f.tier == "frontier"]

    print(f"Phase 5b — DIVERSIFIED seeds + shift=4, DMRG OFF (TT-SVD only), n_seeds={len(seeds)}")
    print()

    # STAGE 1 — function descriptors
    samples = {f.label: f.sample() for f in functions}
    func_descriptors = {}
    for f in functions:
        sd = spectral_decay(samples[f.label])
        er = effective_rank_at_threshold(samples[f.label], threshold=1e-8)
        func_descriptors[f.label] = {
            "spectral_alpha": sd["alpha"], "effective_rank": er["effective_rank"],
        }

    # STAGE 2 — multi-seed MAP-Elites
    print("STAGE 2 — Branch-A MAP-Elites (5 seeds, NO DMRG)")
    msr_by_label = {}
    achievable_lo, achievable_hi = 0.778, 1.609
    achievable_w = achievable_hi - achievable_lo
    for f in functions:
        t_fn = time.time()
        msr = run_multi_seed(f, base_config, grid, seeds)
        dt = time.time() - t_fn
        agg = msr.aggregate_summary()
        pool = _pooled(msr)
        re = pool.get("rank_entropy", np.array([]))
        re_min, re_max = float(re.min()), float(re.max())
        coverage = (re_max - re_min) / achievable_w
        print(f"  [{f.label}] cells_med={agg['n_cells_occupied']['median']:.0f} "
              f"min_err_med={agg['min_error']['median']:.2e} "
              f"entropy=[{re_min:.3f},{re_max:.3f}] coverage={coverage*100:.0f}% "
              f"elapsed={dt:.1f}s")
        msr_by_label[f.label] = msr

    # STAGE 3 — within-band MI with within-band null
    print("\nSTAGE 3 — within-band MI vs within-band null")
    per_function_band_mi = {}
    for label in frontier_labels:
        cols = _pooled(msr_by_label[label])
        result = _within_band_mi_with_null(cols["log_params"], cols["rank_entropy"])
        per_function_band_mi[label] = result
        print(f"  [{label}]")
        for b in result["bands"]:
            if b.get("skipped"):
                print(f"    band {b['band']}: n={b['n']} skipped")
            else:
                print(f"    band {b['band']}: n={b['n']:3d}  obs_MI={b['obs_mi']:.3f}  "
                      f"null_mean={b['null_mean']:.3f}  obs/null={b['obs_over_null']:5.1f}  "
                      f"p={b['p_value']:.3f}")

    # STAGE 4 — full-sample audits
    print("\nSTAGE 4 — full-sample (log_params, rank_entropy) audits")
    full_audits = {}
    for label in frontier_labels:
        cols = _pooled(msr_by_label[label])
        n = len(cols["log_params"])
        if n > 200:
            rng = np.random.default_rng(99)
            idx = rng.choice(n, size=200, replace=False)
            x, y = cols["log_params"][idx], cols["rank_entropy"][idx]
        else:
            x, y = cols["log_params"], cols["rank_entropy"]
        if x.std() > 0 and y.std() > 0:
            pearson = float(np.corrcoef(x, y)[0, 1])
            xn = (x - x.mean()) / x.std()
            yn = (y - y.mean()) / y.std()
            dc = distance_correlation(xn, yn)
            mi = knn_mutual_information(xn, yn, k=3)
        else:
            pearson = dc = mi = 0.0
        full_audits[label] = {
            "n_evals": int(n), "pearson_r": pearson,
            "dcor": float(dc), "ksg_mi": float(mi),
        }
        print(f"  [{label}] n={n}  pearson={pearson:+.3f}  dcor={dc:.3f}  mi={mi:.3f}")

    # STAGE 5 — outcome adjudication
    print("\nSTAGE 5 — Branch A outcome (diversified seeds, no DMRG)")
    branch_a = {}
    for label in frontier_labels:
        pool = _pooled(msr_by_label[label])
        re = pool["rank_entropy"]
        coverage = (re.max() - re.min()) / achievable_w
        max_obs_over_null = max(
            (b.get("obs_over_null", 0.0)
             for b in per_function_band_mi[label]["bands"] if not b.get("skipped")),
            default=0.0,
        )
        entropy_filled = coverage >= 0.6
        mi_decoupled = max_obs_over_null <= 3.0
        if entropy_filled and mi_decoupled:
            outcome = "A_BRANCH_A_VALIDATED"
        elif entropy_filled:
            outcome = "B_GEOMETRY_SIGNAL"
        elif not entropy_filled:
            outcome = "C_PARTIAL_FILL"
        branch_a[label] = {
            "coverage_frac": float(coverage),
            "max_obs_over_null": float(max_obs_over_null),
            "outcome": outcome,
        }
        print(f"  [{label}] {outcome}  coverage={coverage:.1%}  max_obs/null={max_obs_over_null:.1f}")

    # DUMP
    out_dir = Path(__file__).resolve().parent.parent / "results"
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"phase5b_no_dmrg_{ts}.json"
    payload = {
        "experiment": "zoo_phase5b_no_dmrg",
        "timestamp": ts,
        "config": asdict(base_config),
        "seeds": seeds,
        "shape": list(shape),
        "function_descriptors": func_descriptors,
        "multi_seed_summaries": {k: v.aggregate_summary() for k, v in msr_by_label.items()},
        "pooled_history": {
            k: [asdict(e) for a in v.archives for e in a.history]
            for k, v in msr_by_label.items()
        },
        "within_band_mi_with_null": per_function_band_mi,
        "full_sample_audits": full_audits,
        "branch_a_outcome": branch_a,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
