"""Gate item 16 (round 6): the clock is pm:round:r6 with the SWARM_R6 s0 shape; r5 keeps its frozen row."""
from __future__ import annotations

import pytest

from primordial.ops import round_clock as RC
from primordial.tests._live import live_url


def test_r6_row_and_defaults():
    c = RC.plan(0.0, "r6")
    assert c["round_id"] == "r6" and c["stage"] == "PRODUCTION"
    assert (c["epoch_s"], c["epochs"], c["no_new_work_ts"], c["drain_ts"], c["end_ts"]) == (2400.0, 5, 12000, 13200, 14400)
    assert [RC.phase(c, t)["epoch"] for t in (0, 2399, 2400, 11999)] == [1, 1, 2, 5]
    r5 = RC.plan(0.0, "r5")
    assert (r5["stage"], r5["no_new_work_ts"], r5["end_ts"]) == ("PILOT", 6000, 7200)
    assert RC.plan(0.0, "some-test-id", epoch_s=1.0)["epoch_s"] == 1.0


def test_start_writes_pm_round_r6(monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    r.delete("pm:round:r6", RC.CURRENT)
    try:
        c = RC.start(r, "r6", start_ts=5000.0)
        assert r.get(RC.CURRENT) == "r6" and r.hget("pm:round:r6", "stage") == "PRODUCTION"
        assert RC.read(r, "r6") == c and c["end_ts"] == 5000.0 + 14400
        assert RC.read(r) is None                        # D18: a round past its end_ts is history, not the current clock
    finally:
        r.delete("pm:round:r6", RC.CURRENT)
