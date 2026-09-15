"""E-R7-2 (SWARM_R7 O2, s3): a batched GPU evaluator for the R16 cell workload, and the GPU adoption decision.

G's R16 cell_job evaluates the float linear baseline one run at a time (metric.baseline.baseline_run: per run a LuaArchive,
a mutation rng and a sampler rng). LOCKSTEP keeps every one of those per-run objects and their order of use exactly, and
changes only WHEN evaluation happens: each generation, every run samples + mutates (CPU, its own streams), ALL runs'
genomes (32 runs x 128 genomes x the train seeds) are evaluated in ONE call, then every run inserts its own slice. Runs
share no state, so each run's trajectory is the sequential one iff every evaluated fitness and cell is identical.

  evaluators   numba   soup.b6.fused.FusedRollout over the whole generation (the CPU reference path, threaded)
               gpu     nv.cudagraph.graph.GraphRollout (ticks_per_graph = T) in nv-venv-u; every generation's genomes and
                       initial world state are copied host -> device (load) and fitness/cells come back (result): h2d and
                       d2h are INSIDE the timed wall; graph capture is timed separately (compile_s).
  oracle       on a REAL cell: (1) every generation, gpu fitness AND cells == numba on the same batch (all genomes);
               (2) every run's saved elites (save_elites doc: cell, fitness, genome bytes) == G's sequential
               baseline_run elites for that run. Any miss -> INSTRUMENT_FAIL and no timing row.
  timing       baseline stage of the cell (the only stage evaluation batching touches), median of `reps` whole stages:
               cpu_sequential (G's baseline_run loop, numba threads t), cpu_lockstep (numba, t), gpu_lockstep. Same
               estimator on every side. cells/hour = 3600 / stage wall.
  decision     GPU_ADOPT iff oracle clean on EVERY measured cell AND gpu cells/hour >= 1.25 x best CPU cells/hour on EVERY
               measured cell (>= 1 cell measured); else GPU_REJECT. A cell whose one-batch generation does not fit VRAM is a
               DEVICE_OOM row (not measured, not adopted). decide() recomputes from rows; set_decision writes pm:r7:gpu_adopt.

    GPU job (gpuq, venv u):  fn primordial.nv.r7_gpu_eval:cell_job  kwargs {"gen_seed": 13, "pressure": "train8_held64"}
    python -m primordial.nv.r7_gpu_eval decide --rows primordial/ledger/rows/E/E-R7-2-gpu-eval.jsonl [--write]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import statistics
import tempfile
import time

import numpy as np

ARCHIVE_URL = "redis://127.0.0.1:6394/5"        # E's own db: never G's R16 keys (db 0)
ADOPT_KEY = "pm:r7:gpu_adopt"
RATIO_MIN = 1.25
FAMILIES = (4200, 2101, 3303, 5501)
RUN_SEEDS = tuple(range(8))
ADOPT, REJECT = "GPU_ADOPT", "GPU_REJECT"


def _key(tag: str, gs: int, pressure: str, fam: int, rs: int) -> str:
    return f"e-r7-{tag}-w{gs}-{pressure}-f{fam}-r{rs}"


def elites_digest(doc: dict) -> str:
    """sha256 over a save_elites doc's elites sorted by cell: (cell, fitness, genome hex)."""
    items = sorted((int(e[0]), int(e[1]), str(e[2])) for e in doc["elites"])
    return hashlib.sha256(json.dumps(items).encode()).hexdigest()


def concat(gl: list):
    """[((W, b), C) per run] -> one generation ((W, b), C), runs in order."""
    return ((np.concatenate([g[0][0] for g in gl]), np.concatenate([g[0][1] for g in gl])),
            np.concatenate([g[1] for g in gl]))


def numba_evaluator(g7, n_genomes: int, train):
    from primordial.soup.b6.fused import FusedRollout
    fr = FusedRollout(g7.spec, n_genomes, np.asarray(train, np.int64), family="linear")
    return lambda g: fr.run(g)[:2]


