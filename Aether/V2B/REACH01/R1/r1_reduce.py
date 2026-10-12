"""REACH01 R1 reducer: held-out decodability of the planted value, by radius and tick; R1 decision.

Decoder (frozen): for each (tick, radius), the feature of (seed, origin, branch j) is its 4 x 256 ring histogram,
mean-centred over the 8 branches of that (seed, origin) -- label-free. Leave-one-seed-out: centroids per label j
from all OTHER seeds' origins; each held-out (origin, branch) is assigned the nearest centroid (squared Euclidean;
ties -> the lowest label, which scores chance on information-free inputs). Accuracy per held-out seed. Chance
0.125. Null: the same with training labels permuted independently per training origin.

Per seed: Dstat = mean over radius in {2..6} and every tick of (accuracy - 0.125): decodability at radius >= 2.
          D1 = the same at radius 1 (transport).
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

REDUCER_VERSION = "r1_reduce.v1"


def load_law(d, law):
    units = []
    for p in sorted(glob.glob(os.path.join(d, "%s_s*.json" % law))):
        m = json.load(open(p))
        if m.get("schema") != "aether.reach01.r1.unit.v1":
            continue
        z = np.load(os.path.join(d, m["features_npz"]))
        units.append((m["seed_index"], m, z["H"], z["D"]))
    return units


def decode(units, rng_seed=12345, null=False):
    """Returns acc[seed][t, r] (held-out) for a list of (seed, meta, H, D)."""
    rng = np.random.default_rng(rng_seed)
    seeds = [u[0] for u in units]
    T, Rr = units[0][2].shape[2], units[0][2].shape[3]
    acc = {s: np.zeros((T, Rr)) for s in seeds}
    for ti in range(T):
        for ri in range(Rr):
            X = {}
            for s, _m, H, _D in units:
                f = H[:, :, ti, ri].reshape(8, H.shape[1], -1).astype(np.float32)   # (8, O, 1024)
                X[s] = f - f.mean(axis=0, keepdims=True)
            for s in seeds:
                train = [X[q] for q in seeds if q != s]
                if not train:
                    continue
                tr = np.concatenate(train, axis=1)                                 # (8, O', 1024)
                if null:
                    perm = np.argsort(rng.random((tr.shape[1], 8)), axis=1)        # per-origin label shuffle
                    tr = np.stack([tr[perm[:, j], np.arange(tr.shape[1])] for j in range(8)])
                cent = tr.mean(axis=1)                                             # (8, 1024)
                te = X[s]                                                          # (8, O, 1024)
                d = ((te[:, :, None, :] - cent[None, None, :, :]) ** 2).sum(-1)    # (8, O, 8)
                pred = d.argmin(-1)
                acc[s][ti, ri] = float((pred == np.arange(8)[:, None]).mean())
    return acc


def stats(acc):
    out = {}
    for s, a in acc.items():
        out[s] = {"D1": float((a[:, 0] - 0.125).mean()), "Dstat": float((a[:, 1:] - 0.125).mean()),
                  "acc": a.round(4).tolist()}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--laws", default="RX,X,R,V1")
    ap.add_argument("--rules")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res = {"schema": "aether.reach01.r1.reduction.v1", "reducer": REDUCER_VERSION, "laws": {}}
    for law in a.laws.split(","):
        units = load_law(a.unit_dir, law)
        if len(units) < 2:
            continue
        res["laws"][law] = {"decode": stats(decode(units)), "null": stats(decode(units, null=True)),
                            "divergence_mean_by_r": np.mean([u[3].mean(axis=(0, 1, 2)) for u in units], axis=0).round(4).tolist()}
        st = res["laws"][law]
        print(law, "Dstat", [round(v["Dstat"], 3) for v in st["decode"].values()],
              "D1", [round(v["D1"], 3) for v in st["decode"].values()],
              "null Dstat", [round(v["Dstat"], 3) for v in st["null"].values()], "div_by_r", st["divergence_mean_by_r"])
    if a.rules and "RX" in res["laws"] and "X" in res["laws"]:
        Rl = json.load(open(a.rules))
        dx = res["laws"]["X"]["decode"]
        drx = res["laws"]["RX"]["decode"]
        nul = res["laws"]["RX"]["null"]
        common = sorted(set(dx) & set(drx))
        wins = [s for s in common if drx[s]["Dstat"] > dx[s]["Dstat"] + Rl["margin"]
                and drx[s]["Dstat"] > nul[s]["Dstat"] + Rl["margin"]]
        res["decision_decodability"] = {"seeds": len(common), "seeds_RX_beats_X_and_null": len(wins),
                                        "reach": len(wins) >= Rl["seeds_min"]}
        print(json.dumps(res["decision_decodability"]))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
