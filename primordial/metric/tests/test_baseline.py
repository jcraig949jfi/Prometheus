"""M2 / G-R4-3 stage 2: the float linear baseline is E9/E10's search, seeded, at round 1's budget, resumable."""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pytest

from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.metric.ci import median_ci
from primordial.metric.tests.test_invariant import FakeCtx
from primordial.qd import e7_run as E7
from primordial.tests._live import live_url

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _rows(name):
    p = ROOT / "primordial" / "ledger" / "rows" / "E" / f"{name}.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_budget_is_round1_linear_budget_from_committed_rows():
    e9 = {x["genomes"] for x in _rows("E9-family-ranking-fused-8-seeds") if x.get("tag") == "full" and x["family"] == "linear"}
    e10 = {x["closed_genomes"] for x in _rows("E10-linear-closed-vs-open-128-seeds") if x.get("tag") == "full"}
    assert e9 == {np.prod(B.BUDGET["train8_held64"])}
    assert e10 == {np.prod(B.BUDGET["train128_held64"])}


def test_fused_score_equals_numpy_rollout_and_oracles_clean():
    g7 = E7.G7(4, B.FAM)
    g = g7.init(np.random.Generator(np.random.PCG64(11)), 4)
    raw = g7.pack(g)
    seeds = F.HELD64[:3]
    want = float(E7.rollout(g7, g7.unpack(raw), seeds)[0].mean() / len(seeds))
    assert B.fused_per_seed(g7, raw, seeds) == pytest.approx(want, abs=0)
    o = B.oracle_top(4, raw, F.HELD64[:2])
    assert o["fused_eq_numpy"] and o["world"]["elites_failing"] == 0 and o["brain"]["mismatched_rows"] == 0


def test_top_raw_orders_by_fitness_then_genome_bytes():
    el = [(5, b"\x02\x00\x00\x00"), (7, b"\x09\x00\x00\x00"), (5, b"\x01\x00\x00\x00")]
    assert B.top_raw(el, 4, n=2).tobytes() == b"\x09\x00\x00\x00\x01\x00\x00\x00"


def test_summary_median_ci_bytes_and_min_runs():
    runs = [{"run_seed": i, "held64_per_seed": float(v), "genome_bytes": 312, "budget_ok": True, "genomes": 1,
             "world": "w4", "gen_seed": 4, "pressure": "p", "elites": f"e{i}"}
            for i, v in enumerate([90, 91, 85, 101, 100, 89, 93, 88])]
    s = B.summary(runs)
    v = [90, 91, 85, 101, 100, 89, 93, 88]
    assert s["median"] == float(np.median(v)) and s["ci95"] == list(median_ci(v)) and s["bytes"] == 312
    assert s["held64_by_run_seed"]["3"] == 101.0 and s["n_runs"] == 8
    with pytest.raises(ValueError):
        B.summary(runs[:7])


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for k in c.scan_iter("pm:qd:g-r4-base-*", count=5000):
        c.delete(k)


def test_run_is_replayable_and_pause_resume_equals_uninterrupted(r, tmp_path, monkeypatch):
    a = B.baseline_run(r, 4, "train8_held64", 0, gens=4, batch=8, elites_dir=tmp_path / "a")
    b = B.baseline_run(r, 4, "train8_held64", 0, gens=4, batch=8, elites_dir=tmp_path / "b")
    assert a["top_sha256"] == b["top_sha256"] and a["held64_per_seed"] == b["held64_per_seed"]
    assert pathlib.Path(a["elites"]).read_bytes() == pathlib.Path(b["elites"]).read_bytes()
    assert a["genome_bytes"] == E7.G7(4, "linear").glen and not a["budget_ok"]
    monkeypatch.setattr(B, "PAUSE_EVERY", 2)
    first = B.baseline_run(r, 4, "train8_held64", 0, gens=4, batch=8, elites_dir=tmp_path / "p",
                           should_pause=lambda: True)
    assert first["paused"]["gen"] == 2
    rest = B.baseline_run(r, 4, "train8_held64", 0, gens=4, batch=8, elites_dir=tmp_path / "p", state=first["paused"])
    assert rest["top_sha256"] == a["top_sha256"]
    assert pathlib.Path(rest["elites"]).read_bytes() == pathlib.Path(a["elites"]).read_bytes()


def test_job_rows_and_resume(r, tmp_path, monkeypatch):
    monkeypatch.setattr(B, "PAUSE_EVERY", 2)
    kw = dict(cells=[[3, "train8_held64"]], gens=3, batch=8, archive_url=live_url(), elites_dir=str(tmp_path))
    ref = FakeCtx()
    B.job(ref, **kw)
    assert [x["kind"] for x in ref.rows] == ["run"] * 8 + ["baseline"]
    assert ref.rows[0]["oracle_held8"]["world"]["elites_failing"] == 0
    ctx = FakeCtx(pause_after=3)
    with pytest.raises(RuntimeError):
        B.job(ctx, **kw)
    ctx.pause_after = None
    B.job(ctx, **kw)

    def strip(x):
        x = {k: v for k, v in x.items() if k not in ("qd_wall_s", "elites")}
        return x
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]


def test_m2_run_value_is_the_shared_reader_over_its_own_saved_elites(r, tmp_path):
    """R15-1: the baseline assembly and a candidate re-read go through one function (readout.read)."""
    from primordial.metric import readout as RO
    row = B.baseline_run(r, 4, "train8_held64", 0, gens=3, batch=16, elites_dir=tmp_path)
    again = B.reread(4, row["elites"])
    assert row["readout"] == again["readout"] == RO.NAME and row["top"] == 1
    assert row["held64_per_seed"] == again["held64_per_seed"] and row["top_sha256"] == again["top_sha256"]
