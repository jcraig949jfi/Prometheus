"""prometheus_math.native_kill_vector_pilot — first round emitting native KillVector.

Validation pilot for Stream 3's KillVector wiring.  Yesterday Day 4's
``kill_vector_learner`` B-matched the cell-mean baseline because the
legacy categorical kill_path strings carry no per-component margin
data.  This pilot:

  1. Runs ``DiscoveryEnv`` (degree=14, alphabet=±5, reward_shape=step)
     across 4 algorithms × 3 seeds × 2K episodes = 24K episodes.
  2. Emits a *native* KillVector per episode using
     ``kill_vector_from_pipeline_output`` — the same code path the
     pipeline uses internally, but applied to every episode (not just
     sub-Lehmer-band hits).
  3. Persists per-episode kill_vector data to a JSON for re-running
     the Day-4 learner.
  4. Computes coverage stats, component-level distributions, and the
     operator coordinate chart in margin space.

Honest framing
--------------
At degree=14 ±5, the sub-Lehmer band is empirically near-empty for 2K
random episodes (< 0.1% hit rate at deg 14 in the existing archaeology).
The vast majority of episodes fail Phase-0 band check, so the dominant
KillVector pattern will be ``out_of_band`` triggered with a numeric
margin (M - 1.18 for the M > 1.18 majority, M - 1.001 for cyclotomics).
That margin distribution is the *first place* where we can test whether
the native data is richer than the categorical.

Algorithms
----------
* ``random_uniform``   — uniform-random coefficients (run_random_null)
* ``REINFORCE-linear`` — linear contextual policy (run_reinforce_agent)
* ``PPO-MLP``          — SB3 PPO MlpPolicy (run_ppo_agent)
* ``GA_elitist (V2)``  — DiscoveryEnvV2 with selection_strategy='elitist'
                         and a uniform-random policy over the operator
                         menu — same V2 algorithm + pipeline gate.

This pilot does NOT modify ``discovery_env.py``, ``kill_vector.py``,
or ``discovery_pipeline.py`` — purely an instrumentation validation.
"""
from __future__ import annotations

import json
import math
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.kill_vector import (
    KillComponent,
    KillVector,
    kill_vector_from_pipeline_output,
)


# Canonical component names the pilot expects to see in margin-space.
# Mirrors prometheus_math.kill_vector_learner.CANONICAL_COMPONENTS but is
# defined locally to keep this module's analysis independent of the
# learner's import graph (the pilot must run even when the learner's
# data-loading pipeline is broken).
PILOT_COMPONENTS: Tuple[str, ...] = (
    "out_of_band",
    "reciprocity",
    "irreducibility",
    "catalog:Mossinghoff",
    "catalog:lehmer_literature",
    "catalog:LMFDB",
    "catalog:OEIS",
    "catalog:arXiv",
    "F1_permutation_null",
    "F6_base_rate",
    "F9_simpler_explanation",
    "F11_cross_validation",
)


# ---------------------------------------------------------------------------
# Per-episode result
# ---------------------------------------------------------------------------


@dataclass
class EpisodeKillVector:
    """One episode's outcome with native KillVector data attached."""

    algorithm: str
    seed: int
    episode_idx: int
    coeffs: List[int]
    mahler_measure: float
    reward: float
    reward_label: str
    is_known_in_mossinghoff: Optional[bool]
    pipeline_terminal_state: Optional[str]
    legacy_kill_pattern: Optional[str]
    kill_vector_dict: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "seed": self.seed,
            "episode_idx": self.episode_idx,
            "coeffs": list(self.coeffs),
            "mahler_measure": (
                None if not math.isfinite(self.mahler_measure)
                else float(self.mahler_measure)
            ),
            "reward": float(self.reward),
            "reward_label": self.reward_label,
            "is_known_in_mossinghoff": self.is_known_in_mossinghoff,
            "pipeline_terminal_state": self.pipeline_terminal_state,
            "legacy_kill_pattern": self.legacy_kill_pattern,
            "kill_vector": self.kill_vector_dict,
        }


# ---------------------------------------------------------------------------
# KillVector emission for a finished episode
# ---------------------------------------------------------------------------


