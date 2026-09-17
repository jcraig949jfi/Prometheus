"""G-R7-2: the R16 cell_job baseline-stage backend (cpu_sequential | cpu_lockstep | gpu_lockstep), fixed at job start
from pm:r7:backend / pm:r7:gpu_adopt; the cpu_sequential path is unchanged byte for byte; rows stamp the backend."""
from __future__ import annotations

import hashlib
import json

import pytest

from primordial.metric import baseline as B
from primordial.metric import r16_cells as RC
from primordial.metric.tests.test_r16 import Ctx
from primordial.metric.tests.test_r16_cells import _smoke_kw, rs  # noqa: F401  (rs is a fixture)
from primordial.tests._live import live_url

# baseline_run rows on w3 train8 (gens 3, batch 8) computed at 139389a2d BEFORE the _run_row refactor
GOLDEN = {"4200|0": "0b33d6cdc3e2dd6a1178e117def692322219c85df0e853a3350266b577617aae",
          "2101|1": "5950a30f5c18089a5e7c3a61e1511e361fd11bf6e542fe8f24467d5b1603fa3a"}
VOL = ("qd_wall_s", "elites", "search_cpu_s", "search_wall_s")


def _strip(row, extra=()):
    out = {k: v for k, v in row.items() if k not in VOL + tuple(extra)}
    if isinstance(out.get("oracle_held8"), dict):
        o = dict(out["oracle_held8"])
        if isinstance(o.get("world"), dict):
            o["world"] = {k: v for k, v in o["world"].items() if k != "wforge_episodes_per_s"}
        o.pop("wforge_episodes_per_s", None)
        out["oracle_held8"] = o
    return out


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for k in c.scan_iter("pm:qd:g-r16-base-w3-*", count=5000):
        c.delete(k)


def test_baseline_run_rows_are_byte_identical_after_the_row_refactor(r, tmp_path):
    for (fam, run_seed), want in zip(((4200, 0), (2101, 1)), GOLDEN.values()):
        row = B.baseline_run(r, 3, "train8_held64", run_seed, gens=3, batch=8, elites_dir=tmp_path, rng_family=fam)
        got = hashlib.sha256(json.dumps(_strip(row), sort_keys=True).encode()).hexdigest()
        assert got == want, (fam, run_seed)


def test_cpu_lockstep_rows_equal_the_sequential_rows(r, tmp_path):
    kw = dict(run_seeds=[0, 1], gens=3, batch=8, families=[4200, 2101])
    seq = B.baseline_cell(Ctx(), {"done": {}, "cur": None}, r, 3, "train8_held64", kw["run_seeds"], kw["gens"],
                          kw["batch"], str(tmp_path / "s"), families=kw["families"])
    lock_ctx = Ctx()
    lock = B.baseline_cell_lockstep(lock_ctx, {"done": {}, "cur": None}, r, 3, "train8_held64", kw["run_seeds"],
                                    kw["gens"], kw["batch"], str(tmp_path / "l"), families=kw["families"],
                                    evaluator=RC.evaluator_for("cpu_lockstep"), backend="cpu_lockstep")
    assert len(seq) == len(lock) == 4
    assert [_strip(x) for x in seq] == [_strip(x, extra=("backend",)) for x in lock]
    assert all(x["backend"] == "cpu_lockstep" for x in lock) and all("backend" not in x for x in seq)
    assert [x["kind"] for x in lock_ctx.rows] == ["run"] * 4 and "oracle_held8" in lock_ctx.rows[0]


