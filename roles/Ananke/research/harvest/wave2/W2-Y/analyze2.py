"""W2-Y: repeat the analyze1 decomposition with the FLOOD ceiling (flood_ceil.py) in place of the light cone,
for the RELAY delta/decay/economy and MAJ topology/economy (base 1, phys) verdicts.
decay/economy: flood ceiling computed at level 0 only and copied to every level (no transport dial differs)."""
import json, pathlib, collections
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
V = json.load(open(ROOT / "roles/Ananke/pte/c1_rows/boundaries_verdicts.json"))
C = {o["cell"]: o for o in json.load(open(HERE / "out/task1_ceilings.json"))["rows"]}
FL = json.load(open(HERE / "out/task2_flood_rows.json"))["rows"]
flood = collections.defaultdict(lambda: collections.defaultdict(list))
for f in FL:
    k = (f["family"], f["dial"], f["base"], f["track"], f["wave"])
    flood[k + ("plant",)][f["li"]].append(f["flood_plant"])
    if "flood_held" in f:
        flood[k + ("acc",)][f["li"]].append(f["flood_held"])
rows = collections.defaultdict(lambda: collections.defaultdict(list))
for o in C.values():
    for met in ("plant", "acc"):
        if o.get(met) is None: continue
        rows[(o["family"], o["dial"], o["base"], o["track"], o["wave"], met)][o["li"]].append(o[met])


def gfit(m, c):
    x = c - .5; y = m - .5
    return float((x * y).sum() / (x * x).sum()) if (x * x).sum() > 1e-4 else None


out = []
for v in V:
    met = v["metric"]
    if met not in ("acc", "plant"): continue
    key = (v["family"], v["dial"], v["base"], v["track"])
    fk = key + ("B", met)
    if fk not in flood: continue
    lvls = sorted(rows[fk])
    m = np.array([np.mean(rows[fk][i]) for i in lvls])
    fl = flood[fk]
    c = np.array([np.mean(fl[i]) if i in fl else np.mean(fl[0]) for i in lvls])
    a, b = lvls.index(v["between"][0]), lvls.index(v["between"][1])
    nb = [k for k in range(len(lvls)) if k not in (a, b)]
    gl = gfit(m[nb], c[nb]) if nb else None
    g = gl if gl is not None else 1.0
    dc = float(c[b] - c[a]); pred = g * dc; res = v["jump"] - pred
    passes = abs(res) >= max(.10, 3 * v["se"])
    share = pred / v["jump"]
    cls = "IDENTITY" if share >= .67 and not passes else "GENUINE" if passes and share < .33 else "PARTIAL"
    o = {"verdict": f'{v["family"]} {v["dial"]} b{v["base"]} {v["track"]} {met} {v["between"]}', "label": v["label"][15:],
         "means": [round(x, 3) for x in m], "flood_ceil": [round(x, 3) for x in c],
         "attain": [round((mm - .5) / (cc - .5), 2) if cc > .52 else None for mm, cc in zip(m, c)],
         "obs": round(v["jump"], 3), "d_flood": round(dc, 3), "g_local": None if gl is None else round(gl, 3),
         "pred": round(pred, 3), "resid": round(res, 3), "pred_g1": round(dc, 3), "resid_g1": round(v["jump"] - dc, 3),
         "share": round(share, 2), "class_flood": cls}
    fk2 = key + ("B2", met)
    if fk2 in flood:
        l2 = sorted(rows[fk2]); m2 = np.array([np.mean(rows[fk2][i]) for i in l2])
        c2 = np.array([np.mean(flood[fk2][i]) if i in flood[fk2] else np.mean(flood[fk2][0]) for i in l2])
        if v["between"][0] in l2 and v["between"][1] in l2:
            a2, b2 = l2.index(v["between"][0]), l2.index(v["between"][1])
            o.update(B2_means=[round(x, 3) for x in m2], B2_flood=[round(x, 3) for x in c2],
                     B2_obs=round(float(m2[b2] - m2[a2]), 3), B2_pred=round(g * float(c2[b2] - c2[a2]), 3),
                     B2_resid=round(float(m2[b2] - m2[a2]) - g * float(c2[b2] - c2[a2]), 3))
    out.append(o)
    print(json.dumps(o))
json.dump(out, open(HERE / "out/verdict_table_flood.json", "w"), indent=1)
