"""prometheus_math.modal_collapse_continuous -- Aporia diagnostic, day 2.

Decisive Day-2 follow-up to ``modal_collapse_synthetic`` (Case A verdict).

Yesterday's finding: identical RL training pipeline (REINFORCE-linear,
PPO-MLP) on a continuous-output regression cast as a 21-bin classifier
with **binary 0/1 reward** collapsed at the search-mechanism layer.
REINFORCE crushed to <=3 bins on every variant; PPO stayed uniform; on
V3 (low-noise, balanced, lstsq solves at >=60%) REINFORCE matched
random. Verdict: substrate broken at Layer 2.

ChatGPT's reframe: scalar 0/1 reward "projects the gradient away" at
the reward boundary. The simplest Layer-2 fix is a *continuous* reward
that exposes a gradient even when the predicted bin is wrong. The
deeper upgrade -- yet to be tested -- is kill-vector navigation
(structured, multi-channel signal).

THE QUESTION
-------------
Is continuous scalar reward sufficient to break modal collapse, or is
kill-vector navigation actually required?

THE TEST
--------
Identical env, identical trainers, identical hyperparameters. The only
change is the reward signal:

    Reward variant A:  r = -(predicted_y - true_y)^2          (L2)
    Reward variant B:  r = -|predicted_y - true_y|            (L1)
    Reward variant C:  r = -log(1 + |predicted_y - true_y|)   (log)

The action remains a discrete bin index in [0, N_BINS); we map it to
the bin-center y, then compute the continuous error against the true
y. All three rewards are non-positive (perfect prediction = 0).

To keep the trainer hyperparameters apples-to-apples with the binary
case (where ``reward_scale = 1.0 / REWARD_HIT = 1/100`` and rewards lie
in {0, 100}), we **rescale and clip** all three reward shapes so the
dynamic range is [-REWARD_FLOOR, 0] with REWARD_FLOOR = 100. Both the
mean and gradient magnitude of the reward signal are then commensurate
with the binary baseline; only the *shape* of the gradient surface
changes.

VERDICT FRAMEWORK
-----------------
Per-bin prediction distribution (mean of seeds) is the diagnostic.

- Case A persists: REINFORCE still collapses to <=3 bins on V3;
  continuous reward did NOT fix Layer 2; kill-vector navigation is
  the actual upgrade.
- Case B emerges: predictions track truth across many bins on V3;
  continuous reward IS sufficient for Layer 2; kill-vector is over-
  engineering.
- Case C intermediate: partial improvement (>= 8 active bins but not
  matching lstsq) -- both fixes have value; sequence matters.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

# Reuse env, history features, and the round-trip helpers from the
# binary diagnostic. We deliberately do NOT modify modal_collapse_synthetic.
from prometheus_math.modal_collapse_synthetic import (
    DEFAULT_D,
    HISTORY_DIM,
    N_BINS,
    SyntheticRegressionEnv,
)


# ---------------------------------------------------------------------------
# Continuous-reward configuration
# ---------------------------------------------------------------------------

# Floor for the continuous reward (so the trainer's reward_scale = 1/100
# still produces commensurate advantage magnitudes vs the binary case).
REWARD_FLOOR: float = 100.0

REWARD_VARIANTS: Tuple[str, str, str] = ("L2", "L1", "log")


def _bin_center(env: SyntheticRegressionEnv, bin_idx: int) -> float:
    """Predicted y at the *center* of bin ``bin_idx``.

    Outermost bins are unbounded by construction in the SKEWED binning
    (edges = [-1e9, ..., +1e9]); for those we return the inner edge so
    the bin "center" is finite and the L2/L1 error is well-defined.
    """
    edges = env.edges()
    n = env.n_bins()
    if bin_idx < 0 or bin_idx >= n:
        raise ValueError(f"bin_idx {bin_idx} out of [0, {n})")
    lo = edges[bin_idx]
    hi = edges[bin_idx + 1]
    # Outer bins in the skewed regime have edges [-1e9, ...] / [..., +1e9].
    # Use the finite inner edge as the representative y; this is the
    # only sane choice for the L2/L1/log error since the analytic center
    # would diverge.
    if lo < -1e8:
        return float(hi)
    if hi > +1e8:
        return float(lo)
    return 0.5 * float(lo + hi)


def bin_centers(env: SyntheticRegressionEnv) -> np.ndarray:
    """Vector of bin centers for the env (length n_bins)."""
    return np.array(
        [_bin_center(env, k) for k in range(env.n_bins())],
        dtype=np.float64,
    )


def _continuous_reward_raw(predicted_y: float, true_y: float, variant: str) -> float:
    """Raw continuous reward (before clipping/scaling). Always <= 0.

    Variants:
      - "L2":  -(predicted - true)^2
      - "L1":  -|predicted - true|
      - "log": -log(1 + |predicted - true|)
    """
    err = float(predicted_y) - float(true_y)
    abs_err = abs(err)
    if variant == "L2":
        return -(err * err)
    if variant == "L1":
        return -abs_err
    if variant == "log":
        return -math.log1p(abs_err)
    raise ValueError(f"unknown reward variant {variant!r}")


def _scale_factor(variant: str) -> float:
    """Per-variant multiplier so the typical worst-case error maps to
    approximately -REWARD_FLOOR.

    Calibration uses the env's marginal y stdev ~= 1 (||w||=1 + sigma).
    A "very wrong" prediction sits ~3 stdev away, so |err| ~ 3:

       L2:  err^2 ~ 9        -> scale = REWARD_FLOOR / 9
       L1:  |err| ~ 3        -> scale = REWARD_FLOOR / 3
       log: log(1+3) ~ 1.39  -> scale = REWARD_FLOOR / 1.39

    Final reward = clip(scale * raw, -REWARD_FLOOR, 0). The clip is
    rarely active in practice but bounds gradient magnitude (matters
    for V4 where sigma=0.5 stretches the tails).
    """
    if variant == "L2":
        return REWARD_FLOOR / 9.0
    if variant == "L1":
        return REWARD_FLOOR / 3.0
    if variant == "log":
        return REWARD_FLOOR / math.log1p(3.0)
    raise ValueError(f"unknown reward variant {variant!r}")


def continuous_reward(
    predicted_y: float,
    true_y: float,
    variant: str,
) -> float:
    """Final continuous reward: scaled and clipped to [-REWARD_FLOOR, 0]."""
    raw = _continuous_reward_raw(predicted_y, true_y, variant)
    scaled = _scale_factor(variant) * raw
    if scaled < -REWARD_FLOOR:
        return -REWARD_FLOOR
    if scaled > 0.0:
        return 0.0
    return float(scaled)


# ---------------------------------------------------------------------------
# Continuous-reward trainers (byte-for-byte mirrors of the binary trainers
# from modal_collapse_synthetic, with the reward swap as the only change)
# ---------------------------------------------------------------------------


def _step_with_continuous_reward(
    env: SyntheticRegressionEnv,
    action: int,
    centers: np.ndarray,
    variant: str,
) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
    """Drop-in replacement for ``env.step(action)`` that returns the
    continuous reward.

    The env's internal counters still receive the binary 0/1 hit
    semantics (so running_accuracy keeps its meaning), but the trainer
    sees the continuous reward instead.
    """
    obs, _binary_r, term, trunc, info = env.step(int(action))
    pred_y = float(centers[int(action)])
    true_y = float(info.get("y", 0.0))
    cont_r = continuous_reward(pred_y, true_y, variant)
    info = dict(info)
    info["binary_reward"] = float(_binary_r)
    info["continuous_reward"] = cont_r
    info["predicted_y"] = pred_y
    info["reward_variant"] = variant
    return obs, cont_r, term, trunc, info


def train_random(
    env: SyntheticRegressionEnv,
    n_episodes: int,
    *,
    reward_variant: str,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random baseline with continuous reward."""
    if reward_variant not in REWARD_VARIANTS:
        raise ValueError(f"reward_variant must be in {REWARD_VARIANTS}")
    rng = np.random.default_rng(seed)
    centers = bin_centers(env)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(env.n_bins(), dtype=np.int64)
    near_one = 0
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, env.n_bins()))
        pred_counts[a] += 1
        _, r, _, _, info = _step_with_continuous_reward(env, a, centers, reward_variant)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if abs(int(info.get("predicted_bin", -10))
               - int(info.get("true_bin", -100))) <= 1:
            near_one += 1
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "resolution_score": float(near_one / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "random",
        "reward_variant": reward_variant,
        "pred_counts": pred_counts.tolist(),
    }


