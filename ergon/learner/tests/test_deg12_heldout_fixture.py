"""Tests for the deg-12 ±5 unlabeled held-out fixture (E-2026-05-07-T-deg12-fixture).

Coordination ticket from Techne fire-8 (joint sprint commitment T12):
deg-12 brute-force fixture delivered as 113 raw band candidates with
deferred triangulation. Ergon ingests as unlabeled structural held-out.

Tests:
1. Loader reads Techne's JSON without crash
2. Returns expected count (113 records)
3. Each record has palindromic-deg-12 coefficients
4. mahler_measure within band [1.000001, 1.18]
5. triangulation_status is "pending" (deferred per Techne)
6. metadata block carries provenance
7. Deg12HeldoutRecord is NOT a BoundaryLayerRecord (sibling type)
8. Existing BoundaryLayerRecord schema unchanged (regression check)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ergon.pipeline_d.boundary_layer_fixture import (
    DEFAULT_DEG12_RESULTS,
    DEG12_DEGREE,
    DEG12_N_FREE,
    BoundaryLayerRecord,
    Deg12HeldoutRecord,
    load_deg12_heldout_fixture,
)


@pytest.fixture(scope="module")
def deg12():
    if not DEFAULT_DEG12_RESULTS.exists():
        pytest.skip(f"deg-12 fixture not on disk at {DEFAULT_DEG12_RESULTS}")
    records, metadata = load_deg12_heldout_fixture()
    return records, metadata


def test_loader_reads_without_crash(deg12):
    records, metadata = deg12
    assert isinstance(records, list)
    assert isinstance(metadata, dict)


def test_record_count_matches_techne_fixture(deg12):
    records, metadata = deg12
    assert len(records) == 113
    assert metadata["in_band_count"] == 113


def test_palindromic_coefficients(deg12):
    records, _ = deg12
    for r in records:
        coeffs = r.poly_coefficients
        assert len(coeffs) == DEG12_DEGREE + 1
        for i in range(DEG12_DEGREE + 1):
            assert coeffs[i] == coeffs[DEG12_DEGREE - i]


def test_free_coefficients_consistent_with_full(deg12):
    records, _ = deg12
    for r in records:
        assert len(r.free_coefficients) == DEG12_N_FREE
        for i in range(DEG12_N_FREE):
            assert r.free_coefficients[i] == r.poly_coefficients[i]


def test_mahler_in_band(deg12):
    records, _ = deg12
    for r in records:
        assert r.band_lower <= r.mahler_measure <= r.band_upper
        assert r.in_band is True


def test_triangulation_status_pending(deg12):
    records, metadata = deg12
    assert metadata["triangulation_status"] == "pending"
    for r in records:
        assert r.triangulation_status == "pending"


def test_metadata_provenance(deg12):
    _, metadata = deg12
    assert metadata["degree"] == DEG12_DEGREE
    assert metadata["coef_range"] == [-5, 5]
    assert metadata["n_polys_processed"] >= 8_000_000
    assert metadata["techne_ticket"] == "E-2026-05-07-T-deg12-fixture"
    assert metadata["source_module"] == "prometheus_math.lehmer_brute_force_general"


def test_deg12_record_is_not_boundary_layer_record(deg12):
    records, _ = deg12
    sample = records[0]
    assert isinstance(sample, Deg12HeldoutRecord)
    assert not isinstance(sample, BoundaryLayerRecord)


def test_boundary_layer_record_schema_unchanged():
    """Regression check: deg-14 BoundaryLayerRecord schema unchanged."""
    import dataclasses
    fields = {f.name for f in dataclasses.fields(BoundaryLayerRecord)}
    expected = {
        "poly_coefficients", "mahler_measure_dps30", "mahler_measure_dps60",
        "mahler_measure_dps100", "factor_list_strategy", "n_irreducible_factors",
        "cyclotomic_factor_indices", "cyclotomic_factor_powers",
        "non_cyclotomic_factor_present", "non_cyclotomic_factor_mahler",
        "verification_failed", "catalog_match_type", "boundary_layer_silhouette",
        "reflection_pair_partner_idx", "cls", "cls_post_fold",
        "entry_index", "source",
    }
    assert fields == expected


def test_mahler_distribution_spans_band():
    records, _ = load_deg12_heldout_fixture()
    mahlers = [r.mahler_measure for r in records]
    assert max(mahlers) > 1.001
    assert max(mahlers) < 1.18
