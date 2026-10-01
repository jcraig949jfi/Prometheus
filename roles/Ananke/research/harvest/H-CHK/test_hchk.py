"""Bookkeeping tests for hchk.py (z CI, twin construction, theta encoding, frozen readings)."""
import os, sys
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import hchk as H


def _pt(a_acc, s_acc, M=128, K=5, seed=1):
    r = np.random.default_rng(seed)
    n = (r.random((M, K)) < a_acc).astype(float)
    return n, s_acc(n, r)


def test_z_full_flip_and_no_effect():
    n, s = _pt(.7, lambda n, r: 1 - n)
    z = H.z_ci(n, s)
    assert abs(z["z"] + 1) < 1e-9 and z["lo"] <= -1 <= z["hi"]
    n, s = _pt(.7, lambda n, r: n.copy())
    assert abs(H.z_ci(n, s)["z"] - 1) < 1e-9
    n, s = _pt(.7, lambda n, r: (r.random(n.shape) < .5).astype(float))   # must-fail: chance is not z<=-.95
    assert H.z_ci(n, s)["z"] > -0.5


def test_twin_episode_differs_only_in_target_cue():
    pr = H.mod("wn_pr")
    pr.nb.install()
    ph = pr.nb.m2()[0]
    env = pr.nb.spec(2)
    from prometheus.ananke import assays
    seeds = assays.world_seeds(0x77, 8)
    k = 6
    ep = H.twin_episode(ph, env, seeds, k, 2)
    sv = ep.schedule.sense_val.numpy()
    Pd = env.period()
    d = np.flatnonzero((sv[:, 0] != sv[:, 1]).any(-1))
    assert list(d) == list(range((k - 2) * Pd, (k - 2) * Pd + env.cue_len))
    assert ep.y[1, k] == -ep.y[0, k] and ep.scored[:, k].all() and ep.scored.sum() == 8
    ep2 = H.twin_episode(ph, env, seeds, k, 2, back_extra=1)
    assert ep2.y[1, k] == ep2.y[0, k]
    d2 = np.flatnonzero((ep2.schedule.sense_val.numpy()[:, 2] != ep2.schedule.sense_val.numpy()[:, 3]).any(-1))
    assert d2[0] == (k - 3) * Pd


def test_theta_encoding():
    ph0, env, _ = H.champ()
    ph = H.c1_physics(ph0)
    assert ph.dest_mode == "sample" and ph.loss == 0.1 and ph.lat_jitter == 1 and ph.fanout == 8
    for j in (1, 3, 12):
        g = H.c1_genome(ph, j)
        assert (2 * j - 1) << 7 == H.theta_of(j) and g[0, 10, 4] == 2 * j - 1 and g[0, 10, 3] == 7


def test_reading_c3():
    base = {("P1S", "a"): -1.0, ("P1S", "b"): -1.0}
    same = {**base, **{("n1_s0", "a"): -.95, ("n1_s0", "b"): -1.0, ("n2_s2", "a"): -1.06, ("n2_s2", "b"): -.98}}
    assert H.reading_c3(same) == "NOT CONFIRMED"
    conf = {**base, **{("n1_s0", "a"): -.96, ("n1_s0", "b"): -.2, ("n2_s2", "a"): -1.0, ("n2_s2", "b"): .1}}
    assert H.reading_c3(conf) == "CONFUSION CONFIRMED"
    bad_p1s = {**conf, ("P1S", "b"): -.5}       # must-fail: P1S not flipping under (b) -> not confirmed
    assert H.reading_c3(bad_p1s) != "CONFUSION CONFIRMED"
