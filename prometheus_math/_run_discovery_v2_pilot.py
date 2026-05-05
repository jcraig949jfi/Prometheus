"""Pilot driver: V2 random vs V2 + REINFORCE mutation selection.

Per the path-D ablation: ~5K episodes × 3 seeds × 2 arms.  Wall-time
cap ~10 min.  Reports best M per arm per seed + SHADOW_CATALOG entries
per arm + operator-selection histograms (REINFORCE concentration).
"""
from __future__ import annotations

import argparse
import json
import math
import time
from typing import Any, Dict, List, Tuple

import numpy as np

from prometheus_math.discovery_env_v2 import (
    DiscoveryEnvV2,
    N_MUTATION_OPERATORS,
)


# ---------------------------------------------------------------------------
# Random null arm
# ---------------------------------------------------------------------------


def run_random_v2(
    n_episodes: int,
    seed: int,
    degree: int,
    population_size: int,
    n_mutations_per_episode: int,
    seed_with_known: bool,
    enable_pipeline: bool,
) -> Dict[str, Any]:
    env = DiscoveryEnvV2(
        degree=degree,
        population_size=population_size,
        n_mutations_per_episode=n_mutations_per_episode,
        seed_with_known=seed_with_known,
        enable_pipeline=enable_pipeline,
        seed=seed,
    )
    rng = np.random.default_rng(seed)
    rewards = []
    elite_ms = []
    op_counts: Dict[str, int] = {}
    t0 = time.perf_counter()
    for _ in range(n_episodes):
        env.reset()
        terminated = False
        ep_reward = 0.0
        info: Dict[str, Any] = {}
        while not terminated:
            a = int(rng.integers(0, env.n_actions))
            _, r, terminated, _, info = env.step(a)
            ep_reward += r
        rewards.append(ep_reward)
        elite_ms.append(info.get("elite_m", float("inf")))
    elapsed = time.perf_counter() - t0
    op_counts = env.operator_call_counts()
    shadow_entries = [
        d for d in env.discoveries() if d.is_signal_class
    ]
    sub_lehmer_ks = [d for d in env.discoveries() if d.elite_m is not None and 1.001 < d.elite_m < 1.18]
    return {
        "arm": "random",
        "seed": seed,
        "n_episodes": n_episodes,
        "elapsed_seconds": elapsed,
        "best_m_overall": env.best_m_overall(),
        "elite_ms_min": float(min(elite_ms) if elite_ms else float("inf")),
        "elite_ms_median": float(np.median(elite_ms) if elite_ms else float("inf")),
        "mean_reward": float(np.mean(rewards) if rewards else 0.0),
        "operator_call_counts": op_counts,
        "n_shadow_catalog": len(shadow_entries),
        "shadow_catalog": [
            {
                "elite_coeffs": d.elite_coeffs,
                "elite_m": d.elite_m,
                "pipeline_terminal_state": d.pipeline_terminal_state,
                "pipeline_kill_pattern": d.pipeline_kill_pattern,
            }
            for d in shadow_entries
        ],
        "n_sub_lehmer_episodes": len(sub_lehmer_ks),
    }


# ---------------------------------------------------------------------------
# REINFORCE arm — learns a policy over mutation operators
# ---------------------------------------------------------------------------


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max()
    e = np.exp(x)
    return e / e.sum()


