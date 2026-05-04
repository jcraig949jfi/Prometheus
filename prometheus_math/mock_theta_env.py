"""prometheus_math.mock_theta_env -- Gymnasium-compatible mock theta env.

Cross-domain test #4 for the Prometheus discovery substrate. After BSD
(elliptic-curve rank), modular forms (Hecke a_p), and the surrounding
arithmetic-geometry test bed, this env probes a fundamentally
*different* family of objects: harmonic Maass forms via their mock
theta function holomorphic parts.

Per-episode schema
------------------
1. ``reset()`` samples a mock theta function from the configured split
   (train or test) and a "context length" ``k`` uniformly in
   ``[k_min, n_coeffs - 1]``. The agent will see ``a_0..a_{k-1}`` and
   must predict ``a_k``.
2. The agent picks an action ``a in {0, ..., N_BINS - 1}``: a
   discretized prediction of the integer coefficient ``a_k``. Bins
   tile a symmetric range ``[-VALUE_RANGE, VALUE_RANGE]`` uniformly,
   so each bin spans ``2 * VALUE_RANGE / N_BINS`` consecutive integer
   values. Coefficients outside that range are clipped into the
   extreme bins.
3. ``step(a)`` BIND/EVAL-s through the sigma kernel (mirroring the
   substrate-growth invariant of BSDRankEnv and ModularFormEnv: 1
   binding + 1 evaluation row per step), de-quantizes the action to
   an integer prediction, compares to the true coefficient, and pays
   ``REWARD_HIT`` iff the prediction lands in the same bin.

Why bin a wide integer range?
-----------------------------
Mock theta coefficients of length-30 prefixes span a much wider range
than at first sight: the third-order f(q) hits 89 at n=29; the
seventh-order F_3 reaches 14; the sixth-order rho exceeds 970 at
n=29; the universal partition-counting variants A(q) and B(q) blow
past 2000. Restricting to ``|a_k| <= 15`` would clip out a meaningful
share of the corpus. Following the spec, we use 31 bins on
``[-100, 100]``, giving bin width ~6.45 integers; that covers the bulk
of the support while remaining a 31-class classification problem.
Random accuracy is exactly ``1 / N_BINS = 1/31 ~ 3.23%``; a "predict
the modal bin" baseline (the bin containing 0, where most low-index
coefficients land) beats that on the empirical distribution.

Action / reward parameters
--------------------------
- ``N_BINS = 31`` and ``VALUE_RANGE = 100`` -- bin centers are
  approximately ``-100, -93.5, -87.1, ..., 0, ..., +87.1, +93.5,
  +100``.
- Coefficients ``v`` with ``|v| > 100`` clip to the extreme bin (0 or
  ``N_BINS - 1``).
- Reward: ``REWARD_HIT`` (100.0) on correct bin, 0 otherwise.

Skip-with-message contract
--------------------------
The corpus is fully embedded so ``MockThetaEnv.__init__`` never raises
because of missing data; it does raise ``ValueError`` for malformed
inputs. Tests that want a skip path can call
``_mock_theta_corpus.is_available()`` and skip on ``(False, _)`` (which
shouldn't happen in practice).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel

from . import _mock_theta_corpus
from ._mock_theta_corpus import MockThetaEntry


# ---------------------------------------------------------------------------
# Action / reward parameters
# ---------------------------------------------------------------------------


# 31 bins tiling [-VALUE_RANGE, VALUE_RANGE]. Random predictor
# accuracy is 1/N_BINS ~ 3.23%; the modal-bin (containing 0) baseline
# beats that on the empirical distribution.
N_BINS: int = 31

# Half-width of the binned interval. ``VALUE_RANGE = 100`` gives bin
# width ``2 * 100 / 31 ~ 6.45`` integers per bin.
VALUE_RANGE: float = 100.0

# Reward magnitudes: same +100 / 0 convention as the sibling envs.
REWARD_HIT: float = 100.0
REWARD_MISS: float = 0.0

# Default minimum context length in coefficients -- with fewer than 5
# revealed the agent has too little signal.
DEFAULT_CONTEXT_MIN: int = 5

# Default coefficient sequence length on the corpus. The embedded raw
# data has length-30 prefixes.
DEFAULT_N_COEFFS: int = 30


# ---------------------------------------------------------------------------
# Quantization helpers
# ---------------------------------------------------------------------------


def integer_bin_for(
    value: int,
    n_bins: int = N_BINS,
    value_range: float = VALUE_RANGE,
) -> int:
    """Quantize ``value`` into a bin index in ``[0, n_bins)``.

    Bins uniformly tile ``[-value_range, +value_range]``: bin ``i``
    covers values in ``[-VR + i * 2 VR / n_bins, -VR + (i+1) * 2 VR /
    n_bins)``. For ``n_bins = 31`` and ``value_range = 100``, bin width
    is ``200 / 31 ~ 6.45`` and the centre bin (15) covers
    ``[-3.23, +3.23)`` -- which contains 0, +-1, +-2, +-3.

    Out-of-range values clip to the extremes (bin 0 or bin
    ``n_bins-1``).
    """
    if n_bins <= 0:
        raise ValueError(f"n_bins must be > 0; got {n_bins}")
    if value_range <= 0:
        raise ValueError(f"value_range must be > 0; got {value_range}")
    v = float(value)
    # Clip explicitly so the bin formula is robust.
    if v <= -value_range:
        return 0
    if v >= value_range:
        return n_bins - 1
    width = (2.0 * value_range) / n_bins
    idx = int(math.floor((v + value_range) / width))
    if idx < 0:
        idx = 0
    if idx >= n_bins:
        idx = n_bins - 1
    return idx


def bin_to_integer(
    idx: int,
    n_bins: int = N_BINS,
    value_range: float = VALUE_RANGE,
) -> int:
    """Map bin index back to its integer-rounded centre value."""
    if idx < 0 or idx >= n_bins:
        raise ValueError(f"bin idx {idx} out of range [0, {n_bins})")
    width = (2.0 * value_range) / n_bins
    centre = -value_range + (idx + 0.5) * width
    return int(round(centre))


# ---------------------------------------------------------------------------
# Substrate hook (identity binding, mirrors sibling envs)
# ---------------------------------------------------------------------------


def _identity_predictor(bin_idx: int) -> int:
    return int(bin_idx)


_IDENTITY_REF = "prometheus_math.mock_theta_env:_identity_predictor"


# ---------------------------------------------------------------------------
# Spec stubs (gymnasium-optional)
# ---------------------------------------------------------------------------


class _BoxStub:
    def __init__(self, shape: Tuple[int, ...]):
        self.shape = tuple(shape)
        self.dtype = np.float64

    def contains(self, x) -> bool:  # noqa: D401
        return isinstance(x, np.ndarray) and x.shape == self.shape


class _DiscreteStub:
    def __init__(self, n: int):
        self.n = int(n)

    def sample(self) -> int:
        return random.randrange(self.n)

    def contains(self, x) -> bool:
        return isinstance(x, int) and 0 <= x < self.n


# ---------------------------------------------------------------------------
# Observation layout
# ---------------------------------------------------------------------------


# Observation features:
#   - n_coeffs prior coefficient values for a_0..a_{n_coeffs-1};
#     positions >= context_k masked to 0.
#   - n_coeffs mask values (1.0 if revealed, 0.0 otherwise).
#   - level (1)
#   - weight (1)
#   - order (1)
#   - shadow_class (1)
#   - target index k (1)
#   - history features: running accuracy, last reward, last predicted
#     bin, last true bin, n_episodes_seen (5)
HISTORY_DIM = 10


def _obs_dim(n_coeffs: int) -> int:
    return 2 * int(n_coeffs) + HISTORY_DIM


# ---------------------------------------------------------------------------
# Episode state
# ---------------------------------------------------------------------------


@dataclass
class _EpisodeState:
    n_episodes_seen: int = 0
    n_correct: int = 0
    last_reward: float = 0.0
    last_pred_bin: int = -1
    last_true_bin: int = -1


# ---------------------------------------------------------------------------
# Env
# ---------------------------------------------------------------------------


class MockThetaEnv:
    """Gymnasium-compatible env: predict a_k of a mock theta function.

    Parameters
    ----------
    corpus : sequence[MockThetaEntry], optional
        Pre-loaded corpus. If None, the env calls
        ``_mock_theta_corpus.load_mock_theta_corpus(...)``.
    split : {"all", "train", "test"}
    train_frac, split_seed : float, int
    n_coeffs, seed, kernel_db_path :
        Forwarded to the corpus loader (when ``corpus`` is None) and the
        sigma kernel.
    n_bins : int
        Number of action bins (must be > 1; 31 covers integer
        coefficients in [-15, 15]).
    context_min : int
        Minimum number of prior coefficients revealed to the agent.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[MockThetaEntry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        n_coeffs: int = DEFAULT_N_COEFFS,
        seed: Optional[int] = None,
        kernel_db_path: str = ":memory:",
        n_bins: int = N_BINS,
        value_range: float = VALUE_RANGE,
        context_min: int = DEFAULT_CONTEXT_MIN,
    ):
        if split not in ("all", "train", "test"):
            raise ValueError(
                f"split must be 'all', 'train', or 'test'; got {split!r}"
            )
        if n_bins <= 1:
            raise ValueError(f"n_bins must be > 1; got {n_bins}")
        if value_range <= 0:
            raise ValueError(f"value_range must be > 0; got {value_range}")
        if context_min < 1:
            raise ValueError(f"context_min must be >= 1; got {context_min}")

        if corpus is None:
            corpus = _mock_theta_corpus.load_mock_theta_corpus(
                n_coeffs=n_coeffs,
            )
        corpus = list(corpus)
        if not corpus:
            raise ValueError("MockThetaEnv corpus is empty")

        # Verify coefficient length consistency.
        coeff_len = len(corpus[0].coefficients)
        for e in corpus:
            if len(e.coefficients) != coeff_len:
                raise ValueError(
                    f"corpus has inconsistent coefficient lengths: "
                    f"{coeff_len} vs {len(e.coefficients)} at {e.name}"
                )
        if coeff_len <= context_min:
            raise ValueError(
                f"coefficient length {coeff_len} <= context_min "
                f"{context_min}; need at least one coefficient to predict"
            )
        self._n_coeffs = int(coeff_len)

        if split == "all":
            self._split_corpus: List[MockThetaEntry] = list(corpus)
        else:
            train, test = _mock_theta_corpus.split_train_test(
                corpus, train_frac=train_frac, seed=split_seed,
            )
            self._split_corpus = list(train if split == "train" else test)
        if not self._split_corpus:
            raise ValueError(f"split {split!r} is empty after partitioning")

        self.split = split
        self._kernel_db_path = kernel_db_path
        self._n_bins = int(n_bins)
        self._value_range = float(value_range)
        self._context_min = int(context_min)
        self._seed = seed
        self._rng = random.Random(seed)
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._state = _EpisodeState()
        self._current: Optional[MockThetaEntry] = None
        self._context_k: int = self._context_min
        self._step_called = False

        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(_obs_dim(self._n_coeffs),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(self._n_bins)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((_obs_dim(self._n_coeffs),))
            self.action_space = _DiscreteStub(self._n_bins)
            self._gym_spaces = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self._rng = random.Random(int(seed))

        # Fresh kernel each episode (substrate-growth invariant).
        self._kernel = SigmaKernel(self._kernel_db_path)
        self._ext = BindEvalExtension(self._kernel)
        self._step_called = False

        # Sample function + context length.
        idx = self._rng.randrange(len(self._split_corpus))
        self._current = self._split_corpus[idx]
        max_k = self._n_coeffs - 1
        if self._context_min > max_k:
            self._context_k = max_k
        else:
            self._context_k = self._rng.randint(self._context_min, max_k)

        true_a = int(self._current.coefficients[self._context_k])
        true_bin = integer_bin_for(true_a, self._n_bins, self._value_range)

        info = {
            "n_actions": self._n_bins,
            "name": self._current.name,
            "order": self._current.order,
            "level": self._current.level,
            "weight": self._current.weight,
            "shadow_class": self._current.shadow_class,
            "target_index": self._context_k,
            "true_coefficient": true_a,
            "true_bin": true_bin,
            "context_k": self._context_k,
            "split": self.split,
        }
        return self._obs(), info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._ext is None or self._current is None:
            raise RuntimeError("env.step() called before env.reset()")
        if self._step_called:
            raise RuntimeError(
                "MockThetaEnv: step() called twice in one episode "
                "(episode length is 1; call reset() before next step)"
            )
        a = int(action)
        if a < 0 or a >= self._n_bins:
            raise ValueError(
                f"action {a} out of range [0, {self._n_bins})"
            )

        # Compute ground truth.
        true_a = int(self._current.coefficients[self._context_k])
        true_bin = integer_bin_for(true_a, self._n_bins, self._value_range)

        # BIND/EVAL through substrate (substrate-growth invariant).
        cap_b = self._kernel.mint_capability("BindCap")
        binding = self._ext.BIND(
            callable_ref=_IDENTITY_REF,
            cost_model=CostModel(),
            postconditions=[],
            authority_refs=[
                f"mocktheta:{self._current.name}",
                f"index:{self._context_k}",
            ],
            cap=cap_b,
        )
        cap_e = self._kernel.mint_capability("EvalCap")
        ev = self._ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[a],
            kwargs={},
            cap=cap_e,
            eval_version=1,
        )
        try:
            output_bin = int(ev.output_repr)
        except (TypeError, ValueError):
            output_bin = a

        hit = (output_bin == true_bin)
        reward = REWARD_HIT if hit else REWARD_MISS

        self._state.n_episodes_seen += 1
        if hit:
            self._state.n_correct += 1
        self._state.last_reward = float(reward)
        self._state.last_pred_bin = a
        self._state.last_true_bin = true_bin

        terminated = True
        truncated = False
        self._step_called = True

        pred_value = bin_to_integer(a, self._n_bins, self._value_range)

        info = {
            "name": self._current.name,
            "order": self._current.order,
            "level": self._current.level,
            "weight": self._current.weight,
            "shadow_class": self._current.shadow_class,
            "target_index": self._context_k,
            "true_coefficient": true_a,
            "true_bin": true_bin,
            "predicted_bin": a,
            "predicted_value": pred_value,
            "context_k": self._context_k,
            "hit": bool(hit),
            "running_accuracy": self.running_accuracy(),
            "n_episodes_seen": self._state.n_episodes_seen,
            "binding_name": binding.symbol.name,
            "binding_version": binding.symbol.version,
            "eval_success": ev.success,
            "split": self.split,
        }
        return self._obs(), float(reward), terminated, truncated, info

    def close(self) -> None:
        if self._kernel is not None:
            try:
                self._kernel.conn.close()
            except Exception:  # pragma: no cover
                pass
        self._kernel = None
        self._ext = None

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        if self._current is None:
            return np.zeros(_obs_dim(self._n_coeffs), dtype=np.float64)
        # Scale coefficients by VALUE_RANGE so they sit in roughly
        # [-1, 1]; large unscaled values destabilize the PPO MLP.
        coeffs = np.zeros(self._n_coeffs, dtype=np.float64)
        mask = np.zeros(self._n_coeffs, dtype=np.float64)
        for i in range(self._context_k):
            coeffs[i] = float(self._current.coefficients[i]) / max(
                self._value_range, 1.0
            )
            mask[i] = 1.0
        # Discrete features rescaled to small floats for the same reason.
        history = np.array([
            math.log10(max(1, self._current.level)),
            float(self._current.weight),
            float(self._current.order) / 10.0,
            float(self._current.shadow_class) / 10.0,
            float(self._context_k) / max(self._n_coeffs, 1),
            self.running_accuracy(),
            self._state.last_reward / max(REWARD_HIT, 1.0),
            float(self._state.last_pred_bin) / max(self._n_bins, 1),
            float(self._state.last_true_bin) / max(self._n_bins, 1),
            math.log10(1.0 + float(self._state.n_episodes_seen)),
        ], dtype=np.float64)
        return np.concatenate([coeffs, mask, history])

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def running_accuracy(self) -> float:
        n = self._state.n_episodes_seen
        if n <= 0:
            return 0.0
        return float(self._state.n_correct) / float(n)

    def kernel(self) -> SigmaKernel:
        if self._kernel is None:
            raise RuntimeError("env not reset yet")
        return self._kernel

    def corpus_size(self) -> int:
        return len(self._split_corpus)

    def n_coeffs(self) -> int:
        return self._n_coeffs

    def n_bins(self) -> int:
        return self._n_bins

    def value_range(self) -> float:
        return self._value_range


