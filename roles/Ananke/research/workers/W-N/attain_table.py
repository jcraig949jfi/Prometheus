"""Pre-freeze attainability table (PLAN.md s3). No specimen data is read."""
import json, sys, time
import numpy as np
import swap_rel as sr
out = {}
t = time.time()
for P in (32, 64, 128):
    for K in (3, 10, 11):
        pm = sr.p_min(P, K)
        curve = {p: sr.power(p, P, K) for p in (0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9, 1.0)}
        out[f"P{P}_K{K}"] = {"p_min": pm, "power": curve}
        print(P, K, "p_min", pm, {p: round(min(v.values()), 2) for p, v in curve.items()}, round(time.time() - t), flush=True)
json.dump(out, open("out/attain_table.json", "w"), indent=1)
