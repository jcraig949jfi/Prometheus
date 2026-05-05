"""Rich 10K pilot runner: captures per-seed breakdowns, SHADOW_CATALOG
records, arm-separate timings, and provenance row counts.

Writes:
    prometheus_math/four_counts_pilot_run_10k.json   (rich; supersedes basic)
    prometheus_math/four_counts_10k_per_seed.json    (per-seed dump)
    prometheus_math/four_counts_10k_shadow.json      (any SHADOW_CATALOG records)
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.four_counts_pilot import (
    run_random_null,
    run_reinforce_agent,
)


def env_factory():
    return DiscoveryEnv(
        degree=10,
        kernel_db_path=":memory:",
        cost_seconds=0.5,
        log_discoveries=True,
        enable_pipeline=True,
    )


def env_factory_capture():
    """Wraps env_factory but lets us reach in for pipeline_records.
    The four_counts harness already inspects env.pipeline_records()
    internally; we re-implement the loop here so we can also extract
    the actual DiscoveryRecord objects across all seeds."""
    return env_factory()


def run_random_null_capture(n_episodes: int, seed: int):
    """Same as run_random_null but exposes the env after the run so we
    can drain pipeline_records()."""
    import numpy as np
    env = env_factory_capture()
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

        # Tally inline (mirror four_counts_pilot._tally_episode_outcome)
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


def run_reinforce_capture(n_episodes: int, seed: int,
                          lr: float = 0.05, entropy_coef: float = 0.05,
                          reward_scale: float = 1.0 / 100.0,
                          baseline_decay: float = 0.95):
    import numpy as np
    from prometheus_math.demo_discovery import N_COEFFICIENT_ACTIONS

    env = env_factory_capture()
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

        # tally
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
    """Make a DiscoveryRecord JSON-safe."""
    out = {
        "candidate_hash": getattr(rec, "candidate_hash", None),
        "coeffs": list(getattr(rec, "coeffs", [])),
        "mahler_measure": float(getattr(rec, "mahler_measure", float("nan"))),
        "terminal_state": getattr(rec, "terminal_state", None),
        "kill_pattern": getattr(rec, "kill_pattern", None),
    }
    # Optional extras
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


def main():
    seeds = [0, 1, 2]
    n_episodes = 10000
    print(f"=== Rich 10K pilot: {n_episodes} eps x {len(seeds)} seeds ===")

    runs: List[Dict[str, Any]] = []
    arm_total_time = {"random_null": 0.0, "reinforce_agent": 0.0}

    # Random null arm
    for s in seeds:
        print(f"  [random_null seed={s}] starting...")
        r = run_random_null_capture(n_episodes, s)
        arm_total_time["random_null"] += r["elapsed_s"]
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}")

    # REINFORCE arm
    for s in seeds:
        print(f"  [reinforce_agent seed={s}] starting...")
        r = run_reinforce_capture(n_episodes, s)
        arm_total_time["reinforce_agent"] += r["elapsed_s"]
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}")

    # Aggregate
    def by_label(lbl: str):
        return [r for r in runs if r["label"] == lbl]

    def promote_rate(r: Dict[str, Any]) -> float:
        n = r["n_episodes"]
        if n == 0:
            return 0.0
        c = r["counts"]
        return (c["promote"] + c["shadow_catalog"]) / n

    def cat_hit_rate(r: Dict[str, Any]) -> float:
        n = r["n_episodes"]
        if n == 0:
            return 0.0
        return r["counts"]["catalog_hit"] / n

    def claim_rate(r: Dict[str, Any]) -> float:
        n = r["n_episodes"]
        if n == 0:
            return 0.0
        return r["counts"]["claim_into_kernel"] / n

    import numpy as np
    summary: Dict[str, Any] = {
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
                {"seed": r["seed"], **r["counts"],
                 "elapsed_s": r["elapsed_s"]}
                for r in rs
            ],
        }

    # Welch p-value
    a = np.array(summary["per_condition"]["random_null"]["promote_rates"])
    b = np.array(summary["per_condition"]["reinforce_agent"]["promote_rates"])
    if a.var(ddof=1) == 0 and b.var(ddof=1) == 0 and a.mean() == b.mean():
        p_val = 1.0
    else:
        try:
            from scipy.stats import ttest_ind
            t, p = ttest_ind(a, b, equal_var=False, alternative="two-sided")
            p_val = float(p)
        except Exception:
            p_val = float("nan")
    summary["welch_p_two_sided"] = p_val

    # SHADOW_CATALOG / PROMOTED records
    shadow_records = []
    for r in runs:
        for rec in r["pipeline_records"]:
            ts = getattr(rec, "terminal_state", None)
            if ts in ("SHADOW_CATALOG", "PROMOTED"):
                d = serialize_record(rec)
                d["seed"] = r["seed"]
                d["agent"] = r["label"]
                shadow_records.append(d)

    # Provenance row counts (verify episodes x conditions x seeds)
    expected_episodes = n_episodes * 2 * len(seeds)
    summary["provenance_check"] = {
        "expected_total_episodes": expected_episodes,
        "actual_total_pipeline_records": sum(
            len(r["pipeline_records"]) for r in runs
        ),
    }

    # Write outputs
    with open("F:/Prometheus/prometheus_math/four_counts_pilot_run_10k.json",
              "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    per_seed = {
        "n_episodes_per_cell": n_episodes,
        "runs": [
            {
                "label": r["label"],
                "seed": r["seed"],
                "elapsed_s": r["elapsed_s"],
                "counts": r["counts"],
                "by_kill_pattern": r["by_kill_pattern"],
                "n_pipeline_records": len(r["pipeline_records"]),
            }
            for r in runs
        ],
    }
    with open("F:/Prometheus/prometheus_math/four_counts_10k_per_seed.json",
              "w", encoding="utf-8") as f:
        json.dump(per_seed, f, indent=2)

    with open("F:/Prometheus/prometheus_math/four_counts_10k_shadow.json",
              "w", encoding="utf-8") as f:
        json.dump({"shadow_records": shadow_records,
                   "count": len(shadow_records)}, f, indent=2)

    print()
    print("=" * 70)
    print("Summary:")
    print(f"  random_null PROMOTE rates per seed: {summary['per_condition']['random_null']['promote_rates']}")
    print(f"  reinforce_agent PROMOTE rates per seed: {summary['per_condition']['reinforce_agent']['promote_rates']}")
    print(f"  Welch p (two-sided): {p_val}")
    print(f"  Arm wall-clock: random_null={arm_total_time['random_null']:.2f}s  reinforce={arm_total_time['reinforce_agent']:.2f}s")
    print(f"  random_null cat-hit rates per seed: {summary['per_condition']['random_null']['catalog_hit_rates']}")
    print(f"  reinforce cat-hit rates per seed: {summary['per_condition']['reinforce_agent']['catalog_hit_rates']}")
    print(f"  Salem-cluster (random_null): {summary['per_condition']['random_null']['by_kill_pattern'].get('upstream:salem_cluster', 0)}")
    print(f"  Salem-cluster (reinforce):   {summary['per_condition']['reinforce_agent']['by_kill_pattern'].get('upstream:salem_cluster', 0)}")
    print(f"  SHADOW_CATALOG / PROMOTED records found: {len(shadow_records)}")


if __name__ == "__main__":
    main()
