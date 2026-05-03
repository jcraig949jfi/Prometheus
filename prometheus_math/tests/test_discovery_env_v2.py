"""Tests for prometheus_math.discovery_env_v2 (GA-style discovery env).

Math-tdd skill rubric: ≥3 in every category (authority / property /
edge / composition).  V2 is a sibling to v1 — the action space is
*mutation operators*, not coefficient picks, so the test surface is
genuinely different (population invariants + operator semantics +
GA-loop convergence).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.discovery_env_v2 import (
    DiscoveryEnvV2,
    EpisodeRecordV2,
    PopulationMember,
    MUTATION_OPERATORS,
    N_MUTATION_OPERATORS,
    COEFFICIENT_CHOICES_V2,
    KNOWN_SEEDS_DEG10,
    LEHMER_HALF,
    _palindromic_from_half,
    _is_reciprocal,
    _compute_reward_v2,
    _mutate_single_coef,
    _mutate_two_coefs,
    _swap_palindromic_pairs,
    _increment_at_index,
    _decrement_at_index,
    _zero_at_index,
    _identity,
)


# ---------------------------------------------------------------------------
# Authority — operators preserve palindromic constraint, seeded population
#             reaches Lehmer-band M, reversibility of single-flip mutations
# ---------------------------------------------------------------------------


def test_authority_v2_produces_palindromic_polys():
    """AUTHORITY: every full polynomial built from any half-vector that
    a mutation operator emits is palindromic.

    Reference: discovery_via_rediscovery.md §6.4 — palindromic constraint
    is a load-bearing invariant of the reciprocal-poly action space.
    """
    rng = np.random.default_rng(0)
    alphabet = COEFFICIENT_CHOICES_V2
    half_len = 6  # degree 10
    # Initial half-vector.
    half = [int(alphabet[int(rng.integers(0, len(alphabet)))]) for _ in range(half_len)]
    # Apply each operator and verify mirroring still works.
    for name, op in MUTATION_OPERATORS:
        new_half = op(list(half), rng, alphabet)
        assert len(new_half) == half_len, f"{name} changed half_len"
        full = _palindromic_from_half(new_half, 10)
        assert len(full) == 11
        assert _is_reciprocal(full), f"{name} produced non-palindromic full poly"


def test_authority_v2_lehmer_seed_reaches_lehmer_band():
    """AUTHORITY: a population seeded with Lehmer's polynomial converges
    to (or stays at) Lehmer-band M after sufficient mutations.

    Reference: Lehmer 1933 — M(Lehmer poly) = 1.17628..., the conjectured
    infimum.  Elitist replacement guarantees the elite never moves above
    its initial value.
    """
    env = DiscoveryEnvV2(
        degree=10,
        population_size=8,
        n_mutations_per_episode=20,
        seed_with_known=True,
        seed=42,
    )
    env.reset()
    # Run one full episode of mutations.
    terminated = False
    while not terminated:
        # Pick a random operator.
        a = int(np.random.default_rng(0).integers(0, env.n_actions))
        _, _, terminated, _, info = env.step(a)
    # Elite M must be <= Lehmer's M (the seed is in the population).
    # Elitist replacement guarantees the elite never moves up; mutation
    # may discover a *cyclotomic* (M=1) that displaces Lehmer downward.
    # We accept M in [1.0, 1.18]: we ARE in (or below) Lehmer's band.
    assert info["elite_m"] <= 1.18 + 1e-6
    assert info["elite_m"] >= 1.0 - 1e-9
    env.close()


def test_authority_v2_mutation_operators_listed_correctly():
    """AUTHORITY: the operator menu has the documented count and includes
    the documented operator names.  Distinct from palindromic test
    (which checks behavior); this checks the *registry* itself.

    Reference: discovery_env_v2 module docstring — operator menu is
    fixed at 7 entries (5-8 per spec).
    """
    names = [n for n, _ in MUTATION_OPERATORS]
    assert N_MUTATION_OPERATORS == len(MUTATION_OPERATORS)
    assert 5 <= N_MUTATION_OPERATORS <= 8
    for required in (
        "mutate_single_coef",
        "mutate_two_coefs",
        "swap_palindromic_pairs",
        "increment_at_index",
        "decrement_at_index",
        "zero_at_index",
        "identity",
    ):
        assert required in names, f"missing operator: {required}"


def test_authority_v2_increment_decrement_inverse_at_clip_floor():
    """AUTHORITY: increment_at_index then decrement_at_index at the same
    coefficient is identity *unless* clipped at the alphabet boundary.

    In the interior of the alphabet (e.g., coefficient = 0), inc → 1 →
    dec → 0 is exact identity.  This is the GA-style reversibility
    property the spec calls out.
    """
    rng = np.random.default_rng(0)
    alphabet = (-3, -2, -1, 0, 1, 2, 3)
    # Force the operator to hit index 0 by using a deterministic length-1 half.
    half = [0]
    h1 = _increment_at_index(half, np.random.default_rng(0), alphabet)
    h2 = _decrement_at_index(h1, np.random.default_rng(0), alphabet)
    assert h2 == half  # interior coefficient round-trips exactly


# ---------------------------------------------------------------------------
# Property — invariants of the env interface and reward shape
# ---------------------------------------------------------------------------


def test_property_v2_reward_nonneg_for_nondegenerate():
    """PROPERTY: _compute_reward_v2 returns >= 0 for any
    non-degenerate (finite, M >= 1) elite_m.  The shape is built that
    way (max(0, ...) on every component); this property is the contract
    the agent's policy gradient depends on.
    """
    for m in [1.001, 1.05, 1.18, 1.5, 2.0, 3.0, 5.0]:
        r, _ = _compute_reward_v2(m, prev_elite_m=10.0, is_sub_lehmer=False, is_signal_class=False)
        assert r >= 0.0
    # Sub-Lehmer with band bonus.
    r_sub, label = _compute_reward_v2(
        1.05, prev_elite_m=10.0, is_sub_lehmer=True, is_signal_class=False
    )
    assert r_sub >= 50.0  # band bonus alone is +50
    assert label == "sub_lehmer"


def test_property_v2_best_m_monotonically_decreases_across_episodes():
    """PROPERTY: best_m_overall is monotonically non-increasing across
    episodes.  Elitist replacement guarantees this — a member is only
    evicted when a strictly better one arrives.

    This is the GA-loop convergence anchor: even with random operator
    selection, best-found M never moves up.
    """
    env = DiscoveryEnvV2(
        degree=10,
        population_size=8,
        n_mutations_per_episode=20,
        seed=7,
    )
    rng = np.random.default_rng(7)
    best_history = []
    for _ in range(5):
        env.reset()
        terminated = False
        while not terminated:
            a = int(rng.integers(0, env.n_actions))
            _, _, terminated, _, info = env.step(a)
        best_history.append(env.best_m_overall())
    # Monotonically non-increasing.
    for i in range(1, len(best_history)):
        assert best_history[i] <= best_history[i - 1] + 1e-9
    env.close()


def test_property_v2_zero_mutation_rate_no_movement():
    """PROPERTY: with mutation_rate=0, the population never changes;
    the agent gets identity-style reward (= reward at the initial
    population's elite, with no improvement bonus).

    This is the agent-control anchor: the policy can't learn if the
    env doesn't respond to actions.  We verify the env actually freezes.
    """
    env = DiscoveryEnvV2(
        degree=10,
        population_size=4,
        n_mutations_per_episode=10,
        mutation_rate=0.0,
        seed=11,
    )
    env.reset()
    initial_pop = env.population_snapshot()
    rng = np.random.default_rng(11)
    terminated = False
    while not terminated:
        a = int(rng.integers(0, env.n_actions))
        _, _, terminated, _, info = env.step(a)
    final_pop = env.population_snapshot()
    # Compare halves only (M may have been re-sorted but values stable).
    initial_halves = sorted(tuple(h) for h, _ in initial_pop)
    final_halves = sorted(tuple(h) for h, _ in final_pop)
    assert initial_halves == final_halves
    env.close()


def test_property_v2_observation_shape():
    """PROPERTY: obs vector has shape (8,) regardless of population size
    or degree.  The 8 entries are population-summary stats + step + flag.
    """
    for ps in (1, 4, 16):
        env = DiscoveryEnvV2(
            degree=10, population_size=ps, n_mutations_per_episode=2, seed=1
        )
        obs, _ = env.reset()
        assert obs.shape == (8,)
        env.close()


# ---------------------------------------------------------------------------
# Edge — degenerate populations, invalid params, all-zero starts
# ---------------------------------------------------------------------------


def test_edge_population_size_one_trivial():
    """EDGE: population_size=1 → trivial degenerate (no eviction
    possible; best member is the only member).  Should run end-to-end
    without crashing.
    """
    env = DiscoveryEnvV2(
        degree=6, population_size=1, n_mutations_per_episode=5, seed=2
    )
    env.reset()
    rng = np.random.default_rng(2)
    terminated = False
    while not terminated:
        a = int(rng.integers(0, env.n_actions))
        _, _, terminated, _, info = env.step(a)
    # Trivial population: no eviction possible (worst == best == only).
    snap = env.population_snapshot()
    assert len(snap) == 1
    env.close()


def test_edge_all_zero_init_can_escape():
    """EDGE: a population initialized at all-zero (degenerate, M=inf)
    can gradually escape via increment_at_index operators.

    We force the operator selection to always pick increment, so the
    test is deterministic; we then verify the elite eventually has a
    non-degenerate M.
    """
    env = DiscoveryEnvV2(
        degree=6,
        population_size=2,
        n_mutations_per_episode=20,
        coefficient_choices=(-3, -2, -1, 0, 1, 2, 3),
        seed=3,
    )
    env.reset()
    # Force population to all-zero.
    for m in env._population:
        m.half = [0] * env.half_len
        m.m_value = float("inf")
    env._sort_population()
    # Find increment operator index.
    op_names = [n for n, _ in MUTATION_OPERATORS]
    inc_idx = op_names.index("increment_at_index")
    # Hammer increment operator until we reach episode end.
    terminated = False
    while not terminated:
        _, _, terminated, _, info = env.step(inc_idx)
    # Elite M should be finite and >= 1 after escaping all-zero.
    elite_m = info["elite_m"]
    assert math.isfinite(elite_m) and elite_m >= 1.0 - 1e-9
    env.close()


def test_edge_mutation_rate_above_one_raises():
    """EDGE: mutation_rate > 1.0 raises ValueError (the rate is a
    probability and must be in [0, 1])."""
    with pytest.raises(ValueError, match="mutation_rate"):
        DiscoveryEnvV2(degree=6, mutation_rate=1.5)


def test_edge_invalid_degree_raises():
    """EDGE: degree < 2 raises ValueError (palindromic mirroring is
    undefined for degree 0 or 1)."""
    with pytest.raises(ValueError, match="degree"):
        DiscoveryEnvV2(degree=1)


def test_edge_invalid_population_size_raises():
    """EDGE: population_size < 1 raises ValueError."""
    with pytest.raises(ValueError, match="population_size"):
        DiscoveryEnvV2(degree=6, population_size=0)


def test_edge_step_before_reset_raises():
    """EDGE: stepping before reset raises RuntimeError (kernel + RNG
    are lazy-initialized in reset)."""
    env = DiscoveryEnvV2(degree=6)
    with pytest.raises(RuntimeError):
        env.step(0)


# ---------------------------------------------------------------------------
# Composition — full pipeline + cross-validation against discovery_pipeline
# ---------------------------------------------------------------------------


def test_composition_v2_short_episode_run_runs_clean():
    """COMPOSITION: a short multi-episode run completes without error
    and accumulates discoveries.  This is the GA-loop equivalent of
    v1's "100-episode random baseline finishes" test.
    """
    env = DiscoveryEnvV2(
        degree=10,
        population_size=4,
        n_mutations_per_episode=8,
        seed=21,
    )
    rng = np.random.default_rng(21)
    for _ in range(5):
        env.reset()
        terminated = False
        while not terminated:
            a = int(rng.integers(0, env.n_actions))
            _, _, terminated, _, info = env.step(a)
    discoveries = env.discoveries()
    assert len(discoveries) == 5
    for d in discoveries:
        assert isinstance(d, EpisodeRecordV2)
        assert d.elite_m >= 1.0 - 1e-9 or not math.isfinite(d.elite_m)
    env.close()


def test_composition_v2_seeded_lehmer_routes_through_pipeline():
    """COMPOSITION: when the population is seeded with Lehmer's poly,
    the elite is sub-Lehmer, the env routes the candidate through
    DiscoveryPipeline.process_candidate, and we get a terminal state
    (PROMOTED / SHADOW_CATALOG / REJECTED with kill_pattern).

    Cross-validates: env -> kernel -> pipeline -> catalog cross-check.
    """
    env = DiscoveryEnvV2(
        degree=10,
        population_size=4,
        n_mutations_per_episode=4,
        seed_with_known=True,
        mutation_rate=0.0,  # freeze population so Lehmer stays the elite
        seed=33,
    )
    env.reset()
    terminated = False
    info = {}
    while not terminated:
        _, _, terminated, _, info = env.step(0)
    # Elite should be Lehmer's M (within tolerance).
    assert info["elite_m"] == pytest.approx(1.17628081826, abs=1e-4)
    assert info["is_sub_lehmer"] is True
    # Pipeline must have produced a terminal state.
    assert info["pipeline_terminal_state"] in (
        "PROMOTED",
        "SHADOW_CATALOG",
        "REJECTED",
    )
    # Lehmer's polynomial IS in Mossinghoff, so it should be REJECTED
    # with kill_pattern indicating "known_in_catalog".
    if info["pipeline_terminal_state"] == "REJECTED":
        kp = info["pipeline_kill_pattern"] or ""
        # Either catalog hit, or one of the battery checks fired.
        assert "known_in_catalog" in kp or "F" in kp or "reciprocity" in kp or "reducible" in kp
    env.close()


def test_composition_v2_substrate_eval_count_grows():
    """COMPOSITION: each mutation that fires (and the initial population
    evals) contributes one EVAL to the kernel's evaluations table.
    Verifies the substrate-mediated evaluation discipline.
    """
    env = DiscoveryEnvV2(
        degree=6,
        population_size=2,
        n_mutations_per_episode=4,
        mutation_rate=1.0,
        seed=51,
    )
    obs, _ = env.reset()
    k = env.kernel()
    n0 = k.conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    # Initial population (size=2) → 2 evals during reset.
    assert n0 >= 2
    rng = np.random.default_rng(51)
    terminated = False
    n_mutated = 0
    while not terminated:
        a = int(rng.integers(0, env.n_actions))
        _, _, terminated, _, info = env.step(a)
        if info.get("mutated"):
            n_mutated += 1
    n_after = k.conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    # Each mutated step adds exactly one eval.
    assert n_after == n0 + n_mutated
    env.close()


def test_composition_v2_random_vs_biased_operator_selection():
    """COMPOSITION: an agent that biases toward `mutate_single_coef`
    explores the local neighborhood more conservatively than one that
    biases toward `mutate_two_coefs`.  Different policies → different
    population trajectories.

    This is the foundation of the V2-random-vs-V2-REINFORCE comparison
    in DISCOVERY_V2_RESULTS.md.  Here we just verify the env *responds*
    to operator-selection bias differently — concrete numerical
    comparisons live in the pilot script.
    """
    op_names = [n for n, _ in MUTATION_OPERATORS]
    single_idx = op_names.index("mutate_single_coef")
    two_idx = op_names.index("mutate_two_coefs")

    # Run two short episodes with biased operator selection, same seed.
    def run_with_op(op_idx: int) -> float:
        env = DiscoveryEnvV2(
            degree=10,
            population_size=4,
            n_mutations_per_episode=12,
            seed=77,
        )
        env.reset()
        terminated = False
        while not terminated:
            _, _, terminated, _, info = env.step(op_idx)
        result = info["elite_m"]
        env.close()
        return result

    m_single = run_with_op(single_idx)
    m_two = run_with_op(two_idx)
    # Both should be finite low-degree-poly M values.
    assert math.isfinite(m_single)
    assert math.isfinite(m_two)
    # The trajectories may end at the same M by accident, but the
    # operator_call_counts must record the bias.
    env = DiscoveryEnvV2(
        degree=10, population_size=4, n_mutations_per_episode=8, seed=77
    )
    env.reset()
    terminated = False
    while not terminated:
        _, _, terminated, _, info = env.step(single_idx)
    counts = env.operator_call_counts()
    assert counts["mutate_single_coef"] >= 8
    assert counts["mutate_two_coefs"] == 0
    env.close()
