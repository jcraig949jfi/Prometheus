import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_f4 import analyze


def _r(i, both_ticks):
    return {"id": i, "census": [{"tick": t, "halves_func": ({"BOTH": 1} if t in both_ticks else {"LO": 1})} for t in range(100, 2100, 100)]}


def test_f4():
    ALL = set(range(100, 2100, 100)); plan, rows, f1 = [], [], []
    for k in range(20):
        plan += [{"id": "x%d" % k, "cell": "KO1_LOW", "f1_id": "M%d" % k}, {"id": "e%d" % k, "cell": "ECHOH_LOW", "f1_id": "E%d" % k},
                 {"id": "a%d" % k, "cell": "W0R_LOW"}, {"id": "b%d" % k, "cell": "W0R_MED"}]
        rows += [_r("x%d" % k, {1500, 1600} if k < 6 else set()), _r("e%d" % k, set()), _r("a%d" % k, ALL if k < 11 else {100}),
                 _r("b%d" % k, ALL if k < 1 else {100})]
        f1 += [_r("M%d" % k, set()), _r("E%d" % k, set())]
    o = analyze(rows, plan, f1)
    assert o["F4-X1"]["holds"] and o["F4-X1"]["LOW"] == (6, 20) and o["F4-X1"]["MED"] == (0, 20)
    assert o["F4-R"]["holds"] and o["cells"]["KO1_LOW"]["first"][0] == 1500 and json.dumps(o)
    o = analyze([_r(r["id"], set()) for r in rows], plan, f1)
    assert not o["F4-X1"]["holds"] and not o["F4-R"]["holds"]
