"""Offline breakdown of t_a k1 mutants: active plant line vs NOP-padding line, by field. No evaluation."""
import json, sys, numpy as np
sys.argv += [] 
from ak_common import cell, plant, save
p = sys.argv[1]
d = json.load(open(f"out/t_a_neighbourhood_{p}.json"))
r, ph, env, sp = cell(p); pl = plant(p, ph); G, L, F = pl.shape
active = set(int(i) for i in np.flatnonzero(pl[0, :, 0] % 16 != 0))
pa = d["summary"]["plant_acc"]
grp = {}
for m in d["meta"]:
    if m["kind"] != "k1": continue
    gi, rem = divmod(m["pos"][0], L * F); li, fi = divmod(rem, F)
    key = ("active" if li in active else "nop") + f"_f{fi}"
    grp.setdefault(key, []).append(m["acc"])
out = {"plant_acc": pa, "active_lines": sorted(active)}
for k in sorted(grp):
    a = np.array(grp[k]); out[k] = {"n": len(a), "mean": round(float(a.mean()), 3), "frac_ge_plant-.05": round(float((a >= pa - .05).mean()), 3), "frac_lt_.60": round(float((a < .6).mean()), 3)}
    print(k, out[k])
mo = [m for m in d["meta"] if m["kind"] == "mutate_op"]
print("mutate_op lines_changed hist", np.bincount([m["lines_changed"] for m in mo]).tolist())
save(f"nb_detail_{p}.json", out)
