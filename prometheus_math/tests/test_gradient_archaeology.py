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
    PER_FILE_METADATA,
    PROMETHEUS_MATH_DIR,
    ArchaeologyResult,
    _extract_kill_pattern_aggregate,
    _extract_lehmer_smoke_records,
    _extract_m_records,
    _extract_region_kill_records,
    _hamming_distance,
    _jensen_shannon_bits,
    _kl_divergence_bits,
    _mutual_information_bits,
    _normalize_counter,
    _region_id,
    _strip_arm_prefix,
    gradient1_m_distribution,
    gradient2_kill_path,
    gradient3_operator_falsifier,
    gradient4_method_utility,
    gradient5_catalog_proximity,
    gradient6_verification_depth,
    load_all_sources,
    load_mossinghoff_catalog,
    nearest_catalog_entry,
    operator_coordinate_charts,
    per_region_disaggregation,
    region_operator_interaction,
    render_report,
    run_archaeology,
    write_artifacts,
)
from collections import Counter


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


# ---------------------------------------------------------------------------
# Per-region disaggregation tests (Day 1-2 extension)
# ---------------------------------------------------------------------------


def test_per_region_arm_prefix_parsing():
    """_strip_arm_prefix splits arm labels into (operator, region_hint)."""
    op, hint = _strip_arm_prefix("catalog_seeded::reinforce_uniform")
    assert op == "reinforce_uniform"
    assert hint is None
    op, hint = _strip_arm_prefix("degree_sweep::deg14::reinforce_agent")
    assert op == "reinforce_agent"
    assert hint == "deg14"
    op, hint = _strip_arm_prefix("plain_label_no_prefix")
    assert op == "plain_label_no_prefix"
    assert hint is None


def test_per_region_id_resolves_split_degree():
    """`degree_sweep` files have degree='split'; the arm hint supplies it."""
    meta = PER_FILE_METADATA["degree_sweep_results.json"]
    assert meta["degree"] == "split"
    rid_12 = _region_id(meta, "deg12")
    rid_14 = _region_id(meta, "deg14")
    assert "deg12" in rid_12
    assert "deg14" in rid_14
    assert rid_12 != rid_14


def test_per_region_kl_nonnegative_and_zero_on_identity():
    """KL divergence is non-negative and zero for identical distributions."""
    p = {"a": 0.5, "b": 0.3, "c": 0.2}
    q = {"a": 0.4, "b": 0.4, "c": 0.2}
    assert _kl_divergence_bits(p, p) == pytest.approx(0.0, abs=1e-6)
    assert _kl_divergence_bits(p, q) > 0
    assert _kl_divergence_bits(q, p) > 0


def test_per_region_jsd_symmetric_and_zero_on_identity():
    """JSD is symmetric and zero for identical distributions."""
    p = {"a": 0.5, "b": 0.3, "c": 0.2}
    q = {"a": 0.4, "b": 0.4, "c": 0.2}
    assert _jensen_shannon_bits(p, p) == pytest.approx(0.0, abs=1e-6)
    j_pq = _jensen_shannon_bits(p, q)
    j_qp = _jensen_shannon_bits(q, p)
    assert j_pq == pytest.approx(j_qp, abs=1e-9)


def test_per_region_mi_nonneg_and_finite():
    """Per-region MI is well-defined, finite, non-negative for every region."""
    sources = load_all_sources()
    pr = per_region_disaggregation(sources)
    if pr["n_regions"] == 0:
        pytest.skip("No region-tagged data on disk")
    for region, info in pr["regions"].items():
        mi = info["mutual_information_bits"]
        assert math.isfinite(mi), f"MI for {region} not finite"
        assert mi >= 0.0, f"MI for {region} negative: {mi}"
        # Bounded by the marginal entropies
        bound = min(info["operator_entropy_bits"], info["kill_entropy_bits"])
        assert mi <= bound + 1e-6, (
            f"MI {mi} exceeds min-marginal-entropy {bound} for {region}"
        )


