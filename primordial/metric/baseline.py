"""M2 / G-R4-3 stage 2 (round 4 P0, builder G): the FLOAT LINEAR BASELINE, re-seeded.

The round 1 baseline a clause A candidate is judged against, re-run with >= 8 run seeds, a seeded archive
sampler and the elites of every run seed saved (C2), at round 1's budget:

  pressure          TRAIN seeds       budget (gens x batch)   round 1 source of the budget
  train8_held64     9100..9107        200 x 128 = 25,600      E9 linear (E7.G7 + FusedRollout)
  train128_held64   9100..9227        800 x 128 = 102,400     E10 closed linear

Genome: E7.G7(gen_seed, "linear") -- lane C's linear params + lane E's A x W action codebook; bytes =
g7.glen (packed genome, codebook included). Per run seed: the top-16 elites by train fitness, per-seed
mean on HELD64 (E9.fused_score). The cell's baseline: median over run seeds, the bootstrap 95% CI of that
median (M3, primordial.metric.ci.median_ci), and the bytes.

    python -m primordial.fabric.worker submit G primordial.metric.baseline:job --exp G-R4-3-stage2-baseline \\
        --rows primordial/ledger/rows/G/G-R4-3-stage2-baseline.jsonl --ttl-cpu-s S \\
        --kwargs '{"cells": [[4, "train128_held64"]]}'
"""
from __future__ import annotations

import hashlib
import pathlib
import time

import numpy as np

from primordial.metric import floors as F
from primordial.metric.ci import BOOT_SEED, N_BOOT, median_ci
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive, load_elites, save_elites
from primordial.soup.b6.fused import FusedRollout

EXP = "G-R4-3-stage2-baseline"
FAM = "linear"
BUDGET = {"train8_held64": (200, 128), "train128_held64": (800, 128)}
BUDGET_SOURCE = {"train8_held64": "E9-family-ranking-fused-8-seeds linear genomes",
                 "train128_held64": "E10-linear-closed-vs-open-128-seeds closed_genomes"}
TOP = 16
MIN_RUNS = 8
PAUSE_EVERY = 25
ARCHIVE_URL = "redis://127.0.0.1:6394/0"
ELITES_DIR = pathlib.Path("C:/Users/jcrai/lab/pm-data/G") / EXP


def run_key(gen_seed: int, pressure: str, run_seed: int) -> str:
    return f"g-r4-base-w{gen_seed}-{pressure}-r{run_seed}"


def fused_per_seed(g7: E7.G7, raw: np.ndarray, seeds: np.ndarray) -> float:
    """E9.fused_score: mean over genomes of the per-seed held score."""
    fit = FusedRollout(g7.spec, len(raw), seeds, family=FAM).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def top_raw(elites: list, glen: int, n: int = TOP) -> np.ndarray:
    """elites: [(fit, genome bytes)] -> the n best by (-fit, genome bytes), packed [n, glen]."""
    best = sorted(elites, key=lambda v: (-v[0], v[1]))[:n]
    return np.frombuffer(b"".join(g for _, g in best), np.uint8).reshape(-1, glen)


