"""PLAN s8 known-answer checks KA1-KA3 + must-fail M3 for REL3. Writes out/ka_plants.json.
KA1 W-Q rep-1 engine arrays (P=256); KA2 disjoint pair blocks P in {32,64,128}; KA3 W-N rep-0 noiseless
P1S + post-hoc flip noise with an arm-shared mask (readout_noise copied from W-N plants_rel, unchanged logic)."""
import glob
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import swap_rel3 as r3  # noqa: E402

TAB = r3.load_table()
DZ = TAB["designs"]
FIXED_Z = {("P1S", "S1"): -1.0, ("P1S", "S"): -1.0, ("P1S", "S0"): 1.0,
           ("P1SK", "S"): 0.0, ("P1SK", "Kp"): 0.0, ("P1SK", "site_all"): -1.0}
NOT_RUN = -(2 ** 40)


def readout_noise(s0, y, scored, q, gen, mask=None):   # W-N plants_rel.readout_noise, mode 'flip'
    if mask is None:
        mask = gen.random(s0.shape) < q
    v = s0.copy()
    run = v != NOT_RUN
    v = np.where(mask & run, -v, v)
    p = np.where(v == 0, 0.5, (np.sign(v) == y).astype(float))
    return np.where(run & scored, p, np.nan), mask


def region(z):
    return "FLIP_REL" if z < -0.5 else ("NO_EFFECT_REL" if z > 0.5 else "CHANCE_REL")


def exact(z):
    return min(abs(z - t) for t in (-1.0, 0.0, 1.0)) <= 0.05


def row(src, plant, q, arm, z, a, s, K, P=None, blk=None, method=r3.METHOD, floor=None):
    P = len(a)
    r = r3.from_pairs(a, s, K, dz=DZ[f"P{P}_K{K}"], method=method, floor=floor)
    return {"src": src, "plant": plant, "q": q, "arm": arm, "z_true": float(z), "P": P, "blk": blk,
            "normal": r["normal"], "cert": r["certificate"], "label": r["label"], "strict": r["strict"],
            "attain": r["attain"], "zci": r["zci"]}


def pairs(n, sw):
    both = ~np.isnan(n) & ~np.isnan(sw)
    a = r3.pair_means(np.where(both, n, np.nan))
    s = r3.pair_means(np.where(both, sw, np.nan))
    K = int(round(both.sum() / (2 * len(a))))
    return a, s, K


