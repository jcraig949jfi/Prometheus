"""Tests for prometheus_math.kill_vector_navigator (Day 5 of the kill-space pivot).

The navigator is the substrate's first explicit policy primitive: a
two-mode operator-ranker that uses margin-space (squashed-L2) magnitudes
when native KillVector data is available, and falls back to categorical
triggered counts otherwise.

Math-tdd skill rubric: ≥3 each in authority/property/edge/composition.

Authority (≥3):
  * For the canonical native-pilot region (deg14 ±5 step DiscoveryEnv),
    margin mode ranks PPO first.
  * Categorical mode on the same region is approximately indifferent.
  * Both modes agree on the *coverage* (same set of operators) but
    differ on the *spread* of expected magnitudes.

Property (≥3):
  * Determinism: same seed -> same recommendations bit-for-bit.
  * Recommendation order is stable across repeated calls.
  * Bootstrap CI has non-negative width and contains the point estimate.

Edge (≥3):
  * Empty navigator -> empty recommendations.
  * Single-operator region -> returns the only one with a confidence note.
  * mode="margin" with no margin data -> returns nothing (per the spec
    that margin-mode-only returns nothing on margin-less regions).

Composition (≥3):
  * Full pipeline (load both data sources -> navigator -> recommend ->
    calibration) end-to-end.
  * Calibration table is well-formed (rows have all required keys).
  * Cross-mode consistency check produces a meaningful comparison
    (margin and categorical rankings exist on the same operator set
    when both modes are present).
"""
from __future__ import annotations

import os

import pytest

from prometheus_math.kill_vector_navigator import (
    DEFAULT_BOOTSTRAP_RESAMPLES,
    KillVectorNavigator,
    OperatorRecommendation,
    PROMETHEUS_MATH_DIR,
    _RegionStats,
    _bootstrap_mean_ci,
    _kendall_tau,
    _native_pilot_to_region_stats,
    _legacy_archaeology_to_region_stats,
    _merge_region_stats,
    _region_id_from_meta,
    _region_meta_from_id,
)


# ---------------------------------------------------------------------------
# Module-scoped fixture: load the real production data once for all tests
# that need to verify the canonical PPO-first ranking. Bootstrap resamples
# are kept low so the test suite stays fast.
# ---------------------------------------------------------------------------


_NATIVE_PILOT_PATH = os.path.join(
    PROMETHEUS_MATH_DIR, "_native_kill_vector_pilot.json"
)
_LEGACY_ARCHAEOLOGY_PATH = os.path.join(
    PROMETHEUS_MATH_DIR, "_gradient_archaeology_results.json"
)


_HAS_NATIVE = os.path.exists(_NATIVE_PILOT_PATH)
_HAS_LEGACY = os.path.exists(_LEGACY_ARCHAEOLOGY_PATH)


# Region id used by the native pilot (deg14, alphabet width 5, reward=step,
# DiscoveryEnv -- the V1 env carrying random_uniform/reinforce_linear/
# ppo_mlp).
NATIVE_PILOT_REGION = "DiscoveryEnv|deg14|w5|step"


@pytest.fixture(scope="module")
def production_navigator() -> KillVectorNavigator:
    """The full navigator built from real artifacts.  Skipped when the
    production data isn't on disk (CI mirrors)."""
    if not (_HAS_NATIVE or _HAS_LEGACY):
        pytest.skip("no production artifacts present")
    return KillVectorNavigator.from_data(
        bootstrap_resamples=50,  # fast for tests
        seed=0,
    )


# ---------------------------------------------------------------------------
# Synthetic fixtures (no production data dependency)
# ---------------------------------------------------------------------------


