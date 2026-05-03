"""prometheus_math.bsd_rank_env — Gymnasium-compatible BSD rank-prediction env.

A cross-domain validation env for the discovery substrate. Goal: predict
the Mordell-Weil rank of an elliptic curve over Q, given its Hecke-
eigenvalue (a_p) sequence and basic invariants. LMFDB / Cremona supply
the ground truth, so we can score every prediction immediately.

Per-episode schema
------------------
1. ``reset()`` samples one curve from the configured split (train or
   test) and presents its feature vector + a small running-history
   summary as the observation.
2. The agent picks an action ``a in {0, 1, 2, 3, 4}``: predicted rank.
3. ``step(a)`` BIND/EVAL-s the prediction through the sigma kernel
   (binding name encodes the LMFDB label, EVAL output is the predicted
   rank), then issues reward = +100 iff predicted rank matches the
   curve's ground-truth rank, else 0. Episodes are length-1 (one
   prediction per curve).

The substrate growth is intentional: each step produces exactly one
binding row + one evaluation row in the kernel's tables, mirroring the
``SigmaMathEnv`` invariant. The kernel is *fresh* per-episode so that
multi-episode runs don't accumulate state across curves.

Skip-with-message contract
--------------------------
``BSDRankEnv.__init__`` raises ``RuntimeError`` if the corpus loader
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

from . import _bsd_corpus
from ._bsd_corpus import BSDEntry, DEFAULT_N_AP


# ---------------------------------------------------------------------------
# Action space (rank prediction)
# ---------------------------------------------------------------------------

# We allow predictions in {0, 1, 2, 3, 4}. Cremona's coverage at small
# conductor is essentially all rank<=2; the upper actions exist so an
# ablation on a higher-conductor mirror remains meaningful without
# changing the action space.
N_RANK_ACTIONS = 5

# Reward magnitudes (kept consistent with the rest of the substrate's
# +100 jackpot / 0 floor convention used by SigmaMathEnv).
REWARD_HIT = 100.0
REWARD_MISS = 0.0


# ---------------------------------------------------------------------------
# Observation feature layout
# ---------------------------------------------------------------------------

# obs vector layout:
#   - n_ap a_p values             (default 20)
#   - log10(conductor)            (1)
#   - history features:
#       running accuracy          (1)
#       last reward               (1)
#       n_episodes_seen           (1)
#       last predicted rank       (1)
#       last true rank            (1)
# = n_ap + 6 features
HISTORY_DIM = 6


def _obs_dim(n_ap: int) -> int:
    return int(n_ap) + HISTORY_DIM


# ---------------------------------------------------------------------------
# Helpers: substrate BIND/EVAL plumbing
# ---------------------------------------------------------------------------


def _identity_predictor(rank: int) -> int:
    """Trivial callable bound by the env: receives the predicted rank,
    returns it unchanged. The substrate uses this as the EVAL hook so
    each prediction generates one (binding, evaluation) row pair."""
    return int(rank)


_IDENTITY_REF = "prometheus_math.bsd_rank_env:_identity_predictor"


# ---------------------------------------------------------------------------
# Spec stubs (used when gymnasium is not installed)
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
# Env
# ---------------------------------------------------------------------------


@dataclass
class _EpisodeState:
    """Mutable per-env-instance state across episodes."""

    n_episodes_seen: int = 0
    n_correct: int = 0
    last_reward: float = 0.0
    last_pred_rank: int = -1
    last_true_rank: int = -1


class BSDRankEnv:
    """Gymnasium-compatible env: predict Mordell-Weil rank from a_p.

    The corpus and split are determined at construction time. Each
    ``reset()`` samples a fresh curve from the split (with replacement
    across episodes; without replacement within a single episode is
    irrelevant since episodes are length 1). Each ``step()`` issues a
    BIND/EVAL pair on the sigma kernel and returns the reward.

    Parameters
    ----------
    corpus : list[BSDEntry], optional
        Pre-loaded corpus. If None, ``BSDRankEnv`` calls
        ``_bsd_corpus.load_bsd_corpus(...)`` with the kwargs supplied
        below; if THAT raises, the constructor re-raises so callers
        can ``pytest.skip``.
    split : {"all", "train", "test"}
        Which slice to draw episodes from. "all" = corpus as given.
    train_frac, split_seed : float, int
        Forwarded to ``_bsd_corpus.split_train_test`` when ``split`` is
        not "all".
    n_total, n_ap, rank0_share, rank1_share, rank2plus_share, corpus_seed,
    conductor_max :
        Forwarded to ``_bsd_corpus.load_bsd_corpus`` when ``corpus`` is
        None.
    seed : int
        Seed for episode-level curve sampling. Same seed -> same episode
        sequence.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[Sequence[BSDEntry]] = None,
        split: str = "all",
        *,
        train_frac: float = 0.7,
        split_seed: int = 0,
        n_total: int = 1000,
        n_ap: int = DEFAULT_N_AP,
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
            corpus = _bsd_corpus.load_bsd_corpus(
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
            raise ValueError("BSDRankEnv corpus is empty")

        # Verify a_p length consistency.
        ap_len = len(corpus[0].a_p)
        for e in corpus:
            if len(e.a_p) != ap_len:
                raise ValueError(
                    f"corpus has inconsistent a_p lengths: "
                    f"{ap_len} vs {len(e.a_p)} at label {e.label}"
                )
        self._n_ap = int(ap_len)

        if split == "all":
            self._split_corpus: List[BSDEntry] = list(corpus)
        else:
            train, test = _bsd_corpus.split_train_test(
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
        self._current: Optional[BSDEntry] = None
        self._step_called = False  # one prediction per episode

        # Gymnasium-style spec mirrors. Built optimistically but never
        # required.
        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(_obs_dim(self._n_ap),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(N_RANK_ACTIONS)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((_obs_dim(self._n_ap),))
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

        # Fresh kernel each episode so binding/eval state doesn't bleed
        # across curves. The substrate-growth invariant (1 BIND + 1 EVAL
        # row per step) is therefore measured against this episode's
        # kernel, not the union.
        self._kernel = SigmaKernel(self._kernel_db_path)
        self._ext = BindEvalExtension(self._kernel)
        self._step_called = False

        # Sample a curve uniformly from the split.
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
                "BSDRankEnv: step() called twice in one episode "
                "(episode length is 1; call reset() before next step)"
            )
        a = int(action)
        if a < 0 or a >= N_RANK_ACTIONS:
            raise ValueError(
                f"action {a} out of range [0, {N_RANK_ACTIONS})"
            )

        # BIND/EVAL through substrate. The binding-name carries the LMFDB
        # label so kernel inspection downstream can attribute the
        # evaluation to the right curve. Each episode gets its own kernel,
        # so binding names need only be unique per-episode.
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
            output_value = a  # the identity round-trips to the action

        true_rank = int(self._current.rank)
        hit = (output_value == true_rank)
        reward = REWARD_HIT if hit else REWARD_MISS

        self._state.n_episodes_seen += 1
        if hit:
            self._state.n_correct += 1
        self._state.last_reward = float(reward)
        self._state.last_pred_rank = a
        self._state.last_true_rank = true_rank

        terminated = True   # episode length 1
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
            except Exception:  # pragma: no cover -- best-effort close
                pass
        self._kernel = None
        self._ext = None

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        if self._current is None:
            # Pre-reset zeros (some baselines call _obs after construction).
            return np.zeros(_obs_dim(self._n_ap), dtype=np.float64)
        ap = np.asarray(self._current.a_p, dtype=np.float64)
        log_n = math.log10(max(1, self._current.conductor))
        history = np.array([
            log_n,
            self.running_accuracy(),
            self._state.last_reward / REWARD_HIT,  # in [0, 1]
            float(self._state.n_episodes_seen),
            float(self._state.last_pred_rank),
            float(self._state.last_true_rank),
        ], dtype=np.float64)
        return np.concatenate([ap, history])

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


# ---------------------------------------------------------------------------
# Optional gymnasium registration
# ---------------------------------------------------------------------------


def register_with_gymnasium() -> Optional[str]:
    """Register the env with gymnasium if available; return its id or None."""
    try:
        import gymnasium as gym
    except ImportError:
        return None
    env_id = "prometheus/BSDRank-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.bsd_rank_env:BSDRankEnv",
        )
    except Exception:
        # Already registered or signature changed; treat as soft success.
        pass
    return env_id


# ---------------------------------------------------------------------------
# Lightweight trainers (random + REINFORCE) wired against THIS env's
# observation shape.
# ---------------------------------------------------------------------------


def train_random_bsd(
    env: BSDRankEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Uniform-random rank prediction. Returns standard run summary."""
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


def train_majority_bsd(
    env: BSDRankEnv,
    n_episodes: int,
    seed: int = 0,
) -> Dict[str, Any]:
    """Always predict rank 0 (the modal class) baseline."""
    rng = np.random.default_rng(seed)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    for t in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = 0
        _, r, _, _, info = env.step(a)
        rewards[t] = r
        if info.get("hit"):
            n_correct += 1
    return {
        "rewards": rewards,
        "mean_reward": float(rewards.mean()) if n_episodes > 0 else 0.0,
        "accuracy": float(n_correct / max(1, n_episodes)),
        "n_episodes": int(n_episodes),
        "agent": "majority(0)",
    }


def train_reinforce_bsd(
    env: BSDRankEnv,
    n_episodes: int,
    *,
    lr: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.02,
    seed: int = 0,
) -> Dict[str, Any]:
    """Obs-conditioned REINFORCE (linear policy) for BSDRankEnv.

    Policy: logits = W @ obs + b, then softmax. Episode length is 1, so
    the gradient update is a single-step contextual bandit. The obs
    vector includes the a_p sequence + log-conductor + history; the
    policy can therefore learn a linear discriminator from a_p ->
    rank class.
    """
    rng = np.random.default_rng(seed)
    obs_dim = _obs_dim(env.n_ap())
    W = np.zeros((N_RANK_ACTIONS, obs_dim), dtype=np.float64)
    b = np.zeros(N_RANK_ACTIONS, dtype=np.float64)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    baseline = 0.0
    pred_counts = np.zeros(N_RANK_ACTIONS, dtype=np.int64)

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        # Numeric softmax.
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

        # Policy gradient + entropy bonus.
        grad_a = -probs.copy()
        grad_a[a] += 1.0
        log_p = np.log(probs + 1e-12)
        entropy_grad = probs * (log_p - (probs * log_p).sum())
        total_grad = advantage * grad_a + entropy_coef * (-entropy_grad)
        # outer product update on W, direct on b
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


__all__ = [
    "BSDRankEnv",
    "N_RANK_ACTIONS",
    "REWARD_HIT",
    "REWARD_MISS",
    "register_with_gymnasium",
    "train_random_bsd",
    "train_majority_bsd",
    "train_reinforce_bsd",
]
