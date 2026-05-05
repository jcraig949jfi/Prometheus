"""Rich 10K pilot runner under SHAPED reward.

Sibling of `_run_10k_rich.py` — same harness, same seeds [0,1,2], same
budget (10K x 3), only difference is `reward_shape='shaped'` passed
into DiscoveryEnv.  Hypothesis (per `SHAPED_REWARD_RESULTS.md` brief):
the continuous M-gradient gives the policy gradient real information
across the M-band, potentially breaking through the 0/30000 PROMOTE
ceiling that `step` rewards couldn't.

Writes:
    prometheus_math/four_counts_pilot_run_10k_shaped.json   (rich; step counterpart at four_counts_pilot_run_10k.json)
    prometheus_math/four_counts_10k_per_seed_shaped.json    (per-seed)
    prometheus_math/four_counts_10k_shadow_shaped.json      (SHADOW_CATALOG entries)
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from prometheus_math.discovery_env import DiscoveryEnv

REWARD_SHAPE = "shaped"


def env_factory():
    return DiscoveryEnv(
        degree=10,
        kernel_db_path=":memory:",
        cost_seconds=0.5,
        log_discoveries=True,
        enable_pipeline=True,
        reward_shape=REWARD_SHAPE,
    )


def env_factory_capture():
    return env_factory()


def _mband_bucket(m: float) -> str:
    """Reward-shape-independent M-band bucket for proxy concentration
    measurements.  Boundaries match the step-reward bands so cross-shape
    comparisons stay meaningful."""
    import math as _m
    if not _m.isfinite(m):
        return "non_finite_or_artifact"
    if m < 1.001:
        return "cyclotomic"
    if m < 1.18:
        return "sub_lehmer"
    if m < 1.5:
        return "salem_cluster"
    if m < 2.0:
        return "low_m"
    if m < 5.0:
        return "functional"
    return "large_m"


def run_random_null_capture(n_episodes: int, seed: int):
    import numpy as np
    env = env_factory_capture()
    rng = np.random.default_rng(seed)
    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", 7))

    counts = {"catalog_hit": 0, "claim_into_kernel": 0, "promote": 0,
              "shadow_catalog": 0, "rejected": 0}
    by_kp: Dict[str, int] = {}
    by_mband: Dict[str, int] = {}
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
        m_value = last_info.get("mahler_measure", float("nan"))
        mb = _mband_bucket(float(m_value)) if m_value is not None else "non_finite_or_artifact"
        by_mband[mb] = by_mband.get(mb, 0) + 1

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
        "by_mband": by_mband,
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
    by_mband: Dict[str, int] = {}
    pipeline_len_before = 0
    t0 = time.perf_counter()

    cum_rewards: List[float] = []  # for shaped-reward magnitude check
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
        cum_rewards.append(cum_reward)

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
        m_value = last_info.get("mahler_measure", float("nan"))
        mb = _mband_bucket(float(m_value)) if m_value is not None else "non_finite_or_artifact"
        by_mband[mb] = by_mband.get(mb, 0) + 1
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
    mean_reward = float(sum(cum_rewards) / max(1, len(cum_rewards)))
    return {
        "label": "reinforce_agent",
        "seed": seed,
        "elapsed_s": elapsed,
        "counts": counts,
        "by_kill_pattern": by_kp,
        "by_mband": by_mband,
        "pipeline_records": pipeline_records,
        "n_episodes": n_episodes,
        "mean_episode_reward": mean_reward,
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


def main():
    seeds = [0, 1, 2]
    n_episodes = 10000
    print(f"=== Rich 10K SHAPED-REWARD pilot: {n_episodes} eps x {len(seeds)} seeds ===")
    print(f"   reward_shape = {REWARD_SHAPE!r}")

    runs: List[Dict[str, Any]] = []
    arm_total_time = {"random_null": 0.0, "reinforce_agent": 0.0}

    for s in seeds:
        print(f"  [random_null seed={s}] starting...")
        r = run_random_null_capture(n_episodes, s)
        arm_total_time["random_null"] += r["elapsed_s"]
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}")

    for s in seeds:
        print(f"  [reinforce_agent seed={s}] starting...")
        r = run_reinforce_capture(n_episodes, s)
        arm_total_time["reinforce_agent"] += r["elapsed_s"]
        runs.append(r)
        print(f"    elapsed={r['elapsed_s']:.2f}s  counts={r['counts']}  "
              f"mean_episode_reward={r.get('mean_episode_reward', float('nan')):.3f}")

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
        "reward_shape": REWARD_SHAPE,
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
        agg_mb: Dict[str, int] = {}
        for r in rs:
            for k, v in r.get("by_mband", {}).items():
                agg_mb[k] = agg_mb.get(k, 0) + v
        summary["per_condition"][lbl] = {
            "promote_rate_mean": float(np.mean(prs)),
            "promote_rate_std": float(np.std(prs, ddof=1)) if len(prs) > 1 else 0.0,
            "promote_rates": prs,
            "catalog_hit_rate_mean": float(np.mean(chs)),
            "catalog_hit_rates": chs,
            "claim_rate_mean": float(np.mean(cls_)),
            "claim_rates": cls_,
            "by_kill_pattern": agg_kp,
            "by_mband": agg_mb,
            "per_seed_counts": [
                {"seed": r["seed"], **r["counts"],
                 "elapsed_s": r["elapsed_s"]}
                for r in rs
            ],
        }
        if lbl == "reinforce_agent":
            summary["per_condition"][lbl]["mean_episode_reward_per_seed"] = [
                float(r.get("mean_episode_reward", float("nan"))) for r in rs
            ]

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

    shadow_records = []
    for r in runs:
        for rec in r["pipeline_records"]:
            ts = getattr(rec, "terminal_state", None)
            if ts in ("SHADOW_CATALOG", "PROMOTED"):
                d = serialize_record(rec)
                d["seed"] = r["seed"]
                d["agent"] = r["label"]
                shadow_records.append(d)

    expected_episodes = n_episodes * 2 * len(seeds)
    summary["provenance_check"] = {
        "expected_total_episodes": expected_episodes,
        "actual_total_pipeline_records": sum(
            len(r["pipeline_records"]) for r in runs
        ),
    }

    with open("F:/Prometheus/prometheus_math/four_counts_pilot_run_10k_shaped.json",
              "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    per_seed = {
        "n_episodes_per_cell": n_episodes,
        "reward_shape": REWARD_SHAPE,
        "runs": [
            {
                "label": r["label"],
                "seed": r["seed"],
                "elapsed_s": r["elapsed_s"],
                "counts": r["counts"],
                "by_kill_pattern": r["by_kill_pattern"],
                "n_pipeline_records": len(r["pipeline_records"]),
                "mean_episode_reward": r.get("mean_episode_reward", None),
            }
            for r in runs
        ],
    }
    with open("F:/Prometheus/prometheus_math/four_counts_10k_per_seed_shaped.json",
              "w", encoding="utf-8") as f:
        json.dump(per_seed, f, indent=2)

    with open("F:/Prometheus/prometheus_math/four_counts_10k_shadow_shaped.json",
              "w", encoding="utf-8") as f:
        json.dump({"shadow_records": shadow_records,
                   "count": len(shadow_records),
                   "reward_shape": REWARD_SHAPE}, f, indent=2)

    print()
    print("=" * 70)
    print("Summary (shaped reward):")
    print(f"  random_null PROMOTE rates per seed: {summary['per_condition']['random_null']['promote_rates']}")
    print(f"  reinforce_agent PROMOTE rates per seed: {summary['per_condition']['reinforce_agent']['promote_rates']}")
    print(f"  Welch p (two-sided): {p_val}")
    print(f"  Arm wall-clock: random_null={arm_total_time['random_null']:.2f}s  reinforce={arm_total_time['reinforce_agent']:.2f}s")
    print(f"  random_null cat-hit rates per seed: {summary['per_condition']['random_null']['catalog_hit_rates']}")
    print(f"  reinforce cat-hit rates per seed: {summary['per_condition']['reinforce_agent']['catalog_hit_rates']}")
    rn_salem_mb = summary['per_condition']['random_null']['by_mband'].get('salem_cluster', 0)
    re_salem_mb = summary['per_condition']['reinforce_agent']['by_mband'].get('salem_cluster', 0)
    print(f"  Salem-cluster M-band (random_null): {rn_salem_mb}")
    print(f"  Salem-cluster M-band (reinforce):   {re_salem_mb}")
    if rn_salem_mb > 0:
        print(f"  Salem-cluster concentration ratio: {re_salem_mb / rn_salem_mb:.1f}x")
    rn_sub_mb = summary['per_condition']['random_null']['by_mband'].get('sub_lehmer', 0)
    re_sub_mb = summary['per_condition']['reinforce_agent']['by_mband'].get('sub_lehmer', 0)
    print(f"  sub-Lehmer M-band (random_null): {rn_sub_mb}")
    print(f"  sub-Lehmer M-band (reinforce):   {re_sub_mb}")
    print(f"  SHADOW_CATALOG / PROMOTED records found: {len(shadow_records)}")
    if shadow_records:
        print("  --- shadow record details ---")
        for rec in shadow_records:
            print(f"    [{rec.get('agent')} seed={rec.get('seed')}] "
                  f"M={rec.get('mahler_measure'):.6f}  "
                  f"hash={rec.get('candidate_hash')}  "
                  f"coeffs={rec.get('coeffs')}  "
                  f"terminal={rec.get('terminal_state')}  "
                  f"kp={rec.get('kill_pattern')}")


if __name__ == "__main__":
    main()
