"""PLAN s4 V3: engine-plant validation of REL2 (rep 0 from W-N's saved cells, rep 1 fresh arrays).
Writes out/v3_plants.json and prints a per-cell table."""
import glob
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "W-N"))
import swap_rel2 as s2  # noqa: E402
import swap_rel as wn  # noqa: E402

TAB = s2.load_table()
FIXED_Z = {("P1S", "S1"): -1.0, ("P1S", "S"): -1.0, ("P1S", "S0"): 1.0,
           ("P1SK", "S"): 0.0, ("P1SK", "Kp"): 0.0, ("P1SK", "site_all"): -1.0}


def region(z):
    return "FLIP_REL" if z < -0.5 else ("NO_EFFECT_REL" if z > 0.5 else "CHANCE_REL")


def exact(z):
    return min(abs(z - t) for t in (-1.0, 0.0, 1.0)) <= 0.05


def rows_rep0():
    out = []
    for plant in ("P1S", "P1SK"):
        J = json.load(open(HERE.parent / "W-N" / "out" / f"plants_engine_r0_{plant}.json"))
        f0 = {c["arm"]: 1 - c["swap"][0] for c in J["cells"] if c["q"] == 0}
        for c in J["cells"]:
            z = FIXED_Z.get((plant, c["arm"]), 1 - 2 * f0[c["arm"]])
            r = s2.label(c["ungated"], c["normal"][1], c["P"], c["K"], dz=TAB[f"P{c['P']}_K{c['K']}"])
            out.append({"rep": 0, "plant": plant, "q": c["q"], "arm": c["arm"], "z_true": z, "normal": c["normal"],
                        "z_hat": c["z"], "cert": c["ungated"], "rel2": r["label"], "strict": r["strict"],
                        "NE": r["NE"], "attain": r["attain"], "wn_gated": c["verdict"], "abs": c["absolute"]})
    return out


def rows_rep1():
    out = []
    for plant in ("P1S", "P1SK"):
        arr = {}
        for f in sorted(glob.glob(str(HERE / "out" / f"plants_r1_{plant}_*.npz"))):
            d = np.load(f)
            arr.update({k: d[k] for k in d.files})
        qs = sorted({float(k.split("_")[0][1:]) for k in arr})
        kinds = sorted({k.split("_", 1)[1] for k in arr} - {"normal"})
        f0 = {}
        if "q0.00_normal" in arr:
            for k in kinds:
                f0[k] = 1 - np.nanmean(arr[f"q0.00_{k}"])
        for q in qs:
            n = arr[f"q{q:.2f}_normal"]
            for k in kinds:
                sw = arr[f"q{q:.2f}_{k}"]
                z = FIXED_Z.get((plant, k), 1 - 2 * f0[k])
                r = s2.swap_verdict_rel2(n, sw, dz=TAB["P256_K11"])
                w = wn.swap_verdict_rel(n, sw)
                out.append({"rep": 1, "plant": plant, "q": q, "arm": k, "z_true": float(z), "normal": r["normal"],
                            "z_hat": r["z"], "cert": r["certificate"], "rel2": r["label"], "strict": r["strict"],
                            "NE": r["NE"], "attain": r["attain"], "wn_gated": w["verdict"],
                            "abs": wn.absolute_verdict(n, sw)})
    return out


def checks(rows, key="rel2", truth_override=None):
    false_c, miss, hit, ne_bad = [], [], [], []
    for r in rows:
        z = r["z_true"] if truth_override is None else truth_override(r)
        v = r[key]
        if v in s2.CERTS and v != region(z):
            false_c.append(r)
        if exact(z) and r["attain"][region(z)]:
            (hit if v == region(z) else miss).append(r)
        if v == "NOT_ELIGIBLE" and any(r["attain"].values()) and r["cert"] not in s2.CERTS:
            ne_bad.append(r)
    n_att = len(hit) + len(miss)
    return {"false_certificates": len(false_c), "attainable_cells": n_att,
            "issued_when_attainable": len(hit) / n_att if n_att else None,
            "ne_inconsistent": len(ne_bad),
            "PASS": len(false_c) == 0 and (n_att == 0 or len(hit) / n_att >= 0.80) and not ne_bad,
            "false_list": [(r["rep"], r["plant"], r["q"], r["arm"], r[key]) for r in false_c],
            "miss_list": [(r["rep"], r["plant"], r["q"], r["arm"], r[key]) for r in miss]}


if __name__ == "__main__":
    rows = rows_rep0() + rows_rep1()
    res = {}
    for rep in (0, 1):
        R = [r for r in rows if r["rep"] == rep]
        res[f"rep{rep}_REL2"] = checks(R)
        res[f"rep{rep}_REL2_STRICT"] = checks(R, "strict")
        res[f"rep{rep}_WN_gated_mustfail_b"] = checks(R, "wn_gated")
        swapped = lambda r: (-1.0 if r["z_true"] > 0.5 else (1.0 if r["z_true"] < -0.5 else r["z_true"]))
        res[f"rep{rep}_REL2_swapped_truth_mustfail_a"] = checks(R, truth_override=swapped)
    for r in rows:
        print(f"r{r['rep']} {r['plant']:4s} q={r['q']:.2f} {r['arm']:8s} zt={r['z_true']:+.2f} "
              f"n={r['normal'][0]:.3f}[{r['normal'][1]:.3f}] zh={r['z_hat'] if r['z_hat'] is None else round(r['z_hat'], 2)} "
              f"cert={r['cert']:13s} REL2={r['rel2']:13s} strict={r['strict']:13s} WN={r['wn_gated']:13s} "
              f"abs={r['abs']:9s} NE={','.join(x[:2] for x in r['NE'])}")
    for k, v in res.items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ("false_list",)}, "false:", v["false_list"][:6])
    json.dump({"checks": res, "rows": rows}, open(HERE / "out" / "v3_plants.json", "w"), indent=1, default=str)
