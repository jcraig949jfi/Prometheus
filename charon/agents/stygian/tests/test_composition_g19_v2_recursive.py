"""Synthetic-control tests for G19 v2 recursive obligation walk."""
from __future__ import annotations

import json

import pytest

from charon.agents.stygian.loaders.composition_g19_v2_recursive_obligations import (
    MAX_RECURSION_DEPTH,
    _direct_parents,
    _walk_obligations,
    run_g19_v2_recursive_obligations,
)


# ---------------------------------------------------------------------
# _direct_parents primitive
# ---------------------------------------------------------------------

def test_direct_parents_from_extras_field():
    row = {"extras": {"parent_record_ids": ["p1", "p2", "p3"]}}
    assert _direct_parents(row) == ["p1", "p2", "p3"]


def test_direct_parents_from_composition_payload():
    row = {"extras": {"composition_payload": {"parent_record_ids": ["q1"]}}}
    assert _direct_parents(row) == ["q1"]


def test_direct_parents_empty():
    assert _direct_parents({}) == []
    assert _direct_parents({"extras": {}}) == []


def test_direct_parents_strips_none_and_empty():
    row = {"extras": {"parent_record_ids": ["p1", None, "", "p2"]}}
    assert _direct_parents(row) == ["p1", "p2"]


# ---------------------------------------------------------------------
# _walk_obligations BFS
# ---------------------------------------------------------------------

def test_walk_finds_single_leaf():
    """root has no children -> root IS the leaf."""
    by_id = {
        "root": {"record_id": "root", "verdict": "PROMOTED"},
    }
    walk = _walk_obligations(["root"], by_id)
    assert len(walk["leaves"]) == 1
    assert walk["leaves"][0]["record_id"] == "root"


def test_walk_descends_to_leaves():
    """root -> p1, p2 (each a leaf)."""
    by_id = {
        "root": {
            "record_id": "root",
            "verdict": "UNVERIFIED",
            "extras": {"parent_record_ids": ["p1", "p2"]},
        },
        "p1": {"record_id": "p1", "verdict": "PROMOTED"},
        "p2": {"record_id": "p2", "verdict": "PROMOTED"},
    }
    walk = _walk_obligations(["root"], by_id)
    leaf_ids = {l["record_id"] for l in walk["leaves"]}
    assert leaf_ids == {"p1", "p2"}
    assert walk["depth_reached"] == 1


def test_walk_descends_multiple_levels():
    """root -> p1 -> q1, q2."""
    by_id = {
        "root": {
            "record_id": "root", "verdict": "UNVERIFIED",
            "extras": {"parent_record_ids": ["p1"]},
        },
        "p1": {
            "record_id": "p1", "verdict": "UNVERIFIED",
            "extras": {"parent_record_ids": ["q1", "q2"]},
        },
        "q1": {"record_id": "q1", "verdict": "PROMOTED"},
        "q2": {"record_id": "q2", "verdict": "PROMOTED"},
    }
    walk = _walk_obligations(["root"], by_id)
    leaf_ids = {l["record_id"] for l in walk["leaves"]}
    assert leaf_ids == {"q1", "q2"}
    assert walk["depth_reached"] == 2


def test_walk_detects_cycle():
    """A -> B -> A -> ... must NOT loop forever."""
    by_id = {
        "A": {"record_id": "A", "verdict": "UNVERIFIED",
              "extras": {"parent_record_ids": ["B"]}},
        "B": {"record_id": "B", "verdict": "UNVERIFIED",
              "extras": {"parent_record_ids": ["A"]}},
    }
    walk = _walk_obligations(["A"], by_id)
    assert walk["cycle_detected"] is True


def test_walk_records_missing():
    """Reference to non-existent parent is recorded."""
    by_id = {
        "root": {"record_id": "root", "verdict": "UNVERIFIED",
                 "extras": {"parent_record_ids": ["nonexistent_p"]}},
    }
    walk = _walk_obligations(["root"], by_id)
    assert "nonexistent_p" in walk["missing"]


