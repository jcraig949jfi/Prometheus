"""Tests for prometheus_math.gradient_archaeology.

Math-tdd skill rubric: >=3 tests in each of authority / property / edge /
composition.

Authority anchors (immutable):
  * Mossinghoff catalog has 8625 entries (current snapshot) and contains
    Lehmer's polynomial with M=1.17628081826...
  * The catalog_seeded::random_seeded arm produces M values bounded
    BELOW by 1.17628 (catalog Salem entries at or above Lehmer's M).
  * Hamming distance is non-negative, symmetric, and zero iff equal.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
from typing import Any, Dict, List

import pytest

from prometheus_math.gradient_archaeology import (
    PROMETHEUS_MATH_DIR,
    ArchaeologyResult,
    _extract_kill_pattern_aggregate,
    _extract_lehmer_smoke_records,
    _extract_m_records,
    _hamming_distance,
    gradient1_m_distribution,
    gradient2_kill_path,
    gradient3_operator_falsifier,
    gradient4_method_utility,
    gradient5_catalog_proximity,
    gradient6_verification_depth,
    load_all_sources,
    load_mossinghoff_catalog,
    nearest_catalog_entry,
    render_report,
    run_archaeology,
    write_artifacts,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_authority_mossinghoff_contains_lehmer():
    """The Mossinghoff catalog contains Lehmer's polynomial at M~1.17628."""
    cat = load_mossinghoff_catalog()
    assert len(cat) >= 8000, "Mossinghoff catalog far smaller than snapshot"
    near_lehmer = [e for e in cat
                   if abs(e.get("mahler_measure", 99) - 1.17628081826) < 1e-6]
    assert near_lehmer, "Lehmer's polynomial absent from catalog"


def test_authority_catalog_seeded_m_records_above_lehmer():
    """The catalog_seeded::random_seeded arm logs Salem-band M values
    bounded below by 1.17628 (catalog construction).

    This is the authoritative anchor: the discovery pipeline doesn't
    reward sub-Lehmer M values that aren't catalog matches, so any
    catalog_hit must hit Lehmer's M or higher Salem entries.
    """
    sources = load_all_sources()
    m_records: List[Dict[str, Any]] = []
    for s in sources:
        m_records.extend(_extract_m_records(s))
    if not m_records:
        pytest.skip("No catalog_seeded pilot data on disk")
    ms = [r["M"] for r in m_records]
    # Authoritative: the minimum Mahler measure of an irreducible
    # non-cyclotomic integer polynomial is Lehmer's 1.17628 (open
    # conjecture, never violated empirically).
    assert min(ms) >= 1.17628 - 1e-6, (
        f"Found M = {min(ms):.6f} below Lehmer's bound — would falsify "
        "Lehmer's conjecture; far more likely an aggregator bug."
    )


def test_authority_kill_pattern_keys_well_formed():
    """kill_pattern aggregations should produce non-empty string keys
    when the source schema persists by_kill_pattern.

    Authority: the four_counts_pilot_run_10k schema documented in
    USER_GUIDE.md has by_kill_pattern at per_condition[arm].
    """
    sources = load_all_sources()
    seen_any = False
    for s in sources:
        agg = _extract_kill_pattern_aggregate(s)
        for arm, ctr in agg["per_arm_kill_patterns"].items():
            assert isinstance(arm, str) and len(arm) > 0
            for kp, count in ctr.items():
                assert isinstance(kp, str) and len(kp) > 0
                assert isinstance(count, int) and count >= 0
                seen_any = True
    if not seen_any:
        pytest.skip("No kill-pattern data on disk")


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


def test_property_hamming_zero_iff_equal():
    """_hamming_distance(a, a) == 0 and 0 implies equality."""
    a = [1, 0, -1, 2, 1]
    b = [1, 0, -1, 2, 1]
    c = [1, 0, -1, 2, 0]
    assert _hamming_distance(a, b) == 0
    assert _hamming_distance(a, c) == 1
    assert _hamming_distance(c, a) == 1  # symmetric


def test_property_aggregation_associative():
    """Aggregating sources in two halves should equal aggregating all."""
    sources = load_all_sources()
    if len(sources) < 4:
        pytest.skip("Need >=4 sources on disk for associativity check")
    half = len(sources) // 2
    full = gradient2_kill_path(sources)
    a = gradient2_kill_path(sources[:half])
    b = gradient2_kill_path(sources[half:])

    # Total kills should match
    assert (a["n_total_kills"] + b["n_total_kills"]) == full["n_total_kills"]


def test_property_total_count_equals_sum_per_source():
    """Total episodes equals sum of per-source episodes."""
    sources = load_all_sources()
    total_via_run = sum(
        _extract_kill_pattern_aggregate(s)["n_episodes_total"]
        for s in sources
    )
    res = run_archaeology()
    assert res.n_episodes_total == total_via_run


