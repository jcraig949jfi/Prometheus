"""Fast tests for swap_rel3 (REL3). Run from W-U/: PYTHONPATH=<worktree> python -m pytest -q test_swap_rel3.py -p no:cacheprovider"""
import math
import pathlib
import sys

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "W-Q"))
import swap_rel3 as r3  # noqa: E402

TAB = r3.load_table()


def test_distributions_match_scipy():
    st = pytest.importorskip("scipy.stats")
    for df in (1, 3, 7, 15, 31, 63, 127, 255):
        for p in (0.95, 0.995, 0.9995):
            assert abs(r3.t_ppf(p, df) - st.t.ppf(p, df)) < 1e-7
    for p in (1e-6, 0.005, 0.3, 0.5, 0.995):
        assert abs(r3.norm_ppf(p) - st.norm.ppf(p)) < 1e-9
    assert abs(float(r3.norm_cdf(1.3)) - st.norm.cdf(1.3)) < 1e-12


def test_table_matches_module_constants():
    assert TAB["METHOD"] == r3.METHOD
    assert TAB["P_FLOOR"] == r3.P_FLOOR
    for P in (8, 16, 32, 64, 128, 256):
        for K in (3, 11, 12):
            d = TAB["designs"][f"P{P}_K{K}"]
            assert set(d["p_min"]) == set(r3.CERTS)
            if P < r3.P_FLOOR:
                assert not any(d["cert_ok"].values())


def test_tint_matches_simulation_implementation():
    import intervals as iv
    rng = np.random.default_rng(3)
    for P in (8, 32, 256):
        a = rng.binomial(11, 0.7, (200, P)) / 11
        s = rng.binomial(11, 0.45, (200, P)) / 11
        ref = iv.verdicts(a, s, r3.boot_counts(P))
        mine = r3.certificate(a, s)["verdict"]
        assert (ref[r3.METHOD] == mine).all()
        assert (ref["PCT"] == r3.certificate(a, s, method="PCT")["verdict"]).all()


def test_pct_is_rel2_certificate():
    import swap_rel2 as s2
    rng = np.random.default_rng(4)
    a = rng.binomial(11, 0.62, (50, 64)) / 11
    s = rng.binomial(11, 0.40, (50, 64)) / 11
    assert (s2.certificate(a, s)["verdict"] == r3.certificate(a, s, method="PCT")["verdict"]).all()


def _fc(method, P, K, n=4000, level=0.99):
    import swap_rel2 as s2
    rng = np.random.default_rng([99, P, K])
    a, s = s2.simulate("realistic", 0.7, -0.5, P, K, n, rng)
    return float(np.mean(r3.certificate(a, s, method=method, level=level)["verdict"] == "FLIP_REL"))


def test_mustfail_percentile_and_90pct_at_boundary():
    fc_rule = _fc(r3.METHOD, 32, 3)
    assert fc_rule <= 0.01
    assert _fc("TINT", 32, 3, level=0.90) > 0.03          # must-fail: a too-narrow interval
    assert _fc("PCT", 32, 3) > fc_rule                      # REL2 percentile is more permissive at P=32


def test_floor_and_must_fail_without_it():
    rng = np.random.default_rng(5)
    P = max(2, r3.P_FLOOR // 2)
    a = np.clip(rng.binomial(11, 0.9, P) / 11, 0, 1)
    s = 1 - a
    K = 11
    dz = {"cert_ok": {v: True for v in r3.CERTS}, "p_min": {v: 0.51 for v in r3.CERTS}}
    r = r3.from_pairs(a, s, K, dz=dz)
    if P < r3.P_FLOOR:
        assert r["label"] == "NOT_ELIGIBLE"
        assert r3.from_pairs(a, s, K, dz=dz, floor=0)["label"] == "FLIP_REL"   # must-fail: floor disabled


def test_guard():
    rng = np.random.default_rng(6)
    a = rng.binomial(11, 0.5, 256) / 11
    s = rng.binomial(11, 0.40, 256) / 11
    dz = TAB["designs"]["P256_K11"]
    assert r3.from_pairs(a, s, 11, dz=dz)["label"] == "NOT_ELIGIBLE"
    assert r3.from_pairs(a, s, 11, dz=dz, guard=False)["certificate"] == "FLIP_REL"


def test_end_to_end_flip_complete_and_partial():
    rng = np.random.default_rng(7)
    P, K = 64, 11
    a = rng.binomial(K, 0.8, P) / K
    r = r3.from_pairs(a, 1 - a, K, dz=TAB["designs"]["P64_K11"])
    assert r["label"] == "FLIP_REL" and r["zci"]["class"] == "COMPLETE"
    P = 256
    a = rng.binomial(K, 0.8, P) / K
    t = rng.random(P) < 0.8             # 80% transferred, rest fresh chance -> z ~ -0.8
    s = np.where(t, 1 - a, rng.binomial(K, 0.5, P) / K)
    r = r3.from_pairs(a, s, K, dz=TAB["designs"]["P256_K11"])
    assert r["label"] == "FLIP_REL" and r["zci"]["class"] == "PARTIAL"
    r = r3.from_pairs(a, a, K, dz=TAB["designs"]["P256_K11"])
    assert r["label"] == "NO_EFFECT_REL"


def test_world_arrays_entrypoint():
    rng = np.random.default_rng(8)
    M, T = 512, 12
    n = rng.binomial(1, 0.8, (M, T)).astype(float)
    n[:, 0] = np.nan
    r = r3.swap_verdict_rel3(n, 1 - n, table=TAB)
    assert r["P"] == 256 and r["K"] == 11 and r["label"] == "FLIP_REL"


def test_known_weakness_near_degenerate_high_accuracy():
    """Documented REL3 weakness (not a pass condition of the rule): with P=32 pairs all exact transfers
    at normal 1.0 except one pair, most bootstrap resamples have sd*=0 -> t*=+-inf and BOOTT withholds FLIP_REL,
    while the t-interval issues it. The frozen p_min rule turns this power dip at p~.99 into p_min=1.0."""
    a = np.ones(32)
    a[0] = 10 / 11
    s = 1 - a
    assert r3.certificate(a, s)["verdict"] != "FLIP_REL"
    assert r3.certificate(a, s, method="TINT")["verdict"] == "FLIP_REL"
    assert TAB["designs"]["P32_K11"]["p_min"]["FLIP_REL"] >= 0.99
