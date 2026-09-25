"""C-R2-09: drawn cell linear / nk_stub / held_out_seeds / graphblas / none (draw seed 12496832502412519493).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run.

  world     lane E's NK stub (N=64, K=4). A seed is a LANDSCAPE: NKWorld(seed) draws an independent table.
  pressure  held_out_seeds: selection sees 8 train landscapes (seeds 9100..9107, E6's TRAIN values); the score is
            mean NK fitness per landscape on 64 held-out landscapes (seeds 30000..30063, E6's HELD64 values).
  brain     linear policy (target-blind decoder): for locus j of a landscape, features = that locus's 32-entry
            contribution row / 65535; bit_j = [w . row_j + b > 0], w in R^32 and b shared across loci.
            Genome 33 float32 = 132 bytes. Mutation: each gene + N(0, 0.2) with p = 1/8. Init N(0, 1).
  control   bitset: one fixed 64-bit genome (8 bytes) used on every landscape, E1's mutation (p = 1/64 per bit).
            Independent tables share nothing, so this arm can only memorise the train landscapes.
  substrate graphblas (python-graphblas / SuiteSparse): neighbourhood index = BITS mxm circulant weights
            (plus_times), fitness = row-sum of (one-hot selection) ewise_mult (landscape table). numpy builds COO
            inputs and the linear decode; every fitness is GraphBLAS arithmetic.
  budget    300 gens x 128 per arm (E1's generations), 8 run seeds, LuaArchive with E's seeded sampler
            (sampler_seed = 9000 + 10 * run_seed + arm) so runs replay; elites saved to HOT.
            Descriptor: popcount halves of the bits on train landscape 0 (E's stub grid, 33x33).
  primary   median over run seeds of held-out fitness (linear) > median held-out (bitset) + 0.5 * IQR(bitset)
  oracles   numpy reference NKWorld(seed).evaluate == GraphBLAS fitness on every offer of run seed 0 (both arms) and
            on every final elite of every run (train landscapes); cheat: GraphBLAS with a K=3 window mismatches
            >= 90% of seed-0 final elites x train landscapes, counted on ELIGIBLE rows only (bits not all zero:
            an all-zero row has identical K=3/K=5 indices, so no cheat of this kind can differ there), with
            >= 1 eligible row; eligible and all-zero counts are reported. Rule fixed before the predicate, after a
            no-rows check showed random linear genomes emit all-zero rows (raw share 0.863).
  report    random-bits mean per landscape; train fitness per arm; clause A has no NK baseline.

  python -m primordial.cohorts.c.r2_09_nk_linear_heldout_graphblas [--gens 300] [--run-seeds 0-7]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import graphblas as gb
import numpy as np
import redis
from graphblas import Matrix, dtypes, semiring

from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger
from primordial.qd.archive import LuaArchive
from primordial.qd.stubworld import GRID, K, N_BITS, N_CELLS, NKWorld, mutate as bit_mutate

EXP = "C-R2-09-nk-linear-heldout-graphblas"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C") / EXP          # hot data never on F:
N, BATCH, TOP = N_BITS, 128, 16
TRAIN_SEEDS = np.arange(9100, 9108)
HELD_SEEDS = np.arange(30000, 30064)
CELL = {"representation": "linear", "world": "nk_stub", "pressure": "held_out_seeds", "substrate": "graphblas",
        "channel": "none"}
CELL_BITS = dict(CELL, representation="bitset")
LIN_GENES, LIN_GLEN = 33, 132


def circulant(kk: int) -> Matrix:
    r, c, v = [], [], []
    for j in range(N):
        for t in range(kk):
            r.append((j + t) % N); c.append(j); v.append(1 << t)
    return Matrix.from_coo(r, c, v, nrows=N, ncols=N, dtype=dtypes.INT64)


WC = {K + 1: circulant(K + 1), K: circulant(K)}


def gb_fitness(bits: np.ndarray, tables: np.ndarray, window: int = K + 1) -> np.ndarray:
    """bits uint8 [R, N], tables int64 [R, N, 32] (row r uses its own landscape) -> int64 [R]."""
    R = len(bits)
    rr, cc = np.nonzero(bits)
    BM = Matrix.from_coo(rr, cc, np.ones(len(rr), np.int64), nrows=R, ncols=N, dtype=dtypes.INT64)
    idx = np.zeros((R, N), np.int64)
    ir, ic, iv = BM.mxm(WC[window], semiring.plus_times).new().to_coo()
    idx[ir, ic] = iv
    S = Matrix.from_coo(np.repeat(np.arange(R), N), (np.arange(N)[None, :] * 32 + idx).reshape(-1),
                        np.ones(R * N, np.int64), nrows=R, ncols=N * 32, dtype=dtypes.INT64)
    TM = Matrix.from_coo(np.repeat(np.arange(R), N * 32), np.tile(np.arange(N * 32), R), tables.reshape(-1),
                         nrows=R, ncols=N * 32, dtype=dtypes.INT64)
    fi, fv = S.ewise_mult(TM, gb.binary.times).new().reduce_rowwise(gb.monoid.plus).new().to_coo()
    out = np.zeros(R, np.int64)
    out[fi] = fv
    return out


def ref_fitness(bits: np.ndarray, worlds: list, land_idx: np.ndarray) -> np.ndarray:
    """numpy reference: NKWorld(seed).evaluate per row's landscape."""
    out = np.empty(len(bits), np.int64)
    for l in np.unique(land_idx):
        sel = land_idx == l
        out[sel] = worlds[l].evaluate(np.packbits(bits[sel], axis=1))[0]
    return out


