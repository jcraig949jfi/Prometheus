"""Tests for prometheus_math.withheld_benchmark (§6.2.5 of
discovery_via_rediscovery.md).

The withheld-rediscovery benchmark partitions Mossinghoff's snapshot
into visible (catalog) + withheld (held-out 'unknown' targets), runs
the discovery agent, and counts how many withheld entries get
rediscovered + how many survive the full pipeline. It's the stage-2
validation ladder Aporia/ChatGPT spec'd before the open-discovery pilot.

Math-tdd skill: ≥3 tests in each of authority/property/edge/composition.
"""
from __future__ import annotations

import math

import pytest

from prometheus_math.databases.mahler import MAHLER_TABLE
from prometheus_math.withheld_benchmark import (
    WithheldDiscoveryPipeline,
    WithheldPartition,
    WithheldResult,
    partition_mossinghoff,
    run_withheld_pilot,
)


# ---------------------------------------------------------------------------
# Authority
# ---------------------------------------------------------------------------


def test_authority_default_partition_size_against_mossinghoff_snapshot():
    """With holdout_fraction=0.2 and seed=42 the partition produces
    142 visible + 36 withheld (or floor/ceil-equivalent counts that
    sum to len(MAHLER_TABLE)=178).

    Reference: prometheus_math.databases._mahler_data.MAHLER_TABLE is
    the embedded snapshot of Michael Mossinghoff's small-Mahler tables
    (178 entries; cross-checked against techne.lib.mahler_measure at
    import time to better than 1e-9 per entry).
    """
    n = len(MAHLER_TABLE)
    assert n == 178, f"snapshot drifted: expected 178, got {n}"
    p = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    # Round-to-nearest: 178 * 0.2 = 35.6 -> 36 withheld, 142 visible.
    assert p.n_withheld + p.n_visible == n
    assert p.n_withheld == 36
    assert p.n_visible == 142


def test_authority_visible_and_withheld_disjoint_and_cover_full_snapshot():
    """The visible set + the withheld set form a partition (disjoint
    sets whose union = MAHLER_TABLE, up to coefficient identity).

    Reference: Mossinghoff snapshot. A rediscovery benchmark that
    leaks entries between visible and withheld is structurally
    invalid — the agent could 'rediscover' a withheld entry by
    matching a visible one.
    """
    p = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    visible_keys = {tuple(coeffs) for coeffs, _ in p.visible_set}
    withheld_keys = {tuple(coeffs) for coeffs, _ in p.withheld_set}
    assert visible_keys.isdisjoint(withheld_keys)
    union = visible_keys | withheld_keys
    table_keys = {tuple(e["coeffs"]) for e in MAHLER_TABLE}
    assert union == table_keys


def test_authority_tiny_corpus_matches_holdout_fraction():
    """A 5-entry corpus with holdout_fraction=0.4 yields 3 visible + 2
    withheld (round(5*0.4)=2). Hand-verified by direct multiplication.

    Reference: deterministic floor/round behavior — required for
    reproducibility audit.
    """
    tiny_corpus = [
        ([1, 1], 1.0),
        ([1, -1], 1.0),
        ([1, 0, 1], 1.0),
        ([1, 1, 1], 1.0),
        ([1, -1, 1], 1.0),
    ]
    p = partition_mossinghoff(
        holdout_fraction=0.4, seed=42, _corpus=tiny_corpus
    )
    assert p.n_visible == 3
    assert p.n_withheld == 2


def test_authority_withheld_pipeline_treats_withheld_as_catalog_miss():
    """A polynomial whose M matches a withheld entry should get
    catalog_miss=True from the patched check; a polynomial matching a
    visible entry should get catalog_miss=False.

    Reference: §6.2.5 spec — 'monkey-patched to return catalog_miss=True
    for any polynomial whose M matches a withheld entry'.
    """
    # Construct a deterministic 2-entry partition: 1 visible, 1 withheld.
    visible_entry = ([1, 1], 1.0)
    # Use Lehmer's M as the withheld target.
    withheld_entry = ([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], 1.1762808182599176)
    partition = WithheldPartition(
        visible_set=[visible_entry],
        withheld_set=[withheld_entry],
        partition_seed=0,
        n_visible=1,
        n_withheld=1,
    )

    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension

    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    pipeline = WithheldDiscoveryPipeline(kernel=k, ext=ext, partition=partition)

    # The withheld pipeline's catalog check should declare
    # catalog_miss=True for the withheld M (1.176).
    catalog_miss_w, rationale_w, _ = pipeline._withheld_catalog_check(
        withheld_entry[0], withheld_entry[1]
    )
    assert catalog_miss_w is True, rationale_w

    # And catalog_miss=False for the visible M (1.0).
    catalog_miss_v, rationale_v, _ = pipeline._withheld_catalog_check(
        visible_entry[0], visible_entry[1]
    )
    assert catalog_miss_v is False, rationale_v


