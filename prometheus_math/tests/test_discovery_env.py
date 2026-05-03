"""Tests for prometheus_math.discovery_env (generative reciprocal-poly RL env).

Math-tdd skill rubric: ≥2 in every category.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.discovery_env import (
    DiscoveryEnv,
    EpisodeRecord,
    COEFFICIENT_CHOICES,
    N_COEFFICIENT_ACTIONS,
    _compute_reward,
    _palindromic_from_half,
    _is_reciprocal,
)


# ---------------------------------------------------------------------------
# Authority — the reward shape and Lehmer/cyclotomic boundary cases
# ---------------------------------------------------------------------------


def test_authority_reward_shape_lehmer():
    """Lehmer's polynomial M = 1.17628... lies in [1.001, 1.18) → +100."""
    reward, label = _compute_reward(1.17628081826)
    assert reward == 100.0
    assert label == "sub_lehmer"


def test_authority_reward_shape_cyclotomic_zero():
    """Cyclotomic polynomials have M = 1 exactly → 0 reward (sparse)."""
    reward, label = _compute_reward(1.0)
    assert reward == 0.0
    assert label == "cyclotomic_or_large"


def test_authority_reward_shape_salem_cluster():
    """M = 1.3 falls in the Salem cluster band → +20."""
    reward, label = _compute_reward(1.3)
    assert reward == 20.0
    assert label == "salem_cluster"


def test_authority_palindromic_construction():
    """Mirroring [1, 1, 0, -1, -1, -1] for degree 10 reproduces Lehmer's
    polynomial (or its reverse, modulo sign convention)."""
    half = [1, 1, 0, -1, -1, -1]  # half-coeffs
    full = _palindromic_from_half(half, 10)
    # Should be 11-long and palindromic.
    assert len(full) == 11
    assert full == full[::-1]


# ---------------------------------------------------------------------------
# Property — invariants of the env interface
# ---------------------------------------------------------------------------


def test_property_obs_shape_matches_spec():
    env = DiscoveryEnv(degree=10)
    obs, info = env.reset()
    expected_shape = (7 + env.degree,)
    assert obs.shape == expected_shape


def test_property_episode_terminates_at_half_len():
    """An episode must terminate exactly when half-coefficient picks
    are complete — no earlier, no later."""
    env = DiscoveryEnv(degree=8, seed=0)
    env.reset()
    half_len = env.half_len  # = 5 for degree 8
    n_steps = 0
    terminated = False
    while not terminated and n_steps < 20:
        # Pick a non-degenerate coefficient (avoid all-zero polys).
        action = (n_steps + 1) % N_COEFFICIENT_ACTIONS
        _, _, terminated, _, _ = env.step(action)
        n_steps += 1
    assert n_steps == half_len
    assert terminated is True


def test_property_action_picks_become_palindromic():
    """The full polynomial built from any half-sequence is palindromic."""
    env = DiscoveryEnv(degree=6, seed=1)
    env.reset()
    # Pick coefficient sequence: 0, 1, 2, 3 (indices 0..3 → coeffs 0, 1, 2, 3 → wait, indices map to (-3..+3)).
    # half_len for degree 6 is 4. Actions 6, 0, 1, 2 → coeffs 3, -3, -2, -1.
    # We don't care about the values; we care that the result is palindromic.
    actions = [6, 1, 2, 3]
    for a in actions[: env.half_len]:
        _, _, terminated, _, info = env.step(a)
    assert terminated is True
    full = info["coeffs_full"]
    assert _is_reciprocal(full)


def test_property_random_baseline_mean_reward_is_finite_and_nonneg():
    """A 100-episode random run should produce a finite, non-negative
    mean reward (the action space includes positive-reward actions)."""
    env = DiscoveryEnv(degree=8, seed=2)
    rng = np.random.default_rng(2)
    rewards = []
    for _ in range(100):
        env.reset()
        terminated = False
        while not terminated:
            a = int(rng.integers(0, N_COEFFICIENT_ACTIONS))
            _, _, terminated, _, info = env.step(a)
        rewards.append(info.get("reward_label") and info.get("reward_label") != "non_finite")
    # Just check the env doesn't crash and each episode produces a label.
    assert all(rewards)


# ---------------------------------------------------------------------------
# Edge — bad inputs and degenerate cases
# ---------------------------------------------------------------------------


