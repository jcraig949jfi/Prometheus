"""G-R6-2: R16 resume as per-cell jobs -- seeded order, prefill from committed rows, PENDING learner, UNSCREENED."""
from __future__ import annotations

import json

import numpy as np
import pytest

from primordial.metric import r16_cells as RC
from primordial.metric import screen as SC
from primordial.metric import worlds as WR
from primordial.metric.tests.test_r16 import Ctx
from primordial.tests._live import live_url


def test_order_is_pcg64_20260916_over_the_sorted_unscreened_cells():
    doc = RC.build_order()
    assert doc["seed"] == 20260916 and doc["counts"]["cells"] == 74
    uns = [tuple(c) for c in doc["unscreened_sorted"]]
    assert uns == sorted(uns) and doc["counts"]["unscreened"] == len(uns) == 68
    perm = np.random.Generator(np.random.PCG64(20260916)).permutation(len(uns))
    assert doc["order"] == [list(uns[i]) for i in perm] and sorted(map(tuple, doc["order"])) == uns
    rem = [tuple(c) for c in doc["floor_remainder"]]
    assert rem == sorted([(1, "train128_held64"), (1, "train8_held64"), (7, "train128_held64"), (7, "train8_held64"),
                          (26, "train128_held64")])
    assert doc["complete"] == [[13, "train128_held64"]]
    assert not set(rem) & set(uns)


def test_order_file_is_never_regenerated_with_different_content(tmp_path):
    doc = RC.build_order()
    p = RC.write_order(doc, tmp_path / "o.json")
    assert RC.write_order(doc, p) == p                                   # same content: idempotent
    other = dict(doc, seed=1, order=list(reversed(doc["order"])))
    with pytest.raises(ValueError):
        RC.write_order(other, p)


def test_estimates_and_learner128_admission_boundary():
    w13 = RC.estimates(13, "train128_held64")
    assert w13["t_x_s"] == 32 and w13["learner128_admissible"]                           # J3 itself: 12,031 CPU-s
    assert abs(w13["learner128_cpu_s"] - 12030.94) < 1
    w7 = RC.estimates(7, "train128_held64")
    assert w7["t_x_s"] == 256 and not w7["learner128_admissible"]                        # ~96,000 CPU-s -> PENDING + PC
    assert RC.estimates(4, "train8_held64")["learner128_cpu_s"] == 0.0


def test_prefill_reuses_committed_runs_under_their_run_keys():
    st = {"done": {}}
    n = RC.prefill_done(st, 34, "train128_held64")
    assert n == 15 and all(k.startswith("g-r16-base-w34-train128_held64-f") for k in st["done"])
    st7 = {"done": {}}
    n7 = RC.prefill_done(st7, 7, "train8_held64")
    inv = [k for k in st7["done"] if k.startswith("g-r16-inv-w7-train8_held64-f")]      # J1's train8 learner runs
    base = [k for k in st7["done"] if k.startswith("g-r16-base-w7-train8_held64-f")]    # J2 finished w7 train8's baseline
    assert len(inv) == 26 and len(base) == 32 and n7 == len(inv) + len(base) == len(st7["done"])
    assert RC.prefill_done({"done": {}}, 7, "train128_held64") == 32                      # w7 t128 baseline done


def test_plan_puts_the_floor_remainder_first_and_uses_production_envelopes():
    doc = RC.build_order()
    plan = RC.plan_jobs(doc)
    assert len(plan) == 68 + 5 and [p["kwargs"]["gen_seed"] for p in plan[:5]] == [c[0] for c in doc["floor_remainder"]]
    assert [ [p["kwargs"]["gen_seed"], p["kwargs"]["pressure"]] for p in plan[5:]] == doc["order"]
    env = plan[0]["envelope"]
    assert env["campaign_stage"] == "PRODUCTION" and env["checkpointable"] and env["cpu_budget_s"] <= 14400
    assert len({p["job_key"] for p in plan}) == len(plan)


def test_partial_v2_marks_unfinished_cells_unscreened_never_culled():
    doc = RC.partial_v2()
    by = {(c["gen_seed"], c["pressure"]): c for c in doc["cells"]}
    assert len(by) == 74 and doc["coverage"] == {"cells": 74, "complete": 1, "unscreened": 73}
    assert by[(13, "train128_held64")]["verdicts"]["gate_in|HOLD"]["verdict"] == "SURVIVED"
    for key, c in by.items():
        if key != (13, "train128_held64"):
            assert {v["verdict"] for v in c["verdicts"].values()} == {"UNSCREENED"}
            assert c["cull_reason"] is None and c.get("verdict") != "CULLED"
    assert WR.guard(doc, "w7", "train8_held64")["why"] == "UNSCREENED"
    assert WR.guard(doc, "w13", "train128_held64") is None


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for pat in ("pm:qd:g-r16-*",):
        for k in c.scan_iter(pat, count=5000):
            c.delete(k)


