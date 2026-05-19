"""Smoke tests for Penelope.

Asserts the orchestration shape works without touching agora/Postgres or
running the real ingester subprocess. Use this as the always-green floor
before refactoring.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from ergon.penelope import config as cfg
from ergon.penelope.state import processed_ledger as pl
from ergon.penelope.sources import REGISTERED_SOURCES, discover_candidates
from ergon.penelope.orchestration import lifetime as lt


def test_registered_sources_have_names_and_scanners():
    assert {s.name for s in REGISTERED_SOURCES} == {"theseus", "aporia_staged", "techne_mined"}
    for src in REGISTERED_SOURCES:
        result = src.scanner()
        assert isinstance(result, list)
        for p in result:
            assert isinstance(p, Path)
        assert src.runner_type in {"training_anchor", "claim_batch"}


def test_discover_candidates_returns_source_path_runner_tuples():
    candidates = discover_candidates()
    assert isinstance(candidates, list)
    for item in candidates:
        assert len(item) == 3
        source_name, path, runner_type = item
        assert isinstance(source_name, str)
        assert isinstance(path, Path)
        assert runner_type in {"training_anchor", "claim_batch"}


def test_techne_mined_source_finds_claim_jsonls():
    """Sanity: scan_techne_mined returns the per-category claim files (if any
    exist on disk). At minimum, the scanner should not crash and should
    return claim-category-named files when they exist."""
    from ergon.penelope.sources import scan_techne_mined
    result = scan_techne_mined()
    for p in result:
        assert p.name in {"boundary.jsonl", "frontier_survey.jsonl", "substrate_self.jsonl"}
        assert p.stat().st_size > 0


def test_theseus_outbox_excludes_combined_intermediates():
    from ergon.penelope.sources import scan_theseus_outbox
    for p in scan_theseus_outbox():
        assert not p.name.startswith("_combined_")


def test_ledger_round_trip(tmp_path: Path):
    ledger = tmp_path / "ledger.jsonl"
    sample_file = tmp_path / "sample.jsonl"
    sample_file.write_text('{"x": 1}\n', encoding="utf-8")

    entry = pl.make_entry(
        file_path=sample_file,
        source="test",
        batch_id="penelope-test-001",
        n_records_ingested=1,
        n_records_dropped=0,
        validation_failures=0,
        result="success",
    )
    pl.append_entry(entry, ledger_path=ledger)

    keys = pl.load_processed_keys(ledger_path=ledger)
    assert (str(sample_file), entry.sha256) in keys
    assert len(keys) == 1


def test_ledger_idempotency_same_file(tmp_path: Path):
    ledger = tmp_path / "ledger.jsonl"
    sample = tmp_path / "f.jsonl"
    sample.write_text("a\n", encoding="utf-8")
    e1 = pl.make_entry(
        file_path=sample, source="s", batch_id="b1",
        n_records_ingested=0, n_records_dropped=0,
        validation_failures=0, result="success",
    )
    pl.append_entry(e1, ledger_path=ledger)
    # Same file content, second batch → same key
    e2 = pl.make_entry(
        file_path=sample, source="s", batch_id="b2",
        n_records_ingested=0, n_records_dropped=0,
        validation_failures=0, result="success",
    )
    assert e1.sha256 == e2.sha256
    keys = pl.load_processed_keys(ledger_path=ledger)
    assert len(keys) == 1


def test_lifetime_empty_when_no_file(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(lt, "LIFETIME_PATH", tmp_path / "absent.json")
    stats = lt.load_lifetime_stats()
    assert stats["batches_completed"] == 0
    assert stats["lifetime_records_ingested"] == 0


def test_lifetime_merge_round_trip(tmp_path: Path, monkeypatch):
    target = tmp_path / "lt.json"
    monkeypatch.setattr(lt, "LIFETIME_PATH", target)
    summary: Dict[str, Any] = {
        "files_ingested": 3,
        "files_skipped_duplicate": 1,
        "files_failed": 0,
        "records_ingested": 250,
        "records_dropped": 0,
        "validation_failures": 0,
        "per_source": {"theseus": 250},
        "per_domain": {"knots_x_elliptic_curves": 250},
    }
    after = lt.update_lifetime_after_batch(summary)
    assert after["batches_completed"] == 1
    assert after["lifetime_records_ingested"] == 250
    assert after["per_source_lifetime"]["theseus"] == 250

    after2 = lt.update_lifetime_after_batch(summary)
    assert after2["batches_completed"] == 2
    assert after2["lifetime_records_ingested"] == 500
    assert after2["per_source_lifetime"]["theseus"] == 500


def test_run_batch_no_telemetry_runs_clean(monkeypatch, tmp_path: Path):
    """End-to-end: clear ledger + lifetime, run_batch() without telemetry,
    verify summary shape and that the lifetime path got bumped."""
    from ergon.penelope import daemon as d

    monkeypatch.setattr(cfg, "PROCESSED_LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(pl, "PROCESSED_LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(d.cfg, "PROCESSED_LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(d.cfg, "JOURNAL_DIR", tmp_path / "journals")
    monkeypatch.setattr(d.cfg, "BATCHES_JSONL_PATH", tmp_path / "journals" / "batches.jsonl")
    monkeypatch.setattr(d.cfg, "BATCH_LOG_PATH", tmp_path / "journals" / "BATCH_LOG.md")
    monkeypatch.setattr(lt, "LIFETIME_PATH", tmp_path / "lt.json")

    # Replace candidate discovery with empty list so we don't actually
    # invoke ingest_training_anchors.py
    monkeypatch.setattr(d, "discover_candidates", lambda: [])

    summary = d.run_batch(emit_telemetry=False)
    assert summary["files_ingested"] == 0
    assert summary["files_skipped_duplicate"] == 0
    assert "batch_id" in summary
    assert summary["batch_id"].startswith("penelope-")
    assert (tmp_path / "journals" / "batches.jsonl").exists()
