"""Coefficient-set width ablation for the §6.2 four-counts pilot.

Reruns the pilot at three coefficient-set widths -- {-3..3} (the
default; already in `four_counts_pilot_run_10k.json`), {-5..5}
(11 actions), and {-7..7} (15 actions) -- to test the alphabet
hypothesis: that the {-3..3} default structurally excludes
trajectory families containing higher-degree small-Mahler entries
(many of which have coefficients with |c|>=4 in the recently-refreshed
Mossinghoff Known180 catalog).

Per the spec:
    - {-5..5}: 5K episodes x 3 seeds.
    - {-7..7}: 3K episodes x 3 seeds.
    - {-3..3}: skipped (already done at 10K x 3; loaded for comparison).

Writes:
    prometheus_math/four_counts_width_5.json
    prometheus_math/four_counts_width_7.json
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from prometheus_math.discovery_env import DiscoveryEnv


def make_env_factory(width: int):
    """Build a zero-arg env_factory at the given coefficient-set width.
    Width W -> coefficient_choices = (-W, -W+1, ..., W); 2W+1 actions."""
    cc = tuple(range(-width, width + 1))

    def factory():
        return DiscoveryEnv(
            degree=10,
            kernel_db_path=":memory:",
            cost_seconds=0.5,
            log_discoveries=True,
            enable_pipeline=True,
            coefficient_choices=cc,
        )

    return factory, cc


def run_random_null_capture(env_factory, n_episodes: int, seed: int):
    import numpy as np
    env = env_factory()
    rng = np.random.default_rng(seed)
    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", 7))

    counts = {"catalog_hit": 0, "claim_into_kernel": 0, "promote": 0,
              "shadow_catalog": 0, "rejected": 0}
    by_kp: Dict[str, int] = {}
    pipeline_len_before = 0
    catalog_hit_episodes: List[Dict[str, Any]] = []
    t0 = time.perf_counter()

    for ep_idx in range(n_episodes):
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
            catalog_hit_episodes.append({
                "ep": ep_idx,
                "coeffs": last_info.get("coeffs_full"),
                "M": last_info.get("mahler_measure"),
                "discovery_flag": discovery_flag,
                "reward_label": reward_label,
            })
        elif reward_label == "salem_cluster" and is_known:
            counts["catalog_hit"] += 1
            catalog_hit_episodes.append({
                "ep": ep_idx,
                "coeffs": last_info.get("coeffs_full"),
                "M": last_info.get("mahler_measure"),
                "discovery_flag": discovery_flag,
                "reward_label": reward_label,
            })
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
        "catalog_hit_episodes": catalog_hit_episodes,
        "n_episodes": n_episodes,
    }


def run_reinforce_capture(env_factory, n_episodes: int, seed: int,
                          lr: float = 0.05, entropy_coef: float = 0.05,
                          reward_scale: float = 1.0 / 100.0,
                          baseline_decay: float = 0.95):
    import numpy as np

    env = env_factory()
    rng = np.random.default_rng(seed)
    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions", 7))
    half_len = int(info0.get("half_len", env.half_len))
    degree = int(info0.get("degree", env.degree))
    obs_dim = 7 + degree

    W = np.zeros((half_len, n_actions, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, n_actions), dtype=np.float64)
    baseline = 0.0

    counts = {"catalog_hit": 0, "claim_into_kernel": 0, "promote": 0,
              "shadow_catalog": 0, "rejected": 0}
    by_kp: Dict[str, int] = {}
    pipeline_len_before = 0
    catalog_hit_episodes: List[Dict[str, Any]] = []
    t0 = time.perf_counter()

    for ep_idx in range(n_episodes):
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
            catalog_hit_episodes.append({
                "ep": ep_idx,
                "coeffs": last_info.get("coeffs_full"),
                "M": last_info.get("mahler_measure"),
                "discovery_flag": discovery_flag,
                "reward_label": reward_label,
            })
        elif reward_label == "salem_cluster" and is_known:
            counts["catalog_hit"] += 1
            catalog_hit_episodes.append({
                "ep": ep_idx,
                "coeffs": last_info.get("coeffs_full"),
                "M": last_info.get("mahler_measure"),
                "discovery_flag": discovery_flag,
                "reward_label": reward_label,
            })
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
        "catalog_hit_episodes": catalog_hit_episodes,
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


def run_width(width: int, n_episodes: int, seeds: List[int],
              out_path: str) -> Dict[str, Any]:
    factory, cc = make_env_factory(width)
    print(f"\n=== width=±{width}  alphabet={cc}  n_actions={len(cc)}  "
          f"n_episodes={n_episodes} x {len(seeds)} seeds ===")

    runs: List[Dict[str, Any]] = []
    arm_total_time = {"random_null": 0.0, "reinforce_agent": 0.0}

    for s in seeds:
        print(f"  [random_null seed={s}] starting...")
        r = run_random_null_capture(factory, n_episodes, s)
        arm_total_time["random_null"] += r["elapsed_s"]
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}")

    for s in seeds:
        print(f"  [reinforce_agent seed={s}] starting...")
        r = run_reinforce_capture(factory, n_episodes, s)
        arm_total_time["reinforce_agent"] += r["elapsed_s"]
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}")

    def by_label(lbl):
        return [r for r in runs if r["label"] == lbl]

    def promote_rate(r):
        n = r["n_episodes"]
        c = r["counts"]
        return 0.0 if n == 0 else (c["promote"] + c["shadow_catalog"]) / n

    def cat_hit_rate(r):
        n = r["n_episodes"]
        return 0.0 if n == 0 else r["counts"]["catalog_hit"] / n

    def claim_rate(r):
        n = r["n_episodes"]
        return 0.0 if n == 0 else r["counts"]["claim_into_kernel"] / n

    import numpy as np
    summary: Dict[str, Any] = {
        "width": width,
        "coefficient_choices": list(cc),
        "n_actions": len(cc),
        "n_episodes_per_cell": n_episodes,
        "seeds": seeds,
        "arm_wall_clock_seconds": arm_total_time,
        "per_condition": {},
    }

    for lbl in ("random_null", "reinforce_agent"):
        rs = by_label(lbl)
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
        }

    a = np.array(summary["per_condition"]["random_null"]["promote_rates"])
    b_arr = np.array(summary["per_condition"]["reinforce_agent"]["promote_rates"])
    if a.var(ddof=1) == 0 and b_arr.var(ddof=1) == 0 and a.mean() == b_arr.mean():
        p_val = 1.0
    else:
        try:
            from scipy.stats import ttest_ind
            t, p = ttest_ind(a, b_arr, equal_var=False, alternative="two-sided")
            p_val = float(p)
        except Exception:
            p_val = float("nan")
    summary["welch_p_two_sided"] = p_val

    shadow_records = []
    for r in runs:
        for rec in r["pipeline_records"]:
            ts = getattr(rec, "terminal_state", None)
            if ts in ("SHADOW_CATALOG", "PROMOTED"):
                d = serialize_record(rec)
                d["seed"] = r["seed"]
                d["agent"] = r["label"]
                shadow_records.append(d)
    summary["shadow_records"] = shadow_records
    summary["shadow_record_count"] = len(shadow_records)

    # Catalog-hit episodes: aggregate per-arm + max|coef| analysis to
    # answer "did wider alphabet produce hits {-3..3} would have missed?"
    catalog_hits_aggregate = []
    for r in runs:
        for hit in r["catalog_hit_episodes"]:
            coeffs = hit.get("coeffs") or []
            max_c = max((abs(int(c)) for c in coeffs), default=0)
            catalog_hits_aggregate.append({
                "agent": r["label"],
                "seed": r["seed"],
                "ep": hit["ep"],
                "coeffs": coeffs,
                "M": hit["M"],
                "max_abs_coef": max_c,
                "structurally_excluded_by_pm3": max_c >= 4,
            })
    summary["catalog_hit_episodes"] = catalog_hits_aggregate
    summary["catalog_hits_with_max_abs_coef_ge_4"] = sum(
        1 for h in catalog_hits_aggregate if h["structurally_excluded_by_pm3"]
    )

    summary["provenance_check"] = {
        "expected_total_episodes": n_episodes * 2 * len(seeds),
        "actual_total_pipeline_records": sum(
            len(r["pipeline_records"]) for r in runs
        ),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print()
    print("=" * 70)
    print(f"WIDTH ±{width} SUMMARY")
    print(f"  random_null PROMOTE rates:   {summary['per_condition']['random_null']['promote_rates']}")
    print(f"  reinforce  PROMOTE rates:    {summary['per_condition']['reinforce_agent']['promote_rates']}")
    print(f"  random_null catalog-hits:    {[r['counts']['catalog_hit'] for r in by_label('random_null')]}")
    print(f"  reinforce  catalog-hits:     {[r['counts']['catalog_hit'] for r in by_label('reinforce_agent')]}")
    print(f"  Welch p (two-sided):         {p_val}")
    print(f"  SHADOW_CATALOG/PROMOTED:     {len(shadow_records)}")
    print(f"  cat-hits w/ max|c|>=4:       {summary['catalog_hits_with_max_abs_coef_ge_4']}")
    print(f"  Wall clock (random/reinf):   {arm_total_time['random_null']:.1f}s / {arm_total_time['reinforce_agent']:.1f}s")
    return summary


def main():
    seeds = [0, 1, 2]
    # Spec: {-5..5} 5K x 3, {-7..7} 3K x 3.
    run_width(
        width=5, n_episodes=5000, seeds=seeds,
        out_path="F:/Prometheus/prometheus_math/four_counts_width_5.json",
    )
    run_width(
        width=7, n_episodes=3000, seeds=seeds,
        out_path="F:/Prometheus/prometheus_math/four_counts_width_7.json",
    )


if __name__ == "__main__":
    main()
