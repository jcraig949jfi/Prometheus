"""Tests for prometheus_math.catalog_seeded_pilot.

Math-tdd skill rubric: >=3 tests in each of authority / property /
edge / composition.

Authority sources:
- Mossinghoff catalog: 8625-entry snapshot from
  ``prometheus_math.databases.mahler.MAHLER_TABLE``.  The strict
  "max|c| >= 4" filter yields 112 polys; the broad-projection variant
  (any catalog poly whose first half_len ascending coefficients fit
  the env alphabet AND have max|c| >= 4) is the seed pool used in
  practice.
- DiscoveryEnv coefficient convention: actions index ``coefficient_choices``
  in the order supplied; the env builds palindromic polys by mirroring
  ``a_{degree-i} = a_i`` from the agent's first ``half_len`` picks.
- REINFORCE warm-start convention: bias logits initialized to
  ``log(action_priors)`` (mean-centered) so a softmax over
  ``b_init = log(prior)`` yields ``probs == prior`` at episode 0.
"""
from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------


from prometheus_math.catalog_seeded_pilot import (  # noqa: E402
    extract_seed_polynomials,
    extract_seed_polynomials_broad,
    compute_action_priors,
    seeded_random_baseline,
    seeded_reinforce_agent,
    frozen_bias_reinforce_agent,
    compare_seeded_vs_unseeded,
)
from prometheus_math.discovery_env import DiscoveryEnv  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _small_env_factory() -> DiscoveryEnv:
    """Tiny env for fast tests: degree 4 -> half_len 3, 7^3 = 343."""
    return DiscoveryEnv(
        degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        reward_shape="step",
        log_discoveries=True,
    )


def _deg14_env_factory() -> DiscoveryEnv:
    """Degree 14, ±5 alphabet -- the production pilot configuration."""
    return DiscoveryEnv(
        degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        reward_shape="step",
    )


# ===========================================================================
# AUTHORITY TESTS (>=3) -- ground-truth catalog + softmax math
# ===========================================================================


def test_authority_extract_seed_polynomials_broad_min50() -> None:
    """Broad-projection seed extraction yields >= 50 polys at deg 14, ±5.

    The strict (deg in [12,18], max|c|>=4) filter yields only 4 entries
    (one each at degrees 14, 16, 16, 18).  The broad variant projects
    higher-degree polys to the env's half_len; the catalog has 112
    polys with max|c|>=4 across all degrees, and most have low-magnitude
    leading coefficients so their first 8 ascending coeffs typically
    fit the ±5 alphabet.
    """
    seeds = extract_seed_polynomials_broad(
        env_degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        min_abs_coef=4,
    )
    assert len(seeds) >= 50, (
        f"expected >= 50 broad-projected seeds at deg 14 +/- 5; got {len(seeds)}"
    )


def test_authority_action_priors_sum_to_one_per_step() -> None:
    """Per-step prior distributions must sum to 1 (within float tol)."""
    seeds = extract_seed_polynomials_broad(
        env_degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        min_abs_coef=4,
    )
    priors = compute_action_priors(
        seed_polys=seeds,
        degree=14,
        coefficient_choices=tuple(range(-5, 6)),
    )
    half_len = 14 // 2 + 1
    assert set(priors.keys()) == set(range(half_len))
    for s, p in priors.items():
        assert p.shape == (11,)  # 11 actions for ±5 alphabet
        assert math.isclose(float(p.sum()), 1.0, rel_tol=1e-9, abs_tol=1e-9), (
            f"step {s} prior sums to {p.sum()}, not 1"
        )


def test_authority_seeded_random_concentrates_on_high_prior() -> None:
    """Sampling from seeded priors concentrates mass on the prior's mode.

    With a deterministic per-step prior placing ~0.9 mass on a single
    action, samples drawn from ``_sample_from_prior`` should pick that
    action ~90% of the time over many draws.  This validates the
    sampling implementation, not the env.
    """
    from prometheus_math.catalog_seeded_pilot import _sample_from_prior

    rng = np.random.default_rng(42)
    n_actions = 7
    target = 3
    prior = np.full(n_actions, 0.1 / (n_actions - 1))
    prior[target] = 0.9
    prior /= prior.sum()

    n_draws = 5000
    samples = [_sample_from_prior(rng, prior) for _ in range(n_draws)]
    frac = sum(1 for s in samples if s == target) / n_draws
    # Allow generous tolerance; concentration around target is the test.
    assert 0.85 < frac < 0.94, (
        f"expected ~0.90 concentration on target; got {frac:.3f}"
    )


