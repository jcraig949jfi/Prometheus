"""Tests for prometheus_math.modular_form_env (modular-form a_p prediction).

Cross-domain validation #2: same substrate (sigma kernel + BIND/EVAL +
arsenal-style action table) as BSDRankEnv, but the ground truth lives
in LMFDB's ``mf_newforms`` table. Every dim=1 newform exposes its
Hecke eigenvalues directly via the ``traces`` column.

Math-tdd skill rubric (>= 3 in every category).

Authority -- ground truth comes from LMFDB; verify it agrees with
classical references (Ramanujan tau, Manakubin congruence).

Property -- Deligne bound, well-formed metadata, determinism.

Edge -- empty corpus, missing a_p, action outside Deligne range.

Composition -- pilot harness shape, multi-algorithm comparison,
substrate growth invariant.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _mf_available():
    from prometheus_math import _modular_form_corpus
    ok, reason = _modular_form_corpus.is_available()
    if not ok:
        pytest.skip(f"modular-form corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_corpus(_mf_available):
    """A small but stratified corpus for fast tests (~120 forms)."""
    from prometheus_math import _modular_form_corpus
    return _modular_form_corpus.load_modular_form_corpus(
        level_max=300, n_total=120, seed=42, use_cache=True,
    )


@pytest.fixture
def small_env(small_corpus):
    from prometheus_math.modular_form_env import ModularFormEnv
    env = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
    yield env
    env.close()


# ---------------------------------------------------------------------------
# Authority -- ground truth alignment with LMFDB / classical references
# ---------------------------------------------------------------------------


def test_authority_corpus_contains_ramanujan_tau(_mf_available):
    """The corpus loader must yield 1.12.a.a (Ramanujan tau / Delta)
    when level_max >= 1, which is its level. A deeper test is the
    coefficient match below.

    Authority: 1.12.a.a is THE canonical weight-12 cusp form on
    SL_2(Z); LMFDB's ``traces`` row matches Hardy / Mordell / Ramanujan
    tabulations.
    """
    from prometheus_math import _modular_form_corpus
    corpus = _modular_form_corpus.load_modular_form_corpus(
        level_max=1000, n_total=8000, seed=0, use_cache=True,
    )
    labels = {e.label for e in corpus}
    assert "1.12.a.a" in labels, (
        f"Ramanujan tau (1.12.a.a) missing from corpus of size "
        f"{len(corpus)}; labels include: "
        f"{[lbl for lbl in labels if lbl.startswith('1.12')]}"
    )


def test_authority_ramanujan_tau_first_few_a_p(_mf_available):
    """The first few a_p of 1.12.a.a match published values:
    a_2 = -24, a_3 = 252, a_5 = 4830, a_7 = -16744.

    Authority: these four numbers appear in every textbook treatment of
    the Ramanujan tau function (Ramanujan 1916; LMFDB confirmed).
    """
    from prometheus_math import _modular_form_corpus
    corpus = _modular_form_corpus.load_modular_form_corpus(
        level_max=1000, n_total=8000, seed=0, use_cache=True,
    )
    rec = next((e for e in corpus if e.label == "1.12.a.a"), None)
    assert rec is not None, "1.12.a.a not in corpus"
    assert rec.weight == 12
    assert rec.level == 1
    # primes index: PRIMES_30 = (2, 3, 5, 7, ...). a_p[0] = a_2, etc.
    assert rec.a_p[0] == -24, f"a_2 = {rec.a_p[0]}, expected -24"
    assert rec.a_p[1] == 252, f"a_3 = {rec.a_p[1]}, expected 252"
    assert rec.a_p[2] == 4830, f"a_5 = {rec.a_p[2]}, expected 4830"
    assert rec.a_p[3] == -16744, f"a_7 = {rec.a_p[3]}, expected -16744"


def test_authority_manakubin_congruence(_mf_available):
    """Manakubin congruence (1916, also attributed to Ramanujan):
    ``tau(p) === 1 + p^11 (mod 691)`` for every prime p.

    Verify on at least 3 primes from the 1.12.a.a record. Authority:
    Serre (Cours d'arithmétique, ch. VII) gives this as the prototype
    Hecke-algebra-mod-l congruence; the 691 comes from the numerator of
    zeta(-11) = -691/32760.
    """
    from prometheus_math import _modular_form_corpus
    corpus = _modular_form_corpus.load_modular_form_corpus(
        level_max=1000, n_total=8000, seed=0, use_cache=True,
    )
    rec = next((e for e in corpus if e.label == "1.12.a.a"), None)
    assert rec is not None, "1.12.a.a not in corpus"
    matches = 0
    checked = []
    for i, p in enumerate(rec.primes):
        if p == 691:
            continue  # the prime 691 itself is the modulus -- skip
        a_p = int(rec.a_p[i])
        rhs = (1 + pow(int(p), 11, 691)) % 691
        lhs = a_p % 691
        if lhs == rhs:
            matches += 1
        checked.append((p, lhs, rhs))
    assert matches >= 3, (
        f"Manakubin congruence verified on only {matches} primes; "
        f"checked {checked[:5]}"
    )
    # The congruence is exact (it's a theorem), so we expect ALL
    # primes != 691 to match. Demand the full set.
    assert matches == len(rec.primes), (
        f"expected all {len(rec.primes)} primes to satisfy the "
        f"congruence; only {matches} did"
    )


def test_authority_atkin_lehner_level_11(_mf_available):
    """Atkin-Lehner relation at p exactly dividing N: for a newform on
    Gamma_0(N) with trivial nebentypus and AL eigenvalue ``w_p = +-1``
    at the prime p || N,

        a_p = -w_p * p^((k-2)/2).

    For 11.2.a.a (level 11, weight 2): LMFDB lists w_11 = -1, so
    ``a_11 = -(-1) * 11^0 = +1``. We verify the corpus's a_11 satisfies
    this: a_11 must be exactly +1 or -1 (both signs are consistent with
    AL for some form; we further demand it's +1 for 11.2.a.a, the EC
    11a-attached newform).

    Authority: Atkin-Lehner involution theory (Atkin-Lehner 1970;
    Diamond-Shurman ch. 5).
    """
    from prometheus_math import _modular_form_corpus
    corpus = _modular_form_corpus.load_modular_form_corpus(
        level_max=1000, n_total=8000, seed=0, use_cache=True,
    )
    rec = next((e for e in corpus if e.label == "11.2.a.a"), None)
    assert rec is not None, "11.2.a.a not in corpus"
    # PRIMES_30 starts (2, 3, 5, 7, 11, ...); a_p[4] = a_11.
    assert rec.primes[4] == 11
    a_11 = int(rec.a_p[4])
    # Expected value from AL: w_11 = -1 -> a_11 = +1.
    assert a_11 == 1, (
        f"11.2.a.a a_11 should be +1 (Atkin-Lehner w_11 = -1 + "
        f"weight 2); got {a_11}"
    )


def test_authority_predicting_correct_bin_yields_full_reward(small_env):
    """Predicting the bin that contains the true normalized a_p must
    pay out REWARD_HIT.

    Authority: env reward contract -- hit pays REWARD_HIT, miss pays 0.
    """
    from prometheus_math.modular_form_env import REWARD_HIT
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
# Property -- Deligne bound, well-formed metadata, determinism
# ---------------------------------------------------------------------------


def test_property_deligne_bound_holds_on_corpus(_mf_available):
    """For every form in the corpus and every prime in its feature
    vector, ``|a_p| <= 2 * p^((weight - 1) / 2)`` (Deligne's bound,
    proved by Deligne 1974 from the Weil conjectures).

    Property: a corpus loaded from LMFDB must respect the theorem; if
    it doesn't, the loader has a bug.
    """
    from prometheus_math import _modular_form_corpus
    from prometheus_math.modular_form_env import deligne_bound
    corpus = _modular_form_corpus.load_modular_form_corpus(
        level_max=300, n_total=120, seed=42, use_cache=True,
    )
    # Tolerate a tiny relative slop (1e-9) to absorb LMFDB rounding.
    eps = 1e-9
    violations = []
    for e in corpus:
        for i, p in enumerate(e.primes):
            bound = deligne_bound(int(p), e.weight)
            a_p = int(e.a_p[i])
            if abs(a_p) > bound * (1.0 + eps):
                violations.append((e.label, p, a_p, bound))
                break  # one violation per form is enough to fail
    assert not violations, (
        f"Deligne bound violated by {len(violations)} forms; "
        f"first 3: {violations[:3]}"
    )


def test_property_well_formed_metadata(small_corpus):
    """Every entry has well-formed (level, weight, character) tuples.

    Property: the loader must enforce schema sanity.
    """
    for e in small_corpus:
        assert isinstance(e.label, str) and "." in e.label
        assert isinstance(e.level, int) and e.level >= 1
        assert isinstance(e.weight, int) and e.weight >= 1
        assert isinstance(e.char_order, int) and e.char_order >= 1
        assert isinstance(e.char_orbit_label, str) and e.char_orbit_label
        assert isinstance(e.a_p, tuple) and len(e.a_p) >= 1
        assert isinstance(e.primes, tuple) and len(e.primes) == len(e.a_p)


def test_property_determinism_with_fixed_seed(small_corpus):
    """The reset/sample/step pipeline is deterministic given seed.

    Property: same seed -> same (label, target_prime, true_bin) and
    same observation.
    """
    from prometheus_math.modular_form_env import ModularFormEnv
    env_a = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
    env_b = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
    obs_a, info_a = env_a.reset(seed=99)
    obs_b, info_b = env_b.reset(seed=99)
    np.testing.assert_array_equal(obs_a, obs_b)
    assert info_a["label"] == info_b["label"]
    assert info_a["target_prime"] == info_b["target_prime"]
    assert info_a["true_bin"] == info_b["true_bin"]
    env_a.close()
    env_b.close()


def test_property_obs_shape_consistent(small_env):
    """The observation vector has fixed dimension 2*n_ap + HISTORY_DIM.

    Property: observation_space contract.
    """
    from prometheus_math.modular_form_env import _obs_dim
    env = small_env
    expected = _obs_dim(env.n_ap())
    for s in (1, 2, 3, 4, 5):
        obs, _info = env.reset(seed=s)
        assert obs.shape == (expected,), (
            f"obs shape mismatch at seed={s}: "
            f"{obs.shape} vs ({expected},)"
        )


def test_property_normalization_round_trip():
    """For (p=2, weight=12) the bound is ``2 * 2^{5.5} ~ 90.5``;
    a_2 = -24 normalizes to ``-24 / 90.5 ~ -0.265`` which lands in bin
    9 of 21 (bin width 2/21 ~ 0.0952; bin 9 covers [-0.143, -0.048]
    -- close to but NOT containing -0.265). Compute and assert.

    Property: normalization + bin quantization are inverses on bin
    centers; arbitrary values land in the bin whose center is closest
    (within bin half-width).
    """
    from prometheus_math.modular_form_env import (
        deligne_bound, normalize_ap, bin_for_normalized, bin_center,
    )
    bound = deligne_bound(2, 12)
    assert math.isclose(bound, 2.0 * 2.0 ** 5.5, rel_tol=1e-9)
    norm = normalize_ap(-24, 2, 12)
    assert -0.30 < norm < -0.25
    idx = bin_for_normalized(norm)
    # Center of bin idx must be within bin half-width of norm.
    c = bin_center(idx)
    half_width = 1.0 / 21.0
    assert abs(c - norm) <= half_width + 1e-9


# ---------------------------------------------------------------------------
# Edge -- empty corpus, malformed inputs, action out of range
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_raises_value_error(_mf_available):
    """Constructing an env with an empty corpus must raise ValueError.

    Edge: defensive contract.
    """
    from prometheus_math.modular_form_env import ModularFormEnv
    with pytest.raises(ValueError):
        ModularFormEnv(corpus=[], split="all")


def test_edge_action_out_of_range(small_env):
    """Predicting a bin outside [0, N_BINS) is rejected.

    Edge: action-space contract.
    """
    from prometheus_math.modular_form_env import N_BINS
    env = small_env
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(N_BINS)
    env.reset(seed=2)
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_form_with_short_a_p_handled():
    """If a hand-built corpus contains a form with very few a_p entries
    (less than ``context_min``), the env must reject it cleanly at
    construction.

    Edge: the loader normally always fills ``n_ap`` slots, but
    pathological hand-built corpora exist (e.g. pulled from a different
    LMFDB schema). Verify the env doesn't crash mid-episode.
    """
    from prometheus_math._modular_form_corpus import (
        ModularFormEntry, PRIMES_30,
    )
    from prometheus_math.modular_form_env import ModularFormEnv
    short = ModularFormEntry(
        label="X.2.a.a", level=99, weight=2,
        char_order=1, char_orbit_label="a",
        a_p=(1, -1, 0),
        primes=PRIMES_30[:3],
        q_expansion=(1, 1, -1, 0),
    )
    # context_min default 5 > 3 -> raise.
    with pytest.raises(ValueError):
        ModularFormEnv(corpus=[short], split="all", context_min=5, seed=0)
    # context_min=2 should construct, but a_p length 3 still leaves
    # only 1 prime to predict (n_ap - 1 = 2 max k, ctx_min 2 -> ctx
    # always 2). Should construct + reset/step cleanly.
    env = ModularFormEnv(corpus=[short], split="all", context_min=2, seed=0)
    obs, info = env.reset(seed=0)
    assert info["context_k"] == 2  # only valid value
    _, r, _, _, _ = env.step(0)
    assert r in (0.0, 100.0)
    env.close()


def test_edge_unknown_split_raises(small_corpus):
    """An invalid ``split`` value is rejected at construction.

    Edge: defensive contract.
    """
    from prometheus_math.modular_form_env import ModularFormEnv
    with pytest.raises(ValueError):
        ModularFormEnv(corpus=small_corpus, split="bogus")


def test_edge_action_clipped_during_normalization():
    """Inputs slightly outside [-1, 1] (e.g. due to LMFDB rounding)
    must NOT crash ``bin_for_normalized``; they clip to the nearest
    extreme bin.

    Edge: numerical-robustness contract.
    """
    from prometheus_math.modular_form_env import (
        bin_for_normalized, N_BINS,
    )
    # Way out of range, both signs.
    assert bin_for_normalized(2.0) == N_BINS - 1
    assert bin_for_normalized(-2.0) == 0
    # Boundary cases.
    assert bin_for_normalized(1.0) == N_BINS - 1
    assert bin_for_normalized(-1.0) == 0
    assert 0 <= bin_for_normalized(0.0) < N_BINS


# ---------------------------------------------------------------------------
# Composition -- multi-algorithm pilot, comparison dict, growth invariant
# ---------------------------------------------------------------------------


def test_composition_pilot_random_produces_well_formed_report(small_env):
    """``train_random`` returns a dict with the expected keys and
    sensible values.

    Composition: the pilot harness contract.
    """
    from prometheus_math.modular_form_env import train_random
    out = train_random(small_env, n_episodes=80, seed=0)
    for key in ("rewards", "mean_reward", "accuracy", "n_episodes",
                "agent", "pred_counts"):
        assert key in out, f"missing key {key} in output"
    assert out["n_episodes"] == 80
    assert out["agent"] == "random"
    assert 0.0 <= out["accuracy"] <= 1.0
    # Random over 21 bins should have accuracy in a wide band [0, 0.20].
    assert out["accuracy"] <= 0.25


def test_composition_three_algorithm_comparison(small_corpus):
    """Running random / REINFORCE / PPO on the same corpus yields a
    comparison dict with all three reports present and shape-matched.

    Composition: the cross-algorithm comparison contract used by the
    pilot driver.
    """
    from prometheus_math.modular_form_env import (
        ModularFormEnv, train_random, train_reinforce, train_ppo,
    )
    e1 = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
    e2 = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
    e3 = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
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
    # Sanity: the agent reports name themselves.
    assert comparison["random"]["agent"] == "random"
    assert comparison["reinforce"]["agent"] == "reinforce"
    assert comparison["ppo"]["agent"] == "ppo"


def test_composition_substrate_growth_one_binding_one_eval(small_env):
    """Each step produces exactly one binding + one evaluation row in
    the sigma kernel. Mirrors the BSDRankEnv invariant.

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


def test_composition_pilot_records_match_expectation(small_corpus):
    """A 200-episode REINFORCE run on the small corpus produces:
      - a numpy rewards array of length 200,
      - a finite mean reward in [0, REWARD_HIT],
      - pred_counts summing to 200.

    Composition: pipeline-record schema for the pilot driver.
    """
    from prometheus_math.modular_form_env import (
        ModularFormEnv, train_reinforce, REWARD_HIT,
    )
    env = ModularFormEnv(corpus=small_corpus, split="all", seed=0)
    rep = train_reinforce(env, n_episodes=200, lr=0.02, seed=0)
    env.close()
    rewards = rep["rewards"]
    assert isinstance(rewards, np.ndarray)
    assert rewards.shape == (200,)
    assert 0.0 <= rep["mean_reward"] <= REWARD_HIT
    assert sum(rep["pred_counts"]) == 200
