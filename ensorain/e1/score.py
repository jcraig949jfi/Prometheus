"""Frozen E1 scorer (PREREG_E1 part 1 s4-s6). Committed before any
confirmatory row. python -m ensorain.e1.score"""
import collections
import json
from fractions import Fraction  # noqa: F401  (no float gate at an attainable exact value; E0 lesson)

import numpy as np

NON_TT = ("LRU", "KNN", "CP", "LOWRANK", "MLP")
BEST_TT_POOL = ("TT_OBS", "TT_TUNED")
GATED = (128, 192)
RNG = np.random.default_rng(20260924)
BOOT = 10_000


def load(w):
    try:
        return [json.loads(l) for l in open(f"ensorain/runs/e1_confirm_{w}.jsonl")]
    except FileNotFoundError:
        return []


def ok(rows):
    return [r for r in rows if r.get("status") == "OK"]


def rate(r, kinds):
    n = sum(r[f"n_{k}"] for k in kinds)
    return sum(r[f"ok_{k}"] for k in kinds) / n if n else float("nan")


def eff_table(rows):
    """EFF per (arm, cap, lam, kappa_mult) -> {inst: mean over org seeds}."""
    nom = {(r["cap"], r["lam"], r.get("kappa_mult"), r["inst_seed"], r["org_seed"]): r["U"]
           for r in rows if r["arm"] == "NOMEM"}
    t = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r["arm"] == "NOMEM":
            continue
        k = (r["cap"], r["lam"], r.get("kappa_mult"), r["inst_seed"], r["org_seed"])
        if k not in nom:
            continue
        e = (r["U"] - nom[k]) / max(r["P_used"], 1)
        t[(r["arm"], r["cap"], r["lam"], r.get("kappa_mult"))][r["inst_seed"]].append(e)
    return {k: {i: float(np.mean(v)) for i, v in d.items()} for k, d in t.items()}


def per_inst(rows, arm, cap, lam, f):
    d = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == arm and r["cap"] == cap and r["lam"] == lam and r.get("kappa_mult") is None:
            d[r["inst_seed"]].append(f(r))
    return {i: float(np.nanmean(v)) for i, v in d.items()}


def paired(a, b):
    ks = sorted(set(a) & set(b))
    return np.array([a[k] for k in ks]), np.array([b[k] for k in ks])


def lo(diff):
    if len(diff) == 0:
        return float("nan")
    return float(np.quantile(diff[RNG.integers(len(diff), size=(BOOT, len(diff)))].mean(1), 0.025))


def gate_G(E, caps, km=None):
    out, ok_all = {}, True
    for cap in caps:
        tts = {a: E.get((a, cap, 0.0, km), {}) for a in BEST_TT_POOL}
        tts = {a: v for a, v in tts.items() if v}
        if not tts:
            out[cap] = "no TT rows"
            ok_all = False
            continue
        best = max(tts, key=lambda a: np.mean(list(tts[a].values())))
        rows = {}
        for x in NON_TT:
            ex = E.get((x, cap, 0.0, km), {})
            if not ex:
                rows[x] = "NA"
                continue
            t, b = paired(tts[best], ex)
            ratio_ok = t.mean() >= 1.10 * b.mean()
            l = lo(t - 1.10 * b)
            rows[x] = dict(tt=float(t.mean()), x=float(b.mean()), lo=l, pass_=bool(ratio_ok and l > 0))
            ok_all &= rows[x]["pass_"]
        out[cap] = dict(best_tt=best, vs=rows)
    return out, ok_all


