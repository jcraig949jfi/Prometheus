"""Tests for motif extraction Layer 2 primitive (Phase 1C ITER-40)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._motif_extraction import (
    ALL_MOTIF_TYPES,
    MOTIF_CONFUSION,
    MOTIF_KP_CHAIN,
    MOTIF_PLUGIN_DOMAIN_KP,
    MOTIF_PLUGIN_KP,
    Motif,
    MotifExtractionResult,
    extract_all_motifs,
    extract_confusion_motifs,
    extract_kp_chain_motifs,
    extract_plugin_domain_kp_motifs,
    extract_plugin_kp_motifs,
)


# ---------------------------------------------------------------------
# Empty / degenerate inputs
# ---------------------------------------------------------------------

def test_empty_rows_returns_empty_result():
    """All extractors handle empty input without crashing."""
    for fn in (
        extract_plugin_kp_motifs,
        extract_plugin_domain_kp_motifs,
        extract_kp_chain_motifs,
        extract_confusion_motifs,
    ):
        r = fn([])
        assert isinstance(r, MotifExtractionResult)
        assert r.motifs == ()
        assert r.n_rows_scanned == 0


def test_single_row_no_motifs_at_default_threshold():
    """A single row can't recur; min_count=2+ filters it out."""
    rows = [{"row_id": "r1", "plugin_id": "g02_contrast",
             "kill_pattern": "kp_x"}]
    r = extract_plugin_kp_motifs(rows, min_count=2)
    assert r.motifs == ()
    # Lower the threshold to 1 to verify the row WAS seen
    r2 = extract_plugin_kp_motifs(rows, min_count=1)
    assert len(r2.motifs) == 1
    assert r2.motifs[0].count == 1


def test_well_formed_denominator_excludes_malformed_rows():
    """Rows missing required keys are skipped from n_rows_scanned."""
    rows = [
        {"row_id": "r1", "plugin_id": "g10", "kill_pattern": "kp"},
        {"row_id": "r2"},  # no plugin_id
        {"row_id": "r3", "plugin_id": "g10", "kill_pattern": "kp"},
    ]
    r = extract_plugin_kp_motifs(rows, min_count=2)
    assert r.n_rows_scanned == 2  # the malformed row dropped


# ---------------------------------------------------------------------
# Extractor 1: plugin_kp
# ---------------------------------------------------------------------

def test_plugin_kp_counts_recurring_pairs():
    rows = [
        {"row_id": "r1", "plugin_id": "g10", "kill_pattern": "kp_a"},
        {"row_id": "r2", "plugin_id": "g10", "kill_pattern": "kp_a"},
        {"row_id": "r3", "plugin_id": "g10", "kill_pattern": "kp_a"},
        {"row_id": "r4", "plugin_id": "g11", "kill_pattern": "kp_b"},
    ]
    r = extract_plugin_kp_motifs(rows, min_count=2)
    assert len(r.motifs) == 1
    motif = r.motifs[0]
    assert motif.key == ("g10", "kp_a")
    assert motif.count == 3
    assert motif.fraction == pytest.approx(3 / 4)
    assert motif.sample_row_ids == ("r1", "r2", "r3")


def test_plugin_kp_promoted_uses_sentinel():
    """A row with kill_pattern=None becomes ('plugin', 'PROMOTED')."""
    rows = [
        {"row_id": "r1", "plugin_id": "g02", "kill_pattern": None},
        {"row_id": "r2", "plugin_id": "g02", "kill_pattern": None},
        {"row_id": "r3", "plugin_id": "g02"},  # missing key too
    ]
    r = extract_plugin_kp_motifs(rows, min_count=2)
    assert len(r.motifs) == 1
    assert r.motifs[0].key == ("g02", "PROMOTED")
    assert r.motifs[0].count == 3


