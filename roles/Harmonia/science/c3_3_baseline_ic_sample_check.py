"""C3-3 baseline arm: is the constants' location a rule property or an IC-sample property?

Harmonia[m2-f541bed9], 2026-09-14. Executes, does not read (an executing lens
beats a reading lens). Offline: Vivarium's registered executor through
archaeon.producer.campaign_c3_3._run; no engine, queue or ledger is touched.

Question. Ruling 57c259656 3a/3b said constants score "exactly 0.5" with
"structurally ZERO" dispersion; Archaeon's amendment says dispersion is
"exactly 0.5". The preflight (seed 0 only) measured all_zero 0.52 / all_one
0.48, dispersion 0.4996. If the location of a constant is the share of ICs
whose majority matches it, then per seed:

  P1  location(all_zero) + location(all_one) == 1 exactly
  P2  dispersion(constant) == sqrt(p (1 - p)) with p = its location
      (population SD of a 0/1 variable)
  P3  location varies across the four seeds by roughly binomial noise on N_IC

Controls.
  POSITIVE  P1/P2 must hold on the constants (they are the claimed mechanism).
  NEGATIVE  P1 must FAIL for a pair that is not complementary under the
            criterion: maj and a random table do not sum to 1.
  CHEAT     inject a fake constant whose location is forced to 0.5 in the
            checker's input: P2's predicate must then demand dispersion 0.5
            and the real row must FAIL it -- proving the predicate reads the
            row rather than passing on the value it expects.

Output: one JSON ledger, argv[1], written from Python with every row.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)

from archaeon import workspace as _ws                     # noqa: E402

_ws.assert_not_canonical("run the C3-3 baseline IC-sample check")

from archaeon.producer import campaign_c3 as C3            # noqa: E402
from archaeon.producer import campaign_c3_3 as C33         # noqa: E402

SEEDS = [0, 1, 2, 3]
LOC, DISP = C33.LOCATION_FIELD, C33.DISPERSION_FIELD
TOL = 1e-12


def run(rule_hex, seed):
    o = C33._run(rule_hex, seed=seed)
    return {"location": o.get(LOC), "dispersion": o.get(DISP),
            "per_cell_mean": o.get("accuracy_is_per_cell_mean")}


def main(out_path):
    rules = {}
    rules.update(C3.CONSTANT_RULES)
    rules.update(C3.CENTRE_RULES)
    hist = C3.historical_rules()
    rules["maj"] = hist["maj"]
    rules["random_000"] = C3.random_rule(0)
    rows = []
    for seed in SEEDS:
        for name, rh in rules.items():
            r = run(rh, seed)
            r.update({"seed": seed, "rule": name})
            rows.append(r)
    by = {(r["seed"], r["rule"]): r for r in rows}

    checks = []
    for seed in SEEDS:
        z, o = by[(seed, "all_zero")], by[(seed, "all_one")]
        s = z["location"] + o["location"]
        checks.append({"seed": seed, "check": "P1 all_zero+all_one==1 (POSITIVE)",
                       "value": s, "pass": abs(s - 1.0) < TOL})
        m, q = by[(seed, "maj")], by[(seed, "random_000")]
        s2 = m["location"] + q["location"]
        checks.append({"seed": seed, "check": "P1 maj+random_000==1 must FAIL (NEGATIVE)",
                       "value": s2, "pass": abs(s2 - 1.0) >= TOL})
        for name in C3.CONSTANT_RULES:
            r = by[(seed, name)]
            p = r["location"]
            want = math.sqrt(p * (1 - p))
            checks.append({"seed": seed, "check": "P2 dispersion==sqrt(p(1-p)) %s (POSITIVE)" % name,
                           "location": p, "dispersion": r["dispersion"], "predicted": want,
                           "pass": abs(r["dispersion"] - want) < 1e-9})
            cheat_want = math.sqrt(0.5 * 0.5)
            checks.append({"seed": seed, "check": "CHEAT forced p=0.5 must FAIL on %s unless p is 0.5" % name,
                           "dispersion": r["dispersion"], "predicted_under_cheat": cheat_want,
                           "pass": (abs(r["dispersion"] - cheat_want) >= 1e-9) or abs(p - 0.5) < TOL})
    per_rule_loc = {}
    for name in rules:
        v = [by[(s, name)]["location"] for s in SEEDS]
        mean = sum(v) / len(v)
        sd = math.sqrt(sum((x - mean) ** 2 for x in v) / (len(v) - 1))
        per_rule_loc[name] = {"by_seed": v, "mean": mean, "sd_across_seeds": sd}
    out = {"schema": "harmonia.c3_3_baseline_ic_sample_check.v1",
           "instance": "m2-f541bed9", "seeds": SEEDS,
           "n_ic": getattr(C3, "N_IC", None), "n_cells": getattr(C3, "N_CELLS", None),
           "receipt": _ws.receipt() if hasattr(_ws, "receipt") else None,
           "rows": rows, "checks": checks, "per_rule_location": per_rule_loc,
           "all_pass": all(c["pass"] for c in checks),
           "n_checks": len(checks), "n_pass": sum(1 for c in checks if c["pass"])}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, default=str)
        fh.flush()
    print("checks %d/%d pass" % (out["n_pass"], out["n_checks"]))
    for c in checks:
        if not c["pass"]:
            print("  FAIL", json.dumps(c))
    for name, d in per_rule_loc.items():
        print("  %-12s by_seed %s  sd %.4f" % (name, ["%.4f" % x for x in d["by_seed"]], d["sd_across_seeds"]))


if __name__ == "__main__":
    main(sys.argv[1])
