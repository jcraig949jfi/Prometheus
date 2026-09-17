"""viv/deadman.py -- the out-of-process reader of the consumer's heartbeat
(backlog C11b). Every external observation is a hook, so each control is a
verdict about the LOGIC; the two live probes (a real dead consumer row, the
M2 twin refused as WRONG_ENGINE) are in roles/Vivarium/journal/2026-09-16.md.

    POSITIVE  a dead consumer with a live upstream is relaunched and the
              tick is productive once a heartbeat appears
    NEGATIVE  a stale heartbeat whose pid is alive is BUSY, never relaunched
              (the C2 false-dead); a parked or stopping consumer is never
              relaunched; an unreachable or WRONG engine blocks the launch
              (rule 9)
    CHEAT     a launch that is ISSUED but never produces a heartbeat is a
              FAILED tick (emission is not productivity); the bound parks
              the dead-man, disables its task, posts exactly once, and a
              parked dead-man refuses to run again
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from viv import deadman as _dm


def _hb(age_s, pid=4242, host="THISHOST", current=None):
    return {"worker_id": "vivarium@test", "host": host, "pid": pid,
            "age_s": age_s, "current_experiment": current, "build": {}}


class Harness:
    """A scripted world: heartbeats in the order the dead-man reads them."""

    def __init__(self, tmp_path, *, heartbeats, pid_alive=False,
                 upstream_ok=True, launch_ok=True, bound=3):
        self.hbs = list(heartbeats)
        self.launches = 0
        self.disabled = []
        self.posts = []
        self.sleeps = []
        hooks = _dm.Hooks(
            heartbeat=self._next_hb,
            pid_alive=lambda pid, host: pid_alive,
            upstream=lambda: ({"ok": True, "reason": "ANSWERED", "observed": "eng_x"}
                              if upstream_ok else
                              {"ok": False, "reason": "UNREACHABLE", "url": "u"}),
            launch=self._launch,
            disable=lambda name: (self.disabled.append(name) or True),
            post=lambda rec, body: (self.posts.append((rec, body)) or {"posted": True}),
            sleep=lambda s: self.sleeps.append(s),
            stranded_rows=lambda w: [],                  # no queue in the scripted world
            release=lambda eid, reason: {"experiment_id": eid, "released": True})
        self.launch_ok = launch_ok
        cfg = _dm.Config(worker_id="vivarium@test", task_name="VivariumDeadmanTest",
                         launcher="C:/nowhere/launcher.cmd", fresh_s=100.0,
                         settle_s=1.0, bound=bound, var_dir=tmp_path,
                         expected_engine_instance_id="eng_x")
        self.dm = _dm.Deadman(cfg, hooks, log=lambda s: None)

    def _next_hb(self):
        if not self.hbs:
            raise RuntimeError("scripted world ran out of heartbeats")
        hb = self.hbs.pop(0)
        if isinstance(hb, Exception):
            raise hb
        return hb

    def _launch(self):
        self.launches += 1
        return self.launch_ok

    def state(self):
        return json.loads(self.dm.state_path.read_text(encoding="utf-8"))


# ------------------------------------------------------------- positive

def test_positive_live_consumer_is_productive_and_writes_state(tmp_path):
    h = Harness(tmp_path, heartbeats=[_hb(5.0)])
    r = h.dm.tick()
    assert r["exit"] == 0 and r["verdict"] == "LIVE"
    st = h.state()
    assert st["consecutive_failures"] == 0 and st["last_success_at"]
    assert st["parked"] is False and h.launches == 0


def test_positive_dead_consumer_with_live_upstream_is_relaunched(tmp_path):
    h = Harness(tmp_path, heartbeats=[_hb(5000.0), _hb(1.0, pid=5151)])
    r = h.dm.tick()
    assert r["exit"] == 0 and r["relaunched"] is True and r["verdict"] == "LIVE"
    assert h.launches == 1 and h.sleeps == [1.0]
    assert h.state()["consecutive_failures"] == 0


def test_positive_never_heartbeated_worker_is_launched_too(tmp_path):
    h = Harness(tmp_path, heartbeats=[None, _hb(1.0)])
    r = h.dm.tick()
    assert r["exit"] == 0 and r["relaunched"] is True and h.launches == 1


# ------------------------------------------------------------- negative

def test_negative_stale_heartbeat_with_live_pid_is_busy_not_dead(tmp_path):
    """The C2 shape: no heartbeat during a 600 s row. A relaunch here would
    be a second consumer."""
    h = Harness(tmp_path, heartbeats=[_hb(700.0, current="exp-1")], pid_alive=True)
    r = h.dm.tick()
    assert r["exit"] == 0 and r["verdict"] == "BUSY" and h.launches == 0


def test_negative_parked_consumer_is_never_relaunched(tmp_path):
    from viv import daemon as _daemon
    _daemon.park_file_for(tmp_path, "vivarium@test").write_text(
        json.dumps({"kind": "RULE10_BOUND"}), encoding="utf-8")
    h = Harness(tmp_path, heartbeats=[_hb(9999.0)])
    r = h.dm.tick()
    assert r["exit"] == 0 and r["verdict"] == "PARKED" and h.launches == 0


def test_negative_stopping_consumer_is_never_relaunched(tmp_path):
    from viv import daemon as _daemon
    _daemon.stop_file_for(tmp_path, "vivarium@test").write_text("stop", encoding="utf-8")
    h = Harness(tmp_path, heartbeats=[_hb(9999.0)])
    r = h.dm.tick()
    assert r["verdict"] == "STOPPING" and h.launches == 0


def test_negative_dead_upstream_blocks_the_launch_and_parks_to_daedalus(tmp_path):
    """Rule 9: nothing is launched into a dead upstream; the park names the
    seat that owns the upstream, not the queue's producer."""
    h = Harness(tmp_path, heartbeats=[_hb(9999.0)] * 3, upstream_ok=False)
    r1 = h.dm.tick(); r2 = h.dm.tick(); r3 = h.dm.tick()
    assert (r1["exit"], r2["exit"], r3["exit"]) == (1, 1, 3)
    assert h.launches == 0
    assert r3["park"]["accountable_seat"] == "Daedalus"
    assert r3["park"]["upstream"]["reason"] == "UNREACHABLE"
    assert h.state()["parked"] is True


