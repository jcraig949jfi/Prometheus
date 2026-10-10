import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analyze_c2r import analyze


def _row(lane, arm, w, at, lo_ticks, affected=10, step=100):
    cen = [{"tick": t, "alive": 5, "halves_func": {"LO": 1} if t in lo_ticks else {}} for t in range(step, at + 1000 + step, step)]
    return {"lane": lane, "arm": arm, "pair": w, "intervention": {"tick": at, "affected": affected}, "census": cen}


def test_directions():
    c23 = [_row("C2", "REMOVE", "w%d" % i, 500, {500, 600}) for i in range(8)]
    rem = [_row("C2R", "REMOVE", "w%d" % i, 500, {500, 600}) for i in range(8)]         # REMOVE back at +100
    slow = [_row("C2R", "RESET", "w%d" % i, 500, {500, 1200}) for i in range(8)]       # RESET back at +700
    near = [_row("C2R", "NEAR", "w%d" % i, 500, {500}) for i in range(8)]              # NEAR never
    o = analyze(rem + slow + near, c23)
    assert o["C2R-P1"]["holds"] is True and o["C2R-P1"]["faster"] == 8
    assert o["C2R-P2"]["holds"] is True and o["cells"]["NEAR"]["reacquired"] == 0
    fast = [_row("C2R", "RESET", "w%d" % i, 500, {500, 600}) for i in range(8)]        # ties -> NOT_TESTABLE
    o = analyze(rem + fast + near, c23)
    assert o["C2R-P1"]["holds"] == "NOT_TESTABLE"
    rev = [_row("C2R", "RESET", "w%d" % i, 500, {500, 600}) for i in range(8)]
    c23s = [_row("C2", "REMOVE", "w%d" % i, 500, {500, 900}) for i in range(8)]
    rems = [_row("C2R", "REMOVE", "w%d" % i, 500, {500, 900}) for i in range(8)]
    o = analyze(rems + rev + near, c23s)
    assert o["C2R-P1"]["holds"] is False and o["C2R-P1"]["faster"] == 0 and o["replay_invalid"] == []
    o = analyze(rem + rev + near, c23s)                                                 # census mismatch -> excluded
    assert len(o["replay_invalid"]) == 8 and o["C2R-P1"]["holds"] == "NOT_TESTABLE"


def test_fine_census():
    c23 = [_row("C2", "REMOVE", "w%d" % i, 500, {500, 600}) for i in range(6)]
    rem = [_row("C2R", "REMOVE", "w%d" % i, 500, {500, 520, 600}, step=20) for i in range(6)]
    res = [_row("C2R", "RESET", "w%d" % i, 500, {500, 580, 600}, step=20) for i in range(6)]
    o = analyze(rem + res, c23)
    assert o["replay_invalid"] == [] and o["C2R-P1"]["faster"] == 6 and o["cells"]["REMOVE"]["median_delay"] == 20
