import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_f3 import analyze


def _r(i, both_ticks):
    return {"id": i, "census": [{"tick": t, "halves_func": ({"BOTH": 1} if t in both_ticks else {"LO": 1})} for t in range(100, 2100, 100)]}


def test_f3():
    ALL = set(range(100, 2100, 100)); plan, f3, f1 = [], [], []
    for k in range(20):
        plan += [{"id": "v%d" % k, "cell": "W0_VLOW", "arm": "ON", "f1_id": "M%d" % k},
                 {"id": "l%d" % k, "cell": "W0_LOW", "arm": "ON", "f1_id": "M%d" % k},
                 {"id": "o%d" % k, "cell": "W0_VLOW", "arm": "OFF", "f1_id": "X%d" % k}]
        f3 += [_r("v%d" % k, ALL if k < 12 else {100}), _r("l%d" % k, ALL if k < 3 else {100}), _r("o%d" % k, {100})]
        f1 += [_r("M%d" % k, ALL if k < 1 else {100})]
    o = analyze(f3, plan, f1)
    assert o["F3-P0"]["holds"] and o["F3-P0"]["VLOW"] == (12, 20) and o["F3-P0"]["MED"] == (1, 20)
    assert not o["F3-P1"]["holds"] and o["VLOW_OFF_vs_ON"]["OFF"] == (0, 20)
    assert o["cells"]["W0_MED|ON"]["n"] == 20 and json.dumps(o)
