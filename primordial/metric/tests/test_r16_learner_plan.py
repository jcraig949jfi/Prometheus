"""G-R7-3: the 5 PENDING train128 learners -- ascending T/world-only cost, checkpointable chunks under the r7 ceilings."""
from __future__ import annotations

import json
import time

import pytest

from primordial.metric import r16_cells as RC
from primordial.metric import sample as SM
from primordial.tests._live import live_url


def test_order_is_ascending_cost_from_t_and_s_only():
    doc = RC.learner_plan()
    assert [c["gen_seed"] for c in doc["order"]] == [26, 1, 10, 7, 34]          # T*S 64, 128, 128, 256, 256; ties by gen_seed
    for c in doc["order"]:
        assert c["learner128_cpu_s"] == pytest.approx(12030.94 / 32 * RC.ts_of(c["gen_seed"]), abs=0.01)
    assert "T * S" in doc["formula"] and doc["r16_remainder_order_file"] == str(RC.ORDER_FILE)


def test_every_cell_is_eight_chunks_then_one_assembly_under_the_r7_ceilings():
    doc = RC.learner_plan()
    jobs = doc["jobs"]
    assert len(jobs) == 5 * (8 + 1) and len({j["job_key"] for j in jobs}) == len(jobs)
    for n, c in enumerate(doc["order"]):
        block = jobs[n * 9:(n + 1) * 9]
        chunks, asm = block[:8], block[8]
        cover = sorted((j["kwargs"]["rng_family"], rs) for j in chunks for rs in j["kwargs"]["run_seeds"])
        assert cover == sorted((f, rs) for f in RC.R.FAMILIES for rs in RC.R.RUN_SEEDS)      # each run exactly once
        assert all(j["fn"] == RC.LEARNER_CHUNK_FN and j["kwargs"]["gen_seed"] == c["gen_seed"] for j in chunks)
        assert asm["fn"] == RC.FN and asm["job_key"].endswith("-r7") and asm["kwargs"]["cpu_budget_s"] == 36000.0
    for j in jobs:
        env = j["envelope"]
        assert env["checkpointable"] and env["wall_budget_s"] <= 2400 and env["cpu_budget_s"] <= 36000
        assert env["predicate_id"] == "G-R16-SCREEN"
        SM.check_invariant(env)
        assert (env["runs_total"], env["rng_family_count"], env["runs_per_family"]) == (32, 4, 8)
    worst = max(j["estimate_cpu_s"] for j in jobs)
    assert worst == pytest.approx(12030.94 / 32 * 256 * 4 / 32, abs=0.01)                     # w7/w34 chunk
    assert all(j["envelope"]["cpu_budget_s"] >= 2 * j["estimate_cpu_s"] for j in jobs if j["fn"] == RC.LEARNER_CHUNK_FN)


def test_plan_envelopes_pass_envelope_admit_under_a_production_clock():
    """The worker's own admission (EVIDENCE_N_v1 lives inside envelope.admit once H-R7-1 lands)."""
    from primordial.fabric import envelope as EV
    from primordial.ops import round_clock as RCK
    now = time.time()
    clock = RCK.plan(now - 60, round_id="r7")
    if EV.CEILINGS["PRODUCTION"]["cpu_budget_s"] < RC.R7_CPU_CEILING_S:
        pytest.skip("F-R7-5 r7 ceilings (cpu_budget_s 36000) not on this tip yet")
    for j in RC.learner_plan()["jobs"]:
        v = EV.admit(j["envelope"], "cpu", clock={**clock, "stage": "PRODUCTION"}, now=now)
        assert v["ok"], (j["job_key"], v["reasons"])


def test_cell_job_admits_the_learner_on_the_remaining_runs_only():
    gs, p = 7, RC.T128
    st = {"done": {}}
    full = RC.learner128_remaining(st, gs, p)
    assert full["runs_committed"] == 0 and full["remaining_cpu_s"] == pytest.approx(RC.learner128_cost(gs))
    for f in RC.R.FAMILIES:
        for rs in RC.R.RUN_SEEDS:
            if not (f == 5501 and rs >= 4):
                st["done"][RC.I.run_key(gs, p, rs, f)] = {"planted": True}
    part = RC.learner128_remaining(st, gs, p)
    assert part["runs_committed"] == 28 and part["remaining_cpu_s"] == pytest.approx(RC.learner128_cost(gs, runs=4))
    assert part["remaining_cpu_s"] <= RC.R7_CPU_CEILING_S < full["remaining_cpu_s"]


def test_committed_plan_file_reproduces():
    doc = RC.learner_plan()
    committed = json.load(open(RC.LEARNER_PLAN_FILE, encoding="utf-8"))
    assert committed == json.loads(json.dumps(doc))


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for k in c.scan_iter("pm:qd:g-r16-inv-w3-*", count=5000):
        c.delete(k)


def test_learner_chunk_job_smoke_rows_and_resume(r, tmp_path, monkeypatch):
    from primordial.metric.tests.test_r16 import Ctx
    monkeypatch.setattr(RC.I, "PAUSE_EVERY", 2)                 # a 3-generation run polls should_pause at generation 2
    empty = tmp_path / "none.jsonl"
    empty.write_text("")
    kw = dict(gen_seed=3, pressure="train8_held64", rng_family=2101, run_seeds=[0, 1], learner_gens=3, learner_batch=8,
              learn_archive=live_url(), learn_elites=str(tmp_path / "l"), prefill_paths=(empty,))
    ref = Ctx()
    RC.learner_chunk_job(ref, **kw)
    kinds = [x["kind"] for x in ref.rows]
    assert kinds == ["run", "run", "r16_learner_chunk"] and [x["rng_family"] for x in ref.rows[:2]] == [2101, 2101]
    assert "oracle_held8" in ref.rows[0] and ref.rows[-1]["runs"] == 2
    ctx = Ctx(pause_after=1)
    with pytest.raises(RuntimeError):
        RC.learner_chunk_job(ctx, **kw)
    ctx.pause_after = None
    RC.learner_chunk_job(ctx, **kw)
    vol = ("qd_wall_s", "elites", "wall_s", "oracle_held8", "search_cpu_s", "search_wall_s")
    strip = lambda x: {k: v for k, v in x.items() if k not in vol}
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]
