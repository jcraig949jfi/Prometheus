"""Frozen E2 scorer (PREREG_E2 s7). Committed before any confirmatory row.
python -m ensorain.e2.score"""
import collections
import json

import numpy as np

STRUCT = ("TT", "MAT", "CP")
BLIND = ("BLIND1", "RANDPERM", "OUTER")
SIMPLE = ("EXHAUSTIVE", "GREEDY", "MI", "LRSEL")
RNG = np.random.default_rng(22222222)
BOOT = 10_000


def lo(d):
    d = np.asarray(d)
    if len(d) == 0:
        return float("nan")
    return float(np.quantile(d[RNG.integers(len(d), size=(BOOT, len(d)))].mean(1), 0.025))


def paired(a, b):
    ks = sorted(set(a) & set(b))
    return np.array([a[k] for k in ks]), np.array([b[k] for k in ks])


def main():
    try:
        rows = [json.loads(l) for l in open("ensorain/runs/e2_confirm.jsonl")]
    except FileNotFoundError:
        rows = []
    rows = [r for r in rows if r.get("status") == "OK"]
    nom = {(r["set"], r["family"], r["inst_seed"], r["org_seed"]): r["U"] for r in rows if r["arm"] == "NOMEM"}
    E = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        k = (r["set"], r["family"], r["inst_seed"], r["org_seed"])
        if r["arm"] != "NOMEM" and k in nom:
            E[(r["set"], r["family"], r["arm"])][r["inst_seed"]].append((r["U"] - nom[k]) / max(r["P_used"], 1))
    E = {k: {i: float(np.mean(v)) for i, v in d.items()} for k, d in E.items()}

    def sel(**f):
        return [r for r in rows if all(r[k] == v for k, v in f.items())]

    def rate(v, key="correct"):
        return float(np.mean([bool(r[key]) for r in v])) if v else float("nan")

    rep = {}
    print("set fam  arm         correct  EFF     U      r2ho   L2    discMu")
    for s in ("A", "B"):
        for fam in ("TT", "MAT", "CP", "NONE"):
            for a in ("NOMEM", "ORACLE_H", "BLIND1", "RANDPERM", "OUTER", "EXHAUSTIVE", "GREEDY", "MI", "LRSEL", "SD"):
                v = sel(set=s, family=fam, arm=a)
                if not v:
                    continue
                e = E.get((s, fam, a), {})
                print("%s %-4s %-10s %6.2f %7.3f %6.0f %6.2f %5.2f %6.2f" % (
                    s, fam, a, rate(v), np.mean(list(e.values())) if e else float("nan"), np.mean([r["U"] for r in v]),
                    np.nanmedian([r["r2_ho"] for r in v]), np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in v]),
                    np.mean([r["disc_units"] for r in v]) / 1e6))
    # what SD committed to, per family (confusion)
    conf = collections.defaultdict(collections.Counter)
    for r in sel(arm="SD"):
        conf[r["family"]][r["h"].split("|")[0]] += 1
    rep["SD_committed_family_counts"] = {k: dict(v) for k, v in conf.items()}
    # SD "increasingly useful" trace: median validation MSE by halving round
    tr = collections.defaultdict(list)
    for r in sel(arm="SD"):
        for k, t in enumerate(r.get("trace") or []):
            tr[(r["family"], k)].append(t["best"])
    rep["SD_trace_median_val_mse"] = {f"{f}@round{k}": round(float(np.median(v)), 4) for (f, k), v in sorted(tr.items())}

    # controls
    c = {}
    pc_ok = True
    for s in ("A", "B"):
        for fam in STRUCT:
            m = float(np.nanmedian([r["r2_ho"] for r in sel(set=s, family=fam, arm="ORACLE_H")] or [np.nan]))
            c[f"PC_{s}_{fam}"] = round(m, 3)
            pc_ok &= m >= 0.5
    c["PC_pass"] = pc_ok
    neg, neg_ok = {}, True
    for s in ("A", "B"):
        base = np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in sel(set=s, family="NONE", arm="NOMEM")] or [np.nan])
        for a in {r["arm"] for r in rows} - {"NOMEM"}:
            v = sel(set=s, family="NONE", arm=a)
            if v:
                d = float(np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in v]) - base)
                neg[f"{s}_{a}"] = round(d, 4)
                neg_ok &= d <= 0.05
    c["NEG"] = neg
    c["NEG_pass"] = neg_ok
    from ensorain.e1.world import World1
    from ensorain.e1.arms import make
    from ensorain.e1.life import live
    from ensorain.e1 import mem as M1
    try:
        w = World1(0, 40000)
        live(w, make("SMUGGLER", 192, w, 0, dict(lam=30, sweeps=2)), w.events())
        c["CHT_smuggler_refused"] = False
    except M1.AuditError:
        c["CHT_smuggler_refused"] = True
    b = [r for r in rows if r["arm"] == "BLIND1" and r["family"] in STRUCT]
    p = 1 / 17
    se = float(np.sqrt(p * (1 - p) / max(len(b), 1)))
    c["CHT_blind_correct"] = round(rate(b), 4)
    c["CHT_blind_band"] = [round(p - 2 * se, 4), round(p + 2 * se, 4)]
    c["CHT_pass"] = c["CHT_smuggler_refused"] and bool(b) and abs(rate(b) - p) <= 2 * se
    controls = c["PC_pass"] and c["NEG_pass"] and c["CHT_pass"]
    rep["controls"] = c
    rep["controls_pass"] = controls

    # G_ID
    gid, gid_ok = {}, True
    for s in ("A", "B"):
        for fam in STRUCT:
            v = rate(sel(set=s, family=fam, arm="SD"))
            gid[f"{s}_{fam}"] = round(v, 3)
            gid_ok &= v >= 0.70
        v = rate(sel(set=s, family="NONE", arm="SD"))
        gid[f"{s}_NONE"] = round(v, 3)
        gid_ok &= v >= 0.50
    rep["G_ID"] = gid
    rep["G_ID_pass"] = bool(gid_ok)

    # G_EFF and qualifier
    geff, geff_ok = {}, True
    qual = collections.Counter()
    for s in ("A", "B"):
        for fam in STRUCT:
            sd = E.get((s, fam, "SD"), {})
            bl = {a: E.get((s, fam, a), {}) for a in BLIND}
            bstar = max(bl, key=lambda a: np.mean(list(bl[a].values())) if bl[a] else -1e18)
            x, y = paired(sd, bl[bstar])
            ok = bool(len(x)) and x.mean() >= 1.10 * y.mean() and lo(x - 1.10 * y) > 0
            geff[f"{s}_{fam}"] = dict(sd=round(float(x.mean()), 3) if len(x) else None, best_blind=bstar,
                                      blind=round(float(y.mean()), 3) if len(y) else None,
                                      lo=round(lo(x - 1.10 * y), 3) if len(x) else None, pass_=ok)
            geff_ok &= ok
            sm = {a: E.get((s, fam, a), {}) for a in SIMPLE}
            sstar = max(sm, key=lambda a: np.mean(list(sm[a].values())) if sm[a] else -1e18)
            x2, y2 = paired(sd, sm[sstar])
            beat = bool(len(x2)) and x2.mean() >= 1.10 * y2.mean() and lo(x2 - 1.10 * y2) > 0
            geff[f"{s}_{fam}"]["best_simple"] = sstar
            geff[f"{s}_{fam}"]["simple"] = round(float(y2.mean()), 3) if len(y2) else None
            geff[f"{s}_{fam}"]["sd_beats_simple"] = beat
            qual[s] += int(beat)
    rep["G_EFF"] = geff
    rep["G_EFF_pass"] = bool(geff_ok)
    special = all(qual[s] >= 2 for s in ("A", "B"))
    rep["QUALIFIER"] = "SPECIAL" if special else "TEXTBOOK"

    if not controls:
        v = "INDETERMINATE (controls)"
    elif gid_ok and geff_ok:
        v = "DISCOVERY DEMONSTRATED (" + rep["QUALIFIER"] + ")"
    else:
        fails = [n for n, ok in (("G_ID", gid_ok), ("G_EFF", geff_ok)) if not ok]
        v = "CLOSE (B): failed " + ", ".join(fails)
    rep["VERDICT"] = v
    print(json.dumps(rep, indent=1, default=str))
    json.dump(rep, open("ensorain/runs/e2_score.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
