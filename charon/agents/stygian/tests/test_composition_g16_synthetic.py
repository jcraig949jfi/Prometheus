"""Synthetic-control tests for G16 anti-anchor loader.

Covers the band-restriction logic + the ITER-19 permutation-null
refinement.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders.composition_g16_lehmer_extremum import (
    ANCHOR_SURVIVAL_THRESHOLD,
    BAND_WIDTH,
    MIN_BAND_SIZE,
    run_g16_lehmer_extremum,
)
from charon.agents.stygian.loaders._mahler_composition_helpers import M_LEHMER


# ---------------------------------------------------------------------
# Band restriction + survival logic
# ---------------------------------------------------------------------

def test_g16_empty_band_returns_empty_adversarial_band(monkeypatch):
    """If the adversarial band contains zero catalog entries, the
    loader returns the empty-band kill_pattern."""
    import charon.agents.stygian.loaders.composition_g16_lehmer_extremum as g16_mod

    def fake_loader(upper_M=2.0):
        # All entries far below adversarial M=5.0
        return [{"mahler_measure": 1.5} for _ in range(100)]

    monkeypatch.setattr(
        g16_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    r = run_g16_lehmer_extremum(adversarial_M=5.0, param_key="test")
    assert r["verdict"] == "REJECTED"
    assert r["kill_pattern"] == "stygian_composition_empty_adversarial_band"
    assert r["n_band"] == 0


def test_g16_insufficient_band_unverified(monkeypatch):
    """Band with 1-4 entries (below MIN_BAND_SIZE)."""
    import charon.agents.stygian.loaders.composition_g16_lehmer_extremum as g16_mod

    def fake_loader(upper_M=2.0):
        # 3 entries in band [1.45, 1.55]
        return [
            {"mahler_measure": 1.50},
            {"mahler_measure": 1.51},
            {"mahler_measure": 1.52},
        ] + [{"mahler_measure": 1.2} for _ in range(100)]

    monkeypatch.setattr(
        g16_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    r = run_g16_lehmer_extremum(adversarial_M=1.50, param_key="test")
    assert r["verdict"] == "UNVERIFIED"
    assert r["kill_pattern"] == "stygian_composition_insufficient_sample"


def test_g16_high_survival_band_rejects_with_conjecture_survives(monkeypatch):
    """Band entries all >= M_LEHMER -> survival ~1.0 -> anchor
    extends -> REJECTED with conjecture_survives_adversarial_attack."""
    import charon.agents.stygian.loaders.composition_g16_lehmer_extremum as g16_mod

    def fake_loader(upper_M=2.0):
        # 100 entries in band [1.45, 1.55], all >= M_LEHMER
        return [
            {"mahler_measure": 1.50 + 0.001 * (i % 5)}
            for i in range(100)
        ]

    monkeypatch.setattr(
        g16_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    r = run_g16_lehmer_extremum(adversarial_M=1.50, param_key="test")
    assert r["verdict"] == "REJECTED"
    assert r["kill_pattern"] == "conjecture_survives_adversarial_attack"
    assert r["band_survival"] >= ANCHOR_SURVIVAL_THRESHOLD


def test_g16_low_survival_band_promotes(monkeypatch):
    """Band entries mostly < M_LEHMER -> survival < threshold ->
    anchor degrades -> PROMOTED (G16's break-here hypothesis succeeds)."""
    import charon.agents.stygian.loaders.composition_g16_lehmer_extremum as g16_mod

    def fake_loader(upper_M=2.0):
        # 100 entries in band [1.05, 1.15], all < M_LEHMER (1.176)
        return [
            {"mahler_measure": 1.10}
            for _ in range(100)
        ]

    monkeypatch.setattr(
        g16_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    r = run_g16_lehmer_extremum(adversarial_M=1.10, param_key="test")
    assert r["verdict"] == "PROMOTED"
    assert r["band_survival"] < ANCHOR_SURVIVAL_THRESHOLD


# ---------------------------------------------------------------------
# ITER-19 permutation-null refinement
# ---------------------------------------------------------------------

def test_g16_returns_null_p05_and_p95_when_band_has_data(monkeypatch):
    """Loader must populate null_p05, null_p95, structurally_different
    fields after ITER-19 refinement."""
    import charon.agents.stygian.loaders.composition_g16_lehmer_extremum as g16_mod

    def fake_loader(upper_M=2.0):
        return [{"mahler_measure": 1.20 + 0.01 * (i % 5)} for i in range(100)]

    monkeypatch.setattr(
        g16_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    r = run_g16_lehmer_extremum(adversarial_M=1.20, param_key="test")
    assert "null_p05" in r
    assert "null_p95" in r
    assert "band_is_structurally_different" in r
    assert "permutation_n" in r
    assert r["null_p05"] is not None
    assert r["null_p95"] is not None


def test_g16_band_matching_catalog_bulk_not_structurally_different(monkeypatch):
    """If the band is essentially the whole catalog (all entries fall
    in the band), null subsamples and band have identical survival ->
    NOT structurally different."""
    import charon.agents.stygian.loaders.composition_g16_lehmer_extremum as g16_mod

    def fake_loader(upper_M=2.0):
        # All 100 entries fall in band [1.45, 1.55]
        return [{"mahler_measure": 1.50} for _ in range(100)]

    monkeypatch.setattr(
        g16_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    r = run_g16_lehmer_extremum(adversarial_M=1.50, param_key="test")
    # When band == catalog, null subsample == band -> not different
    assert r["band_is_structurally_different"] is False


def test_g16_notes_mention_null_context():
    """Notes addendum about the permutation null must be present after
    ITER-19 refinement."""
    r = run_g16_lehmer_extremum(adversarial_M=1.20, param_key="test")
    if r["verdict"] == "UNVERIFIED":
        pytest.skip(f"Live catalog test: {r.get('notes')}")
    assert "Permutation null" in r["notes"]
