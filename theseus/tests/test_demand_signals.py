"""Tests for demand-signal logging + aggregation."""
from __future__ import annotations

import json
from pathlib import Path

from theseus.scoring.demand_signals import (
    DemandSignalLog,
    aggregate_signals,
    iter_demand_files,
)


def test_record_increments_count():
    log = DemandSignalLog()
    log.reset("b1")
    log.record("a1", "missing_int_invariant", ("knot", "alex"))
    log.record("a1", "missing_int_invariant", ("knot", "alex"))
    summary = log.summary()
    assert len(summary) == 1
    assert summary[0]["count"] == 2


def test_distinct_signatures_separate():
    log = DemandSignalLog()
    log.reset("b1")
    log.record("a1", "missing_int_invariant", ("knot", "alex"))
    log.record("a1", "missing_int_invariant", ("ec", "rank"))
    summary = log.summary()
    assert len(summary) == 2
    sigs = {tuple(s["signature"]) for s in summary}
    assert sigs == {("knot", "alex"), ("ec", "rank")}


def test_summary_sorted_descending(tmp_path):
    log = DemandSignalLog()
    log.reset("b1")
    log.record("a1", "k", ("low",))
    for _ in range(5):
        log.record("a1", "k", ("high",))
    for _ in range(2):
        log.record("a1", "k", ("mid",))
    summary = log.summary()
    counts = [s["count"] for s in summary]
    assert counts == sorted(counts, reverse=True)


def test_example_context_preserved(tmp_path):
    log = DemandSignalLog()
    log.reset("b1")
    log.record(
        "a1", "missing_int_invariant", ("knot", "alex"),
        example_context={"knot_name": "3_1", "value_seen": "polynomial"},
    )
    summary = log.summary()
    assert summary[0]["example_context"]["knot_name"] == "3_1"


def test_flush_writes_jsonl(tmp_path):
    log = DemandSignalLog()
    log.reset("test-batch")
    log.record("a1", "k", ("sig",))
    out = tmp_path / "demand.jsonl"
    log.flush(out)
    assert out.exists()
    lines = out.read_text(encoding="utf-8").strip().split("\n")
    rec = json.loads(lines[0])
    assert rec["generator_id"] == "a1"
    assert rec["kind"] == "k"
    assert rec["signature"] == ["sig"]
    assert rec["count"] == 1


def test_flush_no_signals_returns_none(tmp_path):
    log = DemandSignalLog()
    log.reset("test")
    out = log.flush(tmp_path / "demand.jsonl")
    assert out is None
    assert not (tmp_path / "demand.jsonl").exists()


def test_reset_clears_state():
    log = DemandSignalLog()
    log.reset("b1")
    log.record("a1", "k", ("sig",))
    assert len(log) == 1
    log.reset("b2")
    assert len(log) == 0
    assert log.summary() == []


def test_aggregate_signals_across_batches(tmp_path, monkeypatch):
    """Multi-batch aggregation sums counts by (gen, kind, sig) key."""
    from theseus.scoring import demand_signals as ds
    monkeypatch.setattr(ds, "JOURNAL_DIR", tmp_path)

    # Batch 1
    log1 = DemandSignalLog()
    log1.reset("b1")
    log1.record("a1", "missing_int", ("knot", "alex"))
    log1.record("a1", "missing_int", ("knot", "alex"))
    log1.flush(tmp_path / "demand_b1.jsonl")

    # Batch 2
    log2 = DemandSignalLog()
    log2.reset("b2")
    log2.record("a1", "missing_int", ("knot", "alex"))
    log2.record("g1", "no_twist_pairs", ("ec", "j"))
    log2.flush(tmp_path / "demand_b2.jsonl")

    totals = aggregate_signals(tmp_path)
    assert totals[("a1", "missing_int", ("knot", "alex"))] == 3
    assert totals[("g1", "no_twist_pairs", ("ec", "j"))] == 1


def test_aggregate_signals_empty_dir(tmp_path):
    totals = aggregate_signals(tmp_path)
    assert totals == {}


def test_iter_demand_files_globs_correctly(tmp_path):
    (tmp_path / "demand_b1.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "demand_b2.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "unrelated.jsonl").write_text("", encoding="utf-8")
    files = list(iter_demand_files(tmp_path))
    assert len(files) == 2
    assert all(f.name.startswith("demand_") for f in files)
