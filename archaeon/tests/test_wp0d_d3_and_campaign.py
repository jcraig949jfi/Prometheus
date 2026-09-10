"""WP-0d: reconcile D3's null rate; correct the campaign's statistical
description; pin the sealed plan.

    0d-a  exact F-tail reproduces Harmonia's 0.106 at the floor; simulation
          agrees within its own uncertainty; the pure_null geometry gives ~0
    0d-b  denominators: eligible count, zero-variance neighbourhoods counted
          as skipped-not-fired, per-region and per-corpus reported separately
    0d-c  exact small-L enumeration: mean 1/2, variance 1/(4L); 24 vs 28 differ
    0d-d  plan assignments agree with the declared levels; the sealed plan's
          spec hashes are unchanged by the metadata correction
"""
from __future__ import annotations

import itertools
import hashlib

from archaeon import calibrate_d3_null as C
from archaeon import config as cfg
from archaeon import synth
from archaeon.detectors import d3_variance_anomaly as d3
from archaeon.producer import campaign, specbuild


D = cfg.DEFAULT.detectors


# ---------------------------------------------------------------- 0d-a
def test_exact_f_tail_at_floor_reproduces_harmonias_rate():
    p = C.d3_false_alarm_exact(D.d3_min_n_region, D.d3_min_n_neighborhood,
                               D.d3_low_ratio, D.d3_high_ratio)
    # Harmonia: 0.106 from 20,000 draws (SE ~0.002). Exact F(7,15) tail.
    assert 0.100 <= p <= 0.112, p


def test_simulation_agrees_with_exact_within_uncertainty():
    exact = C.d3_false_alarm_exact(8, 16, D.d3_low_ratio, D.d3_high_ratio)
    sim = C.d3_false_alarm_sim(8, 16, D.d3_low_ratio, D.d3_high_ratio,
                               draws=20_000, seed=20260907)
    assert abs(sim["rate"] - exact) <= 3.5 * sim["se"], (sim, exact)


def test_pure_null_geometry_explains_the_zero():
    rec = C.reconcile(draws=2_000, seeds=20)
    g = rec["archaeon_pure_null_geometry"]
    assert g["n_region"] >= 80 and g["n_neighbourhood"] >= 320
    assert g["exact"] < 1e-6
    assert rec["harmonia_floor"]["exact"] > 0.09


def test_betainc_identities():
    assert C.betainc(1, 1, 0.3) == 0.3 or abs(C.betainc(1, 1, 0.3) - 0.3) < 1e-12
    assert abs(C.f_cdf(1.0, 5, 5) - 0.5) < 1e-9      # F(d,d) median is 1


# ---------------------------------------------------------------- 0d-b
def test_floor_corpora_through_d3_report_denominators_and_fire_near_rate():
    r = C.d3_on_null_corpora(seeds=150, geometry="floor")
    assert r["region_tests"] == 150 * r["eligible_regions_mean"]
    assert r["eligible_regions_mean"] == 8
    # per-region rate should be in the neighbourhood of the exact F tail at
    # (8, 32) -- the floor corpus has k=4 neighbours of 8 -> 32 in the pool
    exact = C.d3_false_alarm_exact(8, 32, D.d3_low_ratio, D.d3_high_ratio)
    assert abs(r["per_region_rate"] - exact) <= 4 * (r["per_region_se"] or 0.02), (r, exact)
    assert r["per_corpus_rate"] > 0.2          # zero was never the truth
    assert r["independence_bound_per_corpus"] is not None
    assert "not the rate" in r["note"]


def test_zero_variance_neighbourhood_is_skipped_not_fired_and_counted():
    import dataclasses
    c0 = synth.pure_null(seed=5, n_regions=3, n_players=1, n_runs=8)
    # make every region except w00 constant -> w00's neighbourhood has zero
    # variance; w01/w02 have each other (also constant) as neighbours
    rows = [r if r.region == "w00" else dataclasses.replace(r, metric=0.5) for r in c0.rows]
    c = synth._wrap(rows, "zero_var_nb")
    res = d3.detect(c, D)
    det = res.eligibility.detail
    assert det["skipped_zero_variance_neighbourhood"] >= 1
    assert det["region_tests"] == res.eligibility.eligible_units - det["skipped_zero_variance_neighbourhood"]
    for s in res.signals:
        assert s.values["neighbourhood_variance"] > 0


