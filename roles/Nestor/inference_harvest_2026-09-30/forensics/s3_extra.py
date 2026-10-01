"""s3 step 5 (post hoc, descriptive; does not alter the frozen verdict): null strata, raw-call ruler, genome
bootstrap CIs, per-genome excess distribution, class enrichment. python -B s3_extra.py -> s3_extra.json"""
import collections, json, random, statistics as st
d = json.load(open("s3_pairs.json")); sg = json.load(open("s3_singles.json"))
P = {g["idx"]: g for g in sg["panel"]}; C = {g["idx"]: g for g in sg["comparators"]}
out = {}
for grp, ref in (("panel", P), ("comparators", C)):
    strata = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for r in d[grp]:
        p = ref[r["idx"]]["p"]
        for i, j, l, c, nu in r["pairs"]:
            k = "%d/3+%d/3" % tuple(sorted((round(3 * p[str(i)]), round(3 * p[str(j)]))))
            s = strata[k]; s[0] += 1; s[1] += bool(l); s[2] += bool(l and c); s[3] += nu
    out[grp + "_strata"] = {k: {"pairs": v[0], "lethal_raw": v[1], "lethal": v[2], "rate": round(v[2] / v[0], 4),
                                "null": round(v[3] / v[0], 4)} for k, v in sorted(strata.items())}
    rs = d[grp]
    n = sum(r["n_pairs"] for r in rs); nu = sum(x[4] for r in rs for x in r["pairs"])
    out[grp + "_raw_excess"] = round(sum(r["n_lethal_raw"] for r in rs) / nu, 4)
    ex = [r["excess"] for r in rs if r["excess"] is not None]
    out[grp + "_excess_quantiles"] = {"min": round(min(ex), 3), "median": round(st.median(ex), 3), "max": round(max(ex), 3),
                                      "n_ge1": sum(e >= 1 for e in ex), "n_ge1.5": sum(e >= 1.5 for e in ex), "n": len(ex)}
rng = random.Random(1)
bs_ex, bs_ratio = [], []
for _ in range(2000):
    a = [rng.choice(d["panel"]) for _ in d["panel"]]; b = [rng.choice(d["comparators"]) for _ in d["comparators"]]
    la = sum(r["n_lethal"] for r in a); na = sum(r["n_pairs"] for r in a); ua = sum(x[4] for r in a for x in r["pairs"])
    lb = sum(r["n_lethal"] for r in b); nb = sum(r["n_pairs"] for r in b)
    bs_ex.append(la / ua); bs_ratio.append((la / na) / (lb / nb))
q = lambda v: [round(sorted(v)[int(0.025 * len(v))], 3), round(sorted(v)[int(0.975 * len(v))], 3)]
out["bootstrap_95"] = {"SF_pooled_excess": q(bs_ex), "SF_over_SD_rate": q(bs_ratio)}
# enrichment of position classes among lethal pairs vs sampled pairs
s = json.load(open("s3_summary.json"))
for g in ("loc_SF", "loc_SD"):
    a, l = s[g]["position_class_all"], s[g]["position_class_lethal"]
    ta, tl = sum(a.values()), sum(l.values())
    out[g + "_enrichment"] = {k: round((l.get(k, 0) / tl) / (a[k] / ta), 2) for k in a}
json.dump(out, open("s3_extra.json", "w"), indent=1)
print(json.dumps(out, indent=1))