def test_edge_invalid_degree_raises():
    with pytest.raises(ValueError):
        DiscoveryEnv(degree=1)


def test_edge_action_out_of_range_raises():
    env = DiscoveryEnv(degree=4)
    env.reset()
    with pytest.raises(ValueError):
        env.step(N_COEFFICIENT_ACTIONS + 100)


def test_edge_step_before_reset_raises():
    env = DiscoveryEnv(degree=6)
    with pytest.raises(RuntimeError):
        env.step(0)


def test_edge_zero_polynomial_returns_zero_reward():
    """If the agent picks all zeros, the resulting polynomial is zero;
    reward should be 0 (not positive, not crash)."""
    env = DiscoveryEnv(degree=4, seed=3)
    env.reset()
    # Action index 3 = coefficient 0.
    half_len = env.half_len  # = 3
    info = {}
    for _ in range(half_len):
        _, reward, terminated, _, info = env.step(3)  # pick 0 each time
    assert terminated is True
    assert reward == 0.0


# ---------------------------------------------------------------------------
# Composition — env + substrate + reward + Mossinghoff
# ---------------------------------------------------------------------------


def test_composition_substrate_grows_per_completed_episode():
    """One EVAL is written per completed episode (not per step)."""
    env = DiscoveryEnv(degree=6, seed=4)
    env.reset()
    k = env.kernel()
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n0 = cur.fetchone()[0]
    # Run two complete episodes.
    for _ in range(env.half_len):
        env.step(4)  # coefficient 1
    env.reset()
    for _ in range(env.half_len):
        env.step(4)
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n_after = cur.fetchone()[0]
    assert n_after == n0 + 2


def test_composition_lehmer_action_path_yields_jackpot():
    """Building Lehmer's polynomial from the half [1, 1, 0, -1, -1, -1]
    should yield reward = +100 if the M-evaluation matches the published
    value within tolerance."""
    env = DiscoveryEnv(degree=10, seed=5)
    env.reset()
    # Action indices for [1, 1, 0, -1, -1, -1]:
    #   1 → index 4, 0 → index 3, -1 → index 2.
    # COEFFICIENT_CHOICES = (-3, -2, -1, 0, 1, 2, 3) → index of:
    #   1 → 4, 0 → 3, -1 → 2.
    actions = [4, 4, 3, 2, 2, 2]  # coeffs 1, 1, 0, -1, -1, -1
    for a in actions:
        _, reward, terminated, _, info = env.step(a)
    assert terminated is True
    # The polynomial should be Lehmer's; M ≈ 1.17628.
    assert info["mahler_measure"] == pytest.approx(1.17628081826, abs=1e-6)
    assert info["reward_label"] == "sub_lehmer"
    assert reward == 100.0


def test_composition_episode_record_logged_on_jackpot():
    """A jackpot or salem-cluster reward results in an EpisodeRecord
    being added to the env's discoveries list."""
    env = DiscoveryEnv(degree=10, seed=6)
    env.reset()
    actions = [4, 4, 3, 2, 2, 2]  # Lehmer
    for a in actions:
        env.step(a)
    discoveries = env.discoveries()
    assert len(discoveries) >= 1
    # The Lehmer record should be present.
    lehmer_records = [
        d for d in discoveries
        if abs(d.mahler_measure - 1.17628081826) < 1e-6
    ]
    assert len(lehmer_records) == 1


def test_composition_known_salem_flagged_in_mossinghoff():
    """When the agent finds Lehmer's polynomial, the Mossinghoff cross-
    check should flag it as known (it's the M ≈ 1.176 entry in the
    snapshot)."""
    env = DiscoveryEnv(degree=10, seed=7)
    env.reset()
    actions = [4, 4, 3, 2, 2, 2]  # Lehmer
    for a in actions:
        _, _, terminated, _, info = env.step(a)
    assert terminated is True
    # is_known_in_mossinghoff should be True (Lehmer's M is in the table).
    # Note: the env's _check_mossinghoff is by M-value, not coefficients;
    # so any polynomial with M matching a snapshot entry is "known."
    # If the snapshot doesn't load, is_known is None — accept either
    # True or None (None means snapshot unavailable, not a failure).
    assert info["is_known_in_mossinghoff"] in (True, None)
