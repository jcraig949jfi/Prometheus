"""F12 scorer as a program: floor-gated compression, own-KILLs unscored, refutations, corrections."""
from __future__ import annotations

import json

from primordial.ops import qd_ledger as Q
from primordial.score import progress as PR


def _qd(median, nbytes, baseline, cohort="B", status="record", exp="x", ts=10.0, **kw):
    return dict({"cell": {"representation": exp, "world": "w4", "pressure": "p", "substrate": "s", "channel": "none"},
                 "mechanism": exp, "fitness": {"held64_median": median, "iqr": 2.0, "n_runs": 8},
                 "footprint": {"genome_bytes": nbytes}, "baseline": baseline, "status": status, "exp_id": exp,
                 "cohort": cohort, "ts": ts}, **kw)


def test_compression_scores_only_floor_pass(monkeypatch):
    qd = [_qd(90.0, 312, True, cohort="round1", exp="base"), _qd(91.0, 40, False, exp="cand")]
    got = PR.compression(qd, "B", (0, 100))
    real_floor = got["floor_verdicts"]
    assert got["raw_pass"] == 1 and got["value"] == 0 and set(real_floor) <= {"NO_FLOOR", "BELOW_FLOOR", "PASS"}
    for fv, scored in (("NO_FLOOR", 0), ("BELOW_FLOOR", 0), ("NO_HEADROOM", 0), ("PASS", 1)):
        monkeypatch.setattr(Q, "check", lambda *a, fv=fv, **k: {"verdict": "PASS", "floor": {"verdict": fv}})
        assert PR.compression(qd, "B", (0, 100))["value"] == scored, fv


def test_superseded_rows_are_dropped_and_count_as_corrections(monkeypatch):
    monkeypatch.setattr(Q, "check", lambda *a, **k: {"verdict": "PASS", "floor": {"verdict": "PASS"}})
    old = _qd(91.0, 40, False, exp="old")
    new = _qd(91.0, 40, False, exp="new", supersedes={"exp_id": "old", "status": "cheat"})
    new["cell"] = old["cell"]
    got = PR.compression([old, new], "B", (0, 100))
    assert got["value"] == 1 and got["scored"][0]["exp_id"] == "new" and got["superseded_dropped"] == 1


def test_refutes_matches_identifiers_only():
    exp_lane = {"C7d-x": "C", "B2-toy": "B", "B9": "B"}
    assert PR.refuted_targets({"exp_id": "B9", "refutes": "C7d-x CAUSE only: 'B2' mislabelled"}, exp_lane) == ["C7d-x"]
    assert PR.refuted_targets({"exp_id": "B9", "refutes": []}, exp_lane) == []
    assert PR.refuted_targets({"exp_id": "B9", "refutes": "B9 and B2-toy"}, exp_lane) == ["B2-toy"]


def _write(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def test_vector_on_a_synthetic_round(tmp_path, monkeypatch):
    monkeypatch.setattr(PR, "DATE", "d")
    exp, root = tmp_path / "exp", tmp_path / "root"
    cheat = {"cheat": "caught 16/16"}
    rec = lambda lane, eid, status, **kw: dict({"lane": lane, "exp_id": eid, "status": status, "ts": 5.0,
                                                "controls": cheat, "rows": f"primordial/ledger/rows/{lane}/{eid}.jsonl",
                                                "claim": "prose never read"}, **kw)
    _write(exp / "pm_results_d.jsonl", [
        rec("C", "C1", "PASS"),
        rec("B", "B1", "KILL"),                                    # own-hypothesis kill: unscored
        rec("B", "B2", "KILL", refutes="C1: wrong"),                # refutes another lane: scored
        rec("B", "B3", "KILL", refutes="B-old retracted", ts=5.0),  # names nothing known: own kill
        rec("B", "B4", "PASS", refutes="B1 was wrong"),             # self-correction
        rec("E", "E1", "PASS")])
    _write(exp / "pm_anomalies_d.jsonl", [
        {"id": "a1", "lane": "D", "ts": "5", "subject": "s"},
        {"id": "a1", "lane": "D", "ts": "6", "event": True, "status": "RESOLVED", "exp_id": "D1"},
        {"id": "a2", "lane": "D", "ts": "6", "event": True, "status": "RESOLVED", "exp_id": "D-no-rows"}])
    _write(root / "primordial/ledger/qd/cells.jsonl", [_qd(90.0, 312, True, cohort="round1", exp="base")])
    _write(root / "primordial/ledger/rows/D/D1.jsonl", [{"status": "dev", "ts": 5.0}, {"status": "record", "ts": 5.0}])
    _write(root / "primordial/ledger/rows/E/E1.jsonl", [{"status": "cheat", "ts": 5.0}, {"status": "control", "ts": 5.0}])
    _write(root / "primordial/ledger/rows/C/C1.jsonl", [{"status": "control", "ts": 5.0}, "not a row"])
    v = PR.vector(exp, root, window=(0, 100))
    assert v["B"]["axes"]["refutations"] == 1 and v["B"]["axes"]["kills_own"] == 2 and v["B"]["axes"]["corrections"] == 1
    assert v["D"]["axes"]["anomalies_filed"] == 1 and v["D"]["axes"]["anomalies_resolved"] == 1
    assert v["D"]["detail"]["anomalies_resolved_unbacked"] == ["a2"] and v["D"]["axes"]["failure_landscape"] == 1
    assert v["E"]["axes"]["instruments"] == 1 and v["C"]["axes"]["instruments"] == 0
    assert v["B"]["axes"]["transfer"] == 0 and v["B"]["detail"]["transfer"] == "NOT_OPEN"
    assert set(v["B"]["axes"]) == set(PR.AXES)


def test_round2_replay_produces_the_vector():
    v = PR.vector()
    assert set(v) == {"B", "C", "D", "E"}
    assert all(set(d["axes"]) == set(PR.AXES) for d in v.values())
    b = v["B"]["detail"]["compression"]
    assert b["raw_pass"] > 0 and b["superseded_dropped"] == 3
    assert "PASS" not in b["floor_verdicts"] and v["B"]["axes"]["compression"] == 0   # nothing clears the floor
    assert v["D"]["axes"]["anomalies_resolved"] == 4 and v["E"]["axes"]["instruments"] >= 1
    assert sum(d["axes"]["refutations"] for d in v.values()) == 0                   # round 2 refuted no lane
    assert PR.vector() == v                                                          # deterministic
