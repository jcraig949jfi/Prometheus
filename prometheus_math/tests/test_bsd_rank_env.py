"""Tests for prometheus_math.bsd_rank_env (BSD rank-prediction env).

Cross-domain validation: same substrate (sigma kernel + BIND/EVAL +
arsenal-style action table) as the Lehmer / SigmaMath env, but the
ground truth is dense. LMFDB / Cremona supply known Mordell-Weil
ranks for every curve, so every prediction has a verifiable answer.

Math-tdd skill rubric (>=3 in every category).

Authority -- the env's ground truth comes from the Cremona mirror;
verify it agrees with LMFDB on small known-rank curves.

Property -- reward shape, determinism, episode length.

Edge -- empty corpus, missing a_p data, mirror unreachable.

Composition -- random vs trained baseline, substrate-growth invariant.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Skip-with-message gate: the entire suite is moot without a Cremona
# mirror.  We probe once at module import.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _bsd_available():
    from prometheus_math import _bsd_corpus
    ok, reason = _bsd_corpus.is_available()
    if not ok:
        pytest.skip(f"BSD corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_corpus(_bsd_available):
    """A small but stratified corpus for fast tests (~200 curves)."""
    from prometheus_math import _bsd_corpus
    return _bsd_corpus.load_bsd_corpus(
        n_total=200,
        seed=42,
        conductor_max=20000,
    )


@pytest.fixture
def small_env(small_corpus):
    from prometheus_math.bsd_rank_env import BSDRankEnv
    env = BSDRankEnv(corpus=small_corpus, split="all", seed=0)
    yield env
    env.close()


# ---------------------------------------------------------------------------
# Authority -- ground truth alignment with LMFDB / Cremona
# ---------------------------------------------------------------------------


def test_authority_corpus_has_at_least_100_entries(_bsd_available):
    """The default 1000-entry stratified corpus should yield well over 100
    entries even when conductor is capped to the smallest mirror block.

    Authority: Cremona mirror documented as covering ~64K curves with
    conductor <= 10K, more than enough to draw 1000 stratified samples.
    """
    from prometheus_math import _bsd_corpus
    corpus = _bsd_corpus.load_bsd_corpus(
        n_total=1000, seed=0, conductor_max=20000
    )
    assert len(corpus) >= 100, (
        f"corpus too small: got {len(corpus)} entries; expected >= 100"
    )


def test_authority_known_curve_11a_rank_zero(_bsd_available):
    """The curve 11.a (LMFDB) / 11a (Cremona) has rank 0 (Mazur 1973;
    LMFDB confirmed). The env's ground truth must agree.

    Authority: classical -- rank of 11.a is the textbook example of an
    EC over Q with no rational points of infinite order.
    """
    from prometheus_math.databases import cremona
    rows = cremona.elliptic_curves(label="11a1", fall_back_to_lmfdb=False)
    assert rows, "Cremona mirror did not return 11a1"
    rec = rows[0]
    assert rec["rank"] == 0, f"11a1 rank should be 0; got {rec['rank']}"
    assert rec["conductor"] == 11


def test_authority_predicting_correct_rank_yields_full_reward(small_env):
    """Predicting a curve's true rank should pay out REWARD_HIT (=100).

    Authority: env reward contract -- hit pays REWARD_HIT, miss pays 0.
    """
    from prometheus_math.bsd_rank_env import REWARD_HIT
    env = small_env
    obs, info = env.reset(seed=123)
    true_rank = int(info["true_rank"])
    _, r, term, _, info2 = env.step(true_rank)
    assert math.isclose(r, REWARD_HIT)
    assert info2["hit"] is True
    assert term is True
    assert info2["true_rank"] == true_rank
    assert info2["predicted_rank"] == true_rank


def test_authority_wrong_rank_yields_zero_reward(small_env):
    """Predicting a rank that does NOT match ground truth pays 0.

    Authority: env reward contract complement.
    """
    from prometheus_math.bsd_rank_env import N_RANK_ACTIONS
    env = small_env
    obs, info = env.reset(seed=4567)
    true_rank = int(info["true_rank"])
    # Pick any other valid action.
    wrong = (true_rank + 1) % N_RANK_ACTIONS
    _, r, term, _, info2 = env.step(wrong)
    assert r == 0.0
    assert info2["hit"] is False
    assert term is True


# ---------------------------------------------------------------------------
# Property -- reward shape, determinism, episode length
# ---------------------------------------------------------------------------


def test_property_reward_in_zero_or_hundred(small_env):
    """For every action, reward is exactly 0 or REWARD_HIT.

    Property: discrete reward function over discrete action space.
    """
    from prometheus_math.bsd_rank_env import REWARD_HIT, N_RANK_ACTIONS
    env = small_env
    rng = np.random.default_rng(7)
    for t in range(40):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, N_RANK_ACTIONS))
        _, r, _, _, _ = env.step(a)
        assert r in (0.0, REWARD_HIT), f"reward escape: r={r}"


def test_property_same_seed_same_split(small_corpus):
    """The train/test split is reproducible from the seed alone.

    Property: deterministic partitioning -> same labels in both halves
    across reruns.
    """
    from prometheus_math import _bsd_corpus
    train_a, test_a = _bsd_corpus.split_train_test(
        small_corpus, train_frac=0.7, seed=11
    )
    train_b, test_b = _bsd_corpus.split_train_test(
        small_corpus, train_frac=0.7, seed=11
    )
    labels_a = [e.label for e in train_a]
    labels_b = [e.label for e in train_b]
    assert labels_a == labels_b
    labels_a_t = [e.label for e in test_a]
    labels_b_t = [e.label for e in test_b]
    assert labels_a_t == labels_b_t


def test_property_episode_length_one(small_env):
    """Every episode terminates after exactly one step.

    Property: ``terminated`` is True after step(); calling step() twice
    without an intervening reset is a hard error.
    """
    from prometheus_math.bsd_rank_env import N_RANK_ACTIONS
    env = small_env
    env.reset(seed=99)
    _, _, term, trunc, _ = env.step(0)
    assert term is True
    assert trunc is False
    with pytest.raises(RuntimeError):
        env.step(0)  # no reset


def test_property_obs_shape_consistent(small_env):
    """The observation vector has fixed dimension n_ap + 6.

    Property: observation_space contract.
    """
    from prometheus_math.bsd_rank_env import _obs_dim
    env = small_env
    expected = _obs_dim(env.n_ap())
    for s in (1, 2, 3, 4):
        obs, _info = env.reset(seed=s)
        assert obs.shape == (expected,)


# ---------------------------------------------------------------------------
# Edge -- empty / malformed inputs and unreachable mirror
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_raises_value_error(_bsd_available):
    """Constructing an env with an empty corpus must raise.

    Edge: defensive contract.
    """
    from prometheus_math.bsd_rank_env import BSDRankEnv
    with pytest.raises(ValueError):
        BSDRankEnv(corpus=[], split="all")


def test_edge_unknown_split_raises(small_corpus):
    """An invalid ``split`` value is rejected at construction.

    Edge: defensive contract.
    """
    from prometheus_math.bsd_rank_env import BSDRankEnv
    with pytest.raises(ValueError):
        BSDRankEnv(corpus=small_corpus, split="bogus")


def test_edge_action_out_of_range(small_env):
    """Predicting a rank outside [0, N_RANK_ACTIONS) is rejected.

    Edge: action-space contract.
    """
    from prometheus_math.bsd_rank_env import N_RANK_ACTIONS
    env = small_env
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(N_RANK_ACTIONS)
    env.reset(seed=2)
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_zero_n_total_raises(_bsd_available):
    """``load_bsd_corpus(n_total=0)`` is a degenerate request and raises.

    Edge: defensive contract on the loader.
    """
    from prometheus_math import _bsd_corpus
    with pytest.raises(ValueError):
        _bsd_corpus.load_bsd_corpus(n_total=0, seed=0)


def test_edge_missing_aplist_skips_curves_when_required():
    """When require_aplist=True the loader drops curves whose isogeny class
    has no aplist row.

    Edge: documented filter behaviour.

    We simulate "missing" by asking for a conductor cap larger than the
    aplist mirror covers; the loader is required NOT to invent zeros and
    NOT to crash, but the resulting corpus may simply be smaller than
    requested.
    """
    from prometheus_math import _bsd_corpus
    ok, _ = _bsd_corpus.is_available()
    if not ok:
        pytest.skip("BSD corpus unavailable")
    corpus = _bsd_corpus.load_bsd_corpus(
        n_total=50, seed=0, conductor_max=15000, require_aplist=True
    )
    # Whatever we got back is non-empty and every entry has a non-zero
    # a_p sequence (we don't expect every prime to be 0 unless really
    # missing).
    assert corpus, "loader returned no curves"
    # At least some entries should have non-trivial a_p.
    has_signal = any(any(x != 0 for x in e.a_p) for e in corpus)
    assert has_signal


# ---------------------------------------------------------------------------
# Composition -- random vs learner, substrate-growth invariant
# ---------------------------------------------------------------------------


def test_composition_random_baseline_in_expected_range(small_env):
    """A uniform-random predictor over 5 classes on a stratified-by-rank
    sample picks correctly with probability roughly equal to the modal
    class frequency divided by 5 (each class is independently and
    uniformly chosen).

    Composition: Bernoulli accuracy per episode -> mean reward in
    [10, 40] over 200 episodes (loose band, catches gross errors).
    """
    from prometheus_math.bsd_rank_env import train_random_bsd
    out = train_random_bsd(small_env, n_episodes=200, seed=0)
    assert 10.0 <= out["mean_reward"] <= 40.0, (
        f"random baseline out of expected band: {out['mean_reward']}"
    )


def test_composition_majority_class_baseline_beats_random(small_env, small_corpus):
    """Predicting rank 0 always (the modal class) should beat uniform-random
    on a corpus where rank-0 is plurality.

    Composition: a stronger baseline must dominate the floor.
    """
    from prometheus_math.bsd_rank_env import (
        train_random_bsd, train_majority_bsd, BSDRankEnv,
    )
    # Use fresh envs to keep state isolated.
    e1 = BSDRankEnv(corpus=small_corpus, split="all", seed=0)
    e2 = BSDRankEnv(corpus=small_corpus, split="all", seed=0)
    rand_out = train_random_bsd(e1, n_episodes=200, seed=0)
    maj_out = train_majority_bsd(e2, n_episodes=200, seed=0)
    e1.close(); e2.close()
    assert maj_out["mean_reward"] > rand_out["mean_reward"], (
        f"majority({maj_out['mean_reward']:.2f}) did not beat "
        f"random({rand_out['mean_reward']:.2f})"
    )


def test_composition_reinforce_learns_signal(small_corpus):
    """A REINFORCE agent with obs-conditioned linear policy should beat
    the uniform-random floor by a clear margin (>= 1.5x lift) over 800
    episodes on a stratified corpus where a_p carries rank information.

    Composition: discovery-grade acceptance criterion -- the substrate
    can recover known math from labelled data.
    """
    from prometheus_math.bsd_rank_env import (
        BSDRankEnv, train_random_bsd, train_reinforce_bsd,
    )
    e_rand = BSDRankEnv(corpus=small_corpus, split="all", seed=0)
    e_lrn = BSDRankEnv(corpus=small_corpus, split="all", seed=0)
    rand_out = train_random_bsd(e_rand, n_episodes=800, seed=0)
    lrn_out = train_reinforce_bsd(
        e_lrn, n_episodes=800, lr=0.05, seed=0,
    )
    e_rand.close(); e_lrn.close()
    rand_mean = rand_out["mean_reward"]
    lrn_mean = lrn_out["mean_reward"]
    assert lrn_mean >= 1.5 * max(1.0, rand_mean), (
        f"REINFORCE failed to beat random: "
        f"random={rand_mean:.2f}, learned={lrn_mean:.2f}"
    )


def test_composition_substrate_growth_one_binding_one_eval(small_env):
    """Each step produces exactly one binding + one evaluation row in the
    sigma kernel. Mirrors the SigmaMathEnv invariant.

    Composition: substrate-attribution contract.
    """
    env = small_env
    env.reset(seed=5)
    k = env.kernel()

    def _count(table: str) -> int:
        return int(k.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

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


# ---------------------------------------------------------------------------
# Telemetry -- substrate v2.3 EvidenceField.computational_friction (Pre-Tier-0
# step 0b instrumentation). info dict must carry elapsed_seconds + oracle_calls
# without breaking pre-existing keys.
# ---------------------------------------------------------------------------


def test_telemetry_step_emits_elapsed_and_oracle_calls(small_env):
    """step() must populate ``elapsed_seconds`` (>0) and ``oracle_calls``
    (>=1) in the returned info dict, while preserving at least one
    pre-existing key (regression check).

    Substrate v2.3 contract: EvidenceField.computational_friction has
    ``elapsed_seconds`` and ``oracle_calls`` as its first two
    components. Without env-side telemetry these axes ship empty.
    """
    env = small_env
    env.reset(seed=2026)
    _, _, _, _, info = env.step(0)
    assert "elapsed_seconds" in info, "missing elapsed_seconds in info"
    assert info["elapsed_seconds"] > 0, (
        f"elapsed_seconds must be > 0; got {info['elapsed_seconds']}"
    )
    assert "oracle_calls" in info, "missing oracle_calls in info"
    assert info["oracle_calls"] >= 1, (
        f"oracle_calls must be >= 1; got {info['oracle_calls']}"
    )
    # Regression: a known pre-existing key is still present.
    assert "true_rank" in info, "regression: pre-existing key true_rank lost"


# ---------------------------------------------------------------------------
# Tier 3 -- KillVector v2 + EvidenceField wired into info dict (substrate
# v2.3 §9). Reported as "observed policy table", not "manifold chart"
# (no CoordinateChart registered for cross-domain envs yet).
# ---------------------------------------------------------------------------


def test_step_info_includes_kill_vector(small_env):
    """``info["kill_vector"]`` is a dict with at least one component.

    Substrate v2.3 §9 Tier 3 contract: each cross-domain env emits a
    KillVector covering its falsifier(s). For prediction-style envs
    the single component is ``"prediction_correct"``.
    """
    env = small_env
    env.reset(seed=2027)
    _, _, _, _, info = env.step(0)
    assert "kill_vector" in info, "missing kill_vector in info"
    kv = info["kill_vector"]
    assert isinstance(kv, dict), f"kill_vector must be dict, got {type(kv)}"
    components = kv.get("components")
    assert isinstance(components, list) and len(components) >= 1, (
        f"kill_vector.components must be non-empty list; got {components!r}"
    )
    # Single-component prediction kill-vector convention.
    names = [c["falsifier_name"] for c in components]
    assert "prediction_correct" in names, (
        f"expected 'prediction_correct' falsifier; got {names}"
    )


def test_step_info_includes_evidence_field(small_env):
    """``info["evidence_field"]`` carries the 6 axes of EvidenceField.

    Substrate v2.3 §6.2 P1 contract: distance_to_target,
    battery_survival_depth, verification_depth, exclusion_distance,
    assumption_load, computational_friction.
    """
    env = small_env
    env.reset(seed=2028)
    _, _, _, _, info = env.step(0)
    assert "evidence_field" in info, "missing evidence_field in info"
    ef = info["evidence_field"]
    assert isinstance(ef, dict), f"evidence_field must be dict; got {type(ef)}"
    expected_axes = {
        "distance_to_target",
        "battery_survival_depth",
        "verification_depth",
        "exclusion_distance",
        "assumption_load",
        "computational_friction",
    }
    missing = expected_axes - set(ef.keys())
    assert not missing, f"evidence_field missing axes: {missing}"


def test_step_info_evidence_field_computational_friction_populated(small_env):
    """``EvidenceField.computational_friction`` carries the per-step
    telemetry verbatim.

    Confirms the Pre-Tier-0 0b telemetry wiring through Tier 3:
    elapsed_seconds + oracle_calls live on the EvidenceField axis,
    not just on the bare info dict.
    """
    env = small_env
    env.reset(seed=2029)
    _, _, _, _, info = env.step(0)
    cf = info["evidence_field"]["computational_friction"]
    assert cf["elapsed_seconds"] is not None
    assert cf["elapsed_seconds"] > 0, (
        f"computational_friction.elapsed_seconds must be > 0; "
        f"got {cf['elapsed_seconds']}"
    )
    assert cf["oracle_calls"] is not None
    assert cf["oracle_calls"] >= 1, (
        f"computational_friction.oracle_calls must be >= 1; "
        f"got {cf['oracle_calls']}"
    )
    # Same numeric values as the bare info keys (single source of truth).
    assert cf["elapsed_seconds"] == info["elapsed_seconds"]
    assert cf["oracle_calls"] == info["oracle_calls"]


def test_step_info_evidence_field_exclusion_distance_null(small_env):
    """``EvidenceField.exclusion_distance`` is NULL with an explanatory
    reason -- anti-fake-topology discipline (no chart+cert pair
    registered for cross-domain envs yet).

    Substrate v2.3 §8 architectural lock-in: no metric without chart.
    Cross-domain envs use ``coordinate_chart_id="provisional:..."`` to
    flag that a real chart is blocked on Charon coord (joint sprint
    T11). The reason_unpopulated string MUST mention either the
    missing chart or the missing certificate.
    """
    env = small_env
    env.reset(seed=2030)
    _, _, _, _, info = env.step(0)
    ed = info["evidence_field"]["exclusion_distance"]
    assert ed["value"] is None, (
        f"exclusion_distance.value must be NULL for cross-domain envs; "
        f"got {ed['value']}"
    )
    reason = ed.get("reason_unpopulated") or ""
    assert reason, "exclusion_distance.reason_unpopulated must be set"
    # Either the chart or the certificate must be flagged as missing.
    low = reason.lower()
    assert ("certificate" in low) or ("chart" in low), (
        f"reason_unpopulated must mention chart/certificate; got {reason!r}"
    )


def test_step_info_existing_keys_still_present(small_env):
    """Regression: pre-existing per-env info keys survive Tier 3 wiring.

    Tier 3 additions are purely additive; existing consumers of
    ``info["true_rank"]``, ``info["hit"]``, etc., must not break.
    """
    env = small_env
    env.reset(seed=2031)
    _, _, _, _, info = env.step(0)
    for key in (
        "true_rank", "predicted_rank", "hit", "label", "conductor",
        "running_accuracy", "n_episodes_seen", "binding_name",
        "elapsed_seconds", "oracle_calls",
    ):
        assert key in info, f"regression: pre-existing key {key} lost"