def emit_kill_vector_for_episode(
    coeffs: Sequence[int],
    mahler_measure: float,
    *,
    operator_class: str,
    region_meta: Dict[str, Any],
    episode_idx: int,
    pipeline_record: Optional[Any] = None,
) -> KillVector:
    """Construct a native KillVector for a finished episode.

    If a ``DiscoveryRecord`` came back from the pipeline (sub-Lehmer-band
    hit), use ITS kill_vector verbatim — that's the rich, multi-component
    instance with margins from F1/F6/F9/F11 + catalog adapters.

    Otherwise (the common case at deg 14 ±5: out-of-band rejection),
    synthesise a phase-0 KillVector via the same helper the pipeline
    uses for phase-0 short-circuits.  This guarantees the native data
    is produced by the SAME emission code path regardless of episode
    outcome — no parallel categorical fallback.
    """
    # Pipeline-routed: use the rich KillVector the pipeline already built.
    if pipeline_record is not None and getattr(pipeline_record, "kill_vector", None) is not None:
        kv = pipeline_record.kill_vector
        # Stamp operator + region meta so downstream aggregation works.
        return KillVector(
            components=tuple(kv.components),
            candidate_hash=kv.candidate_hash,
            operator_class=operator_class,
            region_meta={**dict(kv.region_meta or {}), **region_meta,
                         "episode_idx": episode_idx},
            timestamp=kv.timestamp,
        )

    # Phase-0 short-circuit emission: same helper, marked phase0_kill.
    # Rebuild a candidate_hash deterministically from coeffs + M.
    import hashlib
    blob = json.dumps({"coeffs": list(coeffs), "M": float(mahler_measure)},
                      sort_keys=True)
    h = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return kill_vector_from_pipeline_output(
        coeffs=list(coeffs),
        mahler_measure=mahler_measure,
        check_results={"phase": "phase0_band_check"},
        candidate_hash=h,
        operator_class=operator_class,
        region_meta={**region_meta, "episode_idx": episode_idx},
        phase0_kill=True,
    )


# ---------------------------------------------------------------------------
# Algorithm runners — each emits a list of EpisodeKillVector
# ---------------------------------------------------------------------------


def _env_factory_v1(seed: int) -> DiscoveryEnv:
    return DiscoveryEnv(
        degree=14,
        reward_shape="step",
        coefficient_choices=tuple(range(-5, 6)),
        seed=seed,
        log_discoveries=False,
    )


def _common_region_meta() -> Dict[str, Any]:
    return {
        "env": "DiscoveryEnv",
        "degree": 14,
        "alphabet_width": 5,
        "alphabet_size": 11,
        "reward_shape": "step",
    }


def run_random_uniform_pilot(
    n_episodes: int, seed: int
) -> List[EpisodeKillVector]:
    """Uniform-random sampler over the deg-14 ±5 coefficient space."""
    env = _env_factory_v1(seed)
    rng = np.random.default_rng(seed)
    region_meta = _common_region_meta()
    operator_class = f"random_uniform@seed={seed}"

    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", 11))

    out: List[EpisodeKillVector] = []
    pipeline_len_before = 0
    for ep in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        while not terminated:
            a = int(rng.integers(0, n_actions))
            _, r, terminated, _, last_info = env.step(a)

        coeffs = last_info.get("coeffs_full") or [0] * (env.degree + 1)
        m_value = last_info.get("mahler_measure", float("inf"))
        reward = float(last_info.get("reward_label") and 0.0 or 0.0)
        # Pull reward from env's state — last_info has reward via step return,
        # but `r` from above is already the actual reward.
        reward = float(r)
        reward_label = str(last_info.get("reward_label") or "unknown")
        is_known = last_info.get("is_known_in_mossinghoff")

        # Did the pipeline produce a record this episode?
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
        legacy_kill_pattern = kv.to_legacy_kill_path()

        out.append(EpisodeKillVector(
            algorithm="random_uniform",
            seed=seed,
            episode_idx=ep,
            coeffs=list(coeffs),
            mahler_measure=float(m_value) if m_value is not None else float("nan"),
            reward=reward,
            reward_label=reward_label,
            is_known_in_mossinghoff=is_known,
            pipeline_terminal_state=terminal_state,
            legacy_kill_pattern=legacy_kill_pattern,
            kill_vector_dict=kv.to_dict(),
        ))
    try:
        env.close()
    except Exception:
        pass
    return out


def run_reinforce_pilot(n_episodes: int, seed: int) -> List[EpisodeKillVector]:
    """REINFORCE-linear contextual policy over the deg-14 ±5 space."""
    env = _env_factory_v1(seed)
    rng = np.random.default_rng(seed)
    region_meta = _common_region_meta()
    operator_class = f"reinforce_linear@seed={seed}"

    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions", 11))
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

        # Update policy.
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


