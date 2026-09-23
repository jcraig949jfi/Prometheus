"""G-R4-2: floor = max of the pressure's own four parts; the gate is a column; a missing learner is a bound."""
from __future__ import annotations

import pytest

from primordial.metric import floors as F
from primordial.metric import invariant as I
from primordial.metric import suite as S
from primordial.metric.tests.test_invariant import FakeCtx
from primordial.ops import qd_ledger as Q
from primordial.tests._live import live_url


def test_floor_is_max_of_parts_and_gate_never_enters():
    parts = {"abstain": 88.28, "best_constant": 88.28, "uniform_random_median": 0.0, "input_invariant_learner": 60.0}
    f = S.floor_of_parts(parts)
    assert f == {"floor": 88.28, "floor_kind": "abstain", "floor_is_bound": False,
                 "bound_parts": list(S.PARTS)}
    row = S.suite_row(1, "train8_held64", {"parts": dict(parts, input_invariant_learner=None), "gate_held64": 170.47},
                      {"invariant_held64_median": 60.0, "invariant_held64_iqr": 1.0, "held64_by_run_seed": [60.0] * 8,
                       "run_seeds": list(range(8)), "budget_ok": True})
    assert row["floor"] == 88.28 and row["gate_held64"] == 170.47 and row["learner"]["status"] == "run"


def test_learner_above_others_sets_the_floor():
    f = S.floor_of_parts({"abstain": 10.0, "best_constant": 12.0, "uniform_random_median": 3.0,
                          "input_invariant_learner": 40.0})
    assert f["floor"] == 40.0 and f["floor_kind"] == "input_invariant_learner" and not f["floor_is_bound"]


def test_missing_learner_is_a_bound_over_the_parts_run():
    f = S.floor_of_parts({"abstain": 10.0, "best_constant": 12.0, "uniform_random_median": 3.0,
                          "input_invariant_learner": None})
    assert f["floor"] == 12.0 and f["floor_is_bound"] and f["bound_parts"] == ["abstain", "best_constant",
                                                                                "uniform_random_median"]
    with pytest.raises(ValueError):
        S.floor_of_parts({p: None for p in S.PARTS})


def _committed(world, pressure, kind, exp):
    rs = [r for r in Q.load() if r.get("floor") == kind and r["cell"]["world"] == world
          and r["cell"]["pressure"] == pressure and r["source"]["exp_id"] == exp]
    return rs[0]["fitness"]["held64_median"]


def test_cheap_parts_reproduce_committed_m1_floor_cells_w3():
    got = S.cheap_parts(3)
    for p in F.PRESSURES:
        parts = got[p]["parts"]
        assert round(parts["abstain"], 4) == _committed("w3", p, "abstain", "G-M1-floors-w134")
        assert round(parts["best_constant"], 4) == _committed("w3", p, "best_fixed", "G-M1-floors-w134")
        assert round(parts["uniform_random_median"], 4) == _committed("w3", p, "random_action", "G-M1-floors-w134")
        assert round(got[p]["gate_held64"], 4) == _committed("w3", p, "gate", "G-M1-gate-floor-w134-v2")


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for k in c.scan_iter("pm:qd:g-r4-inv-*", count=5000):
        c.delete(k)


def test_suite_job_rows_learner_only_on_its_pressure_and_resumes(r, tmp_path, monkeypatch):
    monkeypatch.setattr(I, "PAUSE_EVERY", 2)
    kw = dict(gen_seeds=[3], gens=3, batch=8, archive_url=live_url(), elites_dir=str(tmp_path))
    ref = FakeCtx()
    S.job(ref, **kw)
    kinds = [x["kind"] for x in ref.rows]
    assert kinds == ["suite_cheap"] * 2 + ["run"] * 8 + ["floor_suite"] * 2
    s8, s128 = ref.rows[-2], ref.rows[-1]
    assert s8["pressure"] == "train8_held64" and s8["learner"]["status"] == "run" and not s8["floor_is_bound"]
    assert s128["pressure"] == "train128_held64" and s128["learner"]["status"] == "not_run" and s128["floor_is_bound"]
    assert "input_invariant_learner" not in s128["bound_parts"]
    ctx = FakeCtx(pause_after=3)
    with pytest.raises(RuntimeError):
        S.job(ctx, **kw)
    ctx.pause_after = None
    S.job(ctx, **kw)
    vol = ("qd_wall_s", "elites", "wall_s")
    strip = lambda x: {k: v for k, v in x.items() if k not in vol and k != "oracle_held8" and k != "gate"}
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]
