"""W2-Y: per-verdict ceiling decomposition of every C1 boundary verdict (boundaries_verdicts.json).
identity model per transect: metric_l = .5 + g*(ceil_l - .5)
  g_local : least squares (through (.5,.5)) on the transect's NON-boundary levels (task brief)
  g_pool  : same fit over every B level-mean of that family x metric, excluding this verdict's boundary pair
  g=1     : a design that attains its ceiling
pred step = g*(c[j+1]-c[j]); residual = observed jump - pred.
CLASS (accuracy metrics only): IDENTITY  share=pred/obs >= .67 and residual fails the PREREG s8 jump test
                                         (|res| < max(.10, 3*se));
                               GENUINE   residual alone passes that test and share < .33;
                               PARTIAL   otherwise.
sens/emit are program-space metrics (not accuracy): NA, with the ceiling change over the pair reported.
KA: level means recomputed from rows must equal the verdict's recorded means."""
import json, pathlib, collections
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
V = json.load(open(ROOT / "roles/Ananke/pte/c1_rows/boundaries_verdicts.json"))
C = json.load(open(HERE / "out/task1_ceilings.json"))["rows"]
ACC = ("acc", "plant")


def lv(rows, metric, wave):
    by = collections.defaultdict(list); cb = collections.defaultdict(list); blk = collections.defaultdict(list)
    for o in rows:
        if o["wave"] != wave: continue
        if metric == "acc" and o["kind"] != "evolve": continue
        by[o["li"]].append(o[metric])
        cb[o["li"]].append(o["ceil_held"] if metric == "acc" else o["ceil_plant"])
        k = "copy_block_held" if metric == "acc" else "copy_block_plant"
        if k in o: blk[o["li"]].append(o[k])
    idx = sorted(by)
    return (idx, np.array([np.mean(by[i]) for i in idx]), np.array([np.var(by[i], ddof=1) if len(by[i]) > 1 else .01 for i in idx]),
            np.array([len(by[i]) for i in idx]), np.array([np.mean(cb[i]) for i in idx]),
            np.array([np.mean(blk[i]) for i in idx]) if blk else None,
            {i: [o["level"] for o in rows if o["li"] == i][0] for i in idx})


def gfit(m, c):
    x = c - .5; y = m - .5
    return float((x * y).sum() / (x * x).sum()) if (x * x).sum() > 1e-4 else None


groups = collections.defaultdict(list)
for o in C:
    groups[(o["family"], o["dial"], o["base"], o["track"])].append(o)

# pooled level means per family x metric (wave B)
pool = collections.defaultdict(list)
for key, rows in groups.items():
    for metric in ACC:
        if metric == "acc" and not any(o["kind"] == "evolve" for o in rows): continue
        idx, m, _, _, c, _, _ = lv(rows, metric, "B")
        for i, mm, cc in zip(idx, m, c): pool[(key[0], metric)].append((key, i, mm, cc))

res = []
for v in V:
    key = (v["family"], v["dial"], v["base"], v["track"]); rows = groups[key]; met = v["metric"]
    j0, j1 = v["between"]
    o = {k: v[k] for k in ("family", "dial", "base", "track", "metric", "between", "label")}
    o["obs_means"] = [round(x, 3) for x in v["means"]]; o["obs_jump"] = round(v["jump"], 3); o["se"] = round(v["se"], 3)
    if met not in ACC:
        idx, _, _, _, c, _, levels = lv([dict(r, sens=r["sens"], emit=r["emit"]) for r in rows], "plant", "B")
        o["levels"] = [levels[i] for i in idx]
        o["ceil"] = [round(x, 3) for x in c]; o["d_ceil"] = round(float(c[idx.index(j1)] - c[idx.index(j0)]), 3)
        o["class"] = "NA (program-space metric; ceiling " + ("flat" if abs(o["d_ceil"]) < .02 else "moves") + ")"
        res.append(o); continue
    idx, m, var, ns, c, cblk, levels = lv(rows, met, "B")
    o["ka_means_match"] = bool(np.allclose(m, v["means"], atol=1e-9))
    o["levels"] = [levels[i] for i in idx]
    o["ceil"] = [round(x, 3) for x in c]
    if cblk is not None: o["copy_ceil"] = [round(x, 3) for x in cblk]
    a, b = idx.index(j0), idx.index(j1)
    nb = [k for k in range(len(idx)) if k not in (a, b)]
    gl = gfit(m[nb], c[nb]) if nb else None
    P = [(mm, cc) for (kk, i, mm, cc) in pool[(v["family"], met)] if not (kk == key and i in (j0, j1))]
    gp = gfit(np.array([p[0] for p in P]), np.array([p[1] for p in P]))
    dc = float(c[b] - c[a])
    o["d_ceil"] = round(dc, 3); o["g_local"] = None if gl is None else round(gl, 3); o["g_pool"] = None if gp is None else round(gp, 3)
    g = gl if gl is not None else gp
    o["g_used"] = "local" if gl is not None else "pool"
    pred = g * dc; resid = v["jump"] - pred
    o["pred_step"] = round(pred, 3); o["residual"] = round(resid, 3)
    o["resid_se"] = round(resid / v["se"], 1) if v["se"] > 0 else None
    o["pred_g1"] = round(dc, 3); o["resid_g1"] = round(v["jump"] - dc, 3)
    o["pred_pool"] = None if gp is None else round(gp * dc, 3)
    share = pred / v["jump"]
    o["share"] = round(share, 2)
    passes = abs(resid) >= max(.10, 3 * v["se"])
    o["class"] = ("IDENTITY" if share >= .67 and not passes else "GENUINE" if passes and share < .33 else "PARTIAL")
    # fresh-seed (B2) transect, same decomposition with the B-fitted g
    if any(r["wave"] == "B2" for r in rows):
        i2, m2, var2, n2, c2, _, _ = lv(rows, met, "B2")
        if j0 in i2 and j1 in i2:
            a2, b2 = i2.index(j0), i2.index(j1)
            ob2 = float(m2[b2] - m2[a2]); dc2 = float(c2[b2] - c2[a2])
            o["B2_means"] = [round(x, 3) for x in m2]; o["B2_ceil"] = [round(x, 3) for x in c2]
            o["B2_jump"] = round(ob2, 3); o["B2_pred"] = round(g * dc2, 3); o["B2_resid"] = round(ob2 - g * dc2, 3)
    res.append(o)

json.dump(res, open(HERE / "out/verdict_table.json", "w"), indent=1)
for o in res:
    print(json.dumps(o))
print("KA means:", sum(o.get("ka_means_match", False) for o in res), "/", sum(o["metric"] in ACC for o in res))
print(collections.Counter((o["metric"] in ACC, o["class"]) for o in res))
