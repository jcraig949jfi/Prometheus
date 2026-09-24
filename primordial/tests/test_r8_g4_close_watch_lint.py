"""G4 (BUILD_R8, D31): the close/watch protocol lint. D31: A's close note told lanes to stop their watchers; a lane
complied and its gpuq arbiter exited ~1 min after a ruling said to keep it -- 683 s deaf. The lint FAILS on any close
sequence that stops the ask watch before workers or shared services, and flags a shared-service stop without a
current conductor confirmation. Beacons are EMITTED by P (worker.py); this suite checks only the lint over them."""
from __future__ import annotations

import json
import uuid

import pytest

from primordial.ops import epoch as EP
from primordial.tests._live import live_url

GOOD = [{"action": "drain"},
        {"action": "stop", "target": "worker", "lane": "E"},
        {"action": "confirm", "target": "gpuq"},
        {"action": "stop", "target": "gpuq"},
        {"action": "stop", "target": "ask_watch", "lane": "E"}]

# The D31 shape, as a prose note: watchers stopped in the same breath as (and before) workers and the arbiter.
D31_NOTE = """ROUND 7 CLOSE SEQUENCE
1. Drain has begun; no new jobs.
2. Lanes: stop your ask watchers now.
3. Then stop workers.
4. Stop the gpuq arbiter when your last GPU job ends."""


def kinds(rep):
    return sorted(v["kind"] for v in rep["violations"])


def test_good_sequence_passes_and_counts_its_checks():
    rep = EP.protocol_lint(GOOD)
    assert rep["ok"] and rep["violations"] == [] and rep["checks_run"] == 4       # 1 shared + 3 ask-watch checks


def test_d31_note_fails_the_lint():
    steps = EP.parse_close_text(D31_NOTE)
    assert [s["action"] + ":" + s["target"] if s["action"] != "drain" else "drain" for s in steps] == \
        ["drain", "stop:ask_watch", "stop:worker", "stop:gpuq"]
    rep = EP.protocol_lint(steps)
    assert not rep["ok"] and rep["checks_run"] == 4
    assert kinds(rep) == ["ASK_WATCH_STOP_BEFORE_SHARED_SERVICE", "ASK_WATCH_STOP_BEFORE_WORKERS",
                          "SHARED_STOP_UNCONFIRMED"]


@pytest.mark.parametrize("seq,want", [
    ([{"action": "stop", "target": "ask_watch", "lane": "E"}, {"action": "drain"},
      {"action": "stop", "target": "worker", "lane": "E"}],
     ["ASK_WATCH_STOP_BEFORE_DRAIN", "ASK_WATCH_STOP_BEFORE_WORKERS"]),
    ([{"action": "drain"}, {"action": "stop", "target": "ask_watch", "lane": "E"}],
     ["ASK_WATCH_STOP_BEFORE_WORKERS"]),                                            # workers never stopped
    ([{"action": "drain"}, {"action": "stop", "target": "worker", "lane": "*"},
      {"action": "stop", "target": "ask_watch", "lane": "E"}, {"action": "confirm", "target": "gpuq"},
      {"action": "stop", "target": "gpuq"}],
     ["ASK_WATCH_STOP_BEFORE_SHARED_SERVICE"]),
    ([{"action": "drain"}, {"action": "stop", "target": "worker", "lane": "E"}, {"action": "stop", "target": "gpuq"},
      {"action": "stop", "target": "ask_watch", "lane": "E"}],
     ["SHARED_STOP_UNCONFIRMED"]),
    ([{"action": "drain"}, {"action": "stop", "target": "worker", "lane": "B"},
      {"action": "stop", "target": "ask_watch", "lane": "E"}, {"action": "stop", "target": "worker", "lane": "E"}],
     ["ASK_WATCH_STOP_BEFORE_WORKERS"]),                                            # another lane's worker is not E's
])
def test_each_violation_is_caught(seq, want):
    rep = EP.protocol_lint(seq)
    assert not rep["ok"] and kinds(rep) == sorted(want)


def test_controller_close_sequence_is_lint_clean():
    assert EP.protocol_lint(EP.CONTROLLER_CLOSE_SEQUENCE)["ok"]


def beacon(event, lane, kind, ts, pid=1, shared=0):
    return {"event": event, "lane": lane, "kind": kind, "ts": str(ts), "pid": str(pid), "shared": str(shared),
            "tag": "t", "round_id": "r8", "reason": "close"}


def test_beacons_d31_deaf_window_is_measured():
    """The r7 shape in beacons: ask watch stopped, the arbiter kept running 683 s, unconfirmed."""
    b = [beacon("WATCH_START", "E", "ask_watch", 0, pid=10), beacon("WATCH_START", "E", "worker", 1, pid=11),
         beacon("WATCH_STOP", "E", "worker", 100, pid=11), beacon("WATCH_STOP", "E", "ask_watch", 200, pid=10),
         beacon("WATCH_STOP", "E", "gpuq", 883, pid=12, shared=1)]
    rep = EP.beacon_lint(b)
    assert not rep["ok"] and kinds(rep) == ["ASK_WATCH_STOP_BEFORE_SHARED_SERVICE", "SHARED_STOP_UNCONFIRMED"]
    deaf = [v for v in rep["violations"] if v["kind"] == "ASK_WATCH_STOP_BEFORE_SHARED_SERVICE"][0]
    assert deaf["deaf_s"] == 683.0 and rep["checks_run"] == 3


