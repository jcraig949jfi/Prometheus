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


FAMILIES = (4200, 2101, 3303, 5501)          # operator 16 (SWARM_R4 s9): the baseline's four RNG families
R16_MIN_RUNS, R16_MIN_FAMILIES, R16_PER_FAMILY = 32, 4, 8


def run_key(gen_seed: int, pressure: str, run_seed: int, rng_family: int | None = None) -> str:
    if rng_family is None:
        return f"g-r4-inv-w{gen_seed}-{pressure}-r{run_seed}"
    return f"g-r16-inv-w{gen_seed}-{pressure}-f{int(rng_family)}-r{run_seed}"


def seeds_of(gen_seed: int, n_train: int, run_seed: int, rng_family: int | None) -> tuple[list, list]:
    """(mutation rng seed, archive sampler seed). None = the round 4 P0 learner stream (4100/4101); a family F
    uses D-R4-2's convention [F, rs, gs, n_train] / [F+1, rs, gs, n_train]."""
    f = 4100 if rng_family is None else int(rng_family)
    return [f, run_seed, gen_seed, n_train], [f + 1, run_seed, gen_seed, n_train]


def top1_per_seed(spec: E4.Spec, arch_elites: list, seeds: np.ndarray) -> tuple[float, str]:
    """The shared readout's selection (readout.select: -train fit, genome bytes) on an open-loop archive, scored
    by the numba world: (per-seed mean on `seeds`, sha256 of the genome)."""
    from primordial.metric import readout as RO
    raw = RO.packed(RO.select(arch_elites), spec.glen)
    g = spec.unpack(raw)
    return per_seed(spec, g, seeds), hashlib.sha256(np.ascontiguousarray(raw).tobytes()).hexdigest()


def top_genomes(arch: LuaArchive, spec: E4.Spec, n: int = TOP) -> np.ndarray:
    el = arch.dump()
    best = sorted(el.values(), key=lambda v: (-v[0], v[1]))[:n]
    return spec.unpack(np.frombuffer(b"".join(v[1] for v in best), np.uint8).reshape(-1, spec.glen))


def learner_run(r, gen_seed: int, pressure: str, run_seed: int, gens: int | None = None, batch: int | None = None,
                elites_dir=ELITES_DIR, should_pause=None, state: dict | None = None,
                rng_family: int | None = None) -> dict:
    """One run seed. Returns the row, or {"paused": state} when should_pause() fired (archive kept).
    rng_family=None: the round 4 P0 stream and row (top-16 readout). A family: operator 16 run, the row carries
    rng_family and BOTH readouts -- held64_per_seed under readout.NAME (top1_train) and held64_legacy_top16."""
    spec = E4.Spec(gen_seed)
    train = F.PRESSURES[pressure]
    bg, bb = BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    key = run_key(gen_seed, pressure, run_seed, rng_family)
    rseed, sseed = seeds_of(gen_seed, len(train), run_seed, rng_family)
    arch = LuaArchive(r, key, spec.glen, sseed)
    rng = np.random.Generator(np.random.PCG64(rseed))
    if state is None:
        arch.clear()
        state = {"gen": 0, "qd_wall_s": 0.0, "qd_cpu_s": 0.0}
    else:
        rng.bit_generator.state = state["rng"]
        arch.srng.bit_generator.state = state["srng"]
    t0, c0 = time.perf_counter(), time.process_time()
    while state["gen"] < gens:
        if should_pause is not None and state["gen"] > 0 and state["gen"] % PAUSE_EVERY == 0 and should_pause():
            state.update(rng=rng.bit_generator.state, srng=arch.srng.bit_generator.state,
                         qd_wall_s=state["qd_wall_s"] + time.perf_counter() - t0,
                         qd_cpu_s=state.get("qd_cpu_s", 0.0) + time.process_time() - c0)
            return {"paused": state}
        parents = arch.sample(batch)
        kids = E4.init_genomes(rng, spec, batch) if len(parents) == 0 else E4.mutate(rng, spec, spec.unpack(parents))
        arch.insert(E4.descriptor(kids), nb_fit(spec, kids, train), spec.pack(kids), np.zeros((batch, 2), np.uint32))
        state["gen"] += 1
    qd_wall = state["qd_wall_s"] + time.perf_counter() - t0
    qd_cpu = state.get("qd_cpu_s", 0.0) + time.process_time() - c0
    top = top_genomes(arch, spec)
    el = arch.dump()
    n_cells = len(el)
    epath = pathlib.Path(elites_dir) / f"{key}.json"
    save_elites(arch, epath, [run_seed, gen_seed] if rng_family is None else [int(rng_family), run_seed, gen_seed])
    arch.clear()
    row = {"kind": "run", "world": f"w{gen_seed}", "gen_seed": gen_seed, "pressure": pressure, "run_seed": run_seed,
           "T": spec.T, "S": spec.S, "W": spec.W, "genome_bytes": spec.glen,
           "gens": gens, "batch": batch, "genomes": gens * batch, "budget_ok": (gens, batch) == (bg, bb),
           "budget_source": BUDGET_SOURCE[pressure], "train_seeds": len(train), "top": len(top),
           "sampler_seed": sseed, "cells": n_cells, "qd_wall_s": round(qd_wall, 2),
           "train_per_seed": per_seed(spec, top, train), "held64_per_seed": per_seed(spec, top, F.HELD64),
           "top_sha256": hashlib.sha256(np.ascontiguousarray(top).tobytes()).hexdigest(),
           "elites": str(epath)}
    if rng_family is not None:
        from primordial.metric import readout as RO
        h1, sha1 = top1_per_seed(spec, [(v[0], v[1]) for v in el.values()], F.HELD64)
        row.update(rng_family=int(rng_family), readout=RO.NAME, top=1, held64_legacy_top16=row["held64_per_seed"],
                   held64_per_seed=h1, top_sha256=sha1, top16_sha256=row["top_sha256"])
        from primordial.metric import search_budget as SB                # G-R6-1: search-budget accounting fields
        row.update(SB.fields(gens, batch, pressure, cpu_s=round(qd_cpu, 3), wall_s=round(qd_wall, 3)))
    return row


