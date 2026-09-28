#!/usr/bin/env python3
"""Apply the PREREG.md decision rules to results_raw.json -> results.json."""
import json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCALES = (0.25, 0.5, 1.0, 2.0, 4.0)
H_EPS = ("0.001", "0.01", "0.1")
med = statistics.median


def label(zs, n_need):
    pos = sum(1 for z in zs if z > 0)
    neg = sum(1 for z in zs if z < 0)
    m = med(zs)
    if m >= 0.5 and pos >= n_need:
        return "positive"
    if m <= -0.5 and neg >= n_need:
        return "negative"
    return "none"


def summ(zs, n_need):
    return {"median": round(med(zs), 3), "min": round(min(zs), 3), "max": round(max(zs), 3),
            "n_pos": sum(1 for z in zs if z > 0), "n": len(zs), "label": label(zs, n_need)}


def main():
    raw = json.load(open(os.path.join(HERE, "results_raw.json")))
    fams = sorted(set(e["fam"] for e in raw["eval"]))
    E = {(e["fam"], e["a"], e["target"]): e for e in raw["eval"]}
    BX = {(b["fam"], b["a"], b["target"], b["kind"]): b for b in raw["bexp"]}
    TR = {(t["fam"], t["a"], t["kind"]): t for t in raw["train"]}
    rep = {"wall_secs": raw["wall_secs"]}
    for f in fams:
        As = sorted(set(a for (ff, a, _) in E if ff == f))
        nA = len(As)
        need_pairs = 14 if nA == 5 else round(14 * nA * 4 / 20)
        need_x = 4 if nA == 5 else nA - 1
        Btargets = ["B%d" % k for k in range(4)]
        xt = ["Xperm", "Xsk60"] if f == "MOD" else ["P10", "P30"]

        def M(a, t, m):
            return E[(f, a, t)]["res"][m]["M"]

        def SD0(a, t):
            s = statistics.pstdev(E[(f, a, t)]["res"]["noyield"]["post"])
            return s if s > 1e-9 else 1.0

        def z(a, t, m):
            return (M(a, t, "noyield") - M(a, t, m)) / SD0(a, t)

        # scale choices on A
        chosen, closest = {}, {}
        for a in As:
            for fam_m in ("MEM", "SAMEM", "BESTMEM"):
                ks = sorted(SCALES, key=lambda k: (M(a, "A", "%s_x%g" % (fam_m, k)), abs(k - 1)))
                chosen[(a, fam_m)] = "%s_x%g" % (fam_m, ks[0])
                ks2 = sorted(SCALES, key=lambda k: (abs(M(a, "A", "%s_x%g" % (fam_m, k)) - M(a, "A", "NI")), abs(k - 1)))
                closest[(a, fam_m)] = "%s_x%g" % (fam_m, ks2[0])
        # best H eps on A (median over A of M_A)
        hbest = min(H_EPS, key=lambda e: (statistics.mean(M(a, "A", "H" + e) for a in As), float(e)))
        hname = "H" + hbest

        def sysname(a, s):
            return chosen[(a, s)] if s in ("MEM", "SAMEM", "BESTMEM") else s

        systems = ["NI", "NI2", "NIslow", hname, "MEM", "SAMEM", "BESTMEM"] + (["NIblock", "NIinter"] if f == "MOD" else [])
        R = {"n_A": nA, "H_best_eps": hbest,
             "chosen_scales": {str(a): {s: chosen[(a, s)] for s in ("MEM", "SAMEM", "BESTMEM")} for a in As}}
        # per-A table on A
        onA = {}
        for a in As:
            row = {"ground_or_bestplain": E[(f, a, "A")]["ground"], "SD0": round(SD0(a, "A"), 3),
                   "M_noyield": M(a, "A", "noyield")}
            for s in systems:
                m = sysname(a, s)
                post = E[(f, a, "A")]["res"][m]["post"]
                row[s] = {"model": m, "M": round(M(a, "A", m), 3), "z": round(z(a, "A", m), 3),
                          "min": min(post), "modal_frac": E[(f, a, "A")]["res"][m].get("modal_frac")}
            tp = TR[(f, a, "PLAIN")]
            row["plain_best_of_1000"] = tp["plain_best"]
            row["plain_n_distinct_minima"] = tp["plain_n_distinct"]
            row["SA_E"] = TR[(f, a, "SA")]["sa_E"]
            row["WL_fro"] = {k: round(TR[(f, a, k)]["WL_fro"], 3) for k in ("NI", "NI2", "NIslow", hname)}
            row["H_hist_dist_rel"] = round(TR[(f, a, hname)]["hist_dist_rel"], 4)
            onA[str(a)] = row
        R["on_A"] = onA
        # T1a / T1d zero-shot on same-family B
        zero = {}
        for s in systems + ["NI"]:
            zs = [z(a, t, sysname(a, s)) for a in As for t in Btargets]
            zero[s] = summ(zs, need_pairs)
        R["T1a_T1d_zero_shot_sameB"] = zero
        # T1b warm vs scratch
        t1b = {}
        for rb in ("100", "300"):
            ds, dsc, dwm = [], [], []
            for a in As:
                for t in Btargets:
                    sc = BX[(f, a, t, "scratch")]["M"][rb]
                    wm = BX[(f, a, t, "warm")]["M"][rb]
                    ds.append((sc - wm) / SD0(a, t))
                    dsc.append((M(a, t, "noyield") - sc) / SD0(a, t))
                    dwm.append((M(a, t, "noyield") - wm) / SD0(a, t))
            t1b["R_B=" + rb] = {"warm_minus_scratch": summ(ds, need_pairs),
                                "z_scratch": summ(dsc, need_pairs), "z_warm": summ(dwm, need_pairs)}
        zs1000 = [(M(a, t, "noyield") - BX[(f, a, t, "scratch")]["M"]["1000"]) / SD0(a, t) for a in As for t in Btargets]
        t1b["z_scratch_R_B=1000"] = summ(zs1000, need_pairs)
        R["T1b_warm_vs_scratch"] = t1b
        # T1c other targets
        t1c = {}
        for t in xt:
            t1c[t] = {s: summ([z(a, t, sysname(a, s)) for a in As], need_x) for s in systems}
        R["T1c_other_targets"] = t1c
        # T2 matched endpoints
        t2 = {}
        pairs = [("NI2", None), ("NIslow", None), ("MEM", "c"), ("SAMEM", "c"), ("BESTMEM", "c")]
        for (s, c) in pairs:
            matched, hs = [], []
            for a in As:
                m = closest[(a, s)] if c else s
                dA = abs(M(a, "A", m) - M(a, "A", "NI"))
                ok = dA <= 0.25 * SD0(a, "A")
                matched.append({"a": a, "model": m, "M_A_NI": M(a, "A", "NI"), "M_A_X": M(a, "A", m),
                                "dA_SD": round(dA / SD0(a, "A"), 3), "matched": ok})
                if ok:
                    for t in Btargets:
                        hs.append((M(a, t, "NI") - M(a, t, m)) / SD0(a, t))
            ent = {"per_A": matched, "n_matched_A": sum(1 for x in matched if x["matched"])}
            if hs:
                ent["h_median_abs"] = round(med([abs(h) for h in hs]), 3)
                ent["h_median_signed(NI-X, +=X better)"] = round(med(hs), 3)
                ent["history_matters"] = med([abs(h) for h in hs]) >= 0.5
            t2["NI_vs_" + s] = ent

        def q(s1, s2):
            return abs(sum(1 if x == y else -1 for x, y in zip(s1, s2))) / len(s1)
        ov = {}
        for other in ("NI2", "NIslow"):
            ov[other] = [round(q(E[(f, a, "A")]["res"]["NI"]["modal"], E[(f, a, "A")]["res"][other]["modal"]), 3) for a in As]
        t2["modal_overlap_q_with_NI"] = ov
        R["T2"] = t2
        # T3
        zNI = med([z(a, "A", "NI") for a in As])
        t3 = {"median_z_NI_on_A": round(zNI, 3)}
        for s in ("MEM", "SAMEM", "BESTMEM", hname, "NI2", "NIslow"):
            zm = med([z(a, "A", sysname(a, s)) for a in As])
            t3["median_z_%s_on_A" % s] = round(zm, 3)
            t3["rho_%s" % s] = round(zm / zNI, 3) if zNI else None
        t3["H_hist_dist_rel"] = [onA[str(a)]["H_hist_dist_rel"] for a in As]
        t3["SA_E_vs_NI_evalmin_evalmean"] = [(onA[str(a)]["SA_E"], onA[str(a)]["NI"]["min"], onA[str(a)]["NI"]["M"]) for a in As]
        R["T3"] = t3
        # T4
        k1 = zero["NI"]["label"] == "positive"
        diffs = []
        for a in As:
            for t in Btargets:
                best_mem = max(z(a, t, chosen[(a, s)]) for s in ("MEM", "SAMEM", "BESTMEM"))
                diffs.append(z(a, t, "NI") - best_mem)
        k2 = med(diffs) >= 0.25
        R["T4"] = {"K1_zero_shot_positive": k1, "K1_stats": zero["NI"],
                   "K2_median_zNI_minus_best_mem": round(med(diffs), 3),
                   "K2_n_pairs_NI_better": sum(1 for d in diffs if d > 0),
                   "K2": k2, "verdict": "SURVIVES" if (k1 and k2) else "RETIRED"}
        rep[f] = R
    json.dump(rep, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    for f in fams:
        print(f, json.dumps(rep[f]["T4"]))


if __name__ == "__main__":
    main()
