"""M2 / G-R4-3 stage 2 (round 4 P0, builder G): the FLOAT LINEAR BASELINE, re-seeded.

The round 1 baseline a clause A candidate is judged against, re-run with >= 8 run seeds, a seeded archive
sampler and the elites of every run seed saved (C2), at round 1's budget:

  pressure          TRAIN seeds       budget (gens x batch)   round 1 source of the budget
  train8_held64     9100..9107        200 x 128 = 25,600      E9 linear (E7.G7 + FusedRollout)
  train128_held64   9100..9227        800 x 128 = 102,400     E10 closed linear

Genome: E7.G7(gen_seed, "linear") -- lane C's linear params + lane E's A x W action codebook; bytes =
g7.glen (packed genome, codebook included). Per run seed: the value under THE shared readout
(primordial.metric.readout, operator 15 R15-1: top-1 elite by train fitness, per-seed mean on HELD64), stamped
`readout` on every row. Rows written before R15-1 used top-16 (readout.LEGACY; top_raw is kept to reproduce
them). The cell's baseline: median over run seeds, the bootstrap 95% CI of that median (M3,
primordial.metric.ci.median_ci), and the bytes. `reread` re-reads a saved archive (no QD).

Operator 16 (SWARM_R4 s9): >= 32 run seeds pooled over 4 RNG families, 8 each. A family F fixes the whole run:
mutation rng PCG64([F, rs, gs, n_train]) and archive sampler PCG64([F+1, rs, gs, n_train]) -- D-R4-2's
convention; F=4200 is exactly the stream the 8-seed M2 rows used. `rng_family=None` keeps the v1 key and paths
(reproduces committed rows); an explicit family gets its own run key, stamped `rng_family` on the row.

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
from primordial.metric import readout as RO
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
FAMILIES = (4200, 2101, 3303, 5501)          # operator 16: G's M2 stream first, then D-R4-2's
R16_MIN_RUNS, R16_MIN_FAMILIES, R16_PER_FAMILY = 32, 4, 8
PAUSE_EVERY = 25
ARCHIVE_URL = "redis://127.0.0.1:6394/0"
ELITES_DIR = pathlib.Path("C:/Users/jcrai/lab/pm-data/G") / EXP


def run_key(gen_seed: int, pressure: str, run_seed: int, rng_family: int | None = None) -> str:
    if rng_family is None:
        return f"g-r4-base-w{gen_seed}-{pressure}-r{run_seed}"
    return f"g-r16-base-w{gen_seed}-{pressure}-f{int(rng_family)}-r{run_seed}"


def seeds_of(gen_seed: int, n_train: int, run_seed: int, rng_family: int | None) -> tuple[list, list]:
    """(mutation rng seed, archive sampler seed). None = the v1 M2 stream, identical to family 4200."""
    f = 4200 if rng_family is None else int(rng_family)
    return [f, run_seed, gen_seed, n_train], [f + 1, run_seed, gen_seed, n_train]


def fused_per_seed(g7: E7.G7, raw: np.ndarray, seeds: np.ndarray) -> float:
    """E9.fused_score: mean over genomes of the per-seed held score."""
    fit = FusedRollout(g7.spec, len(raw), seeds, family=FAM).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def top_raw(elites: list, glen: int, n: int = TOP) -> np.ndarray:
    """elites: [(fit, genome bytes)] -> the n best by (-fit, genome bytes), packed [n, glen]. LEGACY readout (n=16)
    and the oracle's top-16; the baseline value itself comes from readout.read."""
    best = sorted(elites, key=lambda v: (-v[0], v[1]))[:n]
    return np.frombuffer(b"".join(g for _, g in best), np.uint8).reshape(-1, glen)


