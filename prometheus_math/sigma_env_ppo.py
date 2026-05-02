"""prometheus_math.sigma_env_ppo — learning-agent baselines on SigmaMathEnv.

Acceptance test for the BIND/EVAL pivot (pivot/techne.md §4.4): is the
reward signal actually *learnable*, not merely well-formed? Ships three
agents and a comparison harness:

- ``train_baseline_random``: uniform-random action, the floor we must beat.
- ``train_reinforce``: hand-rolled REINFORCE / policy gradient with a
  categorical softmax over the discrete action space. Numpy-only; no
  hard dependency on torch. ~50 LOC of update math.
- ``train_ppo``: thin wrapper around stable_baselines3.PPO. Skip-with-
  message if SB3 isn't installed; document the fallback path to REINFORCE.
- ``compare_random_vs_learned``: multi-seed comparison with Welch t-test.
- ``learning_curve_plot``: optional matplotlib PNG.

The action space here is *contextual but stateless* — the obs vector
summarises substrate state but doesn't condition the action. The right
baseline is therefore a contextual-bandit-class learner (categorical
policy over the discrete action set), not a deep RL agent. PPO works
too — it just learns a stationary policy over a one-step problem.

Because the env auto-terminates on a successful pick (target hit), we
auto-reset after termination so an "episode" of n_steps is really a
sequence of contiguous one-step bandit pulls. Each step's reward is
attributed to the action taken at that step; this is the right signal
shape for a softmax bandit.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_reset(env: Any, seed: Optional[int] = None) -> tuple:
    """Reset, returning (obs, info, n_actions). Tolerates numpy-int seeds."""
    if seed is not None:
        seed = int(seed)
    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", getattr(env.action_space, "n", 1)))
    return obs, info, n_actions


def _summarize_run(
    rewards: np.ndarray,
    n_terminations: int,
    best_value: Optional[float],
    extras: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Standard return shape for all training fns."""
    rewards = np.asarray(rewards, dtype=np.float64)
    if rewards.size == 0:
        mean_r = 0.0
        mean_per_ep = 0.0
    else:
        mean_r = float(rewards.mean())
        mean_per_ep = (
            float(rewards.sum() / max(1, n_terminations))
            if n_terminations > 0
            else float(rewards.sum())
        )
    out = {
        "rewards": rewards,
        "mean_reward": mean_r,
        "mean_reward_per_episode": mean_per_ep,
        "n_terminations": int(n_terminations),
        "best_value": float(best_value) if best_value is not None else None,
        "n_steps": int(rewards.size),
    }
    if extras:
        out.update(extras)
    return out


def _track_best(
    info: Dict[str, Any], best_value: Optional[float]
) -> Optional[float]:
    """Track minimum-Mahler (or other) finite output across an episode."""
    v = info.get("output_value")
    try:
        v = float(v)
    except (TypeError, ValueError):
        return best_value
    if not math.isfinite(v) or v < 1.0 - 1e-9:
        return best_value
    if best_value is None or v < best_value:
        return v
    return best_value


# ---------------------------------------------------------------------------
# Random baseline
# ---------------------------------------------------------------------------


def train_baseline_random(
    env_factory: Callable[[], Any],
    n_steps: int = 10000,
    seed: int = 0,
) -> Dict[str, Any]:
    """Run a uniform-random-action agent for ``n_steps``.

    Auto-resets the env on termination so n_steps is the contiguous step
    budget across multiple episodes.

    Returns a dict matching ``_summarize_run``.
    """
    if n_steps < 0:
        raise ValueError(f"n_steps must be >= 0, got {n_steps}")
    env = env_factory()
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_steps, dtype=np.float64)
    n_term = 0
    best_value: Optional[float] = None
    if n_steps == 0:
        return _summarize_run(rewards, n_term, best_value)
    _, _, n_actions = _safe_reset(env, seed=seed)
    for t in range(n_steps):
        a = int(rng.integers(0, n_actions))
        obs, r, term, trunc, info = env.step(a)
        rewards[t] = float(r)
        best_value = _track_best(info, best_value)
        if term or trunc:
            n_term += 1
            _, _, n_actions = _safe_reset(env, seed=int(rng.integers(0, 2**31 - 1)))
    return _summarize_run(rewards, n_term, best_value, {"agent": "random"})


# ---------------------------------------------------------------------------
# REINFORCE (numpy, no torch dependency)
# ---------------------------------------------------------------------------


def _softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max()
    e = np.exp(z)
    return e / e.sum()


