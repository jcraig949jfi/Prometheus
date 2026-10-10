import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_f1 import analyze


def _r(i, both_ticks, func=True):
    cen = [{"tick": t, "halves_func": ({"BOTH": 1} if t in both_ticks else ({"LO": 1} if func else {}))} for t in range(100, 2100, 100)]
    return {"id": i, "census": cen}


def test_f1_branches():
    plan = []; rows = []
    for k in range(10):
        plan += [{"id": "w%d" % k, "cell": "W0", "arm": "ON"}, {"id": "a%d" % k, "cell": "KO1", "arm": "ON", "founder_halves": "LO"},
                 {"id": "b%d" % k, "cell": "KO1", "arm": "OFF", "founder_halves": "LO"}, {"id": "c%d" % k, "cell": "REP", "arm": "ON"}]
        rows += [_r("w%d" % k, set(range(100, 2100, 100))), _r("a%d" % k, {800, 900} if k < 7 else set()),
                 _r("b%d" % k, set()), _r("c%d" % k, set())]
    o = analyze(rows, plan)
    assert o["F1-P0"]["holds"] is True and o["F1-P1"]["holds"] and o["F1-P2"]["holds"]
    assert o["cells"]["KO1|ON"]["crossed"] == 7 and o["cells"]["KO1|ON"]["median_first_cross"] == 800
    assert o["cells"]["KO1|ON"]["by_founder"]["LO"] == [7, 10]
    rows2 = [_r("w%d" % k, {100}) for k in range(10)] + rows[10:]
    o = analyze(rows2, plan)
    assert o["F1-P0"]["holds"] is False
    rows3 = [_r(r["id"], set()) for r in rows]
    o = analyze(rows3, plan)
    assert not o["F1-P1"]["holds"] and not o["F1-P2"]["holds"]
