import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_f6 import analyze


def _r(i, both, func=True):
    return {"id": i, "census": [{"tick": t, "halves_func": ({"BOTH": 1} if t in both else ({"LO": 1} if func else {}))} for t in range(100, 2100, 100)]}


def test_f6():
    ALL = set(range(100, 2100, 100)); plan, rows = [], []
    for k in range(20):
        for cell, keep in (("CM_VLOW", k < 10), ("CM_MED", False), ("WM_VLOW", False), ("WM_MED", False)):
            i = "%s_%d" % (cell, k); plan.append({"id": i, "cell": cell})
            rows.append(_r(i, ALL if keep else set(), func=not cell.startswith("WM")))
    o = analyze(rows, plan)
    assert o["F6-P1"]["holds"] is True and o["F6-P1"]["VLOW"] == (10, 20)
    assert o["F6-P2"]["holds"] == "NOT_TESTABLE" and json.dumps(o)