def test_negative_store_unreadable_is_a_failed_tick_not_a_death(tmp_path):
    h = Harness(tmp_path, heartbeats=[RuntimeError("REFUSED: wrong store")])
    r = h.dm.tick()
    assert r["exit"] == 1 and r["verdict"] == "STORE_UNREADABLE"
    assert h.launches == 0 and h.state()["consecutive_failures"] == 1


# ---------------------------------------------------------------- cheat

def test_cheat_an_issued_launch_with_no_heartbeat_is_not_productive(tmp_path):
    """The launcher 'succeeds' every time and nothing ever heartbeats."""
    h = Harness(tmp_path, heartbeats=[_hb(9999.0), None] * 3, launch_ok=True)
    r1 = h.dm.tick(); r2 = h.dm.tick(); r3 = h.dm.tick()
    assert h.launches == 3
    assert (r1["exit"], r2["exit"], r3["exit"]) == (1, 1, 3)
    assert r3["verdict"] == "PARKED_DEADMAN"
    assert r3["park"]["consecutive_non_productive_ticks"] == 3
    assert r3["park"]["accountable_seat"] == "Archaeon"
    assert h.disabled == ["VivariumDeadmanTest"]
    assert len(h.posts) == 1
    assert h.dm.park_path.exists()
    assert Path(str(h.dm.park_path).replace(".park.json", ".park.report.md")).exists()


