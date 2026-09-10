"""Detector tests against synthetic fossils with known properties.

Every planted-effect test is PAIRED with a control that has the identical
structure and no effect. A detector passing only the planted test has not been
shown to detect anything -- it may simply fire on the shape.

Firing is stochastic, so the assertions are on RATES over many seeds, not on a
single corpus. A single-seed assertion would be a coin flip dressed as a test.
"""
from __future__ import annotations

import pytest

from archaeon import config as cfg
from archaeon import synth
from archaeon.detectors import DETECTOR_BY_NAME, run_all, eligibility_census

DCFG = cfg.DEFAULT.detectors
SEEDS = 60


def fire_rate(name, gen, seeds=SEEDS, base=0, **kw):
    mod = DETECTOR_BY_NAME[name]
    k = 0
    for s in range(seeds):
        if mod.detect(gen(seed=base + s, **kw), DCFG).signals:
            k += 1
    return k / seeds


def eligible_rate(name, gen, seeds=SEEDS, base=0, **kw):
    mod = DETECTOR_BY_NAME[name]
    k = 0
    for s in range(seeds):
        if mod.detect(gen(seed=base + s, **kw), DCFG).eligibility.is_eligible:
            k += 1
    return k / seeds


# --------------------------------------------------------------------------
# Pure null must not constantly trigger anything.
# --------------------------------------------------------------------------
ALL = ["REPEATED_SMALL_DEVIATION", "SIGN_INSTABILITY", "LOCAL_VARIANCE_ANOMALY",
       "PLAYER_ORDER_REVERSAL", "REPEATED_OUTLIER_REGION",
       "BOUNDARY_TRANSITION_HINT"]


@pytest.mark.parametrize("name", ALL)
def test_pure_null_does_not_constantly_trigger(name):
    """Corpus-level false-alarm rate stays inside the 0.05 budget (+slack).

    The bound is 0.15 rather than 0.05 because 60 seeds gives a binomial SE of
    ~0.028 at p=0.05; a 0.05 bound would fail on noise about half the time.
    The MEASURED rates live in archaeon/docs/CALIBRATION.md.
    """
    r = fire_rate(name, synth.pure_null, base=10_000)
    assert r <= 0.15, "{} fires on {:.0%} of pure-null corpora".format(name, r)


def test_pure_null_eligibility_is_reported_not_conflated():
    """A detector that cannot fire must say so, distinctly from finding nothing."""
    c = synth.pure_null(seed=1)
    res = run_all(c, DCFG)
    cen = eligibility_census(res)
    assert "any_eligible" in cen and "detectors_fired" in cen
    for name, e in cen["per_detector"].items():
        if e["eligible_units"] == 0:
            assert e["blocked_reason"], \
                "{} reports zero eligible units with no reason".format(name)


def test_no_player_corpus_blocks_player_detectors():
    """The live SFE chart has no player field; the three player-dependent
    detectors must report NOT ELIGIBLE rather than silently finding nothing."""
    from archaeon.fossils import corpus_from_rows
    rows = synth.pure_null(seed=2).rows
    stripped = [type(r)(row_id=r.row_id, source=r.source, seq=r.seq,
                        region=r.region, family=r.family, player=None,
                        metric=r.metric, coords=r.coords, anchors=r.anchors)
                for r in rows]
    c = corpus_from_rows(stripped, cfg.SFE_SCORE_CHART, "test:noplayer")
    res = run_all(c, DCFG)
    for name in ("REPEATED_SMALL_DEVIATION", "SIGN_INSTABILITY",
                 "PLAYER_ORDER_REVERSAL"):
        e = res[name].eligibility
        assert not e.is_eligible
        assert "player" in (e.blocked_reason or "").lower()


# --------------------------------------------------------------------------
# Planted effects, each with its paired control.
# --------------------------------------------------------------------------
def test_d1_repeated_small_deviation_and_control():
    hit = fire_rate("REPEATED_SMALL_DEVIATION",
                    synth.repeated_small_deviation, base=20_000)
    ctl = fire_rate("REPEATED_SMALL_DEVIATION",
                    synth.repeated_no_deviation, base=30_000)
    # D1 is the weakest detector in the suite (see CALIBRATION.md); the
    # assertion is that it SEPARATES, not that it is sensitive.
    assert hit >= 0.20, "D1 hit rate {:.2f} too low to be useful".format(hit)
    assert ctl <= 0.15, "D1 fires on its own null control at {:.2f}".format(ctl)
    assert hit - ctl >= 0.10


