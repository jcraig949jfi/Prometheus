"""Tyche v2 phase diagram (frozen with the preregistration).

Reads every run directory under a campaign dir (CONFIG.json has the axes)
and writes PHASE_DIAGRAM.json:

  cells[condition][class] = {runs, solved, p_solved, gens_to_solve[]}
     condition = "H|V|C|M" (V collapsed to broad / related / solo)
     solved    = a replicated admitted lens with test gain >= 50% of the
                 oracle deficit (the history tracer's definition)
  regime[condition][world] = {option_value_gens: generations after the
     switch until best val gain >= 50% of the L2 oracle deficit (None =
     not within the run), stored optionality at the switch (fraction of
     living lenses carrying any / all L2 precursors), L1 solved}
  histories: counts of assembly modes and survival reasons per class and
     harshness (from HISTORIES.json)

Usage: python -m tyche.v2.report_v2 <campaign_dir>
"""

from __future__ import annotations

import collections
import glob
import json
import os
import sys


def jl(p):
    return [json.loads(x) for x in open(p, encoding="ascii") if x.strip()] if os.path.exists(p) else []


def vgroup(v):
    return "broad" if v in ("broad", "rbroad") else "related" if v in ("rrelated",) or v.startswith("related") \
        else "solo"


POST = 30  # post-switch generations in Block R; a non-adaptation is censored at POST + 1


def block_r(regime):
    """Block R hypotheses (PREREG_BLOCK_R.md), computed mechanically.
    OV = option-value generations (censored -> POST + 1); lower is better."""
    rows = []
    for cond, ws in regime.items():
        h, v, _, _ = cond.split("|")
        for w, lst in ws.items():
            for x in lst:
                ov = x["option_value_gens"] if x["option_value_gens"] is not None else POST + 1
                rows.append({"H": h, "V": v, "world": w.split("_")[0], "ov": ov,
                             "adapted": x["option_value_gens"] is not None, "stored_any": x["stored_any"]})

    def agg(key):
        g = collections.defaultdict(list)
        for r in rows:
            g[r[key]].append(r)
        return {k: {"n": len(v), "mean_ov": round(sum(r["ov"] for r in v) / len(v), 2),
                    "adapted": sum(r["adapted"] for r in v),
                    "mean_stored_any": round(sum(r["stored_any"] or 0 for r in v) / len(v), 4)} for k, v in g.items()}
    byH, byV, byW = agg("H"), agg("V"), agg("world")
    mo = lambda d, k: d.get(k, {}).get("mean_ov")
    ms = lambda d, k: d.get(k, {}).get("mean_stored_any")
    rh = {
        "RH1_ov_RES<LEX<STRICT": None if None in (mo(byH, "RES"), mo(byH, "LEX"), mo(byH, "STRICT"))
        else bool(mo(byH, "RES") < mo(byH, "LEX") < mo(byH, "STRICT")),
        "RH2_stored_RES>LEX>STRICT": None if None in (ms(byH, "RES"), ms(byH, "LEX"), ms(byH, "STRICT"))
        else bool(ms(byH, "RES") > ms(byH, "LEX") > ms(byH, "STRICT")),
        "RH3_ov_broad<solo": None if None in (mo(byV, "broad"), mo(byV, "solo")) else bool(mo(byV, "broad") < mo(byV, "solo")),
        "RH4_ov_R3<R4": None if None in (mo(byW, "R3"), mo(byW, "R4")) else bool(mo(byW, "R3") < mo(byW, "R4")),
        "RH5_R2_adapted_cells": byW.get("R2", {}).get("adapted"),
    }
    return {"by_harshness": byH, "by_diversity": byV, "by_world": byW, "hypotheses": rh, "n_rows": len(rows)}


def main(camp):
    cells = collections.defaultdict(lambda: collections.defaultdict(lambda: {"runs": 0, "solved": 0, "gens": []}))
    regime = collections.defaultdict(dict)
    hist = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for d in sorted(glob.glob(os.path.join(camp, "*"))):
        if not os.path.exists(os.path.join(d, "DONE.json")):
            continue
        c = json.load(open(os.path.join(d, "CONFIG.json")))["args"]
        cond = f"{c['harsh']}|{vgroup(c['worlds'])}|{c['coal']}|{c['chem']}"
        worlds = {w["id"]: w for w in json.load(open(os.path.join(d, "WORLDS.json")))}
        H = {h["spec"]: h for h in (json.load(open(os.path.join(d, "HISTORIES.json")))
                                    if os.path.exists(os.path.join(d, "HISTORIES.json")) else [])}
        gens = jl(os.path.join(d, "GENERATIONS.jsonl"))
        defs = jl(os.path.join(d, "DEFICITS.jsonl"))
        admits = [x for x in jl(os.path.join(d, "ADMISSIONS.jsonl")) if x["admitted"]]
        for slot, w in worlds.items():
            if w["cls"] == "N" or w.get("kind") == "tsd":
                continue
            cell = cells[cond][w["cls"]]
            cell["runs"] += 1
            key = f"{slot}@L2" if "law2" in w else slot   # a regime cell is its L2 adaptation
            if key in H:
                cell["solved"] += 1
                ad = [x for x in admits if x["id"] == H[key]["lens"]]
                cell["gens"].append(ad[0]["epoch"] if ad else None)
            for h in [H[key]] if key in H else []:
                hist[w["cls"]][c["harsh"]][h["assembly"]] += 1
                for k, v in h["why_survived"].items():
                    hist[w["cls"]][c["harsh"]]["why:" + k] += v
            if "law2" in w and c.get("switch"):
                sw = c["switch"]
                d2 = [x for x in defs if x["slot"] == slot and x["tag"] == f"switch_gen{sw}"]
                dl2 = max([v for k, v in d2[0].items() if k.endswith("deficit") and v is not None], default=None) if d2 else None
                opv = None
                for g in gens:
                    if g["gen"] >= sw and dl2 and g["best_val_by_slot"].get(slot, 0) >= 0.5 * dl2:
                        opv = g["gen"] - sw
                        break
                opt = [x for x in jl(os.path.join(d, "OPTIONALITY.jsonl")) if x["slot"] == slot]
                regime[cond].setdefault(slot, []).append({
                    "run": os.path.basename(d), "seed": c["seed"], "option_value_gens": opv, "L2_deficit": dl2,
                    "stored_any": opt[0]["frac_any"] if opt else None, "stored_all": opt[0]["frac_all"] if opt else None,
                    "per_precursor": opt[0]["per_precursor_frac"] if opt else None,
                    "L1_solved": f"{slot}@L1" in H, "L2_solved": f"{slot}@L2" in H})
    for cond in cells:
        for cls, v in cells[cond].items():
            v["p_solved"] = round(v["solved"] / v["runs"], 3) if v["runs"] else None
    out = {"cells": cells, "regime": regime, "histories": hist, "block_r": block_r(regime)}
    json.dump(json.loads(json.dumps(out)), open(os.path.join(camp, "PHASE_DIAGRAM.json"), "w"), indent=1, sort_keys=True)
    for cond in sorted(cells):
        print(cond, {k: f"{v['solved']}/{v['runs']}" for k, v in sorted(cells[cond].items())})


if __name__ == "__main__":
    main(sys.argv[1])
