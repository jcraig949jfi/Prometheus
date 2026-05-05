"""Phase 5 — diversified seeds + larger rank-shift + DMRG (now actually on).

Reviewer 2026-04-25 priorities:
  1. Diversified initial seeds + larger rank-shift mutation (THE proof)
  2. DMRG instrument-trust — verified by unit_test_dmrg.py (separate)
  3. 5+ seeds (restored from 3 in Phase 4)

Plus a critical bug fix: multi_seed.py was silently dropping dmrg_sweeps and
mutation config from per-seed LoopConfig copies. Phase 5 is the first run where
the configured DMRG and hybrid mutation actually execute.

Branch-A claim under test: with the entropy axis actually explored (peaked +
bimodal seeds, shift_magnitude=4), does the within-band MI between log_params
and rank_entropy drop toward null, or does the upper-rim coupling persist?

Outcome A: entropy fills [~0.78, 1.609] AND within-band MI drops to <= 3x null.
           Branch A fully validated; v3 ridge was pure search starvation.
Outcome B: entropy fills but within-band MI stays >> null.
           Coupling generalizes beyond upper rim; real TT-geometry signal.
Outcome C: entropy partially fills.
           Mutation budget is the binding constraint; tune further in Phase 5.1.
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
from zoo.descriptors.spectral import spectral_decay, effective_rank_at_threshold
from zoo.descriptors.stability import stability_under_perturbation
from zoo.descriptors.subspace_stability import subspace_stability
from zoo.lineage.check import lineage_audit
from zoo.diagnostics.nonlinear import (
    distance_correlation, knn_mutual_information, nonlinear_audit,
)


STRUCTURAL_PAIRS = {
    frozenset({"avg_rank", "log_params"}),
    frozenset({"max_rank", "log_params"}),
    frozenset({"max_rank", "avg_rank"}),
}


def _pooled(msr: MultiSeedResult) -> dict[str, np.ndarray]:
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
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def _within_band_mi_with_null(lp: np.ndarray, re: np.ndarray, n_bands: int = 4,
                              n_shuffles: int = 100, seed: int = 99,
                              k: int = 3) -> dict:
    """For each log_params quartile band, compute MI(log_params, rank_entropy)
    and a within-band shuffled null at matched n. Returns per-band records."""
    rng = np.random.default_rng(seed)
    edges = np.quantile(lp, np.linspace(0, 1, n_bands + 1))
    bands = []
    for b in range(n_bands):
        lo, hi = edges[b], edges[b + 1]
        if b == n_bands - 1:
            mask = (lp >= lo) & (lp <= hi)
        else:
            mask = (lp >= lo) & (lp < hi)
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
            "band": b,
            "lp_range": [float(lo), float(hi)],
            "n": int(mask.sum()),
            "obs_mi": float(mi_obs),
            "null_mean": float(nulls.mean()),
            "null_p99": float(np.percentile(nulls, 99)),
            "obs_over_null": float(mi_obs / max(nulls.mean(), 1e-12)),
            "p_value": float((nulls >= mi_obs).mean()),
        })
    return {"bands": bands, "n_bands": n_bands}


def _branch_a_outcome(per_function_band_mi: dict[str, dict],
                      entropy_coverage: dict[str, dict]) -> dict:
    """Adjudicate Outcome A / B / C per the Phase 5 plan."""
    out = {}
    achievable_lo = 0.778  # rank profile (16, 1, 1, 1, 1) entropy at d=6, max_bond=16
    achievable_hi = 1.609
    achievable_w = achievable_hi - achievable_lo

    for label, bands in per_function_band_mi.items():
        cov = entropy_coverage.get(label, {})
        coverage_frac = cov.get("coverage_frac_of_achievable", 0.0)
        max_obs_over_null = max(
            (b.get("obs_over_null", 0.0) for b in bands.get("bands", [])
             if not b.get("skipped")),
            default=0.0,
        )
        # Outcome rules
        entropy_filled = coverage_frac >= 0.6  # at least 60% of achievable range visited
        mi_decoupled = max_obs_over_null <= 3.0  # within 3x of null (per promotion criteria)

        if entropy_filled and mi_decoupled:
            outcome = "A_BRANCH_A_VALIDATED"
        elif entropy_filled and not mi_decoupled:
            outcome = "B_GEOMETRY_SIGNAL"
        elif not entropy_filled:
            outcome = "C_PARTIAL_FILL"
        else:
            outcome = "UNKNOWN"

        out[label] = {
            "entropy_coverage_frac": coverage_frac,
            "entropy_filled (>=0.6)": entropy_filled,
            "max_within_band_obs_over_null": max_obs_over_null,
            "mi_decoupled (<=3x)": mi_decoupled,
            "outcome": outcome,
        }
    return out


def _entropy_coverage(msr: MultiSeedResult) -> dict:
    """Per-function entropy distribution stats relative to achievable [0.778, 1.609]."""
    pool = _pooled(msr)
    re = pool.get("rank_entropy", np.array([]))
    if len(re) == 0:
        return {}
    achievable_lo = 0.778
    achievable_hi = 1.609
    return {
        "n_evals": int(len(re)),
        "mean": float(re.mean()),
        "std": float(re.std()),
        "min": float(re.min()),
        "max": float(re.max()),
        "observed_range_width": float(re.max() - re.min()),
        "achievable_range_width": achievable_hi - achievable_lo,
        "coverage_frac_of_achievable": float(
            (re.max() - re.min()) / (achievable_hi - achievable_lo)
        ),
    }


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


def main() -> int:
    t0 = time.time()
    base_config = LoopConfig(
        n_generations=80,            # P5: more gens to let diversified seeds explore
        n_initial=12,                # P5: more initial seeds (was 8) to fit 3 groups
        max_bond=16,
        seed=0,
        als_sweeps=0,
        dmrg_sweeps=1,                # NOW actually runs (multi_seed bug fixed)
        dmrg_rel_tol=1e-10,
        mutation=MutationConfig(strategy="hybrid", p_shift=0.5, shift_magnitude=4),  # P5: 4 not 1
        seed_strategy="diversified",  # P5: peaked + bimodal + uniform
    )
    grid = grid_params_entropy()
    shape = (12,) * 6
    seeds = [20260424, 20260425, 20260426, 20260427, 20260428]  # 5 seeds (restored)

    functions = [
        product_of_coords(shape=shape),
        sum_of_squares(shape=shape),
        random_gaussian(shape=shape),
        pairwise_tanh(shape=shape),
        runge_dim(shape=shape),
        heat_smoothed_paraboloid(shape=shape, t=0.005),  # smaller t = sharper, more frontier
    ]
    frontier_labels = [f.label for f in functions if f.tier == "frontier"]

    print(f"Phase 5 — diversified seeds (12 initial), shift_magnitude=4, "
          f"DMRG=1 sweep, n_seeds={len(seeds)}, n_gens={base_config.n_generations}")
    print()

    # STAGE 1 — function descriptors
    print("STAGE 1 — function-level descriptors")
    samples = {f.label: f.sample() for f in functions}
    func_descriptors = {}
    for f in functions:
        sd = spectral_decay(samples[f.label])
        er = effective_rank_at_threshold(samples[f.label], threshold=1e-8)
        func_descriptors[f.label] = {
            "spectral_alpha": sd["alpha"],
            "effective_rank": er["effective_rank"],
        }
        a = "inf" if sd["alpha"] == float("inf") else f"{sd['alpha']:.3f}"
        print(f"  [{f.label}] eff_rank={er['effective_rank']:4d}/{er['ceiling']}  alpha={a}")

    # STAGE 2 — multi-seed MAP-Elites
    print(f"\nSTAGE 2 — Branch-A MAP-Elites ({len(seeds)} seeds, DMRG actually on)")
    msr_by_label = {}
    for f in functions:
        t_fn = time.time()
        msr = run_multi_seed(f, base_config, grid, seeds)
        dt = time.time() - t_fn
        agg = msr.aggregate_summary()
        cov = _entropy_coverage(msr)
        print(f"  [{f.label}] cells_med={agg['n_cells_occupied']['median']:.0f} "
              f"min_err_med={agg['min_error']['median']:.2e} "
              f"entropy_range=[{cov['min']:.3f},{cov['max']:.3f}] "
              f"coverage={cov['coverage_frac_of_achievable']*100:.0f}% "
              f"elapsed={dt:.1f}s")
        msr_by_label[f.label] = msr

    # STAGE 3 — entropy coverage
    entropy_coverage = {l: _entropy_coverage(m) for l, m in msr_by_label.items()}

    # STAGE 4 — within-band MI with within-band null
    print("\nSTAGE 4 — within-band MI vs within-band null")
    per_function_band_mi = {}
    for label in frontier_labels:
        cols = _pooled(msr_by_label[label])
        result = _within_band_mi_with_null(
            cols["log_params"], cols["rank_entropy"],
            n_bands=4, n_shuffles=100, seed=99,
        )
        per_function_band_mi[label] = result
        print(f"  [{label}]")
        for b in result["bands"]:
            if b.get("skipped"):
                print(f"    band {b['band']}: n={b['n']} skipped")
                continue
            print(f"    band {b['band']}: n={b['n']:3d}  obs_MI={b['obs_mi']:.3f}  "
                  f"null_mean={b['null_mean']:.3f}  obs/null={b['obs_over_null']:5.1f}  "
                  f"p={b['p_value']:.3f}")

    # STAGE 5 — Branch A outcome
    print("\nSTAGE 5 — Branch A outcome adjudication")
    branch_a = _branch_a_outcome(per_function_band_mi, entropy_coverage)
    for label, v in branch_a.items():
        print(f"  [{label}] {v['outcome']}")
        print(f"    entropy_coverage = {v['entropy_coverage_frac']:.1%}")
        print(f"    max obs/null     = {v['max_within_band_obs_over_null']:.1f}")

    # STAGE 6 — calibration
    print("\nSTAGE 6 — calibration")
    verdicts = _check_calibration(msr_by_label)
    for k, v in verdicts.items():
        print(f"  [{k}] {v.get('verdict', v)}")

    # STAGE 7 — pooled-history Pearson + nonlinear audit
    print("\nSTAGE 7 — full-sample Pearson + nonlinear audits on (log_params, rank_entropy)")
    full_audits = {}
    for label in frontier_labels:
        cols = _pooled(msr_by_label[label])
        n = len(cols["log_params"])
        # Subsample for nonlinear audit at n=150 for tractability
        if n > 150:
            rng = np.random.default_rng(99)
            idx = rng.choice(n, size=150, replace=False)
            cols_sub = {k: v[idx] for k, v in cols.items()}
        else:
            cols_sub = cols
        x, y = cols_sub["log_params"], cols_sub["rank_entropy"]
        pearson = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else 0.0
        if x.std() > 0 and y.std() > 0:
            xn = (x - x.mean()) / x.std()
            yn = (y - y.mean()) / y.std()
            dc = distance_correlation(xn, yn)
            mi = knn_mutual_information(xn, yn, k=3)
        else:
            dc = mi = 0.0
        full_audits[label] = {
            "n_evals_total": int(n),
            "n_evals_subsampled": int(len(x)),
            "pearson_r": pearson,
            "dcor": float(dc),
            "ksg_mi": float(mi),
        }
        print(f"  [{label}] n={n}  pearson={pearson:+.3f}  dcor={dc:.3f}  mi={mi:.3f}")

    # DUMP
    out_dir = Path(__file__).resolve().parent.parent / "results"
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"phase5_{ts}.json"

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
        "experiment": "zoo_phase5",
        "timestamp": ts,
        "config": asdict(base_config),
        "seeds": seeds,
        "shape": list(shape),
        "function_descriptors": func_descriptors,
        "multi_seed_summaries": {k: v.aggregate_summary() for k, v in msr_by_label.items()},
        "archives_per_function_seed_0": {
            k: _arc_to_jsonable(v.archives[0]) for k, v in msr_by_label.items()
        },
        "pooled_history_per_function": {
            k: [asdict(e) for a in v.archives for e in a.history]
            for k, v in msr_by_label.items()
        },
        "entropy_coverage": entropy_coverage,
        "within_band_mi_with_null": per_function_band_mi,
        "branch_a_outcome": branch_a,
        "full_sample_audits": full_audits,
        "calibration_verdicts": verdicts,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