def test_lockstep_pause_and_resume_equal_an_uninterrupted_stage(r, tmp_path, monkeypatch):
    monkeypatch.setattr(B, "PAUSE_EVERY", 2)
    args = (3, "train8_held64", [0, 1], 5, 8)
    ev = RC.evaluator_for("cpu_lockstep")
    ref = Ctx()
    B.baseline_cell_lockstep(ref, {"done": {}, "cur": None}, r, *args, str(tmp_path / "a"), families=[4200, 2101], evaluator=ev)
    ctx = Ctx(pause_after=1)
    st = {"done": {}, "cur": None}
    with pytest.raises(RuntimeError):
        B.baseline_cell_lockstep(ctx, st, r, *args, str(tmp_path / "b"), families=[4200, 2101], evaluator=ev)
    assert ctx.ck["lock"]["gen"] == 2
    ctx.pause_after = None
    B.baseline_cell_lockstep(ctx, ctx.ck, r, *args, str(tmp_path / "b"), families=[4200, 2101], evaluator=ev)
    assert [_strip(x) for x in ctx.rows] == [_strip(x) for x in ref.rows]


class FakeR:
    def __init__(self, **kv):
        self.kv = kv

    def get(self, k):
        return self.kv.get(k)


def test_resolve_backend_is_fixed_by_the_code_decision_and_falls_back_to_cpu_sequential():
    adopt = json.dumps({"decision": "GPU_ADOPT"})
    reject = json.dumps({"decision": "GPU_REJECT"})
    assert RC.resolve_backend(None, FakeR()) == {"backend": "cpu_sequential", "source": "DEFAULT"}
    assert RC.resolve_backend(None, FakeR(**{RC.BACKEND_KEY: "cpu_lockstep"}))["backend"] == "cpu_lockstep"
    assert RC.resolve_backend(None, FakeR(**{RC.BACKEND_KEY: json.dumps({"backend": "cpu_lockstep"})}))["backend"] == "cpu_lockstep"
    gpu_rej = RC.resolve_backend(None, FakeR(**{RC.BACKEND_KEY: "gpu_lockstep", RC.GPU_ADOPT_KEY: reject}))
    assert gpu_rej["backend"] == "cpu_sequential" and gpu_rej["source"].startswith("GPU_NOT_ADOPTED")
    gpu_ok = RC.resolve_backend(None, FakeR(**{RC.BACKEND_KEY: "gpu_lockstep", RC.GPU_ADOPT_KEY: adopt}))
    assert gpu_ok == {"backend": "gpu_lockstep", "source": RC.BACKEND_KEY}
    assert RC.resolve_backend("gpu_lockstep", FakeR())["backend"] == "cpu_sequential"      # a kwarg cannot skip adoption
    assert RC.resolve_backend(None, FakeR(**{RC.BACKEND_KEY: "fpga"}))["source"] == "INVALID:fpga"
    assert RC.resolve_backend("cpu_sequential", FakeR(**{RC.BACKEND_KEY: "cpu_lockstep"}))["backend"] == "cpu_sequential"

    class Down:
        def get(self, k):
            raise ConnectionError("store down")
    assert RC.resolve_backend(None, Down())["source"] == "UNREADABLE:ConnectionError"


def test_cell_job_stamps_the_backend_on_the_baseline_and_cell_rows(rs, tmp_path, monkeypatch):  # noqa: F811
    kw, empty = _smoke_kw(tmp_path, rs)
    kw["backend"] = "cpu_lockstep"
    monkeypatch.setattr(RC.R, "ROWS", {**RC.R.ROWS, "baseline": str(empty)})      # no committed baseline: the stage runs
    ctx = Ctx()
    RC.cell_job(ctx, **kw)
    base = [x for x in ctx.rows if x["kind"] == "baseline_r16"][-1]
    cell = [x for x in ctx.rows if x["kind"] == "r16_cell"][-1]
    runs = [x for x in ctx.rows if x["kind"] == "run" and x.get("family") == "linear"]
    assert base["backend"] == cell["backend"] == "cpu_lockstep" and cell["backend_source"] == "PARAM"
    assert runs and all(x["backend"] == "cpu_lockstep" for x in runs)
    assert ctx.ck["backend"] == {"backend": "cpu_lockstep", "source": "PARAM"}               # fixed at job start
