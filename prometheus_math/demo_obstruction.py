"""prometheus_math.demo_obstruction — REINFORCE vs random on ObstructionEnv.

The acceptance driver for the predicate-discovery env. Mirrors
``demo_discovery.py`` but routes a contextual REINFORCE learner against
the simulated OEIS-shaped battery in ``_obstruction_corpus``.

Run::

    python -m prometheus_math.demo_obstruction --episodes 1000 --seed 0

Acceptance criterion (mirrors DiscoveryEnv):

- Random baseline mean reward is finite + non-negative.
- REINFORCE mean reward strictly above random by lift >= 5x.
- REINFORCE rediscovers OBSTRUCTION_SHAPE or SECONDARY signature on at
  least one episode (tagged in env.discoveries()).
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from .obstruction_env import (
    ObstructionEnv,
    ObstructionEpisodeRecord,
    N_ACTIONS,
    REDISCOVERED_OBSTRUCTION_SHAPE_TAG,
    REDISCOVERED_SECONDARY_TAG,
    STOP_ACTION,
)


# ---------------------------------------------------------------------------
# Random baseline
# ---------------------------------------------------------------------------


def _episode_random(env: ObstructionEnv, rng: np.random.Generator) -> Dict:
    env.reset()
    info: Dict = {}
    cum = 0.0
    terminated = False
    while not terminated:
        a = int(rng.integers(0, N_ACTIONS))
        _, r, terminated, _, info = env.step(a)
        cum += r
    return {"reward": cum, "info": info}


def train_random_obstruction(
    env: ObstructionEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict:
    """Pure random baseline."""
    rng = np.random.default_rng(seed)
    rewards: List[float] = []
    rediscoveries: List[Tuple[int, str]] = []
    for ep in range(n_episodes):
        out = _episode_random(env, rng)
        rewards.append(out["reward"])
        for tag in out["info"].get("tags", []):
            rediscoveries.append((ep, tag))
    return {
        "rewards": np.array(rewards, dtype=np.float64),
        "rediscoveries": rediscoveries,
        "discoveries": env.discoveries(),
    }


# ---------------------------------------------------------------------------
# Contextual REINFORCE — same shape as demo_discovery's contextual policy
# ---------------------------------------------------------------------------


def train_reinforce_obstruction(
    env: ObstructionEnv,
    n_episodes: int,
    lr: float = 0.1,
    reward_scale: float = 0.5,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.05,
    seed: int = 0,
) -> Dict:
    """Obs-conditioned REINFORCE with entropy regularization.

    Mirrors ``prometheus_math.demo_discovery.train_reinforce_contextual``
    but with a STATIONARY-step policy parameterization (single weight
    matrix for all steps): the state already encodes step_count and the
    partial-predicate one-hot, so sharing across steps is fine and
    halves the parameter count.

    Policy: logits = W @ obs + b.
    """
    rng = np.random.default_rng(seed)
    obs, _ = env.reset()
    obs_dim = obs.shape[0]

    W = np.zeros((N_ACTIONS, obs_dim), dtype=np.float64)
    b = np.zeros(N_ACTIONS, dtype=np.float64)

    rewards: List[float] = []
    rediscoveries: List[Tuple[int, str]] = []
    obstruction_first_episode: Optional[int] = None
    secondary_first_episode: Optional[int] = None
    baseline = 0.0

    def _logits(obs: np.ndarray) -> np.ndarray:
        return W @ obs + b

    for ep in range(n_episodes):
        obs, _ = env.reset()
        actions: List[int] = []
        observations: List[np.ndarray] = []
        cum_reward = 0.0
        terminated = False
        info: Dict = {}
        while not terminated:
            l = _logits(obs)
            l_max = float(l.max())
            probs = np.exp(l - l_max)
            probs /= probs.sum()
            a = int(rng.choice(len(probs), p=probs))
            actions.append(a)
            observations.append(obs.copy())
            obs, r, terminated, _, info = env.step(a)
            cum_reward += r

        r_scaled = cum_reward * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        # Policy gradient + entropy bonus per step.
        for a, o in zip(actions, observations):
            l = _logits(o)
            l_max = float(l.max())
            probs = np.exp(l - l_max)
            probs /= probs.sum()
            grad_a = -probs.copy()
            grad_a[a] += 1.0
            log_p = np.log(probs + 1e-12)
            entropy_grad = probs * (log_p - (probs * log_p).sum())
            total_grad = advantage * grad_a + entropy_coef * (-entropy_grad)
            W += lr * np.outer(total_grad, o)
            b += lr * total_grad

        rewards.append(cum_reward)

        for tag in info.get("tags", []):
            rediscoveries.append((ep, tag))
            if tag == REDISCOVERED_OBSTRUCTION_SHAPE_TAG and obstruction_first_episode is None:
                obstruction_first_episode = ep
            if tag == REDISCOVERED_SECONDARY_TAG and secondary_first_episode is None:
                secondary_first_episode = ep

    return {
        "rewards": np.array(rewards, dtype=np.float64),
        "rediscoveries": rediscoveries,
        "obstruction_first_episode": obstruction_first_episode,
        "secondary_first_episode": secondary_first_episode,
        "discoveries": env.discoveries(),
        "policy_W_final": W,
        "policy_b_final": b,
    }


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def welch_t_test_one_sided(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    ma, mb = float(np.mean(a)), float(np.mean(b))
    va, vb = float(np.var(a, ddof=1)), float(np.var(b, ddof=1))
    na, nb = len(a), len(b)
    if (va / na + vb / nb) <= 0:
        return 0.0 if ma > mb else 1.0
    se = math.sqrt(va / na + vb / nb)
    t = (ma - mb) / se
    df = (
        (va / na + vb / nb) ** 2
        / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    )
    try:
        from scipy.stats import t as student_t
        return float(1.0 - student_t.cdf(t, df=df))
    except Exception:
        return float(0.5 * (1.0 - math.erf(t / math.sqrt(2.0))))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--max-complexity", type=int, default=4)
    parser.add_argument("--held-out-fraction", type=float, default=0.3)
    args = parser.parse_args(argv)

    print("=" * 72)
    print(
        f"ObstructionEnv: episodes={args.episodes}, seed={args.seed}, "
        f"max_complexity={args.max_complexity}"
    )
    print("=" * 72)

    # Random.
    print("\n[1] Random baseline")
    t0 = time.perf_counter()
    env_random = ObstructionEnv(
        seed=args.seed,
        max_predicate_complexity=args.max_complexity,
        held_out_fraction=args.held_out_fraction,
    )
    env_random.reset()
    rand = train_random_obstruction(env_random, args.episodes, seed=args.seed)
    elapsed_r = time.perf_counter() - t0
    rand_mean = float(np.mean(rand["rewards"]))
    rand_std = float(np.std(rand["rewards"], ddof=1))
    print(
        f"  episodes:        {args.episodes}\n"
        f"  mean reward:     {rand_mean:.3f}\n"
        f"  std reward:      {rand_std:.3f}\n"
        f"  rediscoveries:   {len(rand['rediscoveries'])}\n"
        f"  elapsed:         {elapsed_r:.1f}s"
    )
    env_random.close()

    # REINFORCE.
    print("\n[2] Contextual REINFORCE")
    t0 = time.perf_counter()
    env_rein = ObstructionEnv(
        seed=args.seed + 1,
        max_predicate_complexity=args.max_complexity,
        held_out_fraction=args.held_out_fraction,
    )
    env_rein.reset()
    rein = train_reinforce_obstruction(
        env_rein, args.episodes, lr=args.lr, seed=args.seed + 1
    )
    elapsed_p = time.perf_counter() - t0
    rein_mean = float(np.mean(rein["rewards"]))
    rein_std = float(np.std(rein["rewards"], ddof=1))
    print(
        f"  episodes:        {args.episodes}\n"
        f"  mean reward:     {rein_mean:.3f}\n"
        f"  std reward:      {rein_std:.3f}\n"
        f"  rediscoveries:   {len(rein['rediscoveries'])}\n"
        f"  elapsed:         {elapsed_p:.1f}s"
    )
    if rein["obstruction_first_episode"] is not None:
        print(
            f"  OBSTRUCTION_SHAPE rediscovered at episode "
            f"{rein['obstruction_first_episode']}"
        )
    if rein["secondary_first_episode"] is not None:
        print(
            f"  SECONDARY rediscovered at episode "
            f"{rein['secondary_first_episode']}"
        )

    # Comparison.
    p = welch_t_test_one_sided(rein["rewards"], rand["rewards"])
    if rand_mean > 0:
        lift = (rein_mean - rand_mean) / rand_mean
    else:
        lift = float("inf") if rein_mean > 0 else 0.0

    print("\n[3] Comparison")
    print(f"  random mean:     {rand_mean:.3f}")
    print(f"  reinforce mean:  {rein_mean:.3f}")
    print(
        f"  lift:            {lift * 100:+.1f}%"
        if math.isfinite(lift) else "  lift: inf"
    )
    print(f"  p-value (Welch): {p:.3e}")

    # Top-5 highest-lift predicates.
    discs = rein["discoveries"]
    top = sorted(discs, key=lambda d: d.held_out_lift, reverse=True)[:5]
    if top:
        print("\n[4] Top-5 highest held-out-lift predicates discovered by REINFORCE")
        for d in top:
            print(
                f"  predicate={d.predicate}  "
                f"lift={d.held_out_lift:.2f}x  "
                f"match_test={d.match_group_size_test}  "
                f"reward={d.reward:.2f}  "
                f"tags={d.tags}"
            )

    # Verdict.
    pass_lift = (
        lift >= 5.0
        if math.isfinite(lift) and rand_mean > 0
        else (rein_mean - rand_mean > 5.0)
    )
    pass_p = p < 1e-3 if math.isfinite(p) else False
    overall = pass_lift and pass_p

    print("\n[5] Verdict")
    print(f"  REINFORCE >> random:  {'PASS' if pass_lift else 'FAIL'}")
    print(f"  p-value < 1e-3:       {'PASS' if pass_p else 'FAIL'}")
    print(f"  OVERALL:              {'PASS' if overall else 'FAIL'}")

    env_rein.close()
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
