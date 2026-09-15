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
    kw = dict(gen_seed=3, pressure="train8_held64", families=(4200, 2101), run_seeds=(0, 1), gens=3, batch=8,
              learner_gens=3, learner_batch=8, base_archive=live_url(), learn_archive=live_url(),
              base_elites=str(tmp_path / "b"), learn_elites=str(tmp_path / "l"), prefill_paths=(empty,))
    monkeypatch.setattr(RC.R, "ROWS", {**RC.R.ROWS, "baseline": str(empty)})
    ref = Ctx()
    RC.cell_job(ref, **kw)
    kinds = [x["kind"] for x in ref.rows]
    assert kinds[:2] == ["r16_det", "r16_random"] and kinds[-1] == "r16_cell"
    assert kinds.count("run") == 8 and "floor_suite_r16" in kinds and "baseline_r16" in kinds
    cell = ref.rows[-1]
    assert cell["status_cell"] == "complete" and cell["job_key"] == "g-r16-cell-w3-train8_held64"
    ctx = Ctx(pause_after=3)
    with pytest.raises(RuntimeError):
        RC.cell_job(ctx, **kw)
    ctx.pause_after = None
    RC.cell_job(ctx, **kw)
    vol = ("qd_wall_s", "elites", "wall_s", "oracle_held8", "gate", "ts", "search_cpu_s", "search_wall_s")
    strip = lambda x: {k: v for k, v in x.items() if k not in vol}
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]