def test_cell_job_smoke_tiny_budget_rows_and_resume(r, tmp_path, monkeypatch):
    """A 1-cell smoke at a tiny budget on w3 train8 (no committed R16 rows for w3: nothing prefilled)."""
    from primordial.metric import baseline as B
    from primordial.metric import invariant as I
    monkeypatch.setattr(B, "PAUSE_EVERY", 2)
    monkeypatch.setattr(I, "PAUSE_EVERY", 2)
    empty = tmp_path / "none.jsonl"
    import redis as _redis
    from primordial.metric import replication as RP
    pub = _redis.Redis.from_url(live_url(), decode_responses=True)       # the worker Ctx has .r; the test Ctx does not
    monkeypatch.setattr(RP, "STREAM", "pm:test:g-r6-smoke-repl")         # never the real replication stream
    monkeypatch.setattr(RP, "PUBLISHED", "pm:test:g-r6-smoke-repl:published:{}|{}")
    monkeypatch.setattr(RC, "EVENTS", "pm:test:g-r6-smoke-events")
    kw = dict(gen_seed=3, pressure="train8_held64", families=(4200, 2101), run_seeds=(0, 1), gens=3, batch=8,
              learner_gens=3, learner_batch=8, base_archive=live_url(), learn_archive=live_url(),
              base_elites=str(tmp_path / "b"), learn_elites=str(tmp_path / "l"), prefill_paths=(empty,),
              replication_r=pub)
    monkeypatch.setattr(RC.R, "ROWS", {**RC.R.ROWS, "baseline": str(empty)})
    ref = Ctx()
    RC.cell_job(ref, **kw)
    kinds = [x["kind"] for x in ref.rows]
    assert kinds[:2] == ["r16_det", "r16_random"] and kinds[-2:] == ["r16_cell", "replication_check"]   # G-R6-3: trigger last
    assert kinds.count("run") == 8 and "floor_suite_r16" in kinds and "baseline_r16" in kinds
    cell = ref.rows[-2]
    assert ref.rows[-1]["published"] == [] and ref.rows[-1]["refused"] is None        # only the origin w13 t128 survives
    assert cell["status_cell"] == "complete" and cell["job_key"] == "g-r16-cell-w3-train8_held64"
    ctx = Ctx(pause_after=3)
    with pytest.raises(RuntimeError):
        RC.cell_job(ctx, **kw)
    ctx.pause_after = None
    RC.cell_job(ctx, **kw)
    vol = ("qd_wall_s", "elites", "wall_s", "oracle_held8", "gate", "ts", "search_cpu_s", "search_wall_s")
    strip = lambda x: {k: v for k, v in x.items() if k not in vol}
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]


# ---------------------------------------------------------------- G-R6-3 wiring: cell_job calls the replication trigger

@pytest.fixture
def rs(monkeypatch):
    """A decode_responses client with the replication and event streams moved to test keys."""
    redis = pytest.importorskip("redis")
    from primordial.metric import replication as RP
    c = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    monkeypatch.setattr(RP, "STREAM", "pm:test:g-r6-repl")
    monkeypatch.setattr(RP, "PUBLISHED", "pm:test:g-r6-repl:published:{}|{}")
    monkeypatch.setattr(RC, "EVENTS", "pm:test:g-r6-events")
    keys = lambda: list(c.scan_iter("pm:test:g-r6-*", count=1000)) + list(c.scan_iter("pm:qd:g-r16-*", count=5000))
    for k in keys():
        c.delete(k)
    yield c
    for k in keys():
        c.delete(k)


def _smoke_kw(tmp_path, rs):
    empty = tmp_path / "none.jsonl"
    return dict(gen_seed=3, pressure="train8_held64", families=(4200, 2101), run_seeds=(0, 1), gens=3, batch=8,
                learner_gens=3, learner_batch=8, base_archive=live_url(), learn_archive=live_url(),
                base_elites=str(tmp_path / "b"), learn_elites=str(tmp_path / "l"), prefill_paths=(empty,),
                replication_r=rs), empty


