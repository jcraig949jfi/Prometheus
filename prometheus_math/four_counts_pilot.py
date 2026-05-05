"""prometheus_math.four_counts_pilot -- §6.2 + §6.4 unified harness.

Implements the two specs of `harmonia/memory/architecture/discovery_via_rediscovery.md`
that overlap on a single concrete artifact (a uniform-random sampler over
`DiscoveryEnv`'s coefficient action space):

    §6.2  "Run discovery_env for 10K episodes under TWO conditions:
           LLM-driven REINFORCE agent vs uniform-random null sampler.
           Same coefficient action space.  Report PROMOTE rates +
           statistical comparison."

    §6.4  "Add at least one non-LLM mutation source (random reciprocal
           polynomial generation in the discovery_env's coefficient
           space, with no LLM prior shaping)."

The two are shipped as one harness because §6.4's "non-LLM source" IS
§6.2's "uniform-random null sampler" -- both are uniform over the
env's `Discrete(7)` action space, both run through the same
`DiscoveryPipeline`, and both report identical four-count tallies.
The function `run_non_llm_mutation_source` is exposed as an alias
for `run_random_null` to make spec-traceability mechanical.

The "four counts" of the spec are:
    1. catalog-hit -- episode produced a polynomial in Mossinghoff
                       (rediscovery; calibration signal).
    2. claim-into-kernel -- episode's polynomial entered the
                       DiscoveryPipeline and minted a CLAIM (sub-Lehmer
                       band catalog miss).
    3. PROMOTE -- the CLAIM survived the kill-path battery and was
                       promoted (PROMOTED + SHADOW_CATALOG, since both
                       are signal-class survivors).
    4. battery-kill -- the CLAIM was rejected by a battery member
                       (F1 / F6 / F9 / F11 / reducibility / etc).

Honest framing: at 1000 episodes, both PROMOTE rates may be 0 (the
+100 sub-Lehmer band is empirically unreachable per Lehmer's
conjecture).  That is STILL informative -- it bounds the discovery
rate from above.  The harness's job is to surface this bound, not to
manufacture significance.

Usage::

    from prometheus_math.four_counts_pilot import (
        run_random_null, run_reinforce_agent, compare_conditions,
        print_pilot_table,
    )
    from prometheus_math.discovery_env import DiscoveryEnv

    env_factory = lambda: DiscoveryEnv(degree=10)
    cb = {
        "random_null":    lambda f, n, s: run_random_null(f, n, s),
        "reinforce_agent": lambda f, n, s: run_reinforce_agent(
            f, n, s, lr=0.05, entropy_coef=0.05),
    }
    out = compare_conditions(env_factory, n_episodes=1000, seeds=[0, 1, 2],
                              condition_callables=cb)
    print_pilot_table(out)
"""
from __future__ import annotations

import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class FourCountsResult:
    """The four-count tally for one (condition, seed) cell.

    Counts are mutually-comprehensive but NOT mutually-exclusive at the
    bucket level:
      - catalog_hit_count is disjoint from claim_into_kernel_count
        (the env routes catalog-hit episodes upstream of the pipeline).
      - promote_count + shadow_catalog_count + (pipeline-routed rejects)
        sum to claim_into_kernel_count.
      - rejected_count includes pipeline-routed rejects PLUS upstream
        rejections (zero polynomials, out-of-band M, cyclotomic).
    """

    condition_label: str
    total_episodes: int
    catalog_hit_count: int
    claim_into_kernel_count: int
    promote_count: int
    shadow_catalog_count: int
    rejected_count: int
    by_kill_pattern: Dict[str, int] = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    seed: int = 0

    @property
    def promote_rate(self) -> float:
        """PROMOTE rate -- fraction of episodes that produced a
        signal-class survivor (PROMOTED or SHADOW_CATALOG)."""
        if self.total_episodes == 0:
            return 0.0
        return (
            self.promote_count + self.shadow_catalog_count
        ) / self.total_episodes

    @property
    def catalog_hit_rate(self) -> float:
        if self.total_episodes == 0:
            return 0.0
        return self.catalog_hit_count / self.total_episodes

    @property
    def claim_rate(self) -> float:
        if self.total_episodes == 0:
            return 0.0
        return self.claim_into_kernel_count / self.total_episodes


# ---------------------------------------------------------------------------
# Internal: tally an env's outcome per episode
# ---------------------------------------------------------------------------


