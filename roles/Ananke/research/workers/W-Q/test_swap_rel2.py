"""Fast tests for swap_rel2 (PLAN s4 V1, V2, V4). Every check is paired with the
input that makes it FAIL, and the test asserts that it does fail.
Run from W-Q/: python -m pytest -q test_swap_rel2.py -p no:cacheprovider"""
import pathlib
import sys

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "W-N"))
import swap_rel2 as s2  # noqa: E402
import swap_rel as wn  # noqa: E402  (W-N rule, imported read-only)

TABLE = s2.load_table()
D11 = TABLE["P256_K11"]


def _coupled(p, z, P=256, K=11, seed=0):
    """One realistic-model draw (pair-level coupled mixture) at normal p, relative swap z."""
    rng = np.random.default_rng(seed)
    a, s = s2.simulate("realistic", p, z, P, K, 1, rng)
    return a[0], s[0]


def _wn_gated(a, s, P=256, K=11):
    """W-N gated verdict on pair means (its gate: lo99(normal) >= p_min(P,K) from attain_table)."""
    idx = wn._boot_idx(P, wn.N_BOOT, 0)
    _, nlo, _ = wn._ci(a, idx)
    pm = wn.p_min(P, K)
    return str(wn.rule(a, s, idx=idx)["verdict"]) if nlo >= pm else "NOT_ELIGIBLE", float(nlo), pm


def _lo(a):
    C = s2.boot_counts(len(a))
    return float(np.quantile((a @ C.T) / len(a), 0.005))


# ---------------------------------------------------------------- certificate identity
def test_certificate_equals_wn_rule():
    rng = np.random.default_rng(3)
    for _ in range(60):
        P = int(rng.choice([16, 64, 256]))
        a, s = s2.simulate("worst", rng.uniform(.5, .95), rng.uniform(-1.2, 1.2), P, 11, 1, rng)
        assert str(wn.rule(a[0], s[0])["verdict"]) == str(s2.certificate(a[0], s[0])["verdict"])


def test_certificate_identity_must_fail_on_other_level():
    # must-fail: the same comparison against a 90% CI rule disagrees somewhere
    rng = np.random.default_rng(3)
    dis = 0
    for _ in range(200):
        a, s = s2.simulate("worst", rng.uniform(.52, .7), rng.uniform(-1, 1), 256, 11, 1, rng)
        dis += str(wn.rule(a[0], s[0])["verdict"]) != str(s2.certificate(a[0], s[0], level=0.90)["verdict"])
    assert dis > 0


# ---------------------------------------------------------------- tables (T1, T2)
def test_table_values_frozen_designs():
    assert all(D11["cert_ok"].values())
    assert (D11["p_min"]["FLIP_REL"], D11["p_min"]["NO_EFFECT_REL"], D11["p_min"]["CHANCE_REL"]) == (.57, .58, .59)
    assert all(TABLE["P256_K12"]["cert_ok"].values())
    # small designs: FLIP/NO_EFFECT certificates exceed the 1% FC target (percentile bootstrap)
    for k in ("P32_K3", "P64_K11"):
        assert not TABLE[k]["cert_ok"]["FLIP_REL"] and not TABLE[k]["cert_ok"]["NO_EFFECT_REL"]
        assert TABLE[k]["cert_ok"]["CHANCE_REL"]


def test_fc_target_met_at_052_and_must_fail_with_loose_level():
    ok = s2.rates("worst", 0.52, -0.5, 256, 11, 4000)["FLIP_REL"]
    loose = s2.rates("worst", 0.52, -0.5, 256, 11, 4000, level=0.80)["FLIP_REL"]
    assert ok <= s2.FC_MAX            # REL2 certificate at its boundary, normal .52
    assert loose > s2.FC_MAX          # must-fail: an 80% rule admits false FLIP_REL at .52


