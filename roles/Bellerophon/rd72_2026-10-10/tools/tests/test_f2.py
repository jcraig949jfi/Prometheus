import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_f2 import analyze


def _r(i, both_ticks, func=True):
    cen = [{"tick": t, "halves_func": ({"BOTH": 1} if t in both_ticks else ({"LO": 1} if func else {}))} for t in range(100, 2100, 100)]
    return {"id": i, "census": cen, "pp": {"pp_correct": 10, "pp_denied": 4}}


def test_f2():
    plan, f2, f1 = [], [], []
    for k in range(20):
        plan += [{"id": "a%d" % k, "cell": "W0", "f1_id": "A%d" % k}, {"id": "b%d" % k, "cell": "KO1", "f1_id": "B%d" % k}]
        f2 += [_r("a%d" % k, set(range(100, 2100, 100)) if k < 10 else {100}), _r("b%d" % k, {900} if k < 6 else set())]
        f1 += [_r("A%d" % k, {100}), _r("B%d" % k, set())]
    o = analyze(f2, plan, f1)
    assert o["F2-P0"]["holds"] and o["F2-P0"]["paired"] == (10, 20) and o["F2-P0"]["kernel"] == (0, 20)
    assert o["F2-P1"]["holds"] and o["cells"]["W0"]["discord_both_end"] == [10, 0] and o["cells"]["KO1"]["pp_denied"] == 80
    o = analyze([_r(r["id"], {100} if r["id"].startswith("a") else set()) for r in f2], plan, f1)
    assert not o["F2-P0"]["holds"] and not o["F2-P1"]["holds"]
