"""F7 warm worker: TTL kills the job (partial rows committed), the worker lives on, job 2 pays no JIT.
Live tests use db 13 on 6390 (other builders' suites FLUSH db 15 concurrently: the first run here
lost its job stream mid-test to NOGROUP) with a unique lane per test, deleting only their own keys."""
from __future__ import annotations

import json
import subprocess
import uuid

import pytest

from primordial.fabric import worker as W

from primordial.tests._live import live_url  # noqa: E402

URL = live_url()                                  # per-lane db (was a shared db 13)
FN = "primordial.fabric.selftest_jobs:"


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
    lane = "t" + uuid.uuid4().hex[:8]
    keys = [W.JOBS.format(lane), W.ROWS.format(lane), W.DONE.format(lane)]
    monkeypatch.setenv("PM_TAG", "t-f7")
    monkeypatch.setenv("PM_LANE", "F")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x", encoding="utf-8")
    git(tmp_path, "add", "README")
    git(tmp_path, "commit", "-q", "-m", "init")
    yield r, tmp_path, lane
    r.delete(*keys)


def committed_rows(repo, rel):
    return [json.loads(x) for x in git(repo, "show", f"HEAD:{rel}").splitlines()]


def test_timeout_kills_job_commits_partial_rows_and_worker_continues(env):
    r, repo, L = env
    W.submit(L, FN + "burn", "F7-burn", "rows/burn.jsonl", ttl_cpu_s=1.0, r=r)
    W.submit(L, FN + "emit_n", "F7-after", "rows/after.jsonl", ttl_cpu_s=30, kwargs={"n": 3}, r=r)
    wk = W.Worker(L, url=URL, repo=repo, log=lambda m: None)
    first, second = wk.serve(max_jobs=2, block_ms=1000)
    assert first["status"] == "timeout" and first["cpu_s"] > 1.0 and first["rows"] >= 1
    rows = committed_rows(repo, "rows/burn.jsonl")
    assert [x["status"] for x in rows[:-1]] == ["dev"] * (len(rows) - 1)
    assert rows[-1]["status"] == "timeout" and rows[-1]["rows_before"] == first["rows"]
    assert git(repo, "status", "--short", "rows") == ""                       # nothing left uncommitted
    assert second["status"] == "ok" and second["rows"] == 3                   # the session survived the kill
    assert [x["i"] for x in committed_rows(repo, "rows/after.jsonl")] == [0, 1, 2]
    assert wk.children_spawned == 2                                           # one kill -> one respawn
    done = [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(L))]
    assert [d["status"] for d in done] == ["timeout", "ok"]


def test_second_job_in_the_warm_child_pays_no_jit(env):
    r, repo, L = env
    for i in range(2):
        W.submit(L, FN + "jit_probe", f"F7-jit{i}", "rows/jit.jsonl", ttl_cpu_s=120, r=r)
    wk = W.Worker(L, url=URL, repo=repo, log=lambda m: None)
    a, b = wk.serve(max_jobs=2, block_ms=1000)
    assert a["status"] == b["status"] == "ok" and wk.children_spawned == 1
    p1, p2 = committed_rows(repo, "rows/jit.jsonl")
    assert (p1["job_in_child"], p2["job_in_child"]) == (1, 2)                 # ctx.cache survived
    assert p1["call_s"] > 0.05                                                # job 1 compiled
    assert p2["call_s"] < p1["call_s"] / 20                                   # job 2 did not
    assert p1["value"] == p2["value"]


def test_failing_job_keeps_its_rows_and_an_aborted_end_row(env):
    r, repo, L = env
    W.submit(L, FN + "fail", "F7-fail", "rows/fail.jsonl", ttl_cpu_s=30, r=r)
    out = W.Worker(L, url=URL, repo=repo, log=lambda m: None).serve(max_jobs=1, block_ms=1000)[0]
    assert out["status"] == "error"
    rows = committed_rows(repo, "rows/fail.jsonl")
    assert [x["status"] for x in rows] == ["dev", "aborted"] and "deliberate" in rows[-1]["error"]


def test_a_rows_commit_failure_is_recorded_and_serve_keeps_running(env, monkeypatch):
    # 09-14 flake: RowWriter.close raised inside run_job and killed that lane's serve thread.
    r, repo, L = env
    real, calls = W.RowWriter.close, {"n": 0}

    def flaky_close(self, note=""):
        calls["n"] += 1
        if calls["n"] == 1:
            self.closed = True
            self.marker.unlink(missing_ok=True)
            raise ValueError("simulated commit failure")
        return real(self, note)

    monkeypatch.setattr(W.RowWriter, "close", flaky_close)
    W.submit(L, FN + "emit_n", "F7-cf1", "rows/cf1.jsonl", ttl_cpu_s=30, kwargs={"n": 2}, r=r)
    W.submit(L, FN + "emit_n", "F7-cf2", "rows/cf2.jsonl", ttl_cpu_s=30, kwargs={"n": 2}, r=r)
    wk = W.Worker(L, url=URL, repo=repo, log=lambda m: None)
    a, b = wk.serve(max_jobs=2, block_ms=1000)
    assert a["status"] == "ok" and a["commit_error"].startswith("ValueError: simulated")
    assert b["status"] == "ok" and b["commit_error"] is None
    assert [x["i"] for x in committed_rows(repo, "rows/cf2.jsonl")] == [0, 1]
    done = [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(L))]
    assert [d["job_id"] for d in done] == [a["job_id"], b["job_id"]]


def test_a_job_longer_than_the_state_ttl_keeps_the_worker_key_alive(env, monkeypatch):
    # 09-14 (G): pm:worker:<L> was set only between jobs, so a liveness reader called a busy worker
    # dead WSTATE_TTL seconds into any long job.
    import threading
    import time
    r, repo, L = env
    monkeypatch.setattr(W, "WSTATE_TTL", 3)
    key = W.WSTATE.format(L)
    W.submit(L, "primordial.fabric.selftest_jobs:sleep_rows", "F7-long", "rows/long.jsonl", ttl_cpu_s=60,
             kwargs={"s": 9.0}, r=r)
    wk = W.Worker(L, url=URL, repo=repo, log=lambda m: None)
    t = threading.Thread(target=wk.serve, kwargs={"max_jobs": 1, "block_ms": 500}, daemon=True)
    t.start()
    t_end = time.monotonic() + 30
    while r.hget(key, "state") != "busy" and time.monotonic() < t_end:
        time.sleep(0.05)
    assert r.hget(key, "state") == "busy"
    seen = []
    for _ in range(12):                       # ~6 s of a 9 s job: twice the TTL
        time.sleep(0.5)
        if not t.is_alive():
            break
        seen.append(r.exists(key) == 1)
    assert len(seen) >= 10 and all(seen)
    t.join(timeout=60)
    assert not t.is_alive()
    done = [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(L))]
    assert [d["status"] for d in done] == ["ok"]
