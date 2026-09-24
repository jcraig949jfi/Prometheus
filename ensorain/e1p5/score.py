"""Frozen E1.5 scorer (PREREG_E1P5 s5). Committed before any confirmatory
row. python -m ensorain.e1p5.score"""
import collections
import json

import numpy as np

from ensorain.e1.world import World1, NV, D
from ensorain.e1.mem import PARTITIONS
from .core import CAPS

NON_TT = ("LRU", "KNN", "CP", "LOWRANK", "MLP")
RNG = np.random.default_rng(15151515)
BOOT = 10_000


def lo(d):
    d = np.asarray(d)
    if len(d) == 0:
        return float("nan")
    return float(np.quantile(d[RNG.integers(len(d), size=(BOOT, len(d)))].mean(1), 0.025))


def paired(a, b):
    ks = sorted(set(a) & set(b))
    return np.array([a[k] for k in ks]), np.array([b[k] for k in ks])


def load():
    try:
        return [json.loads(l) for l in open("ensorain/runs/e1p5_confirm.jsonl")]
    except FileNotFoundError:
        return []


def eff(rows):
    nom = {(r["set"], r["cap"], r["lam"], r["inst_seed"], r["org_seed"]): r["U"] for r in rows if r["arm"] == "NOMEM"}
    t = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        k = (r["set"], r["cap"], r["lam"], r["inst_seed"], r["org_seed"])
        if r["arm"] == "NOMEM" or k not in nom:
            continue
        t[(r["set"], r["arm"], r["cap"], r["lam"])][r["inst_seed"]].append((r["U"] - nom[k]) / max(r["P_used"], 1))
    return {k: {i: float(np.mean(v)) for i, v in d.items()} for k, d in t.items()}


def inst_mean(rows, f, **flt):
    d = collections.defaultdict(list)
    for r in rows:
        if all(r.get(k) == v for k, v in flt.items()):
            x = f(r)
            if x is not None:
                d[r["inst_seed"]].append(x)
    return {i: float(np.mean(v)) for i, v in d.items()}


def lowrank_ceiling(inst, k):
    w = World1(0, inst)
    best = -np.inf
    ho = w.heldout_cell.reshape([NV] * D)
    for (r0, r1), (c0, c1) in PARTITIONS:
        t = np.transpose(w.x, (r0, r1, c0, c1)).reshape(64, 64)
        h = np.transpose(ho, (r0, r1, c0, c1)).reshape(64, 64)
        U, s, Vt = np.linalg.svd(t, full_matrices=False)
        a = (U[:, :k] * s[:k]) @ Vt[:k]
        y = t[h]
        best = max(best, float(1 - ((y - a[h]) ** 2).sum() / ((y - y.mean()) ** 2).sum()))
    return best