def gpu_evaluator(g7, train):
    import torch
    from primordial.nv.cudagraph.graph import GraphRollout
    gr = GraphRollout(g7, "cuda", ticks_per_graph=g7.T)
    seeds = np.asarray(train, np.int64)

    def ev(g):
        gr.load(g, seeds)
        fit, cells = gr.replay()
        torch.cuda.synchronize()
        return fit, cells
    return ev


def lockstep(r, gen_seed: int, pressure: str, evaluate, families=FAMILIES, run_seeds=RUN_SEEDS, gens=None, batch=None,
             tag: str = "lock", check=None, elites_dir=None) -> dict:
    """All runs of one cell stepped together; one evaluate() per generation. -> {digests: {run_id: sha}, wall_s, evals}."""
    from primordial.metric import baseline as B
    from primordial.metric import floors as F
    from primordial.qd import e7_run as E7
    from primordial.qd.archive import LuaArchive, save_elites
    g7 = E7.G7(int(gen_seed), "linear")
    train = F.PRESSURES[pressure]
    bg, bb = B.BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    runs = []
    for fam in families:
        for rs in run_seeds:
            rseed, sseed = B.seeds_of(int(gen_seed), len(train), int(rs), int(fam))
            a = LuaArchive(r, _key(tag, gen_seed, pressure, fam, rs), g7.glen, sseed)
            a.clear()
            runs.append((f"{int(fam)}|{int(rs)}", a, np.random.Generator(np.random.PCG64(rseed)), int(fam), int(rs)))
    t0 = time.perf_counter()
    for gen in range(gens):
        gl = []
        for _, a, rng, _, _ in runs:
            par = a.sample(batch)
            gl.append(g7.init(rng, batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par)))
        g = concat(gl)
        fit, cells = evaluate(g)
        if check is not None:
            check(gen, g, fit, cells)
        (W, b), C = g
        for i, (_, a, _, _, _) in enumerate(runs):
            s = slice(i * batch, (i + 1) * batch)
            a.insert(np.asarray(cells[s]), np.asarray(fit[s]), g7.pack(((W[s], b[s]), C[s])), np.zeros((batch, 2), np.uint32))
    wall = time.perf_counter() - t0
    digests = {}
    tmp = pathlib.Path(elites_dir or tempfile.mkdtemp(prefix="e_r7_lock_"))
    for rid, a, _, fam, rs in runs:
        doc = save_elites(a, tmp / f"{rid.replace('|', '-')}.json", [fam, rs, int(gen_seed)])
        digests[rid] = elites_digest(doc)
        a.clear()
    return {"digests": digests, "wall_s": wall, "gens": gens, "batch": batch, "runs": len(runs),
            "evals_per_gen": len(runs) * batch * len(train)}


def sequential(r, gen_seed: int, pressure: str, families=FAMILIES, run_seeds=RUN_SEEDS, gens=None, batch=None,
               elites_dir=None) -> dict:
    """G's own loop: metric.baseline.baseline_run per run (its keys, streams, readout, elites file)."""
    from primordial.metric import baseline as B
    from primordial.qd.archive import load_elites
    tmp = elites_dir or tempfile.mkdtemp(prefix="e_r7_seq_")
    digests, t0 = {}, time.perf_counter()
    for fam in families:
        for rs in run_seeds:
            row = B.baseline_run(r, int(gen_seed), pressure, int(rs), gens, batch, tmp, None, None, int(fam))
            digests[f"{int(fam)}|{int(rs)}"] = elites_digest(load_elites(row["elites"]))
    return {"digests": digests, "wall_s": time.perf_counter() - t0}


def _timing(question_cell: dict, backend: str, walls: list, comparison: str, **extra) -> dict:
    return {"kind": "timing", "backend": backend, "wall_s": float(statistics.median(walls)),
            "walls_s": [round(w, 4) for w in walls], "reps": len(walls),
            "cells_per_hour": 3600.0 / float(statistics.median(walls)), "transfer_included": backend.startswith("gpu"),
            "warm_state": "warm", "comparison_backend": comparison, "exactness": "PASS", **question_cell, **extra}


