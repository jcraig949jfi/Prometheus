"""Tests for kill tensor v0 (Phase 1C ITER-41)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    AXIS_NAMES,
    AXIS_PLUGIN,
    DEFAULT_DOMAIN,
    DEFAULT_INVARIANT,
    N_AXES,
    PROMOTED_KP,
    KillTensor,
)


# ---------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------

def test_empty_tensor_has_zero_state():
    t = KillTensor()
    assert t.n_populated_cells() == 0
    assert t.total_count() == 0
    assert t.populated_cells() == set()
    assert t.shape() == (0, 0, 0, 0)
    assert len(t) == 0


def test_add_cell_increments():
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a")
    assert t.cell("g10", "mahler", "M", "kp_a") == 1
    t.add_cell("g10", "mahler", "M", "kp_a")
    assert t.cell("g10", "mahler", "M", "kp_a") == 2
    assert t.n_populated_cells() == 1


def test_add_cell_with_explicit_count():
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a", count=5)
    assert t.cell("g10", "mahler", "M", "kp_a") == 5


def test_add_cell_zero_count_is_noop():
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a", count=0)
    assert t.n_populated_cells() == 0


def test_add_cell_negative_count_raises():
    t = KillTensor()
    with pytest.raises(ValueError, match="non-negative"):
        t.add_cell("g10", "mahler", "M", "kp_a", count=-1)


def test_add_row_skips_missing_plugin_id():
    t = KillTensor()
    assert t.add_row({"kill_pattern": "kp"}) is False
    assert t.n_populated_cells() == 0


def test_add_row_uses_default_domain_and_invariant():
    t = KillTensor()
    assert t.add_row({"plugin_id": "g10"}) is True
    # No domain / no invariant / no kill_pattern => defaults / PROMOTED
    assert t.cell("g10", DEFAULT_DOMAIN, DEFAULT_INVARIANT, PROMOTED_KP) == 1


def test_add_row_default_invariant_uses_input_signature():
    t = KillTensor()
    t.add_row({
        "plugin_id": "g10",
        "domain": "mahler",
        "kill_pattern": "kp",
        "input_signature": "sig:lehmer_x_phi16",
    })
    assert t.cell("g10", "mahler", "sig:lehmer_x_phi16", "kp") == 1


def test_add_row_invariant_field_overrides_input_signature():
    """Explicit row['invariant'] takes precedence over input_signature."""
    t = KillTensor()
    t.add_row({
        "plugin_id": "g10",
        "domain": "mahler",
        "kill_pattern": "kp",
        "invariant": "explicit_inv",
        "input_signature": "sig",
    })
    assert t.cell("g10", "mahler", "explicit_inv", "kp") == 1


def test_add_row_custom_invariant_extractor():
    t = KillTensor()
    t.add_row(
        {"plugin_id": "g10", "domain": "d", "kill_pattern": "k"},
        invariant_extractor=lambda r: "custom_inv",
    )
    assert t.cell("g10", "d", "custom_inv", "k") == 1


def test_from_ledger_rows_builds_tensor():
    rows = [
        {"plugin_id": "g10", "domain": "mahler", "invariant": "M",
         "kill_pattern": "kp_a"},
        {"plugin_id": "g10", "domain": "mahler", "invariant": "M",
         "kill_pattern": "kp_a"},
        {"plugin_id": "g11", "domain": "mahler", "invariant": "M",
         "kill_pattern": "kp_b"},
    ]
    t = KillTensor.from_ledger_rows(rows)
    assert t.cell("g10", "mahler", "M", "kp_a") == 2
    assert t.cell("g11", "mahler", "M", "kp_b") == 1
    assert t.n_populated_cells() == 2
    assert t.total_count() == 3


# ---------------------------------------------------------------------
# Axis values
# ---------------------------------------------------------------------

def test_axis_values_for_each_axis():
    t = KillTensor()
    t.add_cell("g10", "mahler", "M_1", "kp_a")
    t.add_cell("g11", "mahler", "M_2", "kp_b")
    t.add_cell("g11", "BSD",    "M_2", "kp_a")
    assert t.axis_values(AXIS_PLUGIN) == {"g10", "g11"}
    assert t.axis_values(AXIS_DOMAIN) == {"mahler", "BSD"}
    assert t.axis_values(AXIS_INVARIANT) == {"M_1", "M_2"}
    assert t.axis_values(AXIS_KP) == {"kp_a", "kp_b"}


def test_axis_values_invalid_axis_raises():
    t = KillTensor()
    with pytest.raises(ValueError, match="axis"):
        t.axis_values(4)
    with pytest.raises(ValueError, match="axis"):
        t.axis_values(-1)


def test_axis_names_match_constants():
    assert AXIS_NAMES == ("plugin", "domain", "invariant", "kp")
    assert N_AXES == 4
    assert AXIS_PLUGIN == 0
    assert AXIS_DOMAIN == 1
    assert AXIS_INVARIANT == 2
    assert AXIS_KP == 3


# ---------------------------------------------------------------------
# Marginals
# ---------------------------------------------------------------------

def test_marginal_over_kp_collapses_kp_axis():
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a", count=3)
    t.add_cell("g10", "mahler", "M", "kp_b", count=2)
    t.add_cell("g11", "BSD", "L", "kp_a", count=1)
    marginal = t.marginal_over(AXIS_KP)
    # kp collapsed -> keyed by (plugin, domain, invariant)
    assert marginal[("g10", "mahler", "M")] == 5
    assert marginal[("g11", "BSD", "L")] == 1
    assert len(marginal) == 2


def test_marginal_over_plugin_collapses_plugin_axis():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k", count=2)
    t.add_cell("g11", "d", "i", "k", count=3)
    marginal = t.marginal_over(AXIS_PLUGIN)
    assert marginal[("d", "i", "k")] == 5


def test_marginal_on_collapses_to_single_axis():
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a", count=3)
    t.add_cell("g11", "BSD", "L", "kp_a", count=4)
    m = t.marginal_on(AXIS_KP)
    assert m["kp_a"] == 7
    assert len(m) == 1


def test_marginal_on_plugin_axis():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k_1", count=2)
    t.add_cell("g10", "d", "i", "k_2", count=3)
    t.add_cell("g11", "d", "i", "k_1", count=1)
    m = t.marginal_on(AXIS_PLUGIN)
    assert m["g10"] == 5
    assert m["g11"] == 1


# ---------------------------------------------------------------------
# Box queries
# ---------------------------------------------------------------------

def test_density_in_box_full_coverage_is_one():
    """If every cell in the box is populated, density == 1.0."""
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    t.add_cell("g10", "d", "i", "kp_b")
    # Box: g10 x d x i x {kp_a, kp_b} = 2 cells, both populated
    d = t.density_in_box(plugins=["g10"], domains=["d"], invariants=["i"])
    assert d == 1.0


def test_density_in_box_partial():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    # Box: g10 x d x i x {kp_a, kp_b} = 2 cells, 1 populated
    d = t.density_in_box(
        plugins=["g10"], domains=["d"], invariants=["i"],
        kps=["kp_a", "kp_b"],
    )
    assert d == 0.5


def test_density_in_box_default_is_full_populated_density():
    """No filter args -> box is the full populated extent ->
    density measured over the implied bounding box."""
    t = KillTensor()
    t.add_cell("g10", "mahler", "M", "kp_a")
    t.add_cell("g11", "BSD", "L", "kp_b")
    # 2 plugins x 2 domains x 2 invariants x 2 kps = 16 cells,
    # only 2 populated
    d = t.density_in_box()
    assert d == pytest.approx(2 / 16)


def test_density_in_box_empty_box_returns_zero():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    d = t.density_in_box(plugins=["never_seen"])
    # plugin set has 1 value, others empty => box_size product = 0
    assert d == 0.0


def test_empty_cells_in_box_returns_voids():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    # Box: {g10, g11} x {d} x {i} x {kp_a, kp_b} = 4 cells
    # Populated: (g10, d, i, kp_a). Empty: 3
    empty = t.empty_cells_in_box(
        plugins=["g10", "g11"],
        domains=["d"],
        invariants=["i"],
        kps=["kp_a", "kp_b"],
    )
    assert len(empty) == 3
    assert ("g11", "d", "i", "kp_a") in empty
    assert ("g10", "d", "i", "kp_b") in empty
    assert ("g11", "d", "i", "kp_b") in empty


def test_empty_cells_does_not_include_populated_cell():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "kp_a")
    empty = t.empty_cells_in_box(
        plugins=["g10"], domains=["d"],
        invariants=["i"], kps=["kp_a"],
    )
    assert empty == set()


# ---------------------------------------------------------------------
# Rank-like measures (consumed by ITER-43)
# ---------------------------------------------------------------------

def test_axis_cardinalities_match_distinct_values():
    t = KillTensor()
    t.add_cell("g10", "d_1", "i_1", "k_1")
    t.add_cell("g10", "d_2", "i_1", "k_2")
    t.add_cell("g11", "d_1", "i_2", "k_1")
    assert t.axis_cardinalities() == (2, 2, 2, 2)


def test_shape_alias_works():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k")
    assert t.shape() == (1, 1, 1, 1)


def test_repr_shows_summary():
    t = KillTensor()
    t.add_cell("g10", "d", "i", "k", count=3)
    s = repr(t)
    assert "KillTensor" in s
    assert "populated=1" in s
    assert "total_count=3" in s


# ---------------------------------------------------------------------
# Integration with motif extractor key shapes
# ---------------------------------------------------------------------

def test_tensor_key_shape_compatible_with_motif_extractor():
    """The motif extractor's plugin_domain_kp keys are 3-tuples
    (plugin, domain, kp). The tensor's marginal_over(AXIS_INVARIANT)
    produces (plugin, domain, kp) keys -- those should match in
    shape so Layer 2 can join them."""
    from charon.agents.erebos._motif_extraction import (
        extract_plugin_domain_kp_motifs,
    )
    rows = [
        {"row_id": f"r{i}", "plugin_id": "g10", "domain": "mahler",
         "invariant": "M", "kill_pattern": "kp_a"}
        for i in range(3)
    ]
    motifs = extract_plugin_domain_kp_motifs(rows, min_count=2).motifs
    assert len(motifs) == 1
    motif_key = motifs[0].key  # (plugin, domain, kp)

    t = KillTensor.from_ledger_rows(rows)
    tensor_marginal_key_set = set(t.marginal_over(AXIS_INVARIANT).keys())
    # Tensor marginal (plugin, domain, kp) matches motif key shape
    assert motif_key in tensor_marginal_key_set


def test_tensor_count_matches_motif_count_at_cell():
    from charon.agents.erebos._motif_extraction import (
        extract_plugin_domain_kp_motifs,
    )
    rows = [
        {"row_id": f"r{i}", "plugin_id": "g10", "domain": "mahler",
         "invariant": "M", "kill_pattern": "kp"}
        for i in range(4)
    ]
    motifs = extract_plugin_domain_kp_motifs(rows, min_count=2).motifs
    t = KillTensor.from_ledger_rows(rows)
    # Both should agree on the count of 4
    assert motifs[0].count == 4
    assert t.cell("g10", "mahler", "M", "kp") == 4
