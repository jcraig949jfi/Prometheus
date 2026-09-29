"""R4_A-001 analysis: per-arm tables, controls, held-out replication, network size."""
import collections as C
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4lib as L
import walks as Wk

DMAX = Wk.DEPTH_MAX


def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 5), round(min(1.0, c + h), 5)]


def load(arm):
    p = os.path.join(L.HERE, "runs_%s.jsonl" % arm)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def classify(r, r0, r_cur):
    """Mirror of the predicates in walks.run_walker (cheat control target)."""
    return {"improved": r > r0 + L.BAND + L.EPS, "anyup": r >= r0 + 1 / 32 - L.EPS,
            "summit": r >= Wk.SUMMIT, "neutral": abs(r - r0) <= L.BAND + L.EPS,
            "imp_vs_cur": r > r_cur + L.BAND + L.EPS}


def arm_table(runs):
    out = {"walkers": len(runs), "parents": len({r["pid"] for r in runs}),
           "stalled": sum(r["stalled"] for r in runs), "evals": sum(r["nevals"] for r in runs),
           "by_L": {}}
    for d in range(DMAX + 1):
        recs = [(r, r["depths"][d]) for r in runs if len(r["depths"]) > d]
        app = sum(x["applied"] for _, x in recs)
        prb = sum(x["probes"] for _, x in recs)
        imp = sum(x["imp"] for _, x in recs)
        up = sum(x["anyup"] for _, x in recs)
        # cumulative walk-level: any improvement at depth <= d
        wk_n = len(recs)
        wk_imp = sum(1 for r, _ in recs if any(y["imp"] for y in r["depths"][:d + 1]))
        wk_up = sum(1 for r, _ in recs if any(y["anyup"] for y in r["depths"][:d + 1]))
        par_imp = len({r["pid"] for r, _ in recs if any(y["imp"] for y in r["depths"][:d + 1])})
        out["by_L"][d + 1] = {
            "walkers_at_depth": wk_n, "probes": prb, "applied": app,
            "neutral_frac": round(sum(x["neutral"] for _, x in recs) / app, 4) if app else None,
            "lethal0_frac": round(sum(x["lethal0"] for _, x in recs) / app, 4) if app else None,
            "probe_D7": imp, "probe_D7_rate": round(imp / app, 6) if app else None, "probe_D7_wilson": wilson(imp, app),
            "probe_anyup": up, "probe_anyup_rate": round(up / app, 6) if app else None,
            "imp_vs_cur": sum(x["imp_vs_cur"] for _, x in recs),
            "summit": sum(x["summit"] for _, x in recs),
            "max_r": max((x["max_r"] or 0) for _, x in recs) if recs else None,
            "max_episode_all_correct": max(x["max_ep"] for _, x in recs) if recs else None,
            "walk_cum_D7": wk_imp, "walk_cum_D7_rate": round(wk_imp / wk_n, 4) if wk_n else None, "walk_cum_D7_wilson": wilson(wk_imp, wk_n),
            "walk_cum_anyup": wk_up, "walk_cum_anyup_wilson": wilson(wk_up, wk_n),
            "parents_with_D7_cum": par_imp,
            "lev_summit_mean": round(sum(x["lev_summit"] for _, x in recs) / wk_n, 2) if wk_n else None,
            "lev_summit_min": min(x["lev_summit"] for _, x in recs) if recs else None,
            "r_cur_mean": round(sum(x["r_cur"] for _, x in recs) / wk_n, 4) if wk_n else None,
            "genome_len_mean": round(sum(x["len"] for _, x in recs) / wk_n, 2) if wk_n else None}
        if d < DMAX:
            sp = [x.get("step_proposals") for _, x in recs if x.get("step_proposals") is not None]
            out["by_L"][d + 1]["step_proposals_mean"] = round(sum(sp) / len(sp), 3) if sp else None
    return out


def network(runs):
    per = {}
    by = C.defaultdict(list)
    for r in runs:
        by[r["pid"]].append(r)
    for pid, rs in by.items():
        visited = [x["geno"] for r in rs for x in r["depths"][1:]]
        steps = len(visited)
        ng = C.Counter(g for r in rs for x in r["depths"] for g in x["neutral_genos"])
        nph = C.Counter(p for r in rs for x in r["depths"] for p in x["neutral_phen"])
        f1 = sum(1 for v in ng.values() if v == 1)
        f2 = sum(1 for v in ng.values() if v == 2)
        s = len(ng)
        chao1 = s + (f1 * f1 / (2 * f2) if f2 else f1 * (f1 - 1) / 2)
        pf1 = sum(1 for v in nph.values() if v == 1)
        pf2 = sum(1 for v in nph.values() if v == 2)
        pchao = len(nph) + (pf1 * pf1 / (2 * pf2) if pf2 else pf1 * (pf1 - 1) / 2)
        per[pid[:12]] = {"steps": steps, "distinct_visited": len(set(visited)),
                         "neutral_probes": sum(ng.values()), "distinct_neutral_genos": s, "chao1_genos": round(chao1, 1),
                         "distinct_neutral_phenotypes": len(nph), "chao1_phenotypes": round(pchao, 1),
                         "top_phenotype_share": round(max(nph.values()) / sum(nph.values()), 3) if nph else None}
    tot_steps = sum(v["steps"] for v in per.values())
    tot_vis = sum(v["distinct_visited"] for v in per.values())
    return {"per_parent": per, "pooled_steps": tot_steps, "pooled_distinct_visited": tot_vis,
            "pooled_neutral_probes": sum(v["neutral_probes"] for v in per.values()),
            "pooled_distinct_neutral_genos": sum(v["distinct_neutral_genos"] for v in per.values()),
            "pooled_distinct_neutral_phenotypes": sum(v["distinct_neutral_phenotypes"] for v in per.values())}


