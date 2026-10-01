"""Fast tests for swap_rel4 (REL4 = H2, variance-floored studentized pair bootstrap).

Frozen rule (plans/T-SWAP-REL4_PLAN.md s2 H2, s4 decision): DF=(s-.5)+(a-.5)/2, DN=(s-.5)-(a-.5)/2; 99% two-sided
REL3 BOOTT interval (B=2000 seed-0 counts) with t*_b = (m*_b-m)/(max(sd*_b, sd_floor)/sqrt P),
sd_floor = sqrt(1/(4K))/sqrt(P)*0.5; FLIP hi(DF)<0 > NO_EFFECT lo(DN)>0 > CHANCE lo(DF)>0 & hi(DN)<0; P_FLOOR 32.
Max FC table (%, F/N/C; K=3 | K=11 | K=12):
  P32  .91 .88 .48 | .96 .96 .60 | .99 .99 .65     P64  .77 .75 .52 | .75 .80 .61 | .76 .80 .65
  P128 .65 .70 .60 | .69 .66 .66 | .69 .69 .66     P256 .66 .68 .62 | .61 .66 .66 | .69 .65 .65
Run: python -m pytest -q roles/Ananke/research/workers/W-W/test_swap_rel4.py
"""
import importlib.util
import pathlib
import sys

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import swap_rel4 as r4  # noqa: E402


def _near_degenerate_flip(P=64, K=11, n_off=3):
    """a=1, s=0 on P-n_off pairs (exact flip, a~1); n_off pairs a=10/11, s=1/11. True verdict FLIP_REL."""
    a = np.ones(P)
    s = np.zeros(P)
    a[:n_off] = (K - 1) / K
    s[:n_off] = 1 / K
    return a, s


def test_constants_and_floor():
    assert r4.P_FLOOR == 32 and r4.N_BOOT == 2000 and r4.LEVEL == 0.99 and r4.METHOD == "H2"
    assert r4.sd_floor(64, 11) == pytest.approx(np.sqrt(1 / 44) / 8 * 0.5)
    assert all(max(v) <= r4.FC_MAX for v in r4.TABLE.values()) and len(r4.TABLE) == 12


def test_boot_counts_rows_sum_to_P():
    C = r4.boot_counts(32)
    assert C.shape == (2000, 32) and np.all(C.sum(1) == 32)


def test_h2_equals_rel3_on_nondegenerate_data():
    rng = np.random.default_rng(3)
    X = rng.binomial(11, 0.7, (50, 64)) / 11 - 0.5
    _, lo0, hi0 = r4.interval(X, method="BOOTT")
    _, lo2, hi2 = r4.interval(X, K=11)
    assert np.array_equal(lo0, lo2) and np.array_equal(hi0, hi2)


def test_h2_nested_in_rel3():
    rng = np.random.default_rng(4)
    a = rng.binomial(3, 0.99, (200, 32)) / 3
    s = 1 - a
    for x in ((s - .5) + (a - .5) / 2, (s - .5) - (a - .5) / 2):
        _, lo0, hi0 = r4.interval(x, method="BOOTT")
        _, lo2, hi2 = r4.interval(x, K=3)
        assert np.all(lo2 >= lo0) and np.all(hi2 <= hi0)


def test_recovers_near_degenerate_flip_that_rel3_misses():
    a, s = _near_degenerate_flip()
    assert str(r4.certificate(a, s, K=11)["verdict"]) == "FLIP_REL"
    assert str(r4.certificate(a, s, method="BOOTT")["verdict"]) == "INDETERMINATE"   # the REL3 blind spot


def test_point_interval_all_pairs_equal():
    a, s = np.ones(40), np.zeros(40)
    m, lo, hi = r4.interval((s - .5) + (a - .5) / 2, K=11)
    assert float(lo) == float(hi) == float(m) == -0.25
    assert str(r4.certificate(a, s, K=11)["verdict"]) == "FLIP_REL"


def test_known_no_effect_and_chance():
    rng = np.random.default_rng(7)
    a = rng.binomial(11, 0.9, 64) / 11
    assert str(r4.certificate(a, a.copy(), K=11)["verdict"]) == "NO_EFFECT_REL"
    s = np.full(64, 0.5)
    assert str(r4.certificate(a, s, K=11)["verdict"]) == "CHANCE_REL"


def test_fc_smoke_at_flip_boundary():
    """worst model, p=.7, z=-1/2, P32 K11, n=2000: FC(FLIP) must be small (grid value <= .96%); bound 2%."""
    rng = np.random.default_rng([99, 32, 11])
    p, z, K, P, n = 0.7, -0.5, 11, 32, 2000
    a = rng.binomial(K, p, (n, P)) / K
    s = rng.binomial(K, 0.5 + z * (p - 0.5), (n, P)) / K
    v = r4.certificate(a, s, K=K, C=r4.boot_counts(P))["verdict"]
    assert np.mean(v == "FLIP_REL") <= 0.02


def test_label_floor_guard_and_table():
    assert r4.label("FLIP_REL", 0.9, 16, 11)["label"] == "NOT_ELIGIBLE"          # below P_FLOOR
    assert r4.label("FLIP_REL", 0.45, 64, 11)["label"] == "NOT_ELIGIBLE"         # identification guard
    assert r4.label("FLIP_REL", 0.9, 64, 11)["label"] == "FLIP_REL"
    assert r4.label("FLIP_REL", 0.9, 64, 7)["label"] == "NOT_ELIGIBLE"           # untabulated design
    lab = r4.label("INDETERMINATE", 0.9, 64, 11, p_min={v: 1.0 for v in r4.CERTS})
    assert lab["label"] == "NOT_ELIGIBLE" and lab["reach_tabulated"]


def test_swap_verdict_end_to_end():
    M, T = 128, 11
    n = np.ones((M, T))
    sw = np.zeros((M, T))
    out = r4.swap_verdict_rel4(n, sw)
    assert out["label"] == "FLIP_REL" and out["P"] == 64 and out["K"] == 11


def test_matches_wu_rel3_boott_when_available():
    p = HERE.parent / "W-U" / "swap_rel3.py"
    if not p.exists():
        pytest.skip("W-U swap_rel3 not present")
    spec = importlib.util.spec_from_file_location("swap_rel3_wu", p)
    r3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r3)
    rng = np.random.default_rng(11)
    X = rng.binomial(3, 0.8, (20, 32)) / 3 - 0.5
    _, lo3, hi3 = r3.interval(X, "BOOTT")
    _, lo0, hi0 = r4.interval(X, method="BOOTT")
    assert np.array_equal(lo3, lo0) and np.array_equal(hi3, hi0)