def run_ppo_pilot(n_episodes: int, seed: int) -> List[EpisodeKillVector]:
    """PPO-MLP via stable_baselines3 over deg-14 ±5.

    Falls back to a no-op (returns []) when SB3 isn't installed; the
    pilot driver surfaces the skip in the JSON.
    """
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import BaseCallback
        from stable_baselines3.common.vec_env import DummyVecEnv
    except ImportError:
        return []

    env = _env_factory_v1(seed)
    region_meta = _common_region_meta()
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
                # Capture this episode.
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


def run_ga_elitist_pilot(n_episodes: int, seed: int) -> List[EpisodeKillVector]:
    """V2 GA with selection_strategy='elitist' + uniform-random operator policy."""
    from prometheus_math.discovery_env_v2 import DiscoveryEnvV2

    env = DiscoveryEnvV2(
        degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        selection_strategy="elitist",
        enable_pipeline=True,
        seed=seed,
        # Match the V2 anti-elitist pilot's defaults so this is the
        # established GA_elitist baseline configuration.
        population_size=8,
        n_mutations_per_episode=12,
    )
    rng = np.random.default_rng(seed)
    region_meta = {**_common_region_meta(), "env": "DiscoveryEnvV2"}
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
            # V2 surfaces the elite via `elite_coeffs`; fall back to
            # zeros if absent.
            coeffs = [0] * (env.degree + 1)
        m_value = last_info.get("elite_m") or last_info.get("mahler_measure", float("inf"))
        reward_label = str(last_info.get("reward_label") or "v2_episode")
        is_known = last_info.get("is_known_in_mossinghoff")

        pipeline_records = env._pipeline_records  # V2 uses _pipeline_records
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


# ---------------------------------------------------------------------------
# Pilot orchestrator
# ---------------------------------------------------------------------------


ALGORITHM_RUNNERS: Dict[str, Callable[[int, int], List[EpisodeKillVector]]] = {
    "random_uniform": run_random_uniform_pilot,
    "reinforce_linear": run_reinforce_pilot,
    "ppo_mlp": run_ppo_pilot,
    "ga_elitist_v2": run_ga_elitist_pilot,
}


def run_pilot(
    n_episodes_per_cell: int = 2000,
    seeds: Tuple[int, ...] = (0, 1, 2),
    algorithms: Tuple[str, ...] = (
        "random_uniform", "reinforce_linear", "ppo_mlp", "ga_elitist_v2",
    ),
    *,
    progress: bool = True,
) -> Dict[str, Any]:
    """Run the full 4 algorithms × 3 seeds × n_episodes pilot.

    Returns a dict with:
      * meta: setup
      * episodes: list[EpisodeKillVector.to_dict()] (size up to ~24K)
      * cell_summary: {(algo, seed): {n, n_pipeline_routed, elapsed_s, ...}}
      * elapsed_s: total wall time
    """
    t_global = time.perf_counter()
    all_episodes: List[EpisodeKillVector] = []
    cell_summary: Dict[str, Dict[str, Any]] = {}
    skipped: List[str] = []

    for algo in algorithms:
        if algo not in ALGORITHM_RUNNERS:
            raise ValueError(f"unknown algorithm {algo!r}")
        runner = ALGORITHM_RUNNERS[algo]
        for s in seeds:
            t0 = time.perf_counter()
            if progress:
                print(f"[pilot] running {algo} seed={s} (target={n_episodes_per_cell} eps)...",
                      flush=True)
            try:
                eps = runner(n_episodes_per_cell, int(s))
            except Exception as e:
                if progress:
                    print(f"  ERROR in {algo} seed={s}: {type(e).__name__}: {e!r}",
                          flush=True)
                skipped.append(f"{algo}@seed={s}: {type(e).__name__}")
                eps = []
            elapsed = time.perf_counter() - t0
            n_pipeline = sum(
                1 for e in eps if e.pipeline_terminal_state is not None
            )
            cell_summary[f"{algo}@seed={s}"] = {
                "algorithm": algo,
                "seed": int(s),
                "n_episodes": len(eps),
                "n_pipeline_routed": n_pipeline,
                "elapsed_s": elapsed,
                "skipped": len(eps) == 0 and n_episodes_per_cell > 0,
            }
            all_episodes.extend(eps)
            if progress:
                print(f"  -> {len(eps)} eps, {n_pipeline} pipeline-routed, "
                      f"{elapsed:.1f}s ({len(eps)/max(elapsed,1e-9):.1f} eps/s)",
                      flush=True)

    elapsed = time.perf_counter() - t_global
    return {
        "meta": {
            "n_episodes_per_cell": int(n_episodes_per_cell),
            "seeds": list(seeds),
            "algorithms": list(algorithms),
            "env": {
                "name": "DiscoveryEnv (V1) + DiscoveryEnvV2 (GA_elitist)",
                "degree": 14,
                "alphabet_width": 5,
                "alphabet": list(range(-5, 6)),
                "reward_shape": "step",
            },
            "pilot_components": list(PILOT_COMPONENTS),
        },
        "episodes": [e.to_dict() for e in all_episodes],
        "cell_summary": cell_summary,
        "skipped": skipped,
        "elapsed_s": float(elapsed),
        "total_episodes": len(all_episodes),
    }


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