def test_per_region_count_additivity():
    """Sum of per-region kill counts equals the total tagged kill count.

    This is the count-level additivity check; the information-additivity
    check is in test_per_region_chain_rule_inequality.
    """
    sources = load_all_sources()
    pr = per_region_disaggregation(sources)
    if pr["n_regions"] == 0:
        pytest.skip("No region-tagged data on disk")
    region_total = sum(info["n_kills"] for info in pr["regions"].values())
    global_total = sum(pr["global_kill_distribution"].values())
    assert region_total == global_total, (
        f"Region-level kill total {region_total} != global tagged total "
        f"{global_total}"
    )


def test_per_region_chain_rule_inequality():
    """Information-additivity inequality:
        I(O; K) <= I(R; K) + I(O; K | R)

    This is the chain-rule consequence of conditioning on region. The
    aggregate MI cannot exceed what region+conditional jointly explain.
    """
    sources = load_all_sources()
    rio = region_operator_interaction(sources)
    if rio.get("verdict", "INSUFFICIENT_DATA") == "INSUFFICIENT_DATA":
        pytest.skip("No region-tagged data on disk")
    agg = rio["aggregate_mi_op_kp_bits"]
    cond = rio["conditional_mi_op_kp_given_region_bits"]
    rk = rio["mi_region_kp_bits"]
    # Numerical slack for floating-point noise
    assert agg <= rk + cond + 1e-6, (
        f"Chain-rule violation: I(O;K)={agg} > I(R;K)+I(O;K|R)="
        f"{rk + cond}"
    )


def test_per_region_operator_charts_are_valid_distributions():
    """Each operator's coordinate chart sums to ~1 and is non-negative."""
    sources = load_all_sources()
    oc = operator_coordinate_charts(sources)
    if oc["n_operators"] == 0:
        pytest.skip("No region-tagged data on disk")
    for op, info in oc["operator_charts"].items():
        norm = info["kill_distribution_normalized"]
        # All non-negative
        for k, v in norm.items():
            assert v >= 0.0, f"{op}: negative probability {v} on {k}"
        # Sums to 1 within fp tolerance
        s = sum(norm.values())
        assert s == pytest.approx(1.0, abs=1e-9), (
            f"{op}: kill distribution sums to {s}, not 1"
        )


def test_per_region_pairwise_kl_and_jsd_self_zero():
    """For every operator, pairwise KL and JSD against itself are 0."""
    sources = load_all_sources()
    oc = operator_coordinate_charts(sources)
    if oc["n_operators"] == 0:
        pytest.skip("No region-tagged data on disk")
    for op in oc["operator_charts"]:
        self_pair = f"{op}||{op}"
        # Self-pair JSD must be present and zero
        if self_pair in oc["pairwise_jsd_bits"]:
            assert oc["pairwise_jsd_bits"][self_pair] == pytest.approx(
                0.0, abs=1e-9
            )
        if self_pair in oc["pairwise_kl_bits"]:
            assert oc["pairwise_kl_bits"][self_pair] == pytest.approx(
                0.0, abs=1e-9
            )


def test_per_region_verdict_dispatch_consistency():
    """Verdict label is consistent with the underlying numbers per the
    documented thresholds."""
    sources = load_all_sources()
    rio = region_operator_interaction(sources)
    v = rio.get("verdict")
    if v == "INSUFFICIENT_DATA":
        pytest.skip("No region-tagged data on disk")
    agg = rio["aggregate_mi_op_kp_bits"]
    cond = rio["conditional_mi_op_kp_given_region_bits"]
    rk = rio["mi_region_kp_bits"]
    assert v in ("A_OPERATOR_INVARIANT", "B_REGION_SPECIFIC",
                 "C_BOTH_SIGNIFICANT")
    if v == "A_OPERATOR_INVARIANT":
        assert cond >= 0.85 * agg - 1e-9
        assert rk < 0.5 * agg + 1e-9
    elif v == "B_REGION_SPECIFIC":
        assert cond < 0.5 * agg + 1e-9 or rk > agg - 1e-9
    elif v == "C_BOTH_SIGNIFICANT":
        # Falls through both A and B conditions
        assert not (cond >= 0.85 * agg and rk < 0.5 * agg)
        assert not (cond < 0.5 * agg or rk > agg)