def _synth_region_stats() -> dict:
    """A synthetic 2-region universe.

    Region "A" has BOTH margin and categorical data with 3 operators
    (Op_PPO is best in margin, all are equal in categorical).
    Region "B" has categorical-only data with 2 operators.
    """
    region_a = _RegionStats(
        region="DiscoveryEnv|deg14|w5|step",
        region_meta={
            "env": "DiscoveryEnv", "degree": 14,
            "alphabet_width": 5, "reward_shape": "step",
        },
        margin_samples={
            "Op_PPO": [0.30] * 200 + [0.40] * 200,  # mean ~ 0.35
            "Op_RAND": [0.85] * 200 + [0.83] * 200,  # mean ~ 0.84
            "Op_REINFORCE": [0.86] * 200 + [0.86] * 200,  # mean ~ 0.86
        },
        categorical_samples={
            "Op_PPO": [1.0] * 400,
            "Op_RAND": [1.0] * 400,
            "Op_REINFORCE": [1.0] * 400,
        },
        has_margin_data=True,
        has_categorical_data=True,
    )
    region_b = _RegionStats(
        region="four_counts|deg10|w5|step",
        region_meta={
            "env": "four_counts", "degree": 10,
            "alphabet_width": 5, "reward_shape": "step",
        },
        margin_samples={},
        categorical_samples={
            "Op_PPO": [1.0] * 200,
            "Op_RAND": [1.0] * 300,
        },
        has_margin_data=False,
        has_categorical_data=True,
    )
    return {region_a.region: region_a, region_b.region: region_b}


@pytest.fixture
def synth_navigator() -> KillVectorNavigator:
    return KillVectorNavigator.from_region_stats(
        _synth_region_stats(),
        bootstrap_resamples=50,
        seed=0,
    )


# ---------------------------------------------------------------------------
# AUTHORITY TESTS (>=3): the navigator's externally-checkable claims
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_NATIVE, reason="native pilot data not present")
def test_authority_margin_mode_ranks_ppo_first(production_navigator):
    """The native pilot's headline finding: in margin space, PPO is the
    operator that gets closest to the band on the deg14 +/-5 step env.

    Mean margins from the pilot meta: PPO=1.08, GA_elitist=3.19,
    random=5.58, REINFORCE=6.69.  Squashed via the unit-aware [0,1]
    map, PPO's expected magnitude is materially smaller than the
    others'."""
    recs = production_navigator.recommend(
        NATIVE_PILOT_REGION, mode="margin", top_k=5,
    )
    assert recs, "expected non-empty margin recommendations on the native region"
    # PPO must be top-1.
    assert recs[0].operator_class == "ppo_mlp", (
        f"expected ppo_mlp first; got order "
        f"{[r.operator_class for r in recs]}"
    )
    # PPO's expected magnitude is materially below the others'.
    others = [r.expected_magnitude for r in recs[1:]]
    assert all(recs[0].expected_magnitude < o for o in others), (
        f"PPO not strictly best: {recs[0].expected_magnitude} vs {others}"
    )


@pytest.mark.skipif(not _HAS_NATIVE, reason="native pilot data not present")
def test_authority_categorical_mode_is_approximately_indifferent(
    production_navigator,
):
    """In categorical mode the same region produces ~indifferent
    rankings: all operators saturate at triggered_count ~= 1.0 because
    the dominant ``out_of_band`` failure mode kills nearly every
    candidate.

    The spread of expected_magnitude across operators is < 0.01 in
    categorical, vs > 0.4 in margin mode."""
    cat = production_navigator.recommend(
        NATIVE_PILOT_REGION, mode="categorical", top_k=10,
    )
    margin = production_navigator.recommend(
        NATIVE_PILOT_REGION, mode="margin", top_k=10,
    )
    assert cat and margin, "both modes should have data on the native region"
    cat_spread = (
        max(r.expected_magnitude for r in cat)
        - min(r.expected_magnitude for r in cat)
    )
    margin_spread = (
        max(r.expected_magnitude for r in margin)
        - min(r.expected_magnitude for r in margin)
    )
    assert cat_spread < 0.01, f"categorical spread too large: {cat_spread}"
    assert margin_spread > 0.4, f"margin spread too small: {margin_spread}"
    # And the spread ratio is the headline signal.
    assert margin_spread > 30 * max(cat_spread, 1e-12)