class Landscapes:
    def __init__(self, seeds):
        self.worlds = [NKWorld(int(s)) for s in seeds]
        self.tables = np.stack([w.table for w in self.worlds])                     # [L, N, 32]
        self.feats = (self.tables / 65535.0).astype(np.float32)                    # [L, N, 32]


def decode(arm: str, g: np.ndarray, land: Landscapes) -> np.ndarray:
    """genomes -> bits uint8 [P, L, N]."""
    P, L = len(g), len(land.worlds)
    if arm == "bitset":
        return np.repeat(np.unpackbits(g, axis=1)[:, None, :], L, axis=1)
    wb = np.frombuffer(np.ascontiguousarray(g).tobytes(), "<f4").reshape(P, LIN_GENES)
    s = np.einsum("lnf,pf->pln", land.feats, wb[:, :32]) + wb[:, 32][:, None, None]
    return (s > 0).astype(np.uint8)


def evaluate(arm, g, land, window=K + 1):
    bits = decode(arm, g, land)
    P, L = bits.shape[:2]
    fit = gb_fitness(bits.reshape(P * L, N), np.tile(land.tables, (P, 1, 1)), window).reshape(P, L)
    d0 = bits[:, 0, :32].sum(1); d1 = bits[:, 0, 32:].sum(1)
    return fit, (d0 * GRID + d1).astype(np.uint32), bits


def init(arm, rng, P):
    if arm == "bitset":
        return rng.integers(0, 256, (P, 8), dtype=np.uint8)
    return np.frombuffer(rng.standard_normal((P, LIN_GENES)).astype("<f4").tobytes(), np.uint8).reshape(P, LIN_GLEN).copy()


