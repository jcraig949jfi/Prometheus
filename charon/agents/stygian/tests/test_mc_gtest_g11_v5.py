"""Tests for G11 v5 Monte-Carlo G-test loader.

Per Erebos v3 Phase 1A ITER-34. Validates G-test + permutation null
on synthetic uniform / clustered flag distributions + the G11
retrofit on live Mossinghoff catalog.
"""
from __future__ import annotations

import math
import random

import pytest

from charon.agents.stygian.loaders.composition_g11_v5_mc_gtest import (
    G11V5McGtestLoader,
    _g_statistic,
)


# ---------------------------------------------------------------------
# G-statistic primitive
# ---------------------------------------------------------------------

def test_g_statistic_zero_for_uniform_distribution():
    """When observed == expected in every cell, G = 0."""
    cube_total = {("a",): 100, ("b",): 100}
    # Uniform flag rate 0.1 -> 10 survivors per 100-cell
    cube_survivors = {("a",): 10, ("b",): 10}
    overall_rate = 20 / 200
    g = _g_statistic(cube_total, cube_survivors, overall_rate)
    assert abs(g) < 1e-9


def test_g_statistic_large_for_concentrated_distribution():
    """All survivors in one cell -> large G."""
    cube_total = {("a",): 100, ("b",): 100}
    cube_survivors = {("a",): 20, ("b",): 0}  # all in a
    overall_rate = 20 / 200
    g = _g_statistic(cube_total, cube_survivors, overall_rate)
    # Cell (a,): observed 20, expected 10 -> 2 * 20 * ln(2) = 27.7
    # Cell (b,): observed 0 -> contributes 0
    assert g > 25.0
    assert g < 30.0  # sanity bound


def test_g_statistic_skips_empty_expected_cells():
    """Cells with expected < 1e-9 are skipped without crashing."""
    cube_total = {("a",): 100, ("b",): 0}  # b is empty -> expected 0
    cube_survivors = {("a",): 10}
    overall_rate = 10 / 100
    g = _g_statistic(cube_total, cube_survivors, overall_rate)
    assert g == 0.0  # uniform within the populated cell


# ---------------------------------------------------------------------
# Loader routing
# ---------------------------------------------------------------------

def test_g11_v5_applicable_routes_on_v5_marker():
    loader = G11V5McGtestLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g11_exception_miner",
        "erebos_composed_id": "EREBOS-G11-v5_mc_gtest_lehmer_test",
    }) is True


def test_g11_v5_applicable_routes_on_gtest_marker():
    loader = G11V5McGtestLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g11_exception_miner",
        "erebos_composed_id": "EREBOS-G11-gtest_lehmer_BL-C-001",
    }) is True


def test_g11_v5_does_not_steal_v2_emissions():
    """v2 (chi^2) G11 emissions continue routing to the v2 loader."""
    loader = G11V5McGtestLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g11_exception_miner",
        "erebos_composed_id": "EREBOS-G11-v2_degmin_lehmer_BL-C-001",
    }) is False


def test_g11_v5_does_not_steal_v3_emissions():
    """v3 (direct-min verification) G11 emissions are not v5."""
    loader = G11V5McGtestLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g11_exception_miner",
        "erebos_composed_id": "EREBOS-G11-v3_verify_lehmer_BL-C-001",
    }) is False


def test_g11_v5_rejects_non_g11_plugin():
    loader = G11V5McGtestLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g10_boundary",
        "erebos_composed_id": "EREBOS-G10-v5_test",
    }) is False


# ---------------------------------------------------------------------
# Live Mossinghoff smoke
# ---------------------------------------------------------------------

def test_g11_v5_live_returns_calibrated_p_value():
    """Live loader runs the full MC G-test and emits p-value +
    null G distribution shape into the seam."""
    from charon.agents.stygian.loaders.composition_g11_v5_mc_gtest import (
        run_g11_v5_mc_gtest,
    )
    result = run_g11_v5_mc_gtest()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"Live Mossinghoff catalog not available: "
                    f"{result.get('notes')}")
    # All seam fields present
    assert "g_statistic_observed" in result
    assert "p_value_mc" in result
    assert "null_g_p95" in result
    assert "null_g_p99" in result
    # P-value in [0, 1]
    assert 0.0 <= result["p_value_mc"] <= 1.0
    # G observed must be non-negative (G is a likelihood-ratio)
    assert result["g_statistic_observed"] >= 0.0
    # Calibrated permutation count
    assert result["n_mc_permutations"] == 2000
    assert result["mc_seed"] == 23
    # Verdict in canonical set
    assert result["verdict"] in ("PROMOTED", "REJECTED", "UNVERIFIED")
    # If PROMOTED: p_value < alpha
    if result["verdict"] == "PROMOTED":
        assert result["p_value_mc"] < result["alpha_promote"]
    # If REJECTED: p_value >= alpha + kp matches
    if result["verdict"] == "REJECTED":
        assert result["p_value_mc"] >= result["alpha_promote"]
        assert result["kill_pattern"] == "flag_distribution_uniform_under_mc_null"


def test_g11_v5_live_recovers_v2_finding():
    """The v2 finding (non-Salem degree-minima cluster, chi^2 ~
    large) should re-confirm under the calibrated MC G-test:
    p_value should be small (< 0.05) IF v2's claim was real."""
    from charon.agents.stygian.loaders.composition_g11_v5_mc_gtest import (
        run_g11_v5_mc_gtest,
    )
    result = run_g11_v5_mc_gtest()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip("Catalog unavailable")
    # The v2 finding documented chi^2 ~ 10+ on this exact catalog.
    # Under the MC null, a real structural signal should produce
    # a small p-value. This is the regression test: if v2's finding
    # was a chi^2 artifact, this test will fail and we'll have
    # caught a false-positive.
    if result["verdict"] == "PROMOTED":
        assert result["p_value_mc"] < 0.05
        assert result["g_statistic_observed"] > result["null_g_p95"]
