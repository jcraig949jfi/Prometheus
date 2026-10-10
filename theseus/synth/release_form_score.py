"""THESEUS-50 scoring (preregistered rules) -> theseus/runs/release_form_2026-10-10/SUMMARY.json.

  PYTHONPATH=. python theseus/synth/release_form_score.py
"""
import json
from collections import defaultdict

import numpy as np
from scipy.stats import wilcoxon

from theseus.synth import pooled as P

D = "theseus/runs/release_form_2026-10-10"
form = [json.loads(l) for l in open(f"{D}/FORM.jsonl", encoding="utf-8")]
st = [r for r in form if r["J_store"] >= 0.6]
rel = lambda r: r["J_release"] >= 0.6  # noqa: E731
tabs = []
for a in ("law", "nolaw"):
    for s in (1, 2, 3, 4):
        A = [r for r in st if r["arm"] == a and r["stratum"] == s and r["F"] >= 1]
        B = [r for r in st if r["arm"] == a and r["stratum"] == s and r["F"] == 0]
        tabs.append((sum(map(rel, A)), len(A), sum(map(rel, B)), len(B)))
tabs_nz = [t for t in tabs if t[1] and t[3]]
z, p = P.cmh(tabs_nz)
rd, lo, hi = P.rd_mh(tabs_nz)
desc = {}
for a in ("law", "nolaw"):
    A = [r for r in form if r["arm"] == a]
    S = [r for r in st if r["arm"] == a]
    desc[a] = {"F_ge1_share_all": [sum(r["F"] >= 1 for r in A), len(A)],
               "release_given_store_F_ge1": [sum(rel(r) for r in S if r["F"] >= 1), sum(r["F"] >= 1 for r in S)],
               "release_given_store_F0": [sum(rel(r) for r in S if r["F"] == 0), sum(r["F"] == 0 for r in S)]}
# Part B
single = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{D}/ROWS.jsonl", encoding="utf-8")}
swap = {json.loads(l)["id"]: json.loads(l)["v"] for l in open("theseus/runs/release_swap_2026-10-10/ROWS.jsonl", encoding="utf-8")}
per = defaultdict(lambda: defaultdict(list))
for k, v in single.items():
    run, i, j, _ = k.split(":")
    per[f"{run}:{i}"]["SINGLE"].append(v)
for k, v in swap.items():
    run, i, j, var = k.split(":")
    per[f"{run}:{i}"][var].append(v)
tab = {f"{x['run']}:{x['id']}": x["J_release"] for x in form}
R = sorted(per)
m = {v: np.array([np.mean(per[r][v]) for r in R]) for v in ("SWAP", "CTRL", "SINGLE")}
base = np.array([tab[r] for r in R])
d = m["CTRL"] - m["SINGLE"]
w = wilcoxon(m["CTRL"], m["SINGLE"], alternative="greater")
resc = {v: int(sum(max(per[r][v]) >= 0.6 for r in R)) for v in ("SWAP", "CTRL", "SINGLE")}
out = {"H_FORM": {"tables_law_s1-4_nolaw_s1-4": tabs, "CMH_z": z, "p_one_sided": p, "RD_MH": rd, "ci95": [lo, hi]},
       "form_by_arm": desc,
       "H_MULTI": {"mean_J": {v: float(m[v].mean()) for v in m}, "mean_base": float(base.mean()),
                   "mean_diff_ctrl_minus_single": float(d.mean()), "median_diff": float(np.median(d)),
                   "wilcoxon_p_one_sided": float(w.pvalue),
                   "swap_minus_single_mean": float((m["SWAP"] - m["SINGLE"]).mean()),
                   "single_minus_base_mean": float((m["SINGLE"] - base).mean()), "rescued": resc, "n": len(R)}}
json.dump(out, open(f"{D}/SUMMARY.json", "w"), indent=1)
print(json.dumps(out, indent=1))
