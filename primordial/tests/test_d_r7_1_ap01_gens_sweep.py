"""D-R7-1: decision rule on synthetic checkpoint tables, bar recomputation, row equality (the sweep is the job's)."""
from primordial.cohorts.d import r7_1_ap01_gens_sweep as D

BAR = 100.0


def runs(h1, hm, h400_up, n=32):
    """32 runs; held(1) = h1, held(m) = hm, held(400) = hm + 1 for the first h400_up runs, else hm - 1."""
    out = []
    for i in range(n):
        h400 = hm + 1.0 if i < h400_up else hm - 1.0
        out.append({"family": 4200, "run_seed": i, "m": 80, "checkpoints": {
            "1": {"held_per_landscape_top1": h1}, "m": {"held_per_landscape_top1": hm},
            "400": {"held_per_landscape_top1": h400}}})
    return out


def test_no_search_signal():
    assert D.decide(True, True, runs(101.0, 105.0, 30), BAR)[0] == "NO_SEARCH_SIGNAL"


def test_stream_draw():
    got, st = D.decide(True, True, runs(90.0, 99.0, 30), BAR)
    assert got == "STREAM_DRAW" and st["Hm"] == 99.0


def test_saturated_and_boundary():
    assert D.decide(True, True, runs(90.0, 101.0, 21), BAR)[0] == "SATURATED"
    assert D.decide(True, True, runs(90.0, 101.0, 22), BAR)[0] == "MIXED"
    assert D.decide(True, True, runs(90.0, 101.0, 25), BAR)[0] == "MIXED"


def test_bar_absorbs_gain():
    got, st = D.decide(True, True, runs(90.0, 101.0, 26), BAR)
    assert got == "BAR_ABSORBS_GAIN" and st["s_held400_gt_heldm"] == 26


def test_equal_held_counts_as_not_rising():
    rr = runs(90.0, 101.0, 0)
    for x in rr:
        x["checkpoints"]["400"]["held_per_landscape_top1"] = 101.0
    assert D.decide(True, True, rr, BAR) == ("SATURATED", {"bar": BAR, "H1": 90.0, "Hm": 101.0, "s_held400_gt_heldm": 0})


def test_indeterminate():
    assert D.decide(False, True, runs(90.0, 101.0, 0), BAR)[0] == "INDETERMINATE"
    assert D.decide(True, False, runs(90.0, 101.0, 0), BAR)[0] == "INDETERMINATE"
    assert D.decide(True, True, runs(90.0, 101.0, 0, n=31), BAR)[0] == "INDETERMINATE"


def test_bar_reproduces_c_summary_from_committed_rows():
    runs_c, _, summ = D.load((D.ROOT / D.SRC_ROWS).read_text(encoding="utf-8"))
    ctrl = [runs_c[("control", f, rs)]["held_per_landscape_top1"] for f in D.FAMILIES for rs in range(8)]
    assert abs(D.bar_of(ctrl) - summ["bar"]) < 0.01
    assert sorted({int(runs_c[("cell", f, rs)]["gens_done"]) for f in D.FAMILIES for rs in range(8)})[0] >= 75


def test_same_compares_only_fields():
    a = {k: 1 for k in D.FIELDS}
    assert D.same(dict(a, extra=2), a) and not D.same(dict(a, held_per_landscape_top1=2), a)