def test_cheat_a_parked_deadman_refuses_to_run_and_posts_nothing_more(tmp_path):
    h = Harness(tmp_path, heartbeats=[_hb(9999.0), None] * 3)
    for _ in range(3):
        h.dm.tick()
    assert len(h.posts) == 1
    r = h.dm.tick()                              # scripted world untouched
    assert r["exit"] == 3 and r["verdict"] == "DEADMAN_PARKED"
    assert len(h.posts) == 1 and h.launches == 3


def test_cheat_a_recovery_resets_the_count(tmp_path):
    h = Harness(tmp_path, heartbeats=[_hb(9999.0), None, _hb(2.0), _hb(9999.0), None])
    assert h.dm.tick()["exit"] == 1                 # 1 of 3
    assert h.dm.tick()["exit"] == 0                 # alive: reset
    assert h.dm.tick()["exit"] == 1                 # 1 of 3 again, not 2
    assert h.state()["consecutive_failures"] == 1


def test_probe_upstream_refuses_the_wrong_engine(monkeypatch):
    """The precondition is IDENTITY, not a port: a twin that answers with
    another ledger's id is WRONG_ENGINE."""
    import io
    import urllib.request

    class R(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: R(json.dumps({"engine_instance_id": "eng_twin",
                                                      "schema_version": 8}).encode()))
    v = _dm.probe_upstream("https://x/v2/version", None, "eng_prod")
    assert v == {"ok": False, "reason": "WRONG_ENGINE", "expected": "eng_prod",
                 "observed": "eng_twin", "url": "https://x/v2/version"}
    ok = _dm.probe_upstream("https://x/v2/version", None, "eng_twin")
    assert ok["ok"] and ok["reason"] == "ANSWERED"


def test_pid_alive_here_only_trusts_this_host(monkeypatch):
    monkeypatch.setenv("COMPUTERNAME", "THISHOST")
    assert _dm.pid_alive_here(1, "OTHERHOST") is False
    assert _dm.pid_alive_here(0, "THISHOST") is False


# ------------------------------------------------------------- s14 canary finding (2026-09-17)

def test_young_heartbeat_with_gone_pid_on_this_host_is_dead_now(tmp_path, monkeypatch):
    """The canary killed the consumer mid-row; the dead-man read LIVE for 15
    minutes because it never looked at the pid while the heartbeat was young.
    POSITIVE: 80 s old (grace 60, fresh 100), same host, pid gone -> DEAD and relaunched.
    NEGATIVE: 80 s old, pid ALIVE -> LIVE (no relaunch); 10 s old, pid gone
    -> LIVE (inside the launch grace). CHEAT: a heartbeat from ANOTHER host
    with an unknown pid stays LIVE -- this host cannot judge it."""
    monkeypatch.setenv("COMPUTERNAME", "THISHOST")
    h = Harness(tmp_path, heartbeats=[_hb(80.0), _hb(1.0, pid=5151)], pid_alive=False)   # fresh_s is 100 in the harness
    r = h.dm.tick()
    assert r["relaunched"] is True and h.launches == 1
    h = Harness(tmp_path, heartbeats=[_hb(80.0)], pid_alive=True)
    assert h.dm.tick()["verdict"] == "LIVE" and h.launches == 0
    h = Harness(tmp_path, heartbeats=[_hb(10.0)], pid_alive=False)
    assert h.dm.tick()["verdict"] == "LIVE" and h.launches == 0
    h = Harness(tmp_path, heartbeats=[_hb(80.0, host="OTHERHOST")], pid_alive=False)
    assert h.dm.tick()["verdict"] == "LIVE" and h.launches == 0


# ------------------------------------------------------------- Campaign 4: bounded auto-recovery (operator PROMPT 3)

