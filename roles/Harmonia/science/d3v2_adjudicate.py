"""Apply d3v2_calibration_plan_2026-09-14.md rules A1-A4 to the calibration ledger,
mechanically, and execute the declared property checks P-DF, P-LIN, P-LAB.

Harmonia[m2-f541bed9], 2026-09-14. Reads roles/Harmonia/science/ledgers/
d3v2_calibration_2026-09-14.json; writes argv[1]. SE(diff) is computed as for
two INDEPENDENT binomial rates, which is conservative here (v1 and v2 read the
same corpora, so the true SE of the difference is smaller); the plan did not
state the pairing, so the conservative form is the declared one.
"""
import dataclasses
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from archaeon import workspace as _ws                                  # noqa: E402

_ws.assert_not_canonical("adjudicate the d3.v2 calibration")

from archaeon import synth                                              # noqa: E402
from archaeon.detectors import d3_variance_anomaly as d3                # noqa: E402
import d3v2_calibration as CAL                                          # noqa: E402

LEDGER = os.path.join(HERE, "ledgers", "d3v2_calibration_2026-09-14.json")
INDET = 0.05


def se_diff(a, b):
    return math.sqrt(a["se"] ** 2 + b["se"] ** 2)


def rule(name, lhs, rhs, margin_sign, extra=0.0, detail=""):
    """PASS iff lhs <= rhs + extra + 2 SE(diff) (margin_sign=+1), or
    lhs >= rhs - extra - 2 SE(diff) is not used; A4 has its own form."""
    s = se_diff(lhs, rhs)
    out = {"rule": name, "lhs": lhs["rate"], "rhs": rhs["rate"], "diff": lhs["rate"] - rhs["rate"],
           "two_se_diff": 2 * s, "detail": detail}
    if 2 * s > INDET:
        out["verdict"] = "INDETERMINATE"
    else:
        out["verdict"] = "PASS" if lhs["rate"] <= rhs["rate"] + 2 * s else "FAIL"
    return out


def cell(cells, g, null, r, pos):
    for c in cells:
        if c["geometry"] == g and c["null"] == null and abs(c["r"] - r) < 1e-9 and c["positive"] == pos:
            return c
    raise KeyError((g, null, r, pos))


def adjudicate(led):
    cells = led["cells"]
    out = {}
    for g in CAL.GEOMETRIES:
        n0 = cell(cells, g, "N0", 0.0, None)
        rows = []
        rows.append(rule("A1 v2 N0 all <= v1 N0 all + 2SE", n0["v2"]["all_region"], n0["v1"]["all_region"], 1))
        for r in (0.577, 0.816):
            n2h = cell(cells, g, "N2h", r, None)
            rows.append(rule("A2 v2 N2h(|r|=%.3f) w03 <= v2 N0 w03 + 2SE" % r,
                             n2h["v2"]["target"], n0["v2"]["target"], 1))
        n1 = cell(cells, g, "N1", 0.0, None)
        rows.append(rule("A3 v2 N1 all <= v2 N0 all + 2SE", n1["v2"]["all_region"], n0["v2"]["all_region"], 1))
        for p in ("HI", "LO"):
            pc = cell(cells, g, "N0", 0.0, p)
            v1, v2 = pc["v1"]["target"], pc["v2"]["target"]
            s = se_diff(v1, v2)
            a4 = {"rule": "A4 POS-%s untrended: v2 w03 >= v1 w03 - 0.10" % p,
                  "lhs": v2["rate"], "rhs": v1["rate"], "diff": v2["rate"] - v1["rate"],
                  "two_se_diff": 2 * s}
            a4["verdict"] = ("INDETERMINATE" if 2 * s > INDET else
                             ("PASS" if v2["rate"] >= v1["rate"] - 0.10 else "FAIL"))
            rows.append(a4)
        verdicts = [x["verdict"] for x in rows]
        admitted = all(v == "PASS" for v in verdicts)
        out[g] = {"rules": rows,
                  "admission": ("ADMITTED (synthetic)" if admitted else
                                ("INDETERMINATE" if "INDETERMINATE" in verdicts and "FAIL" not in verdicts
                                 else "REFUSED")),
                  "exact_refs_target_N0": n0.get("exact_refs_target"),
                  "N0_lower_higher": {"v1": [n0["v1"]["lower"], n0["v1"]["higher"]],
                                      "v2": [n0["v2"]["lower"], n0["v2"]["higher"]]},
                  "not_all_eligible": {v: max(c[v]["corpora_not_all_regions_eligible"] for c in cells
                                              if c["geometry"] == g) for v in ("v1", "v2")}}
    return out


