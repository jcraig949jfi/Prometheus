"""Tests for ergon.learner.reward and ergon.learner.stability."""
from __future__ import annotations

import pytest

from ergon.learner.descriptor import OUT_OF_BAND_BUCKET
from ergon.learner.genome import Genome, NodeRef
from ergon.learner.reward import (
    MVP_REWARD_WEIGHTS,
    RewardComponents,
    V8_REWARD_WEIGHTS_FULL,
    V8_REWARD_WEIGHTS_POST_TRIAL_1,
    compute_reward,
    evaluate_substrate_pass,
    is_promotable,
)
from ergon.learner.stability import (
    INPUT_JITTER_EPSILON,
    INPUT_JITTER_N_TRIALS,
    INPUT_JITTER_PASS_THRESHOLD,
    StabilityCheckResult,
    perturbation_stability_check,
)


# ===========================================================================
# Authority — v8 weights match specification literals
# ===========================================================================


def test_v8_full_weights_match_spec():
    """v8 §5.3: w_S=0.40, w_X=0.15, w_H=0.20, w_NL=0.10, w_R=0.15."""
    assert V8_REWARD_WEIGHTS_FULL["w_S"] == 0.40
    assert V8_REWARD_WEIGHTS_FULL["w_X"] == 0.15
    assert V8_REWARD_WEIGHTS_FULL["w_H"] == 0.20
    assert V8_REWARD_WEIGHTS_FULL["w_NL"] == 0.10
    assert V8_REWARD_WEIGHTS_FULL["w_R"] == 0.15
    assert sum(V8_REWARD_WEIGHTS_FULL.values()) == pytest.approx(1.0)


def test_post_trial_1_weights_renormalized():
    """Trial 1 outcome: w_R=0; remaining weights renormalize to sum to 1.0."""
    assert V8_REWARD_WEIGHTS_POST_TRIAL_1["w_R"] == 0.0
    total = sum(V8_REWARD_WEIGHTS_POST_TRIAL_1.values())
    assert total == pytest.approx(1.0, abs=1e-9)


def test_mvp_weights_promote_only():
    """At MVP scope: w_S=1.0, all others=0 (only substrate-pass active)."""
    assert MVP_REWARD_WEIGHTS["w_S"] == 1.0
    assert MVP_REWARD_WEIGHTS["w_X"] == 0.0
    assert MVP_REWARD_WEIGHTS["w_H"] == 0.0
    assert MVP_REWARD_WEIGHTS["w_NL"] == 0.0
    assert MVP_REWARD_WEIGHTS["w_R"] == 0.0


def test_stability_thresholds_match_v8():
    """v8 §6.2: ε=0.001 across 100 trials, ≥95% pass rate."""
    assert INPUT_JITTER_EPSILON == 0.001
    assert INPUT_JITTER_N_TRIALS == 100
    assert INPUT_JITTER_PASS_THRESHOLD == 0.95


# ===========================================================================
# Property — reward computation semantics
# ===========================================================================


def test_compute_reward_mvp_uses_substrate_pass_only():
    """At MVP, only substrate_pass contributes to reward."""
    components = RewardComponents(
        substrate_pass=1.0,
        cross_model_logical=1.0,  # set but ignored at MVP
        holdout_battery_pass=1.0,
        non_llm_evaluator_pass=1.0,
        signal_class_residual=1.0,
    )
    reward = compute_reward(components)  # default = MVP_REWARD_WEIGHTS
    assert reward == 1.0  # substrate_pass=1, all other weights=0


def test_compute_reward_zero_substrate_zero_reward():
    components = RewardComponents(substrate_pass=0.0)
    reward = compute_reward(components)
    assert reward == 0.0


def test_compute_reward_v8_full_weights_aggregates():
    """With full v8 weights, reward = weighted sum across all 5 components."""
    components = RewardComponents(
        substrate_pass=1.0,
        cross_model_logical=1.0,
        holdout_battery_pass=1.0,
        non_llm_evaluator_pass=1.0,
        signal_class_residual=1.0,
    )
    reward = compute_reward(components, weights=V8_REWARD_WEIGHTS_FULL)
    assert reward == pytest.approx(1.0)  # all components at max → sum = 1.0