def cell_job(emit, gen_seed: int = 13, pressure: str = "train8_held64", families=FAMILIES, run_seeds=RUN_SEEDS,
             gens=None, batch=None, reps: int = 3, threads: int = 8, archive_url: str = ARCHIVE_URL,
             lease_s: float = 600.0, checkpoint_path=None):
    os.environ.setdefault("NUMBA_NUM_THREADS", str(int(threads)))
    import numba
    import redis
    import torch
    from primordial.metric import baseline as B
    from primordial.metric import floors as F
    from primordial.qd import e7_run as E7
    torch.set_num_threads(1)
    numba.set_num_threads(min(int(threads), numba.config.NUMBA_NUM_THREADS))
    r = redis.Redis.from_url(archive_url)
    g7 = E7.G7(int(gen_seed), "linear")
    train = F.PRESSURES[pressure]
    bg, bb = B.BUDGET[pressure]
    gens_, batch_ = gens or bg, batch or bb
    n_runs = len(families) * len(run_seeds)
    cell = {"question": "E-R7-2", "world": f"w{int(gen_seed)}", "gen_seed": int(gen_seed), "pressure": pressure,
            "runs": n_runs, "gens": gens_, "batch_size": n_runs * batch_ * len(train), "genomes_per_gen": n_runs * batch_,
            "train_seeds": len(train), "T": int(g7.T), "numba_threads": numba.get_num_threads(),
            "families": [int(f) for f in families], "run_seeds": [int(s) for s in run_seeds]}
    # ---- evaluators (compile / capture timed apart)
    t0 = time.perf_counter()
    ev_numba = numba_evaluator(g7, n_runs * batch_, train)
    probe = concat([g7.init(np.random.Generator(np.random.PCG64([7707, i])), batch_) for i in range(n_runs)])
    ev_numba(probe)
    numba_init_s = time.perf_counter() - t0
    try:
        t0 = time.perf_counter()
        ev_gpu = gpu_evaluator(g7, train)
        ev_gpu(probe)
        gpu_capture_s = time.perf_counter() - t0
    except torch.OutOfMemoryError as e:                                       # noqa: PERF203
        emit({"kind": "device_oom", "status": "control", **cell, "error": str(e)[:300],
              "note": "one device batch per generation does not fit VRAM: cell not measured, not adopted"})
        return
    # ---- projection from one warm generation of each evaluator: refuse (a row) rather than die at the lease cap
    reps_t = []
    for ev in (ev_numba, ev_gpu):
        t0 = time.perf_counter()
        ev(probe)
        reps_t.append(time.perf_counter() - t0)
    tn, tg = reps_t
    projected = gens_ * (tg + 2 * tn) + int(reps) * gens_ * (tg + 3 * tn)
    cell.update(probe_gen_s_numba=round(tn, 5), probe_gen_s_gpu=round(tg, 5), projected_job_s=round(projected, 1))
    if projected > float(lease_s) * 0.8:
        emit({"kind": "projected_over_lease", "status": "control", **cell, "lease_s": lease_s,
              "note": "oracle + timing projected past 80% of the GPU lease segment: cell not measured, not adopted"})
        return
    # ---- oracle 1: reference = G's sequential loop; oracle 2: gpu lockstep with a numba check every generation
    seq = sequential(r, gen_seed, pressure, families, run_seeds, gens, batch)
    bad = {"gens": 0, "fitness": 0, "cells": 0}

    def check(gen, g, fit, cells):
        rf, rc = ev_numba(g)
        nf, nc = int((np.asarray(fit) != np.asarray(rf)).sum()), int((np.asarray(cells) != np.asarray(rc)).sum())
        bad["fitness"] += nf
        bad["cells"] += nc
        bad["gens"] += int(nf + nc > 0)

    lock = lockstep(r, gen_seed, pressure, ev_gpu, families, run_seeds, gens, batch, tag="gpuoracle", check=check)
    elite_miss = sorted(k for k in seq["digests"] if lock["digests"].get(k) != seq["digests"][k])
    exact = bad["fitness"] == 0 and bad["cells"] == 0 and not elite_miss and len(lock["digests"]) == n_runs
    emit({"kind": "oracle", "status": "control", **cell, "exactness": "PASS" if exact else "FAIL",
          "evaluations_checked": gens_ * n_runs * batch_, "fitness_mismatch": bad["fitness"], "cells_mismatch": bad["cells"],
          "generations_with_mismatch": bad["gens"], "runs_elites_identical": n_runs - len(elite_miss),
          "runs_elites_mismatch": elite_miss, "reference": "metric.baseline.baseline_run (sequential, G's loop)",
          "numba_init_s": round(numba_init_s, 3), "gpu_capture_s": round(gpu_capture_s, 3),
          "device": torch.cuda.get_device_name()})
    if not exact:
        emit({"kind": "verdict", "status": "control", **cell, "verdict": "INSTRUMENT_FAIL", "throughput": None})
        return
    # ---- timing: median of reps of the whole baseline stage, same estimator on every side
    walls = {"cpu_sequential": [], "cpu_lockstep": [], "gpu_lockstep": []}
    for _ in range(int(reps)):
        walls["cpu_sequential"].append(sequential(r, gen_seed, pressure, families, run_seeds, gens, batch)["wall_s"])
        walls["cpu_lockstep"].append(lockstep(r, gen_seed, pressure, ev_numba, families, run_seeds, gens, batch, tag="cpu")["wall_s"])
        walls["gpu_lockstep"].append(lockstep(r, gen_seed, pressure, ev_gpu, families, run_seeds, gens, batch, tag="gpu")["wall_s"])
    best_cpu = min(("cpu_sequential", "cpu_lockstep"), key=lambda k: statistics.median(walls[k]))
    for k, w in walls.items():
        emit(_timing(cell, k, w, best_cpu if k.startswith("gpu") else "gpu_lockstep", status="record",
                     compile_s=round(gpu_capture_s if k.startswith("gpu") else numba_init_s, 3)))
    ratio = statistics.median(walls[best_cpu]) / statistics.median(walls["gpu_lockstep"])
    emit({"kind": "cell_ratio", "status": "record", **cell, "best_cpu": best_cpu, "ratio_gpu_over_best_cpu": ratio,
          "rule": f"cells/hour gpu / best cpu >= {RATIO_MIN}", "meets": ratio >= RATIO_MIN})


