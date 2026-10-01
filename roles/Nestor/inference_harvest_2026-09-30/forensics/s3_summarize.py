"""s3 step 4: rates, ruler, kill rules, lethal-pair locations. python -B s3_summarize.py -> s3_summary.json (+ stdout)

Implementation conventions (fixed before reading results, consistent with the frozen rules):
  * pooled rate = lethal pairs / pairs over all genomes in the group; pooled null = mean null over the same pairs.
  * per-genome excess = rate / null; null == 0 with rate > 0 -> +inf (counts as >= 3x); rate == 0 -> 0;
    a genome with < 2 dispensable positions (no pairs) has no excess and counts as NOT >= 3x in the T3 rule
    (denominator = all 48 panel genomes); the rule is also shown with such genomes dropped.
  * cluster sensitivity: the 8 epoch-700 16000006 genomes collapsed to one (their pairs pooled).
"""
import collections
import json
import math

d = json.load(open("s3_pairs.json"))
ctrl = json.load(open("s3_controls.json"))


def pooled(rs):
    n = sum(r["n_pairs"] for r in rs)
    l = sum(r["n_lethal"] for r in rs)
    raw = sum(r["n_lethal_raw"] for r in rs)
    nu = sum(x[4] for r in rs for x in r["pairs"])
    return {"genomes": len(rs), "pairs": n, "lethal_raw": raw, "lethal": l, "rate": l / n if n else None,
            "null": nu / n if n else None, "excess": (l / nu) if nu else (math.inf if l else None),
            "genomes_with_lethal": sum(r["n_lethal"] > 0 for r in rs)}


P, C = d["panel"], d["comparators"]
sfp, sdp = pooled(P), pooled(C)
ge3 = sum(1 for r in P if r["excess"] is not None and r["excess"] >= 3)
haspairs = [r for r in P if r["n_pairs"]]
ge3b = sum(1 for r in haspairs if r["excess"] >= 3)
ratio_sf_sd = (sfp["rate"] / sdp["rate"]) if sdp["rate"] else (math.inf if sfp["rate"] else None)
t4_dead = (sfp["excess"] is not None and sfp["excess"] <= 1.5) and (ratio_sf_sd is not None and ratio_sf_sd <= 1.2)
t3_dead = ge3 >= 0.5 * len(P)
pos_ok = ctrl["positive_PASS"]
neg_ok = ctrl["negative_pooled"]["PASS"]
if not pos_ok:
    verdict = "INSTRUMENT_UNREACHABLE"
elif t4_dead and t3_dead:
    verdict = "CONTRADICTION (both rules fired)"
elif t4_dead:
    verdict = "T4(c) DEAD"
elif t3_dead:
    verdict = "T3 NO-ORGANIZATION READING DEAD"
else:
    verdict = "INCONCLUSIVE"
# cluster sensitivity
e700 = [r for r in P if r["src"] == "16000006_e700"]
rest = [r for r in P if r["src"] != "16000006_e700"]
clus = pooled(rest + [{"n_pairs": sum(r["n_pairs"] for r in e700), "n_lethal": sum(r["n_lethal"] for r in e700),
                       "n_lethal_raw": sum(r["n_lethal_raw"] for r in e700), "pairs": [x for r in e700 for x in r["pairs"]]}]) if e700 else None
# where lethal pairs sit
def loc(rs):
    cls_all, cls_leth, pair_cls, dist_all, dist_leth, ops = (collections.Counter() for _ in range(6))
    lst = []
    for r in rs:
        a = r["ann"]
        for i, j, l, c, nu in r["pairs"]:
            ci, cj = a[str(i)]["cls"], a[str(j)]["cls"]
            cls_all[ci] += 1; cls_all[cj] += 1
            dd = min(j - i, 64 - (j - i))
            dist_all["adjacent(1)" if dd == 1 else "2-3" if dd <= 3 else ">=4"] += 1
            if l and c:
                cls_leth[ci] += 1; cls_leth[cj] += 1
                pair_cls[" + ".join(sorted((ci, cj)))] += 1
                dist_leth["adjacent(1)" if dd == 1 else "2-3" if dd <= 3 else ">=4"] += 1
                for p in (i, j):
                    x = a[str(p)]
                    ops["%s %s%s" % (x["cls"], x["instr"] or "--", "" if x["is_opcode"] is None else (" op" if x["is_opcode"] else " arg"))] += 1
                lst.append({"genome": r["idx"], "run": r["origin_run"][-8:], "i": i, "j": j, "ann_i": a[str(i)], "ann_j": a[str(j)], "null": round(nu, 4)})
    return {"position_class_all": dict(cls_all), "position_class_lethal": dict(cls_leth), "pair_class_lethal": dict(pair_cls.most_common()),
            "distance_all": dict(dist_all), "distance_lethal": dict(dist_leth), "instr_lethal": dict(ops.most_common(30)), "list": lst}


per = lambda rs: [{"idx": r["idx"], "run": r["origin_run"].split("/")[-1], "cell": r["cell"], "src": r["src"], "n_disp": r["n_disp"],
                   "n_pairs": r["n_pairs"], "lethal_raw": r["n_lethal_raw"], "lethal": r["n_lethal"],
                   "rate": r["rate"], "null": r["null"], "excess": r["excess"]} for r in rs]
summ = {"npairs": d["npairs"], "pooled_SF": sfp, "pooled_SD": sdp, "SF_over_SD_rate": ratio_sf_sd,
        "T3_rule": {"ge3_count": ge3, "of": len(P), "ge3_count_excluding_no_pair_genomes": ge3b, "of_with_pairs": len(haspairs)},
        "T4_dead": t4_dead, "T3_dead": t3_dead, "positive_control_PASS": pos_ok, "negative_control_PASS": neg_ok,
        "verdict": verdict, "cluster_collapsed_SF": clus, "per_genome_SF": per(P), "per_genome_SD": per(C),
        "loc_SF": loc(P), "loc_SD": loc(C), "cpu_pairs_s": d.get("cpu_s")}
json.dump(summ, open("s3_summary.json", "w"), indent=1, default=str)
for k in ("pooled_SF", "pooled_SD", "SF_over_SD_rate", "T3_rule", "T4_dead", "T3_dead", "verdict", "cluster_collapsed_SF"):
    print(k, summ[k])
for g in ("loc_SF", "loc_SD"):
    print(g, {k: v for k, v in summ[g].items() if k != "list"})
