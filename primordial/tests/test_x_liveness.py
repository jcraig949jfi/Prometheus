"""X: liveness. A quiet lane (transcript stale, heartbeat lapsed) that is doing work -- CPU in
its process tree or a live F7 worker -- is BUSY, not STALE (round 2: E flagged during a
background run). No Redis or processes: every source is faked."""
from __future__ import annotations

import datetime

import pytest

from primordial.bus import bus
from primordial.ops import liveness as lv

NOW = datetime.datetime.now().astimezone().isoformat()


class FakeR:
    def __init__(self, workers=()):
        self.workers = set(workers)

    def exists(self, key):
        return int(key.rsplit(":", 1)[-1] in self.workers and key.startswith("pm:worker:"))


@pytest.fixture
def world(monkeypatch):
    launches = {"B": {"pid": 101, "start": NOW, "session_id": "sB"},     # quiet, child burning CPU
                "C": {"pid": 102, "start": NOW, "session_id": "sC"},     # quiet, nothing running
                "D": {"pid": 103, "start": NOW, "session_id": "sD"},     # quiet, live F7 worker
                "E": {"pid": 104, "start": NOW, "session_id": "sE"},     # fresh transcript
                "G": {"pid": 105, "start": NOW, "session_id": "sG"},     # heartbeat live
                "H": {"pid": 106, "start": NOW, "session_id": "sH", "exit_code": 0}}
    ages = {"sB": 900, "sC": 900, "sD": 900, "sE": 30, "sG": 900, "sH": 900}
    monkeypatch.setattr(lv, "launches", lambda log=None: launches)
    monkeypatch.setattr(lv, "transcript_age", lambda sid: ages.get(sid))
    monkeypatch.setattr(lv, "pid_alive", lambda pid: pid != 106)
    monkeypatch.setattr(bus, "alive", lambda r=None: {"G": {"tag": "t-g", "ts": "0"}})
    samples = {101: [{7001: 10.0}, {7001: 12.5}],                         # +2.5 CPU-s between samples
               102: [{7002: 3.0}, {7002: 3.0}],
               103: [{}, {}], 104: [{}, {}], 105: [{}, {}]}
    calls = {}

    def snap(pid):
        i = calls.get(pid, 0)
        calls[pid] = i + 1
        return samples[pid][min(i, 1)]
    return snap, calls


def test_busy_stale_ok_dead(world):
    snap, calls = world
    slept = []
    t = lv.status(stale_s=600, r=FakeR(workers={"D"}), snap=snap, sleep=slept.append, sample_s=0.7)
    assert t["B"]["state"] == "BUSY_COMPUTE" and t["B"]["tree_cpu_gained_s"] == 2.5
    assert t["C"]["state"] == "STALE" and t["C"]["tree_cpu_gained_s"] == 0.0
    assert t["D"]["state"] == "BUSY_COMPUTE" and t["D"]["worker_live"] is True
    assert t["E"]["state"] == "ACTIVE" and t["G"]["state"] == "IDLE" and t["H"]["state"] == "DEAD"
    assert slept == [0.7]                                                   # one sample window for all
    assert set(calls) == {101, 102, 103}                                    # only quiet lanes sampled


def test_a_child_that_exits_between_samples_is_not_activity(world, monkeypatch):
    snap, _ = world
    t = lv.status(stale_s=600, r=FakeR(), snap=lambda pid: {} if pid != 101 else {}, sleep=lambda s: None)
    assert t["B"]["state"] == "STALE"


def test_busy_does_not_post_missing(monkeypatch):
    posted = []
    monkeypatch.setattr(bus, "post", lambda *a, **k: posted.append(a))

    class R:
        def __init__(self):
            self.kv = {"pm:liveness:B": "ACTIVE", "pm:liveness:C": "ACTIVE"}

        def hgetall(self, k):
            return {"state": "busy", "job_id": "j1"} if k == "pm:worker:C" else {}

        def xpending(self, *a):
            return {"pending": 0}

        def get(self, k):
            return self.kv.get(k)

        def set(self, k, v):
            self.kv[k] = v
    lv.post_changes({"B": {"state": "BUSY_COMPUTE"}, "C": {"state": "STALE"}}, R())
    assert [a[1] for a in posted] == ["C STALE"]
