"""World certificates for Tyche v2 (computed before freezing; committed).

Per world (and per regime phase), on calibration seed 0, val+conf+test
region (t >= 3100):
  subset_mi      plug-in MI(Y; precursors in S) for every non-empty subset
                 S, minus the 99th percentile of 20 label permutations
                 (bias-corrected); informative if > 0.005 bits
  lowest_order   smallest |S| with an informative subset (empirical);
                 for table laws also the exact truth-table order
  bank_max       max over a raw feature bank (delays 0..16, window sums
                 w 2..8 at lags 0..12, accumulators mod 2,3 at lags 0..12,
                 every channel) of MI(Y; feature) minus its permutation
                 99th percentile -- a soft single-feature foothold check
  deficit        oracle deficit per organism at eco0 (R0, val) and raw
                 ecology accuracy vs majority
"""

from __future__ import annotations

import itertools
import json
import sys

import numpy as np

from . import worlds_v2 as W2

LO = 3100


def mi(a, y):
    a = np.asarray(a, dtype=np.int64)
    y = np.asarray(y, dtype=np.int64)
    ka = np.unique(a, return_inverse=True)[1]
    ky = np.unique(y, return_inverse=True)[1]
    na, ny = ka.max() + 1, ky.max() + 1
    joint = np.bincount(ka * ny + ky, minlength=na * ny).reshape(na, ny) / len(a)
    pa, py = joint.sum(1, keepdims=True), joint.sum(0, keepdims=True)
    nz = joint > 0
    return float((joint[nz] * np.log2(joint[nz] / (pa @ py)[nz])).sum())


def mi_corrected(a, y, rng, n_perm=20):
    m = mi(a, y)
    null = [mi(a, rng.permutation(y)) for _ in range(n_perm)]
    return m - float(np.percentile(null, 99)), m


def joint_key(cols):
    k = np.zeros(len(cols[0]), dtype=np.int64)
    for c in cols:
        c = np.asarray(c, dtype=np.int64)
        k = k * (int(c.max()) + 1) + c
    return k


def bank(X):
    for ch in range(X.shape[1]):
        x = X[:, ch].astype(np.int64)
        for lag in range(0, 17):
            yield f"d{ch}_{lag}", W2._lag(x, lag)
        c = np.concatenate([[0], np.cumsum(x)])
        for w in range(2, 9):
            s = c[1:] - np.concatenate([np.zeros(w, dtype=np.int64), c[1:-w]])
            for lag in range(0, 13):
                yield f"ws{ch}_{w}_{lag}", W2._lag(s, lag)
        for m in (2, 3):
            a = np.cumsum(x) % m
            for lag in range(0, 13):
                yield f"acc{ch}_{m}_{lag}", W2._lag(a, lag)


def certify_world(spec, seed=0):
    rng = np.random.default_rng(12345)
    X, Y = W2.generate(spec, seed)
    y = Y[LO:]
    out = {"id": spec["id"], "cls": spec["cls"]}
    law = spec["law"]
    if law["comb"] != "prf":
        src = X
        if spec["kind"] == "tsd":  # the precursors of the OBSERVED X carry nothing by design
            src = X
        P = [p[LO:] for p in W2.precursors(law, src)]
        sub = {}
        low = None
        for s in range(1, len(P) + 1):
            for S in itertools.combinations(range(len(P)), s):
                c, raw = mi_corrected(joint_key([P[i] for i in S]), y, rng)
                sub["".join(str(i) for i in S)] = {"mi_bits": round(raw, 5), "above_null": round(c, 5)}
                if c > 0.005 and low is None:
                    low = s
        out["subset_mi"] = sub
        out["lowest_order_empirical"] = low
        if law["comb"] == "table":
            out["lowest_order_exact"] = W2.lowest_informative_order(law["table"])
    best = (None, -1.0)
    for name, f in bank(X):
        c, _ = mi_corrected(f[LO:], y, rng, n_perm=5)
        if c > best[1]:
            best = (name, c)
    out["bank_max"] = {"feature": best[0], "above_null_bits": round(best[1], 5)}
    return out


def main(out_path, master_seed=20261002):
    W = W2.build_static(master_seed, 0) + W2.build_regime(master_seed, 0)
    rows = []
    for spec in W:
        phases = [1, 2] if "law2" in spec else [1]
        for ph in phases:
            s = W2.phase_spec(spec, ph)
            r = certify_world(s)
            rows.append(r)
            print(f"{r['id']:14s} {r['cls']:26s} low={r.get('lowest_order_empirical')} "
                  f"exact={r.get('lowest_order_exact')} bank={r['bank_max']['above_null_bits']:+.4f} "
                  f"({r['bank_max']['feature']})", flush=True)
    json.dump({"master_seed": master_seed, "worlds_hash": W2.worlds_hash(W), "rows": rows},
              open(out_path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