def main():
    rows = [r for r in load() if r.get("status") == "OK"]
    C = [r for r in rows if r["lam"] == 0.0]
    E = eff(rows)
    rep = {}
    # ---- sweep table
    print("set cap  arm         EFF      U     r2ho   L2    learnKunits  P    eff_ranks")
    for s in ("A", "B"):
        for c in CAPS:
            for a in ("LRU", "KNN", "CP", "LOWRANK", "MLP", "TT_TUNED", "TT_LATENT"):
                v = [r for r in C if r["set"] == s and r["cap"] == c and r["arm"] == a]
                if not v:
                    continue
                e = E.get((s, a, c, 0.0), {})
                er = [tuple(r["ranks_effective"]) for r in v if "ranks_effective" in r]
                mode = collections.Counter(er).most_common(1)[0][0] if er else ""
                print("%s %4d %-10s %7.3f %6.0f %6.2f %5.2f %10.0f %4.0f  %s" % (
                    s, c, a, np.mean(list(e.values())) if e else float("nan"), np.mean([r["U"] for r in v]),
                    np.median([r["r2_ho"] for r in v]), np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in v]),
                    np.mean([r.get("comp_learn", r["comp_units"]) for r in v]) / 1e3, np.mean([r["P_used"] for r in v]), mode))
    # ---- PC
    pc = {}
    for s in ("A", "B"):
        v = [r for r in C if r["set"] == s and r["cap"] == 384 and r["arm"] == "TT_LATENT"]
        pc[s] = dict(r2=float(np.median([r["r2_ho"] for r in v])) if v else float("nan"),
                     L2=float(np.median([r["ok_L2"] / max(r["n_L2"], 1) for r in v])) if v else float("nan"))
        pc[s]["pass_"] = bool(v) and pc[s]["r2"] >= 0.5 and pc[s]["L2"] >= 0.5
    rep["PC"] = pc
    pc_ok = all(pc[s]["pass_"] for s in pc)
    rep["PC_pass"] = pc_ok
    # ---- T
    cap_pass = {}
    detail = {}
    for s in ("A", "B"):
        for c in CAPS:
            tt = E.get((s, "TT_TUNED", c, 0.0), {})
            ok = bool(tt)
            d = {}
            for x in NON_TT:
                ex = E.get((s, x, c, 0.0), {})
                if not ex:
                    continue
                t, b = paired(tt, ex)
                l = lo(t - 1.10 * b)
                p = bool(t.mean() >= 1.10 * b.mean() and l > 0)
                d[x] = dict(tt=round(float(t.mean()), 3), x=round(float(b.mean()), 3), lo=round(l, 3), pass_=p)
                ok &= p
            cap_pass[(s, c)] = ok
            detail[f"{s}@{c}"] = d
    rep["T_detail"] = detail
    both = [c for c in CAPS if cap_pass.get(("A", c)) and cap_pass.get(("B", c))]
    t_pairs = [(CAPS[i], CAPS[i + 1]) for i in range(len(CAPS) - 1) if CAPS[i] in both and CAPS[i + 1] in both]
    t_caps = sorted({c for p in t_pairs for c in p})
    rep["T_caps_passing_both_sets"] = both
    rep["T_adjacent_pairs"] = t_pairs
    t_ok = bool(t_pairs)
    rep["T_pass"] = t_ok
    # ---- compression curves (reported for every cap) and C1
    curves = {}
    c1_ok = False
    c1_detail = {}
    for a in ("TT_TUNED", "TT_LATENT", "LOWRANK"):
        for c in CAPS:
            v = [r for r in C if r["arm"] == a and r["cap"] == c and r.get("compress_curve")]
            if not v:
                continue
            trained_r2 = float(np.median([r["r2_ho"] for r in v]))
            trained_u = float(np.mean([r["replay_trained"] - r["replay_nomem"] for r in v]))
            pts = {}
            for b in sorted({p["b"] for r in v for p in r["compress_curve"]}, reverse=True):
                ps = [(r, p) for r in v for p in r["compress_curve"] if p["b"] == b]
                pts[b] = dict(r2=round(float(np.median([p["r2_ho"] for _, p in ps])), 3),
                              u=round(float(np.mean([p["replay"] - r["replay_nomem"] for r, p in ps])), 1),
                              size=int(np.median([p["size"] for _, p in ps])))
            curves[f"{a}@{c}"] = dict(trained_r2=round(trained_r2, 3), trained_u=round(trained_u, 1),
                                      P=int(np.median([r["P_used"] for r in v])), points=pts)
    rep["compression_curves"] = curves
    for c in t_caps:
        cur = curves.get(f"TT_TUNED@{c}")
        if not cur:
            continue
        s_c = cur["P"]
        for b, p in cur["points"].items():
            if b > 0.6 * s_c:
                continue
            a_ok = p["r2"] >= 0.9 * cur["trained_r2"] and p["u"] >= 0.9 * cur["trained_u"]
            nat_cap = max([x for x in CAPS if x <= b], default=None)
            comp = inst_mean(C, lambda r: next((q["replay"] - r["replay_nomem"] for q in r.get("compress_curve", []) if q["b"] == b), None),
                             arm="TT_TUNED", cap=c)
            nat = inst_mean(C, lambda r: r["replay_trained"] - r["replay_nomem"], arm="TT_TUNED", cap=nat_cap)
            x, y = paired(comp, nat)
            b_ok = bool(len(x)) and x.mean() >= 1.10 * y.mean() and lo(x - 1.10 * y) > 0
            c1_detail[f"{c}->{b}"] = dict(retention=a_ok, comp_u=float(x.mean()) if len(x) else None,
                                         native_cap=nat_cap, native_u=float(y.mean()) if len(y) else None,
                                         lo=lo(x - 1.10 * y) if len(x) else None, headroom=b_ok)
            c1_ok |= bool(a_ok and b_ok)
    rep["C1_detail"] = c1_detail
    rep["C1_pass"] = c1_ok
    # ---- C2
    c2 = {}
    c2_ok = bool(t_caps)
    insts = sorted({r["inst_seed"] for r in C})
    for c in t_caps:
        k = c // 128
        ceil = float(np.median([lowrank_ceiling(i, k) for i in insts]))
        tt = float(np.median([r["r2_ho"] for r in C if r["arm"] == "TT_TUNED" and r["cap"] == c]))
        c2[c] = dict(tt_r2=tt, lowrank_ceiling=ceil, pass_=tt >= ceil + 0.10)
        c2_ok &= c2[c]["pass_"]
    rep["C2"] = c2
    rep["C2_pass"] = c2_ok
    # ---- negative control (reported)
    R = [r for r in rows if r["lam"] == 1.0]
    rep["NEG_L2_minus_NOMEM_in_R"] = {
        f"{a}@{c}": round(float(np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in R if r["arm"] == a and r["cap"] == c])
                              - np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in R if r["arm"] == "NOMEM" and r["cap"] == c])), 4)
        for a in {r["arm"] for r in R} - {"NOMEM", "ORACLE"} for c in (192, 384)
        if any(r["arm"] == a and r["cap"] == c for r in R)} if R else {}
    fails = [n for n, ok in (("PC", pc_ok), ("T", t_ok), ("C1 or C2", c1_ok or c2_ok)) if not ok]
    if not fails:
        v = "INTRIGUING -- WORTH EXPLORING"
    elif fails == ["PC"]:
        v = "CLOSE (control)"
    else:
        v = "CLOSE (B): failed " + ", ".join(fails)
    rep["VERDICT"] = v
    print(json.dumps(rep, indent=1, default=str))
    json.dump(rep, open("ensorain/runs/e1p5_score.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
