"""prometheus_math.discovery_env — generative reciprocal-polynomial RL env.

The discovery-grade successor to ``sigma_env.py``'s 13-arm bandit. Where
``SigmaMathEnv`` exposes a hand-curated action table (9 of 13 entries
are jackpots), this env exposes a **combinatorial action space** —
agents build a reciprocal polynomial coefficient by coefficient and
the reward is a function of the resulting Mahler measure.

Key differences from ``SigmaMathEnv``:

1. **Generative actions.**  Each step picks one coefficient from a
   small integer set ``{-3, -2, -1, 0, 1, 2, 3}``.  Episode length is
   ``ceil(degree/2) + 1`` (palindromic constraint enforced — agent
   only picks the first half; the second half is mirrored).  For
   degree 10 the trajectory space is ``7^6 ≈ 117K``.
2. **Sparse, falsifiable reward.**  ``+100`` only for ``1.001 < M <
   1.18`` — *strict* sub-Lehmer territory.  Cyclotomic polynomials
   (M = 1 exactly) earn ``0``, not the jackpot.  This is the discovery
   threshold: if the agent ever earns ``+100``, the polynomial is a
   candidate sub-Lehmer specimen and gets logged for hand-verification.
3. **Substrate-conditioned observations.**  The obs vector exposes
   the partial polynomial under construction, the best M found so far
   in the episode, the running best across episodes, and the
   substrate's binding/evaluation counts.  An agent's policy can
   condition on what's already been built, not just on a stationary
   summary.
4. **BIND/EVAL through the substrate.**  Every M-computation runs as
   an EVAL through the kernel, producing a substrate symbol with cost
   trace and provenance.  This is the architecture the pivot doc
   commits to — substrate-as-action-layer, not substrate-as-bystander.
5. **Cross-check against Mossinghoff.**  Any polynomial that earns
   the jackpot reward is auto-checked against the
   ``prometheus_math.databases.mahler`` snapshot (178 known small-M
   entries).  If it's a known Salem, the env logs the match; if it's
   *not* known, the env logs ``DISCOVERY_CANDIDATE`` and the run is
   flagged for manual verification (almost certainly numerical
   artifact, but the discipline is to record and check).

This env is the eight-week pivot's discovery test (per
``pivot/techne.md`` §4.4).  Random-baseline expected reward is
near-zero on the strict sub-Lehmer threshold; if REINFORCE achieves
mean reward above ``0`` consistently, the env's reward signal is
genuinely sparse-but-learnable and the loop is discovery-grade.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    BudgetExceeded,
    CostModel,
)


# ---------------------------------------------------------------------------
# Action set
# ---------------------------------------------------------------------------


# Small integer alphabet for coefficients.  Wider alphabets blow up the
# trajectory space cubically without proportional payoff — almost all
# small-M polynomials in Mossinghoff have coefficients in {-3..3}.
COEFFICIENT_CHOICES: Tuple[int, ...] = (-3, -2, -1, 0, 1, 2, 3)
N_COEFFICIENT_ACTIONS = len(COEFFICIENT_CHOICES)


# ---------------------------------------------------------------------------
# Episode result
# ---------------------------------------------------------------------------


@dataclass
class EpisodeRecord:
    """A complete episode's outcome.  Useful for downstream auditing."""

    coeffs: List[int]
    mahler_measure: float
    reward: float
    is_reciprocal: bool
    is_known_in_mossinghoff: Optional[bool]
    discovery_flag: Optional[str]


# ---------------------------------------------------------------------------
# Reward shape
# ---------------------------------------------------------------------------


def _compute_reward_shaped(m_value: float) -> Tuple[float, str]:
    """Continuous reward variant: smooth gradient toward low M.

    Reward = max(0, 50 * (5 - M) / 4) for M in [1.001, 5];
    plus a +50 bonus if M in (1.001, 1.18) (sub-Lehmer);
    cyclotomics (M ≈ 1) still score 0 (sparse anchor).

    The continuous gradient gives the agent a learning signal across
    the entire M-range, not just at band boundaries. This addresses
    the local-optimum trap that the step-reward shape produces.
    """
    if not math.isfinite(m_value):
        return 0.0, "non_finite"
    if m_value < 1.0 - 1e-9:
        return 0.0, "numerical_artifact"
    if m_value < 1.001:
        return 0.0, "cyclotomic"  # sparse anchor stays
    if m_value < 1.18:
        # Sub-Lehmer: large bonus on top of continuous gradient.
        return 50.0 + 50.0 * (5.0 - m_value) / 4.0, "sub_lehmer"
    if m_value < 5.0:
        return 50.0 * (5.0 - m_value) / 4.0, "shaped_continuous"
    return 0.0, "large_m"


