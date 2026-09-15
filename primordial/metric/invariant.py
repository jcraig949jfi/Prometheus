"""G-R4-1 (round 4 P0, builder G): the INPUT-INVARIANT LEARNER floor.

The E4 open-loop action tensor [T, S, W] (values in [0, 16), the world reads action % 8) is a policy
whose observations are never read: every env of one genome gets the same action sequence. It is the
class lane B's 8-byte int2 brains fell into. Here it is EVOLVED, at the round 1 baseline's budget:

  pressure          TRAIN seeds       budget (gens x batch)   round 1 source of the budget
  train8_held64     9100..9107        100 x 256 = 25,600      E6 open-loop (E4b QD on NbEncounter)
  train128_held64   9100..9227        400 x 256 = 102,400     E10 open-loop (E8.open_condition)

Search = E4b's MAP-Elites exactly (E4.init_genomes / E4.mutate / E4.descriptor, NbEncounter fitness),
except the archive sampler is SEEDED (C2) and the elites of every run seed are saved. Per run seed the
value is round 1's: the top-16 elites by train fitness, per-seed mean on HELD64 (E8.open_score).
The floor part is the median over >= 8 run seeds.

A long run checkpoints (F9): `should_pause()` is polled every PAUSE_EVERY generations; the archive stays
in Redis, the generation index and both RNG states go into the checkpoint.

    python -m primordial.fabric.worker submit G primordial.metric.invariant:job --exp G-R4-1-invariant-learner \\
        --rows primordial/ledger/rows/G/G-R4-1-invariant-learner.jsonl --ttl-cpu-s S \\
        --kwargs '{"cells": [[4, "train8_held64"]], "run_seeds": [0,1,2,3,4,5,6,7]}'
"""
from __future__ import annotations

import contextlib
import hashlib
import pathlib
import time

import numpy as np

from primordial.metric import floors as F
from primordial.qd import e4_run as E4
from primordial.qd.archive import LuaArchive, save_elites
from primordial.soup.b1.nb_world import NbEncounter

EXP = "G-R4-1-invariant-learner"
BUDGET = {"train8_held64": (100, 256), "train128_held64": (400, 256)}
BUDGET_SOURCE = {"train8_held64": "E6-heldout-seed-generalisation open_genomes",
                 "train128_held64": "E10-linear-closed-vs-open-128-seeds open_genomes"}
TOP = 16
MIN_RUNS = 8
PAUSE_EVERY = 10
ARCHIVE_URL = "redis://127.0.0.1:6394/0"         # round 1's archive substrate; keys pm:qd:g-r4-inv-*
ELITES_DIR = pathlib.Path("C:/Users/jcrai/lab/pm-data/G") / EXP


