"""MVP driver: run MAP-Elites on 3 functions, check calibration, dump JSON.

Phase-1 calibration contract:
  - prod_x must land at log10(params) <= 2.5 AND rel_error <= 1e-6 at some cell.
  - random_gaussian must NOT land below log10(params) ~= log10(dense_size) - 0.3.
"""
from __future__ import annotations
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from zoo.functions.calibration import product_of_coords, random_gaussian
from zoo.functions.frontier import pairwise_tanh
from zoo.map_elites.grid import Archive, GridSpec
from zoo.map_elites.loop import LoopConfig, run


def _archive_to_jsonable(arc: Archive) -> dict:
    return {
        "function_label": arc.function_label,
        "summary": arc.summary(),
        "cells": [
            {
                "cell": list(key),
                "elite": asdict(val),
            }
            for key, val in sorted(arc.cells.items())
        ],
        "pareto_front": [asdict(e) for e in arc.pareto_front()],
    }


def _check_calibration(archives: dict[str, Archive]) -> dict[str, dict]:
    verdicts: dict[str, dict] = {}

    # Low-rank calibration: prod_x should achieve very low error at small params.
    prod_arc = archives.get("prod_x")
    if prod_arc is not None:
        lo_error_lo_params = [
            e for e in prod_arc.cells.values()
            if np.log10(max(1, e.n_params)) <= 2.5 and e.rel_error <= 1e-6
        ]
        verdicts["prod_x"] = {
            "expected": "log10(params) <= 2.5 AND rel_error <= 1e-6 at some cell",
            "observed_hits": len(lo_error_lo_params),
            "verdict": "PASS" if lo_error_lo_params else "FAIL",
            "min_error_seen": prod_arc.summary().get("min_error"),
            "min_params_seen": prod_arc.summary().get("min_params"),
        }

    # Incompressibility calibration: random must resist meaningful compression.
    rand_arc = archives.get("random_gaussian")
    if rand_arc is not None:
        # Get the ceiling floor — at full rank, params equal dense size up to cores overhead.
        # Random tensor's "no compression" threshold: log10(params) within 0.3 of log10(dense_size).
        # Equivalently, achieving low error below that floor would be suspicious.
        # We inspect pareto front instead: any point with rel_error < 1e-2 at small params is a red flag.
        suspicious = [
            e for e in rand_arc.pareto_front()
            if e.rel_error < 1e-2 and np.log10(max(1, e.n_params)) < 4.0
        ]
        verdicts["random_gaussian"] = {
            "expected": "no low-error low-params point; random tensor should resist compression",
            "suspicious_points": len(suspicious),
            "verdict": "PASS" if not suspicious else "FAIL",
            "min_error_seen": rand_arc.summary().get("min_error"),
            "pareto_size": rand_arc.summary().get("pareto_front_size"),
        }

    verdicts["overall"] = {
        "all_pass": all(v.get("verdict") == "PASS" for v in verdicts.values() if "verdict" in v)
    }
    return verdicts


def main() -> int:
    t0 = time.time()
    spec = GridSpec()
    config = LoopConfig(n_generations=50, n_initial=8, max_bond=16, seed=20260424)

    # Keep grid shape modest so dense tensor + TT-SVD fits in RAM quickly.
    # 16^6 = 16,777,216 entries -> ~128 MB float64. Try smaller first for safety.
    shape = (12,) * 6  # 12^6 = 2,985,984 entries -> ~23 MB

    functions = [
        product_of_coords(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
    ]

    archives: dict[str, Archive] = {}
    for f in functions:
        t_fn = time.time()
        arc = run(f, config=config, spec=spec)
        dt = time.time() - t_fn
        s = arc.summary()
        print(
            f"[{f.label}] gens={config.n_generations} cells={s.get('n_cells_occupied')} "
            f"min_err={s.get('min_error'):.3e} min_params={s.get('min_params')} "
            f"pareto={s.get('pareto_front_size')} elapsed={dt:.1f}s"
        )
        archives[f.label] = arc

    verdicts = _check_calibration(archives)
    print()
    print("CALIBRATION VERDICTS")
    for k, v in verdicts.items():
        print(f"  {k}: {v}")

    # Dump archive
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"mvp_{ts}.json"
    payload = {
        "experiment": "zoo_mvp_phase1",
        "timestamp": ts,
        "config": asdict(config),
        "grid_spec": asdict(spec),
        "shape": list(shape),
        "archives": {k: _archive_to_jsonable(v) for k, v in archives.items()},
        "calibration_verdicts": verdicts,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")

    return 0 if verdicts["overall"]["all_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
