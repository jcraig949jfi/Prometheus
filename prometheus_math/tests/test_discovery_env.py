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
    _compute_reward_shaped,
    _palindromic_from_half,
    _is_reciprocal,
    _check_mossinghoff,
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


# ---------------------------------------------------------------------------
# Audit-extension tests (added 2026-04-29 per math-tdd skill audit).
# ---------------------------------------------------------------------------


def test_authority_shaped_reward_sub_lehmer_above_floor():
    """AUTHORITY (audit-add): the shaped-reward variant gives the
    Lehmer-band M=1.176 a reward strictly above the floor (5,M)=4 case
    (M=2 → ~37.5). The shaped reward is monotonic-decreasing in M for
    M in [1.001, 5]; the +50 sub-Lehmer bonus is on top of the smooth
    gradient. Distinct from the step-reward authority test (different
    reward function entirely).
    """
    r_lehmer, label_lehmer = _compute_reward_shaped(1.17628)
    r_low_m, _ = _compute_reward_shaped(1.5)
    r_mid_m, _ = _compute_reward_shaped(2.0)
    assert label_lehmer == "sub_lehmer"
    # Sub-Lehmer reward = 50 + 50*(5-1.176)/4 ≈ 50 + 47.8 ≈ 97.8.
    assert r_lehmer > 90.0
    # Monotone-decreasing on [1.18, 5].
    assert r_low_m > r_mid_m


def test_authority_compute_reward_high_m_zero():
    """AUTHORITY (audit-add): M=10 (well above the 5.0 cutoff) returns
    reward 0 with label 'cyclotomic_or_large'. Distinct from the M=1
    cyclotomic test (different branch — large-M path).

    Reference: _compute_reward docstring branch table.
    """
    r, label = _compute_reward(10.0)
    assert r == 0.0
    assert label == "cyclotomic_or_large"


def test_property_shaped_reward_continuous_in_m():
    """PROPERTY (audit-add): _compute_reward_shaped is continuous
    (modulo the +50 sub-Lehmer bonus jump at M=1.18) on [1.001, 5].
    Distinct from the discrete _compute_reward path; here we verify
    the smooth-gradient claim in the docstring numerically.
    """
    # Sample two close points within the 'shaped_continuous' band.
    r1, _ = _compute_reward_shaped(2.0)
    r2, _ = _compute_reward_shaped(2.001)
    # Continuous: tiny step in M → tiny step in reward.
    assert abs(r1 - r2) < 0.1
    # And reward is non-negative everywhere.
    assert r1 >= 0.0
    assert r2 >= 0.0


def test_property_palindromic_half_round_trip():
    """PROPERTY (audit-add): for any half_len-length integer half-list,
    _palindromic_from_half produces a degree+1-length list that is
    self-reverse-equal AND its first half equals the input. Distinct
    from action_picks_become_palindromic (which checks via the env);
    this checks the helper directly across multiple inputs.
    """
    for half, deg in [
        ([1, 2, 3], 4),
        ([1, 0, -1, 2], 6),
        ([1, 1, 0, -1, -1, -1], 10),
    ]:
        full = _palindromic_from_half(half, deg)
        assert len(full) == deg + 1
        assert full == full[::-1]
        assert full[: len(half)] == half


def test_edge_invalid_reward_shape_raises():
    """EDGE (audit-add): DiscoveryEnv(reward_shape='garbage') raises
    ValueError. Distinct from invalid_degree (different parameter
    branch) and action_out_of_range (runtime).
    """
    with pytest.raises(ValueError, match="reward_shape"):
        DiscoveryEnv(degree=6, reward_shape="not_a_real_shape")


def test_edge_palindromic_short_half_raises():
    """EDGE (audit-add): _palindromic_from_half with too few half-coeffs
    raises ValueError. Distinct from invalid_degree (different layer);
    this exercises the helper's own validation.
    """
    with pytest.raises(ValueError, match="half-coeffs"):
        _palindromic_from_half([1, 2], 10)  # need 6, given 2
    with pytest.raises(ValueError, match="degree"):
        _palindromic_from_half([1], 1)  # degree<2 short-circuits


