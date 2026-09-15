"""G-R4-3 stage 2 driver: gate-headroom order, learner only where cleared, stop at exact survivors."""
from __future__ import annotations

import json

import pytest

from primordial.metric import baseline as B
from primordial.metric import invariant as I
from primordial.metric import stage2 as S2
from primordial.metric.tests.test_invariant import FakeCtx

S8, S128 = "train8_held64", "train128_held64"


def suite_row(gs, p, floor, gate, learner=True):
    return {"kind": "floor_suite", "world": f"w{gs}", "gen_seed": gs, "pressure": p,
            "floor_parts": {"abstain": floor, "best_constant": floor, "uniform_random_median": 0.0,
                            "input_invariant_learner": floor - 10 if learner else None},
            "floor": floor, "gate_held64": gate, "learner": {"status": "run" if learner else "not_run"}}


@pytest.fixture
def fake(tmp_path, monkeypatch):
    """Stage 1 rows on disk; baseline/learner replaced by planted per-cell values (no Redis, no worlds)."""
    rows = [suite_row(1, S8, 100.0, 150.0), suite_row(1, S128, 100.0, 150.0, learner=False),
            suite_row(2, S8, 100.0, 120.0), suite_row(3, S8, 100.0, 100.0), suite_row(4, S8, 100.0, 90.0)]
    path = tmp_path / "stage1.jsonl"
    path.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    medians = {(1, S8): 200.0, (1, S128): 200.0, (2, S8): 200.0, (3, S8): 50.0, (4, S8): 200.0}
    calls = {"base": [], "learn": []}

    def base_cell(ctx, st, r, gs, p, run_seeds, *a, **k):
        calls["base"].append((gs, p))
        m = medians[(gs, p)]
        return [{"run_seed": i, "held64_per_seed": m + (i - 3.5), "genome_bytes": 312, "budget_ok": True,
                 "genomes": 1, "world": f"w{gs}", "gen_seed": gs, "pressure": p, "elites": ""} for i in run_seeds]

    def learn_cell(ctx, st, r, gs, p, run_seeds, *a, **k):
        calls["learn"].append((gs, p))
        return [{"run_seed": i, "held64_per_seed": 120.0, "budget_ok": True, "genomes": 1, "world": f"w{gs}",
                 "gen_seed": gs, "pressure": p} for i in run_seeds]

    monkeypatch.setattr(B, "baseline_cell", base_cell)
    monkeypatch.setattr(I, "learner_cell", learn_cell)
    return str(path), calls


def cells(ctx):
    return [(x["gen_seed"], x["pressure"], x["active"], x["pending"]) for x in ctx.rows if x["kind"] == "stage2_cell"]


def test_order_is_gate_headroom_then_seed_then_pressure(fake):
    path, _ = fake
    assert S2.order(S2.load_suite(path)) == [(1, S8), (1, S128), (2, S8), (3, S8), (4, S8)]


def test_pending_without_clearance_and_learner_when_cleared(fake):
    path, calls = fake
    ctx = FakeCtx()
    S2.job(ctx, path, learner_train128=(), archive_url="redis://127.0.0.1:1/0")
    got = cells(ctx)
    # w1 train128: bound 100, gate 150 > bound -> PENDING, not counted, learner not run
    assert (1, S128, "PENDING_LEARNER", True) in got and calls["learn"] == []
    assert (3, S8, "CULLED", False) in got and (2, S8, "SURVIVED", False) in got
    ctx2 = FakeCtx()
    S2.job(ctx2, path, learner_train128=[1], archive_url="redis://127.0.0.1:1/0")
    assert calls["learn"] == [(1, S128)]
    w1 = [c for c in cells(ctx2) if c[:2] == (1, S128)][0]
    assert w1[3] is False and w1[2] == "SURVIVED"                # floor 120 < gate 150 < CI low: exact survivor


def test_stops_at_exact_survivors_and_resumes_without_redoing_cells(fake):
    path, calls = fake
    ctx = FakeCtx()
    S2.job(ctx, path, learner_train128=[1], max_survivors=2, archive_url="redis://127.0.0.1:1/0")
    assert [c[:2] for c in cells(ctx)] == [(1, S8), (1, S128)]
    stop = [x for x in ctx.rows if x["kind"] == "stage2_stop"]
    assert stop and stop[0]["next_cell"] == [2, S8] and stop[0]["survivors"] == 2
    assert calls["base"] == [(1, S8), (1, S128)]

    ctx.ck = None
    ctx2 = FakeCtx()
    ctx2.checkpoint = lambda st: setattr(ctx2, "ck", __import__("pickle").loads(__import__("pickle").dumps(st)))
    S2.job(ctx2, path, learner_train128=[1], max_survivors=5, archive_url="redis://127.0.0.1:1/0")
    n = len(calls["base"])
    S2.job(ctx2, path, learner_train128=[1], max_survivors=5, archive_url="redis://127.0.0.1:1/0")
    assert len(calls["base"]) == n                                # every cell is in the checkpoint: nothing redone
