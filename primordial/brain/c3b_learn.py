"""C3b: the C3 representation ecology LEARNED from samples, scored on unseen cells.

Task: a known function f of 4 hex digits (C3's targets). A learner sees N distinct cells
(x, f(x) + noise), fits a representation, and is scored on EVERY cell it did not see:
    heldout_rel_mse = mean_{x not in train} (pred(x) - f(x))^2 / var(f)
Bytes = C3's serialized blob length; predictions come from C3's bytes decoder only.

Learners (fitted from the training rows only):
  dense      cell means, unseen cells = train mean
  tt[r]      TT with every bond rank r, ALS sweeps on samples (plastic.als_sweep)
  cp[R]      CP, ALS on samples (per factor, per digit value least squares)
  additive   4 tables of 16 (backfitting on samples)
  pairwise   6 tables of 16x16 (backfitting on samples)
  program    C3's exhaustive tiny digit program, scored on training rows
  dense_leak CHEAT: fits the dense table from the FULL clean target (reads unseen cells)

LEAK PROBE: each learner is fitted twice, on the true table and on a copy whose
held-out cells are scrambled (training cells untouched). A learner that reads only
its training rows produces bit-identical bytes -> CLEAN; any difference -> LEAK.

usage: python -m primordial.brain.c3b_learn [--dev] [--seeds 0,1,2]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import itertools
import json
import pathlib
import time

import numpy as np

from primordial.brain import c3_ecology as c3
from primordial.brain import plastic as pl

EXP_ID = "C3b-ecology-from-samples"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
NOISE = 0.3
NS = (128, 512, 2048, 8192, 32768)
PROBE_N = 512
LEARN_MARGIN = 0.05      # "learns" = held-out at least this far below the mean-predictor baseline (posted rule)
RIDGE = 1e-2
GRID = np.indices(c3.SHAPE).reshape(4, -1).T            # (65536, 4) digits of each flat cell


def _unflat(idx):
    return GRID[idx]


def fit_dense(idx, y, _):
    T = np.full(65536, y.mean(), np.float64)
    T[idx] = y                                          # train cells are distinct
    return c3.pack("dense", [T.reshape(c3.SHAPE).astype(np.float32)])


def fit_dense_leak(idx, y, table):
    return c3.pack("dense", [table.astype(np.float32)])  # CHEAT: reads every cell


def fit_additive(idx, y, _, sweeps=20):
    X = _unflat(idx)
    m = y.mean()
    t = [np.zeros(16) for _ in range(4)]
    for _ in range(sweeps):
        for k in range(4):
            res = y - m - sum(t[l][X[:, l]] for l in range(4) if l != k)
            s = np.bincount(X[:, k], res, 16)
            c = np.bincount(X[:, k], minlength=16)
            t[k] = np.where(c > 0, s / np.maximum(c, 1), 0.0)
    return c3.pack("additive", [np.array([m], np.float32)] + [x.astype(np.float32) for x in t])


def fit_pairwise(idx, y, _, sweeps=20):
    X = _unflat(idx)
    m = y.mean()
    pairs = list(itertools.combinations(range(4), 2))
    P = [np.zeros((16, 16)) for _ in pairs]
    cell = [X[:, k] * 16 + X[:, l] for k, l in pairs]
    for _ in range(sweeps):
        for i in range(len(pairs)):
            res = y - m - sum(P[j].reshape(-1)[cell[j]] for j in range(len(pairs)) if j != i)
            s = np.bincount(cell[i], res, 256)
            c = np.bincount(cell[i], minlength=256)
            P[i] = np.where(c > 0, s / np.maximum(c, 1), 0.0).reshape(16, 16)
    return c3.pack("pairwise", [np.array([m], np.float32)] + [p.astype(np.float32) for p in P])


def fit_tt(idx, y, _, r, seed, sweeps=10):
    X = _unflat(idx).astype(np.uint8)
    rng = np.random.default_rng([seed, r])
    dims = [1] + [min(r, 16 ** min(k, 4 - k)) for k in range(1, 4)] + [1]
    cores = [rng.standard_normal((dims[k], 16, dims[k + 1])) / np.sqrt(dims[k]) for k in range(4)]
    for _ in range(sweeps):
        pl.als_sweep(cores, X, y, RIDGE)
        cores, _ = pl.tt_round(cores, 0.0, r)
    return c3.pack("tt", [c.astype(np.float32) for c in cores])


def fit_cp(idx, y, _, R, seed, sweeps=15):
    X = _unflat(idx)
    rng = np.random.default_rng([seed, 1000 + R])
    U = [rng.standard_normal((16, R)) * 0.5 for _ in range(4)]
    reg = RIDGE * np.eye(R)
    for _ in range(sweeps):
        for k in range(4):
            Z = np.ones((len(y), R))
            for l in range(4):
                if l != k:
                    Z *= U[l][X[:, l]]
            for j in range(16):
                sel = X[:, k] == j
                if sel.any():
                    Zj = Z[sel]
                    U[k][j] = np.linalg.solve(Zj.T @ Zj + reg, Zj.T @ y[sel])
    return c3.pack("cp", [np.ones(R, np.float32)] + [u.astype(np.float32) for u in U])


def fit_program(idx, y, _):
    X = _unflat(idx).T.astype(np.int16)
    t = y - y.mean()
    tt_ = float(t @ t)
    best = (np.inf, None, 0.0, 0.0)
    for a, b, c, d in itertools.permutations(range(4)):
        for o1 in c3.OPS:
            e1 = c3.OPS[o1](X[a], X[b])
            for o2 in c3.OPS:
                e2 = c3.OPS[o2](e1, X[c])
                for o3 in c3.OPS:
                    e = c3.OPS[o3](e2, X[d]).astype(np.float64)
                    ec = e - e.mean()
                    ee = float(ec @ ec)
                    if ee == 0:
                        continue
                    rel = 1.0 - float(ec @ t) ** 2 / (ee * tt_)
                    if rel < best[0] - 1e-12:
                        best = (rel, (a, b, c, d, o1, o2, o3), float(ec @ t) / ee, float(e.mean()))
    _, meta, alpha, emean = best
    beta = y.mean() - alpha * emean
    return c3.pack("program", [np.array([alpha, beta], np.float32)], meta)


def fit_mean(idx, y, _):
    """Baseline: predict the training mean everywhere (stored in the additive format, zero tables)."""
    return c3.pack("additive", [np.array([y.mean()], np.float32)] + [np.zeros(16, np.float32)] * 4)


def learners(seed):
    L = [("mean", fit_mean), ("dense", fit_dense), ("additive", fit_additive), ("pairwise", fit_pairwise),
         ("program", fit_program)]
    L += [(f"tt{r}", (lambda i, y, T, r=r: fit_tt(i, y, T, r, seed))) for r in (1, 2, 4, 8)]
    L += [(f"cp{R}", (lambda i, y, T, R=R: fit_cp(i, y, T, R, seed))) for R in (1, 2, 4, 8, 16)]
    L += [("dense_leak", fit_dense_leak)]
    return L


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    seeds = [100] if a.dev else [int(s) for s in a.seeds.split(",")]
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            fh.write(json.dumps(row) + "\n")
            fh.flush()

        emit({"kind": "header", "exp_id": EXP_ID, "git": c3.git_sha(), "ts": stamp, "seeds": seeds, "Ns": NS,
              "noise": NOISE, "ridge": RIDGE, "probe_N": PROBE_N, "dev": a.dev})
        targets = c3.make_targets(0)                       # C3's seed-0 tables; seeds redraw the SAMPLES
        for s in seeds:
            for tname, T in targets.items():
                flat = T.reshape(-1)
                var = float(flat.var())
                rng = np.random.default_rng([s, 4242, list(targets).index(tname)])
                order = rng.permutation(65536)
                noise = NOISE * rng.standard_normal(65536)
                for N in NS:
                    idx = np.sort(order[:N])
                    held = np.ones(65536, bool)
                    held[idx] = False
                    y = flat[idx] + noise[idx]
                    rows = []
                    for rep, fit in learners(s):
                        t0 = time.perf_counter()
                        blob = fit(idx, y, T)
                        fit_s = time.perf_counter() - t0
                        pred = c3.decode(blob).reshape(-1)
                        row = {"kind": "point", "seed": s, "target": tname, "N": N, "rep": rep,
                               "family": rep.rstrip("0123456789"), "bytes": len(blob),
                               "heldout_rel_mse": float(np.mean((pred[held] - flat[held]) ** 2) / var),
                               "train_rel_mse": float(np.mean((pred[idx] - y) ** 2) / var),
                               "fit_s": round(fit_s, 3)}
                        if N == PROBE_N:
                            scr = flat.copy()
                            hi = np.flatnonzero(held)
                            scr[hi] = scr[rng.permutation(hi)]
                            blob2 = fit(idx, y, scr.reshape(c3.SHAPE))
                            row["probe"] = "CLEAN" if blob2 == blob else "LEAK"
                        rows.append(row)
                        emit(row)
                    base = next(r for r in rows if r["rep"] == "mean")["heldout_rel_mse"]
                    learned = [r for r in rows if r["rep"] not in ("dense_leak", "mean")
                               and r["heldout_rel_mse"] <= base - LEARN_MARGIN]
                    win = min(learned, key=lambda r: (r["heldout_rel_mse"], r["bytes"])) if learned else None
                    emit({"kind": "winner", "seed": s, "target": tname, "N": N, "mean_heldout": base,
                          "rep": win["rep"] if win else None, "bytes": win["bytes"] if win else None,
                          "heldout_rel_mse": win["heldout_rel_mse"] if win else None,
                          "n_learners_that_learn": len(learned)})
                    print(f"s{s} {tname:<16} N={N:<6} winner {(win or {}).get('rep')!s:<9} "
                          f"{(win or {}).get('bytes')!s:>7}B heldout {(win or {}).get('heldout_rel_mse')!s:.10} "
                          f"(mean {base:.3f})", flush=True)
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
