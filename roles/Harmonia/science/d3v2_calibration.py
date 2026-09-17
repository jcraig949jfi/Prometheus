"""d3.v2 calibration, exactly as declared in d3v2_calibration_plan_2026-09-14.md.

Harmonia[m2-f541bed9], 2026-09-14. Runs archaeon.detectors.d3_variance_anomaly.detect
ITSELF (executing, not re-implementing) under v1 (pooled_within) and v2 (d3_detrend)
on the SAME synthetic corpora. Does not edit the detector. Writes one JSON ledger
(argv[1]) and rewrites it after every cell (per-cell flush), so a killed run keeps
every finished cell. Optional argv[2]: corpora per cell (default 600).
"""
import dataclasses
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)

from archaeon import workspace as _ws                                  # noqa: E402

_ws.assert_not_canonical("run the d3.v2 calibration")

from archaeon import config as cfg                                      # noqa: E402
from archaeon import synth                                              # noqa: E402
from archaeon import calibrate_d3_null as C                             # noqa: E402
from archaeon.detectors import d3_variance_anomaly as d3                # noqa: E402

BASE = cfg.DEFAULT.detectors
V1 = dataclasses.replace(BASE, d3_denominator="pooled_within", d3_detrend=False)
V2 = dataclasses.replace(BASE, d3_denominator="pooled_within", d3_detrend=True)
TARGET = "w03"
N_REGIONS = 8
SIGMA = 0.08
GEOMETRIES = {"FLOOR": (8, 8), "LIVE": (36, 36), "UNEQUAL": (8, 40)}   # (tested n, other n)


def slope_for_r(r, n, sigma):
    if r <= 0:
        return 0.0
    var_idx = (n * n - 1) / 12.0
    return sigma * math.sqrt(r * r / (1 - r * r)) / math.sqrt(var_idx)


def build(seed, geometry, null, r=0.0, pos=None):
    """One synthetic corpus. Rows of a region are emitted consecutively, so the
    row counter (seq) is commit order within the region."""
    n_t, n_o = GEOMETRIES[geometry]
    synth.reset()
    rng = random.Random(seed)
    rows = []
    for ri in range(N_REGIONS):
        reg = "w{:02d}".format(ri)
        coord = ri / (N_REGIONS - 1)
        # w03 is the tested region (n_t rows); every other region has n_o rows.
        # Plan s1: UNEQUAL = w03 at 8 against neighbours of 40.
        n = n_t if reg == TARGET else n_o
        mu = 0.5 + (rng.gauss(0.0, 2 * SIGMA) if null == "N1" else 0.0)
        s = SIGMA
        if pos == "HI" and reg == TARGET:
            s = SIGMA * math.sqrt(6.0)
        if pos == "LO" and reg == TARGET:
            s = SIGMA / math.sqrt(6.0)
        trend_here = (null == "N2a") or (null == "N2h" and reg == TARGET) or \
                     (pos is not None and r > 0 and reg == TARGET)
        b = slope_for_r(r, n, s) if trend_here else 0.0
        for j in range(n):
            rows.append(synth._row(reg, "F", "p0",
                                   mu + b * (j - (n - 1) / 2.0) + rng.gauss(0.0, s), coord))
    return synth._wrap(rows, "d3v2cal:%s:%s:r%.3f:%s" % (geometry, null, r, pos))


def count(result, stats):
    el = result.eligibility
    fired = {s.regions[0]: s.values.get("direction") for s in result.signals}
    stats["eligible"] += el.eligible_units
    stats["fires"] += len(fired)
    stats["corpora_fired"] += 1 if fired else 0
    stats["lower"] += sum(1 for v in fired.values() if v == "LOWER_DISPERSION")
    stats["higher"] += sum(1 for v in fired.values() if v == "HIGHER_DISPERSION")
    stats["skipped_zero_var"] += int((el.detail or {}).get("skipped_zero_variance_neighbourhood", 0))
    # w03 is eligible by construction in every geometry (n_t >= 8, pool >= 32);
    # the detector does not expose per-region eligibility, so the assumption is
    # CHECKED as "every region eligible" and violations are counted, not hidden.
    if el.eligible_units == N_REGIONS:
        stats["target_tests"] += 1
        stats["target_fires"] += 1 if TARGET in fired else 0
    else:
        stats["not_all_eligible"] += 1


def summarise(st, corpora):
    def rate(k, n):
        p = k / n if n else float("nan")
        return {"rate": p, "se": math.sqrt(p * (1 - p) / n) if n and 0 < p < 1 else 0.0, "k": k, "n": n}
    return {"corpora": corpora,
            "all_region": rate(st["fires"], st["eligible"]),
            "target": rate(st["target_fires"], st["target_tests"]),
            "per_corpus": rate(st["corpora_fired"], corpora),
            "lower": st["lower"], "higher": st["higher"],
            "eligible_mean": st["eligible"] / corpora,
            "skipped_zero_variance_neighbourhoods": st["skipped_zero_var"],
            "corpora_not_all_regions_eligible": st["not_all_eligible"]}


