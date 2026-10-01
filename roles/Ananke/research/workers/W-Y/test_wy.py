"""W-Y instrument tests (small, CPU, dev namespace 0x67f).
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python -m pytest roles/Ananke/research/workers/W-Y/test_wy.py -q -p no:cacheprovider"""
import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import wy  # noqa: E402
import wyana  # noqa: E402
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402

M = 16


def _small(name, offsets=(8,), trials=(3, 4)):
    ph, env, g, _ = wy.load(name)
    seeds = assays.world_seeds(0x67F, M)
    arms = wy.arm_list(name != "4781b0a1")
    return wy.run(ph, g, env, seeds, list(offsets), list(trials), arms, j=7,
                  jx=22 if name != "4781b0a1" else None), arms


def test_normal_arm_bit_identical_plant_and_champion():
    for name in ("PA", "4781b0a1"):
        r, arms = _small(name, offsets=(10,), trials=(3,))
        a = arms.index(("NORMAL", "normal"))
        assert (r["arm_s0"][a, 0, :, 3] == r["normal_s0"][:, 3]).all()


def test_arm_swaps_touch_only_their_target():
    ph, env, g, _ = wy.load("4781b0a1")
    seeds = assays.world_seeds(0x67F, M)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws1, device="cpu", ctrl=Controls(), schedule=ep.schedule)
    for _ in range(2 * env.period() + 10):
        w.step()
    ro = torch.as_tensor(ep.schedule.read_idx[:, 0], dtype=torch.int64)
    rows = torch.arange(M)
    ar = torch.arange(M)
    for kind in ("kp7", "kpall", "fla", "kp7fla", "site_r"):
        s0 = {n: v.clone() for n, v in w.state_arrays().items()}
        w2 = World(ph, np.repeat(g[None], M, 0), ws1, device="cpu", ctrl=Controls(), schedule=ep.schedule)
        wy._tile_state(w, w2, 1)
        wy.apply_arm(w2, kind, rows, ro, j=7)
        after = w2.state_arrays()
        for n, v in s0.items():
            changed = (after[n] != v)
            if n == "Kp" and kind in ("kp7", "kp7fla"):
                assert (after[n][ar, ro, 7] == v[ar ^ 1, ro, 7]).all()
                changed[ar, ro, 7] = False
            if n == "Kp" and kind in ("kpall", "site_r"):
                assert (after[n][ar, ro] == v[ar ^ 1, ro]).all()
                changed[ar, ro] = False
            if n in ("Msum", "Mcnt") and kind in ("fla", "kp7fla"):
                assert (after[n][:, ar, ro] == v[:, ar ^ 1, ro]).all()
                changed[:, ar, ro] = False
            if n != "Kp" and n not in ("Msum", "Mcnt") and kind == "site_r":
                changed[ar, ro] = False
            assert not changed.any(), (kind, n)


def test_plant_A_kp7_carries_plant_B_constant():
    rA, _ = _small("PA", offsets=(12,), trials=(3, 4, 5))
    rB, _ = _small("PB", offsets=(12,), trials=(3, 4, 5))
    assert rA["cen_kp7_diff"][0][:, [3, 4, 5]].mean() > 0.5
    assert rB["cen_kp7_diff"][0][:, [3, 4, 5]].mean() == 0.0
    assert (rB["cen_kp7_val"][0][:, [3, 4, 5]] == 1).all()


def _tab(kp, fla, joint, site=None, dlo=None, dhi=None, n=200):
    d = joint[0] - max(kp[0], fla[0])
    t = {"n": n, "KP7": dict(zip("e lo hi".split(), kp)), "FLA": dict(zip("e lo hi".split(), fla)),
         "KP7+FLA": dict(zip("e lo hi".split(), joint)),
         "SITE_R": {"e": site if site is not None else fla[0]},
         "diff": {"e": d, "lo": d - .08 if dlo is None else dlo, "hi": d + .08 if dhi is None else dhi}}
    return t


def test_classifier_synthetic():
    assert wyana.classify(_tab((.4, .33, .47), (.6, .53, .67), (1, 1, 1))) == "KP7 IS THE READOUT HALF"
    assert wyana.classify(_tab((.6, .53, .67), (.6, .53, .67), (.62, .55, .69))) == "KP7 REDUNDANT"
    assert wyana.classify(_tab((.0, .0, .01), (.6, .53, .67), (.6, .53, .67))) == "KP7 NOT A CARRIER"
    assert wyana.classify(_tab((.1, .05, .15), (.6, .53, .67), (.7, .6, .8))) == "UNRESOLVED"
    assert wyana.classify(_tab((.4, .33, .47), (.3, .2, .4), (.5, .4, .6), site=.4)) == "NOT-INFORMATIVE"
    assert wyana.classify({"n": 5}) == "UNDEFINED"
