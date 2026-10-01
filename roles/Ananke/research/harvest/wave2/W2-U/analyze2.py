"""TASK 2 analysis: ceiling-normalised dial effects for RELAY (A0 plant viability; A1 evolved held acc).
Reuses campaign.DIALS/ENV_DIALS and a getter-parametrised copy of campaign.dial_effects (KA: identical scores)."""
import json, pathlib, sys, os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
H = pathlib.Path(__file__).resolve().parent
ROOT = H.parents[5]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(H.parents[1] / "H-PLANT"))
import numpy as np
import hp_common as hc
from prometheus.ananke import campaign as C

def dial_effects(rs, get):
    out = []
    for dial in list(C.DIALS) + list(C.ENV_DIALS):
        by = {}
        for r in rs:
            v = get(r)
            if v is None:
                continue
            lv = r["levels"].get(dial, r["env_levels"].get(dial))
            by.setdefault(json.dumps(lv), []).append(v)
        if len(by) < 2:
            continue
        means = {k: float(np.mean(v)) for k, v in by.items()}
        ses = [np.std(v) / np.sqrt(len(v)) if len(v) > 1 else 0.1 for v in by.values()]
        spread = max(means.values()) - min(means.values())
        se = float(np.sqrt(np.mean(np.square(ses)))) + 1e-9
        out.append((spread / se, dial, means, spread))
    return sorted(out, key=lambda x: -x[0])

R = hc.rows()
A0 = [r for r in R if r["wave"] == "A0" and r["env"]["family"] == "RELAY"]
cmap = {o["cell"]: o for o in json.load(open(H / "out/task2_a0_ceil.json"))["rows"]}
big = {o["cell"]: o for o in json.load(open(H / "out/task1b_big.json"))["rows"]}
res = {}
# ---- KA: reproduce the C1 report ranking exactly
ka = C.dial_effects(A0, "RELAY", "plant")
mine = dial_effects(A0, lambda r: r["result"]["plant"]["acc"])
res["ka_dial_effects_identical"] = all(abs(a[0] - b[0]) < 1e-12 and a[1] == b[1] for a, b in zip(ka, mine)) and len(ka) == len(mine)
res["ka_top5"] = [(d, round(s, 1)) for s, d, _ in ka[:5]]
EPS = 0.55
def rank(eff, n=12): return [(d, round(s, 1), round(sp, 4)) for s, d, _, sp in eff[:n]]
def full(eff): return {d: {"score": round(s, 2), "spread": round(sp, 4), "rank": i + 1,
                           "means": {k: round(v, 4) for k, v in sorted(m.items())}} for i, (s, d, m, sp) in enumerate(eff)}
for label, rows, acc, ceil in [
    ("A0_plant", A0, lambda r: r["result"]["plant"]["acc"], lambda r: cmap[r["cell_id"]]["plant"]["joint"]),
]:
    acc_all = np.array([acc(r) for r in rows]); ce = np.array([ceil(r) for r in rows])
    keep = [r for r in rows if ceil(r) > EPS]
    # least-squares gain g in acc-.5 = g (ceil-.5): the "identity" model
    x, y = ce - .5, acc_all - .5
    g = float((x * y).sum() / (x * x).sum())
    corr = float(np.corrcoef(ce, acc_all)[0, 1])
    E = {
        "raw_all": dial_effects(rows, acc),
        "ceiling_itself": dial_effects(rows, ceil),
        "identity_pred(.5+g(ceil-.5))": dial_effects(rows, lambda r: .5 + g * (ceil(r) - .5)),
        "raw_open(ceil>.55)": dial_effects(keep, acc),
        "normalised_open(ceil>.55)": dial_effects(keep, lambda r: (acc(r) - .5) / (ceil(r) - .5)),
        "residual_all(acc-identity_pred)": dial_effects(rows, lambda r: acc(r) - (.5 + g * (ceil(r) - .5))),
    }
    res[label] = {"n": len(rows), "n_open": len(keep), "n_ceil_le_.55": len(rows) - len(keep),
                  "g_identity": g, "corr_ceil_acc": corr,
                  "mean_ceil": float(ce.mean()), "frac_ceil_eq_.5": float((ce <= .5 + 1e-12).mean()),
                  "viable(acc>=.75)_with_ceil_le_.55": int(sum((acc_all >= .75) & (ce <= .55))),
                  "acc_gt_ceil_rows": int(sum(acc_all > ce + 1e-9)),
                  "max_acc_minus_ceil": float((acc_all - ce).max()),
                  "rank": {k: rank(v) for k, v in E.items()}, "full": {k: full(v) for k, v in E.items()}}
    # identity share per focal dial: spread of identity prediction / spread of raw
    fr, fi, fn = full(E["raw_all"]), full(E["identity_pred(.5+g(ceil-.5))"]), full(E["normalised_open(ceil>.55)"])
    res[label]["identity_share"] = {d: round(fi[d]["spread"] / fr[d]["spread"], 3) for d in fr}
