"""Phase 4b counterfactual — same as Phase 4 but with two-site DMRG disabled.

Tests the §4.3 finding from v3 paper: did DMRG rank-adaptation collapse shape
diversity (Runge: 16 cells in Phase 3 -> 7 cells in Phase 4)? Compare archive
occupancy and descriptor coupling against the Phase 4 (DMRG-on) result.

Same seeds, same functions, same hybrid mutation. Only difference:
  dmrg_sweeps=0 (and als_sweeps=0 -- no refinement at all).
"""
from __future__ import annotations
import json
import sys
import time
from dataclasses import asdict
from itertools import combinations
from pathlib import Path

import numpy as np

from zoo.functions.calibration import product_of_coords, random_gaussian, sum_of_squares
from zoo.functions.frontier import pairwise_tanh, runge_dim, heat_smoothed_paraboloid
from zoo.map_elites.grid import Archive, grid_params_entropy
from zoo.map_elites.loop import LoopConfig
from zoo.map_elites.mutation import MutationConfig
from zoo.map_elites.multi_seed import MultiSeedResult, run_multi_seed
from zoo.diagnostics.nonlinear import nonlinear_audit


def _pooled(msr: MultiSeedResult) -> dict[str, np.ndarray]:
    rows = []
    for arc in msr.archives:
        for e in arc.history:
            x = e.extras or {}
            rows.append({
                "log_params": float(np.log10(max(1, e.n_params))),
                "log_error": float(np.log10(max(1e-15, e.rel_error))),
                "rank_entropy": float(x.get("rank_entropy", 0.0)),
                "rank_concentration": float(x.get("rank_concentration", 1.0)),
                "avg_rank": float(x.get("avg_rank", np.mean(e.ranks))),
            })
    if not rows:
        return {}
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def _pearson(cols, a, b):
    x, y = cols[a], cols[b]
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def main() -> int:
    t0 = time.time()
    config = LoopConfig(
        n_generations=50, n_initial=8, max_bond=16, seed=0,
        als_sweeps=0,                # NO ALS
        dmrg_sweeps=0,                # NO DMRG (the counterfactual switch)
        mutation=MutationConfig(strategy="hybrid", p_shift=0.5),
    )
    grid = grid_params_entropy()
    shape = (12,) * 6
    seeds = [20260424, 20260425, 20260426]

    functions = [
        product_of_coords(shape=shape),
        sum_of_squares(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
        runge_dim(shape=shape),
        heat_smoothed_paraboloid(shape=shape, t=0.02),
    ]

    msrs = {}
    print(f"Phase 4b counterfactual (NO DMRG) — {len(seeds)} seeds, hybrid mutation\n")
    for f in functions:
        t_fn = time.time()
        msr = run_multi_seed(f, config, grid, seeds)
        agg = msr.aggregate_summary()
        print(f"[{f.label}] cells_med={agg['n_cells_occupied']['median']:.0f} "
              f"pareto_med={agg['pareto_front_size']['median']:.0f} "
              f"min_err_med={agg['min_error']['median']:.2e} "
              f"elapsed={time.time()-t_fn:.1f}s")
        msrs[f.label] = msr

    # Quick descriptor audit on (log_params, rank_entropy) per function
    print("\nDescriptor audit on (log_params, rank_entropy):")
    audits = {}
    for label, msr in msrs.items():
        cols = _pooled(msr)
        n = len(cols["log_params"])
        # Subsample to 150 to keep dCor tractable
        if n > 150:
            rng = np.random.default_rng(99)
            idx = rng.choice(n, size=150, replace=False)
            cols_sub = {k: v[idx] for k, v in cols.items()}
        else:
            cols_sub = cols
        nl = nonlinear_audit(cols_sub, dcor_threshold=0.5, mi_threshold=0.5)
        pearson_lp_re = _pearson(cols, "log_params", "rank_entropy")
        dc = nl["distance_correlation_matrix"].get("log_params|rank_entropy", 0.0)
        mi = nl["ksg_mi_matrix"].get("log_params|rank_entropy", 0.0)
        audits[label] = {
            "pearson_lp_re": pearson_lp_re,
            "dcor_lp_re": dc,
            "mi_lp_re": mi,
            "n_evals": int(n),
        }
        print(f"  [{label}] n={n}  Pearson r={pearson_lp_re:+.3f}  "
              f"dCor={dc:.3f}  MI={mi:.3f} nats")

    out_dir = Path(__file__).resolve().parent.parent / "results"
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"phase4b_no_dmrg_{ts}.json"
    payload = {
        "experiment": "zoo_phase4b_no_dmrg",
        "timestamp": ts,
        "config": asdict(config),
        "seeds": seeds,
        "shape": list(shape),
        "summaries": {k: v.aggregate_summary() for k, v in msrs.items()},
        "archives_seed_0": {
            k: {
                "summary": v.archives[0].summary(),
                "cells": [{"cell": list(c), "elite": asdict(e)}
                          for c, e in sorted(v.archives[0].cells.items())],
                "pareto_front": [asdict(e) for e in v.archives[0].pareto_front()],
            }
            for k, v in msrs.items()
        },
        "pooled_history": {
            k: [asdict(e) for a in v.archives for e in a.history]
            for k, v in msrs.items()
        },
        "audits": audits,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
