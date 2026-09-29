"""W-R pytest: phase-stratification bookkeeping (+ must-fail inputs) and a
small fork-runner identity check. CPU, 2 threads."""
import pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import torch
import pytest
torch.set_num_threads(2)
import fork
import specs

TRIALS = list(range(1, 12))


def test_phase_of_and_strata():
    assert fork.phase_of(1, 0, 19, 2) == 1 and fork.phase_of(2, 0, 19, 2) == 0
    assert fork.phase_of(1, 1, 19, 2) == 0 and fork.phase_of(4, 3, 11, 2) == 1   # 47 odd
    st = fork.strata(TRIALS, 0, 19, 2)
    assert st[1] == [1, 3, 5, 7, 9, 11] and st[0] == [2, 4, 6, 8, 10]
    st = fork.strata(TRIALS, 5, 19, 2)                       # offset flips the labels
    assert st[0] == [1, 3, 5, 7, 9, 11]
    st = fork.strata(TRIALS, 3, 16, 2)                       # even Pd (E2): one stratum empty
    assert st[0] == [] and st[1] == TRIALS
    assert fork.strata(TRIALS, 0, 17, 1) == {0: TRIALS}


def _synthetic(rule, M=128, nt=12, seed=0):
    """normal all correct; per (pair, trial) pattern S or C chosen by rule(k, pair)."""
    normal = np.ones((M, nt))
    site = np.ones((M, nt))
    chan = np.ones((M, nt))
    for k in range(nt):
        for pr in range(M // 2):
            if rule(k, pr) == "S":
                site[2 * pr:2 * pr + 2, k] = 0          # site arm follows partner -> wrong
            else:
                chan[2 * pr:2 * pr + 2, k] = 0
    s0 = lambda a: np.where(a == 1, 256, -256).astype(np.int64)
    return normal, site, chan, s0(site), s0(chan)


def _run(tab, labels_offset_shift=0, o=0, Pd=19):
    normal, site, chan, ss, sc = tab
    ns0 = np.full(normal.shape, 256, np.int64)
    scored = np.ones(normal.shape, bool)
    res = fork.stratified(normal, ns0, scored, {o: site}, {o: chan}, {o: ss}, {o: sc}, TRIALS,
                          [o + labels_offset_shift], Pd, 2, n_boot=300) if labels_offset_shift else \
        fork.stratified(normal, ns0, scored, {o: site}, {o: chan}, {o: ss}, {o: sc}, TRIALS, [o], Pd, 2, n_boot=300)
    return next(iter(res.values()))


def _phase_rule(Pd=19, o=0):
    return lambda k, pr: "S" if fork.phase_of(k, o, Pd, 2) == 0 else "C"


def test_phase_locked_mixture_resolves():
    r = _run(_synthetic(_phase_rule()))
    assert r["pooled"]["class"] == "MIXTURE"
    assert r["q0"]["class"] == "SITE" and r["q1"]["class"] == "CHANNEL"
    assert r["phase_effect"] and r["resolution"] == "RESOLVES"
    assert r["q0"]["eligible"] == 5 * 64 and r["q1"]["eligible"] == 6 * 64


def test_mustfail_labels_shifted_one_tick():
    """Labels computed for o+1 (one tick off) swap the per-phase classes."""
    tab = _synthetic(_phase_rule())
    normal, site, chan, ss, sc = tab
    ns0 = np.full(normal.shape, 256, np.int64)
    scored = np.ones(normal.shape, bool)
    # store the arrays under key 1 so stratified() labels them with offset 1 instead of 0
    r = fork.stratified(normal, ns0, scored, {1: site}, {1: chan}, {1: ss}, {1: sc}, TRIALS, [1], 19, 2,
                        n_boot=300)[1]
    assert r["q0"]["class"] == "CHANNEL" and r["q1"]["class"] == "SITE"
    assert not (r["q0"]["class"] == "SITE" and r["q1"]["class"] == "CHANNEL")


def test_mustfail_phase_independent_mixture_stays_mixed():
    rng = np.random.default_rng(3)
    draw = {(k, pr): ("S" if rng.random() < 0.5 else "C") for k in range(12) for pr in range(64)}
    r = _run(_synthetic(lambda k, pr: draw[(k, pr)]))
    assert r["pooled"]["class"] == "MIXTURE"
    assert r["q0"]["class"] not in fork.CLEAN and r["q1"]["class"] not in fork.CLEAN
    assert not r["phase_effect"] and r["resolution"] == "STAYS_MIXED"


def test_resolution_rule():
    assert fork.resolution("SITE", ["SITE", "CHANNEL"]) is None
    assert fork.resolution("MIXTURE", ["SITE", "CHANNEL"]) == "RESOLVES"
    assert fork.resolution("NEITHER", ["CHANNEL", "NEITHER"]) == "PARTLY"
    assert fork.resolution("UNRESOLVED", ["CHANNEL", "UNDEFINED"]) == "PARTLY"
    assert fork.resolution("UNRESOLVED", ["NEITHER", "UNRESOLVED"]) == "STAYS_MIXED"


def test_fork_identical_to_run_arms_small():
    from prometheus.ananke import assays, lens_swap as LS
    ph, env, g, _ = specs.load("PLANT2")
    seeds = assays.world_seeds(0x620, 8)
    offs, trials = [4, 5, 6], [1]
    ep, normal, ns0, site, chan, s0s, s0c = fork.fork_single(ph, g, env, seeds, offs, trials)
    arms = [LS.Arm(f"{nm}@{o}", tuple(LS.SITE if nm == "site" else LS.FLIGHT), o, 1)
            for o in offs for nm in ("site", "chan")]
    r = LS.run_arms(ph, g, env, seeds, arms, early_stop=False)
    for o in offs:
        assert np.array_equal(r.s0[f"site@{o}"][:, 1], s0s[o][:, 1])
        assert np.array_equal(r.s0[f"chan@{o}"][:, 1], s0c[o][:, 1])
    # must-fail: fork one tick late differs for the first offset
    _, _, _, site2, chan2, s0s2, s0c2 = fork.fork_single(ph, g, env, seeds, [5], trials, late=1)
    assert not (np.array_equal(s0s2[5][:, 1], s0s[5][:, 1]) and np.array_equal(s0c2[5][:, 1], s0c[5][:, 1]))
