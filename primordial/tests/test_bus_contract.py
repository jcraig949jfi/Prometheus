"""Bus + contract controls. The live tests use a private key prefix-free
throwaway DB (db 15) and skip when the substrate is not reachable."""
from __future__ import annotations

import os

import pytest

from primordial.core import contract as C

GOOD = dict(lane="A", exp_id="t-1", claim="xadd beats sqlite", status="PASS",
            engineering={"events_per_s": 1.0}, science={"kills": 0},
            controls={"cheat": "injected fake 1e9 ev/s rejected", "positive": "ok"},
            rows="primordial/ledger/rows/t-1.jsonl", git={"sha": "x"})


def test_valid_receipt_is_board_eligible():
    assert C.board_eligible(C.validate_receipt(dict(GOOD)))


def test_cheat_control_missing_blocks_board():
    # CHEAT control for the scoreboard itself: a PASS with no cheat control run
    # validates as a record but must never score.
    rec = dict(GOOD, controls={"cheat": "", "positive": "ok"})
    C.validate_receipt(rec)
    assert not C.board_eligible(rec)


def test_ledgers_may_not_share_a_metric():
    with pytest.raises(C.ReceiptError):
        C.validate_receipt(dict(GOOD, science={"events_per_s": 5}))


def test_fail_never_scores():
    assert not C.board_eligible(dict(GOOD, status="FAIL"))


@pytest.fixture
def live(monkeypatch):
    redis = pytest.importorskip("redis")
    from primordial.tests._live import live_url
    url = live_url()                              # per-lane db: concurrent builder suites
    r = redis.Redis.from_url(url, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    r.flushdb()
    from primordial.bus import bus
    monkeypatch.setattr(bus, "URL", url)
    monkeypatch.setenv("PM_RECEIPT_GUARD", "0")   # fake git sha in GOOD; the guard has its own tests
    monkeypatch.setenv("PM_BOARD_SCORING", "1")   # these tests pin the round 1 scoring rules
    monkeypatch.setattr(bus, "LEDGER_DIR", __import__("pathlib").Path(os.environ.get("TMP", "/tmp")) / "pm_ledger_test")
    yield bus, r
    r.flushdb()


def test_claim_race_one_winner(live, monkeypatch):
    bus, r = live
    monkeypatch.setenv("PM_LANE", "B")
    assert bus.claim("exp-x", r=r)
    monkeypatch.setenv("PM_LANE", "C")
    assert not bus.claim("exp-x", r=r)
    assert r.hget(bus.CLAIMS, "exp-x").startswith("B[")


def test_each_lane_sees_each_message_once(live, monkeypatch):
    bus, r = live
    monkeypatch.setenv("PM_LANE", "A")
    bus.read(r=r)                      # create group A at the start
    monkeypatch.setenv("PM_LANE", "D")
    bus.read(r=r)
    monkeypatch.setenv("PM_LANE", "A")
    bus.post("note", "hello swarm", r=r)
    got_a = bus.read(r=r)
    assert [f["subject"] for _, f in got_a] == ["hello swarm"]
    assert bus.read(r=r) == []         # acked: not delivered twice to A
    monkeypatch.setenv("PM_LANE", "D")
    assert [f["subject"] for _, f in bus.read(r=r)] == ["hello swarm"]


def test_ineligible_receipt_does_not_score(live, monkeypatch):
    bus, r = live
    monkeypatch.setenv("PM_LANE", "A")
    bus.receipt(dict(GOOD, exp_id="t-2", controls={"cheat": ""}), board={"events_per_s": 1e9}, r=r)
    assert bus.standings("events_per_s", r=r) == []
    bus.receipt(dict(GOOD, exp_id="t-3"), board={"events_per_s": 7}, r=r)
    assert bus.standings("events_per_s", r=r) == [("A:t-3", 7.0)]
