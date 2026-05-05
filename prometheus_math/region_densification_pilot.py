"""prometheus_math.region_densification_pilot — densify the navigator from 2/8 to 6/8.

The 2026-05-04 native KillVector pilot established margin-mode coverage on
exactly ONE region cell (degree=14, alphabet=±5, reward_shape=step), in
both DiscoveryEnv (V1) and DiscoveryEnvV2 (V2-ga_elitist).  The legacy
gradient archaeology has 6 region cells but is categorical-only — the
navigator currently has 2/8 regions in margin mode.

This driver runs native KillVector pilots on **four additional region
cells** so the navigator can reach 6/8 margin coverage:

    cell A: (degree=10, alphabet_width=5, reward_shape="step")
    cell B: (degree=12, alphabet_width=5, reward_shape="step")
    cell C: (degree=10, alphabet_width=3, reward_shape="step")
    cell D: (degree=14, alphabet_width=3, reward_shape="step")

Each cell × {random_uniform, reinforce_linear, ppo_mlp, ga_elitist_v2} ×
{seed=0, 1, 2} × 1000 episodes = 48,000 total episodes.

Honest framing
--------------
1K episodes per (cell, algorithm, seed) is HALF the budget of the
deg14 ±5 native baseline (which used 2K).  CIs on per-region operator
margins will be wider here.  Don't over-claim: the goal is *coverage*,
not statistical depth.

Region-specific gradient field hypothesis
-----------------------------------------
The deg14 ±5 baseline saw PPO-MLP win in margin space.  If the
kill-space framing is real, then DIFFERENT region cells should have
DIFFERENT operator winners — each region carries its own gradient
field structure (Stream 2's verdict B).  This pilot tests that:

  * verdict A: PPO wins everywhere → operator hierarchy is region-invariant.
  * verdict B: top operator changes across cells → region-specific gradients
    confirmed; navigator's region-conditioning is meaningful.
  * verdict C: margins overlap heavily within each cell → CIs too wide
    to declare a winner; navigator operationally useful but uncertain.

The driver writes ``_region_densification_pilot.json`` with the same
shape as ``_native_kill_vector_pilot.json`` so both files can feed the
same downstream consumers (kill_vector_navigator merges them).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.kill_vector import KillComponent
from prometheus_math.native_kill_vector_pilot import (
    PILOT_COMPONENTS,
    EpisodeKillVector,
    emit_kill_vector_for_episode,
)


# ---------------------------------------------------------------------------
# Region cell specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegionCell:
    """One (degree, alphabet_width, reward_shape) cell to densify."""

    degree: int
    alphabet_width: int
    reward_shape: str

    @property
    def alphabet(self) -> Tuple[int, ...]:
        return tuple(range(-self.alphabet_width, self.alphabet_width + 1))

    @property
    def alphabet_size(self) -> int:
        return 2 * self.alphabet_width + 1

    @property
    def cell_id(self) -> str:
        return f"deg{self.degree}_w{self.alphabet_width}_{self.reward_shape}"

    def region_meta_v1(self) -> Dict[str, Any]:
        return {
            "env": "DiscoveryEnv",
            "degree": self.degree,
            "alphabet_width": self.alphabet_width,
            "alphabet_size": self.alphabet_size,
            "reward_shape": self.reward_shape,
        }

    def region_meta_v2(self) -> Dict[str, Any]:
        return {
            "env": "DiscoveryEnvV2",
            "degree": self.degree,
            "alphabet_width": self.alphabet_width,
            "alphabet_size": self.alphabet_size,
            "reward_shape": self.reward_shape,
        }


DEFAULT_REGION_CELLS: Tuple[RegionCell, ...] = (
    RegionCell(degree=10, alphabet_width=5, reward_shape="step"),
    RegionCell(degree=12, alphabet_width=5, reward_shape="step"),
    RegionCell(degree=10, alphabet_width=3, reward_shape="step"),
    RegionCell(degree=14, alphabet_width=3, reward_shape="step"),
)


# ---------------------------------------------------------------------------
# Parameterized algorithm runners
# ---------------------------------------------------------------------------


def _run_random_uniform_cell(
    cell: RegionCell, n_episodes: int, seed: int
) -> List[EpisodeKillVector]:
    """Uniform-random sampler for a parameterized region cell."""
    env = DiscoveryEnv(
        degree=cell.degree,
        reward_shape=cell.reward_shape,
        coefficient_choices=cell.alphabet,
        seed=seed,
        log_discoveries=False,
    )
    rng = np.random.default_rng(seed)
    region_meta = cell.region_meta_v1()
    operator_class = f"random_uniform@seed={seed}"

    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", cell.alphabet_size))

    out: List[EpisodeKillVector] = []
    pipeline_len_before = 0
    for ep in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        last_r = 0.0
        while not terminated:
            a = int(rng.integers(0, n_actions))
            _, last_r, terminated, _, last_info = env.step(a)

        coeffs = last_info.get("coeffs_full") or [0] * (env.degree + 1)
        m_value = last_info.get("mahler_measure", float("inf"))
        reward_label = str(last_info.get("reward_label") or "unknown")
        is_known = last_info.get("is_known_in_mossinghoff")

        pipeline_records = env.pipeline_records()
        new_pipeline_record = None
        if len(pipeline_records) > pipeline_len_before:
            new_pipeline_record = pipeline_records[-1]
            pipeline_len_before = len(pipeline_records)

        kv = emit_kill_vector_for_episode(
            coeffs=coeffs,
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            operator_class=operator_class,
            region_meta=region_meta,
            episode_idx=ep,
            pipeline_record=new_pipeline_record,
        )
        terminal_state: Optional[str] = (
            new_pipeline_record.terminal_state
            if new_pipeline_record is not None else None
        )
        out.append(EpisodeKillVector(
            algorithm="random_uniform",
            seed=seed,
            episode_idx=ep,
            coeffs=list(coeffs),
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            reward=float(last_r),
            reward_label=reward_label,
            is_known_in_mossinghoff=is_known,
            pipeline_terminal_state=terminal_state,
            legacy_kill_pattern=kv.to_legacy_kill_path(),
            kill_vector_dict=kv.to_dict(),
        ))
    try:
        env.close()
    except Exception:
        pass
    return out


def _run_reinforce_cell(
    cell: RegionCell, n_episodes: int, seed: int
) -> List[EpisodeKillVector]:
    """REINFORCE-linear contextual policy for a parameterized region cell."""
    env = DiscoveryEnv(
        degree=cell.degree,
        reward_shape=cell.reward_shape,
        coefficient_choices=cell.alphabet,
        seed=seed,
        log_discoveries=False,
    )
    rng = np.random.default_rng(seed)
    region_meta = cell.region_meta_v1()
    operator_class = f"reinforce_linear@seed={seed}"

    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions", cell.alphabet_size))
    half_len = int(info0.get("half_len", env.half_len))
    degree = int(info0.get("degree", env.degree))
    obs_dim = 7 + degree

    W = np.zeros((half_len, n_actions, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, n_actions), dtype=np.float64)
    baseline = 0.0
    lr = 0.05
    entropy_coef = 0.05
    reward_scale = 1.0 / 100.0
    baseline_decay = 0.95

    out: List[EpisodeKillVector] = []
    pipeline_len_before = 0
    for ep in range(n_episodes):
        obs, _ = env.reset()
        actions: List[int] = []
        observations: List[np.ndarray] = []
        cum_reward = 0.0
        terminated = False
        step_idx = 0
        last_info: Dict[str, Any] = {}
        last_r = 0.0
        while not terminated:
            l = W[step_idx] @ obs + b[step_idx]
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            a = int(rng.choice(len(probs), p=probs))
            actions.append(a)
            observations.append(obs.copy())
            obs, last_r, terminated, _, last_info = env.step(a)
            cum_reward += last_r
            step_idx += 1

        # Update policy
        r_scaled = cum_reward * reward_scale
        advantage = r_scaled - baseline
        baseline = baseline_decay * baseline + (1.0 - baseline_decay) * r_scaled
        for s_idx, (a, o) in enumerate(zip(actions, observations)):
            l = W[s_idx] @ o + b[s_idx]
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            grad_a = -probs.copy()
            grad_a[a] += 1.0
            log_p = np.log(probs + 1e-12)
            entropy_grad = probs * (log_p - (probs * log_p).sum())
            total_grad = advantage * grad_a + entropy_coef * (-entropy_grad)
            W[s_idx] += lr * np.outer(total_grad, o)
            b[s_idx] += lr * total_grad

        coeffs = last_info.get("coeffs_full") or [0] * (env.degree + 1)
        m_value = last_info.get("mahler_measure", float("inf"))
        reward_label = str(last_info.get("reward_label") or "unknown")
        is_known = last_info.get("is_known_in_mossinghoff")

        pipeline_records = env.pipeline_records()
        new_pipeline_record = None
        if len(pipeline_records) > pipeline_len_before:
            new_pipeline_record = pipeline_records[-1]
            pipeline_len_before = len(pipeline_records)

        kv = emit_kill_vector_for_episode(
            coeffs=coeffs,
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            operator_class=operator_class,
            region_meta=region_meta,
            episode_idx=ep,
            pipeline_record=new_pipeline_record,
        )
        terminal_state = (
            new_pipeline_record.terminal_state
            if new_pipeline_record is not None else None
        )
        out.append(EpisodeKillVector(
            algorithm="reinforce_linear",
            seed=seed,
            episode_idx=ep,
            coeffs=list(coeffs),
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            reward=float(last_r),
            reward_label=reward_label,
            is_known_in_mossinghoff=is_known,
            pipeline_terminal_state=terminal_state,
            legacy_kill_pattern=kv.to_legacy_kill_path(),
            kill_vector_dict=kv.to_dict(),
        ))
    try:
        env.close()
    except Exception:
        pass
    return out


def _run_ppo_cell(
    cell: RegionCell, n_episodes: int, seed: int
) -> List[EpisodeKillVector]:
    """PPO-MLP via stable_baselines3 for a parameterized region cell."""
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import BaseCallback
        from stable_baselines3.common.vec_env import DummyVecEnv
    except ImportError:
        return []

    env = DiscoveryEnv(
        degree=cell.degree,
        reward_shape=cell.reward_shape,
        coefficient_choices=cell.alphabet,
        seed=seed,
        log_discoveries=False,
    )
    region_meta = cell.region_meta_v1()
    operator_class = f"ppo_mlp@seed={seed}"
    half_len = int(getattr(env, "half_len", 8))
    n_steps_rollout = max(64, 4 * half_len)
    n_steps_rollout = ((n_steps_rollout + 63) // 64) * 64

    out: List[EpisodeKillVector] = []
    pipeline_len_holder = {"value": 0}
    episodes_completed = {"value": 0}

    try:
        import gymnasium as gym
        gym_base = gym.Env
    except ImportError:
        gym_base = object  # type: ignore[assignment]

    class _Wrapper(gym_base):  # type: ignore[misc, valid-type]
        metadata = {"render_modes": []}

        def __init__(self, base, n_max):
            self._base = base
            self.observation_space = base.observation_space
            self.action_space = base.action_space
            self.spec = None
            self.render_mode = None
            self._n_max = n_max
            self._stop = False

        def reset(self, *, seed=None, options=None):
            obs, info = self._base.reset(seed=seed)
            return np.asarray(obs, dtype=np.float32), info

        def step(self, action):
            obs, r, term, trunc, info = self._base.step(int(action))
            obs = np.asarray(obs, dtype=np.float32)
            if (term or trunc) and not self._stop:
                ep_idx = episodes_completed["value"]
                coeffs = info.get("coeffs_full") or [0] * (self._base.degree + 1)
                m_value = info.get("mahler_measure", float("inf"))
                reward_label = str(info.get("reward_label") or "unknown")
                is_known = info.get("is_known_in_mossinghoff")

                pipeline_records = self._base.pipeline_records()
                new_pipeline_record = None
                if len(pipeline_records) > pipeline_len_holder["value"]:
                    new_pipeline_record = pipeline_records[-1]
                    pipeline_len_holder["value"] = len(pipeline_records)

                kv = emit_kill_vector_for_episode(
                    coeffs=coeffs,
                    mahler_measure=float(m_value) if m_value is not None else float("nan"),
                    operator_class=operator_class,
                    region_meta=region_meta,
                    episode_idx=ep_idx,
                    pipeline_record=new_pipeline_record,
                )
                terminal_state = (
                    new_pipeline_record.terminal_state
                    if new_pipeline_record is not None else None
                )
                out.append(EpisodeKillVector(
                    algorithm="ppo_mlp",
                    seed=seed,
                    episode_idx=ep_idx,
                    coeffs=list(coeffs),
                    mahler_measure=float(m_value) if m_value is not None else float("nan"),
                    reward=float(r),
                    reward_label=reward_label,
                    is_known_in_mossinghoff=is_known,
                    pipeline_terminal_state=terminal_state,
                    legacy_kill_pattern=kv.to_legacy_kill_path(),
                    kill_vector_dict=kv.to_dict(),
                ))
                episodes_completed["value"] += 1
                if episodes_completed["value"] >= self._n_max:
                    self._stop = True
            return obs, float(r), bool(term), bool(trunc), info

        def close(self):
            return self._base.close()

        def render(self):
            return None

    def _make():
        return _Wrapper(env, n_episodes)

    vec = DummyVecEnv([_make])

    model = PPO(
        "MlpPolicy",
        vec,
        seed=int(seed),
        n_steps=n_steps_rollout,
        verbose=0,
        device="cpu",
    )

    class _StopAfterN(BaseCallback):
        def __init__(self, target):
            super().__init__()
            self._target = target

        def _on_step(self) -> bool:
            return episodes_completed["value"] < self._target

    total_timesteps = int(n_episodes * half_len + n_steps_rollout * 2)
    model.learn(
        total_timesteps=total_timesteps,
        callback=_StopAfterN(n_episodes),
        progress_bar=False,
    )
    try:
        env.close()
    except Exception:
        pass
    return out


def _run_ga_elitist_cell(
    cell: RegionCell, n_episodes: int, seed: int
) -> List[EpisodeKillVector]:
    """V2 GA_elitist for a parameterized region cell.

    Note: DiscoveryEnvV2 does not take a reward_shape kwarg — the V2
    reward path is fixed by selection_strategy.  We tag the region_meta
    with cell.reward_shape so the navigator's region_id is consistent.
    """
    from prometheus_math.discovery_env_v2 import DiscoveryEnvV2

    env = DiscoveryEnvV2(
        degree=cell.degree,
        coefficient_choices=cell.alphabet,
        selection_strategy="elitist",
        enable_pipeline=True,
        seed=seed,
        population_size=8,
        n_mutations_per_episode=12,
    )
    rng = np.random.default_rng(seed)
    region_meta = cell.region_meta_v2()
    operator_class = f"ga_elitist_v2@seed={seed}"

    env.reset(seed=seed)
    out: List[EpisodeKillVector] = []
    pipeline_len_before = 0
    for ep in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        last_r = 0.0
        while not terminated:
            a = int(rng.integers(0, env.n_actions))
            _, last_r, terminated, _, last_info = env.step(a)

        coeffs = last_info.get("elite_coeffs") or last_info.get("coeffs_full")
        if coeffs is None:
            coeffs = [0] * (env.degree + 1)
        m_value = last_info.get("elite_m") or last_info.get("mahler_measure", float("inf"))
        reward_label = str(last_info.get("reward_label") or "v2_episode")
        is_known = last_info.get("is_known_in_mossinghoff")

        pipeline_records = env._pipeline_records
        new_pipeline_record = None
        if len(pipeline_records) > pipeline_len_before:
            new_pipeline_record = pipeline_records[-1]
            pipeline_len_before = len(pipeline_records)

        kv = emit_kill_vector_for_episode(
            coeffs=coeffs,
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            operator_class=operator_class,
            region_meta=region_meta,
            episode_idx=ep,
            pipeline_record=new_pipeline_record,
        )
        terminal_state = (
            new_pipeline_record.terminal_state
            if new_pipeline_record is not None else None
        )
        out.append(EpisodeKillVector(
            algorithm="ga_elitist_v2",
            seed=seed,
            episode_idx=ep,
            coeffs=list(coeffs),
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            reward=float(last_r),
            reward_label=reward_label,
            is_known_in_mossinghoff=is_known,
            pipeline_terminal_state=terminal_state,
            legacy_kill_pattern=kv.to_legacy_kill_path(),
            kill_vector_dict=kv.to_dict(),
        ))
    try:
        env.close()
    except Exception:
        pass
    return out


CELL_ALGORITHM_RUNNERS: Dict[str, Callable[
    [RegionCell, int, int], List[EpisodeKillVector]
]] = {
    "random_uniform": _run_random_uniform_cell,
    "reinforce_linear": _run_reinforce_cell,
    "ppo_mlp": _run_ppo_cell,
    "ga_elitist_v2": _run_ga_elitist_cell,
}


# ---------------------------------------------------------------------------
# Pilot orchestrator
# ---------------------------------------------------------------------------


def run_densification(
    cells: Sequence[RegionCell] = DEFAULT_REGION_CELLS,
    n_episodes_per_cell: int = 1000,
    seeds: Tuple[int, ...] = (0, 1, 2),
    algorithms: Tuple[str, ...] = (
        "random_uniform", "reinforce_linear", "ppo_mlp", "ga_elitist_v2",
    ),
    *,
    progress: bool = True,
) -> Dict[str, Any]:
    """Run native KillVector pilots on multiple region cells.

    Returns a dict with the same shape as ``run_pilot`` from
    ``native_kill_vector_pilot`` so the navigator can consume both:

      * meta: setup
      * episodes: list[EpisodeKillVector.to_dict()]
      * cell_summary: {(cell_id, algo, seed): {n, n_pipeline_routed, ...}}
      * elapsed_s: total wall time
    """
    t_global = time.perf_counter()
    all_episodes: List[EpisodeKillVector] = []
    cell_summary: Dict[str, Dict[str, Any]] = {}
    skipped: List[str] = []

    for cell in cells:
        for algo in algorithms:
            if algo not in CELL_ALGORITHM_RUNNERS:
                raise ValueError(f"unknown algorithm {algo!r}")
            runner = CELL_ALGORITHM_RUNNERS[algo]
            for s in seeds:
                t0 = time.perf_counter()
                key = f"{cell.cell_id}|{algo}@seed={s}"
                if progress:
                    print(
                        f"[densify] {key} (target={n_episodes_per_cell} eps)...",
                        flush=True,
                    )
                try:
                    eps = runner(cell, n_episodes_per_cell, int(s))
                except Exception as e:
                    if progress:
                        print(
                            f"  ERROR in {key}: {type(e).__name__}: {e!r}",
                            flush=True,
                        )
                    skipped.append(f"{key}: {type(e).__name__}")
                    eps = []
                elapsed = time.perf_counter() - t0
                n_pipeline = sum(
                    1 for e in eps if e.pipeline_terminal_state is not None
                )
                cell_summary[key] = {
                    "cell_id": cell.cell_id,
                    "algorithm": algo,
                    "seed": int(s),
                    "n_episodes": len(eps),
                    "n_pipeline_routed": n_pipeline,
                    "elapsed_s": elapsed,
                    "skipped": len(eps) == 0 and n_episodes_per_cell > 0,
                }
                all_episodes.extend(eps)
                if progress:
                    print(
                        f"  -> {len(eps)} eps, {n_pipeline} pipeline-routed,"
                        f" {elapsed:.1f}s ({len(eps)/max(elapsed,1e-9):.1f} eps/s)",
                        flush=True,
                    )

    elapsed = time.perf_counter() - t_global
    return {
        "meta": {
            "n_episodes_per_cell": int(n_episodes_per_cell),
            "seeds": list(seeds),
            "algorithms": list(algorithms),
            "cells": [
                {
                    "cell_id": c.cell_id,
                    "degree": c.degree,
                    "alphabet_width": c.alphabet_width,
                    "alphabet_size": c.alphabet_size,
                    "reward_shape": c.reward_shape,
                }
                for c in cells
            ],
            "pilot_components": list(PILOT_COMPONENTS),
        },
        "episodes": [e.to_dict() for e in all_episodes],
        "cell_summary": cell_summary,
        "skipped": skipped,
        "elapsed_s": float(elapsed),
        "total_episodes": len(all_episodes),
    }


# ---------------------------------------------------------------------------
# Per-region operator margin analysis
# ---------------------------------------------------------------------------


def per_region_operator_margins(
    pilot_result: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """For each (cell × env) region, compute E[||k|| | operator] using
    the unit-aware squashed magnitude.

    Returns ``{region_id: {operator: {n, mean, std, ci_low, ci_high}}}``.
    Lower mean = better (closer to survival band).
    """
    from collections import defaultdict
    from prometheus_math.kill_vector import KillVector
    from prometheus_math.kill_vector_navigator import _bootstrap_mean_ci

    # bucket: (region_id, operator) -> list of magnitudes
    buckets: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    region_meta_seen: Dict[str, Dict[str, Any]] = {}

    for ep in pilot_result.get("episodes", []):
        kv_dict = ep.get("kill_vector")
        if not isinstance(kv_dict, dict):
            continue
        try:
            kv = KillVector.from_dict(kv_dict)
        except Exception:
            continue
        meta = dict(kv.region_meta or {})
        env = meta.get("env", "unknown")
        deg = meta.get("degree", "?")
        width = meta.get("alphabet_width", "?")
        shape = meta.get("reward_shape", "step")
        region_id = f"{env}|deg{deg}|w{width}|{shape}"
        op = ep.get("algorithm") or "_unknown"
        buckets[(region_id, op)].append(kv.magnitude(unit_aware=True))
        if region_id not in region_meta_seen:
            region_meta_seen[region_id] = {
                "env": env, "degree": deg, "alphabet_width": width,
                "reward_shape": shape,
            }

    out: Dict[str, Dict[str, Any]] = {}
    import random as _random
    for (region_id, op), samples in buckets.items():
        rng = _random.Random(0)
        mean, lo, hi = _bootstrap_mean_ci(samples, resamples=200, rng=rng)
        std = float(np.std(samples)) if samples else 0.0
        out.setdefault(region_id, {
            "region_meta": region_meta_seen.get(region_id, {}),
            "operators": {},
        })
        out[region_id]["operators"][op] = {
            "n_episodes": len(samples),
            "mean_magnitude": mean,
            "std_magnitude": std,
            "ci_low": lo,
            "ci_high": hi,
        }
    # Add per-region top operator (lowest mean magnitude).
    for region_id, info in out.items():
        ops = info["operators"]
        if not ops:
            info["top_operator"] = None
            info["top_mean"] = None
            continue
        ranked = sorted(ops.items(), key=lambda kv: kv[1]["mean_magnitude"])
        info["top_operator"] = ranked[0][0]
        info["top_mean"] = ranked[0][1]["mean_magnitude"]
        info["ranking"] = [op for op, _ in ranked]
    return out


def compare_with_baseline(
    densification_margins: Dict[str, Dict[str, Any]],
    baseline_pilot_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare per-region top operator vs the deg14 ±5 step native baseline.

    Loads the existing ``_native_kill_vector_pilot.json`` if present and
    computes its top operator per region.  Reports whether the same
    operator wins everywhere (verdict A) or whether different cells
    have different winners (verdict B), or whether margins overlap so
    much per cell that no clear winner emerges (verdict C).
    """
    if baseline_pilot_path is None:
        baseline_pilot_path = (
            Path(__file__).parent / "_native_kill_vector_pilot.json"
        )
    baseline_pilot_path = Path(baseline_pilot_path)
    baseline_top: Dict[str, str] = {}
    if baseline_pilot_path.exists():
        try:
            blob = json.loads(baseline_pilot_path.read_text(encoding="utf-8"))
            baseline_pilot = blob.get("pilot", {})
            baseline_margins = per_region_operator_margins(baseline_pilot)
            for r, info in baseline_margins.items():
                if info.get("top_operator"):
                    baseline_top[r] = info["top_operator"]
        except Exception:
            pass

    densification_top: Dict[str, str] = {}
    for r, info in densification_margins.items():
        if info.get("top_operator"):
            densification_top[r] = info["top_operator"]

    # Did the same operator win in every densification region?
    densification_winners = set(densification_top.values())
    same_op_everywhere = len(densification_winners) == 1

    # CI overlap test: in any densification region, does the top
    # operator's CI overlap with the runner-up's CI?
    n_overlapping = 0
    n_with_clear = 0
    for r, info in densification_margins.items():
        ranked = info.get("ranking") or []
        ops = info.get("operators") or {}
        if len(ranked) < 2:
            continue
        top, second = ranked[0], ranked[1]
        top_hi = ops[top]["ci_high"]
        second_lo = ops[second]["ci_low"]
        if top_hi >= second_lo:
            n_overlapping += 1
        else:
            n_with_clear += 1

    # Verdict
    if same_op_everywhere and len(densification_winners) > 0:
        verdict_letter = "A"
        verdict_text = (
            "PPO/single-operator wins everywhere -> operator hierarchy is"
            " region-invariant despite Stream 2's region-info finding."
        )
    elif len(densification_winners) >= 2:
        verdict_letter = "B"
        verdict_text = (
            "Different operators win in different regions -> region-specific"
            " gradient field structure confirmed; navigator's region"
            " conditioning is empirically meaningful."
        )
    else:
        verdict_letter = "C"
        verdict_text = "No densification regions had a top operator."

    if n_overlapping > n_with_clear and n_overlapping > 0:
        verdict_letter = "C"
        verdict_text = (
            f"In {n_overlapping}/{n_overlapping + n_with_clear} regions, the"
            " top operator's CI overlaps the runner-up's CI.  Margins"
            " distinguish operators on average but the 1K-episode budget"
            " produces wide CIs; navigator is operationally useful but"
            " per-region recommendations are uncertain."
        )

    return {
        "densification_top_per_region": densification_top,
        "baseline_top_per_region": baseline_top,
        "same_operator_everywhere_in_densification": same_op_everywhere,
        "n_distinct_top_operators": len(densification_winners),
        "n_regions_with_overlapping_top_ci": n_overlapping,
        "n_regions_with_clear_top_winner": n_with_clear,
        "verdict": verdict_letter,
        "verdict_text": verdict_text,
    }


