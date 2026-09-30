"""ARC3 W8 -- per-seed statistics and W1 "natural recurrence exists" criteria.
Reads W8_SUPPLIES.json, W8_GENUINE_CACHE.json, W8_PANEL.json, W8_COVER.json.
Writes W8_RESULTS.json. Single core. FORENSIC, NOT A DISPOSITION."""
import json
import math
import random
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w8_lin as W  # noqa: E402

ESCROWS = (30000, 100000, 250000, 1000000)
N_REP = 2000
N_PANEL = 4


def syn_stats(bodies, sch, rng):
    """W1 statistics on a list of per-family schema-key sets."""
    N = len(bodies)
    ub = sorted(set(bodies))
    first = {}
    for b, ss in zip(bodies, sch):
        first.setdefault(b, ss)
    ucnt = Counter(s for b in ub for s in first[b])
    r3u = sum(any(ucnt[s] >= 3 for s in first[b]) for b in ub) / max(1, len(ub))
    hit = 0
    for _ in range(N_REP):
        pick = rng.sample(range(N), 12)
        vs = set().union(*[sch[i] for i in pick[:4]])
        tc = Counter(s for i in pick[4:] for s in sch[i])
        hit += any(tc[s] >= 2 for s in vs)
    rec = {s for s, c in ucnt.items() if c >= 3}
    return {"dup": round(1 - len(ub) / N, 4), "R3u": round(r3u, 4), "P_reuse": round(hit / N_REP, 4),
            "n_recurring": len(rec)}, rec


def jac(a, b):
    return len(a & b) / len(a | b) if (a | b) else float("nan")


