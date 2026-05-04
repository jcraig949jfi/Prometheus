"""prometheus_math.modal_collapse_synthetic -- Aporia diagnostic.

Decisive 1-hour test: is the cross-domain modal-class collapse a real
substrate finding, or a textbook RL pathology rediscovered six times?

Across 6 real domains (BSD rank, modular forms, knot trace fields,
genus-2, OEIS Sleeping Beauty, mock theta) the same RL pipeline
collapses to predicting the modal class. Aporia's diagnosis: with a
sparse 0/1 reward, episode length 1, and entropy-floor REINFORCE/PPO,
the agent collapses to whichever output prior maximizes expected reward
-- which is the modal class -- regardless of the input. We may be
rediscovering a six-fold confirmation of this RL failure mode.

THE TEST
--------
Train the same training loops on a synthetic continuous-output target:

    y = w . x + b + epsilon                (linearly separable, R^d -> R)
    bin y into K=21 cells                  (matching the modular form env)
    reward = 1 if predicted bin == true bin else 0

If the substrate is fundamentally broken, the agent collapses on this
linearly trivial regression too (Case A). If the agent learns the
linear map and uses many bins, the real domains were the cause -- the
cross-domain "finding" is a spurious confirmation of class-prior
recovery (Case B). If it's a mix, both fixes are needed (Case C).

Four variants:
- V1 BALANCED:        uniform y distribution
- V2 SKEWED:          Gaussian y (concentrates ~50% mass in 3 bins)
- V3 BALANCED + low-noise: sigma=0.01, sanity that the env CAN learn
- V4 SKEWED + high-noise:  sigma=0.5, the real-domain stress test

The agents (random_uniform, REINFORCE-linear, PPO-MLP) are
byte-for-byte ports of ``train_random``, ``train_reinforce``, and
``train_ppo`` from ``modular_form_env.py``. Only the env varies.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Constants matching the real envs
# ---------------------------------------------------------------------------

N_BINS: int = 21              # matches modular_form_env.N_BINS
REWARD_HIT: float = 100.0     # matches modular_form_env / bsd_rank_env
REWARD_MISS: float = 0.0
HISTORY_DIM: int = 6          # matches bsd_rank_env layout

# Default hidden problem geometry. d=20 obs vector + 6 history features.
DEFAULT_D: int = 20


# ---------------------------------------------------------------------------
# Synthetic regression env
# ---------------------------------------------------------------------------


@dataclass
class _EpisodeState:
    n_episodes_seen: int = 0
    n_correct: int = 0
    last_reward: float = 0.0
    last_pred_bin: int = -1
    last_true_bin: int = -1


class SyntheticRegressionEnv:
    """Continuous-output regression cast as a discrete bin classifier.

    Observation: x ~ N(0, I_d) in R^d, concatenated with the same
    HISTORY_DIM=6 history features used by the real envs (so obs_dim is
    identical to bsd_rank_env at d=20: 20 + 6 = 26).

    Hidden truth: y = w . x + b + epsilon, with w, b drawn deterministically
    from ``corpus_seed``, epsilon ~ N(0, sigma^2).

    Bins: discretize the y range across K=21 bins. Two binning modes:
      - "balanced": uniform bins from -y_range to +y_range (V1, V3).
        Quantile binning would be exact-uniform, but at a finite seed
        sample it suffices to use the analytic 5/95 percentile of the
        underlying distribution and assert near-uniform coverage.
      - "skewed":  Gaussian binning -- bin edges at percentiles 0,
        2.5, 5, ..., 97.5, 100 of the *standard normal*. This makes
        the empirical y distribution concentrate ~50% of the mass in
        the central 3 bins (the modal regime that real domains exhibit).

    Reward: REWARD_HIT if predicted_bin == true_bin else REWARD_MISS.
    Episode length: 1 (contextual bandit, identical to real envs).
    """

    def __init__(
        self,
        d: int = DEFAULT_D,
        n_bins: int = N_BINS,
        sigma: float = 0.1,
        binning: str = "balanced",
        corpus_seed: int = 0,
        seed: Optional[int] = None,
    ):
        if binning not in ("balanced", "skewed"):
            raise ValueError(
                f"binning must be 'balanced' or 'skewed'; got {binning!r}"
            )
        if d <= 0:
            raise ValueError(f"d must be positive; got {d}")
        if n_bins < 2:
            raise ValueError(f"n_bins must be >= 2; got {n_bins}")
        if sigma < 0:
            raise ValueError(f"sigma must be >= 0; got {sigma}")

        self._d = int(d)
        self._n_bins = int(n_bins)
        self._sigma = float(sigma)
        self._binning = binning

        # Deterministic hidden ground truth.
        truth_rng = np.random.default_rng(corpus_seed)
        # Unit-norm w so y has variance exactly 1 (plus noise) when x ~ N(0, I).
        w_raw = truth_rng.standard_normal(self._d)
        self._w = w_raw / np.linalg.norm(w_raw)
        self._b = float(truth_rng.standard_normal())

        # Bin edges. y = w.x + b has marginal distribution N(b, 1) when x
        # is unit-Gaussian and ||w|| = 1. Add a touch of noise variance.
        # We construct edges in normalized form then shift by b.
        if binning == "balanced":
            # Uniform bins covering 5th to 95th percentile of N(0, 1+sigma^2).
            from math import sqrt as _sqrt
            scale = _sqrt(1.0 + self._sigma * self._sigma)
            # Use an explicit symmetric range -2.5*scale to +2.5*scale.
            lo = -2.5 * scale
            hi = +2.5 * scale
            edges = np.linspace(lo, hi, self._n_bins + 1)
        else:
            # SKEWED: tight uniform bins inside a narrow window, with
            # the outermost two bins absorbing the (heavy-tailed) y
            # distribution's wings. We deliberately set the inner
            # window to +/- 0.6 standard deviations so y ~ N(0, 1+sigma^2)
            # dumps ~50%+ of its mass into the outermost two bins and
            # the central few. This reproduces the empirical class-prior
            # imbalance the six real domains exhibit (rank-0 curves =
            # ~50% of the BSD corpus, central trace bin = modal class
            # for high-weight modular forms, etc.).
            from math import sqrt as _sqrt
            scale = _sqrt(1.0 + self._sigma * self._sigma)
            inner_lo = -0.6 * scale
            inner_hi = +0.6 * scale
            edges_inner = np.linspace(inner_lo, inner_hi, self._n_bins - 1)
            edges = np.concatenate([[-1e9], edges_inner, [1e9]])

        # Shift bin edges to absorb the bias b.
        self._edges = edges + self._b
        # Sanity: edges strictly increasing.
        if not np.all(np.diff(self._edges) > 0):
            raise RuntimeError(
                f"bin edges not strictly increasing: {self._edges.tolist()}"
            )

        self._seed = seed
        self._rng = np.random.default_rng(seed)
        self._state = _EpisodeState()
        self._current_x: Optional[np.ndarray] = None
        self._current_y: Optional[float] = None
        self._current_true_bin: Optional[int] = None
        self._step_called = False

    # --- introspection ---

    def n_bins(self) -> int:
        return self._n_bins

    def n_ap(self) -> int:
        # Compatibility with the real env trainers' shape calls.
        return self._d

    def obs_dim(self) -> int:
        return self._d + HISTORY_DIM

    def truth(self) -> Tuple[np.ndarray, float]:
        return self._w.copy(), self._b

    def edges(self) -> np.ndarray:
        return self._edges.copy()

    def running_accuracy(self) -> float:
        n = self._state.n_episodes_seen
        if n <= 0:
            return 0.0
        return float(self._state.n_correct) / float(n)

    # --- lifecycle ---

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self._rng = np.random.default_rng(int(seed))
        self._step_called = False

        x = self._rng.standard_normal(self._d)
        eps = float(self._rng.standard_normal()) * self._sigma
        y = float(self._w @ x) + self._b + eps
        true_bin = int(np.clip(
            np.searchsorted(self._edges, y, side="right") - 1,
            0, self._n_bins - 1,
        ))
        self._current_x = x
        self._current_y = y
        self._current_true_bin = true_bin

        info = {
            "true_bin": true_bin,
            "y": y,
            "n_actions": self._n_bins,
        }
        return self._obs(), info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._current_x is None:
            raise RuntimeError("env.step() called before env.reset()")
        if self._step_called:
            raise RuntimeError(
                "step() called twice in one episode (length 1; reset first)"
            )
        a = int(action)
        if a < 0 or a >= self._n_bins:
            raise ValueError(f"action {a} out of range [0, {self._n_bins})")

        true_bin = int(self._current_true_bin)
        hit = (a == true_bin)
        reward = REWARD_HIT if hit else REWARD_MISS

        self._state.n_episodes_seen += 1
        if hit:
            self._state.n_correct += 1
        self._state.last_reward = float(reward)
        self._state.last_pred_bin = a
        self._state.last_true_bin = true_bin

        self._step_called = True
        info = {
            "true_bin": true_bin,
            "predicted_bin": a,
            "hit": bool(hit),
            "running_accuracy": self.running_accuracy(),
            "n_episodes_seen": self._state.n_episodes_seen,
            "y": float(self._current_y) if self._current_y is not None else 0.0,
        }
        return self._obs(), float(reward), True, False, info

    def close(self) -> None:
        self._current_x = None
        self._current_y = None
        self._current_true_bin = None

    # --- observation ---

    def _obs(self) -> np.ndarray:
        if self._current_x is None:
            return np.zeros(self.obs_dim(), dtype=np.float64)
        history = np.array([
            0.0,                              # log_n placeholder (matches BSD)
            self.running_accuracy(),
            self._state.last_reward / REWARD_HIT,
            float(self._state.n_episodes_seen),
            float(self._state.last_pred_bin),
            float(self._state.last_true_bin),
        ], dtype=np.float64)
        return np.concatenate([self._current_x, history])


# ---------------------------------------------------------------------------
# Inverse normal CDF (Beasley-Springer-Moro) -- avoids scipy dependency.
# ---------------------------------------------------------------------------


def _inv_normal_cdf(p: float) -> float:
    """Inverse standard-normal CDF; pure-NumPy / Python implementation.

    Standard Beasley-Springer-Moro approximation; max abs error ~1e-9
    over (1e-12, 1 - 1e-12), which is plenty for bin-edge construction.
    """
    if p <= 0.0 or p >= 1.0:
        raise ValueError(f"p must be in (0, 1); got {p}")
    a = [-3.969683028665376e+01,  2.209460984245205e+02,
         -2.759285104469687e+02,  1.383577518672690e+02,
         -3.066479806614716e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02,
         -1.556989798598866e+02,  6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00,  2.938163982698783e+00]
    d_coef = [7.784695709041462e-03, 3.224671290700398e-01,
              2.445134137142996e+00, 3.754408661907416e+00]
    p_low = 0.02425
    p_high = 1 - p_low
    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d_coef[0]*q + d_coef[1])*q + d_coef[2])*q + d_coef[3])*q + 1)
    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q / \
               (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)
    q = math.sqrt(-2.0 * math.log(1 - p))
    return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
           ((((d_coef[0]*q + d_coef[1])*q + d_coef[2])*q + d_coef[3])*q + 1)


# ---------------------------------------------------------------------------
# Trainers (byte-for-byte ports of modular_form_env.train_*)
# ---------------------------------------------------------------------------


def train_random(
    env: SyntheticRegressionEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random bin prediction baseline (port of train_random)."""
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(env.n_bins(), dtype=np.int64)
    near_one = 0
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, env.n_bins()))
        pred_counts[a] += 1
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if abs(int(info.get("predicted_bin", -10)) -
               int(info.get("true_bin", -100))) <= 1:
            near_one += 1
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "resolution_score": float(near_one / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "random",
        "pred_counts": pred_counts.tolist(),
    }


