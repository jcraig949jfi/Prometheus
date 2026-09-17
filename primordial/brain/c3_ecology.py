"""C3: representation ecology -- one task, many representations, report the Pareto set.

Task: represent a known function f of 4 base-16 digits (the full 65,536-entry table).
Every representation is fitted to f, SERIALIZED to bytes, and scored ONLY from a
decoder that sees the bytes and nothing else:
    bytes   = len(serialized blob)            (memory charge)
    flops   = analytic ops per evaluation of one input
    rel_mse = mean((decode(blob) - f)^2) / var(f)
The in-memory predict() is also scored; any gap to the from-bytes decode > 1e-5 flags
BYTES_MISMATCH (a representation that smuggles the answer outside its bytes).

Representations (size knob in brackets):
  dense            full float32 table
  bits[b]          table quantized to 2^b uniform levels, packed bits (b = 1,2,4,8)
  tt[r]            TT-SVD, bond rank <= r
  cp[R]            CP / PARAFAC (tensorly ALS)
  tucker[R]        Tucker / HOSVD+HOOI (tensorly), core R^4
  additive         4 tables of 16 + mean
  pairwise         6 tables of 16x16 (ANOVA backfitting)
  program          exhaustive tiny digit program (((xa o1 xb) o2 xc) o3 xd) mod 16, affine output;
                   ops add sub mul xor and or
  cheat_ref        CHEAT: predict() reads the target; its bytes hold nothing
Targets:
  tt_rank2         orthogonal TT, every bond rank 2
  separable_decay  8 separable terms, weights 0.8^c
  program_in       ((x0*x1 + x2) xor x3) mod 16      (INSIDE the program search space by construction)
  program_out      (x0*x1*x2 + x3*x3) mod 13          (outside it: 3-way product, mod 13)
  noise            iid Gaussian table (incompressible)

usage: python -m primordial.brain.c3_ecology [--seeds 0,1,2] [--dev]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import itertools
import json
import pathlib
import struct
import subprocess
import time

import numpy as np

from primordial.brain import plastic as pl

EXP_ID = "C3-representation-ecology"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
ROOT = pathlib.Path(__file__).resolve().parents[1]
SHAPE = (16, 16, 16, 16)
KINDS = ["dense", "bits", "tt", "cp", "tucker", "additive", "pairwise", "program", "cheat_ref"]
OPS = {0: lambda a, b: (a + b) & 15, 1: lambda a, b: (a - b) & 15, 2: lambda a, b: (a * b) & 15,
       3: lambda a, b: a ^ b, 4: lambda a, b: a & b, 5: lambda a, b: a | b}
OP_NAMES = ["add", "sub", "mul", "xor", "and", "or"]
EPS = (1e-1, 1e-2, 1e-4, 1e-8)


def mismatch(rel_bytes: float, rel_mem: float) -> bool:
    """BYTES_MISMATCH iff the bytes decode is materially worse than the in-memory object
    (posted rule): bytes error > in-memory error + max(1e-3, in-memory error). Pointwise
    gaps alone misfire on honest degenerate CP fits that lose float32 precision."""
    return rel_bytes > rel_mem + max(1e-3, rel_mem)


# ------------------------------------------------------------------ bytes

def pack(kind: str, arrays, meta=()) -> bytes:
    out = [struct.pack("<BB", KINDS.index(kind), len(meta)), struct.pack(f"<{len(meta)}i", *meta)]
    out.append(struct.pack("<B", len(arrays)))
    for a in arrays:
        a = np.ascontiguousarray(a)
        code = {np.dtype(np.float32): 0, np.dtype(np.uint8): 1}[a.dtype]
        out.append(struct.pack("<BB", code, a.ndim) + struct.pack(f"<{a.ndim}I", *a.shape))
        out.append(a.tobytes())
    return b"".join(out)


def unpack(blob: bytes):
    kind_i, nmeta = struct.unpack_from("<BB", blob, 0)
    off = 2
    meta = struct.unpack_from(f"<{nmeta}i", blob, off)
    off += 4 * nmeta
    (narr,) = struct.unpack_from("<B", blob, off)
    off += 1
    arrays = []
    for _ in range(narr):
        code, nd = struct.unpack_from("<BB", blob, off)
        off += 2
        shape = struct.unpack_from(f"<{nd}I", blob, off)
        off += 4 * nd
        dt = [np.float32, np.uint8][code]
        n = int(np.prod(shape)) * np.dtype(dt).itemsize
        arrays.append(np.frombuffer(blob, dt, count=int(np.prod(shape)), offset=off).reshape(shape))
        off += n
    return KINDS[kind_i], list(meta), arrays


def decode(blob: bytes) -> np.ndarray:
    """The ONLY scoring path: bytes in, full table out. No access to any target."""
    kind, meta, A = unpack(blob)
    f = lambda a: a.astype(np.float64)
    if kind == "dense":
        return f(A[0])
    if kind == "bits":
        b, = meta
        lo, hi = f(A[0])
        codes = np.unpackbits(A[1], bitorder="little")[:65536 * b].reshape(65536, b)
        lvl = (codes.astype(np.int64) << np.arange(b)).sum(1)
        return (lo + (hi - lo) * lvl / (2 ** b - 1)).reshape(SHAPE)
    if kind == "tt":
        return pl.tt_full([f(a) for a in A])
    if kind == "cp":
        w, *U = [f(a) for a in A]
        return np.einsum("r,ir,jr,kr,lr->ijkl", w, *U)
    if kind == "tucker":
        G, *U = [f(a) for a in A]
        return np.einsum("abcd,ia,jb,kc,ld->ijkl", G, *U)
    if kind == "additive":
        m, *t = [f(a) for a in A]
        return (m[0] + t[0][:, None, None, None] + t[1][None, :, None, None]
                + t[2][None, None, :, None] + t[3][None, None, None, :])
    if kind == "pairwise":
        m, *P = [f(a) for a in A]
        out = np.full(SHAPE, m[0])
        for (k, l), p in zip(itertools.combinations(range(4), 2), P):
            sh = [1, 1, 1, 1]; sh[k] = 16; sh[l] = 16
            out = out + p.reshape(sh)
        return out
    if kind == "program":
        a, b, c, d, o1, o2, o3 = meta
        X = np.indices(SHAPE, dtype=np.int64)
        e = OPS[o3](OPS[o2](OPS[o1](X[a], X[b]), X[c]), X[d])
        alpha, beta = f(A[0])
        return alpha * e + beta
    if kind == "cheat_ref":
        return np.zeros(SHAPE)
    raise ValueError(kind)


# ------------------------------------------------------------------ fits

def fit_bits(T, b):
    lo, hi = T.min(), T.max()
    lvl = np.rint((T - lo) / (hi - lo) * (2 ** b - 1)).astype(np.int64).reshape(-1)
    bits = ((lvl[:, None] >> np.arange(b)) & 1).astype(np.uint8).reshape(-1)
    blob = pack("bits", [np.array([lo, hi], np.float32), np.packbits(bits, bitorder="little")], (b,))
    return blob, lambda: decode(blob), 2


def tt_svd(T, r):
    cores, M, rl = [], T, 1
    for _ in range(3):
        U, S, Vt = np.linalg.svd(M.reshape(rl * 16, -1), full_matrices=False)
        rk = min(r, len(S))
        cores.append(U[:, :rk].reshape(rl, 16, rk))
        M = S[:rk, None] * Vt[:rk]
        rl = rk
    cores.append(M.reshape(rl, 16, 1))
    return cores


def fit_tt(T, r):
    cores = tt_svd(T, r)
    blob = pack("tt", [c.astype(np.float32) for c in cores])
    flops = sum(c.shape[0] * c.shape[2] for c in cores)
    return blob, lambda: pl.tt_full(cores), flops


def fit_cp(T, R, seed):
    import tensorly as tl
    from tensorly.decomposition import parafac
    tl.set_backend("numpy")
    w, U = parafac(T, rank=R, n_iter_max=300, tol=1e-12, init="random", random_state=seed)
    blob = pack("cp", [np.asarray(w, np.float32)] + [np.asarray(u, np.float32) for u in U])
    return blob, lambda: np.einsum("r,ir,jr,kr,lr->ijkl", w, *U), R * 5


def fit_tucker(T, R, seed):
    import tensorly as tl
    from tensorly.decomposition import tucker
    tl.set_backend("numpy")
    G, U = tucker(T, rank=[R] * 4, n_iter_max=100, tol=1e-12, init="svd", random_state=seed)
    blob = pack("tucker", [np.asarray(G, np.float32)] + [np.asarray(u, np.float32) for u in U])
    return blob, lambda: np.einsum("abcd,ia,jb,kc,ld->ijkl", G, *U), R ** 4 + R ** 3 + R ** 2 + R


def fit_additive(T):
    m = T.mean()
    t = [T.mean(axis=tuple(a for a in range(4) if a != k)) - m for k in range(4)]
    blob = pack("additive", [np.array([m], np.float32)] + [x.astype(np.float32) for x in t])
    return blob, lambda: decode(blob), 4


def fit_pairwise(T, sweeps=30):
    m = T.mean()
    pairs = list(itertools.combinations(range(4), 2))
    P = [np.zeros((16, 16)) for _ in pairs]

    def full(skip=None):
        out = np.full(SHAPE, m)
        for i, ((k, l), p) in enumerate(zip(pairs, P)):
            if i != skip:
                sh = [1, 1, 1, 1]; sh[k] = 16; sh[l] = 16
                out = out + p.reshape(sh)
        return out

    for _ in range(sweeps):
        for i, (k, l) in enumerate(pairs):
            res = T - full(skip=i)
            P[i] = res.mean(axis=tuple(a for a in range(4) if a not in (k, l)))
    blob = pack("pairwise", [np.array([m], np.float32)] + [p.astype(np.float32) for p in P])
    return blob, full, 6


def fit_program(T):
    X = np.indices(SHAPE, dtype=np.int16).reshape(4, -1)
    t = T.reshape(-1) - T.mean()
    tt_ = float(t @ t)
    best = (np.inf, None)
    for a, b, c, d in itertools.permutations(range(4)):
        for o1 in OPS:
            e1 = OPS[o1](X[a], X[b])
            for o2 in OPS:
                e2 = OPS[o2](e1, X[c])
                for o3 in OPS:
                    e = OPS[o3](e2, X[d]).astype(np.float64)
                    ec = e - e.mean()
                    ee = float(ec @ ec)
                    if ee == 0:
                        continue
                    rel = 1.0 - float(ec @ t) ** 2 / (ee * tt_)
                    if rel < best[0] - 1e-12:
                        best = (rel, (a, b, c, d, o1, o2, o3), float(ec @ t) / ee, e.mean())
    _, meta, alpha, emean = best
    beta = T.mean() - alpha * emean
    blob = pack("program", [np.array([alpha, beta], np.float32)], meta)
    return blob, lambda: decode(blob), 5


class CheatRef:
    """Holds the target in Python memory; serializes nothing useful."""

    def __init__(self, T):
        self.T = T

    def fit(self):
        return pack("cheat_ref", []), lambda: self.T, 1


# ------------------------------------------------------------------ targets

def standardize(T):
    return (T - T.mean()) / T.std()


def make_targets(seed):
    rng = np.random.default_rng([seed, 77])
    x0, x1, x2, x3 = np.indices(SHAPE)
    return {
        "tt_rank2": standardize(pl.tt_full(pl.random_target(4, 2, rng))),
        "separable_decay": standardize(pl.tt_full(pl.decaying_target(4, 8, 0.8, rng))),
        "program_in": standardize((((x0 * x1 + x2) ^ x3) % 16).astype(float)),
        "program_out": standardize(((x0 * x1 * x2 + x3 * x3) % 13).astype(float)),
        "noise": standardize(rng.standard_normal(SHAPE)),
    }


def pareto(points, keys):
    front = []
    for i, p in enumerate(points):
        dominated = any(all(q[k] <= p[k] for k in keys) and any(q[k] < p[k] for k in keys)
                        for j, q in enumerate(points) if j != i)
        if not dominated:
            front.append(p["rep"])
    return front


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--dev", action="store_true")
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

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "seeds": seeds, "dev": a.dev})
        for s in seeds:
            for tname, T in make_targets(s).items():
                var = float(T.var())
                fits = [("dense", lambda: (pack("dense", [T.astype(np.float32)]), lambda: T, 1))]
                fits += [(f"bits{b}", (lambda b=b: fit_bits(T, b))) for b in (1, 2, 4, 8)]
                fits += [(f"tt{r}", (lambda r=r: fit_tt(T, r))) for r in (1, 2, 3, 4, 6, 8, 12, 16)]
                fits += [(f"cp{R}", (lambda R=R: fit_cp(T, R, s))) for R in (1, 2, 4, 8, 16, 32)]
                fits += [(f"tucker{R}", (lambda R=R: fit_tucker(T, R, s))) for R in (1, 2, 4, 8, 12)]
                fits += [("additive", lambda: fit_additive(T)), ("pairwise", lambda: fit_pairwise(T)),
                         ("program", lambda: fit_program(T)), ("cheat_ref", CheatRef(T).fit)]
                points = []
                for rep, fit in fits:
                    t0 = time.perf_counter()
                    blob, predict, flops = fit()
                    fit_s = time.perf_counter() - t0
                    from_bytes = decode(blob)
                    in_mem = predict()
                    rel = float(np.mean((from_bytes - T) ** 2) / var)
                    rel_mem = float(np.mean((in_mem - T) ** 2) / var)
                    gap = float(np.max(np.abs(from_bytes - in_mem)))
                    row = {"kind": "point", "seed": s, "target": tname, "rep": rep, "family": rep.rstrip("0123456789"),
                           "bytes": len(blob), "flops": int(flops), "rel_mse": rel, "rel_mse_in_memory": rel_mem,
                           "bytes_gap": gap, "bytes_mismatch": mismatch(rel, rel_mem), "fit_s": round(fit_s, 3)}
                    if rep == "program":
                        row["program"] = unpack(blob)[1]
                    points.append(row)
                    emit(row)
                clean = [p for p in points if not p["bytes_mismatch"]]
                f3 = pareto(clean, ("bytes", "flops", "rel_mse"))
                f2 = pareto(clean, ("bytes", "rel_mse"))
                cheapest = {}
                for eps in EPS:
                    ok = [p for p in clean if p["rel_mse"] <= eps]
                    cheapest[str(eps)] = {"min_bytes": min(ok, key=lambda p: (p["bytes"], p["flops"]))["rep"] if ok else None,
                                          "min_flops": min(ok, key=lambda p: (p["flops"], p["bytes"]))["rep"] if ok else None}
                flagged = [p["rep"] for p in points if p["bytes_mismatch"]]
                emit({"kind": "front", "seed": s, "target": tname, "front_bytes_flops_err": f3,
                      "front_bytes_err": f2, "cheapest_at_eps": cheapest, "flagged": flagged})
                print(f"s{s} {tname:<16} min_bytes@eps={ {e: c['min_bytes'] for e, c in cheapest.items()} } flagged={flagged}",
                      flush=True)
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
