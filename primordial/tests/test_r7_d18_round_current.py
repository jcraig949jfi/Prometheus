"""D18 (round 6 -> 7): a CLOSED round still named by pm:round:current must not be the active clock. round_clock.read(r)
(the current-round lookup admission uses) returns None once now > end_ts or pm:epoch:state marks that round closed,
so a build-phase job is admitted again; read(r, round_id) still returns the hash as history."""
from __future__ import annotations

import time

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
RID = "t-r7-d18"
LANE = "Fd18"


@pytest.fixture
def r(monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [RC.CURRENT, RC.KEY.format(RID), RC.EPOCH_STATE, W.JOBS.format(LANE), W.DONE.format(LANE),
            W.ROWS.format(LANE), W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-d18")
    yield r
    r.delete(*keys)


def test_past_end_ts_is_not_current(r):
    c = RC.start(r, RID, start_ts=1000.0, epoch_s=10, epochs=1, drain_s=10, close_s=10)   # ended at 1030
    assert r.get(RC.CURRENT) == RID
    assert RC.read(r, now=1020.0) == c                                  # still inside the round
    assert RC.read(r, now=1031.0) is None and RC.read(r) is None        # over: no active clock
    assert RC.read(r, RID) == c                                          # history stays readable
    assert RC.start(r, RID, start_ts=99999.0) == c                       # start stays idempotent


def test_epoch_state_closed_is_not_current(r):
    now = time.time()
    RC.start(r, RID, start_ts=now - 5, epoch_s=3600, epochs=1, drain_s=60, close_s=60)
    assert RC.read(r) is not None
    r.hset(RC.EPOCH_STATE, mapping={"phase": "closed", "round_id": "other-round"})
    assert RC.read(r) is not None                                        # another round's close does not count
    r.hset(RC.EPOCH_STATE, mapping={"phase": "closed", "round_id": RID})
    assert RC.read(r) is None and RC.read(r, RID)["round_id"] == RID


def test_admission_after_close_is_not_no_new_work(r, tmp_path):
    """The D18 symptom: every job refused NO_NEW_WORK after the round closed."""
    import subprocess
    RC.start(r, RID, start_ts=1000.0, epoch_s=10, epochs=1, drain_s=10, close_s=10)
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", "d18", "rows/d18.jsonl", 30, {"n": 1}, r=r,
             envelope=EV.example())
    done = W.Worker(LANE, url=URL, repo=tmp_path, log=lambda *_: None, broker=False).serve(max_jobs=1, block_ms=300)
    assert done[0]["status"] == "ok" and EV.events(r, EV.NO_NEW_WORK_REFUSAL) == []