def mutate(arm, rng, g):
    if arm == "bitset":
        return bit_mutate(rng, g)
    wb = np.frombuffer(np.ascontiguousarray(g).tobytes(), "<f4").reshape(len(g), LIN_GENES).copy()
    wb += (rng.random(wb.shape) < 1.0 / 8) * rng.normal(0, 0.2, wb.shape).astype(np.float32)
    return np.frombuffer(wb.astype("<f4").tobytes(), np.uint8).reshape(len(g), LIN_GLEN).copy()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=300)
    p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--port", type=int, default=6392)
    a = p.parse_args()
    lo, hi = (int(x) for x in a.run_seeds.split("-"))
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    train, held = Landscapes(TRAIN_SEEDS), Landscapes(HELD_SEEDS)
    rr = np.random.Generator(np.random.PCG64(5))
    rbits = rr.integers(0, 2, (256, N)).astype(np.uint8)
    random_mean = float(ref_fitness(np.repeat(rbits, len(held.worlds), 0), held.worlds,
                                    np.tile(np.arange(len(held.worlds)), 256)).mean())
    arms = (("linear", LIN_GLEN, CELL), ("bitset", 8, CELL_BITS))
    heldv = {"linear": [], "bitset": []}
    clean = True
    cheat_share = None
    with RowWriter(ROWS, EXP, commit_every_s=120) as w:
        w.write({"kind": "reference", "random_bits_mean_per_held_landscape": random_mean, "status": "control"})
        for rs in range(lo, hi + 1):
            for ai, (arm, glen, cell) in enumerate(arms):
                t0 = time.perf_counter()
                arch = LuaArchive(r, f"c-r2-09-{arm}-{rs}", glen, sampler_seed=9000 + 10 * rs + ai)
                arch.clear()
                rng = np.random.Generator(np.random.PCG64([909, rs, ai]))
                offers = offer_bad = 0
                t_eval = 0.0
                for _ in range(a.gens):
                    par = arch.sample(BATCH)
                    g = init(arm, rng, BATCH) if len(par) == 0 else mutate(arm, rng, par)
                    s = time.perf_counter()
                    fit, cells, bits = evaluate(arm, g, train)
                    t_eval += time.perf_counter() - s
                    if rs == lo:
                        P, L = bits.shape[:2]
                        ref = ref_fitness(bits.reshape(P * L, N), train.worlds, np.tile(np.arange(L), P)).reshape(P, L)
                        offers += P * L
                        offer_bad += int((ref != fit).sum())
                    arch.insert(cells, fit.sum(1).astype(np.int32), g, np.zeros((BATCH, 2), np.uint32))
                el = arch.dump()
                arch.clear()
                order = sorted(el.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
                eg = np.frombuffer(b"".join(v[1] for _, v in order), np.uint8).reshape(-1, glen)
                ef = np.array([v[0] for _, v in order], np.int64)
                np.save(HOT / f"{arm}_r{rs}_elites.npy", eg)
                fit_e, _, bits_e = evaluate(arm, eg, train)
                P, L = bits_e.shape[:2]
                ref_e = ref_fitness(bits_e.reshape(P * L, N), train.worlds, np.tile(np.arange(L), P)).reshape(P, L)
                elite_bad = int((ref_e.sum(1) != ef).sum()) + int((fit_e != ref_e).sum())
                top = eg[:TOP]
                fh = evaluate(arm, top, held)[0]
                row = {"kind": "run", "arm": arm, "cell": cell, "run_seed": rs, "gens": a.gens, "genomes": a.gens * BATCH,
                       "genome_bytes": glen, "archive_cells": len(el), "coverage": round(len(el) / N_CELLS, 4),
                       "train_per_landscape_top16": float(fit_e[:TOP].mean()),
                       "held_per_landscape_top16": float(fh.mean()),
                       "held_minus_random": float(fh.mean() - random_mean),
                       "elites_mismatched": elite_bad, "offers_audited": offers, "offers_mismatched": offer_bad,
                       "gb_eval_s": round(t_eval, 2), "status": "record" if arm == "linear" else "control"}
                clean = clean and elite_bad == 0 and offer_bad == 0
                if rs == lo:
                    ch = evaluate(arm, eg, train, window=K)[0]
                    eligible = bits_e.any(axis=2)          # all-zero bits give identical K=3/K=5 indices: cheat cannot differ
                    n_elig = int(eligible.sum())
                    share = float((ch != ref_e)[eligible].mean()) if n_elig else 0.0
                    row["cheat_k3_window_mismatch_share_eligible"] = round(share, 4)
                    row["cheat_k3_eligible_rows"] = n_elig
                    row["cheat_k3_all_zero_rows"] = int(eligible.size - n_elig)
                    clean = clean and n_elig > 0 and share >= 0.9
                    cheat_share = share if cheat_share is None else min(cheat_share, share)
                row["wall_s"] = round(time.perf_counter() - t0, 2)
                heldv[arm].append(row["held_per_landscape_top16"])
                print(json.dumps(row), flush=True)
                w.write(row)
        st = {arm: tuple(float(x) for x in np.percentile(heldv[arm], [25, 50, 75])) for arm in heldv}
        bar = st["bitset"][1] + 0.5 * (st["bitset"][2] - st["bitset"][0])
        n = min(len(heldv["linear"]), len(heldv["bitset"]))
        summary = {"kind": "summary", "cell": CELL, "n_runs": n, "random_bits_mean": random_mean,
                   "held_median_linear": round(st["linear"][1], 1), "iqr_linear": round(st["linear"][2] - st["linear"][0], 1),
                   "held_median_bitset": round(st["bitset"][1], 1), "iqr_bitset": round(st["bitset"][2] - st["bitset"][0], 1),
                   "bar": round(bar, 1), "oracle_clean": clean, "cheat_k3_min_share": cheat_share,
                   "primary": ("INDETERMINATE" if not clean else
                               ("PASS" if n >= 8 and st["linear"][1] > bar else "FAIL")),
                   "status": "record" if clean else "cheat"}
        print(json.dumps(summary), flush=True)
        w.write(summary)
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        for arm, cell, glen, status in (("linear", CELL, LIN_GLEN, summary["status"]), ("bitset", CELL_BITS, 8, "control")):
            q.write({"cell": cell, "mechanism": f"nk_{arm}_policy_train8_landscapes_{a.gens}gens",
                     "fitness": {"held64_median": None, "held_per_landscape_median": round(st[arm][1], 1),
                                 "iqr": round(st[arm][2] - st[arm][0], 1), "random_bits_mean": round(random_mean, 1),
                                 "n_runs": len(heldv[arm])},
                     "footprint": {"genome_bytes": glen},
                     "oracle": "clean (numpy NK reference == GraphBLAS on all seed-0 offers + all elites; K=3 cheat caught)"
                               if clean else "NOT clean",
                     "baseline": False, "cohort": "C", "status": status,
                     "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


if __name__ == "__main__":
    main()
