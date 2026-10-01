"""W2-2 a7: does the individual single-interaction law (h1, 7ae3, BASE) reproduce X-TICKET's burst-size distribution,
and does it produce any runaways? Pure arithmetic on h1 output (no VM). Offspring = P-11-causal births of an individual
within H=60 interactions (the causal-lineage ruler X-TICKET uses); founder law = generation 0, descendants = generations >= 1.
Also the ATOMIC law for comparison with C-ATOMIC C1 (46/80 runaways). python -B a7_gw_vs_ticket.py -> a7_gw_vs_ticket.json
"""
import json, pathlib, random
from collections import Counter
HERE = pathlib.Path(__file__).resolve().parent
T = json.load(open(HERE / "h1_lineage_tree_7ae3.json"))
TK = json.load(open(HERE / "a1_ticket.json"))
out = {}
rng = random.Random(20260930)

def laws(key, field):
    ind = [x for r in T["runs"][key] for x in r["tree"]]
    f0 = [x[field] for x in ind if x["gen"] == 0]
    f1 = [x[field] for x in ind if x["gen"] >= 1]
    return f0, f1

def sim(f0, f1, n=20000, cap=2000):
    tot = []
    for _ in range(n):
        alive = rng.choice(f0); total = alive
        while alive and total < cap:
            k = sum(rng.choice(f1) for _ in range(alive)); total += k; alive = k
        tot.append(total)
    return tot

def bins(v):
    n = len(v)
    return {"0": round(sum(x == 0 for x in v) / n, 4), "1-4": round(sum(1 <= x <= 4 for x in v) / n, 4),
            "5-26": round(sum(5 <= x <= 26 for x in v) / n, 4), "27-162": round(sum(27 <= x <= 162 for x in v) / n, 4),
            ">=163": round(sum(x >= 163 for x in v) / n, 4)}
for key in ("7ae3_BASE", "7ae3_ATOMIC"):
    for field in ("causal", "births"):
        f0, f1 = laws(key, field)
        s = sim(f0, f1)
        out[f"{key}_{field}"] = dict(m0=round(sum(f0) / len(f0), 3), m1=round(sum(f1) / len(f1), 3), predicted=bins(s),
                                     max_finite=max(x for x in s if x < 2000) if any(x < 2000 for x in s) else None)
obs = [r["B300"] for r in TK["rows"]]
out["x_ticket_observed_B300"] = bins(obs)
out["x_ticket_n"] = len(obs)
# observed B300 among runs where the founder survived epoch 1 or copied (removes the 28% epoch-1 loss the h1 founder law already contains? reported both)
json.dump(out, open(HERE / "a7_gw_vs_ticket.json", "w"), indent=1)
print(json.dumps(out, indent=1))
