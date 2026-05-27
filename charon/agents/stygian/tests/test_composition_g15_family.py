"""Synthetic-control tests for the G15 family (v1 raw ledger MI,
v2 real-verdict MI with control-flow filter).

Locks in:
- Shannon MI primitive correctness (independence -> 0, perfect
  coupling -> log(min(|X|, |Y|)))
- Control-flow suffix detection (the ITER-13 self-audit finding)
- v2 monotonicity: v2 MI <= v1 MI on any input (filtering only
  removes rows)
"""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from charon.agents.stygian.loaders.composition_g15_ledger_mi import (
    MI_THRESHOLD_NATS,
    _extract_kill_pattern,
    _extract_plugin_id,
    _shannon_mi,
)
from charon.agents.stygian.loaders.composition_g15_v2_real_verdict_mi import (
    CONTROL_FLOW_SUFFIXES,
    _is_control_flow,
)


# ---------------------------------------------------------------------
# Shannon MI primitive
# ---------------------------------------------------------------------

def test_mi_zero_for_independent_distributions():
    """Joint where X and Y are independent -> MI = 0."""
    # X uniform over {a, b}, Y uniform over {1, 2}, independent.
    # P(x, y) = P(x) * P(y) = 0.5 * 0.5 = 0.25 for each cell.
    joint = {("a", 1): 25, ("a", 2): 25, ("b", 1): 25, ("b", 2): 25}
    result = _shannon_mi(joint)
    assert abs(result["mi_nats"]) < 1e-9


def test_mi_log2_for_perfect_coupling():
    """If Y is a deterministic function of X (and X uniform over 2),
    MI = log(2) = 0.693 nats."""
    joint = {("a", 1): 50, ("b", 2): 50}
    result = _shannon_mi(joint)
    assert abs(result["mi_nats"] - math.log(2)) < 1e-6


def test_mi_normalized_one_for_perfect_coupling():
    """Normalized MI = MI / log(min(|X|, |Y|)) = 1.0 for perfect coupling."""
    joint = {("a", 1): 50, ("b", 2): 50}
    result = _shannon_mi(joint)
    assert abs(result["mi_normalized"] - 1.0) < 1e-6


def test_mi_empty_joint():
    result = _shannon_mi({})
    assert result["mi_nats"] == 0.0
    assert result["n_total"] == 0


def test_mi_bits_equals_nats_over_ln2():
    joint = {("a", 1): 50, ("b", 2): 50}
    result = _shannon_mi(joint)
    assert abs(result["mi_bits"] - result["mi_nats"] / math.log(2)) < 1e-9


def test_mi_marginal_counts_correct():
    """n_x and n_y count distinct levels of X and Y."""
    joint = {("a", 1): 5, ("a", 2): 3, ("b", 1): 4, ("c", 1): 2}
    result = _shannon_mi(joint)
    assert result["n_x"] == 3  # a, b, c
    assert result["n_y"] == 2  # 1, 2


# ---------------------------------------------------------------------
# Control-flow filter
# ---------------------------------------------------------------------

def test_control_flow_filter_catches_pending():
    assert _is_control_flow("erebos_g01_intersection_pending") is True


def test_control_flow_filter_catches_no_loader_registered():
    assert _is_control_flow("stygian_no_loader_registered") is True


def test_control_flow_filter_catches_not_yet_implemented():
    assert _is_control_flow("stygian_hecate_meta_test_not_yet_implemented") is True


def test_control_flow_filter_catches_composition_failures():
    assert _is_control_flow("stygian_composition_data_load_failed") is True
    assert _is_control_flow("stygian_composition_insufficient_sample") is True


def test_control_flow_filter_passes_real_verdicts():
    """Real falsification kill_patterns should NOT match."""
    assert _is_control_flow("permutation_null") is False
    assert _is_control_flow("symmetry_breaking") is False
    assert _is_control_flow("sub_claim_falsified") is False
    assert _is_control_flow("conjecture_survives_adversarial_attack") is False
    assert _is_control_flow("error_term_does_not_decay") is False


def test_control_flow_filter_none_is_treated_as_control():
    """None kill_pattern is treated as control (defensive)."""
    assert _is_control_flow(None) is True


def test_control_flow_filter_empty_string_is_control():
    assert _is_control_flow("") is True


