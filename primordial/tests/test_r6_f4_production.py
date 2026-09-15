"""F-R6-4: PRODUCTION round-scoped ceilings in the ONE envelope.CEILINGS table (SWARM_R6 s2, operator 22).
Segment wall 2400 s, cpu_budget_s 14400 (cumulative), gpu 600, completion <= drain_ts; a checkpointable job
continues by segment and reproduces an unsegmented run exactly; no module holds a copy of the table."""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import time

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fr6seg"
ROOT = pathlib.Path(__file__).resolve().parents[2]
VOLATILE = ("ts", "job_id", "exp_id", "segment")


def prod_clock(start=0.0):
    return RC.plan(start, "t-r6", stage="PRODUCTION", epoch_s=2400, epochs=5, drain_s=1200, close_s=1200)


def test_production_row():
    assert EV.CEILINGS["PRODUCTION"] == {"cpu_wall_s": 2400, "gpu_wall_s": 600, "cpu_budget_s": 14400}
    assert EV.CEILINGS["REPLICATION"] == EV.CEILINGS["PRODUCTION"]


@pytest.mark.parametrize("override,kind,reason", [
    ({"wall_budget_s": 2401}, "cpu", "CPU_WALL_OVER_CEILING"),
    ({"cpu_budget_s": 14401}, "cpu", "CPU_BUDGET_OVER_CEILING"),
    ({"gpu_budget_s": 601}, "gpu", "GPU_WALL_OVER_CEILING"),
])
def test_production_refusals(override, kind, reason):
    v = EV.admit(EV.example(campaign_stage="PRODUCTION", **override), kind=kind, clock=prod_clock(), now=0.0)
    assert v["reasons"] == [reason]


def test_production_edges_and_drain_horizon():
    c = prod_clock()
    assert EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=2400, cpu_budget_s=14400), clock=c, now=0)["ok"]
    assert EV.admit(EV.example(campaign_stage="PILOT"), clock=c, now=0)["ok"]           # a PRODUCTION round admits all
    late = EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=2400), clock=c, now=c["drain_ts"] - 2399)
    assert late["reasons"] == ["NO_NEW_WORK"] or late["reasons"] == ["PROJECTED_PAST_ROUND_END"]
    pre = EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=2400), clock=c, now=c["no_new_work_ts"] - 1)
    assert pre["reasons"] == ["PROJECTED_PAST_ROUND_END"]


def test_no_copy_of_the_ceiling_table():
    pat = re.compile(r"""["'](cpu_wall_s|gpu_wall_s|cpu_budget_s)["']\s*:\s*\d""")
    hits = [str(p.relative_to(ROOT)) for p in (ROOT / "primordial").rglob("*.py")
            if "tests" not in p.parts and p.name != "envelope.py" and pat.search(p.read_text(encoding="utf-8",
                                                                                            errors="replace"))]
    assert hits == []


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), W.RESUMABLE, EV.EVENTS, EV.CANDIDATES, RC.CURRENT, RC.KEY.format("t-r6-seg")]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r6-4")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def stable(path):
    return [{k: v for k, v in json.loads(x).items() if k not in VOLATILE}
            for x in path.read_text(encoding="utf-8").splitlines() if json.loads(x).get("kind") == "walk"]


def test_checkpointable_job_continues_by_segment(env):
    r, repo = env
    RC.start(r, "t-r6-seg", start_ts=time.time(), stage="PRODUCTION", epoch_s=600, epochs=2, drain_s=300,
             close_s=300)
    kw = {"steps": 50, "seed": 3, "step_s": 0.05}
    base = dict(campaign_stage="PRODUCTION", checkpointable=True, cpu_budget_s=120, expected_output_rows=50)
    W.submit(LANE, "primordial.fabric.selftest_jobs:walk", "seg-ref", "rows/ref.jsonl", 120, kw, r=r,
             envelope=EV.example(wall_budget_s=60, **base))
    W.submit(LANE, "primordial.fabric.selftest_jobs:walk", "seg-cut", "rows/cut.jsonl", 120, kw, r=r,
             envelope=EV.example(wall_budget_s=1, **base), job_key="seg-cut")
    w = W.Worker(LANE, url=URL, repo=repo, ckpt_dir=repo / "ck", log=lambda *_: None, broker=False)
    done = w.serve(block_ms=300, idle_exit_s=3, deadline_s=90)
    cut = [d for d in done if d["job_key"] == "seg-cut"]
    assert [d["status"] for d in cut][-1] == "ok" and len(cut) >= 2
    assert all(d["status"] == "paused" for d in cut[:-1]) and [d["segment"] for d in cut] == list(range(len(cut)))
    assert all(d["wall_s"] < 1 + 5 for d in cut)                            # paused at the segment wall, not killed
    assert stable(repo / "rows" / "cut.jsonl") == stable(repo / "rows" / "ref.jsonl") and len(stable(repo / "rows" / "ref.jsonl")) == 50
