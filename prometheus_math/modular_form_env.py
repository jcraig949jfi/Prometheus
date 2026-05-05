"""prometheus_math.modular_form_env -- Gymnasium-compatible newform env.

Cross-domain test #2 for the Prometheus discovery substrate. The BSD
rank env established the architecture works on a labelled domain;
modular forms push the same machinery onto a number-theoretically
deeper object: predict the next Hecke eigenvalue ``a_{p_{k+1}}`` of a
cuspidal newform, given its (level, weight, character) and the
preceding ``a_{p_1}, ..., a_{p_k}``.

Per-episode schema
------------------
1. ``reset()`` samples one newform from the configured split (train or
   test). Internally we also pick a "context length" ``k`` uniformly in
   ``[k_min, n_ap - 1]`` -- the agent will see ``a_{p_1}..a_{p_k}`` and
   must predict ``a_{p_{k+1}}``.
2. The agent picks an action ``a in {0, ..., N_BINS - 1}``: a
   discretized prediction of the *normalized* eigenvalue
   ``a_{p_{k+1}} / (2 * p_{k+1}^{(weight - 1) / 2})``, which by Deligne
   sits in [-1, 1].
3. ``step(a)`` BIND/EVAL-s through the sigma kernel (mirroring
   BSDRankEnv's substrate-growth invariant: 1 binding + 1 evaluation
   row per step), de-quantizes the action to a normalized prediction,
   compares to the true normalized eigenvalue, and pays out
   ``REWARD_HIT`` iff the prediction lands in the same bin as the
   ground truth.

Why bin-on-normalized?
----------------------
Without normalization the integer action space would be unbounded:
weight-24 forms have ``|a_p|`` up to ``2 * 113^{11.5} ~ 10^{23}``
while weight-2 forms have ``|a_p| < 22``. Normalizing by the Deligne
bound puts all forms on the same [-1, 1] scale and lets a *single*
21-bin action space cover every weight uniformly. Bin width
``2 / N_BINS`` gives a uniform-prior accuracy of ``1 / N_BINS``
(~5 % at N_BINS=21), which is the random baseline.

Skip-with-message contract
--------------------------
``ModularFormEnv.__init__`` raises ``RuntimeError`` if the corpus
loader reports unavailable. Tests catch this with ``pytest.skip``.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel

from . import _modular_form_corpus
from ._modular_form_corpus import (
    DEFAULT_N_AP,
    ModularFormEntry,
    PRIMES_30,
)


# ---------------------------------------------------------------------------
# Action / reward parameters
# ---------------------------------------------------------------------------

# 21 bins on [-1, 1] with bin width 2/21 ~ 0.095. The middle bin (10)
# straddles 0 and is the modal class for high-weight forms (where
# normalized a_p concentrate near 0 by Sato-Tate). Random predictor
# accuracy is 1/21 ~ 4.76%.
N_BINS: int = 21

# Reward magnitudes: same +100 / 0 convention as BSDRankEnv.
REWARD_HIT: float = 100.0
REWARD_MISS: float = 0.0

# Default minimum context length in primes -- fewer than 5 a_p exposed
# to the agent gives almost no signal. Cap at n_ap - 1 (we always need
# at least one prime to predict).
DEFAULT_CONTEXT_MIN: int = 5


# ---------------------------------------------------------------------------
# Quantization / Deligne helpers
# ---------------------------------------------------------------------------


def deligne_bound(prime: int, weight: int) -> float:
    """Deligne (Ramanujan-Petersson): ``|a_p| <= 2 * p^((weight-1)/2)``.

    Returns the upper bound as a float. For weight 2 this reduces to
    Hasse's ``|a_p| <= 2 sqrt(p)``.
    """
    if prime <= 1:
        raise ValueError(f"prime must be > 1; got {prime}")
    if weight < 1:
        raise ValueError(f"weight must be >= 1; got {weight}")
    return 2.0 * float(prime) ** ((weight - 1) / 2.0)


def normalize_ap(a_p: int, prime: int, weight: int) -> float:
    """Map raw a_p to the Deligne-normalized value in [-1, 1].

    Result may slightly exceed [-1, 1] for forms where the LMFDB
    ``traces`` row was computed with a different convention than the
    classical Petersson normalization; we clip in the env when forming
    bins.
    """
    bound = deligne_bound(prime, weight)
    if bound <= 0:
        return 0.0
    return float(a_p) / bound


def bin_for_normalized(value: float, n_bins: int = N_BINS) -> int:
    """Quantize a normalized eigenvalue in [-1, 1] into a bin index in
    ``[0, n_bins)``.

    Out-of-range inputs are clipped (a robustness concession in case a
    form's ``a_p`` exceeds the Deligne bound by a hair due to LMFDB
    rounding -- the relative slop is < 1e-9 in practice).
    """
    if n_bins <= 0:
        raise ValueError(f"n_bins must be > 0; got {n_bins}")
    v = max(-1.0, min(1.0, float(value)))
    # Map [-1, 1] -> [0, n_bins). The boundary v == 1.0 collapses into
    # the last bin.
    idx = int(math.floor(((v + 1.0) / 2.0) * n_bins))
    if idx >= n_bins:
        idx = n_bins - 1
    if idx < 0:
        idx = 0
    return idx


def bin_center(idx: int, n_bins: int = N_BINS) -> float:
    """Return the center of bin ``idx`` as a normalized value in [-1, 1]."""
    if idx < 0 or idx >= n_bins:
        raise ValueError(f"bin idx {idx} out of range [0, {n_bins})")
    return (2.0 * (idx + 0.5) / n_bins) - 1.0


# ---------------------------------------------------------------------------
# Substrate hook (identity binding, mirrors BSDRankEnv)
# ---------------------------------------------------------------------------


def _identity_predictor(bin_idx: int) -> int:
    return int(bin_idx)


_IDENTITY_REF = "prometheus_math.modular_form_env:_identity_predictor"


# ---------------------------------------------------------------------------
# Spec stubs
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
#   - n_ap normalized a_p values for primes p_1..p_{n_ap}; primes whose
#     index >= context_k (i.e. NOT yet revealed) are zeroed.
#   - n_ap mask values (1.0 if revealed, 0.0 otherwise).
#   - log10(level)                       (1)
#   - weight                             (1)
#   - char_order                         (1)
#   - target prime p_{k+1}               (1)
#   - log10(target prime)                (1)
#   - context length k                   (1)
#   - history features: running accuracy, last reward, last predicted
#     bin, last true bin, n_episodes_seen        (5)
HISTORY_DIM = 11


def _obs_dim(n_ap: int) -> int:
    return 2 * int(n_ap) + HISTORY_DIM


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


class ModularFormEnv:
    """Gymnasium-compatible env: predict a_{p_{k+1}} of a newform.

    Parameters
    ----------
    corpus : sequence[ModularFormEntry], optional
        Pre-loaded corpus. If None, the env calls
        ``_modular_form_corpus.load_modular_form_corpus(...)``; if THAT
        raises, the constructor re-raises so callers ``pytest.skip``.
    split : {"all", "train", "test"}
    train_frac, split_seed : float, int
    n_total, level_max, n_ap, seed, kernel_db_path :
        Forwarded to the corpus loader (when ``corpus`` is None) and the
        sigma kernel.
    n_bins : int
        Number of action bins on [-1, 1].
    context_min : int
        Minimum number of primes revealed to the agent before the
        prediction. Always at least 1.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[ModularFormEntry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        n_total: int = 1000,
        level_max: int = 1000,
        n_ap: int = DEFAULT_N_AP,
        seed: Optional[int] = None,
        kernel_db_path: str = ":memory:",
        n_bins: int = N_BINS,
        context_min: int = DEFAULT_CONTEXT_MIN,
        small_share: float = 0.4,
        medium_share: float = 0.4,
        large_share: float = 0.2,
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

        if corpus is None:
            corpus = _modular_form_corpus.load_modular_form_corpus(
                level_max=level_max,
                n_ap=n_ap,
                n_total=n_total,
                seed=corpus_seed,
                small_share=small_share,
                medium_share=medium_share,
                large_share=large_share,
            )
        corpus = list(corpus)
        if not corpus:
            raise ValueError("ModularFormEnv corpus is empty")

        # Verify a_p length consistency.
        ap_len = len(corpus[0].a_p)
        for e in corpus:
            if len(e.a_p) != ap_len:
                raise ValueError(
                    f"corpus has inconsistent a_p lengths: "
                    f"{ap_len} vs {len(e.a_p)} at {e.label}"
                )
        if ap_len <= context_min:
            raise ValueError(
                f"a_p length {ap_len} <= context_min {context_min}; "
                f"need at least one prime to predict"
            )
        self._n_ap = int(ap_len)

        if split == "all":
            self._split_corpus: List[ModularFormEntry] = list(corpus)
        else:
            train, test = _modular_form_corpus.split_train_test(
                corpus, train_frac=train_frac, seed=split_seed
            )
            self._split_corpus = list(train if split == "train" else test)
        if not self._split_corpus:
            raise ValueError(f"split {split!r} is empty after partitioning")

        self.split = split
        self._kernel_db_path = kernel_db_path
        self._n_bins = int(n_bins)
        self._context_min = int(context_min)
        self._seed = seed
        self._rng = random.Random(seed)
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._state = _EpisodeState()
        self._current: Optional[ModularFormEntry] = None
        self._context_k: int = self._context_min
        self._step_called = False

        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(_obs_dim(self._n_ap),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(self._n_bins)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((_obs_dim(self._n_ap),))
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

        # Sample form + context length.
        idx = self._rng.randrange(len(self._split_corpus))
        self._current = self._split_corpus[idx]
        max_k = self._n_ap - 1
        if self._context_min > max_k:
            self._context_k = max_k
        else:
            self._context_k = self._rng.randint(self._context_min, max_k)

        target_prime = int(self._current.primes[self._context_k])
        true_a_p = int(self._current.a_p[self._context_k])
        true_norm = normalize_ap(true_a_p, target_prime, self._current.weight)
        true_bin = bin_for_normalized(true_norm, self._n_bins)

        info = {
            "n_actions": self._n_bins,
            "label": self._current.label,
            "level": self._current.level,
            "weight": self._current.weight,
            "char_order": self._current.char_order,
            "target_prime": target_prime,
            "true_a_p": true_a_p,
            "true_normalized": true_norm,
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
                "ModularFormEnv: step() called twice in one episode "
                "(episode length is 1; call reset() before next step)"
            )
        a = int(action)
        if a < 0 or a >= self._n_bins:
            raise ValueError(
                f"action {a} out of range [0, {self._n_bins})"
            )

        # Compute ground truth.
        target_prime = int(self._current.primes[self._context_k])
        true_a_p = int(self._current.a_p[self._context_k])
        true_norm = normalize_ap(true_a_p, target_prime, self._current.weight)
        true_bin = bin_for_normalized(true_norm, self._n_bins)

        # BIND/EVAL through substrate. Episode-fresh kernel so binding
        # names need only be unique within the episode.
        cap_b = self._kernel.mint_capability("BindCap")
        binding = self._ext.BIND(
            callable_ref=_IDENTITY_REF,
            cost_model=CostModel(),
            postconditions=[],
            authority_refs=[
                f"lmfdb:{self._current.label}",
                f"prime:{target_prime}",
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

        # Predicted normalized & implied a_p (from bin center).
        pred_norm = bin_center(a, self._n_bins)
        bound = deligne_bound(target_prime, self._current.weight)
        pred_a_p = pred_norm * bound

        info = {
            "label": self._current.label,
            "level": self._current.level,
            "weight": self._current.weight,
            "target_prime": target_prime,
            "true_a_p": true_a_p,
            "true_normalized": true_norm,
            "true_bin": true_bin,
            "predicted_bin": a,
            "predicted_normalized": pred_norm,
            "predicted_a_p_estimate": pred_a_p,
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
            return np.zeros(_obs_dim(self._n_ap), dtype=np.float64)
        # Normalized a_p, with primes >= context_k masked to 0.
        norm = np.zeros(self._n_ap, dtype=np.float64)
        mask = np.zeros(self._n_ap, dtype=np.float64)
        for i in range(self._context_k):
            p_i = int(self._current.primes[i])
            a_i = int(self._current.a_p[i])
            try:
                norm[i] = normalize_ap(a_i, p_i, self._current.weight)
            except ValueError:
                norm[i] = 0.0
            mask[i] = 1.0
        target_prime = int(self._current.primes[self._context_k])
        log_lvl = math.log10(max(1, self._current.level))
        log_p = math.log10(target_prime)
        history = np.array([
            float(self._current.weight),
            float(self._current.char_order),
            float(target_prime),
            log_lvl,
            log_p,
            float(self._context_k),
            self.running_accuracy(),
            self._state.last_reward / max(REWARD_HIT, 1.0),
            float(self._state.last_pred_bin),
            float(self._state.last_true_bin),
            float(self._state.n_episodes_seen),
        ], dtype=np.float64)
        return np.concatenate([norm, mask, history])

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

    def n_ap(self) -> int:
        return self._n_ap

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
    env_id = "prometheus/ModularForm-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.modular_form_env:ModularFormEnv",
        )
    except Exception:
        pass
    return env_id


# ---------------------------------------------------------------------------
# Lightweight trainers (random, REINFORCE-linear, PPO-MLP)
# ---------------------------------------------------------------------------


def train_random(
    env: ModularFormEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random bin prediction baseline.

    Equivalent to drawing a uniform a_p in [-Deligne, +Deligne] then
    bin-ing -- the Deligne-bounded random prediction the spec calls
    out.
    """
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
    env: ModularFormEnv,
    n_episodes: int,
    *,
    lr: float = 0.02,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """Obs-conditioned REINFORCE (linear policy) for ModularFormEnv.

    Same architecture as ``train_reinforce_bsd``: logits = W @ obs + b,
    softmax, single-step contextual-bandit update. Episode length is 1.
    """
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.n_ap())
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
    env: ModularFormEnv,
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
    """Tiny PPO-style trainer with a 2-layer MLP policy + value head.

    This is a self-contained PPO variant matching the architecture used
    by ``discovery_env`` callers. We keep all logic in NumPy to avoid a
    torch dependency in the test environment. Episode length is 1 so
    advantages reduce to ``A = r_scaled - V(s)``.
    """
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.n_ap())
    n_actions = env.n_bins()
    h = int(hidden)

    # Xavier-ish init.
    rng_torch = np.random.default_rng(seed + 1)
    W1 = rng_torch.standard_normal((h, obs_dim)) * (1.0 / math.sqrt(obs_dim))
    b1 = np.zeros(h, dtype=np.float64)
    Wp = rng_torch.standard_normal((n_actions, h)) * (1.0 / math.sqrt(h))
    bp = np.zeros(n_actions, dtype=np.float64)
    Wv = rng_torch.standard_normal((1, h)) * (1.0 / math.sqrt(h))
    bv = np.zeros(1, dtype=np.float64)

    def _forward(obs: np.ndarray):
        # obs: (B, obs_dim) or (obs_dim,)
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

    # Rolling buffers for batch updates.
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

        ret = float(r) * reward_scale
        adv = ret - float(value)

        buf_obs.append(obs.astype(np.float64))
        buf_act.append(a)
        buf_logp.append(logp_old)
        buf_adv.append(adv)
        buf_ret.append(ret)

        # Update when batch ready.
        if len(buf_obs) >= batch_size:
            obs_arr = np.stack(buf_obs, axis=0)
            act_arr = np.asarray(buf_act, dtype=np.int64)
            logp_old_arr = np.asarray(buf_logp, dtype=np.float64)
            adv_arr = np.asarray(buf_adv, dtype=np.float64)
            ret_arr = np.asarray(buf_ret, dtype=np.float64)
            # Standardize advantages (PPO best practice).
            if adv_arr.std() > 1e-8:
                adv_arr = (adv_arr - adv_arr.mean()) / (adv_arr.std() + 1e-8)

            for _epoch in range(n_epochs):
                # Forward.
                h_pre = obs_arr @ W1.T + b1
                h_act = np.maximum(h_pre, 0.0)
                logits = h_act @ Wp.T + bp
                values = (h_act @ Wv.T + bv).squeeze(-1)
                probs_new = _softmax(logits)
                logp_new = np.log(
                    probs_new[np.arange(obs_arr.shape[0]), act_arr] + 1e-12
                )
                ratio = np.exp(logp_new - logp_old_arr)
                # PPO clip surrogate: maximize min(r*A, clip(r)*A).
                clipped = np.clip(ratio, 1.0 - clip_eps, 1.0 + clip_eps)
                surr = np.minimum(ratio * adv_arr, clipped * adv_arr)
                # Entropy bonus.
                ent = -(probs_new * np.log(probs_new + 1e-12)).sum(axis=-1)
                # Loss = -(surr + ent_coef * ent) + 0.5 * (V - ret)^2.
                # We do a simple gradient via finite differences? No --
                # we'll compute analytic gradients per layer.

                # Value loss gradient.
                v_err = values - ret_arr  # dL_v / dV
                grad_h_v = v_err[:, None] @ Wv  # (B, h)

                # Policy gradient.
                # d log p_a / d logits = e_a - p; clipped surrogate
                # gradient is r * A * (e_a - p) where mask = whether
                # clipped or not. We'll compute it with a where-mask.
                use_clip = (
                    ((ratio > 1.0 + clip_eps) & (adv_arr > 0)) |
                    ((ratio < 1.0 - clip_eps) & (adv_arr < 0))
                )
                effective_ratio = np.where(use_clip, 0.0, ratio * adv_arr)
                # Per-sample gradient of surrogate w.r.t. logits.
                onehot = np.zeros_like(probs_new)
                onehot[np.arange(obs_arr.shape[0]), act_arr] = 1.0
                d_logits = -effective_ratio[:, None] * (onehot - probs_new)
                # Entropy gradient w.r.t. logits: d (-sum p log p) / d
                # logits_i = -p_i * (log p_i + 1) + p_i * (sum p_j (log p_j + 1)).
                lp = np.log(probs_new + 1e-12)
                ent_grad = -probs_new * (lp + 1.0) + probs_new * (
                    (probs_new * (lp + 1.0)).sum(axis=-1, keepdims=True)
                )
                d_logits = d_logits - entropy_coef * ent_grad

                # Backprop into MLP.
                grad_Wp = d_logits.T @ h_act  # (n_actions, h)
                grad_bp = d_logits.sum(axis=0)
                grad_h_pol = d_logits @ Wp  # (B, h)

                # Value head.
                grad_Wv = (v_err[:, None] * h_act).sum(axis=0, keepdims=True)
                grad_bv = np.array([v_err.sum()])

                # Hidden layer (ReLU mask).
                grad_h_total = grad_h_pol + grad_h_v
                relu_mask = (h_pre > 0).astype(np.float64)
                grad_pre = grad_h_total * relu_mask
                grad_W1 = grad_pre.T @ obs_arr
                grad_b1 = grad_pre.sum(axis=0)

                # Average across batch.
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
    "ModularFormEnv",
    "N_BINS",
    "REWARD_HIT",
    "REWARD_MISS",
    "DEFAULT_CONTEXT_MIN",
    "deligne_bound",
    "normalize_ap",
    "bin_for_normalized",
    "bin_center",
    "register_with_gymnasium",
    "train_random",
    "train_reinforce",
    "train_ppo",
]
