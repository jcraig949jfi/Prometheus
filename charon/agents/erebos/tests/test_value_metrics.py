"""Synthetic-control tests for value_metrics.

Per Erebos v3 Phase 0 ITER-27. Validates the closed-loop epistemic
economy primitives + the value_per_tick metric that Sprint-1
measures against.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

import pytest

from charon.agents.erebos._value_metrics import (
    information_gain_estimate,
    summarize_economy,
    update_reuse_value_counts,
    value_per_tick,
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


# ---------------------------------------------------------------------
# value_per_tick
# ---------------------------------------------------------------------

def test_value_per_tick_zero_for_empty_ledger():
    assert value_per_tick([]) == 0.0


def test_value_per_tick_zero_when_all_costs_zero():
    rows = [{
        "emitted_at": _iso_now(),
        "information_gain_nats": 1.0,
        "reuse_value_count": 5,
        "generation_cost_seconds": 0.0,
        "falsification_cost_seconds": 0.0,
    }]
    assert value_per_tick(rows) == 0.0


def test_value_per_tick_increases_with_information_gain():
    base = {
        "emitted_at": _iso_now(),
        "reuse_value_count": 3,
        "generation_cost_seconds": 1.0,
        "falsification_cost_seconds": 1.0,
    }
    row_low = {**base, "information_gain_nats": 0.1}
    row_high = {**base, "information_gain_nats": 1.0}
    assert value_per_tick([row_high]) > value_per_tick([row_low])


def test_value_per_tick_decreases_with_falsification_cost():
    base = {
        "emitted_at": _iso_now(),
        "information_gain_nats": 0.5,
        "reuse_value_count": 2,
        "generation_cost_seconds": 1.0,
    }
    row_cheap = {**base, "falsification_cost_seconds": 1.0}
    row_expensive = {**base, "falsification_cost_seconds": 10.0}
    assert value_per_tick([row_cheap]) > value_per_tick([row_expensive])


def test_value_per_tick_window_filter():
    """Rows older than window_days excluded."""
    fresh = {
        "emitted_at": _iso_now(),
        "information_gain_nats": 1.0,
        "reuse_value_count": 5,
        "generation_cost_seconds": 1.0,
        "falsification_cost_seconds": 1.0,
    }
    stale = {
        "emitted_at": _iso_days_ago(120),  # outside 60-day window
        "information_gain_nats": 100.0,
        "reuse_value_count": 100,
        "generation_cost_seconds": 0.001,
        "falsification_cost_seconds": 0.001,
    }
    vpt_with_stale_excluded = value_per_tick([fresh, stale], window_days=60)
    vpt_fresh_only = value_per_tick([fresh], window_days=60)
    assert vpt_with_stale_excluded == vpt_fresh_only


def test_value_per_tick_handles_missing_fields():
    """Missing fields treated as zeros — must not crash."""
    rows = [{"emitted_at": _iso_now()}]  # no costs, no info, no reuse
    assert value_per_tick(rows) == 0.0


# ---------------------------------------------------------------------
# information_gain_estimate (KL divergence)
# ---------------------------------------------------------------------

def test_information_gain_zero_for_identical_distributions():
    dist = {"a": 0.5, "b": 0.5}
    assert information_gain_estimate(dist, dist) < 1e-6


def test_information_gain_positive_for_diverged_distributions():
    before = {"a": 0.5, "b": 0.5}
    after = {"a": 0.9, "b": 0.1}
    kl = information_gain_estimate(before, after)
    assert kl > 0


def test_information_gain_zero_for_empty_distributions():
    assert information_gain_estimate({}, {"a": 1.0}) == 0.0
    assert information_gain_estimate({"a": 1.0}, {}) == 0.0


def test_information_gain_handles_unnormalized_distributions():
    """Unnormalized inputs handled (internal normalization)."""
    before = {"a": 50, "b": 50}      # sums to 100
    after = {"a": 90, "b": 10}       # sums to 100
    # Should equal information_gain on normalized versions
    kl_unnorm = information_gain_estimate(before, after)
    kl_norm = information_gain_estimate(
        {"a": 0.5, "b": 0.5}, {"a": 0.9, "b": 0.1}
    )
    assert abs(kl_unnorm - kl_norm) < 1e-6


def test_information_gain_disjoint_supports():
    """before puts mass on {a}, after on {b} — KL is finite (due to
    epsilon smoothing) but large."""
    before = {"a": 1.0}
    after = {"b": 1.0}
    kl = information_gain_estimate(before, after)
    assert kl > 5.0  # large positive value


# ---------------------------------------------------------------------
# update_reuse_value_counts
# ---------------------------------------------------------------------

def test_update_reuse_value_counts_missing_file_returns_empty(tmp_path):
    nonexistent = tmp_path / "nope.jsonl"
    assert update_reuse_value_counts(nonexistent) == {}


def test_update_reuse_value_counts_correct_on_synthetic_ledger(tmp_path):
    """Synthetic ledger with parent_record_ids pointing to in-window
    rows. Counts must match the references."""
    ledger = tmp_path / "synth.jsonl"
    rows = [
        # row_1 is in window
        {
            "record_id": "row_1",
            "emitted_at": _iso_now(),
            "parent_record_ids": [],
        },
        # row_2 references row_1 -> reuse count for row_1 == 1
        {
            "record_id": "row_2",
            "emitted_at": _iso_now(),
            "parent_record_ids": ["row_1"],
        },
        # row_3 also references row_1 -> reuse count for row_1 == 2
        {
            "record_id": "row_3",
            "emitted_at": _iso_now(),
            "parent_record_ids": ["row_1"],
        },
    ]
    with ledger.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    counts = update_reuse_value_counts(ledger)
    assert counts.get("row_1") == 2


def test_update_reuse_value_counts_excludes_stale_parents(tmp_path):
    """Parent emitted outside window is not counted."""
    ledger = tmp_path / "synth.jsonl"
    rows = [
        {  # stale parent
            "record_id": "stale_p",
            "emitted_at": _iso_days_ago(120),
            "parent_record_ids": [],
        },
        {  # in-window child referencing stale parent
            "record_id": "child",
            "emitted_at": _iso_now(),
            "parent_record_ids": ["stale_p"],
        },
    ]
    with ledger.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    counts = update_reuse_value_counts(ledger, window_days=60)
    # stale_p excluded -> reuse count not recorded
    assert "stale_p" not in counts


def test_update_reuse_value_counts_skips_malformed_lines(tmp_path):
    """Malformed JSON lines are skipped, not fatal."""
    ledger = tmp_path / "synth.jsonl"
    with ledger.open("w", encoding="utf-8") as f:
        f.write('{"record_id": "good", "emitted_at": "' + _iso_now() + '", "parent_record_ids": []}\n')
        f.write('not valid json\n')
        f.write('{"record_id": "child", "emitted_at": "' + _iso_now() + '", "parent_record_ids": ["good"]}\n')
    counts = update_reuse_value_counts(ledger)
    assert counts.get("good") == 1


# ---------------------------------------------------------------------
# summarize_economy
# ---------------------------------------------------------------------

def test_summarize_economy_empty():
    summary = summarize_economy([])
    assert summary["n_emissions"] == 0
    assert summary["value_per_tick_nat_per_sec"] == 0.0


def test_summarize_economy_basic_stats():
    rows = [
        {
            "emitted_at": _iso_now(),
            "generation_cost_seconds": 1.0,
            "falsification_cost_seconds": 2.0,
            "information_gain_nats": 0.5,
            "reuse_value_count": 3,
        },
        {
            "emitted_at": _iso_now(),
            "generation_cost_seconds": 2.0,
            "falsification_cost_seconds": 3.0,
            "information_gain_nats": 1.0,
            "reuse_value_count": 5,
        },
    ]
    summary = summarize_economy(rows, window_days=60)
    assert summary["n_emissions"] == 2
    assert summary["total_generation_cost_seconds"] == 3.0
    assert summary["total_falsification_cost_seconds"] == 5.0
    assert summary["total_information_gain_nats"] == 1.5
    assert summary["total_reuse_value_count"] == 8


def test_summarize_economy_window_filter():
    rows = [
        {"emitted_at": _iso_now(),
         "generation_cost_seconds": 1.0,
         "falsification_cost_seconds": 1.0,
         "information_gain_nats": 0.5,
         "reuse_value_count": 1},
        {"emitted_at": _iso_days_ago(120),
         "generation_cost_seconds": 100.0,
         "falsification_cost_seconds": 100.0,
         "information_gain_nats": 10.0,
         "reuse_value_count": 100},
    ]
    summary = summarize_economy(rows, window_days=60)
    assert summary["n_emissions"] == 1  # stale excluded


# ---------------------------------------------------------------------
# ComposedClaim integration — fields default to safe values
# ---------------------------------------------------------------------

def test_composed_claim_has_cost_fields_default_zero():
    from charon.agents.erebos.generators._base import ComposedClaim
    claim = ComposedClaim(
        plugin_id="g_test",
        composed_id="TEST-COST-001",
        input_provenance={},
        transformation_description="t",
        output_claim_text="claim",
        falsification_route="f",
        expected_kill_pattern="kp",
        loader_feasibility_note="n",
    )
    assert claim.generation_cost_seconds == 0.0
    assert claim.falsification_cost_seconds is None
    assert claim.information_gain_nats is None
    assert claim.reuse_value_count == 0