def train_reinforce(
    env: SyntheticRegressionEnv,
    n_episodes: int,
    *,
    reward_variant: str,
    lr: float = 0.02,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """REINFORCE-linear with continuous reward.

    Hyperparameters and update rule are identical to
    ``modal_collapse_synthetic.train_reinforce`` -- only the reward
    signal changes. ``reward_scale = 1/100`` still applies because the
    continuous reward is calibrated to the [-100, 0] range.
    """
    if reward_variant not in REWARD_VARIANTS:
        raise ValueError(f"reward_variant must be in {REWARD_VARIANTS}")
    rng = np.random.default_rng(seed)
    obs_dim = env.obs_dim()
    n_actions = env.n_bins()
    W = np.zeros((n_actions, obs_dim), dtype=np.float64)
    b = np.zeros(n_actions, dtype=np.float64)
    centers = bin_centers(env)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    baseline = 0.0
    pred_counts = np.zeros(n_actions, dtype=np.int64)
    near_one = 0

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        z = logits - logits.max()
        probs = np.exp(z)
        probs = probs / probs.sum()
        a = int(rng.choice(n_actions, p=probs))
        pred_counts[a] += 1
        _, r, _, _, info = _step_with_continuous_reward(env, a, centers, reward_variant)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if abs(int(info.get("predicted_bin", -10))
               - int(info.get("true_bin", -100))) <= 1:
            near_one += 1

        r_scaled = float(r) * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        grad_a = -probs.copy()
        grad_a[a] += 1.0
        log_p = np.log(probs + 1e-12)
        entropy_grad = probs * (log_p - (probs * log_p).sum())
        total_grad = advantage * grad_a + entropy_coef * (-entropy_grad)
        W += lr * np.outer(total_grad, obs)
        b += lr * total_grad

    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "resolution_score": float(near_one / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "reinforce",
        "reward_variant": reward_variant,
        "pred_counts": pred_counts.tolist(),
    }


def _softmax(x: np.ndarray) -> np.ndarray:
    z = x - x.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def train_ppo(
    env: SyntheticRegressionEnv,
    n_episodes: int,
    *,
    reward_variant: str,
    lr: float = 0.005,
    hidden: int = 32,
    clip_eps: float = 0.2,
    n_epochs: int = 4,
    batch_size: int = 64,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """PPO-MLP with continuous reward (mirror of binary PPO trainer)."""
    if reward_variant not in REWARD_VARIANTS:
        raise ValueError(f"reward_variant must be in {REWARD_VARIANTS}")
    rng = np.random.default_rng(seed)
    obs_dim = env.obs_dim()
    n_actions = env.n_bins()
    h = int(hidden)

    rng_torch = np.random.default_rng(seed + 1)
    W1 = rng_torch.standard_normal((h, obs_dim)) * (1.0 / math.sqrt(obs_dim))
    b1 = np.zeros(h, dtype=np.float64)
    Wp = rng_torch.standard_normal((n_actions, h)) * (1.0 / math.sqrt(h))
    bp = np.zeros(n_actions, dtype=np.float64)
    Wv = rng_torch.standard_normal((1, h)) * (1.0 / math.sqrt(h))
    bv = np.zeros(1, dtype=np.float64)

    centers = bin_centers(env)

    def _forward(obs: np.ndarray):
        single = obs.ndim == 1
        if single:
            obs = obs[None, :]
        h_pre = obs @ W1.T + b1
        h_act = np.maximum(h_pre, 0.0)
        logits = h_act @ Wp.T + bp
        value = (h_act @ Wv.T + bv).squeeze(-1)
        probs = _softmax(logits)
        if single:
            return probs[0], value[0], h_act[0], obs[0]
        return probs, value, h_act, obs

    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(n_actions, dtype=np.int64)
    near_one = 0

    buf_obs: List[np.ndarray] = []
    buf_act: List[int] = []
    buf_logp: List[float] = []
    buf_adv: List[float] = []
    buf_ret: List[float] = []
    reward_scale = 1.0 / REWARD_FLOOR  # same magnitude as binary 1/REWARD_HIT

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        probs, value, _h, _ = _forward(obs)
        a = int(rng.choice(n_actions, p=probs))
        pred_counts[a] += 1
        logp_old = float(np.log(probs[a] + 1e-12))
        _, r, _, _, info = _step_with_continuous_reward(env, a, centers, reward_variant)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if abs(int(info.get("predicted_bin", -10))
               - int(info.get("true_bin", -100))) <= 1:
            near_one += 1

        ret = float(r) * reward_scale
        adv = ret - float(value)

        buf_obs.append(obs.astype(np.float64))
        buf_act.append(a)
        buf_logp.append(logp_old)
        buf_adv.append(adv)
        buf_ret.append(ret)

        if len(buf_obs) >= batch_size:
            obs_arr = np.stack(buf_obs, axis=0)
            act_arr = np.asarray(buf_act, dtype=np.int64)
            logp_old_arr = np.asarray(buf_logp, dtype=np.float64)
            adv_arr = np.asarray(buf_adv, dtype=np.float64)
            ret_arr = np.asarray(buf_ret, dtype=np.float64)
            if adv_arr.std() > 1e-8:
                adv_arr = (adv_arr - adv_arr.mean()) / (adv_arr.std() + 1e-8)

            for _epoch in range(n_epochs):
                h_pre = obs_arr @ W1.T + b1
                h_act = np.maximum(h_pre, 0.0)
                logits = h_act @ Wp.T + bp
                values = (h_act @ Wv.T + bv).squeeze(-1)
                probs_new = _softmax(logits)
                logp_new = np.log(
                    probs_new[np.arange(obs_arr.shape[0]), act_arr] + 1e-12
                )
                ratio = np.exp(logp_new - logp_old_arr)
                use_clip = (
                    ((ratio > 1.0 + clip_eps) & (adv_arr > 0)) |
                    ((ratio < 1.0 - clip_eps) & (adv_arr < 0))
                )
                effective_ratio = np.where(use_clip, 0.0, ratio * adv_arr)
                onehot = np.zeros_like(probs_new)
                onehot[np.arange(obs_arr.shape[0]), act_arr] = 1.0
                d_logits = -effective_ratio[:, None] * (onehot - probs_new)
                lp = np.log(probs_new + 1e-12)
                ent_grad = -probs_new * (lp + 1.0) + probs_new * (
                    (probs_new * (lp + 1.0)).sum(axis=-1, keepdims=True)
                )
                d_logits = d_logits - entropy_coef * ent_grad

                grad_Wp = d_logits.T @ h_act
                grad_bp = d_logits.sum(axis=0)
                grad_h_pol = d_logits @ Wp

                v_err = values - ret_arr
                grad_Wv = (v_err[:, None] * h_act).sum(axis=0, keepdims=True)
                grad_bv = np.array([v_err.sum()])
                grad_h_v = v_err[:, None] @ Wv

                grad_h_total = grad_h_pol + grad_h_v
                relu_mask = (h_pre > 0).astype(np.float64)
                grad_pre = grad_h_total * relu_mask
                grad_W1 = grad_pre.T @ obs_arr
                grad_b1 = grad_pre.sum(axis=0)

                bs = float(obs_arr.shape[0])
                Wp -= lr * grad_Wp / bs
                bp -= lr * grad_bp / bs
                Wv -= lr * grad_Wv / bs
                bv -= lr * grad_bv / bs
                W1 -= lr * grad_W1 / bs
                b1 -= lr * grad_b1 / bs

            buf_obs.clear()
            buf_act.clear()
            buf_logp.clear()
            buf_adv.clear()
            buf_ret.clear()

    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "resolution_score": float(near_one / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "ppo",
        "reward_variant": reward_variant,
        "pred_counts": pred_counts.tolist(),
    }


# ---------------------------------------------------------------------------
# Diagnostic comparison driver
# ---------------------------------------------------------------------------


VARIANTS: Dict[str, Dict[str, Any]] = {
    "V1_balanced":      {"binning": "balanced", "sigma": 0.1},
    "V2_skewed":        {"binning": "skewed",   "sigma": 0.1},
    "V3_low_noise":     {"binning": "balanced", "sigma": 0.01},
    "V4_skewed_high":   {"binning": "skewed",   "sigma": 0.5},
}


def run_diagnostic(
    n_episodes: int = 5000,
    seeds: Tuple[int, ...] = (0, 1, 2),
    reward_variants: Tuple[str, ...] = REWARD_VARIANTS,
    d: int = DEFAULT_D,
    n_bins: int = N_BINS,
    corpus_seed: int = 0,
) -> Dict[str, Any]:
    """3 reward variants x 4 env variants x 3 algorithms x ``len(seeds)`` seeds.

    Returns a nested dict::

        {
          "L2": {
             "V1_balanced": { "random": {...}, "reinforce": {...}, "ppo": {...} },
             ...
          },
          "L1": {...},
          "log": {...},
          "verdict": "A_persists" | "B_emerges" | "C_intermediate",
          "n_episodes": ...,
          "n_seeds": ...,
        }
    """
    out: Dict[str, Any] = {
        "n_episodes": n_episodes,
        "n_seeds": len(seeds),
        "d": d,
        "n_bins": n_bins,
        "rewards": {},
    }
    trainers = [
        ("random", train_random),
        ("reinforce", train_reinforce),
        ("ppo", train_ppo),
    ]
    for r_variant in reward_variants:
        if r_variant not in REWARD_VARIANTS:
            raise ValueError(f"unknown reward variant {r_variant!r}")
        r_block: Dict[str, Any] = {}
        for v_name, v_kwargs in VARIANTS.items():
            v_results: Dict[str, Any] = {}
            for agent_name, fn in trainers:
                accs: List[float] = []
                ress: List[float] = []
                rew_means: List[float] = []
                pred_count_seeds: List[np.ndarray] = []
                for s in seeds:
                    env = SyntheticRegressionEnv(
                        d=d, n_bins=n_bins,
                        corpus_seed=corpus_seed,
                        seed=s,
                        **v_kwargs,
                    )
                    res = fn(
                        env, n_episodes=n_episodes,
                        reward_variant=r_variant, seed=s,
                    )
                    accs.append(res["accuracy"])
                    ress.append(res["resolution_score"])
                    rew_means.append(res["mean_reward"])
                    pred_count_seeds.append(np.asarray(res["pred_counts"]))
                    env.close()
                pc_mean = np.mean(np.stack(pred_count_seeds, axis=0), axis=0)
                v_results[agent_name] = {
                    "acc_mean":   float(np.mean(accs)),
                    "acc_std":    float(np.std(accs)),
                    "res_mean":   float(np.mean(ress)),
                    "res_std":    float(np.std(ress)),
                    "reward_mean": float(np.mean(rew_means)),
                    "reward_std":  float(np.std(rew_means)),
                    "pred_counts_mean": pc_mean.tolist(),
                    "active_bins": int(
                        np.sum(pc_mean / pc_mean.sum() >= 0.01)
                    ),
                }
            r_block[v_name] = v_results
        out["rewards"][r_variant] = r_block

    out["verdict"] = _classify_verdict(out)
    return out


def _classify_verdict(report: Dict[str, Any]) -> str:
    """Classify the continuous-reward outcome relative to Day-1's Case A.

    Decisive variant: V3_low_noise (lstsq solves at >=60%). Across all
    three reward variants, look at REINFORCE and PPO behavior on V3.

    Two failure modes from Day 1 *both* count as collapse, not progress:
      (i) REINFORCE collapse signature: <=3 active bins.
      (ii) PPO uniform signature: 21 active bins AT random-baseline
           accuracy (it isn't "exploring widely", it's uninformed).
    "Real learning" requires BOTH: accuracy >= 2x random AND active
    bins covering a meaningful fraction (>=8) of the action space.

    - "A_persists":   For ALL three reward variants, on V3 neither
      REINFORCE nor PPO reaches accuracy >= 2x random with active_bins
      >= 8. Continuous reward did NOT fix Layer 2.
    - "B_emerges":    For at least ONE reward variant, BOTH trainers
      on V3 reach accuracy >= 4x random AND active_bins >= 8.
      Continuous reward IS sufficient.
    - "C_intermediate": One trainer learns, or partial lift with
      genuine bin coverage (>=2x random AND active_bins >= 8).
    """
    rewards = report.get("rewards", {})
    if not rewards:
        return "indeterminate"

    any_full_recovery = False
    any_partial_improvement = False

    for r_variant, r_block in rewards.items():
        v3 = r_block.get("V3_low_noise", {})
        if not v3:
            continue
        rand_acc = v3.get("random", {}).get("acc_mean", 0.0)
        re_acc = v3.get("reinforce", {}).get("acc_mean", 0.0)
        ppo_acc = v3.get("ppo", {}).get("acc_mean", 0.0)
        re_active = v3.get("reinforce", {}).get("active_bins", 0)
        ppo_active = v3.get("ppo", {}).get("active_bins", 0)

        # "Learned" = both accuracy lift AND broad bin coverage.
        re_learned = (re_acc >= 4.0 * max(rand_acc, 1e-6) and re_active >= 8)
        ppo_learned = (ppo_acc >= 4.0 * max(rand_acc, 1e-6) and ppo_active >= 8)
        # "Partial" = >=2x random with >=8 active bins. Uniform PPO
        # at random accuracy does NOT count as partial.
        re_partial = (re_acc >= 2.0 * max(rand_acc, 1e-6) and re_active >= 8)
        ppo_partial = (ppo_acc >= 2.0 * max(rand_acc, 1e-6) and ppo_active >= 8)

        if re_learned and ppo_learned:
            any_full_recovery = True
        if re_learned or ppo_learned or re_partial or ppo_partial:
            any_partial_improvement = True

    if any_full_recovery:
        return "B_emerges"
    if any_partial_improvement:
        return "C_intermediate"
    return "A_persists"


__all__ = [
    "REWARD_FLOOR",
    "REWARD_VARIANTS",
    "VARIANTS",
    "continuous_reward",
    "bin_centers",
    "train_random",
    "train_reinforce",
    "train_ppo",
    "run_diagnostic",
]
