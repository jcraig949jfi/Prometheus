"""Calibration harness: MEASURE the detectors, do not assert them.

Two numbers per detector, both measured over many seeds:

  NULL RATE   fraction of pure-null corpora on which the detector fires at
              least once. This is the false-alarm rate the thresholds actually
              deliver. It is not asserted anywhere; it is measured here, and if
              it is bad that is a fact about the thresholds.

  HIT RATE    fraction of planted corpora on which the detector fires, plus the
              PAIRED CONTROL rate on the same structure without the effect.
              A detector with a high hit rate AND a high control rate has
              learned the structure, not the effect, and the pair is the only
              way to see that.

Run:  python -m archaeon.calibrate --seeds 200
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Callable, Dict, List

from . import config as cfg
from . import synth
from .detectors import DETECTOR_BY_NAME, run_all

# detector name -> (planted generator, paired control generator(s))
PAIRS: Dict[str, Any] = {
    "REPEATED_SMALL_DEVIATION": (synth.repeated_small_deviation,
                                 {"no_deviation": synth.repeated_no_deviation}),
    "SIGN_INSTABILITY":         (synth.sign_instability,
                                 {"sign_stable": synth.sign_stable}),
    "LOCAL_VARIANCE_ANOMALY":   (synth.variance_anomaly,
                                 {"equal_variance": synth.variance_equal}),
    "PLAYER_ORDER_REVERSAL":    (synth.order_reversal,
                                 {"stable_order": synth.order_stable}),
    "REPEATED_OUTLIER_REGION":  (synth.repeated_outliers,
                                 {"no_outliers": synth.no_outliers}),
    "BOUNDARY_TRANSITION_HINT": (synth.boundary_step,
                                 {"flat": synth.boundary_smooth,
                                  "gradual": synth.boundary_gradual}),
}


def _fires(corpus, name: str, dcfg) -> bool:
    mod = DETECTOR_BY_NAME[name]
    return len(mod.detect(corpus, dcfg).signals) > 0


def _eligible(corpus, name: str, dcfg) -> bool:
    mod = DETECTOR_BY_NAME[name]
    return mod.detect(corpus, dcfg).eligibility.is_eligible


def measure(seeds: int = 200, dcfg=None) -> Dict[str, Any]:
    dcfg = dcfg or cfg.DEFAULT.detectors
    out: Dict[str, Any] = {"seeds": seeds,
                           "thresholds_version": cfg.THRESHOLDS_VERSION,
                           "detectors": {}}

    # --- null: one pure-null corpus per seed, every detector run on it ----
    null_fire = {n: 0 for n in PAIRS}
    null_elig = {n: 0 for n in PAIRS}
    for s in range(seeds):
        c = synth.pure_null(seed=10_000 + s)
        res = run_all(c, dcfg)
        for n in PAIRS:
            if res[n].eligibility.is_eligible:
                null_elig[n] += 1
            if res[n].signals:
                null_fire[n] += 1

    for name, (planted, controls) in PAIRS.items():
        hit = 0
        elig = 0
        for s in range(seeds):
            c = planted(seed=20_000 + s)
            mod = DETECTOR_BY_NAME[name]
            r = mod.detect(c, dcfg)
            if r.eligibility.is_eligible:
                elig += 1
            if r.signals:
                hit += 1

        ctrl_rates = {}
        for cname, gen in controls.items():
            k = 0
            for s in range(seeds):
                if _fires(gen(seed=30_000 + s), name, dcfg):
                    k += 1
            ctrl_rates[cname] = k / seeds

        out["detectors"][name] = {
            "null_fire_rate": null_fire[name] / seeds,
            "null_eligible_rate": null_elig[name] / seeds,
            "planted_hit_rate": hit / seeds,
            "planted_eligible_rate": elig / seeds,
            "paired_control_fire_rate": ctrl_rates,
            # Separation is the honest headline: a detector is only useful
            # insofar as it fires MORE on the effect than on its own control.
            "separation_vs_worst_control":
                (hit / seeds) - (max(ctrl_rates.values()) if ctrl_rates else 0.0),
        }
    return out


# --------------------------------------------------------------------------
# Power curves. A single hit rate at one effect size is not a characterisation
# of a detector; the curve is. Reported so a reader can see WHERE each detector
# stops being able to see anything, rather than being told it "works".
# --------------------------------------------------------------------------
POWER_SWEEPS = {
    "REPEATED_SMALL_DEVIATION": (
        "effect_sd", [0.4, 0.6, 0.7, 0.8, 0.9, 1.0],
        lambda v, s: synth.repeated_small_deviation(seed=s, effect_sd=v)),
    "LOCAL_VARIANCE_ANOMALY": (
        "variance_ratio", [1.5, 2.0, 3.0, 4.0, 6.0, 9.0],
        lambda v, s: synth.variance_anomaly(seed=s, ratio=v)),
    "SIGN_INSTABILITY": (
        "gap", [0.01, 0.02, 0.04, 0.06, 0.10],
        lambda v, s: synth.sign_instability(seed=s, gap=v)),
    "PLAYER_ORDER_REVERSAL": (
        "gap", [0.01, 0.02, 0.04, 0.08, 0.12],
        lambda v, s: synth.order_reversal(seed=s, gap=v)),
    "REPEATED_OUTLIER_REGION": (
        "offset_sd", [2.0, 3.0, 4.0, 6.0, 12.0],
        lambda v, s: synth.repeated_outliers(seed=s, offset_sd=v)),
    "BOUNDARY_TRANSITION_HINT": (
        "step", [0.02, 0.05, 0.10, 0.25, 0.50],
        lambda v, s: synth.boundary_step(seed=s, step=v)),
}


def power_curves(seeds: int = 60, dcfg=None) -> Dict[str, Any]:
    dcfg = dcfg or cfg.DEFAULT.detectors
    out: Dict[str, Any] = {}
    for name, (param, values, gen) in POWER_SWEEPS.items():
        curve = []
        for v in values:
            k = 0
            e = 0
            for s in range(seeds):
                mod = DETECTOR_BY_NAME[name]
                r = mod.detect(gen(v, 40_000 + s), dcfg)
                if r.eligibility.is_eligible:
                    e += 1
                if r.signals:
                    k += 1
            curve.append({param: v, "hit_rate": k / seeds,
                          "eligible_rate": e / seeds})
        out[name] = {"parameter": param, "curve": curve}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.calibrate")
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--power", action="store_true",
                    help="also compute power curves")
    args = ap.parse_args(argv)

    r = measure(args.seeds)
    if args.power:
        r["power_curves"] = power_curves(args.seeds)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0

    print("Archaeon detector calibration -- {} seeds, {}".format(
        r["seeds"], r["thresholds_version"]))
    print()
    for name, d in r["detectors"].items():
        print(name)
        print("  null fire rate        {:.3f}   (eligible on {:.0%} of null corpora)"
              .format(d["null_fire_rate"], d["null_eligible_rate"]))
        print("  planted hit rate      {:.3f}   (eligible on {:.0%} of planted corpora)"
              .format(d["planted_hit_rate"], d["planted_eligible_rate"]))
        for cname, v in d["paired_control_fire_rate"].items():
            print("  control [{}] {:.3f}".format(cname.ljust(14), v))
        print("  separation            {:+.3f}".format(d["separation_vs_worst_control"]))
        print()

    if "power_curves" in r:
        print("POWER CURVES")
        for name, pc in r["power_curves"].items():
            pts = "  ".join("{}={}: {:.2f}".format(pc["parameter"], p[pc["parameter"]],
                                                   p["hit_rate"])
                            for p in pc["curve"])
            print("  {}".format(name))
            print("    {}".format(pts))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
