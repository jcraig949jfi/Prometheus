"""Degree-sweep runner: replicate the four-counts pilot at degree 10 / 12 / 14.

Tests the hypothesis from FOUR_COUNTS_RESULTS that widening the polynomial
degree (more action-space real estate) breaks the structural 0-PROMOTE
ceiling observed at degree 10 with 30K episodes.

Writes:
    prometheus_math/degree_sweep_results.json   (full per-degree summary)
    prometheus_math/degree_sweep_shadow.json    (any SHADOW_CATALOG records)
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv


def make_env_factory(degree: int):
    def _factory():
        return DiscoveryEnv(
            degree=degree,
            kernel_db_path=":memory:",
            cost_seconds=1.0,
            log_discoveries=True,
            enable_pipeline=True,
        )
    return _factory


def run_random_null_capture(env_factory, n_episodes: int, seed: int):
    env = env_factory()
    rng = np.random.default_rng(seed)
    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", 7))

    counts = {"catalog_hit": 0, "claim_into_kernel": 0, "promote": 0,
              "shadow_catalog": 0, "rejected": 0}
    by_kp: Dict[str, int] = {}
    pipeline_len_before = 0
    t0 = time.perf_counter()

    for _ in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        while not terminated:
            a = int(rng.integers(0, n_actions))
            obs, r, terminated, _, last_info = env.step(a)

        discovery_flag = last_info.get("discovery_flag")
        is_known = last_info.get("is_known_in_mossinghoff")
        reward_label = last_info.get("reward_label")

        if (discovery_flag and isinstance(discovery_flag, str)
                and discovery_flag.startswith("known_salem:")):
            counts["catalog_hit"] += 1
        elif reward_label == "salem_cluster" and is_known:
            counts["catalog_hit"] += 1
        else:
            pipeline_records = env.pipeline_records()
            new_len = len(pipeline_records)
            if new_len > pipeline_len_before:
                rec = pipeline_records[-1]
                counts["claim_into_kernel"] += 1
                if rec.terminal_state == "PROMOTED":
                    counts["promote"] += 1
                elif rec.terminal_state == "SHADOW_CATALOG":
                    counts["shadow_catalog"] += 1
                elif rec.terminal_state == "REJECTED":
                    counts["rejected"] += 1
                    kp = rec.kill_pattern or "unknown_pipeline_reject"
                    by_kp[kp] = by_kp.get(kp, 0) + 1
                pipeline_len_before = new_len
            elif reward_label is not None:
                counts["rejected"] += 1
                k = "upstream:" + str(reward_label)
                by_kp[k] = by_kp.get(k, 0) + 1
            else:
                counts["rejected"] += 1
                by_kp["upstream:unknown"] = by_kp.get("upstream:unknown", 0) + 1

    elapsed = time.perf_counter() - t0
    pipeline_records = list(env.pipeline_records())
    return {
        "label": "random_null",
        "seed": seed,
        "elapsed_s": elapsed,
        "counts": counts,
        "by_kill_pattern": by_kp,
        "pipeline_records": pipeline_records,
        "n_episodes": n_episodes,
    }


def run_reinforce_capture(env_factory, n_episodes: int, seed: int,
                          lr: float = 0.05, entropy_coef: float = 0.05,
                          reward_scale: float = 1.0 / 100.0,
                          baseline_decay: float = 0.95):
    from prometheus_math.demo_discovery import N_COEFFICIENT_ACTIONS

    env = env_factory()
    rng = np.random.default_rng(seed)
    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions", N_COEFFICIENT_ACTIONS))
    half_len = int(info0.get("half_len", env.half_len if hasattr(env, "half_len") else 6))
    degree = int(info0.get("degree", env.degree if hasattr(env, "degree") else 10))
    obs_dim = 7 + degree

    W = np.zeros((half_len, n_actions, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, n_actions), dtype=np.float64)
    baseline = 0.0

    counts = {"catalog_hit": 0, "claim_into_kernel": 0, "promote": 0,
              "shadow_catalog": 0, "rejected": 0}
    by_kp: Dict[str, int] = {}
    pipeline_len_before = 0
    t0 = time.perf_counter()

    for _ in range(n_episodes):
        obs, _ = env.reset()
        actions: List[int] = []
        observations: List[np.ndarray] = []
        cum_reward = 0.0
        terminated = False
        step_idx = 0
        last_info: Dict[str, Any] = {}
        while not terminated:
            l = W[step_idx] @ obs + b[step_idx]
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            a = int(rng.choice(len(probs), p=probs))
            actions.append(a)
            observations.append(obs.copy())
            obs, r, terminated, _, last_info = env.step(a)
            cum_reward += r
            step_idx += 1

        r_scaled = cum_reward * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        for s_idx, (a, o) in enumerate(zip(actions, observations)):
            l = W[s_idx] @ o + b[s_idx]
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            grad_a = -probs.copy()
            grad_a[a] += 1.0
            log_p = np.log(probs + 1e-12)
            entropy_grad = probs * (log_p - (probs * log_p).sum())
            total_grad = advantage * grad_a + entropy_coef * (-entropy_grad)
            W[s_idx] += lr * np.outer(total_grad, o)
            b[s_idx] += lr * total_grad

        discovery_flag = last_info.get("discovery_flag")
        is_known = last_info.get("is_known_in_mossinghoff")
        reward_label = last_info.get("reward_label")
        if (discovery_flag and isinstance(discovery_flag, str)
                and discovery_flag.startswith("known_salem:")):
            counts["catalog_hit"] += 1
        elif reward_label == "salem_cluster" and is_known:
            counts["catalog_hit"] += 1
        else:
            pipeline_records = env.pipeline_records()
            new_len = len(pipeline_records)
            if new_len > pipeline_len_before:
                rec = pipeline_records[-1]
                counts["claim_into_kernel"] += 1
                if rec.terminal_state == "PROMOTED":
                    counts["promote"] += 1
                elif rec.terminal_state == "SHADOW_CATALOG":
                    counts["shadow_catalog"] += 1
                elif rec.terminal_state == "REJECTED":
                    counts["rejected"] += 1
                    kp = rec.kill_pattern or "unknown_pipeline_reject"
                    by_kp[kp] = by_kp.get(kp, 0) + 1
                pipeline_len_before = new_len
            elif reward_label is not None:
                counts["rejected"] += 1
                k = "upstream:" + str(reward_label)
                by_kp[k] = by_kp.get(k, 0) + 1
            else:
                counts["rejected"] += 1
                by_kp["upstream:unknown"] = by_kp.get("upstream:unknown", 0) + 1

    elapsed = time.perf_counter() - t0
    pipeline_records = list(env.pipeline_records())
    return {
        "label": "reinforce_agent",
        "seed": seed,
        "elapsed_s": elapsed,
        "counts": counts,
        "by_kill_pattern": by_kp,
        "pipeline_records": pipeline_records,
        "n_episodes": n_episodes,
    }


def serialize_record(rec) -> Dict[str, Any]:
    out = {
        "candidate_hash": getattr(rec, "candidate_hash", None),
        "coeffs": list(getattr(rec, "coeffs", [])),
        "mahler_measure": float(getattr(rec, "mahler_measure", float("nan"))),
        "terminal_state": getattr(rec, "terminal_state", None),
        "kill_pattern": getattr(rec, "kill_pattern", None),
    }
    for attr in ("kernel_claim_symbol", "consulted_catalogs",
                 "battery_results", "promote_reason"):
        v = getattr(rec, attr, None)
        if v is not None:
            try:
                json.dumps(v)
                out[attr] = v
            except (TypeError, ValueError):
                out[attr] = repr(v)
    return out


def aggregate_summary(runs: List[Dict[str, Any]], n_episodes: int) -> Dict[str, Any]:
    def by_label(lbl: str):
        return [r for r in runs if r["label"] == lbl]

    def promote_rate(r):
        n = r["n_episodes"]
        if n == 0:
            return 0.0
        c = r["counts"]
        return (c["promote"] + c["shadow_catalog"]) / n

    def cat_hit_rate(r):
        n = r["n_episodes"]
        if n == 0:
            return 0.0
        return r["counts"]["catalog_hit"] / n

    def claim_rate(r):
        n = r["n_episodes"]
        if n == 0:
            return 0.0
        return r["counts"]["claim_into_kernel"] / n

    summary: Dict[str, Any] = {"per_condition": {}}
    for lbl in ("random_null", "reinforce_agent"):
        rs = by_label(lbl)
        if not rs:
            continue
        prs = [promote_rate(r) for r in rs]
        chs = [cat_hit_rate(r) for r in rs]
        cls_ = [claim_rate(r) for r in rs]
        agg_kp: Dict[str, int] = {}
        for r in rs:
            for k, v in r["by_kill_pattern"].items():
                agg_kp[k] = agg_kp.get(k, 0) + v
        summary["per_condition"][lbl] = {
            "promote_rate_mean": float(np.mean(prs)),
            "promote_rate_std": float(np.std(prs, ddof=1)) if len(prs) > 1 else 0.0,
            "promote_rates": prs,
            "catalog_hit_rate_mean": float(np.mean(chs)),
            "catalog_hit_rates": chs,
            "claim_rate_mean": float(np.mean(cls_)),
            "claim_rates": cls_,
            "by_kill_pattern": agg_kp,
            "per_seed_counts": [
                {"seed": r["seed"], **r["counts"], "elapsed_s": r["elapsed_s"]}
                for r in rs
            ],
            "total_elapsed_s": sum(r["elapsed_s"] for r in rs),
        }
    return summary


def run_one_degree(degree: int, n_episodes: int, seeds: List[int],
                   reinforce_seeds: List[int] = None) -> Dict[str, Any]:
    """Run both arms at one degree; reinforce_seeds defaults to seeds."""
    if reinforce_seeds is None:
        reinforce_seeds = seeds
    env_factory = make_env_factory(degree)
    runs: List[Dict[str, Any]] = []

    for s in seeds:
        print(f"  [degree={degree} random_null seed={s}] starting...", flush=True)
        r = run_random_null_capture(env_factory, n_episodes, s)
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}", flush=True)

    for s in reinforce_seeds:
        print(f"  [degree={degree} reinforce_agent seed={s}] starting...", flush=True)
        r = run_reinforce_capture(env_factory, n_episodes, s)
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}", flush=True)

    summary = aggregate_summary(runs, n_episodes)
    summary["degree"] = degree
    summary["n_episodes_per_cell"] = n_episodes
    summary["random_null_seeds"] = seeds
    summary["reinforce_seeds"] = reinforce_seeds

    # Capture all pipeline records (signal-class survivors only — empty
    # for REJECTED-only runs).
    shadow_records = []
    for r in runs:
        for rec in r["pipeline_records"]:
            ts = getattr(rec, "terminal_state", None)
            if ts in ("SHADOW_CATALOG", "PROMOTED"):
                d = serialize_record(rec)
                d["seed"] = r["seed"]
                d["agent"] = r["label"]
                d["degree"] = degree
                shadow_records.append(d)
    summary["shadow_records"] = shadow_records
    summary["n_shadow_records"] = len(shadow_records)
    return summary


def main():
    overall_t0 = time.perf_counter()

    print("=== Degree-sweep pilot ===", flush=True)
    print("Step 1: timing benchmark already complete (per-ep ~0.6ms across degrees).", flush=True)
    print("Step 2: degree=12 at 5K x 3 seeds (random_null + reinforce).", flush=True)

    # Compute budget: ~0.6ms/episode * 5K * 6 cells ~= 18s.
    # Use 5K x 3 for both degree 12 and degree 14 (they fit easily).
    summaries: Dict[int, Dict[str, Any]] = {}

    seeds = [0, 1, 2]

    # Degree 12: 5K x 3
    summaries[12] = run_one_degree(12, n_episodes=5000, seeds=seeds)

    elapsed = time.perf_counter() - overall_t0
    print(f"\nDegree-12 done.  Cumulative wall: {elapsed:.1f}s", flush=True)

    # Degree 14: 3K x 3 if degree-12 was fast; else 1K x 1
    if elapsed < 600:  # 10 min budget remaining for degree 14
        d14_eps, d14_seeds = 3000, [0, 1, 2]
    else:
        d14_eps, d14_seeds = 1000, [0]
    print(f"Step 3: degree=14 at {d14_eps} x {len(d14_seeds)} seeds.", flush=True)
    summaries[14] = run_one_degree(14, n_episodes=d14_eps, seeds=d14_seeds)

    elapsed = time.perf_counter() - overall_t0
    print(f"\nDegree-14 done.  Cumulative wall: {elapsed:.1f}s", flush=True)

    # Write outputs
    out_path = "F:/Prometheus/prometheus_math/degree_sweep_results.json"
    # Strip pipeline_records (non-serializable) before writing.
    serializable = {}
    for d, summ in summaries.items():
        s2 = {k: v for k, v in summ.items() if k != "shadow_records"}
        s2["shadow_records"] = summ["shadow_records"]  # already serialized
        serializable[str(d)] = s2

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)

    # Aggregate shadow records across all degrees
    all_shadow = []
    for d, summ in summaries.items():
        all_shadow.extend(summ["shadow_records"])
    with open("F:/Prometheus/prometheus_math/degree_sweep_shadow.json",
              "w", encoding="utf-8") as f:
        json.dump({"shadow_records": all_shadow,
                   "count": len(all_shadow)}, f, indent=2)

    # Final summary print
    print("\n" + "=" * 70, flush=True)
    print("DEGREE SWEEP — FINAL SUMMARY", flush=True)
    print("=" * 70, flush=True)
    for d, summ in summaries.items():
        n_eps = summ["n_episodes_per_cell"]
        n_seeds = len(summ["random_null_seeds"])
        print(f"\nDegree {d}  ({n_eps} eps x {n_seeds} seeds):", flush=True)
        for lbl in ("random_null", "reinforce_agent"):
            if lbl not in summ["per_condition"]:
                continue
            pc = summ["per_condition"][lbl]
            promote_total = sum(c["promote"] + c["shadow_catalog"] for c in pc["per_seed_counts"])
            cat_hit_total = sum(c["catalog_hit"] for c in pc["per_seed_counts"])
            salem_total = pc["by_kill_pattern"].get("upstream:salem_cluster", 0)
            print(f"  {lbl:18s}  PROMOTE={promote_total}/{n_eps*n_seeds}  "
                  f"cat-hit={cat_hit_total}  salem-cluster={salem_total}  "
                  f"wall={pc['total_elapsed_s']:.1f}s", flush=True)
        print(f"  SHADOW_CATALOG records at degree {d}: {summ['n_shadow_records']}", flush=True)

    total_elapsed = time.perf_counter() - overall_t0
    print(f"\nTotal sweep wall time: {total_elapsed:.1f}s", flush=True)
    print(f"Outputs: {out_path}", flush=True)
    print(f"         F:/Prometheus/prometheus_math/degree_sweep_shadow.json", flush=True)


if __name__ == "__main__":
    main()
