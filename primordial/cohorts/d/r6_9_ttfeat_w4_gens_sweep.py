"""D-R6-9 (ANOM-1789417561532-0): tt_feat w4 -- C-R2-01 (13-14 generations) reached 92% of E9's 200-generation train
score but only 76% of its held64. Does held64 keep rising after train plateaus?

The anomaly's discriminator, at minimum size: E9's loop exactly (E7.G7(4, "tt_feat") + codebook, LuaArchive, batch 128,
E6's 8 train seeds, fused rollout), run seeds 0..7, one 200-generation trajectory per run seed, top-16 (E9's readout)
read at checkpoints 14, 25, 50, 100, 200. Reading the archive at generation g inside one trajectory is exactly a run
stopped at g (same RNG path). Mutation stream = E9's PCG64([990, rs, 4, family index]); the archive sampler is SEEDED
(PCG64([991, rs, 4, family index])) because E9's was UNSEEDED (not reproducible), so E9's rows are references only.

Rule (fixed before reading), per run seed rs:
  rt = (train(200) - train(14)) / train(200);   rh = (held(200) - held(14)) / held(200)
  d = median_rs(rh) - median_rs(rt);  up = #rs with held(200) > held(50)
  HELD_KEEPS_RISING   d >= 0.05 and up >= 6
  TRACKS              |d| < 0.05
  TRAIN_KEEPS_RISING  d <= -0.05
  MIXED               otherwise
  I1  8 run seeds, every checkpoint's top-16 train score == the archive's stored fitness of those 16 genomes (recount,
      exact), and a repeat of run seed 0 reproduces every checkpoint value exactly -- else INDETERMINATE.
Reported, not judged: per checkpoint medians of train and held64 (top-16) and of top1_train; references C-R2-01
(train 133.3 / held 59.9 at 13-14 gens) and E9 (143.9 / 79.2 at 200 gens) from the anomaly text.
"""
from __future__ import annotations

import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R6-9-ttfeat-w4-gens-sweep"
PREDICATE_ID = EXP
ANOMALY = "1789417561532-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
GS, FAM, BATCH, GENS, TOP = 4, "tt_feat", 128, 200, 16
CHECKPOINTS = (14, 25, 50, 100, 200)
RUN_SEEDS = tuple(range(8))
ARCHIVE_URL = "redis://127.0.0.1:6393/0"          # lane D substrate
REF = {"C-R2-01": {"gens": "13-14", "train": 133.3, "held64": 59.9}, "E9": {"gens": 200, "train": 143.9, "held64": 79.2}}


def fused_score(g7, raw, seeds) -> float:
    fit = FusedRollout(g7.spec, len(raw), seeds, family=FAM).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def read_checkpoint(g7, arch) -> dict:
    el = sorted(arch.dump().values(), key=lambda v: (-v[0], v[1]))
    top = el[:TOP]
    raw = np.frombuffer(b"".join(v[1] for v in top), np.uint8).reshape(-1, g7.glen)
    train = fused_score(g7, raw, E7.TRAIN)
    recount = float(np.mean([v[0] for v in top]) / len(E7.TRAIN))
    return {"cells": len(el), "train": train, "held64": fused_score(g7, raw, E7.HELD64),
            "top1_train": fused_score(g7, raw[:1], E7.TRAIN), "top1_held64": fused_score(g7, raw[:1], E7.HELD64),
            "recount_ok": bool(train == recount)}


def trajectory(r, rs: int, key_suffix: str = "") -> dict:
    g7 = E7.G7(GS, FAM)
    fi = list(gm.FAMILIES).index(FAM)
    arch = LuaArchive(r, f"d-r6-9-w{GS}-{FAM}-r{rs}{key_suffix}", g7.glen, [991, rs, GS, fi])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([990, rs, GS, fi]))
    fr = FusedRollout(g7.spec, BATCH, E7.TRAIN, family=FAM)
    out, t0 = {}, time.perf_counter()
    for gen in range(1, GENS + 1):
        par = arch.sample(BATCH)
        g = g7.init(rng, BATCH) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
        fit, cells = fr.run(g)[:2]
        arch.insert(cells, fit, g7.pack(g), np.zeros((BATCH, 2), np.uint32))
        if gen in CHECKPOINTS:
            out[str(gen)] = read_checkpoint(g7, arch)
    arch.clear()
    return {"run_seed": rs, "checkpoints": out, "wall_s": round(time.perf_counter() - t0, 2)}


def decide(i1: bool, runs: list[dict]) -> tuple[str, dict]:
    if not i1 or len(runs) != 8:
        return "INDETERMINATE", {}
    rt = [(x["checkpoints"]["200"]["train"] - x["checkpoints"]["14"]["train"]) / x["checkpoints"]["200"]["train"] for x in runs]
    rh = [(x["checkpoints"]["200"]["held64"] - x["checkpoints"]["14"]["held64"]) / x["checkpoints"]["200"]["held64"] for x in runs]
    d = float(np.median(rh) - np.median(rt))
    up = sum(x["checkpoints"]["200"]["held64"] > x["checkpoints"]["50"]["held64"] for x in runs)
    stats = {"median_rt": float(np.median(rt)), "median_rh": float(np.median(rh)), "d": d, "held_up_50_to_200": int(up),
             "rt": rt, "rh": rh}
    if d >= 0.05 and up >= 6:
        return "HELD_KEEPS_RISING", stats
    if abs(d) < 0.05:
        return "TRACKS", stats
    if d <= -0.05:
        return "TRAIN_KEEPS_RISING", stats
    return "MIXED", stats


def job(ctx, status="record", run_seeds=RUN_SEEDS):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis.from_url(ARCHIVE_URL)
    runs = []
    for rs in run_seeds:
        x = trajectory(r, int(rs))
        runs.append(x)
        ctx.emit({"kind": "run", "exp": EXP, "status": status, "ts": round(time.time(), 3), **x})
    rep = trajectory(r, int(run_seeds[0]), "-repeat")
    same = rep["checkpoints"] == runs[0]["checkpoints"]
    recount = all(c["recount_ok"] for x in runs for c in x["checkpoints"].values())
    i1 = {"runs_8": len(runs) == 8, "recount_all_checkpoints": bool(recount), "repeat_run_seed_0_identical": bool(same)}
    decision, stats = decide(all(i1.values()), runs)
    med = {g: {k: float(np.median([x["checkpoints"][g][k] for x in runs])) for k in ("train", "held64", "top1_train", "top1_held64")}
           for g in map(str, CHECKPOINTS)}
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "world": f"w{GS}", "family": FAM, "gens": GENS, "batch": BATCH,
              "checkpoints": list(CHECKPOINTS), "readout": "top16 (E9 / C-R2-01 legacy)", "runs_total": len(runs),
              "rng_family_count": 1, "runs_per_family": len(runs), "streams": {"mutation": "[990, rs, 4, fam]", "sampler": "[991, rs, 4, fam]"},
              "checks": {"I1": i1}, "controls": {"repeat_run_seed_0": {"identical": bool(same)}},
              "medians_by_checkpoint": med, "references": REF, "stats": stats, "decision": decision,
              "wall_s": round(time.perf_counter() - t0, 3)})
