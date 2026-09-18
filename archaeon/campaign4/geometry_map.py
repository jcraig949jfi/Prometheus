"""Campaign 4 -- the DAMAGE GEOMETRY MAP (directive section 6), assembled from the committed
attempt-of-record tables of every slot. Pure reader: no evaluation, no rows.

    python -m archaeon.campaign4.geometry_map [--out archaeon/campaign4/DAMAGE_GEOMETRY_MAP]

Columns per condition (rows): mutation magnitude -> P(fatal loss) [D1: eligible 0 on this
substrate, D4-002] -> P(degeneracy, D2) -> P(neutrality, D5) -> P(coherent behavioural
displacement: D3/D4/D6/D7 or D5 with displacement > 0) -> P(viability: reward >= 3/16 after the
edit, = 1 - D2 - D3 - D0) -> P(exaptation, D6) -> eventual descendant consequence (from the
lineage slots, stated in words with its number). Every number carries its source path.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C4 = REPO / "archaeon" / "campaign4"
D = ("D0", "D2", "D3", "D4", "D5", "D6", "D7")


def load(rel: str):
    p = C4 / rel
    if not p.exists():
        return None
    if rel.endswith(".gz"):
        return json.load(gzip.open(p, "rt", encoding="utf-8"))
    return json.loads(p.read_text(encoding="utf-8"))


def rates(g: dict) -> dict:
    r = g["rates"]
    p = {d: (r[d]["p"] or 0.0) for d in D}
    return {"fatal": 0.0, "degenerate": p["D2"], "neutral": p["D5"], "distinct_nonviable": p["D3"], "viable_worse": p["D4"],
            "exaptive": p["D6"], "improved": p["D7"], "viable": round(1 - p["D0"] - p["D2"] - p["D3"], 4), "n": g["applied"], "displacement_mean": g.get("displacement_mean")}


def coherent_from_rows(rows: list, key) -> dict:
    out = {}
    for r in rows:
        if not r.get("applied"):
            continue
        k = key(r)
        g = out.setdefault(k, [0, 0])
        g[1] += 1
        if r["D"] in ("D3", "D4", "D6", "D7") or (r["D"] == "D5" and (r.get("displacement") or 0) > 0):
            g[0] += 1
    return {k: round(v[0] / v[1], 4) if v[1] else None for k, v in out.items()}


def build() -> dict:
    m = {"schema": "archaeon.c4.damage_geometry_map.v1", "substrate": {}, "rows": [], "descendant_consequences": [], "sources": []}
    c401 = load("C4-01/attempts/a02/FLOW_TABLES.json")
    c401_rows = load("C4-01/attempts/a02/children.json.gz")
    if c401:
        m["sources"].append("C4-01/attempts/a02/FLOW_TABLES.json")
        coh_op = coherent_from_rows(c401_rows, lambda r: r["operator"]) if c401_rows else {}
        coh_st = coherent_from_rows(c401_rows, lambda r: r["stratum"]) if c401_rows else {}
        for op, g in c401["by_operator"].items():
            if op.startswith("control"):
                continue
            m["rows"].append({"condition": "frozen substrate, single edit", "magnitude": 1, "operator": op, **rates(g), "coherent": coh_op.get(op), "source": "C4-01"})
        for st, g in c401["by_stratum"].items():
            m["rows"].append({"condition": "single edit, stratum", "magnitude": 1, "stratum": st, **rates(g), "coherent": coh_st.get(st), "source": "C4-01"})
        m["substrate"]["d1_eligible"] = 0
        m["substrate"]["pairwise_tvd_min_max"] = [c401["min_pairwise_tvd"], c401["max_pairwise_tvd"]]
    c402 = load("C4-02/attempts/a01/CURVES.json")
    c402_rows = load("C4-02/attempts/a01/children.json.gz")
    if c402:
        m["sources"].append("C4-02/attempts/a01/CURVES.json")
        coh = coherent_from_rows(c402_rows, lambda r: r["arm"]) if c402_rows else {}
        for arm, g in sorted(c402["by_radius"].items(), key=lambda kv: int(kv[0][1:])):
            if arm == "r0":
                continue
            m["rows"].append({"condition": "frozen substrate, radius %s" % arm[1:], "magnitude": int(arm[1:]), **rates(g), "coherent": coh.get(arm), "source": "C4-02"})
        m["substrate"]["traversable_region_by_stratum"] = c402["shapes"]["traversable_region_by_stratum"]
    c408 = load("C4-08/attempts/a01/ROBUSTNESS_TABLES.json")
    if c408:
        m["sources"].append("C4-08/attempts/a01/ROBUSTNESS_TABLES.json")
        for arm, t in c408["tables"].items():
            n = t["edits_applied"]
            m["rows"].append({"condition": "single edit of %s population on W2_K2" % arm, "magnitude": 1, "population": arm,
                              "fatal": 0.0, "degenerate": None, "neutral": t["neutral"]["p"], "loss_D2_D3": t["loss"]["p"], "viable": round(1 - t["loss"]["p"], 4),
                              "coherent": t["coherent"]["p"], "improved": round(t["improved"]["k"] / n, 4) if n else None, "mean_len": t["mean_len"], "n": n, "source": "C4-08"})
    c405 = load("C4-05/attempts/a01/WALK_TABLES.json")
    if c405:
        m["sources"].append("C4-05/attempts/a01/WALK_TABLES.json")
        v = c405["aggregate"]["viable"]
        m["descendant_consequences"].append({"from": "C4-05 neutral walk", "connected_depth_median": v["connected_depth_median"],
                                             "acceptance_by_bin": {k: x["rate"] for k, x in v["acceptance_by_bin"].items()},
                                             "held_out_exaptation_by_depth": {str(d): e["rate"] for d, e in v["exposure_by_depth"].items()},
                                             "structural_diversity_by_depth": {str(d): e["structural_diversity"] for d, e in v["exposure_by_depth"].items()},
                                             "reading": "the neutral band is fully connected to depth 16; held-out exaptation grows .016 -> .043 (single edit .006); below the .05 bars"})
    c406 = load("C4-06/attempts/a01/SUMMARY.json")
    if c406:
        m["sources"].append("C4-06/attempts/a01/SUMMARY.json")
        m["descendant_consequences"].append({"from": "C4-06 recombination vs mutation-only", "crossings": {a: c406[a]["crossings"] for a in ("mutation_only", "recombination")},
                                             "births_viable_share": {a: {k: b["viable_share"] for k, b in c406[a]["births"].items()} for a in ("mutation_only", "recombination")},
                                             "reading": "no W2_K2 summit in either arm at G=100 from 188 drifted lineages; mate-splice births 8 points less viable"})
    if c408:
        m["descendant_consequences"].append({"from": "C4-08 selected descendants", "loss_by_population": {a: t["loss"]["p"] for a, t in c408["tables"].items()},
                                             "coherent_by_population": {a: t["coherent"]["p"] for a, t in c408["tables"].items()},
                                             "mean_len_by_population": {a: t["mean_len"] for a, t in c408["tables"].items()},
                                             "reading": "selection halves single-edit loss (.42 -> .19 -> .13) by building neutrality (coherent .15 -> .04) and length (19 -> 62); no structure to ablate"})
    c409 = load("C4-09/attempts/a01/ECOLOGY.json")
    if c409:
        m["sources"].append("C4-09/attempts/a01/ECOLOGY.json")
        m["descendant_consequences"].append({"from": "C4-09 lateral ecology", "rescues": c409["rescues"], "rescue_survival": c409["rescue_survival"],
                                             "per_world_improved_seeds": c409["per_world_improved_seeds"], "extra_compute_ratio": c409["extra_compute_ratio"],
                                             "predictions": c409["predictions"], "overhead_shape": c409["overhead_shape"]})
    c410 = load("C4-10/attempts/a01/TRIAL.json")
    if c410:
        m["sources"].append("C4-10/attempts/a01/TRIAL.json")
        for cond, t in c410["tables"].items():
            m["rows"].append({"condition": "held-out family, %s (per birth)" % cond, "magnitude": "birth", "fatal": 0.0, "loss_below_floor": t["fatal_mass"]["p"],
                              "viable": round(1 - (t["fatal_mass"]["p"] or 0), 4), "nontrivial_yield": t["nontrivial_yield"]["p"], "behavioural_diversity": t["behavioural_diversity_mean"],
                              "lineage_depth": t["lineage_depth_mean"], "novel_capability_cells": "%d/%d" % (t["novel_capability_cells"], t["cells"]), "n": t["births"], "source": "C4-10"})
        m["campaign_disposition"] = c410["campaign_disposition"]
        m["c410_selection"] = c410["selection"]["selected"]
        m["c410_claims"] = c410["claims"]
    return m


def render(m: dict) -> str:
    L = ["+" + "=" * 69 + "+", "|  CAMPAIGN 4 -- DAMAGE GEOMETRY MAP (directive section 6)            |", "+" + "=" * 69 + "+", "",
         "Every rate is an applied-edit (or birth) share with its source slot; D1",
         "(execution fault) is 0 by construction on this substrate (D4-002), so the",
         "'fatal loss' column is 0 everywhere and the loss lives in D2 + D3.", "",
         "%-46s %5s %6s %6s %6s %6s %6s %6s %6s" % ("condition", "mag", "fatal", "degen", "neutr", "coher", "viable", "exapt", "n"), "-" * 100]
    for r in m["rows"]:
        name = r["condition"] + (" / " + r["operator"] if r.get("operator") else "") + (" / " + r["stratum"] if r.get("stratum") else "")
        def f(x):
            return "%.3f" % x if isinstance(x, (int, float)) and x is not None else ("  -  " if x is None else str(x))
        L.append("%-46s %5s %6s %6s %6s %6s %6s %6s %6s" % (name[:46], str(r.get("magnitude")), f(r.get("fatal")), f(r.get("degenerate")), f(r.get("neutral")),
                                                             f(r.get("coherent")), f(r.get("viable")), f(r.get("exaptive")), str(r.get("n"))))
    L += ["", "EVENTUAL DESCENDANT CONSEQUENCE (lineage slots)", "-" * 60]
    for d in m["descendant_consequences"]:
        L.append("  %s" % d["from"])
        for k, v in d.items():
            if k in ("from",):
                continue
            L.append("    %-32s %s" % (k, json.dumps(v)[:120]))
    L += ["", "SUBSTRATE FACTS: %s" % json.dumps(m["substrate"])]
    if "campaign_disposition" in m:
        L += ["", "CAMPAIGN DISPOSITION (C4-10): %s   selected: %s" % (m["campaign_disposition"], m.get("c410_selection")), "claims: %s" % json.dumps(m.get("c410_claims"))]
    L += ["", "sources: " + ", ".join(m["sources"]), ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="archaeon/campaign4/DAMAGE_GEOMETRY_MAP")
    a = ap.parse_args(argv)
    m = build()
    base = REPO / a.out
    base.with_suffix(".json").write_text(json.dumps(m, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    txt = render(m)
    base.with_suffix(".md").write_text(txt, encoding="utf-8", newline="\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
