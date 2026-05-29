"""Tests for rank-expansion test (Phase 1C ITER-43)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    AXIS_PLUGIN,
    N_AXES,
    KillTensor,
)
from charon.agents.erebos._rank_expansion import (
    RankComparison,
    RankSnapshot,
    StallReport,
    compare_snapshots,
    consecutive_zero_growth_run,
    is_stalled,
)


# ---------------------------------------------------------------------
# Snapshot capture
# ---------------------------------------------------------------------

def test_empty_tensor_snapshot():
    t = KillTensor()
    s = RankSnapshot.take(t, timestamp=0)
    assert s.n_populated == 0
    assert s.axis_cardinalities == (0, 0, 0, 0)
    assert s.density is None
    assert s.n_total_count == 0


def test_snapshot_captures_cardinalities():
    t = KillTensor()
    t.add_cell("g10", "d1", "i1", "k1")
    t.add_cell("g10", "d1", "i2", "k1")  # +1 invariant
    t.add_cell("g11", "d2", "i1", "k2")  # +1 plugin, +1 domain, +1 kp
    s = RankSnapshot.take(t, timestamp="t1")
    assert s.axis_cardinalities == (2, 2, 2, 2)
    assert s.n_populated == 3
    # 3 populated / 16 possible
    assert s.density == pytest.approx(3 / 16)


def test_snapshot_density_handles_total_count():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k", count=5)
    s = RankSnapshot.take(t, timestamp=1)
    assert s.n_total_count == 5
    assert s.n_populated == 1
    assert s.density == 1.0  # single cell, 1x1x1x1 box


def test_snapshot_is_frozen():
    s = RankSnapshot.take(KillTensor(), timestamp=0)
    with pytest.raises((AttributeError, Exception)):
        s.n_populated = 999  # type: ignore[misc]


def test_snapshot_timestamp_is_caller_supplied_object():
    """Any sortable type works for timestamp; primitive doesn't parse."""
    iso = "2026-05-29T12:00:00Z"
    s = RankSnapshot.take(KillTensor(), timestamp=iso)
    assert s.timestamp == iso

    int_ts = RankSnapshot.take(KillTensor(), timestamp=42)
    assert int_ts.timestamp == 42


# ---------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------

def test_compare_two_identical_snapshots():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    s2 = RankSnapshot.take(t, timestamp=2)
    cmp = compare_snapshots(s1, s2)
    assert cmp.delta_populated == 0
    assert cmp.delta_axis_cardinalities == (0, 0, 0, 0)
    assert cmp.growing() is False
    assert cmp.populated_grew() is False
    assert cmp.any_axis_grew() is False


def test_compare_detects_populated_growth():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    # Add a cell that reuses existing axis values -> only n_populated grows
    t.add_cell("g10", "d", "i", "k_new")  # +1 populated, +1 kp axis
    s2 = RankSnapshot.take(t, timestamp=2)
    cmp = compare_snapshots(s1, s2)
    assert cmp.delta_populated == 1
    assert cmp.delta_axis_cardinalities == (0, 0, 0, 1)
    assert cmp.populated_grew() is True
    assert cmp.any_axis_grew() is True
    assert cmp.growing() is True


