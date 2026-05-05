"""Phase 4 driver — Branch-A grid under rank-shift mutation + two-site DMRG.

Directly addresses external-review feedback on v2.0:
  1. Rank-shift mutation operator (close the operator-descriptor gap)
  2. Nonlinear collapse audit (distance correlation + KSG MI)
  3. Two-site DMRG (adaptive-rank refinement; real refinement_gain)
  4. Heat-PDE frontier function (spectral stress-test)
  5. Placement grid on (log_params, rank_entropy) — Branch A primary grid

The validation condition for Phase 4:
  - All calibration anchors still PASS under rank-shift + DMRG.
  - Phase-4 Branch-A grid occupies MORE cells than the Phase-3 grid on
    frontier functions (direct evidence the 2D plane is navigable).
  - Both Pearson and nonlinear audits on (log_params, rank_entropy) for
    frontier functions return no non-structural flags.

Deferred to Phase 5:
  - Stability as an active MAP-Elites tie-breaker.
  - Multi-seed for DMRG to keep runtime bounded.
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
from zoo.map_elites.grid import Archive, GridSpec, grid_params_entropy
from zoo.map_elites.loop import LoopConfig, run
from zoo.map_elites.mutation import MutationConfig
from zoo.map_elites.multi_seed import MultiSeedResult, run_multi_seed
from zoo.descriptors.spectral import spectral_decay, effective_rank_at_threshold
from zoo.descriptors.stability import stability_under_perturbation
from zoo.descriptors.subspace_stability import subspace_stability
from zoo.lineage.check import lineage_audit
from zoo.nulls.rank_ceiling import null_curve
from zoo.diagnostics.nonlinear import (
    distance_correlation, knn_mutual_information, nonlinear_audit,
)


STRUCTURAL_PAIRS = {
    frozenset({"avg_rank", "log_params"}),
    frozenset({"max_rank", "log_params"}),
    frozenset({"max_rank", "avg_rank"}),
    # rank_entropy vs rank_concentration: partially tautological (both summary statistics
    # of the same rank profile), but they measure complementary aspects — log one expects
    # moderate correlation but not perfect. Not excluded.
}


def _pooled_descriptors(msr: MultiSeedResult) -> dict[str, np.ndarray]:
    rows = []
    for arc in msr.archives:
        for e in arc.history:
            x = e.extras or {}
            rows.append({
                "log_params": float(np.log10(max(1, e.n_params))),
                "log_error": float(np.log10(max(1e-15, e.rel_error))),
                "avg_rank": float(x.get("avg_rank", np.mean(e.ranks))),
                "max_rank": float(x.get("max_rank", np.max(e.ranks))),
                "rank_entropy": float(x.get("rank_entropy", 0.0)),
                "rank_concentration": float(x.get("rank_concentration", 1.0)),
                "refinement_gain": float(x.get("refinement_gain", 0.0)),
            })
    if not rows:
        return {}
    keys = list(rows[0].keys())
    return {k: np.array([r[k] for r in rows]) for k in keys}


def _pearson_audit(cols: dict[str, np.ndarray], threshold: float = 0.9) -> dict:
    keys = list(cols)
    matrix: dict[str, float] = {}
    flagged: list[dict] = []
    for a, b in combinations(keys, 2):
        x, y = cols[a], cols[b]
        if x.std() == 0 or y.std() == 0:
            r = 0.0
        else:
            r = float(np.corrcoef(x, y)[0, 1])
        matrix[f"{a}|{b}"] = r
        if abs(r) >= threshold and frozenset({a, b}) not in STRUCTURAL_PAIRS:
            flagged.append({"pair": [a, b], "correlation": r})
    return {"matrix": matrix, "flagged_nonstructural": flagged, "threshold": threshold}


def _check_calibration(msr_by_label: dict[str, MultiSeedResult]) -> dict:
    verdicts = {}
    contract = {
        "prod_x": {"max_log_params": 2.5, "max_rel_err": 1e-6},
        "sum_of_squares": {"max_log_params": 2.7, "max_rel_err": 1e-6},
    }
    for label, c in contract.items():
        msr = msr_by_label.get(label)
        if msr is None:
            continue
        per_seed_hits = []
        min_errors = []
        for arc in msr.archives:
            hits = [e for e in arc.cells.values()
                    if np.log10(max(1, e.n_params)) <= c["max_log_params"]
                    and e.rel_error <= c["max_rel_err"]]
            per_seed_hits.append(len(hits))
            min_errors.append(arc.summary().get("min_error"))
        verdicts[label] = {
            "contract": f"log10(params) <= {c['max_log_params']} AND rel_err <= {c['max_rel_err']:.0e}",
            "per_seed_hits": per_seed_hits,
            "min_errors_per_seed": min_errors,
            "verdict": "PASS" if all(h > 0 for h in per_seed_hits) else "FAIL",
        }
    rand = msr_by_label.get("random_gaussian")
    if rand is not None:
        suspicious_per_seed = []
        for arc in rand.archives:
            susp = [e for e in arc.pareto_front()
                    if e.rel_error < 1e-2 and np.log10(max(1, e.n_params)) < 4.0]
            suspicious_per_seed.append(len(susp))
        verdicts["random_gaussian"] = {
            "contract": "no low-error low-params point; resists compression",
            "suspicious_per_seed": suspicious_per_seed,
            "verdict": "PASS" if all(s == 0 for s in suspicious_per_seed) else "FAIL",
        }
    verdicts["overall"] = {
        "all_pass": all(v.get("verdict") == "PASS" for v in verdicts.values() if "verdict" in v),
    }
    return verdicts


def _branch_a_verdict(p4_grid_audits: dict[str, dict],
                      p4_nonlinear_audits: dict[str, dict],
                      frontier_labels: list[str]) -> dict:
    """Phase 4 Branch A passes on a frontier function iff:
      - The (log_params, rank_entropy) pair has |Pearson| < 0.9 AND
      - dCor and MI also below their thresholds.
    """
    per_function = {}
    any_pass = False
    for label in frontier_labels:
        p_audit = p4_grid_audits.get(label)
        n_audit = p4_nonlinear_audits.get(label)
        if p_audit is None or n_audit is None:
            continue
        # Pick out (log_params, rank_entropy) row
        key_candidates = ["log_params|rank_entropy", "rank_entropy|log_params"]
        pearson_r = None
        dcor = None
        mi = None
        for k in key_candidates:
            if k in p_audit["matrix"]:
                pearson_r = p_audit["matrix"][k]
            if k in n_audit["distance_correlation_matrix"]:
                dcor = n_audit["distance_correlation_matrix"][k]
            if k in n_audit["ksg_mi_matrix"]:
                mi = n_audit["ksg_mi_matrix"][k]
        verdict = "PASS" if (pearson_r is not None and abs(pearson_r) < 0.9
                             and (dcor is None or dcor < 0.5)
                             and (mi is None or mi < 0.5)) else "FAIL"
        per_function[label] = {
            "pearson_log_params_rank_entropy": pearson_r,
            "dcor_log_params_rank_entropy": dcor,
            "mi_log_params_rank_entropy": mi,
            "verdict": verdict,
        }
        if verdict == "PASS":
            any_pass = True
    return {"any_frontier_passes": any_pass, "per_frontier_function": per_function}


def main() -> int:
    t0 = time.time()

    # Phase 4 config: hybrid mutation (50/50 classical / rank-shift),
    # two-site DMRG refinement with 1 sweep budget.
    base_config = LoopConfig(
        n_generations=50,
        n_initial=8,
        max_bond=16,
        seed=0,
        als_sweeps=0,              # disabled
        dmrg_sweeps=1,             # enabled (replaces ALS as default)
        dmrg_rel_tol=1e-10,
        mutation=MutationConfig(strategy="hybrid", p_shift=0.5),
    )
    # Phase 4 primary grid: Branch A (log_params, rank_entropy)
    grid_a = grid_params_entropy()
    shape = (12,) * 6
    # Multi-seed is expensive with DMRG. Drop to 3 seeds for Phase 4.
    seeds = [20260424, 20260425, 20260426]

    functions = [
        product_of_coords(shape=shape),
        sum_of_squares(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
        runge_dim(shape=shape),
        heat_smoothed_paraboloid(shape=shape, t=0.02),
    ]
    frontier_labels = [f.label for f in functions if f.tier == "frontier"]

    # STAGE 1 — lineage
    print("STAGE 1 — lineage audit (full catalog, 6 functions)")
    samples = {f.label: f.sample() for f in functions}
    lineage = lineage_audit(
        samples=samples, frontier_labels=frontier_labels,
        cosine_threshold=0.9, r2_threshold=0.95,
    )
    for pair, cos in lineage["pairwise"]["matrix"].items():
        print(f"    cos({pair}) = {cos:+.3f}")
    for label, sp in lineage["frontier_in_calibration_basis"].items():
        print(f"    span[{label}] R^2={sp['r_squared']:.3f} -> {sp['verdict']}")

    # STAGE 2 — function-level descriptors
    print("\nSTAGE 2 — function-level descriptors")
    func_descriptors: dict[str, dict] = {}
    for f in functions:
        sd = spectral_decay(samples[f.label])
        er = effective_rank_at_threshold(samples[f.label], threshold=1e-8)
        func_descriptors[f.label] = {
            "spectral_alpha": sd["alpha"],
            "effective_rank": er["effective_rank"],
        }
        alpha_str = "inf" if sd["alpha"] == float("inf") else f"{sd['alpha']:.3f}"
        print(f"  [{f.label}] eff_rank={er['effective_rank']:4d}/{er['ceiling']}   "
              f"alpha={alpha_str}")

    # STAGE 3 — multi-seed MAP-Elites on Branch-A grid
    print(f"\nSTAGE 3 — Branch-A MAP-Elites ({len(seeds)} seeds, DMRG refinement)")
    msr_by_label: dict[str, MultiSeedResult] = {}
    for f in functions:
        t_fn = time.time()
        msr = run_multi_seed(f, base_config, grid_a, seeds)
        dt = time.time() - t_fn
        agg = msr.aggregate_summary()
        print(f"  [{f.label}] cells(med)={agg['n_cells_occupied']['median']:.0f} "
              f"pareto(med)={agg['pareto_front_size']['median']:.0f} "
              f"min_err(med)={agg['min_error']['median']:.2e} "
              f"elapsed={dt:.1f}s")
        msr_by_label[f.label] = msr

    # STAGE 4 — stability (Pareto elites, seed 0 only) for diagnostic continuity
    print("\nSTAGE 4 — stability (seed 0 Pareto elites; post-hoc)")
    stability_records: dict[str, list[dict]] = {}
    for label, msr in msr_by_label.items():
        arc0 = msr.archives[0]
        records = []
        for elite in arc0.pareto_front()[:5]:
            stab = stability_under_perturbation(
                samples[label], elite.ranks, noise_level=1e-3, n_trials=3, seed=seeds[0],
            )
            sub = subspace_stability(
                samples[label], elite.ranks, noise_level=1e-3, n_trials=3, seed=seeds[0],
            )
            records.append({
                "ranks": list(elite.ranks),
                "n_params": elite.n_params,
                "reconstruction_stability": stab,
                "subspace_stability": sub,
            })
        stability_records[label] = records
        if records:
            recon_ratios = [r["reconstruction_stability"]["stability_ratio"] for r in records]
            print(f"  [{label}] n={len(records)} recon_stab_med={np.median(recon_ratios):.2e}")

    # STAGE 5 — Pearson audit (pooled across seeds)
    print("\nSTAGE 5 — Pearson descriptor correlation audit (Phase 3-style)")
    p4_grid_audits: dict[str, dict] = {}
    for label, msr in msr_by_label.items():
        cols = _pooled_descriptors(msr)
        audit = _pearson_audit(cols, threshold=0.9)
        p4_grid_audits[label] = audit
        n_flag = len(audit["flagged_nonstructural"])
        print(f"  [{label}] n_evals={len(next(iter(cols.values())))} "
              f"pearson_nonstruct_flags={n_flag}")
        for fp in audit["flagged_nonstructural"]:
            print(f"      {fp['pair']}: r={fp['correlation']:+.3f}")

    # STAGE 6 — nonlinear audit (Phase 4 addition)
    print("\nSTAGE 6 — nonlinear audit (distance correlation + KSG MI)")
    p4_nonlinear_audits: dict[str, dict] = {}
    for label, msr in msr_by_label.items():
        cols = _pooled_descriptors(msr)
        # Subsample to 150 to keep the n^2 dCor tractable; seeded
        n = len(next(iter(cols.values())))
        if n > 150:
            rng = np.random.default_rng(99)
            idx = rng.choice(n, size=150, replace=False)
            cols_sub = {k: v[idx] for k, v in cols.items()}
        else:
            cols_sub = cols
        audit = nonlinear_audit(cols_sub, dcor_threshold=0.5, mi_threshold=0.5)
        p4_nonlinear_audits[label] = audit
        n_flag = len(audit["flagged"])
        print(f"  [{label}] nonlinear_flags={n_flag}")
        for fp in audit["flagged"]:
            print(f"      {fp['pair']}: dcor={fp['distance_correlation']:.3f} "
                  f"mi={fp['ksg_mi_nats']:.3f}")

    # STAGE 7 — Branch A verdict
    print("\nSTAGE 7 — Branch A verdict on (log_params, rank_entropy) axis")
    branch_a = _branch_a_verdict(p4_grid_audits, p4_nonlinear_audits, frontier_labels)
    print(f"  any_frontier_passes = {branch_a['any_frontier_passes']}")
    for label, v in branch_a["per_frontier_function"].items():
        p = v["pearson_log_params_rank_entropy"]
        dc = v["dcor_log_params_rank_entropy"]
        mi = v["mi_log_params_rank_entropy"]
        p_s = "n/a" if p is None else f"{p:+.3f}"
        dc_s = "n/a" if dc is None else f"{dc:.3f}"
        mi_s = "n/a" if mi is None else f"{mi:.3f}"
        print(f"  [{label}] {v['verdict']}  pearson={p_s}  dcor={dc_s}  mi={mi_s}")

    # STAGE 8 — calibration
    print("\nSTAGE 8 — calibration verdicts")
    verdicts = _check_calibration(msr_by_label)
    for k, v in verdicts.items():
        print(f"  [{k}] {v}")

    # DUMP
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"phase4_{ts}.json"

    def _arc_to_jsonable(arc: Archive) -> dict:
        return {
            "function_label": arc.function_label,
            "axis_names": list(arc.spec.axis_names()),
            "summary": arc.summary(),
            "cells": [{"cell": list(k), "elite": asdict(v)}
                      for k, v in sorted(arc.cells.items())],
            "pareto_front": [asdict(e) for e in arc.pareto_front()],
            "history": [asdict(e) for e in arc.history],
        }

    payload = {
        "experiment": "zoo_phase4",
        "timestamp": ts,
        "config": asdict(base_config),
        "seeds": seeds,
        "grid_spec_axes": list(grid_a.axis_names()),
        "shape": list(shape),
        "function_descriptors": func_descriptors,
        "lineage": lineage,
        "multi_seed_summaries": {k: v.aggregate_summary() for k, v in msr_by_label.items()},
        "archives_per_function_seed_0": {
            k: _arc_to_jsonable(v.archives[0]) for k, v in msr_by_label.items()
        },
        "pooled_history_per_function": {
            k: [asdict(e) for a in v.archives for e in a.history]
            for k, v in msr_by_label.items()
        },
        "stability_records": stability_records,
        "pearson_audits": p4_grid_audits,
        "nonlinear_audits": p4_nonlinear_audits,
        "branch_a_verdict": branch_a,
        "calibration_verdicts": verdicts,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0 if (branch_a["any_frontier_passes"] and verdicts["overall"]["all_pass"]) else 2


if __name__ == "__main__":
    sys.exit(main())
