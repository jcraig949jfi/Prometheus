"""F-R5-6 review fix: the job-sized drain (up to wall budget + margin, e.g. 930 s) must not push the round's
close past end_ts. The final drain boundary is capped at the time left to end_ts; a straggler is recorded."""
from __future__ import annotations

import subprocess
import time

import pytest

from primordial.bus import bus
from primordial.fabric import worker as W
from primordial.ops import epoch as EP
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fcap"


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.STOP.format(LANE), W.WSTATE.format(LANE), EP.STATE]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r5-6cap")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def test_final_drain_capped_at_round_end(env):
    r, repo = env
    r.hset(W.WSTATE.format(LANE), mapping={"state": "busy", "job_id": "no-envelope-job", "ts": "0"})
    r.expire(W.WSTATE.format(LANE), 60)                       # a busy job the controller cannot see -> 900 s bound
    ec = EP.EpochController([LANE], r=r, out=repo / "epochs", repo=repo, post=False, log=lambda *_: None,
                            export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    assert ec.drain_timeout() == pytest.approx(900 + EP.DRAIN_MARGIN_S)
    t = time.monotonic()
    rec = ec.boundary(4, resume=False, max_drain_s=0.4)
    assert time.monotonic() - t < 10
    assert rec["drain_timeout_s"] == pytest.approx(0.4) and rec["stragglers"] == [LANE]
    assert ec.boundary(5, resume=False, max_drain_s=-3)["drain_timeout_s"] == 0.0
