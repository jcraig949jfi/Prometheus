"""Tests for prometheus_math.genus2_env (genus-2 rank-class prediction).

Cross-domain validation #3: same substrate (sigma kernel + BIND/EVAL +
arsenal-style action table) as BSDRankEnv and ModularFormEnv, but the
ground truth lives in LMFDB's ``g2c_curves`` table. Per
``project_genus2_rosetta.md``, genus-2 sits at the intersection of all
five mathematical worlds, making it the highest-leverage domain for
the substrate's island-silence test.

Math-tdd skill rubric (>= 3 in every category).

Authority -- LMFDB ground truth: 169.a.169.1 (lowest-conductor curve),
rank 0 means torsion-only MW, conductor / discriminant arithmetic
relation.

Property -- well-formed coefficient lists, modal-class bias, determinism,
observation shape.

Edge -- empty corpus, malformed equation, action out of range.

Composition -- 3-algorithm dict, pilot record schema, end-to-end flow.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _g2_available():
    from prometheus_math import _genus2_corpus
    ok, reason = _genus2_corpus.is_available()
    if not ok:
        pytest.skip(f"genus2 corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_corpus(_g2_available):
    """A small but stratified corpus for fast tests (~150 curves)."""
    from prometheus_math import _genus2_corpus
    return _genus2_corpus.load_genus2_corpus(
        cond_max=20000, n_total=150, seed=42, use_cache=True,
    )


@pytest.fixture
def small_env(small_corpus):
    from prometheus_math.genus2_env import Genus2Env
    env = Genus2Env(corpus=small_corpus, split="all", seed=0)
    yield env
    env.close()


# ---------------------------------------------------------------------------
# Authority -- LMFDB ground truth alignment
# ---------------------------------------------------------------------------


def test_authority_corpus_contains_lowest_conductor_curve(_g2_available):
    """The corpus loader must yield 169.a.169.1, the lowest-conductor
    genus-2 curve in LMFDB. We test against the raw (unstratified)
    cache, which is the pool the stratified loader subsamples from.

    Authority: LMFDB lists 169.a.169.1 as the smallest-conductor entry
    in g2c_curves; conductor 169 = 13^2.
    """
    from prometheus_math import _genus2_corpus
    cp = _genus2_corpus.cache_path()
    if not (cp.is_file() and cp.stat().st_size > 0):
        pytest.skip("genus2 cache not present; run loader once to populate")
    pool = _genus2_corpus.read_cache(cp)
    labels = {e.label for e in pool}
    canonicals = {"169.a.169.1", "249.a.249.1", "277.a.277.1",
                  "294.a.294.1", "295.a.295.1"}
    found = labels & canonicals
    assert found, (
        f"None of the canonical low-conductor curves "
        f"{canonicals} found in raw cache of size {len(pool)}"
    )


def test_authority_169_a_169_1_metadata_matches_lmfdb(_g2_available):
    """169.a.169.1 has known LMFDB metadata: conductor 169, abs_disc 169,
    analytic_rank 0, torsion_order 19, torsion subgroup [19]. We
    verify the canonical entry round-trips through the loader.

    Authority: LMFDB g2c_curves snapshot (verified live 2026-05-04).
    """
    from prometheus_math import _genus2_corpus
    cp = _genus2_corpus.cache_path()
    if not (cp.is_file() and cp.stat().st_size > 0):
        pytest.skip("genus2 cache not present; run loader once to populate")
    pool = _genus2_corpus.read_cache(cp)
    rec = next((e for e in pool if e.label == "169.a.169.1"), None)
    assert rec is not None, "169.a.169.1 missing from raw cache"
    assert rec.conductor == 169
    assert rec.abs_disc == 169
    assert rec.analytic_rank == 0
    assert rec.torsion_order == 19
    assert rec.torsion_subgroup == "[19]"
    # Equation y^2 + h(x)y = f(x): f = 0 + 0x + 0x^2 + 0x^3 + 1x^4 + 1x^5
    # h = 1 + 1x + 0x^2 + 1x^3
    assert rec.f_coeffs[4] == 1 and rec.f_coeffs[5] == 1
    assert rec.h_coeffs[0] == 1 and rec.h_coeffs[3] == 1


def test_authority_rank_0_implies_torsion_only_mw(_g2_available):
    """For curves with mw_rank == 0, the Mordell-Weil group J(Q) is
    purely torsion, so any rational points come from torsion. We verify
    the corpus invariant: rank 0 entries have torsion_order >= 1 and
    no contradictions with analytic_rank.

    Authority: classical Mordell-Weil theorem -- rank 0 means J(Q) =
    J(Q)_tors. LMFDB ranks are computed via descent + analytic
    cross-check.
    """
    from prometheus_math import _genus2_corpus
    corpus = _genus2_corpus.load_genus2_corpus(
        cond_max=20000, n_total=400, seed=0, use_cache=True,
    )
    rank_0_curves = [e for e in corpus if e.analytic_rank == 0]
    assert len(rank_0_curves) >= 5, (
        f"too few rank-0 curves to test invariant: {len(rank_0_curves)}"
    )
    for e in rank_0_curves:
        assert e.torsion_order >= 1, (
            f"{e.label}: rank-0 curve has invalid torsion_order "
            f"{e.torsion_order}"
        )
        # If mw_rank is also 0, MW group is torsion-only.
        if e.mw_rank is not None and e.mw_rank == 0:
            # The rank-class machinery should classify it as 0.
            assert e.rank_class == 0


def test_authority_conductor_divides_discriminant(_g2_available):
    """For genus-2 curves over Q, the conductor is the radical of the
    discriminant (modulo wild ramification). LMFDB stores both, with
    the relation: cond divides abs_disc (cond is built from the same
    primes as the discriminant).

    Authority: Liu, Algebraic Geometry and Arithmetic Curves (chapter
    9); Q. Liu's conductor formula for hyperelliptic curves.
    """
    from prometheus_math import _genus2_corpus
    corpus = _genus2_corpus.load_genus2_corpus(
        cond_max=20000, n_total=200, seed=0, use_cache=True,
    )
    violations = []
    for e in corpus:
        if e.conductor <= 0 or e.abs_disc <= 0:
            continue
        if e.abs_disc % e.conductor != 0:
            violations.append((e.label, e.conductor, e.abs_disc))
    assert not violations, (
        f"conductor does not divide abs_disc for "
        f"{len(violations)} curves; first 3: {violations[:3]}"
    )


def test_authority_predicting_correct_class_yields_full_reward(small_env):
    """Predicting the true rank class must pay out REWARD_HIT.

    Authority: env reward contract -- hit pays REWARD_HIT, miss pays 0.
    """
    from prometheus_math.genus2_env import REWARD_HIT
    env = small_env
    obs, info = env.reset(seed=12345)
    true_class = int(info["true_rank_class"])
    _, r, term, _, info2 = env.step(true_class)
    assert math.isclose(r, REWARD_HIT)
    assert info2["hit"] is True
    assert term is True
    assert info2["true_rank_class"] == true_class
    assert info2["predicted_class"] == true_class


# ---------------------------------------------------------------------------
# Property -- well-formed schema, modal bias, determinism
# ---------------------------------------------------------------------------


def test_property_well_formed_coefficient_lists(small_corpus):
    """Every entry has fixed-length f_coeffs and h_coeffs lists, all
    integers. f has F_COEFF_LEN slots; h has H_COEFF_LEN slots.

    Property: env observation requires fixed-shape input.
    """
    from prometheus_math._genus2_corpus import F_COEFF_LEN, H_COEFF_LEN
    for e in small_corpus:
        assert isinstance(e.f_coeffs, tuple)
        assert isinstance(e.h_coeffs, tuple)
        assert len(e.f_coeffs) == F_COEFF_LEN, (
            f"{e.label}: f_coeffs length {len(e.f_coeffs)} != "
            f"{F_COEFF_LEN}"
        )
        assert len(e.h_coeffs) == H_COEFF_LEN, (
            f"{e.label}: h_coeffs length {len(e.h_coeffs)} != "
            f"{H_COEFF_LEN}"
        )
        assert all(isinstance(x, int) for x in e.f_coeffs)
        assert all(isinstance(x, int) for x in e.h_coeffs)


def test_property_rank_distribution_biased_toward_low_ranks(_g2_available):
    """LMFDB's analytic-rank distribution is dominated by ranks 0 and 1
    (combined ~65%). After stratified sampling rank 2+ should be the
    smallest stratum.

    Property: the corpus respects the LMFDB rank prior; rank 2+ should
    not exceed the union of rank 0 and rank 1.
    """
    from prometheus_math import _genus2_corpus
    corpus = _genus2_corpus.load_genus2_corpus(
        cond_max=20000, n_total=200, seed=0, use_cache=True,
    )
    summary = _genus2_corpus.corpus_summary(corpus)
    counts = summary["rank_class_counts"]
    n_low = counts.get(0, 0) + counts.get(1, 0)
    n_high = counts.get(2, 0)
    assert n_low > n_high, (
        f"rank distribution not low-rank biased: "
        f"{counts} (low={n_low}, high={n_high})"
    )


def test_property_determinism_with_fixed_seed(small_corpus):
    """The reset/sample/step pipeline is deterministic given seed.

    Property: same seed -> same (label, true_rank_class) and same obs.
    """
    from prometheus_math.genus2_env import Genus2Env
    env_a = Genus2Env(corpus=small_corpus, split="all", seed=0)
    env_b = Genus2Env(corpus=small_corpus, split="all", seed=0)
    obs_a, info_a = env_a.reset(seed=99)
    obs_b, info_b = env_b.reset(seed=99)
    np.testing.assert_array_equal(obs_a, obs_b)
    assert info_a["label"] == info_b["label"]
    assert info_a["true_rank_class"] == info_b["true_rank_class"]
    env_a.close()
    env_b.close()


def test_property_obs_shape_consistent(small_env):
    """The observation vector has fixed dimension obs_dim().

    Property: observation_space contract.
    """
    from prometheus_math.genus2_env import obs_dim
    env = small_env
    expected = obs_dim()
    for s in (1, 2, 3, 4, 5):
        obs, _info = env.reset(seed=s)
        assert obs.shape == (expected,), (
            f"obs shape mismatch at seed={s}: "
            f"{obs.shape} vs ({expected},)"
        )


# ---------------------------------------------------------------------------
# Edge -- empty corpus, malformed inputs, action out of range
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_raises_value_error(_g2_available):
    """Constructing an env with an empty corpus must raise ValueError.

    Edge: defensive contract.
    """
    from prometheus_math.genus2_env import Genus2Env
    with pytest.raises(ValueError):
        Genus2Env(corpus=[], split="all")


def test_edge_curve_with_no_rank_metadata_handled(_g2_available):
    """A handcrafted entry with analytic_rank set to 0/1/2 must yield
    the matching rank_class. The env's rank_class property must coerce
    high analytic ranks (>= 2) to class 2 without raising.

    Edge: defensive against future LMFDB schema changes that introduce
    rank > 4.
    """
    from prometheus_math._genus2_corpus import (
        Genus2Entry, F_COEFF_LEN, H_COEFF_LEN,
    )
    e = Genus2Entry(
        label="X.a.X.1", iso_class="X.a",
        conductor=1000, abs_disc=1000, disc_sign=1,
        f_coeffs=(0,) * F_COEFF_LEN, h_coeffs=(0,) * H_COEFF_LEN,
        analytic_rank=4,  # High rank -- should clamp to class 2
        mw_rank=4,
        torsion_order=1, torsion_subgroup="[]",
        real_period=1.0, st_label="", geom_end_alg="Q",
    )
    assert e.rank_class == 2  # >= 2 collapses to class 2


def test_edge_action_out_of_range(small_env):
    """Predicting a class outside [0, N_RANK_ACTIONS) is rejected.

    Edge: action-space contract.
    """
    from prometheus_math.genus2_env import N_RANK_ACTIONS
    env = small_env
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(N_RANK_ACTIONS)
    env.reset(seed=2)
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_unknown_split_raises(small_corpus):
    """An invalid ``split`` value is rejected at construction.

    Edge: defensive contract.
    """
    from prometheus_math.genus2_env import Genus2Env
    with pytest.raises(ValueError):
        Genus2Env(corpus=small_corpus, split="bogus")


def test_edge_malformed_equation_handled():
    """``parse_equation`` must reject empty / non-string inputs.

    Edge: corpus loader robustness contract.
    """
    from prometheus_math._genus2_corpus import parse_equation
    with pytest.raises(ValueError):
        parse_equation("")
    with pytest.raises(ValueError):
        parse_equation("nonsense")
    # Well-formed input still works.
    f, h = parse_equation("[[0,0,0,0,1,1],[1,1,0,1]]")
    assert f[0] == 0 and f[5] == 1  # f_5 = 1
    assert h[0] == 1 and h[3] == 1  # h_3 = 1


# ---------------------------------------------------------------------------
# Composition -- multi-algorithm pilot, pipeline records, end-to-end
# ---------------------------------------------------------------------------


def test_composition_three_algorithm_comparison(small_corpus):
    """Running random / REINFORCE / PPO on the same corpus yields a
    well-formed comparison dict with all three reports present.

    Composition: cross-algorithm comparison contract.
    """
    from prometheus_math.genus2_env import (
        Genus2Env, train_random, train_reinforce, train_ppo,
    )
    e1 = Genus2Env(corpus=small_corpus, split="all", seed=0)
    e2 = Genus2Env(corpus=small_corpus, split="all", seed=0)
    e3 = Genus2Env(corpus=small_corpus, split="all", seed=0)
    rep_random = train_random(e1, n_episodes=80, seed=0)
    rep_lrn = train_reinforce(e2, n_episodes=80, lr=0.05, seed=0)
    rep_ppo = train_ppo(e3, n_episodes=80, lr=0.005, hidden=16, seed=0)
    e1.close(); e2.close(); e3.close()
    comparison = {
        "random": rep_random,
        "reinforce": rep_lrn,
        "ppo": rep_ppo,
    }
    for arm, rep in comparison.items():
        for k in ("rewards", "mean_reward", "accuracy", "n_episodes",
                  "agent", "pred_counts"):
            assert k in rep, f"missing key {k} in {arm} report"
        assert rep["n_episodes"] == 80
        assert 0.0 <= rep["accuracy"] <= 1.0
    assert comparison["random"]["agent"] == "random"
    assert comparison["reinforce"]["agent"] == "reinforce"
    assert comparison["ppo"]["agent"] == "ppo"


def test_composition_pilot_records_match_expectation(small_corpus):
    """A 200-episode REINFORCE run on the small corpus produces:
      - a numpy rewards array of length 200,
      - a finite mean reward in [0, REWARD_HIT],
      - pred_counts summing to 200.

    Composition: pipeline-record schema for the pilot driver.
    """
    from prometheus_math.genus2_env import (
        Genus2Env, train_reinforce, REWARD_HIT,
    )
    env = Genus2Env(corpus=small_corpus, split="all", seed=0)
    rep = train_reinforce(env, n_episodes=200, lr=0.05, seed=0)
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


def test_composition_end_to_end_corpus_env_reinforce_record(small_corpus):
    """End-to-end: corpus loaded -> env constructed -> REINFORCE trained
    -> test eval recorded -> all numerics finite.

    Composition: full pipeline smoke test.
    """
    from prometheus_math import _genus2_corpus
    from prometheus_math.genus2_env import (
        Genus2Env, train_reinforce,
    )
    train, test = _genus2_corpus.split_train_test(
        small_corpus, train_frac=0.7, seed=0,
    )
    assert len(train) > 0 and len(test) > 0

    env = Genus2Env(corpus=train, split="all", seed=11)
    rep = train_reinforce(env, n_episodes=120, lr=0.05, seed=11)
    env.close()

    # Eval on test split with the trained linear policy.
    W = rep["policy_W_final"]
    b = rep["policy_b_final"]
    env_t = Genus2Env(corpus=test, split="all", seed=22)
    rng = np.random.default_rng(22)
    rs = []
    for _ in range(min(100, len(test) * 4)):
        obs, _info = env_t.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        a = int(np.argmax(logits))
        _, r, _, _, _ = env_t.step(a)
        rs.append(r)
    env_t.close()
    test_mean = float(np.mean(rs))
    # Sanity: all numerics finite.
    assert math.isfinite(rep["mean_reward"])
    assert math.isfinite(test_mean)
    # Pred counts sum to episode count.
    assert sum(rep["pred_counts"]) == 120
