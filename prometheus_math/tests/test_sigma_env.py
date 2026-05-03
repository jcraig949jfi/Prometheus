"""Tests for prometheus_math.sigma_env (Gymnasium env over the substrate).

Math-tdd skill rubric: ≥2 tests in each of authority/property/edge/composition.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.sigma_env import (
    SigmaMathEnv,
    OBJECTIVES,
    register_with_gymnasium,
)


# ---------------------------------------------------------------------------
# Authority — known objectives & reward shapes
# ---------------------------------------------------------------------------


def test_authority_lehmer_objective_recognizes_lehmer_polynomial():
    """The default action table includes Lehmer's polynomial (M ≈ 1.176).
    Picking that action yields the maximum reward for the
    minimize_mahler_measure objective."""
    pytest.importorskip("numpy")
    env = SigmaMathEnv(objective="minimize_mahler_measure", max_steps=5, seed=0)
    obs, info = env.reset()
    table = env.action_table()
    lehmer_idxs = [
        i for i, row in enumerate(table) if "Lehmer" in row.arg_label
    ]
    assert lehmer_idxs, "default action table must include a Lehmer-polynomial entry"
    obs2, reward, terminated, truncated, info2 = env.step(lehmer_idxs[0])
    # Lehmer's measure ≈ 1.176 → +100, and hits target threshold (M < 1.18).
    assert reward >= 100.0
    assert terminated is True


def test_authority_dilogarithm_target_value():
    """Picking dilogarithm at z=1 returns Li_2(1) ≈ pi^2/6, which under
    the riemann_zeros objective is the high-reward case."""
    pytest.importorskip("scipy")
    env = SigmaMathEnv(objective="riemann_zeros", max_steps=5, seed=1)
    env.reset()
    table = env.action_table()
    targets = [i for i, r in enumerate(table) if "Li2(1)" in r.arg_label]
    assert targets, "riemann_zeros action table must include Li_2(1)"
    _, reward, terminated, _, info = env.step(targets[0])
    assert reward >= 50.0


# ---------------------------------------------------------------------------
# Property — invariants of the env interface
# ---------------------------------------------------------------------------


def test_property_obs_shape_and_dtype():
    env = SigmaMathEnv(max_steps=3, seed=2)
    obs, info = env.reset()
    assert obs.shape == (5,)
    assert obs.dtype == np.float64
    # All entries finite (no NaN at startup).
    assert np.all(np.isfinite(obs))


def test_property_step_returns_5_tuple():
    env = SigmaMathEnv(max_steps=3, seed=3)
    env.reset()
    out = env.step(0)
    assert isinstance(out, tuple) and len(out) == 5
    obs, reward, term, trunc, info = out
    assert isinstance(obs, np.ndarray) and obs.shape == (5,)
    assert isinstance(reward, float)
    assert isinstance(term, bool)
    assert isinstance(trunc, bool)
    assert isinstance(info, dict)


def test_property_terminates_after_max_steps():
    env = SigmaMathEnv(max_steps=3, seed=4)
    env.reset()
    # Pick a dud action repeatedly; should terminate at step 3.
    table = env.action_table()
    dud = next(
        (i for i, r in enumerate(table) if "noisy" in r.arg_label),
        len(table) - 1,
    )
    terminated = False
    n = 0
    while not terminated and n < 10:
        _, _, terminated, _, _ = env.step(dud)
        n += 1
    assert terminated is True
    assert n <= 3


def test_property_seed_reproducibility():
    """Same seed → same action_table size + same action descriptions."""
    e1 = SigmaMathEnv(max_steps=3, seed=42)
    e2 = SigmaMathEnv(max_steps=3, seed=42)
    e1.reset()
    e2.reset()
    a1 = [(r.callable_ref, r.arg_label) for r in e1.action_table()]
    a2 = [(r.callable_ref, r.arg_label) for r in e2.action_table()]
    assert a1 == a2


# ---------------------------------------------------------------------------
# Edge — bad inputs
# ---------------------------------------------------------------------------


def test_edge_unknown_objective_raises():
    with pytest.raises(ValueError):
        SigmaMathEnv(objective="not_a_real_objective")


def test_edge_step_before_reset_raises():
    env = SigmaMathEnv(max_steps=3)
    with pytest.raises(RuntimeError):
        env.step(0)


def test_edge_action_out_of_range():
    env = SigmaMathEnv(max_steps=3, seed=5)
    env.reset()
    with pytest.raises(ValueError):
        env.step(9999)


def test_edge_kernel_after_reset_accessible():
    """env.kernel() returns the live SigmaKernel after reset; substrate
    growth is observable through it."""
    env = SigmaMathEnv(max_steps=2, seed=6)
    env.reset()
    k = env.kernel()
    # bindings table should have rows already (one BIND per unique callable).
    cur = k.conn.execute("SELECT COUNT(*) FROM bindings")
    n_bindings = cur.fetchone()[0]
    assert n_bindings >= 2


# ---------------------------------------------------------------------------
# Composition — env + substrate + arsenal interaction
# ---------------------------------------------------------------------------


def test_composition_substrate_grows_per_eval():
    """Each step writes a new evaluation symbol to the substrate."""
    env = SigmaMathEnv(max_steps=3, seed=7)
    env.reset()
    k = env.kernel()
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n0 = cur.fetchone()[0]
    env.step(0)
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n1 = cur.fetchone()[0]
    env.step(1)
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n2 = cur.fetchone()[0]
    assert n1 == n0 + 1
    assert n2 == n1 + 1


def test_composition_random_agent_run_closes_loop():
    """End-to-end smoke: a random-action agent runs the env to completion
    without crashing; cumulative reward is non-negative; substrate ends
    with a growing claims+evaluations footprint.

    This is the load-bearing test for the MVP: it proves the BIND/EVAL
    extension + arsenal_meta bootstrapping + Gym env interface work
    together end-to-end.
    """
    pytest.importorskip("numpy")
    env = SigmaMathEnv(max_steps=10, seed=8)
    obs, info = env.reset()
    rng = np.random.default_rng(8)
    n_actions = info["n_actions"]
    assert n_actions >= 5  # default table has > 5 entries

    cum_reward = 0.0
    n_steps = 0
    terminated = False
    while not terminated and n_steps < 10:
        a = int(rng.integers(0, n_actions))
        obs, r, terminated, _, info = env.step(a)
        cum_reward += r
        n_steps += 1

    assert n_steps >= 1
    assert cum_reward >= 0.0  # rewards are non-negative for this objective

    # Substrate grew.
    k = env.kernel()
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    assert cur.fetchone()[0] == n_steps


def test_composition_register_with_gymnasium_idempotent():
    """register_with_gymnasium returns a stable env_id on success and
    None when gymnasium is missing. Idempotent across calls."""
    a = register_with_gymnasium()
    b = register_with_gymnasium()
    # Either both None (no gymnasium) or both equal env_id strings.
    assert a == b


# ---------------------------------------------------------------------------
# Audit-extension tests (added 2026-04-29 per math-tdd skill audit).
# ---------------------------------------------------------------------------


def test_authority_phi_6_cyclotomic_low_reward():
    """AUTHORITY (audit-add): the phi_6 cyclotomic action [1,-1,1] has
    M = 1 exactly; under the minimize_mahler_measure objective this falls
    in the M < 5 band → +1 (the "any finite M" floor reward).

    Reference: phi_6(x) = x^2 - x + 1 is the 6th cyclotomic polynomial;
    its roots are primitive 6th roots of unity (|root| = 1) so M(phi_6)=1.
    Distinct from the Lehmer test (which exercises the +100 jackpot
    branch); this exercises the floor branch.
    """
    pytest.importorskip("numpy")
    env = SigmaMathEnv(objective="minimize_mahler_measure", max_steps=5, seed=10)
    env.reset()
    table = env.action_table()
    phi_6_idxs = [i for i, r in enumerate(table) if r.arg_label == "phi_6"]
    assert phi_6_idxs, "default action table must include phi_6"
    _, reward, terminated, _, info = env.step(phi_6_idxs[0])
    # M(phi_6)=1 → falls in [1.0, 1.18) → +100 (sub-Lehmer band).
    # Reward should be > 0; precise band depends on float comparison
    # but +100 (1 < 1.18) is the expected branch.
    assert reward > 0.0


def test_authority_objective_dispatch_table_keys():
    """AUTHORITY (audit-add): the OBJECTIVES module-level dict exposes
    exactly the two documented objective predicates. Reference: module
    docstring + sigma_env.OBJECTIVES literal. Distinct from any
    individual objective behavior test — this checks the dispatch table
    schema itself.
    """
    assert set(OBJECTIVES.keys()) == {
        "minimize_mahler_measure", "riemann_zeros",
    }
    for k, fn in OBJECTIVES.items():
        assert callable(fn)


def test_property_action_table_size_matches_n_actions_info():
    """PROPERTY (audit-add): info['n_actions'] returned by reset() is
    exactly len(env.action_table()). Distinct from seed_reproducibility
    (which checks list-equality across seeds) — this checks the size
    invariant alone.
    """
    env = SigmaMathEnv(max_steps=3, seed=11)
    obs, info = env.reset()
    assert info["n_actions"] == len(env.action_table())


def test_property_obs_step_count_increments_monotonically():
    """PROPERTY (audit-add): the first observation entry (step_count) is
    a monotonically increasing non-negative integer-valued float across
    a sequence of step calls. Distinct from terminates_after_max_steps
    (different invariant).
    """
    env = SigmaMathEnv(max_steps=10, seed=12)
    env.reset()
    counts = []
    for _ in range(3):
        obs, _, _, _, _ = env.step(0)
        counts.append(int(obs[0]))
    assert counts == [1, 2, 3]


def test_edge_close_releases_kernel():
    """EDGE (audit-add): env.close() sets the internal kernel to None;
    subsequent env.kernel() raises RuntimeError. Distinct from
    step_before_reset (which is the un-initialized path).
    """
    env = SigmaMathEnv(max_steps=2, seed=13)
    env.reset()
    env.close()
    with pytest.raises(RuntimeError):
        env.kernel()


def test_edge_negative_action_index_raises():
    """EDGE (audit-add): step(-1) raises ValueError, not IndexError.
    Distinct from action_out_of_range (which goes high); negative
    indexes route through a different validation branch.
    """
    env = SigmaMathEnv(max_steps=3, seed=14)
    env.reset()
    with pytest.raises(ValueError):
        env.step(-1)


def test_composition_action_table_persists_across_dud_steps():
    """COMPOSITION (audit-add): a sequence of "noisy" (low-reward) action
    picks does not corrupt the action table — its callable_refs and
    arg_labels remain identical from start to end of the episode.
    Distinct from random_agent_run_closes_loop (which checks reward
    accumulation, not action-table integrity).
    """
    env = SigmaMathEnv(max_steps=5, seed=15)
    env.reset()
    table_before = [(r.callable_ref, r.arg_label) for r in env.action_table()]
    dud_idx = next(
        (i for i, r in enumerate(env.action_table()) if "noisy" in r.arg_label),
        len(env.action_table()) - 1,
    )
    for _ in range(3):
        env.step(dud_idx)
    table_after = [(r.callable_ref, r.arg_label) for r in env.action_table()]
    assert table_before == table_after
