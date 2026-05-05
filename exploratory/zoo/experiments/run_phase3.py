"""Phase 3 driver — descriptor collapse audit.

Incorporates external-review feedback:
  - Formal gauge-invariant stability + subspace-angle cross-check
  - Bounded spectral descriptor (effective_rank_at_threshold)
  - Multi-seed (5 seeds per function) with median + IQR aggregation
  - One additional frontier function (Runge) for cross-function correlation
  - Bond-rank distribution descriptors (rank_entropy, rank_concentration)
  - Rank-ceiling null overlay
  - Branch A evaluation: does the collapse clear under rank-orthogonal descriptors?

Branch A gate (primary output): per-function correlations of
(log_params, log_error, rank_entropy, rank_concentration, refinement_gain)
pooled across seeds. If at least one non-structural pair has |r| < 0.9 on
the frontier functions, Branch A passes.
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
from zoo.functions.frontier import pairwise_tanh, runge_dim
from zoo.map_elites.grid import Archive, GridSpec
from zoo.map_elites.loop import LoopConfig
from zoo.map_elites.multi_seed import MultiSeedResult, run_multi_seed
from zoo.descriptors.spectral import spectral_decay, effective_rank_at_threshold
from zoo.descriptors.stability import stability_under_perturbation
from zoo.descriptors.subspace_stability import subspace_stability
from zoo.descriptors.rank_profile import rank_profile_summary
from zoo.lineage.check import lineage_audit
from zoo.nulls.rank_ceiling import null_curve


STRUCTURAL_PAIRS = {
    # These always correlate by construction and should not be counted as collapse.
    frozenset({"avg_rank", "log_params"}),
    frozenset({"max_rank", "log_params"}),
    frozenset({"max_rank", "avg_rank"}),
}


def _pooled_descriptors(msr: MultiSeedResult) -> dict[str, np.ndarray]:
    """Stack per-evaluation descriptors across all seeds for correlation analysis."""
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


def _correlation_matrix(cols: dict[str, np.ndarray], threshold: float = 0.9) -> dict:
    """Pairwise Pearson across columns, flag non-structural pairs above threshold."""
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


def _branch_a_verdict(per_function_audits: dict[str, dict],
                      frontier_labels: list[str]) -> dict:
    """Branch A passes if at least one frontier function has a
    non-structural pair BELOW threshold involving a rank-orthogonal
    descriptor (rank_entropy, rank_concentration, or refinement_gain).
    """
    rank_orth = {"rank_entropy", "rank_concentration", "refinement_gain"}
    per_function = {}
    any_pass = False
    for label in frontier_labels:
        audit = per_function_audits.get(label)
        if audit is None:
            continue
        matrix = audit["matrix"]
        # For each rank-orthogonal descriptor, is |corr(., log_params)| < 0.9?
        decoupled_axes = []
        for key in rank_orth:
            pair_key = None
            if f"{key}|log_params" in matrix:
                pair_key = f"{key}|log_params"
            elif f"log_params|{key}" in matrix:
                pair_key = f"log_params|{key}"
            if pair_key is None:
                continue
            r = matrix[pair_key]
            if abs(r) < 0.9:
                decoupled_axes.append({"axis": key, "corr_with_log_params": r})
        verdict = "PASS" if decoupled_axes else "FAIL"
        per_function[label] = {
            "verdict": verdict,
            "decoupled_axes": decoupled_axes,
            "flagged_nonstructural_pairs": len(audit["flagged_nonstructural"]),
        }
        if verdict == "PASS":
            any_pass = True
    return {"any_frontier_passes": any_pass, "per_frontier_function": per_function}


def _check_calibration(msr_by_label: dict[str, MultiSeedResult]) -> dict:
    verdicts = {}
    contract = {
        "prod_x": {"max_log_params": 2.5, "max_rel_err": 1e-6, "expected_rank": 1},
        "sum_of_squares": {"max_log_params": 2.7, "max_rel_err": 1e-6, "expected_rank": 2},
    }
    for label, c in contract.items():
        msr = msr_by_label.get(label)
        if msr is None:
            continue
        # For each seed, check if the contract was met; verdict = median vote
        per_seed_hits = []
        min_errors = []
        for arc in msr.archives:
            hits = [
                e for e in arc.cells.values()
                if np.log10(max(1, e.n_params)) <= c["max_log_params"]
                and e.rel_error <= c["max_rel_err"]
            ]
            per_seed_hits.append(len(hits))
            min_errors.append(arc.summary().get("min_error"))
        verdict = "PASS" if all(h > 0 for h in per_seed_hits) else "FAIL"
        verdicts[label] = {
            "expected_tt_rank": c["expected_rank"],
            "contract": f"log10(params) <= {c['max_log_params']} AND rel_err <= {c['max_rel_err']:.0e}",
            "per_seed_hits": per_seed_hits,
            "min_errors_per_seed": min_errors,
            "verdict": verdict,
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
        "all_pass": all(v.get("verdict") == "PASS" for v in verdicts.values() if "verdict" in v)
    }
    return verdicts


def main() -> int:
    t0 = time.time()
    spec = GridSpec()
    base_config = LoopConfig(
        n_generations=50, n_initial=8, max_bond=16, seed=0, als_sweeps=1,
    )
    shape = (12,) * 6
    seeds = [20260424, 20260425, 20260426, 20260427, 20260428]

    functions = [
        product_of_coords(shape=shape),
        sum_of_squares(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
        runge_dim(shape=shape),
    ]
    frontier_labels = [f.label for f in functions if f.tier == "frontier"]

    # STAGE 1 — lineage
    print("STAGE 1 — lineage audit")
    samples = {f.label: f.sample() for f in functions}
    lineage = lineage_audit(
        samples=samples, frontier_labels=frontier_labels,
        cosine_threshold=0.9, r2_threshold=0.95,
    )
    for pair, cos in lineage["pairwise"]["matrix"].items():
        print(f"    cos({pair}) = {cos:+.3f}")
    for label, sp in lineage["frontier_in_calibration_basis"].items():
        print(f"    span[{label}] R^2={sp['r_squared']:.3f} -> {sp['verdict']}")

    # STAGE 2 — function-level descriptors (spectral + effective_rank + stability)
    print("\nSTAGE 2 — function-level descriptors")
    func_descriptors: dict[str, dict] = {}
    for f in functions:
        sd = spectral_decay(samples[f.label])
        er = effective_rank_at_threshold(samples[f.label], threshold=1e-8)
        func_descriptors[f.label] = {
            "spectral_alpha": sd["alpha"],
            "spectral_fit_r2": sd["fit_r2"],
            "effective_rank": er["effective_rank"],
            "log_effective_rank": er.get("log_effective_rank"),
        }
        alpha_str = ("inf" if sd["alpha"] == float("inf")
                     else f"{sd['alpha']:.3f}")
        print(f"  [{f.label}] eff_rank={er['effective_rank']} / {er['ceiling']}   "
              f"alpha={alpha_str}")

    # STAGE 3 — multi-seed MAP-Elites
    print(f"\nSTAGE 3 — multi-seed MAP-Elites ({len(seeds)} seeds per function)")
    msr_by_label: dict[str, MultiSeedResult] = {}
    for f in functions:
        t_fn = time.time()
        msr = run_multi_seed(f, base_config, spec, seeds)
        dt = time.time() - t_fn
        agg = msr.aggregate_summary()
        print(f"  [{f.label}] cells(med)={agg['n_cells_occupied']['median']:.0f} "
              f"pareto(med)={agg['pareto_front_size']['median']:.0f} "
              f"min_err(med)={agg['min_error']['median']:.2e} "
              f"elapsed={dt:.1f}s")
        msr_by_label[f.label] = msr

    # STAGE 4 — stability per Pareto elite (first-seed archives only; cross-seed is expensive)
    print("\nSTAGE 4 — stability + subspace-stability (Pareto elites, seed 0 only)")
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
            sub_ratios = [1.0 / max(r["subspace_stability"]["mean_angle"], 1e-15)
                          for r in records]
            # Agreement between metrics: Spearman-style rank agreement
            order_recon = np.argsort(recon_ratios)
            order_sub = np.argsort(sub_ratios)
            # Kendall tau simplified: count pairwise agreements
            n = len(order_recon)
            agree = 0
            total = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if (recon_ratios[i] - recon_ratios[j]) * (sub_ratios[i] - sub_ratios[j]) > 0:
                        agree += 1
                    total += 1
            tau_like = agree / total if total > 0 else None
            print(f"  [{label}] pareto_n={n} recon_stab_med={np.median(recon_ratios):.2e} "
                  f"sub_stab_med={np.median(sub_ratios):.2e} metric_agreement={tau_like}")

    # STAGE 5 — descriptor correlation audit (pooled across seeds)
    print("\nSTAGE 5 — descriptor correlation audit (pooled across seeds)")
    per_function_audits: dict[str, dict] = {}
    for label, msr in msr_by_label.items():
        cols = _pooled_descriptors(msr)
        audit = _correlation_matrix(cols, threshold=0.9)
        per_function_audits[label] = audit
        n_flag = len(audit["flagged_nonstructural"])
        print(f"  [{label}] n_evals={len(next(iter(cols.values())))} "
              f"non_structural_flags={n_flag}")
        for fp in audit["flagged_nonstructural"]:
            print(f"      {fp['pair']}: r={fp['correlation']:+.3f}")

    # STAGE 6 — Branch A verdict
    print("\nSTAGE 6 — Branch A verdict (does a rank-orthogonal descriptor decouple?)")
    branch_a = _branch_a_verdict(per_function_audits, frontier_labels)
    print(f"  any_frontier_passes = {branch_a['any_frontier_passes']}")
    for label, v in branch_a["per_frontier_function"].items():
        print(f"  [{label}] {v['verdict']}: decoupled_axes = {v['decoupled_axes']}")

    # STAGE 7 — rank-ceiling null
    print("\nSTAGE 7 — rank-ceiling null curve")
    null = null_curve(shape, rank_levels=[1, 2, 4, 8, 12, 16],
                      n_trials=2, seed=99, max_bond=16)
    for rec in null:
        print(f"  r={rec['ranks'][0]:2d} params={rec['n_params']:7d} "
              f"null_err={rec['mean_error']:.3f} +/- {rec['std_error']:.3f}")

    # STAGE 8 — calibration verdicts
    print("\nSTAGE 8 — calibration verdicts")
    verdicts = _check_calibration(msr_by_label)
    for k, v in verdicts.items():
        print(f"  [{k}] {v}")

    # DUMP
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"phase3_{ts}.json"

    def _arc_to_jsonable(arc: Archive) -> dict:
        return {
            "function_label": arc.function_label,
            "summary": arc.summary(),
            "cells": [{"cell": list(k), "elite": asdict(v)}
                      for k, v in sorted(arc.cells.items())],
            "pareto_front": [asdict(e) for e in arc.pareto_front()],
            "history": [asdict(e) for e in arc.history],
        }

    payload = {
        "experiment": "zoo_phase3",
        "timestamp": ts,
        "config": asdict(base_config),
        "seeds": seeds,
        "grid_spec": asdict(spec),
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
        "correlation_audits": per_function_audits,
        "branch_a_verdict": branch_a,
        "rank_ceiling_null": null,
        "calibration_verdicts": verdicts,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0 if (branch_a["any_frontier_passes"] and verdicts["overall"]["all_pass"]) else 2


if __name__ == "__main__":
    sys.exit(main())
