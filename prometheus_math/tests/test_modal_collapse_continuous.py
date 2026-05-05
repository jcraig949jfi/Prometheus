"""Tests for prometheus_math.modal_collapse_continuous.

Day-2 follow-up to ``test_modal_collapse_synthetic``. The continuous-
reward variant swaps the binary 0/1 reward for one of {L2, L1, log}
distance to the true continuous y. Same env, same trainers, same
hyperparameters as Day 1.

Authority -- the continuous reward is bounded above by 0, bounded
below by -REWARD_FLOOR, maps to bin centers correctly, and the lstsq
authority gate (V3 solvable at >=60%) still holds (the env is
unchanged).

Property -- determinism with fixed seed; reward is non-positive;
aggregation in run_diagnostic is correct.

Edge -- zero error -> reward=0; very large error -> reward >= -REWARD_FLOOR;
degenerate w (would-be unlearnable env) doesn't crash.

Composition -- full pipeline runs; 3-reward x 3-algorithm comparison
dict is well-formed; per-bin distribution recoverable per cell.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.modal_collapse_continuous import (
    REWARD_FLOOR,
    REWARD_VARIANTS,
    VARIANTS,
    bin_centers,
    continuous_reward,
    run_diagnostic,
    train_ppo,
    train_random,
    train_reinforce,
)
from prometheus_math.modal_collapse_synthetic import (
    N_BINS,
    SyntheticRegressionEnv,
)


# ---------------------------------------------------------------------------
# Authority -- ground-truth correctness of the reward map
# ---------------------------------------------------------------------------


def test_authority_l2_reward_bounded():
    """L2 continuous reward must lie in [-REWARD_FLOOR, 0] for all inputs."""
    rng = np.random.default_rng(0)
    for _ in range(200):
        pred = float(rng.standard_normal()) * 5.0
        true = float(rng.standard_normal()) * 5.0
        r = continuous_reward(pred, true, "L2")
        assert -REWARD_FLOOR <= r <= 0.0, (
            f"L2 reward out of bounds: pred={pred}, true={true}, r={r}"
        )


def test_authority_reward_maps_to_bin_centers():
    """``bin_centers`` returns finite y values for every bin index, and
    ``_step_with_continuous_reward`` semantics match: predicting bin k
    against a true y gives ``continuous_reward(centers[k], true_y, ...)``.
    """
    env = SyntheticRegressionEnv(binning="balanced", sigma=0.1, seed=0)
    centers = bin_centers(env)
    assert centers.shape == (env.n_bins(),)
    assert np.all(np.isfinite(centers))
    edges = env.edges()
    # Inner bins: center is the average of the two adjacent edges.
    for k in range(1, env.n_bins() - 1):
        expected = 0.5 * (edges[k] + edges[k + 1])
        assert centers[k] == pytest.approx(expected)
    # Skewed env: outer bins have +/-1e9 sentinels; centers must be finite.
    env_sk = SyntheticRegressionEnv(binning="skewed", sigma=0.1, seed=0)
    centers_sk = bin_centers(env_sk)
    assert np.all(np.isfinite(centers_sk))
    assert abs(centers_sk[0]) < 1e6
    assert abs(centers_sk[-1]) < 1e6


def test_authority_lstsq_still_solves_v3():
    """Authority gate (Day 1 invariant): lstsq on V3 low-noise still
    solves at >=60% bin accuracy. The continuous reward changes nothing
    about the env, so this must still hold.
    """
    env = SyntheticRegressionEnv(
        d=10, n_bins=21, binning="balanced", sigma=0.01,
        corpus_seed=0, seed=0,
    )
    Xs, ys, true_bins = [], [], []
    for _ in range(1000):
        _obs, info = env.reset()
        Xs.append(env._current_x.copy())
        ys.append(info["y"])
        true_bins.append(info["true_bin"])
        env.step(0)
    X = np.stack(Xs)
    y = np.asarray(ys)
    tb = np.asarray(true_bins)
    A = np.hstack([X, np.ones((X.shape[0], 1))])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    edges = env.edges()
    pred_bins = np.clip(
        np.searchsorted(edges, pred, side="right") - 1,
        0, env.n_bins() - 1,
    )
    acc = float((pred_bins == tb).mean())
    assert acc >= 0.6, (
        f"lstsq authority gate FAILED on V3: acc={acc:.3f} < 0.6"
    )


def test_authority_reward_variants_exist():
    """All three reward variants are implemented and produce different
    values for a non-trivial error.
    """
    pred, true = 0.0, 1.0
    r_l2 = continuous_reward(pred, true, "L2")
    r_l1 = continuous_reward(pred, true, "L1")
    r_log = continuous_reward(pred, true, "log")
    assert r_l2 < 0.0
    assert r_l1 < 0.0
    assert r_log < 0.0
    # The three rewards are not all the same number.
    assert len({round(r_l2, 4), round(r_l1, 4), round(r_log, 4)}) >= 2


# ---------------------------------------------------------------------------
# Property -- determinism, sign, aggregation
# ---------------------------------------------------------------------------


def test_property_determinism_fixed_seed():
    """Same seed => identical pred_counts and accuracy across runs."""
    env_a = SyntheticRegressionEnv(binning="balanced", sigma=0.1, seed=0)
    env_b = SyntheticRegressionEnv(binning="balanced", sigma=0.1, seed=0)
    res_a = train_reinforce(env_a, n_episodes=300, reward_variant="L2", seed=7)
    res_b = train_reinforce(env_b, n_episodes=300, reward_variant="L2", seed=7)
    assert res_a["pred_counts"] == res_b["pred_counts"]
    assert res_a["accuracy"] == pytest.approx(res_b["accuracy"])
    assert res_a["mean_reward"] == pytest.approx(res_b["mean_reward"])


def test_property_reward_non_positive():
    """Continuous reward over a training run is always <= 0."""
    env = SyntheticRegressionEnv(binning="balanced", sigma=0.1, seed=0)
    for variant in REWARD_VARIANTS:
        res = train_random(env, n_episodes=200, reward_variant=variant, seed=0)
        rewards = np.asarray(res["rewards"])
        assert np.all(rewards <= 1e-9), (
            f"variant {variant}: positive reward observed (max={rewards.max()})"
        )


def test_property_aggregation_correct():
    """run_diagnostic per-cell pred_counts_mean averages over seeds."""
    rep = run_diagnostic(
        n_episodes=200, seeds=(0, 1),
        reward_variants=("L2",), d=10, n_bins=11,
    )
    assert "rewards" in rep
    block = rep["rewards"]["L2"]
    for v_name, v_data in block.items():
        for agent, agent_res in v_data.items():
            pc = np.asarray(agent_res["pred_counts_mean"])
            assert pc.shape == (11,)
            # Mean per-seed pred_counts must sum to n_episodes.
            assert int(round(pc.sum())) == 200, (
                f"{v_name}/{agent}: pc sum={pc.sum()} != 200"
            )


# ---------------------------------------------------------------------------
# Edge -- degenerate inputs
# ---------------------------------------------------------------------------


def test_edge_zero_error_reward_zero():
    """Predicted y == true y => reward exactly 0 in all variants."""
    for variant in REWARD_VARIANTS:
        r = continuous_reward(3.14, 3.14, variant)
        assert r == 0.0, f"variant {variant}: zero-error reward = {r}, expected 0"


def test_edge_very_large_error_clipped():
    """|error| >> 1 => reward floor at -REWARD_FLOOR (no -inf, no NaN)."""
    for variant in REWARD_VARIANTS:
        r = continuous_reward(1000.0, 0.0, variant)
        assert r >= -REWARD_FLOOR, (
            f"variant {variant}: large-error reward {r} below floor"
        )
        assert math.isfinite(r), f"variant {variant}: non-finite reward {r}"


def test_edge_unknown_reward_variant_raises():
    """Unknown variant strings should raise."""
    with pytest.raises(ValueError):
        continuous_reward(0.0, 1.0, "huber")
    env = SyntheticRegressionEnv(seed=0)
    with pytest.raises(ValueError):
        train_random(env, n_episodes=10, reward_variant="huber", seed=0)


def test_edge_log_reward_monotone_in_error():
    """log reward is monotone non-increasing in |error|."""
    errs = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 20.0]
    rs = [continuous_reward(e, 0.0, "log") for e in errs]
    for i in range(1, len(rs)):
        assert rs[i] <= rs[i - 1] + 1e-9, (
            f"log reward not monotone: errs={errs}, rs={rs}"
        )


# ---------------------------------------------------------------------------
# Composition -- full pipeline
# ---------------------------------------------------------------------------


def test_composition_full_pipeline_runs():
    """run_diagnostic with small budget completes for all 3 reward variants."""
    rep = run_diagnostic(
        n_episodes=100, seeds=(0,),
        reward_variants=REWARD_VARIANTS, d=8, n_bins=11,
    )
    assert set(rep["rewards"].keys()) == set(REWARD_VARIANTS)
    for r_variant, r_block in rep["rewards"].items():
        assert set(r_block.keys()) == set(VARIANTS.keys())
        for v_name, v_data in r_block.items():
            assert set(v_data.keys()) == {"random", "reinforce", "ppo"}


def test_composition_comparison_dict_well_formed():
    """Each cell of the 3 x 4 x 3 grid has the expected metric keys."""
    rep = run_diagnostic(
        n_episodes=100, seeds=(0, 1),
        reward_variants=("L1",), d=8, n_bins=11,
    )
    expected = {
        "acc_mean", "acc_std", "res_mean", "res_std",
        "reward_mean", "reward_std",
        "pred_counts_mean", "active_bins",
    }
    block = rep["rewards"]["L1"]
    for v_name, v_data in block.items():
        for agent, agent_res in v_data.items():
            assert expected <= set(agent_res.keys()), (
                f"missing keys in {v_name}/{agent}: "
                f"{expected - set(agent_res.keys())}"
            )
            assert 0.0 <= agent_res["acc_mean"] <= 1.0
            assert agent_res["reward_mean"] <= 1e-6


def test_composition_per_bin_distribution_recoverable():
    """Per-bin pred_counts_mean is a length-n_bins vector summing to
    the per-seed n_episodes (when normalised to the seed mean).
    """
    rep = run_diagnostic(
        n_episodes=200, seeds=(0, 1, 2),
        reward_variants=("L2",), d=8, n_bins=11,
    )
    block = rep["rewards"]["L2"]
    for v_name, v_data in block.items():
        for agent, agent_res in v_data.items():
            pc = np.asarray(agent_res["pred_counts_mean"])
            # active_bins consistent with pred_counts_mean
            n_active = int(np.sum(pc / pc.sum() >= 0.01))
            assert n_active == agent_res["active_bins"]


def test_composition_three_trainers_run_with_continuous_reward():
    """Smoke that random / reinforce / ppo all run with each reward variant."""
    for variant in REWARD_VARIANTS:
        for trainer, name in [(train_random, "random"),
                              (train_reinforce, "reinforce"),
                              (train_ppo, "ppo")]:
            env = SyntheticRegressionEnv(
                binning="balanced", sigma=0.1, seed=0,
            )
            res = trainer(
                env, n_episodes=200,
                reward_variant=variant, seed=0,
            )
            assert res["agent"] == name
            assert res["reward_variant"] == variant
            assert "accuracy" in res
            assert "pred_counts" in res
            env.close()
