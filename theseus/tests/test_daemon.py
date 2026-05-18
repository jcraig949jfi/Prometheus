"""End-to-end daemon smoke test."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.daemon import run_batch


@pytest.fixture
def isolated_paths(tmp_path, monkeypatch):
    """Redirect corpus + journal paths to tmp_path so tests don't
    pollute the engine's real journal."""
    from theseus import config as cfg

    monkeypatch.setattr(cfg, "CORPUS_DIR", tmp_path / "corpus")
    monkeypatch.setattr(cfg, "JOURNAL_DIR", tmp_path / "journal")
    monkeypatch.setattr(
        cfg, "BATCH_LOG_PATH", tmp_path / "journal" / "BATCH_LOG.md"
    )
    monkeypatch.setattr(
        cfg, "BATCHES_JSONL_PATH", tmp_path / "journal" / "batches.jsonl"
    )
    return tmp_path


def test_run_batch_short_emits_records(isolated_paths):
    bm = run_batch(
        generator_ids=["a1", "b5"],
        batch_hours=0.001,  # ~3.6 seconds
        seed=0,
        corpus_dir=isolated_paths / "corpus",
        emit_telemetry=False,  # skip Postgres/Redis calls in tests
    )
    assert bm.total_records > 0
    corpus_files = list((isolated_paths / "corpus").glob("*.jsonl"))
    assert len(corpus_files) == 1
    lines = corpus_files[0].read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) > 0
    parsed = json.loads(lines[0])
    assert parsed["generator_id"] in ("a1", "b5")


def test_run_batch_filters_stubs(isolated_paths):
    bm = run_batch(
        generator_ids=["a1", "f1"],
        batch_hours=0.001,
        seed=0,
        corpus_dir=isolated_paths / "corpus",
        emit_telemetry=False,
    )
    # Only a1 ran; f1 dropped
    assert "a1" in bm.per_generator
    assert "f1" not in bm.per_generator
