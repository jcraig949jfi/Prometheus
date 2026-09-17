"""F-R5-6: the drain window is sized to the running jobs' wall budgets (defect F8), and the epoch
controller refuses to run in the worktree holding this code (defect F7)."""
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
from primordial.ops import epoch as EP
from primordial.tests._live import live_url

URL = live_url()


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def fake_export(out, stamp, r):
    out.mkdir(parents=True, exist_ok=True)
    return {}


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r5-6")
    monkeypatch.setenv("PM_LANE", "F")
    repo = tmp_path / "ctl"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    (repo / "README").write_text("x", encoding="utf-8")
    git(repo, "add", "README")
    git(repo, "commit", "-q", "-m", "init")
    lanes = []
    yield r, repo, lanes
    for L in lanes:
        r.delete(W.JOBS.format(L), W.ROWS.format(L), W.DONE.format(L), W.STOP.format(L), W.WSTATE.format(L))


def busy_worker(r, lane, wall_budget_s=None, wall_prior=0.0):
    job_id = uuid.uuid4().hex[:12]
    spec = {"job_id": job_id, "fn": "x:y", "wall_prior": str(wall_prior)}
    if wall_budget_s is not None:
        spec["envelope"] = json.dumps(EV.example(wall_budget_s=wall_budget_s))
    r.xadd(W.JOBS.format(lane), spec)
    r.hset(W.WSTATE.format(lane), mapping={"state": "busy", "job_id": job_id, "ts": f"{time.time():.3f}"})
    r.expire(W.WSTATE.format(lane), 60)
    return job_id


def test_drain_timeout_sized_to_job_wall(env):
    r, repo, lanes = env
    La, Lb = f"F6a{uuid.uuid4().hex[:5]}", f"F6b{uuid.uuid4().hex[:5]}"
    lanes += [La, Lb]
    busy_worker(r, La, wall_budget_s=40, wall_prior=10)
    ctl = EP.EpochController([La], r=r, out=repo / "epochs", repo=repo, export=fake_export, post=False,
                             log=lambda m: None)
    assert ctl.drain_timeout() == 30 + EP.DRAIN_MARGIN_S == 60
    busy_worker(r, Lb)                                                 # no envelope -> PILOT cpu wall ceiling
    ctl.lanes = [La, Lb]
    assert ctl.drain_timeout() == EV.CEILINGS["PILOT"]["cpu_wall_s"] + EP.DRAIN_MARGIN_S
    assert EP.EpochController([La], r=r, drain_timeout_s=7, post=False, log=lambda m: None).drain_timeout() == 7


def test_no_busy_worker_is_margin(env):
    r, repo, lanes = env
    L = f"F6c{uuid.uuid4().hex[:5]}"
    lanes.append(L)
    r.hset(W.WSTATE.format(L), mapping={"state": "idle", "job_id": "", "ts": "0"})
    ctl = EP.EpochController([L, f"F6none{uuid.uuid4().hex[:5]}"], r=r, post=False, log=lambda m: None)
    assert ctl.drain_timeout() == EP.DRAIN_MARGIN_S


def _straggler_boundary(r, repo, lane, monkeypatch, **kw):
    monkeypatch.setattr(EP, "DRAIN_MARGIN_S", 0.5)
    busy_worker(r, lane, wall_budget_s=2)

    def finish():
        time.sleep(1.5)
        r.hset(W.WSTATE.format(lane), "state", "stopped")
    th = threading.Thread(target=finish, daemon=True)
    th.start()
    ctl = EP.EpochController([lane], r=r, out=repo / f"epochs_{lane}", repo=repo, export=fake_export, post=False,
                             log=lambda m: None, **kw)
    rec = ctl.boundary(1)
    th.join()
    return ctl, rec


def test_sized_drain_waits_for_the_straggler(env, monkeypatch):
    r, repo, lanes = env
    L = f"F6d{uuid.uuid4().hex[:5]}"
    lanes.append(L)
    ctl, rec = _straggler_boundary(r, repo, L, monkeypatch)
    assert rec["stragglers"] == [] and rec["drain_timeout_s"] == 2.5
    drained = next(e for e in ctl.events if e["event"] == "drained")
    assert drained["drain_timeout_s"] == 2.5 and drained["stragglers"] == []


def test_explicit_short_drain_records_the_straggler(env, monkeypatch):
    r, repo, lanes = env
    L = f"F6e{uuid.uuid4().hex[:5]}"
    lanes.append(L)
    ctl, rec = _straggler_boundary(r, repo, L, monkeypatch, drain_timeout_s=0.2)
    assert rec["stragglers"] == [L] and rec["drain_timeout_s"] == 0.2


def test_controller_repo_refusals(tmp_path, env):
    r, repo, lanes = env
    assert not EP.controller_repo(None)[0]
    assert not EP.controller_repo("")[0]
    assert not EP.controller_repo(EP.ROOT)[0]
    assert not EP.controller_repo(EP.ROOT / "primordial")[0]                 # inside this code's worktree
    plain = tmp_path / "plain"
    plain.mkdir()
    ok, why = EP.controller_repo(plain)
    assert not ok and "git" in why
    assert EP.controller_repo(repo) == (True, "")


def test_cli_without_repo_refuses_and_writes_nothing(env, monkeypatch, capsys):
    r, repo, lanes = env
    monkeypatch.delenv("PM_EPOCH_REPO", raising=False)
    monkeypatch.setattr(bus, "conn", lambda: pytest.fail("CLI touched Redis before the repo check"))
    r.delete(EP.STATE)
    assert EP.main(["boundary", "1", "--lanes", "X"]) == 2
    assert EP.main(["boundary", "1", "--lanes", "X", "--repo", str(EP.ROOT)]) == 2
    assert "refused" in capsys.readouterr().err
    assert not r.exists(EP.STATE)


def test_boundary_in_own_repo_leaves_code_worktree_untouched(env):
    r, repo, lanes = env
    L = f"F6f{uuid.uuid4().hex[:5]}"
    lanes.append(L)
    root_epochs = EP.ROOT / EP.EPOCHS_REL

    def snapshot():
        if not root_epochs.exists():
            return None
        return sorted((str(p.relative_to(root_epochs)), p.stat().st_mtime_ns) for p in root_epochs.rglob("*"))
    before = snapshot()
    ctl = EP.EpochController([L], r=r, out=repo / EP.EPOCHS_REL, repo=repo, export=fake_export, post=False,
                             log=lambda m: None)
    rec = ctl.boundary(1)
    assert snapshot() == before
    assert (repo / EP.EPOCHS_REL / "EPOCH_1.json").exists()
    assert "EPOCH-1" in git(repo, "log", "--format=%s") and rec["sha"]
    r.delete(EP.STATE)
