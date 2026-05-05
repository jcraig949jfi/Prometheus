"""prometheus_math.genus2_env -- Gymnasium-compatible genus-2 rank env.

Cross-domain test #3 for the Prometheus discovery substrate. Per
``project_genus2_rosetta.md``, genus-2 sits at the intersection of all
five mathematical worlds (elliptic curves, modular forms, abelian
surfaces, number fields, L-functions) -- making it the highest-leverage
domain for the substrate's island-silence test.

Per-episode schema
------------------
1. ``reset()`` samples one curve from the configured split (train or
   test) and presents its feature vector + a small running-history
   summary as the observation.
2. The agent picks an action ``a in {0, 1, 2}``: predicted rank class.
   Class 0 = analytic_rank 0; 1 = analytic_rank 1; 2 = analytic_rank
   2 or higher.
3. ``step(a)`` BIND/EVAL-s the prediction through the sigma kernel,
   then issues reward = +100 iff the predicted class matches the
   curve's ground-truth rank class, else 0. Episodes are length 1.

The substrate growth invariant (1 binding + 1 evaluation row per step)
is preserved to mirror BSDRankEnv and ModularFormEnv.

Skip-with-message contract
--------------------------
``Genus2Env.__init__`` raises ``RuntimeError`` if the corpus loader
reports unavailable. Tests catch this with ``pytest.skip``.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel

from . import _genus2_corpus
from ._genus2_corpus import (
    F_COEFF_LEN,
    H_COEFF_LEN,
    Genus2Entry,
    N_RANK_CLASSES,
)


# ---------------------------------------------------------------------------
# Action / reward parameters
# ---------------------------------------------------------------------------

# Three rank classes: 0, 1, "2+". Random baseline accuracy = 1/3.
N_RANK_ACTIONS: int = N_RANK_CLASSES

# Reward magnitudes (kept consistent with BSDRankEnv / ModularFormEnv).
REWARD_HIT: float = 100.0
REWARD_MISS: float = 0.0


# ---------------------------------------------------------------------------
# Substrate hook (identity binding, mirrors BSDRankEnv / ModularFormEnv)
# ---------------------------------------------------------------------------


def _identity_predictor(rank_class: int) -> int:
    """Identity callable bound by the env: returns the predicted class."""
    return int(rank_class)


_IDENTITY_REF = "prometheus_math.genus2_env:_identity_predictor"


# ---------------------------------------------------------------------------
# Spec stubs (for environments without gymnasium)
# ---------------------------------------------------------------------------


class _BoxStub:
    """Minimal stand-in for gymnasium.spaces.Box."""

    def __init__(self, shape: Tuple[int, ...]):
        self.shape = tuple(shape)
        self.dtype = np.float64

    def contains(self, x) -> bool:  # noqa: D401
        return isinstance(x, np.ndarray) and x.shape == self.shape


class _DiscreteStub:
    """Minimal stand-in for gymnasium.spaces.Discrete."""

    def __init__(self, n: int):
        self.n = int(n)

    def sample(self) -> int:
        return random.randrange(self.n)

    def contains(self, x) -> bool:
        return isinstance(x, int) and 0 <= x < self.n


# ---------------------------------------------------------------------------
# Observation feature layout
# ---------------------------------------------------------------------------


# obs vector layout:
#   - log10(conductor)                    (1)
#   - log10(abs_disc)                     (1)
#   - disc_sign                           (1)
#   - log10(torsion_order)                (1)
#   - real_period (clipped log)           (1)
#   - f_coeffs (degree-6 polynomial)      (F_COEFF_LEN = 7)
#   - h_coeffs (degree-3 polynomial)      (H_COEFF_LEN = 4)
#   - history features:
#       running accuracy                  (1)
#       last reward                       (1)
#       n_episodes_seen                   (1)
#       last predicted class              (1)
#       last true class                   (1)
HISTORY_DIM: int = 6  # log_period + 5 history slots
SCALAR_DIM: int = 4   # log_cond, log_disc, disc_sign, log_torsion


def obs_dim() -> int:
    return SCALAR_DIM + 1 + F_COEFF_LEN + H_COEFF_LEN + 5


def _safe_log10(x: float, floor: float = 1.0) -> float:
    return math.log10(max(float(floor), float(x)))


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


class Genus2Env:
    """Gymnasium-compatible env: predict rank class of a genus-2 curve.

    Parameters
    ----------
    corpus : sequence[Genus2Entry], optional
        Pre-loaded corpus. If None, ``Genus2Env`` calls
        ``_genus2_corpus.load_genus2_corpus(...)`` with the kwargs
        below; if THAT raises, the constructor re-raises so callers
        ``pytest.skip``.
    split : {"all", "train", "test"}
    train_frac, split_seed : float, int
    n_total, cond_max, seed, kernel_db_path :
        Forwarded to the corpus loader (when ``corpus`` is None) and
        the sigma kernel.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[Genus2Entry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        n_total: int = 2000,
        cond_max: int = 50000,
        rank0_share: float = 0.30,
        rank1_share: float = 0.45,
        rank2plus_share: float = 0.25,
        corpus_seed: int = 0,
        seed: Optional[int] = None,
        kernel_db_path: str = ":memory:",
    ):
        if split not in ("all", "train", "test"):
            raise ValueError(
                f"split must be 'all', 'train', or 'test'; got {split!r}"
            )

        if corpus is None:
            corpus = _genus2_corpus.load_genus2_corpus(
                cond_max=cond_max,
                n_total=n_total,
                rank0_share=rank0_share,
                rank1_share=rank1_share,
                rank2plus_share=rank2plus_share,
                seed=corpus_seed,
            )
        corpus = list(corpus)
        if not corpus:
            raise ValueError("Genus2Env corpus is empty")

        # Verify schema consistency.
        for e in corpus:
            if len(e.f_coeffs) != F_COEFF_LEN:
                raise ValueError(
                    f"corpus has malformed f_coeffs at {e.label}: "
                    f"len={len(e.f_coeffs)} != {F_COEFF_LEN}"
                )
            if len(e.h_coeffs) != H_COEFF_LEN:
                raise ValueError(
                    f"corpus has malformed h_coeffs at {e.label}: "
                    f"len={len(e.h_coeffs)} != {H_COEFF_LEN}"
                )

        if split == "all":
            self._split_corpus: List[Genus2Entry] = list(corpus)
        else:
            train, test = _genus2_corpus.split_train_test(
                corpus, train_frac=train_frac, seed=split_seed
            )
            self._split_corpus = list(train if split == "train" else test)
        if not self._split_corpus:
            raise ValueError(f"split {split!r} is empty after partitioning")

        self.split = split
        self._kernel_db_path = kernel_db_path
        self._seed = seed
        self._rng = random.Random(seed)
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._state = _EpisodeState()
        self._current: Optional[Genus2Entry] = None
        self._step_called = False  # one prediction per episode

        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(obs_dim(),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(N_RANK_ACTIONS)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((obs_dim(),))
            self.action_space = _DiscreteStub(N_RANK_ACTIONS)
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

        # Sample a curve uniformly from the split.
        idx = self._rng.randrange(len(self._split_corpus))
        self._current = self._split_corpus[idx]

        info = {
            "n_actions": N_RANK_ACTIONS,
            "label": self._current.label,
            "iso_class": self._current.iso_class,
            "conductor": self._current.conductor,
            "abs_disc": self._current.abs_disc,
            "true_rank_class": self._current.rank_class,
            "true_analytic_rank": self._current.analytic_rank,
            "torsion_order": self._current.torsion_order,
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
                "Genus2Env: step() called twice in one episode "
                "(episode length is 1; call reset() before next step)"
            )
        a = int(action)
        if a < 0 or a >= N_RANK_ACTIONS:
            raise ValueError(
                f"action {a} out of range [0, {N_RANK_ACTIONS})"
            )

        # BIND/EVAL through substrate.
        cap_b = self._kernel.mint_capability("BindCap")
        binding = self._ext.BIND(
            callable_ref=_IDENTITY_REF,
            cost_model=CostModel(),
            postconditions=[],
            authority_refs=[
                f"lmfdb:{self._current.label}",
                f"iso:{self._current.iso_class}",
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
            output_value = int(ev.output_repr)
        except (TypeError, ValueError):
            output_value = a  # identity round-trips

        true_class = int(self._current.rank_class)
        hit = (output_value == true_class)
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
            "label": self._current.label,
            "iso_class": self._current.iso_class,
            "conductor": self._current.conductor,
            "abs_disc": self._current.abs_disc,
            "true_rank_class": true_class,
            "true_analytic_rank": int(self._current.analytic_rank),
            "predicted_class": a,
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
            except Exception:  # pragma: no cover -- best-effort close
                pass
        self._kernel = None
        self._ext = None

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        if self._current is None:
            return np.zeros(obs_dim(), dtype=np.float64)
        e = self._current
        # Stabilized scalars: log scales clipped to small range.
        scalars = np.array([
            _safe_log10(e.conductor) / 6.0,        # ~ [0, 1]
            _safe_log10(e.abs_disc) / 10.0,        # ~ [0, 1]
            float(e.disc_sign),                    # +/- 1
            _safe_log10(max(1, e.torsion_order)) / 2.0,  # ~ [0, 1]
        ], dtype=np.float64)
        # Real period: log-stabilized.
        rp = max(1e-3, abs(float(e.real_period)))
        log_period = math.log10(rp)
        log_period = max(-3.0, min(6.0, log_period)) / 6.0  # ~ [-0.5, 1]

        # Coefficient features: clip + sign-log compress to keep
        # magnitudes bounded (g2c models can have |coeff| up to ~1e3).
        def _clog(v: float) -> float:
            s = 1.0 if v > 0 else (-1.0 if v < 0 else 0.0)
            return s * math.log10(1.0 + abs(float(v)))

        f_co = np.array([_clog(x) for x in e.f_coeffs], dtype=np.float64)
        h_co = np.array([_clog(x) for x in e.h_coeffs], dtype=np.float64)

        history = np.array([
            self.running_accuracy(),
            self._state.last_reward / REWARD_HIT,  # in [0, 1]
            min(1.0, float(self._state.n_episodes_seen) / 1000.0),
            float(self._state.last_pred_class) / max(1, N_RANK_ACTIONS - 1),
            float(self._state.last_true_class) / max(1, N_RANK_ACTIONS - 1),
        ], dtype=np.float64)

        return np.concatenate([
            scalars,
            np.array([log_period], dtype=np.float64),
            f_co,
            h_co,
            history,
        ])

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


# ---------------------------------------------------------------------------
# Optional gymnasium registration
# ---------------------------------------------------------------------------


def register_with_gymnasium() -> Optional[str]:
    """Register the env with gymnasium if available; return its id or None."""
    try:
        import gymnasium as gym
    except ImportError:
        return None
    env_id = "prometheus/Genus2-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.genus2_env:Genus2Env",
        )
    except Exception:
        # Already registered or signature changed; treat as soft success.
        pass
    return env_id


# ---------------------------------------------------------------------------
# Lightweight trainers (random + REINFORCE-linear + PPO-MLP).
# Same architecture as BSDRankEnv / ModularFormEnv trainers.
# ---------------------------------------------------------------------------


def train_random(
    env: Genus2Env,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random rank-class baseline."""
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(N_RANK_ACTIONS, dtype=np.int64)
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, N_RANK_ACTIONS))
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
    env: Genus2Env,
    n_episodes: int,
    *,
    lr: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.02,
    seed: int = 0,
) -> Dict[str, Any]:
    """Obs-conditioned REINFORCE (linear policy) for Genus2Env.

    Policy: logits = W @ obs + b, then softmax. Episode length is 1, so
    the gradient update is a single-step contextual bandit. The obs
    vector includes log-conductor, log-disc, coefficients, torsion --
    the policy can therefore learn a linear discriminator from these
    features to rank class.
    """
    rng = np.random.default_rng(seed)
    od = obs_dim()
    W = np.zeros((N_RANK_ACTIONS, od), dtype=np.float64)
    b = np.zeros(N_RANK_ACTIONS, dtype=np.float64)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    baseline = 0.0
    pred_counts = np.zeros(N_RANK_ACTIONS, dtype=np.int64)

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        z = logits - logits.max()
        probs = np.exp(z)
        probs = probs / probs.sum()
        a = int(rng.choice(N_RANK_ACTIONS, p=probs))
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
    # Clip raw logits to avoid overflow in degenerate runs.
    x = np.clip(x, -50.0, 50.0)
    z = x - x.max(axis=-1, keepdims=True)
    e = np.exp(z)
    s = e.sum(axis=-1, keepdims=True)
    s = np.where(s <= 0, 1.0, s)
    return e / s


def train_ppo(
    env: Genus2Env,
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
    """NumPy PPO trainer with a 2-layer MLP policy + value head.

    Same architecture as ``modular_form_env.train_ppo``: episode length
    is 1, advantages reduce to ``A = r_scaled - V(s)``.
    """
    rng = np.random.default_rng(seed)
    od = obs_dim()
    n_actions = N_RANK_ACTIONS
    h = int(hidden)

    rng_init = np.random.default_rng(seed + 1)
    W1 = rng_init.standard_normal((h, od)) * (1.0 / math.sqrt(od))
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

                v_err = values - ret_arr  # dL_v / dV
                grad_h_v = v_err[:, None] @ Wv  # (B, h)

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
    "Genus2Env",
    "N_RANK_ACTIONS",
    "REWARD_HIT",
    "REWARD_MISS",
    "obs_dim",
    "register_with_gymnasium",
    "train_random",
    "train_reinforce",
    "train_ppo",
]