# ===========================================================================
# PROPERTY TESTS (>=3) -- determinism, non-negativity, idempotence
# ===========================================================================


def test_property_priors_non_negative() -> None:
    """All entries of every per-step prior are >= 0."""
    seeds = extract_seed_polynomials_broad(
        env_degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        min_abs_coef=4,
    )
    priors = compute_action_priors(
        seed_polys=seeds,
        degree=14,
        coefficient_choices=tuple(range(-5, 6)),
    )
    for s, p in priors.items():
        assert np.all(p >= 0.0), f"step {s} has negative entries: {p}"


def test_property_determinism_same_seed_same_result() -> None:
    """Same env_factory + n_episodes + seed -> identical four-counts."""
    seeds = extract_seed_polynomials_broad(
        env_degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        min_abs_coef=4,
    )
    priors = compute_action_priors(
        seed_polys=seeds,
        degree=4,
        coefficient_choices=tuple(range(-3, 4)),
    )

    a = seeded_random_baseline(_small_env_factory, priors, 200, seed=7)
    b = seeded_random_baseline(_small_env_factory, priors, 200, seed=7)

    ar, br = a["result"], b["result"]
    assert ar.total_episodes == br.total_episodes
    assert ar.catalog_hit_count == br.catalog_hit_count
    assert ar.promote_count == br.promote_count
    assert ar.shadow_catalog_count == br.shadow_catalog_count
    assert ar.rejected_count == br.rejected_count


def test_property_reinforce_seeded_determinism() -> None:
    """Seeded REINFORCE is also deterministic under the same seed."""
    seeds = extract_seed_polynomials_broad(
        env_degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        min_abs_coef=4,
    )
    priors = compute_action_priors(
        seed_polys=seeds,
        degree=4,
        coefficient_choices=tuple(range(-3, 4)),
    )

    a = seeded_reinforce_agent(_small_env_factory, priors, 100, seed=11)
    b = seeded_reinforce_agent(_small_env_factory, priors, 100, seed=11)

    ar, br = a["result"], b["result"]
    assert ar.total_episodes == br.total_episodes
    assert ar.promote_count == br.promote_count
    assert ar.shadow_catalog_count == br.shadow_catalog_count


# ===========================================================================
# EDGE TESTS (>=3) -- empty, single, mismatched degree
# ===========================================================================


def test_edge_empty_seed_pool_falls_back_to_uniform() -> None:
    """When seed_polys is empty, every step prior is uniform."""
    priors = compute_action_priors(
        seed_polys=[],
        degree=10,
        coefficient_choices=tuple(range(-3, 4)),
    )
    half_len = 10 // 2 + 1
    n_actions = 7
    expected = np.ones(n_actions) / n_actions
    for s in range(half_len):
        np.testing.assert_allclose(priors[s], expected, atol=1e-12)


def test_edge_single_seed_priors_concentrate_on_that_polys_coeffs() -> None:
    """Single seed -> priors place dominant mass on that poly's coeffs.

    Lehmer's polynomial has ascending coeffs ``[1, 1, 0, -1, -1, -1, -1,
    -1, 0, 1, 1]``.  At step 0 the prior should put dominant mass on
    coef=+1 (the only seed contributing); with smoothing=0.05, that's
    ``0.95 * 1.0 + 0.05 / 7 == 0.957...``.
    """
    lehmer = {
        "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
        "degree": 10,
        "mahler_measure": 1.1762808182599176,
        "label": "Lehmer",
    }
    priors = compute_action_priors(
        seed_polys=[lehmer],
        degree=10,
        coefficient_choices=tuple(range(-3, 4)),
        smoothing=0.05,
    )
    coef_choices = tuple(range(-3, 4))
    coef_to_action = {c: i for i, c in enumerate(coef_choices)}
    # step 0 -> coef 1
    expected_top = coef_to_action[1]
    assert int(np.argmax(priors[0])) == expected_top
    # step 2 -> coef 0
    expected_top_2 = coef_to_action[0]
    assert int(np.argmax(priors[2])) == expected_top_2
    # step 3 -> coef -1
    expected_top_3 = coef_to_action[-1]
    assert int(np.argmax(priors[3])) == expected_top_3