def baseline_run(r, gen_seed: int, pressure: str, run_seed: int, gens: int | None = None,
                 batch: int | None = None, elites_dir=ELITES_DIR, should_pause=None, state: dict | None = None) -> dict:
    """One run seed. Returns the row, or {"paused": state} when should_pause() fired (archive kept)."""
    g7 = E7.G7(gen_seed, FAM)
    train = F.PRESSURES[pressure]
    bg, bb = BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    key = run_key(gen_seed, pressure, run_seed)
    sseed = [4201, run_seed, gen_seed, len(train)]
    arch = LuaArchive(r, key, g7.glen, sseed)
    rng = np.random.Generator(np.random.PCG64([4200, run_seed, gen_seed, len(train)]))
    if state is None:
        arch.clear()
        state = {"gen": 0, "qd_wall_s": 0.0}
    else:
        rng.bit_generator.state = state["rng"]
        arch.srng.bit_generator.state = state["srng"]
    fr = FusedRollout(g7.spec, batch, train, family=FAM)
    t0 = time.perf_counter()
    while state["gen"] < gens:
        if should_pause is not None and state["gen"] > 0 and state["gen"] % PAUSE_EVERY == 0 and should_pause():
            state.update(rng=rng.bit_generator.state, srng=arch.srng.bit_generator.state,
                         qd_wall_s=state["qd_wall_s"] + time.perf_counter() - t0)
            return {"paused": state}
        par = arch.sample(batch)
        g = g7.init(rng, batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
        fit, cells = fr.run(g)[:2]
        arch.insert(cells, fit, g7.pack(g), np.zeros((batch, 2), np.uint32))
        state["gen"] += 1
    qd_wall = state["qd_wall_s"] + time.perf_counter() - t0
    el = arch.dump()
    raw = top_raw([(v[0], v[1]) for v in el.values()], g7.glen)
    epath = pathlib.Path(elites_dir) / f"{key}.json"
    save_elites(arch, epath, [run_seed, gen_seed])
    arch.clear()
    return {"kind": "run", "world": f"w{gen_seed}", "gen_seed": gen_seed, "pressure": pressure, "run_seed": run_seed,
            "family": FAM, "genome_bytes": int(g7.glen), "param_bytes": int(g7.pb),
            "gens": gens, "batch": batch, "genomes": gens * batch, "budget_ok": (gens, batch) == (bg, bb),
            "budget_source": BUDGET_SOURCE[pressure], "train_seeds": len(train), "top": len(raw),
            "sampler_seed": sseed, "cells": len(el), "qd_wall_s": round(qd_wall, 2),
            "train_per_seed": fused_per_seed(g7, raw, train), "held64_per_seed": fused_per_seed(g7, raw, F.HELD64),
            "top_sha256": hashlib.sha256(raw.tobytes()).hexdigest(), "elites": str(epath)}


def summary(runs: list[dict]) -> dict:
    """The cell's baseline: median, M3 bootstrap CI of the median, IQR, bytes, per-run-seed values."""
    runs = sorted(runs, key=lambda x: x["run_seed"])
    v = [x["held64_per_seed"] for x in runs]
    if len(v) < MIN_RUNS:
        raise ValueError(f"{len(v)} run seeds < {MIN_RUNS}")
    lo, hi = median_ci(v)
    x0 = runs[0]
    return {"kind": "baseline", "world": x0["world"], "gen_seed": x0["gen_seed"], "pressure": x0["pressure"],
            "family": FAM, "median": float(np.median(v)), "ci95": [lo, hi],
            "iqr": float(np.percentile(v, 75) - np.percentile(v, 25)), "bytes": x0["genome_bytes"],
            "n_runs": len(v), "held64_by_run_seed": {str(x["run_seed"]): x["held64_per_seed"] for x in runs},
            "bootstrap": {"fn": "primordial.metric.ci.median_ci", "resamples": N_BOOT, "seed": BOOT_SEED},
            "budget_ok": all(x["budget_ok"] for x in runs), "genomes": x0["genomes"],
            "elites": {str(x["run_seed"]): x["elites"] for x in runs}}


def oracle_top(gen_seed: int, raw: np.ndarray, seeds=F.HELD64[:8]) -> dict:
    """E7 world oracle (wforge hash + charge) and brain oracle on the top elites; fused == numpy E7.rollout."""
    g7 = E7.G7(gen_seed, FAM)
    top = g7.unpack(raw)
    fused = FusedRollout(g7.spec, len(raw), np.asarray(seeds), family=FAM).run(top)[0]
    numpy_fit = E7.rollout(g7, top, np.asarray(seeds))[0]
    return {"world": E7.world_oracle(g7, top, np.asarray(seeds)),
            "brain": E7.brain_oracle(g7, top, np.asarray(seeds)),
            "fused_eq_numpy": bool(np.array_equal(np.asarray(fused, np.int64), np.asarray(numpy_fit, np.int64)))}


def baseline_cell(ctx, st: dict, r, gs: int, pressure: str, run_seeds, gens=None, batch=None,
                  elites_dir=str(ELITES_DIR), oracle_run_seed=0) -> list[dict]:
    """Every run seed of one (gen_seed, pressure) inside a worker job: emits a run row per run seed not yet
    in st["done"] (oracle on oracle_run_seed); on should_pause() stores the generation state in st["cur"]
    and calls ctx.pause(st)."""
    runs = []
    for rs in run_seeds:
        k = run_key(gs, pressure, int(rs))
        if k in st["done"]:
            runs.append(st["done"][k])
            continue
        cur = st["cur"]["state"] if st.get("cur") and st["cur"]["key"] == k else None
        out = baseline_run(r, gs, pressure, int(rs), gens, batch, elites_dir, ctx.should_pause, cur)
        if "paused" in out:
            st["cur"] = {"key": k, "state": out["paused"]}
            ctx.pause(st)
        if int(rs) == oracle_run_seed:
            doc = load_elites(out["elites"])
            raw = top_raw([(e[1], bytes.fromhex(e[2])) for e in doc["elites"]], doc["glen"])
            out["oracle_held8"] = oracle_top(gs, raw)
        out["status"] = "control"
        ctx.emit(out)
        st["done"][k], st["cur"] = out, None
        runs.append(out)
    return runs


def job(ctx, cells, run_seeds=tuple(range(MIN_RUNS)), gens=None, batch=None, archive_url=ARCHIVE_URL,
        elites_dir=str(ELITES_DIR), oracle_run_seed=0):
    """F7 worker job: per (gen_seed, pressure) a run row per run seed (oracle on oracle_run_seed), then one
    baseline row. Resumable (F9) between generations."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None}
    for gs, pressure in cells:
        runs = baseline_cell(ctx, st, r, int(gs), pressure, run_seeds, gens, batch, elites_dir, oracle_run_seed)
        if len(runs) >= MIN_RUNS:
            ctx.emit({**summary(runs), "status": "control"})