def decide(rows: list[dict]) -> dict:
    """GPU_ADOPT iff >= 1 measured cell, every oracle row clean, and every measured cell's ratio >= RATIO_MIN."""
    oracles = [x for x in rows if x.get("kind") == "oracle"]
    ratios = [x for x in rows if x.get("kind") == "cell_ratio"]
    fails = [x for x in rows if x.get("kind") == "verdict" and x.get("verdict") == "INSTRUMENT_FAIL"]
    ooms = [f"{x['world']} {x['pressure']}" for x in rows if x.get("kind") == "device_oom"]
    clean = bool(oracles) and all(x.get("exactness") == "PASS" for x in oracles) and not fails
    cells = {f"{x['world']} {x['pressure']}": float(x["ratio_gpu_over_best_cpu"]) for x in ratios}
    ok = clean and bool(cells) and all(v >= RATIO_MIN for v in cells.values())
    return {"decision": ADOPT if ok else REJECT, "oracle_clean": clean, "ratios": cells, "ratio_min": RATIO_MIN,
            "device_oom_cells": ooms, "rule": "SWARM_R7 O2: oracle 100% clean AND end-to-end >= 1.25x best CPU on every measured cell"}


def set_decision(r, doc: dict, rows_ref: str) -> dict:
    rec = dict(doc, rows=rows_ref, ts=round(time.time(), 3), writer="primordial.nv.r7_gpu_eval.decide")
    r.set(ADOPT_KEY, json.dumps(rec, sort_keys=True))
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide")
    d.add_argument("--rows", required=True)
    d.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in pathlib.Path(a.rows).read_text(encoding="utf-8").splitlines() if l.strip()]
    doc = decide(rows)
    if a.write:
        from primordial.bus import bus
        doc = set_decision(bus.conn(), doc, a.rows)
    print(json.dumps(doc, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
