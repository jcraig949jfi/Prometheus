"""ARC3 W8 -- extra forensic tables (single core):
 (a) per-seed table (LIN/STAR/U);
 (b) families that CARRY a recurring genuine schema (>= 3 distinct bodies): share, and
     their PRISTINE p=0 / window / p=1 fractions at each escrow vs non-carriers;
 (c) G1-genuine members: window fractions;
 (d) CG-1d (LIN + duplicate-body guard) if W8_SUPPLIES_LIND.json exists (syntactic +
     genuine via the cache; unknown pairs counted non-genuine and reported).
Writes W8_EXTRA.json."""
import json
import random
import statistics as st
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w8_lin as W  # noqa: E402
import w8_analyse as A  # noqa: E402

ESC = (30000, 100000, 250000, 1000000)


def cls(ch, E):
    p = sum(c <= E for c in ch) / 4
    return "p1" if p == 1 else ("p0" if p == 0 else "win")


def main():
    W.init()
    sup = json.loads((HERE / "W8_SUPPLIES.json").read_text())
    gc = json.loads((HERE / "W8_GENUINE_CACHE.json").read_text())
    cov = json.loads((HERE / "W8_COVER.json").read_text())
    res = json.loads((HERE / "W8_RESULTS.json").read_text())
    g1idx = W.comp_index(W.a18.G1, gc, True)
    table, carr = [], {}
    for tag, r in res["per_seed"].items():
        table.append([tag, r["syntactic"]["dup"], r["syntactic"]["R3u"], r["syntactic"]["P_reuse"],
                      r["syntactic"]["n_recurring"], r["genuine"]["R3u"], r["genuine"]["P_reuse"],
                      r["genuine"]["n_recurring"], r["X_nontrivial"]["G1"]["COND"], r["X_genuine"]["G1"]["COND"],
                      r["X_genuine"]["G1"]["share"], r["covered"], r["window"]["30000"]["window"],
                      r["window"]["250000"]["window"]])
        kind = r["kind"]
        fams = sup[tag]["families"]
        dec = [W.schemas(f[2]) for f in fams]
        schg = [{k for k, v in d.items() if v and gc.get("%s||%s" % tuple(v))} for d in dec]
        first = {}
        for f, ss in zip(fams, schg):
            first.setdefault(f[2], ss)
        ucnt = Counter(s for b in first for s in first[b])
        c = carr.setdefault(kind, {"carrier": Counter(), "non": Counter(), "g1": Counter(), "n": Counter()})
        for f, ss in zip(fams, schg):
            grp = "carrier" if any(ucnt[s] >= 3 for s in ss) else "non"
            c["n"][grp] += 1
            for E in ESC:
                c[grp]["%d_%s" % (E, cls(cov[f[0]]["charges"], E))] += 1
            if f[2] in g1idx:
                c["n"]["g1"] += 1
                for E in ESC:
                    c["g1"]["%d_%s" % (E, cls(cov[f[0]]["charges"], E))] += 1
    out = {"per_seed_table_cols": ["tag", "dup", "R3u", "P_reuse", "n_rec", "R3u_gen", "P_reuse_gen", "n_rec_gen",
                                   "XG1_nt", "XG1_gen", "G1share_gen", "covered", "win30k", "win250k"],
           "per_seed_table": table, "carriers": {}}
    for kind, c in carr.items():
        o = {"n": dict(c["n"])}
        for grp in ("carrier", "non", "g1"):
            n = c["n"][grp]
            o[grp] = {k: round(v / n, 3) for k, v in sorted(c[grp].items())} if n else None
        out["carriers"][kind] = o
    lp = HERE / "W8_SUPPLIES_LIND.json"
    if lp.exists():
        lind = json.loads(lp.read_text())
        rows, recs, unknown, total = {}, [], 0, 0
        for tag, r in lind.items():
            bodies = [f[2] for f in r["families"]]
            dec = [W.schemas(b) for b in bodies]
            for d in dec:
                for v in d.values():
                    if v:
                        total += 1
                        unknown += ("%s||%s" % tuple(v)) not in gc
            sch = [set(d) for d in dec]
            schg = [{k for k, v in d.items() if v and gc.get("%s||%s" % tuple(v))} for d in dec]
            rng = random.Random("ARC3/W8/MEASURE/" + tag)
            s1, rec = A.syn_stats(bodies, sch, rng)
            s2, _ = A.syn_stats(bodies, schg, rng)
            recs.append(rec)
            xg = W.xs(bodies, g1idx)
            rows[tag] = {"stats": r["stats"], "syntactic": s1, "genuine": s2, "XG1_gen": xg}
        seeds = sorted(int(t.split(":")[1]) for t in rows)
        star = res["per_seed"]
        ratio = [rows["LIND:%d" % s]["syntactic"]["P_reuse"] >= 5 * star["STAR:%d" % s]["syntactic"]["P_reuse"]
                 for s in seeds]
        out["LIND"] = {"per_seed": rows, "n": len(rows),
                       "dup_mean": round(st.mean(r["syntactic"]["dup"] for r in rows.values()), 4),
                       "R3u_mean": round(st.mean(r["syntactic"]["R3u"] for r in rows.values()), 4),
                       "P_reuse_mean": round(st.mean(r["syntactic"]["P_reuse"] for r in rows.values()), 4),
                       "P_reuse_gen_mean": round(st.mean(r["genuine"]["P_reuse"] for r in rows.values()), 4),
                       "frac_Preuse_ge_5x_STAR_same_seed": round(sum(ratio) / len(ratio), 3),
                       "jaccard": A.jac and round(st.mean([A.jac(recs[i], recs[j]) for i in range(len(recs))
                                                          for j in range(i + 1, len(recs))]), 4),
                       "XG1_gen_frac_ge_.10": round(sum(r["XG1_gen"]["COND"] >= .10 for r in rows.values()) / len(rows), 3),
                       "XG1_gen_frac_le_.02": round(sum(r["XG1_gen"]["COND"] <= .02 for r in rows.values()) / len(rows), 3),
                       "genuine_pairs_unknown_frac": round(unknown / max(1, total), 3)}
    (HERE / "W8_EXTRA.json").write_text(json.dumps(out, indent=1))
    for t in table:
        print(" ".join(str(x) for x in t))
    print(json.dumps(out["carriers"], indent=1))
    if "LIND" in out:
        print(json.dumps({k: v for k, v in out["LIND"].items() if k != "per_seed"}, indent=1))


if __name__ == "__main__":
    main()
