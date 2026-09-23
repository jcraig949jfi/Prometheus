"""F-R7-3 (D4 rest, PC 1789489827401-0; gate item 28): the warm child's fingerprint covers the job fn's IMPORT
CLOSURE, not only the fn module. Replays D-R6-5: job A loads helper v1; helper changes signature; a NEW job module B
calls the new signature. Round 6 ran the stale helper (TypeError, 0 rows); now the child is respawned
(CODE_RELOADED naming the helper) and B runs. The fingerprint also records the code repo (D14 guard)."""
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
LANE = "Fr7cl"
HELPER = "def f(*args):\n    return {v!r} if len(args) == {n} else (_ for _ in ()).throw(TypeError('arity'))\n"
JOB = ("from {pkg} import helper\n\n\ndef job(ctx):\n"
       "    ctx.emit({{'status': 'record', 'kind': 'cl', 'v': helper.f({args})}})\n")


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
    monkeypatch.setenv("PM_TAG", "t-r7-3")
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    pkg = f"pmcl_{uuid.uuid4().hex[:8]}"
    monkeypatch.setenv("PM_CLOSURE_PREFIXES", f"primordial.,{pkg}.")      # tmp modules count as in-repo code
    repo = tmp_path / "repo"
    repo.mkdir()
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *a], check=True)
    (repo / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    mods = tmp_path / "mods"
    (mods / pkg).mkdir(parents=True)
    (mods / pkg / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.syspath_prepend(str(mods))
    yield r, repo, mods / pkg, pkg
    r.delete(*keys)


def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]


def test_imported_helper_edit_reloads_the_child(env):
    """D-R6-5 replay, inside ONE serve() so the child that ran job A is still warm when job B arrives."""
    r, repo, d, pkg = env
    (d / "helper.py").write_text(HELPER.format(v="helper-v1", n=1), encoding="utf-8")
    (d / "job_a.py").write_text(JOB.format(pkg=pkg, args="1"), encoding="utf-8")
    w = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None)
    W.submit(LANE, f"{pkg}.job_a:job", "cl-a", "rows/a.jsonl", 30, r=r)
    ids = {}

    def feed():
        t = time.monotonic()
        while r.xlen(W.DONE.format(LANE)) < 1 and time.monotonic() - t < 60:
            time.sleep(0.02)
        (d / "helper.py").write_text(HELPER.format(v="helper-v2-three-args", n=3), encoding="utf-8")
        (d / "job_b.py").write_text(JOB.format(pkg=pkg, args="1, 2, 3"), encoding="utf-8")
        ids["b"] = W.submit(LANE, f"{pkg}.job_b:job", "cl-b", "rows/b.jsonl", 30, r=r)
        while r.xlen(W.DONE.format(LANE)) < 2 and time.monotonic() - t < 60:
            time.sleep(0.02)
        ids["b2"] = W.submit(LANE, f"{pkg}.job_b:job", "cl-b2", "rows/b2.jsonl", 30, r=r)   # nothing changed
    th = threading.Thread(target=feed, daemon=True)
    th.start()
    done = w.serve(max_jobs=3, block_ms=300, deadline_s=90)
    th.join(timeout=10)
    assert [d_["status"] for d_ in done] == ["ok", "ok", "ok"], done
    assert [x["v"] for x in rows(repo / "rows" / "a.jsonl") if x.get("kind") == "cl"] == ["helper-v1"]
    assert [x["v"] for x in rows(repo / "rows" / "b.jsonl") if x.get("kind") == "cl"] == ["helper-v2-three-args"]
    rel = EV.events(r, "CODE_RELOADED")
    assert len(rel) == 1 and rel[0]["job_id"] == ids["b"] and f"{pkg}.helper" in rel[0]["changed"]
    assert w.children_spawned == 2                                          # no respawn for the unchanged job b2


def test_fn_edited_after_submit_still_refused(env):
    r, repo, d, pkg = env
    (d / "helper.py").write_text(HELPER.format(v="h", n=1), encoding="utf-8")
    (d / "job_a.py").write_text(JOB.format(pkg=pkg, args="1"), encoding="utf-8")
    W.submit(LANE, f"{pkg}.job_a:job", "cl-x", "rows/x.jsonl", 30, r=r)
    (d / "job_a.py").write_text(JOB.format(pkg=pkg, args="1") + "# edited after submit\n", encoding="utf-8")
    done = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=1, block_ms=300)
    assert done[0]["status"] == "refused" and done[0]["reasons"] == ["CODE_FINGERPRINT_MISMATCH"]
    assert not (repo / "rows" / "x.jsonl").exists()


def test_code_repo_mismatch_is_refused(env):
    """D14: a worker whose child imports the fn module from a DIFFERENT repo than the submitter's is refused."""
    r, repo, d, pkg = env
    (d / "helper.py").write_text(HELPER.format(v="h", n=1), encoding="utf-8")
    (d / "job_a.py").write_text(JOB.format(pkg=pkg, args="1"), encoding="utf-8")
    jid = W.submit(LANE, f"{pkg}.job_a:job", "cl-repo", "rows/repo.jsonl", 30, r=r)
    [(mid, spec)] = [(m, f) for m, f in r.xrange(W.JOBS.format(LANE)) if f["job_id"] == jid]
    assert spec.get("code_repo")                                            # submit records where the code lives
    r.xdel(W.JOBS.format(LANE), mid)
    r.xadd(W.JOBS.format(LANE), dict(spec, code_repo="X:/Prometheus-worktrees/nestor-r5-d"))
    done = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=1, block_ms=300)
    assert done[0]["status"] == "refused" and done[0]["reasons"] == ["CODE_REPO_MISMATCH"]
    assert not (repo / "rows" / "repo.jsonl").exists() and EV.candidates(r) == []