def test_compute_reward_post_trial_1_ignores_residual():
    """Post-Trial-1: setting signal_class_residual=1 has no effect (w_R=0)."""
    components_with_residual = RewardComponents(
        substrate_pass=1.0,
        cross_model_logical=1.0,
        holdout_battery_pass=1.0,
        non_llm_evaluator_pass=1.0,
        signal_class_residual=1.0,
    )
    components_without = RewardComponents(
        substrate_pass=1.0,
        cross_model_logical=1.0,
        holdout_battery_pass=1.0,
        non_llm_evaluator_pass=1.0,
        signal_class_residual=0.0,
    )
    r1 = compute_reward(components_with_residual, weights=V8_REWARD_WEIGHTS_POST_TRIAL_1)
    r2 = compute_reward(components_without, weights=V8_REWARD_WEIGHTS_POST_TRIAL_1)
    assert r1 == r2


def test_is_promotable_at_threshold():
    """Default threshold = 0.5; substrate_pass=1.0 → promotable at MVP."""
    components = RewardComponents(substrate_pass=1.0)
    assert is_promotable(components)


def test_is_not_promotable_zero_substrate():
    components = RewardComponents(substrate_pass=0.0)
    assert not is_promotable(components)


# ===========================================================================
# Property — substrate_pass from kill-test verdicts
# ===========================================================================


def test_substrate_pass_unanimous_clear():
    verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
    assert evaluate_substrate_pass(verdicts) == 1.0


def test_substrate_pass_with_warns_still_passes():
    verdicts = {"F1": "CLEAR", "F6": "WARN", "F9": "CLEAR", "F11": "WARN"}
    assert evaluate_substrate_pass(verdicts) == 1.0


def test_substrate_block_kills_promotion():
    verdicts = {"F1": "CLEAR", "F6": "BLOCK", "F9": "CLEAR", "F11": "CLEAR"}
    assert evaluate_substrate_pass(verdicts) == 0.0


def test_substrate_missing_test_treats_as_block():
    """Missing kill-test verdict defaults to BLOCK (defense-in-depth)."""
    verdicts = {"F1": "CLEAR", "F6": "CLEAR"}  # F9 + F11 missing
    assert evaluate_substrate_pass(verdicts) == 0.0


# ===========================================================================
# Property — stability check (MVP stub behavior)
# ===========================================================================


def make_test_genome() -> Genome:
    return Genome(
        nodes=(
            NodeRef(callable_ref="atom_a", arg_bindings=(("literal", 1),)),
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )


def test_stability_low_magnitude_trivially_passes():
    """Low-magnitude buckets (0, 1, 2) trivially pass without evaluation."""
    g = make_test_genome()
    for bucket in (0, 1, 2):
        result = perturbation_stability_check(
            genome=g,
            nominal_magnitude=10.0 ** (bucket * 3),
            nominal_bucket=bucket,
            evaluator_fn=None,
        )
        assert result.passes
        assert result.new_magnitude_bucket == bucket
        assert result.metadata.get("trivial_pass_low_magnitude")


def test_stability_high_magnitude_mvp_stub_passes():
    """High-magnitude buckets pass-through under MVP stub (no evaluator wired)."""
    g = make_test_genome()
    result = perturbation_stability_check(
        genome=g,
        nominal_magnitude=1e10,
        nominal_bucket=3,
        evaluator_fn=None,
    )
    assert result.passes
    assert result.new_magnitude_bucket == 3
    assert result.metadata.get("mvp_stub_pass")


def test_stability_with_evaluator_fn_unstable_fails():
    """When evaluator_fn returns wildly different magnitudes, stability fails."""
    g = make_test_genome()

    # Stub evaluator that returns out-of-bucket magnitude on most jitter trials
    def unstable_eval(genome, jitter_epsilon=None, jitter_seed=None, precision=None):
        if jitter_seed is not None:
            # 95% of jitter trials produce small magnitude (bucket 0)
            return 1.0 if jitter_seed % 20 != 0 else 1e10
        # Half-precision: also drop to bucket 0
        return 1.0

    result = perturbation_stability_check(
        genome=g,
        nominal_magnitude=1e10,
        nominal_bucket=3,
        evaluator_fn=unstable_eval,
    )
    assert not result.passes
    assert result.input_jitter_pass_rate < 0.95
    assert result.new_magnitude_bucket == OUT_OF_BAND_BUCKET


def test_stability_with_evaluator_fn_stable_passes():
    """When evaluator_fn returns consistent magnitudes, stability passes."""
    g = make_test_genome()

    # Stub evaluator that returns same bucket-3 magnitude on all trials
    def stable_eval(genome, jitter_epsilon=None, jitter_seed=None, precision=None):
        return 1e10  # always bucket 3

    result = perturbation_stability_check(
        genome=g,
        nominal_magnitude=1e10,
        nominal_bucket=3,
        evaluator_fn=stable_eval,
    )
    assert result.passes
    assert result.input_jitter_pass_rate == 1.0
    assert result.half_precision_pass
    assert result.new_magnitude_bucket == 3