# ---------------------------------------------------------------------------
# Property
# ---------------------------------------------------------------------------


def test_property_partition_is_seed_deterministic():
    """Same seed -> same partition (set equality of withheld coeffs)."""
    p1 = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    p2 = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    w1 = {tuple(c) for c, _ in p1.withheld_set}
    w2 = {tuple(c) for c, _ in p2.withheld_set}
    assert w1 == w2


def test_property_different_seeds_yield_different_partitions():
    """seed=42 and seed=43 produce DIFFERENT withheld sets (almost
    surely, given 178-choose-36 is huge)."""
    p_a = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    p_b = partition_mossinghoff(holdout_fraction=0.2, seed=43)
    w_a = {tuple(c) for c, _ in p_a.withheld_set}
    w_b = {tuple(c) for c, _ in p_b.withheld_set}
    assert w_a != w_b


def test_property_rediscovery_rate_in_unit_interval():
    """For any pilot run, withheld_rediscovery_rate in [0, 1] and
    withheld_PROMOTE_rate in [0, 1]."""
    partition = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    result = run_withheld_pilot(
        partition,
        n_episodes=20,
        seeds=(0,),
        agent="reinforce",
    )
    assert 0.0 <= result.withheld_rediscovery_rate <= 1.0
    assert 0.0 <= result.withheld_PROMOTE_rate <= 1.0


def test_property_promote_count_le_rediscovery_count():
    """The agent can't promote more withheld entries than it
    rediscovered (PROMOTE is downstream of rediscovery)."""
    partition = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    result = run_withheld_pilot(
        partition,
        n_episodes=15,
        seeds=(0,),
        agent="reinforce",
    )
    assert result.withheld_PROMOTE_count <= result.withheld_rediscovery_count


def test_property_zero_holdout_means_empty_withheld():
    """holdout_fraction=0 -> empty withheld set (well-defined edge)."""
    p = partition_mossinghoff(holdout_fraction=0.0, seed=42)
    assert p.n_withheld == 0
    assert p.n_visible == len(MAHLER_TABLE)


# ---------------------------------------------------------------------------
# Edge
# ---------------------------------------------------------------------------


def test_edge_zero_holdout_pilot_returns_zero_rate():
    """holdout=0 -> no withheld entries -> rediscovery rate is NaN
    (zero divided by zero) or zero by convention. We choose 0.0."""
    p = partition_mossinghoff(holdout_fraction=0.0, seed=42)
    result = run_withheld_pilot(p, n_episodes=5, seeds=(0,), agent="reinforce")
    assert result.n_withheld == 0
    assert result.withheld_rediscovery_count == 0
    # Rate is 0.0 by convention when n_withheld==0.
    assert result.withheld_rediscovery_rate == 0.0


def test_edge_holdout_fraction_one_is_degenerate():
    """holdout_fraction=1 -> empty visible set. Either ValueError or
    a degenerate partition where every entry is withheld. We choose
    ValueError because a 'visible catalog of size 0' breaks the
    benchmark contract."""
    with pytest.raises(ValueError):
        partition_mossinghoff(holdout_fraction=1.0, seed=42)


def test_edge_holdout_fraction_out_of_range():
    """holdout_fraction outside [0, 1] -> ValueError."""
    with pytest.raises(ValueError):
        partition_mossinghoff(holdout_fraction=-0.1, seed=42)
    with pytest.raises(ValueError):
        partition_mossinghoff(holdout_fraction=1.5, seed=42)


def test_edge_empty_corpus_raises():
    """Partitioning an empty Mossinghoff snapshot is undefined."""
    with pytest.raises(ValueError):
        partition_mossinghoff(holdout_fraction=0.2, seed=42, _corpus=[])


def test_edge_zero_episodes_yields_zero_rediscovery():
    """n_episodes=0 -> the agent never gets to act -> 0 rediscoveries."""
    partition = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    result = run_withheld_pilot(
        partition, n_episodes=0, seeds=(0,), agent="reinforce"
    )
    assert result.withheld_rediscovery_count == 0
    assert result.withheld_PROMOTE_count == 0


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


