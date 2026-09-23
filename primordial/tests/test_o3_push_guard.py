"""O3: RowWriter PM_TAG guard, live-writer markers, fast-forward-only push while a writer is live."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from primordial.fabric.rows import RowWriter, commit_path, live_writers, writers_dir
from primordial.ops import push as P
from primordial.ops.push import CONFLICT, REFUSED, push

BR = "integ"


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def init(path):
    git(path, "config", "user.email", "t@t")
    git(path, "config", "user.name", "t")


def commit_file(repo, name, text):
    (repo / name).write_text(text, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", name)


@pytest.fixture(autouse=True)
def tagged(monkeypatch):
    monkeypatch.setenv("PM_TAG", "t-0000")
    monkeypatch.setenv("PM_LANE", "F")
    # the push lock talks to the bus; these git-only tests must never touch the production bus
    monkeypatch.setattr(P, "acquire_push_lock", lambda *a, **k: None)


@pytest.fixture
def world(tmp_path):
    """bare remote; clone `me` (the lane) and clone `other` (a sibling pusher)."""
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q")
    init(seed)
    commit_file(seed, "README", "x")
    git(seed, "push", "-q", str(remote), f"HEAD:refs/heads/{BR}")
    clones = []
    for name in ("me", "other"):
        subprocess.run(["git", "clone", "-q", "-b", BR, str(remote), str(tmp_path / name)], check=True)
        init(tmp_path / name)
        clones.append(tmp_path / name)
    return remote, clones[0], clones[1]


@pytest.mark.parametrize("bad", [None, "", "untagged", "  "])
def test_rowwriter_and_commit_refuse_without_pm_tag(world, monkeypatch, bad):
    _, me, _ = world
    if bad is None:
        monkeypatch.delenv("PM_TAG", raising=False)
    else:
        monkeypatch.setenv("PM_TAG", bad)
    with pytest.raises(RuntimeError, match="PM_TAG"):
        RowWriter(me / "rows" / "x.jsonl", "X", repo=me)
    (me / "loose.jsonl").write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="PM_TAG"):
        commit_path(me / "loose.jsonl", "X", repo=me)
    assert not (me / "rows" / "x.jsonl").exists()


def test_live_marker_lifecycle_and_dead_pid_pruned(world):
    _, me, _ = world
    w = RowWriter(me / "rows" / "a.jsonl", "A1", commit_every_s=3600, repo=me)
    live = live_writers(me)
    assert [x["exp_id"] for x in live] == ["A1"] and live[0]["tag"] == "t-0000"
    dead = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True, text=True)
    stale = writers_dir(me) / "999-dead.json"
    stale.write_text(json.dumps({"pid": int(dead.stdout), "exp_id": "ghost"}), encoding="utf-8")
    assert [x["exp_id"] for x in live_writers(me)] == ["A1"]
    assert not stale.exists()                                       # pruned
    w.write({"status": "dev", "v": 1})
    w.close()
    assert live_writers(me) == []
    assert "pm-rowwriters" not in git(me, "status", "--short", "--untracked-files=all")  # marker lives in the git dir


def test_push_refuses_rebase_while_writer_live_then_rebases_after_close(world):
    remote, me, other = world
    commit_file(other, "o.txt", "sibling")
    git(other, "push", "-q", "origin", f"HEAD:{BR}")
    commit_file(me, "m.txt", "mine")
    head_before = git(me, "rev-parse", "HEAD")
    w = RowWriter(me / "rows" / "b.jsonl", "B1", commit_every_s=3600, repo=me)
    w.write({"status": "dev", "v": 1})
    msgs = []
    assert push(me, branch=BR, log=msgs.append) == REFUSED
    assert "B1" in msgs[-1]
    assert git(me, "rev-parse", "HEAD") == head_before              # no rebase happened
    w.close()                                                       # commits rows on top of m.txt
    assert push(me, branch=BR, log=msgs.append) == 0
    files = git(remote, "ls-tree", "-r", "--name-only", BR).split()
    assert {"o.txt", "m.txt", "rows/b.jsonl"} <= set(files)


def test_push_fast_forwards_while_writer_live(world):
    remote, me, _ = world
    w = RowWriter(me / "rows" / "c.jsonl", "C1", commit_every_s=0, repo=me)
    w.write({"status": "record", "v": 2})                          # committed immediately
    assert push(me, branch=BR, log=lambda m: None) == 0
    assert git(remote, "rev-parse", BR) == git(me, "rev-parse", "HEAD")
    w.close()


def test_push_aborts_conflicting_rebase(world):
    _, me, other = world
    commit_file(other, "README", "theirs")
    git(other, "push", "-q", "origin", f"HEAD:{BR}")
    commit_file(me, "README", "mine")
    assert push(me, branch=BR, log=lambda m: None) == CONFLICT
    assert "rebase" not in git(me, "status")                        # aborted, clean


@pytest.fixture
def lockenv(monkeypatch):
    redis = pytest.importorskip("redis")
    import uuid
    from primordial.tests._live import live_url
    r = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    from primordial.fabric.worker import PUSH_LOCK, WSTATE
    lane = "p" + uuid.uuid4().hex[:8]
    monkeypatch.setenv("PM_LANE", lane)
    monkeypatch.setattr(P, "acquire_push_lock", REAL_ACQUIRE)
    yield r, lane, PUSH_LOCK.format(lane), WSTATE.format(lane)
    r.delete(PUSH_LOCK.format(lane), WSTATE.format(lane))


REAL_ACQUIRE = P.acquire_push_lock


def test_push_holds_the_lane_lock_during_the_rebase_and_releases_it(world, lockenv, monkeypatch):
    # 09-15 E: the epoch controller cleared the stop flag mid-rebase and the next segment's RowWriter
    # opened its rows file; the push lock is what the worker honours instead
    r, lane, key, _ = lockenv
    remote, me, other = world
    commit_file(other, "o.txt", "sibling")
    git(other, "push", "-q", "origin", f"HEAD:{BR}")
    commit_file(me, "m.txt", "mine")
    seen, real_git = [], P._git
    def spy(repo, *a, **k):
        if a and a[0] == "rebase" and a[1:2] != ("--abort",):
            seen.append(bool(r.exists(key)))
        return real_git(repo, *a, **k)
    monkeypatch.setattr(P, "_git", spy)
    assert push(me, branch=BR, log=lambda m: None, lock_redis=r) == 0
    assert seen == [True]                       # the lock was held while git rebase ran
    assert not r.exists(key)                    # and released after the push
    assert {"o.txt", "m.txt"} <= set(git(remote, "ls-tree", "-r", "--name-only", BR).split())


def test_push_refuses_without_rebasing_while_the_worker_stays_busy(world, lockenv):
    r, lane, key, wstate = lockenv
    _, me, other = world
    commit_file(other, "o.txt", "sibling")
    git(other, "push", "-q", "origin", f"HEAD:{BR}")
    commit_file(me, "m.txt", "mine")
    head = git(me, "rev-parse", "HEAD")
    r.hset(wstate, mapping={"state": "busy", "job_id": "j"})
    msgs = []
    assert push(me, branch=BR, log=msgs.append, lock_wait_s=0.5, lock_redis=r) == REFUSED
    assert "stayed busy" in msgs[-1]
    assert git(me, "rev-parse", "HEAD") == head
    assert not r.exists(key)