def main():
    W.init()
    sup = json.loads((HERE / "W8_SUPPLIES.json").read_text())
    gc = json.loads((HERE / "W8_GENUINE_CACHE.json").read_text())
    pan = json.loads((HERE / "W8_PANEL.json").read_text())
    cov = json.loads((HERE / "W8_COVER.json").read_text())
    G1 = W.a18.G1
    # frequency-matched panel: matched candidates; if fewer than N_PANEL, nearest by
    # |log share ratio| + |log COND ratio| (declared)
    cands = [c for c in pan["candidates"] if c["U_genuine"]["share"] > 0 and c["U_genuine"]["COND"] > 0]
    cands.sort(key=lambda c: (not c["matched"], abs(math.log(c["ratio_share"])) + abs(math.log(c["ratio_COND"]))))
    uniq, seen = [], set()
    for c in cands:                      # dedupe commutative / identical-instance duplicates
        k = frozenset(W.T3D.instantiate(c["schema"]))
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    panel = {"P%s" % "ABCD"[i]: c for i, c in enumerate(uniq[:N_PANEL])}
    idx_gen = {"G1": W.comp_index(G1, gc, True)}
    idx_nt = {"G1": W.comp_index(G1, gc, False)}
    for k, c in panel.items():
        idx_gen[k] = W.comp_index(c["schema"], gc, True)
        idx_nt[k] = W.comp_index(c["schema"], gc, False)
    ub = [f[2] for t, r in sup.items() if t.startswith("U:") for f in r["families"]]
    g1m = {b for b in ub if b in idx_gen["G1"]}
    for k in panel:
        pm = {b for b in ub if b in idx_gen[k]}
        panel[k]["U_member_jaccard_with_G1"] = round(len(g1m & pm) / len(g1m | pm), 3) if (g1m | pm) else None
    rows, recs, recs_g = {}, defaultdict(list), defaultdict(list)
    for tag in sorted(sup, key=lambda t: (t.split(":")[0], int(t.split(":")[1]))):
        kind = tag.split(":")[0]
        fams = sup[tag]["families"]
        bodies = [f[2] for f in fams]
        dec = [W.schemas(b) for b in bodies]
        sch = [set(d) for d in dec]
        schg = [{k for k, v in d.items() if v and gc.get("%s||%s" % tuple(v))} for d in dec]
        rng = random.Random("ARC3/W8/MEASURE/" + tag)
        s1, rec = syn_stats(bodies, sch, rng)
        s2, recg = syn_stats(bodies, schg, rng)
        recs[kind].append(rec)
        recs_g[kind].append(recg)
        xg = {k: W.xs(bodies, v) for k, v in idx_gen.items()}
        xn = {k: W.xs(bodies, v) for k, v in idx_nt.items()}
        # PRISTINE equivalence-reachability window (W2 logic, 4 A19 pilot seeds per family)
        win = {}
        for E in ESCROWS:
            ps = [sum(c <= E for c in cov[f[0]]["charges"]) / 4 for f in fams]
            win[E] = {"window": round(sum(0 < p < 1 for p in ps) / len(ps), 4),
                      "p1": round(sum(p == 1 for p in ps) / len(ps), 4),
                      "p0": round(sum(p == 0 for p in ps) / len(ps), 4)}
        g1mem = [f for f in fams if f[2] in idx_gen["G1"]]
        g1win = {E: (round(sum(0 < sum(c <= E for c in cov[f[0]]["charges"]) < 4 for f in g1mem) / len(g1mem), 3)
                     if g1mem else None) for E in (30000, 250000)}
        cg = Counter(k for ss in schg for k in ss)
        rows[tag] = {"kind": kind, "stats": sup[tag]["stats"], "syntactic": s1, "genuine": s2,
                     "X_genuine": xg, "X_nontrivial": xn,
                     "covered": round(sum(cov[f[0]]["covered"] for f in fams) / len(fams), 4),
                     "window": win, "G1_member_window": g1win,
                     "top_genuine_schemas": cg.most_common(3)}
        print(tag, s1, s2, "XG1g", xg["G1"], "XG1nt", xn["G1"], "cov", rows[tag]["covered"],
              "win30k", win[30000]["window"], "win250k", win[250000]["window"], flush=True)

    def js(ss):
        v = [jac(ss[i], ss[j]) for i in range(len(ss)) for j in range(i + 1, len(ss))]
        v = [x for x in v if not math.isnan(x)]
        return round(st.mean(v), 4) if v else None

    agg = {}
    for kind in ("LIN", "STAR", "U"):
        R = [r for r in rows.values() if r["kind"] == kind]
        if not R:
            continue

        def m(f):
            v = [f(r) for r in R]
            return {"mean": round(st.mean(v), 4), "median": round(st.median(v), 4),
                    "min": round(min(v), 4), "max": round(max(v), 4)}
        a = {"n_seeds": len(R),
             "admit_per_proposal": m(lambda r: r["stats"]["admitted"] / r["stats"]["proposals"]),
             "jaccard_syntactic": js(recs[kind]), "jaccard_genuine": js(recs_g[kind]),
             "covered": m(lambda r: r["covered"])}
        for fam in ("syntactic", "genuine"):
            for k in ("dup", "R3u", "P_reuse", "n_recurring"):
                a["%s_%s" % (fam, k)] = m(lambda r, fam=fam, k=k: r[fam][k])
        for xk in ("X_genuine", "X_nontrivial"):
            for S in idx_gen:
                a["%s_%s_COND" % (xk, S)] = m(lambda r, xk=xk, S=S: r[xk][S]["COND"])
                a["%s_%s_share" % (xk, S)] = m(lambda r, xk=xk, S=S: r[xk][S]["share"])
            a["%s_G1_frac_ge_.10" % xk] = round(sum(r[xk]["G1"]["COND"] >= .10 for r in R) / len(R), 4)
            a["%s_G1_frac_le_.02" % xk] = round(sum(r[xk]["G1"]["COND"] <= .02 for r in R) / len(R), 4)
        for E in ESCROWS:
            for k in ("window", "p1", "p0"):
                a["%s_%d" % (k, E)] = m(lambda r, E=E, k=k: r["window"][E][k])
        agg[kind] = a

    def crit(fam, xk):
        pairs = [(rows["LIN:%d" % s], rows["STAR:%d" % s]) for s in range(100)
                 if "LIN:%d" % s in rows and "STAR:%d" % s in rows]
        ratio_ok = [l[fam]["P_reuse"] > 0 and l[fam]["P_reuse"] >= 5 * s_[fam]["P_reuse"] for l, s_ in pairs]
        c = {"C1_frac_seeds_LIN_Preuse_ge_5x_STAR": round(sum(ratio_ok) / len(pairs), 4),
             "C1_pass(>=.80)": sum(ratio_ok) / len(pairs) >= .80,
             "C2_LIN_jaccard": agg["LIN"]["jaccard_%s" % fam], "C2_pass(<=.10)": (agg["LIN"]["jaccard_%s" % fam] or 0) <= .10,
             "C3_LIN_dup_mean": agg["LIN"]["%s_dup" % fam]["mean"],
             "C3_frac_seeds_dup_le_.35": round(sum(r[fam]["dup"] <= .35 for r, _ in pairs) / len(pairs), 4),
             "C3_pass(mean<=.35)": agg["LIN"]["%s_dup" % fam]["mean"] <= .35,
             "C4_frac_XG1_ge_.10": agg["LIN"]["%s_G1_frac_ge_.10" % xk],
             "C4_frac_XG1_le_.02": agg["LIN"]["%s_G1_frac_le_.02" % xk],
             "C4_pass": agg["LIN"]["%s_G1_frac_ge_.10" % xk] >= .25 and agg["LIN"]["%s_G1_frac_le_.02" % xk] >= .25,
             "paired_Preuse_ratio_median": round(st.median([l[fam]["P_reuse"] / s_[fam]["P_reuse"] if s_[fam]["P_reuse"] else float("inf") for l, s_ in pairs]), 3)}
        c["ALL_PASS"] = c["C1_pass(>=.80)"] and c["C2_pass(<=.10)"] and c["C3_pass(mean<=.35)"] and c["C4_pass"]
        return c

    crits = {"W1_syntactic+X_nontrivial": crit("syntactic", "X_nontrivial"),
             "genuine+X_genuine": crit("genuine", "X_genuine")}
    out = {"panel": {k: {"schema": c["schema"], "U_genuine": c["U_genuine"], "ratio_share": c["ratio_share"],
                         "ratio_COND": c["ratio_COND"], "matched": c["matched"],
                         "U_member_jaccard_with_G1": c.get("U_member_jaccard_with_G1")} for k, c in panel.items()},
           "G1_U_genuine": pan["G1_U_genuine"], "per_seed": rows, "per_generator": agg, "criteria": crits}
    (HERE / "W8_RESULTS.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({"criteria": crits, "panel": out["panel"]}, indent=1, default=str))
    for k, a in agg.items():
        print(k, json.dumps(a, default=str))


if __name__ == "__main__":
    main()