def test_composition_end_to_end_pilot_returns_well_formed_result():
    """A 50-episode pilot returns a WithheldResult with all required
    fields populated and internally consistent.

    Composition: partition_mossinghoff -> WithheldDiscoveryPipeline ->
    DiscoveryEnv.step -> train_reinforce_contextual -> WithheldResult.
    The whole chain has to compose without error for the benchmark to
    produce a usable calibration estimate.
    """
    partition = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    result = run_withheld_pilot(
        partition,
        n_episodes=50,
        seeds=(0,),
        agent="reinforce",
    )
    # Every field present and well-typed.
    assert isinstance(result, WithheldResult)
    assert result.n_visible == 142
    assert result.n_withheld == 36
    assert result.withheld_rediscovery_count >= 0
    assert result.withheld_PROMOTE_count >= 0
    # The by_seed dict carries one entry per seed.
    assert set(result.by_seed.keys()) == {0}
    # Episodes-per-rediscovery is well-defined: inf if no rediscoveries,
    # else a finite positive float.
    if result.withheld_rediscovery_count == 0:
        assert math.isinf(result.episodes_per_rediscovery)
    else:
        assert result.episodes_per_rediscovery > 0


def test_composition_rediscovered_terminal_state_in_pipeline():
    """When the pipeline records a withheld rediscovery, its terminal
    state must be PROMOTED or SHADOW_CATALOG (battery-survivor states),
    NOT REJECTED — the catalog_miss override is exactly what unlocks
    the pipeline path past 'known_in_catalog'.

    Composition: WithheldDiscoveryPipeline.process_candidate returns a
    DiscoveryRecord; if the polynomial matches a withheld entry the
    record's terminal_state must be in the survivor set OR rejected
    by a battery member (F1/F6/F11) — but never via catalog match.
    """
    # Use Lehmer (in band, irreducible, non-trivial coefficients) as
    # the withheld target. Build a 1-entry withheld partition.
    lehmer = ([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], 1.1762808182599176)
    partition = WithheldPartition(
        visible_set=[],
        withheld_set=[lehmer],
        partition_seed=0,
        n_visible=0,
        n_withheld=1,
    )
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension

    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    pipeline = WithheldDiscoveryPipeline(kernel=k, ext=ext, partition=partition)
    record = pipeline.process_candidate(lehmer[0], lehmer[1])
    # The kill_pattern, if any, must NOT be 'known_in_catalog'.
    if record.kill_pattern is not None:
        assert "known_in_catalog" not in record.kill_pattern, (
            f"withheld override failed: kill_pattern={record.kill_pattern}"
        )


def test_composition_cross_seed_aggregate_well_defined():
    """3 seeds with the same partition: rediscovery counts are
    individually consistent and the aggregate count is the union of
    distinct withheld matches across seeds.

    Composition: by_seed -> aggregate. Tests that the aggregator
    de-duplicates correctly (rediscovering the same withheld entry
    in seeds 0 and 1 should count once).
    """
    partition = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    result = run_withheld_pilot(
        partition, n_episodes=30, seeds=(0, 1, 2), agent="reinforce"
    )
    assert set(result.by_seed.keys()) == {0, 1, 2}
    # Aggregate count is at least the max over seeds (since the union
    # is at least as big as any single seed).
    per_seed_max = max(
        v["rediscovery_count"] for v in result.by_seed.values()
    )
    assert result.withheld_rediscovery_count >= per_seed_max
    # And bounded above by the sum (with equality only when the seeds
    # rediscovered fully disjoint sets of withheld entries).
    per_seed_sum = sum(
        v["rediscovery_count"] for v in result.by_seed.values()
    )
    assert result.withheld_rediscovery_count <= per_seed_sum


def test_composition_pipeline_does_not_break_default_discovery_pipeline():
    """Instantiating a WithheldDiscoveryPipeline must NOT mutate
    module globals (e.g., the regular DiscoveryPipeline's
    catalog-check function). Patches must be instance-scoped.

    Composition: regular DiscoveryPipeline is reused across the env's
    discovery branch; if the withheld pipeline globally clobbered
    _check_catalog_miss, every subsequent call would erroneously
    treat real catalog entries as misses.
    """
    from prometheus_math import discovery_pipeline as dp_module
    # Capture the original check before instantiating the withheld pipeline.
    original_check = dp_module._check_catalog_miss

    partition = partition_mossinghoff(holdout_fraction=0.2, seed=42)
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension

    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    _ = WithheldDiscoveryPipeline(kernel=k, ext=ext, partition=partition)

    # Module-level check function unchanged.
    assert dp_module._check_catalog_miss is original_check
