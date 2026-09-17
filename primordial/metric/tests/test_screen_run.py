"""G-R4-4: worlds_r4.json is assembled from rows files only; PENDING blocks the write; report for A."""
from __future__ import annotations

import json

import pytest

from primordial.metric import screen_run as SR
from primordial.metric import worlds as WR

S8, S128 = "train8_held64", "train128_held64"


def suite(gs, p, floor, gate, learner=True):
    return {"kind": "floor_suite", "world": f"w{gs}", "gen_seed": gs, "pressure": p, "floor": floor, "gate_held64": gate,
            "floor_parts": {"abstain": floor, "best_constant": floor, "uniform_random_median": 0.0,
                            "input_invariant_learner": floor - 5 if learner else None},
            "learner": {"status": "run" if learner else "not_run"}, "status": "control"}


def base(gs, p, median, lo, hi):
    return {"kind": "baseline", "gen_seed": gs, "pressure": p, "median": median, "ci95": [lo, hi], "bytes": 312,
            "n_runs": 8, "held64_by_run_seed": {str(i): median for i in range(8)}, "elites": {}, "status": "control"}


def learner(gs, p, med):
    return {"kind": "floor_invariant", "gen_seed": gs, "pressure": p, "world": f"w{gs}", "invariant_held64_median": med,
            "invariant_held64_iqr": 0.0, "held64_by_run_seed": [med] * 8, "run_seeds": list(range(8)),
            "budget_ok": True, "status": "control"}


def write_rows(path, rows):
    path.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    return path


@pytest.fixture
def files(tmp_path):
    s1 = write_rows(tmp_path / "s1.jsonl", [suite(4, S8, 100.0, 150.0), suite(4, S128, 100.0, 150.0, learner=False),
                                            suite(5, S8, 100.0, 90.0), suite(6, S8, 100.0, 80.0)])
    s2 = write_rows(tmp_path / "s2.jsonl", [base(4, S8, 200.0, 180.0, 220.0), base(4, S128, 120.0, 110.0, 130.0),
                                            base(5, S8, 50.0, 40.0, 60.0)])
    return s1, s2


def test_survivable_pending_cell_blocks_write_and_is_reported_with_hours(files, tmp_path):
    s1, s2 = files
    doc = WR.build(SR.assemble(s1, s2, tmp_path / "none.jsonl"), commit="t")
    rep = SR.report(doc)
    assert rep["cells"] == 4 and rep["stage2_cells"] == 3
    blk = rep["pending_survivable_blocking"]
    assert [p["world"] for p in blk] == ["w4"] and blk[0]["est_hours"] > 0 and rep["pending_non_survivable"] == []
    assert rep["survived"] == [("w4", S8)] and rep["not_reached"]["gate_in|HOLD"] == 1       # w6: stage 1 only
    with pytest.raises(ValueError):
        WR.write(doc, tmp_path / "out.json")


def test_non_survivable_pending_is_written_and_guarded_as_pending(tmp_path):
    s1 = write_rows(tmp_path / "s1.jsonl", [suite(7, S128, 189.19, 1482.5, learner=False)])
    s2 = write_rows(tmp_path / "s2.jsonl", [base(7, S128, 183.94, 161.45, 187.43)])            # the real w7 t128 shape
    doc = WR.build(SR.assemble(s1, s2, tmp_path / "none.jsonl"), commit="t")
    rep = SR.report(doc)
    assert rep["pending_survivable_blocking"] == [] and [p["world"] for p in rep["pending_non_survivable"]] == ["w7"]
    c = doc["cells"][0]
    assert c["pending"] == "non_survivable" and c["learner"]["status"] == "not_run"
    assert c["learner"]["reason"] == WR.NON_SURVIVABLE_REASON and c["learner"]["est_hours"] > 0
    assert c["verdicts"]["gate_in|HOLD"]["verdict"] == "PENDING" and c["verdicts"]["four_policy|HOLD"]["verdict"] == "PENDING"
    assert c["verdicts"]["gate_in|CULL"] == {"verdict": "CULLED", "cull_reason": "PENDING", "floor": 1482.5}
    assert all(v["verdict"] != "SURVIVED" for v in c["verdicts"].values())
    got = WR.load(WR.write(doc, tmp_path / "w.json"))
    assert WR.guard(got, "w7", S128)["why"] == "PENDING"
    from primordial.ops import qd_ledger as Q
    blk = Q.clause_a_r4_block(Q.check_r4("w7", S128, 1e9, 0, 8, doc=got))
    assert blk["verdict"] == "INELIGIBLE" and blk["screen"] == "PENDING" and blk["floor"] == 1482.5


def test_learner_row_resolves_pending_and_file_is_written(files, tmp_path):
    s1, s2 = files
    lrows = write_rows(tmp_path / "learner.jsonl", [{**learner(4, S128, 140.0), "exp_id": "G-R4-3-stage2-learner"}])
    assert SR.main(["--stage1", str(s1), "--stage2", str(s2), "--learner", str(lrows), "--write", "--commit", "abc",
                    "--out", str(tmp_path / "w.json")]) == 0
    got = WR.load(tmp_path / "w.json")
    by = {(c["world"], c["pressure"]): c for c in got["cells"]}
    w4 = by[("w4", S128)]
    assert w4["floor"] == 140.0 and not w4["floor_is_bound"] and w4["verdict"] == "HELD"   # 110 <= max(140,150), 150 > 140
    assert w4["sources"]["learner"]["exp_id"] == "G-R4-3-stage2-learner" and w4["pending"] is None
    assert by[("w5", S8)]["verdict"] == "CULLED" and by[("w6", S8)]["cull_reason"] == "NOT_REACHED"
    assert got["commit"] == "abc" and got["q1_floor_policy"] == "gate_in"


def test_write_needs_a_commit(files, tmp_path):
    s1, _ = files
    empty = write_rows(tmp_path / "e.jsonl", [])
    with pytest.raises(SystemExit):
        SR.main(["--stage1", str(s1), "--stage2", str(empty), "--learner", str(empty), "--write",
                 "--out", str(tmp_path / "x.json")])
