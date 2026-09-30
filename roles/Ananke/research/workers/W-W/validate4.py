"""PLAN s6 known answers for H0-H3 (+PCT reference) at the CERTIFICATE level (addendum D6), reusing W-U validate3's
cell construction and truths unchanged: KA1 W-Q rep-1 P256, KA2 disjoint blocks P32/64/128, KA3 W-N rep-0 noiseless
+ flip noise. PASS iff 0 false certificates and the candidate issues the true verdict on every cell where H0 does.
-> out/ka4.json"""
import glob
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import intervals4 as i4  # noqa: E402
import swap_rel2 as s2  # noqa: E402
import validate3 as v3  # noqa: E402  (W-U; path added by intervals4)

ALL = i4.CANDS + ("PCT",)
_CC = {}


def cc(P):
    if P not in _CC:
        _CC[P] = (s2.boot_counts(P), s2.boot_counts(P + 1))
    return _CC[P]


def cert_row(src, plant, q, arm, z, a, s, K, blk=None):
    P = len(a)
    C, C1 = cc(P)
    vv = i4.verdicts(a[None, :], s[None, :], C, C1, K, cands=ALL)
    return {"src": src, "plant": plant, "q": q, "arm": arm, "z_true": float(z), "P": P, "blk": blk, "K": K,
            "cert": {c: str(vv[c][0]) for c in ALL}}


def rep1(blocks):
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
                z = v3.FIXED_Z.get((plant, k), 1 - 2 * f0[k])
                a, s, K = v3.pairs(n, arr[f"q{q:.2f}_{k}"])
                for P in blocks:
                    for b in range(len(a) // P):
                        sl = slice(b * P, (b + 1) * P)
                        out.append(cert_row("rep1", plant, q, k, z, a[sl], s[sl], K, blk=b))
    return out


def rep0():
    zf = np.load(HERE.parent / "W-N" / "out" / "p1s_noiseless_r0.npz")
    n0, y, sc = zf["n0"], zf["y"], zf["scored"]
    kinds = ["S1", "S", "S0", "S1_half", "S1_3q"]
    base = {}
    for k in kinds:
        s, _ = v3.readout_noise(zf[f"s0_{k}"], y, sc, 0.0, None, mask=np.zeros(n0.shape, bool))
        base[k] = 1 - np.nanmean(s)
    out = []
    for q in (0.0, 0.1, 0.2, 0.3, 0.4):
        g = np.random.default_rng([5, int(round(q * 100))])
        nrm, m = v3.readout_noise(n0, y, sc, q, g)
        for k in kinds:
            s, _ = v3.readout_noise(zf[f"s0_{k}"], y, sc, q, g, mask=m)
            z = v3.FIXED_Z.get(("P1S", k), 1 - 2 * base[k])
            a, ss, K = v3.pairs(nrm, s)
            out.append(cert_row("rep0nl", "P1S", q, k, z, a, ss, K))
    return out


def check(rows, c, truth=None):
    fc, hit, h0hit, lost = 0, 0, 0, []
    for r in rows:
        z = r["z_true"] if truth is None else truth(r)
        reg = v3.region(z)
        v = r["cert"][c]
        if v in ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL") and v != reg:
            fc += 1
        if v3.exact(z) and v == reg:
            hit += 1
        if v3.exact(z) and r["cert"]["H0"] == reg:
            h0hit += 1
            if v != reg:
                lost.append((r["src"], r["plant"], r["q"], r["arm"], r["P"], r["blk"], v))
    return {"cells": len(rows), "false_certificates": fc, "exact_true_issued": hit, "H0_exact_true_issued": h0hit,
            "lost_vs_H0": len(lost), "lost_list": lost[:6]}


if __name__ == "__main__":
    sets = {"KA1_P256": rep1((256,))}
    ka2 = rep1((32, 64, 128))
    for P in (32, 64, 128):
        sets[f"KA2_P{P}"] = [r for r in ka2 if r["P"] == P]
    sets["KA3_rep0nl"] = rep0()
    R = {}
    for name, rows in sets.items():
        R[name] = {c: check(rows, c) for c in ALL}
    sw = lambda r: -1.0 if r["z_true"] > 0.5 else (1.0 if r["z_true"] < -0.5 else r["z_true"])  # noqa: E731
    R["M3_KA1_swapped_truth_mustfail"] = {c: check(sets["KA1_P256"], c, truth=sw) for c in ALL}
    passes = {}
    for c in i4.CANDS:
        ok = all(R[k][c]["false_certificates"] == 0 and R[k][c]["lost_vs_H0"] == 0
                 for k in ("KA1_P256", "KA2_P32", "KA2_P64", "KA2_P128", "KA3_rep0nl"))
        passes[c] = ok
    R["KA_PASS"] = passes
    for k, v in R.items():
        print(k, json.dumps(v))
    json.dump(R, open(HERE / "out" / "ka4.json", "w"), indent=1)
