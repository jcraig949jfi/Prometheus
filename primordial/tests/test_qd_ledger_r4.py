"""G-R4-4 / G-R4-5: worlds_r4.json records + JIT guard, and clause A as progress above floor in `check`."""
from __future__ import annotations

import json

import pytest

from primordial.metric import screen as SC
from primordial.metric import worlds as WR
from primordial.ops import qd_ledger as Q

S8, S128 = "train8_held64", "train128_held64"


def suite(gs, p, parts, gate, learner=True):
    parts = {"abstain": parts[0], "best_constant": parts[1], "uniform_random_median": parts[2],
             "input_invariant_learner": parts[3] if learner else None}
    return {"kind": "floor_suite", "world": f"w{gs}", "gen_seed": gs, "pressure": p, "floor_parts": parts,
            "gate_held64": gate, "learner": {"status": "run" if learner else "not_run"}}


def base(gs, p, median, lo, hi, nbytes=312):
    return {"gen_seed": gs, "pressure": p, "median": median, "ci95": [lo, hi], "bytes": nbytes, "n_runs": 8,
            "held64_by_run_seed": {str(i): median for i in range(8)}, "elites": {}}


def learner(gs, p, med):
    return {"gen_seed": gs, "pressure": p, "invariant_held64_median": med, "invariant_held64_iqr": 0.0,
            "held64_by_run_seed": [med] * 8, "run_seeds": list(range(8)), "budget_ok": True}


@pytest.fixture
def doc():
    recs = [
        WR.cell(suite(7, S8, (100.0, 100.0, 5.0, 60.0), 90.0), base(7, S8, 200.0, 150.0, 250.0)),        # SURVIVED
        WR.cell(suite(8, S8, (100.0, 100.0, 5.0, 60.0), 90.0), base(8, S8, 95.0, 80.0, 99.0)),           # CULLED
        WR.cell(suite(9, S8, (100.0, 100.0, 5.0, 60.0), 170.0), base(9, S8, 140.0, 120.0, 160.0)),       # HELD
        WR.cell(suite(10, S128, (100.0, 100.0, 5.0, 0.0), 90.0, learner=False), base(10, S128, 95.0, 80.0, 99.0)),
        WR.cell(suite(11, S8, (1.0, 1.0, 0.0, 0.0), 1.0), None),                                         # stage 1 only
    ]
    return WR.build(recs, commit="abc1234")


def test_records_and_active_variant(doc):
    by = {(c["world"], c["pressure"]): c for c in doc["cells"]}
    assert doc["q1_floor_policy"] == "gate_in" and doc["q2_policy"] == "HOLD" and doc["schema"] == "worlds_r4/v1"
    assert by[("w7", S8)]["verdict"] == "SURVIVED"
    assert by[("w8", S8)]["verdict"] == "CULLED" and by[("w8", S8)]["cull_reason"] == "WEAK_WORLD"
    assert by[("w9", S8)]["verdict"] == "HELD" and by[("w9", S8)]["verdicts"]["four_policy|CULL"]["verdict"] == "SURVIVED"
    w10 = by[("w10", S128)]                                   # a bound, exact: CI low and gate below it
    assert w10["floor_is_bound"] and w10["learner"]["status"] == "not_run" and w10["verdict"] == "CULLED"
    assert by[("w11", S8)]["stage"] == 1 and by[("w11", S8)]["cull_reason"] == "NOT_REACHED"
    assert set(by[("w7", S8)]["verdicts"]) == {SC.vkey(*v) for v in SC.VARIANTS}
    assert WR.survivor_worlds(doc) == ["w7"]