def test_compare_detects_axis_only_growth_via_reused_count():
    """A new plugin added on existing (domain, invariant, kp) grows
    populated AND the plugin axis."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g11", "d", "i", "k")
    s2 = RankSnapshot.take(t, timestamp=2)
    cmp = compare_snapshots(s1, s2)
    assert cmp.delta_axis_cardinalities[AXIS_PLUGIN] == 1
    assert cmp.delta_populated == 1


def test_compare_is_frozen():
    s = RankSnapshot.take(KillTensor(), timestamp=0)
    cmp = compare_snapshots(s, s)
    with pytest.raises((AttributeError, Exception)):
        cmp.delta_populated = 99  # type: ignore[misc]


# ---------------------------------------------------------------------
# is_stalled: too-few snapshots
# ---------------------------------------------------------------------

def test_is_stalled_with_zero_snapshots_returns_not_stalled():
    r = is_stalled([])
    assert r.is_stalled is False
    assert "fewer than 2" in r.notes


def test_is_stalled_with_one_snapshot_returns_not_stalled():
    s = RankSnapshot.take(KillTensor(), timestamp=0)
    r = is_stalled([s])
    assert r.is_stalled is False
    assert r.n_snapshots_examined == 1


# ---------------------------------------------------------------------
# is_stalled: flat substrate
# ---------------------------------------------------------------------

def test_is_stalled_when_no_growth_across_window():
    """All snapshots identical -> stalled."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    snapshots = [
        RankSnapshot.take(t, timestamp=i) for i in range(5)
    ]
    r = is_stalled(snapshots, window=5)
    assert r.is_stalled is True
    assert "STALLED" in r.notes
    # All axes flat
    assert set(r.stalled_axes) == set(range(N_AXES))


def test_is_stalled_false_when_populated_grew():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k1")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g10", "d", "i", "k2")  # populated grew
    s2 = RankSnapshot.take(t, timestamp=2)
    r = is_stalled([s1, s2], window=2)
    assert r.is_stalled is False


def test_is_stalled_false_when_plugin_axis_grew():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g11", "d", "i", "k")  # plugin axis grew
    s2 = RankSnapshot.take(t, timestamp=2)
    r = is_stalled([s1, s2], window=2)
    assert r.is_stalled is False
    assert AXIS_PLUGIN in r.growing_axes


# ---------------------------------------------------------------------
# is_stalled: partial stalls (per-axis diagnosis)
# ---------------------------------------------------------------------

def test_partial_stall_reports_which_axes_are_stalled():
    """Plugin axis grew; domain / invariant / kp didn't."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g11", "d", "i", "k")  # only plugin axis grew
    s2 = RankSnapshot.take(t, timestamp=2)
    r = is_stalled([s1, s2], window=2)
    # Plugin grew; others stalled
    assert AXIS_PLUGIN in r.growing_axes
    assert AXIS_DOMAIN in r.stalled_axes
    # Substrate not fully stalled
    assert r.is_stalled is False


# ---------------------------------------------------------------------
# is_stalled: configurable thresholds
# ---------------------------------------------------------------------

def test_custom_per_axis_threshold():
    """Bump plugin threshold to require >= 2 new plugins per
    window. A single new plugin is then NOT enough to count as
    growing."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g11", "d", "i", "k")  # +1 plugin
    s2 = RankSnapshot.take(t, timestamp=2)
    r = is_stalled(
        [s1, s2], window=2,
        threshold_per_axis={AXIS_PLUGIN: 1},  # require > 1
    )
    # Plugin delta == 1, threshold > 1 -> plugin axis NOW stalled
    assert AXIS_PLUGIN in r.stalled_axes


def test_custom_populated_threshold():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k1")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g10", "d", "i", "k2")  # +1 populated, +1 kp
    s2 = RankSnapshot.take(t, timestamp=2)
    # Require > 5 new populated cells per window
    r = is_stalled(
        [s1, s2], window=2,
        threshold_populated=5,
        # Also set kp axis threshold high so it doesn't save the day
        threshold_per_axis={AXIS_KP: 5},
    )
    # populated delta=1, threshold > 5 -> populated stalled
    # kp delta=1, threshold > 5 -> kp stalled
    # plugin/domain/invariant unchanged -> stalled (default threshold > 0)
    assert r.is_stalled is True


# ---------------------------------------------------------------------
# is_stalled: window slicing
# ---------------------------------------------------------------------