# ---- A1 / all-RELAY evolve held acc, normalised by EXACT held-set ceiling
for label, wv in [("A1_heldacc", ("A",)), ("evolve_all_heldacc", ("A", "B", "B2", "C", "D", "E"))]:
    rows = [r for r in R if r["kind"] == "evolve" and r["env"]["family"] == "RELAY" and r["wave"] in wv]
    acc = lambda r: r["result"]["held"]["acc"]
    ceil = lambda r: big[r["cell_id"]]["held"]["joint"]
    keep = [r for r in rows if ceil(r) > EPS]
    ce = np.array([ceil(r) for r in rows]); aa = np.array([acc(r) for r in rows])
    x, y = ce - .5, aa - .5
    g = float((x * y).sum() / (x * x).sum())
    E = {"raw_all": dial_effects(rows, acc), "ceiling_itself": dial_effects(rows, ceil),
         "identity_pred": dial_effects(rows, lambda r: .5 + g * (ceil(r) - .5)),
         "raw_open(ceil>.55)": dial_effects(keep, acc),
         "normalised_open(ceil>.55)": dial_effects(keep, lambda r: (acc(r) - .5) / (ceil(r) - .5))}
    if label == "A1_heldacc":
        ka2 = C.dial_effects(rows, "RELAY", "acc")
        res["ka_A1_acc_identical"] = all(abs(a[0] - b[0]) < 1e-12 and a[1] == b[1] for a, b in zip(ka2, E["raw_all"]))
    fr, fi = full(E["raw_all"]), full(E["identity_pred"])
    res[label] = {"n": len(rows), "n_open": len(keep), "g_identity": g, "corr": float(np.corrcoef(ce, aa)[0, 1]),
                  "rank": {k: rank(v) for k, v in E.items()}, "full": {k: full(v) for k, v in E.items()},
                  "identity_share": {d: round(fi[d]["spread"] / fr[d]["spread"], 3) for d in fr}}
# sensitivity: is the sens metric related to the ceiling at all?
sens = np.array([r["result"]["gen0"]["frac_sensitive_any"] for r in A0])
ce = np.array([cmap[r["cell_id"]]["plant"]["joint"] for r in A0])
res["sens_corr_with_ceiling"] = float(np.corrcoef(sens, ce)[0, 1])
json.dump(res, open(H / "out/task2_summary.json", "w"), indent=1)
print("KA", res["ka_dial_effects_identical"], res.get("ka_A1_acc_identical"), res["ka_top5"])
for lab in ("A0_plant", "A1_heldacc", "evolve_all_heldacc"):
    print("=====", lab, {k: res[lab][k] for k in res[lab] if k not in ("rank", "full", "identity_share")})
    for k, v in res[lab]["rank"].items():
        print("  ", k, v[:8])
    foc = ("delta", "lat_base", "update_mode", "decay_shift", "economy", "topology", "d", "loss", "update_p", "update_period", "lat_hop")
    print("   identity share:", {d: res[lab]["identity_share"].get(d) for d in foc})
    print("   ranks normalised:", {d: (res[lab]["full"]["raw_all"][d]["rank"], res[lab]["full"]["normalised_open(ceil>.55)"][d]["rank"], res[lab]["full"]["raw_open(ceil>.55)"][d]["rank"]) for d in foc if d in res[lab]["full"]["raw_all"]})
print("sens corr", res["sens_corr_with_ceiling"])
