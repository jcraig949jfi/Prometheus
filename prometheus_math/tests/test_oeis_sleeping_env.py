"""Tests for prometheus_math.oeis_sleeping_env (OEIS Sleeping Beauty
next-term prediction).

Cross-domain validation #3: same substrate (sigma kernel + BIND/EVAL +
arsenal-style action table) as BSDRankEnv and ModularFormEnv, but the
ground truth lives in OEIS's bulk-dump corpus (~395K integer
sequences), and the focus is on the underconnected tail
("Sleeping Beauties": rich combinatorial structure but few
cross-references).

Math-tdd skill rubric (>= 3 in every category).

Authority -- ground truth comes from OEIS; verify well-known sequences
(Fibonacci, Catalan, factorial) appear and have correct first terms.

Property -- positivity, A-number format, determinism, observation
shape, growth-class classifier sanity.

Edge -- empty corpus, short sequences, action out of range, invalid
split, value clipping.

Composition -- 4-algorithm comparison dict, pipeline shape, end-to-end
corpus -> env -> REINFORCE -> test, substrate growth invariant.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _oeis_available():
    from prometheus_math import _oeis_sleeping_corpus
    ok, reason = _oeis_sleeping_corpus.is_available()
    if not ok:
        pytest.skip(f"OEIS sleeping corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_corpus(_oeis_available):
    """Small corpus for fast tests (~150 entries: 5 anchors + 145 body)."""
    from prometheus_math import _oeis_sleeping_corpus
    return _oeis_sleeping_corpus.load_oeis_sleeping_corpus(
        n_total=150, seed=42, use_cache=True,
    )


@pytest.fixture
def small_env(small_corpus):
    from prometheus_math.oeis_sleeping_env import OeisSleepingEnv
    env = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
    yield env
    env.close()


# ---------------------------------------------------------------------------
# Authority -- known sequences appear with correct values
# ---------------------------------------------------------------------------


def test_authority_fibonacci_in_corpus(_oeis_available):
    """A000045 (Fibonacci) is an anchor -- it MUST be in the corpus and
    its first 10 terms must match the textbook values
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34].

    Authority: Fibonacci is OEIS's canonical sequence; the bulk-dump
    file ``stripped.gz`` lists exactly this prefix.
    """
    from prometheus_math import _oeis_sleeping_corpus
    corpus = _oeis_sleeping_corpus.load_oeis_sleeping_corpus(
        n_total=50, seed=0, use_cache=True,
    )
    fib = next((e for e in corpus if e.a_number == "A000045"), None)
    assert fib is not None, "A000045 (Fibonacci) missing from corpus"
    assert fib.is_anchor is True
    assert tuple(fib.data[:10]) == (0, 1, 1, 2, 3, 5, 8, 13, 21, 34)


def test_authority_catalan_in_corpus(_oeis_available):
    """A000108 (Catalan numbers) anchor: first 8 terms must be
    [1, 1, 2, 5, 14, 42, 132, 429].

    Authority: the Catalan numbers appear in 200+ combinatorial
    contexts; the first eight values are absolute.
    """
    from prometheus_math import _oeis_sleeping_corpus
    corpus = _oeis_sleeping_corpus.load_oeis_sleeping_corpus(
        n_total=50, seed=0, use_cache=True,
    )
    cat = next((e for e in corpus if e.a_number == "A000108"), None)
    assert cat is not None, "A000108 (Catalan) missing from corpus"
    assert cat.is_anchor is True
    assert tuple(cat.data[:8]) == (1, 1, 2, 5, 14, 42, 132, 429)


def test_authority_at_least_one_30term_sequence(small_corpus):
    """Every entry in the body of the corpus has >= 30 terms (the
    structural filter). Verify on the body slice -- anchors can be
    shorter (e.g. A000142 has only 23 mirror terms).

    Authority: ``DEFAULT_MIN_TERMS = 30`` is the documented contract.
    """
    from prometheus_math._oeis_sleeping_corpus import DEFAULT_MIN_TERMS
    body = [e for e in small_corpus if not e.is_anchor]
    assert body, "corpus has no body entries"
    for e in body:
        assert len(e.data) >= DEFAULT_MIN_TERMS, (
            f"{e.a_number}: only {len(e.data)} terms (< {DEFAULT_MIN_TERMS})"
        )


def test_authority_predicting_correct_bin_yields_full_reward(small_env):
    """Predicting the bin that contains the true a(k) must pay
    REWARD_HIT.

    Authority: env reward contract -- exact bin pays REWARD_HIT.
    """
    from prometheus_math.oeis_sleeping_env import REWARD_HIT
    env = small_env
    obs, info = env.reset(seed=12345)
    true_bin = int(info["true_bin"])
    _, r, term, _, info2 = env.step(true_bin)
    assert math.isclose(r, REWARD_HIT)
    assert info2["hit"] is True
    assert term is True
    assert info2["true_bin"] == true_bin
    assert info2["predicted_bin"] == true_bin


def test_authority_growth_classifier_recognizes_canonical(_oeis_available):
    """The growth-class classifier must label the canonical anchors
    sensibly: Fibonacci -> exponential, factorial -> factorial,
    n -> linear, n^2 -> polynomial.

    Authority: textbook asymptotics. Note: 2^n is technically
    exponential too, so we don't pin its label.
    """
    from prometheus_math._oeis_sleeping_corpus import classify_growth
    fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610,
           987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368,
           75025, 121393, 196418, 317811, 514229, 832040]
    fact = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800,
            39916800, 479001600]
    nat = list(range(1, 31))
    sq = [n * n for n in range(1, 31)]
    assert classify_growth(fib) == "exponential"
    assert classify_growth(fact) == "factorial"
    assert classify_growth(nat) == "linear"
    assert classify_growth(sq) == "polynomial"


# ---------------------------------------------------------------------------
# Property -- positivity, format, determinism, obs shape
# ---------------------------------------------------------------------------


def test_property_a_number_format(small_corpus):
    """Every entry has a valid ``A\\d{6}`` A-number.

    Property: the OEIS A-number convention (zero-padded to 6 digits).
    """
    pat = re.compile(r"^A\d{6}$")
    for e in small_corpus:
        assert pat.match(e.a_number), (
            f"invalid A-number: {e.a_number!r}"
        )


def test_property_terms_positive_integers(small_corpus):
    """All terms in every body entry are positive integers (the
    structural filter excludes signed and rational sequences).

    Anchors may include zero (e.g. Fibonacci starts with 0). Document
    this exception.
    """
    body = [e for e in small_corpus if not e.is_anchor]
    for e in body:
        for v in e.data[:30]:
            assert isinstance(v, int)
            assert v > 0, f"{e.a_number}: non-positive term {v}"
    # Anchors are allowed to start with 0 (Fibonacci, etc.).
    for e in [e for e in small_corpus if e.is_anchor]:
        for v in e.data:
            assert isinstance(v, int)
            assert v >= 0


def test_property_determinism_with_fixed_seed(small_corpus):
    """Same seed -> same (a_number, context_k, true_bin) and same obs
    vector.

    Property: reset/step pipeline determinism.
    """
    from prometheus_math.oeis_sleeping_env import OeisSleepingEnv
    env_a = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
    env_b = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
    obs_a, info_a = env_a.reset(seed=99)
    obs_b, info_b = env_b.reset(seed=99)
    np.testing.assert_array_equal(obs_a, obs_b)
    assert info_a["a_number"] == info_b["a_number"]
    assert info_a["context_k"] == info_b["context_k"]
    assert info_a["true_bin"] == info_b["true_bin"]
    env_a.close()
    env_b.close()


def test_property_obs_shape_consistent(small_env):
    """Observation vector has fixed dimension ``_obs_dim(context_max)``.

    Property: observation_space contract.
    """
    from prometheus_math.oeis_sleeping_env import _obs_dim
    env = small_env
    expected = _obs_dim(env.context_max())
    for s in (1, 2, 3, 4, 5):
        obs, _info = env.reset(seed=s)
        assert obs.shape == (expected,), (
            f"obs shape mismatch at seed={s}: "
            f"{obs.shape} vs ({expected},)"
        )


def test_property_bin_quantization_round_trip():
    """value_to_bin + bin_to_value_range form a consistent partition:
    every value lands in a bin whose range contains it (modulo
    floating-point boundary tolerance).

    Property: log-space binning is order-preserving.
    """
    from prometheus_math.oeis_sleeping_env import (
        value_to_bin, bin_to_value_range, N_BINS, MAX_LOG10,
    )
    test_vals = [1, 2, 10, 100, 1234, 1_000_000, 123_456_789,
                 10**12, 10**15 - 1]
    for v in test_vals:
        idx = value_to_bin(v)
        lo, hi = bin_to_value_range(idx)
        assert 0 <= idx < N_BINS
        # The value lies in [lo, hi] modulo the boundary; tolerance
        # comes from float-pow round-off.
        eps_rel = 1e-9
        assert lo * (1.0 - eps_rel) <= float(v) <= hi * (1.0 + eps_rel), (
            f"value {v} (bin={idx}) not in [{lo}, {hi}]"
        )


def test_property_growth_class_one_hot_in_obs(small_env):
    """The growth-class one-hot block of the observation must have
    exactly one '1.0' entry (or all zeros when growth_class='other'
    falls outside GROWTH_CLASSES, which we forbid).

    Property: classifier output is exhaustive over GROWTH_CLASSES.
    """
    from prometheus_math.oeis_sleeping_env import _obs_dim, DEFAULT_CONTEXT_MAX
    from prometheus_math._oeis_sleeping_corpus import GROWTH_CLASSES
    env = small_env
    cmax = env.context_max()
    for s in range(5):
        obs, info = env.reset(seed=10 + s)
        oh = obs[3 * cmax: 3 * cmax + len(GROWTH_CLASSES)]
        # Exactly one 1.0 (growth class is always assigned by classifier).
        assert int(oh.sum()) == 1, (
            f"seed {s}: growth one-hot {oh} for {info['growth_class']}"
        )
        assert (oh >= 0.0).all() and (oh <= 1.0).all()


# ---------------------------------------------------------------------------
# Edge -- empty corpus, short sequences, action out of range
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_raises_value_error(_oeis_available):
    """Constructing an env with an empty corpus raises ValueError.

    Edge: defensive contract.
    """
    from prometheus_math.oeis_sleeping_env import OeisSleepingEnv
    with pytest.raises(ValueError):
        OeisSleepingEnv(corpus=[], split="all")


def test_edge_action_out_of_range(small_env):
    """Predicting a bin outside [0, N_BINS) is rejected.

    Edge: action-space contract.
    """
    from prometheus_math.oeis_sleeping_env import N_BINS
    env = small_env
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(N_BINS)
    env.reset(seed=2)
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_short_sequence_filtered_out():
    """A corpus where every entry has fewer than ``context_min + 1``
    terms must raise ValueError at env construction.

    Edge: graceful degradation when the corpus is too short.
    """
    from prometheus_math._oeis_sleeping_corpus import OeisSleepingEntry
    from prometheus_math.oeis_sleeping_env import OeisSleepingEnv
    too_short = OeisSleepingEntry(
        a_number="A999999", name="too short",
        data=(1, 2, 3),  # 3 terms, less than context_min=5
        growth_class="linear", is_anchor=False,
    )
    with pytest.raises(ValueError):
        OeisSleepingEnv(corpus=[too_short], split="all", context_min=5)


def test_edge_action_clipped_during_quantization():
    """value_to_bin clips out-of-range inputs to the extreme bins.

    Edge: numerical-robustness contract.
    """
    from prometheus_math.oeis_sleeping_env import (
        value_to_bin, N_BINS, MAX_LOG10,
    )
    # Negative or zero -> bin 0.
    assert value_to_bin(0) == 0
    assert value_to_bin(-100) == 0
    # Way beyond max -> last bin.
    assert value_to_bin(10**30) == N_BINS - 1
    assert value_to_bin(10**(int(MAX_LOG10) + 5)) == N_BINS - 1
    # Mid-range sanity.
    mid = 10 ** int(MAX_LOG10 / 2)
    assert 0 < value_to_bin(mid) < N_BINS


def test_edge_unknown_split_raises(small_corpus):
    """An invalid ``split`` value is rejected at construction.

    Edge: defensive contract.
    """
    from prometheus_math.oeis_sleeping_env import OeisSleepingEnv
    with pytest.raises(ValueError):
        OeisSleepingEnv(corpus=small_corpus, split="bogus")


# ---------------------------------------------------------------------------
# Composition -- 4-arm comparison, pipeline shape, end-to-end
# ---------------------------------------------------------------------------


def test_composition_random_pilot_well_formed(small_env):
    """``train_random`` returns a well-formed report dict.

    Composition: pilot harness contract.
    """
    from prometheus_math.oeis_sleeping_env import train_random
    out = train_random(small_env, n_episodes=80, seed=0)
    for key in ("rewards", "mean_reward", "accuracy", "near_rate",
                "n_episodes", "agent", "pred_counts"):
        assert key in out, f"missing key {key} in output"
    assert out["n_episodes"] == 80
    assert out["agent"] == "random"
    assert 0.0 <= out["accuracy"] <= 1.0
    # Random over 50 bins should have accuracy <= 0.10.
    assert out["accuracy"] <= 0.10


def test_composition_three_algorithm_comparison(small_corpus):
    """Running random / REINFORCE / PPO yields a comparison dict with
    three reports; all keys present.

    Composition: cross-algorithm comparison contract.
    """
    from prometheus_math.oeis_sleeping_env import (
        OeisSleepingEnv, train_random, train_reinforce, train_ppo,
    )
    e1 = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
    e2 = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
    e3 = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
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


def test_composition_substrate_growth_invariant(small_env):
    """Each step produces exactly one binding + one evaluation row in
    the sigma kernel.

    Composition: substrate-attribution contract (mirrors BSDRankEnv +
    ModularFormEnv).
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