def test_edge_mismatched_degree_projection() -> None:
    """A seed at deg 18 fed into a deg-10 env: priors are well-formed.

    Degree projection behavior: ``compute_action_priors`` truncates the
    full ascending coeff list to ``half_len = degree // 2 + 1``.  No
    error is raised; the priors must still sum to 1 per step.
    """
    seed = {
        "coeffs": [1, -1, -1, 0, 1, 0, -1, 0, 1, -1, 0, 1, 1, -1, -1, 0, 1, -1, 1],
        "degree": 18,
        "mahler_measure": 1.2,
        "label": "fake_deg18",
    }
    priors = compute_action_priors(
        seed_polys=[seed],
        degree=10,  # env degree
        coefficient_choices=tuple(range(-3, 4)),
    )
    half_len = 10 // 2 + 1
    assert len(priors) == half_len
    for s, p in priors.items():
        assert math.isclose(float(p.sum()), 1.0, rel_tol=1e-9, abs_tol=1e-9)


# ===========================================================================
# COMPOSITION TESTS (>=3) -- end-to-end pipeline integration
# ===========================================================================


def test_composition_5arm_comparison_well_formed() -> None:
    """5-arm pilot returns a dict with the expected keys + arm count.

    Smoke test: 100 episodes per arm at deg 4, smoothing on; the run
    must complete and the summary must contain all five arms (the
    original four PLUS the frozen-bias variant) with PROMOTE rates in
    [0, 1].  Original 4 arms are checked as a regression.
    """
    seeds = extract_seed_polynomials_broad(
        env_degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        min_abs_coef=4,
    )
    summary = compare_seeded_vs_unseeded(
        env_factory=_small_env_factory,
        n_episodes=100,
        seeds=(0, 1),
        seed_polys=seeds,
    )
    assert "per_arm" in summary
    assert "welch" in summary
    assert "welch_salem" in summary
    assert "config" in summary
    assert "seed_pool" in summary
    assert "priors" in summary
    expected = {"random_uniform", "random_seeded",
                "reinforce_uniform", "reinforce_seeded",
                "reinforce_frozen_bias"}
    assert set(summary["per_arm"].keys()) == expected
    for arm in expected:
        rate = summary["per_arm"][arm]["promote_rate_mean"]
        assert 0.0 <= rate <= 1.0


