"""prometheus_math.oeis_sleeping_env -- Gymnasium env for next-term
prediction on OEIS Sleeping Beauty sequences.

Cross-domain test #3 for the Prometheus discovery substrate. Where the
BSD env (rank prediction; +1.37x lift) and the modular-form env
(a_p prediction; +1.58x lift) sit on labelled, well-tabulated number
theory, this env tests the substrate on the *underconnected tail* of
OEIS: ~68,770 sequences with rich combinatorial structure but few
cross-references to the rest of the integer-sequence world.

Per-episode schema
------------------
1. ``reset()`` samples one sequence from the configured split. We pick
   a context length ``k`` uniformly in ``[k_min, n_terms - 1]``. The
   agent will see ``a(0), ..., a(k-1)`` and must predict ``a(k)``.
2. The agent picks a discrete bin in ``[0, N_BINS)``; bins partition
   ``[1, 10^MAX_LOG10]`` in log-space (50 bins by default).
3. ``step(a)`` BIND/EVAL-s through the sigma kernel (mirrors
   BSDRankEnv / ModularFormEnv: 1 binding + 1 evaluation row per
   step), de-quantizes to a numeric prediction range, and pays out
   ``REWARD_HIT`` iff the bin contains the true ``a(k)``. Partial
   credit ``REWARD_NEAR`` is paid when the prediction is one bin off.

Action / reward parameters
--------------------------
Logarithmic binning across [1, 10^15] with 50 bins. Bin width on the
log10 axis: 15/50 = 0.30 decades = factor of ~1.995 per bin. Random
predictor accuracy is ~1/50 = 2.0%.

Skip-with-message contract
--------------------------
``OeisSleepingEnv.__init__`` raises ``ValueError`` on an empty corpus.
Tests that need a live corpus catch this with ``pytest.skip``.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel

from . import _oeis_sleeping_corpus
from ._oeis_sleeping_corpus import (
    OeisSleepingEntry,
    GROWTH_CLASSES,
    growth_class_index,
)


# ---------------------------------------------------------------------------
# Action / reward parameters
# ---------------------------------------------------------------------------


# Logarithmic binning. Bin i covers a(k) in
# ``[10^(i * MAX_LOG10 / N_BINS), 10^((i+1) * MAX_LOG10 / N_BINS))``.
# With MAX_LOG10=15 and N_BINS=50, each bin covers about a factor of
# 10^0.3 ~ 1.995 in value space.
N_BINS: int = 50
MAX_LOG10: float = 15.0


# Reward magnitudes mirror the +100 / 0 convention from BSDRankEnv +
# ModularFormEnv, with an extra near-bin partial credit channel.
REWARD_HIT: float = 100.0
REWARD_NEAR: float = 25.0   # one bin off either way
REWARD_MISS: float = 0.0


# Default minimum context length. Below 5 visible terms there is
# essentially no signal for the agent.
DEFAULT_CONTEXT_MIN: int = 5


# ---------------------------------------------------------------------------
# Quantization helpers
# ---------------------------------------------------------------------------


def value_to_bin(value: int, n_bins: int = N_BINS,
                 max_log10: float = MAX_LOG10) -> int:
    """Quantize a positive integer ``value`` into a log-spaced bin
    index in ``[0, n_bins)``.

    Values <= 0 clip to bin 0; values >= 10**max_log10 clip to the last
    bin. Bin 0 covers [1, 10^(max_log10/n_bins)).
    """
    if n_bins <= 0:
        raise ValueError(f"n_bins must be > 0; got {n_bins}")
    if max_log10 <= 0.0:
        raise ValueError(f"max_log10 must be > 0; got {max_log10}")
    if value <= 0:
        return 0
    log_v = math.log10(float(value))
    if log_v >= max_log10:
        return n_bins - 1
    if log_v < 0.0:
        return 0
    width = max_log10 / n_bins
    idx = int(math.floor(log_v / width))
    if idx >= n_bins:
        idx = n_bins - 1
    if idx < 0:
        idx = 0
    return idx


def bin_to_value_range(idx: int, n_bins: int = N_BINS,
                       max_log10: float = MAX_LOG10) -> Tuple[float, float]:
    """Return the (low, high) numeric range of bin ``idx`` (log-spaced)."""
    if idx < 0 or idx >= n_bins:
        raise ValueError(f"bin idx {idx} out of range [0, {n_bins})")
    width = max_log10 / n_bins
    lo = 10.0 ** (idx * width)
    hi = 10.0 ** ((idx + 1) * width)
    return float(lo), float(hi)


def bin_center_value(idx: int, n_bins: int = N_BINS,
                     max_log10: float = MAX_LOG10) -> float:
    """Geometric mean of the bin's range -- the "typical" value in the
    bin."""
    lo, hi = bin_to_value_range(idx, n_bins, max_log10)
    return math.sqrt(lo * hi)


# ---------------------------------------------------------------------------
# Substrate hook
# ---------------------------------------------------------------------------


def _identity_predictor(bin_idx: int) -> int:
    return int(bin_idx)


_IDENTITY_REF = "prometheus_math.oeis_sleeping_env:_identity_predictor"


# ---------------------------------------------------------------------------
# Spec stubs (used when gymnasium is missing)
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


# Observation features (per-episode, fixed dim):
#   - context_max log10(a(i)) values, primes >= context_k zeroed
#   - context_max mask (1.0 if revealed)
#   - context_max ratios r(i) = a(i+1) / a(i) (clipped, log-spaced)
#   - growth class one-hot (len(GROWTH_CLASSES))
#   - log10 of last revealed term
#   - context length k
#   - last delta (log10(a(k-1)) - log10(a(k-2)))
#   - mean log-ratio across context
#   - history features: running accuracy, last reward, last predicted
#     bin, last true bin, n_episodes_seen   (5)
DEFAULT_CONTEXT_MAX: int = 30
HISTORY_DIM: int = 5
META_DIM: int = 4   # log10_last, k, last_delta, mean_log_ratio


def _obs_dim(context_max: int) -> int:
    return 3 * context_max + len(GROWTH_CLASSES) + META_DIM + HISTORY_DIM


# ---------------------------------------------------------------------------
# Episode state
# ---------------------------------------------------------------------------


@dataclass
class _EpisodeState:
    n_episodes_seen: int = 0
    n_correct: int = 0
    n_near: int = 0
    last_reward: float = 0.0
    last_pred_bin: int = -1
    last_true_bin: int = -1


# ---------------------------------------------------------------------------
# Env
# ---------------------------------------------------------------------------


class OeisSleepingEnv:
    """Gymnasium-compatible env: predict a(k) of an OEIS sequence.

    Parameters
    ----------
    corpus : sequence[OeisSleepingEntry], optional
        Pre-loaded corpus. If None, ``load_oeis_sleeping_corpus`` is
        called.
    split : {"all", "train", "test"}
    train_frac, split_seed : float, int
    n_total, seed, kernel_db_path :
        Forwarded to corpus loader / sigma kernel.
    n_bins : int
        Number of action bins.
    max_log10 : float
        Upper bound for log-spaced binning.
    context_min : int
        Minimum revealed-term count.
    context_max : int
        Maximum revealed-term count (also the obs-vector window size).
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[OeisSleepingEntry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        n_total: int = 200,
        seed: Optional[int] = None,
        kernel_db_path: str = ":memory:",
        n_bins: int = N_BINS,
        max_log10: float = MAX_LOG10,
        context_min: int = DEFAULT_CONTEXT_MIN,
        context_max: int = DEFAULT_CONTEXT_MAX,
        corpus_seed: int = 0,
    ):
        if split not in ("all", "train", "test"):
            raise ValueError(
                f"split must be 'all', 'train', or 'test'; got {split!r}"
            )
        if n_bins <= 1:
            raise ValueError(f"n_bins must be > 1; got {n_bins}")
        if context_min < 1:
            raise ValueError(f"context_min must be >= 1; got {context_min}")
        if context_max <= context_min:
            raise ValueError(
                f"context_max ({context_max}) must exceed context_min "
                f"({context_min})"
            )
        if max_log10 <= 0.0:
            raise ValueError(f"max_log10 must be > 0; got {max_log10}")

        if corpus is None:
            corpus = _oeis_sleeping_corpus.load_oeis_sleeping_corpus(
                n_total=n_total, seed=corpus_seed,
            )
        corpus = list(corpus)
        if not corpus:
            raise ValueError("OeisSleepingEnv corpus is empty")

        # Filter to entries with at least context_min + 1 terms, so we
        # can always reveal context_min and predict the next.
        usable: List[OeisSleepingEntry] = []
        for e in corpus:
            if len(e.data) > context_min:
                usable.append(e)
        if not usable:
            raise ValueError(
                f"corpus has no entries with > {context_min} terms"
            )
        corpus = usable

        if split == "all":
            self._split_corpus: List[OeisSleepingEntry] = list(corpus)
        else:
            train, test = _oeis_sleeping_corpus.split_train_test(
                corpus, train_frac=train_frac, seed=split_seed
            )
            self._split_corpus = list(train if split == "train" else test)
        if not self._split_corpus:
            raise ValueError(f"split {split!r} is empty after partitioning")

        self.split = split
        self._kernel_db_path = kernel_db_path
        self._n_bins = int(n_bins)
        self._max_log10 = float(max_log10)
        self._context_min = int(context_min)
        self._context_max = int(context_max)
        self._seed = seed
        self._rng = random.Random(seed)
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._state = _EpisodeState()
        self._current: Optional[OeisSleepingEntry] = None
        self._context_k: int = self._context_min
        self._step_called = False

        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9,
                shape=(_obs_dim(self._context_max),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(self._n_bins)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((_obs_dim(self._context_max),))
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

        # Sample sequence + context length.
        idx = self._rng.randrange(len(self._split_corpus))
        self._current = self._split_corpus[idx]
        n = len(self._current.data)
        # Effective max context: min(n - 1, context_max).
        max_k = min(n - 1, self._context_max)
        if self._context_min > max_k:
            self._context_k = max_k
        else:
            self._context_k = self._rng.randint(self._context_min, max_k)

        true_value = int(self._current.data[self._context_k])
        true_bin = value_to_bin(true_value, self._n_bins, self._max_log10)

        info = {
            "n_actions": self._n_bins,
            "a_number": self._current.a_number,
            "name": self._current.name,
            "growth_class": self._current.growth_class,
            "is_anchor": self._current.is_anchor,
            "context_k": self._context_k,
            "true_value": true_value,
            "true_bin": true_bin,
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
                "OeisSleepingEnv: step() called twice in one episode "
                "(episode length is 1; call reset() before next step)"
            )
        a = int(action)
        if a < 0 or a >= self._n_bins:
            raise ValueError(
                f"action {a} out of range [0, {self._n_bins})"
            )

        # Compute ground truth.
        true_value = int(self._current.data[self._context_k])
        true_bin = value_to_bin(true_value, self._n_bins, self._max_log10)

        # BIND/EVAL through substrate.
        cap_b = self._kernel.mint_capability("BindCap")
        binding = self._ext.BIND(
            callable_ref=_IDENTITY_REF,
            cost_model=CostModel(),
            postconditions=[],
            authority_refs=[
                f"oeis:{self._current.a_number}",
                f"context_k:{self._context_k}",
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

        # Reward: exact bin -> HIT, neighbour -> NEAR, else MISS.
        if output_bin == true_bin:
            reward = REWARD_HIT
            hit = True
            near = False
        elif abs(output_bin - true_bin) == 1:
            reward = REWARD_NEAR
            hit = False
            near = True
        else:
            reward = REWARD_MISS
            hit = False
            near = False

        self._state.n_episodes_seen += 1
        if hit:
            self._state.n_correct += 1
        if near:
            self._state.n_near += 1
        self._state.last_reward = float(reward)
        self._state.last_pred_bin = a
        self._state.last_true_bin = true_bin

        terminated = True
        truncated = False
        self._step_called = True

        pred_lo, pred_hi = bin_to_value_range(
            a, self._n_bins, self._max_log10
        )
        info = {
            "a_number": self._current.a_number,
            "growth_class": self._current.growth_class,
            "is_anchor": self._current.is_anchor,
            "context_k": self._context_k,
            "true_value": true_value,
            "true_bin": true_bin,
            "predicted_bin": a,
            "predicted_value_low": pred_lo,
            "predicted_value_high": pred_hi,
            "hit": bool(hit),
            "near": bool(near),
            "running_accuracy": self.running_accuracy(),
            "running_near_rate": self.running_near_rate(),
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
        cmax = self._context_max
        if self._current is None:
            return np.zeros(_obs_dim(cmax), dtype=np.float64)
        log_terms = np.zeros(cmax, dtype=np.float64)
        mask = np.zeros(cmax, dtype=np.float64)
        ratios = np.zeros(cmax, dtype=np.float64)
        last_log: float = 0.0
        log_ratio_sum: float = 0.0
        n_ratios: int = 0
        prev_log: Optional[float] = None
        for i in range(min(self._context_k, cmax)):
            v = self._current.data[i]
            if v > 0:
                lv = math.log10(float(v))
            else:
                lv = 0.0
            log_terms[i] = lv
            mask[i] = 1.0
            if prev_log is not None:
                r = lv - prev_log
                # Clip ratio for numerical stability.
                r = max(-5.0, min(5.0, r))
                ratios[i] = r
                log_ratio_sum += r
                n_ratios += 1
            prev_log = lv
            last_log = lv
        last_delta = float(ratios[self._context_k - 1]) if (
            self._context_k - 1 < cmax and self._context_k >= 1
        ) else 0.0
        mean_log_ratio = log_ratio_sum / max(1, n_ratios)
        # Growth class one-hot.
        gc_oh = np.zeros(len(GROWTH_CLASSES), dtype=np.float64)
        gi = growth_class_index(self._current.growth_class)
        if 0 <= gi < len(GROWTH_CLASSES):
            gc_oh[gi] = 1.0
        meta = np.array([
            last_log,
            float(self._context_k),
            last_delta,
            mean_log_ratio,
        ], dtype=np.float64)
        history = np.array([
            self.running_accuracy(),
            self._state.last_reward / max(REWARD_HIT, 1.0),
            float(self._state.last_pred_bin),
            float(self._state.last_true_bin),
            float(self._state.n_episodes_seen),
        ], dtype=np.float64)
        return np.concatenate([log_terms, mask, ratios, gc_oh, meta, history])

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def running_accuracy(self) -> float:
        n = self._state.n_episodes_seen
        if n <= 0:
            return 0.0
        return float(self._state.n_correct) / float(n)

    def running_near_rate(self) -> float:
        n = self._state.n_episodes_seen
        if n <= 0:
            return 0.0
        return float(self._state.n_near) / float(n)

    def kernel(self) -> SigmaKernel:
        if self._kernel is None:
            raise RuntimeError("env not reset yet")
        return self._kernel

    def corpus_size(self) -> int:
        return len(self._split_corpus)

    def context_max(self) -> int:
        return self._context_max

    def n_bins(self) -> int:
        return self._n_bins


# ---------------------------------------------------------------------------
# Optional gymnasium registration
# ---------------------------------------------------------------------------


def register_with_gymnasium() -> Optional[str]:
    try:
        import gymnasium as gym
    except ImportError:
        return None
    env_id = "prometheus/OeisSleeping-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.oeis_sleeping_env:OeisSleepingEnv",
        )
    except Exception:
        pass
    return env_id


# ---------------------------------------------------------------------------
# Trainers (random, growth-baseline, REINFORCE-linear, PPO-MLP)
# ---------------------------------------------------------------------------


def train_random(
    env: OeisSleepingEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random bin prediction baseline."""
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    n_near = 0
    pred_counts = np.zeros(env.n_bins(), dtype=np.int64)
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, env.n_bins()))
        pred_counts[a] += 1
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if info.get("near"):
            n_near += 1
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "near_rate": float(n_near / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "random",
        "pred_counts": pred_counts.tolist(),
    }


def train_growth_baseline(
    env: OeisSleepingEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Heuristic baseline: extrapolate using the running growth class.

    Strategy: take the last visible term ``a(k-1)`` and the running mean
    log-ratio. Extrapolate ``log10(a(k)) ~ log10(a(k-1)) + mean_ratio``.
    Quantize to a bin. This is the "predict the same growth class as
    the prior terms" heuristic the spec calls out.
    """
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    n_near = 0
    pred_counts = np.zeros(env.n_bins(), dtype=np.int64)
    for t in range(n_episodes):
        obs, info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        # Extract last log term + mean log ratio from the obs vector.
        cmax = env.context_max()
        log_terms = obs[:cmax]
        mask = obs[cmax: 2 * cmax]
        # last_log is the META block's first scalar.
        meta_start = 3 * cmax + len(GROWTH_CLASSES)
        last_log = float(obs[meta_start])
        mean_log_ratio = float(obs[meta_start + 3])
        # Predict next log term.
        pred_log = last_log + mean_log_ratio
        pred_log = max(0.0, min(MAX_LOG10 - 1e-9, pred_log))
        width = MAX_LOG10 / env.n_bins()
        a = int(min(env.n_bins() - 1, max(0, math.floor(pred_log / width))))
        pred_counts[a] += 1
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if info.get("near"):
            n_near += 1
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "near_rate": float(n_near / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "growth_baseline",
        "pred_counts": pred_counts.tolist(),
    }


def train_reinforce(
    env: OeisSleepingEnv,
    n_episodes: int,
    *,
    lr: float = 0.02,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """Obs-conditioned REINFORCE (linear policy)."""
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.context_max())
    n_actions = env.n_bins()
    W = np.zeros((n_actions, obs_dim), dtype=np.float64)
    b = np.zeros(n_actions, dtype=np.float64)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    n_near = 0
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
        if info.get("near"):
            n_near += 1

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
        "near_rate": float(n_near / max(1, n_episodes)),
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
    env: OeisSleepingEnv,
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
    """Tiny PPO (NumPy MLP, 1 hidden layer, value head)."""
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.context_max())
    n_actions = env.n_bins()
    h = int(hidden)

    rng_init = np.random.default_rng(seed + 1)
    W1 = rng_init.standard_normal((h, obs_dim)) * (1.0 / math.sqrt(obs_dim))
    b1 = np.zeros(h, dtype=np.float64)
    Wp = rng_init.standard_normal((n_actions, h)) * (1.0 / math.sqrt(h))
    bp = np.zeros(n_actions, dtype=np.float64)
    Wv = rng_init.standard_normal((1, h)) * (1.0 / math.sqrt(h))
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
    n_near = 0
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
        a = int(rng.choice(n_actions, p=probs))
        pred_counts[a] += 1
        logp_old = float(np.log(probs[a] + 1e-12))
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
        if info.get("near"):
            n_near += 1

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
        "near_rate": float(n_near / max(1, n_episodes)),
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
    "OeisSleepingEnv",
    "N_BINS",
    "MAX_LOG10",
    "REWARD_HIT",
    "REWARD_NEAR",
    "REWARD_MISS",
    "DEFAULT_CONTEXT_MIN",
    "DEFAULT_CONTEXT_MAX",
    "value_to_bin",
    "bin_to_value_range",
    "bin_center_value",
    "register_with_gymnasium",
    "train_random",
    "train_growth_baseline",
    "train_reinforce",
    "train_ppo",
    "_obs_dim",
]
