import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
import analyze_k2
from fixtures_k import fixtures

F = fixtures(); X, Y = F["X_al"], F["Y_al"]
COMPOSITE = Y[:12] + X[12:]


def _anat(tape, tags):
    cc = [2, 4, 5, 7] + list(range(8, 18))
    return {"tape": tape.hex(), "ccrit_origins": [list(tags(p)) + [p] for p in cc]}


def _row(i, cell, arm, comp=None, extinct=False, xt=None, persist=0):
    c = {"C": {"gain": 1 if comp else 0, "comp_func_births": 1 if comp else 0}, "first_comp_sr": {"anatomy": comp} if comp else None,
         "comp_func_alive": persist}
    return {"id": i, "cell": cell, "arm": arm, "comp": c, "summary": {"extinct": extinct, "extinct_tick": xt}, "exposure": 1}


def test_strict_two_source_and_mislabel():
    true_comp = _anat(COMPOSITE, lambda p: ("F", 1, "transplant1" if p < 12 else "transplant0"))
    assert analyze_k2.two_source_strict({"cell": "XY_AL/PARTIAL_BYTE", "comp": {"first_comp_sr": {"anatomy": true_comp}}})
    # reviewer specimen: shared positions 2,4 tagged X, Y bytes 7-11,17 tagged Y, transform 12-16 mutation-born
    mis = _anat(COMPOSITE, lambda p: ("F", 1, "transplant0") if p in (2, 4) else (("M", 9, "mut") if 12 <= p <= 16 else ("F", 2, "transplant1")))
    assert not analyze_k2.two_source_strict({"cell": "XY_AL/PARTIAL_BYTE", "comp": {"first_comp_sr": {"anatomy": mis}}})


def test_branches(tmp_path):
    good = _anat(COMPOSITE, lambda p: ("F", 1, "transplant1" if p < 12 else "transplant0"))
    rows, plan = [], []
    def add(cell, arm, n, **kw):
        for k in range(n):
            i = "%s_%s_%d" % (cell, arm, k); rows.append(_row(i, cell, arm, **kw)); plan.append({"id": i, "cfg": {}})
    add("XY_AL/PARTIAL_BYTE", "ON", 20, comp=good, persist=3)
    add("XY_AL/PARTIAL_BYTE", "ON", 40)
    for c in ("X_ONLY/PARTIAL_BYTE", "Y_ONLY/PARTIAL_BYTE", "XY_AL/COPY_BYTE"):
        add(c, "ON", 60)
    add("XY_AL/COPY_STRUCT", "ON", 50, extinct=True, xt=100); add("XY_AL/COPY_STRUCT", "ON", 10)
    add("XY_AL/PARTIAL_BYTE", "RANDOM_REWARD", 20, comp=good, persist=0); add("XY_AL/PARTIAL_BYTE", "RANDOM_REWARD", 40)
    add("XY_AL/PARTIAL_BYTE", "OFF", 60)
    p = tmp_path / "r.jsonl"; p.write_text("\n".join(json.dumps(r) for r in rows)); q = tmp_path / "p.json"; q.write_text(json.dumps(plan))
    o = analyze_k2.main(str(p), str(q), str(tmp_path / "o.json"), check256=False)
    assert o["K-P1"]["COPY_STRUCT"]["holds"] == "NOT_TESTABLE" and o["K-P1"]["holds"] == "NOT_TESTABLE"
    assert o["K-P1"]["COPY_BYTE"]["holds"] is True
    assert o["K-P2"]["holds"] is True and o["K-P3"]["holds"] is True
    assert o["K-P4"]["tests"]["comp_any_vs_RR"]["pass"] is False and o["K-P4"]["holds"] is True