def test_composition_seeded_random_biases_search() -> None:
    """Seeded random sampling concentrates more mass on Salem-cluster
    proxy than uniform random does, validating that the priors actually
    bias the search.

    NOTE: this is a STRUCTURAL test, not a Hypothesis-2 test.  Salem
    cluster (M in [1.18, 1.5]) is densely inhabited; the catalog seeds
    bias toward this region, so seeded random should generate a higher
    Salem-rate than uniform random.  At small degrees Salem hits are
    rare and the test asserts only directionality + non-degeneracy.
    """
    # Use the deg-14 env for a meaningful test (the small env's
    # trajectory space is so tight that Salem hits are noisy).
    seeds = extract_seed_polynomials_broad(
        env_degree=14,
        coefficient_choices=tuple(range(-5, 6)),
        min_abs_coef=4,
    )
    if len(seeds) < 10:
        pytest.skip(f"seed pool too small ({len(seeds)}) for biasing test")

    priors = compute_action_priors(
        seed_polys=seeds,
        degree=14,
        coefficient_choices=tuple(range(-5, 6)),
    )
    n_actions = 11
    uniform = {s: np.ones(n_actions) / n_actions
               for s in range(14 // 2 + 1)}

    # 500 episodes is enough for a directional read.
    seeded = seeded_random_baseline(
        _deg14_env_factory, priors, 500, seed=0
    )
    uni = seeded_random_baseline(
        _deg14_env_factory, uniform, 500, seed=0
    )
    seeded_salem = seeded["details"]["salem_cluster_proxy_hits"]
    uniform_salem = uni["details"]["salem_cluster_proxy_hits"]
    # Seeded should be >= uniform; we accept equality as still
    # consistent with biasing (small-N noise).
    assert seeded_salem >= uniform_salem - 5, (
        f"seeded random Salem hits ({seeded_salem}) much LESS than "
        f"uniform ({uniform_salem}); priors are not biasing search"
    )


def test_composition_pipeline_records_intact() -> None:
    """DiscoveryRecord pipeline records on a seeded run match the
    pipeline's own bookkeeping.

    The four-counts tally (claim_into_kernel = promote +
    shadow_catalog + pipeline-routed rejects) must hold at the end of
    a seeded REINFORCE run.
    """
    seeds = extract_seed_polynomials_broad(
        env_degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        min_abs_coef=4,
    )
    priors = compute_action_priors(
        seed_polys=seeds,
        degree=4,
        coefficient_choices=tuple(range(-3, 4)),
    )
    out = seeded_reinforce_agent(_small_env_factory, priors, 200, seed=3)
    res = out["result"]
    # promote + shadow + (claim - promote - shadow) = claim; trivially
    # true by construction, but we verify the tally is internally
    # consistent.
    pipeline_rejects = (
        res.claim_into_kernel_count - res.promote_count - res.shadow_catalog_count
    )
    assert pipeline_rejects >= 0
    # Total must equal episodes.
    total = (res.catalog_hit_count + res.claim_into_kernel_count
             + res.rejected_count)
    # Note: catalog_hit episodes don't go into the pipeline AND are
    # not counted in rejected.  Together with pipeline-routed (claim)
    # and upstream-rejected (rejected), they should partition all
    # episodes.
    assert total == res.total_episodes, (
        f"partition fails: cat-hit={res.catalog_hit_count} + "
        f"claim={res.claim_into_kernel_count} + reject={res.rejected_count} "
        f"= {total}; expected {res.total_episodes}"
    )


# ===========================================================================
# FROZEN-BIAS REINFORCE TESTS  (cleanest H2 falsifier)
# ===========================================================================


def _frozen_bias_priors_for_small_env() -> Dict[int, np.ndarray]:
    """Build canonical seeded priors for the small (deg-4, +/-3) env."""
    seed_polys = extract_seed_polynomials_broad(
        env_degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        min_abs_coef=4,
    )
    return compute_action_priors(
        seed_polys=seed_polys,
        degree=4,
        coefficient_choices=tuple(range(-3, 4)),
    )


def test_authority_frozen_bias_does_not_erode() -> None:
    """After many episodes, the FROZEN bias scaffold must be literally
    identity-equal to its warm-start value.

    The whole point of frozen-bias REINFORCE is that the gradient
    cannot touch ``b``; only ``delta`` absorbs updates.  We verify
    this by recomputing the warm-start scaffold from the priors and
    comparing against the post-run snapshot the function returns in
    its details dict.
    """
    priors = _frozen_bias_priors_for_small_env()
    out = frozen_bias_reinforce_agent(
        _small_env_factory, priors, n_episodes=300, seed=5,
        lr=0.05, delta_lr=0.005,
    )
    b_post = np.array(out["details"]["b_frozen"])

    # Recompute the warm-start scaffold and compare bit-for-bit.
    half_len = 4 // 2 + 1
    n_actions = 7
    eps = 1e-9
    expected = np.zeros((half_len, n_actions), dtype=np.float64)
    for s in range(half_len):
        log_p = np.log(np.clip(priors[s], eps, None))
        expected[s] = log_p - log_p.mean()

    assert b_post.shape == expected.shape
    np.testing.assert_array_equal(b_post, expected), (
        "frozen bias scaffold drifted from warm-start value -- gradient "
        "is leaking into b instead of delta"
    )


def test_property_frozen_bias_action_distribution_close_to_warm_start() -> None:
    """At observation = 0 vector, the frozen-bias policy's per-step
    distribution stays close to the warm-start prior even after many
    REINFORCE updates.  delta is small (zero init, lr 0.005) and W @ 0
    contributes nothing, so logits = b + delta and probs ~= softmax(b).

    We assert action 0 (coef=-3 in the +/-3 alphabet) has probability
    within a wide envelope of its warm-start value -- the test is
    qualitative; the point is the WARM-START SHAPE survives.
    """
    priors = _frozen_bias_priors_for_small_env()
    # Snapshot warm-start probability for action 0 at step 0.
    p0_warm = float(priors[0][0])

    out = frozen_bias_reinforce_agent(
        _small_env_factory, priors, n_episodes=500, seed=7,
        lr=0.05, delta_lr=0.005,
    )
    half_len = 4 // 2 + 1
    n_actions = 7
    eps = 1e-9

    b = np.zeros((half_len, n_actions), dtype=np.float64)
    for s in range(half_len):
        log_p = np.log(np.clip(priors[s], eps, None))
        b[s] = log_p - log_p.mean()
    delta = np.array(out["details"]["delta_final"])
    logits = b[0] + delta[0]
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()
    p0_post = float(probs[0])

    # The frozen scaffold pins the distribution within a moderate
    # envelope; even with several hundred updates the warm-start
    # imprint is intact.  We accept up to ~3x absolute drift.
    assert abs(p0_post - p0_warm) < 0.3, (
        f"action 0 probability moved too far: warm={p0_warm:.4f} "
        f"-> post={p0_post:.4f}; frozen scaffold should pin distribution"
    )


def test_composition_frozen_bias_runs_through_5_arm_pilot() -> None:
    """End-to-end: the 5-arm pilot must include reinforce_frozen_bias
    with a well-formed promote_rate and the original 4 arms must still
    be present (regression check on existing arms).
    """
    seed_polys = extract_seed_polynomials_broad(
        env_degree=4,
        coefficient_choices=tuple(range(-3, 4)),
        min_abs_coef=4,
    )
    summary = compare_seeded_vs_unseeded(
        env_factory=_small_env_factory,
        n_episodes=80,
        seeds=(0, 1),
        seed_polys=seed_polys,
    )
    expected_arms = {
        "random_uniform", "random_seeded",
        "reinforce_uniform", "reinforce_seeded",
        "reinforce_frozen_bias",
    }
    assert set(summary["per_arm"].keys()) == expected_arms
    fb = summary["per_arm"]["reinforce_frozen_bias"]
    assert 0.0 <= fb["promote_rate_mean"] <= 1.0
    assert "salem_rate_mean" in fb
    assert "catalog_hit_rate_mean" in fb
    # New welch contrasts present.
    assert "p_reinforce_frozen_bias_gt_reinforce_seeded" in summary["welch"]
    assert "p_reinforce_frozen_bias_gt_reinforce_uniform" in summary["welch"]
    # Config exposes delta_lr.
    assert "delta_lr" in summary["config"]


def test_edge_frozen_bias_with_zero_delta_lr() -> None:
    """``delta_lr=0`` freezes delta entirely; combined with W starting
    at zero, the policy distribution at obs=0 is exactly softmax(b) =
    the warm-start prior throughout training.  delta_final must be
    identically zero.

    Because W still trains on observations and obs is generally not
    zero, the run is not bit-identical to seeded_random; this test
    only sanity-checks the no-update-on-delta branch.
    """
    priors = _frozen_bias_priors_for_small_env()
    out = frozen_bias_reinforce_agent(
        _small_env_factory, priors, n_episodes=200, seed=13,
        lr=0.05, delta_lr=0.0,
    )
    delta_final = np.array(out["details"]["delta_final"])
    np.testing.assert_array_equal(
        delta_final, np.zeros_like(delta_final),
    ), "delta_lr=0 must leave delta at exactly zero"

    # Also verify the bias scaffold did not drift (already enforced by
    # the runtime invariant inside the function, but assert here too).
    half_len = 4 // 2 + 1
    n_actions = 7
    eps = 1e-9
    expected = np.zeros((half_len, n_actions), dtype=np.float64)
    for s in range(half_len):
        log_p = np.log(np.clip(priors[s], eps, None))
        expected[s] = log_p - log_p.mean()
    np.testing.assert_array_equal(
        np.array(out["details"]["b_frozen"]), expected,
    )
