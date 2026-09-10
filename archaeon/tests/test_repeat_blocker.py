"""Harmonia's repeat blocker (RULING_NK_CA_PACKET_V2_AND_ROUTES, 2026-09-08):
D3 counted ROWS; repeats of one experiment share a draw and inflate the
false-alarm rate 6.4x at the floor. Fix (a): aggregate to one row per
independent unit before any detector runs. d3.v0 is untouched.
"""
from __future__ import annotations

import random

from archaeon import config as cfg
from archaeon import fossils, synth
from archaeon.detectors import d3_variance_anomaly as d3
from archaeon.fossils import FossilRow

D = cfg.DEFAULT.detectors


def _repeat_corpus(seed, n_regions=8, units_per_region=2, repeats=4,
                   unit_sd=1.0, repeat_sd=0.1):
    """Pure null: each unit (experiment) draws a value; its repeats scatter
    tightly around it. Rows carry exp_id so unit_key groups them."""
    rng = random.Random(seed)
    rows = []
    i = 0
    for ri in range(n_regions):
        reg = "w{:02d}".format(ri)
        for u in range(units_per_region):
            ex = "exp_{}_{}".format(reg, u)
            v = rng.gauss(0.0, unit_sd)
            for rep in range(repeats):
                i += 1
                rows.append(FossilRow(row_id="obs_{}".format(i), source="sfe", seq=i,
                                      region=reg, family="F", player=None,
                                      metric=v + rng.gauss(0.0, repeat_sd),
                                      coords={"spec.candidate": ri / (n_regions - 1)},
                                      anchors={"exp_id": ex, "obs_id": "obs_{}".format(i)}))
    return fossils.corpus_from_rows(rows, synth.SYNTH_CHART, source_ref="synthetic:repeats")


def _rate(corpora, detect_on):
    tests = fires = 0
    for c in corpora:
        res = d3.detect(detect_on(c), D)
        tests += res.eligibility.eligible_units
        fires += len(res.signals)
    return fires / tests if tests else float("nan"), tests


def test_raw_repeats_inflate_d3_and_aggregation_restores_the_calibrated_rate():
    # 2 units x 4 repeats = 8 rows per region: eligible as ROWS, and inflated
    raw = [_repeat_corpus(1000 + s) for s in range(120)]
    r_raw, n_raw = _rate(raw, lambda c: c)
    assert n_raw == 120 * 8
    assert r_raw > 0.3, r_raw            # Harmonia measured 0.56; calibrated is 0.088
    # aggregated: 2 units per region -> below the floor -> NOT eligible
    r_agg, n_agg = _rate(raw, fossils.aggregate_repeats)
    assert n_agg == 0
    # 8 units x 4 repeats per region: aggregated -> 8 independent units,
    # k=4 neighbours -> pool 32 -> the floor geometry, calibrated at 0.083
    big = [_repeat_corpus(5000 + s, units_per_region=8) for s in range(150)]
    r_big, n_big = _rate(big, fossils.aggregate_repeats)
    assert n_big == 150 * 8
    from archaeon.calibrate_d3_null import d3_false_alarm_exact
    exact = d3_false_alarm_exact(8, 32, D.d3_low_ratio, D.d3_high_ratio)
    se = (exact * (1 - exact) / n_big) ** 0.5
    assert abs(r_big - exact) <= 4 * se, (r_big, exact, se)


def test_aggregation_records_its_denominators_and_keeps_provenance():
    c = _repeat_corpus(7, units_per_region=3)
    a = fossils.aggregate_repeats(c)
    w = a.window["aggregation"]
    assert w == {"independent_unit": "experiment", "how": "mean",
                 "rows_before": 8 * 3 * 4, "units_after": 8 * 3,
                 "max_repeats_in_a_unit": 4}
    row = a.rows[0]
    assert row.anchors["aggregated_n"] == 4 and len(row.anchors["aggregated_from"]) == 4
    assert row.row_id.startswith("agg:")


def test_rows_without_an_experiment_anchor_are_their_own_unit():
    c = synth.pure_null(seed=3, n_regions=4, n_players=2, n_runs=4)
    a = fossils.aggregate_repeats(c)
    assert len(a.rows) == len(c.rows)
    assert a.window["aggregation"]["max_repeats_in_a_unit"] == 1


def test_tick_runs_detectors_on_the_aggregated_corpus():
    from archaeon.tests.conftest import executable_source
    from archaeon.producer import tick as tickmod
    src = executable_source(tickmod)
    assert "aggregate_repeats(corpus)" in src
    assert "run_all(agg_corpus" in src
