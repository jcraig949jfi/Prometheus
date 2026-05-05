"""Path (A) pilot: DiscoveryEnv at degree=14, coefficient_choices=(-5..5).

Triple-#3 / hypothesis-2 calibration test. The 0-PROMOTE ceiling at
degree 10 across step/shaped reward and ±3/±5/±7 alphabets persisted
through 200K cumulative episodes. Hypothesis 2 is that the +100 band
exists at degree >= 14 but our policy class hadn't reached it because
we were at the wrong degree.

Pre-flight (combined Known180 + phase1_curated):
  deg 14, max|c| in {2,3,4,5}: 6 entries; only ONE has max|c| >= 4
  (M=1.176281, max|c|=5, the canonical Lehmer rep).

Budget: 5000 episodes x 3 seeds x 2 arms = 30K episodes.
Ceiling on wall time per spec: ~5 min; if exceeded, fall back to 3K.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.four_counts_pilot import (
    FourCountsResult,
    _tally_episode_outcome,
    _welch_t_test_one_sided,
    print_pilot_table,
)


# ---------------------------------------------------------------------------
# Verbose runners that ALSO capture every shadow_catalog entry, every
# catalog-hit, every promote, and per-arm proxy concentration counts.
# ---------------------------------------------------------------------------


def _serialize_record(rec) -> Dict[str, Any]:
    """Cherry-pick the fields we want to log per pipeline record."""
    out = {
        "candidate_hash": getattr(rec, "candidate_hash", None),
        "coeffs": list(getattr(rec, "coeffs", []) or []),
        "mahler_measure": float(getattr(rec, "mahler_measure", 0.0) or 0.0),
        "terminal_state": getattr(rec, "terminal_state", None),
        "kill_pattern": getattr(rec, "kill_pattern", None),
        "claim_id": getattr(rec, "claim_id", None),
        "symbol_ref": getattr(rec, "symbol_ref", None),
        "check_results": None,
    }
    cr = getattr(rec, "check_results", None)
    if cr is not None:
        try:
            # check_results may be a dict or a list; coerce sanely.
            if isinstance(cr, dict):
                out["check_results"] = {
                    str(k): (v if isinstance(v, (int, float, str, bool, type(None)))
                             else str(v))
                    for k, v in cr.items()
                }
            elif isinstance(cr, list):
                out["check_results"] = [
                    (v if isinstance(v, (int, float, str, bool, type(None)))
                     else str(v))
                    for v in cr
                ]
            else:
                out["check_results"] = str(cr)
        except Exception:
            out["check_results"] = str(cr)
    return out


def run_random_null_verbose(env_factory, n_episodes, seed):
    """Random null with full per-episode logging."""
    env = env_factory()
    rng = np.random.default_rng(seed)

    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions"))
    salem_cluster_hits = 0  # proxy concentration
    low_m_hits = 0

    counts = {
        "catalog_hit": 0,
        "claim_into_kernel": 0,
        "promote": 0,
        "shadow_catalog": 0,
        "rejected": 0,
    }
    by_kp: Dict[str, int] = {}
    catalog_hits: List[Dict[str, Any]] = []
    promotes: List[Dict[str, Any]] = []
    shadow_catalog: List[Dict[str, Any]] = []
    pipeline_len = 0

    t0 = time.perf_counter()
    for ep in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        while not terminated:
            a = int(rng.integers(0, n_actions))
            obs, r, terminated, _, last_info = env.step(a)

        # Tally proxy concentration (independent of pipeline routing).
        rl = last_info.get("reward_label")
        if rl == "salem_cluster":
            salem_cluster_hits += 1
        elif rl == "low_m":
            low_m_hits += 1

        # Capture catalog hits with their info BEFORE _tally_episode_outcome.
        df = last_info.get("discovery_flag")
        if df and isinstance(df, str) and df.startswith("known_salem:"):
            catalog_hits.append({
                "seed": seed, "episode": ep, "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl,
            })
        elif rl == "salem_cluster" and last_info.get("is_known_in_mossinghoff"):
            catalog_hits.append({
                "seed": seed, "episode": ep,
                "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl,
                "via": "salem_cluster_known",
            })

        new_len, by_kp = _tally_episode_outcome(
            last_info, pipeline_len, env, counts, by_kp
        )
        # If a new pipeline record dropped, capture it if PROMOTED or SHADOW.
        if new_len > pipeline_len:
            rec = env.pipeline_records()[-1]
            if rec.terminal_state == "PROMOTED":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                promotes.append(d)
            elif rec.terminal_state == "SHADOW_CATALOG":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                shadow_catalog.append(d)
        pipeline_len = new_len

    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    res = FourCountsResult(
        condition_label="random_null",
        total_episodes=n_episodes,
        catalog_hit_count=counts["catalog_hit"],
        claim_into_kernel_count=counts["claim_into_kernel"],
        promote_count=counts["promote"],
        shadow_catalog_count=counts["shadow_catalog"],
        rejected_count=counts["rejected"],
        by_kill_pattern=by_kp,
        elapsed_seconds=elapsed,
        seed=seed,
    )
    return res, {
        "catalog_hits": catalog_hits,
        "promotes": promotes,
        "shadow_catalog": shadow_catalog,
        "salem_cluster_proxy_hits": salem_cluster_hits,
        "low_m_proxy_hits": low_m_hits,
    }


def run_reinforce_agent_verbose(env_factory, n_episodes, seed,
                                 lr=0.05, entropy_coef=0.05,
                                 reward_scale=1.0/100.0,
                                 baseline_decay=0.95):
    """REINFORCE agent with full per-episode logging."""
    env = env_factory()
    rng = np.random.default_rng(seed)

    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions"))
    half_len = int(info0.get("half_len", env.half_len))
    degree = int(info0.get("degree", env.degree))
    obs_dim = 7 + degree

    W = np.zeros((half_len, n_actions, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, n_actions), dtype=np.float64)
    baseline = 0.0

    counts = {"catalog_hit": 0, "claim_into_kernel": 0,
              "promote": 0, "shadow_catalog": 0, "rejected": 0}
    by_kp: Dict[str, int] = {}
    catalog_hits: List[Dict[str, Any]] = []
    promotes: List[Dict[str, Any]] = []
    shadow_catalog: List[Dict[str, Any]] = []
    salem_cluster_hits = 0
    low_m_hits = 0
    pipeline_len = 0

    t0 = time.perf_counter()
    for ep in range(n_episodes):
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

        rl = last_info.get("reward_label")
        if rl == "salem_cluster":
            salem_cluster_hits += 1
        elif rl == "low_m":
            low_m_hits += 1

        df = last_info.get("discovery_flag")
        if df and isinstance(df, str) and df.startswith("known_salem:"):
            catalog_hits.append({
                "seed": seed, "episode": ep, "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl,
            })
        elif rl == "salem_cluster" and last_info.get("is_known_in_mossinghoff"):
            catalog_hits.append({
                "seed": seed, "episode": ep,
                "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl,
                "via": "salem_cluster_known",
            })

        new_len, by_kp = _tally_episode_outcome(
            last_info, pipeline_len, env, counts, by_kp
        )
        if new_len > pipeline_len:
            rec = env.pipeline_records()[-1]
            if rec.terminal_state == "PROMOTED":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                promotes.append(d)
            elif rec.terminal_state == "SHADOW_CATALOG":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                shadow_catalog.append(d)
        pipeline_len = new_len

    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    res = FourCountsResult(
        condition_label="reinforce_agent",
        total_episodes=n_episodes,
        catalog_hit_count=counts["catalog_hit"],
        claim_into_kernel_count=counts["claim_into_kernel"],
        promote_count=counts["promote"],
        shadow_catalog_count=counts["shadow_catalog"],
        rejected_count=counts["rejected"],
        by_kill_pattern=by_kp,
        elapsed_seconds=elapsed,
        seed=seed,
    )
    return res, {
        "catalog_hits": catalog_hits,
        "promotes": promotes,
        "shadow_catalog": shadow_catalog,
        "salem_cluster_proxy_hits": salem_cluster_hits,
        "low_m_proxy_hits": low_m_hits,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(n_episodes=5000, seeds=(0, 1, 2)):
    print("=" * 78)
    print(f"PATH (A) PILOT  degree=14  alphabet=(-5..5)  step reward")
    print(f"  budget: {n_episodes} episodes x {len(seeds)} seeds x 2 arms"
          f" = {n_episodes * len(seeds) * 2}")
    print("=" * 78)

    env_factory = lambda: DiscoveryEnv(
        degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        reward_shape="step",
    )

    arms = {
        "random_null": run_random_null_verbose,
        "reinforce_agent": run_reinforce_agent_verbose,
    }

    per_arm: Dict[str, Dict[str, Any]] = {}
    for label, fn in arms.items():
        results: List[FourCountsResult] = []
        details: List[Dict[str, Any]] = []
        for s in seeds:
            print(f"  running arm={label}  seed={s} ...", flush=True)
            res, det = fn(env_factory, n_episodes, int(s))
            results.append(res)
            det["seed"] = s
            details.append(det)
            print(f"    elapsed={res.elapsed_seconds:.1f}s  "
                  f"PROMOTE={res.promote_count}  SHADOW={res.shadow_catalog_count}  "
                  f"cat-hit={res.catalog_hit_count}  claim={res.claim_into_kernel_count}",
                  flush=True)

        promote_rates = np.array([r.promote_rate for r in results])
        catalog_hit_rates = np.array([r.catalog_hit_rate for r in results])
        claim_rates = np.array([r.claim_rate for r in results])

        per_arm[label] = {
            "promote_rate_mean": float(promote_rates.mean()),
            "promote_rate_std": float(promote_rates.std(ddof=1))
                if promote_rates.size > 1 else 0.0,
            "promote_rates": promote_rates.tolist(),
            "catalog_hit_rate_mean": float(catalog_hit_rates.mean()),
            "claim_rate_mean": float(claim_rates.mean()),
            "results": [r.__dict__ for r in results],
            "details": details,
        }

    # Welch t-test
    a_rates = np.array(per_arm["reinforce_agent"]["promote_rates"])
    b_rates = np.array(per_arm["random_null"]["promote_rates"])
    p_rein_gt_rand = _welch_t_test_one_sided(a_rates, b_rates)
    p_rand_gt_rein = _welch_t_test_one_sided(b_rates, a_rates)

    summary = {
        "config": {
            "degree": 14,
            "coefficient_choices": list(range(-5, 6)),
            "alphabet_size": 11,
            "n_episodes_per_cell": n_episodes,
            "seeds": list(seeds),
            "reward_shape": "step",
        },
        "per_arm": per_arm,
        "welch": {
            "p_reinforce_gt_random": p_rein_gt_rand,
            "p_random_gt_reinforce": p_rand_gt_rein,
            "mean_reinforce": float(a_rates.mean()),
            "mean_random": float(b_rates.mean()),
        },
    }

    # Print summary
    print()
    print("=" * 78)
    print("RESULTS SUMMARY")
    print("=" * 78)
    for label, info in per_arm.items():
        pr = info["promote_rate_mean"]
        std = info["promote_rate_std"]
        ch = info["catalog_hit_rate_mean"]
        cl = info["claim_rate_mean"]
        print(f"  {label:<22} PROMOTE={pr:.4f} +/-{std:.4f}  "
              f"cat-hit={ch:.4f}  claim={cl:.4f}")
        # Per-seed
        for r in info["results"]:
            print(f"    seed={r['seed']}: promote={r['promote_count']} "
                  f"shadow={r['shadow_catalog_count']} "
                  f"cat-hit={r['catalog_hit_count']} "
                  f"claim={r['claim_into_kernel_count']} "
                  f"reject={r['rejected_count']} "
                  f"elapsed={r['elapsed_seconds']:.1f}s")
        # Per-seed proxy concentration
        for det in info["details"]:
            print(f"    seed={det['seed']} proxy: salem={det['salem_cluster_proxy_hits']} "
                  f"low_m={det['low_m_proxy_hits']}")

    print()
    print(f"Welch p(REINFORCE > random): {p_rein_gt_rand}")
    print(f"Welch p(random > REINFORCE): {p_rand_gt_rein}")

    # SHADOW_CATALOG details
    print()
    print("=" * 78)
    print("SHADOW_CATALOG ENTRIES (these are candidates worth manual review)")
    print("=" * 78)
    total_shadow = 0
    for label, info in per_arm.items():
        for det in info["details"]:
            for s in det["shadow_catalog"]:
                total_shadow += 1
                print(f"  arm={label} seed={det['seed']} ep={s.get('episode')}: "
                      f"M={s['mahler_measure']:.6f} hash={s['candidate_hash']}")
                print(f"    coeffs={s['coeffs']}")
                print(f"    kill_pattern={s['kill_pattern']} "
                      f"checks={s['check_results']}")
    print(f"Total SHADOW_CATALOG entries: {total_shadow}")

    # PROMOTED details
    print()
    print("=" * 78)
    print("PROMOTED ENTRIES")
    print("=" * 78)
    total_prom = 0
    for label, info in per_arm.items():
        for det in info["details"]:
            for p in det["promotes"]:
                total_prom += 1
                print(f"  arm={label} seed={det['seed']} ep={p.get('episode')}: "
                      f"M={p['mahler_measure']:.6f} hash={p['candidate_hash']}")
                print(f"    coeffs={p['coeffs']}")
    print(f"Total PROMOTED entries: {total_prom}")

    # Catalog hits
    print()
    print("=" * 78)
    print("CATALOG-HIT EPISODES (rediscoveries; calibration signal)")
    print("=" * 78)
    total_cat = 0
    for label, info in per_arm.items():
        for det in info["details"]:
            for c in det["catalog_hits"][:50]:  # cap printed list
                total_cat += 1
                print(f"  arm={label} seed={det['seed']} ep={c.get('episode')}: "
                      f"M={c['mahler_measure']:.6f}  flag={c['discovery_flag']}")
                print(f"    coeffs={c['coeffs']}")
    print(f"Total catalog-hit episodes (across all arms/seeds): "
          f"{sum(len(d['catalog_hits']) for arm in per_arm.values() for d in arm['details'])}")

    out_path = os.path.join(
        os.path.dirname(__file__), "four_counts_d14_w5.json"
    )
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print()
    print(f"JSON dump: {out_path}")
    return summary


if __name__ == "__main__":
    n_eps = 5000
    if len(sys.argv) > 1:
        n_eps = int(sys.argv[1])
    main(n_episodes=n_eps)