# ---------------------------------------------------------------------------
# End-to-end driver
# ---------------------------------------------------------------------------


def main(
    out_path: str = "prometheus_math/_region_densification_pilot.json",
    n_episodes_per_cell: int = 1000,
    seeds: Tuple[int, ...] = (0, 1, 2),
    cells: Sequence[RegionCell] = DEFAULT_REGION_CELLS,
    algorithms: Tuple[str, ...] = (
        "random_uniform", "reinforce_linear", "ppo_mlp", "ga_elitist_v2",
    ),
) -> Dict[str, Any]:
    """Run the densification end-to-end and persist results."""
    print(f"[densify] starting region-densification pilot")
    n_total = len(cells) * len(algorithms) * len(seeds) * n_episodes_per_cell
    print(
        f"[densify] {len(cells)} cells × {len(algorithms)} algos ×"
        f" {len(seeds)} seeds × {n_episodes_per_cell} eps = {n_total} eps"
    )
    pilot_result = run_densification(
        cells=cells,
        n_episodes_per_cell=n_episodes_per_cell,
        seeds=seeds,
        algorithms=algorithms,
    )

    print(f"[densify] computing per-region margins...")
    margins = per_region_operator_margins(pilot_result)
    comparison = compare_with_baseline(margins)

    out = {
        "pilot": pilot_result,
        "per_region_operator_margins": margins,
        "baseline_comparison": comparison,
    }
    out_path_p = Path(out_path)
    out_path_p.parent.mkdir(parents=True, exist_ok=True)
    out_path_p.write_text(json.dumps(out, indent=2, default=str))
    print(
        f"[densify] wrote {out_path_p} ({pilot_result['total_episodes']} eps,"
        f" {pilot_result['elapsed_s']:.1f}s)"
    )
    print(f"[densify] verdict: {comparison['verdict']}")
    print(f"[densify]   {comparison['verdict_text']}")
    print(f"[densify] per-region top operator:")
    for r, op in comparison["densification_top_per_region"].items():
        print(f"  {r}  ->  {op}")
    return out


__all__ = [
    "RegionCell",
    "DEFAULT_REGION_CELLS",
    "CELL_ALGORITHM_RUNNERS",
    "run_densification",
    "per_region_operator_margins",
    "compare_with_baseline",
    "main",
]


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    main(n_episodes_per_cell=n)