def train_reinforce(
    env_factory: Callable[[], Any],
    n_steps: int = 10000,
    seed: int = 0,
    lr: float = 1e-2,
    log_interval: int = 500,
    baseline_decay: float = 0.99,
    reward_scale: float = 1.0 / 100.0,
) -> Dict[str, Any]:
    """Hand-rolled REINFORCE with a categorical softmax policy.

    Policy: pi(a) = softmax(theta)[a], where theta is a vector of
    logits, one per discrete action. Update per step:

        grad_theta_a log pi(a) = (1[a == taken] - pi(a))
        theta += lr * (R - baseline) * grad

    Baseline is an EMA of recent rewards (variance reduction). Because
    the obs is uninformative for action selection (action space is
    contextual-stateless), the policy is a stationary distribution; this
    is a contextual-bandit / multi-armed-bandit policy gradient, which
    is the right shape for the env.

    Numpy-only; no torch dependency. Returns the standard run dict plus
    ``policy_logits`` (final theta) and ``log`` (list of per-interval
    snapshots).
    """
    if n_steps < 0:
        raise ValueError(f"n_steps must be >= 0, got {n_steps}")
    if lr <= 0:
        raise ValueError(f"lr must be > 0, got {lr}")

    env = env_factory()
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_steps, dtype=np.float64)
    n_term = 0
    best_value: Optional[float] = None
    log: List[Dict[str, float]] = []

    if n_steps == 0:
        return _summarize_run(
            rewards,
            n_term,
            best_value,
            {"agent": "reinforce", "policy_logits": None, "log": log},
        )

    _, _, n_actions = _safe_reset(env, seed=seed)
    theta = np.zeros(n_actions, dtype=np.float64)
    baseline = 0.0
    interval_acc = 0.0
    interval_n = 0

    for t in range(n_steps):
        pi = _softmax(theta)
        # Categorical sample from pi.
        u = rng.random()
        cdf = np.cumsum(pi)
        a = int(np.searchsorted(cdf, u, side="right"))
        if a >= n_actions:
            a = n_actions - 1

        obs, r, term, trunc, info = env.step(a)
        rewards[t] = float(r)
        best_value = _track_best(info, best_value)

        # Scale reward into a sane numerical range (raw +100 makes
        # softmax updates unstable). reward_scale=1/100 puts the +100
        # branch at +1, +20 at +0.2, etc.
        r_scaled = float(r) * reward_scale
        advantage = r_scaled - baseline
        # grad log pi(a) = e_a - pi  (where e_a is one-hot).
        grad = -pi.copy()
        grad[a] += 1.0
        theta += lr * advantage * grad
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        interval_acc += float(r)
        interval_n += 1
        if log_interval and (t + 1) % log_interval == 0:
            entropy = -float(np.sum(pi * np.log(pi + 1e-12)))
            log.append(
                {
                    "step": t + 1,
                    "mean_reward_window": interval_acc / max(1, interval_n),
                    "entropy": entropy,
                    "argmax_action": int(np.argmax(theta)),
                    "argmax_prob": float(pi.max()),
                }
            )
            interval_acc = 0.0
            interval_n = 0

        if term or trunc:
            n_term += 1
            _, _, n_actions_new = _safe_reset(
                env, seed=int(rng.integers(0, 2**31 - 1))
            )
            # Action table size shouldn't change between resets; if it
            # somehow did, gracefully expand/contract theta.
            if n_actions_new != n_actions:
                if n_actions_new > n_actions:
                    pad = np.zeros(n_actions_new - n_actions)
                    theta = np.concatenate([theta, pad])
                else:
                    theta = theta[:n_actions_new]
                n_actions = n_actions_new

    return _summarize_run(
        rewards,
        n_term,
        best_value,
        {
            "agent": "reinforce",
            "policy_logits": theta.tolist(),
            "policy_probs": _softmax(theta).tolist(),
            "log": log,
        },
    )


# ---------------------------------------------------------------------------
# PPO via stable_baselines3 (optional)
# ---------------------------------------------------------------------------


