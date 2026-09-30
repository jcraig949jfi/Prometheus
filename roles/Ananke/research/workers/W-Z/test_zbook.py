"""Small bookkeeping tests for W-Z (no engine runs)."""
import numpy as np

import zcommon as Z
import run_z as RZ


def test_order_covers_all_groups_ambiguous_first():
    first, rest = Z.order()
    g = Z.groups()
    assert len(first) == 31 and len(first) + len(rest) == len(g) == 249
    assert set(first).isdisjoint(rest)
    r3 = Z.rel3_rows()
    assert sum(r3[x["vid"]]["status"] == "AMBIGUOUS" for k in first for x in g[k]) == 64
    assert sum(len(v) for v in g.values()) == 733


def test_group_class():
    assert Z.group_class([("FLIP_REL", "COMPLETE"), ("CHANCE_REL", "")]) == "CARRIER-NAMED"
    assert Z.group_class([("FLIP_REL", "PARTIAL"), ("FLIP_REL", "PARTIAL")]) == "CARRIER-PARTIAL"
    assert Z.group_class([("FLIP_REL", "PARTIAL"), ("FLIP_REL", "OVERSHOOT")]) == "CARRIER-OVERSHOOT"
    assert Z.group_class([("INDETERMINATE", ""), ("NO_EFFECT_REL", "")]) == "NO-CARRIER-FOUND"
    assert Z.group_class([("INDETERMINATE", ""), ("NOT_ELIGIBLE", "")]) == "UNDECIDED"
    # must-fail: a PARTIAL-only FLIP group is never CARRIER-NAMED
    assert Z.group_class([("FLIP_REL", "PARTIAL")]) != "CARRIER-NAMED"


def test_pair_arrays_roundtrip_reproduce_label_inputs():
    rng = np.random.default_rng(1)
    Mw, nt = 16, 5
    npt = rng.choice([0.0, 0.5, 1.0], size=(Mw, nt))
    spt = rng.choice([0.0, 0.5, 1.0], size=(Mw, nt))
    npt[:, 0] = np.nan          # unscored trial
    spt[3, 2] = np.nan          # one unscored swap cell
    trials = [1, 2, 3, 4]
    at, st, a, b, K, cells, ok = RZ.arm_pairs(npt, spt, trials)
    ea, es = RZ.enc(at), RZ.enc(st)
    da = np.where(ea == 255, np.nan, ea / 4.0)
    ds = np.where(es == 255, np.nan, es / 4.0)
    # over-trial pair means rebuilt from the saved per-trial arrays (weights = both-scored cells per pair-trial)
    both = ~np.isnan(np.where(np.isnan(npt) | np.isnan(spt), np.nan, 1.0)[:, trials])
    w = both.reshape(Mw // 2, 2, -1).sum(1)
    ra = np.nansum(np.nan_to_num(da) * w, 1) / w.sum(1)
    rs = np.nansum(np.nan_to_num(ds) * w, 1) / w.sum(1)
    assert np.allclose(ra[ok], a) and np.allclose(rs[ok], b)
    assert cells == int(both.sum()) and K == round(cells / (2 * len(a)))