S_PER_T64_RUN = 320.0            # measured: E10-budget learner on w4 (T=64, S=1), 5 threads (journal, G-R4 iteration 1)


def est_hours(gen_seed: int, pressure: str = "train128_held64", runs: int = MIN_RUNS) -> float:
    """Wall-hours estimate of `runs` learner run seeds at the pressure's budget: scales with T x S and genomes x seeds."""
    spec = E4.Spec(gen_seed)
    gens, batch = BUDGET[pressure]
    work = gens * batch * len(F.PRESSURES[pressure]) / (400 * 256 * 128)
    return S_PER_T64_RUN * (spec.T * spec.S / 64) * work * runs / 3600


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


def learner_cell(ctx, st: dict, r, gs: int, pressure: str, run_seeds, gens=None, batch=None,
                 elites_dir=str(ELITES_DIR), oracle_run_seed=0, families=None) -> list[dict]:
    """Every run of one (gen_seed, pressure) inside a worker job: emits a run row per run not yet in st["done"];
    on should_pause() stores the generation state in st["cur"] and calls ctx.pause(st).
    families=None: the round 4 P0 single stream; else every family x run seed (operator 16)."""
    runs = []
    for fam in (families if families is not None else [None]):
        for rs in run_seeds:
            k = run_key(gs, pressure, int(rs), fam)
            if k in st["done"]:
                runs.append(st["done"][k])
                continue
            cur = st["cur"]["state"] if st.get("cur") and st["cur"]["key"] == k else None
            out = learner_run(r, gs, pressure, int(rs), gens, batch, elites_dir, ctx.should_pause, cur, fam)
            if "paused" in out:
                st["cur"] = {"key": k, "state": out["paused"]}
                ctx.pause(st)
            if int(rs) == oracle_run_seed and (families is None or fam == families[0]):
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
    return runs


def pooled_summary(runs: list[dict], readout: str | None = None, min_runs: int = R16_MIN_RUNS,
                   min_families: int = R16_MIN_FAMILIES, per_family: int = R16_PER_FAMILY) -> dict:
    """Operator 16 floor part: the input-invariant learner pooled over RNG families. readout=None: the rows'
    own readout (top1_train); 'm2_top16': the legacy value each R16 row also carries. Refuses fewer than
    min_runs / min_families / per_family, duplicate run ids."""
    from primordial.metric import readout as RO
    ids = [f"{int(x['rng_family'])}|{int(x['run_seed'])}" for x in runs]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate run ids in the pool")
    order = sorted(range(len(runs)), key=lambda i: (FAMILIES.index(int(runs[i]["rng_family"])), int(runs[i]["run_seed"])))
    runs, ids = [runs[i] for i in order], [ids[i] for i in order]
    fams = sorted({int(x["rng_family"]) for x in runs})
    per = {str(f): sum(int(x["rng_family"]) == f for x in runs) for f in fams}
    if len(runs) < min_runs or len(fams) < min_families or min(per.values()) < per_family:
        raise ValueError(f"LEARNER_N: {len(runs)} runs over families {per}; need >= {min_runs} runs, "
                         f">= {min_families} families x {per_family}")
    rd = readout or runs[0].get("readout", RO.NAME)
    key = "held64_legacy_top16" if rd == RO.LEGACY else "held64_per_seed"
    v = [float(x[key]) for x in runs]
    x0 = runs[0]
    from primordial.metric import sample as SM
    return {**SM.from_counts(per), "kind": "floor_invariant_r16", "world": x0["world"], "gen_seed": x0["gen_seed"],
            "pressure": x0["pressure"], "readout": rd, "invariant_held64_median": float(np.median(v)),
            "invariant_held64_iqr": float(np.percentile(v, 75) - np.percentile(v, 25)),
            "n_runs": len(v), "families": fams, "n_per_family": per, "held64_by_run": dict(zip(ids, v)),
            "run_seeds": ids, "budget_ok": all(x["budget_ok"] for x in runs), "genomes": x0["genomes"]}


def job(ctx, cells, run_seeds=tuple(range(MIN_RUNS)), gens=None, batch=None, archive_url=ARCHIVE_URL,
        elites_dir=str(ELITES_DIR), oracle_run_seed=0):
    """F7 worker job: every (gen_seed, pressure) in `cells` x run seed; one row per run seed, then one
    floor_invariant row per cell. Checkpoints between generations (F9)."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None}
    for gs, pressure in cells:
        runs = learner_cell(ctx, st, r, int(gs), pressure, run_seeds, gens, batch, elites_dir, oracle_run_seed)
        if len(runs) >= MIN_RUNS:
            ctx.emit({**summary(runs), "status": "control"})
