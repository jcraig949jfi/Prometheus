"""Aggregate champion truth tables -> out/summary_<cell>.json + printed table.
python analyze.py <cell> [main|verify]"""
import json, sys, glob
import numpy as np
import common
import ana, tt
from collections import Counter

name = sys.argv[1]
OUT = common.HERE / "out"


def load_main():
    files = sorted(glob.glob(str(OUT / f"tt_{name}_main_k*.npz")))
    d = []
    for f in files:
        x = dict(np.load(f))
        x["k"] = int(f.split("_k")[-1].split(".")[0])
        d.append(x)
    return d


def main():
    ds = load_main()
    names = [str(x) for x in ds[0]["names"]]
    ph, env, g, _ = common.load(name)
    comps = tt.coarse_components(ph)
    site_mask = [tt.is_site(comps[k]) for k in names]
    half = [tuple(z) for z in ds[0]["subs"]]
    n = len(names)
    offs = list(ds[0]["offsets"])
    res = {"cell": name, "names": names, "trials": [d["k"] for d in ds], "offsets": {}}
    allrecs = {}
    for o in offs:
        tabs = []
        for d in ds:
            y = d["y"]
            tabs.append((ana.full_a(d[f"o{o}"], half, n), y[0::2], y[1::2]))
        recs = ana.analyse(tabs, names, site_mask)
        for r in recs:
            r["k"] = int(ds[r["trial"]]["k"])
        s = ana.summarize(recs, names, P=128)
        # S and C pair-trials: which single component carries them (dictator)?
        for q in ("S", "C"):
            rq = [r for r in recs if r["pat"] == q and r.get("full")]
            s[f"{q}_cls"] = {k: v / max(1, len(rq)) for k, v in Counter(r["cls"] for r in rq).items()}
            s[f"{q}_R_top"] = [(list(k), v / max(1, len(rq))) for k, v in Counter(r["R"] for r in rq).most_common(3)]
        # N split by AND/OR orientation vs the sign of y_A
        rn = [r for r in recs if r["pat"] == "N" and r.get("full")]
        s["N_cls_by_yA"] = {str(ya): dict(Counter(r["cls"] for r in rn if r["yA"] == ya)) for ya in (-1, 1)}
        for par in (0, 1):     # sync phase: parity of the swap tick t0+o (4781b0a1 update_period 2)
            rp = [r for r in recs if (int(ds[r["trial"]]["k"]) * env.period() + int(o)) % 2 == par]
            if rp:
                sp = ana.summarize(rp, names, P=128, n_boot=200)
                s[f"parity{par}"] = {k: sp.get(k) for k in ("eligible", "fS", "fC", "fN", "base_N", "class", "polarity", "d_plus", "fn_top")}
        res["offsets"][int(o)] = s
        allrecs[int(o)] = recs
        print(f"o{o:>2} el={s['eligible']} fS={s['fS']:.2f} fC={s['fC']:.2f} fN={s['fN']:.2f} [{s.get('fN_ci99', (0, 0))[0]:.2f},{s.get('fN_ci99', (0, 0))[1]:.2f}] "
              f"tie={s['ftie']:.2f} baseN={s['base_N']} {s['class']} {s.get('polarity')} "
              f"j2={s.get('pt', {}).get('joint2', 0):.2f}{tuple(round(x, 2) for x in s.get('ci99', {}).get('joint2') or ())} "
              f"top2={s.get('top2')} cls={ {k: round(v, 2) for k, v in s.get('cls', {}).items()} } "
              f"md={[(m, round(v, 2)) for m, v in s.get('md_top', [])[:2]]} d+={s.get('d_plus', 0):.2f}", flush=True)
        print("     fn_top", [(R, fn, round(v, 2)) for R, fn, v in s.get("fn_top", [])[:3]],
              " | par0", {k: s.get("parity0", {}).get(k) for k in ("base_N", "fN", "class")},
              " par1", {k: s.get("parity1", {}).get(k) for k in ("base_N", "fN", "class")}, flush=True)
    json.dump(res, open(OUT / f"summary_{name}.json", "w"), indent=1, default=str)
    import pickle
    pickle.dump(allrecs, open(OUT / f"recs_{name}.pkl", "wb"))


def verify():
    f = sorted(glob.glob(str(OUT / f"tt_{name}_verify_k*.npz")))[0]
    d = np.load(f)
    names = list(d["names"])
    subs = [tuple(z) for z in d["subs"]]
    n = len(names)
    y = d["y"]
    yA, yB = y[0::2], y[1::2]
    out = {}
    for o in d["offsets"]:
        s0 = d[f"o{o}"]
        ident = ana.identity_rate(s0, subs)
        a = np.sign(s0[:, 0::2])
        fz, elig = ana.f_table(a, yA, yB)
        Rs = []
        for p in np.flatnonzero(elig):
            if (fz[:, p] >= 0).all():
                Rs.append(tuple(names[i] for i in ana.relevant(fz[:, p], n)))
        wR = sum("w" in R for R in Rs)
        dd, el2 = ana.direct_decisive(s0, np.array(subs), yA, yB)
        nod = sum(x is None for x, e in zip(dd, el2) if e)
        out[int(o)] = {"identity": ident, "eligible": int(elig.sum()), "full": len(Rs), "w_in_R": wR,
                       "no_decisive_direct": nod}
        print(f"verify o{o:>2} identity={ident:.3f} eligible={int(elig.sum())} full={len(Rs)} w_in_R={wR} "
              f"no_decisive(direct)={nod}", flush=True)
    json.dump({"file": f, "names": names, "offsets": out}, open(OUT / f"verify_{name}.json", "w"), indent=1)


if __name__ == "__main__":
    (verify if len(sys.argv) > 2 and sys.argv[2] == "verify" else main)()