def _tally_episode_outcome(
    info: Dict[str, Any],
    pipeline_records_before: int,
    env: Any,
    counts: Dict[str, int],
    by_kill_pattern: Dict[str, int],
) -> Tuple[int, Dict[str, int]]:
    """Inspect a finished episode's `info` dict + the env's growing
    `pipeline_records()` list and update the running counts.

    Returns the new pipeline_records length so the caller can detect
    whether THIS episode added a record.
    """
    discovery_flag = info.get("discovery_flag")
    is_known = info.get("is_known_in_mossinghoff")
    reward_label = info.get("reward_label")

    # Catalog hit: the env upstream of the pipeline matched a Mossinghoff
    # entry.  This includes:
    #   - sub_lehmer band hits where is_known=True (discovery_flag starts
    #     with "known_salem:")
    #   - salem_cluster band hits where is_known=True
    if (
        discovery_flag
        and isinstance(discovery_flag, str)
        and discovery_flag.startswith("known_salem:")
    ):
        counts["catalog_hit"] += 1
        return pipeline_records_before, by_kill_pattern
    if reward_label == "salem_cluster" and is_known:
        counts["catalog_hit"] += 1
        return pipeline_records_before, by_kill_pattern

    # Pipeline-routed: the env minted a DiscoveryRecord this episode.
    pipeline_records = env.pipeline_records()
    new_len = len(pipeline_records)
    if new_len > pipeline_records_before:
        # Last record is THIS episode's.
        rec = pipeline_records[-1]
        counts["claim_into_kernel"] += 1
        if rec.terminal_state == "PROMOTED":
            counts["promote"] += 1
        elif rec.terminal_state == "SHADOW_CATALOG":
            counts["shadow_catalog"] += 1
        elif rec.terminal_state == "REJECTED":
            counts["rejected"] += 1
            kp = rec.kill_pattern or "unknown_pipeline_reject"
            by_kill_pattern[kp] = by_kill_pattern.get(kp, 0) + 1
        return new_len, by_kill_pattern

    # Otherwise: rewarded but not catalog-hit and not pipeline-routed.
    # That covers reward_label == "low_m" / "functional" / Salem-cluster
    # not-in-catalog (rare) / cyclotomic / non-finite / out-of-band.
    # We bucket all of these as "rejected" for the four-counts view --
    # they're not signal-class survivors.
    if reward_label is not None:
        counts["rejected"] += 1
        by_kill_pattern["upstream:" + str(reward_label)] = (
            by_kill_pattern.get("upstream:" + str(reward_label), 0) + 1
        )
    else:
        # Defensive: unknown terminal -> still counts as rejected for
        # the partition property to hold.
        counts["rejected"] += 1
        by_kill_pattern["upstream:unknown"] = (
            by_kill_pattern.get("upstream:unknown", 0) + 1
        )
    return new_len, by_kill_pattern


# ---------------------------------------------------------------------------
# Random-null condition (also serves as §6.4's non-LLM source)
# ---------------------------------------------------------------------------


def run_random_null(
    env_factory: Callable[[], Any],
    n_episodes: int,
    seed: int,
) -> FourCountsResult:
    """Uniform-random sampler over the discovery_env's coefficient
    action space.  Every episode picks each coefficient independently
    from the env's Discrete(7) action space; no policy, no obs
    conditioning, no LLM prior.

    This is BOTH:
      - §6.2's "uniform-random null sampler" (the floor REINFORCE must
        beat to claim a learning effect).
      - §6.4's "non-LLM mutation source" (the prior-free baseline that
        determines whether the LLM prior is well-tuned or too tight).

    Each episode runs through `DiscoveryEnv.step()` to completion, then
    catalog-hit / claim-into-kernel / PROMOTE / battery-kill counts are
    tallied off the env's `pipeline_records()` list.

    Args:
        env_factory: zero-arg callable returning a fresh DiscoveryEnv.
        n_episodes: number of full episodes to run.
        seed: RNG seed for action selection.

    Returns:
        FourCountsResult with `condition_label = "random_null"`.

    Raises:
        ValueError: if n_episodes < 0.
    """
    if n_episodes < 0:
        raise ValueError(f"n_episodes must be >= 0, got {n_episodes}")
    if n_episodes == 0:
        return FourCountsResult(
            condition_label="random_null",
            total_episodes=0,
            catalog_hit_count=0,
            claim_into_kernel_count=0,
            promote_count=0,
            shadow_catalog_count=0,
            rejected_count=0,
            by_kill_pattern={},
            elapsed_seconds=0.0,
            seed=seed,
        )

    env = env_factory()
    rng = np.random.default_rng(seed)

    # Get n_actions from env's first reset.
    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions", 7))

    counts = {
        "catalog_hit": 0,
        "claim_into_kernel": 0,
        "promote": 0,
        "shadow_catalog": 0,
        "rejected": 0,
    }
    by_kp: Dict[str, int] = {}
    pipeline_len = 0
    t0 = time.perf_counter()

    for _ in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        while not terminated:
            a = int(rng.integers(0, n_actions))
            obs, r, terminated, _, last_info = env.step(a)
        pipeline_len, by_kp = _tally_episode_outcome(
            last_info, pipeline_len, env, counts, by_kp
        )

    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    return FourCountsResult(
        condition_label="random_null",
        total_episodes=n_episodes,
        catalog_hit_count=counts["catalog_hit"],
        claim_into_kernel_count=counts["claim_into_kernel"],
        promote_count=counts["promote"],
        shadow_catalog_count=counts["shadow_catalog"],
        rejected_count=counts["rejected"],
        by_kill_pattern=by_kp,
        elapsed_seconds=elapsed,
        seed=seed,
    )


