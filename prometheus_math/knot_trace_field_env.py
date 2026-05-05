"""prometheus_math.knot_trace_field_env -- Knot trace-field class env.

Cross-domain test #3 for the Prometheus discovery substrate. After
BSD rank (+1.37x) and modular forms (+1.58x), we test whether the
substrate transports to a TOPOLOGICAL domain: predict the coarse
class of the *trace field* of a hyperbolic knot from its KnotInfo
invariants (Alexander polynomial coefficients, signature, determinant,
hyperbolic volume).

Per-episode schema
------------------
1. ``reset()`` samples one knot from the configured split (train or
   test). The observation is a fixed-length feature vector built from:
       - Alexander polynomial coefficients (zero-padded to
         DEFAULT_ALEXANDER_LEN),
       - signature, determinant, three-genus, hyperbolic volume,
       - log10(determinant), volume / pi (a unit-normalized form),
       - history features (running accuracy etc).
2. The agent picks an action ``a in {0, 1, ..., N_CLASSES - 1}``: the
   predicted trace-field class.
3. ``step(a)`` BIND/EVAL-s through the sigma kernel (mirroring
   BSDRankEnv / ModularFormEnv: 1 binding + 1 evaluation row per
   step), compares to the true class, pays out REWARD_HIT iff the
   classes match.

Action / class mapping
----------------------
The 7 classes in ``_knot_trace_field_corpus.TRACE_FIELD_CLASSES`` are:
    0: Q
    1: real_quadratic
    2: complex_quadratic       (figure-8 4_1 lives here)
    3: totally_real_cubic
    4: complex_cubic           (5_2 is a canonical example)
    5: degree_4
    6: degree_5_plus

The corpus is dominated by degree_5_plus and degree_4 entries (the
generic case for hyperbolic knots beyond 7 crossings). A uniform
random predictor over 7 classes attains accuracy 1/7 ~= 0.143; an
"always predict the modal class" predictor will do considerably
better. Welch p-values vs the random baseline are still meaningful
because both predictors are constant-in-effort.

Skip-with-message contract
--------------------------
``KnotTraceFieldEnv.__init__`` raises ``RuntimeError`` if the corpus
loader reports unavailable. The hand-curated fallback is always
shipped inline so this never actually fires; the contract exists for
parity with the BSD / modular-form envs.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel

from . import _knot_trace_field_corpus
from ._knot_trace_field_corpus import (
    DEFAULT_ALEXANDER_LEN,
    KnotTraceFieldEntry,
    N_CLASSES,
    TRACE_FIELD_CLASSES,
)


# ---------------------------------------------------------------------------
# Action / reward parameters
# ---------------------------------------------------------------------------

# Reward magnitudes -- same +100 / 0 convention as BSDRankEnv and
# ModularFormEnv, so the +/-100 scale is consistent across all three
# cross-domain validation envs.
REWARD_HIT: float = 100.0
REWARD_MISS: float = 0.0


# ---------------------------------------------------------------------------
# Substrate hook (identity binding, mirrors BSDRankEnv / ModularFormEnv)
# ---------------------------------------------------------------------------


def _identity_predictor(class_idx: int) -> int:
    """Trivial callable bound by the env: receives the predicted
    class and returns it unchanged. The substrate uses this as the
    EVAL hook so each prediction generates one (binding, evaluation)
    row pair.
    """
    return int(class_idx)


_IDENTITY_REF = "prometheus_math.knot_trace_field_env:_identity_predictor"


# ---------------------------------------------------------------------------
# Spec stubs (used when gymnasium is not installed)
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
#   - Alexander polynomial coefficients (length alexander_len)
#   - signature                                 (1)
#   - determinant                               (1)
#   - log10(determinant)                        (1)
#   - three_genus                               (1)
#   - hyperbolic_volume                         (1)
#   - volume / pi                               (1)
#   - crossing_number                           (1)
#   - history features (5):
#       running accuracy
#       last reward (normalized)
#       last predicted class
#       last true class
#       n_episodes_seen
HISTORY_DIM = 5
INVARIANT_DIM = 7  # signature, det, log10(det), three_genus, vol, vol/pi, crossings


def _obs_dim(alexander_len: int) -> int:
    return int(alexander_len) + INVARIANT_DIM + HISTORY_DIM


# ---------------------------------------------------------------------------
# Episode state
# ---------------------------------------------------------------------------


@dataclass
class _EpisodeState:
    n_episodes_seen: int = 0
    n_correct: int = 0
    last_reward: float = 0.0
    last_pred_class: int = -1
    last_true_class: int = -1


# ---------------------------------------------------------------------------
# Env
# ---------------------------------------------------------------------------


class KnotTraceFieldEnv:
    """Gymnasium-compatible env: predict the trace-field class of a
    hyperbolic knot from KnotInfo invariants.

    Parameters
    ----------
    corpus : sequence[KnotTraceFieldEntry], optional
        Pre-loaded corpus. If None, calls
        ``_knot_trace_field_corpus.load_knot_trace_field_corpus(...)``;
        if THAT raises, the constructor re-raises so callers
        ``pytest.skip``.
    split : {"all", "train", "test"}
    train_frac, split_seed : float, int
        Train/test split parameters.
    seed, kernel_db_path :
        Forwarded to the sigma kernel.
    include_non_hyperbolic : bool
        If True, allow torus knots (Class 0) into the corpus. Default
        False.
    alexander_pad_to : int
        Target Alexander polynomial vector length.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[KnotTraceFieldEntry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        seed: Optional[int] = None,
        kernel_db_path: str = ":memory:",
        include_non_hyperbolic: bool = False,
        alexander_pad_to: int = DEFAULT_ALEXANDER_LEN,
    ):
        if split not in ("all", "train", "test"):
            raise ValueError(
                f"split must be 'all', 'train', or 'test'; got {split!r}"
            )
        if alexander_pad_to <= 0:
            raise ValueError(
                f"alexander_pad_to must be > 0; got {alexander_pad_to}"
            )

        if corpus is None:
            corpus = _knot_trace_field_corpus.load_knot_trace_field_corpus(
                include_non_hyperbolic=include_non_hyperbolic,
                alexander_pad_to=alexander_pad_to,
            )
        corpus = list(corpus)
        if not corpus:
            raise ValueError("KnotTraceFieldEnv corpus is empty")

        # Verify schema consistency: every entry must have an Alexander
        # polynomial vector of the same length AND a class in [0, N_CLASSES).
        alex_len = len(corpus[0].alexander_coeffs)
        for e in corpus:
            if len(e.alexander_coeffs) != alex_len:
                raise ValueError(
                    f"corpus has inconsistent Alexander vector lengths: "
                    f"{alex_len} vs {len(e.alexander_coeffs)} at {e.name}"
                )
            if not (0 <= e.trace_field_class < N_CLASSES):
                raise ValueError(
                    f"trace_field_class {e.trace_field_class} out of "
                    f"range at {e.name}"
                )

        if split == "all":
            self._split_corpus: List[KnotTraceFieldEntry] = list(corpus)
        else:
            train, test = _knot_trace_field_corpus.split_train_test(
                corpus, train_frac=train_frac, seed=split_seed
            )
            self._split_corpus = list(train if split == "train" else test)
        if not self._split_corpus:
            raise ValueError(f"split {split!r} is empty after partitioning")

        self.split = split
        self._kernel_db_path = kernel_db_path
        self._alex_len = int(alex_len)
        self._seed = seed
        self._rng = random.Random(seed)
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._state = _EpisodeState()
        self._current: Optional[KnotTraceFieldEntry] = None
        self._step_called = False

        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(_obs_dim(self._alex_len),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(N_CLASSES)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((_obs_dim(self._alex_len),))
            self.action_space = _DiscreteStub(N_CLASSES)
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

        idx = self._rng.randrange(len(self._split_corpus))
        self._current = self._split_corpus[idx]

        info = {
            "n_actions": N_CLASSES,
            "name": self._current.name,
            "crossing_number": self._current.crossing_number,
            "trace_field_class": int(self._current.trace_field_class),
            "trace_field_class_name":
                TRACE_FIELD_CLASSES[self._current.trace_field_class],
            "trace_field_degree": self._current.trace_field_degree,
            "hyperbolic_volume": self._current.hyperbolic_volume,
            "split": self.split,
            "true_class": int(self._current.trace_field_class),
        }
        return self._obs(), info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._ext is None or self._current is None:
            raise RuntimeError("env.step() called before env.reset()")
        if self._step_called:
            raise RuntimeError(
                "KnotTraceFieldEnv: step() called twice in one episode "
                "(episode length is 1; call reset() before next step)"
            )
        a = int(action)
        if a < 0 or a >= N_CLASSES:
            raise ValueError(
                f"action {a} out of range [0, {N_CLASSES})"
            )

        true_class = int(self._current.trace_field_class)

        # BIND/EVAL through the substrate. Episode-fresh kernel so binding
        # names need only be unique within the episode.
        cap_b = self._kernel.mint_capability("BindCap")
        binding = self._ext.BIND(
            callable_ref=_IDENTITY_REF,
            cost_model=CostModel(),
            postconditions=[],
            authority_refs=[
                f"knotinfo:{self._current.name}",
                f"trace_field:{self._current.source}",
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
            output_class = int(ev.output_repr)
        except (TypeError, ValueError):
            output_class = a

        hit = (output_class == true_class)
        reward = REWARD_HIT if hit else REWARD_MISS

        self._state.n_episodes_seen += 1
        if hit:
            self._state.n_correct += 1
        self._state.last_reward = float(reward)
        self._state.last_pred_class = a
        self._state.last_true_class = true_class

        terminated = True
        truncated = False
        self._step_called = True

        info = {
            "name": self._current.name,
            "crossing_number": self._current.crossing_number,
            "trace_field_class": true_class,
            "trace_field_class_name": TRACE_FIELD_CLASSES[true_class],
            "trace_field_degree": self._current.trace_field_degree,
            "predicted_class": a,
            "predicted_class_name": TRACE_FIELD_CLASSES[a],
            "hit": bool(hit),
            "running_accuracy": self.running_accuracy(),
            "n_episodes_seen": self._state.n_episodes_seen,
            "binding_name": binding.symbol.name,
            "binding_version": binding.symbol.version,
            "eval_success": ev.success,
            "split": self.split,
            "hyperbolic_volume": self._current.hyperbolic_volume,
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
            return np.zeros(_obs_dim(self._alex_len), dtype=np.float64)
        e = self._current
        # Alexander polynomial coefficients (already padded by loader).
        alex = np.asarray(e.alexander_coeffs, dtype=np.float64)
        if alex.shape[0] != self._alex_len:
            # Defensive: pad / truncate to declared length.
            if alex.shape[0] < self._alex_len:
                alex = np.concatenate([
                    alex, np.zeros(self._alex_len - alex.shape[0])
                ])
            else:
                alex = alex[:self._alex_len]

        det = max(1, int(e.determinant))
        log_det = math.log10(det)
        vol = float(e.hyperbolic_volume)
        vol_per_pi = vol / math.pi if math.isfinite(vol) else 0.0

        invariants = np.array([
            float(e.signature),
            float(e.determinant),
            float(log_det),
            float(e.three_genus),
            vol,
            vol_per_pi,
            float(e.crossing_number),
        ], dtype=np.float64)

        history = np.array([
            self.running_accuracy(),
            self._state.last_reward / max(REWARD_HIT, 1.0),
            float(self._state.last_pred_class),
            float(self._state.last_true_class),
            float(self._state.n_episodes_seen),
        ], dtype=np.float64)

        return np.concatenate([alex, invariants, history])

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

    def alexander_len(self) -> int:
        return self._alex_len

    def n_classes(self) -> int:
        return N_CLASSES


# ---------------------------------------------------------------------------
# Optional gymnasium registration
# ---------------------------------------------------------------------------


def register_with_gymnasium() -> Optional[str]:
    try:
        import gymnasium as gym
    except ImportError:
        return None
    env_id = "prometheus/KnotTraceField-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.knot_trace_field_env:KnotTraceFieldEnv",
        )
    except Exception:
        pass
    return env_id


# ---------------------------------------------------------------------------
# Lightweight trainers (random, REINFORCE-linear, PPO-MLP)
# ---------------------------------------------------------------------------


def train_random(
    env: KnotTraceFieldEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random class prediction baseline."""
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(N_CLASSES, dtype=np.int64)
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, N_CLASSES))
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
    env: KnotTraceFieldEnv,
    n_episodes: int,
    *,
    lr: float = 0.02,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    seed: int = 0,
) -> Dict[str, Any]:
    """Obs-conditioned REINFORCE (linear policy) for KnotTraceFieldEnv.

    Same architecture as ``train_reinforce`` in the BSD / modular form
    envs: logits = W @ obs + b, softmax, single-step contextual-bandit
    update. Episode length is 1.
    """
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.alexander_len())
    n_actions = env.n_classes()
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
    env: KnotTraceFieldEnv,
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

    Mirrors ``modular_form_env.train_ppo`` exactly (NumPy implementation,
    no torch dep). Episode length is 1 so advantages reduce to
    ``A = r_scaled - V(s)``.
    """
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.alexander_len())
    n_actions = env.n_classes()
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
    "KnotTraceFieldEnv",
    "REWARD_HIT",
    "REWARD_MISS",
    "N_CLASSES",
    "TRACE_FIELD_CLASSES",
    "register_with_gymnasium",
    "train_random",
    "train_reinforce",
    "train_ppo",
]
