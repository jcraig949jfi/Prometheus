"""TDD tests for the relational positive control / calibration (Stage 0b).

These confirm the instrument FIRES on genuine curl -- the positive control the
relational pipeline was missing. If these pass, the prior NULLs are trustworthy.
"""
import pytest

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow
from aporia.experiments.reasoning_steering.stage0b.prescreen import signal_screen
from aporia.experiments.reasoning_steering.stage0b.runner import run_h_r1
from aporia.experiments.reasoning_steering.stage0b.calibration import (
    dice_win_prob, intransitive_dice_flow, cyclic_profile, EFRON_DICE,
)
import networkx as nx


# 1. AUTHORITY — Efron's dice are non-transitive; the decomposer recovers the cycle.
def test_authority_efron_dice_cycle_and_curl():
    """A>B>C>D>A each with P=2/3 (Efron 1970), and the win-probability flow on K4 is
    curl-dominated."""
    assert dice_win_prob(EFRON_DICE["A"], EFRON_DICE["B"]) == pytest.approx(2 / 3, abs=1e-9)
    assert dice_win_prob(EFRON_DICE["B"], EFRON_DICE["C"]) == pytest.approx(2 / 3, abs=1e-9)
    assert dice_win_prob(EFRON_DICE["C"], EFRON_DICE["D"]) == pytest.approx(2 / 3, abs=1e-9)
    assert dice_win_prob(EFRON_DICE["D"], EFRON_DICE["A"]) == pytest.approx(2 / 3, abs=1e-9)

    labels, flow = intransitive_dice_flow()
    G = nx.complete_graph(len(labels))
    d = hodge_decompose(G, flow)
    assert d.curl_mass > 0.4                      # the intransitive cycle shows as curl


# 2. AUTHORITY — the scaled cyclic profile is curl-dominated at H-R1 scale.
def test_authority_cyclic_profile_is_curl_dominated():
    recs = cyclic_profile(n=30)
    G, flow = relational_flow([r["margins"] for r in recs])
    d = hodge_decompose(G, flow)
    assert d.non_gradient_mass > 0.5              # genuine, dominant curl at n=30


# 3. THE CALIBRATION — full pipeline fires on planted curl at the g2c scale.
def test_calibration_screen_pass_and_beats_null():
    """signal_screen PASSes and run_h_r1 BEATS_NULL on the n=30 cyclic profile --
    the positive control that de-ambiguates the prior NULLs (same scale, real curl)."""
    recs = cyclic_profile(n=30)
    sc = signal_screen(recs, quick_null=80, seed=0)
    assert sc.verdict == "PASS"
    rep = run_h_r1(recs, n_null=200, seed=0)
    assert rep["verdict"] == "BEATS_NULL"
    assert rep["observed"]["non_gradient_mass"] > rep["nulls"]["falsifier_column_shuffle"]["null_mean"]


# 4. EDGE
def test_edge_cases():
    with pytest.raises(ValueError):
        cyclic_profile(n=2)
    # tie handling in win-prob
    assert dice_win_prob([1, 1], [1, 1]) == pytest.approx(0.5)
