"""prometheus_math.bsd_rich_env — BSDRankEnv variant on rich features.

Sidecar to ``bsd_rank_env.py`` (which is left untouched as a regression
anchor for the raw-feature baseline). The substrate growth invariants
and reward semantics are identical. Only the observation pipeline
changes: the obs vector is now produced by ``bsd_rich_features.
vectorize_rich`` instead of ``[a_p, log_conductor, history]``.

This keeps the linear-vs-MLP comparison from ``bsd_rank_mlp.py``
intact: same env class shape, same trainers, just a different obs.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension, CostModel

from . import _bsd_rich_features
from ._bsd_rich_features import RichBSDEntry
from .bsd_rich_features import vectorize_rich, feature_dim
from .bsd_rank_env import (
    N_RANK_ACTIONS,
    REWARD_HIT,
    REWARD_MISS,
    _IDENTITY_REF,
    _BoxStub,
    _DiscreteStub,
    _EpisodeState,
)


# Number of history features appended after the rich vector.
HISTORY_DIM = 5  # running_acc, last_reward, n_seen, last_pred, last_true


def rich_obs_dim(n_ap: int = 20) -> int:
    return int(feature_dim(n_ap)) + HISTORY_DIM


class BSDRichRankEnv:
    """Same contract as ``BSDRankEnv`` but with a rich-feature obs.

    Each ``reset()`` samples one ``RichBSDEntry`` from the configured
    split. The observation is the concatenation of:

        vectorize_rich(entry, n_ap=20)         -> feature_dim(20) = 66
        history features                       -> 5

    so the total obs dim is ``feature_dim(20) + 5 = 71`` by default.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[RichBSDEntry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        n_total: int = 1000,
        n_ap: int = 20,
        rank0_share: float = 0.5,
        rank1_share: float = 0.4,
        rank2plus_share: float = 0.1,
        corpus_seed: int = 0,
        conductor_max: Optional[int] = None,
        seed: Optional[int] = None,
        kernel_db_path: str = ":memory:",
    ):
        if split not in ("all", "train", "test"):
            raise ValueError(
                f"split must be 'all', 'train', or 'test'; got {split!r}"
            )

        if corpus is None:
            corpus = _bsd_rich_features.load_bsd_rich_corpus(
                n_total=n_total,
                n_ap=n_ap,
                rank0_share=rank0_share,
                rank1_share=rank1_share,
                rank2plus_share=rank2plus_share,
                seed=corpus_seed,
                conductor_max=conductor_max,
            )
        corpus = list(corpus)
        if not corpus:
            raise ValueError("BSDRichRankEnv corpus is empty")

        self._n_ap = int(n_ap)

        if split == "all":
            self._split_corpus: List[RichBSDEntry] = list(corpus)
        else:
            train, test = _bsd_rich_features.split_train_test_rich(
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
        self._current: Optional[RichBSDEntry] = None
        self._step_called = False

        try:
            from gymnasium import spaces  # noqa: F401
            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(rich_obs_dim(n_ap),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(N_RANK_ACTIONS)
        except ImportError:
            self.observation_space = _BoxStub((rich_obs_dim(n_ap),))
            self.action_space = _DiscreteStub(N_RANK_ACTIONS)

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
        self._kernel = SigmaKernel(self._kernel_db_path)
        self._ext = BindEvalExtension(self._kernel)
        self._step_called = False

        idx = self._rng.randrange(len(self._split_corpus))
        self._current = self._split_corpus[idx]

        info = {
            "n_actions": N_RANK_ACTIONS,
            "label": self._current.label,
            "cremona_label": self._current.cremona_label,
            "conductor": self._current.conductor,
            "true_rank": self._current.rank,
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
                "BSDRichRankEnv: step() called twice in one episode"
            )
        a = int(action)
        if a < 0 or a >= N_RANK_ACTIONS:
            raise ValueError(
                f"action {a} out of range [0, {N_RANK_ACTIONS})"
            )

        cap_b = self._kernel.mint_capability("BindCap")
        binding = self._ext.BIND(
            callable_ref=_IDENTITY_REF,
            cost_model=CostModel(),
            postconditions=[],
            authority_refs=[f"lmfdb:{self._current.label}"],
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
            output_value = a

        true_rank = int(self._current.rank)
        hit = (output_value == true_rank)
        reward = REWARD_HIT if hit else REWARD_MISS

        self._state.n_episodes_seen += 1
        if hit:
            self._state.n_correct += 1
        self._state.last_reward = float(reward)
        self._state.last_pred_rank = a
        self._state.last_true_rank = true_rank

        terminated = True
        truncated = False
        self._step_called = True

        info = {
            "label": self._current.label,
            "cremona_label": self._current.cremona_label,
            "conductor": self._current.conductor,
            "true_rank": true_rank,
            "predicted_rank": a,
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
            except Exception:
                pass
        self._kernel = None
        self._ext = None

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        if self._current is None:
            return np.zeros(rich_obs_dim(self._n_ap), dtype=np.float64)
        rich_vec = vectorize_rich(self._current, n_ap=self._n_ap)
        history = np.array([
            self.running_accuracy(),
            self._state.last_reward / REWARD_HIT,
            float(self._state.n_episodes_seen),
            float(self._state.last_pred_rank),
            float(self._state.last_true_rank),
        ], dtype=np.float64)
        return np.concatenate([rich_vec, history])

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

    def obs_dim(self) -> int:
        return rich_obs_dim(self._n_ap)


# ---------------------------------------------------------------------------
# Rich-feature trainers (mirror bsd_rank_env trainers)
# ---------------------------------------------------------------------------


def train_random_rich(
    env: BSDRichRankEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random rank prediction, rich-feature variant."""
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
        "agent": "random_rich",
        "pred_counts": pred_counts.tolist(),
    }


def train_reinforce_rich(
    env: BSDRichRankEnv,
    n_episodes: int,
    *,
    lr: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.02,
    seed: int = 0,
) -> Dict[str, Any]:
    """Linear REINFORCE on rich features."""
    rng = np.random.default_rng(seed)
    obs_dim = env.obs_dim()
    W = np.zeros((N_RANK_ACTIONS, obs_dim), dtype=np.float64)
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
        "agent": "reinforce_rich",
        "policy_W_final": W,
        "policy_b_final": b,
        "pred_counts": pred_counts.tolist(),
    }


def train_mlp_rich(
    env: BSDRichRankEnv,
    n_episodes: int,
    *,
    lr: float = 1e-3,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    hidden: Sequence[int] = (128, 64),
    seed: int = 0,
    weight_decay: float = 0.0,
) -> Dict[str, Any]:
    """MLP REINFORCE on rich features (sidecar to bsd_rank_mlp.train_mlp_bsd)."""
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError:
        raise RuntimeError(
            "PyTorch is required for the MLP rich backend"
        )

    rng = np.random.default_rng(seed)
    torch.manual_seed(int(seed))
    obs_dim = env.obs_dim()

    layers: List[nn.Module] = []
    prev = obs_dim
    for h in hidden:
        layers.append(nn.Linear(prev, int(h)))
        layers.append(nn.ReLU())
        prev = int(h)
    layers.append(nn.Linear(prev, N_RANK_ACTIONS))
    policy = nn.Sequential(*layers)
    optimizer = torch.optim.Adam(
        policy.parameters(), lr=float(lr), weight_decay=float(weight_decay),
    )

    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    baseline = 0.0
    pred_counts = np.zeros(N_RANK_ACTIONS, dtype=np.int64)

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        obs_t = torch.as_tensor(obs, dtype=torch.float32)
        logits = policy(obs_t)
        log_probs = F.log_softmax(logits, dim=-1)
        probs = torch.exp(log_probs)
        a_t = torch.multinomial(probs, num_samples=1).item()
        a = int(a_t)
        pred_counts[a] += 1
        _, r, _, _, info = env.step(a)
        rewards[t] = float(r)
        if info.get("hit"):
            n_correct += 1

        r_scaled = float(r) * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        log_p_a = log_probs[a]
        entropy = -(probs * log_probs).sum()
        loss = -(advantage * log_p_a + entropy_coef * entropy)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "mlp_rich",
        "policy": policy,
        "pred_counts": pred_counts.tolist(),
        "lr": float(lr),
        "entropy_coef": float(entropy_coef),
        "hidden": tuple(int(h) for h in hidden),
        "obs_dim": int(obs_dim),
    }


# ---------------------------------------------------------------------------
# Held-out test eval helpers (deterministic argmax)
# ---------------------------------------------------------------------------


def evaluate_linear_on_test(
    W: np.ndarray,
    b: np.ndarray,
    test_corpus: Sequence[RichBSDEntry],
    *,
    seed: int = 0,
    n_episodes: Optional[int] = None,
) -> Dict[str, Any]:
    """Deterministic argmax eval of a trained linear policy on test split."""
    env = BSDRichRankEnv(corpus=test_corpus, split="all", seed=seed)
    rng = np.random.default_rng(seed)
    n = len(test_corpus) if n_episodes is None else int(n_episodes)
    rewards = np.zeros(n, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(N_RANK_ACTIONS, dtype=np.int64)
    for t in range(n):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        a = int(np.argmax(logits))
        pred_counts[a] += 1
        _, r, _, _, info = env.step(a)
        rewards[t] = float(r)
        if info.get("hit"):
            n_correct += 1
    env.close()
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n)),
        "n_episodes": int(n),
        "agent": "linear_argmax_eval",
        "pred_counts": pred_counts.tolist(),
    }


def evaluate_mlp_on_test(
    policy,
    test_corpus: Sequence[RichBSDEntry],
    *,
    seed: int = 0,
    n_episodes: Optional[int] = None,
) -> Dict[str, Any]:
    """Deterministic argmax eval of a trained MLP on test split."""
    import torch
    env = BSDRichRankEnv(corpus=test_corpus, split="all", seed=seed)
    rng = np.random.default_rng(seed)
    n = len(test_corpus) if n_episodes is None else int(n_episodes)
    rewards = np.zeros(n, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(N_RANK_ACTIONS, dtype=np.int64)
    policy.eval()
    with torch.no_grad():
        for t in range(n):
            obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
            obs_t = torch.as_tensor(obs, dtype=torch.float32)
            logits = policy(obs_t)
            a = int(torch.argmax(logits).item())
            pred_counts[a] += 1
            _, r, _, _, info = env.step(a)
            rewards[t] = float(r)
            if info.get("hit"):
                n_correct += 1
    env.close()
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n)),
        "n_episodes": int(n),
        "agent": "mlp_argmax_eval",
        "pred_counts": pred_counts.tolist(),
    }


__all__ = [
    "BSDRichRankEnv",
    "rich_obs_dim",
    "HISTORY_DIM",
    "train_random_rich",
    "train_reinforce_rich",
    "train_mlp_rich",
    "evaluate_linear_on_test",
    "evaluate_mlp_on_test",
]