def nb_fit(spec: E4.Spec, G: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    """Summed clipped final charge over `seeds` per genome [P] (int64); E4b.nb_evaluate with explicit seeds."""
    P, k = len(G), len(seeds)
    w = NbEncounter(spec.mech, spec.wid)
    w.prepare(np.tile(seeds, P), log=True)
    acts = np.ascontiguousarray(np.repeat(G, k, axis=0).transpose(1, 0, 2, 3)).astype(np.int32)
    w.run(acts)
    ep = np.clip(w.log_charge[w.done_tick - 1, np.arange(P * k)], 0, None)
    return ep.sum(1).reshape(P, k).sum(1).astype(np.int64)


def per_seed(spec: E4.Spec, G: np.ndarray, seeds: np.ndarray) -> float:
    """Mean over genomes of the per-seed score (E8.open_score, numba world)."""
    return float(nb_fit(spec, G, seeds).mean() / len(seeds))


@contextlib.contextmanager
def e4_seeds(seeds):
    """E4.evaluate / E4.oracle read the module global SEEDS; set it for the block and restore it."""
    old = E4.SEEDS
    E4.SEEDS = np.asarray(seeds, np.int64)
    try:
        yield
    finally:
        E4.SEEDS = old


def run_key(gen_seed: int, pressure: str, run_seed: int) -> str:
    return f"g-r4-inv-w{gen_seed}-{pressure}-r{run_seed}"


def top_genomes(arch: LuaArchive, spec: E4.Spec, n: int = TOP) -> np.ndarray:
    el = arch.dump()
    best = sorted(el.values(), key=lambda v: (-v[0], v[1]))[:n]
    return spec.unpack(np.frombuffer(b"".join(v[1] for v in best), np.uint8).reshape(-1, spec.glen))


def learner_run(r, gen_seed: int, pressure: str, run_seed: int, gens: int | None = None, batch: int | None = None,
                elites_dir=ELITES_DIR, should_pause=None, state: dict | None = None) -> dict:
    """One run seed. Returns the row, or {"paused": state} when should_pause() fired (archive kept)."""
    spec = E4.Spec(gen_seed)
    train = F.PRESSURES[pressure]
    bg, bb = BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    key = run_key(gen_seed, pressure, run_seed)
    sseed = [4101, run_seed, gen_seed, len(train)]
    arch = LuaArchive(r, key, spec.glen, sseed)
    rng = np.random.Generator(np.random.PCG64([4100, run_seed, gen_seed, len(train)]))
    if state is None:
        arch.clear()
        state = {"gen": 0, "qd_wall_s": 0.0}
    else:
        rng.bit_generator.state = state["rng"]
        arch.srng.bit_generator.state = state["srng"]
    t0 = time.perf_counter()
    while state["gen"] < gens:
        if should_pause is not None and state["gen"] > 0 and state["gen"] % PAUSE_EVERY == 0 and should_pause():
            state.update(rng=rng.bit_generator.state, srng=arch.srng.bit_generator.state,
                         qd_wall_s=state["qd_wall_s"] + time.perf_counter() - t0)
            return {"paused": state}
        parents = arch.sample(batch)
        kids = E4.init_genomes(rng, spec, batch) if len(parents) == 0 else E4.mutate(rng, spec, spec.unpack(parents))
        arch.insert(E4.descriptor(kids), nb_fit(spec, kids, train), spec.pack(kids), np.zeros((batch, 2), np.uint32))
        state["gen"] += 1
    qd_wall = state["qd_wall_s"] + time.perf_counter() - t0
    top = top_genomes(arch, spec)
    n_cells = len(arch.dump())
    epath = pathlib.Path(elites_dir) / f"{key}.json"
    save_elites(arch, epath, [run_seed, gen_seed])
    arch.clear()
    return {"kind": "run", "world": f"w{gen_seed}", "gen_seed": gen_seed, "pressure": pressure, "run_seed": run_seed,
            "T": spec.T, "S": spec.S, "W": spec.W, "genome_bytes": spec.glen,
            "gens": gens, "batch": batch, "genomes": gens * batch, "budget_ok": (gens, batch) == (bg, bb),
            "budget_source": BUDGET_SOURCE[pressure], "train_seeds": len(train), "top": len(top),
            "sampler_seed": sseed, "cells": n_cells, "qd_wall_s": round(qd_wall, 2),
            "train_per_seed": per_seed(spec, top, train), "held64_per_seed": per_seed(spec, top, F.HELD64),
            "top_sha256": hashlib.sha256(np.ascontiguousarray(top).tobytes()).hexdigest(),
            "elites": str(epath)}


def floor_part(values) -> float:
    """The G-R4-1 floor: median of the per-run-seed held64 values over >= MIN_RUNS run seeds."""
    v = [float(x) for x in values]
    if len(v) < MIN_RUNS:
        raise ValueError(f"{len(v)} run seeds < {MIN_RUNS}")
    return float(np.median(v))


def summary(runs: list[dict]) -> dict:
    v = [x["held64_per_seed"] for x in sorted(runs, key=lambda x: x["run_seed"])]
    x0 = runs[0]
    return {"kind": "floor_invariant", "world": x0["world"], "gen_seed": x0["gen_seed"], "pressure": x0["pressure"],
            "run_seeds": sorted(x["run_seed"] for x in runs), "held64_by_run_seed": v,
            "invariant_held64_median": floor_part(v),
            "invariant_held64_iqr": float(np.percentile(v, 75) - np.percentile(v, 25)),
            "budget_ok": all(x["budget_ok"] for x in runs), "genomes": x0["genomes"]}


def oracle_top(gen_seed: int, top: np.ndarray, seeds=F.HELD64[:8]) -> dict:
    """wforge trace hash + charge on the top elites (E4.oracle) and numba == numpy fitness."""
    spec = E4.Spec(gen_seed)
    with e4_seeds(seeds):
        o = E4.oracle(spec, top, "")
        o["nb_np_fitness_equal"] = bool(np.array_equal(nb_fit(spec, top, np.asarray(seeds)), E4.evaluate(spec, top)[0]))
    return o


def job(ctx, cells, run_seeds=tuple(range(MIN_RUNS)), gens=None, batch=None, archive_url=ARCHIVE_URL,
        elites_dir=str(ELITES_DIR), oracle_run_seed=0):
    """F7 worker job: every (gen_seed, pressure) in `cells` x run seed; one row per run seed, then one
    floor_invariant row per cell. Checkpoints between generations (F9)."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None}
    for gs, pressure in cells:
        gs = int(gs)
        runs = []
        for rs in run_seeds:
            k = run_key(gs, pressure, int(rs))
            if k in st["done"]:
                runs.append(st["done"][k])
                continue
            cur = st["cur"]["state"] if st["cur"] and st["cur"]["key"] == k else None
            out = learner_run(r, gs, pressure, int(rs), gens, batch, elites_dir, ctx.should_pause, cur)
            if "paused" in out:
                st["cur"] = {"key": k, "state": out["paused"]}
                ctx.pause(st)
            if int(rs) == oracle_run_seed:
                from primordial.qd.archive import load_elites
                doc = load_elites(out["elites"])
                spec = E4.Spec(gs)
                best = sorted(doc["elites"], key=lambda e: (-e[1], e[2]))[:TOP]
                top = spec.unpack(np.frombuffer(bytes.fromhex("".join(e[2] for e in best)), np.uint8)
                                  .reshape(-1, spec.glen))
                out["oracle_held8"] = oracle_top(gs, top)
            out["status"] = "control"
            ctx.emit(out)
            st["done"][k], st["cur"] = out, None
            runs.append(out)
        if len(runs) >= MIN_RUNS:
            ctx.emit({**summary(runs), "status": "control"})
