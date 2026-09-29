"""Pre-freeze attainability table, larger designs (PLAN.md s3). No specimen data read."""
import json, time
import swap_rel as sr
out = json.load(open("out/attain_table.json"))
t = time.time()
for P, K in ((128, 12), (256, 10), (256, 11), (256, 12)):
    pm = sr.p_min(P, K)
    curve = {p: sr.power(p, P, K) for p in (0.55, 0.58, 0.6, 0.65, 0.7)}
    out[f"P{P}_K{K}"] = {"p_min": pm, "power": curve}
    print(P, K, "p_min", pm, {p: round(min(v.values()), 2) for p, v in curve.items()}, round(time.time() - t), flush=True)
json.dump(out, open("out/attain_table.json", "w"), indent=1)
