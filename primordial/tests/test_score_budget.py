"""F13 budget enforcement: shares from the worker done streams, one warning per OVER cohort per epoch."""
from __future__ import annotations

import json

import pytest

from primordial.bus import bus
from primordial.score import budget as BU


def led(**cpu):
    return {k: {"cpu_s": v, "metered": True} for k, v in cpu.items()}


def test_report_flags_over_share_and_holds_on_small_or_unmetered_totals():
    rep = BU.report(led(B=50.0, C=20.0, D=20.0, E=10.0))
    assert {k: v["verdict"] for k, v in rep["lanes"].items()} == {"B": "OVER", "C": "WITHIN", "D": "WITHIN", "E": "WITHIN"}
    assert rep["lanes"]["B"]["actual"] == 0.5 and rep["lanes"]["B"]["over_cpu_s"] == 10.0
    assert rep["lanes"]["E"]["verdict"] == "WITHIN"                      # exactly at share is within
    small = BU.report(led(B=30.0, C=0.0, D=0.0, E=0.0))
    assert set(v["verdict"] for v in small["lanes"].values()) == {"INDETERMINATE"} and "< 60" in small["why_indeterminate"]
    gap = BU.report({**led(B=500.0, C=500.0, D=0.0), "E": {"cpu_s": 0.0, "metered": False}})
    assert gap["lanes"]["B"]["verdict"] == "INDETERMINATE" and "['E']" in gap["why_indeterminate"]


def test_round2_replay_is_indeterminate_because_most_cohorts_recorded_no_cpu():
    ledger = BU.rows_ledger()
    assert ledger["C"]["metered"] and ledger["C"]["cpu_s"] > 0
    assert not ledger["B"]["metered"] and not ledger["D"]["metered"]
    rep = BU.report(ledger)
    assert rep["why_indeterminate"].startswith("unmetered cohorts")


@pytest.fixture
def live(monkeypatch):
    redis = pytest.importorskip("redis")
    from primordial.tests._live import live_url
    url = live_url()
    r = redis.Redis.from_url(url, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    r.flushdb()
    monkeypatch.setattr(bus, "URL", url)
    monkeypatch.setenv("PM_LANE", "H")
    monkeypatch.setenv("PM_TAG", "test-h")
    yield r
    r.flushdb()


def _job(r, lane, job_id, exp, ms, cpu, status="ok"):
    r.xadd(BU.JOBS.format(lane), {"job_id": job_id, "exp_id": exp, "fn": "m:f", "ttl_cpu_s": "60"}, id=f"{ms - 1}-0")
    r.xadd(BU.DONE.format(lane), {"json": json.dumps({"job_id": job_id, "status": status, "cpu_s": cpu})}, id=f"{ms}-0")


def test_job_ledger_reads_done_streams_inside_the_window(live):
    _job(live, "B", "j1", "B-x", 1000, 12.5)
    _job(live, "B", "j2", "B-x", 2000, 7.5, "timeout")
    _job(live, "B", "j3", "B-y", 3000, None, "died")
    _job(live, "B", "j4", "B-late", 9000, 99.0)
    got = BU.job_ledger(live, lanes=("B", "C"), window=(0.5, 5.0))
    b = got["B"]
    assert b["cpu_s"] == 20.0 and b["jobs"] == 3 and b["cpu_unknown_jobs"] == 1
    assert b["status"] == {"ok": 1, "timeout": 1, "died": 1} and b["by_exp"] == {"B-x": 20.0}
    assert got["C"]["jobs"] == 0 and got["C"]["cpu_s"] == 0.0


def test_warning_is_posted_once_per_cohort_per_epoch(live):
    rep = BU.report(led(B=80.0, C=10.0, D=5.0, E=5.0))
    assert BU.warn(rep, 7, live) == ["B"]
    assert BU.warn(rep, 7, live) == []                                   # same epoch: deduplicated
    assert BU.warn(rep, 8, live) == ["B"]
    posts = [f for _, f in live.xrange(bus.SWARM) if f["subject"].startswith("BUDGET WARNING")]
    assert len(posts) == 2 and posts[0]["to"] == "B,A" and json.loads(posts[0]["body"])["verdict"] == "OVER"
