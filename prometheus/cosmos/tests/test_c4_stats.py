"""Regression tests for the R-STAT BLOCKING findings A1 and A4 (Ananke interim, ded6f5729).

A1: a family-constant predictor must FAIL S0-A. The v0.2 pooled statistic is kept here as the red reference
(it accepts the cheat), so a regression to pooled BA is caught.
A4: S2 must pass a planted universal law and reject planted family-specific laws.
"""
import numpy as np
import pytest

from prometheus.cosmos.c4 import calib_s2 as C
from prometheus.cosmos.c4 import power_s0 as V02
from prometheus.cosmos.c4 import stats as S

BASE = np.array([.8, .7, .5, .3, .2])


def _cheat(rng, n=160):
    fam = np.arange(n) % 5
    y = (rng.random(n) < BASE[fam]).astype(int)
    return y, (BASE[fam] >= .5).astype(int), np.ones(n, int), fam


def test_a1_red_reference_v02_pooled_statistic_accepts_cheat():
    rng = np.random.default_rng(1)
    y, c, t3, fam = _cheat(rng)
    assert V02.ba(y, c) - V02.ba(y, t3) >= V02.DELTA_A          # the defect, preserved


def test_a1_family_constant_cheat_has_zero_within_family_uplift():
    rng = np.random.default_rng(1)
    y, c, t3, fam = _cheat(rng)
    wf = S.within_family_uplift(y, c, t3, fam)
    assert abs(wf["U"]) < 1e-12 and all(abs(v) < 1e-12 for v in wf["per_family"].values())


@pytest.mark.parametrize("seed", range(10))
def test_a1_family_constant_cheat_fails_s0a(seed):
    rng = np.random.default_rng(seed)
    y, c, t3, fam = _cheat(rng)
    assert not S.s0a_verdict(y, c, t3, fam, rng, nflip=1000, nboot=200)["pass"]


def test_genuine_within_family_predictor_passes_s0a():
    rng = np.random.default_rng(3)
    ok = 0
    for _ in range(20):
        n = 240
        fam = np.arange(n) % 5
        y = (rng.random(n) < BASE[fam]).astype(int)
        c = np.where(rng.random(n) < .80, y, 1 - y)
        ok += S.s0a_verdict(y, c, np.ones(n, int), fam, rng, nflip=1000, nboot=200)["pass"]
    assert ok >= 18


def test_single_class_family_is_dropped_and_counted():
    y = np.array([1, 1, 1, 0, 1, 0])
    fam = np.array([0, 0, 0, 1, 1, 1])
    wf = S.within_family_uplift(y, y, np.ones(6, int), fam)
    assert wf["families_used"] == 1 and wf["families_dropped"] == [0]


def test_family_level_signflip_floor():
    rng = np.random.default_rng(0)
    n = 200
    fam = np.arange(n) % 5
    y = (rng.random(n) < .5).astype(int)
    assert S.family_level_signflip_p(y, y, 1 - y, fam) == pytest.approx(1 / 32)


def test_holm():
    assert S.holm({"a": .01, "b": .02, "c": .04}) == {"a": True, "b": True, "c": True}
    assert S.holm({"a": .01, "b": .03, "c": .04}) == {"a": True, "b": False, "c": False}


def _s2_rate(kind, nsim, seed, **kw):
    rng = np.random.default_rng(seed)
    ok = 0
    for _ in range(nsim):
        y, s, fam = C.planted(kind, 240, rng, **kw)
        ok += S.s2_verdict(y, s, C.lofo_p(y, s, fam), fam, rng, nperm=150)["pass"]
    return ok / nsim


def test_a4_universal_law_passes_s2():
    assert _s2_rate("UNIVERSAL", 30, 11) >= 0.80


@pytest.mark.parametrize("kind", ["FAM_OFFSET", "FAM_SLOPE"])
def test_a4_family_specific_law_fails_s2(kind):
    assert _s2_rate(kind, 20, 12) <= 0.10


def test_a6_equivalence_bound_declares_absence_only_when_tight():
    rng = np.random.default_rng(4)
    n = 2000
    fam = np.arange(n) % 5
    y = rng.integers(0, 2, n)
    noise = rng.integers(0, 2, n)
    assert S.equivalence_bound(y, noise, 1 - noise, fam, rng, nboot=300)["verdict"] == "ABSENT_ABOVE_MIN_EFFECT"
    small = slice(0, 60)
    assert S.equivalence_bound(y[small], noise[small], 1 - noise[small], fam[small], rng,
                               nboot=300)["verdict"] == "UNDETERMINED"


def test_a9_exclusion_bounds_bracket():
    rng = np.random.default_rng(5)
    n = 200
    fam = np.arange(n) % 5
    y = rng.integers(0, 2, n)
    a = np.where(rng.random(n) < .8, y, 1 - y)
    b = S.exclusion_bounds(y, a, fam, excluded_fam=np.arange(20) % 5)
    mid = np.nanmean([S.ba(y[fam == f], a[fam == f]) for f in range(5)])
    assert b["worst"] <= mid <= b["best"]


def test_newcombe_contains_truth():
    lo, hi = S.newcombe_diff(30, 100, 20, 100)
    assert lo < 0.10 < hi and lo > -0.05


def test_one_family_carrying_fails_s0a():
    from prometheus.cosmos.c4 import calib_s2 as C2
    rng = np.random.default_rng(8)
    assert C2.s0a_power_realistic(240, 10, rng, uplift=.10, carried=True, nflip=500, nboot=200) <= 0.1
