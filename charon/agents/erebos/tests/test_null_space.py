"""Tests for null-space detection (Phase 1C ITER-42)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    AXIS_PLUGIN,
    KillTensor,
)
from charon.agents.erebos._null_space import (
    NullSpaceResult,
    Void,
    find_voids,
    find_voids_all_scans,
)


# ---------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------

def test_find_voids_rejects_wrong_axis_count():
    t = KillTensor()
    with pytest.raises(ValueError, match="3 of 4"):
        find_voids(t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN))


def test_find_voids_rejects_out_of_range_axis():
    t = KillTensor()
    with pytest.raises(ValueError, match="in 0..3"):
        find_voids(t, fix_axes=(0, 1, 99))


def test_find_voids_rejects_duplicate_axes():
    t = KillTensor()
    with pytest.raises(ValueError, match="duplicates"):
        find_voids(t, fix_axes=(0, 0, 1))


# ---------------------------------------------------------------------
# Empty / trivial inputs
# ---------------------------------------------------------------------

def test_empty_tensor_has_no_voids():
    t = KillTensor()
    r = find_voids(t)
    assert r.voids == ()
    assert r.n_frames_scanned == 0


def test_single_cell_has_no_voids():
    """One frame, one populated value -> nothing to be void OF."""
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp")
    r = find_voids(t)
    assert r.voids == ()


def test_single_frame_multiple_values_has_no_voids():
    """One frame with multiple kps -> no other frame to compare
    against -> no voids."""
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a")
    t.add_cell("g10", "mahler", "M", "kp_b")
    r = find_voids(t)
    # Single frame -> score = 0 by definition
    assert r.voids == ()


# ---------------------------------------------------------------------
# Fully-dense -> no voids
# ---------------------------------------------------------------------

def test_fully_dense_box_has_no_voids():
    """Every (frame, scan_value) cell populated -> zero voids."""
    t = KillTensor()
    for plugin in ("g10", "g11"):
        for kp in ("kp_a", "kp_b"):
            t.add_cell(plugin, "d", "i", kp)
    # Frame = (plugin, d, i); scan = kp; every frame has both kps
    r = find_voids(t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT))
    assert r.voids == ()
    assert r.n_frames_scanned == 2


# ---------------------------------------------------------------------
# Single void detection
# ---------------------------------------------------------------------

def test_single_void_detected_with_correct_score():
    """g10 has kp_a + kp_b; g11 only has kp_a. The cell
    (g11, d, i, kp_b) is a void of score 1.0 (kp_b is populated
    for 1 of 1 other frame)."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    t.add_cell("g10", "d", "i", "kp_b")
    t.add_cell("g11", "d", "i", "kp_a")
    r = find_voids(t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT))
    assert len(r.voids) == 1
    v = r.voids[0]
    assert v.frame_key == ("g11", "d", "i")
    assert v.missing_value == "kp_b"
    assert v.score == 1.0
    assert v.scan_axis == AXIS_KP
    assert v.n_frames_with_value == 1
    assert v.n_total_frames == 2


# ---------------------------------------------------------------------
# Score: globally-rare value -> low void score
# ---------------------------------------------------------------------

def test_globally_rare_missing_value_yields_low_score():
    """kp_rare appears in only 1 of 5 frames. Its absence from
    the other 4 yields voids of score = 1/4 = 0.25."""
    t = KillTensor()
    for plugin in ("g1", "g2", "g3", "g4", "g5"):
        t.add_cell(plugin, "d", "i", "kp_common")
    t.add_cell("g1", "d", "i", "kp_rare")
    # No min_score filter
    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
        min_score=0.0,
    )
    # 4 voids of (gi, d, i, kp_rare) for i in 2..5
    rare_voids = [v for v in r.voids if v.missing_value == "kp_rare"]
    assert len(rare_voids) == 4
    assert all(v.score == 0.25 for v in rare_voids)


def test_globally_common_missing_value_yields_high_score():
    """kp_common appears in 4/5 frames; absence from the 5th
    yields a high-score void."""
    t = KillTensor()
    for plugin in ("g1", "g2", "g3", "g4"):
        t.add_cell(plugin, "d", "i", "kp_common")
    t.add_cell("g5", "d", "i", "kp_other")
    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
        min_score=0.0,
    )
    void_for_g5 = [v for v in r.voids
                   if v.frame_key == ("g5", "d", "i")
                   and v.missing_value == "kp_common"]
    assert len(void_for_g5) == 1
    # 4 OTHER frames out of 4 others have kp_common -> score 1.0
    assert void_for_g5[0].score == 1.0


# ---------------------------------------------------------------------
# Threshold filter
# ---------------------------------------------------------------------

def test_min_score_filter_excludes_low_scores():
    """Set min_score = 0.5; only voids with score >= 0.5 returned."""
    t = KillTensor()
    for plugin in ("g1", "g2", "g3", "g4", "g5"):
        t.add_cell(plugin, "d", "i", "kp_common")
    t.add_cell("g1", "d", "i", "kp_rare")
    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
        min_score=0.5,
    )
    # All "kp_rare" voids have score 0.25 -> excluded
    assert all(v.missing_value != "kp_rare" for v in r.voids)
    # n_voids_before_threshold should reflect the 4 filtered voids
    assert r.n_voids_before_threshold == 4


# ---------------------------------------------------------------------
# Different scan axes
# ---------------------------------------------------------------------

def test_scan_along_domain_axis_works():
    """Fix (plugin, invariant, kp); scan domain. Detect missing
    domains."""
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp")
    t.add_cell("g10", "BSD",    "M", "kp")
    t.add_cell("g11", "mahler", "M", "kp")
    # Frames: (g10, M, kp), (g11, M, kp). g10 has {mahler, BSD}; g11
    # has only {mahler}. Void: (g11, M, kp, BSD).
    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_INVARIANT, AXIS_KP),
        min_score=0.0,
    )
    assert len(r.voids) == 1
    v = r.voids[0]
    assert v.scan_axis == AXIS_DOMAIN
    assert v.frame_key == ("g11", "M", "kp")
    assert v.missing_value == "BSD"