def _compute_reward(m_value: float) -> Tuple[float, str]:
    """Return (reward, label) for a Mahler measure.

    Reward shape (sparse — cyclotomics drop out, sub-Lehmer pays):
        +100  iff 1.001 < M < 1.18    (sub-Lehmer; would be a real find)
         +20  iff 1.18  <= M < 1.5    (Salem cluster — real but known)
         +5   iff 1.5   <= M < 2.0    (low-M but unremarkable)
         +1   iff 2.0   <= M < 5.0    (functional but high)
          0   otherwise (cyclotomic with M ≈ 1; or M >= 5)
    """
    if not math.isfinite(m_value):
        return 0.0, "non_finite"
    if m_value < 1.0 - 1e-9:
        # Numerical artifact — should not happen for a non-zero integer
        # poly.  Treat as zero; do not credit.
        return 0.0, "numerical_artifact"
    if 1.001 < m_value < 1.18:
        return 100.0, "sub_lehmer"
    if 1.18 <= m_value < 1.5:
        return 20.0, "salem_cluster"
    if 1.5 <= m_value < 2.0:
        return 5.0, "low_m"
    if 2.0 <= m_value < 5.0:
        return 1.0, "functional"
    return 0.0, "cyclotomic_or_large"


# ---------------------------------------------------------------------------
# Polynomial construction
# ---------------------------------------------------------------------------


