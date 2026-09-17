"""D28 (r8 conditional C3): a registration survives a job that outlives REG_TTL.

r7: `refresh()` was `EXPIRE key REG_TTL`, and EXPIRE on a missing key is a no-op, so once C-R7-01's 217.6 s GPU job
outlived the 90 s TTL the arbiter stayed unregistered for ~23 min while refreshing every turn. The claim tested here
is behavioural: after the key is GONE, refresh brings it back -- but only for a live process that registered it.
"""
from __future__ import annotations

import os
import time

import pytest

from primordial.ops import residue as RS
from primordial.tests._live import live_url

REPO = "F:/Prometheus-worktrees/nestor-r8-e"


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = []
    yield c, keys
    for k in keys:
        RS.unregister(c, k)


def test_refresh_recreates_an_expired_registration_of_a_live_process(r):
    c, keys = r
    key = RS.register(c, "gpu", REPO, round_id="t-d28", tag="t-d28")
    keys.append(key)
    before = c.hgetall(key)
    c.delete(key)                                                   # REG_TTL elapsed while blocked in a job
    assert not c.exists(key)
    assert RS.refresh(c, key) is True
    after = c.hgetall(key)
    assert after and 0 < c.ttl(key) <= RS.REG_TTL
    for f in ("pid", "lane", "repo", "round_id", "cmdline", "tag", "started_ts"):
        assert after[f] == before[f], f
    assert after["pid"] == str(os.getpid()) and after["reregistered_n"] == "1"   # disclosed, not silent
    c.delete(key)
    RS.refresh(c, key)
    assert c.hget(key, "reregistered_n") == "2"


def test_refresh_really_expired_key_not_just_deleted(r):
    c, keys = r
    key = RS.register(c, "gpu", REPO, round_id="t-d28", tag="t-d28")
    keys.append(key)
    c.pexpire(key, 50)
    time.sleep(0.2)
    assert not c.exists(key)
    assert RS.refresh(c, key) and c.hget(key, "lane") == "gpu"


def test_refresh_never_resurrects_a_dead_pid_an_unregistered_key_or_a_foreign_key(r, monkeypatch):
    c, keys = r
    dead = RS.register(c, "gpu", REPO, round_id="t-d28", pid=999999, tag="t-d28-dead")
    keys.append(dead)
    monkeypatch.setattr(RS, "_live", lambda pid: (False, None))
    c.delete(dead)
    assert RS.refresh(c, dead) is False and not c.exists(dead)
    monkeypatch.undo()

    gone = RS.register(c, "gpu", REPO, round_id="t-d28", tag="t-d28-gone")
    RS.unregister(c, gone)
    assert RS.refresh(c, gone) is False and not c.exists(gone)

    foreign = "pm:worker:reg:gpu:424242"                            # registered by some other process
    assert RS.refresh(c, foreign) is False and not c.exists(foreign)


def test_keepalive_holds_a_registration_through_a_block_longer_than_the_ttl(r, monkeypatch):
    c, keys = r
    monkeypatch.setattr(RS, "REG_TTL", 1)                           # a 1 s TTL; the "job" blocks 3 s
    key = RS.register(c, "gpu", REPO, round_id="t-d28", tag="t-d28-ka")
    keys.append(key)
    stop = RS.keepalive(c, key, interval_s=0.2)
    try:
        t0, seen = time.monotonic(), []
        while time.monotonic() - t0 < 3.0:                          # the blocking job
            seen.append(bool(c.exists(key)))
            time.sleep(0.25)
        assert all(seen) and len(seen) >= 10
    finally:
        stop.set()
    RS.unregister(c, key)
    time.sleep(0.5)
    assert not c.exists(key)                                        # the keepalive cannot re-create after unregister


def test_without_keepalive_the_same_block_loses_the_key_so_the_test_above_is_not_vacuous(r, monkeypatch):
    c, keys = r
    monkeypatch.setattr(RS, "REG_TTL", 1)
    key = RS.register(c, "gpu", REPO, round_id="t-d28", tag="t-d28-nk")
    keys.append(key)
    time.sleep(1.5)
    assert not c.exists(key)
