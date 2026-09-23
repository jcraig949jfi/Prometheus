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


def test_v1_rows_refuse_clause_a_on_every_survivor(tmp_path):
    """H-R16-1: 8-seed baselines with no rng_family are retired from judging (operator 16)."""
    recs, _ = SR.replay(*_write_rows(tmp_path))
    s = SR.summary(recs)
    assert s["survived"] == [["w1", T8], ["w3", T128]]
    assert s["clause_a_refused_baseline_n"] == s["survived"] and s["clause_a_eligible"] == []


def _pooled_rows(tmp_path, counts):
    """One cell (w5 train8): learner 8 runs, baseline runs split over rng families as `counts` {family: n}."""
    s1 = [_cheap(5, T8, 100.0, 100.0)] + _runs(5, T8, 60.0)
    s2, i = [], 0
    for fam, n in counts.items():
        for rs in range(n):
            s2.append({**_runs(5, T8, 0.0, family="linear")[0], "rng_family": fam, "run_seed": rs,
                       "held64_per_seed": 200.0 + i})
            i += 1
    paths = []
    for name, rows in (("s1", s1), ("s2", s2), ("sl", [])):
        f = tmp_path / f"{name}.jsonl"
        f.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        paths.append(f)
    return paths


def test_pooled_8x4_baseline_is_eligible_and_29_1_1_1_is_refused(tmp_path):
    recs, defects = SR.replay(*_pooled_rows(tmp_path, {4200: 8, 2101: 8, 3303: 8, 5501: 8}))
    r = _by(recs)[("w5", T8)]
    assert defects == [] and r["baseline"]["n_runs"] == 32                  # seeds 0-7 repeat across families
    assert r["baseline"]["families"] == [2101, 3303, 4200, 5501]
    assert r["baseline"]["n_per_family"] == {"2101": 8, "3303": 8, "4200": 8, "5501": 8}
    assert r["clause_a_baseline_n"] == "OK" and r["verdicts"]["gate_in|HOLD"]["verdict"] == "SURVIVED"
    # pooling order is SWARM_R4 s9's listing (4200, 2101, 3303, 5501), then run seed: the CI depends on it
    from primordial.metric.ci import median_ci
    shuffled = _pooled_rows(tmp_path, {3303: 8, 5501: 8, 2101: 8, 4200: 8})      # rows written 3303 first
    m, _ = SR.measure(*shuffled)
    rows = [json.loads(x) for x in shuffled[1].read_text(encoding="utf-8").splitlines()]
    in_order = [r["held64_per_seed"] for r in sorted(rows, key=lambda r: (SR.FAMILY_ORDER.index(r["rng_family"]),
                                                                          r["run_seed"]))]
    assert m[(5, T8)]["baseline"]["ci95"] == list(median_ci(in_order))
    assert SR._family_rank(None) < SR._family_rank(4200) < SR._family_rank(2101) < SR._family_rank(9999)
    recs, _ = SR.replay(*_pooled_rows(tmp_path, {4200: 29, 2101: 1, 3303: 1, 5501: 1}))
    r = _by(recs)[("w5", T8)]
    assert r["baseline"]["n_runs"] == 32 and r["clause_a_baseline_n"] == "BASELINE_N"


def test_the_committed_screen_replays_with_zero_mismatches():
    if not SR.WORLDS_R4.exists():
        pytest.skip("worlds_r4.json not committed")
    doc = json.loads(SR.WORLDS_R4.read_text(encoding="utf-8"))
    recs, defects = SR.replay()
    assert defects == []
    assert SR.compare(doc, recs) == []
    s = SR.summary(recs)
    assert s["cells"] == len(doc["cells"])
    if doc.get("schema") == "worlds_r4/v1":                                  # 8-seed survivors carry no clause A
        assert s["clause_a_refused_baseline_n"] == s["survived"] and s["clause_a_eligible"] == []
