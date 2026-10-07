"""PROP01 reducer: per-seed causal class, clamp counterfactual, candidate vs mechanical comparator.

    python prop01_reduce.py UNIT_DIR --candidate LAW --comparators LAW[,LAW] [--rules RULES.json] [--out F]

Unit files: <LAW>_s<k>.json (uncut) and <LAW>_s<k>_cut.json (clamp of B chosen from the uncut tree).
Per seed:
  max_gen, ever_sites, ever_radius, peak concurrent divergent sites, unknown_sites, extinction tick, re-entry,
  counts of first-time divergences by (generation, type); STRUCT_ge2 = STRUCT-typed sites at generation >= 2;
  multiplies = peak concurrent divergent sites >= rules.multiply_min.
  CLAMP: D = B's descendants in the uncut tree; cut_desc = fraction of D that ever diverge in the CUT world;
         cut_ctrl = same fraction over impulse-ever sites NOT in D and not B (matched control set).
         clamp_pass = (cut_desc <= rules.clamp_desc_max) and (cut_desc <= rules.clamp_ratio_max * cut_ctrl).
Seed class (frozen):
  LOCAL_ONLY          max_gen <= 1
  DIRECT_TRANSPORT    max_gen >= 2 and not (multiplies or STRUCT_ge2 > 0)
  MULTIGEN_UNCLAMPED  max_gen >= 2 and (multiplies or STRUCT_ge2 > 0) but the clamp check fails / absent
  MULTIGENERATION     max_gen >= 2 and (multiplies or STRUCT_ge2 > 0) and clamp_pass
Law disposition (candidate):
  CAUSAL_PROPAGATION_SUPPORTED  >= rules.seeds_min seeds MULTIGENERATION, and candidate median ever_sites >=
                                rules.reach_ratio x every comparator's median, and candidate median max_gen > every
                                comparator's median max_gen
  MULTIGENERATION_WEAK          >= 1 seed MULTIGENERATION but not SUPPORTED
  DIRECT_TRANSPORT_ONLY         no MULTIGENERATION seed and >= half the seeds DIRECT_TRANSPORT or MULTIGEN_UNCLAMPED
  LOCAL_ONLY                    otherwise
"""

import argparse
import glob
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop01_tree as T  # noqa: E402

REDUCER_VERSION = "prop01_reduce.v1"


def seed_row(u, cut, R):
    g = {}
    for k, v in u["gen_type_counts"].items():
        gg, ty = (int(x) for x in k.split("_"))
        g[(gg, ty)] = v
    struct_ge2 = sum(v for (gg, ty), v in g.items() if gg >= 2 and ty == 1)
    peak = max((r["div_sites"] for r in u["series"]), default=0)
    row = {"seed": u["seed_index"], "max_gen": u["max_gen"], "ever_sites": u["ever_sites"],
           "ever_radius": u["ever_radius"], "peak_concurrent": peak, "unknown_sites": u["unknown_sites"],
           "extinct_tick": u["extinct_tick"], "reentry": u["reentry_events"], "struct_ge2": struct_ge2,
           "by_gen": {str(gg): sum(v for (g2, _t), v in g.items() if g2 == gg) for gg in sorted({k[0] for k in g})},
           "type_counts": {"STRUCT": sum(v for (_g, t), v in g.items() if t == 1),
                           "CARRY": sum(v for (_g, t), v in g.items() if t == 2),
                           "RULE": sum(v for (_g, t), v in g.items() if t == 3)}}
    row["multiplies"] = peak >= R["multiply_min"]
    rich = row["multiplies"] or struct_ge2 > 0
    row["clamp"] = None
    if cut and cut.get("cut"):
        b = cut["cut"]["site"]
        D = T.descendants(u["tree"], b)
        ev = set(u["tree"]["site"]) - D - {b}
        cs = set(cut["cut"]["cut_ever_sites"])
        cd = (len(D & cs) / len(D)) if D else None
        cc = (len(ev & cs) / len(ev)) if ev else None
        ok = cd is not None and cd <= R["clamp_desc_max"] and (cc is None or cd <= R["clamp_ratio_max"] * cc)
        row["clamp"] = {"B": b, "descendants": len(D), "cut_desc_frac": cd, "cut_ctrl_frac": cc, "pass": bool(ok)}
    if u["max_gen"] <= 1:
        row["class"] = "LOCAL_ONLY"
    elif not rich:
        row["class"] = "DIRECT_TRANSPORT"
    elif row["clamp"] and row["clamp"]["pass"]:
        row["class"] = "MULTIGENERATION"
    else:
        row["class"] = "MULTIGEN_UNCLAMPED"
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--comparators", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    raw = open(a.rules, "rb").read()
    R = json.loads(raw)
    laws = {}
    for p in sorted(glob.glob(os.path.join(a.unit_dir, "*_s*.json"))):
        if p.endswith("_cut.json"):
            continue
        u = json.load(open(p))
        if u.get("schema") != "aether.prop01.unit.v1" or "tree" not in u:
            continue
        cp = p[:-5] + "_cut.json"
        cut = json.load(open(cp)) if os.path.exists(cp) else None
        laws.setdefault(u["law"], []).append(seed_row(u, cut, R))
    summ = {}
    for law, rows in laws.items():
        cls = [r["class"] for r in rows]
        summ[law] = {"seeds": len(rows), "classes": {c: cls.count(c) for c in sorted(set(cls))},
                     "median_ever_sites": st.median(r["ever_sites"] for r in rows),
                     "median_max_gen": st.median(r["max_gen"] for r in rows),
                     "median_radius": st.median(r["ever_radius"] for r in rows),
                     "median_peak": st.median(r["peak_concurrent"] for r in rows),
                     "median_struct_ge2": st.median(r["struct_ge2"] for r in rows),
                     "unknown_total": sum(r["unknown_sites"] for r in rows)}
    c = a.candidate
    comps = [x for x in a.comparators.split(",") if x in summ]
    nm = summ.get(c, {}).get("classes", {}).get("MULTIGENERATION", 0)
    sup = (nm >= R["seeds_min"] and all(summ[c]["median_ever_sites"] >= R["reach_ratio"] * max(1, summ[x]["median_ever_sites"])
                                        and summ[c]["median_max_gen"] > summ[x]["median_max_gen"] for x in comps))
    ncl = summ.get(c, {}).get("classes", {})
    if sup:
        disp = "CAUSAL_PROPAGATION_SUPPORTED"
    elif nm >= 1:
        disp = "MULTIGENERATION_WEAK"
    elif ncl.get("DIRECT_TRANSPORT", 0) + ncl.get("MULTIGEN_UNCLAMPED", 0) >= max(1, summ.get(c, {}).get("seeds", 0)) / 2:
        disp = "DIRECT_TRANSPORT_ONLY"
    else:
        disp = "LOCAL_ONLY"
    res = {"schema": "aether.prop01.reduction.v1", "reducer": REDUCER_VERSION, "rules_sha256": hashlib.sha256(raw).hexdigest(),
           "candidate": c, "comparators": comps, "per_law": laws, "summary": summ, "disposition": disp}
    if a.out:
        open(a.out, "w").write(json.dumps(res, indent=1))
    print(json.dumps(summ, indent=1))
    for law, rows in laws.items():
        for r in rows:
            print(law, "s%d" % r["seed"], r["class"], "gen", r["max_gen"], "ever", r["ever_sites"], "rad", r["ever_radius"],
                  "peak", r["peak_concurrent"], "S>=2", r["struct_ge2"], "unk", r["unknown_sites"], "ext", r["extinct_tick"],
                  "clamp", r["clamp"])
    print("DISPOSITION", disp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