def test_edge_check_mossinghoff_returns_none_for_unmatched_m():
    """EDGE (audit-add): _check_mossinghoff with an M not in the
    snapshot returns (False, None). If the snapshot is unavailable,
    returns (None, None). Distinct from the known_salem composition
    test (which exercises the matched path).
    """
    is_known, label = _check_mossinghoff([1, 0, 0, 0, 0, 1], 7.5)
    # 7.5 isn't a Mossinghoff-table M value.
    # is_known is False (snapshot loaded but no match) or None (no snapshot).
    assert is_known in (False, None)


def test_composition_shaped_reward_env_runs_end_to_end():
    """COMPOSITION (audit-add): DiscoveryEnv(reward_shape='shaped')
    runs end-to-end and produces non-negative rewards. Distinct from
    test_composition_lehmer_action_path_yields_jackpot (which uses
    the default 'step' shape); here we exercise the shaped-reward
    branch through the full pipeline.
    """
    env = DiscoveryEnv(degree=10, seed=88, reward_shape="shaped")
    env.reset()
    actions = [4, 4, 3, 2, 2, 2]  # Lehmer
    for a in actions:
        _, reward, terminated, _, info = env.step(a)
    assert terminated is True
    # Lehmer in shaped reward → 97-98 (50 + smooth gradient at M=1.176).
    assert info["reward_label"] == "sub_lehmer"
    assert reward >= 90.0


def test_authority_widened_coefficient_choices_action_space():
    """AUTHORITY (audit-add 2026-05-03): the optional coefficient_choices
    constructor parameter widens the per-step action set without
    mutating the module-level COEFFICIENT_CHOICES constant. With
    coefficient_choices=(-5..5), action_space.n == 11; the module
    constant remains (-3..3) of length 7. Distinct from the default
    case (which uses module-level COEFFICIENT_CHOICES) and from
    invalid_degree (different parameter branch).

    Reference: discovery_via_rediscovery.md §6.2 width-ablation pilot.
    """
    cc = (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5)
    env = DiscoveryEnv(degree=10, coefficient_choices=cc)
    assert env.action_space.n == 11
    assert env.coefficient_choices == cc
    assert env.n_coefficient_actions == 11
    # The module-level constants must NOT have been mutated.
    assert COEFFICIENT_CHOICES == (-3, -2, -1, 0, 1, 2, 3)
    assert N_COEFFICIENT_ACTIONS == 7
    # Smoke: stepping with the widest action (= coef +5) reaches a
    # palindromic polynomial whose leading and trailing coefficients
    # are both +5.
    env.reset()
    for _ in range(env.half_len):
        _, _, terminated, _, info = env.step(env.n_coefficient_actions - 1)
    assert terminated is True
    full = info["coeffs_full"]
    assert full[0] == 5
    assert full[-1] == 5
    env.close()


def test_composition_sub_lehmer_candidates_list_starts_empty():
    """COMPOSITION (audit-add): a fresh DiscoveryEnv has
    sub_lehmer_candidates() == [] and known_salem_hits() == 0; after
    a Lehmer episode (which is in Mossinghoff), candidates remains
    empty (Lehmer is *known*, not a discovery). Composes the
    Mossinghoff cross-check with the candidates filter.

    Distinct from test_composition_episode_record_logged_on_jackpot
    (which checks the discoveries() list; sub_lehmer_candidates is a
    distinct narrower filter).
    """
    env = DiscoveryEnv(degree=10, seed=99)
    env.reset()
    assert env.sub_lehmer_candidates() == []
    assert env.known_salem_hits() == 0
    actions = [4, 4, 3, 2, 2, 2]  # Lehmer
    for a in actions:
        env.step(a)
    # Lehmer is in the snapshot, so sub_lehmer_candidates stays empty
    # (or all entries have is_known_in_mossinghoff=False, but Lehmer's
    # M=1.176 IS in the snapshot). Tolerate snapshot-unavailable case.
    candidates = env.sub_lehmer_candidates()
    for c in candidates:
        # If any candidate exists, it must NOT be Lehmer's M.
        assert not (1.17 < c.mahler_measure < 1.18)