def run_reinforce_v2(
    n_episodes: int,
    seed: int,
    degree: int,
    population_size: int,
    n_mutations_per_episode: int,
    seed_with_known: bool,
    enable_pipeline: bool,
    lr: float = 0.05,
    entropy_coef: float = 0.05,
    reward_scale: float = 1.0 / 50.0,
    baseline_decay: float = 0.95,
) -> Dict[str, Any]:
    """Contextual REINFORCE: logits = W @ obs + b over mutation
    operators.  Obs is the 8-dim population summary; policy outputs a
    distribution over the operator menu.  Single linear layer, entropy
    regularization, EMA baseline."""
    env = DiscoveryEnvV2(
        degree=degree,
        population_size=population_size,
        n_mutations_per_episode=n_mutations_per_episode,
        seed_with_known=seed_with_known,
        enable_pipeline=enable_pipeline,
        seed=seed,
    )
    rng = np.random.default_rng(seed)

    # Policy: W (n_actions × obs_dim), b (n_actions).
    obs_dim = 8
    n_actions = env.n_actions
    W = rng.normal(scale=0.01, size=(n_actions, obs_dim))
    b = np.zeros(n_actions)
    baseline = 0.0

    rewards = []
    elite_ms = []
    t0 = time.perf_counter()
    for ep in range(n_episodes):
        obs, _ = env.reset()
        terminated = False
        ep_log_grad_W = np.zeros_like(W)
        ep_log_grad_b = np.zeros_like(b)
        ep_entropy_grad_W = np.zeros_like(W)
        ep_entropy_grad_b = np.zeros_like(b)
        ep_reward = 0.0
        info: Dict[str, Any] = {}
        while not terminated:
            # Replace -1 sentinel (unset) with 5.0 for stability.
            obs_safe = np.where(obs < 0, 5.0, obs)
            logits = W @ obs_safe + b
            probs = _softmax(logits)
            a = int(rng.choice(n_actions, p=probs))
            _, r, terminated, _, info = env.step(a)
            ep_reward += r

            # ∂log π(a|s) / ∂logit_i = (1{i=a} - probs[i])
            one_hot = np.zeros(n_actions)
            one_hot[a] = 1.0
            grad_b_step = one_hot - probs
            grad_W_step = np.outer(grad_b_step, obs_safe)
            ep_log_grad_W += grad_W_step
            ep_log_grad_b += grad_b_step

            # Entropy gradient: ∂H/∂logit_i = -probs[i] * (logits[i] - sum(probs * logits))
            log_probs = np.log(probs + 1e-12)
            grad_b_ent = -probs * (log_probs - (probs * log_probs).sum())
            grad_W_ent = np.outer(grad_b_ent, obs_safe)
            ep_entropy_grad_W += grad_W_ent
            ep_entropy_grad_b += grad_b_ent

            obs, _ = env._obs(), None  # update obs reference (env's obs at next step)

        # REINFORCE update with EMA baseline.
        scaled = ep_reward * reward_scale
        advantage = scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * scaled
        W += lr * advantage * ep_log_grad_W + lr * entropy_coef * ep_entropy_grad_W
        b += lr * advantage * ep_log_grad_b + lr * entropy_coef * ep_entropy_grad_b

        rewards.append(ep_reward)
        elite_ms.append(info.get("elite_m", float("inf")))

    elapsed = time.perf_counter() - t0
    op_counts = env.operator_call_counts()
    shadow_entries = [d for d in env.discoveries() if d.is_signal_class]
    sub_lehmer_ks = [
        d for d in env.discoveries() if d.elite_m is not None and 1.001 < d.elite_m < 1.18
    ]
    return {
        "arm": "reinforce",
        "seed": seed,
        "n_episodes": n_episodes,
        "elapsed_seconds": elapsed,
        "best_m_overall": env.best_m_overall(),
        "elite_ms_min": float(min(elite_ms) if elite_ms else float("inf")),
        "elite_ms_median": float(np.median(elite_ms) if elite_ms else float("inf")),
        "mean_reward": float(np.mean(rewards) if rewards else 0.0),
        "operator_call_counts": op_counts,
        "policy_weights_norm": float(np.linalg.norm(W)),
        "n_shadow_catalog": len(shadow_entries),
        "shadow_catalog": [
            {
                "elite_coeffs": d.elite_coeffs,
                "elite_m": d.elite_m,
                "pipeline_terminal_state": d.pipeline_terminal_state,
                "pipeline_kill_pattern": d.pipeline_kill_pattern,
            }
            for d in shadow_entries
        ],
        "n_sub_lehmer_episodes": len(sub_lehmer_ks),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-episodes", type=int, default=5000)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--degree", type=int, default=10)
    parser.add_argument("--population-size", type=int, default=8)
    parser.add_argument("--n-mutations-per-episode", type=int, default=12)
    parser.add_argument("--seed-with-known", action="store_true")
    parser.add_argument("--no-pipeline", action="store_true")
    parser.add_argument("--out", type=str, default="prometheus_math/_discovery_v2_pilot.json")
    args = parser.parse_args()

    enable_pipeline = not args.no_pipeline

    results: List[Dict[str, Any]] = []
    t_start = time.perf_counter()
    for seed in args.seeds:
        print(f"[seed={seed}] running random arm ...")
        r = run_random_v2(
            n_episodes=args.n_episodes,
            seed=seed,
            degree=args.degree,
            population_size=args.population_size,
            n_mutations_per_episode=args.n_mutations_per_episode,
            seed_with_known=args.seed_with_known,
            enable_pipeline=enable_pipeline,
        )
        results.append(r)
        print(
            f"  random seed={seed} best_M={r['best_m_overall']:.5f} "
            f"shadow={r['n_shadow_catalog']} "
            f"elapsed={r['elapsed_seconds']:.1f}s"
        )
        print(f"[seed={seed}] running reinforce arm ...")
        r = run_reinforce_v2(
            n_episodes=args.n_episodes,
            seed=seed,
            degree=args.degree,
            population_size=args.population_size,
            n_mutations_per_episode=args.n_mutations_per_episode,
            seed_with_known=args.seed_with_known,
            enable_pipeline=enable_pipeline,
        )
        results.append(r)
        print(
            f"  reinforce seed={seed} best_M={r['best_m_overall']:.5f} "
            f"shadow={r['n_shadow_catalog']} "
            f"elapsed={r['elapsed_seconds']:.1f}s"
        )
        elapsed_total = time.perf_counter() - t_start
        print(f"  elapsed_total={elapsed_total:.1f}s")

    with open(args.out, "w") as f:
        json.dump(
            {
                "config": vars(args),
                "results": results,
                "elapsed_total_seconds": time.perf_counter() - t_start,
            },
            f,
            indent=2,
        )
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