def new_stats():
    return {k: 0 for k in ("eligible", "fires", "corpora_fired", "lower", "higher",
                           "skipped_zero_var", "target_tests", "target_fires",
                           "not_all_eligible")}


def run_cell(geometry, null, r, pos, corpora, seed0):
    s1, s2 = new_stats(), new_stats()
    for i in range(corpora):
        c = build(seed0 + i, geometry, null, r, pos)
        count(d3.detect(c, V1), s1)
        count(d3.detect(c, V2), s2)
    return {"v1": summarise(s1, corpora), "v2": summarise(s2, corpora)}


class _Stub:
    def __init__(self, always):
        self.always = always

    def detect(self, corpus, dcfg):
        real = d3.detect(corpus, dcfg)
        el = real.eligibility
        if not self.always:
            return type(real)(el, tuple())
        # one fake signal per eligible region, carrying only what count() reads
        regs = sorted({r.region for r in corpus.rows})[:el.eligible_units]
        fakes = tuple(type("S", (), {"regions": (g,), "values": {"direction": "LOWER_DISPERSION"}})()
                      for g in regs)
        return type(real)(el, fakes)


def harness_controls(corpora=60):
    out = {}
    for name, always in (("CHEAT_ALWAYS", True), ("CHEAT_NEVER", False)):
        st = new_stats()
        stub = _Stub(always)
        for i in range(corpora):
            count(stub.detect(build(90_000 + i, "LIVE", "N0"), V1), st)
        sm = summarise(st, corpora)
        want = 1.0 if always else 0.0
        out[name] = {"all_region_rate": sm["all_region"]["rate"], "want": want,
                     "pass": abs(sm["all_region"]["rate"] - want) < 1e-12}
    pos = run_cell("LIVE", "N0", 0.0, "HI", 200, 95_000)
    out["POSITIVE_v1_LIVE_POS_HI"] = {"target_rate": pos["v1"]["target"]["rate"],
                                      "pass": pos["v1"]["target"]["rate"] >= 0.90}
    return out


def exact_refs(geometry):
    n_t, n_o = GEOMETRIES[geometry]
    pool = 4 * n_o
    return {"F(n_r-1, sum(n_o-1))": C.f_cdf(BASE.d3_low_ratio, n_t - 1, pool - 4)
            + 1 - C.f_cdf(BASE.d3_high_ratio, n_t - 1, pool - 4),
            "F(n_r-2, sum(n_o-2))": C.f_cdf(BASE.d3_low_ratio, n_t - 2, pool - 8)
            + 1 - C.f_cdf(BASE.d3_high_ratio, n_t - 2, pool - 8),
            "note": "references for the TARGET region against 4 neighbours of n_o each"}


def main(out_path, corpora):
    t0 = time.time()
    ledger = {"schema": "harmonia.d3v2_calibration.v1", "instance": "m2-f541bed9",
              "plan": "roles/Harmonia/science/d3v2_calibration_plan_2026-09-14.md",
              "receipt": _ws.receipt(), "corpora_per_cell": corpora,
              "config_v1": {k: getattr(V1, k) for k in dir(V1) if k.startswith("d3_")},
              "config_v2": {k: getattr(V2, k) for k in dir(V2) if k.startswith("d3_")},
              "sigma": SIGMA, "regions_per_corpus": N_REGIONS, "geometries": GEOMETRIES,
              "cells": [], "status": "running"}

    def flush():
        with open(out_path, "w") as fh:
            json.dump(ledger, fh, indent=1, default=str)
            fh.flush()

    ctl = harness_controls()
    ledger["harness_controls"] = ctl
    if not all(v["pass"] for v in ctl.values()):
        ledger["status"] = "ABORTED: harness control failed"
        flush()
        print(json.dumps(ctl, indent=1))
        return 1
    flush()

    plan = []
    seed = 100_000
    for g in GEOMETRIES:
        plan.append((g, "N0", 0.0, None))
        plan.append((g, "N1", 0.0, None))
        for r in (0.577, 0.816):
            plan.append((g, "N2h", r, None))
            plan.append((g, "N2a", r, None))
        for p in ("HI", "LO"):
            plan.append((g, "N0", 0.0, p))
            plan.append((g, "N0", 0.816, p))
    for g, null, r, pos in plan:
        seed += 10_000
        res = run_cell(g, null, r, pos, corpora, seed)
        cell = {"geometry": g, "null": null, "r": r, "positive": pos, "seed0": seed,
                "v1": res["v1"], "v2": res["v2"]}
        if null == "N0" and pos is None:
            cell["exact_refs_target"] = exact_refs(g)
        ledger["cells"].append(cell)
        ledger["elapsed_s"] = round(time.time() - t0, 1)
        flush()
        print("%-8s %-4s r=%.3f pos=%-4s v1 all %.4f tgt %.4f | v2 all %.4f tgt %.4f  (%.0fs)"
              % (g, null, r, pos, res["v1"]["all_region"]["rate"], res["v1"]["target"]["rate"],
                 res["v2"]["all_region"]["rate"], res["v2"]["target"]["rate"], time.time() - t0),
              flush=True)
    ledger["status"] = "complete"
    flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 600))
