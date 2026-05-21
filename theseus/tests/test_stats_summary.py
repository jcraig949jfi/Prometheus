"""Smoke tests for theseus.scripts.stats_summary."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from theseus.scripts.stats_summary import (
    collect_summary,
    render_text,
    _fmt_int,
)


def test_fmt_int_millions():
    assert _fmt_int(5_000_000) == "5.00M"
    assert _fmt_int(174_562_011) == "174.56M"


def test_fmt_int_thousands():
    assert _fmt_int(5000) == "5.0k"
    assert _fmt_int(1234) == "1.2k"


def test_fmt_int_small():
    assert _fmt_int(42) == "42"
    assert _fmt_int(0) == "0"


def test_collect_summary_handles_empty_state(tmp_path, monkeypatch):
    """Missing files → empty summary that doesn't crash."""
    from theseus.scripts import stats_summary as ss
    monkeypatch.setattr(ss, "LIFETIME_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(ss, "BANDIT_HISTORY_PATH", tmp_path / "missing2.json")
    monkeypatch.setattr(ss, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(ss, "BATCHES_JSONL_PATH", tmp_path / "batches.jsonl")
    summary = ss.collect_summary()
    assert summary["lifetime"] == {}
    assert summary["generators"] == {}
    assert summary["recent_batches"] == []
    assert summary["caches"]["arxiv"] == 0


def test_render_text_handles_missing_lifetime():
    """When lifetime file is empty, render gracefully."""
    out = render_text({"lifetime": {}, "generators": {}, "recent_batches": [],
                       "caches": {}})
    assert "no lifetime_stats" in out.lower()


def test_collect_summary_with_data(tmp_path, monkeypatch):
    """Round-trip: write some test data, collect_summary returns it."""
    from theseus.scripts import stats_summary as ss
    monkeypatch.setattr(ss, "LIFETIME_PATH", tmp_path / "lifetime.json")
    monkeypatch.setattr(ss, "BANDIT_HISTORY_PATH", tmp_path / "bandit.json")
    monkeypatch.setattr(ss, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(ss, "BATCHES_JSONL_PATH", tmp_path / "batches.jsonl")

    (tmp_path / "lifetime.json").write_text(json.dumps({
        "batches_completed": 5,
        "lifetime_records": 1_000_000,
        "lifetime_kills": 500_000,
        "lifetime_confirmations": 480_000,
        "lifetime_inconclusive": 20_000,
        "lifetime_errors": 0,
        "lifetime_discoveries_emitted": 10,
        "per_generator_lifetime": {"a1": 800_000, "g3": 20_000},
    }))
    (tmp_path / "bandit.json").write_text(json.dumps({
        "version": 1,
        "yield_scores": {"a1": [0.0039, 0.0040], "g3": [0.0052, 0.0050]},
    }))
    summary = ss.collect_summary()
    assert summary["lifetime"]["batches_completed"] == 5
    assert summary["generators"]["a1"]["fires"] == 2
    assert summary["generators"]["g3"]["yield_score_mean"] == pytest.approx(0.0051)


def test_render_text_emits_expected_sections(tmp_path, monkeypatch):
    """Output contains the section headers."""
    from theseus.scripts import stats_summary as ss
    monkeypatch.setattr(ss, "LIFETIME_PATH", tmp_path / "lifetime.json")
    monkeypatch.setattr(ss, "BANDIT_HISTORY_PATH", tmp_path / "bandit.json")
    monkeypatch.setattr(ss, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(ss, "BATCHES_JSONL_PATH", tmp_path / "batches.jsonl")

    (tmp_path / "lifetime.json").write_text(json.dumps({
        "batches_completed": 1,
        "lifetime_records": 100,
        "lifetime_kills": 50,
        "lifetime_confirmations": 50,
        "lifetime_inconclusive": 0,
        "lifetime_errors": 0,
        "lifetime_discoveries_emitted": 0,
        "per_generator_lifetime": {"a1": 100},
    }))
    summary = ss.collect_summary()
    out = render_text(summary)
    assert "THESEUS LIFETIME SUMMARY" in out
    assert "kill share" in out
    assert "CACHES" in out
    assert "TOP-VOLUME GENERATORS" in out