# ---------------------------------------------------------------------------
# Optional gymnasium registration
# ---------------------------------------------------------------------------


def register_with_gymnasium() -> Optional[str]:
    try:
        import gymnasium as gym
    except ImportError:
        return None
    env_id = "prometheus/MockTheta-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.mock_theta_env:MockThetaEnv",
        )
    except Exception:
        pass
    return env_id


# ---------------------------------------------------------------------------
# Lightweight trainers (random, REINFORCE-linear, PPO-MLP)
# ---------------------------------------------------------------------------


def train_random(
    env: MockThetaEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random bin prediction baseline."""
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(env.n_bins(), dtype=np.int64)
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, env.n_bins()))
        pred_counts[a] += 1
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "random",
        "pred_counts": pred_counts.tolist(),
    }


def train_reinforce(
    env: MockThetaEnv,
    n_episodes: int,
    *,
    lr: float = 0.02,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """Obs-conditioned REINFORCE (linear policy) for MockThetaEnv."""
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.n_coeffs())
    n_actions = env.n_bins()
    W = np.zeros((n_actions, obs_dim), dtype=np.float64)
    b = np.zeros(n_actions, dtype=np.float64)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    baseline = 0.0
    pred_counts = np.zeros(n_actions, dtype=np.int64)

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
        "n_episodes": int(n_episodes),
        "agent": "reinforce",
        "policy_W_final": W,
        "policy_b_final": b,
        "pred_counts": pred_counts.tolist(),
    }


def _softmax(x: np.ndarray) -> np.ndarray:
    z = x - x.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def train_ppo(
    env: MockThetaEnv,
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
    """Tiny PPO-style trainer with a 2-layer MLP policy + value head."""
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.n_coeffs())
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

    buf_obs: List[np.ndarray] = []
    buf_act: List[int] = []
    buf_logp: List[float] = []
    buf_adv: List[float] = []
    buf_ret: List[float] = []
    reward_scale = 1.0 / REWARD_HIT

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        probs, value, _h, _ = _forward(obs)
        # Defensive: if the forward pass NaNs out (e.g. weights
        # diverged), fall back to uniform so the trainer can recover.
        if not np.all(np.isfinite(probs)) or probs.sum() <= 0:
            probs = np.full(n_actions, 1.0 / n_actions)
            value = 0.0
        a = int(rng.choice(n_actions, p=probs))
        pred_counts[a] += 1
        logp_old = float(np.log(probs[a] + 1e-12))
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1

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
                clipped = np.clip(ratio, 1.0 - clip_eps, 1.0 + clip_eps)
                # surr = np.minimum(ratio * adv_arr, clipped * adv_arr)
                _ = np.minimum(ratio * adv_arr, clipped * adv_arr)

                v_err = values - ret_arr
                grad_h_v = v_err[:, None] @ Wv

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

                grad_Wv = (v_err[:, None] * h_act).sum(axis=0, keepdims=True)
                grad_bv = np.array([v_err.sum()])

                grad_h_total = grad_h_pol + grad_h_v
                relu_mask = (h_pre > 0).astype(np.float64)
                grad_pre = grad_h_total * relu_mask
                grad_W1 = grad_pre.T @ obs_arr
                grad_b1 = grad_pre.sum(axis=0)

                bs = float(obs_arr.shape[0])

                # Gradient clipping (max-norm 1.0 per tensor) to
                # prevent NaN explosion on the wide-bin MockThetaEnv.
                def _clip_grad(g):
                    g = g / bs
                    if not np.all(np.isfinite(g)):
                        g = np.nan_to_num(
                            g, nan=0.0, posinf=0.0, neginf=0.0
                        )
                    n = float(np.linalg.norm(g))
                    if n > 1.0:
                        g = g / n
                    return g

                Wp -= lr * _clip_grad(grad_Wp)
                bp -= lr * _clip_grad(grad_bp)
                Wv -= lr * _clip_grad(grad_Wv)
                bv -= lr * _clip_grad(grad_bv)
                W1 -= lr * _clip_grad(grad_W1)
                b1 -= lr * _clip_grad(grad_b1)

            buf_obs.clear()
            buf_act.clear()
            buf_logp.clear()
            buf_adv.clear()
            buf_ret.clear()

    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "ppo",
        "policy_W1_final": W1,
        "policy_b1_final": b1,
        "policy_Wp_final": Wp,
        "policy_bp_final": bp,
        "value_Wv_final": Wv,
        "value_bv_final": bv,
        "pred_counts": pred_counts.tolist(),
    }


__all__ = [
    "MockThetaEnv",
    "N_BINS",
    "VALUE_RANGE",
    "REWARD_HIT",
    "REWARD_MISS",
    "DEFAULT_CONTEXT_MIN",
    "DEFAULT_N_COEFFS",
    "integer_bin_for",
    "bin_to_integer",
    "register_with_gymnasium",
    "train_random",
    "train_reinforce",
    "train_ppo",
]