def test_plugin_kp_sort_is_count_desc_then_key_asc():
    rows = (
        [{"row_id": f"r{i}", "plugin_id": "g_top",
          "kill_pattern": "kp_top"} for i in range(5)]
        + [{"row_id": f"r{i}", "plugin_id": "g_zz",
            "kill_pattern": "kp_x"} for i in range(2)]
        + [{"row_id": f"r{i}", "plugin_id": "g_aa",
            "kill_pattern": "kp_x"} for i in range(2)]
    )
    r = extract_plugin_kp_motifs(rows, min_count=2)
    # g_top with count=5 comes first
    assert r.motifs[0].key == ("g_top", "kp_top")
    # Tie at count=2: g_aa comes before g_zz alphabetically
    assert r.motifs[1].key == ("g_aa", "kp_x")
    assert r.motifs[2].key == ("g_zz", "kp_x")


def test_plugin_kp_sample_row_ids_capped():
    rows = [
        {"row_id": f"r{i}", "plugin_id": "g10", "kill_pattern": "kp"}
        for i in range(20)
    ]
    r = extract_plugin_kp_motifs(rows, min_count=2, sample_limit=3)
    assert r.motifs[0].count == 20
    assert len(r.motifs[0].sample_row_ids) == 3
    assert r.motifs[0].sample_row_ids == ("r0", "r1", "r2")


# ---------------------------------------------------------------------
# Extractor 2: plugin_domain_kp (tensor cells)
# ---------------------------------------------------------------------

def test_plugin_domain_kp_separates_by_domain():
    """Same (plugin, kp) in two domains -> two motifs."""
    rows = [
        {"row_id": "r1", "plugin_id": "g10", "domain": "mahler",
         "kill_pattern": "kp_a"},
        {"row_id": "r2", "plugin_id": "g10", "domain": "mahler",
         "kill_pattern": "kp_a"},
        {"row_id": "r3", "plugin_id": "g10", "domain": "BSD",
         "kill_pattern": "kp_a"},
        {"row_id": "r4", "plugin_id": "g10", "domain": "BSD",
         "kill_pattern": "kp_a"},
    ]
    r = extract_plugin_domain_kp_motifs(rows, min_count=2)
    assert len(r.motifs) == 2
    keys = {m.key for m in r.motifs}
    assert ("g10", "BSD", "kp_a") in keys
    assert ("g10", "mahler", "kp_a") in keys


def test_plugin_domain_kp_default_domain_fills_missing():
    rows = [
        {"row_id": "r1", "plugin_id": "g10", "kill_pattern": "kp"},
        {"row_id": "r2", "plugin_id": "g10", "kill_pattern": "kp"},
    ]
    r = extract_plugin_domain_kp_motifs(
        rows, min_count=2, default_domain="unset"
    )
    assert len(r.motifs) == 1
    assert r.motifs[0].key == ("g10", "unset", "kp")


def test_plugin_domain_kp_key_shape_matches_tensor_cell():
    """Tensor v0 (ITER-41) will use 3-tuple (plugin, domain, kp)
    as cell key. Lock the shape here."""
    rows = [
        {"row_id": f"r{i}", "plugin_id": "p", "domain": "d",
         "kill_pattern": "k"} for i in range(3)
    ]
    r = extract_plugin_domain_kp_motifs(rows, min_count=2)
    assert len(r.motifs) == 1
    assert len(r.motifs[0].key) == 3


# ---------------------------------------------------------------------
# Extractor 3: kp_chain
# ---------------------------------------------------------------------

def test_kp_chain_pairs_consecutive_rows():
    rows = [
        {"row_id": "r1", "plugin_id": "p", "kill_pattern": "A"},
        {"row_id": "r2", "plugin_id": "p", "kill_pattern": "B"},
        {"row_id": "r3", "plugin_id": "p", "kill_pattern": "A"},
        {"row_id": "r4", "plugin_id": "p", "kill_pattern": "B"},
    ]
    # Pairs: (A,B), (B,A), (A,B). (A,B) appears 2x.
    r = extract_kp_chain_motifs(rows, min_count=2)
    assert len(r.motifs) == 1
    assert r.motifs[0].key == ("A", "B")
    assert r.motifs[0].count == 2