def _park_consumer(tmp_path, *, failure_class="ENGINE_TRANSPORT", eid="e-1"):
    from viv import daemon as _daemon
    p = _daemon.park_file_for(tmp_path, "vivarium@test")
    p.write_text(json.dumps({"kind": "FAILURE_CLASS_HALT", "worker_id": "vivarium@test",
                             "last_tick": {"failure_class": failure_class, "experiment_id": eid},
                             "parked_at": "2026-09-17T15:51:28Z"}), encoding="utf-8")
    return p


def _auto_harness(tmp_path, heartbeats, *, upstream_ok=True, released=None, stranded=None, bound=3, pid_alive=False):
    h = Harness(tmp_path, heartbeats=heartbeats, upstream_ok=upstream_ok, pid_alive=pid_alive)
    h.releases = []
    h.dm.h.release = lambda eid, reason: (h.releases.append((eid, reason)) or (released or {"experiment_id": eid, "released": True}))
    h.dm.h.stranded_rows = lambda w: list(stranded or [])
    h.dm.cfg.auto_recover_bound = bound
    return h


def test_positive_a_transport_park_is_auto_cleared_released_and_relaunched_when_the_engine_answers(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPUTERNAME", "THISHOST")
    park = _park_consumer(tmp_path)
    # the parked consumer exited: its heartbeat is young but its pid is gone
    h = _auto_harness(tmp_path, [_hb(80.0), _hb(1.0, pid=5151)])
    r = h.dm.tick()
    assert not park.exists(), "the park record must be cleared (renamed)"
    cleared = list(tmp_path.glob("park-vivarium@test.cleared-*.json"))
    assert len(cleared) == 1 and "auto-recovery 1 of 3" in json.loads(cleared[0].read_text())["cleared"]["reason"]
    assert h.releases and h.releases[0][0] == "e-1"                 # the halted row -> NEW ATTEMPT
    assert r.get("relaunched") is True and h.launches == 1
    st = h.state()
    assert len(st["auto_recoveries"]) == 1 and st["parked"] is False


def test_negative_the_bound_the_engine_and_the_park_kind_all_keep_it_parked(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPUTERNAME", "THISHOST")
    # (a) bound reached: three recoveries already in the window
    park = _park_consumer(tmp_path)
    h = _auto_harness(tmp_path, [_hb(80.0)])
    h.dm._write_state(auto_recoveries=["2026-09-17T10:00:00Z", "2026-09-17T11:00:00Z", "2026-09-17T12:00:00Z"][0:0]
                      + [__import__("viv.deadman", fromlist=["_utc"])._utc()] * 3)
    r = h.dm.tick()
    assert r["verdict"] == "PARKED" and park.exists() and h.launches == 0 and not h.releases
    # (b) engine not answering
    h = _auto_harness(tmp_path, [_hb(80.0)], upstream_ok=False)
    assert h.dm.tick()["verdict"] == "PARKED" and park.exists() and not h.releases
    # (c) a non-transport halt (EXECUTOR_ERROR would never park, but a rule-10 bound park has no failure_class)
    park.unlink(); _park_consumer(tmp_path, failure_class="INSTRUMENT_INVALID")
    h = _auto_harness(tmp_path, [_hb(80.0)])
    assert h.dm.tick()["verdict"] == "PARKED" and not h.releases and h.launches == 0


def test_a_dead_workers_stranded_rows_are_released_before_the_relaunch(tmp_path, monkeypatch):
    """CHEAT control: a release the queue REFUSES is recorded, never retried
    in a loop, and does not stop the relaunch."""
    monkeypatch.setenv("COMPUTERNAME", "THISHOST")
    h = _auto_harness(tmp_path, [_hb(5000.0), _hb(1.0, pid=5151)], stranded=["e-a", "e-b"],
                      released={"released": False, "error": "cannot release: status is completed"})
    r = h.dm.tick()
    assert [e for e, _ in h.releases] == ["e-a", "e-b"]
    assert r.get("relaunched") is True and h.launches == 1
    assert all(x["released"] is False for x in r["released_before_relaunch"])
