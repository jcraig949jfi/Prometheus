"""prometheus_math.extended_ppo_pilot — extended PPO scaling test for deg14 ±5.

The 2K-episode native pilot showed PPO touched margin = -0.001 (band edge)
and produced 17/6000 sub-Lehmer hits, all rediscoveries of Lehmer's
polynomial.  This pilot scales 50x to **100K episodes per seed × 3 seeds
= 300K total** to answer:

  Does PPO actually CROSS the band given proper budget, or hover at the
  edge?

Verdict dispatch
----------------
* **A** — PPO produced ≥1 SHADOW_CATALOG / PROMOTE not in Mossinghoff
* **B** — PPO crossed band but only rediscovered Mossinghoff entries
* **C** — PPO touched band but never crossed in 300K episodes
* **D** — PPO didn't even touch band at scale

Honest framing
--------------
The kill-space navigator's first concrete recommendation was PPO for
this region.  If A: navigator validated empirically.  If B: operator
behavior matches recommendation, subspace is bounded by Lehmer.
If C: operator approaches but doesn't reach.  If D: 6K-episode pilot
was a lucky outlier and operator-utility was overestimated.

This pilot does NOT modify discovery_env / kill_vector / pipeline —
it's pure instrumentation + scaling.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.kill_vector import (
    kill_vector_from_pipeline_output,
)


# ---------------------------------------------------------------------------
# Per-seed result
# ---------------------------------------------------------------------------


@dataclass
class SeedResult:
    """Aggregate per-seed metrics for the extended PPO run."""

    seed: int
    n_episodes: int
    elapsed_s: float
    # Episode index of first time margin <= 0.0 (band touch).
    first_band_touch_episode: Optional[int]
    first_band_touch_margin: Optional[float]
    # First time margin < 0 STRICTLY (band cross).
    first_band_cross_episode: Optional[int]
    first_band_cross_margin: Optional[float]
    # First sub-Lehmer hit (1.001 < M < 1.18, in-band proper).
    first_sub_lehmer_episode: Optional[int]
    first_sub_lehmer_M: Optional[float]
    # First SHADOW_CATALOG hit (band hit + not in Mossinghoff + survived
    # battery).
    first_shadow_catalog_episode: Optional[int]
    # First PROMOTE if ever (today the pipeline always lands in
    # SHADOW_CATALOG for survivors; PROMOTE requires independent
    # verification we don't automate).
    first_promote_episode: Optional[int]
    # Distribution of margins across all episodes.
    best_margin: float
    mean_margin: float
    median_margin: float
    std_margin: float
    p10_margin: float
    p25_margin: float
    p75_margin: float
    p90_margin: float
    # Counts.
    n_band_touch: int          # margin <= 0
    n_band_cross: int          # margin < 0
    n_sub_lehmer: int          # 1.001 < M < 1.18
    n_cyclotomic: int          # M < 1.001
    n_above_band: int          # M >= 1.18
    n_known_in_mossinghoff: int   # cross-check against Mossinghoff
    n_novel_in_band: int       # in-band AND NOT in Mossinghoff
    n_pipeline_routed: int     # episodes that reached pipeline
    n_promoted: int
    n_shadow_catalog: int
    n_rejected_post_pipeline: int
    # Sample of trajectory: (episode_idx, margin, M) for every band-touch.
    band_touch_samples: List[Tuple[int, float, float]] = field(default_factory=list)
    # Novel candidates (not in Mossinghoff) full record.
    novel_candidates: List[Dict[str, Any]] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "n_episodes": self.n_episodes,
            "elapsed_s": self.elapsed_s,
            "first_band_touch_episode": self.first_band_touch_episode,
            "first_band_touch_margin": self.first_band_touch_margin,
            "first_band_cross_episode": self.first_band_cross_episode,
            "first_band_cross_margin": self.first_band_cross_margin,
            "first_sub_lehmer_episode": self.first_sub_lehmer_episode,
            "first_sub_lehmer_M": self.first_sub_lehmer_M,
            "first_shadow_catalog_episode": self.first_shadow_catalog_episode,
            "first_promote_episode": self.first_promote_episode,
            "best_margin": self.best_margin,
            "mean_margin": self.mean_margin,
            "median_margin": self.median_margin,
            "std_margin": self.std_margin,
            "p10_margin": self.p10_margin,
            "p25_margin": self.p25_margin,
            "p75_margin": self.p75_margin,
            "p90_margin": self.p90_margin,
            "n_band_touch": self.n_band_touch,
            "n_band_cross": self.n_band_cross,
            "n_sub_lehmer": self.n_sub_lehmer,
            "n_cyclotomic": self.n_cyclotomic,
            "n_above_band": self.n_above_band,
            "n_known_in_mossinghoff": self.n_known_in_mossinghoff,
            "n_novel_in_band": self.n_novel_in_band,
            "n_pipeline_routed": self.n_pipeline_routed,
            "n_promoted": self.n_promoted,
            "n_shadow_catalog": self.n_shadow_catalog,
            "n_rejected_post_pipeline": self.n_rejected_post_pipeline,
            "band_touch_samples_count": len(self.band_touch_samples),
            "band_touch_samples": self.band_touch_samples[:50],  # cap
            "novel_candidates": self.novel_candidates[:20],   # cap (full survivors are rare)
        }


# ---------------------------------------------------------------------------
# Margin computation (mirrors kill_vector.kill_vector_from_pipeline_output)
# ---------------------------------------------------------------------------


def _band_margin(M: float) -> Optional[float]:
    """Signed band margin: positive=above-band, negative=below-1.001 cyclotomic
    OR strict in-band; zero=exactly on a band boundary; None=non-finite.

    Definition (from kill_vector.py L565-572):
      M > 1.18   -> margin = M - 1.18 (positive)
      M < 1.001  -> margin = M - 1.001 (negative)
      otherwise  -> margin = 0.0 (in-band)

    NOTE: This margin is signed and reflects distance to the nearest
    band boundary on the EXIT side.  An in-band hit (1.001 < M < 1.18)
    has margin = 0.0, NOT a negative number — the negative-margin
    cluster at -0.001 in the prior pilot was M=1.000 cyclotomics, not
    sub-Lehmer poly.
    """
    if not math.isfinite(M):
        return None
    if M > 1.18:
        return M - 1.18
    if M < 1.001:
        return M - 1.001
    return 0.0


# ---------------------------------------------------------------------------
# PPO runner with rich trajectory capture
# ---------------------------------------------------------------------------


def run_ppo_extended(
    n_episodes: int,
    seed: int,
    *,
    progress_every: int = 5000,
) -> SeedResult:
    """Run PPO for n_episodes at the deg14 ±5 step config and return a
    full SeedResult.

    Skips cleanly with a stub SeedResult if SB3 isn't installed.
    """
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import BaseCallback
        from stable_baselines3.common.vec_env import DummyVecEnv
    except ImportError:
        return SeedResult(
            seed=seed, n_episodes=0, elapsed_s=0.0,
            first_band_touch_episode=None, first_band_touch_margin=None,
            first_band_cross_episode=None, first_band_cross_margin=None,
            first_sub_lehmer_episode=None, first_sub_lehmer_M=None,
            first_shadow_catalog_episode=None, first_promote_episode=None,
            best_margin=float("inf"), mean_margin=float("nan"),
            median_margin=float("nan"), std_margin=float("nan"),
            p10_margin=float("nan"), p25_margin=float("nan"),
            p75_margin=float("nan"), p90_margin=float("nan"),
            n_band_touch=0, n_band_cross=0, n_sub_lehmer=0,
            n_cyclotomic=0, n_above_band=0, n_known_in_mossinghoff=0,
            n_novel_in_band=0, n_pipeline_routed=0,
            n_promoted=0, n_shadow_catalog=0, n_rejected_post_pipeline=0,
        )

    env = DiscoveryEnv(
        degree=14,
        reward_shape="step",
        coefficient_choices=tuple(range(-5, 6)),
        seed=seed,
        log_discoveries=False,
    )

    half_len = int(getattr(env, "half_len", 8))
    n_steps_rollout = max(64, 4 * half_len)
    n_steps_rollout = ((n_steps_rollout + 63) // 64) * 64

    # Trajectory accumulators.
    margins: List[float] = []
    band_touch_samples: List[Tuple[int, float, float]] = []
    novel_candidates: List[Dict[str, Any]] = []

    counts = {
        "n_band_touch": 0,
        "n_band_cross": 0,
        "n_sub_lehmer": 0,
        "n_cyclotomic": 0,
        "n_above_band": 0,
        "n_known_in_mossinghoff": 0,
        "n_novel_in_band": 0,
        "n_pipeline_routed": 0,
        "n_promoted": 0,
        "n_shadow_catalog": 0,
        "n_rejected_post_pipeline": 0,
    }
    firsts = {
        "first_band_touch_episode": None,
        "first_band_touch_margin": None,
        "first_band_cross_episode": None,
        "first_band_cross_margin": None,
        "first_sub_lehmer_episode": None,
        "first_sub_lehmer_M": None,
        "first_shadow_catalog_episode": None,
        "first_promote_episode": None,
    }

    pipeline_len_holder = {"value": 0}
    episodes_completed = {"value": 0}
    progress_holder = {"next": progress_every}

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
                M = info.get("mahler_measure", float("inf"))
                M = float(M) if M is not None else float("inf")
                coeffs = info.get("coeffs_full") or [0] * (self._base.degree + 1)
                is_known = info.get("is_known_in_mossinghoff")

                margin = _band_margin(M)
                if margin is not None and math.isfinite(margin):
                    margins.append(margin)
                else:
                    # Use a large positive sentinel for non-finite (rare).
                    margins.append(99.0)

                # Buckets.
                if margin is not None:
                    if margin <= 0:
                        counts["n_band_touch"] += 1
                        if firsts["first_band_touch_episode"] is None:
                            firsts["first_band_touch_episode"] = ep_idx
                            firsts["first_band_touch_margin"] = float(margin)
                    if margin < 0:
                        counts["n_band_cross"] += 1
                        if firsts["first_band_cross_episode"] is None:
                            firsts["first_band_cross_episode"] = ep_idx
                            firsts["first_band_cross_margin"] = float(margin)
                if M < 1.001:
                    counts["n_cyclotomic"] += 1
                elif 1.001 < M < 1.18:
                    counts["n_sub_lehmer"] += 1
                    if firsts["first_sub_lehmer_episode"] is None:
                        firsts["first_sub_lehmer_episode"] = ep_idx
                        firsts["first_sub_lehmer_M"] = float(M)
                elif M >= 1.18:
                    counts["n_above_band"] += 1

                # Capture all band touches as trajectory samples.
                if margin is not None and margin <= 0 and len(band_touch_samples) < 1000:
                    band_touch_samples.append((ep_idx, float(margin), float(M)))

                # Mossinghoff cross-check + pipeline check.
                if 1.001 < M < 1.18:
                    # Sub-Lehmer hit. is_known is the env's Mossinghoff
                    # cross-check at the M level.
                    if is_known:
                        counts["n_known_in_mossinghoff"] += 1
                    else:
                        counts["n_novel_in_band"] += 1
                        # Pull the pipeline record (this is the SAME
                        # env we constructed; the pipeline ran when env
                        # detected sub-Lehmer + not-known).
                        recs = self._base.pipeline_records()
                        rec = None
                        if len(recs) > pipeline_len_holder["value"]:
                            rec = recs[-1]
                            pipeline_len_holder["value"] = len(recs)
                        if rec is not None:
                            counts["n_pipeline_routed"] += 1
                            ts = getattr(rec, "terminal_state", None)
                            if ts == "PROMOTED":
                                counts["n_promoted"] += 1
                                if firsts["first_promote_episode"] is None:
                                    firsts["first_promote_episode"] = ep_idx
                            elif ts == "SHADOW_CATALOG":
                                counts["n_shadow_catalog"] += 1
                                if firsts["first_shadow_catalog_episode"] is None:
                                    firsts["first_shadow_catalog_episode"] = ep_idx
                            else:
                                counts["n_rejected_post_pipeline"] += 1
                            if len(novel_candidates) < 20:
                                novel_candidates.append({
                                    "episode_idx": ep_idx,
                                    "coeffs": list(coeffs),
                                    "M": float(M),
                                    "terminal_state": ts,
                                    "kill_pattern": getattr(rec, "kill_pattern", None),
                                    "candidate_hash": getattr(
                                        rec, "candidate_hash", None
                                    ),
                                })

                episodes_completed["value"] += 1
                if (
                    progress_every > 0
                    and episodes_completed["value"] >= progress_holder["next"]
                ):
                    print(
                        f"  [seed={seed}] {episodes_completed['value']}/{n_episodes} eps "
                        f"| best={min(margins) if margins else float('nan'):.4f} "
                        f"| band_touch={counts['n_band_touch']} "
                        f"| sub_lehmer={counts['n_sub_lehmer']} "
                        f"| novel={counts['n_novel_in_band']}",
                        flush=True,
                    )
                    progress_holder["next"] += progress_every
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

    total_timesteps = int(n_episodes * half_len + n_steps_rollout * 4)
    t0 = time.perf_counter()
    model.learn(
        total_timesteps=total_timesteps,
        callback=_StopAfterN(n_episodes),
        progress_bar=False,
    )
    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    arr = np.asarray(margins, dtype=float) if margins else np.zeros(0)
    if arr.size > 0:
        best_margin = float(arr.min())
        mean_margin = float(arr.mean())
        median_margin = float(np.median(arr))
        std_margin = float(arr.std())
        p10_margin = float(np.percentile(arr, 10))
        p25_margin = float(np.percentile(arr, 25))
        p75_margin = float(np.percentile(arr, 75))
        p90_margin = float(np.percentile(arr, 90))
    else:
        best_margin = float("inf")
        mean_margin = float("nan")
        median_margin = float("nan")
        std_margin = float("nan")
        p10_margin = p25_margin = p75_margin = p90_margin = float("nan")

    return SeedResult(
        seed=seed,
        n_episodes=int(episodes_completed["value"]),
        elapsed_s=float(elapsed),
        first_band_touch_episode=firsts["first_band_touch_episode"],
        first_band_touch_margin=firsts["first_band_touch_margin"],
        first_band_cross_episode=firsts["first_band_cross_episode"],
        first_band_cross_margin=firsts["first_band_cross_margin"],
        first_sub_lehmer_episode=firsts["first_sub_lehmer_episode"],
        first_sub_lehmer_M=firsts["first_sub_lehmer_M"],
        first_shadow_catalog_episode=firsts["first_shadow_catalog_episode"],
        first_promote_episode=firsts["first_promote_episode"],
        best_margin=best_margin,
        mean_margin=mean_margin,
        median_margin=median_margin,
        std_margin=std_margin,
        p10_margin=p10_margin,
        p25_margin=p25_margin,
        p75_margin=p75_margin,
        p90_margin=p90_margin,
        n_band_touch=counts["n_band_touch"],
        n_band_cross=counts["n_band_cross"],
        n_sub_lehmer=counts["n_sub_lehmer"],
        n_cyclotomic=counts["n_cyclotomic"],
        n_above_band=counts["n_above_band"],
        n_known_in_mossinghoff=counts["n_known_in_mossinghoff"],
        n_novel_in_band=counts["n_novel_in_band"],
        n_pipeline_routed=counts["n_pipeline_routed"],
        n_promoted=counts["n_promoted"],
        n_shadow_catalog=counts["n_shadow_catalog"],
        n_rejected_post_pipeline=counts["n_rejected_post_pipeline"],
        band_touch_samples=band_touch_samples,
        novel_candidates=novel_candidates,
    )


# ---------------------------------------------------------------------------
# Pilot orchestrator
# ---------------------------------------------------------------------------


def run_extended_pilot(
    n_episodes_per_seed: int = 100_000,
    seeds: Tuple[int, ...] = (0, 1, 2),
    *,
    progress: bool = True,
) -> Dict[str, Any]:
    """Run the extended PPO pilot.

    Returns a dict with:
      * meta: setup
      * seed_results: List[SeedResult.to_dict()]
      * aggregate: aggregated metrics across seeds
      * elapsed_s: total wall time
    """
    t_global = time.perf_counter()
    seed_results: List[SeedResult] = []

    for s in seeds:
        if progress:
            print(
                f"[ext-ppo] seed={s} target={n_episodes_per_seed} eps...",
                flush=True,
            )
        try:
            sr = run_ppo_extended(n_episodes_per_seed, int(s), progress_every=10000)
        except Exception as e:
            if progress:
                print(f"  ERROR seed={s}: {type(e).__name__}: {e!r}", flush=True)
            sr = SeedResult(
                seed=int(s), n_episodes=0, elapsed_s=0.0,
                first_band_touch_episode=None, first_band_touch_margin=None,
                first_band_cross_episode=None, first_band_cross_margin=None,
                first_sub_lehmer_episode=None, first_sub_lehmer_M=None,
                first_shadow_catalog_episode=None, first_promote_episode=None,
                best_margin=float("inf"), mean_margin=float("nan"),
                median_margin=float("nan"), std_margin=float("nan"),
                p10_margin=float("nan"), p25_margin=float("nan"),
                p75_margin=float("nan"), p90_margin=float("nan"),
                n_band_touch=0, n_band_cross=0, n_sub_lehmer=0,
                n_cyclotomic=0, n_above_band=0, n_known_in_mossinghoff=0,
                n_novel_in_band=0, n_pipeline_routed=0,
                n_promoted=0, n_shadow_catalog=0, n_rejected_post_pipeline=0,
            )
        seed_results.append(sr)
        if progress:
            print(
                f"  -> {sr.n_episodes} eps in {sr.elapsed_s:.1f}s, "
                f"best_margin={sr.best_margin:.4f}, "
                f"band_touch={sr.n_band_touch}, "
                f"sub_lehmer={sr.n_sub_lehmer}, "
                f"novel={sr.n_novel_in_band}, "
                f"shadow={sr.n_shadow_catalog}, "
                f"promote={sr.n_promoted}",
                flush=True,
            )

    # Aggregate across seeds.
    agg = aggregate_seed_results(seed_results)

    elapsed = time.perf_counter() - t_global
    return {
        "meta": {
            "n_episodes_per_seed": int(n_episodes_per_seed),
            "seeds": list(seeds),
            "algorithm": "PPO-MLP",
            "env": {
                "name": "DiscoveryEnv",
                "degree": 14,
                "alphabet_width": 5,
                "alphabet": list(range(-5, 6)),
                "reward_shape": "step",
            },
            "band_definition": "1.001 < M < 1.18 (sub-Lehmer)",
            "navigator_recommendation": "PPO for deg14 ±5 step Lehmer search",
        },
        "seed_results": [sr.to_dict() for sr in seed_results],
        "aggregate": agg,
        "elapsed_s": float(elapsed),
        "verdict": classify_verdict(agg, seed_results),
    }


def aggregate_seed_results(srs: List[SeedResult]) -> Dict[str, Any]:
    """Aggregate per-seed results."""
    if not srs:
        return {}
    total_eps = sum(sr.n_episodes for sr in srs)
    sum_band_touch = sum(sr.n_band_touch for sr in srs)
    sum_band_cross = sum(sr.n_band_cross for sr in srs)
    sum_sub_lehmer = sum(sr.n_sub_lehmer for sr in srs)
    sum_cyclo = sum(sr.n_cyclotomic for sr in srs)
    sum_above = sum(sr.n_above_band for sr in srs)
    sum_known = sum(sr.n_known_in_mossinghoff for sr in srs)
    sum_novel = sum(sr.n_novel_in_band for sr in srs)
    sum_pipeline = sum(sr.n_pipeline_routed for sr in srs)
    sum_promoted = sum(sr.n_promoted for sr in srs)
    sum_shadow = sum(sr.n_shadow_catalog for sr in srs)
    sum_reject = sum(sr.n_rejected_post_pipeline for sr in srs)
    best_margin_overall = (
        min((sr.best_margin for sr in srs if math.isfinite(sr.best_margin)),
            default=float("inf"))
    )
    mean_of_means = float(
        np.mean([sr.mean_margin for sr in srs if math.isfinite(sr.mean_margin)])
    ) if any(math.isfinite(sr.mean_margin) for sr in srs) else float("nan")

    return {
        "total_episodes": int(total_eps),
        "n_band_touch": int(sum_band_touch),
        "n_band_cross": int(sum_band_cross),
        "n_sub_lehmer": int(sum_sub_lehmer),
        "n_cyclotomic": int(sum_cyclo),
        "n_above_band": int(sum_above),
        "n_known_in_mossinghoff": int(sum_known),
        "n_novel_in_band": int(sum_novel),
        "n_pipeline_routed": int(sum_pipeline),
        "n_promoted": int(sum_promoted),
        "n_shadow_catalog": int(sum_shadow),
        "n_rejected_post_pipeline": int(sum_reject),
        "best_margin_overall": float(best_margin_overall),
        "mean_of_seed_means": float(mean_of_means),
    }


def classify_verdict(agg: Dict[str, Any], srs: List[SeedResult]) -> Dict[str, str]:
    """Map aggregate metrics to A/B/C/D verdict per the spec."""
    n_promote = int(agg.get("n_promoted", 0))
    n_shadow = int(agg.get("n_shadow_catalog", 0))
    n_sub_lehmer = int(agg.get("n_sub_lehmer", 0))
    n_band_touch = int(agg.get("n_band_touch", 0))
    n_novel = int(agg.get("n_novel_in_band", 0))
    n_known = int(agg.get("n_known_in_mossinghoff", 0))

    # A: ≥1 SHADOW_CATALOG or PROMOTE not in Mossinghoff.
    if n_shadow > 0 or n_promote > 0:
        return {
            "verdict": "A_NAVIGATOR_VALIDATED",
            "rationale": (
                f"PPO produced {n_shadow} SHADOW_CATALOG and {n_promote} "
                f"PROMOTE entries — non-Mossinghoff in-band candidates that "
                f"survived F1+F6+F9+F11.  First operator-level discovery; "
                f"the kill-space navigator's recommendation of PPO for "
                f"deg14 ±5 is empirically validated. Pause and report."
            ),
        }
    # B: PPO crossed band but only rediscovered Mossinghoff entries.
    if n_sub_lehmer > 0 and n_known > 0 and n_novel == 0:
        return {
            "verdict": "B_BOUNDED_REDISCOVERY",
            "rationale": (
                f"PPO crossed the band {n_sub_lehmer} times (all "
                f"{n_known} Mossinghoff rediscoveries; 0 novel).  "
                f"Operator behaviour matches the navigator recommendation; "
                f"the deg14 ±5 sub-Lehmer subspace appears bounded by "
                f"Lehmer's conjecture — consistent with brute-force "
                f"expectations once the F bug-fix enumeration runs."
            ),
        }
    # C: PPO touched band but never crossed (band edges only, no sub-Lehmer hits).
    if n_band_touch > 0 and n_sub_lehmer == 0:
        return {
            "verdict": "C_STRUCTURALLY_ELUSIVE",
            "rationale": (
                f"PPO touched the band edge {n_band_touch} times but "
                f"never produced a sub-Lehmer in-band poly in {agg.get('total_episodes', 0)} "
                f"episodes.  Operator approaches but doesn't reach; the "
                f"subspace is structurally elusive at this scale "
                f"(or the band-touches were cyclotomic boundary hits)."
            ),
        }
    # D: PPO didn't even touch band at scale.
    return {
        "verdict": "D_OVERESTIMATED_UTILITY",
        "rationale": (
            f"PPO produced {n_band_touch} band-touches and {n_sub_lehmer} "
            f"sub-Lehmer hits in {agg.get('total_episodes', 0)} episodes.  "
            f"The 6K-episode pilot's reach was a lucky outlier; operator-"
            f"utility was overestimated by the navigator."
        ),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(
    out_path: str = "prometheus_math/_extended_ppo_pilot.json",
    n_episodes_per_seed: int = 100_000,
    seeds: Tuple[int, ...] = (0, 1, 2),
) -> Dict[str, Any]:
    """Run the extended PPO pilot and persist results."""
    print(
        f"[ext-ppo] starting extended PPO pilot: "
        f"{len(seeds)} seeds × {n_episodes_per_seed} eps "
        f"= {len(seeds)*n_episodes_per_seed} total"
    )
    result = run_extended_pilot(
        n_episodes_per_seed=n_episodes_per_seed,
        seeds=seeds,
    )
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(result, indent=2, default=str))
    agg = result["aggregate"]
    verdict = result["verdict"]
    print(f"[ext-ppo] wrote {out_p}")
    print(f"[ext-ppo] total wall time: {result['elapsed_s']:.1f}s")
    print(
        f"[ext-ppo] aggregate: band_touch={agg['n_band_touch']}, "
        f"sub_lehmer={agg['n_sub_lehmer']} "
        f"({agg['n_known_in_mossinghoff']} known, {agg['n_novel_in_band']} novel), "
        f"shadow={agg['n_shadow_catalog']}, promote={agg['n_promoted']}, "
        f"best_margin={agg['best_margin_overall']:.4f}"
    )
    print(f"[ext-ppo] VERDICT: {verdict['verdict']}")
    print(f"[ext-ppo] {verdict['rationale']}")
    return result


__all__ = [
    "SeedResult",
    "_band_margin",
    "aggregate_seed_results",
    "classify_verdict",
    "main",
    "run_extended_pilot",
    "run_ppo_extended",
]


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    main(n_episodes_per_seed=n)
