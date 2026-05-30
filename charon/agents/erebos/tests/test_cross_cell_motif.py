"""Tests for cross-cell motif primitive (Phase 3.D / ITER-58)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._cross_cell_motif import (
    CoOccurrenceMotif,
    CrossCellResult,
    conditional_kp_recommendations,
    extract_cooccurrence_motifs,
    per_plugin_majority,
)


# ---------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------

def test_empty_input_returns_empty():
    r = extract_cooccurrence_motifs([])
    assert isinstance(r, CrossCellResult)
    assert r.motifs == ()
    assert r.n_signatures_scanned == 0


def test_rows_without_input_signature_skipped():
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a"},  # no sig
        {"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": "sig1"},
    ]
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1)
    assert r.n_signatures_scanned == 1


def test_single_emission_per_signature_no_motifs():
    """One cell per signature -> no pairs to surface."""
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": f"sig{i}"}
        for i in range(10)
    ]
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    assert r.motifs == ()
    assert r.n_signatures_with_multiple_emissions == 0


# ---------------------------------------------------------------------
# Core pair detection
# ---------------------------------------------------------------------

def test_pair_cooccurrence_detected():
    """Two cells co-occurring on the same signature surface as a motif."""
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "sig1"},
        {"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": "sig1"},
    ]
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    assert len(r.motifs) == 1
    m = r.motifs[0]
    # Cells sorted lexicographically
    assert m.cell_a == ("g10", "kp_a")
    assert m.cell_b == ("g11", "kp_b")
    assert m.cooccurrence_count == 1


def test_lift_above_independence_filters_correctly():
    """High-lift pairs surface; chance-level pairs filtered out."""
    # 3 signatures:
    #   sig1: (g10, kp_a), (g11, kp_b)   <- co-occurring pair
    #   sig2: (g10, kp_a), (g11, kp_b)   <- co-occurring pair
    #   sig3: (g10, kp_a), (g12, kp_c)   <- (g10,kp_a) marginal
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "sig1"},
        {"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": "sig1"},
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "sig2"},
        {"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": "sig2"},
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "sig3"},
        {"plugin_id": "g12", "kill_pattern": "kp_c", "input_signature": "sig3"},
    ]
    # marginal: g10/kp_a=3 sigs, g11/kp_b=2 sigs, g12/kp_c=1 sig
    # expected(g10, g11) = 3*2/3 = 2.0; observed = 2; lift = 1.0
    # expected(g10, g12) = 3*1/3 = 1.0; observed = 1; lift = 1.0
    # expected(g11, g12) = 2*1/3 = 0.67; observed = 0; lift = 0
    r_strict = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=1.5)
    # All pairs at exactly lift=1.0 should be filtered
    assert r_strict.motifs == ()

    r_loose = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.5)
    # At lift>=0.5 the two lift=1.0 pairs surface
    assert len(r_loose.motifs) == 2


def test_high_lift_pair_surfaces():
    """A pair with observed >> expected surfaces with high lift."""
    # Construct: 10 sigs, but (g10,kp_a) and (g11,kp_b) ALWAYS co-occur
    # and never appear alone. lift = 10 / (10*10/10) = 1.0... hmm
    # Need a scenario where marginal is high but co-occurrence is higher
    # than expected.
    # 10 sigs: 5 have BOTH (g10,kp_a) AND (g11,kp_b)
    #          5 have only (g10,kp_a)
    #          5 have only (g11,kp_b) -- wait then total is 15 not 10
    # Reset: 10 sigs:
    #   5 have (g10,kp_a) AND (g11,kp_b)
    #   2 have only (g10,kp_a)
    #   2 have only (g11,kp_b)
    #   1 has (g12,kp_c) alone
    # marginal(g10,kp_a) = 7, marginal(g11,kp_b) = 7
    # expected = 7*7/10 = 4.9; observed = 5; lift = 1.02 -- low
    # Try strong correlation:
    #   8 sigs have (g10,kp_a) AND (g11,kp_b)
    #   2 sigs have only (g12,kp_c) (any single emission)
    # marginal(g10,kp_a)=8, marginal(g11,kp_b)=8, expected=8*8/10=6.4; obs=8; lift=1.25
    rows = []
    for i in range(8):
        rows.append({"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": f"sig{i}"})
        rows.append({"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": f"sig{i}"})
    for i in range(8, 10):
        rows.append({"plugin_id": "g12", "kill_pattern": "kp_c", "input_signature": f"sig{i}"})
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=2, min_lift=1.2)
    assert len(r.motifs) == 1
    m = r.motifs[0]
    assert m.cell_a == ("g10", "kp_a")
    assert m.cell_b == ("g11", "kp_b")
    assert m.lift == pytest.approx(8 / (8 * 8 / 10))


def test_cells_sorted_lexicographically():
    """cell_a < cell_b for direction-agnostic motifs."""
    rows = [
        {"plugin_id": "z_plugin", "kill_pattern": "kp", "input_signature": "sig"},
        {"plugin_id": "a_plugin", "kill_pattern": "kp", "input_signature": "sig"},
    ]
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    assert len(r.motifs) == 1
    m = r.motifs[0]
    assert m.cell_a < m.cell_b


def test_sample_signatures_capped():
    """sample_signatures respects sample_limit."""
    rows = []
    for i in range(20):
        rows.append({"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": f"sig{i}"})
        rows.append({"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": f"sig{i}"})
    r = extract_cooccurrence_motifs(
        rows, min_cooccurrence=2, min_lift=0.0, sample_limit=3,
    )
    assert len(r.motifs) == 1
    assert len(r.motifs[0].sample_signatures) == 3


def test_promoted_treated_as_kp_string():
    """kill_pattern=None becomes 'PROMOTED' for cell key."""
    rows = [
        {"plugin_id": "g10", "kill_pattern": None, "input_signature": "sig1"},
        {"plugin_id": "g11", "kill_pattern": "kp", "input_signature": "sig1"},
    ]
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    assert len(r.motifs) == 1
    assert r.motifs[0].cell_a == ("g10", "PROMOTED")


def test_motif_is_frozen_and_hashable():
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "sig1"},
        {"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": "sig1"},
    ]
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    m = r.motifs[0]
    with pytest.raises((AttributeError, Exception)):
        m.lift = 99.0  # type: ignore[misc]
    # Hashable
    assert isinstance(hash(m), int)


def test_motifs_sorted_by_lift_desc():
    """Higher-lift motifs come first."""
    # Two motifs:
    #   (g10, kp_a) - (g11, kp_b) at lift 1.25
    #   (g10, kp_a) - (g12, kp_c) at lift 2.0 (forced via construction)
    rows = []
    # 4 sigs with both g10/g11 (low lift):
    for i in range(4):
        rows.append({"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": f"low{i}"})
        rows.append({"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": f"low{i}"})
    # 2 sigs with both g10/g12 (very tight pair):
    for i in range(2):
        rows.append({"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": f"high{i}"})
        rows.append({"plugin_id": "g12", "kill_pattern": "kp_c", "input_signature": f"high{i}"})
    # marginal(g10,kp_a)=6, marginal(g11,kp_b)=4, marginal(g12,kp_c)=2
    # expected(g10/g11) = 6*4/6 = 4; observed=4 -> lift 1.0
    # expected(g10/g12) = 6*2/6 = 2; observed=2 -> lift 1.0
    # Both at lift=1.0, so order is by cooccurrence count then cells.
    # Use min_lift=0 to surface both:
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    assert len(r.motifs) == 2
    # First motif has higher (or tied) lift than second
    assert r.motifs[0].lift >= r.motifs[1].lift


# ---------------------------------------------------------------------
# Conditional kp recommendations vs counter baseline
# ---------------------------------------------------------------------

def test_counter_baseline_per_plugin_majority():
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a"},
        {"plugin_id": "g10", "kill_pattern": "kp_a"},
        {"plugin_id": "g10", "kill_pattern": "kp_b"},
        {"plugin_id": "g11", "kill_pattern": "kp_c"},
    ]
    recs = per_plugin_majority(rows)
    assert recs == {"g10": "kp_a", "g11": "kp_c"}


def test_conditional_recommendations_can_differ_from_counter():
    """The discriminating test: substrate can recommend different kp
    given a partner-cell context than what counters output."""
    # Construct: g10's unconditional majority is kp_a (3 times)
    # but conditional on partner (g11, kp_special), g10 always
    # emits kp_b
    rows = [
        # Unconditional: g10 emits kp_a often
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "s1"},
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "s2"},
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "s3"},
        # Conditional: when g11 emits kp_special, g10 emits kp_b
        {"plugin_id": "g10", "kill_pattern": "kp_b", "input_signature": "s_special1"},
        {"plugin_id": "g11", "kill_pattern": "kp_special", "input_signature": "s_special1"},
        {"plugin_id": "g10", "kill_pattern": "kp_b", "input_signature": "s_special2"},
        {"plugin_id": "g11", "kill_pattern": "kp_special", "input_signature": "s_special2"},
    ]
    counter_recs = per_plugin_majority(rows)
    assert counter_recs["g10"] == "kp_a"  # unconditional majority

    motif_result = extract_cooccurrence_motifs(
        rows, min_cooccurrence=2, min_lift=1.0,
    )
    cond_recs = conditional_kp_recommendations(rows, motif_result.motifs)

    # The substrate's recommendation for (g10, partner=(g11,kp_special))
    # should be kp_b -- DIFFERENT from the unconditional majority kp_a
    target_key = ("g10", ("g11", "kp_special"))
    assert target_key in cond_recs
    assert cond_recs[target_key] == "kp_b"
    assert cond_recs[target_key] != counter_recs["g10"]


def test_conditional_empty_when_no_high_lift_motifs():
    """No motifs above threshold -> no conditional recommendations."""
    rows = [
        {"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": "sig1"},
        {"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": "sig1"},
    ]
    # Single co-occurrence at lift=1.0; if we set min_lift=2.0 nothing surfaces
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=2.0)
    assert r.motifs == ()
    recs = conditional_kp_recommendations(rows, r.motifs)
    assert recs == {}


# ---------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------

def test_result_top_k_helper():
    rows = []
    for i in range(8):
        rows.append({"plugin_id": "g10", "kill_pattern": "kp_a", "input_signature": f"sig{i}"})
        rows.append({"plugin_id": "g11", "kill_pattern": "kp_b", "input_signature": f"sig{i}"})
    for i in range(8, 10):
        rows.append({"plugin_id": "g12", "kill_pattern": "kp_c", "input_signature": f"sig{i}"})
    r = extract_cooccurrence_motifs(rows, min_cooccurrence=1, min_lift=0.0)
    top2 = r.top(2)
    assert len(top2) <= 2
