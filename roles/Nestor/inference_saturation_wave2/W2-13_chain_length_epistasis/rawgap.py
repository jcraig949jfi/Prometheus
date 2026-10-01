"""W2-13: unadjusted EVO_SD - RAND gap (genome bootstrap CI + label-permutation p) and the share explained by L_pre.
python -B rawgap.py -> rawgap.json"""
import json, random, pathlib
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / "lengths.json"))["rows"]
ev = [r for r in D if r["group"] == "EVO_SD" and r["n_null0"]]
un = [r for r in D if r["group"] == "RAND" and r["n_null0"]]
pr = lambda rs: sum(r["n_strict"] for r in rs) / sum(r["n_null0"] for r in rs)
obs = pr(ev) - pr(un)
rng = random.Random(11)
bs = [pr([rng.choice(ev) for _ in ev]) - pr([rng.choice(un) for _ in un]) for _ in range(4000)]
pool = ev + un; ge = 0
for _ in range(4000):
    rng.shuffle(pool); ge += abs(pr(pool[:len(ev)]) - pr(pool[len(ev):])) >= abs(obs) - 1e-12
a = json.load(open(HERE / "analysis.json"))["fits"]["PRIMARY_SDvsRAND|L_pre"]["WLS"]
out = {"raw_gap": obs, "boot95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p_perm": (ge + 1) / 4001,
       "adjusted_c": a["c_EVO"], "share_of_gap_explained_by_L_pre": 1 - a["c_EVO"] / obs,
       "genome_rate_vs_L_pre": {g: [[r["L_pre"], round(r["n_strict"] / r["n_null0"], 4), r["n_null0"]] for r in rs]
                                for g, rs in (("EVO_SD", ev), ("RAND", un))}}
json.dump(out, open(HERE / "rawgap.json", "w"), indent=1)
print({k: v for k, v in out.items() if k != "genome_rate_vs_L_pre"})
for g, rs in (("EVO_SD", ev), ("RAND", un)):
    for lo, hi in ((0, 15), (15, 30), (30, 45), (45, 65)):
        s = [r for r in rs if lo <= r["L_pre"] < hi]
        print(g, (lo, hi), len(s), round(pr(s), 4) if s else None, sum(r["n_null0"] for r in s))
