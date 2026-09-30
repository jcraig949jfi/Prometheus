"""W-Y known-answer checks (PLAN s4, PLAN_ADDENDUM A3 + A6). python ka.py -> out/ka.json"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wyana  # noqa: E402

res = {}
pa = wyana.summarize("pa", quiet=True)
pb = wyana.summarize("pb", quiet=True)
dec = lambda out: {k: t for k, t in out["strata"].items() if t["lab"] != "pooled"}
inf = lambda out: {k: t for k, t in dec(out).items() if t["class"] not in ("UNDEFINED", "NOT-INFORMATIVE")}

# KA-A as pre-registered (A3): IS at every informative stratum with kp7_diff >= .5 and fla_diff >= .5, >= 2 strata
live = {k: t["class"] for k, t in inf(pa).items() if t["cen_kp7_diff"] >= 0.5 and t["cen_fla_diff"] >= 0.5}
res["KA-A_prereg"] = {"strata": live, "pass": len(live) >= 2 and all(c == "KP7 IS THE READOUT HALF" for c in live.values())}

# A6 (POST HOC, labelled): cue-bearing census. In Plant A, Kp[7] carries THIS trial's cue iff the readout has
# processed >= 1 vote of trial k (Kp[7] != the previous trial's final sum, which is the stale value).
raw, meta = wyana.load_raw("pa")
Pd = int(raw["Pd"])
ns0 = raw["normal_s0"]
cur = {}
for oi, o in enumerate(raw["offsets"].tolist()):
    kv = raw["cen_kp7_val"][oi]                          # [M, nt]
    stale = np.zeros_like(kv)
    stale[:, 1:] = ns0[:, :-1]
    c = (kv != stale)[0::2]                              # pair: A-world's Kp[7] is current
    for lab, q in (("q0", 0), ("q1", 1)):
        trs = [k for k in raw["trials"].tolist() if (k * Pd + o) % 2 == q]
        cur[f"o{o}{lab}"] = float(c[:, trs].mean())
both = {k: (t["class"], round(cur[k], 2), round(t["cen_fla_diff"], 2), round(t["cen_inbox_diff"], 2))
        for k, t in inf(pa).items() if cur[k] >= 0.5 and t["cen_fla_diff"] >= 0.5}
res["KA-A_A6_posthoc"] = {"kp7_current_frac": cur, "both_halves_carry_strata": both,
                          "pass": len(both) >= 1 and all(v[0] == "KP7 IS THE READOUT HALF" for k, v in both.items()
                                                         if v[3] == 0.0)}
# KA-B
b = {k: t["class"] for k, t in inf(pb).items()}
res["KA-B"] = {"strata": b, "pass": len(b) >= 2 and all(c == "KP7 NOT A CARRIER" for c in b.values())}
# MF-X
px = wyana.summarize("pa", kp="KPX", quiet=True)
x = {k: t["class"] for k, t in inf(px).items()}
res["MF-X"] = {"strata": x, "pass": len(x) >= 2 and all(c == "KP7 NOT A CARRIER" for c in x.values())}
# MF-SHUF (5 seeds)
sh = {}
for s in range(5):
    o = wyana.summarize("pa", shuffle_seed=s, quiet=True, write=(s == 0))
    sh[s] = {k: t["class"] for k, t in dec(o).items()}
    sh[s]["_e"] = {k: [round(t[a]["e"], 2) for a in ("KP7", "FLA", "KP7+FLA", "SITE_R")] for k, t in dec(o).items()
                   if "KP7" in t}
res["MF-SHUF"] = {"classes": sh,
                  "pass_no_IS": all(c != "KP7 IS THE READOUT HALF" for s in sh.values() for k, c in s.items() if k != "_e"),
                  "pass_literal": all(c in ("UNRESOLVED", "KP7 NOT A CARRIER", "NOT-INFORMATIVE", "UNDEFINED")
                                      for s in sh.values() for k, c in s.items() if k != "_e")}
(HERE / "out" / "ka.json").write_text(json.dumps(res, indent=1, default=float))
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "classes"} for k, v in res.items()}, indent=1, default=float))
print("MF-SHUF seed0", res["MF-SHUF"]["classes"][0])