def test_scan_along_invariant_axis_works():
    """Fix (plugin, domain, kp); scan invariant."""
    t = KillTensor()
    t.add_cell("g10", "d", "inv_1", "kp")
    t.add_cell("g10", "d", "inv_2", "kp")
    t.add_cell("g11", "d", "inv_1", "kp")
    # Frame (g11, d, kp) missing inv_2
    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_KP),
        min_score=0.0,
    )
    voids = [v for v in r.voids if v.frame_key == ("g11", "d", "kp")]
    assert len(voids) == 1
    assert voids[0].missing_value == "inv_2"


def test_scan_along_plugin_axis_works():
    """Fix (domain, invariant, kp); scan plugin."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    t.add_cell("g11", "d", "i", "kp_a")
    t.add_cell("g10", "d", "i", "kp_b")
    # Frame (d, i, kp_b) missing g11
    r = find_voids(
        t, fix_axes=(AXIS_DOMAIN, AXIS_INVARIANT, AXIS_KP),
        min_score=0.0,
    )
    voids = [v for v in r.voids if v.frame_key == ("d", "i", "kp_b")]
    assert len(voids) == 1
    assert voids[0].missing_value == "g11"


# ---------------------------------------------------------------------
# Sort + cap
# ---------------------------------------------------------------------

def test_voids_sorted_by_score_desc():
    """Highest-score voids come first."""
    t = KillTensor()
    # kp_high: populated for 3/4 frames -> missing from 1 -> score 3/3
    for plugin in ("g1", "g2", "g3"):
        t.add_cell(plugin, "d", "i", "kp_high")
    # kp_low: populated for 1/4 frames -> missing from 3 -> score 1/3
    t.add_cell("g1", "d", "i", "kp_low")
    # Need a 4th frame to have something be missing
    t.add_cell("g4", "d", "i", "kp_other")

    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
        min_score=0.0,
    )
    assert len(r.voids) > 1
    # All high-score voids should come before any low-score
    scores = [v.score for v in r.voids]
    assert scores == sorted(scores, reverse=True)


def test_sample_limit_caps_results():
    """sample_limit truncates output."""
    t = KillTensor()
    # Many frames, each missing many values, so many voids
    for plugin in [f"g{i}" for i in range(10)]:
        t.add_cell(plugin, "d", "i", "kp_common")
    # Each frame missing 9 OTHER plugin's "kp_x" cells, but we
    # need other values. Add a unique kp for each frame:
    for plugin in [f"g{i}" for i in range(10)]:
        t.add_cell(plugin, "d", "i", f"kp_{plugin}")
    # Total scan values: 10 unique kps + 1 = 11 values per frame
    # Each frame has 2 populated -> 9 missing per frame x 10 frames
    r = find_voids(
        t, fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
        min_score=0.0,
        sample_limit=10,
    )
    assert len(r.voids) <= 10
    assert "truncated" in r.notes


# ---------------------------------------------------------------------
# find_voids_all_scans
# ---------------------------------------------------------------------

def test_find_voids_all_scans_returns_one_per_axis():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    t.add_cell("g10", "d", "i", "kp_b")
    t.add_cell("g11", "d", "i", "kp_a")
    results = find_voids_all_scans(t, min_score=0.0)
    assert set(results.keys()) == {"plugin", "domain", "invariant", "kp"}
    for r in results.values():
        assert isinstance(r, NullSpaceResult)


# ---------------------------------------------------------------------
# Void is frozen / hashable
# ---------------------------------------------------------------------

def test_void_is_frozen():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    t.add_cell("g10", "d", "i", "kp_b")
    t.add_cell("g11", "d", "i", "kp_a")
    r = find_voids(t)
    if r.voids:
        v = r.voids[0]
        with pytest.raises((AttributeError, Exception)):
            v.score = 0.0  # type: ignore[misc]


def test_void_axis_name_helpers():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    t.add_cell("g10", "d", "i", "kp_b")
    t.add_cell("g11", "d", "i", "kp_a")
    r = find_voids(t)
    v = r.voids[0]
    assert v.axis_name() == "kp"
    assert v.frame_axis_names() == ("plugin", "domain", "invariant")


# ---------------------------------------------------------------------
# Integration: realistic substrate scenario
# ---------------------------------------------------------------------

def test_void_for_g23_in_a_domain_where_other_plugins_fired():
    """Realistic-ish: g10 + g11 fire in Mahler domain producing kp_a;
    g23 never fired in Mahler but fired in BSD. The (g23, Mahler,
    M, kp_a) cell is a void candidate."""
    t = KillTensor()
    # Mahler-context emissions
    t.add_cell("g10_boundary", "mahler", "M", "kp_a")
    t.add_cell("g11_exception_miner", "mahler", "M", "kp_a")
    # g23 elsewhere
    t.add_cell("g23_asymptotic_limit", "BSD", "regulator", "kp_a")

    # Scan plugin axis: which plugins are missing from each
    # (domain, invariant, kp) frame?
    r = find_voids(
        t, fix_axes=(AXIS_DOMAIN, AXIS_INVARIANT, AXIS_KP),
        min_score=0.0,
    )

    # Frame (mahler, M, kp_a) should be missing g23
    void_g23_in_mahler = [
        v for v in r.voids
        if v.frame_key == ("mahler", "M", "kp_a")
        and v.missing_value == "g23_asymptotic_limit"
    ]
    assert len(void_g23_in_mahler) == 1
