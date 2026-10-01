"""(8) Independence units + stratified / Simpson guard; (9) pairing-aware CIs, ratio guard, replication label.
Core only (no PTE import); W-Z's saved pair arrays and row table are read as plain data."""
from __future__ import annotations

import csv
import pathlib

import numpy as np
import pytest

from explib.outcomes import FAIL, PASS
from explib.stats import (Estimate, Units, cluster_bootstrap_ci, count_check, joint_arm_ci, margin,
                          mirror_pair_means, ratio_guard, replication_label, stratified)

REPO = pathlib.Path(__file__).resolve().parents[7]
WZ = REPO / "roles/Ananke/research/workers/W-Z/out"


def test_simpson_and_mixed_flags_with_unit_resampling():
    """W-R pattern: a pooled reading that matches no stratum. Two phases with opposite treatment effects
    and unbalanced arm composition: the pooled contrast has the opposite sign to both strata (SIMPSON)."""
    rng = np.random.default_rng(0)
    rows = []
    for ph, (n1, n0, p1, p0) in {"q0": (90, 10, 0.80, 0.90), "q1": (10, 90, 0.20, 0.30)}.items():
        for i in range(n1 + n0):
            arm = int(i < n1)
            rows.append((ph, arm, (p1 if arm else p0) + rng.normal(0, 0.01), f"{ph}-{i}"))
    ph, arm, val, uid = (np.array(x) for x in zip(*rows))
    r = stratified(val, ph, Units.of(uid, "world"), arm=arm, B=500)
    assert r["pooled"]["m"] > 0 and all(v["m"] < 0 for v in r["per_stratum"].values())
    assert "SIMPSON" in r["flags"] and r["label"] == "MIXED_ACROSS_STRATA"
    # NEGATIVE: balanced arms, same effect in both strata -> no flag
    rows = [(p, i % 2, float(rng.random() < (0.7 if i % 2 else 0.5)), f"{p}-{i}") for p in ("q0", "q1") for i in range(200)]
    ph, arm, val, uid = (np.array(x) for x in zip(*rows))
    assert stratified(val, ph, Units.of(uid, "world"), arm=arm, B=500)["label"] == "POOLED_OK"


def test_mixed_flag_on_means():
    v = np.r_[np.ones(40) * 0.9, np.ones(40) * 0.1] + np.random.default_rng(1).normal(0, 0.01, 80)
    st = np.r_[["q0"] * 40, ["q1"] * 40]
    r = stratified(v, st, Units.of(np.arange(80), "pair"), B=300)
    assert "MIXED" in r["flags"]


@pytest.mark.skipif(not (WZ / "row_table.csv").exists(), reason="W-Z data not present")
def test_AUDIT3_22_rows_are_10_units():
    """HISTORICAL (W-Z): arms of a group share one normal run, so the 22 inconsistent rows are 10 events.
    (Same lesson as W-O's '42 transfers' = 20 dependent groups, W-Q.)"""
    rs = list(csv.DictReader(open(WZ / "row_table.csv")))
    det = [r for r in rs if r["WU_status"] == "DETERMINED" and r["new_certificate"]]
    inc = [r for r in det if r["WU_rel3"] != r["new_certificate"]]
    assert len(det) == 301 and len(inc) == 22
    c = count_check(len(inc), Units.of([r["gid"] for r in inc], "specimen_x_offset_group"))
    assert c.outcome == FAIL and c.detail["units"] == 10
    assert count_check(10, Units.of([r["gid"] for r in inc], "g")).outcome == PASS


def _wz_certified_rows():
    rs = list(csv.DictReader(open(WZ / "row_table.csv")))
    det = [r for r in rs if r["WU_status"] == "DETERMINED" and r["new_certificate"] not in ("", "INDETERMINATE")]
    out = []
    con = {"DF": lambda m: (m["s"] - .5) + (m["a"] - .5) / 2, "DN": lambda m: (m["s"] - .5) - (m["a"] - .5) / 2}
    for r in det:
        d = np.load(WZ / "pairs" / f"{r['gid']}.npz")
        a = d["a__" + r["arm"]].astype(float).mean(1) / 4          # pair statistic in [0, 1]
        s = d["s__" + r["arm"]].astype(float).mean(1) / 4
        c = joint_arm_ci({"a": a, "s": s}, Units.of(np.arange(len(a)), "pair"), con, B=1000)
        cis = {k: (v["m"], v["lo"], v["hi"]) for k, v in c.items()}
        cert = r["new_certificate"]
        ci = cis["DF"] if cert == "FLIP_REL" else cis["DN"] if cert == "NO_EFFECT_REL" else \
            min(cis.values(), key=lambda t: margin(t, [0]))
        out.append((r["WU_rel3"] != cert, ci))
    return out