def train_ppo(
    env_factory: Callable[[], Any],
    n_steps: int = 10000,
    seed: int = 0,
    log_interval: int = 500,
) -> Dict[str, Any]:
    """Wrapper around stable_baselines3.PPO.

    Skip-with-message if SB3 isn't installed. The fallback is to use
    ``train_reinforce``; for our contextual-bandit-class problem they
    converge to similar policies but REINFORCE has substantially less
    overhead and no nn-init nondeterminism.
    """
    try:
        import stable_baselines3 as sb3
        from stable_baselines3 import PPO
        from stable_baselines3.common.monitor import Monitor
        from stable_baselines3.common.vec_env import DummyVecEnv
    except ImportError as e:
        return {
            "agent": "ppo",
            "skipped": True,
            "reason": f"stable_baselines3 not installed ({e}); fallback: train_reinforce",
            "rewards": np.zeros(0, dtype=np.float64),
            "mean_reward": 0.0,
            "mean_reward_per_episode": 0.0,
            "n_terminations": 0,
            "best_value": None,
            "n_steps": 0,
        }

    # SB3 expects a true Gymnasium-spec env. Ours is compatible but the
    # action_space.sample() / observation_space.sample() may differ
    # slightly. Wrap in a tiny adapter to force the right interface.
    def _make() -> Any:
        env = env_factory()
        # Auto-reset on termination is needed for a continuous step count.
        return _AutoResetWrapper(Monitor(_GymCompatWrapper(env)))

    vec = DummyVecEnv([_make])
    model = PPO("MlpPolicy", vec, seed=seed, verbose=0)
    t0 = time.time()
    model.learn(total_timesteps=n_steps)
    elapsed = time.time() - t0

    # After training, evaluate the policy by running n_steps with the
    # learned model (deterministic=False for stochastic eval).
    eval_env = _AutoResetWrapper(_GymCompatWrapper(env_factory()))
    obs, _ = eval_env.reset(seed=seed)
    rewards = np.zeros(n_steps, dtype=np.float64)
    best_value: Optional[float] = None
    n_term = 0
    for t in range(n_steps):
        action, _ = model.predict(obs, deterministic=False)
        obs, r, term, trunc, info = eval_env.step(int(action))
        rewards[t] = float(r)
        best_value = _track_best(info, best_value)
        if term or trunc:
            n_term += 1
            obs, _ = eval_env.reset()
    return _summarize_run(
        rewards,
        n_term,
        best_value,
        {"agent": "ppo", "training_seconds": elapsed},
    )


class _GymCompatWrapper:
    """Minimal adapter to force gymnasium-style 5-tuple step + dict info."""

    def __init__(self, env: Any):
        self._env = env
        self.observation_space = env.observation_space
        self.action_space = env.action_space
        self.metadata = getattr(env, "metadata", {})
        self.spec = None
        self.render_mode = None

    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict] = None):
        return self._env.reset(seed=int(seed) if seed is not None else None)

    def step(self, action):
        return self._env.step(int(action))

    def close(self):
        return self._env.close()

    def render(self):
        return None


class _AutoResetWrapper:
    """Auto-reset on terminated/truncated so a continuous step budget works."""

    def __init__(self, env: Any):
        self._env = env
        self.observation_space = env.observation_space
        self.action_space = env.action_space
        self.metadata = getattr(env, "metadata", {})
        self.spec = None
        self.render_mode = None

    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict] = None):
        return self._env.reset(seed=seed)

    def step(self, action):
        obs, r, term, trunc, info = self._env.step(action)
        if term or trunc:
            obs, _ = self._env.reset()
        return obs, r, term, trunc, info

    def close(self):
        return self._env.close()

    def render(self):
        return None


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def _welch_t_test(a: np.ndarray, b: np.ndarray) -> float:
    """One-sided Welch t-test p-value: H1 = mean(a) > mean(b).

    Falls back to scipy if available; otherwise computes the two-sided
    p from Welch's formula and halves it for the one-sided case.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size < 2:
        return float("nan")
    try:
        from scipy import stats

        t, p_two = stats.ttest_ind(a, b, equal_var=False, alternative="greater")
        return float(p_two)
    except ImportError:
        pass
    ma, mb = a.mean(), b.mean()
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / a.size + vb / b.size)
    if se == 0:
        return 0.0 if ma > mb else 1.0
    t = (ma - mb) / se
    # Approximate two-sided p with normal tail; one-sided = half.
    p_two = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))
    return p_two / 2.0 if ma > mb else 1.0 - p_two / 2.0


def compare_random_vs_learned(
    env_factory: Callable[[], Any],
    n_steps: int = 10000,
    n_seeds: int = 3,
    learner: str = "reinforce",
    learner_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run random and learned across n_seeds; return aggregate stats.

    Returns:
        {
            "random_mean", "random_std", "random_means" (per-seed),
            "learned_mean", "learned_std", "learned_means" (per-seed),
            "lift" = (learned_mean - random_mean) / abs(random_mean),
            "p_value" = one-sided Welch t-test on per-seed means,
            "n_steps", "n_seeds", "learner",
            "rewards_random_curve" (mean over seeds, smoothed),
            "rewards_learned_curve" (mean over seeds, smoothed),
            "random_curve_std", "learned_curve_std",
        }
    """
    learner_kwargs = dict(learner_kwargs or {})
    if learner == "reinforce":
        train_fn = train_reinforce
    elif learner == "ppo":
        train_fn = train_ppo
    else:
        raise ValueError(f"unknown learner {learner!r}; choose 'reinforce' or 'ppo'")

    random_means = []
    learned_means = []
    random_curves = []
    learned_curves = []
    learned_skipped = False
    learned_skip_reason = ""

    for s in range(n_seeds):
        seed = int(s) * 1009 + 17
        r_run = train_baseline_random(env_factory, n_steps=n_steps, seed=seed)
        l_run = train_fn(env_factory, n_steps=n_steps, seed=seed, **learner_kwargs)
        if l_run.get("skipped"):
            learned_skipped = True
            learned_skip_reason = l_run.get("reason", "")
            break
        random_means.append(r_run["mean_reward"])
        learned_means.append(l_run["mean_reward"])
        random_curves.append(r_run["rewards"])
        learned_curves.append(l_run["rewards"])

    if learned_skipped:
        return {
            "skipped": True,
            "reason": learned_skip_reason,
            "n_steps": n_steps,
            "n_seeds": n_seeds,
            "learner": learner,
        }

    random_means_arr = np.asarray(random_means, dtype=np.float64)
    learned_means_arr = np.asarray(learned_means, dtype=np.float64)
    rmean = float(random_means_arr.mean())
    lmean = float(learned_means_arr.mean())
    denom = abs(rmean) if abs(rmean) > 1e-9 else 1.0
    lift = (lmean - rmean) / denom

    # Stack per-step curves (they should all be n_steps long).
    rcurve = np.stack(random_curves, axis=0)  # (n_seeds, n_steps)
    lcurve = np.stack(learned_curves, axis=0)
    rcurve_mean = rcurve.mean(axis=0)
    lcurve_mean = lcurve.mean(axis=0)
    rcurve_std = rcurve.std(axis=0)
    lcurve_std = lcurve.std(axis=0)

    p_value = _welch_t_test(learned_means_arr, random_means_arr)

    return {
        "random_mean": rmean,
        "random_std": float(random_means_arr.std(ddof=1) if n_seeds > 1 else 0.0),
        "random_means": random_means_arr.tolist(),
        "learned_mean": lmean,
        "learned_std": float(learned_means_arr.std(ddof=1) if n_seeds > 1 else 0.0),
        "learned_means": learned_means_arr.tolist(),
        "lift": float(lift),
        "p_value": float(p_value),
        "n_steps": int(n_steps),
        "n_seeds": int(n_seeds),
        "learner": learner,
        "rewards_random_curve": rcurve_mean,
        "rewards_learned_curve": lcurve_mean,
        "random_curve_std": rcurve_std,
        "learned_curve_std": lcurve_std,
    }


