"""ER01 reducer: unit JSONs -> per-cell table, paired regime contrasts, disposition.

    python er01_reduce.py UNIT_DIR [--rules RULES.json] [--out REDUCTION.json]

Without --rules it only tabulates (Flight 1 / Flight 2 use). With --rules (the
preregistered thresholds) it also applies the order's dispositions. The rules
file is part of the preregistration and is hashed into the output.

Definitions (all from er01_run.py output, perturbation arm P0 unless stated):
  late_turnover   late_window.tmpl_change_site_per_tick: mean fraction of sites
                  whose template changed per tick over the final `late` ticks
  frozen_strict   fraction of sites with no template change at any tick of the
                  final `late` ticks
  persistence     mean tmpl_change_site over the final 10% of bins divided by
                  the mean over the bins in [50%, 60%) of the horizon. ~1 =
                  stationary, << 1 = still decaying (relaxation, not sustained)
  t_quiesce       first bin end tick at which tmpl_change_site <= 2 x the
                  late-window rate ("within 2x of its late level"); a
                  relaxation-time proxy, defined identically for every regime
  paired ratio    late_turnover(regime, seed k) / late_turnover(R0, seed k)
"""

import argparse
import glob
import hashlib
import json
import os
import statistics as st
import sys

REDUCER_VERSION = "er01_reduce.v1"


def load(unit_dir):
    units = []
    for p in sorted(glob.glob(os.path.join(unit_dir, "*.json"))):
        if p.endswith(("plan.json", "REDUCTION.json")) or os.path.basename(p).startswith("RULES"):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if d.get("schema") != "aether.er01.unit.v1":
            continue
        d["_file"] = os.path.basename(p)
        units.append(d)
    return units