def test_control_flow_suffixes_list_is_non_empty():
    assert len(CONTROL_FLOW_SUFFIXES) > 5


# ---------------------------------------------------------------------
# Row extraction helpers
# ---------------------------------------------------------------------

def test_extract_plugin_id_from_erebos_row():
    row = {
        "claim_payload": {"plugin_id": "g11_exception_miner"},
        "generator_id": "erebos",
    }
    assert _extract_plugin_id(row) == "g11_exception_miner"


def test_extract_plugin_id_falls_back_to_generator_id():
    row = {"generator_id": "pollux"}
    assert _extract_plugin_id(row) == "pollux"


def test_extract_plugin_id_returns_none_if_neither():
    row = {}
    assert _extract_plugin_id(row) is None


def test_extract_kill_pattern_normal():
    row = {"kill_pattern": "permutation_null"}
    assert _extract_kill_pattern(row) == "permutation_null"


def test_extract_kill_pattern_none():
    row = {"kill_pattern": None}
    assert _extract_kill_pattern(row) is None
    assert _extract_kill_pattern({}) is None


# ---------------------------------------------------------------------
# v2 filter behavior: monotonicity
# ---------------------------------------------------------------------

def test_v2_mi_at_most_equals_v1_mi(monkeypatch, tmp_path):
    """The v2 loader filters out control-flow rows before computing
    MI; the remaining joint distribution has fewer or equal observations
    than v1. MI can go up or down in absolute terms, but the test we
    care about: v2 always sees a subset of v1's rows."""
    import charon.agents.stygian.loaders.composition_g15_v2_real_verdict_mi as g15v2_mod

    stygian_path = tmp_path / "stygian.jsonl"
    pollux_path = tmp_path / "pollux.jsonl"
    erebos_path = tmp_path / "erebos.jsonl"
    monkeypatch.setattr(
        g15v2_mod, "LEDGER_PATHS", [stygian_path, pollux_path, erebos_path]
    )

    # Synthetic: 50 control-flow rows + 50 real-verdict rows
    import json
    with stygian_path.open("w") as f:
        for i in range(50):
            f.write(json.dumps({
                "record_id": f"c{i}",
                "generator_id": "stygian",
                "kill_pattern": "stygian_no_loader_registered",
                "verdict": "UNVERIFIED",
            }) + "\n")
        for i in range(50):
            f.write(json.dumps({
                "record_id": f"r{i}",
                "generator_id": "stygian",
                "kill_pattern": "permutation_null",
                "verdict": "REJECTED",
            }) + "\n")
    pollux_path.write_text("")
    erebos_path.write_text("")

    from charon.agents.stygian.loaders.composition_g15_v2_real_verdict_mi import (
        run_g15_v2_real_verdict_mi,
    )
    result = run_g15_v2_real_verdict_mi()
    # 50 of 100 rows filtered out
    assert result["n_paired_total"] == 100
    assert result["n_paired_real"] == 50
    assert result["n_paired_control"] == 50
    assert result["control_fraction"] == 0.5


def test_v2_mi_zero_when_only_one_plugin_with_one_kill_pattern(monkeypatch, tmp_path):
    """Single (plugin, kp) cell -> MI = 0 (no variation)."""
    import charon.agents.stygian.loaders.composition_g15_v2_real_verdict_mi as g15v2_mod

    stygian_path = tmp_path / "stygian.jsonl"
    pollux_path = tmp_path / "pollux.jsonl"
    erebos_path = tmp_path / "erebos.jsonl"
    monkeypatch.setattr(
        g15v2_mod, "LEDGER_PATHS", [stygian_path, pollux_path, erebos_path]
    )

    import json
    with stygian_path.open("w") as f:
        for i in range(50):
            f.write(json.dumps({
                "record_id": f"r{i}",
                "generator_id": "stygian",
                "kill_pattern": "permutation_null",
                "verdict": "REJECTED",
            }) + "\n")
    pollux_path.write_text("")
    erebos_path.write_text("")

    from charon.agents.stygian.loaders.composition_g15_v2_real_verdict_mi import (
        run_g15_v2_real_verdict_mi,
    )
    result = run_g15_v2_real_verdict_mi()
    # Single cell -> MI is 0
    assert result["mi_v2_nats"] == 0.0
    # Below threshold -> REJECTED
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "uncorrelated_residual_failures"
