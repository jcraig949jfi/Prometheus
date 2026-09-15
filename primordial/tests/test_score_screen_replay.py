"""H-R4-3: the independent screen replay recomputes G's worlds_r4 verdicts from rows, and catches tampering."""
from __future__ import annotations

import copy
import json

import numpy as np
import pytest

from primordial.score import screen_replay as SR

T8, T128 = "train8_held64", "train128_held64"
RND = [1, 2, 3, 4, 5, 6, 7, 8]


def _cheap(gs, p, abstain, gate):
    return {"kind": "suite_cheap", "exp_id": "G-R4-3-stage1", "world": f"w{gs}", "gen_seed": gs, "pressure": p,
            "status": "control", "gate": {"gate_held64": gate}, "gate_held64": gate,
            "floors": {"abstain_held64": abstain, "best_fixed_held64": abstain, "random_action_held64_by_policy_seed": RND},
            "parts": {"abstain": abstain, "best_constant": abstain, "uniform_random_median": float(np.median(RND)),
                      "input_invariant_learner": None}}


def _runs(gs, p, start, family=None, exp="x"):
    return [{"kind": "run", "exp_id": exp, "world": f"w{gs}", "gen_seed": gs, "pressure": p, "run_seed": rs,
             "held64_per_seed": float(start + rs), "budget_ok": True, "genomes": 1, "genome_bytes": 200,
             "elites": f"e{rs}", "status": "control", **({"family": family} if family else {})} for rs in range(8)]


# (gen_seed, pressure, abstain, gate, learner run start or None, baseline run start)
CELLS = [
    (1, T8, 100.0, 150.0, 60.0, 200.0),      # SURVIVED everywhere
    (1, T128, 100.0, 100.0, None, 50.0),     # bound, exact: CULLED WEAK_WORLD
    (2, T8, 100.0, 180.0, 60.0, 160.0),      # four_policy SURVIVED; gate_in HELD / CULLED BASELINE
    (2, T128, 100.0, 180.0, None, 90.0),     # bound, lo <= bound < gate: non-survivable PENDING
    (3, T8, 100.0, 120.0, 60.0, 90.0),       # HELD under HOLD, CULLED BASELINE under CULL
    (3, T128, 100.0, 100.0, 116.0, 200.0),   # train128 learner 119.5 is the floor; SURVIVED
]


def _write_rows(tmp_path, cells=CELLS):
    """Low rows for the replay plus G's own aggregate rows, so G's assembler builds the file from the same data."""
    from primordial.metric import baseline as BL
    from primordial.metric import invariant as INV
    from primordial.metric import suite as SU
    s1, s2, sl = [], [], []
    for gs, p, ab, gate, lstart, bstart in cells:
        ch = _cheap(gs, p, ab, gate)
        s1.append(ch)
        lsum = None
        if lstart is not None:
            lr = _runs(gs, p, lstart)
            lsum = INV.summary(lr)
            (s1 if p == T8 else sl).extend(lr)
            if p == T128:
                sl.append({**lsum, "exp_id": "G-R4-3-stage2-learner", "status": "control"})
        suite_learner = lsum if p == T8 else None
        s1.append(SU.suite_row(gs, p, {"parts": ch["parts"], "gate_held64": gate}, suite_learner))
        br = _runs(gs, p, bstart, family="linear")
        s2.extend(br)
        s2.append({**BL.summary(br), "status": "control"})
    paths = []
    for name, rows in (("s1", s1), ("s2", s2), ("sl", sl)):
        f = tmp_path / f"{name}.jsonl"
        f.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        paths.append(f)
    return paths


def _g_doc(paths, max_survivors=8):
    from primordial.metric import screen_run as SRUN
    from primordial.metric import worlds as WR
    return WR.build(SRUN.assemble(*map(str, paths)), commit="test", max_survivors=max_survivors)


def _by(recs):
    return {(r["world"], r["pressure"]): r for r in recs}


def test_rules_on_planted_cells(tmp_path):
    recs, defects = SR.replay(*_write_rows(tmp_path))
    assert defects == []
    r = _by(recs)
    act = lambda k: (r[k]["verdicts"]["gate_in|HOLD"]["verdict"], r[k]["verdicts"]["gate_in|HOLD"]["cull_reason"])
    assert act(("w1", T8)) == ("SURVIVED", None)
    assert act(("w1", T128)) == ("CULLED", "WEAK_WORLD") and r[("w1", T128)]["floor_is_bound"]
    assert act(("w2", T8)) == ("HELD", None)
    assert r[("w2", T8)]["verdicts"]["four_policy|CULL"]["verdict"] == "SURVIVED"
    assert r[("w2", T8)]["verdicts"]["gate_in|CULL"] == {"verdict": "CULLED", "cull_reason": "BASELINE", "floor": 180.0}
    assert r[("w2", T128)]["pending"] == "non_survivable" and r[("w2", T128)]["non_survivable_exact"]["holds"]
    assert act(("w2", T128)) == ("PENDING", None)
    assert r[("w2", T128)]["verdicts"]["four_policy|CULL"] == {"verdict": "CULLED", "cull_reason": "PENDING", "floor": 100.0}
    assert act(("w3", T8)) == ("HELD", None) and r[("w3", T8)]["verdicts"]["four_policy|CULL"]["cull_reason"] == "BASELINE"
    assert r[("w3", T128)]["floor"] == 119.5 and act(("w3", T128)) == ("SURVIVED", None)
    assert r[("w1", T8)]["floor_parts"]["input_invariant_learner"] == 63.5        # train8 learner stays in train8
    assert r[("w1", T128)]["floor_parts"]["input_invariant_learner"] is None