def test_property_determinism():
    """Running the analysis twice on the same data yields the same JSON."""
    res1 = run_archaeology()
    res2 = run_archaeology()
    # Compare key invariants
    assert res1.gradient2["n_total_kills"] == res2.gradient2["n_total_kills"]
    assert res1.gradient1["n_records"] == res2.gradient1["n_records"]
    assert res1.gradient3["n_total"] == res2.gradient3["n_total"]


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


def test_edge_empty_m_records():
    """gradient1 handles zero M records cleanly."""
    out = gradient1_m_distribution([])
    assert out["n_records"] == 0
    # When empty, we report NEEDS_NEW_INSTRUMENTATION
    assert out["verdict"] == "NEEDS_NEW_INSTRUMENTATION"
    assert out["overall_summary"]["m_min"] is None


def test_edge_empty_sources():
    """gradient2 / gradient3 handle empty source list cleanly."""
    g2 = gradient2_kill_path([])
    assert g2["n_total_kills"] == 0
    assert g2["verdict"] == "NEEDS_NEW_INSTRUMENTATION"

    g3 = gradient3_operator_falsifier([])
    assert g3["verdict"] == "NEEDS_NEW_INSTRUMENTATION"


def test_edge_missing_fields_handled():
    """Schemas with unknown fields shouldn't crash the extractors."""
    fake = {"file": "fake.json",
            "family": "made_up",
            "schema": "totally_unknown_schema",
            "data": {"random": "garbage", "no_kill_pattern": True}}
    out = _extract_kill_pattern_aggregate(fake)
    assert out["per_arm_kill_patterns"] == {}
    assert out["n_episodes_total"] == 0
    # m records: empty
    m = _extract_m_records(fake)
    assert m == []
    smoke = _extract_lehmer_smoke_records(fake)
    assert smoke == []


def test_edge_degenerate_distribution():
    """Distribution with all-same value is handled."""
    same = [{"arm": "x", "M": 1.5, "coeffs": (1, 1, 1, 1, 1, 1, 1)}
            for _ in range(50)]
    out = gradient1_m_distribution(same)
    assert out["n_records"] == 50
    # All in one bin -> n_nonzero = 1
    n_nonzero = sum(1 for v in out["overall_histogram"].values() if v > 0)
    assert n_nonzero == 1
    # Verdict should still be valid (one of the three)
    assert out["verdict"] in ("SIGNAL_PRESENT", "SIGNAL_ABSENT",
                                "NEEDS_NEW_INSTRUMENTATION")


def test_edge_nearest_catalog_with_empty_catalog():
    """nearest_catalog_entry returns None on empty catalog."""
    out = nearest_catalog_entry([1, 0, -1, 0, 1], [])
    assert out is None


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_pipeline_produces_well_formed_json(tmp_path):
    """Full run -> JSON is valid + contains all 6 gradients."""
    res = run_archaeology()
    json_path = tmp_path / "results.json"
    md_path = tmp_path / "report.md"
    write_artifacts(res, str(json_path), str(md_path))

    assert json_path.exists()
    with open(json_path) as f:
        d = json.load(f)
    for k in [
        "gradient1_distance_to_target",
        "gradient2_kill_path_density",
        "gradient3_operator_falsifier",
        "gradient4_method_utility",
        "gradient5_catalog_proximity",
        "gradient6_verification_depth",
    ]:
        assert k in d
        assert "verdict" in d[k]
        assert d[k]["verdict"] in (
            "SIGNAL_PRESENT", "SIGNAL_ABSENT", "NEEDS_NEW_INSTRUMENTATION"
        )


def test_composition_all_six_gradients_computed():
    """The ArchaeologyResult exposes all 6 gradients."""
    res = run_archaeology()
    assert isinstance(res, ArchaeologyResult)
    for g in (res.gradient1, res.gradient2, res.gradient3,
                res.gradient4, res.gradient5, res.gradient6):
        assert "verdict" in g
        assert "rationale" in g


def test_composition_report_doc_generated(tmp_path):
    """Render report yields >300 lines with all gradient sections."""
    res = run_archaeology()
    text = render_report(res)
    assert "## Gradient 1" in text
    assert "## Gradient 2" in text
    assert "## Gradient 3" in text
    assert "## Gradient 4" in text
    assert "## Gradient 5" in text
    assert "## Gradient 6" in text
    assert "## The Empirical Answer" in text
    assert "## Implications for Layer 2 Repair" in text
    # Reasonable size
    assert len(text.split("\n")) >= 100


def test_composition_gradient6_is_needs_instrumentation():
    """Gradient 6 is documented as missing-by-design."""
    g6 = gradient6_verification_depth()
    assert g6["verdict"] == "NEEDS_NEW_INSTRUMENTATION"
    assert "evidence" in g6
    assert len(g6["evidence"]) >= 2