def cell_metrics(u):
    s = u["series"]
    lw = u["late_window"]
    nb = len(s)
    rate = [r["tmpl_change_site"] for r in s]
    tail = rate[max(0, nb - max(1, nb // 10)):]
    mid = rate[nb // 2: max(nb // 2 + 1, (6 * nb) // 10)]
    late = lw["tmpl_change_site_per_tick"]
    t_q = None
    for r in s:
        if r["tmpl_change_site"] <= 2 * late:
            t_q = r["tick"]
            break
    late_bins = [r for r in s if r["tick"] > u["ticks"] - u["late"]]

    def lmean(k):
        return st.mean(r[k] for r in late_bins) if late_bins else None

    return {
        "file": u["_file"], "regime": u["regime"], "label": u["regime_label"],
        "pert": u["perturbation"], "seed_index": u["seed_index"], "n": u["n"],
        "ticks": u["ticks"], "late": u["late"],
        "regime_table_hash": u["regime_table_hash"], "final_digest": u["final_digest"],
        "late_turnover": late,
        "frozen_strict": lw["frozen_strict"],
        "frozen_net64": lw["frozen_net64"],
        "ever_changed": s[-1]["ever_changed"],
        "persistence": (st.mean(tail) / st.mean(mid)) if mid and st.mean(mid) > 0 else None,
        "t_quiesce": t_q,
        "first_bin_turnover": rate[0],
        "late_active_density": lmean("active_density"),
        "late_write_density": lmean("write_density"),
        "late_starved_density": lmean("starved_density"),
        "late_rain_events": lmean("rain_events"),
        "late_starve_events": lmean("starve_events"),
        "late_revive_events": lmean("revive_events"),
        "final_energy_mean": s[-1]["energy_mean"],
        "final_energy_median": s[-1]["energy_median"],
        "final_energy_zero_frac": s[-1]["energy_zero_frac"],
        "field_share": lw["field_share"],
        "top_decile_share": lw["top_decile_share"],
        "change_count_gini": lw["change_count_gini_changed_sites"],
        "periodic_le16": lw["tail64_periodic_le16_frac"],
        "novel_change_frac": lw["tail64_novel_change_frac"],
        "tail64_changes": lw["tail64_changes"],
        "wall_seconds": u["wall_seconds"],
        "vram_pool_bytes": (u.get("gpu") or {}).get("mempool_total_bytes"),
        "host_rss_bytes": u.get("host_rss_bytes"),
    }


def summarize(cells):
    groups = {}
    for c in cells:
        groups.setdefault((c["regime"], c["pert"], c["n"], c["ticks"]), []).append(c)
    out = []
    keys = ["late_turnover", "frozen_strict", "frozen_net64", "persistence", "t_quiesce",
            "late_active_density", "late_starved_density", "late_rain_events",
            "late_starve_events", "late_revive_events", "final_energy_mean",
            "final_energy_zero_frac", "periodic_le16", "novel_change_frac",
            "top_decile_share", "ever_changed"]
    for (reg, pert, n, ticks), cs in sorted(groups.items()):
        row = {"regime": reg, "label": cs[0]["label"], "pert": pert, "n": n, "ticks": ticks,
               "seeds": len(cs)}
        for k in keys:
            vals = [c[k] for c in cs if c[k] is not None]
            row[k + "_median"] = st.median(vals) if vals else None
            row[k + "_min"] = min(vals) if vals else None
            row[k + "_max"] = max(vals) if vals else None
        out.append(row)
    return out


def paired(cells, pert="P0"):
    base = {(c["seed_index"], c["n"], c["ticks"]): c for c in cells
            if c["regime"] == "R0" and c["pert"] == pert}
    out = {}
    for c in cells:
        if c["pert"] != pert or c["regime"] == "R0":
            continue
        b = base.get((c["seed_index"], c["n"], c["ticks"]))
        if b is None:
            continue
        r = c["late_turnover"] / b["late_turnover"] if b["late_turnover"] > 0 else float("inf")
        out.setdefault(c["regime"], []).append(
            {"seed_index": c["seed_index"], "ratio": r,
             "d_frozen_strict": c["frozen_strict"] - b["frozen_strict"]})
    return out


def decide(cells, pairs, rules):
    """Apply the preregistered rules. Returns per-regime class + overall disposition."""
    R = rules
    per = {}
    p0 = [c for c in cells if c["pert"] == "P0"]
    for reg in sorted({c["regime"] for c in p0}):
        cs = [c for c in p0 if c["regime"] == reg]
        med = lambda k: st.median(c[k] for c in cs if c[k] is not None)  # noqa: E731
        info = {"seeds": len(cs), "late_turnover_median": med("late_turnover"),
                "frozen_strict_median": med("frozen_strict"),
                "late_active_median": med("late_active_density")}
        if med("late_active_density") < R["starved_active_max"] and \
                med("late_turnover") < R["starved_turnover_max"]:
            info["class"] = "ENERGY_STARVED"
            per[reg] = info
            continue
        if reg == "R0":
            info["class"] = "REFERENCE"
            per[reg] = info
            continue
        pr = pairs.get(reg, [])
        frac_up = (sum(1 for p in pr if p["ratio"] >= R["mobile_ratio_min"]) / len(pr)) if pr else 0.0
        info["paired_ratio_median"] = st.median(p["ratio"] for p in pr) if pr else None
        info["paired_frac_ratio_ge_min"] = frac_up
        sustained = med("persistence") >= R["persistence_min"]
        info["persistence_median"] = med("persistence")
        mobile = (frac_up >= R["mobile_seed_frac_min"] and sustained and
                  med("late_turnover") >= R["mobile_turnover_abs_min"] and
                  med("frozen_strict") <= R["mobile_frozen_strict_max"])
        info["mobile_candidate"] = mobile
        if not mobile:
            info["class"] = "NOT_MOBILE"
            per[reg] = info
            continue
        # Cheap trivial-mobility attack (order s8), seed medians.
        attack = {
            "periodic_le16": med("periodic_le16") >= R["trivial_periodic_min"],
            "low_novelty": med("novel_change_frac") <= R["trivial_novelty_max"],
            "one_field": st.median(max(c["field_share"]) for c in cs) >= R["trivial_field_share_min"],
            "confined": med("top_decile_share") >= R["trivial_top_decile_min"],
        }
        info["attack"] = attack
        info["class"] = "MOBILE_BUT_TRIVIAL" if any(attack.values()) else "MOBILE_NONTRIVIAL"
        per[reg] = info
    classes = {k: v["class"] for k, v in per.items()}
    alt = {k: v for k, v in classes.items() if k != "R0"}
    if any(v == "MOBILE_NONTRIVIAL" for v in alt.values()):
        disp = "REGIME_SENSITIVE"
    elif any(v == "MOBILE_BUT_TRIVIAL" for v in alt.values()):
        disp = "MOBILE_BUT_TRIVIAL"
    elif all(v in ("NOT_MOBILE", "ENERGY_STARVED") for v in alt.values()) and alt:
        disp = "REGIME_ROBUST_FROZEN"
    else:
        disp = "UNRESOLVED"
    return {"per_regime": per, "disposition": disp}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--rules", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    units = load(a.unit_dir)
    cells = [cell_metrics(u) for u in units]
    hashes = sorted({c["regime_table_hash"] for c in cells})
    res = {"schema": "aether.er01.reduction.v1", "reducer": REDUCER_VERSION,
           "unit_dir": a.unit_dir, "units": len(cells), "regime_table_hashes": hashes,
           "cells": cells, "summary": summarize(cells), "paired_P0": paired(cells)}
    if a.rules:
        raw = open(a.rules, "rb").read()
        rules = json.loads(raw)
        res["rules_sha256"] = hashlib.sha256(raw).hexdigest()
        res["decision"] = decide(cells, res["paired_P0"], rules)
    txt = json.dumps(res, indent=1)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
    for row in res["summary"]:
        print("%-3s %-2s n=%-4d T=%-6d k=%d  late_turn %.6f [%.6f,%.6f]  frozen_strict %.4f  net64 %.4f  "
              "persist %s  t_q %s  active %.4f  starved %.4f  E %.1f  E0 %.3f  per16 %s  novel %s"
              % (row["regime"], row["pert"], row["n"], row["ticks"], row["seeds"],
                 row["late_turnover_median"], row["late_turnover_min"], row["late_turnover_max"],
                 row["frozen_strict_median"], row["frozen_net64_median"],
                 "%.3f" % row["persistence_median"] if row["persistence_median"] is not None else None,
                 row["t_quiesce_median"], row["late_active_density_median"],
                 row["late_starved_density_median"], row["final_energy_mean_median"],
                 row["final_energy_zero_frac_median"],
                 "%.3f" % row["periodic_le16_median"] if row["periodic_le16_median"] is not None else None,
                 "%.3f" % row["novel_change_frac_median"] if row["novel_change_frac_median"] is not None else None))
    for reg, pr in sorted(res["paired_P0"].items()):
        print("paired %s vs R0: ratios %s" % (reg, ["%.2f" % p["ratio"] for p in pr]))
    if "decision" in res:
        print(json.dumps(res["decision"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