@pytest.mark.parametrize("max_survivors", [8, 1])
def test_replay_matches_g_assembly_from_the_same_rows(tmp_path, max_survivors):
    paths = _write_rows(tmp_path)
    recs, defects = SR.replay(*paths, max_survivors=max_survivors)
    assert defects == [] and SR.compare(_g_doc(paths, max_survivors), recs, max_survivors=max_survivors) == []


def test_stop_marks_later_survivors_not_reached(tmp_path):
    recs, _ = SR.replay(*_write_rows(tmp_path), max_survivors=1)
    r = _by(recs)
    # order: w2 t8, w2 t128, w1 t8, w3 t8, w1 t128, w3 t128
    assert [(x["world"], x["pressure"]) for x in recs][:3] == [("w2", T8), ("w2", T128), ("w1", T8)]
    assert r[("w1", T8)]["verdicts"]["four_policy|HOLD"]["cull_reason"] == "NOT_REACHED"       # w2 t8 came first
    assert r[("w1", T8)]["verdicts"]["gate_in|HOLD"]["verdict"] == "SURVIVED"                  # w2 t8 is HELD there
    assert r[("w3", T128)]["verdicts"]["gate_in|HOLD"]["cull_reason"] == "NOT_REACHED"


@pytest.mark.parametrize("field,edit", [
    ("verdicts.gate_in|HOLD.verdict", lambda c: c["verdicts"]["gate_in|HOLD"].update(verdict="SURVIVED")),
    ("baseline.ci95[0]", lambda c: c["baseline"]["ci95"].__setitem__(0, c["baseline"]["ci95"][0] + 0.5)),
    ("floor_parts.abstain", lambda c: c["floor_parts"].update(abstain=99.0)),
    ("verdicts.four_policy|CULL.cull_reason", lambda c: c["verdicts"]["four_policy|CULL"].update(cull_reason="WEAK_WORLD")),
])
def test_a_tampered_file_is_caught_by_field(tmp_path, field, edit):
    paths = _write_rows(tmp_path)
    doc = _g_doc(paths)
    bad = copy.deepcopy(doc)
    edit(next(c for c in bad["cells"] if (c["world"], c["pressure"]) == ("w2", T8)))
    mm = SR.compare(bad, SR.replay(*paths)[0])
    assert any(m["field"] == field and m["world"] == "w2" for m in mm), mm


def test_row_defects_are_reported(tmp_path):
    s1, s2, sl = _write_rows(tmp_path)
    rows = [json.loads(x) for x in s2.read_text(encoding="utf-8").splitlines()]
    dup = dict(next(r for r in rows if r["kind"] == "run"), held64_per_seed=-1.0)
    s2.write_text("".join(json.dumps(r) + "\n" for r in rows + [dup]), encoding="utf-8")
    _, defects = SR.replay(s1, s2, sl)
    assert any("two values" in d for d in defects)
    short = [r for r in rows if not (r["kind"] == "run" and r["gen_seed"] == 1 and r["pressure"] == T8 and r["run_seed"] == 7)]
    s2.write_text("".join(json.dumps(r) + "\n" for r in short), encoding="utf-8")
    _, defects = SR.replay(s1, s2, sl)
    assert any("7 run seeds < 8" in d for d in defects)


def test_a_written_survivable_pending_cell_is_a_mismatch(tmp_path):
    paths = _write_rows(tmp_path, CELLS + [(4, T128, 100.0, 100.0, None, 200.0)])      # bound, lo > bound
    recs, _ = SR.replay(*paths)
    assert _by(recs)[("w4", T128)]["pending"] == "survivable"
    mm = SR.compare(_g_doc(paths), recs)
    assert [m["field"] for m in mm] == ["survivable PENDING in a written file"]


def test_the_committed_screen_replays_with_zero_mismatches():
    if not SR.WORLDS_R4.exists():
        pytest.skip("worlds_r4.json not committed")
    doc = json.loads(SR.WORLDS_R4.read_text(encoding="utf-8"))
    recs, defects = SR.replay()
    assert defects == []
    assert SR.compare(doc, recs) == []
    assert SR.summary(recs)["cells"] == len(doc["cells"])
