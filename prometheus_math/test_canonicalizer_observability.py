"""Tests for prometheus_math.canonicalizer_observability — R21 hot-swap mitigation.

Coverage:
  * Observer writes one JSONL line per observe() call
  * read_all returns observations in append order
  * observed_distribution aggregates and normalises to fractions
  * hot_swap_imminent threshold detection
  * dominant_canonicalizer extraction
  * unique_claims dedup
  * since-filter for windowed analysis
  * Thread-safety (concurrent observe calls don't corrupt log)
  * alert_summary one-call dashboard
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from prometheus_math.canonicalizer_observability import (
    HOT_SWAP_THRESHOLD,
    KNOWN_CANONICALIZERS,
    CanonicalizerObservation,
    CanonicalizerObserver,
    alert_summary,
    dominant_canonicalizer,
    hot_swap_imminent,
    observed_distribution,
)


# ---------------------------------------------------------------------------
# Observer write/read round-trip
# ---------------------------------------------------------------------------


def test_observer_writes_one_jsonl_line_per_observe(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    obs.observe("variety_fingerprint", claim_id="c1")
    obs.observe("partition_refinement", claim_id="c2")
    lines = log.read_text().strip().split("\n")
    assert len(lines) == 2


def test_observer_observe_returns_observation_object(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    o = obs.observe("variety_fingerprint", claim_id="c1", context={"deg": 10})
    assert o.canonicalizer == "variety_fingerprint"
    assert o.claim_id == "c1"
    assert o.context == {"deg": 10}
    assert o.timestamp > 0


def test_observer_read_all_returns_observations_in_append_order(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    obs.observe("variety_fingerprint", claim_id="c1")
    obs.observe("partition_refinement", claim_id="c2")
    obs.observe("group_quotient", claim_id="c3")
    seen = list(obs.read_all())
    assert len(seen) == 3
    assert seen[0].canonicalizer == "variety_fingerprint"
    assert seen[1].canonicalizer == "partition_refinement"
    assert seen[2].canonicalizer == "group_quotient"


def test_observer_read_all_on_missing_log_returns_empty(tmp_path: Path):
    """Reading from a non-existent log is safe (returns empty), not an error."""
    obs = CanonicalizerObserver(log_path=tmp_path / "does_not_exist.jsonl")
    assert list(obs.read_all()) == []


# ---------------------------------------------------------------------------
# Distribution aggregation
# ---------------------------------------------------------------------------


def test_observed_distribution_aggregates_to_fractions(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    for _ in range(5):
        obs.observe("variety_fingerprint")
    for _ in range(3):
        obs.observe("partition_refinement")
    for _ in range(2):
        obs.observe("group_quotient")

    dist = observed_distribution(log_path=log)
    assert abs(dist["variety_fingerprint"] - 0.5) < 1e-9
    assert abs(dist["partition_refinement"] - 0.3) < 1e-9
    assert abs(dist["group_quotient"] - 0.2) < 1e-9
    assert abs(sum(dist.values()) - 1.0) < 1e-9


def test_observed_distribution_empty_log_returns_empty_dict(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    assert observed_distribution(log_path=log) == {}


def test_observed_distribution_unique_claims_deduplicates(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    # Same claim observed 3 times under variety_fingerprint should count once.
    obs.observe("variety_fingerprint", claim_id="c1")
    obs.observe("variety_fingerprint", claim_id="c1")
    obs.observe("variety_fingerprint", claim_id="c1")
    obs.observe("partition_refinement", claim_id="c2")

    dist = observed_distribution(log_path=log, unique_claims=True)
    assert abs(dist["variety_fingerprint"] - 0.5) < 1e-9
    assert abs(dist["partition_refinement"] - 0.5) < 1e-9


def test_observed_distribution_since_filter(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    obs.observe("variety_fingerprint", claim_id="early")
    # Sleep enough to clear Windows clock-resolution; cutoff strictly
    # after the early observation.
    time.sleep(0.1)
    cutoff = time.time()
    time.sleep(0.1)
    obs.observe("partition_refinement", claim_id="late")

    dist_all = observed_distribution(log_path=log)
    assert "variety_fingerprint" in dist_all and "partition_refinement" in dist_all

    dist_recent = observed_distribution(log_path=log, since=cutoff)
    assert "partition_refinement" in dist_recent
    assert "variety_fingerprint" not in dist_recent


# ---------------------------------------------------------------------------
# Hot-swap threshold detection (R21 mitigation core)
# ---------------------------------------------------------------------------


def test_hot_swap_imminent_returns_false_below_threshold():
    dist = {"variety_fingerprint": 0.52, "partition_refinement": 0.48}
    assert not hot_swap_imminent(dist, threshold=0.70)


def test_hot_swap_imminent_returns_true_at_threshold():
    dist = {"variety_fingerprint": 0.70, "partition_refinement": 0.30}
    assert hot_swap_imminent(dist, threshold=0.70)


def test_hot_swap_imminent_returns_true_above_threshold():
    dist = {"variety_fingerprint": 0.85, "partition_refinement": 0.15}
    assert hot_swap_imminent(dist, threshold=0.70)


def test_hot_swap_imminent_returns_false_on_empty():
    assert not hot_swap_imminent({})


def test_default_threshold_matches_descriptor_logic():
    """The 70% threshold is the descriptor.py hot-swap trigger; do not
    accidentally drift this constant."""
    assert HOT_SWAP_THRESHOLD == 0.70


# ---------------------------------------------------------------------------
# Dominant canonicalizer
# ---------------------------------------------------------------------------


def test_dominant_canonicalizer_returns_max_fraction():
    dist = {"variety_fingerprint": 0.52, "partition_refinement": 0.48}
    name, frac = dominant_canonicalizer(dist)
    assert name == "variety_fingerprint"
    assert abs(frac - 0.52) < 1e-9


def test_dominant_canonicalizer_returns_none_on_empty():
    assert dominant_canonicalizer({}) is None


# ---------------------------------------------------------------------------
# alert_summary — dashboard one-call
# ---------------------------------------------------------------------------


def test_alert_summary_returns_full_status(tmp_path: Path):
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    for _ in range(8):
        obs.observe("variety_fingerprint")
    for _ in range(2):
        obs.observe("partition_refinement")

    summary = alert_summary(log_path=log)
    assert summary["n_events"] == 10
    assert summary["distribution"]["variety_fingerprint"] == 0.8
    assert summary["hot_swap_imminent"] is True  # 0.8 >= 0.7
    assert summary["dominant"] == ("variety_fingerprint", 0.8)
    assert summary["threshold"] == HOT_SWAP_THRESHOLD


def test_alert_summary_below_threshold_reports_safe(tmp_path: Path):
    """The Day-0 scenario: variety_fingerprint at 52%, below threshold."""
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    for _ in range(52):
        obs.observe("variety_fingerprint")
    for _ in range(48):
        obs.observe("partition_refinement")

    summary = alert_summary(log_path=log)
    assert summary["hot_swap_imminent"] is False
    assert summary["dominant"][0] == "variety_fingerprint"
    assert abs(summary["dominant"][1] - 0.52) < 1e-9


# ---------------------------------------------------------------------------
# Thread-safety
# ---------------------------------------------------------------------------


def test_observer_thread_safe_concurrent_writes(tmp_path: Path):
    """Concurrent observe() calls from multiple threads must produce a
    well-formed JSONL log (no torn writes)."""
    log = tmp_path / "obs.jsonl"
    obs = CanonicalizerObserver(log_path=log)
    n_threads = 8
    n_per_thread = 50

    def worker(c: str):
        for _ in range(n_per_thread):
            obs.observe(c, claim_id=f"{threading.get_ident()}-{time.time_ns()}")

    threads = [
        threading.Thread(target=worker, args=(KNOWN_CANONICALIZERS[i % len(KNOWN_CANONICALIZERS)],))
        for i in range(n_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Every line should be valid JSON (no torn writes from interleaved fwrites).
    lines = log.read_text().strip().split("\n")
    assert len(lines) == n_threads * n_per_thread
    for line in lines:
        json.loads(line)  # raises if torn


# ---------------------------------------------------------------------------
# Round-trip via from_dict
# ---------------------------------------------------------------------------


def test_observation_to_dict_from_dict_round_trip():
    o = CanonicalizerObservation(
        timestamp=12345.6,
        canonicalizer="variety_fingerprint",
        claim_id="c1",
        context={"deg": 10, "seed": 42},
    )
    d = o.to_dict()
    o2 = CanonicalizerObservation.from_dict(d)
    assert o2.timestamp == o.timestamp
    assert o2.canonicalizer == o.canonicalizer
    assert o2.claim_id == o.claim_id
    assert o2.context == o.context