def test_is_stalled_only_examines_last_window():
    """Earlier snapshots that show growth are ignored by the
    window. If the trailing `window` snapshots are flat, the
    substrate IS stalled for that window even with historical
    growth."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k1")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g11", "d", "i", "k1")
    s2 = RankSnapshot.take(t, timestamp=2)
    # Now stall: no further changes
    s3 = RankSnapshot.take(t, timestamp=3)
    s4 = RankSnapshot.take(t, timestamp=4)
    s5 = RankSnapshot.take(t, timestamp=5)
    snapshots = [s1, s2, s3, s4, s5]

    # Full history -> grew between s1 and s5; NOT stalled
    r_full = is_stalled(snapshots, window=5)
    assert r_full.is_stalled is False

    # Last 3 -> all identical; stalled
    r_recent = is_stalled(snapshots, window=3)
    assert r_recent.is_stalled is True


def test_is_stalled_window_larger_than_snapshot_count():
    """window > len(snapshots) just uses all of them."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s = [RankSnapshot.take(t, timestamp=i) for i in range(3)]
    r = is_stalled(s, window=100)
    assert r.n_snapshots_examined == 3


# ---------------------------------------------------------------------
# consecutive_zero_growth_run
# ---------------------------------------------------------------------

def test_consecutive_zero_run_zero_when_grew_last_step():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k1")
    s1 = RankSnapshot.take(t, timestamp=1)
    t.add_cell("g10", "d", "i", "k2")
    s2 = RankSnapshot.take(t, timestamp=2)
    assert consecutive_zero_growth_run([s1, s2]) == 0


def test_consecutive_zero_run_counts_trailing_zeros():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    s1 = RankSnapshot.take(t, timestamp=1)
    s2 = RankSnapshot.take(t, timestamp=2)
    s3 = RankSnapshot.take(t, timestamp=3)
    s4 = RankSnapshot.take(t, timestamp=4)
    # All identical -> 3 trailing zeros (s4-s3, s3-s2, s2-s1)
    assert consecutive_zero_growth_run([s1, s2, s3, s4]) == 3


def test_consecutive_zero_run_stops_at_growth():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k1")
    s1 = RankSnapshot.take(t, timestamp=1)
    # Add growth
    t.add_cell("g10", "d", "i", "k2")
    s2 = RankSnapshot.take(t, timestamp=2)
    # Then stall
    s3 = RankSnapshot.take(t, timestamp=3)
    s4 = RankSnapshot.take(t, timestamp=4)
    # Trailing: s4-s3 zero; s3-s2 zero; s2-s1 nonzero -> stop
    # consecutive zeros = 2
    assert consecutive_zero_growth_run([s1, s2, s3, s4]) == 2


def test_consecutive_zero_run_empty_input():
    assert consecutive_zero_growth_run([]) == 0
    s = RankSnapshot.take(KillTensor(), timestamp=0)
    assert consecutive_zero_growth_run([s]) == 0


# ---------------------------------------------------------------------
# Integration: realistic stall scenario (mirrors Techne 90-zero)
# ---------------------------------------------------------------------

def test_techne_style_long_zero_streak_is_stalled():
    """Simulate Techne's pattern: tensor grew early, then 90+
    consecutive snapshots with no new populated cells."""
    t = KillTensor()
    # Early growth phase
    snapshots = []
    for i, kp in enumerate(["kp_a", "kp_b", "kp_c", "kp_d"]):
        t.add_cell("g10", "d", "i", kp)
        snapshots.append(RankSnapshot.take(t, timestamp=f"t{i}"))
    # 20 stall snapshots
    for i in range(20):
        snapshots.append(RankSnapshot.take(t, timestamp=f"t_stall_{i}"))

    # Full window from start to end will show growth
    r_full = is_stalled(snapshots, window=len(snapshots))
    assert r_full.is_stalled is False

    # Last 10 snapshots should show stall
    r_recent = is_stalled(snapshots, window=10)
    assert r_recent.is_stalled is True

    # The trailing-zero counter mirrors Techne's "N consecutive
    # 0-promoted" headline metric
    assert consecutive_zero_growth_run(snapshots) >= 19
