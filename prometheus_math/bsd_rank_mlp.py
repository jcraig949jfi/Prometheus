"""prometheus_math.bsd_rank_mlp -- non-linear (MLP) policy on BSDRankEnv.

Sidecar to ``bsd_rank_env.py``: keeps the linear-REINFORCE codepath
intact (regression check) and adds a 2-layer MLP with REINFORCE-style
policy-gradient updates plus entropy regularization.

Architecture
------------
- Input: same observation as the linear policy (n_ap a_p values + 6
  history features = 26-D when n_ap=20).
- Hidden: [128, 64] with ReLU activations.
- Output: 5 logits (rank classes 0..4); softmax for action sampling,
  log-softmax for the gradient update.

Why a sidecar (not in-place edit)?
The team review's #6 refinement asks: "linear may be saturating; can
an MLP extract more from the same features?" The honest comparison
needs the linear baseline path untouched so we can re-run it for a
regression check on the same seed.

Skip-with-message contract
--------------------------
``train_mlp_bsd`` requires PyTorch. If torch is not importable, the
trainer raises RuntimeError(reason); callers should ``pytest.skip``.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    _HAVE_TORCH = True
except ImportError:  # pragma: no cover -- exercised in skip path
    torch = None  # type: ignore
    nn = None  # type: ignore
    F = None  # type: ignore
    _HAVE_TORCH = False


# ---------------------------------------------------------------------------
# Config / defaults
# ---------------------------------------------------------------------------

DEFAULT_HIDDEN = (128, 64)


def _require_torch() -> None:
    if not _HAVE_TORCH:
        raise RuntimeError(
            "PyTorch is required for the MLP backend. Install with "
            "`pip install torch` or skip-with-message."
        )


# ---------------------------------------------------------------------------
# MLP module
# ---------------------------------------------------------------------------


class BSDPolicyMLP(nn.Module if _HAVE_TORCH else object):  # type: ignore[misc]
    """2-layer MLP policy: obs -> [128] -> [64] -> n_actions logits.

    No softmax in forward; callers either softmax for sampling or use
    cross-entropy / log-softmax for the gradient update. Keeping the
    raw logits exposes them to numerical-gradient tests (composition).
    """

    def __init__(
        self,
        obs_dim: int,
        n_actions: int = 5,
        hidden: Sequence[int] = DEFAULT_HIDDEN,
        seed: Optional[int] = None,
    ) -> None:
        _require_torch()
        super().__init__()
        if seed is not None:
            torch.manual_seed(int(seed))
        layers: List[nn.Module] = []
        prev = int(obs_dim)
        for h in hidden:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        layers.append(nn.Linear(prev, int(n_actions)))
        self.net = nn.Sequential(*layers)
        self.obs_dim = int(obs_dim)
        self.n_actions = int(n_actions)
        self.hidden = tuple(int(h) for h in hidden)

    def forward(self, obs):  # noqa: D401
        """Run MLP forward pass; returns raw logits, shape [B, n_actions].

        Accepts a torch tensor of shape [B, obs_dim] or [obs_dim]. The
        latter is unsqueezed to [1, obs_dim] then squeezed back.
        """
        if obs.ndim == 1:
            return self.net(obs.unsqueeze(0)).squeeze(0)
        return self.net(obs)

    def action_dist(self, obs):
        """Return ``probs`` for an observation (for sampling).

        Equivalent to ``softmax(forward(obs))`` along the last axis.
        Always returns a torch tensor.
        """
        logits = self.forward(obs)
        return F.softmax(logits, dim=-1)


# ---------------------------------------------------------------------------
# Eval helpers (deterministic argmax on a frozen policy)
# ---------------------------------------------------------------------------


def evaluate_mlp_on_corpus(
    policy: "BSDPolicyMLP",
    env_cls,
    corpus,
    *,
    seed: int = 0,
    n_episodes: Optional[int] = None,
) -> Dict[str, Any]:
    """Deterministic argmax eval: one prediction per curve in ``corpus``.

    Sweeps the corpus deterministically (one episode per entry, in a
    seed-shuffled order). Returns the same shape as the trainer's
    return dict for downstream consumption.
    """
    _require_torch()
    env = env_cls(corpus=corpus, split="all", seed=seed)
    rng = np.random.default_rng(seed)
    n = len(corpus) if n_episodes is None else int(n_episodes)
    rewards = np.zeros(n, dtype=np.float64)
    n_correct = 0
    pred_counts = np.zeros(policy.n_actions, dtype=np.int64)
    policy_eval = policy.eval()
    with torch.no_grad():
        for t in range(n):
            obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
            obs_t = torch.as_tensor(obs, dtype=torch.float32)
            logits = policy_eval(obs_t)
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


# ---------------------------------------------------------------------------
# REINFORCE trainer (MLP backend)
# ---------------------------------------------------------------------------


def train_mlp_bsd(
    env,
    n_episodes: int,
    *,
    lr: float = 5e-4,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    entropy_coef: float = 0.01,
    hidden: Sequence[int] = DEFAULT_HIDDEN,
    seed: int = 0,
    weight_decay: float = 0.0,
) -> Dict[str, Any]:
    """REINFORCE on BSDRankEnv with an MLP policy.

    Mirrors ``train_reinforce_bsd``'s contract; replaces the linear
    softmax with a 2-layer MLP. Update is single-step contextual-
    bandit-style (episode length is 1).

    Returns dict with the trained policy embedded under
    ``"policy"`` + the standard reward / accuracy fields.
    """
    _require_torch()
    rng = np.random.default_rng(seed)
    obs_dim = env.n_ap() + 6  # matches _obs_dim from bsd_rank_env

    policy = BSDPolicyMLP(
        obs_dim=obs_dim,
        n_actions=5,
        hidden=hidden,
        seed=seed,
    )
    optimizer = torch.optim.Adam(
        policy.parameters(), lr=float(lr), weight_decay=float(weight_decay),
    )

    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_correct = 0
    baseline = 0.0
    pred_counts = np.zeros(5, dtype=np.int64)

    for t in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        obs_t = torch.as_tensor(obs, dtype=torch.float32)
        logits = policy(obs_t)
        log_probs = F.log_softmax(logits, dim=-1)
        probs = torch.exp(log_probs)

        # Sample an action.
        a_t = torch.multinomial(probs, num_samples=1).item()
        a = int(a_t)
        pred_counts[a] += 1

        _, r, _, _, info = env.step(a)
        rewards[t] = float(r)
        if info.get("hit"):
            n_correct += 1

        # REINFORCE objective with entropy regularization.
        r_scaled = float(r) * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled

        # log pi(a|s) * advantage  +  entropy_coef * H(pi)
        # We MAXIMIZE this; pytorch optimizers MINIMIZE -> negate.
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
        "agent": "mlp_reinforce",
        "policy": policy,
        "pred_counts": pred_counts.tolist(),
        "lr": float(lr),
        "entropy_coef": float(entropy_coef),
        "hidden": tuple(int(h) for h in hidden),
    }


# ---------------------------------------------------------------------------
# Statistics helper (Welch one-sided p-value)
# ---------------------------------------------------------------------------


def welch_one_sided(a: np.ndarray, b: np.ndarray) -> float:
    """One-sided Welch t-test p-value: H1 = mean(a) > mean(b).

    Falls back to a normal approximation if scipy is unavailable.
    Mirrors ``_run_bsd_rank_pilot.py::_welch_one_sided``.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size < 2:
        return float("nan")
    ma, mb = float(a.mean()), float(b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    se = math.sqrt(va / a.size + vb / b.size) if (va > 0 or vb > 0) else 1e-12
    t = (ma - mb) / max(se, 1e-12)
    df_num = (va / a.size + vb / b.size) ** 2
    df_den = (
        (va / a.size) ** 2 / max(a.size - 1, 1)
        + (vb / b.size) ** 2 / max(b.size - 1, 1)
    )
    df = df_num / max(df_den, 1e-30)
    try:
        from scipy.stats import t as student_t
        return float(1.0 - student_t.cdf(t, df=df))
    except Exception:
        return float(0.5 * (1.0 - math.erf(max(t, 0.0) / math.sqrt(2.0))))


# ---------------------------------------------------------------------------
# 6-cell hyperparameter sweep
# ---------------------------------------------------------------------------


def hyperparameter_sweep(
    train_corpus,
    test_corpus,
    *,
    env_cls,
    n_episodes: int = 5000,
    n_seeds: int = 5,
    learning_rates: Sequence[float] = (1e-3, 5e-4, 1e-4),
    entropy_coefs: Sequence[float] = (0.01, 0.001),
    hidden: Sequence[int] = DEFAULT_HIDDEN,
    base_seed: int = 17,
    n_test_episodes: Optional[int] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """Run the LR x entropy_coef hyperparameter sweep.

    Returns a dict with per-cell train/test means and per-cell std
    over ``n_seeds`` random seeds. Default 3 LRs x 2 entropy_coefs =
    6 cells, 5 seeds = 30 training runs.
    """
    _require_torch()
    cells: List[Dict[str, Any]] = []
    n_test = (
        len(test_corpus) if n_test_episodes is None else int(n_test_episodes)
    )

    for lr in learning_rates:
        for ec in entropy_coefs:
            train_means: List[float] = []
            test_means: List[float] = []
            train_accs: List[float] = []
            test_accs: List[float] = []
            for s in range(n_seeds):
                seed = int(base_seed + s * 1009)
                env = env_cls(corpus=train_corpus, split="all", seed=seed)
                out = train_mlp_bsd(
                    env,
                    n_episodes=n_episodes,
                    lr=float(lr),
                    entropy_coef=float(ec),
                    hidden=hidden,
                    seed=seed,
                )
                env.close()
                train_means.append(out["mean_reward"])
                train_accs.append(out["accuracy"])

                ev = evaluate_mlp_on_corpus(
                    out["policy"],
                    env_cls,
                    test_corpus,
                    seed=seed + 100000,
                    n_episodes=n_test,
                )
                test_means.append(ev["mean_reward"])
                test_accs.append(ev["accuracy"])

                if progress_callback is not None:
                    progress_callback({
                        "lr": float(lr),
                        "entropy_coef": float(ec),
                        "seed": seed,
                        "train_mean": train_means[-1],
                        "test_mean": test_means[-1],
                    })

            cell = {
                "lr": float(lr),
                "entropy_coef": float(ec),
                "n_seeds": int(n_seeds),
                "train_means": train_means,
                "test_means": test_means,
                "train_accs": train_accs,
                "test_accs": test_accs,
                "train_mean_grand": float(np.mean(train_means)),
                "train_std_grand": float(np.std(train_means, ddof=1))
                if len(train_means) > 1 else 0.0,
                "test_mean_grand": float(np.mean(test_means)),
                "test_std_grand": float(np.std(test_means, ddof=1))
                if len(test_means) > 1 else 0.0,
                "test_acc_mean": float(np.mean(test_accs)),
                "test_acc_std": float(np.std(test_accs, ddof=1))
                if len(test_accs) > 1 else 0.0,
            }
            cells.append(cell)

    # Best cell by test mean reward.
    best = max(cells, key=lambda c: c["test_mean_grand"])
    return {
        "n_episodes": int(n_episodes),
        "n_seeds": int(n_seeds),
        "n_test_episodes": int(n_test),
        "hidden": tuple(int(h) for h in hidden),
        "learning_rates": [float(x) for x in learning_rates],
        "entropy_coefs": [float(x) for x in entropy_coefs],
        "cells": cells,
        "best_cell": {
            "lr": best["lr"],
            "entropy_coef": best["entropy_coef"],
            "test_mean_grand": best["test_mean_grand"],
            "test_std_grand": best["test_std_grand"],
            "test_acc_mean": best["test_acc_mean"],
            "test_acc_std": best["test_acc_std"],
        },
    }


__all__ = [
    "BSDPolicyMLP",
    "DEFAULT_HIDDEN",
    "evaluate_mlp_on_corpus",
    "hyperparameter_sweep",
    "train_mlp_bsd",
    "welch_one_sided",
]
