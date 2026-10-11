import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_f5 import analyze


def _r(i, both, func=True):
    return {"id": i, "census": [{"tick": t, "halves_func": ({"BOTH": 1} if t in both else ({"LO": 1} if func else {}))} for t in range(100, 3100, 100)]}


def test_f5():
    plan, rows = [], []
    for k in range(20):
        plan += [{"id": "p%d" % k, "cell": "KO1_PHASED"}, {"id": "m%d" % k, "cell": "KO1_MED"}]
        rows += [_r("p%d" % k, set(range(800, 3100, 100)) if k < 7 else set()), _r("m%d" % k, {800} if k < 7 else set())]
    o = analyze(rows, plan)
    assert o["F5-P1"]["holds"] and o["F5-P1"]["PHASED"] == (7, 20) and o["cells"]["KO1_PHASED"]["first_before_switch"] == 7
    assert o["cells"]["KO1_MED"]["crossed"] == 7 and o["cells"]["KO1_MED"]["keep3000"] == 0 and json.dumps(o)
    o = analyze([_r(r["id"], set()) for r in rows], plan)
    assert not o["F5-P1"]["holds"]
