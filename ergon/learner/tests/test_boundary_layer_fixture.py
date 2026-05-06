"""Tests for ergon.pipeline_d.boundary_layer_fixture (W3.2).

Validates the 17-entry Lehmer boundary-layer fixture in the PROVISIONAL
schema (per James's 2026-05-06 override; NOT v2.2-aligned).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from ergon.pipeline_d.boundary_layer_fixture import (
    CATALOG_MATCH_TYPES,
    CLASS_LABELS,
    CLASS_POST_FOLD,
    FACTOR_STRATEGIES,
    BoundaryLayerRecord,
    dump_to_jsonl,
    load_17_entry_fixture,
    load_from_jsonl,
    load_heldout_fixture,
)


# ---------------------------------------------------------------------------
# 17-entry fixture
# ---------------------------------------------------------------------------

def test_loads_17_entries():
    records = load_17_entry_fixture()
    assert len(records) == 17
    assert all(isinstance(r, BoundaryLayerRecord) for r in records)


def test_all_records_schema_conformant():
    records = load_17_entry_fixture()
    for r in records:
        # Required enums
        assert r.cls in CLASS_LABELS
        assert r.cls_post_fold in CLASS_POST_FOLD
        assert r.factor_list_strategy in FACTOR_STRATEGIES
        assert r.catalog_match_type in CATALOG_MATCH_TYPES
        # Polynomial geometry
        assert len(r.poly_coefficients) == 15  # deg-14 ascending
        assert all(isinstance(c, int) for c in r.poly_coefficients)
        assert all(-5 <= c <= 5 for c in r.poly_coefficients)
        # Palindromicity
        assert r.poly_coefficients == list(reversed(r.poly_coefficients))
        # Cyclotomic factor lists same length
        assert len(r.cyclotomic_factor_indices) == len(r.cyclotomic_factor_powers)
        # Mahler measures finite (mpmath polyroots converges at all 3 dps)
        for M in (r.mahler_measure_dps30, r.mahler_measure_dps60, r.mahler_measure_dps100):
            assert math.isfinite(M), f"non-finite Mahler measure: {M}"
            assert M >= 0.999  # at least 1 to within float-noise
        # boundary_layer_silhouette is the global k=2 score, ~0.86 on these data
        assert math.isfinite(r.boundary_layer_silhouette)
        assert 0.5 < r.boundary_layer_silhouette < 1.0


def test_per_class_counts_15_plus_2():
    """Techne path-B: 15 cyclotomic-noise + 2 lehmer-composite (post fold)."""
    records = load_17_entry_fixture()
    post_fold_counts = {label: 0 for label in CLASS_POST_FOLD}
    for r in records:
        post_fold_counts[r.cls_post_fold] += 1
    assert post_fold_counts["cyclotomic_noise"] == 15
    assert post_fold_counts["lehmer_composite"] == 2


def test_per_class_counts_4way():
    """4-class breakdown: 12 std + 2 reflection + 1 phi_4 + 2 lehmer = 17."""
    records = load_17_entry_fixture()
    counts = {label: 0 for label in CLASS_LABELS}
    for r in records:
        counts[r.cls] += 1
    assert counts["lehmer_x_phi_n_k_composite"] == 2
    assert counts["high_degree_reflection_pair"] == 2
    assert counts["phi_4_singleton"] == 1
    assert counts["standard_quad_factor"] == 12
    assert sum(counts.values()) == 17


def test_lehmer_composite_records_have_non_cyclotomic_factor():
    records = load_17_entry_fixture()
    for r in records:
        if r.cls_post_fold == "lehmer_composite":
            assert r.non_cyclotomic_factor_present
            assert r.non_cyclotomic_factor_mahler is not None
            # Lehmer's M ~ 1.17628
            assert abs(r.non_cyclotomic_factor_mahler - 1.17628) < 0.001


def test_cyclotomic_noise_records_have_no_non_cyclotomic_factor():
    records = load_17_entry_fixture()
    for r in records:
        if r.cls_post_fold == "cyclotomic_noise":
            assert not r.non_cyclotomic_factor_present
            assert r.non_cyclotomic_factor_mahler is None


def test_reflection_pair_partner_indices_consistent():
    """If A says partner=B then B should say partner=A (involution)."""
    records = load_17_entry_fixture()
    for i, r in enumerate(records):
        if r.reflection_pair_partner_idx is not None:
            j = r.reflection_pair_partner_idx
            assert 0 <= j < len(records)
            assert j != i, "self-partner should be encoded as None"
            assert records[j].reflection_pair_partner_idx == i


def test_high_degree_reflection_pair_class_appears_in_pairs():
    """The 2 high_degree_reflection_pair entries should be each other's partners."""
    records = load_17_entry_fixture()
    refl_idxs = [
        i for i, r in enumerate(records) if r.cls == "high_degree_reflection_pair"
    ]
    assert len(refl_idxs) == 2
    a, b = refl_idxs
    assert records[a].reflection_pair_partner_idx == b
    assert records[b].reflection_pair_partner_idx == a


# ---------------------------------------------------------------------------
# Held-out fixture
# ---------------------------------------------------------------------------