def test_d1_reports_empty_band_rather_than_silence():
    """With too few runs the effect band is unreachable. That must be reported
    as NOT ELIGIBLE, not as a quiet detector -- it is the defect the first
    calibration run found."""
    tight = cfg.DetectorConfig(d1_min_runs=4, d1_min_t=3.0,
                               d1_max_effect_sd=1.0)
    c = synth.repeated_small_deviation(seed=1, n_runs=4)
    e = DETECTOR_BY_NAME["REPEATED_SMALL_DEVIATION"].detect(c, tight).eligibility
    assert not e.is_eligible
    assert e.detail.get("reachability") in ("EMPTY_BAND", "INSUFFICIENT_RUNS")


def test_d2_sign_instability_and_stable_control():
    hit = fire_rate("SIGN_INSTABILITY", synth.sign_instability, base=20_000)
    ctl = fire_rate("SIGN_INSTABILITY", synth.sign_stable, base=30_000)
    assert hit >= 0.60
    assert ctl <= 0.10, "fires on a STABLE ordering at {:.2f}".format(ctl)


def test_d3_variance_anomaly_and_equal_variance_control():
    hit = fire_rate("LOCAL_VARIANCE_ANOMALY", synth.variance_anomaly,
                    base=20_000)
    ctl = fire_rate("LOCAL_VARIANCE_ANOMALY", synth.variance_equal, base=30_000)
    assert hit >= 0.80
    assert ctl <= 0.15, "fires on EQUAL variance at {:.2f}".format(ctl)


def test_d3_detects_low_dispersion_too():
    """Unusually LOW dispersion is as much a reason to look again as high."""
    mod = DETECTOR_BY_NAME["LOCAL_VARIANCE_ANOMALY"]
    found = False
    for s in range(30):
        c = synth.variance_anomaly(seed=s, ratio=0.05)
        for sig in mod.detect(c, DCFG).signals:
            if sig.values["direction"] == "LOWER_DISPERSION":
                found = True
    assert found, "D3 never reported LOWER_DISPERSION on a low-variance region"


def test_d3_v1_pooled_within_denominator_is_immune_to_between_region_mean_shifts():
    """Harmonia items 7-8: 28 of 30 live fires were LOWER because the
    concatenated pool carries between-region variance. v0 must reproduce the
    artifact on the bias model; v1 must not, and must keep the real
    detection. v0 remains the default until v1 is admitted."""
    import dataclasses
    mod = DETECTOR_BY_NAME["LOCAL_VARIANCE_ANOMALY"]
    v0 = dataclasses.replace(DCFG, d3_denominator="concatenated")
    v1 = dataclasses.replace(DCFG, d3_denominator="pooled_within")
    assert DCFG.d3_denominator == "pooled_within"        # admitted 2026-09-10

    def rate(dc, gen, **kw):
        k = 0
        for s in range(SEEDS):
            if mod.detect(gen(seed=40_000 + s, **kw), dc).signals:
                k += 1
        return k / SEEDS
    art_v0 = rate(v0, synth.variance_equal_shifted_means)
    art_v1 = rate(v1, synth.variance_equal_shifted_means)
    assert art_v0 >= 0.5, "v0 did not reproduce the artifact ({:.2f})".format(art_v0)
    assert art_v1 <= 0.10, "v1 still fires on shifted means ({:.2f})".format(art_v1)
    # the direction of the artifact is LOWER, as observed live
    dirs = [sig.values["direction"] for s in range(20)
            for sig in mod.detect(synth.variance_equal_shifted_means(seed=40_000 + s), v0).signals]
    assert dirs and dirs.count("LOWER_DISPERSION") / len(dirs) >= 0.9
    # v1 keeps the real detection and its control, and stamps its version
    assert rate(v1, synth.variance_anomaly) >= 0.80
    assert rate(v1, synth.variance_equal) <= 0.15
    sig = mod.detect(synth.variance_anomaly(seed=1), v1).signals[0]
    assert sig.detector_version == "d3.v1" and sig.values["denominator"] == "pooled_within"
    assert mod.detect(synth.variance_anomaly(seed=1), v0).signals[0].detector_version == "d3.v0"


def test_d4_order_reversal_and_stable_control():
    hit = fire_rate("PLAYER_ORDER_REVERSAL", synth.order_reversal, base=20_000)
    ctl = fire_rate("PLAYER_ORDER_REVERSAL", synth.order_stable, base=30_000)
    assert hit >= 0.80
    assert ctl <= 0.10, "fires on a STABLE ordering at {:.2f}".format(ctl)


