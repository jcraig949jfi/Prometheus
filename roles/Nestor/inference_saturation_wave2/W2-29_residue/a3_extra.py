"""W2-29 a3: secondary numbers (not rule-bearing): B readout Fisher, pooled with X-TICKET 4/4; Mantel-Haenszel FULL vs BANK
across ring-morph strata; byte-43 = C3 (W2-24 keep variant) and side-0 share in successes with no side-0 genome."""
import json, pathlib
from scipy.stats import fisher_exact
from scipy.stats import chi2
HERE = pathlib.Path(__file__).resolve().parent
A = json.load(open(HERE / "a2_ring.json"))
c = json.load(open(HERE / "c1_classes.json"))
out = {}
F, B = A["primary_B"]["FULL"], A["primary_B"]["BANK"]
out["B_readout_FULL_vs_BANK_p1s"] = fisher_exact([[F[0], F[1]-F[0]], [B[0], B[1]-B[0]]], alternative="greater")[1]
out["B_readout_FULL+XTICKET(13/26)_vs_BANK_p1s"] = fisher_exact([[F[0]+4, F[1]-F[0]], [B[0], B[1]-B[0]]], alternative="greater")[1]
out["FULL_B_vs_XTICKET_4of4_p2s"] = fisher_exact([[F[0], F[1]-F[0]], [4, 0]])[1]
tabs = []
for k in ("morph", "none"):
    f, b = A["rule_present"]["strata"]["FULL"][k], A["rule_present"]["strata"]["BANK"][k]
    tabs.append([[f[0], f[1]-f[0]], [b[0], b[1]-b[0]]])
num = sum(t[0][0]*t[1][1]/sum(map(sum, t)) for t in tabs); den = sum(t[0][1]*t[1][0]/sum(map(sum, t)) for t in tabs)
out["MH_OR_FULL_vs_BANK_ring_present"] = num / den
E = V = O = 0.0
for (a, b), (cc, d) in tabs:
    n = a+b+cc+d; r1, c1 = a+b, a+cc
    O += a; E += r1*c1/n; V += r1*(n-r1)*c1*(n-c1)/(n*n*(n-1))
out["CMH_chi2"] = (O-E)**2/V
out["CMH_p_2s"] = chi2.sf((O-E)**2/V, 1)
rows = {(r["arm"], r["s"]): r for r in A["rows"]}
per = {}
for tag, arm in (("FULL", "FULL"), ("BANKREP", "BANK")):
    for l in open(HERE / ("genomes_%s.jsonl" % tag)):
        d = json.loads(l)
        if (arm, d["s"]) not in rows: continue
        tot = sum(x[3] for x in d["genomes"])
        s0 = sum(x[3] for x in d["genomes"] if c[x[0]]["side0"])
        c3 = sum(x[3] for x in d["genomes"] if bytes.fromhex(x[0])[43] == 0xC3)
        r = rows[(arm, d["s"])]
        per["%s_%d" % (arm, d["s"])] = {"succ": r["succ"], "B": r["B"], "side0_birth_share": round(s0 / tot, 3),
                                        "c3_birth_share": round(c3 / tot, 3), "ring_morph": r["m_present"]}
out["per_run"] = per
json.dump(out, open(HERE / "a3_extra.json", "w"), indent=1)
for k, v in out.items():
    if k != "per_run": print(k, v)
for k, v in per.items():
    if v["succ"] or v["c3_birth_share"] > 0.05: print(k, v)
