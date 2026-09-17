"""F14: two simulated epochs on dummy workers; the log shows clean boundaries.
Live: the per-lane test db (tests._live.live_url()) with unique lanes."""
from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid

import pytest

from primordial.bus import bus
from primordial.fabric import worker as W
from primordial.ops.epoch import EpochController
from primordial.tests._live import live_url

URL = live_url()
FN = "primordial.fabric.selftest_jobs:sleep_rows"


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-f14")
    monkeypatch.setenv("PM_LANE", "F")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x", encoding="utf-8")
    git(tmp_path, "add", "README")
    git(tmp_path, "commit", "-q", "-m", "init")
    lanes = ["e" + uuid.uuid4().hex[:6], "e" + uuid.uuid4().hex[:6]]
    yield r, tmp_path, lanes
    for L in lanes:
        r.delete(W.JOBS.format(L), W.ROWS.format(L), W.DONE.format(L), W.STOP.format(L), W.WSTATE.format(L))


def fake_export(out, stamp, r):
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"pm_swarm_{stamp}.jsonl"
    p.write_text(json.dumps({"stamp": stamp}) + "\n", encoding="utf-8")
    return {"swarm": (str(p), 1)}


def test_two_simulated_epochs_have_clean_boundaries(env):
    r, repo, lanes = env
    stop = threading.Event()

    def submitter():
        i = 0
        while not stop.is_set():
            for L in lanes:
                if r.xlen(W.JOBS.format(L)) - len(r.xrange(W.DONE.format(L))) < 2:
                    W.submit(L, FN, f"F14-{L}-{i}", f"rows/{L}.jsonl", ttl_cpu_s=30, kwargs={"s": 0.25}, r=r)
                    i += 1
            time.sleep(0.05)

    workers = [W.Worker(L, url=URL, repo=repo, log=lambda m: None) for L in lanes]
    threads = [threading.Thread(target=w.serve, kwargs={"block_ms": 100, "deadline_s": 60}, daemon=True)
               for w in workers]
    for t in threads + [threading.Thread(target=submitter, daemon=True)]:
        t.start()
    # wait until both workers are live before the clock starts
    t_wait = time.monotonic() + 30
    while not all(r.exists(W.WSTATE.format(L)) for L in lanes) and time.monotonic() < t_wait:
        time.sleep(0.05)
    ctl = EpochController(lanes, epoch_s=4, r=r, out=repo / "epochs", repo=repo, export=fake_export,
                          drain_timeout_s=20, log=lambda m: None)
    recs = ctl.run(epochs=2)
    time.sleep(1.5)                                          # epoch 3 work after the last resume
    stop.set()
    done = {L: [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(L))] for L in lanes}
    for w in workers:
        w.exit_requested = True
    for t in threads:
        t.join(timeout=30)
    assert not any(t.is_alive() for t in threads)

    names = [e["event"] for e in ctl.events]
    assert names == ["start"] + ["epoch_post", "stop_set", "drained", "exported", "committed", "resumed"] * 2
    bounds = []
    for n in (1, 2):
        seg = ctl.events[1 + 6 * (n - 1): 1 + 6 * n]
        drained, resumed = seg[2], seg[5]
        assert drained["stragglers"] == [] and sorted(drained["workers"]) == sorted(lanes)
        assert seg[4]["sha"]                                             # committed
        bounds.append((drained["ts"], resumed["ts"]))
    jobs = [j for L in lanes for j in done[L]]
    assert all(j["status"] == "ok" for j in jobs)
    for d_ts, r_ts in bounds:
        straddlers = [j for j in jobs if j["started"] < r_ts and j["ended"] > d_ts]
        assert straddlers == [], straddlers                               # nothing ran across export+commit
    start_ts = ctl.events[0]["ts"]
    windows = [(start_ts, bounds[0][0]), (bounds[0][1], bounds[1][0]), (bounds[1][1], float("inf"))]
    for L in lanes:
        for lo, hi in windows:
            assert any(lo <= j["started"] and j["ended"] <= hi for j in done[L]), (L, lo, hi)
    log = git(repo, "log", "--format=%s", "--", "epochs")
    assert "rows EPOCH-1" in log and "rows EPOCH-2" in log
    rec2 = json.loads(git(repo, "show", "HEAD:epochs/EPOCH_2.json"))
    assert rec2["epoch"] == 2 and rec2["stragglers"] == [] and rec2["export"] == {"swarm": 1}
    # F-R6-1 (D3): the full log lives outside the repo; the in-repo copy is written just BEFORE each commit, so
    # it holds every event up to the last `committed` (never an event appended after a commit)
    assert [json.loads(x)["event"] for x in ctl.log_path.read_text().splitlines()] == names
    last_commit = len(names) - 1 - names[::-1].index("committed")
    assert [json.loads(x)["event"] for x in (repo / "epochs" / "epoch_log.jsonl").read_text().splitlines()] == \
        names[:last_commit]
    assert not any(r.exists(W.STOP.format(L)) for L in lanes)                # flags cleared at resume
    assert r.hgetall("pm:epoch:state")["phase"] == "running" and len(recs) == 2