def rep1(blocks=(256,), method=r3.METHOD):
    out = []
    for plant in ("P1S", "P1SK"):
        arr = {}
        for f in sorted(glob.glob(str(HERE.parent / "W-Q" / "out" / f"plants_r1_{plant}_*.npz"))):
            d = np.load(f)
            arr.update({k: d[k] for k in d.files})
        qs = sorted({float(k.split("_")[0][1:]) for k in arr})
        kinds = sorted({k.split("_", 1)[1] for k in arr} - {"normal"})
        f0 = {k: 1 - np.nanmean(arr[f"q0.00_{k}"]) for k in kinds}
        for q in qs:
            n = arr[f"q{q:.2f}_normal"]
            for k in kinds:
                z = FIXED_Z.get((plant, k), 1 - 2 * f0[k])
                a, s, K = pairs(n, arr[f"q{q:.2f}_{k}"])
                for P in blocks:
                    for b in range(len(a) // P):
                        sl = slice(b * P, (b + 1) * P)
                        out.append(row("rep1", plant, q, k, z, a[sl], s[sl], K, blk=b, method=method))
    return out


def rep0_noiseless(qs=(0.0, 0.1, 0.2, 0.3, 0.4)):
    zf = np.load(HERE.parent / "W-N" / "out" / "p1s_noiseless_r0.npz")
    n0, y, sc = zf["n0"], zf["y"], zf["scored"]
    kinds = ["S1", "S", "S0", "S1_half", "S1_3q"]
    out = []
    base = {}
    for k in kinds:
        s, _ = readout_noise(zf[f"s0_{k}"], y, sc, 0.0, None, mask=np.zeros(n0.shape, bool))
        base[k] = 1 - np.nanmean(s)
    for q in qs:
        g = np.random.default_rng([5, int(round(q * 100))])
        nrm, m = readout_noise(n0, y, sc, q, g)
        for k in kinds:
            s, _ = readout_noise(zf[f"s0_{k}"], y, sc, q, g, mask=m)
            z = FIXED_Z.get(("P1S", k), 1 - 2 * base[k])
            a, ss, K = pairs(nrm, s)
            out.append(row("rep0nl", "P1S", q, k, z, a, ss, K))
    return out


def checks(rows, key="label", truth=None):
    fc, hit, miss = [], [], []
    for r in rows:
        z = r["z_true"] if truth is None else truth(r)
        v = r[key]
        if v in r3.CERTS and v != region(z):
            fc.append(r)
        if exact(z) and r["attain"][region(z)]:
            (hit if v == region(z) else miss).append(r)
    na = len(hit) + len(miss)
    return {"cells": len(rows), "false_certificates": len(fc), "fc_rate": len(fc) / max(1, len(rows)),
            "attainable_exact": na, "issued": len(hit), "recovery": len(hit) / na if na else None,
            "false_list": [(r["src"], r["plant"], r["q"], r["arm"], r["P"], r["blk"], r[key]) for r in fc][:10],
            "miss_list": [(r["src"], r["plant"], r["q"], r["arm"], r["P"], r["blk"], r[key]) for r in miss][:10]}


if __name__ == "__main__":
    R = {}
    ka1 = rep1()
    R["KA1_rep1_P256"] = checks(ka1)
    R["KA1_rep1_P256_strict"] = checks(ka1, "strict")
    sw = lambda r: -1.0 if r["z_true"] > 0.5 else (1.0 if r["z_true"] < -0.5 else r["z_true"])  # noqa: E731
    R["M3_swapped_truth_mustfail"] = checks(ka1, truth=sw)
    ka2 = rep1(blocks=(32, 64, 128))
    for P in (32, 64, 128):
        R[f"KA2_blocks_P{P}"] = checks([r for r in ka2 if r["P"] == P])
    ka2p = rep1(blocks=(32, 64), method="PCT")
    for P in (32, 64):
        R[f"KA2_blocks_P{P}_PCT_reference"] = checks([r for r in ka2p if r["P"] == P], "cert")
    ka3 = rep0_noiseless()
    R["KA3_rep0_noiseless_flipnoise"] = checks(ka3)
    R["KA3_rep0_noiseless_flipnoise_strict"] = checks(ka3, "strict")
    for k, v in R.items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ("false_list", "miss_list")},
              "FALSE:", v["false_list"][:4], "MISS:", v["miss_list"][:4])
    flips = [r for r in ka1 + ka3 if r["label"] == "FLIP_REL"]
    print("\nFLIP_REL z CI (P=256 cells):")
    for r in flips:
        print(f"  {r['src']} {r['plant']} q={r['q']:.2f} {r['arm']:8s} zt={r['z_true']:+.2f} "
              f"z={r['zci']['z']:+.3f} [{r['zci']['lo']:+.3f},{r['zci']['hi']:+.3f}] {r['zci']['class']}")
    for r in ka1 + ka3:
        print(f"{r['src']} {r['plant']:4s} q={r['q']:.2f} {r['arm']:8s} zt={r['z_true']:+.2f} n={r['normal'][0]:.3f}"
              f"[{r['normal'][1]:.3f}] cert={r['cert']:13s} REL3={r['label']:13s} strict={r['strict']}")
    json.dump({"checks": R, "rows_P256": ka1 + ka3}, open(HERE / "out" / "ka_plants.json", "w"), indent=1, default=str)