def test_cell_job_publishes_a_planted_survivor_exactly_once_and_a_rerun_publishes_none(rs, tmp_path, monkeypatch):
    from primordial.metric import replication as RP
    kw, empty = _smoke_kw(tmp_path, rs)
    monkeypatch.setattr(RC.R, "ROWS", {**RC.R.ROWS, "baseline": str(empty)})
    seen = {}
    real = RC.partial_v2

    def planted(**k):
        seen["extra_kinds"] = sorted(x.get("kind") for x in k.get("extra_rows", ()))
        doc = real(**k)
        for c in doc["cells"]:
            if (c["gen_seed"], c["pressure"]) == (4, "train8_held64"):                 # the planted new survivor
                c["verdicts"] = {SC.vkey(*v): {"verdict": "SURVIVED", "cull_reason": None, "floor": 1.0} for v in SC.VARIANTS}
        return doc
    monkeypatch.setattr(RC, "partial_v2", planted)
    first = Ctx()
    RC.cell_job(first, **kw)
    assert seen["extra_kinds"] == ["baseline_r16", "floor_suite_r16"]                      # the job's own rows are in the doc
    chk = [x for x in first.rows if x["kind"] == "replication_check"]
    assert len(chk) == 1 and chk[0]["published"] == [{"world": "w4", "pressure": "train8_held64", "gen_seed": 4}]
    assert first.rows[-1]["kind"] == "replication_check"                                  # the last step of the job
    recs = RP.records(rs)
    assert len(recs) == 1 and recs[0]["source"] == "r16_cell_job" and recs[0]["recipe"]["id"] == "B-R5-1"
    again = Ctx()
    RC.cell_job(again, **kw)
    chk2 = [x for x in again.rows if x["kind"] == "replication_check"]
    assert len(chk2) == 1 and chk2[0]["published"] == [] and len(RP.records(rs)) == 1        # rerun: nothing new


def test_cell_job_refuses_to_publish_when_the_recipe_code_changed(rs, tmp_path, monkeypatch):
    from primordial.metric import replication as RP
    kw, empty = _smoke_kw(tmp_path, rs)
    monkeypatch.setattr(RC.R, "ROWS", {**RC.R.ROWS, "baseline": str(empty)})
    monkeypatch.setattr(RP, "frozen_code_intact", lambda root=None: False)

    def planted(**k):
        doc = RC.WR.build([], commit="", max_survivors=None, schema=RC.WR.SCHEMA_V2)
        doc["cells"] = [{"world": "w4", "pressure": "train8_held64", "gen_seed": 4,
                         "verdicts": {SC.vkey(*v): {"verdict": "SURVIVED"} for v in SC.VARIANTS}}]
        return doc
    monkeypatch.setattr(RC, "partial_v2", planted)
    ctx = Ctx()
    RC.cell_job(ctx, **kw)
    chk = [x for x in ctx.rows if x["kind"] == "replication_check"][0]
    assert chk["refused"] == RC.RECIPE_CHANGED and chk["published"] == []
    assert RP.records(rs) == []
    ev = rs.xrange("pm:test:g-r6-events")
    assert len(ev) == 1 and ev[0][1]["event"] == "REPLICATION_RECIPE_CHANGED"
    assert json.loads(ev[0][1]["json"])["frozen_code_sha"] == "c2e9b5ec3"


def test_partial_v2_merges_extra_rows_over_committed_rows():
    doc = RC.partial_v2()
    assert doc["coverage"]["complete"] == 1
    fl = [x for x in RC.R._rows(RC.R.ROWS["floors"]) if x.get("kind") == "floor_suite_r16" and x["gen_seed"] == 13
          and x["pressure"] == "train128_held64"][-1]
    base = {**[x for x in RC.R._rows(RC.R.ROWS["baseline"]) if x.get("kind") == "baseline_r16" and x["gen_seed"] == 13][-1]}
    planted_fl = {**fl, "gen_seed": 99, "world": "w99"}
    planted_base = {**base, "gen_seed": 99, "world": "w99"}
    with_extra = RC.partial_v2(extra_rows=[planted_fl, planted_base])                      # w99 is not a stage 1 cell
    assert with_extra["coverage"] == doc["coverage"]                                        # only stage 1 cells are listed


def test_every_plan_envelope_is_admitted_by_the_worker_rules_under_a_production_clock():
    """R6 11:01: predicate_id None made the worker refuse all 73 submits; the plan must pass envelope.admit itself."""
    import time
    from primordial.fabric import envelope as EV
    from primordial.ops import round_clock as RCK
    now = time.time()
    clock = RCK.plan(now - 60, round_id="r6")                 # the r6 clock record exactly as round_clock writes it
    assert clock["stage"] == "PRODUCTION" and RCK.phase(clock, now)["phase"] != "NO_ROUND"
    for p in RC.plan_jobs(RC.build_order()):
        env = p["envelope"]
        assert EV.validate(env) == [], (p["job_key"], EV.validate(env))
        v = EV.admit(env, "cpu", clock=clock, now=now)
        assert v["ok"], (p["job_key"], v["reasons"])
        assert EV.admit(env, "cpu", clock=None, now=now)["ok"]
    assert all(p["envelope"]["predicate_id"] == RC.PREDICATE_ID for p in RC.plan_jobs(RC.build_order()))
