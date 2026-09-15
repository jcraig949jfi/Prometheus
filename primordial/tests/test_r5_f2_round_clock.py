"""F-R5-2: the round clock (launch gate item 7). F14 runs 4 epochs, NO_NEW_WORK and the drain from the
clock alone; after no_new_work_ts the worker refuses every new job with NO_NEW_WORK_REFUSAL and starts none."""
from __future__ import annotations

import subprocess
import threading
import time

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import epoch as EP
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fr2"
RID = "t-r5-2"


def test_r5_plan_is_frozen_o7():
    c = RC.plan(0.0, "r5")
    assert (c["epoch_s"], c["epochs"], c["no_new_work_ts"], c["drain_ts"], c["end_ts"]) == (1500.0, 4, 6000, 6600, 7200)
    assert [RC.phase(c, t)["phase"] for t in (-1, 0, 5999, 6000, 6599, 6600, 7199, 7200)] == [
        "NOT_STARTED", "WORKING", "WORKING", "NO_NEW_WORK", "NO_NEW_WORK", "DRAINING", "DRAINING", "CLOSED"]
    assert [RC.phase(c, t)["epoch"] for t in (0, 1499, 1500, 4500, 5999)] == [1, 1, 2, 4, 4]


def test_no_new_work_admission_rule():
    c = RC.plan(0.0, "r5")
    v = EV.admit(EV.example(wall_budget_s=60), clock=c, now=6000)
    assert v["reasons"] == ["NO_NEW_WORK"] and v["event"] == EV.NO_NEW_WORK_REFUSAL
    assert EV.admit(EV.example(wall_budget_s=60), clock=c, now=5999)["ok"]
    assert EV.admit(EV.example(wall_budget_s=60), clock=c, now=6100, continuation=True)["ok"]   # fits the drain
    assert EV.admit(EV.example(wall_budget_s=600), clock=c, now=6100, continuation=True)["reasons"] == ["NO_NEW_WORK"]


def test_start_is_idempotent_no_extension():
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    r.delete(RC.KEY.format(RID), RC.CURRENT)
    try:
        a = RC.start(r, RID, start_ts=1000.0, **RC.ROUNDS["r5"])
        b = RC.start(r, RID, start_ts=99999.0)
        assert a == b == RC.read(r) and b["end_ts"] == 8200.0
    finally:
        r.delete(RC.KEY.format(RID), RC.CURRENT)


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES, RC.CURRENT, RC.KEY.format(RID), EP.STATE,
            EP.NO_NEW_WORK.format(RID)]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r5-2")
    monkeypatch.setenv("PM_LANE", "F")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def test_round_runs_itself_and_refuses_after_no_new_work(env):
    r, repo = env
    clock = RC.start(r, RID, stage="PILOT", start_ts=time.time() + 0.5, epoch_s=2.5, epochs=4, drain_s=2.5,
                     close_s=2.0)
    worker = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None)
    stop = threading.Event()
    submitted = []

    def feed():
        i = 0
        while not stop.is_set() and time.time() < clock["drain_ts"]:
            W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", f"R5-2-{i}", "rows/r52.jsonl", 10, {"n": 1},
                     r=r, envelope=EV.example(wall_budget_s=1, cpu_budget_s=5))
            submitted.append(time.time())
            i += 1
            time.sleep(0.3)

    done = []
    wt = threading.Thread(target=lambda: done.extend(worker.serve(deadline_s=clock["end_ts"] - time.time() + 1,
                                                                  block_ms=200)))
    ft = threading.Thread(target=feed)
    time.sleep(max(0.0, clock["start_ts"] - time.time()))
    wt.start()
    ft.start()
    ec = EP.EpochController([LANE], r=r, out=repo / "epochs", repo=repo, export=lambda out, stamp, r: (
        out.mkdir(parents=True, exist_ok=True), {})[1], drain_timeout_s=5, post=False, log=lambda *_: None)
    rec = ec.run_round(clock)
    stop.set()
    ft.join()
    worker.exit_requested = True
    wt.join(timeout=30)

    names = [e["event"] for e in ec.events]
    assert names[0] == "round_start" and names[-2:] == ["round_closed", "round_committed"]
    assert names.count("resumed") == 3 and names.count("drain_hold") == 1
    assert names.index("no_new_work") > max(i for i, n in enumerate(names) if n == "resumed")
    assert names.index("no_new_work") < names.index("drain_hold")
    nnw = next(e["ts"] for e in ec.events if e["event"] == "no_new_work")
    assert abs(nnw - clock["no_new_work_ts"]) < 1.0
    ran = [d for d in done if d["status"] == "ok"]
    refused = [d for d in done if d["status"] == "refused"]
    assert ran and refused and any(t >= clock["no_new_work_ts"] for t in submitted)
    # no job admitted after NO_NEW_WORK (started is stamped just after admission, hence the 0.5 s slack)
    assert all(d["started"] < clock["no_new_work_ts"] + 0.5 for d in ran)
    late = [d for d in refused if d["ended"] >= clock["no_new_work_ts"]]
    assert late and all(d["event"] == EV.NO_NEW_WORK_REFUSAL and d["reasons"] == ["NO_NEW_WORK"] for d in late)
    assert len(EV.events(r, EV.NO_NEW_WORK_REFUSAL)) == len(late)
    for n in (1, 2, 3):                                                         # work ran in epochs 1..3
        lo = clock["start_ts"] + (n - 1) * clock["epoch_s"]
        assert any(lo <= d["started"] < lo + clock["epoch_s"] for d in ran), n
    log = subprocess.run(["git", "-C", str(repo), "log", "--format=%s"], capture_output=True, text=True).stdout
    for tag in ("EPOCH-1", "EPOCH-2", "EPOCH-3", "EPOCH-4", f"ROUND-{RID}"):
        assert tag in log, tag
    assert r.hget(EP.STATE, "phase") == "closed" and r.exists(W.STOP.format(LANE))
    assert rec["budget"]["by_cohort"]["F"]["jobs"] == len(done)