def coverage_stats(episodes: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Coverage: per-component, what fraction of episodes have non-None margin?"""
    n_total = len(episodes)
    if n_total == 0:
        return {"n_total": 0, "per_component": {}}

    triggered_count: Counter = Counter()
    margin_count: Counter = Counter()
    component_seen: Counter = Counter()
    has_any_margin = 0

    for e in episodes:
        kv = e["kill_vector"]
        any_margin = False
        for c in kv["components"]:
            name = c["falsifier_name"]
            component_seen[name] += 1
            if c["triggered"]:
                triggered_count[name] += 1
            if c["margin"] is not None:
                margin_count[name] += 1
                any_margin = True
        if any_margin:
            has_any_margin += 1

    per_component = {}
    for name in PILOT_COMPONENTS:
        seen = component_seen.get(name, 0)
        per_component[name] = {
            "n_seen": seen,
            "n_triggered": triggered_count.get(name, 0),
            "n_with_margin": margin_count.get(name, 0),
            "triggered_rate": (
                triggered_count.get(name, 0) / seen if seen > 0 else 0.0
            ),
            "margin_coverage": (
                margin_count.get(name, 0) / seen if seen > 0 else 0.0
            ),
        }
    return {
        "n_total": n_total,
        "n_with_any_margin": has_any_margin,
        "fraction_with_any_margin": has_any_margin / max(n_total, 1),
        "per_component": per_component,
    }


def component_distributions(
    episodes: Sequence[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """For each component: triggered rate + margin distribution summary
    (mean, median, p25, p75, std, n).  Margins are the RAW values (signed)
    from the KillComponent, not squashed."""
    per_component: Dict[str, Dict[str, Any]] = {}
    for name in PILOT_COMPONENTS:
        per_component[name] = {
            "triggered_margins": [],   # margins on triggered=True only
            "untriggered_margins": [], # margins on triggered=False
            "all_margins": [],
            "all_triggered": [],
        }
    for e in episodes:
        for c in e["kill_vector"]["components"]:
            name = c["falsifier_name"]
            if name not in per_component:
                continue
            m = c["margin"]
            if m is not None and math.isfinite(m):
                per_component[name]["all_margins"].append(float(m))
                if c["triggered"]:
                    per_component[name]["triggered_margins"].append(float(m))
                else:
                    per_component[name]["untriggered_margins"].append(float(m))
            per_component[name]["all_triggered"].append(1.0 if c["triggered"] else 0.0)

    summary: Dict[str, Dict[str, Any]] = {}
    for name, data in per_component.items():
        am = np.asarray(data["all_margins"], dtype=float) if data["all_margins"] else np.zeros(0)
        tm = np.asarray(data["triggered_margins"], dtype=float) if data["triggered_margins"] else np.zeros(0)
        ut = np.asarray(data["untriggered_margins"], dtype=float) if data["untriggered_margins"] else np.zeros(0)
        trig = np.asarray(data["all_triggered"], dtype=float) if data["all_triggered"] else np.zeros(0)
        summary[name] = {
            "n_with_margin": int(am.size),
            "n_triggered_with_margin": int(tm.size),
            "n_untriggered_with_margin": int(ut.size),
            "triggered_rate": float(trig.mean()) if trig.size else 0.0,
            "margin_mean": float(am.mean()) if am.size else None,
            "margin_std": float(am.std()) if am.size else None,
            "margin_median": float(np.median(am)) if am.size else None,
            "margin_p25": float(np.percentile(am, 25)) if am.size else None,
            "margin_p75": float(np.percentile(am, 75)) if am.size else None,
            "margin_min": float(am.min()) if am.size else None,
            "margin_max": float(am.max()) if am.size else None,
            "triggered_margin_mean": float(tm.mean()) if tm.size else None,
            "triggered_margin_std": float(tm.std()) if tm.size else None,
        }
    return summary


def operator_chart_margin_space(
    episodes: Sequence[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """For each operator (algorithm), compute E[k | operator] using the
    FULL kill_vector (squashed margins as a [0, 1] kill-strength PER
    component), not just triggered/not."""
    by_op: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    by_op_triggered: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for e in episodes:
        op = e["algorithm"]
        for c in e["kill_vector"]["components"]:
            name = c["falsifier_name"]
            # Squashed margin (the unit-aware kill-strength).
            kc = KillComponent.from_dict(c)
            sq = kc.squashed()
            by_op[op][name].append(float(sq))
            by_op_triggered[op][name].append(1.0 if c["triggered"] else 0.0)

    out: Dict[str, Dict[str, Any]] = {}
    for op, comps in by_op.items():
        e_k = {}
        e_trig = {}
        for name in PILOT_COMPONENTS:
            arr = comps.get(name, [])
            tarr = by_op_triggered[op].get(name, [])
            e_k[name] = float(np.mean(arr)) if arr else 0.0
            e_trig[name] = float(np.mean(tarr)) if tarr else 0.0
        out[op] = {
            "n_episodes": int(sum(len(v) for v in by_op_triggered[op].values()) //
                              max(len(by_op_triggered[op]), 1)),
            "E_k_squashed_per_component": e_k,
            "E_triggered_per_component": e_trig,
        }
    return out


def kl_divergence_distinguishability(
    chart: Dict[str, Dict[str, Any]],
    *,
    use_squashed: bool = True,
) -> float:
    """Compute pairwise symmetric-KL distances between operators in the
    chart and average them.  Larger = operators are MORE distinguishable
    in this representation.

    The chart is treated as one categorical distribution per operator
    over the K canonical components.  For numerical stability we
    Laplace-smooth with eps=0.01.

    The "legacy" baseline uses ``E_triggered_per_component`` (binary);
    the "native" uses ``E_k_squashed_per_component`` (margin-aware).
    """
    key = "E_k_squashed_per_component" if use_squashed else "E_triggered_per_component"
    ops = sorted(chart.keys())
    if len(ops) < 2:
        return 0.0

    eps = 0.01
    dists: List[np.ndarray] = []
    for op in ops:
        v = np.array(
            [chart[op][key].get(name, 0.0) for name in PILOT_COMPONENTS],
            dtype=float,
        )
        v = np.clip(v, 0.0, None) + eps
        v = v / v.sum()
        dists.append(v)

    n = len(dists)
    total = 0.0
    n_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            p, q = dists[i], dists[j]
            # symmetric KL = KL(p||q) + KL(q||p)
            skl = float(np.sum(p * np.log(p / q)) + np.sum(q * np.log(q / p)))
            total += skl
            n_pairs += 1
    return total / max(n_pairs, 1)


def comparative_distinguishability(
    chart: Dict[str, Dict[str, Any]],
) -> Dict[str, float]:
    """Compute the legacy (categorical/triggered) vs native (squashed)
    operator-chart distinguishability."""
    legacy_kl = kl_divergence_distinguishability(chart, use_squashed=False)
    native_kl = kl_divergence_distinguishability(chart, use_squashed=True)
    gain = native_kl / max(legacy_kl, 1e-12) if legacy_kl > 0 else float("inf")
    return {
        "legacy_avg_pairwise_skl": float(legacy_kl),
        "native_avg_pairwise_skl": float(native_kl),
        "native_over_legacy_ratio": float(gain),
    }


def f6_margin_cluster_analysis(
    episodes: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """For candidates that legacy would have categorically lumped as
    'F6_base_rate killed', what's the distribution of their F6 margin
    z-scores?  Tight cluster = legacy was hiding fine structure.
    """
    margins: List[float] = []
    triggered_margins: List[float] = []
    untriggered_margins: List[float] = []
    for e in episodes:
        for c in e["kill_vector"]["components"]:
            if c["falsifier_name"] != "F6_base_rate":
                continue
            m = c["margin"]
            if m is None or not math.isfinite(m):
                continue
            margins.append(float(m))
            if c["triggered"]:
                triggered_margins.append(float(m))
            else:
                untriggered_margins.append(float(m))
    if not margins:
        return {
            "n": 0, "n_triggered": 0, "n_untriggered": 0,
            "mean": None, "std": None, "unique_values": [],
        }
    arr = np.asarray(margins, dtype=float)
    uniq, counts = np.unique(arr, return_counts=True)
    return {
        "n": int(arr.size),
        "n_triggered": int(len(triggered_margins)),
        "n_untriggered": int(len(untriggered_margins)),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "median": float(np.median(arr)),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "unique_values": [
            {"value": float(v), "count": int(c)} for v, c in zip(uniq, counts)
        ][:20],   # cap the histogram for JSON size
        "n_unique_values": int(uniq.size),
        "verdict": (
            "spread"
            if arr.std() > 0.5
            else "tight_cluster_or_bimodal"
        ),
    }


# ---------------------------------------------------------------------------
# End-to-end: pilot -> analysis -> JSON
# ---------------------------------------------------------------------------


def analyze(pilot_result: Dict[str, Any]) -> Dict[str, Any]:
    """Run all analyses on a pilot_result dict; return the analysis dict."""
    eps = pilot_result.get("episodes", [])
    cov = coverage_stats(eps)
    dist = component_distributions(eps)
    chart = operator_chart_margin_space(eps)
    distinguish = comparative_distinguishability(chart)
    f6 = f6_margin_cluster_analysis(eps)
    return {
        "coverage": cov,
        "component_distributions": dist,
        "operator_chart": chart,
        "distinguishability": distinguish,
        "f6_margin_analysis": f6,
    }


# ---------------------------------------------------------------------------
# Day 4 learner re-run on native kill_vector data
# ---------------------------------------------------------------------------


def _episodes_to_learner_records(
    episodes: Sequence[Dict[str, Any]],
) -> List[Any]:
    """Convert native pilot episodes into ``LearnerRecord`` instances
    that the Day-4 learner can consume.

    Each episode becomes ONE record with:
      * region   = "deg14_w5_step" (single region for this pilot)
      * operator = the algorithm name (random_uniform / reinforce_linear /
                   ppo_mlp / ga_elitist_v2)
      * y_triggered = (n_components,) one-hot over PILOT_COMPONENTS
      * y_margin    = (n_components,) raw margins (NaN where None)
    """
    from prometheus_math.kill_vector_learner import (
        CANONICAL_COMPONENTS, LearnerRecord,
    )

    name_to_idx = {n: i for i, n in enumerate(CANONICAL_COMPONENTS)}
    n_components = len(CANONICAL_COMPONENTS)

    records: List[Any] = []
    for e in episodes:
        kv = e["kill_vector"]
        region_meta = dict(kv.get("region_meta") or {})
        # Single region for this pilot.
        region = "deg14_w5_step"
        operator = e["algorithm"]

        y_trig = np.zeros(n_components, dtype=float)
        y_marg = np.full(n_components, np.nan, dtype=float)
        for c in kv["components"]:
            name = c["falsifier_name"]
            idx = name_to_idx.get(name)
            if idx is None:
                continue
            if c["triggered"]:
                y_trig[idx] = 1.0
            if c["margin"] is not None:
                try:
                    v = float(c["margin"])
                    if math.isfinite(v):
                        y_marg[idx] = v
                except (TypeError, ValueError):
                    pass

        records.append(LearnerRecord(
            region=region,
            operator=operator,
            region_meta={
                "degree": 14,
                "alphabet_width": 5,
                "reward_shape": "step",
                "env": region_meta.get("env", "DiscoveryEnv"),
            },
            y_triggered=y_trig,
            y_margin=y_marg,
            weight=1.0,
        ))
    return records


def rerun_day4_learner(
    pilot_result: Dict[str, Any],
    *,
    test_size: float = 0.20,
    val_size: float = 0.10,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Re-run the Day-4 learner on the native kill_vector dataset.

    Returns a dict with:
      * dataset_stats
      * learner_kv_mae
      * baseline_kv_mae (global / region / operator / cell)
      * verdict (A / B / C)
      * rationale
    """
    from prometheus_math.kill_vector_learner import (
        Baselines, CANONICAL_COMPONENTS, Dataset, Learner,
        _verdict_from_mae, operator_chart_recovery,
        overall_kill_vector_mae, per_component_metrics,
        stratified_split,
    )

    eps = pilot_result.get("episodes", [])
    if not eps:
        return {
            "n_records": 0,
            "verdict": "C_REPRESENTATION_ISSUE",
            "rationale": "Empty pilot — no episodes to train on.",
        }

    records = _episodes_to_learner_records(eps)
    if not records:
        return {
            "n_records": 0,
            "verdict": "C_REPRESENTATION_ISSUE",
            "rationale": "No records survived conversion.",
        }

    # Build a Dataset from the records (skip build_dataset which loads
    # legacy JSONs from disk).
    regions = sorted({r.region for r in records})
    operators = sorted({r.operator for r in records})
    dataset = Dataset(
        records=records,
        component_names=CANONICAL_COMPONENTS,
        region_to_idx={r: i for i, r in enumerate(regions)},
        operator_to_idx={o: i for i, o in enumerate(operators)},
    )

    train_idx, val_idx, test_idx = stratified_split(
        dataset, test_size=test_size, val_size=val_size,
        random_state=random_state,
    )
    train_records = [dataset.records[i] for i in train_idx]
    test_records = [dataset.records[i] for i in test_idx]

    # Defensive: the dataset may have only one region in this pilot;
    # stratified_split may yield empty test if so.  Fall back to a
    # plain random split.
    if not test_records:
        rng = np.random.RandomState(random_state)
        all_idxs = list(range(len(records)))
        rng.shuffle(all_idxs)
        n = len(all_idxs)
        n_test = max(1, int(n * test_size))
        test_idx = all_idxs[:n_test]
        train_idx = all_idxs[n_test:]
        train_records = [dataset.records[i] for i in train_idx]
        test_records = [dataset.records[i] for i in test_idx]

    learner = Learner.fit(train_records, random_state=random_state)
    baselines = Baselines.fit(train_records, dataset.n_components)

    pred_learner = learner.predict_proba(test_records)
    pred_global = baselines.predict(test_records, kind="global")
    pred_region = baselines.predict(test_records, kind="region")
    pred_operator = baselines.predict(test_records, kind="operator")
    pred_cell = baselines.predict(test_records, kind="cell")

    learner_kv_mae = overall_kill_vector_mae(test_records, pred_learner)
    baseline_kv_mae = {
        "global": overall_kill_vector_mae(test_records, pred_global),
        "region": overall_kill_vector_mae(test_records, pred_region),
        "operator": overall_kill_vector_mae(test_records, pred_operator),
        "cell": overall_kill_vector_mae(test_records, pred_cell),
    }
    verdict, rationale = _verdict_from_mae(
        learner_kv_mae, baseline_kv_mae["cell"], baseline_kv_mae["region"]
    )

    # Per-component metrics, scoped to the test set.
    learner_metrics = per_component_metrics(
        test_records, pred_learner, CANONICAL_COMPONENTS
    )
    cell_metrics = per_component_metrics(
        test_records, pred_cell, CANONICAL_COMPONENTS
    )

    chart_recov = operator_chart_recovery(test_records, pred_learner)

    return {
        "n_records": len(records),
        "n_train": len(train_records),
        "n_test": len(test_records),
        "n_regions": len(regions),
        "n_operators": len(operators),
        "learner_kv_mae": float(learner_kv_mae),
        "baseline_kv_mae": {k: float(v) for k, v in baseline_kv_mae.items()},
        "verdict": verdict,
        "rationale": rationale,
        "per_component_metrics": {
            "learner": learner_metrics,
            "cell": cell_metrics,
        },
        "operator_chart_recovery": chart_recov,
    }


# Map the Day-4 learner verdict to the spec's A/B/C verdict (which is
# almost the same thing, but with kill-space-framing-specific wording).
def map_to_pilot_verdict(
    learner_result: Dict[str, Any],
    coverage: Dict[str, Any],
) -> Dict[str, str]:
    """Apply the spec's A/B/C verdict dispatch:

      * A: Margin-rich data → learner beats cell-mean
        ⇒ kill-space framing is empirically validated
      * B: Even margin-rich data → learner ties cell-mean
        ⇒ cell-mean is the empirical ceiling
      * C: Margin data is corrupt or sparse
        ⇒ instrumentation bug — Stream 3 needs revisit
    """
    learner_verdict = learner_result.get("verdict", "C_REPRESENTATION_ISSUE")
    frac_with_margin = coverage.get("fraction_with_any_margin", 0.0)
    learner_mae = learner_result.get("learner_kv_mae", float("nan"))
    cell_mae = learner_result.get("baseline_kv_mae", {}).get("cell", float("nan"))

    if frac_with_margin < 0.10:
        return {
            "verdict": "C_INSTRUMENTATION_BUG",
            "rationale": (
                f"Margin coverage is {frac_with_margin:.1%} — under 10%."
                " Native KillVector emission isn't capturing margins;"
                " Stream 3's emission code path likely has a bug. Revisit"
                " the per-component margin extractors before Day 5."
            ),
        }
    if learner_verdict == "A_BEATS_CELL_MEAN":
        return {
            "verdict": "A_KILL_SPACE_VALIDATED",
            "rationale": (
                f"Margin-rich data (coverage={frac_with_margin:.1%}) → "
                f"learner MAE {learner_mae:.4f} beats cell-mean baseline"
                f" {cell_mae:.4f}.  Day 4's B-result was a data-coarseness"
                " problem, not a framing problem.  Kill-space framing is"
                " empirically validated; Day 5 navigation has a learnable"
                " gradient field on this region."
            ),
        }
    if learner_verdict == "B_MATCHES_CELL_MEAN":
        return {
            "verdict": "B_OPERATIONAL_CEILING",
            "rationale": (
                f"Even with margin coverage at {frac_with_margin:.1%}, the"
                f" learner MAE {learner_mae:.4f} only ties the cell-mean"
                f" baseline {cell_mae:.4f}.  Cell-mean is the empirical"
                " ceiling on this single-region dataset.  Kill-space"
                " framing is operationally useful (it gave us per-"
                "component margins to inspect) but doesn't unlock"
                " additional learned signal beyond table lookup at this"
                " scale.  Need denser cross-region data, or a richer"
                " sub-Lehmer hit rate, before Day 5 navigation can claim"
                " a learned gradient."
            ),
        }
    # Fallback: learner underperforms cell-mean → instrumentation issue.
    return {
        "verdict": "C_INSTRUMENTATION_BUG",
        "rationale": (
            f"Learner ({learner_mae:.4f}) underperforms cell-mean "
            f"({cell_mae:.4f}). Likely instrumentation bug or data"
            " representation mismatch."
        ),
    }


def main(
    out_path: str = "prometheus_math/_native_kill_vector_pilot.json",
    n_episodes_per_cell: int = 2000,
    seeds: Tuple[int, ...] = (0, 1, 2),
    algorithms: Tuple[str, ...] = (
        "random_uniform", "reinforce_linear", "ppo_mlp", "ga_elitist_v2",
    ),
) -> Dict[str, Any]:
    """Run the pilot end-to-end and persist results."""
    print(f"[pilot] starting native-kill-vector pilot")
    print(f"[pilot] {len(algorithms)} algorithms × {len(seeds)} seeds × "
          f"{n_episodes_per_cell} eps = {len(algorithms)*len(seeds)*n_episodes_per_cell} eps")
    pilot_result = run_pilot(
        n_episodes_per_cell=n_episodes_per_cell,
        seeds=seeds,
        algorithms=algorithms,
    )
    analysis = analyze(pilot_result)

    # Re-run the Day-4 learner on the new dataset.
    print(f"[pilot] re-running Day-4 learner on native data...")
    try:
        learner_rerun = rerun_day4_learner(pilot_result)
    except Exception as e:
        learner_rerun = {
            "error": f"{type(e).__name__}: {e!r}"[:300],
            "verdict": "C_REPRESENTATION_ISSUE",
            "rationale": "Learner re-run crashed; see error.",
        }

    pilot_verdict = map_to_pilot_verdict(learner_rerun, analysis["coverage"])

    out = {
        "pilot": pilot_result,
        "analysis": analysis,
        "learner_rerun": learner_rerun,
        "pilot_verdict": pilot_verdict,
    }
    out_path_p = Path(out_path)
    out_path_p.parent.mkdir(parents=True, exist_ok=True)
    out_path_p.write_text(json.dumps(out, indent=2, default=str))
    print(f"[pilot] wrote {out_path_p}  ({pilot_result['total_episodes']} episodes,"
          f" {pilot_result['elapsed_s']:.1f}s)")
    print(f"[pilot] learner_kv_mae = {learner_rerun.get('learner_kv_mae', float('nan'))}")
    print(f"[pilot] cell_baseline_mae = {learner_rerun.get('baseline_kv_mae', {}).get('cell', float('nan'))}")
    print(f"[pilot] VERDICT = {pilot_verdict['verdict']}")
    return out


__all__ = [
    "PILOT_COMPONENTS",
    "EpisodeKillVector",
    "ALGORITHM_RUNNERS",
    "analyze",
    "comparative_distinguishability",
    "component_distributions",
    "coverage_stats",
    "emit_kill_vector_for_episode",
    "f6_margin_cluster_analysis",
    "kl_divergence_distinguishability",
    "main",
    "map_to_pilot_verdict",
    "operator_chart_margin_space",
    "rerun_day4_learner",
    "run_ga_elitist_pilot",
    "run_pilot",
    "run_ppo_pilot",
    "run_random_uniform_pilot",
    "run_reinforce_pilot",
]


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    main(n_episodes_per_cell=n)