def train_reinforce(
    env: SyntheticRegressionEnv,
    n_episodes: int,
    *,
    lr: float = 0.02,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """REINFORCE-linear (port of modular_form_env.train_reinforce)."""
    rng = np.random.default_rng(seed)
    obs_dim = env.obs_dim()
    n_actions = env.n_bins()
    W = np.zeros((n_actions, obs_dim), dtype=np.float64)
    b = np.zeros(n_actions, dtype=np.float64)
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
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if abs(int(info.get("predicted_bin", -10)) -
               int(info.get("true_bin", -100))) <= 1:
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
    lr: float = 0.005,
    hidden: int = 32,
    clip_eps: float = 0.2,
    n_epochs: int = 4,
    batch_size: int = 64,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """PPO-MLP (port of modular_form_env.train_ppo)."""
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
    reward_scale = 1.0 / REWARD_HIT

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        probs, value, _h, _ = _forward(obs)
        a = int(rng.choice(n_actions, p=probs))
        pred_counts[a] += 1
        logp_old = float(np.log(probs[a] + 1e-12))
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if abs(int(info.get("predicted_bin", -10)) -
               int(info.get("true_bin", -100))) <= 1:
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
        "pred_counts": pred_counts.tolist(),
    }


# ---------------------------------------------------------------------------
# Test-set evaluation (held-out prediction-distribution probe)
# ---------------------------------------------------------------------------