# §6.4 spec-clarity alias.  Same function; different name to make the
# spec-to-code mapping mechanical when reviewers go looking for the
# "non-LLM mutation source" the spec calls out.
def run_non_llm_mutation_source(
    env_factory: Callable[[], Any],
    n_episodes: int,
    seed: int,
) -> FourCountsResult:
    """Spec-clarity alias for `run_random_null` (§6.4: 'at least one
    non-LLM mutation source').

    Identical to `run_random_null` -- uniform-random sampling over the
    env's coefficient action space, no LLM prior shaping.  The alias
    exists so that code reading `run_non_llm_mutation_source(...)`
    maps unambiguously to §6.4 of `discovery_via_rediscovery.md`.
    """
    res = run_random_null(env_factory, n_episodes, seed)
    # Re-stamp condition_label for spec-clarity at the call site.
    return FourCountsResult(
        condition_label="non_llm_mutation_source",
        total_episodes=res.total_episodes,
        catalog_hit_count=res.catalog_hit_count,
        claim_into_kernel_count=res.claim_into_kernel_count,
        promote_count=res.promote_count,
        shadow_catalog_count=res.shadow_catalog_count,
        rejected_count=res.rejected_count,
        by_kill_pattern=dict(res.by_kill_pattern),
        elapsed_seconds=res.elapsed_seconds,
        seed=res.seed,
    )


# ---------------------------------------------------------------------------
# REINFORCE agent condition
# ---------------------------------------------------------------------------