def _palindromic_from_half(half: List[int], degree: int) -> List[int]:
    """Mirror a half-coefficient list into a palindromic polynomial.

    The agent picks the first ``ceil(degree/2)+1`` coefficients
    ``a_0, a_1, ..., a_k`` where ``k = ceil(degree/2)``; the rest are
    mirrored to ``a_{degree-i} = a_i``.  Even-degree case has a single
    central coefficient; odd-degree case has two adjacent middle
    coefficients that must be equal — we enforce this by mirroring.
    """
    if degree < 2:
        raise ValueError(f"degree must be >= 2; got {degree}")
    n = degree + 1  # coefficient count
    out = [0] * n
    half_len = (degree // 2) + 1
    if len(half) < half_len:
        raise ValueError(
            f"need {half_len} half-coeffs for degree {degree}; got {len(half)}"
        )
    for i in range(half_len):
        out[i] = half[i]
        out[degree - i] = half[i]
    return out


def _is_reciprocal(coeffs: List[int]) -> bool:
    """Palindromic check.  Trivially true for our generator output, but
    kept for downstream auditing (a future env variant might allow
    non-palindromic actions)."""
    n = len(coeffs)
    return all(coeffs[i] == coeffs[n - 1 - i] for i in range(n // 2))


# ---------------------------------------------------------------------------
# Mossinghoff cross-check
# ---------------------------------------------------------------------------


def _check_mossinghoff(
    coeffs: List[int], m_value: float
) -> Tuple[Optional[bool], Optional[str]]:
    """Return (is_known, label).  ``is_known=True`` if the polynomial
    matches a Mossinghoff entry by Mahler measure within 1e-5; ``False``
    if it doesn't; ``None`` if the snapshot is unavailable."""
    try:
        from prometheus_math.databases import mahler as _mahler_db
    except Exception:
        return None, None
    # Mossinghoff snapshot is keyed by M-value; do a tolerance check.
    snapshot = getattr(_mahler_db, "MAHLER_TABLE", None)
    if snapshot is None:
        return None, None
    for entry in snapshot:
        try:
            entry_m = float(entry.get("mahler_measure", float("inf")))
        except (TypeError, ValueError):
            continue
        if abs(entry_m - m_value) < 1e-5:
            return True, entry.get("label") or entry.get("name") or "unknown"
    return False, None


# ---------------------------------------------------------------------------
# The env
# ---------------------------------------------------------------------------


class DiscoveryEnv:
    """Generative reciprocal-polynomial discovery env.

    Gymnasium-compatible (same step/reset/spaces interface as
    ``SigmaMathEnv``); does not hard-depend on gymnasium.

    Action space: ``Discrete(7)`` per step (coefficient from
    ``COEFFICIENT_CHOICES``).
    Observation space: ``Box(shape=(7 + degree,))`` —
        [step, half_len, best_m_in_episode, best_m_overall,
         n_evaluations, last_reward, episode_done_flag,
         partial_coeffs (degree+1 entries, padded with 0)].
    Episode: ``ceil(degree/2) + 1`` build-steps; the final step
    triggers M-evaluation, reward, and termination.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        degree: int = 10,
        max_episodes: int = 1000,
        kernel_db_path: str = ":memory:",
        cost_seconds: float = 0.5,
        seed: Optional[int] = None,
        log_discoveries: bool = True,
        reward_shape: str = "step",
    ):
        if reward_shape not in ("step", "shaped"):
            raise ValueError(
                f"reward_shape must be 'step' or 'shaped'; got {reward_shape!r}"
            )
        self._reward_fn = (
            _compute_reward_shaped if reward_shape == "shaped" else _compute_reward
        )
        self.reward_shape = reward_shape
        if degree < 2:
            raise ValueError(f"degree must be >= 2; got {degree}")
        self.degree = int(degree)
        self.half_len = (self.degree // 2) + 1
        self.max_episodes = int(max_episodes)
        self.kernel_db_path = str(kernel_db_path)
        self.cost_seconds = float(cost_seconds)
        self.seed = seed
        self.log_discoveries = bool(log_discoveries)

        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._mm_binding_name: Optional[str] = None
        self._mm_binding_version: Optional[int] = None

        self._partial: List[int] = []  # half-coeffs picked so far
        self._step_count = 0
        self._episode_count = 0
        self._n_evals = 0
        self._best_m_episode: float = float("inf")
        self._best_m_overall: float = float("inf")
        self._last_reward: float = 0.0
        self._discoveries: List[EpisodeRecord] = []
        self._known_salem_hits: int = 0
        self._sub_lehmer_candidates: List[EpisodeRecord] = []

        # Spaces (Gymnasium if available, stubs otherwise).
        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9,
                high=1e9,
                shape=(7 + self.degree,),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(N_COEFFICIENT_ACTIONS)
            self._gym_spaces = spaces
        except ImportError:
            from .sigma_env import _BoxStub, _DiscreteStub  # local fallback

            self.observation_space = _BoxStub((7 + self.degree,))
            self.action_space = _DiscreteStub(N_COEFFICIENT_ACTIONS)
            self._gym_spaces = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self.seed = int(seed)

        if self._kernel is None:
            self._kernel = SigmaKernel(self.kernel_db_path)
            self._ext = BindEvalExtension(self._kernel)
            cap = self._kernel.mint_capability("BindCap")
            binding = self._ext.BIND(
                callable_ref="techne.lib.mahler_measure:mahler_measure",
                cost_model=CostModel(max_seconds=self.cost_seconds),
                postconditions=["M(P) >= 1 for any non-zero integer poly"],
                authority_refs=["Mossinghoff Mahler tables", "Lehmer 1933"],
                cap=cap,
            )
            self._mm_binding_name = binding.symbol.name
            self._mm_binding_version = binding.symbol.version

        self._partial = []
        self._step_count = 0
        self._best_m_episode = float("inf")
        self._last_reward = 0.0

        info = {
            "episode": self._episode_count,
            "degree": self.degree,
            "half_len": self.half_len,
            "n_actions": N_COEFFICIENT_ACTIONS,
        }
        return self._obs(), info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._ext is None:
            raise RuntimeError("env.step() called before env.reset()")
        if action < 0 or action >= N_COEFFICIENT_ACTIONS:
            raise ValueError(
                f"action {action} out of [0, {N_COEFFICIENT_ACTIONS})"
            )

        # Append the chosen coefficient.
        coef = COEFFICIENT_CHOICES[action]
        self._partial.append(coef)
        self._step_count += 1

        info: Dict[str, Any] = {
            "step": self._step_count,
            "chosen_coef": coef,
            "partial": list(self._partial),
        }

        # If the half-polynomial isn't complete yet, return zero reward.
        if len(self._partial) < self.half_len:
            return self._obs(), 0.0, False, False, info

        # Half complete — mirror, evaluate, terminate.
        try:
            full = _palindromic_from_half(self._partial, self.degree)
        except ValueError as e:
            self._last_reward = 0.0
            info["error"] = str(e)
            return self._obs(), 0.0, True, False, info

        # Reject zero polynomials immediately.
        if all(c == 0 for c in full):
            self._last_reward = 0.0
            info["reward_label"] = "zero_polynomial"
            self._episode_count += 1
            return self._obs(), 0.0, True, False, info

        # EVAL through the substrate.
        cap = self._kernel.mint_capability("EvalCap")
        try:
            ev = self._ext.EVAL(
                binding_name=self._mm_binding_name,
                binding_version=self._mm_binding_version,
                args=[full],
                cap=cap,
                eval_version=self._n_evals + 1,
            )
            self._n_evals += 1
        except BudgetExceeded as e:
            self._last_reward = -1.0
            info["error"] = f"budget_exceeded: {e}"
            self._episode_count += 1
            return self._obs(), -1.0, True, False, info

        if not ev.success:
            self._last_reward = 0.0
            info["error"] = ev.error_repr
            self._episode_count += 1
            return self._obs(), 0.0, True, False, info

        # Parse the M-value.
        try:
            m_value = float(ev.output_repr)
        except (TypeError, ValueError):
            m_value = float("inf")

        reward, label = self._reward_fn(m_value)

        # Update episode + global bests.
        if math.isfinite(m_value) and m_value >= 1.0 - 1e-9:
            if m_value < self._best_m_episode:
                self._best_m_episode = m_value
            if m_value < self._best_m_overall:
                self._best_m_overall = m_value

        # Mossinghoff cross-check + discovery flag.
        is_known, mossinghoff_label = _check_mossinghoff(full, m_value)
        discovery_flag: Optional[str] = None
        if label == "sub_lehmer":
            if is_known:
                discovery_flag = f"known_salem:{mossinghoff_label}"
            else:
                discovery_flag = "DISCOVERY_CANDIDATE"
                # Log it loudly — almost certainly numerical artifact,
                # but the discipline is to capture every candidate.
                self._sub_lehmer_candidates.append(
                    EpisodeRecord(
                        coeffs=full,
                        mahler_measure=m_value,
                        reward=reward,
                        is_reciprocal=_is_reciprocal(full),
                        is_known_in_mossinghoff=False,
                        discovery_flag="DISCOVERY_CANDIDATE",
                    )
                )
        elif label == "salem_cluster" and is_known:
            self._known_salem_hits += 1

        record = EpisodeRecord(
            coeffs=full,
            mahler_measure=m_value,
            reward=reward,
            is_reciprocal=True,
            is_known_in_mossinghoff=is_known,
            discovery_flag=discovery_flag,
        )
        if self.log_discoveries and label in ("sub_lehmer", "salem_cluster"):
            self._discoveries.append(record)

        self._last_reward = float(reward)
        self._episode_count += 1
        info.update(
            {
                "coeffs_full": full,
                "mahler_measure": m_value,
                "reward_label": label,
                "discovery_flag": discovery_flag,
                "is_known_in_mossinghoff": is_known,
                "best_m_episode": self._best_m_episode,
                "best_m_overall": self._best_m_overall,
            }
        )
        return self._obs(), float(reward), True, False, info

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        partial_padded = list(self._partial) + [0.0] * (
            self.degree + 1 - len(self._partial)
        )
        # Truncate to exactly degree (matches obs shape (7 + degree,)).
        partial_padded = partial_padded[: self.degree]

        episode_done_flag = 1.0 if len(self._partial) >= self.half_len else 0.0
        best_m_ep = (
            self._best_m_episode if math.isfinite(self._best_m_episode) else -1.0
        )
        best_m_all = (
            self._best_m_overall if math.isfinite(self._best_m_overall) else -1.0
        )

        return np.array(
            [
                float(self._step_count),
                float(self.half_len),
                float(best_m_ep),
                float(best_m_all),
                float(self._n_evals),
                float(self._last_reward),
                float(episode_done_flag),
                *partial_padded,
            ],
            dtype=np.float64,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def discoveries(self) -> List[EpisodeRecord]:
        """Return all rewarded episodes (sub-Lehmer + Salem cluster)."""
        return list(self._discoveries)

    def sub_lehmer_candidates(self) -> List[EpisodeRecord]:
        """Return only sub-Lehmer-candidate episodes that are NOT in the
        Mossinghoff snapshot.  Each one is a hand-verification target."""
        return list(self._sub_lehmer_candidates)

    def known_salem_hits(self) -> int:
        """How many episodes hit a polynomial already in Mossinghoff."""
        return self._known_salem_hits

    def kernel(self) -> SigmaKernel:
        if self._kernel is None:
            raise RuntimeError("env not reset yet")
        return self._kernel

    def close(self) -> None:
        if self._kernel is not None:
            try:
                self._kernel.conn.close()
            except Exception:
                pass
        self._kernel = None
        self._ext = None


__all__ = [
    "DiscoveryEnv",
    "EpisodeRecord",
    "COEFFICIENT_CHOICES",
    "N_COEFFICIENT_ACTIONS",
]
