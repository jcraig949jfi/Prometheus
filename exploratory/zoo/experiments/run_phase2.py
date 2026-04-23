"""Phase 2 driver. Order per James 2026-04-24:
  1. Add separable-sum calibration (sum_of_squares, TT rank 2).
  2. Spectral decay descriptor (function-level intrinsic axis).
  3. Lineage check (Pattern-30 analog: pairwise + span).
  4. Constrained ALS refinement (1 sweep budget per evaluation).
  5. Stability under perturbation (per-Pareto-elite probe).
  6. Descriptor correlation diagnostic (collapse warning).

Calibration verdict contract (Phase 2):
  - prod_x:        TT rank 1, log10(params) <= 2.5, rel_err <= 1e-6.
  - sum_of_squares: TT rank 2, log10(params) <= 2.7, rel_err <= 1e-6.
  - random_gaussian: no low-error low-params point; resists compression.
"""
from __future__ import annotations
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from zoo.functions.calibration import product_of_coords, random_gaussian, sum_of_squares
from zoo.functions.frontier import pairwise_tanh
from zoo.map_elites.grid import Archive, GridSpec
from zoo.map_elites.loop import LoopConfig, run
from zoo.descriptors.spectral import spectral_decay
from zoo.descriptors.stability import stability_under_perturbation
from zoo.lineage.check import lineage_audit
from zoo.diagnostics.correlation import correlation_audit, cross_function_audit


def _archive_to_jsonable(arc: Archive) -> dict:
    return {
        "function_label": arc.function_label,
        "summary": arc.summary(),
        "cells": [
            {"cell": list(key), "elite": asdict(val)}
            for key, val in sorted(arc.cells.items())
        ],
        "pareto_front": [asdict(e) for e in arc.pareto_front()],
    }


