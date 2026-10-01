"""Known-answer gate G2: W-V PMAJ / PDICT re-run at W-V's design, offsets 2,4,6,12 (PLAN_ADDENDUM X1).
-> out/raw_g2_{pmaj,pdict}.npz, out/gate_g2.json"""
import os, sys, time
import numpy as np
import hchk as H
from prometheus.ananke import assays
wv, ana = H.mod("wv_wv"), H.mod("wv_ana")
H.threads1()
OFFS = [2, 4, 6, 12]
res = {"pid": os.getpid()}
outs = {}
t0 = time.time()
for nm in ("PMAJ", "PDICT"):
    ph, env, g, meta = wv.load(nm)
    H.threads1()
    seeds = assays.world_seeds(0x650, 128)
    r = wv.run(ph, g, env, seeds, OFFS, list(range(1, env.trials)), device=H.DEV)
    np.savez_compressed(H.OUT / f"raw_g2_{nm.lower()}.npz", **{k: v for k, v in r.items() if k != "arms"})
    outs[nm] = H.wv_summary(r)
    for t in outs[nm]["strata"].values():
        print(nm, H.wv_line(t), flush=True)
    if nm == "PMAJ":
        rawp = r
INF = (2, 4, 6)
pm, pd = outs["PMAJ"], outs["PDICT"]
s = H.informative(pm, INF)
res["KA-MAJ"] = {"classes": {k: t["class"] for k, t in s.items()}, "D": {k: t["piv"]["D"] for k, t in s.items()},
                 "pass": bool(s) and all(t["class"][0] == "MAJORITY" for t in s.values())}
s = H.informative(pd, INF)
res["KA-DICT"] = {"classes": {k: t["class"] for k, t in s.items()},
                  "pass": bool(s) and all(t["class"] == ["DICTATOR", [4]] for t in s.values())}
s = {k: t for k, t in pd["strata"].items() if t["o"] in INF and t["lab"] in ("q0", "q1") and t["n"] >= 20}
res["MF1"] = {"pass": bool(s) and all(max(t[f"s{j}"]["hi"] for j in range(4)) <= 0.05 for t in s.values())}
res["MF2"] = {"pass": all(t["class"][0] != "MAJORITY" for t in pd["strata"].values())}
# MF3: permuted pivot labels on my PMAJ run
perm = {}
for oi, o in enumerate(OFFS):
    if o not in INF:
        continue
    Pd = int(rawp["Pd"])
    trials = [int(k) for k in rawp["trials"]]
    for lab, trs in (("q0", [k for k in trials if (k * Pd + o) % 2 == 0]), ("q1", [k for k in trials if (k * Pd + o) % 2 == 1])):
        t = ana.stratum(rawp, oi, trs, permute_votes=True)
        c = ana.classify(t)
        perm[f"o{o}{lab}"] = {"class": c[0], "D": t["piv"]["D"]}
res["MF3"] = {"strata": perm, "pass": all(v["class"] != "MAJORITY" and v["D"] < 0.5 for v in perm.values())}
mf4 = {f"{nm}:{k}": t["class"][0] for nm, out in (("pmaj", pm), ("pdict", pd)) for k, t in out["strata"].items() if t["o"] == 12}
res["MF4"] = {"classes": mf4, "pass": all(c in ("NOT-INFORMATIVE", "UNDEFINED") for c in mf4.values())}
res["PASS"] = all(v["pass"] for v in res.values() if isinstance(v, dict) and "pass" in v)
res["summaries"] = outs
res["wall_s"] = time.time() - t0
H.dump(res, "gate_g2.json")
print("G2 PASS", res["PASS"], {k: v["pass"] for k, v in res.items() if isinstance(v, dict) and "pass" in v}, round(time.time() - t0), "s", flush=True)
