"""THESEUS-49 scoring (preregistered rules) -> theseus/runs/release_swap_2026-10-10/SUMMARY.json.

  PYTHONPATH=. python theseus/synth/release_swap_score.py
"""
import json
from collections import defaultdict

import numpy as np
from scipy.stats import binomtest, wilcoxon

D = "theseus/runs/release_swap_2026-10-10"
rows = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{D}/ROWS.jsonl", encoding="utf-8")}
tab = {f"{x['run']}:{x['id']}": x for x in map(json.loads, open("theseus/runs/store_release_2026-10-10/TABLE.jsonl", encoding="utf-8"))}
per = defaultdict(lambda: {"SWAP": [], "CTRL": []})
for k, v in rows.items():
    run, i, j, var = k.split(":")
    per[f"{run}:{i}"][var].append(v)
R = sorted(per)
sw = np.array([np.mean(per[r]["SWAP"]) for r in R])
ct = np.array([np.mean(per[r]["CTRL"]) for r in R])
base = np.array([tab[r]["J_release"] for r in R])
d = sw - ct
w = wilcoxon(sw, ct, alternative="greater")
res_sw = np.array([max(per[r]["SWAP"]) >= 0.6 for r in R])
res_ct = np.array([max(per[r]["CTRL"]) >= 0.6 for r in R])
b, c = int((res_sw & ~res_ct).sum()), int((~res_sw & res_ct).sum())
mc = binomtest(b, b + c, 0.5, alternative="greater").pvalue if b + c else 1.0
out = {"recipients": len(R),
       "H_SWAP": {"mean_J_swap": float(sw.mean()), "mean_J_ctrl": float(ct.mean()),
                  "mean_diff": float(d.mean()), "median_diff": float(np.median(d)),
                  "wilcoxon_p_one_sided": float(w.pvalue)},
       "S1_rescue": {"swap": int(res_sw.sum()), "ctrl": int(res_ct.sum()), "discordant_swap_only": b,
                     "discordant_ctrl_only": c, "mcnemar_exact_p_one_sided": float(mc)},
       "S2_swap_vs_base": {"mean_base": float(base.mean()), "mean_change": float((sw - base).mean())},
       "S3_ctrl_vs_base": {"mean_change": float((ct - base).mean())},
       "per_eval_rescue": {"swap": int(sum(v >= 0.6 for k, v in rows.items() if k.endswith("SWAP"))),
                           "ctrl": int(sum(v >= 0.6 for k, v in rows.items() if k.endswith("CTRL"))),
                           "n_each": int(sum(1 for k in rows if k.endswith("SWAP")))}}
json.dump(out, open(f"{D}/SUMMARY.json", "w"), indent=1)
print(json.dumps(out, indent=1))
