"""F-R6-2 (D4, gate item 18): a warm worker never runs stale resident code. The job carries the fn module's
source sha256 from submit; the child that already imported an older version is respawned (CODE_RELOADED) and
job 2 runs the NEW code; a module that changed again after submit is refused CODE_FINGERPRINT_MISMATCH."""
from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fr6fp"
SRC = 'def job(ctx):\n    ctx.emit({{"status": "record", "kind": "fp", "v": {v!r}}})\n'


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES, "pm:round:current"]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r6-2")
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    repo = tmp_path / "repo"
    repo.mkdir()
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *a], check=True)
    (repo / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    mods = tmp_path / "mods"
    mods.mkdir()
    monkeypatch.syspath_prepend(str(mods))
    name = f"pm_fp_{uuid.uuid4().hex[:8]}"
    yield r, repo, mods / f"{name}.py", f"{name}:job"
    r.delete(*keys)


def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]


def test_edit_between_jobs_reloads_and_runs_new_code(env):
    """ONE serve() call, so the child that ran job 1 is still warm when job 2 arrives (serve() stops its child
    on return: two serve() calls would give job 2 a fresh child and never exercise the stale-module path)."""
    r, repo, src, fn = env
    src.write_text(SRC.format(v="one"), encoding="utf-8")
    w = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None)
    W.submit(LANE, fn, "fp1", "rows/fp1.jsonl", 30, r=r)
    ids = {}

    def feed():
        def n_done():
            return r.xlen(W.DONE.format(LANE))
        t = time.monotonic()
        while n_done() < 1 and time.monotonic() - t < 60:
            time.sleep(0.02)
        src.write_text(SRC.format(v="two-longer"), encoding="utf-8")   # the repair lands mid-round
        ids["fp2"] = W.submit(LANE, fn, "fp2", "rows/fp2.jsonl", 30, r=r)
        while n_done() < 2 and time.monotonic() - t < 60:
            time.sleep(0.02)
        ids["fp3"] = W.submit(LANE, fn, "fp3", "rows/fp3.jsonl", 30, r=r)  # unchanged code: no respawn
    th = threading.Thread(target=feed, daemon=True)
    th.start()
    done = w.serve(max_jobs=3, block_ms=300, deadline_s=90)
    th.join(timeout=10)
    assert [d["status"] for d in done] == ["ok", "ok", "ok"]
    assert w.children_spawned == 2                                      # job 1 child + ONE reload for job 2
    assert [x["v"] for x in rows(repo / "rows" / "fp1.jsonl") if x.get("kind") == "fp"] == ["one"]
    assert [x["v"] for x in rows(repo / "rows" / "fp2.jsonl") if x.get("kind") == "fp"] == ["two-longer"]
    assert [x["v"] for x in rows(repo / "rows" / "fp3.jsonl") if x.get("kind") == "fp"] == ["two-longer"]
    rel = EV.events(r, "CODE_RELOADED")
    assert len(rel) == 1 and rel[0]["job_id"] == ids["fp2"] and rel[0]["loaded"] != rel[0]["want"]


def test_changed_after_submit_is_refused(env):
    r, repo, src, fn = env
    src.write_text(SRC.format(v="submitted"), encoding="utf-8")
    W.submit(LANE, fn, "fpx", "rows/fpx.jsonl", 30, r=r)                # fingerprint of the submitted source
    src.write_text(SRC.format(v="edited-after-submit"), encoding="utf-8")
    w = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None)
    d = w.serve(max_jobs=1, block_ms=300)
    assert d[0]["status"] == "refused" and d[0]["reasons"] == ["CODE_FINGERPRINT_MISMATCH"]
    assert d[0]["event"] == "CODE_FINGERPRINT_MISMATCH"
    assert not (repo / "rows" / "fpx.jsonl").exists()
    assert len(EV.events(r, "CODE_RELOADED")) == 1 and len(EV.events(r, "CODE_FINGERPRINT_MISMATCH")) == 1
    assert EV.candidates(r) == []                                        # a code mismatch is not a cost stub


def test_legacy_job_without_fingerprint_runs(env):
    r, repo, src, fn = env
    src.write_text(SRC.format(v="legacy"), encoding="utf-8")
    r.xadd(W.JOBS.format(LANE), {"job_id": "legacy1", "fn": fn, "exp_id": "lg", "rows": "rows/lg.jsonl",
                                 "ttl_cpu_s": "30", "kwargs": "{}", "job_key": "legacy1", "segment": "0"})
    d = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=1, block_ms=300)
    assert d[0]["status"] == "ok" and EV.events(r, "CODE_RELOADED") == []
