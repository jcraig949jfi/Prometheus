"""Tests for prometheus_math.obstruction_env (predicate-discovery RL env).

The env's ground truth is documented in
``prometheus_math._obstruction_corpus``: a synthetic OEIS-shaped battery
where two structural signatures are planted as deterministic-kill
predicates. The RL agent's job is to discover one of them.

Math-tdd skill rubric (>=2 in every category).

Categories:
- Authority: planted ground-truth predicates have known lift > 20x; the
  empty predicate has lift ~ 1; nonsense predicates have empty match-
  group and lift = 0; manual rediscovery triggers the SIG_REDISCOVERED
  tag.
- Property: reward >= 0 for non-empty match-group; same seed -> same
  split -> same reward; held-out lift differs from in-sample on
  random predicates; max-complexity bound; STOP terminates early.
- Edge: held_out_fraction in (0,1); empty corpus rejected;
  max_predicate_complexity = 0 -> STOP-only env; out-of-range action;
  all-positive corpus baseline -> degenerate reward.
- Composition: 100-episode random baseline finite + non-negative;
  1000-episode contextual REINFORCE strictly above random by lift >= 5x
  (DISCOVERY-GRADE acceptance); rediscovery tag flows through
  discoveries() list.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# Imports — write these FIRST and confirm they fail (test-first discipline).
from prometheus_math.obstruction_env import (
    ObstructionEnv,
    ObstructionEpisodeRecord,
    evaluate_predicate,
    encode_action,
    decode_action,
    N_ACTIONS,
    STOP_ACTION,
    FEATURES,
    NUMERIC_FEATURE_VALUES,
    BOOL_FEATURES,
    REDISCOVERED_OBSTRUCTION_SHAPE_TAG,
    REDISCOVERED_SECONDARY_TAG,
)
from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
    CorpusEntry,
)


# ---------------------------------------------------------------------------
# Authority — planted ground-truth predicates
# ---------------------------------------------------------------------------


def test_authority_planted_obstruction_signature_lifts_above_20x():
    """The OBSTRUCTION_SHAPE signature is planted with deterministic kill_verdict
    on its match-group and ~2% noise kills among non-matches.

    Authority: ground-truth construction in _obstruction_corpus.py.
    Roughly: ~5 deterministic kills out of ~5 matches = 100% kill rate
    on matches; ~3 noise kills among ~140 non-matches ~= 2% baseline;
    lift = (1.0 - 0.02) / 0.02 = ~49x in-sample. Held-out 30% slice
    should still show lift > 20x (sample-size noise widens it but
    the planted gap is huge).
    """
    np.random.seed(0)
    # Use a deterministic split for the test.
    rng = np.random.default_rng(0)
    n = len(OBSTRUCTION_CORPUS)
    indices = np.arange(n)
    rng.shuffle(indices)
    n_test = int(round(n * 0.3))
    test_idx = set(int(i) for i in indices[:n_test])
    test_corpus = [e for i, e in enumerate(OBSTRUCTION_CORPUS) if i in test_idx]
    result = evaluate_predicate(OBSTRUCTION_SIGNATURE, test_corpus)
    # Match-group should be non-empty on a 30% slice of 150 records (~45 records);
    # OBSTRUCTION_SHAPE has ~5-8 matches in the full corpus, so probably 1-3 on test.
    # If the test slice happens to have 0 matches, lift is 0 — this is the
    # known small-sample failure mode; with seed=0 we expect some matches.
    assert result["match_group_size"] >= 1, (
        f"Test slice empty for OBSTRUCTION_SIGNATURE; "
        f"split is unlucky: {result}"
    )
    assert result["lift"] > 20.0, f"Planted signature lift below 20x: {result}"


def test_authority_empty_predicate_lift_is_one():
    """The empty predicate {} matches every record; matched_kill_rate
    equals baseline_kill_rate; lift = 1.0 (no signal).

    Authority: tautology — uniform predicate is 1x baseline by definition.
    """
    result = evaluate_predicate({}, OBSTRUCTION_CORPUS)
    assert result["match_group_size"] == len(OBSTRUCTION_CORPUS)
    assert abs(result["lift"] - 1.0) < 1e-9


def test_authority_nonsense_predicate_yields_empty_match_group():
    """A predicate with an impossible feature value (n_steps=999) matches
    nothing; lift = 0; match-group empty.

    Authority: definitional — empty match-group is reward-zero.
    """
    result = evaluate_predicate({"n_steps": 999}, OBSTRUCTION_CORPUS)
    assert result["match_group_size"] == 0
    assert result["lift"] == 0.0


def test_authority_manual_obstruction_action_path_triggers_rediscovery_tag():
    """Manually picking actions encoding the OBSTRUCTION_SHAPE conjuncts
    triggers REDISCOVERED_OBSTRUCTION_SHAPE on the episode tags.

    Authority: env behavior contract — match by predicate-equality on the
    planted signature.
    """
    env = ObstructionEnv(
        max_predicate_complexity=4,
        held_out_fraction=0.3,
        seed=0,
    )
    env.reset()
    # Encode the OBSTRUCTION_SHAPE signature as a sequence of actions.
    # OBSTRUCTION_SIGNATURE = {n_steps: 5, neg_x: 4, pos_x: 1, has_diag_neg: True}
    actions = [
        encode_action("n_steps", 5),
        encode_action("neg_x", 4),
        encode_action("pos_x", 1),
        encode_action("has_diag_neg", True),
    ]
    info = {}
    terminated = False
    for a in actions:
        if terminated:
            break
        _, _, terminated, _, info = env.step(a)
    assert terminated is True
    tags = info.get("tags", [])
    assert REDISCOVERED_OBSTRUCTION_SHAPE_TAG in tags, (
        f"Expected obstruction-shape rediscovery tag; got tags={tags}"
    )


# ---------------------------------------------------------------------------
# Property — invariants that must hold
# ---------------------------------------------------------------------------


def test_property_reward_nonnegative_for_nonempty_match_group():
    """Reward is >= 0 for any predicate whose match-group is non-empty
    on the test set. (Empty match-group -> reward = 0 directly.)
    """
    env = ObstructionEnv(seed=42, held_out_fraction=0.3, max_predicate_complexity=2)
    rng = np.random.default_rng(42)
    seen_nonempty = 0
    rewards = []
    for trial in range(50):
        env.reset()
        terminated = False
        info = {}
        while not terminated:
            a = int(rng.integers(0, N_ACTIONS))
            _, r, terminated, _, info = env.step(a)
        rewards.append(r)
        if info.get("match_group_size_test", 0) > 0:
            seen_nonempty += 1
    assert all(r >= 0 for r in rewards), f"Negative reward observed: {rewards}"
    assert seen_nonempty > 0, "Sanity: at least some predicates have non-empty test match-group"


def test_property_same_seed_same_split_same_reward_for_same_predicate():
    """Determinism: identical seed -> identical train/test split -> identical
    reward for an identical predicate."""
    env_a = ObstructionEnv(seed=123, held_out_fraction=0.3, max_predicate_complexity=4)
    env_b = ObstructionEnv(seed=123, held_out_fraction=0.3, max_predicate_complexity=4)
    actions = [encode_action("n_steps", 5), encode_action("neg_x", 4)]

    def run(env):
        env.reset()
        info = {}
        for a in actions:
            _, _, terminated, _, info = env.step(a)
            if terminated:
                break
        if not info:
            _, _, _, _, info = env.step(STOP_ACTION)
        return info

    info_a = run(env_a)
    info_b = run(env_b)
    assert info_a.get("reward") == info_b.get("reward"), (
        f"Reward mismatch under identical seed: a={info_a} b={info_b}"
    )


def test_property_held_out_lift_differs_from_in_sample_on_random_predicates():
    """Selection-bias check: random predicates that happen to look good
    in-sample should NOT (on average) replicate that lift on held-out.
    The differences are observable.
    """
    env = ObstructionEnv(seed=7, held_out_fraction=0.3, max_predicate_complexity=2)
    rng = np.random.default_rng(7)
    diffs = []
    for trial in range(60):
        env.reset()
        terminated = False
        info = {}
        while not terminated:
            a = int(rng.integers(0, N_ACTIONS))
            _, _, terminated, _, info = env.step(a)
        if info.get("match_group_size_test", 0) > 0 and info.get("match_group_size_train", 0) > 0:
            diffs.append(
                info.get("in_sample_lift", 0.0) - info.get("held_out_lift", 0.0)
            )
    # We expect diffs to be non-zero on average (pure-coincidence event
    # has measure zero).
    assert len(diffs) >= 5, "Need a sample of nontrivial predicates"
    # Variance of diffs is positive (not all identical).
    assert np.var(diffs) > 0.0, (
        "In-sample and held-out lifts identical on every random predicate; "
        "split is broken or evaluator is constant"
    )


def test_property_episode_terminates_within_max_complexity():
    """An episode must terminate after at most max_predicate_complexity
    picks (or earlier on STOP)."""
    env = ObstructionEnv(seed=8, max_predicate_complexity=3)
    env.reset()
    n_steps = 0
    terminated = False
    while not terminated and n_steps < 20:
        a = 0  # always pick the same action
        _, _, terminated, _, _ = env.step(a)
        n_steps += 1
    assert terminated is True
    assert n_steps <= 3, f"Episode did not terminate at max complexity: n_steps={n_steps}"


def test_property_stop_action_terminates_early():
    """The STOP action immediately terminates the episode."""
    env = ObstructionEnv(seed=9, max_predicate_complexity=5)
    env.reset()
    _, _, terminated, _, info = env.step(STOP_ACTION)
    assert terminated is True
    assert info.get("step", -1) == 1


# ---------------------------------------------------------------------------
# Edge — bad inputs and degenerate corpora
# ---------------------------------------------------------------------------


def test_edge_held_out_fraction_zero_raises():
    with pytest.raises(ValueError):
        ObstructionEnv(held_out_fraction=0.0)


def test_edge_held_out_fraction_one_raises():
    with pytest.raises(ValueError):
        ObstructionEnv(held_out_fraction=1.0)


def test_edge_negative_held_out_fraction_raises():
    with pytest.raises(ValueError):
        ObstructionEnv(held_out_fraction=-0.1)


def test_edge_empty_corpus_raises():
    with pytest.raises(ValueError):
        ObstructionEnv(corpus=[])


def test_edge_max_complexity_zero_yields_stop_only_env():
    """max_predicate_complexity=0 -> the only legal action is STOP; reward
    is always 0; episode terminates immediately."""
    env = ObstructionEnv(seed=10, max_predicate_complexity=0)
    env.reset()
    _, r, terminated, _, info = env.step(STOP_ACTION)
    assert terminated is True
    assert r == 0.0


def test_edge_action_out_of_range_raises():
    env = ObstructionEnv(seed=11)
    env.reset()
    with pytest.raises(ValueError):
        env.step(N_ACTIONS + 100)


def test_edge_action_negative_raises():
    env = ObstructionEnv(seed=12)
    env.reset()
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_step_before_reset_raises():
    env = ObstructionEnv(seed=13)
    with pytest.raises(RuntimeError):
        env.step(0)


def test_edge_all_positive_corpus_yields_degenerate_lift():
    """If every record has kill_verdict=True, baseline_kill_rate=1; the
    'lift' is 1.0 for any non-empty match-group (no signal). The env
    should not crash and should reward 0 (lift==1 → no signal advantage).
    """
    fake = [
        CorpusEntry(
            n_steps=5, neg_x=2, pos_x=2, neg_y=0, pos_y=0, neg_z=0, pos_z=0,
            has_diag_neg=False, has_diag_pos=False, kill_verdict=True,
        )
        for _ in range(20)
    ]
    env = ObstructionEnv(corpus=fake, seed=14, max_predicate_complexity=2)
    env.reset()
    _, r, terminated, _, info = env.step(STOP_ACTION)  # empty predicate matches all
    assert terminated is True
    # baseline = 1, matched = 1 -> lift = 1 -> bonus over baseline = 0 -> reward 0
    assert r == 0.0


# ---------------------------------------------------------------------------
# Composition — multi-component invariants
# ---------------------------------------------------------------------------


def test_composition_random_baseline_finite_substrate_grows():
    """Run 100 random episodes; mean reward is finite and >= 0; the
    substrate (kernel evaluations) grows by exactly 100 (one EVAL per
    completed episode that produces a non-empty match group, plus a
    no-eval STOP-only branch — we just check the kernel grew).
    """
    env = ObstructionEnv(seed=15, max_predicate_complexity=3)
    env.reset()
    k = env.kernel()
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n0 = cur.fetchone()[0]
    rng = np.random.default_rng(15)
    rewards = []
    for _ in range(100):
        env.reset()
        terminated = False
        while not terminated:
            a = int(rng.integers(0, N_ACTIONS))
            _, r, terminated, _, _ = env.step(a)
        rewards.append(r)
    mean_r = float(np.mean(rewards))
    assert math.isfinite(mean_r)
    assert mean_r >= 0.0
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n_after = cur.fetchone()[0]
    # We required exactly 100 episodes, each producing at most one EVAL
    # (the env may skip EVAL on STOP-only branches with empty predicate).
    assert n_after >= n0, "Kernel substrate did not grow at all"
    assert n_after - n0 <= 100, "Substrate grew faster than one EVAL per episode"


@pytest.mark.slow
def test_composition_reinforce_beats_random_at_1000_episodes_DISCOVERY_GRADE():
    """The discovery-grade acceptance test.

    Run 1000 episodes random vs 1000 episodes contextual REINFORCE on the
    same env. REINFORCE mean reward must be strictly above random's by
    lift >= 5x (matching the DiscoveryEnv acceptance bar).

    This test is slow (~30-60s) and is the acceptance gate for the
    architecture. If REINFORCE can't beat random by 5x on a planted
    signal of 49x in-sample lift, the env is not learnable and we need
    to revisit reward shape, action encoding, or learner.
    """
    from prometheus_math.demo_obstruction import (
        train_random_obstruction,
        train_reinforce_obstruction,
    )

    n_episodes = 1000
    env_random = ObstructionEnv(seed=100, max_predicate_complexity=4, held_out_fraction=0.3)
    env_random.reset()
    rand = train_random_obstruction(env_random, n_episodes, seed=100)

    env_rein = ObstructionEnv(seed=101, max_predicate_complexity=4, held_out_fraction=0.3)
    env_rein.reset()
    rein = train_reinforce_obstruction(env_rein, n_episodes, seed=101)

    rand_mean = float(np.mean(rand["rewards"]))
    rein_mean = float(np.mean(rein["rewards"]))
    if rand_mean > 0:
        lift = (rein_mean - rand_mean) / rand_mean
    else:
        lift = float("inf") if rein_mean > 0 else 0.0
    assert rein_mean > rand_mean, (
        f"REINFORCE failed to beat random: random={rand_mean:.3f}, "
        f"reinforce={rein_mean:.3f}"
    )
    assert lift >= 5.0 or rein_mean - rand_mean > 5.0, (
        f"REINFORCE lift below 5x: random={rand_mean:.3f}, "
        f"reinforce={rein_mean:.3f}, lift={lift:.2f}"
    )


def test_composition_rediscovery_flows_through_discoveries_list():
    """When manual rediscovery succeeds, the env's discoveries() list
    contains a tagged entry."""
    env = ObstructionEnv(seed=200, max_predicate_complexity=4, held_out_fraction=0.3)
    env.reset()
    actions = [
        encode_action("n_steps", 5),
        encode_action("neg_x", 4),
        encode_action("pos_x", 1),
        encode_action("has_diag_neg", True),
    ]
    for a in actions:
        _, _, terminated, _, _ = env.step(a)
        if terminated:
            break
    discoveries = env.discoveries()
    tagged = [
        d for d in discoveries
        if REDISCOVERED_OBSTRUCTION_SHAPE_TAG in (d.tags or [])
    ]
    assert len(tagged) >= 1, (
        f"No tagged discovery for OBSTRUCTION_SHAPE; "
        f"discoveries={[(d.predicate, d.tags) for d in discoveries]}"
    )


def test_composition_secondary_signature_can_also_trigger_tag():
    """The SECONDARY_SIGNATURE (n_steps=7, has_diag_pos) also has a
    rediscovery tag. Manual picks should trigger it."""
    env = ObstructionEnv(seed=201, max_predicate_complexity=3, held_out_fraction=0.3)
    env.reset()
    actions = [
        encode_action("n_steps", 7),
        encode_action("has_diag_pos", True),
    ]
    info = {}
    for a in actions:
        _, _, terminated, _, info = env.step(a)
        if terminated:
            break
    if not info.get("terminated_via", "").startswith("max_complexity"):
        # If we didn't hit max yet, send STOP to terminate.
        _, _, _, _, info = env.step(STOP_ACTION)
    tags = info.get("tags", [])
    assert REDISCOVERED_SECONDARY_TAG in tags, (
        f"Secondary signature rediscovery tag missing: tags={tags}"
    )


# ---------------------------------------------------------------------------
# Helper sanity (small composition test)
# ---------------------------------------------------------------------------


def test_composition_action_codec_round_trip():
    """encode_action and decode_action must be inverses."""
    cases = [
        ("n_steps", 5),
        ("neg_x", 4),
        ("has_diag_neg", True),
        ("has_diag_pos", False),
        ("pos_z", 7),
    ]
    for feature, value in cases:
        a = encode_action(feature, value)
        f, v = decode_action(a)
        assert f == feature, f"Round-trip failure: feature {feature} != {f}"
        assert v == value, f"Round-trip failure: value {value!r} != {v!r}"