def baseline_run(r, gen_seed: int, pressure: str, run_seed: int, gens: int | None = None,
                 batch: int | None = None, elites_dir=ELITES_DIR, should_pause=None, state: dict | None = None,
                 rng_family: int | None = None) -> dict:
    """One run seed. Returns the row, or {"paused": state} when should_pause() fired (archive kept)."""
    g7 = E7.G7(gen_seed, FAM)
    train = F.PRESSURES[pressure]
    bg, bb = BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    key = run_key(gen_seed, pressure, run_seed, rng_family)
    rseed, sseed = seeds_of(gen_seed, len(train), run_seed, rng_family)
    arch = LuaArchive(r, key, g7.glen, sseed)
    rng = np.random.Generator(np.random.PCG64(rseed))
    if state is None:
        arch.clear()
        state = {"gen": 0, "qd_wall_s": 0.0, "qd_cpu_s": 0.0}
    else:
        rng.bit_generator.state = state["rng"]
        arch.srng.bit_generator.state = state["srng"]
    fr = FusedRollout(g7.spec, batch, train, family=FAM)
    t0, c0 = time.perf_counter(), time.process_time()
    while state["gen"] < gens:
        if should_pause is not None and state["gen"] > 0 and state["gen"] % PAUSE_EVERY == 0 and should_pause():
            state.update(rng=rng.bit_generator.state, srng=arch.srng.bit_generator.state,
                         qd_wall_s=state["qd_wall_s"] + time.perf_counter() - t0,
                         qd_cpu_s=state.get("qd_cpu_s", 0.0) + time.process_time() - c0)
            return {"paused": state}
        par = arch.sample(batch)
        g = g7.init(rng, batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
        fit, cells = fr.run(g)[:2]
        arch.insert(cells, fit, g7.pack(g), np.zeros((batch, 2), np.uint32))
        state["gen"] += 1
    qd_wall = state["qd_wall_s"] + time.perf_counter() - t0
    qd_cpu = state.get("qd_cpu_s", 0.0) + time.process_time() - c0      # process CPU: every numba thread of the child
    el = arch.dump()
    pairs = [(v[0], v[1]) for v in el.values()]
    raw = RO.packed(RO.select(pairs), g7.glen)
    epath = pathlib.Path(elites_dir) / f"{key}.json"
    save_elites(arch, epath, [run_seed, gen_seed] if rng_family is None else [int(rng_family), run_seed, gen_seed])
    arch.clear()
    row = {"kind": "run", "world": f"w{gen_seed}", "gen_seed": gen_seed, "pressure": pressure, "run_seed": run_seed,
           "family": FAM, "genome_bytes": int(g7.glen), "param_bytes": int(g7.pb),
           "gens": gens, "batch": batch, "genomes": gens * batch, "budget_ok": (gens, batch) == (bg, bb),
           "budget_source": BUDGET_SOURCE[pressure], "train_seeds": len(train), "readout": RO.NAME, "top": len(raw),
           "sampler_seed": sseed, "cells": len(el), "qd_wall_s": round(qd_wall, 2),
           "train_per_seed": fused_per_seed(g7, raw, train), "held64_per_seed": fused_per_seed(g7, raw, F.HELD64),
           "top_sha256": hashlib.sha256(raw.tobytes()).hexdigest(), "elites": str(epath)}
    if rng_family is not None:
        row["rng_family"] = int(rng_family)
        row["held64_legacy_top16"] = fused_per_seed(g7, top_raw(pairs, g7.glen), F.HELD64)   # D-R4-2 cross-check only
        from primordial.metric import search_budget as SB                # G-R6-1: search-budget accounting fields
        row.update(SB.fields(gens, batch, pressure, cpu_s=round(qd_cpu, 3), wall_s=round(qd_wall, 3)))
    return row


def reread(gen_seed: int, elites_path) -> dict:
    """One saved M2 archive under the shared readout (rows only, no QD): {readout, held64_per_seed, ...}."""
    return RO.read_doc(load_elites(elites_path), RO.linear_scorer(gen_seed))


def summary(runs: list[dict]) -> dict:
    """The cell's baseline: median, M3 bootstrap CI of the median, IQR, bytes, per-run-seed values, readout.
    Refuses run rows read under different readouts."""
    runs = sorted(runs, key=lambda x: x["run_seed"])
    kinds = {x.get("readout", RO.LEGACY) for x in runs}
    if len(kinds) != 1:
        raise ValueError(f"run rows mix readouts {sorted(kinds)}")
    v = [x["held64_per_seed"] for x in runs]
    if len(v) < MIN_RUNS:
        raise ValueError(f"{len(v)} run seeds < {MIN_RUNS}")
    lo, hi = median_ci(v)
    x0 = runs[0]
    return {"kind": "baseline", "world": x0["world"], "gen_seed": x0["gen_seed"], "pressure": x0["pressure"],
            "family": FAM, "readout": kinds.pop(), "median": float(np.median(v)), "ci95": [lo, hi],
            "iqr": float(np.percentile(v, 75) - np.percentile(v, 25)), "bytes": x0["genome_bytes"],
            "n_runs": len(v), "held64_by_run_seed": {str(x["run_seed"]): x["held64_per_seed"] for x in runs},
            "bootstrap": {"fn": "primordial.metric.ci.median_ci", "resamples": N_BOOT, "seed": BOOT_SEED},
            "budget_ok": all(x["budget_ok"] for x in runs), "genomes": x0["genomes"],
            "elites": {str(x["run_seed"]): x["elites"] for x in runs}}


def run_id(x: dict) -> str:
    return f"{int(x['rng_family'])}|{int(x['run_seed'])}"


def pooled_stats(runs: list[dict], min_runs: int = R16_MIN_RUNS, min_families: int = R16_MIN_FAMILIES,
                 per_family: int = R16_PER_FAMILY) -> dict:
    """Operator 16: the pooled value of runs across RNG families (run_id 'F|rs'), in (family, run seed) order.
    Refuses fewer than min_runs runs, fewer than min_families families, a family with fewer than per_family runs,
    a duplicate run id, or mixed readouts."""
    runs = sorted(runs, key=lambda x: (FAMILIES.index(int(x["rng_family"])) if int(x["rng_family"]) in FAMILIES
                                       else len(FAMILIES) + int(x["rng_family"]), int(x["run_seed"])))
    ids = [run_id(x) for x in runs]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate run ids in the pool")
    kinds = {x.get("readout", RO.LEGACY) for x in runs}
    if len(kinds) != 1:
        raise ValueError(f"run rows mix readouts {sorted(kinds)}")
    fams = sorted({int(x["rng_family"]) for x in runs})
    per = {str(f): sum(int(x["rng_family"]) == f for x in runs) for f in fams}
    if len(runs) < min_runs or len(fams) < min_families or min(per.values()) < per_family:
        raise ValueError(f"BASELINE_N: {len(runs)} runs over families {per}; need >= {min_runs} runs, "
                         f">= {min_families} families x {per_family}")
    v = [x["held64_per_seed"] for x in runs]
    lo, hi = median_ci(v)
    from primordial.metric import sample as SM
    return {**SM.from_counts(per), "readout": kinds.pop(), "median": float(np.median(v)), "ci95": [lo, hi],
            "iqr": float(np.percentile(v, 75) - np.percentile(v, 25)), "n_runs": len(v), "families": fams,
            "n_per_family": per, "held64_by_run": dict(zip(ids, v)),
            "bootstrap": {"fn": "primordial.metric.ci.median_ci", "resamples": N_BOOT, "seed": BOOT_SEED,
                          "order": "family (4200, 2101, 3303, 5501) then run seed"}}


def pooled_summary(runs: list[dict], **kw) -> dict:
    """The cell's R16 baseline row (kind baseline_r16)."""
    s = pooled_stats(runs, **kw)
    x0 = runs[0]
    return {"kind": "baseline_r16", "world": x0["world"], "gen_seed": x0["gen_seed"], "pressure": x0["pressure"],
            "family": FAM, **s, "bytes": x0["genome_bytes"], "budget_ok": all(x["budget_ok"] for x in runs),
            "genomes": x0["genomes"], "elites": {run_id(x): x["elites"] for x in runs}}


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
                  elites_dir=str(ELITES_DIR), oracle_run_seed=0, families=None) -> list[dict]:
    """Every run of one (gen_seed, pressure) inside a worker job: emits a run row per run not yet in st["done"]
    (oracle on the first family's oracle_run_seed); on should_pause() stores the generation state in st["cur"]
    and calls ctx.pause(st). families=None: the v1 single stream (no rng_family); else every family x run seed."""
    runs = []
    for fam in (families if families is not None else [None]):
        for rs in run_seeds:
            k = run_key(gs, pressure, int(rs), fam)
            if k in st["done"]:
                runs.append(st["done"][k])
                continue
            cur = st["cur"]["state"] if st.get("cur") and st["cur"]["key"] == k else None
            out = baseline_run(r, gs, pressure, int(rs), gens, batch, elites_dir, ctx.should_pause, cur, fam)
            if "paused" in out:
                st["cur"] = {"key": k, "state": out["paused"]}
                ctx.pause(st)
            if int(rs) == oracle_run_seed and (families is None or fam == families[0]):
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