@pytest.mark.skipif(not _HAS_NATIVE, reason="native pilot data not present")
def test_authority_modes_share_operator_coverage_on_native_region(
    production_navigator,
):
    """Both modes should be defined on the same set of operators within
    the native-data region (the per-episode KillVector contributes both
    margin and categorical samples).  The rankings disagree on
    *spread*, but not on *which operators are present*."""
    margin = production_navigator.recommend(
        NATIVE_PILOT_REGION, mode="margin", top_k=10,
    )
    cat = production_navigator.recommend(
        NATIVE_PILOT_REGION, mode="categorical", top_k=10,
    )
    assert {r.operator_class for r in margin} == {r.operator_class for r in cat}


# ---------------------------------------------------------------------------
# PROPERTY TESTS (>=3)
# ---------------------------------------------------------------------------


def test_property_determinism_under_fixed_seed(synth_navigator):
    """Same data + same seed -> bit-identical recommendations."""
    nav2 = KillVectorNavigator.from_region_stats(
        _synth_region_stats(),
        bootstrap_resamples=50,
        seed=0,
    )
    r1 = synth_navigator.recommend(
        "DiscoveryEnv|deg14|w5|step", mode="margin", top_k=10,
    )
    r2 = nav2.recommend(
        "DiscoveryEnv|deg14|w5|step", mode="margin", top_k=10,
    )
    assert [r.as_dict() for r in r1] == [r.as_dict() for r in r2]


def test_property_recommendation_order_is_stable(synth_navigator):
    """Repeated calls return the same ordering."""
    region = "DiscoveryEnv|deg14|w5|step"
    orderings = [
        [r.operator_class for r in synth_navigator.recommend(
            region, mode="margin", top_k=10,
        )]
        for _ in range(5)
    ]
    for o in orderings[1:]:
        assert o == orderings[0]


def test_property_ci_well_formed_and_contains_point_estimate(synth_navigator):
    """Each recommendation's CI must satisfy ci_low <= mean <= ci_high
    and have non-negative width.  This is the contract downstream
    consumers rely on for confidence-aware sampling."""
    for region in synth_navigator.regions:
        for mode in ("margin", "categorical"):
            recs = synth_navigator.recommend(
                region, mode=mode, top_k=10, min_episodes=0,
            )
            for r in recs:
                assert r.ci_low <= r.expected_magnitude <= r.ci_high, (
                    f"CI violation on {region}/{mode}/{r.operator_class}: "
                    f"low={r.ci_low}, mean={r.expected_magnitude}, "
                    f"high={r.ci_high}"
                )
                assert r.ci_high - r.ci_low >= 0.0


def test_property_bootstrap_helper_is_deterministic_with_supplied_rng():
    """Hardening: ``_bootstrap_mean_ci`` is deterministic with an
    explicit RNG; the navigator's determinism property leans on this."""
    import random as _r
    samples = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    a = _bootstrap_mean_ci(samples, resamples=100, rng=_r.Random(42))
    b = _bootstrap_mean_ci(samples, resamples=100, rng=_r.Random(42))
    assert a == b


# ---------------------------------------------------------------------------
# EDGE TESTS (>=3)
# ---------------------------------------------------------------------------


def test_edge_empty_navigator_returns_empty_recommendations():
    nav = KillVectorNavigator.from_region_stats(
        {}, bootstrap_resamples=10, seed=0,
    )
    assert nav.regions == []
    assert nav.recommend("anything", mode="auto") == []
    assert nav.recommend("anything", mode="margin") == []
    assert nav.recommend("anything", mode="categorical") == []
    s = nav.summary()
    assert s["n_regions"] == 0
    assert s["regions"] == []


