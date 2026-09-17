"""S3 prior-vs-reality view on the live board (pm:board:prior_vs_reality), per-lane test db."""
from __future__ import annotations

import pytest

from primordial.bus import bus
from primordial.score import round2 as R2


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
    yield r
    r.flushdb()


def test_board_publishes_round2_calibration_and_replaces_atomically(live):
    live.zadd(R2.BOARD, {"stale|member|brier": 9.0})
    out = R2.resolve()
    n = R2.publish_board(out, live)
    assert n == live.zcard(R2.BOARD) and live.zscore(R2.BOARD, "stale|member|brier") is None
    assert live.zscore(R2.BOARD, "ALL|all|n_decided") == 41.0
    assert live.zscore(R2.BOARD, "B|all|brier") == pytest.approx(0.1945)
    assert live.zscore(R2.BOARD, "C|all|hit_rate") == pytest.approx(0.3333)
    assert live.zscore(R2.BOARD, "B|w4|n_decided") == 10.0
    assert [k for k, _ in bus.standings("prior_vs_reality", n=10**6, r=live)]      # visible to `bus board`
