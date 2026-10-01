"""Known-answer tests for lens_swap (promoted from W-M test_lens_ins6, T-INS-6/7). CPU only, 2 torch threads.
Every positive assertion is paired with the input that makes it FAIL, and
that failure is asserted too (a check that cannot fail is not a check).

    python -m pytest prometheus/ananke/tests/test_lens_swap.py -q
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import numpy as np
import pytest
import torch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, envs, lens, plants  # noqa: E402
from prometheus.ananke import lens_swap as L  # noqa: E402

torch.set_num_threads(2)
SEEDS = assays.world_seeds(0x7E57, 32)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=8)
MID = 6                          # HOLD: cue ticks 0,1; readout at offset 10
TRIALS = [1, 3, 5, 7]


def _latch():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    return ph, plants.plant("hold_latch", ph)


def _echo():
    ph = plants.c1b_echo_physics()
    return ph, plants.echo_hold(ph)[None]


def _null():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    return ph, plants.plant("null", ph)


def _scan(spec, offsets, mode="single", env=HOLD, seeds=SEEDS, trials=TRIALS):
    ph, g = spec
    return L.mixture_scan(ph, g, env, seeds, offsets, mode, trials, n_boot=200)["offsets"]


@pytest.fixture(scope="module")
def latch():
    return _scan(_latch(), [-1, MID])


@pytest.fixture(scope="module")
def echo():
    return _scan(_echo(), [-1, MID])


@pytest.fixture(scope="module")
def null():
    return _scan(_null(), [MID])


# ------------------------------------------------------------ KA6 batching
def test_batched_arms_bit_identical_to_lens_run():
    ph, g = _echo()
    ok = L.selfcheck(ph, g, HOLD, SEEDS, offset=MID, trial=3)
    assert all(ok.values()), ok


def test_batched_single_arm_differs_from_misplaced_hook():
    """Must-fail input for KA6: lens.run hooked at a DIFFERENT tick (trial 4
    instead of 3) must not match the batched single-trial arm."""
    ph, g = _echo()
    Pd = HOLD.period()
    r = L.run_arms(ph, g, HOLD, SEEDS, [L.Arm("x", tuple(L.FLIGHT), MID, 3)], early_stop=False)
    fn = lambda w: lens.swap(w, L.FLIGHT)
    good = lens.run(ph, g, HOLD, SEEDS, device="cpu", hooks={3 * Pd + MID: fn})
    bad = lens.run(ph, g, HOLD, SEEDS, device="cpu", hooks={4 * Pd + MID: fn})
    assert np.array_equal(good.trace, r.trace["x"])
    assert not np.array_equal(bad.trace, r.trace["x"])


def test_single_trial_arm_scores_only_its_trial():
    ph, g = _echo()
    r = L.run_arms(ph, g, HOLD, SEEDS, [L.Arm("n"), L.Arm("x", tuple(L.FLIGHT), MID, 3)])
    p = r.per_trial["x"]
    assert not np.isnan(p[:, 3]).any()
    assert np.isnan(np.delete(p, 3, axis=1)).all()
    # the swap flips the echo's trial-3 answer; normal is correct there
    assert (p[:, 3] == 0).all() and (r.per_trial["n"][:, 3] == 1).all()


# ------------------------------------------------------------ KA1-KA3 plants
def test_latch_is_site(latch):
    c = latch[MID]
    assert c["class"] == "SITE" and c["fS"] == 1.0 and c["identity"] == 1.0


def test_echo_is_channel(echo):
    c = echo[MID]
    assert c["class"] == "CHANNEL" and c["fC"] == 1.0 and c["identity"] == 1.0


def test_site_and_channel_assertions_fail_on_the_wrong_plant(latch, echo):
    """Must-fail inputs for KA1/KA2: echo is not SITE, latch is not CHANNEL,
    and neither reads as MIXTURE."""
    assert echo[MID]["class"] != "SITE"
    assert latch[MID]["class"] != "CHANNEL"
    assert "MIXTURE" not in (echo[MID]["class"], latch[MID]["class"])


def test_no_memory_is_undefined_not_a_carrier(null, latch):
    assert null[MID]["class"] == "UNDEFINED" and null[MID]["eligible"] == 0
    assert latch[MID]["class"] != "UNDEFINED"          # must-fail input for KA3


# ------------------------------------------------------------ KA5 identity
def test_identity_forced_after_cue_and_broken_before(latch, echo):
    """After the cue nothing mirror-different reaches the latch/echo readout:
    identity 1. A swap at o=-1 lets the mirror-different cue arrive after the
    swap: identity must break (the must-fail input)."""
    assert latch[MID]["identity"] == 1.0 and latch[MID]["identity_s0"] == 1.0
    assert latch[-1]["identity"] < L.MIN_IDENTITY
    assert latch[-1]["class"] == "IDENTITY-BROKEN"
    assert echo[-1]["class"] == "IDENTITY-BROKEN"


def test_identity_forced_in_relay_single_trial():
    ph = plants.c1b_da_physics()
    env = envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=8)
    g = plants.plant("relay_flood", ph)
    sc = L.mixture_scan(ph, g, env, SEEDS, [-1, 1, 2], "single", TRIALS, n_boot=100)["offsets"]
    for o in (1, 2):
        assert sc[o]["eligible"] >= L.MIN_ELIGIBLE and sc[o]["identity"] == 1.0
    assert sc[-1]["identity"] < L.MIN_IDENTITY       # must-fail input: swap before the cue


# ------------------------------------------------------------ KA4 statistic
def _synthetic(patterns, P=32, nt=10, seed=1):
    """Build per-trial arrays whose (pair, trial) patterns are drawn from
    `patterns` (dict pattern -> prob). Identity holds by construction for
    S/C/N; X breaks it."""
    rng = np.random.default_rng(seed)
    keys = list(patterns)
    pr = np.array([patterns[k] for k in keys], float)
    pat = rng.choice(keys, size=(P, nt), p=pr / pr.sum())
    normal = np.ones((2 * P, nt))
    site = np.zeros((2 * P, nt))
    chan = np.zeros((2 * P, nt))
    table = {"S": (0, 0, 1, 1), "C": (1, 1, 0, 0), "N1": (1, 0, 1, 0), "N2": (0, 1, 0, 1), "X": (1, 1, 1, 1)}
    for p in range(P):
        for k in range(nt):
            sA, sB, cA, cB = table[pat[p, k]]
            site[2 * p, k], site[2 * p + 1, k], chan[2 * p, k], chan[2 * p + 1, k] = sA, sB, cA, cB
    # raw readouts consistent with the outcomes: +1 / -1 targets, A = +1
    y = np.tile(np.array([1, -1]), P)[:, None]
    s0s = np.where(site == 1, y, -y) * 256
    s0c = np.where(chan == 1, y, -y) * 256
    return normal, site, chan, s0s, s0c


def _cen(patterns, **kw):
    n, s, c, a, b = _synthetic(patterns, **kw)
    r = L.census(n, s, c, a, b, n_boot=300)
    r["class"] = L.classify(r)
    return r


def test_sum_is_one_for_mixture_and_for_neither_but_census_separates_them():
    mix = _cen({"S": .5, "C": .5})
    nei = _cen({"N1": .5, "N2": .5})
    for r in (mix, nei):
        assert abs(r["site_acc"] + r["chan_acc"] - 1) < 1e-9
        assert abs(r["site_acc"] - 0.5) < 0.1
    assert mix["class"] == "MIXTURE" and mix["phi"] < -0.99
    assert nei["class"] == "NEITHER" and nei["phi"] > 0.99      # must-fail input for MIXTURE


def test_rare_channel_trials_give_phi_minus_one_but_not_mixture():
    """Degenerate-marginal trap: 95% S + 5% C gives phi = -1 exactly; the
    fraction rule (fC >= .15), not phi, must stop MIXTURE."""
    r = _cen({"S": .95, "C": .05})
    assert r["phi"] < -0.99
    assert r["class"] == "SITE"


def test_site_plus_neither_gives_positive_phi():
    r = _cen({"S": .6, "N1": .2, "N2": .2})
    assert r["phi"] > 0 and r["class"] == "UNRESOLVED"


def test_broken_identity_is_not_classified():
    r = _cen({"S": .4, "C": .3, "X": .3})
    assert r["identity"] < L.MIN_IDENTITY and r["class"] == "IDENTITY-BROKEN"


def test_too_few_eligible_is_undefined():
    r = _cen({"S": .5, "C": .5}, P=4, nt=2)
    assert r["eligible"] < L.MIN_ELIGIBLE and r["class"] == "UNDEFINED"


# ------------------------------------------------------------ KA7 designed handoff
def _design(key, gap):
    sys.path.insert(0, str(REPO / "roles/Ananke/research/designed_echoes"))
    import design
    torch.set_num_threads(2)
    ph, g, _ = design.build(key)
    return ph, g, dataclasses.replace(design.ENV0, gap=gap)


@pytest.fixture(scope="module")
def e2():
    ph, g, env = _design("E2_pipe2", 11)
    ro = env.cue_len + env.gap
    sc = L.mixture_scan(ph, g, env, assays.world_seeds(0x5F1, 32), list(range(-1, ro)), "single",
                        [2, 5, 8], n_boot=100)["offsets"]
    return sc, ro


@pytest.fixture(scope="module")
def e1():
    ph, g, env = _design("E1_canon", 7)
    ro = env.cue_len + env.gap
    sc = L.mixture_scan(ph, g, env, assays.world_seeds(0x5F1, 32), list(range(-1, ro)), "single",
                        [2, 5, 8], n_boot=100)["offsets"]
    return sc, ro


def test_E2_designed_channel_to_site_handoff(e2):
    sc, ro = e2
    h = L.handoff(sc, ro)
    assert h["pass"], (h, {o: (c["class"], c["fS"], c["fC"]) for o, c in sc.items()})


def test_handoff_rule_fails_on_E1_and_on_latch(e1):
    """Must-fail inputs for KA7: E1 (no pipeline, bit enters S0 at the last
    wake) fails (b); the latch (never channel) fails (a)."""
    sc, ro = e1
    assert not L.handoff(sc, ro)["b"]
    ls = _scan(_latch(), list(range(-1, 10)))
    assert not L.handoff(ls, 10)["a"]


# ------------------------------------------------------------ D1 follow census
def test_follow_census_reduces_to_frozen_census_when_both_correct():
    for pats in ({"S": .5, "C": .5}, {"N1": .5, "N2": .5}, {"S": .7, "X": .3}):
        n, s, c, a, b = _synthetic(pats)
        y = np.tile(np.array([1, -1]), n.shape[0] // 2)[:, None] * 256
        n_s0 = np.broadcast_to(y, n.shape).copy()
        f = L.census_follow(n_s0, a, b, np.ones(n.shape, bool), n_boot=50)
        r = L.census(n, s, c, a, b, n_boot=50)
        for k in ("eligible", "fS", "fC", "fN", "identity"):
            assert f[k] == r[k], (pats, k, f[k], r[k])


def test_follow_census_sees_an_abstainer_the_frozen_census_cannot():
    """Partner B abstains (S0 = 0) in every trial; site-carried bit: the
    chimera with A's site answers like A, the other abstains. Frozen census:
    0 eligible (UNDEFINED); follow census: SITE. Must-fail input: the same
    arrays with the chimeras swapped read CHANNEL, not SITE."""
    P, nt = 16, 4
    n_s0 = np.zeros((2 * P, nt), np.int64)
    n_s0[0::2] = 256
    site_s0 = np.zeros_like(n_s0)
    chan_s0 = np.zeros_like(n_s0)
    site_s0[1::2] = 256          # B's site arm = X = (site_A, chan_B) -> answers like A
    chan_s0[0::2] = 256          # A's chan arm = X
    normal = np.where(n_s0 == 0, 0.5, 1.0)
    fr = L.census(normal, np.where(site_s0 == 0, .5, 1.), np.where(chan_s0 == 0, .5, 1.), site_s0, chan_s0, n_boot=20)
    assert L.classify(fr) == "UNDEFINED"
    f = L.census_follow(n_s0, site_s0, chan_s0, np.ones(n_s0.shape, bool), n_boot=20)
    assert L.classify(f) == "SITE" and f["identity"] == 1.0
    g = L.census_follow(n_s0, chan_s0, site_s0, np.ones(n_s0.shape, bool), n_boot=20)
    assert L.classify(g) == "CHANNEL"


def test_follow_identity_is_sign_level_raw_identity_reported_separately():
    """HOLD case (LOG A7): the two copies of a chimera may differ in S0
    magnitude (distractors after the swap) but not in sign. Must-fail input:
    a sign difference breaks identity."""
    n, s, c, a, b = _synthetic({"S": 1.0})
    y = np.tile(np.array([1, -1]), n.shape[0] // 2)[:, None] * 256
    n_s0 = np.broadcast_to(y, n.shape).copy()
    f = L.census_follow(n_s0, a, b * 2, np.ones(n.shape, bool), n_boot=20)
    assert f["identity"] == 1.0 and f["identity_s0"] == 0.0 and L.classify(f) == "SITE"
    g = L.census_follow(n_s0, a, -b, np.ones(n.shape, bool), n_boot=20)
    assert g["identity"] == 0.0 and L.classify(g) == "IDENTITY-BROKEN"


# ------------------------------------------------------------ twin profile (axis a)
def test_twin_profile_matches_W_I_and_separates_latch_from_echo():
    sys.path.insert(0, str(REPO / "roles/Ananke/research/workers/W-I"))
    import traj
    ph, g = _echo()
    mine = L.twin_profile(ph, g, HOLD, 0x5EE, trials=(3, 5), M=16)
    ref = traj.twin_profile(ph, g, HOLD, 0x5EE, trials=(3, 5), M=16, device="cpu")
    for o, row in mine["avg"].items():
        for k, v in row.items():
            assert v == ref["avg"][o][k], (o, k)
    lph, lg = _latch()
    lat = L.twin_profile(lph, lg, HOLD, 0x5EE, trials=(3, 5), M=16)
    # echo: the cue difference is in flight mid-gap; latch: never in flight, always in S
    assert mine["avg"][MID]["fl_cnt"] + mine["avg"][MID]["fl_pay"] > 0.5
    assert lat["avg"][MID]["fl_cnt"] + lat["avg"][MID]["fl_pay"] == 0.0     # must-fail input: echo
    assert lat["avg"][MID]["S"] == 1.0