def replicate(runs, parents):
    held = L.episodes("train", 2, 64)
    hexp = L.expected_vector(held)
    big = L.episodes("r4big", 1, 2000)      # amendment A2
    bexp = L.expected_vector(big)
    pr = {pid: L.score(L.answers(pm, held), hexp) for pid, pm in parents.items()}
    prb = {}
    rows = []
    for r in runs:
        for x in r["depths"]:
            for im in x["improvements"]:
                if im["child"] is None:
                    continue
                h = L.score(L.answers(im["child"], held), hexp)
                if r["pid"] not in prb:
                    prb[r["pid"]] = L.score(L.answers(parents[r["pid"]], big), bexp)
                hb = L.score(L.answers(im["child"], big), bexp)
                rows.append({"pid": r["pid"][:12], "w": r["w"], "L": x["d"] + 1, "op": im["op"], "train_r": im["r"],
                             "train_r0": r["r0"], "held_r": h, "held_r0": pr[r["pid"]],
                             "replicated": h > pr[r["pid"]] + L.BAND + L.EPS,
                             "held_summit": h >= Wk.SUMMIT, "big_r": round(hb, 4), "big_r0": round(prb[r["pid"]], 4),
                             "robust": hb > prb[r["pid"]] + L.BAND + L.EPS})
    return rows


def main():
    parents = dict(Wk.shelf_parents())
    parents["planted_2clobber"] = L.manifest_of(L.summit_genome(2))
    res = {}
    for arm in ("N", "RW", "RS", "POS", "NEG"):
        runs = load(arm)
        if not runs:
            continue
        res[arm] = {"table": arm_table(runs)}
        if arm in ("N", "RW", "POS"):
            res[arm]["network"] = network(runs)
        if arm != "NEG":
            rep = replicate(runs, parents)
            res[arm]["replication"] = {"n_improvements": len(rep), "n_replicated": sum(x["replicated"] for x in rep), "n_robust_A2": sum(x["robust"] for x in rep),
                                       "parents_replicated": sorted({x["pid"] for x in rep if x["replicated"]}),
                                       "rows": rep}
        if arm == "NEG":
            imp = sum(x["imp"] for r in runs for x in r["depths"])
            both = sum(x["imp_and_B_imp"] for r in runs for x in r["depths"])
            app = sum(x["applied"] for r in runs for x in r["depths"])
            bimp = sum(x["B_imp"] for r in runs for x in r["depths"])
            base = bimp / app if app else 0
            w = wilson(bimp, app)
            cond = both / imp if imp else None
            res[arm]["neg_control"] = {"applied": app, "S_A_improvements": imp, "S_A_rate": round(imp / app, 5) if app else None,
                                       "S_B_improvements": bimp, "S_B_rate": round(base, 5), "S_B_wilson": w,
                                       "S_A_imp_also_S_B": both, "cond_rate": cond,
                                       "cond_wilson": wilson(both, imp),
                                       "PASS": (cond is None) or (cond <= base + (w[1] - base))}
    # POS decision
    if "POS" in res:
        t = res["POS"]["table"]["by_L"]
        res["POS"]["PASS"] = t[2]["walk_cum_D7"] - t[1]["walk_cum_D7"] >= 1 and t[2]["walk_cum_D7_rate"] > t[1]["walk_cum_D7_rate"]
    # CHEAT
    c = classify(1.0, 0.53125, 0.53125)
    res["CHEAT"] = {"classified": c, "PASS": c["improved"] and c["summit"] and c["anyup"] and not c["neutral"]}
    json.dump(res, open(os.path.join(L.HERE, "analysis.json"), "w"), indent=1, sort_keys=True)
    # compact print
    for arm, v in res.items():
        if arm == "CHEAT":
            print("CHEAT", v)
            continue
        t = v["table"]
        print("==", arm, "walkers", t["walkers"], "stalled", t["stalled"], "evals", t["evals"])
        for Lk, x in t["by_L"].items():
            print(" L=%d walkers %d applied %d neutral %.3f D7 %d rate %s wil %s | walkD7 %d/%d %s | anyup %d walkUp %d | summit %d maxr %.3f maxEp %.3f | lev %.1f min %d len %.1f | steps %s"
                  % (int(Lk), x["walkers_at_depth"], x["applied"], x["neutral_frac"] or 0, x["probe_D7"], x["probe_D7_rate"], x["probe_D7_wilson"],
                     x["walk_cum_D7"], x["walkers_at_depth"], x["walk_cum_D7_wilson"], x["probe_anyup"], x["walk_cum_anyup"], x["summit"],
                     x["max_r"], x["max_episode_all_correct"], x["lev_summit_mean"], x["lev_summit_min"], x["genome_len_mean"], x.get("step_proposals_mean")))
        if "replication" in v:
            rp = v["replication"]
            print(" REPL improvements", rp["n_improvements"], "replicated", rp["n_replicated"], "robust(A2)", rp["n_robust_A2"], "parents", rp["parents_replicated"])
        if "network" in v:
            n = v["network"]
            print(" NET steps", n["pooled_steps"], "distinct visited", n["pooled_distinct_visited"], "neutral probes", n["pooled_neutral_probes"],
                  "distinct neutral genos", n["pooled_distinct_neutral_genos"], "distinct neutral phen", n["pooled_distinct_neutral_phenotypes"])
        if "neg_control" in v:
            print(" NEG", v["neg_control"])
        if "PASS" in v:
            print(" PASS", v["PASS"])


if __name__ == "__main__":
    main()