def test_kp_chain_breaks_on_malformed_row():
    """A row without plugin_id breaks the chain (no spurious pair)."""
    rows = [
        {"row_id": "r1", "plugin_id": "p", "kill_pattern": "A"},
        {"row_id": "r2"},  # break
        {"row_id": "r3", "plugin_id": "p", "kill_pattern": "B"},
    ]
    r = extract_kp_chain_motifs(rows, min_count=1)
    assert r.n_rows_scanned == 0
    assert r.motifs == ()


def test_kp_chain_empty_when_under_two_rows():
    r = extract_kp_chain_motifs(
        [{"row_id": "r1", "plugin_id": "p", "kill_pattern": "A"}],
        min_count=1,
    )
    assert r.motifs == ()


def test_kp_chain_promoted_uses_sentinel():
    rows = [
        {"row_id": "r1", "plugin_id": "p", "kill_pattern": "A"},
        {"row_id": "r2", "plugin_id": "p", "kill_pattern": None},
        {"row_id": "r3", "plugin_id": "p", "kill_pattern": "A"},
        {"row_id": "r4", "plugin_id": "p", "kill_pattern": None},
    ]
    # Pairs: (A,PROMOTED), (PROMOTED,A), (A,PROMOTED)
    r = extract_kp_chain_motifs(rows, min_count=2)
    keys = [m.key for m in r.motifs]
    assert ("A", "PROMOTED") in keys


# ---------------------------------------------------------------------
# Extractor 4: confusion
# ---------------------------------------------------------------------

def test_confusion_fires_on_conflicting_kps_for_same_input():
    rows = [
        {"row_id": "r1", "plugin_id": "p1", "kill_pattern": "kp_A",
         "input_signature": "sig:lehmer_x_phi16"},
        {"row_id": "r2", "plugin_id": "p2", "kill_pattern": "kp_B",
         "input_signature": "sig:lehmer_x_phi16"},
    ]
    r = extract_confusion_motifs(rows, min_distinct_kps=2)
    assert len(r.motifs) == 1
    motif = r.motifs[0]
    assert motif.key == ("sig:lehmer_x_phi16",)
    assert motif.count == 2
    # Payload carries the distinct kps as sorted tuple
    assert motif.sample_payload == ("kp_A", "kp_B")


def test_confusion_skips_signatures_with_only_one_kp():
    rows = [
        {"row_id": "r1", "plugin_id": "p1", "kill_pattern": "kp",
         "input_signature": "sig:stable"},
        {"row_id": "r2", "plugin_id": "p2", "kill_pattern": "kp",
         "input_signature": "sig:stable"},
        {"row_id": "r3", "plugin_id": "p1", "kill_pattern": "kp_A",
         "input_signature": "sig:conflicted"},
        {"row_id": "r4", "plugin_id": "p2", "kill_pattern": "kp_B",
         "input_signature": "sig:conflicted"},
    ]
    r = extract_confusion_motifs(rows, min_distinct_kps=2)
    assert len(r.motifs) == 1
    assert r.motifs[0].key == ("sig:conflicted",)


def test_confusion_promoted_vs_rejected_counts_as_conflict():
    """A signature that was PROMOTED once and REJECTED once is
    confused (the substrate's verdict is unstable)."""
    rows = [
        {"row_id": "r1", "plugin_id": "p", "kill_pattern": None,
         "input_signature": "sig:flippy"},
        {"row_id": "r2", "plugin_id": "p", "kill_pattern": "kp",
         "input_signature": "sig:flippy"},
    ]
    r = extract_confusion_motifs(rows, min_distinct_kps=2)
    assert len(r.motifs) == 1
    assert r.motifs[0].sample_payload == ("PROMOTED", "kp")