def _check_calibration(archives: dict[str, Archive]) -> dict[str, dict]:
    verdicts: dict[str, dict] = {}

    contract = {
        "prod_x": {"max_log_params": 2.5, "max_rel_err": 1e-6, "expected_rank": 1},
        "sum_of_squares": {"max_log_params": 2.7, "max_rel_err": 1e-6, "expected_rank": 2},
    }
    for label, c in contract.items():
        arc = archives.get(label)
        if arc is None:
            continue
        hits = [
            e for e in arc.cells.values()
            if np.log10(max(1, e.n_params)) <= c["max_log_params"]
            and e.rel_error <= c["max_rel_err"]
        ]
        verdicts[label] = {
            "expected_tt_rank": c["expected_rank"],
            "expected": (
                f"log10(params) <= {c['max_log_params']} AND rel_err <= {c['max_rel_err']:.0e}"
            ),
            "observed_hits": len(hits),
            "verdict": "PASS" if hits else "FAIL",
            "min_error_seen": arc.summary().get("min_error"),
            "min_params_seen": arc.summary().get("min_params"),
        }

    rand_arc = archives.get("random_gaussian")
    if rand_arc is not None:
        suspicious = [
            e for e in rand_arc.pareto_front()
            if e.rel_error < 1e-2 and np.log10(max(1, e.n_params)) < 4.0
        ]
        verdicts["random_gaussian"] = {
            "expected": "no low-error low-params point; should resist compression",
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
    config = LoopConfig(
        n_generations=50,
        n_initial=8,
        max_bond=16,
        seed=20260424,
        als_sweeps=1,  # Phase 2: constrained refinement
    )
    shape = (12,) * 6  # 12^6 = 2,985,984 entries

    functions = [
        product_of_coords(shape=shape),
        sum_of_squares(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
    ]
    func_labels = [f.label for f in functions]
    frontier_labels = [f.label for f in functions if f.tier == "frontier"]

    # ---- Stage 1: lineage check before any evolution. Cheap; gates downstream interpretation.
    print("STAGE 1 — lineage audit")
    samples = {f.label: f.sample() for f in functions}
    lineage = lineage_audit(
        samples=samples,
        frontier_labels=frontier_labels,
        cosine_threshold=0.9,
        r2_threshold=0.95,
    )
    print(f"  pairwise flags: {len(lineage['pairwise']['flags'])}")
    for pair, cos in lineage["pairwise"]["matrix"].items():
        print(f"    cos({pair}) = {cos:+.3f}")
    for label, sp in lineage["frontier_in_calibration_basis"].items():
        print(f"  span_check[{label}]: R^2 = {sp['r_squared']:.3f} -> {sp['verdict']}")

    # ---- Stage 2: spectral decay (function-level intrinsic descriptor).
    print("\nSTAGE 2 — spectral decay (function-level)")
    func_descriptors: dict[str, dict] = {}
    for f in functions:
        sd = spectral_decay(samples[f.label])
        func_descriptors[f.label] = {
            "spectral_alpha": sd["alpha"],
            "spectral_fit_r2": sd["fit_r2"],
            "spectral_bond": sd["bond"],
            "spectral_note": sd.get("note"),
        }
        alpha_str = (
            "inf" if sd["alpha"] == float("inf") else f"{sd['alpha']:.3f}"
        )
        r2_str = "n/a" if sd["fit_r2"] is None else f"{sd['fit_r2']:.3f}"
        print(f"  [{f.label}] alpha={alpha_str} R^2={r2_str} note={sd.get('note')}")

    # ---- Stage 3: MAP-Elites with constrained ALS refinement.
    print(f"\nSTAGE 3 — MAP-Elites (als_sweeps={config.als_sweeps}) on {len(functions)} functions")
    archives: dict[str, Archive] = {}
    for f in functions:
        t_fn = time.time()
        arc = run(f, config=config, spec=spec)
        dt = time.time() - t_fn
        s = arc.summary()
        # Average refinement gain (where applicable)
        gains = [
            e.extras["refinement_gain"]
            for e in arc.history
            if e.extras and "refinement_gain" in e.extras
        ]
        gain_str = f"avg_gain={np.mean(gains):.3e}" if gains else "no_refinement"
        print(
            f"  [{f.label}] cells={s['n_cells_occupied']} pareto={s['pareto_front_size']} "
            f"min_err={s['min_error']:.3e} min_params={s['min_params']} "
            f"{gain_str} elapsed={dt:.1f}s"
        )
        archives[f.label] = arc

    # ---- Stage 4: stability per Pareto elite.
    print("\nSTAGE 4 — stability under perturbation (Pareto elites only)")
    stability_records: dict[str, list[dict]] = {}
    for label, arc in archives.items():
        records = []
        for elite in arc.pareto_front()[:5]:  # top 5 by params, cheap
            stab = stability_under_perturbation(
                samples[label], elite.ranks, noise_level=1e-3, n_trials=3,
                seed=config.seed,
            )
            records.append({
                "ranks": list(elite.ranks),
                "n_params": elite.n_params,
                "stability": stab,
            })
        stability_records[label] = records
        if records:
            ratios = [r["stability"]["stability_ratio"] for r in records]
            print(
                f"  [{label}] pareto_n={len(records)} "
                f"stability_ratio: median={np.median(ratios):.2e} "
                f"min={np.min(ratios):.2e} max={np.max(ratios):.2e}"
            )

    # ---- Stage 5: descriptor correlation diagnostic.
    print("\nSTAGE 5 — descriptor correlation diagnostic")
    per_function_corr: dict[str, dict] = {}
    for label, arc in archives.items():
        ca = correlation_audit(
            arc, threshold=0.9,
            function_level_descriptors=func_descriptors[label],
        )
        per_function_corr[label] = ca
        if ca.get("warning"):
            print(f"  [{label}] WARN: {ca['warning']}")
            for f_pair in ca.get("flagged", []):
                print(f"    {f_pair['pair']}: r={f_pair['correlation']:+.3f}")
        else:
            print(f"  [{label}] no flagged pairs (matrix: "
                  f"{', '.join(f'{k}={v:+.2f}' for k, v in ca['matrix'].items())})")

    cross = cross_function_audit(archives, func_descriptors)
    print(
        f"  CROSS: spectral_alpha vs log10(min_error) corr = {cross['spectral_alpha_vs_log_min_error']}"
    )

    # ---- Stage 6: calibration verdicts.
    print("\nSTAGE 6 — calibration verdicts")
    verdicts = _check_calibration(archives)
    for k, v in verdicts.items():
        print(f"  [{k}] {v}")

    # ---- Dump.
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"phase2_{ts}.json"
    payload = {
        "experiment": "zoo_phase2",
        "timestamp": ts,
        "config": asdict(config),
        "grid_spec": asdict(spec),
        "shape": list(shape),
        "function_descriptors": func_descriptors,
        "lineage": lineage,
        "archives": {k: _archive_to_jsonable(v) for k, v in archives.items()},
        "stability_per_function": stability_records,
        "correlation_audit_per_function": per_function_corr,
        "cross_function_audit": cross,
        "calibration_verdicts": verdicts,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0 if verdicts["overall"]["all_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
