"""W-V bookkeeping tests (PLAN s1 T1-T4 + classifier). Small M, 1 thread.
PYTHONDONTWRITEBYTECODE=1 python -m pytest roles/Ananke/research/workers/W-V/test_wv.py -q -p no:cacheprovider"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import pytest
import torch

import wv
import ana
from prometheus.ananke import assays, envs, lens_swap as LS
from prometheus.ananke.engine import Controls, World

M = 8


def _setup(name):
    ph, env, g, _ = wv.load(name)
    seeds = assays.world_seeds(0x659, M)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    return ph, env, g, seeds, ep, ws1


@pytest.mark.parametrize("name", ["4781b0a1", "PMAJ"])
def test_T1_T2_tagworld_identical_and_decomposes(name):
    ph, env, g, seeds, ep, ws1 = _setup(name)
    a = World(ph, np.repeat(g[None], M, 0), ws1, device="cpu", ctrl=Controls(), schedule=ep.schedule)
    b = wv.TagWorld(ph, np.repeat(g[None], M, 0), ws1, device="cpu", ctrl=Controls(), schedule=ep.schedule)
    bi = torch.arange(M)
    seen = 0
    for t in range(3 * env.period()):
        a.step()
        b.step()
        assert torch.equal(b.Msum[:, bi, b.ro], b.Tsum.sum(2)), t        # T2
        assert torch.equal(b.Mcnt[:, bi, b.ro], b.Tcnt.sum(2)), t
        seen += int(b.Tcnt[:, :, :5].sum())
    assert a.digest() == b.digest()                                        # T1
    assert np.array_equal(a.trace.numpy(), b.trace.numpy())
    assert seen > 0                                                        # sensors do send to the readout


def _one_fork(name, arms, o=4, k=2):
    ph, env, g, seeds, ep, ws1 = _setup(name)
    r = wv.run(ph, g, env, seeds, [o], [k], arms=arms)
    return r


def test_T3_empty_swap_is_normal():
    r = _one_fork("4781b0a1", [("none", "tag", ()), ("s0", "tag", (0,))])
    assert np.array_equal(r["arm_s0"][0, 0, :, 2], r["normal_s0"][:, 2])


@pytest.mark.parametrize("name", ["PMAJ", "PDICT"])
def test_T4_all5_equals_flight_a_in_plants(name):
    r = _one_fork(name, [("ALL5", "tag", tuple(range(5))), ("FLA", "fla", ())])
    assert np.array_equal(r["arm_s0"][0, 0, :, 2], r["arm_s0"][1, 0, :, 2])
    # and the swap moves the readout at all (all 5 votes in flight at o4)
    assert not np.array_equal(r["arm_s0"][0, 0, :, 2], r["normal_s0"][:, 2])


def test_follow_scoring():
    ns0 = np.array([[256], [-256], [256], [-256]])
    arm = np.array([[-5], [-256], [0], [9]])
    elig, f = ana.follow_table(ns0, arm, np.array([[1], [-1], [1], [-1]]), np.ones((4, 1), bool), [0])
    assert elig.tolist() == [[True], [True]]
    assert f[:, 0].tolist() == [0.5, 0.5]            # pair0: A follows, B own; pair1: 0 -> not follow, B follows


def _eff(e, lo=None, hi=None):
    return {"e": e, "lo": e - 0.04 if lo is None else lo, "hi": e + 0.04 if hi is None else hi}


def _tab(s, c, E, dpiv, dlo, drop_lo=None):
    t = {f"s{j}": _eff(v) for j, v in enumerate(s)}
    t.update({f"c{j}": _eff(v) for j, v in enumerate(c)})
    t["ALL5"] = _eff(E)
    t["drop"] = {j: {"lo": (E - c[j] - 0.04) if drop_lo is None else drop_lo[j]} for j in range(5)}
    t["piv"] = {"D": dpiv, "lo": dlo}
    t["n"] = 300
    return t


def test_classifier_known_tables():
    maj = _tab([.22] * 5, [.78] * 5, 1.0, 1.0, .9)
    assert ana.classify(maj)[0] == "MAJORITY"
    dic = _tab([0, 0, 0, 0, 1.0], [1, 1, 1, 1, 0], 1.0, .1, 0)
    dic["s0"] = dic["s1"] = dic["s2"] = dic["s3"] = _eff(0.0, 0.0, 0.01)
    assert ana.classify(dic) == ("DICTATOR", (4,))
    sub = _tab([.5, .5, 0, 0, 0], [.5, .5, 1, 1, 1], 1.0, .1, 0)
    for j in (2, 3, 4):
        sub[f"s{j}"] = _eff(0.0, 0.0, 0.01)
    assert ana.classify(sub) == ("SUBSET", (0, 1))
    red = _tab([0] * 5, [1] * 5, 1.0, 0, 0)
    for j in range(5):
        red[f"s{j}"] = _eff(0.0, 0.0, 0.01)
    assert ana.classify(red)[0] == "REDUNDANT-JOINT"
    maj_nopiv = _tab([.22] * 5, [.78] * 5, 1.0, 0.1, -0.1)      # MF3 shape
    assert ana.classify(maj_nopiv)[0] == "DISTRIBUTED-NONMAJ"
    low = _tab([.1] * 5, [.3] * 5, 0.4, 1, 1)
    assert ana.classify(low)[0] == "NOT-INFORMATIVE"


def test_T5_fla_equals_ws_flight_a_runner():
    """My per-offset fork == W-S probe.fork (fork at o_min + hooks; KA-F-checked vs lens_swap.run_arms)."""
    sys.path.insert(0, str(HERE.parent / "W-S"))
    import probe
    ph, env, g, seeds, ep, ws1 = _setup("4781b0a1")
    r = wv.run(ph, g, env, seeds, [4, 8], [2], arms=[("FLA", "fla", ())])
    ref = probe.fork(ph, g, env, seeds, [4, 8], [2], kinds=("flight_a",), cue=False)
    for oi, o in enumerate([4, 8]):
        assert np.array_equal(r["arm_s0"][0, oi, :, 2], ref["res"]["flight_a"][o][1][:, 2])
