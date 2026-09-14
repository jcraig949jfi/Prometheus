"""F9: a 3-epoch job resumes from checkpoints and reproduces the uninterrupted rows exactly."""
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
WALK = "primordial.fabric.selftest_jobs:walk"
VOLATILE = ("ts", "job_id", "exp_id", "segment")


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
    monkeypatch.setenv("PM_TAG", "t-f9")
    monkeypatch.setenv("PM_LANE", "F")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x", encoding="utf-8")
    git(tmp_path, "add", "README")
    git(tmp_path, "commit", "-q", "-m", "init")
    lanes = []
    yield r, tmp_path, lanes
    for L in lanes:
        r.delete(W.JOBS.format(L), W.ROWS.format(L), W.DONE.format(L), W.STOP.format(L), W.WSTATE.format(L))


def fake_export(out, stamp, r):
    out.mkdir(parents=True, exist_ok=True)
    return {}


def stable(rows):
    return [{k: v for k, v in x.items() if k not in VOLATILE} for x in rows]


def committed(repo, rel):
    return [json.loads(x) for x in git(repo, "show", f"HEAD:{rel}").splitlines()]


def test_three_epoch_job_reproduces_uninterrupted_rows(env):
    r, repo, lanes = env
    ck = repo.parent / "ckpt"
    kw = {"steps": 60, "seed": 11, "step_s": 0.03}

    # A: uninterrupted
    La = "a" + uuid.uuid4().hex[:6]
    lanes.append(La)
    W.submit(La, WALK, "F9-a", "rows/a.jsonl", ttl_cpu_s=120, kwargs=kw, r=r)
    (a,) = W.Worker(La, url=URL, repo=repo, log=lambda m: None, ckpt_dir=ck).serve(max_jobs=1, block_ms=500)
    assert a["status"] == "ok" and a["rows"] == 60

    # B: the same job across 3 epochs (2 boundaries while it runs)
    Lb = "b" + uuid.uuid4().hex[:6]
    lanes.append(Lb)
    W.submit(Lb, WALK, "F9-b", "rows/b.jsonl", ttl_cpu_s=120, kwargs=kw, r=r, job_key="walk-b")
    wk = W.Worker(Lb, url=URL, repo=repo, log=lambda m: None, ckpt_dir=ck)
    th = threading.Thread(target=wk.serve, kwargs={"block_ms": 100, "deadline_s": 90}, daemon=True)
    th.start()
    ctl = EpochController([Lb], epoch_s=1, r=r, out=repo / "epochs", repo=repo, export=fake_export,
                          drain_timeout_s=30, post=False, log=lambda m: None)

    def rows_seen():
        return sum(1 for _, f in r.xrange(W.ROWS.format(Lb)))

    for n, at in ((1, 15), (2, 35)):
        end = time.monotonic() + 60
        while rows_seen() < at and time.monotonic() < end:
            time.sleep(0.01)
        rec = ctl.boundary(n)
        assert rec["stragglers"] == []
    end = time.monotonic() + 60
    while len(r.xrange(W.DONE.format(Lb))) < 3 and time.monotonic() < end:
        time.sleep(0.05)
    wk.exit_requested = True
    th.join(timeout=30)

    done = [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(Lb))]
    assert [d["status"] for d in done] == ["paused", "paused", "ok"]
    assert [d["segment"] for d in done] == [0, 1, 2] and {d["job_key"] for d in done} == {"walk-b"}
    assert done[2]["cpu_prior"] > 0                                           # CPU carried across segments
    rows_a, rows_b = committed(repo, "rows/a.jsonl"), committed(repo, "rows/b.jsonl")
    assert sorted({x["segment"] for x in rows_b}) == [0, 1, 2]                # it really spanned 3 epochs
    assert stable(rows_b) == stable(rows_a)                                  # exact reproduction
    assert not (ck / Lb / "walk-b.pkl").exists()                             # checkpoint removed at the end


def test_ttl_bounds_the_whole_checkpointed_job(env):
    r, repo, lanes = env
    L = "c" + uuid.uuid4().hex[:6]
    lanes.append(L)
    W.submit(L, "primordial.fabric.selftest_jobs:burn", "F9-c", "rows/c.jsonl", ttl_cpu_s=1.0, r=r,
             job_key="burn-c", segment=3, cpu_prior=0.9)
    (d,) = W.Worker(L, url=URL, repo=repo, log=lambda m: None, ckpt_dir=repo.parent / "ck2").serve(
        max_jobs=1, block_ms=500)
    assert d["status"] == "timeout" and d["cpu_s"] < 0.9                      # 0.9 prior + < 0.1 s of burn
    end = committed(repo, "rows/c.jsonl")[-1]
    assert end["status"] == "timeout" and end["segment"] == 3 and end["cpu_prior"] == 0.9