def test_beacons_clean_close_passes_with_current_confirmation():
    b = [beacon("WATCH_START", "E", "worker", 1, pid=11), beacon("WATCH_STOP", "E", "worker", 100, pid=11),
         beacon("WATCH_STOP", "E", "gpuq", 150, pid=12, shared=1), beacon("WATCH_STOP", "E", "ask_watch", 200, pid=10)]
    assert EP.beacon_lint(b, {"gpuq": {"ts": "120", "by": "A", "ref": "1789-0"}})["ok"]
    stale = EP.beacon_lint(b, {"gpuq": {"ts": str(150 - EP.CONFIRM_MAX_AGE_S - 1), "by": "A"}})
    late = EP.beacon_lint(b, {"gpuq": {"ts": "151", "by": "A"}})                     # written AFTER the stop
    assert kinds(stale) == kinds(late) == ["SHARED_STOP_UNCONFIRMED"]


def test_beacons_worker_still_running_when_watch_stops():
    b = [beacon("WATCH_START", "C", "worker", 1, pid=21), beacon("WATCH_STOP", "C", "ask_watch", 50, pid=20)]
    rep = EP.beacon_lint(b)
    assert kinds(rep) == ["ASK_WATCH_STOP_BEFORE_WORKERS"] and rep["violations"][0]["unstopped_worker_pids"] == ["21"]


def test_lint_cli_rc_and_checks_run(tmp_path, capsys):
    good, bad, empty = tmp_path / "good.json", tmp_path / "d31.txt", tmp_path / "empty.txt"
    good.write_text(json.dumps(GOOD), encoding="utf-8")
    bad.write_text(D31_NOTE, encoding="utf-8")
    empty.write_text("nothing to see\n", encoding="utf-8")
    assert EP.main(["lint", "--sequence", str(good)]) == 0
    out = capsys.readouterr().out
    assert "checks run: 4" in out and "PROTOCOL LINT PASS" in out
    assert EP.main(["lint", "--sequence", str(bad)]) == 1
    assert "PROTOCOL LINT FAIL" in capsys.readouterr().out
    assert EP.main(["lint"]) == 1                                                     # no lint ran: never PASS
    assert "checks run: 0" in capsys.readouterr().out


def test_close_sweep_reads_live_beacons_and_confirmations(monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    key, svc = f"pm:telemetry:watch:t-{uuid.uuid4().hex[:6]}", f"svc{uuid.uuid4().hex[:6]}"
    monkeypatch.setattr(EP, "BEACONS", key)
    try:
        r.xadd(key, beacon("WATCH_STOP", "E", svc, 100, shared=1))
        assert kinds(EP.close_sweep(r, shared=(svc,))) == ["SHARED_STOP_UNCONFIRMED"]
        r.hset(EP.CONFIRM.format(svc), mapping={"ts": "90", "by": "A", "ref": "x"})
        assert EP.close_sweep(r, shared=(svc,))["ok"]
    finally:
        r.delete(key, EP.CONFIRM.format(svc))


def test_p_agreed_beacon_record_is_linted():
    """P 1789564787642-0: pm:telemetry:watch, field json = WATCH_BEACON {beacon START|BEAT|STOP, watcher, ...}."""
    assert EP.BEACONS == "pm:telemetry:watch"
    raw = [{"json": json.dumps(b)} for b in EP.PLANTED_D31_BEACONS]
    raw.insert(1, {"json": json.dumps({"record": "WATCH_BEACON", "beacon": "BEAT", "lane": "E", "watcher": "worker",
                                       "pid": 11, "ts": 50.0})})
    rows = EP.normalize_beacons(raw)
    assert len(rows) == 4 and {r["event"] for r in rows} == {"WATCH_START", "WATCH_STOP"}      # BEAT dropped
    rep = EP.beacon_lint(raw)
    assert kinds(rep) == ["ASK_WATCH_STOP_BEFORE_SHARED_SERVICE", "SHARED_STOP_UNCONFIRMED"]


def test_self_test_gate_argv(capsys):
    """The gate argv A wires: `python -m primordial.ops.epoch lint --self-test` -> rc 0, checks run: 4."""
    res = EP.self_test()
    assert [n for n, ok, _ in res if not ok] == [] and len(res) == 4
    assert EP.main(["lint", "--self-test"]) == 0
    out = capsys.readouterr().out
    assert "checks run: 4" in out and "PROTOCOL LINT PASS" in out


def test_self_test_fails_if_the_lint_goes_blind(monkeypatch):
    monkeypatch.setattr(EP, "protocol_lint", lambda seq, shared=EP.SHARED_SERVICES: {"ok": True, "checks_run": 0,
                                                                                    "violations": []})
    assert EP.main(["lint", "--self-test"]) == 1
