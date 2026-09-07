"""WP-0d: reconcile D3's reported null fire rate (0.000) with Harmonia's
measured per-region false-alarm rate (0.106).

Both numbers are correct about what they measured. They differ in SAMPLE
SIZE, not in generator coupling:

    Harmonia's null     region n = 8, neighbourhood n = 16 -- the ELIGIBILITY
                        FLOOR (d3_min_n_region, d3_min_n_neighborhood)
    Archaeon's null     synth.pure_null: 4 players x 20 runs = 80 per region,
                        k = 4 neighbours -> 320 in the neighbourhood

For i.i.d. Gaussian data the ratio of two sample variances is F-distributed
with (n_r - 1, n_nb - 1) degrees of freedom. The probability that F leaves
the band [1/3, 3] is

    F(7, 15):     ~0.106     (Harmonia's number, exactly)
    F(79, 319):   < 1e-6     (why pure_null never fired)

So the calibration null was structurally easier than a floor-sized real
corpus. Not a coupling artefact; a corpus far larger than the smallest
corpus D3 is willing to test. The consequence Harmonia named stands: every
downstream false-discovery figure computed from pure_null is optimistic, and
the honest per-region rate for a floor-sized corpus is ~0.106.

This module gives (a) the EXACT F-tail (a deterministic identity, CI-grade),
(b) a seeded simulation with binomial uncertainty, (c) the per-region and
per-corpus rates on floor-sized synthetic null corpora run through D3 ITSELF,
with denominators, and (d) the independence bound for the corpus-level rate
beside the measured one, since overlapping neighbourhoods make regions
dependent and the bound is not the rate.

Nothing here changes D3. Changing the band to depend on n is a new detector
version for Harmonia to qualify; this module only reports.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List

from . import config as cfg
from . import synth
from .detectors import d3_variance_anomaly as d3


# --------------------------------------------------------------------------
# (a) exact: regularized incomplete beta -> F cdf, no scipy
# --------------------------------------------------------------------------
def _betacf(a: float, b: float, x: float) -> float:
    MAXIT, EPS, FPMIN = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / (c if abs(c) > FPMIN else FPMIN)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / (c if abs(c) > FPMIN else FPMIN)
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def f_cdf(x: float, d1: int, d2: int) -> float:
    if x <= 0:
        return 0.0
    return betainc(d1 / 2.0, d2 / 2.0, d1 * x / (d1 * x + d2))


def d3_false_alarm_exact(n_region: int, n_neighbourhood: int,
                         low: float, high: float) -> float:
    """P(var_r / var_nb outside [low, high]) under i.i.d. Gaussian data."""
    d1, d2 = n_region - 1, n_neighbourhood - 1
    return f_cdf(low, d1, d2) + (1.0 - f_cdf(high, d1, d2))


# --------------------------------------------------------------------------
# (b) simulation with uncertainty
# --------------------------------------------------------------------------
def d3_false_alarm_sim(n_region: int, n_neighbourhood: int, low: float,
                       high: float, draws: int = 20_000,
                       seed: int = 20260907) -> Dict[str, float]:
    rng = random.Random(seed)

    def var(xs):
        m = sum(xs) / len(xs)
        return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)

    fires = 0
    for _ in range(draws):
        r = var([rng.gauss(0, 1) for _ in range(n_region)])
        nb = var([rng.gauss(0, 1) for _ in range(n_neighbourhood)])
        ratio = r / nb
        if ratio < low or ratio > high:
            fires += 1
    p = fires / draws
    return {"rate": p, "se": math.sqrt(p * (1 - p) / draws), "draws": draws,
            "seed": seed, "fires": fires}


# --------------------------------------------------------------------------
# (c) D3 itself on floor-sized synthetic null corpora, with denominators
# --------------------------------------------------------------------------
def floor_null(seed: int, n_regions: int = 8, dcfg=None):
    """A pure null whose regions sit AT the eligibility floor: 8 per region
    (2 players x 4 runs) and k=4 neighbours -> 32 in the neighbourhood."""
    dcfg = dcfg or cfg.DEFAULT.detectors
    per = dcfg.d3_min_n_region
    n_players = 2
    n_runs = per // n_players
    return synth.pure_null(seed=seed, n_regions=n_regions,
                           n_players=n_players, n_runs=n_runs)


def d3_on_null_corpora(seeds: int = 300, n_regions: int = 8, geometry: str = "floor",
                       dcfg=None) -> Dict[str, Any]:
    dcfg = dcfg or cfg.DEFAULT.detectors
    region_tests = 0
    region_fires = 0
    corpora_fired = 0
    eligible_counts: List[int] = []
    skipped = 0
    for s in range(seeds):
        c = (floor_null(30_000 + s, n_regions, dcfg) if geometry == "floor"
             else synth.pure_null(seed=30_000 + s, n_regions=n_regions))
        res = d3.detect(c, dcfg)
        el = res.eligibility
        eligible_counts.append(el.eligible_units)
        region_tests += el.eligible_units
        skipped += int((el.detail or {}).get("skipped_zero_variance_neighbourhood", 0))
        n_f = len(res.signals)
        region_fires += n_f
        if n_f:
            corpora_fired += 1
    per_region = region_fires / region_tests if region_tests else float("nan")
    per_corpus = corpora_fired / seeds
    k = sum(eligible_counts) / len(eligible_counts)
    return {
        "geometry": geometry, "corpora": seeds, "regions_per_corpus": n_regions,
        "eligible_regions_mean": k,
        "region_tests": region_tests, "region_fires": region_fires,
        "per_region_rate": per_region,
        "per_region_se": (math.sqrt(per_region * (1 - per_region) / region_tests)
                          if region_tests and 0 < per_region < 1 else None),
        "corpora_fired": corpora_fired, "per_corpus_rate": per_corpus,
        "per_corpus_se": (math.sqrt(per_corpus * (1 - per_corpus) / seeds)
                          if 0 < per_corpus < 1 else None),
        "independence_bound_per_corpus": 1 - (1 - per_region) ** k
        if region_tests else None,
        "zero_variance_neighbourhoods_skipped": skipped,
        "note": ("per-corpus rate is MEASURED with overlapping neighbourhoods; "
                 "the independence bound is reported beside it and is not the "
                 "rate"),
    }


def reconcile(draws: int = 20_000, seeds: int = 300) -> Dict[str, Any]:
    d = cfg.DEFAULT.detectors
    low, high = d.d3_low_ratio, d.d3_high_ratio
    floor = (d.d3_min_n_region, d.d3_min_n_neighborhood)
    # what synth.pure_null actually gives D3
    pn = synth.pure_null(seed=10_000)
    by = {}
    for r in pn.rows:
        by.setdefault(r.region, 0)
        by[r.region] += 1
    n_reg = min(by.values())
    n_nb = d.d3_neighbors_k * n_reg
    return {
        "band": [low, high],
        "harmonia_floor": {"n_region": floor[0], "n_neighbourhood": floor[1],
                           "exact": d3_false_alarm_exact(*floor, low, high),
                           "sim": d3_false_alarm_sim(*floor, low, high, draws)},
        "archaeon_pure_null_geometry": {
            "n_region": n_reg, "n_neighbourhood": n_nb,
            "exact": d3_false_alarm_exact(n_reg, n_nb, low, high)},
        "floor_synthetic_corpora_through_d3": d3_on_null_corpora(seeds, geometry="floor"),
        "original_pure_null_through_d3": d3_on_null_corpora(min(seeds, 100), geometry="original"),
        "conclusion": (
            "0.000 and 0.106 are both correct: the calibration null had ~{}x "
            "the floor's observations per region, where the F-tail outside the "
            "band is ~0. At the eligibility floor the per-region false-alarm "
            "rate is ~{:.3f} (exact F({},{})). Calibration must report rates "
            "at the floor geometry with denominators; pure_null's 0.000 is "
            "retired as a headline number.".format(
                n_reg // floor[0],
                d3_false_alarm_exact(*floor, low, high), floor[0] - 1, floor[1] - 1)),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.calibrate_d3_null")
    ap.add_argument("--draws", type=int, default=20_000)
    ap.add_argument("--seeds", type=int, default=300)
    a = ap.parse_args(argv)
    print(json.dumps(reconcile(a.draws, a.seeds), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