def test_confusion_skips_rows_without_signature():
    rows = [
        {"row_id": "r1", "plugin_id": "p", "kill_pattern": "kp"},
        {"row_id": "r2", "plugin_id": "p", "kill_pattern": "kp"},
    ]
    r = extract_confusion_motifs(rows)
    assert r.n_rows_scanned == 0
    assert r.motifs == ()


# ---------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------

def test_result_top_k_helper():
    rows = (
        [{"row_id": f"a{i}", "plugin_id": "p", "kill_pattern": "A"}
         for i in range(5)]
        + [{"row_id": f"b{i}", "plugin_id": "p", "kill_pattern": "B"}
           for i in range(4)]
        + [{"row_id": f"c{i}", "plugin_id": "p", "kill_pattern": "C"}
           for i in range(3)]
    )
    r = extract_plugin_kp_motifs(rows, min_count=2)
    top2 = r.top(2)
    assert len(top2) == 2
    assert top2[0].key == ("p", "A")
    assert top2[1].key == ("p", "B")


def test_result_count_at_or_above_helper():
    rows = (
        [{"row_id": f"a{i}", "plugin_id": "p", "kill_pattern": "A"}
         for i in range(10)]
        + [{"row_id": f"b{i}", "plugin_id": "p", "kill_pattern": "B"}
           for i in range(5)]
        + [{"row_id": f"c{i}", "plugin_id": "p", "kill_pattern": "C"}
           for i in range(2)]
    )
    r = extract_plugin_kp_motifs(rows, min_count=2)
    assert r.count_at_or_above(10) == 1
    assert r.count_at_or_above(5) == 2
    assert r.count_at_or_above(2) == 3


def test_motif_is_frozen():
    rows = [{"row_id": "r1", "plugin_id": "p", "kill_pattern": "k"},
            {"row_id": "r2", "plugin_id": "p", "kill_pattern": "k"}]
    r = extract_plugin_kp_motifs(rows, min_count=2)
    motif = r.motifs[0]
    with pytest.raises((AttributeError, Exception)):
        motif.count = 99  # type: ignore[misc]


def test_motif_is_hashable():
    """sample_row_ids and sample_payload are tuples so Motif hashes."""
    rows = [{"row_id": "r1", "plugin_id": "p", "kill_pattern": "k"},
            {"row_id": "r2", "plugin_id": "p", "kill_pattern": "k"}]
    r = extract_plugin_kp_motifs(rows, min_count=2)
    s = {r.motifs[0]}
    assert len(s) == 1


# ---------------------------------------------------------------------
# extract_all_motifs convenience
# ---------------------------------------------------------------------

def test_extract_all_motifs_runs_all_four():
    rows = [
        {"row_id": "r1", "plugin_id": "g10", "domain": "mahler",
         "kill_pattern": "A", "input_signature": "sig1"},
        {"row_id": "r2", "plugin_id": "g10", "domain": "mahler",
         "kill_pattern": "A", "input_signature": "sig1"},
        {"row_id": "r3", "plugin_id": "g11", "domain": "mahler",
         "kill_pattern": "B", "input_signature": "sig1"},
    ]
    bundle = extract_all_motifs(rows, min_count=2)
    assert set(bundle.keys()) == set(ALL_MOTIF_TYPES)
    for r in bundle.values():
        assert isinstance(r, MotifExtractionResult)


def test_extract_all_motifs_results_consistent_with_individual_calls():
    rows = [{"row_id": f"r{i}", "plugin_id": "g10",
             "kill_pattern": "A", "domain": "d"}
            for i in range(4)]
    bundle = extract_all_motifs(rows, min_count=2)
    direct = extract_plugin_kp_motifs(rows, min_count=2)
    assert bundle[MOTIF_PLUGIN_KP].motifs == direct.motifs