def test_edge_single_operator_region_carries_confidence_note():
    """When a region has only one operator, the recommendation surfaces
    a note that the comparison is undefined (no peers to rank against).
    """
    only_one = {
        "DiscoveryEnvV2|deg14|w5|step": _RegionStats(
            region="DiscoveryEnvV2|deg14|w5|step",
            region_meta={"env": "DiscoveryEnvV2", "degree": 14},
            margin_samples={"ga_elitist_v2": [0.7] * 200},
            categorical_samples={"ga_elitist_v2": [1.0] * 200},
            has_margin_data=True,
            has_categorical_data=True,
        ),
    }
    nav = KillVectorNavigator.from_region_stats(
        only_one, bootstrap_resamples=20, seed=0,
    )
    recs = nav.recommend(
        "DiscoveryEnvV2|deg14|w5|step", mode="margin", top_k=5,
    )
    assert len(recs) == 1
    assert recs[0].operator_class == "ga_elitist_v2"
    assert "single operator" in recs[0].notes.lower()


def test_edge_margin_mode_returns_nothing_when_no_margin_data():
    """Per the spec, mode='margin' on a region whose only data is
    categorical must return [] (no fallback -- callers asked for
    margin specifically)."""
    cat_only = {
        "four_counts|deg10|w5|step": _RegionStats(
            region="four_counts|deg10|w5|step",
            region_meta={"env": "four_counts"},
            margin_samples={},
            categorical_samples={"OP_X": [1.0] * 500, "OP_Y": [1.0] * 500},
            has_margin_data=False,
            has_categorical_data=True,
        ),
    }
    nav = KillVectorNavigator.from_region_stats(
        cat_only, bootstrap_resamples=10, seed=0,
    )
    # margin mode: empty
    margin = nav.recommend(
        "four_counts|deg10|w5|step", mode="margin", top_k=5,
    )
    assert margin == []
    # auto mode: falls back to categorical
    auto = nav.recommend(
        "four_counts|deg10|w5|step", mode="auto", top_k=5,
    )
    assert auto and all(r.mode == "categorical" for r in auto)


def test_edge_unknown_region_returns_empty():
    nav = KillVectorNavigator.from_region_stats(
        _synth_region_stats(), bootstrap_resamples=10, seed=0,
    )
    assert nav.recommend("not|a|real|region", mode="auto") == []


def test_edge_min_episodes_filters_thin_cells():
    sparse = {
        "R": _RegionStats(
            region="R", region_meta={},
            margin_samples={"thin": [0.1] * 5, "fat": [0.5] * 500},
            categorical_samples={},
            has_margin_data=True,
        ),
    }
    nav = KillVectorNavigator.from_region_stats(
        sparse, bootstrap_resamples=10, seed=0,
    )
    recs = nav.recommend("R", mode="margin", top_k=5, min_episodes=100)
    assert {r.operator_class for r in recs} == {"fat"}


# ---------------------------------------------------------------------------
# COMPOSITION TESTS (>=3): pipeline-level checks
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_NATIVE, reason="native pilot data not present")
def test_composition_full_pipeline_load_recommend_calibrate(
    production_navigator,
):
    """End-to-end: from_data -> summary -> per-region recommend ->
    calibration.  All steps return well-shaped artifacts."""
    nav = production_navigator
    s = nav.summary()
    assert s["n_regions"] >= 1
    assert s["n_with_margin"] >= 1
    assert any("native" in src for src in s["sources_loaded"]) or any(
        "kill_vector_pilot" in src for src in s["sources_loaded"]
    )
    # Every region's recommend(mode='auto') returns either margin or
    # categorical (never an undefined mode).
    for region in nav.regions:
        recs = nav.recommend(region, mode="auto", top_k=5)
        for r in recs:
            assert r.mode in ("margin", "categorical")
    cal = nav.calibration()
    assert cal["n_eligible_regions"] >= 1
    for row in cal["rows"]:
        for k in (
            "region", "margin_top1", "categorical_top1",
            "agree_top1", "kendall_tau", "n_common_operators",
            "margin_ranking", "categorical_ranking",
        ):
            assert k in row, f"missing key {k} in calibration row"