# ---------------------------------------------------------------- too strict (W-N gate)
def test_true_flip_at_060_certified_and_wn_gate_refuses():
    for seed in range(200):           # first seed with REL2 p_min_FLIP (.57) <= lo99 < W-N's .59
        a, s = _coupled(0.60, -1.0, seed=seed)
        v_wn, nlo, pm = _wn_gated(a, s)
        if D11["p_min"]["FLIP_REL"] <= nlo < pm:
            break
    assert D11["p_min"]["FLIP_REL"] <= nlo < pm
    c = str(s2.certificate(a, s)["verdict"])
    r = s2.label(c, nlo, 256, 11, dz=D11)
    assert r["label"] == "FLIP_REL" and r["strict"] == "FLIP_REL"
    assert v_wn == "NOT_ELIGIBLE"     # must-fail: the single worst-case gate suppresses it


# ---------------------------------------------------------------- too loose (guard)
def test_identification_guard_and_must_fail_without_it():
    rng = np.random.default_rng(11)
    a = rng.binomial(11, 0.5, 256) / 11            # no bit: normal .5
    s = rng.binomial(11, 0.47, 256) / 11           # swap with a bit-free bias
    c = str(s2.certificate(a, s)["verdict"])
    nlo = _lo(a)
    assert nlo <= 0.5 and c == "FLIP_REL"          # the raw certificate fires
    assert s2.label(c, nlo, 256, 11, dz=D11)["label"] == "NOT_ELIGIBLE"
    assert s2.label(c, nlo, 256, 11, dz=D11, guard=False)["label"] == "FLIP_REL"   # must-fail


# ---------------------------------------------------------------- per-verdict NE flags
def test_per_verdict_ne_and_must_fail_at_point_estimate():
    r = s2.label("INDETERMINATE", 0.575, 256, 11, dz=D11)
    assert r["label"] == "INDETERMINATE" and r["NE"] == ["NO_EFFECT_REL", "CHANCE_REL"]
    bad = s2.label("INDETERMINATE", 0.575, 256, 11, dz=D11, reach_at=0.60)   # point estimate
    assert "CHANCE_REL" not in bad["NE"]            # must-fail: it hides CHANCE's unreachability


def test_all_unattainable_is_not_eligible_but_certificate_survives():
    r = s2.label("INDETERMINATE", 0.53, 256, 11, dz=D11)
    assert r["label"] == "NOT_ELIGIBLE" and len(r["NE"]) == 3
    f = s2.label("FLIP_REL", 0.53, 256, 11, dz=D11)
    assert f["label"] == "FLIP_REL" and f["strict"] == "NOT_ELIGIBLE"


def test_small_design_cert_not_ok():
    d = TABLE["P32_K3"]
    assert s2.label("FLIP_REL", 0.95, 32, 3, dz=d)["label"] == "NOT_ELIGIBLE"
    assert s2.label("CHANCE_REL", 0.95, 32, 3, dz=d)["label"] == "CHANCE_REL"
    # must-fail: the P256 table would have admitted the same FLIP certificate
    assert s2.label("FLIP_REL", 0.95, 32, 3, dz=D11)["label"] == "FLIP_REL"


# ---------------------------------------------------------------- end to end on arrays
def test_swap_verdict_rel2_known_answers_and_must_fail():
    rng = np.random.default_rng(5)
    M, T = 512, 12
    x = (rng.random((M // 2, 1, T - 1)) < 0.62).astype(float)
    n = np.concatenate([np.repeat(x, 2, 1).reshape(M, T - 1), np.full((M, 1), np.nan)], 1)[:, ::-1]
    flip = 1 - n
    same = n.copy()
    r = s2.swap_verdict_rel2(n, flip, dz=D11)
    assert r["K"] == 11 and r["P"] == 256
    assert r["label"] == "FLIP_REL" and abs(r["z"] + 1) < 1e-9
    assert s2.swap_verdict_rel2(n, same, dz=D11)["label"] == "NO_EFFECT_REL"
    # must-fail: feeding the NO-EFFECT arm to the FLIP check
    assert s2.swap_verdict_rel2(n, same, dz=D11)["label"] != "FLIP_REL"