# ---------------------------------------------------------------- 0d-c
def _score_moments(L: int, candidate: str):
    scores = []
    for tgt in itertools.product("01", repeat=L):
        m = sum(1 for a, b in zip(candidate, tgt) if a == b)
        scores.append(m / L)
    mean = sum(scores) / len(scores)
    var = sum((x - mean) ** 2 for x in scores) / len(scores)
    return mean, var


def test_exact_enumeration_mean_half_variance_one_over_4L():
    for L in (2, 3, 5, 8):
        for cand in ("0" * L, "1" * L, "01" * (L // 2) + "0" * (L % 2)):
            mean, var = _score_moments(L, cand)
            assert abs(mean - 0.5) < 1e-12
            assert abs(var - 1.0 / (4 * L)) < 1e-12, (L, cand, var)


def test_campaign_lengths_imply_different_variances_not_no_information():
    a, b = campaign.ARMS["arm-a"]["length"], campaign.ARMS["arm-b"]["length"]
    va, vb = 1.0 / (4 * a), 1.0 / (4 * b)
    assert (a, b) == (24, 28)
    assert abs(va - 1 / 96) < 1e-15 and abs(vb - 1 / 112) < 1e-15
    assert va != vb
    lv = campaign.check()["levels"]
    assert "1/96" in lv["arm_information"] and "1/112" in lv["arm_information"]
    assert "no arm information" not in lv["arm_information"]


# ---------------------------------------------------------------- 0d-d
PINNED_HASHES = {
    "M-ELIGIBLE-1-01": "sha256:67b90150a06b8bf5", "M-ELIGIBLE-1-02": "sha256:234793d903c3582c",
    "M-ELIGIBLE-1-03": "sha256:f674add4814c195b", "M-ELIGIBLE-1-04": "sha256:b2216250d91e99d3",
    "M-ELIGIBLE-1-05": "sha256:33e0048b3571c7cd", "M-ELIGIBLE-1-06": "sha256:06facc6eba6173c3",
    "M-ELIGIBLE-1-07": "sha256:b9ff0080fbc8cf28", "M-ELIGIBLE-1-08": "sha256:ec8a357e76fd866d",
}


def test_sealed_plan_hashes_unchanged_by_metadata_correction():
    for r in campaign.plan():
        assert specbuild.spec_hash(r["spec"])[:23] == PINNED_HASHES[r["request_key"]]


def test_plan_assignments_agree_with_declared_levels():
    rows = campaign.plan()
    lv = campaign.check()["levels"]
    per_arm = {}
    for r in rows:
        per_arm.setdefault(r["arm_id"], set()).add(r["seed_root"])
    assert {len(v) for v in per_arm.values()} == {4}          # 4 WORLDS per arm
    assert len(rows) == 8
    assert sum(r["spec"]["repeat"]["count"] for r in rows) == 32
    assert lv["assignment"]["unit"] == "world"
    assert lv["assignment"]["randomized"] is False
    assert lv["assignment"]["method"] == "deterministic_enumeration"
    assert lv["randomized"].startswith("WORLD") and lv["analyzed"].startswith("WORLD")
    # deterministic: plan() replays identically
    a = hashlib.sha256(str([(r["request_key"], r["arm_id"], r["seed_root"]) for r in rows]).encode()).hexdigest()
    b = hashlib.sha256(str([(r["request_key"], r["arm_id"], r["seed_root"]) for r in campaign.plan()]).encode()).hexdigest()
    assert a == b


# ---------------------------------------------------------------- 0d-e / 0d-f (third amendment)
def test_production_tick_imports_no_calibration_code():
    """Recalibration lives outside the tick: computation in production,
    qualification and calibration elsewhere."""
    from archaeon.tests.conftest import executable_source
    from archaeon.producer import tick as tickmod, loop as loopmod
    for mod in (tickmod, loopmod):
        src = executable_source(mod)
        assert "calibrate" not in src and "reconcile" not in src, mod.__name__


def test_signal_carries_the_frozen_estimator_parameters():
    c = synth.variance_anomaly(seed=3)
    res = d3.detect(c, D)
    assert res.signals, "the planted anomaly must fire"
    s = res.signals[0]
    assert s.detector_version == "d3.v0"
    for k in ("d3_high_ratio", "d3_low_ratio", "d3_min_n_region",
              "d3_min_n_neighborhood", "d3_neighbors_k"):
        assert k in s.thresholds
    assert s.values["region_variance"] > 0 and s.values["neighbourhood_variance"] > 0
