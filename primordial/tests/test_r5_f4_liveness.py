"""F-R5-4: liveness states ACTIVE / BUSY_COMPUTE / IDLE / DRAINING / STALE / DEAD from worker state +
heartbeat + transcript, and paging A only on STALE or DEAD of a lane holding a job. Every source faked."""
from __future__ import annotations

import datetime

import pytest

from primordial.bus import bus
from primordial.ops import liveness as lv

NOW = datetime.datetime.now().astimezone().isoformat()


class FakeR:
    """Redis stand-in: worker hashes, stop flags, epoch state, pending counts, liveness kv."""

    def __init__(self, workers=None, stops=(), phase=None, pending=None, kv=None):
        self.workers, self.stops, self.phase = dict(workers or {}), set(stops), phase
        self.pending, self.kv = dict(pending or {}), dict(kv or {})

    def exists(self, key):
        if key.startswith("pm:worker:"):
            return int(key[len("pm:worker:"):] in self.workers)
        if key.startswith("pm:jobs:") and key.endswith(":stop"):
            return int(key[len("pm:jobs:"):-len(":stop")] in self.stops)
        return 0

    def hgetall(self, key):
        return dict(self.workers.get(key[len("pm:worker:"):], {})) if key.startswith("pm:worker:") else {}

    def hget(self, key, field):
        return self.phase if (key, field) == ("pm:epoch:state", "phase") else None

    def xpending(self, stream, group):
        lane = stream[len("pm:jobs:"):]
        if group != f"worker-{lane}" or lane not in self.pending:
            raise Exception("NOGROUP")
        return {"pending": self.pending[lane]}

    def get(self, k):
        return self.kv.get(k)

    def set(self, k, v):
        self.kv[k] = v


@pytest.fixture
def six(monkeypatch):
    launches = {"A": {"pid": 1, "start": NOW, "session_id": "sA"},    # fresh transcript -> ACTIVE
                "B": {"pid": 2, "start": NOW, "session_id": "sB"},    # worker busy, quiet transcript -> BUSY_COMPUTE
                "C": {"pid": 3, "start": NOW, "session_id": "sC"},    # heartbeat live, transcript 900 s -> IDLE
                "D": {"pid": 4, "start": NOW, "session_id": "sD"},    # stop flag + worker stopped, quiet -> DRAINING
                "E": {"pid": 5, "start": NOW, "session_id": "sE"},    # quiet, nothing -> STALE
                "G": {"pid": 6, "start": NOW, "session_id": "sG", "exit_code": 1}}   # -> DEAD
    ages = {"sA": 30, "sB": 900, "sC": 900, "sD": 900, "sE": 900, "sG": 900}
    monkeypatch.setattr(lv, "launches", lambda log=None: launches)
    monkeypatch.setattr(lv, "transcript_age", lambda sid: ages.get(sid))
    monkeypatch.setattr(lv, "pid_alive", lambda pid: True)
    monkeypatch.setattr(bus, "alive", lambda r=None: {"C": {"tag": "t-c", "ts": "0"}})
    return FakeR(workers={"B": {"state": "busy", "job_id": "jb"}, "D": {"state": "stopped", "job_id": ""}},
                 stops={"D"})


def test_six_states(six):
    sampled = []

    def snap(pid):
        sampled.append(pid)
        return {}
    t = lv.status(stale_s=600, r=six, snap=snap, sleep=lambda s: None)
    got = {L: t[L]["state"] for L in ("A", "B", "C", "D", "E", "G")}
    assert got == {"A": "ACTIVE", "B": "BUSY_COMPUTE", "C": "IDLE", "D": "DRAINING", "E": "STALE", "G": "DEAD"}
    assert set(sampled) == {5}                                  # only the quiet, otherwise-STALE lane is sampled


def test_epoch_phase_draining_counts_and_busy_beats_draining(six):
    six.stops.clear()
    six.phase = "draining"
    t = lv.status(stale_s=600, r=six, snap=lambda pid: {}, sleep=lambda s: None)
    assert t["D"]["state"] == "DRAINING"
    assert t["B"]["state"] == "BUSY_COMPUTE"                    # a running job during the drain is compute, not drain
    assert t["E"]["state"] == "DRAINING"                        # no worker + draining round -> never paged as STALE


def test_holds_job_sources():
    r = FakeR(workers={"B": {"state": "busy", "job_id": "j"}, "C": {"state": "idle", "job_id": ""}},
              pending={"C": 0, "D": 2})
    assert lv.holds_job(r, "B") and lv.holds_job(r, "D")
    assert not lv.holds_job(r, "C") and not lv.holds_job(r, "E")   # E: no group -> False, no exception


def test_paging_only_stale_or_dead_holding_a_job(monkeypatch):
    posted = []
    monkeypatch.setattr(bus, "post", lambda kind, subject, *a, **k: posted.append((kind, subject, k.get("to"))))
    lanes = ("B", "C", "D", "E", "G", "H", "P")
    r = FakeR(workers={"B": {"state": "busy", "job_id": "jb"}, "E": {"state": "busy", "job_id": "je"},
                       "D": {"state": "stopped", "job_id": ""}},
              pending={"C": 1, "G": 0, "H": 0, "P": 0},
              kv={f"pm:liveness:{L}": "ACTIVE" for L in lanes})
    t = {"B": {"state": "STALE"},          # holds job (worker)       -> page
         "C": {"state": "DEAD"},           # holds job (pending)      -> page
         "D": {"state": "DRAINING"},       # never pages
         "E": {"state": "BUSY_COMPUTE"},   # never pages
         "G": {"state": "STALE"},          # no job                   -> silent
         "H": {"state": "DEAD"},           # no job                   -> silent
         "P": {"state": "IDLE"}}           # never pages
    paged = lv.post_changes(t, r)
    assert sorted(paged) == ["B", "C"]
    assert sorted(posted) == [("missing", "B STALE", "A"), ("missing", "C DEAD", "A")]
    assert all(r.kv[f"pm:liveness:{L}"] == t[L]["state"] for L in lanes)   # silent lanes still recorded
    posted.clear()
    assert lv.post_changes(t, r) == [] and posted == []                   # no change -> no second page
