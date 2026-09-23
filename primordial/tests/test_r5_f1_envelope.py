"""F-R5-1: stage admission (launch gate item 1). An over-ceiling job is REFUSED as a normal event --
STAGE_BUDGET_REFUSAL on pm:events + a PRODUCTION_CANDIDATE stub -- never an exception; the worker
survives and runs the next admitted job; the envelope's wall budget kills a job that sleeps past it."""
from __future__ import annotations

import json
import subprocess
import time

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
LANE = "F-r5-1"


# ------------------------------------------------------------------ the table (no Redis)

def test_ceilings_pilot_values():
    assert EV.CEILINGS["PILOT"] == {"cpu_wall_s": 900, "cpu_wall_noncheckpointable_s": 900, "gpu_wall_s": 600,
                                    "cpu_budget_s": 2400}   # operator 20; R7 non-checkpointable key
    for stage in EV.STAGES:
        assert set(EV.CEILINGS[stage]) == {"cpu_wall_s", "cpu_wall_noncheckpointable_s", "gpu_wall_s", "cpu_budget_s"}


@pytest.mark.parametrize("override,kind,reason", [
    ({"wall_budget_s": 901}, "cpu", "CPU_WALL_OVER_CEILING"),
    ({"cpu_budget_s": 2401}, "cpu", "CPU_BUDGET_OVER_CEILING"),   # one over the operator-20 ceiling
    ({"gpu_budget_s": 601}, "gpu", "GPU_WALL_OVER_CEILING"),
    ({"campaign_stage": "PRODUCTION"}, "cpu", "STAGE_NOT_ALLOWED"),
    ({"checkpointable": "yes"}, "cpu", "ENVELOPE_BAD_VALUE:checkpointable"),
    ({"cohort": ""}, "cpu", "ENVELOPE_BAD_VALUE:cohort"),
])
def test_refusal_reasons(override, kind, reason):
    clock = RC.plan(1000.0, "r5")
    v = EV.admit(EV.example(**override), kind=kind, clock=clock, now=1000.0)
    assert not v["ok"] and reason in v["reasons"] and v["event"] == EV.STAGE_BUDGET_REFUSAL


def test_edges_admitted_and_missing_field():
    clock = RC.plan(1000.0, "r5")
    ok = EV.admit(EV.example(wall_budget_s=900, cpu_budget_s=2400), clock=clock, now=1000.0)
    assert ok["ok"] and ok["reasons"] == [] and ok["event"] is None
    assert EV.admit(EV.example(gpu_budget_s=600), kind="gpu", clock=clock, now=1000.0)["ok"]
    env = EV.example()
    del env["predicate_id"]
    v = EV.admit(env, clock=clock, now=1000.0)
    assert v["reasons"] == ["ENVELOPE_MISSING_FIELD:predicate_id"]
    assert EV.admit(None)["reasons"] == ["ENVELOPE_MISSING"]


def test_stage_pins_in_a_pilot_round():
    """A 1789467348712-0: PRODUCTION refused; SMOKE/REPLICATION admitted at PILOT ceilings, never looser;
    an unlisted stage (job or clock) -> STAGE_NOT_ALLOWED."""
    clock = RC.plan(1000.0, "r5")
    assert EV.admit(EV.example(campaign_stage="PRODUCTION"), clock=clock, now=1000.0)["reasons"] == ["STAGE_NOT_ALLOWED"]
    for s in ("SMOKE", "REPLICATION"):
        assert EV.admit(EV.example(campaign_stage=s), clock=clock, now=1000.0)["ok"]
        v = EV.admit(EV.example(campaign_stage=s, wall_budget_s=901), clock=clock, now=1000.0)
        assert v["reasons"] == ["CPU_WALL_OVER_CEILING"] and v["ceiling"] == EV.CEILINGS["PILOT"]
    assert "STAGE_NOT_ALLOWED" in EV.admit(EV.example(campaign_stage="EXPLORATORY"), clock=clock, now=1000.0)["reasons"]
    odd = dict(clock, stage="EXPLORATORY")
    assert EV.admit(EV.example(), clock=odd, now=1000.0)["reasons"] == ["STAGE_NOT_ALLOWED"]


def test_projected_past_round_end():
    clock = RC.plan(0.0, "r5")
    v = EV.admit(EV.example(wall_budget_s=900), clock=clock, now=clock["no_new_work_ts"] - 1)
    assert v["reasons"] == ["PROJECTED_PAST_ROUND_END"]
    late = EV.admit(EV.example(wall_budget_s=700), clock=clock, now=clock["drain_ts"])   # past NNW: one reason
    assert late["reasons"] == ["NO_NEW_WORK"] and late["event"] == EV.NO_NEW_WORK_REFUSAL