def evaluate_random_agent_test(
    env_kwargs: Dict[str, Any],
    n_test: int = 200,
    eval_seed: int = 7,
) -> Dict[str, Any]:
    """Held-out evaluation of the random baseline.

    Used by the comparison driver only as a sanity reference; the policy
    parameters of REINFORCE / PPO are *not* used for held-out eval since
    those trainers don't expose a ``predict()`` method in the real envs
    either. We instead measure prediction distribution from the *training*
    rollouts -- the modal-collapse signature is visible in the
    ``pred_counts`` field already.

    Returns a dict with keys ``hit_rate``, ``per_bin``, ``n_test``.
    """
    env = SyntheticRegressionEnv(**env_kwargs, seed=eval_seed)
    n_correct = 0
    rng = np.random.default_rng(eval_seed)
    per_true = np.zeros(env.n_bins(), dtype=np.int64)
    for _ in range(n_test):
        obs, info = env.reset()
        per_true[info["true_bin"]] += 1
        a = int(rng.integers(0, env.n_bins()))
        _, r, _, _, info = env.step(a)
        if info.get("hit"):
            n_correct += 1
    env.close()
    return {
        "hit_rate": float(n_correct / max(1, n_test)),
        "true_bin_distribution": per_true.tolist(),
        "n_test": int(n_test),
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
    d: int = DEFAULT_D,
    n_bins: int = N_BINS,
    corpus_seed: int = 0,
) -> Dict[str, Any]:
    """Run all 4 variants x 3 algorithms x ``len(seeds)`` seeds.

    Returns a nested dict::

        {
          "V1_balanced": {
             "random":    {"acc_mean": ..., "acc_std": ..., "pred_counts_mean": [...]},
             "reinforce": {...},
             "ppo":       {...},
          },
          ...
          "verdict": "A" | "B" | "C",
          "n_episodes": ...,
          "n_seeds": ...,
        }

    Per-bin "pred_counts_mean" is the seed-averaged prediction histogram
    (length n_bins). The modal-collapse signature is high mass on 1-2
    bins and near-zero on the rest.
    """
    out: Dict[str, Any] = {
        "n_episodes": n_episodes,
        "n_seeds": len(seeds),
        "d": d,
        "n_bins": n_bins,
        "variants": {},
    }
    trainers = [("random", train_random),
                ("reinforce", train_reinforce),
                ("ppo", train_ppo)]
    for v_name, v_kwargs in VARIANTS.items():
        v_results: Dict[str, Any] = {}
        for agent_name, fn in trainers:
            accs: List[float] = []
            ress: List[float] = []
            pred_count_seeds: List[np.ndarray] = []
            for s in seeds:
                env = SyntheticRegressionEnv(
                    d=d, n_bins=n_bins,
                    corpus_seed=corpus_seed,
                    seed=s,
                    **v_kwargs,
                )
                if agent_name == "random":
                    res = train_random(env, n_episodes=n_episodes, seed=s)
                elif agent_name == "reinforce":
                    res = train_reinforce(env, n_episodes=n_episodes, seed=s)
                else:
                    res = train_ppo(env, n_episodes=n_episodes, seed=s)
                accs.append(res["accuracy"])
                ress.append(res["resolution_score"])
                pred_count_seeds.append(np.asarray(res["pred_counts"]))
                env.close()
            pc_mean = np.mean(np.stack(pred_count_seeds, axis=0), axis=0)
            v_results[agent_name] = {
                "acc_mean":   float(np.mean(accs)),
                "acc_std":    float(np.std(accs)),
                "res_mean":   float(np.mean(ress)),
                "res_std":    float(np.std(ress)),
                "pred_counts_mean": pc_mean.tolist(),
                # How many bins capture >=1% of the mass? <=2 means
                # textbook modal collapse.
                "active_bins": int(
                    np.sum(pc_mean / pc_mean.sum() >= 0.01)
                ),
            }
        out["variants"][v_name] = v_results

    out["verdict"] = _classify_verdict(out)
    return out