def p_lin():
    """P-LIN: w03 an exact line in commit order, other regions i.i.d. N0 at LIVE."""
    res = {}
    for g in ("FLOOR", "LIVE"):
        n_t, n_o = CAL.GEOMETRIES[g]
        synth.reset()
        import random
        rng = random.Random(7)
        rows = []
        for ri in range(CAL.N_REGIONS):
            reg = "w{:02d}".format(ri)
            n = n_t if reg == CAL.TARGET else n_o
            for j in range(n):
                m = 0.5 + 0.01 * j if reg == CAL.TARGET else rng.gauss(0.5, CAL.SIGMA)
                rows.append(synth._row(reg, "F", "p0", m, ri / 7.0))
        c = synth._wrap(rows, "p_lin:%s" % g)
        for name, dc in (("v1", CAL.V1), ("v2", CAL.V2)):
            sig = [s for s in d3.detect(c, dc).signals if s.regions[0] == CAL.TARGET]
            res["%s_%s" % (g, name)] = (None if not sig else
                                        {k: sig[0].values[k] for k in ("variance_ratio", "direction", "serial_r",
                                                                        "exchangeability", "region_variance")})
    return res


def p_lab(led):
    """P-LAB: on a v2 signal, is the exchangeability label computed on raw rows?
    Executed on one N2h |r|=0.816 LIVE-positive corpus where v2 fires on w03."""
    c = CAL.build(123_456, "LIVE", "N0", 0.816, "LO")
    sig = [s for s in d3.detect(c, CAL.V2).signals if s.regions[0] == CAL.TARGET]
    if not sig:
        return {"fired": False}
    v = sig[0].values
    rows = [r for r in c.rows if r.region == CAL.TARGET]
    resid = d3._detrended(rows)
    n = len(resid)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(resid) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in resid)
    r_resid = (sum((x - mx) * (y - my) for x, y in zip(xs, resid)) / math.sqrt(sxx * syy)) if syy > 0 else 0.0
    return {"fired": True, "detector_version": sig[0].detector_version, "label": v["exchangeability"],
            "serial_r_reported": v["serial_r"], "serial_r_of_residuals": r_resid,
            "trend_inflation_reported": v["trend_inflation_of_ratio"]}


def main(out_path):
    led = json.load(open(LEDGER))
    if led.get("status") != "complete":
        raise SystemExit("ledger not complete: %s" % led.get("status"))
    res = {"schema": "harmonia.d3v2_adjudication.v1", "instance": "m2-f541bed9",
           "ledger": "roles/Harmonia/science/ledgers/d3v2_calibration_2026-09-14.json",
           "ledger_receipt": led.get("receipt"), "harness_controls": led.get("harness_controls"),
           "receipt": _ws.receipt(), "se_diff_form": "independent binomial (conservative; declared)",
           "by_geometry": adjudicate(led), "P_LIN": p_lin(), "P_LAB": p_lab(led)}
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
        fh.flush()
    for g, v in res["by_geometry"].items():
        print("==", g, v["admission"], "exact", v["exact_refs_target_N0"], "N0 L/H", v["N0_lower_higher"],
              "not_all_eligible", v["not_all_eligible"])
        for r in v["rules"]:
            print("   %-52s lhs %.4f rhs %.4f diff %+.4f 2SE %.4f  %s"
                  % (r["rule"], r["lhs"], r["rhs"], r["diff"], r["two_se_diff"], r["verdict"]))
    print("P_LIN", json.dumps(res["P_LIN"]))
    print("P_LAB", json.dumps(res["P_LAB"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