def test_bound_that_could_flip_is_pending_and_write_refuses(tmp_path):
    rec = WR.cell(suite(12, S128, (100.0, 100.0, 5.0, 0.0), 90.0, learner=False), base(12, S128, 200.0, 150.0, 250.0))
    d = WR.build([rec], commit="x")
    assert WR.pending(d) == WR.blocking(d) == [("w12", S128)] and rec["pending"] == "survivable"
    assert all(v["verdict"] == "PENDING" for v in rec["verdicts"].values())
    with pytest.raises(ValueError):
        WR.write(d, tmp_path / "w.json")
    full = WR.cell(suite(12, S128, (100.0, 100.0, 5.0, 0.0), 90.0, learner=False), base(12, S128, 200.0, 150.0, 250.0),
                   learner=learner(12, S128, 180.0))
    assert not full["floor_is_bound"] and full["floor"] == 180.0 and full["verdicts"]["gate_in|HOLD"]["verdict"] == "CULLED"
    with pytest.raises(ValueError):                           # a learner from the other pressure never enters
        WR.cell(suite(12, S128, (1, 1, 0, 0), 1.0, learner=False), None, learner=learner(12, S8, 5.0))


def test_write_load_roundtrip_and_guard(doc, tmp_path):
    p = WR.write(doc, tmp_path / "worlds_r4.json")
    got = WR.load(p)
    assert got == json.loads(json.dumps(doc))
    assert WR.guard(got, "w7", S8) is None
    assert WR.guard(got, "w7", S128)["why"] == "UNSCREENED"
    assert WR.guard(got, "w99", S8)["why"] == "UNSCREENED"
    assert WR.guard(got, "w8", S8)["why"] == "CULLED" and WR.guard(got, "w9", S8)["why"] == "HELD"
    assert WR.guard(None, "w7", S8)["why"] == "UNSCREENED"


# ---------------------------------------------------------------- G-R4-5: planted candidates on w7 train8
# floor (gate_in) = max(100, gate 90) = 100; baseline median 200, bytes 312

def test_progress_095_passes_094_fails_negative_is_below_floor(doc):
    at = Q.check_r4("w7", S8, 195.0, 200, 8, doc=doc)
    assert at["verdict"] == "PASS" and at["progress"] == pytest.approx(0.95) and at["progress"] >= 0.95
    lo = Q.check_r4("w7", S8, 194.0, 200, 8, doc=doc)
    assert lo["verdict"] == "FAIL" and lo["progress"] == pytest.approx(0.94) and lo["why"] == "progress < 0.95"
    neg = Q.check_r4("w7", S8, 99.0, 1, 8, doc=doc)
    assert neg["verdict"] == "BELOW_FLOOR" and neg["progress"] == pytest.approx(-0.01)


def test_bytes_tie_fails_and_ci_is_mapped_not_judged(doc):
    tie = Q.check_r4("w7", S8, 250.0, 312, 8, doc=doc)
    assert tie["progress"] > 0.95 and tie["verdict"] == "FAIL" and tie["why"] == "bytes not below the baseline's"
    held = [150.0, 160.0, 170.0, 190.0, 195.0, 200.0, 210.0, 260.0]
    got = Q.check_r4("w7", S8, 192.5, 200, 8, held=held, doc=doc)
    lo, hi = got["candidate_ci95"]
    assert got["progress_ci95"] == [pytest.approx((lo - 100) / 100), pytest.approx((hi - 100) / 100)]
    assert got["verdict"] == "FAIL"                           # progress 0.925: the CI high above 0.95 does not pass it


def test_world_not_on_the_list_and_not_surviving_cells_are_ineligible(doc):
    assert Q.check_r4("w99", S8, 1e9, 0, 8, doc=doc)["why"] == "UNSCREENED"
    assert Q.check_r4("w4", S128, 1e9, 0, 8, doc=doc)["why"] == "UNSCREENED"
    assert Q.check_r4("w8", S8, 1e9, 0, 8, doc=doc)["why"] == "CULLED"
    assert Q.check_r4("w9", S8, 1e9, 0, 8, doc=doc)["why"] == "HELD"
    assert Q.check_r4("w7", S8, 195.0, 200, 7, doc=doc)["verdict"] == "INELIGIBLE"
    assert Q.check_r4("w7", S8, 195.0, 200, 8, oracle_clean=False, doc=doc)["verdict"] == "INELIGIBLE"
    assert Q.check_r4("w7", S8, 195.0, 200, 8, cheat_failed=False, doc=doc)["verdict"] == "INELIGIBLE"
    assert Q.check_r4("w7", S8, 195.0, 200, 8, doc={**doc, "cells": []})["why"] == "UNSCREENED"