def test_heldout_fixture_loads():
    records, meta = load_heldout_fixture()
    assert len(records) == 17
    assert meta["holdout_kind"] == "synthetic_holdout"
    assert meta["transform"] == "x_to_minus_x_reflection"


def test_heldout_preserves_post_fold_labels():
    """Reflection preserves cyclotomic-noise vs lehmer-composite split."""
    base = load_17_entry_fixture()
    held, _ = load_heldout_fixture()
    base_pf = sorted(r.cls_post_fold for r in base)
    held_pf = sorted(r.cls_post_fold for r in held)
    assert base_pf == held_pf


def test_heldout_preserves_mahler_measures():
    """M(P) is invariant under x -> -x."""
    base = load_17_entry_fixture()
    held, _ = load_heldout_fixture()
    for b, h in zip(base, held):
        assert h.mahler_measure_dps30 == pytest.approx(b.mahler_measure_dps30)
        assert h.mahler_measure_dps60 == pytest.approx(b.mahler_measure_dps60)
        assert h.mahler_measure_dps100 == pytest.approx(b.mahler_measure_dps100)


def test_heldout_palindromic_and_in_range():
    held, _ = load_heldout_fixture()
    for r in held:
        assert len(r.poly_coefficients) == 15
        assert r.poly_coefficients == list(reversed(r.poly_coefficients))
        assert all(-5 <= c <= 5 for c in r.poly_coefficients)


def test_heldout_marked_synthetic_in_source():
    held, _ = load_heldout_fixture()
    for r in held:
        assert r.source.startswith("synthetic_holdout_")


# ---------------------------------------------------------------------------
# JSONL round-trip
# ---------------------------------------------------------------------------

def test_jsonl_round_trip(tmp_path: Path):
    records = load_17_entry_fixture()
    path = tmp_path / "fixture.jsonl"
    dump_to_jsonl(records, path)
    assert path.exists()

    # File should have exactly 17 non-empty lines.
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 17

    # Each line is JSON-decodable and has 'class' + 'class_post_fold' (not 'cls').
    first = json.loads(lines[0])
    assert "class" in first
    assert "class_post_fold" in first
    assert "cls" not in first

    reloaded = load_from_jsonl(path)
    assert len(reloaded) == 17
    for orig, back in zip(records, reloaded):
        assert orig.poly_coefficients == back.poly_coefficients
        assert orig.cls == back.cls
        assert orig.cls_post_fold == back.cls_post_fold
        assert orig.cyclotomic_factor_indices == back.cyclotomic_factor_indices
        assert orig.cyclotomic_factor_powers == back.cyclotomic_factor_powers
        assert orig.non_cyclotomic_factor_present == back.non_cyclotomic_factor_present
        assert orig.catalog_match_type == back.catalog_match_type
        assert orig.entry_index == back.entry_index
        assert orig.reflection_pair_partner_idx == back.reflection_pair_partner_idx


def test_jsonl_round_trip_heldout(tmp_path: Path):
    held, _ = load_heldout_fixture()
    path = tmp_path / "heldout.jsonl"
    dump_to_jsonl(held, path)
    reloaded = load_from_jsonl(path)
    assert len(reloaded) == 17
    for orig, back in zip(held, reloaded):
        assert orig.poly_coefficients == back.poly_coefficients
        assert orig.cls == back.cls
        assert orig.cls_post_fold == back.cls_post_fold
        assert orig.source == back.source


def test_record_validation_rejects_bad_enum():
    with pytest.raises(ValueError):
        BoundaryLayerRecord(
            poly_coefficients=[1] * 15,
            mahler_measure_dps30=1.0,
            mahler_measure_dps60=1.0,
            mahler_measure_dps100=1.0,
            factor_list_strategy="not_a_strategy",
            n_irreducible_factors=1,
            cyclotomic_factor_indices=[],
            cyclotomic_factor_powers=[],
            non_cyclotomic_factor_present=False,
            non_cyclotomic_factor_mahler=None,
            verification_failed=False,
            catalog_match_type="all_cyclotomic",
            boundary_layer_silhouette=0.86,
            reflection_pair_partner_idx=None,
            cls="standard_quad_factor",
            cls_post_fold="cyclotomic_noise",
        )


def test_record_validation_rejects_mismatched_cyc_lists():
    with pytest.raises(ValueError):
        BoundaryLayerRecord(
            poly_coefficients=[1] * 15,
            mahler_measure_dps30=1.0,
            mahler_measure_dps60=1.0,
            mahler_measure_dps100=1.0,
            factor_list_strategy="factor_first",
            n_irreducible_factors=1,
            cyclotomic_factor_indices=[1, 2],
            cyclotomic_factor_powers=[3],  # length mismatch
            non_cyclotomic_factor_present=False,
            non_cyclotomic_factor_mahler=None,
            verification_failed=False,
            catalog_match_type="all_cyclotomic",
            boundary_layer_silhouette=0.86,
            reflection_pair_partner_idx=None,
            cls="standard_quad_factor",
            cls_post_fold="cyclotomic_noise",
        )
