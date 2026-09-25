"""F-R6-1 (D3), launch gate item 17: the epoch controller publishes from a clone of a bare remote and leaves it
CLEAN with push rc 0 at every boundary and at close. Round 5: epoch_log.jsonl was appended after each commit,
so ops.push refused on the dirty tree 5/5 and A pushed by hand."""
from __future__ import annotations

import json
import subprocess
import time

import pytest

from primordial.bus import bus
from primordial.fabric import worker as W
from primordial.ops import epoch as EP
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fr6c"
RID = "t-r6-1"
BRANCH = "integ-r6-test"


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
    keys = [W.JOBS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE), W.WSTATE.format(LANE), EP.STATE,
            EP.NO_NEW_WORK.format(RID)]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r6-1")
    monkeypatch.setenv("PM_LANE", "F")
    monkeypatch.setenv("PM_INTEGRATION_BRANCH", BRANCH)
    bare, clone = tmp_path / "remote.git", tmp_path / "ctl"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], check=True, capture_output=True)
    git(clone, "config", "user.email", "t@t")
    git(clone, "config", "user.name", "t")
    git(clone, "checkout", "-q", "-b", BRANCH)
    (clone / "README").write_text("x", encoding="utf-8")
    git(clone, "add", "README")
    git(clone, "commit", "-q", "-m", "init")
    git(clone, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    yield r, bare, clone, tmp_path / "outside-logs"
    r.delete(*keys)


def test_controller_publishes_clean_with_push_rc0(env):
    r, bare, clone, logdir = env
    out = clone / EP.EPOCHS_REL
    ec = EP.EpochController([LANE], r=r, out=out, repo=clone, post=False, log=lambda *_: None, push=True,
                            push_branch=BRANCH, log_dir=logdir, drain_timeout_s=0.2,
                            export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    snaps = []
    real_push = ec._push

    def spy():
        real_push()
        snaps.append({"porcelain": git(clone, "status", "--porcelain"), "head": git(clone, "rev-parse", "HEAD"),
                      "origin": git(bare, "rev-parse", f"refs/heads/{BRANCH}"), "last": ec.events[-1]})
    ec._push = spy
    clock = RC.plan(time.time() + 0.3, round_id=RID, stage="PRODUCTION", epoch_s=1.5, epochs=2, drain_s=1.0,
                    close_s=1.0)
    ec.run_round(clock)

    assert len(snaps) == 3                                              # boundary 1, drain boundary 2, close
    for s in snaps:
        assert s["porcelain"] == "", s["porcelain"]                     # clean after every commit + push
        assert s["last"]["event"] == "pushed", s["last"]                # push rc 0
        assert s["head"] == s["origin"]
    names = [e["event"] for e in ec.events]
    assert "push_failed" not in names and names.count("pushed") == 3
    assert git(clone, "status", "--porcelain") == ""                   # still clean after the final events
    committed = git(clone, "show", f"HEAD:{EP.EPOCHS_REL.as_posix()}/epoch_log.jsonl").splitlines()
    cnames = [json.loads(x)["event"] for x in committed]
    assert "round_closed" in cnames and "round_committed" not in cnames
    outside = [json.loads(x)["event"] for x in ec.log_path.read_text(encoding="utf-8").splitlines()]
    assert outside == names and outside.index("pushed", outside.index("round_committed")) > outside.index(
        "round_committed")
    assert cnames == outside[:len(cnames)]                             # the commit carries a verbatim prefix
    log = git(clone, "log", "--format=%s")
    assert "EPOCH-1" in log and "EPOCH-2" in log and f"ROUND-{RID}" in log
