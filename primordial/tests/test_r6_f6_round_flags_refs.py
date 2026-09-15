"""F-R6-6 (A 1789479834686-0): `epoch round` shape flags reach the clock; defaults are the round's ROUNDS row
(r5 unchanged). A 1789479784925-0 (H-R6-1 D7 guard): the controller/push never prunes, mirrors or deletes refs,
so refs/pm/pred/* pins survive a controller push that has to rebase."""
from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

from primordial.bus import bus
from primordial.fabric import worker as W
from primordial.ops import epoch as EP
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = live_url()
LANE = "Fr6ref"
BRANCH = "integ-r6-refs"


def test_launch_command_shape_reaches_the_plan():
    a = EP.parser().parse_args(["round", "--lanes", "B,C,D,E,G", "--round", "r6", "--stage", "PRODUCTION",
                                "--epoch-s", "2400", "--epochs", "3", "--drain-s", "1200", "--close-s", "1200",
                                "--repo", "X"])
    c = RC.plan(100.0, a.round, **EP.round_shape(a))
    assert (c["round_id"], c["stage"], c["epoch_s"], c["epochs"]) == ("r6", "PRODUCTION", 2400.0, 3)
    assert (c["no_new_work_ts"], c["drain_ts"], c["end_ts"]) == (100 + 7200, 100 + 8400, 100 + 9600)


def test_flag_defaults_are_the_round_row():
    r5 = EP.parser().parse_args(["round", "--lanes", "B", "--round", "r5", "--repo", "X"])
    assert RC.plan(0.0, r5.round, **EP.round_shape(r5)) == RC.plan(0.0, "r5")
    assert RC.plan(0.0, "r5")["end_ts"] == 7200 and RC.plan(0.0, "r5")["stage"] == "PILOT"
    r6 = EP.parser().parse_args(["round", "--lanes", "B", "--round", "r6", "--repo", "X"])
    assert r6.round == "r6" and RC.plan(0.0, r6.round, **EP.round_shape(r6)) == RC.plan(0.0, "r6")


def test_no_ref_pruning_or_deletion_in_ops_or_fabric():
    bad = re.compile(r"""--prune|--mirror|--delete|["']:refs/|push\s+-d\b""")
    hits = []
    for d in ("ops", "fabric"):
        for p in (ROOT / "primordial" / d).rglob("*.py"):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if bad.search(line):
                    hits.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()}")
    assert hits == []


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
    keys = [W.STOP.format(LANE), W.WSTATE.format(LANE), W.DONE.format(LANE), EP.STATE]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r6-6")
    monkeypatch.setenv("PM_LANE", "F")
    monkeypatch.setenv("PM_INTEGRATION_BRANCH", BRANCH)
    bare, ctl, other = tmp_path / "remote.git", tmp_path / "ctl", tmp_path / "other"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    for c in (ctl, other):
        subprocess.run(["git", "clone", "-q", str(bare), str(c)], check=True, capture_output=True)
        git(c, "config", "user.email", "t@t")
        git(c, "config", "user.name", "t")
    git(ctl, "checkout", "-q", "-b", BRANCH)
    (ctl / "README").write_text("x", encoding="utf-8")
    git(ctl, "add", "README")
    git(ctl, "commit", "-q", "-m", "init")
    git(ctl, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    yield r, bare, ctl, other, tmp_path
    r.delete(*keys)


def test_pred_refs_survive_a_rebasing_controller_push(env):
    r, bare, ctl, other, tmp = env
    git(other, "fetch", "-q", "origin")
    git(other, "checkout", "-q", "-b", "lane", f"origin/{BRANCH}")
    (other / "lane.txt").write_text("predicate code", encoding="utf-8")
    git(other, "add", "lane.txt")
    git(other, "commit", "-q", "-m", "predicate-cited commit")
    cited = git(other, "rev-parse", "HEAD")
    git(other, "push", "-q", "origin", f"{cited}:refs/pm/pred/P-test")             # H's pin (a ref push)
    git(other, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")                 # the remote moves on
    ec = EP.EpochController([LANE], r=r, out=ctl / EP.EPOCHS_REL, repo=ctl, post=False, log=lambda *_: None,
                            push=True, push_branch=BRANCH, log_dir=tmp / "logs", drain_timeout_s=0.2,
                            export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    ec.boundary(1)
    assert ec.events[-2]["event"] == "pushed" or "pushed" in [e["event"] for e in ec.events]
    assert "push_failed" not in [e["event"] for e in ec.events]
    assert git(bare, "rev-parse", "refs/pm/pred/P-test") == cited                   # the pin survives
    assert git(bare, "merge-base", "--is-ancestor", cited, f"refs/heads/{BRANCH}") == ""   # rebased onto it
    assert git(ctl, "status", "--porcelain") == ""
