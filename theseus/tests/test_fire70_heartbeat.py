"""Fire #70 heartbeat logger tests.

Background: Fire #70 stalled silently for 60+ minutes with no
observability. This module's HeartbeatLogger provides per-tick
instrumentation + periodic snapshots.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from theseus.orchestration.heartbeat import HeartbeatLogger


def _read_lines(path: Path) -> list:
    return [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]


def test_heartbeat_writes_start_event(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test1",
        journal_dir=tmp_path,
        interval_seconds=30.0,
        tee_stdout=False,
    )
    hb.start(["a1", "b2"])
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test1.jsonl")
    assert len(lines) == 1
    assert lines[0]["event"] == "batch_start"
    assert lines[0]["generator_ids"] == ["a1", "b2"]


def test_heartbeat_records_tick_durations(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test2",
        journal_dir=tmp_path,
        slow_next_threshold_seconds=0.05,  # 50ms threshold
        tee_stdout=False,
    )
    hb.start(["a1"])
    with hb.tick("a1"):
        time.sleep(0.1)  # > 50ms threshold
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test2.jsonl")
    slow = [l for l in lines if l.get("event") == "slow_next"]
    assert len(slow) == 1
    assert slow[0]["generator_id"] == "a1"
    assert slow[0]["next_seconds"] >= 0.05


def test_heartbeat_record_result_tracks_consecutive_nones(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test3",
        journal_dir=tmp_path,
        interval_seconds=0.01,  # fast snapshot for test
        tee_stdout=False,
    )
    hb.start(["a1"])
    for _ in range(5):
        with hb.tick("a1"):
            pass
        hb.record_result("a1", None)
    # Force a snapshot regardless of interval
    time.sleep(0.05)
    hb.maybe_snapshot(tick_count=5, records_written=0)
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test3.jsonl")
    snaps = [l for l in lines if l.get("event") == "snapshot"]
    assert len(snaps) >= 1
    assert snaps[-1]["per_gen"]["a1"]["consec_nones"] == 5
    assert snaps[-1]["per_gen"]["a1"]["records"] == 0


def test_heartbeat_resets_consec_nones_on_record(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test4",
        journal_dir=tmp_path,
        interval_seconds=0.01,
        tee_stdout=False,
    )
    hb.start(["a1"])
    for _ in range(3):
        with hb.tick("a1"):
            pass
        hb.record_result("a1", None)
    with hb.tick("a1"):
        pass
    hb.record_result("a1", {"r": 1})  # emission resets nones
    time.sleep(0.05)
    hb.maybe_snapshot(tick_count=4, records_written=1)
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test4.jsonl")
    snaps = [l for l in lines if l.get("event") == "snapshot"]
    assert snaps[-1]["per_gen"]["a1"]["consec_nones"] == 0
    assert snaps[-1]["per_gen"]["a1"]["records"] == 1


def test_heartbeat_mark_exhausted_writes_event(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test5",
        journal_dir=tmp_path,
        tee_stdout=False,
    )
    hb.start(["a1"])
    hb.mark_exhausted("a1")
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test5.jsonl")
    exh = [l for l in lines if l.get("event") == "exhausted"]
    assert len(exh) == 1
    assert exh[0]["generator_id"] == "a1"


def test_heartbeat_snapshot_includes_tick_rate(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test6",
        journal_dir=tmp_path,
        interval_seconds=0.01,
        tee_stdout=False,
    )
    hb.start(["a1"])
    time.sleep(0.1)
    hb.maybe_snapshot(tick_count=100, records_written=50)
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test6.jsonl")
    snaps = [l for l in lines if l.get("event") == "snapshot"]
    assert snaps[-1]["tick_count"] == 100
    assert snaps[-1]["records_written"] == 50
    assert snaps[-1]["tick_rate_per_s"] > 0  # 100 ticks / 0.1+s


def test_heartbeat_final_snapshot_kind(tmp_path):
    hb = HeartbeatLogger(
        batch_id="test7",
        journal_dir=tmp_path,
        tee_stdout=False,
    )
    hb.start(["a1"])
    hb.final_snapshot(tick_count=5, records_written=3)
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test7.jsonl")
    snaps = [l for l in lines if l.get("event") == "snapshot"]
    assert snaps[-1]["kind"] == "final"


def test_heartbeat_per_gen_metrics_separate(tmp_path):
    """Two gens, different tick patterns — stats stay separate."""
    hb = HeartbeatLogger(
        batch_id="test8",
        journal_dir=tmp_path,
        interval_seconds=0.01,
        tee_stdout=False,
    )
    hb.start(["a1", "b2"])
    for _ in range(10):
        with hb.tick("a1"):
            pass
        hb.record_result("a1", None)
    with hb.tick("b2"):
        pass
    hb.record_result("b2", {"r": 1})
    time.sleep(0.05)
    hb.maybe_snapshot(tick_count=11, records_written=1)
    hb.close()
    lines = _read_lines(tmp_path / "heartbeat_test8.jsonl")
    snap = next(l for l in reversed(lines) if l.get("event") == "snapshot")
    assert snap["per_gen"]["a1"]["records"] == 0
    assert snap["per_gen"]["a1"]["consec_nones"] == 10
    assert snap["per_gen"]["b2"]["records"] == 1
    assert snap["per_gen"]["b2"]["consec_nones"] == 0
