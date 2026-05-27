"""Synthetic-control tests for the two ITER-19 new loaders:
G11 v4 (palindromic cube) and G24 v2 (reciprocal symmetry audit).
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders.composition_g11_v4_palindromic_cube import (
    CHI2_THRESHOLD_V4,
    _is_palindromic,
    run_g11_v4_palindromic_cube,
)
from charon.agents.stygian.loaders.composition_g24_v2_reciprocal_audit import (
    SAMPLE_SIZE as G24V2_SAMPLE_SIZE,
    TOLERANCE as G24V2_TOLERANCE,
    _is_palindromic as g24v2_is_palindromic,
    _reciprocal,
    run_g24_v2_reciprocal_audit,
)


# ---------------------------------------------------------------------
# G11 v4: palindromic primitive
# ---------------------------------------------------------------------

def test_g11v4_palindromic_detects_simple_case():
    assert _is_palindromic([1, 2, 3, 2, 1]) is True


def test_g11v4_palindromic_detects_anti_palindromic_correctly():
    """Anti-palindromic ([1, 2, -2, -1]) is NOT palindromic in the
    'equals reverse' sense — the test should return False."""
    assert _is_palindromic([1, 2, -2, -1]) is False


def test_g11v4_palindromic_empty():
    assert _is_palindromic([]) is False
    assert _is_palindromic(None) is False


def test_g11v4_palindromic_single():
    assert _is_palindromic([5]) is True


def test_g11v4_palindromic_lehmer_polynomial():
    """Lehmer's polynomial: [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1] —
    palindromic."""
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    assert _is_palindromic(lehmer) is True


def test_g11v4_no_palindromic_entries(monkeypatch):
    """If no entries are palindromic, the cube has structure but
    pal_implies_salem_rate is 0 (no palindromic, so the conditional
    is 0/0; loader returns 0 by convention)."""
    import charon.agents.stygian.loaders.composition_g11_v4_palindromic_cube as g11v4_mod

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.5,
             "coeffs": [1, 2, 3, 4],  # not palindromic
             "salem_class": False,
             "is_smyth_extremal": False,
             "degree": 4,
             "degree_minimum": (i == 0)}
            for i in range(100)
        ]

    monkeypatch.setattr(
        g11v4_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v4_palindromic_cube()
    # 1 cell populated -> insufficient sample
    assert result["verdict"] == "UNVERIFIED"
    assert "insufficient_sample" in result["kill_pattern"]


def test_g11v4_palindromic_equals_salem_synthetic(monkeypatch):
    """In a synthetic catalog where palindromic ALWAYS implies salem
    and vice versa, pal_implies_salem_rate = 1.0 (catalog-equivalent
    case)."""
    import charon.agents.stygian.loaders.composition_g11_v4_palindromic_cube as g11v4_mod

    def fake_loader(upper_M=2.0):
        out = []
        # Salem + palindromic (matched)
        for i in range(100):
            out.append({
                "mahler_measure": 1.2, "salem_class": True,
                "is_smyth_extremal": False, "degree": 10,
                "coeffs": [1, 2, 1], "degree_minimum": (i == 0),
            })
        # Non-salem + non-palindromic (matched)
        for i in range(50):
            out.append({
                "mahler_measure": 1.5, "salem_class": False,
                "is_smyth_extremal": False, "degree": 11,
                "coeffs": [1, 2, 3], "degree_minimum": (i < 2),
            })
        # Additional cells to satisfy MIN_CELLS_NONEMPTY=4. The cube
        # axes are (salem, smyth, palindromic) — populate distinct
        # combos so we get >= 4 cells.
        # (salem=True, smyth=True, pal=True)
        for i in range(20):
            out.append({
                "mahler_measure": 1.4, "salem_class": True,
                "is_smyth_extremal": True, "degree": 10,
                "coeffs": [1, 2, 1], "degree_minimum": False,
            })
        # (salem=False, smyth=True, pal=False)
        for i in range(20):
            out.append({
                "mahler_measure": 1.6, "salem_class": False,
                "is_smyth_extremal": True, "degree": 10,
                "coeffs": [1, 2, 3], "degree_minimum": False,
            })
        # (salem=True, smyth=False, pal=True) with odd degree
        for i in range(20):
            out.append({
                "mahler_measure": 1.45, "salem_class": True,
                "is_smyth_extremal": False, "degree": 11,
                "coeffs": [1, 2, 1], "degree_minimum": False,
            })
        return out

    monkeypatch.setattr(
        g11v4_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = run_g11_v4_palindromic_cube()
    # P(salem | palindromic): pal entries are salem-pal (100+20=120),
    # all of which are salem. -> rate = 1.0
    assert result["pal_implies_salem_rate"] == 1.0


# ---------------------------------------------------------------------
# G24 v2: reciprocal primitive
# ---------------------------------------------------------------------

def test_g24v2_reciprocal_is_reverse():
    assert _reciprocal([1, 2, 3, 4, 5]) == [5, 4, 3, 2, 1]


def test_g24v2_reciprocal_palindromic_unchanged():
    """Palindromic coefficients are reciprocal-invariant."""
    coeffs = [1, 2, 3, 2, 1]
    assert _reciprocal(coeffs) == coeffs


def test_g24v2_reciprocal_idempotent_squared():
    coeffs = [3, -7, 2, 9, -1]
    assert _reciprocal(_reciprocal(coeffs)) == coeffs


def test_g24v2_is_palindromic_helper():
    assert g24v2_is_palindromic([1, 2, 1]) is True
    assert g24v2_is_palindromic([1, 2, 3]) is False


# ---------------------------------------------------------------------
# G24 v2 end-to-end with mocked catalog + Mahler
# ---------------------------------------------------------------------

def test_g24v2_audit_passes_synthetic_clean(monkeypatch):
    """All sampled entries: Mahler(reciprocal) == Mahler(original)
    within tolerance -> PROMOTED, 0 mismatches."""
    import charon.agents.stygian.loaders.composition_g24_v2_reciprocal_audit as g24v2_mod

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.5, "degree": 4, "coeffs": [1, 2, 3, 4]}
            for _ in range(G24V2_SAMPLE_SIZE)
        ]

    def fake_mahler(coeffs):
        return 1.5  # constant; matches stored value

    monkeypatch.setattr(
        g24v2_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    import sys
    fake_module = type(sys)("techne.lib.mahler_measure_mock")
    fake_module.mahler_measure = fake_mahler
    monkeypatch.setitem(sys.modules, "techne.lib.mahler_measure", fake_module)

    result = run_g24_v2_reciprocal_audit()
    assert result["verdict"] == "PROMOTED"
    assert result["n_mismatches"] == 0


def test_g24v2_audit_detects_synthetic_corruption(monkeypatch):
    """If recomputed Mahler differs from stored value beyond tolerance
    -> REJECTED with symmetry_breaking."""
    import charon.agents.stygian.loaders.composition_g24_v2_reciprocal_audit as g24v2_mod

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.5, "degree": 4, "coeffs": [1, 2, 3, 4]}
            for _ in range(50)
        ]

    def fake_mahler(coeffs):
        # Returns wrong value -> all 50 entries flagged as mismatches
        return 2.0

    monkeypatch.setattr(
        g24v2_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    import sys
    fake_module = type(sys)("techne.lib.mahler_measure_mock")
    fake_module.mahler_measure = fake_mahler
    monkeypatch.setitem(sys.modules, "techne.lib.mahler_measure", fake_module)

    result = run_g24_v2_reciprocal_audit()
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "symmetry_breaking"


def test_g24v2_distinguishes_palindromic_vs_non():
    """Live result: the audit must report n_palindromic and
    n_non_palindromic counts separately."""
    result = run_g24_v2_reciprocal_audit()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"Live catalog test: {result.get('notes')}")
    assert "n_palindromic" in result
    assert "n_non_palindromic" in result
    # ITER-19 documented: 89 informative non-pal + 111 trivial pal
    assert result["n_non_palindromic"] >= 50