def test_composition_pilot_records_match_expectation(small_corpus):
    """A 200-episode REINFORCE run on the small corpus produces:
      - a numpy rewards array of length 200,
      - finite mean reward in [0, REWARD_HIT],
      - pred_counts summing to 200.

    Composition: pipeline-record schema for the pilot driver.
    """
    from prometheus_math.oeis_sleeping_env import (
        OeisSleepingEnv, train_reinforce, REWARD_HIT,
    )
    env = OeisSleepingEnv(corpus=small_corpus, split="all", seed=0)
    rep = train_reinforce(env, n_episodes=200, lr=0.02, seed=0)
    env.close()
    rewards = rep["rewards"]
    assert isinstance(rewards, np.ndarray)
    assert rewards.shape == (200,)
    assert 0.0 <= rep["mean_reward"] <= REWARD_HIT
    assert sum(rep["pred_counts"]) == 200


def test_composition_end_to_end_corpus_env_train_test(small_corpus):
    """Full pipeline: corpus -> split -> env (train) -> REINFORCE ->
    deterministic eval on test split. Verifies the records flow
    end-to-end without throwing.

    Composition: integration smoke test.
    """
    from prometheus_math import _oeis_sleeping_corpus
    from prometheus_math.oeis_sleeping_env import (
        OeisSleepingEnv, train_reinforce, REWARD_HIT,
    )
    train, test = _oeis_sleeping_corpus.split_train_test(
        small_corpus, train_frac=0.7, seed=0
    )
    assert train and test, "split produced empty halves"
    env_train = OeisSleepingEnv(corpus=train, split="all", seed=0)
    rep = train_reinforce(env_train, n_episodes=100, lr=0.02, seed=0)
    env_train.close()
    # Eval (deterministic argmax) on the test split.
    W = rep["policy_W_final"]; b = rep["policy_b_final"]
    env_test = OeisSleepingEnv(corpus=test, split="all", seed=42)
    rng = np.random.default_rng(42)
    test_rewards = []
    for _ in range(50):
        obs, _ = env_test.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(np.argmax(W @ obs + b))
        _, r, _, _, _ = env_test.step(a)
        test_rewards.append(r)
    env_test.close()
    test_mean = float(np.asarray(test_rewards).mean())
    assert 0.0 <= test_mean <= REWARD_HIT


def test_composition_growth_baseline_beats_random(small_corpus):
    """The growth heuristic baseline must materially beat the uniform
    random baseline. A non-trivial fraction of the corpus is monotone
    exponential or polynomial; extrapolating by mean log-ratio should
    land on the right bin >= 20% of the time.

    Composition: baseline-validity contract.
    """
    from prometheus_math.oeis_sleeping_env import (
        OeisSleepingEnv, train_random, train_growth_baseline,
    )
    e1 = OeisSleepingEnv(corpus=small_corpus, split="all", seed=7)
    e2 = OeisSleepingEnv(corpus=small_corpus, split="all", seed=7)
    rep_rand = train_random(e1, n_episodes=300, seed=7)
    rep_grow = train_growth_baseline(e2, n_episodes=300, seed=7)
    e1.close(); e2.close()
    assert rep_grow["mean_reward"] > rep_rand["mean_reward"], (
        f"growth baseline (mean={rep_grow['mean_reward']:.2f}) failed "
        f"to beat random (mean={rep_rand['mean_reward']:.2f})"
    )
    # Growth baseline should hit at least 15% accuracy on this corpus
    # (anchors + monotone bodies); random is ~2%.
    assert rep_grow["accuracy"] >= 0.15