def test_composition_policy_for_region_well_formed(synth_navigator):
    """policy_for_region returns the full table dump with both modes,
    region meta, and the boolean availability flags."""
    pol = synth_navigator.policy_for_region(
        "DiscoveryEnv|deg14|w5|step",
    )
    assert pol["region"] == "DiscoveryEnv|deg14|w5|step"
    assert pol["has_margin_data"] is True
    assert pol["has_categorical_data"] is True
    assert len(pol["margin"]) >= 1
    assert len(pol["categorical"]) >= 1
    # margin recs should be ordered ascending by expected_magnitude
    margins = [m["expected_magnitude"] for m in pol["margin"]]
    assert margins == sorted(margins)


def test_composition_calibration_meaningful_when_modes_diverge(synth_navigator):
    """In the synthetic universe, margin mode separates Op_PPO from the
    rest (mean ~0.35 vs ~0.84/0.86) while categorical is exactly tied
    at 1.0.  The calibration row must report a meaningful margin
    ranking distinct from the categorical (tied) ranking.

    We check: the margin top1 is Op_PPO; the categorical-mode rankings
    are tied (so the ordering is name-sorted; first by deterministic
    tie-break)."""
    cal = synth_navigator.calibration()
    rows_by_region = {row["region"]: row for row in cal["rows"]}
    row = rows_by_region["DiscoveryEnv|deg14|w5|step"]
    assert row["margin_top1"] == "Op_PPO"
    # Margin ranking puts PPO first, then the others by name-sort.
    assert row["margin_ranking"][0] == "Op_PPO"
    # Categorical ranking is tied -> sort by name (deterministic).
    assert row["categorical_ranking"] == sorted(row["categorical_ranking"])


def test_composition_loaders_extract_known_structure():
    """Smoke-test the two loaders with hand-crafted minimal dicts so we
    don't depend on real production data."""
    pilot = {
        "episodes": [
            {
                "algorithm": "ppo_mlp",
                "kill_vector": {
                    "components": [
                        {"falsifier_name": "out_of_band", "triggered": True,
                         "margin": 0.5, "margin_unit": "absolute",
                         "metadata": {}},
                    ],
                    "candidate_hash": "deadbeef",
                    "operator_class": "ppo_mlp@seed=0",
                    "region_meta": {
                        "env": "DiscoveryEnv", "degree": 14,
                        "alphabet_width": 5, "reward_shape": "step",
                    },
                    "timestamp": 0.0,
                },
            },
        ],
    }
    arch = {
        "per_region_disaggregation": {
            "regions": {
                "four_counts|deg10|w5|step": {
                    "operator_kill_table": {
                        "OP_X|upstream:functional": 5,
                        "OP_Y|upstream:functional": 3,
                    },
                },
            },
        },
    }
    n = _native_pilot_to_region_stats(pilot)
    a = _legacy_archaeology_to_region_stats(arch)
    assert "DiscoveryEnv|deg14|w5|step" in n
    assert "four_counts|deg10|w5|step" in a
    assert n["DiscoveryEnv|deg14|w5|step"].has_margin_data
    assert a["four_counts|deg10|w5|step"].has_categorical_data
    merged = _merge_region_stats(n, a)
    assert set(merged.keys()) == {
        "DiscoveryEnv|deg14|w5|step",
        "four_counts|deg10|w5|step",
    }


# ---------------------------------------------------------------------------
# Helper unit tests
# ---------------------------------------------------------------------------


def test_helper_region_id_round_trip():
    meta = {
        "env": "DiscoveryEnv", "degree": 14,
        "alphabet_width": 5, "reward_shape": "step",
    }
    rid = _region_id_from_meta(meta)
    parsed = _region_meta_from_id(rid)
    assert parsed["env"] == "DiscoveryEnv"
    assert parsed["degree"] == 14
    assert parsed["alphabet_width"] == 5
    assert parsed["reward_shape"] == "step"


def test_helper_kendall_tau_basics():
    a = ["X", "Y", "Z"]
    b = ["X", "Y", "Z"]
    assert _kendall_tau(a, b) == pytest.approx(1.0)
    c = ["Z", "Y", "X"]
    assert _kendall_tau(a, c) == pytest.approx(-1.0)
    # No overlap -> 0
    assert _kendall_tau(["P"], ["Q"]) == 0.0
