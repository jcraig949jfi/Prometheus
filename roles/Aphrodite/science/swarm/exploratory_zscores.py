"""EXPLORATORY, POST-HOC diagnostic (not preregistered). Per-cell CI gates aggregated
with "any INDETERMINATE -> INDETERMINATE" make INDETERMINATE near-certain over
hundreds of cells even when a model is exact. The multiplicity-aware question:
is the distribution of per-cell z = (sim - model)/SE consistent with the model
being right (|z| > 1.96 in ~5% of cells, |z| > 3 in ~0.3%, no systematic sign)?
Reads ledgers/VERDICTS.json only; writes ledgers/X_ZSCORES.json.
"""
import json
import math
from pathlib import Path

L = Path(__file__).resolve().parent / "ledgers"
V = json.loads((L / "VERDICTS.json").read_text(encoding="utf-8"))


def se(p, n):
    return math.sqrt(max(p * (1 - p), 1e-12) / n)


fams = {"S1b_P_major": [], "S1c_final": [], "S2a1_precision": [], "S2b1_accuracy": [], "S4a_majority": []}
for c in V["S1"]["cells"]:
    if c["R0"] >= 1.2:
        fams["S1b_P_major"].append((c["P_major"] - c["model_P_major"]) / se(c["model_P_major"], 400))
        if c.get("final_se"):
            fams["S1c_final"].append((c["final_given_major"] - c["model_final"]) / c["final_se"])
for c in V["S2a"]["cells"]:
    if "precision" in c:
        fams["S2a1_precision"].append((c["precision"] - c["model_precision"]) / se(c["model_precision"], c["accepted"]))
for h in V["S2b"]["by_h"].values():
    for s in h["series"]:
        fams["S2b1_accuracy"].append((s["sim"] - s["model"]) / se(s["model"], 4000))
for c in V["S4"]["cells"]:
    fams["S4a_majority"].append((c["sim"] - c["model"]) / se(c["model"], 20000))
out = {}
for k, zs in fams.items():
    n = len(zs)
    out[k] = {"cells": n, "frac_abs_z_gt_1.96": sum(abs(z) > 1.96 for z in zs) / n,
              "frac_abs_z_gt_3": sum(abs(z) > 3 for z in zs) / n, "max_abs_z": max(abs(z) for z in zs),
              "mean_z": sum(zs) / n}
(L / "X_ZSCORES.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out.items():
    print(k, {a: round(b, 3) for a, b in v.items()})
