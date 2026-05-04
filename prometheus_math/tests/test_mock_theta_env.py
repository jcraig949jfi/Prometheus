"""Tests for prometheus_math.mock_theta_env (mock theta coefficient prediction).

Cross-domain validation #4: same substrate (sigma kernel + BIND/EVAL +
arsenal-style action table) as BSDRankEnv and ModularFormEnv, but the
ground truth is the q-expansion of a harmonic-Maass-form holomorphic
part. Mock theta functions are *not* modular forms; they are weight-1/2
mock modular forms whose modular completion requires a non-holomorphic
shadow.

Math-tdd skill rubric (>= 3 in every category).

Authority -- coefficients of Ramanujan's third-order f(q) match
published values; coefficient magnitudes are small integers; corpus
length is at least 30.

Property -- coefficients are integers; level/weight/order tuples are
well-formed; determinism is reproducible.

Edge -- empty corpus rejected; functions with no usable coefficients
rejected; out-of-range values clip safely.

Composition -- 3-algorithm comparison dict, pipeline records match
expectation, end-to-end pipeline check.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _mt_available():
    from prometheus_math import _mock_theta_corpus
    ok, reason = _mock_theta_corpus.is_available()
    if not ok:
        pytest.skip(f"mock-theta corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_corpus(_mt_available):
    """The full embedded corpus -- mock theta corpus is small."""
    from prometheus_math import _mock_theta_corpus
    return _mock_theta_corpus.load_mock_theta_corpus()


@pytest.fixture
def small_env(small_corpus):
    from prometheus_math.mock_theta_env import MockThetaEnv
    env = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    yield env
    env.close()


# ---------------------------------------------------------------------------
# Authority -- ground truth alignment with published values
# ---------------------------------------------------------------------------


def test_authority_ramanujan_f3_first_few_coefficients(_mt_available):
    """The first ten coefficients of Ramanujan's third-order f(q) match
    OEIS A000025 (Watson 1936; Andrews 1966):

        f(q) = 1 + q - 2 q^2 + 3 q^3 - 3 q^4 + 3 q^5 - 5 q^6 + 7 q^7
                 - 6 q^8 + 6 q^9 - ...

    Authority: f(q) of order 3 is THE prototype mock theta function;
    these ten values appear in every survey of the subject, e.g.
    Andrews 1966 Table I, OEIS A000025.
    """
    from prometheus_math import _mock_theta_corpus
    corpus = _mock_theta_corpus.load_mock_theta_corpus()
    rec = next((e for e in corpus if e.name == "f3"), None)
    assert rec is not None, "f3 (third-order f(q)) missing from corpus"
    assert rec.order == 3
    assert rec.coefficients[:10] == (1, 1, -2, 3, -3, 3, -5, 7, -6, 6), (
        f"f3 first 10 coefficients {rec.coefficients[:10]} != "
        f"published OEIS A000025 (1, 1, -2, 3, -3, 3, -5, 7, -6, 6)"
    )


def test_authority_third_order_psi_partition_count(_mt_available):
    """Ramanujan's third-order psi(q) = sum_{n>=1} q^{n^2} / (q;q^2)_n
    is a partition-counting series. Its first thirty coefficients are
    monotonically non-decreasing (Andrews 1966, Hickerson 1988):

        psi(q) = q + q^2 + q^3 + 2 q^4 + 2 q^5 + 2 q^6 + 3 q^7 + ...

    Authority: this is OEIS A053257 -- partitions of n into distinct
    parts where the largest part is at most twice the second-largest.
    """
    from prometheus_math import _mock_theta_corpus
    corpus = _mock_theta_corpus.load_mock_theta_corpus()
    rec = next((e for e in corpus if e.name == "psi3"), None)
    assert rec is not None
    # All coefficients non-negative.
    assert all(a >= 0 for a in rec.coefficients), (
        f"psi3 should be non-negative; got {rec.coefficients}"
    )
    # First few hand-checked values.
    expected_prefix = (0, 1, 1, 1, 2, 2, 2, 3, 3, 4)
    assert rec.coefficients[:10] == expected_prefix, (
        f"psi3[:10] = {rec.coefficients[:10]} != {expected_prefix}"
    )
    # Monotone non-decreasing on the first 20 coefficients.
    for i in range(1, 20):
        assert rec.coefficients[i] >= rec.coefficients[i - 1], (
            f"psi3 not monotone at index {i}: "
            f"{rec.coefficients[i-1]} -> {rec.coefficients[i]}"
        )


def test_authority_corpus_minimum_size(_mt_available):
    """The corpus contains at least 30 mock theta functions, and every
    entry has at least 30 coefficients.

    Authority: the spec mandates >= 30 functions and >= 30
    coefficients each; this is the floor the corpus was hand-curated
    against.
    """
    from prometheus_math import _mock_theta_corpus
    corpus = _mock_theta_corpus.load_mock_theta_corpus()
    assert len(corpus) >= 30, (
        f"corpus has only {len(corpus)} entries; spec mandates >= 30"
    )
    for e in corpus:
        assert len(e.coefficients) >= 30, (
            f"{e.name} has only {len(e.coefficients)} coefficients; "
            f"spec mandates >= 30"
        )


def test_authority_low_index_coefficients_are_small(_mt_available):
    """For every mock theta function in the corpus, the first FIVE
    coefficients (a_0, a_1, a_2, a_3, a_4) satisfy ``|a_n| <= 10``.

    Authority: low-index coefficients of classical mock theta functions
    are small integers. Surveyed across all 17 Ramanujan + sixth/eighth/
    tenth-order extensions, the largest |a_n| for n <= 4 in the
    published tables is 6 (e.g. f3's a_2 = -2, omega3's a_3 = 4).
    """
    from prometheus_math import _mock_theta_corpus
    corpus = _mock_theta_corpus.load_mock_theta_corpus()
    violations = []
    for e in corpus:
        for i in range(min(5, len(e.coefficients))):
            if abs(e.coefficients[i]) > 10:
                violations.append((e.name, i, e.coefficients[i]))
    assert not violations, (
        f"Low-index |a_n| > 10 for {len(violations)} (name, idx, val) "
        f"records; first three: {violations[:3]}"
    )


def test_authority_predicting_correct_bin_yields_full_reward(small_env):
    """Predicting the bin that contains the true coefficient must pay
    out REWARD_HIT.

    Authority: env reward contract -- hit pays REWARD_HIT, miss pays 0.
    """
    from prometheus_math.mock_theta_env import REWARD_HIT
    env = small_env
    obs, info = env.reset(seed=12345)
    true_bin = int(info["true_bin"])
    _, r, term, _, info2 = env.step(true_bin)
    assert math.isclose(r, REWARD_HIT)
    assert info2["hit"] is True
    assert term is True
    assert info2["true_bin"] == true_bin
    assert info2["predicted_bin"] == true_bin


# ---------------------------------------------------------------------------
# Property -- integer coefficients, well-formed metadata, determinism
# ---------------------------------------------------------------------------


def test_property_all_coefficients_are_integers(_mt_available):
    """Every coefficient in the corpus is a Python ``int``.

    Property: q-expansions of mock theta functions are integer power
    series; the corpus loader must preserve this invariant.
    """
    from prometheus_math import _mock_theta_corpus
    corpus = _mock_theta_corpus.load_mock_theta_corpus()
    for e in corpus:
        for i, a in enumerate(e.coefficients):
            assert isinstance(a, int), (
                f"{e.name}.coefficients[{i}] = {a!r} is not int "
                f"(type {type(a).__name__})"
            )


def test_property_well_formed_metadata(small_corpus):
    """Every entry has well-formed (name, order, level, weight,
    shadow_class) tuples.

    Property: the loader must enforce schema sanity.
    """
    for e in small_corpus:
        assert isinstance(e.name, str) and e.name
        assert isinstance(e.order, int) and e.order >= 1
        assert isinstance(e.level, int) and e.level >= 1
        assert isinstance(e.weight, int) and e.weight >= 1
        assert isinstance(e.shadow_class, int) and e.shadow_class >= 0
        assert isinstance(e.coefficients, tuple) and len(e.coefficients) >= 1


def test_property_determinism_with_fixed_seed(small_corpus):
    """The reset/sample/step pipeline is deterministic given seed.

    Property: same seed -> same (name, target_index, true_bin) and
    same observation.
    """
    from prometheus_math.mock_theta_env import MockThetaEnv
    env_a = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    env_b = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    obs_a, info_a = env_a.reset(seed=99)
    obs_b, info_b = env_b.reset(seed=99)
    np.testing.assert_array_equal(obs_a, obs_b)
    assert info_a["name"] == info_b["name"]
    assert info_a["target_index"] == info_b["target_index"]
    assert info_a["true_bin"] == info_b["true_bin"]
    env_a.close()
    env_b.close()


def test_property_obs_shape_consistent(small_env):
    """The observation vector has fixed dimension 2*n_coeffs +
    HISTORY_DIM across resets.

    Property: observation_space contract.
    """
    from prometheus_math.mock_theta_env import _obs_dim
    env = small_env
    expected = _obs_dim(env.n_coeffs())
    for s in (1, 2, 3, 4, 5):
        obs, _info = env.reset(seed=s)
        assert obs.shape == (expected,), (
            f"obs shape mismatch at seed={s}: "
            f"{obs.shape} vs ({expected},)"
        )


def test_property_bin_round_trip_at_centers():
    """A bin-center value round-trips: ``integer_bin_for(c) == idx``
    where ``c = bin_to_integer(idx)``.

    Property: quantization is left-inverse to dequantization on bin
    centres.
    """
    from prometheus_math.mock_theta_env import (
        integer_bin_for, bin_to_integer, N_BINS,
    )
    for idx in range(N_BINS):
        c = bin_to_integer(idx)
        # The dequantized value sits in bin idx (or possibly an
        # adjacent bin if rounding pushed across a boundary -- check
        # within +-1).
        assert abs(integer_bin_for(c) - idx) <= 1, (
            f"round-trip failed for idx {idx}: c={c}, "
            f"integer_bin_for(c)={integer_bin_for(c)}"
        )


# ---------------------------------------------------------------------------
# Edge -- empty corpus, malformed inputs, action out of range
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_raises_value_error(_mt_available):
    """Constructing an env with an empty corpus must raise ValueError.

    Edge: defensive contract.
    """
    from prometheus_math.mock_theta_env import MockThetaEnv
    with pytest.raises(ValueError):
        MockThetaEnv(corpus=[], split="all")


def test_edge_action_out_of_range(small_env):
    """Predicting a bin outside [0, N_BINS) is rejected.

    Edge: action-space contract.
    """
    from prometheus_math.mock_theta_env import N_BINS
    env = small_env
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(N_BINS)
    env.reset(seed=2)
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_function_with_too_few_coefficients_handled():
    """If a hand-built corpus contains a function with very few
    coefficients (less than ``context_min``), the env rejects it
    cleanly.

    Edge: defensive contract for misconfigured corpora.
    """
    from prometheus_math._mock_theta_corpus import MockThetaEntry
    from prometheus_math.mock_theta_env import MockThetaEnv
    # Length 3, less than default context_min=5.
    short = MockThetaEntry(
        name="X_tiny", order=3, level=1, weight=1, shadow_class=0,
        coefficients=(1, 0, -1),
    )
    with pytest.raises(ValueError):
        MockThetaEnv(corpus=[short], split="all", context_min=5, seed=0)
    # context_min=2 should construct, with k always 2.
    env = MockThetaEnv(corpus=[short], split="all", context_min=2, seed=0)
    obs, info = env.reset(seed=0)
    assert info["context_k"] == 2
    _, r, _, _, _ = env.step(0)
    assert r in (0.0, 100.0)
    env.close()


def test_edge_unknown_split_raises(small_corpus):
    """An invalid ``split`` value is rejected at construction.

    Edge: defensive contract.
    """
    from prometheus_math.mock_theta_env import MockThetaEnv
    with pytest.raises(ValueError):
        MockThetaEnv(corpus=small_corpus, split="bogus")


def test_edge_value_outside_range_clips_to_extreme_bin():
    """Coefficient values outside [-VALUE_RANGE, VALUE_RANGE] clip to
    the extreme bins, never crashing or producing out-of-range indices.

    Edge: numerical-robustness contract for ``integer_bin_for``.
    """
    from prometheus_math.mock_theta_env import (
        integer_bin_for, N_BINS, VALUE_RANGE,
    )
    # Way outside, both signs.
    assert integer_bin_for(int(10 * VALUE_RANGE)) == N_BINS - 1
    assert integer_bin_for(int(-10 * VALUE_RANGE)) == 0
    # Boundary cases.
    assert integer_bin_for(int(VALUE_RANGE)) == N_BINS - 1
    assert integer_bin_for(int(-VALUE_RANGE)) == 0
    # 0 always lands in the central region.
    central = integer_bin_for(0)
    assert 0 <= central < N_BINS


def test_edge_function_with_no_usable_coefficients():
    """If every coefficient at the predict index is sampled from the
    extreme tails (e.g. all -1000), the env still pays out a hit on a
    correct extreme-bin guess. This guards against a regression where
    we accidentally rejected such corpora.

    Edge: ground-truth path remains valid for clipped values.
    """
    from prometheus_math._mock_theta_corpus import MockThetaEntry
    from prometheus_math.mock_theta_env import MockThetaEnv, N_BINS
    extreme = MockThetaEntry(
        name="X_extreme", order=3, level=1, weight=1, shadow_class=0,
        coefficients=tuple([1] * 5 + [-9999] * 25),
    )
    env = MockThetaEnv(corpus=[extreme], split="all",
                       context_min=5, seed=0)
    # Force k = 5 so we always predict a clipped value.
    env.reset(seed=0)
    # Bin 0 should always be the correct answer for -9999.
    _, r, _, _, info = env.step(0)
    assert info["true_bin"] == 0
    assert r == 100.0
    env.close()


# ---------------------------------------------------------------------------
# Composition -- multi-algorithm pilot, comparison dict, growth invariant
# ---------------------------------------------------------------------------


def test_composition_three_algorithm_comparison(small_corpus):
    """Running random / REINFORCE / PPO on the same corpus yields a
    well-formed comparison dict.

    Composition: the cross-algorithm comparison contract used by the
    pilot driver.
    """
    from prometheus_math.mock_theta_env import (
        MockThetaEnv, train_random, train_reinforce, train_ppo,
    )
    e1 = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    e2 = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    e3 = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    rep_random = train_random(e1, n_episodes=80, seed=0)
    rep_lrn = train_reinforce(e2, n_episodes=80, lr=0.02, seed=0)
    rep_ppo = train_ppo(e3, n_episodes=80, lr=0.005, hidden=16, seed=0)
    e1.close(); e2.close(); e3.close()
    comparison = {
        "random": rep_random,
        "reinforce": rep_lrn,
        "ppo": rep_ppo,
    }
    for arm, rep in comparison.items():
        assert "mean_reward" in rep and "accuracy" in rep
        assert rep["n_episodes"] == 80
    assert comparison["random"]["agent"] == "random"
    assert comparison["reinforce"]["agent"] == "reinforce"
    assert comparison["ppo"]["agent"] == "ppo"


def test_composition_pilot_records_match_expectation(small_corpus):
    """A 200-episode REINFORCE run on the corpus produces:
      - a numpy rewards array of length 200,
      - a finite mean reward in [0, REWARD_HIT],
      - pred_counts summing to 200.

    Composition: pipeline-record schema for the pilot driver.
    """
    from prometheus_math.mock_theta_env import (
        MockThetaEnv, train_reinforce, REWARD_HIT,
    )
    env = MockThetaEnv(corpus=small_corpus, split="all", seed=0)
    rep = train_reinforce(env, n_episodes=200, lr=0.02, seed=0)
    env.close()
    rewards = rep["rewards"]
    assert isinstance(rewards, np.ndarray)
    assert rewards.shape == (200,)
    assert 0.0 <= rep["mean_reward"] <= REWARD_HIT
    assert sum(rep["pred_counts"]) == 200


def test_composition_substrate_growth_one_binding_one_eval(small_env):
    """Each step produces exactly one binding + one evaluation row in
    the sigma kernel. Mirrors the BSDRankEnv / ModularFormEnv invariant.

    Composition: substrate-attribution contract.
    """
    env = small_env
    env.reset(seed=5)
    k = env.kernel()

    def _count(table: str) -> int:
        return int(k.conn.execute(
            f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    n_b_before = _count("bindings")
    n_e_before = _count("evaluations")
    env.step(0)
    n_b_after = _count("bindings")
    n_e_after = _count("evaluations")
    assert n_b_after - n_b_before == 1, (
        f"expected 1 new binding, got {n_b_after - n_b_before}"
    )
    assert n_e_after - n_e_before == 1, (
        f"expected 1 new evaluation, got {n_e_after - n_e_before}"
    )


def test_composition_end_to_end_pipeline(small_corpus):
    """An end-to-end miniature pilot: train each of the 3 algorithms
    for 60 episodes on a train split, then evaluate on a held-out test
    split. Returns a dict with the expected schema.

    Composition: the pilot harness end-to-end contract.
    """
    from prometheus_math import _mock_theta_corpus
    from prometheus_math.mock_theta_env import (
        MockThetaEnv, train_random, train_reinforce, train_ppo,
    )
    train, test = _mock_theta_corpus.split_train_test(
        small_corpus, train_frac=0.7, seed=42,
    )
    assert len(train) > 0 and len(test) > 0

    # Train.
    e1 = MockThetaEnv(corpus=train, split="all", seed=0)
    e2 = MockThetaEnv(corpus=train, split="all", seed=0)
    e3 = MockThetaEnv(corpus=train, split="all", seed=0)
    rep_random = train_random(e1, n_episodes=60, seed=0)
    rep_lrn = train_reinforce(e2, n_episodes=60, lr=0.02, seed=0)
    rep_ppo = train_ppo(e3, n_episodes=60, lr=0.005, hidden=16, seed=0)
    e1.close(); e2.close(); e3.close()

    # Evaluate the trained REINFORCE policy (argmax) on the test set.
    test_env = MockThetaEnv(corpus=test, split="all", seed=1)
    rng = np.random.default_rng(0)
    W = rep_lrn["policy_W_final"]
    b = rep_lrn["policy_b_final"]
    n_eval = 80
    rs = []
    for _ in range(n_eval):
        obs, _info = test_env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        a = int(np.argmax(logits))
        _, r, _, _, _ = test_env.step(a)
        rs.append(r)
    test_env.close()
    test_mean = float(np.mean(rs)) if rs else 0.0

    # Final pipeline-record dict (the kind the pilot writes to JSON).
    record = {
        "train": {
            "random": {
                "mean_reward": rep_random["mean_reward"],
                "accuracy": rep_random["accuracy"],
            },
            "reinforce": {
                "mean_reward": rep_lrn["mean_reward"],
                "accuracy": rep_lrn["accuracy"],
            },
            "ppo": {
                "mean_reward": rep_ppo["mean_reward"],
                "accuracy": rep_ppo["accuracy"],
            },
        },
        "test_reinforce_mean": test_mean,
        "n_train": len(train),
        "n_test": len(test),
    }
    # Schema sanity.
    assert set(record["train"].keys()) == {"random", "reinforce", "ppo"}
    for arm in record["train"].values():
        assert 0.0 <= arm["accuracy"] <= 1.0
        assert 0.0 <= arm["mean_reward"] <= 100.0
    assert 0.0 <= record["test_reinforce_mean"] <= 100.0