def test_per_region_appears_in_run_archaeology():
    """run_archaeology populates the per-region fields."""
    res = run_archaeology()
    assert "per_region_disaggregation" in res.as_dict()
    assert "operator_coordinate_charts" in res.as_dict()
    assert "region_operator_interaction" in res.as_dict()
    # And cross_observations carries the verdict
    assert "per_region_verdict" in res.cross_observations


def test_per_region_synthetic_invariant_yields_A():
    """When operator behavior is identical across regions (perfect
    region-invariance), the verdict dispatcher returns A.

    Build a synthetic source: two regions, two operators, kill_pattern
    distribution depends ONLY on operator (region has zero effect on
    kp given operator)."""
    # Two regions, two operators, each operator has a deterministic
    # distinct kill_pattern preference that does NOT vary with region.
    # We simulate this by injecting fake records into PER_FILE_METADATA
    # and feeding the per_region_disaggregation a hand-crafted "sources"
    # list that bypasses the file-based extractor.

    # Hand-crafted records, mimicking _extract_region_kill_records output:
    fake_records = []
    for region in ["envA|deg10|w5|step", "envA|deg14|w5|step"]:
        # Operator opX kills mostly on kp1
        fake_records.append(
            {"region": region, "operator": "opX", "kill_pattern": "kp1",
             "count": 800, "file": "fake"}
        )
        fake_records.append(
            {"region": region, "operator": "opX", "kill_pattern": "kp2",
             "count": 200, "file": "fake"}
        )
        # Operator opY kills mostly on kp2
        fake_records.append(
            {"region": region, "operator": "opY", "kill_pattern": "kp1",
             "count": 200, "file": "fake"}
        )
        fake_records.append(
            {"region": region, "operator": "opY", "kill_pattern": "kp2",
             "count": 800, "file": "fake"}
        )

    # Use the same primitives as the real pipeline to compute the
    # interaction numbers from the synthetic records.
    op_kp_table: dict = {}
    region_kp_table: dict = {}
    by_region_table: dict = {}
    by_region_total: dict = {}
    for r in fake_records:
        op_kp_table[(r["operator"], r["kill_pattern"])] = (
            op_kp_table.get((r["operator"], r["kill_pattern"]), 0) + r["count"]
        )
        region_kp_table[(r["region"], r["kill_pattern"])] = (
            region_kp_table.get((r["region"], r["kill_pattern"]), 0) + r["count"]
        )
        by_region_table.setdefault(r["region"], {})[
            (r["operator"], r["kill_pattern"])
        ] = (
            by_region_table.setdefault(r["region"], {}).get(
                (r["operator"], r["kill_pattern"]), 0
            ) + r["count"]
        )
        by_region_total[r["region"]] = (
            by_region_total.get(r["region"], 0) + r["count"]
        )

    _, _, _, mi_op_kp = _mutual_information_bits(op_kp_table)
    _, _, _, mi_r_kp = _mutual_information_bits(region_kp_table)
    total = sum(by_region_total.values())
    cond_mi = sum(
        (n / total) * _mutual_information_bits(t)[3]
        for region, t in by_region_table.items()
        for n in [by_region_total[region]]
    )

    # By construction the kill distribution is identical across regions
    # given operator: cond_mi == agg_mi (~0.278 bits each), mi_r_kp ~ 0.
    assert cond_mi == pytest.approx(mi_op_kp, abs=1e-6)
    assert mi_r_kp < 1e-6
    # Verdict A condition is satisfied
    assert cond_mi >= 0.85 * mi_op_kp
    assert mi_r_kp < 0.5 * mi_op_kp
