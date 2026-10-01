"""W2-2 a4: analyse h1 lineage trees: offspring law, GW escape, heritability of fecundity, what the fecund variants changed.
python -B a4_tree_analysis.py -> a4_tree_analysis.json
"""
import json, pathlib, statistics as st
from collections import Counter
HERE = pathlib.Path(__file__).resolve().parent
F7 = json.load(open(HERE / "h1_lineage_tree_7ae3.json"))
FB = json.load(open(HERE / "h1_lineage_tree_cb7f.json"))
FOUNDER = {"7ae3": None, "cb7f": None}
out = {}

def gw_q(dist, it=2000):
    """extinction prob of a GW with offspring pmf dist (Counter n->count)."""
    tot = sum(dist.values()); q = 0.0
    for _ in range(it):
        q = sum(c / tot * q ** n for n, c in dist.items())
    return q

def spearman(x, y):
    def rk(v):
        s = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v); i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            for k in range(i, j + 1):
                r[s[k]] = (i + j) / 2
            i = j + 1
        return r
    a, b = rk(x), rk(y); ma, mb = st.mean(a), st.mean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b)); den = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5
    return round(num / den, 3) if den else None

for key, src in (("7ae3_BASE", F7), ("7ae3_ATOMIC", F7), ("cb7f_BASE", FB), ("cb7f_ATOMIC", FB)):
    reps = src["runs"][key]
    trees = [r["tree"] for r in reps if "tree" in r]
    if not trees:
        continue
    allind = [x for t in trees for x in t]
    founder_hex = trees[0][0]["hex"]
    d_all = Counter(x["births"] for x in allind); d_c = Counter(x["causal"] for x in allind)
    m = st.mean(x["births"] for x in allind); mc = st.mean(x["causal"] for x in allind)
    # per-generation means (gen>=1 are children: inherit victim registers)
    pg = {}
    for x in allind:
        pg.setdefault(x["gen"], []).append(x)
    # heritability: parent fecundity vs child fecundity
    pairs = []
    for t in trees:
        for x in t:
            if x["parent"] >= 0:
                pairs.append((t[x["parent"]]["births"], x["births"]))
    # age profile
    ages = [a for x in allind for a in x["ages"]]
    late = sum(a >= 7 for a in ages) / len(ages) if ages else None
    # fecund variants: births >= 8; positions where they differ from founder
    fec = [x for x in allind if x["births"] >= 8]
    nonfec = [x for x in allind if x["gen"] >= 1 and x["births"] <= 1]
    def diffpos(xs):
        c = Counter()
        for x in xs:
            g = bytes.fromhex(x["hex"]); f = bytes.fromhex(founder_hex)
            for i in range(min(len(g), len(f))):
                if g[i] != f[i]:
                    c[i] += 1
        return c
    dfec, dnon = diffpos(fec), diffpos(nonfec)
    enrich = sorted(((round(dfec[i] / max(1, len(fec)) - dnon[i] / max(1, len(nonfec)), 2), i, dfec[i], dnon[i]) for i in range(64)), reverse=True)[:8]
    out[key] = dict(
        n_ind=len(allind), mean_births=round(m, 3), mean_causal=round(mc, 3),
        var_births=round(st.pvariance([x["births"] for x in allind]), 2),
        gw_escape_all=round(1 - gw_q(d_all), 3), gw_escape_causal=round(1 - gw_q(d_c), 3),
        gen_means={g: (round(st.mean(x["births"] for x in v), 2), round(st.mean(x["causal"] for x in v), 2), len(v)) for g, v in sorted(pg.items())},
        gen1plus_mean=round(st.mean(x["births"] for x in allind if x["gen"] >= 1), 3),
        gen1plus_gw_escape=round(1 - gw_q(Counter(x["births"] for x in allind if x["gen"] >= 1)), 3),
        founder_gw_escape=round(1 - gw_q(Counter(x["births"] for x in allind if x["gen"] == 0)), 3),
        offspring_pmf=dict(sorted(d_all.items())),
        heritability_spearman_parent_child=spearman([p for p, c in pairs], [c for p, c in pairs]), n_pairs=len(pairs),
        child_mean_by_parent_fecundity={lab: round(st.mean([c for p, c in pairs if lo <= p <= hi]), 2) if [c for p, c in pairs if lo <= p <= hi] else None
                                        for lab, lo, hi in (("p1", 1, 1), ("p2-3", 2, 3), ("p4-7", 4, 7), ("p8+", 8, 10 ** 6))},
        late_birth_share_age_ge7=round(late, 3) if late is not None else None,
        n_fecund_ge8=len(fec), fecund_survive_H=sum(x["died"] is None for x in fec),
        fecund_vs_nonfecund_diff_enrichment=enrich,
        fecund_examples=[(x["gen"], x["births"], x["died"], x["hex"]) for x in sorted(fec, key=lambda x: -x["births"])[:4]],
    )
    print(key, json.dumps({k: v for k, v in out[key].items() if k not in ("fecund_examples",)}))
out["founders"] = {"7ae3": F7["runs"]["7ae3_BASE"][0]["tree"][0]["hex"]}
json.dump(out, open(HERE / "a4_tree_analysis.json", "w"), indent=1)
