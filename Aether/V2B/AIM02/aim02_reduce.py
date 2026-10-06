"""AIM02 reducer: unit JSONs -> activity-matched L1-vs-flicker contrasts -> frozen richness disposition.

    python aim02_reduce.py UNIT_DIR [--rules RULES.json] [--out REDUCTION.json]

Primary channel = non-AIM fields only (opcode, arg1, payload). For every L1 density and seed k the treatment's
per-activity-bin statistics are compared with each flicker comparator's (C1FREE, C2RICH; same seed k), weighting the
comparator by the TREATMENT's bin mix (aim02_meter.compare_conds). Families (independent richness dimensions):
  NOVELTY     n64 (64-tick memory novelty)            diff = L1 - comparator
  REPERTOIRE  upc (distinct values entered / change)  diff
  DISCOVERY   dr2 (late-half discovery / change)      diff
  TRANSITIONS tpc (distinct transitions / change)     diff
  RECURRENCE  return-time median                      ratio = L1 / comparator
A family is material at a density if, in >= seeds_min paired seeds, L1 exceeds BOTH comparators by its
preregistered margin. n16 is reported (and used only for the WEAK clause: novelty that disappears at 64 ticks).
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
import aim02_meter as MTR  # noqa: E402

REDUCER_VERSION = "aim02_reduce.v1"
FAMILIES = {"NOVELTY": ("n64", "diff"), "REPERTOIRE": ("upc", "diff"), "DISCOVERY": ("dr2", "diff"),
            "TRANSITIONS": ("tpc", "diff"), "RECURRENCE": ("return_median", "ratio")}
DENS = ("L1D25", "L1D50", "L1D75")
COMPS = ("C1FREE", "C2RICH")


def load(d):
    out = {}
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            u = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(u, dict) and u.get("schema") == "aether.aim02.unit.v1":
            u["_file"] = os.path.basename(p)
            out[(u["cond"], u["seed_index"], u["window"], u["ticks"], u["_file"].startswith("dup_"))] = u
    return out


def contrasts(units, window, ticks):
    """Per L1 density, per seed: compare_conds vs each comparator, and vs L0 at the same density (descriptive)."""
    res = {}
    for cond in DENS:
        rows = []
        seeds = sorted(k for (c, k, w, t, dup) in units if c == cond and w == window and t == ticks and not dup)
        for k in seeds:
            tb = units[(cond, k, window, ticks, False)]["primary"]["bins"]
            row = {"seed": k, "vs": {}}
            for comp in COMPS + ("L0" + cond[2:],):
                key = (comp, k, window, ticks, False)
                if key in units:
                    row["vs"][comp] = MTR.compare_conds(tb, units[key]["primary"]["bins"])
            rows.append(row)
        res[cond] = rows
    return res


def decide(con, rules):
    R = rules
    per = {}
    for cond, rows in con.items():
        fam = {}
        for f, (metric, kind) in FAMILIES.items():
            margin = R["margins"][f]
            ok_seeds, vals = 0, []
            for r in rows:
                beat = []
                for comp in COMPS:
                    v = r["vs"].get(comp, {}).get(metric)
                    cov = r["vs"].get(comp, {}).get("coverage", 0.0)
                    if v is None or v.get(kind) is None or cov < R["coverage_min"]:
                        beat.append(False)
                        continue
                    beat.append(v[kind] >= margin)
                    vals.append(v[kind])
                if beat and all(beat):
                    ok_seeds += 1
            fam[f] = {"seeds_beating_both": ok_seeds, "seeds": len(rows), "median_" + kind:
                      st.median(vals) if vals else None, "material": ok_seeds >= R["seeds_min"]}
        # n16-only novelty (for the WEAK clause)
        n16_ok = 0
        for r in rows:
            beat = [r["vs"].get(c, {}).get("n16", {}).get("diff", -1) >= R["margins"]["NOVELTY"] for c in COMPS]
            if all(beat):
                n16_ok += 1
        mats = [f for f in fam if fam[f]["material"]]
        per[cond] = {"families": fam, "material_families": mats, "n16_material": n16_ok >= R["seeds_min"],
                     "supported": fam["NOVELTY"]["material"] and len(mats) >= 2}
    sup = [c for c in per if per[c]["supported"]]
    anym = any(per[c]["material_families"] or per[c]["n16_material"] for c in per)
    if len(sup) >= R["densities_min"]:
        disp = "RICHNESS_SUPPORTED"
    elif anym:
        disp = "RICHNESS_WEAK"
    else:
        disp = "FLICKER_EQUIVALENT"
    return {"per_density": per, "supported_densities": sup, "disposition": disp,
            "interpretation_if_flicker_equivalent": "REAIM_MOBILE_BUT_TRIVIAL"}


def cond_summary(units, window, ticks):
    out = {}
    for (c, k, w, t, dup), u in units.items():
        if w != window or t != ticks or dup:
            continue
        p = u["primary"]
        d = out.setdefault(c, {"seeds": 0, "columns_changing": [], "late_nonaim_turnover": [], "n_ch_hist": None})
        d["seeds"] += 1
        d["columns_changing"].append(p["columns_changing"] / p["M"])
        d["late_nonaim_turnover"].append(u["late_nonaim_turnover_site"])
    return {c: {"seeds": d["seeds"], "changing_column_frac_median": st.median(d["columns_changing"]),
                "late_nonaim_turnover_median": st.median(d["late_nonaim_turnover"])} for c, d in sorted(out.items())}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--window", type=int, required=True)
    ap.add_argument("--ticks", type=int, required=True)
    ap.add_argument("--rules")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    units = load(a.unit_dir)
    hashes = sorted({u["table_hash"] for u in units.values()})
    dups = []
    for (c, k, w, t, dup), u in units.items():
        if dup:
            o = units.get((c, k, w, t, False))
            dups.append({"cond": c, "seed": k, "equal": bool(o) and o["final_digest"] == u["final_digest"]
                         and o["primary"] == u["primary"]})
    res = {"schema": "aether.aim02.reduction.v1", "reducer": REDUCER_VERSION, "units": len(units),
           "table_hashes": hashes, "duplicates": dups, "conditions": cond_summary(units, a.window, a.ticks),
           "contrasts": contrasts(units, a.window, a.ticks)}
    gates = {"single_table_hash_ok": len(hashes) == 1, "duplicates_ok": bool(dups) and all(d["equal"] for d in dups)}
    res["gates"] = gates
    if a.rules:
        raw = open(a.rules, "rb").read()
        res["rules_sha256"] = hashlib.sha256(raw).hexdigest()
        dec = decide(res["contrasts"], json.loads(raw))
        if not all(gates.values()):
            dec["disposition_if_valid"] = dec["disposition"]
            dec["disposition"] = "MEASUREMENT_FAILED"
        res["decision"] = dec
    if a.out:
        open(a.out, "w", encoding="utf-8").write(json.dumps(res, indent=1))
    print(json.dumps(res["conditions"], indent=0))
    for cond, rows in res["contrasts"].items():
        for r in rows:
            for comp, v in r["vs"].items():
                print(cond, "s%d" % r["seed"], "vs", comp, "cov %.2f" % v.get("coverage", 0),
                      " ".join("%s %s" % (m, ("%+.4f" % v[m]["diff"]) if m in v else "-")
                               for m in ("n16", "n64", "upc", "tpc", "dr2")),
                      "ret %s" % (("%.2fx" % v["return_median"]["ratio"]) if "return_median" in v and v["return_median"]["ratio"] else "-"))
    if "decision" in res:
        print(json.dumps(res["decision"], indent=1))
    else:
        print(json.dumps(gates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
