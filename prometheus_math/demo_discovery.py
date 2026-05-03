"""prometheus_math.demo_discovery — REINFORCE vs random on DiscoveryEnv.

The acceptance test for the eight-week pivot's discovery claim. Runs:

  1. Random baseline for N episodes; report mean reward, distribution
     of reward labels, best M found, known-Salem hits, sub-Lehmer
     candidates flagged.
  2. REINFORCE for N episodes (same budget); same report.
  3. Statistical comparison: lift, p-value (Welch one-sided).
  4. Honest verdict.

The env is harder than ``SigmaMathEnv``:

- Action space is 7 per step × 6 steps for degree-10 polynomials (~117K
  trajectories).
- Reward is sparse: cyclotomic polys (M = 1) score 0, not the jackpot.
- The +100 jackpot ONLY fires for ``1.001 < M < 1.18`` — strict
  sub-Lehmer territory. Almost certainly doesn't exist; if it appears,
  the run logs ``DISCOVERY_CANDIDATE`` for hand-verification.

Run::

    python -m prometheus_math.demo_discovery --episodes 2000 --seed 0
    python -m prometheus_math.demo_discovery --episodes 5000 --seed 0 --degree 10

Acceptance criterion:

- Random baseline mean reward < 5 / episode.
- REINFORCE mean reward >> random (lift > 5x and p-value < 1e-3).
- REINFORCE concentrates on Salem cluster (known-salem-hit count > 1%
  of episodes).

If the criterion holds, the env is RL-compatible at the discovery
level. If it doesn't, the harder action space + sparse reward broke
REINFORCE's gradient signal and we need to revisit (action shaping,
reward shaping, or move to PPO with value function).
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from typing import Dict, List

import numpy as np

from .discovery_env import (
    DiscoveryEnv,
    EpisodeRecord,
    N_COEFFICIENT_ACTIONS,
)


# ---------------------------------------------------------------------------
# Trainers
# ---------------------------------------------------------------------------


def _episode_random(env: DiscoveryEnv, rng: np.random.Generator) -> Dict:
    """Run one episode with uniform random action selection."""
    env.reset()
    cum_reward = 0.0
    final_info: Dict = {}
    terminated = False
    while not terminated:
        a = int(rng.integers(0, N_COEFFICIENT_ACTIONS))
        _, r, terminated, _, info = env.step(a)
        cum_reward += r
        final_info = info
    return {"reward": cum_reward, "info": final_info}


def _episode_reinforce(
    env: DiscoveryEnv,
    logits: np.ndarray,
    rng: np.random.Generator,
) -> Dict:
    """Run one episode with categorical-softmax policy, returning the
    trajectory for downstream gradient updates.

    ``logits`` shape: (half_len, n_actions) — one categorical per step.
    """
    env.reset()
    actions: List[int] = []
    log_probs: List[float] = []
    final_info: Dict = {}
    cum_reward = 0.0
    terminated = False
    step_idx = 0
    while not terminated:
        # Softmax over this step's logits.
        l = logits[step_idx]
        probs = np.exp(l - l.max())
        probs /= probs.sum()
        a = int(rng.choice(len(probs), p=probs))
        log_probs.append(math.log(max(probs[a], 1e-12)))
        actions.append(a)
        _, r, terminated, _, info = env.step(a)
        cum_reward += r
        final_info = info
        step_idx += 1
    return {
        "reward": cum_reward,
        "info": final_info,
        "actions": actions,
        "log_probs": log_probs,
    }


def train_random(
    env: DiscoveryEnv, n_episodes: int, seed: int = 0
) -> Dict:
    """Pure random baseline."""
    rng = np.random.default_rng(seed)
    rewards: List[float] = []
    labels: Dict[str, int] = {}
    for _ in range(n_episodes):
        out = _episode_random(env, rng)
        rewards.append(out["reward"])
        lbl = out["info"].get("reward_label") or "unknown"
        labels[lbl] = labels.get(lbl, 0) + 1
    return {
        "rewards": np.array(rewards, dtype=np.float64),
        "label_counts": labels,
        "best_m": env._best_m_overall,
        "known_salem_hits": env.known_salem_hits(),
        "sub_lehmer_candidates": list(env.sub_lehmer_candidates()),
    }


def train_reinforce_contextual(
    env: DiscoveryEnv,
    n_episodes: int,
    lr: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.05,
    seed: int = 0,
) -> Dict:
    """Obs-conditioned REINFORCE with entropy regularization.

    Policy: logits = W[step] @ obs_features + b[step] for each step.
    The obs vector includes the partial polynomial under construction,
    so the policy can learn joint coefficient distributions instead of
    marginal-only.

    Entropy coefficient prevents premature deterministic collapse.
    """
    rng = np.random.default_rng(seed)
    half_len = env.half_len
    obs_dim = 7 + env.degree

    # Linear policy: logits = W[step] @ obs + b[step].
    # W shape: (half_len, n_actions, obs_dim); b shape: (half_len, n_actions).
    W = np.zeros((half_len, N_COEFFICIENT_ACTIONS, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, N_COEFFICIENT_ACTIONS), dtype=np.float64)

    rewards: List[float] = []
    labels: Dict[str, int] = {}
    baseline = 0.0

    def _policy_logits(step_idx: int, obs: np.ndarray) -> np.ndarray:
        return W[step_idx] @ obs + b[step_idx]

    for _ in range(n_episodes):
        obs, _ = env.reset()
        actions: List[int] = []
        observations: List[np.ndarray] = []
        cum_reward = 0.0
        terminated = False
        step_idx = 0
        while not terminated:
            l = _policy_logits(step_idx, obs)
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            a = int(rng.choice(len(probs), p=probs))
            actions.append(a)
            observations.append(obs.copy())
            obs, r, terminated, _, info = env.step(a)
            cum_reward += r
            step_idx += 1

        r_scaled = cum_reward * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        # Apply policy gradient + entropy bonus per step.
        for step_idx, (a, o) in enumerate(zip(actions, observations)):
            l = _policy_logits(step_idx, o)
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            # Policy gradient: ∇W += lr * advantage * (one_hot(a) - p) ⊗ obs
            grad_a = -probs.copy()
            grad_a[a] += 1.0
            # Entropy bonus: encourage exploration. ∇H = -∑ (1 + log p) * ∇p_a.
            # For softmax policy: ∇H w.r.t. logits = p ⊙ log p - p ⊙ ⟨log p⟩.
            log_p = np.log(probs + 1e-12)
            entropy_grad = probs * (log_p - (probs * log_p).sum())
            total_grad = advantage * grad_a + entropy_coef * (-entropy_grad)
            # Outer-product update for W; direct for b.
            W[step_idx] += lr * np.outer(total_grad, o)
            b[step_idx] += lr * total_grad

        rewards.append(cum_reward)
        lbl = info.get("reward_label") or "unknown"
        labels[lbl] = labels.get(lbl, 0) + 1

    return {
        "rewards": np.array(rewards, dtype=np.float64),
        "label_counts": labels,
        "best_m": env._best_m_overall,
        "known_salem_hits": env.known_salem_hits(),
        "sub_lehmer_candidates": list(env.sub_lehmer_candidates()),
        "policy_W_final": W,
        "policy_b_final": b,
    }


def train_reinforce(
    env: DiscoveryEnv,
    n_episodes: int,
    lr: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    seed: int = 0,
) -> Dict:
    """Hand-rolled REINFORCE with EMA baseline.

    Policy: independent categorical at each step (no obs conditioning
    yet — the env's full sequential structure is captured in the
    per-step logits, but the policy is stationary across episodes).
    This is intentionally simple; per pivot ``LEARNING_CURVE.md`` the
    next step is to make the policy obs-conditioned.
    """
    rng = np.random.default_rng(seed)
    half_len = env.half_len
    logits = np.zeros((half_len, N_COEFFICIENT_ACTIONS), dtype=np.float64)
    rewards: List[float] = []
    labels: Dict[str, int] = {}
    baseline = 0.0

    for _ in range(n_episodes):
        out = _episode_reinforce(env, logits, rng)
        r = out["reward"] * reward_scale
        advantage = r - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r

        # REINFORCE gradient: ∇ log π(a) * advantage.
        # For categorical softmax, ∂log p_a / ∂l_a = 1 - p_a; ∂log p_a / ∂l_b = -p_b for b≠a.
        for step_idx, a in enumerate(out["actions"]):
            l = logits[step_idx]
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            grad = -probs.copy()
            grad[a] += 1.0
            logits[step_idx] += lr * advantage * grad

        rewards.append(out["reward"])
        lbl = out["info"].get("reward_label") or "unknown"
        labels[lbl] = labels.get(lbl, 0) + 1

    return {
        "rewards": np.array(rewards, dtype=np.float64),
        "label_counts": labels,
        "best_m": env._best_m_overall,
        "known_salem_hits": env.known_salem_hits(),
        "sub_lehmer_candidates": list(env.sub_lehmer_candidates()),
        "logits_final": logits,
    }


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def welch_t_test_one_sided(
    a: np.ndarray, b: np.ndarray
) -> float:
    """Welch one-sided t-test: H1 = mean(a) > mean(b). Returns p-value."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    ma, mb = float(np.mean(a)), float(np.mean(b))
    va, vb = float(np.var(a, ddof=1)), float(np.var(b, ddof=1))
    na, nb = len(a), len(b)
    se = math.sqrt(va / na + vb / nb) if (va / na + vb / nb) > 0 else 1e-12
    t = (ma - mb) / se
    # Approximate Welch DoF.
    df = (
        (va / na + vb / nb) ** 2
        / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    )
    # One-sided p-value via scipy if available; else normal approx.
    try:
        from scipy.stats import t as student_t

        return float(1.0 - student_t.cdf(t, df=df))
    except Exception:
        # Normal approximation.
        return float(0.5 * (1.0 - math.erf(t / math.sqrt(2.0))))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--degree", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument(
        "--policy",
        choices=["stationary", "contextual"],
        default="contextual",
        help="stationary = independent-step categorical (fails on this env); "
        "contextual = obs-conditioned linear policy with entropy bonus",
    )
    args = parser.parse_args(argv)

    print("=" * 72)
    print(f"DiscoveryEnv: degree={args.degree}, episodes={args.episodes}, seed={args.seed}")
    print("=" * 72)

    # ------------------------------------------------------------------
    # Random baseline
    # ------------------------------------------------------------------
    print("\n[1] Random baseline")
    t0 = time.perf_counter()
    env_random = DiscoveryEnv(degree=args.degree, seed=args.seed)
    env_random.reset()
    rand = train_random(env_random, args.episodes, seed=args.seed)
    elapsed = time.perf_counter() - t0
    print(
        f"  episodes:        {args.episodes}\n"
        f"  mean reward:     {rand['rewards'].mean():.3f}\n"
        f"  std reward:      {rand['rewards'].std(ddof=1):.3f}\n"
        f"  best M found:    {rand['best_m']:.6f}\n"
        f"  known Salem:     {rand['known_salem_hits']}\n"
        f"  sub-Lehmer cand: {len(rand['sub_lehmer_candidates'])}\n"
        f"  elapsed:         {elapsed:.1f}s"
    )
    print(f"  label distribution: {rand['label_counts']}")
    env_random.close()

    # ------------------------------------------------------------------
    # REINFORCE
    # ------------------------------------------------------------------
    print(f"\n[2] REINFORCE ({args.policy} policy)")
    t0 = time.perf_counter()
    env_rein = DiscoveryEnv(degree=args.degree, seed=args.seed + 1)
    env_rein.reset()
    if args.policy == "contextual":
        rein = train_reinforce_contextual(
            env_rein, args.episodes, lr=args.lr, seed=args.seed + 1
        )
    else:
        rein = train_reinforce(
            env_rein, args.episodes, lr=args.lr, seed=args.seed + 1
        )
    elapsed = time.perf_counter() - t0
    print(
        f"  episodes:        {args.episodes}\n"
        f"  mean reward:     {rein['rewards'].mean():.3f}\n"
        f"  std reward:      {rein['rewards'].std(ddof=1):.3f}\n"
        f"  best M found:    {rein['best_m']:.6f}\n"
        f"  known Salem:     {rein['known_salem_hits']}\n"
        f"  sub-Lehmer cand: {len(rein['sub_lehmer_candidates'])}\n"
        f"  elapsed:         {elapsed:.1f}s"
    )
    print(f"  label distribution: {rein['label_counts']}")

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------
    p = welch_t_test_one_sided(rein["rewards"], rand["rewards"])
    rand_mean = float(rand["rewards"].mean())
    rein_mean = float(rein["rewards"].mean())
    lift = (
        (rein_mean - rand_mean) / max(rand_mean, 1e-9)
        if rand_mean != 0
        else float("inf")
    )

    print("\n[3] Comparison")
    print(f"  random mean:     {rand_mean:.3f}")
    print(f"  reinforce mean:  {rein_mean:.3f}")
    print(f"  lift:            {lift * 100:+.1f}%" if math.isfinite(lift) else "  lift: inf")
    print(f"  p-value (Welch): {p:.3e}")

    # Acceptance verdict.
    print("\n[4] Verdict")
    pass_lift = lift > 5.0 if math.isfinite(lift) else (rein_mean > rand_mean + 1.0)
    pass_p = p < 1e-3 if math.isfinite(p) else False
    pass_salem = rein["known_salem_hits"] > 0.01 * args.episodes
    overall = pass_lift and pass_p and pass_salem

    print(f"  random < 5/ep:           {'PASS' if rand_mean < 5.0 else 'FAIL'}")
    print(f"  REINFORCE >> random:     {'PASS' if pass_lift else 'FAIL'}")
    print(f"  p-value < 1e-3:          {'PASS' if pass_p else 'FAIL'}")
    print(f"  Salem cluster hit > 1%:  {'PASS' if pass_salem else 'FAIL'}")
    print(f"  OVERALL:                 {'PASS' if overall else 'FAIL'}")

    if rein["sub_lehmer_candidates"]:
        print("\n[5] DISCOVERY CANDIDATES (sub-Lehmer; not in Mossinghoff)")
        print("    (almost certainly numerical artifacts; record + verify)")
        for c in rein["sub_lehmer_candidates"][:5]:
            print(f"    coeffs={c.coeffs}  M={c.mahler_measure:.10f}")

    env_rein.close()
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
