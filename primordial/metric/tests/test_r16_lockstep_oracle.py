"""G-R7-2 option (b) (A 1789505640089-0, E 1789505779961-0): before pm:r7:backend is written, G's production
lockstep baseline stage must match cpu_sequential and E's measured lockstep on one real cell, wall within 10%."""
from __future__ import annotations

import pytest

from primordial.metric import r16_cells as RC
from primordial.metric.tests.test_r16 import Ctx
from primordial.tests._live import live_url

TINY = dict(gen_seed=3, pressure="train8_held64", families=(4200, 2101), run_seeds=(0, 1), gens=3, batch=8)


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


def test_oracle_row_passes_only_with_matching_e_digests_and_wall(r, tmp_path):
    kw = dict(TINY, base_archive=live_url(), elites_root=str(tmp_path))
    first = Ctx()
    got = RC.lockstep_oracle_job(first, backends=("cpu_lockstep",), **kw)[0]
    assert got["kind"] == "lockstep_oracle" and got["runs"] == 4
    assert got["elites_eq_sequential"] and got["rows_eq_sequential"]
    assert not got["pass"] and got["reasons"] == ["E_REFERENCE_MISSING"]                      # no E reference yet
    e_d = {"cpu_lockstep": dict(got["digests"])}
    ok = RC.lockstep_oracle_job(Ctx(), backends=("cpu_lockstep",), e_digests=e_d,
                                e_wall_s={"cpu_lockstep": got["g_stage_wall_s"] * 1.0 or 1.0}, **kw)[0]
    assert ok["elites_eq_e_lockstep"] and ok["reasons"] in ([], ["WALL_OUTSIDE_10PCT"])        # walls of tiny stages jitter
    bad_d = {"cpu_lockstep": {**got["digests"], "4200|0": "0" * 64}}
    bad = RC.lockstep_oracle_job(Ctx(), backends=("cpu_lockstep",), e_digests=bad_d, e_wall_s={"cpu_lockstep": 1e9}, **kw)[0]
    assert not bad["pass"] and "ELITES_NE_E_LOCKSTEP" in bad["reasons"] and "WALL_OUTSIDE_10PCT" in bad["reasons"]
    assert bad["mismatched_runs"]["elites_vs_e"] == ["4200|0"]


def test_an_unrunnable_backend_is_a_failed_oracle_row_not_a_crash(r, tmp_path, monkeypatch):
    def boom(backend):
        raise ImportError("no torch in this venv")
    monkeypatch.setattr(RC, "evaluator_for", boom)
    ctx = Ctx()
    rows = RC.lockstep_oracle_job(ctx, backends=("gpu_lockstep",), base_archive=live_url(), elites_root=str(tmp_path), **TINY)
    assert len(rows) == 1 and rows[0]["backend"] == "gpu_lockstep" and not rows[0]["pass"]
    assert rows[0]["reason"].startswith("STAGE_FAILED:ImportError")
    assert [x["kind"] for x in ctx.rows] == ["lockstep_oracle"]                                # stage rows stay inside
