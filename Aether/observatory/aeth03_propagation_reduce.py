"""Apply PHYSICS_DESIGN_02 s2.4's preregistered thresholds to the assay.

Reads `prop_<law>_n<n>_s<k>.json` from a directory, pools origins per law
and arm, and evaluates the KILL / EARNS-AN-INTERVENTION criteria against
v1 from the same assay. Thresholds are copied from the design document;
changing one requires changing the document.
"""

import argparse
import glob
import json
import os
import statistics

K1_ESC_X, K1_ESC_FLOOR = 2.0, 0.05
K1_SUST_X, K1_SUST_FLOOR = 2.0, 0.02
K2_MECH = 0.90
K3_ON = 0.10
K4_FRAC, K4_RADIUS, K4_SHARE = 0.25, 60, 0.50
J1_SUST, J1_X = 0.10, 3.0
J2_SEED = 0.05
J3_DEPTH = 8


def pool(runs):
    s = [r["summary"] for r in runs]
    n = len(s)
    new = sum(x["new_differences"] for x in s)
    gen1 = sum(x["new_gen1"] for x in s)
    sust = [x for x in s if x["class"] == "SUSTAINED"]
    classes = {}
    for x in s:
        classes[x["class"]] = classes.get(x["class"], 0) + 1
    return {
        "origins": n,
        "classes": classes,
        "P_esc": sum(x["max_radius"] >= 3 for x in s) / n,
        "P_sec": sum(x["max_generation"] >= 2 for x in s) / n,
        "P_sust": len(sust) / n,
        "M_gen1_share": gen1 / new if new else None,
        "new_differences": new,
        "new_gen_ge2": sum(x["new_gen_ge2"] for x in s),
        "new_gen_ge5": sum(x["new_gen_ge5"] for x in s),
        "G_s": statistics.median([x["max_generation"] for x in sust]) if sust else None,
        "median_max_generation": statistics.median([x["max_generation"] for x in s]),
        "max_max_generation": max(x["max_generation"] for x in s),
        "median_max_radius": statistics.median([x["max_radius"] for x in s]),
        "max_max_radius": max(x["max_radius"] for x in s),
        "F_median_final_fraction": statistics.median(
            [x["final_differing_fraction"] for x in s]),
        "share_radius_ge_60": sum(x["max_radius"] >= K4_RADIUS for x in s) / n,
        "died": sum(x["died"] for x in s) / n,
        "branch_points": sum(x["branch_points"] for x in s),
        "reentries": sum(x["reentries"] for x in s),
        "locality_violations": sum(x["locality_violations"] for x in s),
    }


def judge(off, on, base_off, per_seed_sust):
    k1 = (off["P_esc"] <= max(K1_ESC_X * base_off["P_esc"], K1_ESC_FLOOR)
          and off["P_sust"] <= max(K1_SUST_X * base_off["P_sust"], K1_SUST_FLOOR))
    k2 = off["M_gen1_share"] is not None and off["M_gen1_share"] >= K2_MECH
    k3 = (off["P_sust"] <= max(K1_SUST_X * base_off["P_sust"], K1_SUST_FLOOR)
          and on["P_sust"] >= K3_ON)
    k4 = (off["F_median_final_fraction"] >= K4_FRAC
          or off["share_radius_ge_60"] >= K4_SHARE)
    j1 = off["P_sust"] >= J1_SUST and off["P_sust"] >= J1_X * base_off["P_sust"]
    j2 = all(p >= J2_SEED for p in per_seed_sust)
    j3 = off["G_s"] is not None and off["G_s"] >= J3_DEPTH
    j4 = not k4
    killed = k1 or k2 or k3 or k4
    earns = (not killed) and j1 and j2 and j3 and j4
    return {"K1_local": k1, "K2_mechanical": k2, "K3_perturbation_dependent": k3,
            "K4_noise": k4, "J1": j1, "J2_each_seed": j2, "J3_depth": j3,
            "J4": j4, "per_seed_P_sust_off": per_seed_sust,
            "verdict": "KILLED" if killed else ("EARNS_INTERVENTION" if earns
                                                else "UNRESOLVED")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    a = ap.parse_args(argv)
    by = {}
    for p in sorted(glob.glob(os.path.join(a.dir, "prop_*_n*_s*.json"))):
        if os.path.basename(p).startswith("prop_null_"):
            continue
        with open(p, encoding="utf-8") as fh:
            r = json.load(fh)
        by.setdefault(r["variant"], []).append(r)
    out = {"laws": {}, "verdicts": {}}
    for law, rs in by.items():
        out["laws"][law] = {
            arm: pool([run for r in rs for run in r["arms"][arm]])
            for arm in ("perturbation_off", "perturbation_on")}
        out["laws"][law]["seeds"] = sorted(r["seed_index"] for r in rs)
    if "v1" in out["laws"]:
        base = out["laws"]["v1"]["perturbation_off"]
        for law, rs in by.items():
            if law == "v1":
                continue
            per_seed = [pool(r["arms"]["perturbation_off"])["P_sust"]
                        for r in sorted(rs, key=lambda x: x["seed_index"])]
            out["verdicts"][law] = judge(out["laws"][law]["perturbation_off"],
                                         out["laws"][law]["perturbation_on"],
                                         base, per_seed)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
