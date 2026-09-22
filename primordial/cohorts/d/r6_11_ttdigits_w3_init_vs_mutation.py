"""D-R6-11 (ANOM-1789415790372-0): tt_digits w3 held-out swings with the run RNG (E7 -> E7b: 53.4 -> 87.7; E7b runs
17.5..86.8 while linear stays 84-106). Is the swing carried by the initial population or by the mutation / sampling path?

The anomaly's discriminator at minimum size: E7b's setup (E7.G7(3, "tt_digits") + codebook, LuaArchive, fused rollout,
200 gens x batch 128 on E6's 8 train seeds, top-16 on HELD64) with the single run RNG split in two:
  init stream      PCG64([992, i, 3, fam])  -- used only for g7.init (the first generation, empty archive)
  mutation stream  PCG64([993, m, 3, fam])  -- every g7.mutate; archive sampler seeded PCG64([994, m, 3, fam])
A 4 x 4 grid (i, m in 0..3), one run per cell, plus a determinism repeat of (0, 0).

Rule (fixed before reading), H[i][m] = top-16 held64 per seed of cell (i, m):
  NO_SWING            max(H) - min(H) < 20   (the filed swing does not appear in this grid)
  otherwise, with vi = variance over i of the row means (mean over m) and vm = variance over m of the column means:
  INIT_DOMINATES      vi >= 2 vm
  MUTATION_DOMINATES  vm >= 2 vi
  BOTH                otherwise
  I1  16 cells, top-16 train == archive fitness recount (exact) in every cell, the (0, 0) repeat identical
      -- else INDETERMINATE.
Reported, not judged: the grid, row / column means, interaction residual variance, train grid.
"""
from __future__ import annotations

import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R6-11-ttdigits-w3-init-vs-mutation"
PREDICATE_ID = EXP
ANOMALY = "1789415790372-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
GS, FAM, BATCH, GENS, TOP = 3, "tt_digits", 128, 200, 16
SEEDS = (0, 1, 2, 3)
ARCHIVE_URL = "redis://127.0.0.1:6393/0"          # lane D substrate
SWING_MIN = 20.0


def fused_score(g7, raw, seeds) -> float:
    fit = FusedRollout(g7.spec, len(raw), seeds, family=FAM).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def cell_run(r, i: int, m: int, suffix: str = "") -> dict:
    g7 = E7.G7(GS, FAM)
    fi = list(gm.FAMILIES).index(FAM)
    arch = LuaArchive(r, f"d-r6-11-w{GS}-{FAM}-i{i}-m{m}{suffix}", g7.glen, [994, m, GS, fi])
    arch.clear()
    rng_init = np.random.Generator(np.random.PCG64([992, i, GS, fi]))
    rng_mut = np.random.Generator(np.random.PCG64([993, m, GS, fi]))
    fr = FusedRollout(g7.spec, BATCH, E7.TRAIN, family=FAM)
    t0 = time.perf_counter()
    inits = 0
    for _ in range(GENS):
        par = arch.sample(BATCH)
        if len(par) == 0:
            g = g7.init(rng_init, BATCH)
            inits += 1
        else:
            g = g7.mutate(rng_mut, g7.unpack(par))
        fit, cells = fr.run(g)[:2]
        arch.insert(cells, fit, g7.pack(g), np.zeros((BATCH, 2), np.uint32))
    el = sorted(arch.dump().values(), key=lambda v: (-v[0], v[1]))
    arch.clear()
    top = el[:TOP]
    raw = np.frombuffer(b"".join(v[1] for v in top), np.uint8).reshape(-1, g7.glen)
    train = fused_score(g7, raw, E7.TRAIN)
    return {"init_seed": i, "mut_seed": m, "cells": len(el), "init_generations": inits,
            "train": train, "held64": fused_score(g7, raw, E7.HELD64),
            "recount_ok": bool(train == float(np.mean([v[0] for v in top]) / len(E7.TRAIN))),
            "wall_s": round(time.perf_counter() - t0, 2)}


def decide(i1: bool, H: np.ndarray) -> tuple[str, dict]:
    if not i1 or H.shape != (len(SEEDS), len(SEEDS)):
        return "INDETERMINATE", {}
    row, col = H.mean(1), H.mean(0)
    vi, vm = float(np.var(row, ddof=1)), float(np.var(col, ddof=1))
    resid = H - row[:, None] - col[None, :] + H.mean()
    stats = {"range": float(H.max() - H.min()), "row_means_init": row.tolist(), "col_means_mut": col.tolist(),
             "var_init_means": vi, "var_mut_means": vm,
             "var_interaction_resid": float((resid ** 2).sum() / ((len(SEEDS) - 1) ** 2))}
    if stats["range"] < SWING_MIN:
        return "NO_SWING", stats
    if vi >= 2 * vm:
        return "INIT_DOMINATES", stats
    if vm >= 2 * vi:
        return "MUTATION_DOMINATES", stats
    return "BOTH", stats


def job(ctx, status="record"):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis.from_url(ARCHIVE_URL)
    grid = {}
    for i in SEEDS:
        for m in SEEDS:
            x = cell_run(r, i, m)
            grid[(i, m)] = x
            ctx.emit({"kind": "cell", "exp": EXP, "status": status, "ts": round(time.time(), 3), **x})
    rep = cell_run(r, 0, 0, "-repeat")
    same = all(rep[k] == grid[(0, 0)][k] for k in ("train", "held64", "cells"))
    i1 = {"cells_16": len(grid) == 16, "recount_all": all(v["recount_ok"] for v in grid.values()),
          "repeat_0_0_identical": bool(same)}
    H = np.array([[grid[(i, m)]["held64"] for m in SEEDS] for i in SEEDS])
    T = np.array([[grid[(i, m)]["train"] for m in SEEDS] for i in SEEDS])
    decision, stats = decide(all(i1.values()), H)
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "world": f"w{GS}", "family": FAM, "gens": GENS, "batch": BATCH,
              "readout": "top16 (E7 / E7b)", "grid_held64": H.tolist(), "grid_train": T.tolist(),
              "checks": {"I1": i1}, "controls": {"repeat_0_0": {"identical": bool(same), "held64": rep["held64"]}},
              "runs_total": 16, "rng_family_count": 1, "runs_per_family": 16,
              "stats": stats, "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
