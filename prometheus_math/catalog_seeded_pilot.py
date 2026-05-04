"""prometheus_math.catalog_seeded_pilot — Hypothesis-2 stress test.

Sidecar driver that warm-starts the Lehmer/Mahler-measure search policy
at known small-M neighborhoods (Mossinghoff polynomials with ``max|c|
>= 4`` at degree >= 12).  This is the strictest remaining live test of
"is REINFORCE+linear too weak?" for the 0-PROMOTE ceiling on
``DiscoveryEnv``: if the policy is initialized to bias toward the
regions where catalog small-M polynomials live, and STILL fails to
reach sub-Lehmer territory, then Hypothesis 1 (Lehmer's conjecture /
structural emptiness in (1.001, 1.18)) is essentially won.

Conventions
-----------
The Mossinghoff snapshot stores coefficients in **ascending** order
``[a_0, a_1, ..., a_n]``.  ``DiscoveryEnv`` builds a palindromic poly
from the agent's first ``half_len = degree//2 + 1`` picks and mirrors
``a_{degree-i} = a_i``, so we extract per-step coefficient priors from
the **first** ``half_len`` ascending coefficients of each catalog poly.
For seeds whose degree differs from the env's degree, we project by
truncating to ``half_len`` (catalog deg >= env deg) or padding with the
seed's own first half (catalog deg < env deg) before computing priors.

Public API
----------
* ``extract_seed_polynomials(min_abs_coef, degree_range)`` -- pull
  matching polys from the catalog.
* ``compute_action_priors(seed_polys, degree, coefficient_choices)``
  -- per-step marginal distribution over the env's action set.
* ``seeded_random_baseline(env_factory, action_priors, n_episodes,
  seed)`` -- random sampling biased by the action priors per step.
* ``seeded_reinforce_agent(env_factory, action_priors, n_episodes,
  seed, lr, entropy_coef)`` -- REINFORCE with logits warm-started to
  ``log(action_priors)`` at each step.
* ``compare_seeded_vs_unseeded(env_factory, n_episodes, seeds)`` --
  4-arm pilot (random uniform, random seeded, REINFORCE uniform,
  REINFORCE seeded).

Honest framing
--------------
This module implements ONE specific seeding strategy: per-step
marginal coefficient distributions over a curated subset of catalog
polys.  Alternative seedings (root-space sampling near Salem polys;
Bayesian priors over coefficient vectors; mixture-of-poly priors) are
explicitly NOT tested here.  A negative result strengthens hypothesis
1 but does not disprove hypothesis 2.

Forged: 2026-04-29 by Techne (pilot driver, no env edits).
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.four_counts_pilot import (
    FourCountsResult,
    _tally_episode_outcome,
    _welch_t_test_one_sided,
)


# ---------------------------------------------------------------------------
# Seed pool extraction
# ---------------------------------------------------------------------------


def extract_seed_polynomials(
    min_abs_coef: int = 4,
    degree_range: Tuple[int, int] = (12, 18),
) -> List[Dict[str, Any]]:
    """Pull catalog polys matching ``max|c| >= min_abs_coef`` and
    ``degree in [degree_range[0], degree_range[1]]``.

    Parameters
    ----------
    min_abs_coef : int, default 4
        Minimum value of ``max(|c_i|)`` over the polynomial's
        ascending coefficients.
    degree_range : (int, int), default (12, 18)
        Inclusive degree band.  Pass ``(0, 1000)`` to disable.

    Returns
    -------
    list of dict
        One entry per matching catalog poly with fields:
        ``coeffs`` (ascending list), ``degree`` (int),
        ``mahler_measure`` (float), ``label`` (str -- catalog name).
        Empty list if no matches.

    Notes
    -----
    The Mossinghoff snapshot has 8625 entries as of refresh
    2026-04-29; the strict (max|c| >= 4, deg in [12, 18]) filter
    yields 4 entries.  Callers wanting a richer seed pool typically
    broaden the degree range and project to the env's half-length in
    ``compute_action_priors``.
    """
    from prometheus_math.databases.mahler import MAHLER_TABLE

    lo, hi = int(degree_range[0]), int(degree_range[1])
    out: List[Dict[str, Any]] = []
    for e in MAHLER_TABLE:
        d = int(e["degree"])
        if d < lo or d > hi:
            continue
        coeffs = list(e["coeffs"])
        if not coeffs:
            continue
        if max(abs(c) for c in coeffs) < int(min_abs_coef):
            continue
        out.append({
            "coeffs": coeffs,
            "degree": d,
            "mahler_measure": float(e["mahler_measure"]),
            "label": e.get("name") or e.get("label") or f"deg{d}_M{e['mahler_measure']:.4f}",
        })
    return out


def extract_seed_polynomials_broad(
    env_degree: int,
    coefficient_choices: Tuple[int, ...],
    min_abs_coef: int = 4,
) -> List[Dict[str, Any]]:
    """Broad seed extraction: any catalog poly with max|c| >= ``min_abs_coef``
    whose ascending coefficients ALL fit within the env's coefficient
    alphabet.  Used when the strict (env_degree only) filter yields too
    few entries.

    The seed coeffs are projected to env_degree by truncating to
    ``half_len = env_degree // 2 + 1`` ascending coeffs.  Polys whose
    half is entirely zero or which contain coefficients outside the
    alphabet are dropped.

    Parameters
    ----------
    env_degree : int
        The env's degree (target for projection).
    coefficient_choices : tuple of int
        The env's coefficient alphabet.  Polys with any of their first
        ``half_len`` ascending coeffs OUTSIDE this alphabet are dropped.
    min_abs_coef : int, default 4
        Minimum max|c| for inclusion (applied to the projected half).

    Returns
    -------
    list of dict
        Same schema as ``extract_seed_polynomials``, but with an extra
        field ``half_coeffs`` holding the env-projected ascending half.
    """
    from prometheus_math.databases.mahler import MAHLER_TABLE

    half_len = env_degree // 2 + 1
    alphabet = set(int(c) for c in coefficient_choices)
    out: List[Dict[str, Any]] = []
    for e in MAHLER_TABLE:
        coeffs = list(e["coeffs"])
        if len(coeffs) < half_len:
            continue
        # Apply max|c| filter to the FULL polynomial -- we want to seed
        # toward known low-M neighborhoods regardless of which half the
        # extremal coefficient sits in.  The half-coeff alphabet check
        # below ensures the seed is REPRESENTABLE in the env's action
        # space; the max|c| check ensures it's catalog-relevant.
        if max(abs(int(c)) for c in coeffs) < int(min_abs_coef):
            continue
        half = coeffs[:half_len]
        if any(int(c) not in alphabet for c in half):
            continue
        if all(int(c) == 0 for c in half):
            continue
        out.append({
            "coeffs": coeffs,
            "half_coeffs": [int(c) for c in half],
            "degree": int(e["degree"]),
            "mahler_measure": float(e["mahler_measure"]),
            "label": e.get("name") or e.get("label")
                    or f"deg{e['degree']}_M{e['mahler_measure']:.4f}",
        })
    return out


# ---------------------------------------------------------------------------
# Action prior construction
# ---------------------------------------------------------------------------


def compute_action_priors(
    seed_polys: List[Dict[str, Any]],
    degree: int,
    coefficient_choices: Tuple[int, ...],
    smoothing: float = 0.05,
) -> Dict[int, np.ndarray]:
    """Per-step marginal distribution over coefficient values.

    For each step ``i`` in ``[0, half_len)`` (where
    ``half_len = degree // 2 + 1``), we tabulate the empirical
    distribution of ``coeffs[i]`` across the seed pool, projected to
    the env's coefficient alphabet ``coefficient_choices``.

    Parameters
    ----------
    seed_polys : list of dict
        Output of ``extract_seed_polynomials*``.  Each dict has either
        a ``half_coeffs`` field (preferred; pre-projected to the env
        half) or a ``coeffs`` field (full ascending list; we truncate
        to half_len).
    degree : int
        Env degree.  Determines half_len.
    coefficient_choices : tuple of int
        Env's action set, in policy-action order.
    smoothing : float, default 0.05
        Laplace-smoothing alpha (fraction of mass added uniformly to
        every action).  Prevents hard zeros that would freeze REINFORCE
        gradients.  ``0.0`` for raw empirical priors.

    Returns
    -------
    dict ``{step: np.ndarray of shape (n_actions,)}``
        Per-step probability distribution over the env's actions.
        Each distribution sums to 1.  If ``seed_polys`` is empty,
        every step gets a uniform distribution.

    Edge cases
    ----------
    * Empty seed pool -> uniform per step.
    * Single seed poly -> a near-degenerate distribution at that
      poly's coefficients (with ``smoothing`` mass spread over the rest).
    * Degree mismatch (a seed poly's degree != env degree) -> we use
      the seed's first ``half_len`` ascending coefficients (padding
      with the seed's last coefficient if too short).
    """
    half_len = degree // 2 + 1
    n_actions = len(coefficient_choices)
    coef_to_action = {int(c): i for i, c in enumerate(coefficient_choices)}

    if not seed_polys:
        priors: Dict[int, np.ndarray] = {}
        for s in range(half_len):
            priors[s] = np.ones(n_actions, dtype=np.float64) / n_actions
        return priors

    counts = np.zeros((half_len, n_actions), dtype=np.float64)
    for entry in seed_polys:
        if "half_coeffs" in entry and len(entry["half_coeffs"]) >= half_len:
            half = list(entry["half_coeffs"])[:half_len]
        else:
            full = list(entry["coeffs"])
            if len(full) < half_len:
                # Pad with last coeff (or 0 if empty)
                pad = full[-1] if full else 0
                full = full + [pad] * (half_len - len(full))
            half = full[:half_len]

        for s, c in enumerate(half):
            ci = int(c)
            if ci in coef_to_action:
                counts[s, coef_to_action[ci]] += 1.0
            # If a seed coefficient is outside the env alphabet, skip
            # it for that step (the per-step row will sum to fewer
            # than len(seed_polys), and smoothing handles zero rows).

    priors: Dict[int, np.ndarray] = {}
    alpha = float(smoothing)
    for s in range(half_len):
        row = counts[s].copy()
        total = row.sum()
        if total < 1e-12:
            # No usable seed at this step -> uniform.
            priors[s] = np.ones(n_actions, dtype=np.float64) / n_actions
            continue
        emp = row / total
        # Mix with uniform smoothing.
        priors[s] = (1.0 - alpha) * emp + alpha * (np.ones(n_actions) / n_actions)
        # Renormalize against floating slop.
        priors[s] = priors[s] / priors[s].sum()
    return priors


# ---------------------------------------------------------------------------
# Sampling helpers
# ---------------------------------------------------------------------------


def _sample_from_prior(rng: np.random.Generator,
                       prior: np.ndarray) -> int:
    """Sample an action index from a categorical prior."""
    p = np.asarray(prior, dtype=np.float64)
    p = np.clip(p, 0.0, None)
    s = p.sum()
    if s <= 0.0:
        # Defensive fallback: uniform.
        return int(rng.integers(0, len(p)))
    p = p / s
    return int(rng.choice(len(p), p=p))


def _serialize_record(rec) -> Dict[str, Any]:
    """Cherry-pick the fields we want to log per pipeline record."""
    out = {
        "candidate_hash": getattr(rec, "candidate_hash", None),
        "coeffs": list(getattr(rec, "coeffs", []) or []),
        "mahler_measure": float(getattr(rec, "mahler_measure", 0.0) or 0.0),
        "terminal_state": getattr(rec, "terminal_state", None),
        "kill_pattern": getattr(rec, "kill_pattern", None),
        "claim_id": getattr(rec, "claim_id", None),
        "symbol_ref": getattr(rec, "symbol_ref", None),
    }
    return out


# ---------------------------------------------------------------------------
# Seeded random baseline
# ---------------------------------------------------------------------------


def seeded_random_baseline(
    env_factory: Callable[[], Any],
    action_priors: Dict[int, np.ndarray],
    n_episodes: int,
    seed: int,
) -> Dict[str, Any]:
    """Random sampling BIASED by the per-step action priors.

    At each step ``s``, the agent samples an action from
    ``action_priors[s]`` instead of from a uniform distribution.  The
    rest of the loop is identical to ``run_random_null``: no learning,
    no observation conditioning, no policy gradient -- this is the
    natural baseline against which seeded-REINFORCE is compared.

    Returns
    -------
    dict
        ``{"result": FourCountsResult, "details": {...}}`` where
        ``details`` contains catalog hits, promotes, shadow-catalog
        entries, and proxy concentration counts.
    """
    if n_episodes < 0:
        raise ValueError(f"n_episodes must be >= 0; got {n_episodes}")
    env = env_factory()
    rng = np.random.default_rng(seed)
    obs, info = env.reset(seed=seed)
    n_actions = int(info.get("n_actions"))
    half_len = int(info.get("half_len", env.half_len))

    counts = {
        "catalog_hit": 0, "claim_into_kernel": 0,
        "promote": 0, "shadow_catalog": 0, "rejected": 0,
    }
    by_kp: Dict[str, int] = {}
    catalog_hits: List[Dict[str, Any]] = []
    promotes: List[Dict[str, Any]] = []
    shadow_catalog: List[Dict[str, Any]] = []
    salem_cluster_hits = 0
    low_m_hits = 0
    pipeline_len = 0

    t0 = time.perf_counter()
    for ep in range(n_episodes):
        env.reset()
        terminated = False
        last_info: Dict[str, Any] = {}
        step_idx = 0
        while not terminated:
            prior = action_priors.get(step_idx)
            if prior is None:
                a = int(rng.integers(0, n_actions))
            else:
                a = _sample_from_prior(rng, prior)
            obs, r, terminated, _, last_info = env.step(a)
            step_idx += 1

        rl = last_info.get("reward_label")
        if rl == "salem_cluster":
            salem_cluster_hits += 1
        elif rl == "low_m":
            low_m_hits += 1

        df = last_info.get("discovery_flag")
        if df and isinstance(df, str) and df.startswith("known_salem:"):
            catalog_hits.append({
                "seed": seed, "episode": ep, "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs_full", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl,
            })
        elif rl == "salem_cluster" and last_info.get("is_known_in_mossinghoff"):
            catalog_hits.append({
                "seed": seed, "episode": ep, "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs_full", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl, "via": "salem_cluster_known",
            })

        new_len, by_kp = _tally_episode_outcome(
            last_info, pipeline_len, env, counts, by_kp
        )
        if new_len > pipeline_len:
            rec = env.pipeline_records()[-1]
            if rec.terminal_state == "PROMOTED":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                promotes.append(d)
            elif rec.terminal_state == "SHADOW_CATALOG":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                shadow_catalog.append(d)
        pipeline_len = new_len

    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    res = FourCountsResult(
        condition_label="random_seeded",
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
    return {
        "result": res,
        "details": {
            "catalog_hits": catalog_hits,
            "promotes": promotes,
            "shadow_catalog": shadow_catalog,
            "salem_cluster_proxy_hits": salem_cluster_hits,
            "low_m_proxy_hits": low_m_hits,
            "seed": seed,
        },
    }


# ---------------------------------------------------------------------------
# Seeded REINFORCE
# ---------------------------------------------------------------------------


def seeded_reinforce_agent(
    env_factory: Callable[[], Any],
    action_priors: Dict[int, np.ndarray],
    n_episodes: int,
    seed: int,
    lr: float = 0.05,
    entropy_coef: float = 0.05,
    reward_scale: float = 1.0 / 100.0,
    baseline_decay: float = 0.95,
    prior_strength: float = 1.0,
) -> Dict[str, Any]:
    """REINFORCE with WARM-STARTED LOGITS at log(action_priors).

    The policy is a per-step linear softmax: at step ``s``, given
    observation ``o``, the action distribution is::

        logits = W[s] @ o + b[s]
        probs  = softmax(logits)

    The catalog-seeded variant initializes ``b[s] = prior_strength *
    log(action_priors[s])`` (W still starts at zero).  After warm
    start, REINFORCE updates W[s] and b[s] with policy-gradient +
    entropy-regularization terms exactly as the unseeded variant.

    Parameters
    ----------
    prior_strength : float, default 1.0
        Multiplier on the log-prior bias.  ``1.0`` gives the literal
        catalog marginal as the start; values > 1 sharpen the prior
        further; ``0.0`` collapses to the unseeded variant.

    Returns
    -------
    dict
        Same shape as ``seeded_random_baseline``.
    """
    if n_episodes < 0:
        raise ValueError(f"n_episodes must be >= 0; got {n_episodes}")
    env = env_factory()
    rng = np.random.default_rng(seed)

    _, info0 = env.reset(seed=seed)
    n_actions = int(info0.get("n_actions"))
    half_len = int(info0.get("half_len", env.half_len))
    degree = int(info0.get("degree", env.degree))
    obs_dim = 7 + degree

    # Linear policy: logits = W[s] @ obs + b[s].
    W = np.zeros((half_len, n_actions, obs_dim), dtype=np.float64)
    b = np.zeros((half_len, n_actions), dtype=np.float64)

    # Warm-start the bias logits to log(action_priors[s]).
    eps = 1e-9
    for s in range(half_len):
        prior = action_priors.get(s)
        if prior is None:
            continue
        prior = np.asarray(prior, dtype=np.float64)
        if prior.shape != (n_actions,):
            raise ValueError(
                f"action_priors[{s}] has shape {prior.shape}; expected ({n_actions},)"
            )
        log_p = np.log(np.clip(prior, eps, None))
        # Center: remove the mean so logits are anchored without a global offset.
        log_p = log_p - log_p.mean()
        b[s] = prior_strength * log_p

    baseline = 0.0

    counts = {
        "catalog_hit": 0, "claim_into_kernel": 0,
        "promote": 0, "shadow_catalog": 0, "rejected": 0,
    }
    by_kp: Dict[str, int] = {}
    catalog_hits: List[Dict[str, Any]] = []
    promotes: List[Dict[str, Any]] = []
    shadow_catalog: List[Dict[str, Any]] = []
    salem_cluster_hits = 0
    low_m_hits = 0
    pipeline_len = 0

    t0 = time.perf_counter()
    for ep in range(n_episodes):
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

        rl = last_info.get("reward_label")
        if rl == "salem_cluster":
            salem_cluster_hits += 1
        elif rl == "low_m":
            low_m_hits += 1

        df = last_info.get("discovery_flag")
        if df and isinstance(df, str) and df.startswith("known_salem:"):
            catalog_hits.append({
                "seed": seed, "episode": ep, "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs_full", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl,
            })
        elif rl == "salem_cluster" and last_info.get("is_known_in_mossinghoff"):
            catalog_hits.append({
                "seed": seed, "episode": ep, "discovery_flag": df,
                "coeffs": list(last_info.get("coeffs_full", []) or []),
                "mahler_measure": float(last_info.get("mahler_measure", 0.0) or 0.0),
                "reward_label": rl, "via": "salem_cluster_known",
            })

        new_len, by_kp = _tally_episode_outcome(
            last_info, pipeline_len, env, counts, by_kp
        )
        if new_len > pipeline_len:
            rec = env.pipeline_records()[-1]
            if rec.terminal_state == "PROMOTED":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                promotes.append(d)
            elif rec.terminal_state == "SHADOW_CATALOG":
                d = _serialize_record(rec)
                d.update({"seed": seed, "episode": ep})
                shadow_catalog.append(d)
        pipeline_len = new_len

    elapsed = time.perf_counter() - t0
    try:
        env.close()
    except Exception:
        pass

    res = FourCountsResult(
        condition_label="reinforce_seeded",
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
    return {
        "result": res,
        "details": {
            "catalog_hits": catalog_hits,
            "promotes": promotes,
            "shadow_catalog": shadow_catalog,
            "salem_cluster_proxy_hits": salem_cluster_hits,
            "low_m_proxy_hits": low_m_hits,
            "seed": seed,
        },
    }


# ---------------------------------------------------------------------------
# Unseeded baselines (for the 4-arm comparison)
# ---------------------------------------------------------------------------


def _uniform_priors(degree: int, n_actions: int) -> Dict[int, np.ndarray]:
    half_len = degree // 2 + 1
    return {s: np.ones(n_actions, dtype=np.float64) / n_actions
            for s in range(half_len)}


# ---------------------------------------------------------------------------
# 4-arm comparison
# ---------------------------------------------------------------------------


def compare_seeded_vs_unseeded(
    env_factory: Callable[[], Any],
    n_episodes: int,
    seeds: Tuple[int, ...] = (0, 1, 2),
    seed_polys: Optional[List[Dict[str, Any]]] = None,
    lr: float = 0.05,
    entropy_coef: float = 0.05,
    prior_strength: float = 1.0,
) -> Dict[str, Any]:
    """Run all four arms (random uniform / random seeded / REINFORCE
    uniform / REINFORCE seeded) and tabulate results.

    Parameters
    ----------
    env_factory : callable
        Zero-arg DiscoveryEnv builder.
    n_episodes : int
        Episodes per (arm, seed).
    seeds : tuple of int, default (0, 1, 2)
        Seeds to average over.
    seed_polys : list of dict, optional
        Pre-extracted seed pool.  If None, falls back to
        ``extract_seed_polynomials_broad`` with min_abs_coef=4
        keyed off the env-factory's degree.

    Returns
    -------
    dict
        Well-formed summary with keys ``per_arm`` (per-arm aggregates),
        ``welch`` (one-sided t-tests), ``seed_pool`` (size + degree
        distribution), and ``priors`` (per-step priors used).
    """
    # Probe env to discover degree + alphabet.
    probe_env = env_factory()
    obs, info = probe_env.reset(seed=0)
    degree = int(info.get("degree", probe_env.degree))
    n_actions = int(info.get("n_actions"))
    coefficient_choices = tuple(info.get("coefficient_choices", probe_env.coefficient_choices))
    try:
        probe_env.close()
    except Exception:
        pass

    if seed_polys is None:
        seed_polys = extract_seed_polynomials_broad(
            env_degree=degree,
            coefficient_choices=coefficient_choices,
            min_abs_coef=4,
        )

    seeded_priors = compute_action_priors(
        seed_polys=seed_polys,
        degree=degree,
        coefficient_choices=coefficient_choices,
    )
    uniform = _uniform_priors(degree, n_actions)

    arms = {
        "random_uniform": ("random",   uniform),
        "random_seeded":  ("random",   seeded_priors),
        "reinforce_uniform": ("reinforce", uniform),
        "reinforce_seeded":  ("reinforce", seeded_priors),
    }

    per_arm: Dict[str, Any] = {}
    for label, (kind, priors) in arms.items():
        results: List[FourCountsResult] = []
        details: List[Dict[str, Any]] = []
        for s in seeds:
            if kind == "random":
                r = seeded_random_baseline(env_factory, priors, n_episodes, int(s))
            else:
                r = seeded_reinforce_agent(
                    env_factory, priors, n_episodes, int(s),
                    lr=lr, entropy_coef=entropy_coef,
                    prior_strength=prior_strength,
                )
            results.append(r["result"])
            details.append(r["details"])

        promote_rates = np.array([r.promote_rate for r in results])
        salem_rates = np.array(
            [d["salem_cluster_proxy_hits"] / max(1, n_episodes) for d in details]
        )
        catalog_hit_rates = np.array([r.catalog_hit_rate for r in results])

        per_arm[label] = {
            "kind": kind,
            "promote_rate_mean": float(promote_rates.mean()),
            "promote_rate_std": float(promote_rates.std(ddof=1))
                if promote_rates.size > 1 else 0.0,
            "promote_rates": promote_rates.tolist(),
            "salem_rate_mean": float(salem_rates.mean()),
            "salem_rate_std": float(salem_rates.std(ddof=1))
                if salem_rates.size > 1 else 0.0,
            "salem_rates": salem_rates.tolist(),
            "catalog_hit_rate_mean": float(catalog_hit_rates.mean()),
            "catalog_hit_rates": catalog_hit_rates.tolist(),
            "results": [r.__dict__ for r in results],
            "details": details,
        }

    # Welch t-tests on key contrasts.
    def _welch(a_lbl: str, b_lbl: str) -> float:
        a = np.array(per_arm[a_lbl]["promote_rates"])
        b = np.array(per_arm[b_lbl]["promote_rates"])
        return _welch_t_test_one_sided(a, b)

    welch = {
        "p_reinforce_seeded_gt_reinforce_uniform":
            _welch("reinforce_seeded", "reinforce_uniform"),
        "p_reinforce_seeded_gt_random_seeded":
            _welch("reinforce_seeded", "random_seeded"),
        "p_random_seeded_gt_random_uniform":
            _welch("random_seeded", "random_uniform"),
    }

    # Salem-concentration contrast (the "did seeding bias the search"
    # check that doesn't depend on the +100 band being inhabited).
    def _welch_salem(a_lbl: str, b_lbl: str) -> float:
        a = np.array(per_arm[a_lbl]["salem_rates"])
        b = np.array(per_arm[b_lbl]["salem_rates"])
        return _welch_t_test_one_sided(a, b)

    welch_salem = {
        "p_reinforce_seeded_gt_reinforce_uniform_on_salem":
            _welch_salem("reinforce_seeded", "reinforce_uniform"),
        "p_random_seeded_gt_random_uniform_on_salem":
            _welch_salem("random_seeded", "random_uniform"),
    }

    seed_pool_summary = _summarize_seed_pool(seed_polys)
    priors_summary = _summarize_priors(seeded_priors, coefficient_choices)

    return {
        "config": {
            "degree": degree,
            "coefficient_choices": list(coefficient_choices),
            "n_actions": n_actions,
            "n_episodes_per_cell": n_episodes,
            "seeds": list(seeds),
            "lr": lr,
            "entropy_coef": entropy_coef,
            "prior_strength": prior_strength,
        },
        "seed_pool": seed_pool_summary,
        "priors": priors_summary,
        "per_arm": per_arm,
        "welch": welch,
        "welch_salem": welch_salem,
    }


# ---------------------------------------------------------------------------
# Summarizers (for results.md generation)
# ---------------------------------------------------------------------------


def _summarize_seed_pool(seed_polys: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not seed_polys:
        return {"size": 0, "degree_dist": {}, "max_abs_coef_dist": {},
                "M_min": None, "M_max": None}
    deg_dist: Dict[int, int] = {}
    mac_dist: Dict[int, int] = {}
    Ms: List[float] = []
    for e in seed_polys:
        d = int(e["degree"])
        deg_dist[d] = deg_dist.get(d, 0) + 1
        mc = max(abs(int(c)) for c in e["coeffs"])
        mac_dist[mc] = mac_dist.get(mc, 0) + 1
        Ms.append(float(e["mahler_measure"]))
    return {
        "size": len(seed_polys),
        "degree_dist": dict(sorted(deg_dist.items())),
        "max_abs_coef_dist": dict(sorted(mac_dist.items())),
        "M_min": float(min(Ms)),
        "M_max": float(max(Ms)),
    }


def _summarize_priors(priors: Dict[int, np.ndarray],
                      coefficient_choices: Tuple[int, ...]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for s in sorted(priors.keys()):
        p = priors[s]
        row = {
            "step": int(s),
            "top_coef": int(coefficient_choices[int(np.argmax(p))]),
            "top_prob": float(p.max()),
            "entropy": float(-(p * np.log(np.clip(p, 1e-12, None))).sum()),
            "by_coef": {
                int(coefficient_choices[i]): float(p[i])
                for i in range(len(p))
            },
        }
        rows.append(row)
    return {"per_step": rows}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(degree: int = 14,
         coefficient_choices: Tuple[int, ...] = tuple(range(-5, 6)),
         n_episodes: int = 5000,
         seeds: Tuple[int, ...] = (0, 1, 2),
         out_path: Optional[str] = None) -> Dict[str, Any]:
    """Run the catalog-seeded 4-arm pilot at the requested config."""
    print("=" * 78)
    print(f"CATALOG-SEEDED PILOT  degree={degree}  alphabet={coefficient_choices}")
    print(f"  budget: {n_episodes} eps x {len(seeds)} seeds x 4 arms"
          f" = {n_episodes * len(seeds) * 4}")
    print("=" * 78)

    env_factory = lambda: DiscoveryEnv(
        degree=degree,
        coefficient_choices=coefficient_choices,
        reward_shape="step",
    )

    # Pre-extract seed pool with broad projection (dropped polys whose
    # half-coeffs fall outside the env alphabet).
    seed_polys = extract_seed_polynomials_broad(
        env_degree=degree,
        coefficient_choices=coefficient_choices,
        min_abs_coef=4,
    )
    print(f"  seed pool size: {len(seed_polys)}")
    if seed_polys:
        sp_summary = _summarize_seed_pool(seed_polys)
        print(f"    degree dist: {sp_summary['degree_dist']}")
        print(f"    max|c| dist: {sp_summary['max_abs_coef_dist']}")
        print(f"    M range: [{sp_summary['M_min']:.6f}, {sp_summary['M_max']:.6f}]")

    summary = compare_seeded_vs_unseeded(
        env_factory=env_factory,
        n_episodes=n_episodes,
        seeds=seeds,
        seed_polys=seed_polys,
    )

    print()
    print("=" * 78)
    print("4-ARM RESULTS SUMMARY")
    print("=" * 78)
    for label, info in summary["per_arm"].items():
        pr = info["promote_rate_mean"]
        sal = info["salem_rate_mean"]
        ch = info["catalog_hit_rate_mean"]
        print(f"  {label:<22} PROMOTE={pr:.5f}  salem={sal:.5f}  cat-hit={ch:.5f}")

    print()
    print("Welch p-values (one-sided, on PROMOTE rates):")
    for k, v in summary["welch"].items():
        print(f"  {k}: {v:.4f}")
    print("Welch p-values (one-sided, on SALEM-cluster rates):")
    for k, v in summary["welch_salem"].items():
        print(f"  {k}: {v:.4f}")

    # SHADOW_CATALOG entries
    print()
    print("=" * 78)
    print("SHADOW_CATALOG ENTRIES (any > 0 is real signal)")
    print("=" * 78)
    total_shadow = 0
    for label, info in summary["per_arm"].items():
        for det in info["details"]:
            for s in det["shadow_catalog"]:
                total_shadow += 1
                print(f"  arm={label} seed={det['seed']} ep={s.get('episode')}: "
                      f"M={s['mahler_measure']:.6f} hash={s['candidate_hash']}")
                print(f"    coeffs={s['coeffs']}")
                print(f"    kill_pattern={s['kill_pattern']}")
    print(f"Total SHADOW_CATALOG entries: {total_shadow}")

    # PROMOTED entries
    print()
    print("=" * 78)
    print("PROMOTED ENTRIES")
    print("=" * 78)
    total_prom = 0
    for label, info in summary["per_arm"].items():
        for det in info["details"]:
            for p in det["promotes"]:
                total_prom += 1
                print(f"  arm={label} seed={det['seed']} ep={p.get('episode')}: "
                      f"M={p['mahler_measure']:.6f} hash={p['candidate_hash']}")
                print(f"    coeffs={p['coeffs']}")
    print(f"Total PROMOTED entries: {total_prom}")

    # Catalog hits
    print()
    print("=" * 78)
    print("CATALOG-HIT EPISODES (rediscoveries)")
    print("=" * 78)
    total_cat = 0
    for label, info in summary["per_arm"].items():
        for det in info["details"]:
            total_cat += len(det["catalog_hits"])
            for c in det["catalog_hits"][:5]:
                print(f"  arm={label} seed={det['seed']} ep={c.get('episode')}: "
                      f"M={c['mahler_measure']:.6f}  flag={c['discovery_flag']}")
    print(f"Total catalog-hit episodes (across all arms/seeds): {total_cat}")

    if out_path is None:
        out_path = os.path.join(
            os.path.dirname(__file__), "_catalog_seeded_pilot.json"
        )
    try:
        with open(out_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print()
        print(f"JSON dump: {out_path}")
    except Exception as e:
        print(f"Could not write JSON dump: {e}")

    return summary


if __name__ == "__main__":
    n_eps = 5000
    if len(sys.argv) > 1:
        n_eps = int(sys.argv[1])
    main(n_episodes=n_eps)


__all__ = [
    "extract_seed_polynomials",
    "extract_seed_polynomials_broad",
    "compute_action_priors",
    "seeded_random_baseline",
    "seeded_reinforce_agent",
    "compare_seeded_vs_unseeded",
]
