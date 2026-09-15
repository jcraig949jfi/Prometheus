"""E-R7-2 (SWARM_R7 O2 + O2', s3): batched evaluation for the R16 cell workload, and the backend adoption decision.

G's R16 cell_job evaluates the float linear baseline one run at a time (metric.baseline.baseline_run: per run a LuaArchive,
a mutation rng and a sampler rng). LOCKSTEP keeps every one of those per-run objects and their order of use exactly, and
changes only WHEN evaluation happens: each generation, every run samples + mutates (CPU, its own streams), ALL runs'
genomes (32 runs x 128 genomes x the train seeds) are evaluated in ONE call, then every run inserts its own slice. Runs
share no state, so each run's trajectory is the sequential one iff every evaluated fitness and cell is identical.

  backends     cpu_sequential  G's baseline_run loop (the reference; always eligible)
               cpu_lockstep    one numba soup.b6.fused.FusedRollout call per generation over all runs
               gpu_lockstep    nv.cudagraph.graph.GraphRollout (ticks_per_graph = T) in nv-venv-u: every generation's genomes
                               and initial state go host -> device (load) and fitness/cells come back (result) INSIDE the
                               timed wall; graph capture is timed separately (compile_s)
  oracles      cpu_lockstep: every run's saved elites (save_elites: cell, fitness, genome bytes) == sequential;
               gpu_lockstep: every generation's fitness AND cells == numba on the same batch AND every run's elites ==
               sequential. Any gpu miss -> INSTRUMENT_FAIL (no timing row).
  timing       baseline stage of a REAL cell, median of `reps` whole stages per backend; cells/hour = 3600 / stage wall.
  decision     (A 1789505093129-0, amendment posted before any timing row) per measured cell eligible = backends whose
               oracle rows all PASS (+ cpu_sequential); CHOSEN = fastest eligible iff its cells/hour >= 1.25 x
               cpu_sequential on EVERY measured cell (>= 1 measured), else cpu_sequential. set_decision writes STRING keys
               pm:r7:backend {backend} and pm:r7:gpu_adopt {decision: GPU_ADOPT iff chosen == gpu_lockstep}.
               A cell whose one-batch generation does not fit VRAM is a device_oom row; a cell projected past 80% of the
               lease is a projected_over_lease row; neither is measured.
  G's hook     baseline_runs_lockstep(...) returns run rows with baseline_run's fields and values (G-R7-2).

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
BACKEND_KEY = "pm:r7:backend"
RATIO_MIN = 1.25
FAMILIES = (4200, 2101, 3303, 5501)
RUN_SEEDS = tuple(range(8))
ADOPT, REJECT = "GPU_ADOPT", "GPU_REJECT"
BACKENDS = ("cpu_sequential", "cpu_lockstep", "gpu_lockstep")


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


def _step_all(g7, runs, evaluate, batch, gen_from, gen_to, check=None, should_pause=None, pause_every=None):
    """runs: [(archive, rng)]. Steps generations [gen_from, gen_to); returns the generation reached (paused if < gen_to)."""
    for gen in range(gen_from, gen_to):
        if should_pause is not None and gen > gen_from and pause_every and gen % pause_every == 0 and should_pause():
            return gen
        gl = []
        for a, rng in runs:
            par = a.sample(batch)
            gl.append(g7.init(rng, batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par)))
        g = concat(gl)
        fit, cells = evaluate(g)
        if check is not None:
            check(gen, g, fit, cells)
        (W, b), C = g
        for i, (a, _) in enumerate(runs):
            s = slice(i * batch, (i + 1) * batch)
            a.insert(np.asarray(cells[s]), np.asarray(fit[s]), g7.pack(((W[s], b[s]), C[s])), np.zeros((batch, 2), np.uint32))
    return gen_to


def lockstep(r, gen_seed: int, pressure: str, evaluate, families=FAMILIES, run_seeds=RUN_SEEDS, gens=None, batch=None,
             tag: str = "lock", check=None, elites_dir=None) -> dict:
    """All runs of one cell stepped together; one evaluate() per generation. -> {digests: {run_id: sha}, wall_s, ...}."""
    from primordial.metric import baseline as B
    from primordial.metric import floors as F
    from primordial.qd import e7_run as E7
    from primordial.qd.archive import LuaArchive, save_elites
    g7 = E7.G7(int(gen_seed), "linear")
    train = F.PRESSURES[pressure]
    bg, bb = B.BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    meta = []
    for fam in families:
        for rs in run_seeds:
            rseed, sseed = B.seeds_of(int(gen_seed), len(train), int(rs), int(fam))
            a = LuaArchive(r, _key(tag, gen_seed, pressure, fam, rs), g7.glen, sseed)
            a.clear()
            meta.append((f"{int(fam)}|{int(rs)}", a, np.random.Generator(np.random.PCG64(rseed)), int(fam), int(rs)))
    t0 = time.perf_counter()
    _step_all(g7, [(a, rng) for _, a, rng, _, _ in meta], evaluate, batch, 0, gens, check)
    wall = time.perf_counter() - t0
    digests = {}
    tmp = pathlib.Path(elites_dir or tempfile.mkdtemp(prefix="e_r7_lock_"))
    for rid, a, _, fam, rs in meta:
        doc = save_elites(a, tmp / f"{rid.replace('|', '-')}.json", [fam, rs, int(gen_seed)])
        digests[rid] = elites_digest(doc)
        a.clear()
    return {"digests": digests, "wall_s": wall, "gens": gens, "batch": batch, "runs": len(meta),
            "evals_per_gen": len(meta) * batch * len(train)}


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


# ------------------------------------------------------------------ G-R7-2 hook: run rows identical to baseline_run's
def baseline_runs_lockstep(r, gen_seed: int, pressure: str, families, run_seeds, gens=None, batch=None, elites_dir=None,
                           done=None, backend: str = "cpu_lockstep", should_pause=None, state=None) -> dict:
    """Every (family, run_seed) not in `done` (keys = baseline.run_key) stepped in lockstep on `backend`. -> {'rows': [...],
    'paused': None} or {'rows': [], 'paused': state} (pass state back to resume; archives stay in redis)."""
    import hashlib as _h
    from primordial.metric import baseline as B
    from primordial.metric import floors as F
    from primordial.metric import readout as RO
    from primordial.metric import search_budget as SB
    from primordial.qd import e7_run as E7
    from primordial.qd.archive import LuaArchive, save_elites
    if backend not in ("cpu_lockstep", "gpu_lockstep"):
        raise ValueError(f"lockstep backend {backend!r}")
    done = done or {}
    g7 = E7.G7(int(gen_seed), "linear")
    train = F.PRESSURES[pressure]
    bg, bb = B.BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    elites_dir = elites_dir or str(B.ELITES_DIR)
    todo = [(int(f), int(rs)) for f in families for rs in run_seeds if B.run_key(gen_seed, pressure, int(rs), int(f)) not in done]
    if not todo:
        return {"rows": [], "paused": None}
    runs, keys = [], []
    for fam, rs in todo:
        key = B.run_key(gen_seed, pressure, rs, fam)
        rseed, sseed = B.seeds_of(int(gen_seed), len(train), rs, fam)
        a = LuaArchive(r, key, g7.glen, sseed)
        rng = np.random.Generator(np.random.PCG64(rseed))
        runs.append((a, rng))
        keys.append(key)
    if state is None:
        for a, _ in runs:
            a.clear()
        state = {"gen": 0, "wall_s": 0.0, "cpu_s": 0.0, "keys": keys}
    else:
        if state["keys"] != keys:
            raise ValueError("lockstep state does not match the runs still to do")
        for (a, rng), (rs_state, ss_state) in zip(runs, state["rng"]):
            rng.bit_generator.state, a.srng.bit_generator.state = rs_state, ss_state
    ev = numba_evaluator(g7, len(runs) * batch, train) if backend == "cpu_lockstep" else gpu_evaluator(g7, train)
    t0, c0 = time.perf_counter(), time.process_time()
    reached = _step_all(g7, runs, ev, batch, state["gen"], gens, should_pause=should_pause, pause_every=B.PAUSE_EVERY)
    state.update(wall_s=state["wall_s"] + time.perf_counter() - t0, cpu_s=state["cpu_s"] + time.process_time() - c0)
    if reached < gens:
        state.update(gen=reached, rng=[(rng.bit_generator.state, a.srng.bit_generator.state) for a, rng in runs])
        return {"rows": [], "paused": state}
    rows, n = [], len(runs)
    for (fam, rs), key, (a, _) in zip(todo, keys, runs):
        el = a.dump()
        pairs = [(v[0], v[1]) for v in el.values()]
        raw = RO.packed(RO.select(pairs), g7.glen)
        epath = pathlib.Path(elites_dir) / f"{key}.json"
        save_elites(a, epath, [fam, rs, int(gen_seed)])
        a.clear()
        row = {"kind": "run", "world": f"w{gen_seed}", "gen_seed": int(gen_seed), "pressure": pressure, "run_seed": rs,
               "family": B.FAM, "genome_bytes": int(g7.glen), "param_bytes": int(g7.pb),
               "gens": gens, "batch": batch, "genomes": gens * batch, "budget_ok": (gens, batch) == (bg, bb),
               "budget_source": B.BUDGET_SOURCE[pressure], "train_seeds": len(train), "readout": RO.NAME, "top": len(raw),
               "sampler_seed": B.seeds_of(int(gen_seed), len(train), rs, fam)[1], "cells": len(el),
               "qd_wall_s": round(state["wall_s"] / n, 2),
               "train_per_seed": B.fused_per_seed(g7, raw, train), "held64_per_seed": B.fused_per_seed(g7, raw, F.HELD64),
               "top_sha256": _h.sha256(raw.tobytes()).hexdigest(), "elites": str(epath), "rng_family": fam,
               "held64_legacy_top16": B.fused_per_seed(g7, B.top_raw(pairs, g7.glen), F.HELD64),
               "backend": backend, "search_split": "lockstep_even"}
        row.update(SB.fields(gens, batch, pressure, cpu_s=round(state["cpu_s"] / n, 3), wall_s=round(state["wall_s"] / n, 3)))
        rows.append(row)
    return {"rows": rows, "paused": None}


def _timing(cell: dict, backend: str, walls: list, comparison: str, **extra) -> dict:
    return {"kind": "timing", "backend": backend, "wall_s": float(statistics.median(walls)),
            "walls_s": [round(w, 4) for w in walls], "reps": len(walls),
            "cells_per_hour": 3600.0 / float(statistics.median(walls)), "transfer_included": backend.startswith("gpu"),
            "warm_state": "warm", "comparison_backend": comparison, "exactness": "PASS", **cell, **extra}


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
    ev_gpu, gpu_capture_s, oom = None, None, None
    try:
        t0 = time.perf_counter()
        ev_gpu = gpu_evaluator(g7, train)
        ev_gpu(probe)
        gpu_capture_s = time.perf_counter() - t0
    except torch.OutOfMemoryError as e:                                       # noqa: PERF203
        oom = str(e)[:300]
        ev_gpu = None
        torch.cuda.empty_cache()
        emit({"kind": "device_oom", "status": "control", **cell, "backend": "gpu_lockstep", "error": oom,
              "note": "one device batch per generation does not fit VRAM: gpu_lockstep not measured on this cell"})
    # ---- projection from one warm generation of each evaluator
    t0 = time.perf_counter()
    ev_numba(probe)
    tn = time.perf_counter() - t0
    tg = 0.0
    if ev_gpu is not None:
        t0 = time.perf_counter()
        ev_gpu(probe)
        tg = time.perf_counter() - t0
    projected = gens_ * (tg + 3 * tn) + int(reps) * gens_ * (tg + 3 * tn)
    cell.update(probe_gen_s_numba=round(tn, 5), probe_gen_s_gpu=round(tg, 5) if ev_gpu else None,
                projected_job_s=round(projected, 1))
    if projected > float(lease_s) * 0.8:
        emit({"kind": "projected_over_lease", "status": "control", **cell, "lease_s": lease_s,
              "note": "oracles + timing projected past 80% of the lease segment: cell not measured"})
        return
    # ---- oracles: reference = G's sequential loop
    seq = sequential(r, gen_seed, pressure, families, run_seeds, gens, batch)
    lock_cpu = lockstep(r, gen_seed, pressure, ev_numba, families, run_seeds, gens, batch, tag="cpuoracle")
    miss_cpu = sorted(k for k in seq["digests"] if lock_cpu["digests"].get(k) != seq["digests"][k])
    emit({"kind": "oracle", "status": "control", **cell, "backend": "cpu_lockstep",
          "exactness": "PASS" if not miss_cpu and len(lock_cpu["digests"]) == n_runs else "FAIL",
          "runs_elites_identical": n_runs - len(miss_cpu), "runs_elites_mismatch": miss_cpu,
          "reference": "metric.baseline.baseline_run (sequential, G's loop)", "numba_init_s": round(numba_init_s, 3)})
    eligible = ["cpu_sequential"] + (["cpu_lockstep"] if not miss_cpu else [])
    if ev_gpu is not None:
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
        emit({"kind": "oracle", "status": "control", **cell, "backend": "gpu_lockstep", "exactness": "PASS" if exact else "FAIL",
              "evaluations_checked": gens_ * n_runs * batch_, "fitness_mismatch": bad["fitness"], "cells_mismatch": bad["cells"],
              "generations_with_mismatch": bad["gens"], "runs_elites_identical": n_runs - len(elite_miss),
              "runs_elites_mismatch": elite_miss, "reference": "numba FusedRollout per generation + baseline_run elites",
              "gpu_capture_s": round(gpu_capture_s, 3), "device": torch.cuda.get_device_name()})
        if exact:
            eligible.append("gpu_lockstep")
        else:
            emit({"kind": "verdict", "status": "control", **cell, "backend": "gpu_lockstep", "verdict": "INSTRUMENT_FAIL",
                  "throughput": None})
    # ---- timing: median of reps of the whole baseline stage, same estimator on every eligible backend
    walls = {k: [] for k in eligible}
    for _ in range(int(reps)):
        walls["cpu_sequential"].append(sequential(r, gen_seed, pressure, families, run_seeds, gens, batch)["wall_s"])
        if "cpu_lockstep" in walls:
            walls["cpu_lockstep"].append(lockstep(r, gen_seed, pressure, ev_numba, families, run_seeds, gens, batch, tag="cpu")["wall_s"])
        if "gpu_lockstep" in walls:
            walls["gpu_lockstep"].append(lockstep(r, gen_seed, pressure, ev_gpu, families, run_seeds, gens, batch, tag="gpu")["wall_s"])
    for k, w in walls.items():
        emit(_timing(cell, k, w, "cpu_sequential" if k != "cpu_sequential" else "fastest_eligible", status="record",
                     compile_s=round(gpu_capture_s if k == "gpu_lockstep" else numba_init_s, 3)))
    med = {k: statistics.median(w) for k, w in walls.items()}
    emit({"kind": "cell_ratio", "status": "record", **cell, "eligible": eligible,
          "ratio_vs_cpu_sequential": {k: med["cpu_sequential"] / med[k] for k in eligible},
          "rule": f"fastest eligible backend iff cells/hour >= {RATIO_MIN} x cpu_sequential on every measured cell"})


def decide(rows: list[dict]) -> dict:
    """A 1789505093129-0 (amended E-R7-2): per measured cell, eligible = cpu_sequential + backends whose oracle rows all
    PASS; chosen = the fastest eligible backend (median of its per-cell ratios' minimum) iff its ratio vs cpu_sequential is
    >= RATIO_MIN on EVERY measured cell, else cpu_sequential. GPU_ADOPT iff chosen == gpu_lockstep."""
    oracle_ok: dict = {}
    for x in rows:
        if x.get("kind") == "oracle":
            oracle_ok[x["backend"]] = oracle_ok.get(x["backend"], True) and x.get("exactness") == "PASS"
    for x in rows:
        if x.get("kind") == "verdict" and x.get("verdict") == "INSTRUMENT_FAIL":
            oracle_ok[x.get("backend", "gpu_lockstep")] = False
    cells = [x for x in rows if x.get("kind") == "cell_ratio"]
    ratios = {f"{x['world']} {x['pressure']}": x["ratio_vs_cpu_sequential"] for x in cells}
    candidates = {}
    for b in ("cpu_lockstep", "gpu_lockstep"):
        if not oracle_ok.get(b) or not cells:
            continue
        per = [float(c["ratio_vs_cpu_sequential"][b]) for c in cells if b in c.get("eligible", ()) and b in c["ratio_vs_cpu_sequential"]]
        if len(per) == len(cells):
            candidates[b] = min(per)
    passing = {b: v for b, v in candidates.items() if v >= RATIO_MIN}
    chosen = max(passing, key=passing.get) if passing else "cpu_sequential"
    return {"backend": chosen, "decision": ADOPT if chosen == "gpu_lockstep" else REJECT, "ratios": ratios,
            "min_ratio_by_backend": candidates, "oracle_ok": oracle_ok, "ratio_min": RATIO_MIN,
            "device_oom_cells": [f"{x['world']} {x['pressure']}" for x in rows if x.get("kind") == "device_oom"],
            "over_lease_cells": [f"{x['world']} {x['pressure']}" for x in rows if x.get("kind") == "projected_over_lease"],
            "rule": "SWARM_R7 O2 + O2' (A 1789505093129-0): fastest eligible (oracle PASS) backend iff >= 1.25x cpu_sequential "
                    "on every measured cell, else cpu_sequential; GPU_ADOPT iff chosen == gpu_lockstep"}


def set_decision(r, doc: dict, rows_ref: str) -> dict:
    rec = dict(doc, rows=rows_ref, ts=round(time.time(), 3), writer="primordial.nv.r7_gpu_eval.set_decision")
    r.set(BACKEND_KEY, json.dumps(rec, sort_keys=True))
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