def main():
    C1, C2, C3, C4 = (ok(load(w)) for w in ("C1", "C2", "C3", "C4"))
    raw3 = load("C3")
    rep = {}
    # table
    agg = collections.defaultdict(list)
    for r in C1:
        agg[(r["lam"], r["cap"], r["arm"])].append(r)
    print("lam  cap arm         n   reward   U       comp$  L1    L2    L3s   L3h   r2ho   P")
    for k in sorted(agg):
        v = agg[k]
        print("%.1f %4d %-10s %3d %7.0f %7.0f %6.1f %5.2f %5.2f %5.2f %5.2f %6.2f %4.0f" % (
            k[0], k[1], k[2], len(v), np.mean([r["reward"] for r in v]), np.mean([r["U"] for r in v]),
            np.mean([r["comp_energy"] for r in v]), np.nanmean([rate(r, ["L1"]) for r in v]),
            np.nanmean([rate(r, ["L2"]) for r in v]), np.nanmean([rate(r, ["L3s"]) for r in v]),
            np.nanmean([rate(r, ["L3h"]) for r in v]), np.median([r["r2_ho"] for r in v]),
            np.mean([r["P_used"] for r in v])))
    E = eff_table(C1)
    print("EFF (mean over instances)")
    for k in sorted(E, key=str):
        print("  ", k, round(float(np.mean(list(E[k].values()))), 4))

    # controls
    c = {}
    lat = [r for r in C1 if r["arm"] == "TT_LATENT" and r["cap"] == 192 and r["lam"] == 0.0]
    c["POS_L2_median"] = float(np.median([rate(r, ["L2"]) for r in lat])) if lat else float("nan")
    c["POS_r2ho_median"] = float(np.median([r["r2_ho"] for r in lat])) if lat else float("nan")
    c["POS_pass"] = bool(lat) and c["POS_L2_median"] >= 0.5 and c["POS_r2ho_median"] >= 0.5
    c["CHEAT_smuggler"] = [r.get("status") for r in raw3]
    c["CHEAT_smuggler_pass"] = bool(raw3) and all(r.get("status") == "AUDIT_REFUSED" for r in raw3)
    inj = [r["reward"] for r in C1 if r["arm"] == "TT_INJECT" and r["cap"] == 192 and r["lam"] == 0.0]
    orc = [r["reward"] for r in C1 if r["arm"] == "ORACLE" and r["cap"] == 192 and r["lam"] == 0.0]
    c["CHEAT_inject_ratio"] = float(np.mean(inj) / np.mean(orc)) if inj and orc else float("nan")
    c["CHEAT_inject_pass"] = c["CHEAT_inject_ratio"] >= 0.9
    neg = {}
    neg_ok = True
    for cap in GATED:
        nm = [rate(r, ["L2"]) for r in C1 if r["arm"] == "NOMEM" and r["cap"] == cap and r["lam"] == 1.0]
        for a in {r["arm"] for r in C1} - {"NOMEM", "ORACLE", "TT_INJECT"}:
            v = [rate(r, ["L2"]) for r in C1 if r["arm"] == a and r["cap"] == cap and r["lam"] == 1.0]
            if v and nm:
                d = float(np.nanmean(v) - np.nanmean(nm))
                neg[f"{a}@{cap}"] = round(d, 4)
                neg_ok &= d <= 0.05
    c["NEG_L2_minus_NOMEM_in_R"] = neg
    c["NEG_pass"] = neg_ok
    controls = c["POS_pass"] and c["CHEAT_smuggler_pass"] and c["CHEAT_inject_pass"] and c["NEG_pass"]
    rep["controls"] = c
    rep["controls_pass"] = controls

    # G
    g, g_ok = gate_G(E, GATED)
    rep["G"] = g
    rep["G_pass"] = g_ok
    rep["G_reported_caps_96_384"] = gate_G(E, (96, 384))[0]

    # TRANSFER at 192
    best192 = g.get(192, {}).get("best_tt") if isinstance(g.get(192), dict) else None
    tr_ok = False
    if best192:
        t, b = paired(per_inst(C1, best192, 192, 0.0, lambda r: rate(r, ["L2"])),
                      per_inst(C1, "NOMEM", 192, 0.0, lambda r: rate(r, ["L2"])))
        rep["TRANSFER"] = dict(arm=best192, tt_L2=float(t.mean()), nomem_L2=float(b.mean()), lo=lo(t - b))
        tr_ok = rep["TRANSFER"]["lo"] > 0
    rep["TRANSFER_pass"] = tr_ok

    # TRANSPLANT
    tp = {}
    for a in sorted({r["arm"] for r in C2}):
        car = per_inst(C2, a, 192, 0.0, lambda r: (r["tc_ok_L1"] + r["tc_ok_L2"]) / max(r["tc_n_L1"] + r["tc_n_L2"], 1))
        fre = per_inst(C2, a, 192, 0.0, lambda r: (r["tf_ok_L1"] + r["tf_ok_L2"]) / max(r["tf_n_L1"] + r["tf_n_L2"], 1))
        x, y = paired(car, fre)
        if len(x):
            tp[a] = dict(carried=float(x.mean()), fresh=float(y.mean()), lo=lo(x - y))
    rep["TRANSPLANT"] = tp
    tp_ok = bool(best192) and best192 in tp and tp[best192]["lo"] > 0
    rep["TRANSPLANT_pass"] = tp_ok

    # secondary: kappa sensitivity
    E4 = eff_table(C4)
    rep["kappa_sensitivity"] = {str(km): gate_G(E4, GATED, km)[1] for km in (0.0, 4.0)}

    if not controls:
        v = "INDETERMINATE (controls)"
    elif not g_ok:
        v = "B"
    elif not tr_ok:
        v = "B (no transfer)"
    elif tp_ok:
        v = "A"
    else:
        v = "A-BOUND"
    rep["VERDICT"] = v
    print(json.dumps(rep, indent=1, default=str))
    with open("ensorain/runs/e1_score.json", "w") as f:
        json.dump(rep, f, indent=1, default=str)


if __name__ == "__main__":
    main()
