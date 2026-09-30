"""Tyche v1 verdicts (frozen with the preregistration).

GATE 6 (operator): at least one case where every necessary precursor would
have died under v0 selection, yet the dark ecology assembles a useful
sensor. Per Z world w and evolutionary seed s:

  de_ok(w, s): arm DE admitted a FUSED sensor on w that
     - has test gain >= 0.10, replicated (test z >= 4, both fresh seeds
       z >= 3), beats the matched random-PAIR null p95, is causal, and
       has twin z < 3 where w has a TARGET_STRUCTURE_DESTROYED twin;
     - whose two components each had max individual val gain on w
       < 0.01 at every logged evaluation (no contemporaneous ruler could
       detect value) AND test gain alone with z < 3.
  v0_fail(w, s): arm V0 admitted nothing on w that has test gain >= 0.10
     and is replicated, within the same unit budget.

GATE6 = PASS if some Z world has de_ok and v0_fail in EVERY seed run;
PARTIAL if in some but not all; FAIL otherwise. NOTHING_COULD_FIRE if no
Z world is valid (pass A: best initial single test gain >= 0.03 or the
initial-pair floor >= 0.10 voids that world).

Also reported: DENR (preservation ablation) per world; units to solve;
capability-deficit trajectory; false positives on N worlds; baseline
monotonicity (no organism's ecology baseline may fall > 0.03 below its
eco0 value: the v0 F2 manufactured-gap check).

Usage: python -m tyche.v1.report_v1 <campaign_dir>   (holds <ARM>_s<seed>/)
"""

from __future__ import annotations

import glob
import json
import os
import sys

MIN_TEST = 0.10
PREC_MAX = 0.01


def jl(p):
    return [json.loads(x) for x in open(p, encoding="ascii") if x.strip()] if os.path.exists(p) else []


def de_ok_rows(rows, w, twin_needed):
    hits = []
    for r in rows:
        if r["home"] != w or r["kind"] != "pair":
            continue
        ok = (r["home_test"][0] >= MIN_TEST and r["replicated"] and r["beats_null"]
              and r["causality"]["pass"])
        if twin_needed:
            ok = ok and "twin" in r and r["twin"]["z"] < 3.0
        comps = r.get("components", {})
        prec_ok = len(comps) == 2 and all(
            c["max_individual_val_gain_home"] is not None and c["max_individual_val_gain_home"] < PREC_MAX
            and c["test_alone_z"] < 3.0 for c in comps.values())
        if ok and prec_ok:
            hits.append(r["id"])
    return hits


def solved_rows(rows, w):
    return [r["id"] for r in rows if r["home"] == w and r["home_test"][0] >= MIN_TEST and r["replicated"]]


def evaluate(camp):
    runs = {}
    for d in sorted(glob.glob(os.path.join(camp, "*_s*"))):
        if not os.path.exists(os.path.join(d, "PASS_D.json")):
            continue
        arm, seed = os.path.basename(d).rsplit("_s", 1)
        runs[(arm, int(seed))] = d
    seeds = sorted({s for (_, s) in runs})
    any_dir = next(iter(runs.values()))
    specs = json.load(open(os.path.join(any_dir, "WORLDS.json")))
    by = {s["id"]: s for s in specs}
    zw = [s["id"] for s in specs if s["cls"] == "Z" and s["role"] == "train"]
    twins = {s["twin_of"] for s in specs if s.get("twin_of")}
    pa = {}
    for s in seeds:
        p = os.path.join(camp, f"PASS_A_s{s}", "PASS_A.json")
        pa[s] = json.load(open(p)) if os.path.exists(p) else None

    def void(w, s):
        a = pa.get(s)
        if not a:
            return None
        if a["single_best"][w]["test"] >= 0.03:
            return "initial single access"
        pf = a.get("pair_floor", {}).get(w)
        if pf and pf["best_val_joint"] >= MIN_TEST:
            return "initial pair floor"
        return None

    per = {}
    for w in zw:
        per[w] = {}
        for s in seeds:
            v = void(w, s)
            de = json.load(open(os.path.join(runs[("DE", s)], "PASS_D.json"))) if ("DE", s) in runs else []
            v0 = json.load(open(os.path.join(runs[("V0", s)], "PASS_D.json"))) if ("V0", s) in runs else []
            dn = json.load(open(os.path.join(runs[("DENR", s)], "PASS_D.json"))) if ("DENR", s) in runs else []
            hits = de_ok_rows(de, w, w in twins)
            v0s = solved_rows(v0, w)
            per[w][s] = {"void": v, "de_gate_lenses": hits, "v0_solved": v0s,
                         "denr_solved": solved_rows(dn, w), "de_solved_any": solved_rows(de, w),
                         "gate": bool(hits) and not v0s and v is None}
    passing = [w for w in zw if all(per[w][s]["gate"] for s in seeds)]
    some = [w for w in zw if any(per[w][s]["gate"] for s in seeds)]
    valid = [w for w in zw if all(per[w][s]["void"] is None for s in seeds)]
    gate6 = ("NOTHING_COULD_FIRE" if not valid else
             "PASS" if passing else "PARTIAL" if some else "FAIL")

    # descriptive: solves per arm x world class; false positives; baselines
    table, fp, mono = {}, {}, {}
    for (arm, s), d in runs.items():
        rows = json.load(open(os.path.join(d, "PASS_D.json")))
        for w in by:
            if by[w]["role"] != "train":
                continue
            table.setdefault(w, {})[f"{arm}_s{s}"] = len(solved_rows(rows, w))
        fp[f"{arm}_s{s}"] = [r["id"] for r in rows if by[r["home"]]["cls"] == "N"]
        defs = jl(os.path.join(d, "DEFICITS.jsonl"))
        e0 = {x["world"]: x for x in defs if x["tag"] == "eco0" and x["split"] == "val"}
        viol = []
        for x in defs:
            if x["split"] != "val" or x["tag"] == "eco0" or x["world"] not in e0:
                continue
            for k, v in x.items():
                if k.endswith("acc_eco") and v < e0[x["world"]][k] - 0.03:
                    viol.append((x["tag"], x["world"], k, round(v, 3), round(e0[x["world"]][k], 3)))
        mono[f"{arm}_s{s}"] = viol
    out = {"GATE6": gate6, "per_world": per, "valid_Z_worlds": valid, "passing_worlds": passing,
           "solves_by_arm": table, "admissions_on_negative_worlds": fp, "baseline_drops": mono,
           "seeds": seeds, "arms": sorted({a for a, _ in runs})}
    json.dump(out, open(os.path.join(camp, "REPORT_v1.json"), "w"), indent=1, sort_keys=True)
    return out


if __name__ == "__main__":
    o = evaluate(sys.argv[1])
    print(json.dumps({k: o[k] for k in ("GATE6", "valid_Z_worlds", "passing_worlds")}, indent=1))