def _classify_verdict(report: Dict[str, Any]) -> str:
    """Triangulate Case A/B/C from the four-variant results.

    The decisive variant is V3_low_noise (balanced binning + sigma=0.01),
    where the linear map y = w.x + b is essentially exact and a
    least-squares fit recovers true_bin >60% of the time. If the agents
    *cannot* learn this, the substrate is broken regardless of what the
    real domains do.

    - Case A (substrate broken): in V3, NEITHER REINFORCE nor PPO
      achieves accuracy >= 2x random (i.e. neither learns the linear
      map). Failure mode (uniform vs collapsed) doesn't matter; the
      point is the agent can't extract structure from a trivially
      learnable env.
    - Case B (real envs were the cause): in V3, both REINFORCE and PPO
      beat random by >= 4x AND use >= 8 active bins.
    - Case C (intermediate): one trainer works, the other doesn't, or
      partial recovery (>= 2x random but < 4x and/or insufficient
      bin coverage).
    """
    v3 = report["variants"].get("V3_low_noise", {})
    if not v3:
        return "indeterminate"
    rand_acc = v3.get("random", {}).get("acc_mean", 0.0)
    re_acc = v3.get("reinforce", {}).get("acc_mean", 0.0)
    ppo_acc = v3.get("ppo", {}).get("acc_mean", 0.0)
    re_active = v3.get("reinforce", {}).get("active_bins", 0)
    ppo_active = v3.get("ppo", {}).get("active_bins", 0)

    re_learned = (re_acc >= 4.0 * rand_acc and re_active >= 8)
    ppo_learned = (ppo_acc >= 4.0 * rand_acc and ppo_active >= 8)
    re_failed = re_acc < 2.0 * rand_acc
    ppo_failed = ppo_acc < 2.0 * rand_acc

    if re_failed and ppo_failed:
        return "A"
    if re_learned and ppo_learned:
        return "B"
    return "C"


__all__ = [
    "N_BINS", "REWARD_HIT", "REWARD_MISS", "HISTORY_DIM", "DEFAULT_D",
    "SyntheticRegressionEnv",
    "train_random", "train_reinforce", "train_ppo",
    "run_diagnostic", "VARIANTS",
    "evaluate_random_agent_test",
]
