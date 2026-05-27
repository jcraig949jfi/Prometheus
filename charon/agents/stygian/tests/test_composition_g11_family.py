"""Synthetic-control tests for the G11 family (v1 boolean cube,
v2 degree-minima, v3 direct-min verification).

The G11 family went through 3 iterations of substrate self-correction:
- v1 (ITER-12): tautological collapse to Salem-class identity
- v2 (ITER-13): orthogonal degree_minimum criterion -> chi^2=191
- v3 (ITER-15): independent argmin verification of v2's flag input;
  caught cyclotomic-extension false positives + ULP ties.

These tests lock in all three loaders' decision logic.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders._mahler_composition_helpers import M_LEHMER
from charon.agents.stygian.loaders.composition_g11_mahler_boolean_cube import (
    CHI2_THRESHOLD,
    SURVIVAL_THRESHOLD,
    _chi_squared,
    _cube_key,
    run_g11_mahler_boolean_cube,
)
from charon.agents.stygian.loaders.composition_g11_v2_lehmer_degree_minima import (
    CHI2_THRESHOLD_V2,
    run_g11_v2_lehmer_degree_minima,
)
from charon.agents.stygian.loaders.composition_g11_v3_direct_min_verification import (
    run_g11_v3_direct_min_verification,
)


# ---------------------------------------------------------------------
# Cube key primitive (shared across v1, v2)
# ---------------------------------------------------------------------

def test_cube_key_extracts_three_bools():
    e = {"salem_class": True, "is_smyth_extremal": False, "degree": 12}
    assert _cube_key(e) == (True, False, True)  # 12 is even


def test_cube_key_odd_degree():
    e = {"salem_class": False, "is_smyth_extremal": True, "degree": 7}
    assert _cube_key(e) == (False, True, False)  # 7 is odd


def test_cube_key_missing_flags_default_false():
    e = {"degree": 10}
    assert _cube_key(e) == (False, False, True)


# ---------------------------------------------------------------------
# Chi-squared primitive
# ---------------------------------------------------------------------

def test_chi_squared_zero_for_perfect_fit():
    """If observed == expected for all cells, chi^2 = 0."""
    assert _chi_squared([10.0, 20.0, 30.0], [10.0, 20.0, 30.0]) == 0.0


def test_chi_squared_skips_tiny_expected_cells():
    """Cells with E < 1 are skipped (avoid degenerate division)."""
    # Cell 1: E=0.5 (skipped). Cell 2: E=10, O=10 (contributes 0).
    # Cell 3: E=20, O=22 (contributes (22-20)^2/20 = 0.2).
    chi2 = _chi_squared(
        [5.0, 10.0, 22.0],
        [0.5, 10.0, 20.0],
    )
    assert chi2 == pytest.approx(0.2, abs=1e-9)


def test_chi_squared_grows_with_deviation():
    base = _chi_squared([10.0], [10.0])  # 0
    far = _chi_squared([100.0], [10.0])  # (100-10)^2 / 10 = 810
    assert far > base


# ---------------------------------------------------------------------
# v1 boolean cube against synthetic catalogs
# ---------------------------------------------------------------------

def test_v1_uniform_distribution_rejects(monkeypatch):
    """If every cube cell has the same survival rate, chi^2 ~= 0 ->
    REJECTED with out_of_sample_failure."""
    import charon.agents.stygian.loaders.composition_g11_mahler_boolean_cube as g11_mod

    def fake_loader(upper_M=2.0):
        # 8 cells * 100 entries each, each cell has 50% survivors
        # (50 below threshold + 50 above)
        out = []
        for salem in (True, False):
            for smyth in (True, False):
                for deg_par in (10, 11):  # even, odd
                    for i in range(50):
                        # Half below SURVIVAL_THRESHOLD
                        out.append({
                            "mahler_measure": SURVIVAL_THRESHOLD - 0.05,
                            "salem_class": salem, "is_smyth_extremal": smyth,
                            "degree": deg_par,
                        })
                    for i in range(50):
                        # Half above
                        out.append({
                            "mahler_measure": SURVIVAL_THRESHOLD + 0.05,
                            "salem_class": salem, "is_smyth_extremal": smyth,
                            "degree": deg_par,
                        })
        return out

    monkeypatch.setattr(
        g11_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_mahler_boolean_cube()
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "out_of_sample_failure"


def test_v1_extreme_heterogeneity_promoted(monkeypatch):
    """If one cell has 100% survival and another has 0%, chi^2 is
    enormous -> PROMOTED."""
    import charon.agents.stygian.loaders.composition_g11_mahler_boolean_cube as g11_mod

    def fake_loader(upper_M=2.0):
        out = []
        # Cell A: 100 entries all below SURVIVAL_THRESHOLD (100% survivors)
        for _ in range(100):
            out.append({
                "mahler_measure": SURVIVAL_THRESHOLD - 0.05,
                "salem_class": True, "is_smyth_extremal": False, "degree": 10,
            })
        # Cell B: 100 entries all above SURVIVAL_THRESHOLD (0% survivors)
        for _ in range(100):
            out.append({
                "mahler_measure": SURVIVAL_THRESHOLD + 0.05,
                "salem_class": False, "is_smyth_extremal": False, "degree": 10,
            })
        # Two more cells with mixed for MIN_CELLS_NONEMPTY threshold
        for _ in range(50):
            out.append({
                "mahler_measure": SURVIVAL_THRESHOLD - 0.05,
                "salem_class": True, "is_smyth_extremal": False, "degree": 11,
            })
        for _ in range(50):
            out.append({
                "mahler_measure": SURVIVAL_THRESHOLD + 0.05,
                "salem_class": False, "is_smyth_extremal": True, "degree": 10,
            })
        return out

    monkeypatch.setattr(
        g11_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_mahler_boolean_cube()
    assert result["verdict"] == "PROMOTED"
    assert result["chi_squared"] > CHI2_THRESHOLD


def test_v1_too_few_cells_unverified(monkeypatch):
    """Only 1 cell populated -> insufficient for heterogeneity test."""
    import charon.agents.stygian.loaders.composition_g11_mahler_boolean_cube as g11_mod

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.5, "salem_class": True, "is_smyth_extremal": False, "degree": 10}
            for _ in range(100)
        ]

    monkeypatch.setattr(
        g11_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_mahler_boolean_cube()
    assert result["verdict"] == "UNVERIFIED"
    assert "insufficient_sample" in result["kill_pattern"]


# ---------------------------------------------------------------------
# v2 degree-minima
# ---------------------------------------------------------------------

def test_v2_uniformly_distributed_minima_rejects(monkeypatch):
    """If degree_minimum flags are uniformly distributed across cells,
    chi^2 small -> REJECTED."""
    import charon.agents.stygian.loaders.composition_g11_v2_lehmer_degree_minima as g11v2_mod

    def fake_loader(upper_M=2.0):
        out = []
        # 8 cells, each with 100 entries; 1 degree_minimum per cell
        for cell_id, (salem, smyth, deg_par) in enumerate([
            (True, True, 10), (True, True, 11),
            (True, False, 10), (True, False, 11),
            (False, True, 10), (False, True, 11),
            (False, False, 10), (False, False, 11),
        ]):
            for i in range(100):
                out.append({
                    "mahler_measure": 1.5 + 0.01 * cell_id,
                    "salem_class": salem, "is_smyth_extremal": smyth,
                    "degree": deg_par,
                    "degree_minimum": (i == 0),  # 1 per cell
                })
        return out

    monkeypatch.setattr(
        g11v2_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v2_lehmer_degree_minima()
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "out_of_sample_failure"


def test_v2_concentrated_minima_promoted(monkeypatch):
    """If degree_minimum flags concentrate in a tiny minority cell,
    chi^2 large -> PROMOTED."""
    import charon.agents.stygian.loaders.composition_g11_v2_lehmer_degree_minima as g11v2_mod

    def fake_loader(upper_M=2.0):
        out = []
        # Cell A: 1000 entries, 1 minimum (rate 0.1%)
        for i in range(1000):
            out.append({
                "mahler_measure": 1.5,
                "salem_class": True, "is_smyth_extremal": False, "degree": 10,
                "degree_minimum": (i == 0),
            })
        # Cell B: 10 entries, 5 minima (rate 50%) — gross over-rep
        for i in range(10):
            out.append({
                "mahler_measure": 1.6,
                "salem_class": False, "is_smyth_extremal": True, "degree": 11,
                "degree_minimum": (i < 5),
            })
        # Three more cells to satisfy MIN_CELLS_NONEMPTY
        for cell_idx, (salem, smyth, deg) in enumerate([
            (True, True, 11), (True, False, 11), (False, False, 10),
        ]):
            for _ in range(50):
                out.append({
                    "mahler_measure": 1.7 + 0.01 * cell_idx,
                    "salem_class": salem, "is_smyth_extremal": smyth,
                    "degree": deg,
                    "degree_minimum": False,
                })
        return out

    monkeypatch.setattr(
        g11v2_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v2_lehmer_degree_minima()
    assert result["verdict"] == "PROMOTED"
    assert result["chi_squared"] > CHI2_THRESHOLD_V2


def test_v2_no_minima_at_all_unverified(monkeypatch):
    """No degree_minimum flags anywhere -> can't compute heterogeneity."""
    import charon.agents.stygian.loaders.composition_g11_v2_lehmer_degree_minima as g11v2_mod

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.5, "salem_class": s, "is_smyth_extremal": False,
             "degree": d, "degree_minimum": False}
            for s in (True, False)
            for d in (10, 11)
            for _ in range(50)
        ]

    monkeypatch.setattr(
        g11v2_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v2_lehmer_degree_minima()
    assert result["verdict"] == "UNVERIFIED"
    assert result["kill_pattern"] == "stygian_composition_no_survivors"


# ---------------------------------------------------------------------
# v3 direct-min verification: cyclotomic-extension filter is the
# critical correction
# ---------------------------------------------------------------------

def test_v3_cyclotomic_extension_filter_excludes_lehmer_copies(monkeypatch):
    """v3 must NOT crown Lehmer x Phi_k entries (degree 12, 14, ...
    with M = M_LEHMER) as 'true argmin at degree > 10'. The
    cyclotomic-extension filter inside the loader skips them."""
    import charon.agents.stygian.loaders.composition_g11_v3_direct_min_verification as g11v3_mod

    def fake_loader(upper_M=2.0):
        return [
            # Lehmer himself at degree 10
            {"degree": 10, "mahler_measure": M_LEHMER, "degree_minimum": True,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
            # Lehmer x Phi_2 at degree 12 (cyclotomic extension)
            {"degree": 12, "mahler_measure": M_LEHMER, "degree_minimum": False,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
            # A genuine degree-12 minimum, larger M
            {"degree": 12, "mahler_measure": 1.25, "degree_minimum": True,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
        ]

    monkeypatch.setattr(
        g11v3_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v3_direct_min_verification()
    # Both degrees flagged should match (degree 10: Lehmer; degree 12:
    # genuine minimum at M=1.25, NOT the cyclotomic extension)
    assert result["verdict"] == "PROMOTED"
    assert result["match_rate"] >= 0.95


def test_v3_genuine_flag_mismatch_rejects(monkeypatch):
    """If catalog flag is on a non-argmin entry (even after filtering),
    v3 should report inconsistency."""
    import charon.agents.stygian.loaders.composition_g11_v3_direct_min_verification as g11v3_mod

    def fake_loader(upper_M=2.0):
        return [
            # Genuine min at degree 10: M=1.20 (NOT flagged)
            {"degree": 10, "mahler_measure": 1.20, "degree_minimum": False,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
            # Larger M at degree 10, flagged (wrong)
            {"degree": 10, "mahler_measure": 1.40, "degree_minimum": True,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
        ]

    monkeypatch.setattr(
        g11v3_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v3_direct_min_verification()
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "catalog_flag_inconsistent"


def test_v3_ulp_tolerance_treats_identical_M_as_match(monkeypatch):
    """Two entries at same degree with identical M (within ULPs);
    flag on one but argmin picks the other index. v3 must treat
    this as a match (per ITER-15 fix)."""
    import charon.agents.stygian.loaders.composition_g11_v3_direct_min_verification as g11v3_mod

    def fake_loader(upper_M=2.0):
        return [
            # Two entries at degree 10, identical M, flag on second
            {"degree": 10, "mahler_measure": 1.20, "degree_minimum": False,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
            {"degree": 10, "mahler_measure": 1.20, "degree_minimum": True,
             "salem_class": True, "is_smyth_extremal": False, "coeffs": []},
        ]

    monkeypatch.setattr(
        g11v3_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v3_direct_min_verification()
    # Both entries have M=1.20; flag is on one, argmin picks first by
    # (m, idx) tuple, but ULP tolerance accepts the second's flag.
    assert result["verdict"] == "PROMOTED"
    assert result["match_rate"] == 1.0