def run_reinforce_agent(
    env_factory: Callable[[], Any],
    n_episodes: int,
    seed: int,
    lr: float = 0.05,
    entropy_coef: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
) -> FourCountsResult:
    """The contextual REINFORCE agent of §6.2 ("LLM-driven REINFORCE").

    Reuses `train_reinforce_contextual` from
    `prometheus_math.demo_discovery` -- the obs-conditioned linear
    policy with entropy regularization that beat random by +367.9% on
    the bandit env and rediscovered Salem cluster + OBSTRUCTION_SHAPE.

    Per spec: "LLM-driven" here means policy-driven (the policy is the
    LLM proxy in the contextual-bandit framing -- it conditions on
    structured obs, encodes a learnable prior, and its rollouts are the
    "prompted agent" mutation source §6.4 contrasts with the non-LLM
    source).

    Args:
        env_factory: zero-arg callable returning a fresh DiscoveryEnv.
        n_episodes: number of full episodes to run.
        seed: RNG seed for action selection + policy init.
        lr: REINFORCE learning rate.
        entropy_coef: entropy bonus coefficient (encourages exploration).
        reward_scale: scales raw +100 reward into a sane gradient range.
        baseline_decay: EMA decay for variance-reduction baseline.

    Returns:
        FourCountsResult with `condition_label = "reinforce_agent"`.

    Raises:
        ValueError: if n_episodes < 0.
    """
    if n_episodes < 0:
        raise ValueError(f"n_episodes must be >= 0, got {n_episodes}")
    if n_episodes == 0:
        return FourCountsResult(
            condition_label="reinforce_agent",
            total_episodes=0,
            catalog_hit_count=0,
            claim_into_kernel_count=0,
            promote_count=0,
            shadow_catalog_count=0,
            rejected_count=0,
            by_kill_pattern={},
            elapsed_seconds=0.0,
            seed=seed,
        )

    # Reuse the canonical contextual REINFORCE.  We replicate its policy
    # logic here because we need to count terminal states per-episode
    # (the demo function returns aggregate stats; we need to hook into
    # each episode's tail).
    from .demo_discovery import (
        N_COEFFICIENT_ACTIONS,
    )

    env = env_factory()
    rng = np.random.default_rng(seed)

    # Initial reset to get obs + dimensions.
    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions", N_COEFFICIENT_ACTIONS))
    half_len = int(info0.get("half_len", env.half_len if hasattr(env, "half_len") else 6))
    degree = int(info0.get("degree", env.degree if hasattr(env, "degree") else 10))
    obs_dim = 7 + degree

    # Linear policy: logits = W[step] @ obs + b[step].
    W = np.zeros((half_len, n_actions, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, n_actions), dtype=np.float64)
    baseline = 0.0

    counts = {
        "catalog_hit": 0,
        "claim_into_kernel": 0,
        "promote": 0,
        "shadow_catalog": 0,
        "rejected": 0,
    }
    by_kp: Dict[str, int] = {}
    pipeline_len = 0
    t0 = time.perf_counter()

    for _ in range(n_episodes):
        obs, _ = env.reset()
        actions: List[int] = []
        observations: List[np.ndarray] = []
        cum_reward = 0.0
        terminated = False
        step_idx = 0
        last_info: Dict[str, Any] = {}
        while not terminated:
            l = W[step_idx] @ obs + b[step_idx]
            probs = np.exp(l - l.max())
            probs /= probs.sum()
            a = int(rng.choice(len(probs), p=probs))
            actions.append(a)
            observations.append(obs.copy())
            obs, r, terminated, _, last_info = env.step(a)
            cum_reward += r
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

        pipeline_len, by_kp = _tally_episode_outcome(
            last_info, pipeline_len, env, counts, by_kp
        )

    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    return FourCountsResult(
        condition_label="reinforce_agent",
        total_episodes=n_episodes,
        catalog_hit_count=counts["catalog_hit"],
        claim_into_kernel_count=counts["claim_into_kernel"],
        promote_count=counts["promote"],
        shadow_catalog_count=counts["shadow_catalog"],
        rejected_count=counts["rejected"],
        by_kill_pattern=by_kp,
        elapsed_seconds=elapsed,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# PPO agent condition (path B — stronger algorithm than REINFORCE)
# ---------------------------------------------------------------------------


def run_ppo_agent(
    env_factory: Callable[[], Any],
    n_episodes: int,
    seed: int,
    n_steps_rollout: Optional[int] = None,
    verbose: int = 0,
) -> FourCountsResult:
    """PPO agent over the same DiscoveryEnv action space (§6.2 path B).

    Runs ``stable_baselines3.PPO`` with default hyperparameters
    (Adam, GAE-lambda=0.95, clip_range=0.2, MlpPolicy 64-64) for
    ``total_timesteps = n_episodes * episode_length`` on a single env
    instance, tallying outcomes from each terminal step's info dict
    via an SB3 callback. This is the live training run — we tally
    discovery outcomes *during* training, not via post-hoc rollout, so
    the count reflects the agent's policy as it learns.

    If ``stable_baselines3`` is not installed, returns a
    FourCountsResult flagged with ``condition_label='ppo_agent_skipped'``
    so the comparison harness can surface the skip in the pairwise
    table without crashing.

    Args:
        env_factory: zero-arg callable returning a fresh DiscoveryEnv.
        n_episodes: number of full episodes to run (=> total_timesteps =
            n_episodes * env.half_len).
        seed: RNG seed for SB3 + env.
        n_steps_rollout: PPO rollout buffer size (>= 4 * episode_length
            recommended). Default: max(64, 4 * half_len).
        verbose: SB3 verbosity (0 = silent, 1 = progress, 2 = debug).

    Returns:
        FourCountsResult with `condition_label = "ppo_agent"`.

    Raises:
        ValueError: if n_episodes < 0.
    """
    if n_episodes < 0:
        raise ValueError(f"n_episodes must be >= 0, got {n_episodes}")
    if n_episodes == 0:
        return FourCountsResult(
            condition_label="ppo_agent",
            total_episodes=0,
            catalog_hit_count=0,
            claim_into_kernel_count=0,
            promote_count=0,
            shadow_catalog_count=0,
            rejected_count=0,
            by_kill_pattern={},
            elapsed_seconds=0.0,
            seed=seed,
        )

    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import BaseCallback
        from stable_baselines3.common.vec_env import DummyVecEnv
    except ImportError as e:
        # SB3 missing — skip with a flagged FourCountsResult so callers
        # can detect and surface the skip in the comparison table.
        return FourCountsResult(
            condition_label="ppo_agent_skipped",
            total_episodes=0,
            catalog_hit_count=0,
            claim_into_kernel_count=0,
            promote_count=0,
            shadow_catalog_count=0,
            rejected_count=0,
            by_kill_pattern={"sb3_missing": 1},
            elapsed_seconds=0.0,
            seed=seed,
        )

    # Build the env once and wrap it for SB3 (it auto-resets on
    # termination, but we want to keep `_pipeline_records` accumulating
    # so the four-counts tally is correct).
    env = env_factory()
    half_len = int(getattr(env, "half_len", 6))
    if n_steps_rollout is None:
        n_steps_rollout = max(64, 4 * half_len)

    # Tally state — closed over by the callback below.
    counts = {
        "catalog_hit": 0,
        "claim_into_kernel": 0,
        "promote": 0,
        "shadow_catalog": 0,
        "rejected": 0,
    }
    by_kp: Dict[str, int] = {}
    pipeline_len_holder = {"value": 0}
    episodes_completed = {"value": 0}

    # SB3-compatible Env wrapper. Inherit from gymnasium.Env so
    # DummyVecEnv's isinstance checks pass.
    try:
        import gymnasium as gym

        gym_base = gym.Env
    except ImportError:
        gym_base = object  # type: ignore[assignment]

    class _DiscoveryGymWrapper(gym_base):  # type: ignore[misc, valid-type]
        """Wrap DiscoveryEnv for SB3 PPO; tally outcomes on each terminal
        step before the auto-reset clobbers them."""

        metadata = {"render_modes": []}

        def __init__(self, base: Any, n_max_episodes: int):
            self._base = base
            self.observation_space = base.observation_space
            self.action_space = base.action_space
            self.spec = None
            self.render_mode = None
            self._n_max = n_max_episodes
            self._stop = False

        def reset(self, *, seed: Optional[int] = None, options: Optional[Dict] = None):
            obs, info = self._base.reset(seed=seed)
            return np.asarray(obs, dtype=np.float32), info

        def step(self, action):
            obs, r, term, trunc, info = self._base.step(int(action))
            obs = np.asarray(obs, dtype=np.float32)
            # Tally on episode boundary.
            if term or trunc:
                if not self._stop:
                    pipeline_len_holder["value"], _by_kp = _tally_episode_outcome(
                        info,
                        pipeline_len_holder["value"],
                        self._base,
                        counts,
                        by_kp,
                    )
                    episodes_completed["value"] += 1
                    if episodes_completed["value"] >= self._n_max:
                        self._stop = True
            return obs, float(r), bool(term), bool(trunc), info

        def close(self):
            return self._base.close()

        def render(self):
            return None

    # Vec env with single underlying env so pipeline_records
    # accumulates correctly.
    wrapper_holder: Dict[str, Any] = {}

    def _make() -> Any:
        w = _DiscoveryGymWrapper(env, n_episodes)
        wrapper_holder["env"] = w
        return w

    vec = DummyVecEnv([_make])

    # n_steps must be a multiple of batch_size (default 64). Round up.
    n_steps_rollout = ((n_steps_rollout + 63) // 64) * 64

    model = PPO(
        "MlpPolicy",
        vec,
        seed=int(seed),
        n_steps=n_steps_rollout,
        verbose=int(verbose),
        device="cpu",  # avoid CUDA warning; tiny MLP, CPU is faster
    )

    class _StopAfterNEpisodes(BaseCallback):
        """Halt training once the wrapped env has completed n_episodes."""

        def __init__(self, n_episodes_target: int):
            super().__init__()
            self._target = n_episodes_target

        def _on_step(self) -> bool:
            return episodes_completed["value"] < self._target

    # Generous timestep cap so the callback's stop signal is the actual
    # terminator. Each episode is half_len steps; allow some slack for
    # mid-rollout stop.
    total_timesteps = int(n_episodes * half_len + n_steps_rollout * 2)

    t0 = time.perf_counter()
    model.learn(
        total_timesteps=total_timesteps,
        callback=_StopAfterNEpisodes(n_episodes),
        progress_bar=False,
    )
    elapsed = time.perf_counter() - t0

    try:
        env.close()
    except Exception:
        pass

    actual_episodes = episodes_completed["value"]
    return FourCountsResult(
        condition_label="ppo_agent",
        total_episodes=actual_episodes,
        catalog_hit_count=counts["catalog_hit"],
        claim_into_kernel_count=counts["claim_into_kernel"],
        promote_count=counts["promote"],
        shadow_catalog_count=counts["shadow_catalog"],
        rejected_count=counts["rejected"],
        by_kill_pattern=by_kp,
        elapsed_seconds=elapsed,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Comparison harness
# ---------------------------------------------------------------------------


def _welch_t_test_one_sided(
    a: np.ndarray, b: np.ndarray
) -> float:
    """Welch one-sided t-test: H1 = mean(a) > mean(b).  Returns NaN if
    either array has < 2 samples (variance undefined)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size < 2:
        return float("nan")
    ma, mb = float(a.mean()), float(b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    se_sq = va / a.size + vb / b.size
    if se_sq <= 0.0:
        return 0.0 if ma > mb else 1.0
    se = math.sqrt(se_sq)
    t = (ma - mb) / se
    df = (
        se_sq ** 2
        / ((va / a.size) ** 2 / (a.size - 1) + (vb / b.size) ** 2 / (b.size - 1))
    )
    try:
        from scipy.stats import t as student_t

        return float(1.0 - student_t.cdf(t, df=df))
    except Exception:
        # Normal approximation fallback.
        return float(0.5 * (1.0 - math.erf(t / math.sqrt(2.0))))


def compare_conditions(
    env_factory: Callable[[], Any],
    n_episodes: int,
    seeds: List[int],
    condition_callables: Dict[str, Callable[..., FourCountsResult]],
) -> Dict[str, Any]:
    """Run each (condition, seed) cell, aggregate per-condition stats,
    and emit pairwise Welch t-tests on PROMOTE rates.

    Args:
        env_factory: zero-arg callable producing a fresh env per cell.
        n_episodes: episodes per cell.
        seeds: list of seeds to run each condition over.
        condition_callables: dict mapping condition_label ->
            callable(env_factory, n_episodes, seed) -> FourCountsResult.

    Returns:
        {
            "per_condition": {
                <label>: {
                    "promote_rate_mean": float,
                    "promote_rate_std": float,
                    "promote_rates": list[float],
                    "catalog_hit_rate_mean": float,
                    "claim_rate_mean": float,
                    "results": list[FourCountsResult],
                },
                ...
            },
            "pairwise": {
                (a, b): {"p_value": float, "lift": float,
                         "winner": str | None},
                ...
            },
            "n_episodes": int,
            "n_seeds": int,
            "annotation": str | None,
        }

    Raises:
        ValueError: if condition_callables is empty.
    """
    if not condition_callables:
        raise ValueError("condition_callables must be non-empty")
    n_seeds = len(seeds)

    # Per-condition results.
    per_condition: Dict[str, Dict[str, Any]] = {}
    for label, fn in condition_callables.items():
        results: List[FourCountsResult] = []
        for s in seeds:
            res = fn(env_factory, n_episodes, int(s))
            results.append(res)
        promote_rates = np.array(
            [r.promote_rate for r in results], dtype=np.float64
        )
        catalog_hit_rates = np.array(
            [r.catalog_hit_rate for r in results], dtype=np.float64
        )
        claim_rates = np.array(
            [r.claim_rate for r in results], dtype=np.float64
        )
        per_condition[label] = {
            "promote_rate_mean": float(promote_rates.mean()) if promote_rates.size else 0.0,
            "promote_rate_std": (
                float(promote_rates.std(ddof=1)) if promote_rates.size > 1 else 0.0
            ),
            "promote_rates": promote_rates.tolist(),
            "catalog_hit_rate_mean": (
                float(catalog_hit_rates.mean()) if catalog_hit_rates.size else 0.0
            ),
            "claim_rate_mean": (
                float(claim_rates.mean()) if claim_rates.size else 0.0
            ),
            "results": results,
        }

    # Pairwise Welch t-tests on per-seed PROMOTE rates.
    pairwise: Dict[Tuple[str, str], Dict[str, Any]] = {}
    labels = list(condition_callables.keys())
    for a, b in itertools.combinations(labels, 2):
        rates_a = np.array(per_condition[a]["promote_rates"], dtype=np.float64)
        rates_b = np.array(per_condition[b]["promote_rates"], dtype=np.float64)
        ma = float(rates_a.mean()) if rates_a.size else 0.0
        mb = float(rates_b.mean()) if rates_b.size else 0.0
        # Two one-sided tests; report the directional one.
        if ma >= mb:
            p = _welch_t_test_one_sided(rates_a, rates_b)
            winner = a if (not math.isnan(p)) and p < 0.05 else None
            lift_dir = (ma - mb) / max(mb, 1e-12) if mb > 0 else (
                float("inf") if ma > 0 else 0.0
            )
        else:
            p = _welch_t_test_one_sided(rates_b, rates_a)
            winner = b if (not math.isnan(p)) and p < 0.05 else None
            lift_dir = (mb - ma) / max(ma, 1e-12) if ma > 0 else (
                float("inf") if mb > 0 else 0.0
            )
        pairwise[(a, b)] = {
            "p_value": p,
            "lift": lift_dir,
            "winner": winner,
            "mean_a": ma,
            "mean_b": mb,
        }

    annotation: Optional[str] = None
    if n_seeds < 2:
        annotation = (
            f"n_seeds={n_seeds}: Welch t-test undefined (variance requires "
            f">=2 samples).  All p-values reported as NaN."
        )

    return {
        "per_condition": per_condition,
        "pairwise": pairwise,
        "n_episodes": int(n_episodes),
        "n_seeds": int(n_seeds),
        "annotation": annotation,
    }


# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------


def print_pilot_table(results: Dict[str, Any]) -> None:
    """Pretty-print the agent-vs-null table.  Honest framing:
    explicitly notes when both rates are zero (joint upper bound on
    discovery rate) instead of silently reporting 'no significance'."""
    n_episodes = results.get("n_episodes", 0)
    n_seeds = results.get("n_seeds", 0)
    print("=" * 78)
    print(
        f"FOUR-COUNTS PILOT  n_episodes={n_episodes} per cell  n_seeds={n_seeds}"
    )
    print("=" * 78)
    header = (
        f"{'condition':<28}{'PROMOTE rate':>14}{'cat-hit rate':>14}"
        f"{'claim rate':>14}"
    )
    print(header)
    print("-" * 78)
    for label, info in results["per_condition"].items():
        pr = info["promote_rate_mean"]
        ch = info["catalog_hit_rate_mean"]
        cl = info["claim_rate_mean"]
        std = info["promote_rate_std"]
        print(
            f"{label:<28}{pr:>10.4f} +/-{std:.4f}{ch:>14.4f}{cl:>14.4f}"
        )
    print("-" * 78)
    if results["pairwise"]:
        print("\nPairwise Welch t-tests (one-sided on PROMOTE rate):")
        for (a, b), info in results["pairwise"].items():
            p = info["p_value"]
            lift = info["lift"]
            ma = info["mean_a"]
            mb = info["mean_b"]
            winner = info["winner"]
            both_zero = ma == 0.0 and mb == 0.0
            if both_zero:
                tag = (
                    "TIED-AT-ZERO (both PROMOTE rates 0; joint upper bound on "
                    "discovery rate at this configuration)"
                )
            elif winner is None:
                tag = "no significance"
            else:
                tag = f"WINNER: {winner}"
            p_str = "NaN" if math.isnan(p) else f"{p:.3e}"
            lift_str = "inf" if math.isinf(lift) else f"{lift:+.2f}x"
            print(
                f"  {a}  vs  {b}:  p={p_str}  lift={lift_str}  "
                f"({ma:.4f} vs {mb:.4f}) -- {tag}"
            )
    if results.get("annotation"):
        print(f"\nNote: {results['annotation']}")
    print("=" * 78)


__all__ = [
    "FourCountsResult",
    "run_random_null",
    "run_non_llm_mutation_source",
    "run_reinforce_agent",
    "run_ppo_agent",
    "compare_conditions",
    "print_pilot_table",
]
