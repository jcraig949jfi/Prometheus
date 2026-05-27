"""Synthetic-control tests for G19 ledger-transitivity loader.

Builds synthetic in-memory ledgers and feeds them through the
transitivity logic. Validates each decision branch (all-promoted,
any-rejected, mixed, missing).
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from charon.agents.stygian.loaders.composition_g19_ledger_transitivity import (
    run_g19_transitivity,
)


# ---------------------------------------------------------------------
# Empty / degenerate inputs
# ---------------------------------------------------------------------

def test_empty_obligation_list():
    result = run_g19_transitivity([])
    assert result["verdict"] == "UNVERIFIED"
    assert result["kill_pattern"] == "stygian_composition_no_obligations"


# ---------------------------------------------------------------------
# Synthetic-ledger branches (with monkeypatched ledger paths)
# ---------------------------------------------------------------------

@pytest.fixture
def synthetic_ledger(monkeypatch, tmp_path):
    """Build 3 synthetic ledger files (Stygian, Pollux, Erebos) and
    monkeypatch LEDGER_PATHS to point at them."""
    import charon.agents.stygian.loaders.composition_g19_ledger_transitivity as g19_mod

    stygian_path = tmp_path / "stygian.jsonl"
    pollux_path = tmp_path / "pollux.jsonl"
    erebos_path = tmp_path / "erebos.jsonl"

    monkeypatch.setattr(
        g19_mod, "LEDGER_PATHS", [stygian_path, pollux_path, erebos_path]
    )

    def write_rows(path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

    return {
        "stygian_path": stygian_path,
        "pollux_path": pollux_path,
        "erebos_path": erebos_path,
        "write_rows": write_rows,
    }


def test_all_obligations_promoted(synthetic_ledger):
    """All parents PROMOTED -> conjunction holds -> PROMOTED."""
    synthetic_ledger["write_rows"](
        synthetic_ledger["stygian_path"],
        [
            {"record_id": "p1", "verdict": "PROMOTED", "emitted_at": "2026-05-26T10:00:00Z"},
            {"record_id": "p2", "verdict": "PROMOTED", "emitted_at": "2026-05-26T10:00:00Z"},
        ],
    )
    synthetic_ledger["write_rows"](synthetic_ledger["pollux_path"], [])
    synthetic_ledger["write_rows"](synthetic_ledger["erebos_path"], [])

    result = run_g19_transitivity(["p1", "p2"])
    assert result["verdict"] == "PROMOTED"
    assert result["kill_pattern"] is None
    assert result["n_rejected"] == 0
    assert result["n_promoted"] == 2


def test_one_obligation_rejected_kills_macro(synthetic_ledger):
    """ANY parent REJECTED -> macro REJECTED with sub_claim_falsified."""
    synthetic_ledger["write_rows"](
        synthetic_ledger["stygian_path"],
        [
            {"record_id": "p1", "verdict": "PROMOTED", "emitted_at": "2026-05-26T10:00:00Z"},
            {"record_id": "p2", "verdict": "REJECTED",
             "kill_pattern": "f17_failed", "emitted_at": "2026-05-26T10:00:00Z"},
        ],
    )
    synthetic_ledger["write_rows"](synthetic_ledger["pollux_path"], [])
    synthetic_ledger["write_rows"](synthetic_ledger["erebos_path"], [])

    result = run_g19_transitivity(["p1", "p2"])
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "sub_claim_falsified"
    assert result["n_rejected"] == 1
    assert "p2" in result["rejected_parent_ids"]


def test_missing_obligations_unverified(synthetic_ledger):
    """Missing parents in ledger -> UNVERIFIED with obligation_unknown."""
    synthetic_ledger["write_rows"](synthetic_ledger["stygian_path"], [])
    synthetic_ledger["write_rows"](synthetic_ledger["pollux_path"], [])
    synthetic_ledger["write_rows"](synthetic_ledger["erebos_path"], [])

    result = run_g19_transitivity(["missing_p1", "missing_p2"])
    assert result["verdict"] == "UNVERIFIED"
    assert result["kill_pattern"] == "stygian_composition_obligation_unknown"
    assert result["n_not_found"] == 2


def test_mixed_promoted_and_unverified(synthetic_ledger):
    """Some PROMOTED, some UNVERIFIED, none REJECTED -> UNVERIFIED.
    Per loader logic: parents present-as-UNVERIFIED are NOT_FOUND-like
    for the conjunction (can't conclude)."""
    synthetic_ledger["write_rows"](
        synthetic_ledger["stygian_path"],
        [
            {"record_id": "p1", "verdict": "PROMOTED", "emitted_at": "2026-05-26T10:00:00Z"},
            {"record_id": "p2", "verdict": "UNVERIFIED", "emitted_at": "2026-05-26T10:00:00Z"},
        ],
    )
    synthetic_ledger["write_rows"](synthetic_ledger["pollux_path"], [])
    synthetic_ledger["write_rows"](synthetic_ledger["erebos_path"], [])

    result = run_g19_transitivity(["p1", "p2"])
    assert result["verdict"] == "UNVERIFIED"
    # n_promoted=1, n_rejected=0, so by loader logic this lands in the
    # "mixed but no rejection" branch with obligation_unknown.
    assert result["n_promoted"] == 1


def test_latest_emission_wins(synthetic_ledger):
    """If a parent has multiple ledger rows, latest emitted_at wins."""
    synthetic_ledger["write_rows"](
        synthetic_ledger["stygian_path"],
        [
            {"record_id": "p1", "verdict": "REJECTED",
             "kill_pattern": "old_fail", "emitted_at": "2026-05-26T08:00:00Z"},
            {"record_id": "p1", "verdict": "PROMOTED",
             "emitted_at": "2026-05-26T12:00:00Z"},
        ],
    )
    synthetic_ledger["write_rows"](synthetic_ledger["pollux_path"], [])
    synthetic_ledger["write_rows"](synthetic_ledger["erebos_path"], [])

    result = run_g19_transitivity(["p1"])
    # Latest is PROMOTED, so conjunction holds
    assert result["verdict"] == "PROMOTED"
    assert result["n_promoted"] == 1


def test_cross_ledger_lookup(synthetic_ledger):
    """Parents can live in any of Stygian/Pollux/Erebos ledgers."""
    synthetic_ledger["write_rows"](
        synthetic_ledger["stygian_path"],
        [{"record_id": "p1", "verdict": "PROMOTED",
          "emitted_at": "2026-05-26T10:00:00Z"}],
    )
    synthetic_ledger["write_rows"](
        synthetic_ledger["pollux_path"],
        [{"record_id": "p2", "verdict": "PROMOTED",
          "emitted_at": "2026-05-26T10:00:00Z"}],
    )
    synthetic_ledger["write_rows"](
        synthetic_ledger["erebos_path"],
        [{"record_id": "p3", "verdict": "PROMOTED",
          "emitted_at": "2026-05-26T10:00:00Z"}],
    )

    result = run_g19_transitivity(["p1", "p2", "p3"])
    assert result["verdict"] == "PROMOTED"
    assert result["n_promoted"] == 3
