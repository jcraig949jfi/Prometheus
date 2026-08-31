"""Full Phase-1 pipeline for ONE substrate (synthetic control or real).

Identical code path for controls and real substrates — the instrument is
validated on known geometry and applied unchanged.
"""
from __future__ import annotations

import json
import os

import numpy as np

from .gates import THRESHOLDS, evaluate_gates
from .interface import MenuWrapper, Meter
from .metrics import (graph_metrics, op_census, run_census, run_coverage,
                      run_navigation, select_targets, summarize_navigation)
from .navigators import COMPETITIVE_PAIR, EdgeStore
from .oracle import oracle_reachability

DEFAULT_CFG = {
    "seed": 11000,
    # v4: single source of scale — instrument validation and binding runs
    # use the SAME configuration (the red team flagged the scale mismatch).
    "census_n": 10_000,
    "op_parents": 1200,
    "op_reps": 4,
    "n_cross": 500,
    "rev_sample": 400,
    "n_walks": 64,
    "walk_len": 150,
    "n_ref": 48,
    "k_low": 6,
    "k_high": 6,
    "nav_budget": 1200,
    "nav_plan": [["N1_RESTART_WALK", 3], ["N2_HILLCLIMB", 5],
                 ["N3_NOVELTY", 2], ["N4_RECOMBINER", 5]],
    "coverage_seeds": 2,
    "coverage_budget": 3000,
    # ablation seeds 4: at 2 seeds the collapse gate was unattainable for
    # baselines in [0.15, ~0.21) (total collapse could not reach z=1.96)
    "ablation_seeds": 4,
    "cf_seeds": 2,          # reweight/radius/encoding variants (real only)
}