@pytest.mark.skipif(not (WZ / "pairs").exists(), reason="W-Z pair arrays not present")
def test_single_draw_certificates_near_threshold_W_Z():
    """HISTORICAL (AUDIT3 A3b): single-draw certificates near the bar flipped to INDETERMINATE (or back) on a
    new namespace (20 of the 22 inconsistencies sit on rows W-Z certified).
      - H-INST B4's rule 'within one half-width of a bar' can NEVER flag an issued one-sided certificate (its
        interval excludes the bar, so the margin is > 1): it catches 0 of 20. A guard that cannot fire.
      - The predictive replication rule (P(replicate certifies) < .95) catches 14/20 at inflation 1 and
        20/20 at inflation 2, at a cost of flagging some stable rows (reported, not asserted tightly)."""
    rows = _wz_certified_rows()
    flip = [ci for f, ci in rows if f]
    stable = [ci for f, ci in rows if not f]
    assert len(flip) == 20 and len(stable) == 256
    b4 = sum(replication_label(ci, [0], 1) == "MARGINAL" for ci in flip)
    p1 = sum(replication_label(ci, [0], 1, p_min=0.95) == "MARGINAL" for ci in flip)
    p2 = sum(replication_label(ci, [0], 1, p_min=0.95, inflation=2.0) == "MARGINAL" for ci in flip)
    cost2 = sum(replication_label(ci, [0], 1, p_min=0.95, inflation=2.0) == "MARGINAL" for ci in stable)
    assert b4 == 0
    assert p1 >= 12 and p2 == 20
    assert cost2 < 0.3 * len(stable)
    # with two agreeing namespaces the label is NEEDS_AGREEMENT, not MARGINAL
    assert replication_label(flip[0], [0], 2, p_min=0.95, inflation=2.0) == "NEEDS_AGREEMENT"


def test_joint_arm_ci_keeps_pairing_and_ratio_guard():
    """Arms that share one normal run: the joint (paired) interval of swap - normal is much narrower than
    resampling the arms separately would give, and a ratio of a single-draw or unlike estimator is refused
    (fleet `ratio_of_unlike_estimators`)."""
    rng = np.random.default_rng(3)
    normal = rng.random(256)
    swap = normal - 0.05 + rng.normal(0, 0.01, 256)
    u = Units.of(np.arange(256), "pair")
    j = joint_arm_ci({"n": normal, "s": swap}, u, {"d": lambda m: m["s"] - m["n"]}, B=800)["d"]
    sep_n = cluster_bootstrap_ci(normal, u, B=800, seed=1)
    sep_s = cluster_bootstrap_ci(swap, u, B=800, seed=2)
    sep_hw = ((sep_n["hi"] - sep_n["lo"]) ** 2 + (sep_s["hi"] - sep_s["lo"]) ** 2) ** 0.5 / 2
    assert j["hi"] < 0 and (j["hi"] - j["lo"]) / 2 < 0.2 * sep_hw
    good = Estimate(0.3, 0.2, 0.4, "mean_over_pairs", 3, "pair")
    assert ratio_guard(good, Estimate(0.6, 0.5, 0.7, "mean_over_pairs", 3, "pair")).outcome == PASS
    assert ratio_guard(good, Estimate(0.6, 0.5, 0.7, "median_of_5", 3, "pair")).outcome == FAIL
    assert ratio_guard(good, Estimate(0.6, 0.5, 0.7, "mean_over_pairs", 1, "pair")).outcome == FAIL
    assert ratio_guard(good, Estimate(0.1, -0.1, 0.3, "mean_over_pairs", 3, "pair")).outcome == FAIL


def test_mirror_pair_means_requires_a_perfect_matching():
    x = np.array([1.0, 0.0, 0.5, 0.5])
    assert mirror_pair_means(x).tolist() == [0.5, 0.5]
    with pytest.raises(ValueError):
        mirror_pair_means(x, pair_index=np.array([1, 0, 2, 3]))                  # unit paired with itself
