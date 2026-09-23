"""D19 (E 1789505689927-0): a job granted an 8-thread CPU token ran numba at 3 threads, because the warm child inherited
the session's NUMBA_NUM_THREADS=3. The worker now spawns the child with the grant in its environment and sets numba
to it; rows and the done record carry granted_threads and the effective numba_threads."""
from __future__ import annotations

import json
import os
import subprocess

import pytest

from primordial.bus import bus
from primordial.fabric import broker as BR
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fd19"


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES, BR.PROFILE_KEY, "pm:round:current"] + \
           [BR.TOKEN.format(i) for i in range(8)]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-d19")
    for k in W.THREAD_ENV:                                        # the planted session environment
        monkeypatch.setenv(k, "3")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def report(repo, name):
    return [json.loads(x) for x in (repo / "rows" / name).read_text(encoding="utf-8").splitlines()
            if json.loads(x).get("kind") == "threads"]


def test_granted_threads_reach_the_child(env):
    r, repo = env
    r.set(BR.PROFILE_KEY, json.dumps({"k_star": 1, "threads_per_worker": 8}))
    W.submit(LANE, "primordial.fabric.selftest_jobs:thread_report", "d19-grant", "rows/grant.jsonl", 60, r=r,
             envelope=EV.example())
    done = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None, broker=True).serve(max_jobs=1, block_ms=300)
    [row] = report(repo, "grant.jsonl")
    assert (row["numba_get"], row["numba_config"], row["omp_env"], row["numba_env"]) == (8, 8, "8", "8")
    assert row["granted_threads"] == 8 and row["numba_threads"] == 8
    assert done[0]["granted_threads"] == 8 and done[0]["numba_threads"] == 8 and done[0]["cpu_token"]["threads"] == 8
    assert os.environ["NUMBA_NUM_THREADS"] == "3"                 # the parent's environment is restored


def test_without_a_grant_the_planted_env_still_bites(env):
    """Control: no token -> the child inherits the session's 3 (proves the planted environment is real)."""
    r, repo = env
    W.submit(LANE, "primordial.fabric.selftest_jobs:thread_report", "d19-none", "rows/none.jsonl", 60, r=r)
    done = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None, broker=False).serve(max_jobs=1, block_ms=300)
    [row] = report(repo, "none.jsonl")
    assert row["numba_config"] == 3 and row["numba_get"] == 3 and done[0]["granted_threads"] is None


def test_child_respawned_when_grant_changes(env):
    r, repo = env
    w = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None, broker=False)
    for n, t in (("a", "4"), ("b", "4"), ("c", "8")):
        jid = W.submit(LANE, "primordial.fabric.selftest_jobs:thread_report", f"d19-{n}", f"rows/{n}.jsonl", 60, r=r)
        [(mid, spec)] = [(m, f) for m, f in r.xrange(W.JOBS.format(LANE)) if f["job_id"] == jid]
        r.xdel(W.JOBS.format(LANE), mid)
        r.xadd(W.JOBS.format(LANE), dict(spec, threads=t))        # the token grant, as serve() stamps it
    done = w.serve(max_jobs=3, block_ms=300)
    assert [d["numba_threads"] for d in done] == [4, 4, 8] and w.children_spawned == 2