def _san(x):
    """JSON sanitizer; drops fingerprint objects and private keys."""
    if isinstance(x, dict):
        return {str(k): _san(v) for k, v in x.items()
                if not str(k).startswith("_") and str(k) != "fp"}
    if isinstance(x, (list, tuple)):
        return [_san(v) for v in x]
    if isinstance(x, set):
        return sorted(_san(v) for v in x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def _stratum_rates(rows, nav_name):
    out = {}
    for sname in ("near", "mid", "far"):
        rs = [r for r in rows if r["navigator"] == nav_name and r["stratum"] == sname]
        if rs:
            out[sname] = (sum(r["hit"] for r in rs) / len(rs), len(rs))
    return out


def run_pipeline(sub, cfg: dict, out_dir: str, is_real: bool = False,
                 encoding_variant_factory=None, radius_variant_factory=None,
                 log=print) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    cfg = {**DEFAULT_CFG, **cfg}
    meter = Meter()
    sub.bind_meter(meter)
    store = EdgeStore()
    rng = np.random.default_rng(cfg["seed"])
    res: dict = {"substrate": sub.name, "cfg": {k: v for k, v in cfg.items()}}

    log(f"[{sub.name}] census n={cfg['census_n']}")
    census = run_census(sub, cfg["census_n"], rng, store)
    res["census"] = census

    log(f"[{sub.name}] operator causal census")
    viable_pool = census["_viable_pool"]
    if len(viable_pool) >= 10:
        res["op_census"] = op_census(sub, viable_pool, rng, cfg["op_parents"],
                                     cfg["op_reps"], store, cfg["n_cross"],
                                     cfg["rev_sample"])
    else:
        res["op_census"] = {"pooled_identity_rate": 1.0, "pooled_effective_rate": 0.0,
                            "n_alive_ops": 0, "alive_ops": [], "per_op": {},
                            "identifiability": {"status": "INSUFFICIENT_DATA"},
                            "anisotropy_top_share": None,
                            "status": "NO_VIABLE_PARENTS"}

    log(f"[{sub.name}] target selection")
    # dedicated RNG stream (independent of census/op-census consumption) and
    # dedicated edge store: target-generation edges must not enter the
    # oracle graph (they would make oracle reachability partially true by
    # construction along the walk that created each target).
    rng_t = np.random.default_rng(cfg["seed"] + 777)
    tg_store = EdgeStore()
    tsel = select_targets(sub, rng_t, cfg["n_walks"], cfg["walk_len"], cfg["n_ref"],
                          THRESHOLDS["EPS_DENS"], cfg["k_low"], cfg["k_high"], tg_store,
                          min_remote=THRESHOLDS["EPS_HIT"] + 0.05)
    res["target_selection"] = {k: v for k, v in tsel.items()
                               if k not in ("targets", "_pool_pkeys")}
    targets = tsel.get("targets", [])
    census_class_keys = set(census["_class_counts"].keys())
    pool_keys = set(tsel.get("_pool_pkeys", []))
    res["diversity"] = {
        "census_classes": len(census_class_keys),
        "pool_classes": len(pool_keys),
        "combined_classes": len(census_class_keys | pool_keys),
    }
    res["target_selection"]["targets_meta"] = [
        {k: v for k, v in t.items() if k != "fp"} for t in targets]

    log(f"[{sub.name}] navigation battery ({len(targets)} targets)")
    nav_rows = run_navigation(sub, targets, cfg["nav_plan"], cfg["nav_budget"],
                              THRESHOLDS["EPS_HIT"], store)
    res["nav_rows"] = nav_rows
    res["nav_summary"] = summarize_navigation(nav_rows, COMPETITIVE_PAIR)

    log(f"[{sub.name}] coverage runs")
    res["coverage"] = run_coverage(sub, ["N1_RESTART_WALK", "N3_NOVELTY"],
                                   cfg["coverage_seeds"], cfg["coverage_budget"], store)

    # --- ablation counterfactuals (single-mechanism removal) --------------
    best_nav = res["nav_summary"].get("best_pair_nav") or "N2_HILLCLIMB"
    log(f"[{sub.name}] ablation counterfactuals (navigator={best_nav})")
    stratum_drops: dict = {}
    baseline_best = _stratum_rates(nav_rows, best_nav)
    baseline_n4 = _stratum_rates(nav_rows, "N4_RECOMBINER")
    if targets:
        for op in range(sub.n_ops):
            allowed = [o for o in range(sub.n_ops) if o != op]
            wsub = MenuWrapper(sub, allowed_ops=allowed)
            wsub.bind_meter(meter)
            meter.set_component("counterfactual")
            cf_store = EdgeStore()
            rows = run_navigation(wsub, targets, [[best_nav, cfg["ablation_seeds"]]],
                                  cfg["nav_budget"], THRESHOLDS["EPS_HIT"], cf_store,
                                  component="counterfactual", base_seed=7000 + op)
            abl = _stratum_rates(rows, best_nav)
            stratum_drops[f"remove_op{op}"] = {
                s: {"baseline": baseline_best[s][0], "n_base": baseline_best[s][1],
                    "ablated": abl.get(s, (0.0, 0))[0], "n_abl": abl.get(s, (0.0, 0))[1]}
                for s in baseline_best}
        # crossover removal (N4 is the only crossover consumer)
        wsub = MenuWrapper(sub, use_crossover=False)
        wsub.bind_meter(meter)
        cf_store = EdgeStore()
        rows = run_navigation(wsub, targets, [["N4_RECOMBINER", cfg["ablation_seeds"]]],
                              cfg["nav_budget"], THRESHOLDS["EPS_HIT"], cf_store,
                              component="counterfactual", base_seed=7600)
        abl = _stratum_rates(rows, "N4_RECOMBINER")
        stratum_drops["remove_crossover"] = {
            s: {"baseline": baseline_n4[s][0], "n_base": baseline_n4[s][1],
                "ablated": abl.get(s, (0.0, 0))[0], "n_abl": abl.get(s, (0.0, 0))[1]}
            for s in baseline_n4}
    res["ablation"] = {"navigator": best_nav, "stratum_drops": stratum_drops}

    # --- reweight / radius / encoding counterfactuals (real substrates) ---
    if is_real and targets:
        base_stats = res["nav_summary"]["per_navigator"].get(best_nav, {})
        base_pooled = base_stats.get("pooled_hit_rate", 0.0)
        base_n = base_stats.get("n_runs", 0)
        variants: dict = {}
        for wi, wseed in enumerate((101, 102, 103)):
            w = np.random.default_rng(wseed).dirichlet(np.ones(sub.n_ops) * 2.0)
            wsub = MenuWrapper(sub, weights=list(w))
            wsub.bind_meter(meter)
            cf_store = EdgeStore()
            rows = run_navigation(wsub, targets, [[best_nav, cfg["cf_seeds"]]],
                                  cfg["nav_budget"], THRESHOLDS["EPS_HIT"], cf_store,
                                  component="counterfactual", base_seed=7700 + wi)
            hits = [r["hit"] for r in rows]
            variants[f"reweight_{wseed}"] = {
                "weights": [float(x) for x in w],
                "pooled_hit": float(np.mean(hits)) if hits else 0.0,
                "n_runs": len(hits), "baseline_n": base_n,
                "baseline_pooled_hit": base_pooled}
        # seed-symmetric baseline for counterfactual comparisons: restrict
        # the baseline to the SAME number of seeds per target as the
        # counterfactual runs, so the two-proportion test compares
        # like-with-like populations.
        base_rows_cf = [r for r in nav_rows if r["navigator"] == best_nav
                        and r["seed"] < cfg["cf_seeds"]]
        base_pooled = (float(np.mean([r["hit"] for r in base_rows_cf]))
                       if base_rows_cf else 0.0)
        base_n = len(base_rows_cf)
        for v in variants.values():
            v["baseline_pooled_hit"] = base_pooled
            v["baseline_n"] = base_n
        if radius_variant_factory is not None:
            rsub = radius_variant_factory()
            rsub.bind_meter(meter)
            cf_store = EdgeStore()
            rows = run_navigation(rsub, targets, [[best_nav, cfg["cf_seeds"]]],
                                  cfg["nav_budget"], THRESHOLDS["EPS_HIT"], cf_store,
                                  component="counterfactual", base_seed=7800)
            hits = [r["hit"] for r in rows]
            variants["radius_x2"] = {"pooled_hit": float(np.mean(hits)) if hits else 0.0,
                                     "n_runs": len(hits), "baseline_n": base_n,
                                     "baseline_pooled_hit": base_pooled}
        res["counterfactual_stability"] = {"status": "OK", "variants": variants}

        if encoding_variant_factory is not None:
            esub = encoding_variant_factory()
            esub.bind_meter(meter)
            cf_store = EdgeStore()
            # re-coded physics: same phenotype set, different mutation adjacency.
            # Fresh targets under the SAME frozen procedure on the re-coded
            # substrate, then the same navigator suite subset.
            meter.set_component("counterfactual")
            rng_e = np.random.default_rng(cfg["seed"] + 555)
            tsel_e = select_targets(esub, rng_e, cfg["n_walks"], cfg["walk_len"],
                                    cfg["n_ref"], THRESHOLDS["EPS_DENS"],
                                    cfg["k_low"], cfg["k_high"], cf_store,
                                    min_remote=THRESHOLDS["EPS_HIT"] + 0.05,
                                    component="counterfactual")
            if tsel_e.get("status") == "OK":
                rows = run_navigation(esub, tsel_e["targets"],
                                      [[best_nav, cfg["cf_seeds"]]],
                                      cfg["nav_budget"], THRESHOLDS["EPS_HIT"],
                                      cf_store, component="counterfactual",
                                      base_seed=7900)
                hits = [r["hit"] for r in rows]
                res["representation"] = {
                    "status": "OK",
                    "pooled_hit": float(np.mean(hits)) if hits else 0.0,
                    "n_runs": len(hits), "baseline_n": base_n,
                    "baseline_pooled_hit": base_pooled}
            else:
                res["representation"] = {"status": tsel_e.get("status")}

    # --- oracle + graph (analysis only, after all navigation is final) ----
    log(f"[{sub.name}] oracle + graph analysis")
    meter.set_component("oracle_validation")
    if targets:
        res["oracle"] = oracle_reachability(sub, store, targets, THRESHOLDS["EPS_HIT"],
                                            nav_rows)
    else:
        res["oracle"] = {}
    res["graph"] = graph_metrics(store)

    # accessible-mass summary
    viable_seen = sum(1 for f in store.fp_by_pkey.values() if sub.viable(f))
    res["mass_summary"] = {
        "phenotype_classes_census": census["n_classes_viable"],
        "accessible_viable_pkeys_all_processes": viable_seen,
        "note": "reproducibly-accessible mass = re-findability over targets (nav_summary)",
    }

    res["meter"] = meter.snapshot()
    res["gates"] = evaluate_gates(res)
    log(f"[{sub.name}] PRIMARY: {res['gates']['primary']}  flags={res['gates']['flags']}")

    with open(os.path.join(out_dir, f"{sub.name}_results.json"), "w") as fh:
        json.dump(_san(res), fh, indent=1)
    with open(os.path.join(out_dir, f"{sub.name}_nav_rows.jsonl"), "w") as fh:
        for r in nav_rows:
            fh.write(json.dumps(_san(r)) + "\n")
    return res