def test_d5_repeated_outliers_and_clean_control():
    hit = fire_rate("REPEATED_OUTLIER_REGION", synth.repeated_outliers,
                    base=20_000)
    ctl = fire_rate("REPEATED_OUTLIER_REGION", synth.no_outliers, base=30_000)
    assert hit >= 0.80
    assert ctl <= 0.10


def test_d5_ignores_a_single_outlier():
    """REPEATED is the word in the name: one extreme value must not fire it."""
    r = fire_rate("REPEATED_OUTLIER_REGION", synth.repeated_outliers,
                  seeds=30, base=50_000, n_outliers=1)
    assert r <= 0.10, "D5 fires on a SINGLE outlier at {:.2f}".format(r)


def test_d6_boundary_and_flat_control():
    hit = fire_rate("BOUNDARY_TRANSITION_HINT", synth.boundary_step, base=20_000)
    ctl = fire_rate("BOUNDARY_TRANSITION_HINT", synth.boundary_smooth,
                    base=30_000)
    assert hit >= 0.80
    assert ctl <= 0.10


def test_d6_does_not_fire_on_a_gradual_trend():
    """The control that matters: the SAME end-to-end change, spread smoothly.

    A detector that fires here is detecting a trend, not a boundary. The v0
    build did exactly this on 83% of such corpora.
    """
    r = fire_rate("BOUNDARY_TRANSITION_HINT", synth.boundary_gradual,
                  base=30_000)
    assert r <= 0.15, "D6 fires on a smooth gradient at {:.2f}".format(r)


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------
def test_detectors_are_deterministic():
    c = synth.variance_anomaly(seed=7)
    a = run_all(c, DCFG)
    b = run_all(c, DCFG)
    for name in a:
        assert ([s.signal_id() for s in a[name].signals]
                == [s.signal_id() for s in b[name].signals])


def test_signal_ids_are_stable_across_runs():
    c = synth.order_reversal(seed=9)
    mod = DETECTOR_BY_NAME["PLAYER_ORDER_REVERSAL"]
    ids1 = sorted(s.signal_id() for s in mod.detect(c, DCFG).signals)
    c2 = synth.order_reversal(seed=9)
    ids2 = sorted(s.signal_id() for s in mod.detect(c2, DCFG).signals)
    assert ids1 == ids2 and ids1


def test_d3_v1_labels_a_climbing_region_exchangeability_suspect_without_changing_the_statistic():
    """Harmonia a1d0ed9c8: both live UPPER fires were trajectories, not samples.
    The label is reported; the ratio is untouched (detrending would be v2)."""
    import dataclasses
    from archaeon import fossils
    mod = DETECTOR_BY_NAME["LOCAL_VARIANCE_ANOMALY"]
    c = synth.variance_anomaly(seed=5, ratio=6.0)
    # make the anomalous region w03 a monotone climb in committed order
    rows = []
    k = 0
    for r in c.rows:
        if r.region == "w03":
            k += 1
            rows.append(dataclasses.replace(r, metric=0.1 + 0.04 * k, seq=k))
        else:
            rows.append(r)
    climbing = fossils.corpus_from_rows(rows, c.chart) if "chart" in fossils.corpus_from_rows.__code__.co_varnames else dataclasses.replace(c, rows=rows)
    sig = [s for s in mod.detect(climbing, DCFG).signals if s.regions[0] == "w03"]
    assert sig, "the climbing region must still fire on its variance"
    v = sig[0].values
    assert v["exchangeability"] == "EXCHANGEABILITY_VIOLATED" and v["trend_fraction"] > 0.9    # a pure ramp: |r| ~ 1 >= 0.816
    assert v["trend_inflation_of_ratio"] > 3.0                                              # trend alone crosses the band edge
    # the statistic itself is unchanged by the label: same ratio as a shuffled-order copy
    import random
    rng = random.Random(1)
    shuffled = []
    seqs = [r.seq for r in rows if r.region == "w03"]; rng.shuffle(seqs)
    it = iter(seqs)
    for r in rows:
        shuffled.append(dataclasses.replace(r, seq=next(it)) if r.region == "w03" else r)
    c2 = fossils.corpus_from_rows(shuffled, c.chart) if "chart" in fossils.corpus_from_rows.__code__.co_varnames else dataclasses.replace(c, rows=shuffled)
    s2 = [s for s in mod.detect(c2, DCFG).signals if s.regions[0] == "w03"][0]
    assert abs(s2.values["variance_ratio"] - v["variance_ratio"]) < 1e-12
    assert s2.values["exchangeability"] in ("EXCHANGEABLE", "EXCHANGEABILITY_SUSPECT")       # shuffled order: no ramp
