"""AIM01 reducer: unit JSONs -> cells, paired L1-vs-L0 contrasts, L0 density contrasts, verdicts.

    python aim01_reduce.py UNIT_DIR [--rules RULES.json] [--out REDUCTION.json]

All primary quantities are EFFECT (re-aim bookkeeping excluded). Pairing key = (density, seed).
Rules (RULES.json) are applied only with --rules; the rules file is hashed into the output.
Rung hierarchy reported separately (order s8): AIM_EXPANDS, MEDIUM_EXPANDS, MUTABILITY_PERSISTS,
NONTRIVIAL_DYNAMICS.
"""

import argparse
import glob
import hashlib
import json
import os
import statistics as st
import sys

REDUCER_VERSION = "aim01_reduce.v1"
DENS = ("D25", "D50", "D75")


def load(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            u = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(u, dict) and u.get("schema") == "aether.aim01.unit.v1":
            u["_file"] = os.path.basename(p)
            out.append(u)
    return out


def cell(u):
    s, ser = u["summary"], u["series"]
    nb = len(ser)
    rate = [r["eff_turnover"] for r in ser]
    tail = rate[max(0, nb - max(1, nb // 10)):]
    mid = rate[nb // 2: max(nb // 2 + 1, (6 * nb) // 10)]
    late = s["late_turnover_eff"]
    tq = next((r["tick"] for r in ser if r["eff_turnover"] <= 2 * late), None)
    # support saturation: first bin at which ever_changed_eff reaches 99% of its final value
    fin = s["ever_changed_eff"]
    tsat = next((r["tick"] for r in ser if fin == 0 or r["ever_changed_eff"] >= 0.99 * fin), None)
    tsat_tgt = next((r["tick"] for r in ser if r["ever_targeted_site"] >= 0.99 * s["ever_targeted_site"]), None)
    lb = [r for r in ser if r["tick"] > u["ticks"] - u["late"]]
    return dict(file=u["_file"], law=u["law"], dens=u["density_id"], seed=u["seed_index"], n=u["n"],
                ticks=u["ticks"], table_hash=u["table_hash"], final_digest=u["final_digest"],
                persistence=(st.mean(tail) / st.mean(mid)) if mid and st.mean(mid) > 0 else None,
                t_quiesce=tq, t_support_sat=tsat, t_target_sat=tsat_tgt,
                late_active=st.mean(r["active_density"] for r in lb) if lb else None,
                late_reaim_rate=st.mean(r["reaim_rate"] for r in lb) if lb else None,
                final_energy_mean=ser[-1]["energy_mean"], final_energy_zero=ser[-1]["energy_zero_frac"],
                max_field_share=max(s["late_field_share_eff"]),
                wall=u["wall_seconds"], vram=(u.get("gpu") or {}).get("mempool_total_bytes"),
                rss=u.get("host_rss_bytes"), **s)


KEYS = ["ever_changed_eff", "ever_changed_raw", "frozen_strict_eff", "frozen_net64_eff", "late_turnover_eff",
        "late_turnover_raw", "persistence", "t_quiesce", "t_support_sat", "t_target_sat", "late_active",
        "late_reaim_rate", "ever_targeted_site", "ever_targeted_tmpl_sf", "init_support_site",
        "init_support_tmpl_sf", "change_given_new_target", "change_given_init_target",
        "overlap_changed_in_targeted", "overlap_changed_in_init", "late_out_init_share",
        "tail64_novel_change_frac", "tail64_periodic_le16_frac", "tail64_unique_nonaim_mean",
        "max_field_share", "final_energy_mean", "final_energy_zero", "subset_violations"]


def med(cs, k):
    v = [c[k] for c in cs if c.get(k) is not None]
    return st.median(v) if v else None


def summarize(cells):
    g = {}
    for c in cells:
        g.setdefault((c["law"], c["dens"], c["n"], c["ticks"]), []).append(c)
    out = []
    for (law, d, n, t), cs in sorted(g.items()):
        row = dict(law=law, dens=d, n=n, ticks=t, seeds=len(cs))
        for k in KEYS:
            row[k] = med(cs, k)
        out.append(row)
    return out


def paired(cells):
    idx = {(c["law"], c["dens"], c["seed"]): c for c in cells}
    out = {}
    for d in DENS:
        rows = []
        for (law, dd, k), c1 in sorted(idx.items()):
            if law != "L1" or dd != d or ("L0", d, k) not in idx:
                continue
            c0 = idx[("L0", d, k)]
            rows.append(dict(seed=k,
                             d_ever=c1["ever_changed_eff"] - c0["ever_changed_eff"],
                             d_frozen=c1["frozen_strict_eff"] - c0["frozen_strict_eff"],
                             d_target_sf=c1["ever_targeted_tmpl_sf"] - c0["ever_targeted_tmpl_sf"],
                             d_target_site=c1["ever_targeted_site"] - c0["ever_targeted_site"],
                             turnover_ratio=(c1["late_turnover_eff"] / c0["late_turnover_eff"]
                                             if c0["late_turnover_eff"] > 0 else None)))
        out[d] = rows
    return out


def density_contrast(cells):
    """L0 only: paired by seed, D75-D25, D50-D25, D75-D50 of ever_changed_eff."""
    idx = {(c["dens"], c["seed"]): c for c in cells if c["law"] == "L0"}
    seeds = sorted({k for (_d, k) in idx})
    out = {}
    for a, b in (("D25", "D50"), ("D50", "D75"), ("D25", "D75")):
        v = [idx[(b, k)]["ever_changed_eff"] - idx[(a, k)]["ever_changed_eff"]
             for k in seeds if (a, k) in idx and (b, k) in idx]
        out["%s->%s" % (a, b)] = {"diffs": v, "median": st.median(v) if v else None}
    return out


def decide(cells, pairs, dcon, rules, gates):
    R = rules
    res = {"gates": gates}
    # Initial-density verdict (L0)
    m = R["materiality"]
    d25_50, d50_75, d25_75 = (dcon[k]["median"] for k in ("D25->D50", "D50->D75", "D25->D75"))
    if None in (d25_50, d50_75, d25_75):
        init = "UNRESOLVED"
    elif max(abs(d25_50), abs(d50_75), abs(d25_75)) < m:
        init = "INIT_SUPPORT_ROBUST"
    elif abs(d25_75) >= m and ((d25_50 >= 0 and d50_75 >= 0) or (d25_50 <= 0 and d50_75 <= 0)):
        init = "INIT_SUPPORT_SENSITIVE"
    else:
        init = "MIXED"
    l0 = [c for c in cells if c["law"] == "L0"]
    ov = [med([c for c in l0 if c["dens"] == d], "overlap_changed_in_init") for d in DENS]
    geom = init == "INIT_SUPPORT_SENSITIVE" and all(o is not None and o >= R["init_geometry_overlap_min"] for o in ov)
    res["initial_density"] = {"class": init, "paired_medians": {k: v["median"] for k, v in dcon.items()},
                              "L0_overlap_changed_in_init_by_density": ov,
                              "INITIAL_GEOMETRY_DOMINANT": geom}
    # Re-aim rungs per density
    per = {}
    for d in DENS:
        pr = pairs.get(d, [])
        l1 = [c for c in cells if c["law"] == "L1" and c["dens"] == d]
        if not pr:
            continue
        n = len(pr)
        favor = sum(1 for p in pr if p["d_ever"] > 0)
        info = {"seeds": n, "d_ever_median": st.median(p["d_ever"] for p in pr), "seeds_favor_L1": favor,
                "d_frozen_median": st.median(p["d_frozen"] for p in pr),
                "d_target_sf_median": st.median(p["d_target_sf"] for p in pr),
                "d_target_site_median": st.median(p["d_target_site"] for p in pr)}
        info["AIM_EXPANDS"] = info["d_target_sf_median"] >= R["target_growth_min"]
        info["MEDIUM_EXPANDS"] = (info["d_ever_median"] >= m and favor >= R["seeds_favor_min"]
                                  and info["d_frozen_median"] < 0 and info["AIM_EXPANDS"])
        pers = med(l1, "persistence")
        outi = med(l1, "late_out_init_share")
        info["L1_persistence"] = pers
        info["L1_late_out_init_share"] = outi
        info["MUTABILITY_PERSISTS"] = (info["MEDIUM_EXPANDS"] and pers is not None and pers >= R["persistence_min"]
                                       and outi is not None and outi >= R["late_out_init_min"])
        att = {"low_novelty": (med(l1, "tail64_novel_change_frac") or 0.0) <= R["novelty_max_trivial"],
               "short_period": (med(l1, "tail64_periodic_le16_frac") or 0.0) >= R["periodic_min_trivial"],
               "one_field": (med(l1, "max_field_share") or 0.0) >= R["field_share_min_trivial"]}
        info["attack"] = att
        info["attack_values"] = {k: med(l1, k) for k in ("tail64_novel_change_frac", "tail64_periodic_le16_frac",
                                                         "max_field_share", "tail64_unique_nonaim_mean")}
        info["NONTRIVIAL_DYNAMICS"] = info["MUTABILITY_PERSISTS"] and not any(att.values())
        per[d] = info
    res["per_density"] = per
    ext = [d for d, v in per.items() if v["MEDIUM_EXPANDS"]]
    res["REAIM_EXTENDS_SUPPORT"] = len(ext) >= R["densities_min"]
    res["extending_densities"] = ext
    if not all(gates[k] for k in gates if k.endswith("_ok")):
        disp = "MEASUREMENT_FAILED"
    elif not res["REAIM_EXTENDS_SUPPORT"]:
        disp = "REAIM_NO_SUPPORT_EFFECT"
    else:
        nt = [d for d in ext if per[d]["NONTRIVIAL_DYNAMICS"]]
        disp = "REAIM_NONTRIVIAL_CANDIDATE" if len(nt) >= R["densities_min"] else "REAIM_MOBILE_BUT_TRIVIAL"
    res["disposition"] = disp
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--rules")
    ap.add_argument("--continuity", default=None, help="JSON {seed: ER01 final digest} for L0 D50")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    us = load(a.unit_dir)
    main_u = [u for u in us if not u["_file"].startswith("dup_")]
    dups = []
    for d in (u for u in us if u["_file"].startswith("dup_")):
        o = [u for u in main_u if u["_file"] == d["_file"][4:]]
        dups.append({"dup": d["_file"], "equal": bool(o) and o[0]["final_digest"] == d["final_digest"]
                     and o[0]["series"] == d["series"]})
    cells = [cell(u) for u in main_u]
    hashes = sorted({c["table_hash"] for c in cells})
    res = {"schema": "aether.aim01.reduction.v1", "reducer": REDUCER_VERSION, "units": len(cells),
           "table_hashes": hashes, "duplicates": dups, "cells": cells, "summary": summarize(cells),
           "paired": paired(cells), "L0_density_contrast": density_contrast(cells)}
    l0 = [c for c in cells if c["law"] == "L0"]
    gates = {
        "subset_violations_ok": all(c["subset_violations"] == 0 for c in cells),
        "L0_raw_equals_effect_ok": all(c["late_turnover_raw"] == c["late_turnover_eff"]
                                       and c["ever_changed_raw"] == c["ever_changed_eff"] for c in l0),
        "single_table_hash_ok": len(hashes) == 1,
        "duplicates_ok": bool(dups) and all(d["equal"] for d in dups),
    }
    if a.continuity:
        ref = json.load(open(a.continuity))
        chk = [(c["seed"], c["final_digest"] == ref.get(str(c["seed"]))) for c in l0
               if c["dens"] == "D50" and str(c["seed"]) in ref]
        gates["L0_D50_equals_ER01_ok"] = bool(chk) and all(x for _, x in chk)
        res["continuity_checked"] = chk
    if a.rules:
        raw = open(a.rules, "rb").read()
        res["rules_sha256"] = hashlib.sha256(raw).hexdigest()
        res["decision"] = decide(cells, res["paired"], res["L0_density_contrast"], json.loads(raw), gates)
    else:
        res["gates"] = gates
    if a.out:
        open(a.out, "w", encoding="utf-8").write(json.dumps(res, indent=1))
    for r in res["summary"]:
        print("%s %s n=%d T=%d k=%d ever_eff %.4f raw %.4f tgt_site %.4f init_site %.4f frozen %.4f late_eff %.6f "
              "raw %.6f persist %s novel %s per16 %s uniq %s out_init %s tsat %s tgt_sat %s"
              % (r["law"], r["dens"], r["n"], r["ticks"], r["seeds"], r["ever_changed_eff"], r["ever_changed_raw"],
                 r["ever_targeted_site"], r["init_support_site"], r["frozen_strict_eff"], r["late_turnover_eff"],
                 r["late_turnover_raw"], r["persistence"], r["tail64_novel_change_frac"],
                 r["tail64_periodic_le16_frac"], r["tail64_unique_nonaim_mean"], r["late_out_init_share"],
                 r["t_support_sat"], r["t_target_sat"]))
    if "decision" in res:
        print(json.dumps(res["decision"], indent=1))
    else:
        print(json.dumps(gates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