def test_walk_respects_depth_cap():
    """Linear chain longer than MAX_RECURSION_DEPTH is truncated."""
    by_id = {}
    chain_length = MAX_RECURSION_DEPTH + 3
    for i in range(chain_length):
        children = [f"n{i+1}"] if i < chain_length - 1 else []
        by_id[f"n{i}"] = {
            "record_id": f"n{i}", "verdict": "UNVERIFIED",
            "extras": {"parent_record_ids": children},
        }
    walk = _walk_obligations(["n0"], by_id, max_depth=MAX_RECURSION_DEPTH)
    assert walk["depth_reached"] <= MAX_RECURSION_DEPTH


# ---------------------------------------------------------------------
# End-to-end verdicts via synthetic ledger
# ---------------------------------------------------------------------

@pytest.fixture
def synthetic_v2_ledger(monkeypatch, tmp_path):
    """Helper that builds synthetic ledger and points the loader at it."""
    import charon.agents.stygian.loaders.composition_g19_v2_recursive_obligations as g19v2_mod
    import charon.agents.stygian.loaders.composition_g19_ledger_transitivity as g19_v1_mod

    stygian = tmp_path / "stygian.jsonl"
    pollux = tmp_path / "pollux.jsonl"
    erebos = tmp_path / "erebos.jsonl"

    # v2 imports LEDGER_PATHS via from-import; patch both modules
    monkeypatch.setattr(g19v2_mod, "LEDGER_PATHS", [stygian, pollux, erebos])
    monkeypatch.setattr(g19_v1_mod, "LEDGER_PATHS", [stygian, pollux, erebos])

    def write(path, rows):
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

    return {"stygian": stygian, "pollux": pollux, "erebos": erebos,
            "write": write}


def test_v2_recursive_deep_rejected_leaf_kills_macro(synthetic_v2_ledger):
    """Macro has direct parents all PROMOTED, but a DEEP leaf is
    REJECTED. v1 would say PROMOTED; v2 must say REJECTED."""
    fix = synthetic_v2_ledger
    fix["write"](fix["stygian"], [
        {"record_id": "p1", "verdict": "PROMOTED",
         "emitted_at": "2026-05-26T10:00:00Z",
         "extras": {"parent_record_ids": ["q1", "q2"]}},
        {"record_id": "q1", "verdict": "PROMOTED",
         "emitted_at": "2026-05-26T10:00:00Z"},
        {"record_id": "q2", "verdict": "REJECTED",
         "emitted_at": "2026-05-26T10:00:00Z",
         "kill_pattern": "f17_failed"},
    ])
    fix["write"](fix["pollux"], [])
    fix["write"](fix["erebos"], [])

    result = run_g19_v2_recursive_obligations(["p1"])
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "sub_claim_falsified"
    assert "q2" in result["rejected_leaf_ids"]
    assert result["depth_reached"] >= 1


def test_v2_recursive_all_leaves_promoted_promotes(synthetic_v2_ledger):
    fix = synthetic_v2_ledger
    fix["write"](fix["stygian"], [
        {"record_id": "p1", "verdict": "PROMOTED",
         "emitted_at": "2026-05-26T10:00:00Z",
         "extras": {"parent_record_ids": ["q1", "q2"]}},
        {"record_id": "q1", "verdict": "PROMOTED",
         "emitted_at": "2026-05-26T10:00:00Z"},
        {"record_id": "q2", "verdict": "PROMOTED",
         "emitted_at": "2026-05-26T10:00:00Z"},
    ])
    fix["write"](fix["pollux"], [])
    fix["write"](fix["erebos"], [])

    result = run_g19_v2_recursive_obligations(["p1"])
    assert result["verdict"] == "PROMOTED"
    assert result["n_promoted_leaves"] == 2


def test_v2_empty_obligation_list():
    result = run_g19_v2_recursive_obligations([])
    assert result["verdict"] == "UNVERIFIED"
    assert result["kill_pattern"] == "stygian_composition_no_obligations"