def test_horizon_is_drain_ts_not_end_ts():
    """A 1789468596599-0 / operator 19 s14: no job accepted if projected completion exceeds T+110 (drain_ts)."""
    clock = RC.plan(0.0, "r5")                                                     # drain 6600, end 7200
    inside = EV.admit(EV.example(wall_budget_s=800), clock=clock, now=5900)  # completes 6700 in (drain, end]
    assert inside["reasons"] == ["PROJECTED_PAST_ROUND_END"] and inside["event"] == EV.STAGE_BUDGET_REFUSAL
    assert EV.admit(EV.example(wall_budget_s=700), clock=clock, now=5900)["ok"]   # completes exactly at drain_ts


def test_production_stage_outside_a_round_uses_its_own_row():
    """R6 (F-R6-4): PRODUCTION is no longer unbounded; outside a round its own CEILINGS row applies."""
    assert EV.admit(EV.example(campaign_stage="PRODUCTION", checkpointable=True, wall_budget_s=2400,
                               cpu_budget_s=14400))["ok"]   # R7: a 2400 s wall needs checkpointable
    v = EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=10 ** 6, cpu_budget_s=10 ** 6))
    assert set(v["reasons"]) == {"CPU_WALL_OVER_CEILING", "CPU_BUDGET_OVER_CEILING"}


# ------------------------------------------------------------------ the worker (live db)

@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES, RC.CURRENT, RC.KEY.format("t-r5-1")]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r5-1")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def test_worker_refuses_over_ceiling_then_runs_next(env):
    r, repo = env
    RC.start(r, "t-r5-1", stage="PILOT")
    big = EV.example(wall_budget_s=3600, cpu_budget_s=7200, predicate_id="P-big", experiment_class="CLAUSE_A",
                     cohort="B", runs_total=32, rng_family_count=4, runs_per_family=8,       # H-R7-1: EVIDENCE_N_v1
                     families=[4200, 2101, 3303, 5501], n_per_family={"4200": 8, "2101": 8, "3303": 8, "5501": 8})
    W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", "R5-1-big", "rows/big.jsonl", 60, {"n": 2}, r=r,
             envelope=big)
    W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", "R5-1-bare", "rows/bare.jsonl", 60, {"n": 2}, r=r)
    W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", "R5-1-ok", "rows/ok.jsonl", 60, {"n": 2}, r=r,
             envelope=EV.example(cohort="D"))
    done = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=3, block_ms=500)
    assert [d["status"] for d in done] == ["refused", "refused", "ok"]
    assert set(done[0]["reasons"]) == {"CPU_WALL_OVER_CEILING", "CPU_BUDGET_OVER_CEILING"}
    assert done[0]["event"] == EV.STAGE_BUDGET_REFUSAL and done[0]["cohort"] == "B"
    assert done[1]["reasons"] == ["ENVELOPE_MISSING"]          # inside a round an envelope is mandatory
    assert done[2]["rows"] == 2 and done[2]["cohort"] == "D" and done[2]["campaign_stage"] == "PILOT"
    evs = EV.events(r, EV.STAGE_BUDGET_REFUSAL)
    assert [e["exp_id"] for e in evs] == ["R5-1-big", "R5-1-bare"]
    stubs = EV.candidates(r)
    assert stubs[0]["kind"] == "PRODUCTION_CANDIDATE" and stubs[0]["question"] == "P-big"
    assert stubs[0]["requested_cost"]["wall_budget_s"] == 3600
    assert not (repo / "rows" / "big.jsonl").exists() and not (repo / "rows" / "bare.jsonl").exists()
    assert (repo / "rows" / "ok.jsonl").exists()


def test_wall_budget_kills_a_sleeping_job(env):
    r, repo = env
    W.submit(LANE, "primordial.fabric.selftest_jobs:sleep_rows", "R5-1-sleep", "rows/sleep.jsonl", 60,
             {"s": 30}, r=r, envelope=EV.example(wall_budget_s=4))
    t = time.monotonic()
    done = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=1, block_ms=500)
    assert time.monotonic() - t < 25
    assert done[0]["status"] == "timeout" and done[0]["limit"] == "wall"
    rows = [json.loads(x) for x in (repo / "rows" / "sleep.jsonl").read_text(encoding="utf-8").splitlines()]
    assert rows[-1]["status"] == "timeout" and rows[-1]["limit"] == "wall" and rows[-1]["wall_budget_s"] == 4
    assert [e["job_id"] for e in EV.events(r, "TIMEOUT")] == [done[0]["job_id"]]