def test_every_verdict_carries_its_variant_floor(doc):
    for c in doc["cells"]:
        for k, v in c["verdicts"].items():
            want = c["floor"] if k.startswith("four_policy") else max(c["floor"], c["gate_held64"])
            assert v["floor"] == want, (c["world"], k, v)
    one = WR.build([WR.cell(suite(n, S8, (10.0, 10.0, 0.0, 0.0), 11.0 + n), base(n, S8, 50.0, 40.0, 60.0))
                    for n in range(1, 4)], commit="t", max_survivors=1)
    nr = [c["verdicts"]["gate_in|HOLD"] for c in one["cells"] if c["cull_reason"] == "NOT_REACHED"]
    assert len(nr) == 2 and all(v["floor"] == v["computed"]["floor"] for v in nr)


def test_check_carries_the_r4_judge_block_for_f12(doc):
    rows = [{"cell": {"representation": "linear", "world": "w7", "pressure": S8, "substrate": "x", "channel": "none"},
             "mechanism": "linear", "fitness": {"held64_median": 200.0, "iqr": 1.0, "n_runs": 8},
             "footprint": {"genome_bytes": 312}, "baseline": True, "status": "record", "source": {"exp_id": "t"}}]
    got = Q.check(rows, "w7", S8, 195.0, 1.0, 200, 8, doc=doc)["clause_a_r4"]
    assert got == {"verdict": "PASS", "why": None, "progress": pytest.approx(0.95), "progress_ci": None, "floor": 100.0,
                   "baseline_median": 200.0, "baseline_bytes": 312, "variant": "gate_in|HOLD", "screen": "SURVIVED"}
    assert got["verdict"] == Q.check_r4("w7", S8, 195.0, 200, 8, doc=doc)["verdict"]
    held = Q.check(rows, "w9", S8, 1e9, 1.0, 0, 8, doc=doc)["clause_a_r4"]
    assert held["verdict"] == "INELIGIBLE" and held["screen"] == "HELD" and held["floor"] == 170.0
    assert Q.check(rows, "w11", S8, 1e9, 1.0, 0, 8, doc=doc)["clause_a_r4"]["screen"] == "NOT_REACHED"
    assert Q.check(rows, "w1", S8, 1e9, 1.0, 0, 8, doc=doc)["clause_a_r4"]["screen"] == "UNSCREENED"
    below = Q.check(rows, "w7", S8, 99.0, 1.0, 0, 8, oracle_clean=True, held=[90.0, 95, 99, 99, 100, 101, 104, 110],
                    doc=doc)["clause_a_r4"]
    assert below["verdict"] == "BELOW_FLOOR" and below["progress_ci"][0] < below["progress"] < below["progress_ci"][1]


def test_cli_check_defaults_to_r4(doc, tmp_path, capsys):
    p = WR.write(doc, tmp_path / "worlds_r4.json")
    assert Q.main(["check", "--world", "w7", "--pressure", S8, "--median", "195", "--bytes", "200", "--runs", "8",
                   "--worlds", str(p)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["rules"] == "r4" and out["verdict"] == "PASS"
    assert Q.main(["check", "--world", "w1", "--pressure", S8, "--median", "195", "--bytes", "200", "--runs", "8",
                   "--worlds", str(p)]) == 0
    assert json.loads(capsys.readouterr().out)["why"] == "UNSCREENED"
