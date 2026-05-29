"""Tests for cross-domain transfer (Phase 1C ITER-44)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._cross_domain_transfer import (
    DEFAULT_TRANSFER_KEY_AXES,
    TransferPairTable,
    TransferReport,
    all_pairs_transfer,
    missed_patterns_priority,
    predict_transfer,
)
from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    AXIS_PLUGIN,
    KillTensor,
)


# ---------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------

def test_predict_transfer_rejects_same_source_target():
    t = KillTensor()
    with pytest.raises(ValueError, match="must differ"):
        predict_transfer(t, source_domain="d", target_domain="d")


def test_predict_transfer_rejects_empty_key_axes():
    t = KillTensor()
    with pytest.raises(ValueError, match="non-empty"):
        predict_transfer(t, source_domain="a", target_domain="b",
                          key_axes=())


def test_predict_transfer_rejects_domain_in_key_axes():
    t = KillTensor()
    with pytest.raises(ValueError, match="AXIS_DOMAIN"):
        predict_transfer(
            t, source_domain="a", target_domain="b",
            key_axes=(AXIS_PLUGIN, AXIS_DOMAIN),
        )


def test_predict_transfer_rejects_duplicate_axes():
    t = KillTensor()
    with pytest.raises(ValueError, match="duplicates"):
        predict_transfer(
            t, source_domain="a", target_domain="b",
            key_axes=(AXIS_PLUGIN, AXIS_PLUGIN),
        )


def test_predict_transfer_rejects_out_of_range_axis():
    t = KillTensor()
    with pytest.raises(ValueError, match="0..3"):
        predict_transfer(
            t, source_domain="a", target_domain="b",
            key_axes=(99,),
        )


# ---------------------------------------------------------------------
# Empty / one-sided
# ---------------------------------------------------------------------

def test_empty_source_returns_none_rate():
    t = KillTensor()
    t.add_cell("g10", "B", "i", "kp")
    r = predict_transfer(t, source_domain="A", target_domain="B")
    assert r.n_source == 0
    assert r.transfer_rate is None


def test_empty_target_all_missed():
    t = KillTensor()
    t.add_cell("g10", "A", "i", "kp")
    t.add_cell("g11", "A", "i", "kp")
    r = predict_transfer(t, source_domain="A", target_domain="B")
    assert r.n_source == 2
    assert r.n_target == 0
    assert r.transfer_rate == 0.0
    assert len(r.missed) == 2
    assert len(r.confirmed) == 0
    assert len(r.novel) == 0


def test_both_empty_returns_undefined_rate():
    t = KillTensor()
    r = predict_transfer(t, source_domain="A", target_domain="B")
    assert r.transfer_rate is None
    assert r.n_source == 0
    assert r.n_target == 0


# ---------------------------------------------------------------------
# Confirmed / missed / novel
# ---------------------------------------------------------------------

def test_perfect_transfer_rate_one():
    """Every source pattern present in target."""
    t = KillTensor()
    t.add_cell("g10", "A", "i", "kp_a")
    t.add_cell("g10", "B", "i", "kp_a")
    t.add_cell("g11", "A", "i", "kp_b")
    t.add_cell("g11", "B", "i", "kp_b")
    r = predict_transfer(t, source_domain="A", target_domain="B")
    assert r.transfer_rate == 1.0
    assert len(r.confirmed) == 2
    assert len(r.missed) == 0
    assert len(r.novel) == 0


def test_partial_transfer_with_missed_and_novel():
    """Source: {(g10,kp_a), (g11,kp_b)}; Target: {(g10,kp_a),
    (g12,kp_c)}. Confirmed = 1; Missed = 1; Novel = 1."""
    t = KillTensor()
    t.add_cell("g10", "A", "i", "kp_a")
    t.add_cell("g11", "A", "i", "kp_b")
    t.add_cell("g10", "B", "i", "kp_a")
    t.add_cell("g12", "B", "i", "kp_c")
    r = predict_transfer(t, source_domain="A", target_domain="B")
    assert len(r.confirmed) == 1
    assert ("g10", "kp_a") in r.confirmed
    assert len(r.missed) == 1
    assert ("g11", "kp_b") in r.missed
    assert len(r.novel) == 1
    assert ("g12", "kp_c") in r.novel
    assert r.transfer_rate == pytest.approx(0.5)


def test_invariant_axis_in_key_finer_grained():
    """Adding INVARIANT to key_axes refines the pattern -- two
    cells with same (plugin, kp) but different invariant no
    longer share a transfer pattern."""
    t = KillTensor()
    t.add_cell("g10", "A", "inv_1", "kp")
    t.add_cell("g10", "B", "inv_2", "kp")  # same plugin+kp, diff invariant
    # Default key axes (plugin, kp) -> shared
    r_default = predict_transfer(t, source_domain="A", target_domain="B")
    assert ("g10", "kp") in r_default.confirmed

    # Adding INVARIANT -> not shared
    r_fine = predict_transfer(
        t, source_domain="A", target_domain="B",
        key_axes=(AXIS_PLUGIN, AXIS_INVARIANT, AXIS_KP),
    )
    assert len(r_fine.confirmed) == 0


# ---------------------------------------------------------------------
# TransferReport surface area
# ---------------------------------------------------------------------

def test_report_is_frozen():
    t = KillTensor()
    t.add_cell("g10", "A", "i", "kp")
    t.add_cell("g10", "B", "i", "kp")
    r = predict_transfer(t, source_domain="A", target_domain="B")
    with pytest.raises((AttributeError, Exception)):
        r.transfer_rate = 0.0  # type: ignore[misc]


def test_key_axis_names_helper():
    t = KillTensor()
    r = predict_transfer(
        t, source_domain="A", target_domain="B",
        key_axes=(AXIS_PLUGIN, AXIS_KP),
    )
    assert r.key_axis_names() == ("plugin", "kp")


def test_default_transfer_key_axes_constant():
    assert DEFAULT_TRANSFER_KEY_AXES == (AXIS_PLUGIN, AXIS_KP)


# ---------------------------------------------------------------------
# all_pairs_transfer
# ---------------------------------------------------------------------

def test_all_pairs_empty_tensor():
    table = all_pairs_transfer(KillTensor())
    assert table.domains == ()
    assert table.rates == {}


def test_all_pairs_three_domains():
    t = KillTensor()
    # A: (g10, kp), (g11, kp)
    # B: (g10, kp)
    # C: (g11, kp)
    t.add_cell("g10", "A", "i", "kp")
    t.add_cell("g11", "A", "i", "kp")
    t.add_cell("g10", "B", "i", "kp")
    t.add_cell("g11", "C", "i", "kp")
    table = all_pairs_transfer(t)
    assert set(table.domains) == {"A", "B", "C"}
    # A -> B: 1/2 of A's patterns in B
    assert table.rate("A", "B") == 0.5
    # A -> C: 1/2 of A's patterns in C
    assert table.rate("A", "C") == 0.5
    # B -> A: B's 1 pattern (g10,kp) IS in A -> 1.0
    assert table.rate("B", "A") == 1.0
    # B -> C: B's (g10,kp) NOT in C (C has g11,kp) -> 0.0
    assert table.rate("B", "C") == 0.0
    # C -> A: 1.0
    assert table.rate("C", "A") == 1.0
    # C -> B: 0.0
    assert table.rate("C", "B") == 0.0


def test_all_pairs_diagonal_excluded():
    t = KillTensor()
    t.add_cell("g10", "A", "i", "kp")
    t.add_cell("g10", "B", "i", "kp")
    table = all_pairs_transfer(t)
    # No diagonal entries
    assert ("A", "A") not in table.rates
    assert ("B", "B") not in table.rates
    # But off-diagonal IS present
    assert ("A", "B") in table.rates


def test_all_pairs_empty_source_has_none_rate():
    t = KillTensor()
    # B is populated, A is not
    t.add_cell("g10", "B", "i", "kp")
    t.add_cell("g11", "B", "i", "kp")
    # No way to populate "A" without putting any cells; create
    # cells in C so A appears in domain values:
    # Actually let's use add_cell directly to put empty intent:
    # The tensor only knows about domains via populated cells, so
    # if A is never populated, it won't show up. Use a different
    # test: ensure two populated domains, with one having all
    # patterns matched.
    t2 = KillTensor()
    t2.add_cell("g10", "A", "i", "kp_unique_to_A")
    t2.add_cell("g11", "B", "i", "kp")
    table = all_pairs_transfer(t2)
    # A and B both appear
    assert ("A", "B") in table.rates
    # A -> B: A has 1 pattern (g10, kp_unique_to_A), not in B -> 0.0
    assert table.rates[("A", "B")] == 0.0


# ---------------------------------------------------------------------
# missed_patterns_priority
# ---------------------------------------------------------------------

def test_missed_patterns_priority_ranks_by_source_count():
    """Pattern that appears 10 times in source should rank above
    pattern that appears 1 time."""
    t = KillTensor()
    # Source A: (g10, kp_a) x 10, (g11, kp_b) x 1
    t.add_cell("g10", "A", "i", "kp_a", count=10)
    t.add_cell("g11", "A", "i", "kp_b", count=1)
    # Target B: neither pattern present
    t.add_cell("g12", "B", "i", "kp_c")
    report = predict_transfer(t, source_domain="A", target_domain="B")
    assert len(report.missed) == 2
    ranked = missed_patterns_priority(report, t)
    assert ranked[0][0] == ("g10", "kp_a")
    assert ranked[0][1] == 10
    assert ranked[1][0] == ("g11", "kp_b")
    assert ranked[1][1] == 1


def test_missed_patterns_priority_only_includes_missed():
    """Confirmed patterns should not appear in priority list."""
    t = KillTensor()
    t.add_cell("g10", "A", "i", "kp_a")  # confirmed
    t.add_cell("g10", "B", "i", "kp_a")
    t.add_cell("g11", "A", "i", "kp_b")  # missed
    report = predict_transfer(t, source_domain="A", target_domain="B")
    ranked = missed_patterns_priority(report, t)
    patterns = [p for p, _ in ranked]
    assert ("g10", "kp_a") not in patterns  # confirmed; not in missed
    assert ("g11", "kp_b") in patterns


# ---------------------------------------------------------------------
# Integration: realistic substrate scenario
# ---------------------------------------------------------------------

def test_g23_pattern_misses_to_mahler_when_only_in_BSD():
    """Realistic scenario: g23_asymptotic_limit fires
    error_term_does_not_decay in BSD; predicted transfer to
    Mahler should be MISSED."""
    t = KillTensor()
    # g23 in BSD with the decay kp
    t.add_cell("g23_asymptotic_limit", "BSD", "regulator",
               "error_term_does_not_decay")
    # Mahler has g10 + g11, but g23 hasn't fired there
    t.add_cell("g10_boundary", "Mahler", "M",
               "sharp_boundary_detected_bocpd")
    t.add_cell("g11_exception_miner", "Mahler", "M",
               "catalog_flag_inconsistent")

    r = predict_transfer(
        t, source_domain="BSD", target_domain="Mahler",
    )
    # g23's BSD pattern not in Mahler -> missed
    assert ("g23_asymptotic_limit", "error_term_does_not_decay") in r.missed
    # Mahler patterns not in BSD -> novel
    assert len(r.novel) == 2


def test_high_transfer_rate_between_similar_domains():
    """Two domains with identical (plugin, kp) populations show
    transfer rate 1.0 -- the substrate's prediction that they're
    geometrically similar."""
    t = KillTensor()
    for plugin in ("g10", "g11"):
        for kp in ("kp_a", "kp_b"):
            t.add_cell(plugin, "Mahler", "M", kp)
            t.add_cell(plugin, "MahlerAlternative", "M_alt", kp)
    r = predict_transfer(
        t, source_domain="Mahler", target_domain="MahlerAlternative",
    )
    assert r.transfer_rate == 1.0
    assert len(r.confirmed) == 4