# ---------------------------------------------------------------------------
# Plotting (optional)
# ---------------------------------------------------------------------------


def learning_curve_plot(
    comparison_result: Dict[str, Any],
    path: str,
    smooth_window: int = 200,
) -> Optional[str]:
    """Save a matplotlib PNG showing both curves with std bands.

    Skip-with-message if matplotlib not installed or comparison_result
    is a skipped run. Returns the path on success, None on skip.
    """
    if comparison_result.get("skipped"):
        return None
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("learning_curve_plot: matplotlib not installed; skipping plot")
        return None

    rcurve = np.asarray(comparison_result["rewards_random_curve"], dtype=np.float64)
    lcurve = np.asarray(comparison_result["rewards_learned_curve"], dtype=np.float64)
    rstd = np.asarray(comparison_result["random_curve_std"], dtype=np.float64)
    lstd = np.asarray(comparison_result["learned_curve_std"], dtype=np.float64)

    def _smooth(x: np.ndarray, w: int) -> np.ndarray:
        if w <= 1 or x.size <= w:
            return x
        kernel = np.ones(w, dtype=np.float64) / w
        return np.convolve(x, kernel, mode="same")

    w = max(1, smooth_window)
    rs = _smooth(rcurve, w)
    ls = _smooth(lcurve, w)
    rss = _smooth(rstd, w)
    lss = _smooth(lstd, w)
    x = np.arange(rs.size)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, rs, label=f"random (mean={comparison_result['random_mean']:.2f})", color="tab:gray")
    ax.fill_between(x, rs - rss, rs + rss, color="tab:gray", alpha=0.2)
    ax.plot(
        x,
        ls,
        label=f"learned ({comparison_result['learner']}, mean={comparison_result['learned_mean']:.2f})",
        color="tab:blue",
    )
    ax.fill_between(x, ls - lss, ls + lss, color="tab:blue", alpha=0.2)
    ax.set_xlabel("step")
    ax.set_ylabel(f"reward (smoothed window={w})")
    ax.set_title(
        f"SigmaMathEnv learning curve | lift={comparison_result['lift']:+.3f}"
        f" p={comparison_result['p_value']:.3g}"
    )
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


__all__ = [
    "train_baseline_random",
    "train_reinforce",
    "train_ppo",
    "compare_random_vs_learned",
    "learning_curve_plot",
]
