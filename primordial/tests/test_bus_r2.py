"""Round 2 bus gate (F2 heartbeat, F3 addressing/tail/tag guard, F5 receipt guard,
ANOMALY queue). Live tests use throwaway db 15 on 6390 and skip without it."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess

import pytest

from primordial.bus import bus

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture
def live(monkeypatch, tmp_path):
    redis = pytest.importorskip("redis")
    url = "redis://127.0.0.1:6390/15"
    r = redis.Redis.from_url(url, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    r.flushdb()
    monkeypatch.setattr(bus, "URL", url)
    monkeypatch.setattr(bus, "LEDGER_DIR", tmp_path / "ledger")
    monkeypatch.setenv("PM_RECEIPT_GUARD", "0")
    monkeypatch.delenv("PM_TAKEOVER", raising=False)
    yield r
    r.flushdb()


def test_every_call_refreshes_heartbeat_with_ttl(live, monkeypatch):
    monkeypatch.setenv("PM_LANE", "B")
    monkeypatch.setenv("PM_TAG", "m1-bbbb")
    bus.post("note", "x", r=live)
    h = live.hgetall("pm:alive:B")
    assert h["tag"] == "m1-bbbb" and h["status"] == "note"
    assert 0 < live.ttl("pm:alive:B") <= bus.ALIVE_TTL


def test_addressed_messages_and_tail_is_read_only(live, monkeypatch):
    monkeypatch.setenv("PM_LANE", "A")
    bus.read(r=live)
    monkeypatch.setenv("PM_LANE", "B")
    bus.post("note", "to A only", "x" * 1000, to="A", r=live)
    bus.post("note", "to everyone", to="ALL", r=live)
    bus.post("note", "unaddressed", r=live)
    before = live.xinfo_groups(bus.SWARM)
    tailed = bus.tail(10, r=live)
    assert [f["subject"] for _, f in tailed] == ["to A only", "to everyone", "unaddressed"]
    assert live.xinfo_groups(bus.SWARM) == before                     # tail consumed nothing
    monkeypatch.setenv("PM_LANE", "A")
    got = bus.read(r=live)
    assert [bus.addressed_to(f, "A") for _, f in got] == [True, True, False]
    assert len(got[0][1]["body"]) == 1000                              # full body kept on the bus


def test_unregistered_tag_cannot_consume_a_lane_group(live, monkeypatch):
    monkeypatch.setenv("PM_LANE", "C")
    monkeypatch.setenv("PM_TAG", "m1-real")
    bus.register(r=live)
    bus.post("note", "from the real holder", r=live)
    monkeypatch.setenv("PM_TAG", "m1-observer")
    with pytest.raises(SystemExit):
        bus.read(r=live)
    assert [f["subject"] for _, f in bus.tail(5, r=live)] == ["from the real holder"]  # observers use tail


def test_register_refuses_live_holder_allows_takeover(live, monkeypatch):
    monkeypatch.setenv("PM_LANE", "D")
    monkeypatch.setenv("PM_TAG", "m1-first")
    bus.register(r=live)
    monkeypatch.setenv("PM_TAG", "m1-second")
    with pytest.raises(SystemExit):
        bus.register(r=live)
    monkeypatch.setenv("PM_TAKEOVER", "1")
    bus.register(r=live)
    assert live.hget(bus.TAGS, "D") == "m1-second"


def test_anomaly_queue_add_list_resolve_seed(live, monkeypatch, tmp_path):
    monkeypatch.setenv("PM_LANE", "A")
    aid = bus.anomaly_add("load speeds up numba", "x1.26 under burn8", expected="slower", r=live)
    assert [(i, s) for i, _, s in bus.anomaly_list(r=live)] == [(aid, "OPEN")]
    bus.anomaly_resolve(aid, "RESOLVED", "thread scheduling", exp_id="D2-x", r=live)
    assert bus.anomaly_list("OPEN", r=live) == []
    with pytest.raises(ValueError):
        bus.anomaly_resolve(aid, "DONE", "bad status", r=live)
    seed = tmp_path / "seed.jsonl"
    seed.write_text(json.dumps({"subject": "load speeds up numba", "observation": "dup"}) + "\n"
                    + json.dumps({"subject": "new one", "observation": "o"}) + "\n", encoding="utf-8")
    added = bus.anomaly_seed(seed, r=live)
    assert len(added) == 1 and len(bus.anomaly_list(r=live)) == 2


def test_receipt_records_host_load_when_guard_off(live, monkeypatch):
    monkeypatch.setenv("PM_LANE", "E")
    rec = dict(lane="E", exp_id="t-host", claim="c", status="PASS", engineering={}, science={"s": 1},
               controls={"cheat": "ran"}, rows="primordial/ledger/rows/E/x.jsonl", git="abc1234")
    bus.receipt(rec, r=live)
    got = json.loads(live.xrange(bus.RESULTS)[-1][1]["json"])
    assert "cpu_pct" in got["engineering"]["host_load"]


def _git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def test_guard_git_accepts_committed_rows_and_rejects_the_rest():
    head = _git("rev-parse", "HEAD")
    parent = _git("rev-parse", "HEAD~1")
    ok = {"git": head, "rows": "primordial/bus/bus.py"}
    assert bus.guard_git(ok, fetch=False, ref="HEAD") == []
    assert bus.guard_git({"git": "x", "rows": "primordial/bus/bus.py"}, fetch=False, ref="HEAD")
    assert any("absent" in p for p in bus.guard_git({"git": head, "rows": "primordial/nope/none.jsonl"},
                                                     fetch=False, ref="HEAD"))
    assert any("not on" in p for p in bus.guard_git({"git": head, "rows": "primordial/bus/bus.py"},
                                                     fetch=False, ref=parent))
    assert bus.guard_git({"git": {"sha": head}, "rows": "rows at primordial/bus/bus.py (+ notes)"},
                         fetch=False, ref="HEAD") == []

def test_round2_receipts_do_not_self_score(live, monkeypatch):
    monkeypatch.setenv("PM_LANE", "B")
    monkeypatch.delenv("PM_BOARD_SCORING", raising=False)
    rec = dict(lane="B", exp_id="t-kill", claim="c", status="KILL", engineering={}, science={"s": 1},
               controls={"cheat": "ran"}, rows="primordial/ledger/rows/B/x.jsonl", git="abc1234")
    bus.receipt(rec, board={"steps_per_s_verified": 1e9}, r=live)
    assert live.zrange("pm:board:kills", 0, -1) == [] and live.zrange("pm:board:steps_per_s_verified", 0, -1) == []
