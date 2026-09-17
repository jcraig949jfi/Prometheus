"""E1: vectorised MAP-Elites sharing ONE Redis archive across N processes.

  python -m primordial.qd.e1_run driver [--gens G] [--batch B] [--port P]
  python -m primordial.qd.e1_run worker ...   (spawned by the driver)

Conditions (fresh run id each):
  serial1  1 worker, LuaArchive           engineering baseline
  lua4     4 workers, LuaArchive          claim: archive == serial reference, 0 audit flags
  racy4    4 workers, RacyArchive         CHEAT CONTROL: exactness instrument must see lost elites
  liar4    4 workers, LuaArchive, worker 0 inflates 1% of fits  CHEAT CONTROL: audit must flag every lie present

Rows -> primordial/ledger/rows/E/E1-qd-core-redis-archive.jsonl ; raw offer logs -> pm-data/E (hot data, sha256 in rows).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import threading
import time

import numpy as np
import psutil
import redis

from primordial.qd.archive import UNSEEDED, LuaArchive, RacyArchive, serial_reference
from primordial.qd.stubworld import GLEN, N_CELLS, NKWorld, mutate, random_genomes

EXP = "E1-qd-core-redis-archive"
ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "E" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/E") / EXP
LIE_BONUS = 200_000
LIE_RATE = 0.01


def worker(a) -> None:
    r = redis.Redis(host="127.0.0.1", port=a.port)
    arch = (LuaArchive if a.kind == "lua" else RacyArchive)(r, a.run, GLEN, UNSEEDED)
    world = NKWorld()
    rng = np.random.Generator(np.random.PCG64([a.k, int(a.run.split("-")[-1])]))
    while not r.exists(f"pm:qd:{a.run}:go"):
        time.sleep(0.005)
    logs = {k: [] for k in ("cells", "fits", "genomes", "lie")}
    t_sample, t_insert, t_eval, wins = [], [], [], 0
    t0 = time.perf_counter()
    for gen in range(a.gens):
        s = time.perf_counter()
        parents = arch.sample(a.batch)
        t_sample.append(time.perf_counter() - s)
        s = time.perf_counter()
        kids = random_genomes(rng, a.batch) if len(parents) == 0 else mutate(rng, parents)
        fits, cells = world.evaluate(kids)
        lie = np.zeros(a.batch, bool)
        if a.liar:
            lie = rng.random(a.batch) < LIE_RATE
            fits = fits + (lie * LIE_BONUS).astype(np.int32)
        meta = np.stack([np.full(a.batch, a.k, np.uint32), np.full(a.batch, gen, np.uint32)], axis=1)
        t_eval.append(time.perf_counter() - s)
        s = time.perf_counter()
        wins += arch.insert(cells, fits, kids, meta)
        t_insert.append(time.perf_counter() - s)
        for k, v in (("cells", cells), ("fits", fits), ("genomes", kids), ("lie", lie)):
            logs[k].append(v)
    wall = time.perf_counter() - t0
    out = pathlib.Path(a.out) / f"{a.run}_w{a.k}.npz"
    np.savez(out, **{k: np.concatenate(v) for k, v in logs.items()},
             t_sample=np.array(t_sample), t_insert=np.array(t_insert), t_eval=np.array(t_eval),
             wall=np.array(wall), wins=np.array(wins))


def _pct(x, q):
    return round(float(np.percentile(x, q)) * 1e3, 3)


def run_condition(name, kind, n_workers, liar, a, py) -> dict:
    run = f"e1{name}-{int(time.time() * 1000) % 10**9}"
    r = redis.Redis(host="127.0.0.1", port=a.port)
    arch = LuaArchive(r, run, GLEN, UNSEEDED)
    arch.clear()
    procs = [subprocess.Popen([py, "-m", "primordial.qd.e1_run", "worker", "--run", run, "--kind", kind,
                              "--k", str(k), "--gens", str(a.gens), "--batch", str(a.batch),
                              "--liar", str(int(liar and k == 0)), "--port", str(a.port), "--out", str(HOT)],
                             cwd=ROOT) for k in range(n_workers)]
    time.sleep(3.0)  # let interpreters import before the barrier opens
    cpu, stop = [], threading.Event()
    th = threading.Thread(target=lambda: [cpu.append(psutil.cpu_percent(0.5)) for _ in iter(lambda: stop.is_set(), True)])
    psutil.cpu_percent(None)
    th.start()
    t0 = time.perf_counter()
    r.set(f"pm:qd:{run}:go", 1)
    rc = [p.wait() for p in procs]
    wall = time.perf_counter() - t0
    stop.set(); th.join()
    if any(rc):
        raise SystemExit(f"{name}: worker exit codes {rc}")

    logs = [np.load(HOT / f"{run}_w{k}.npz") for k in range(n_workers)]
    sha = {f"w{k}": hashlib.sha256((HOT / f"{run}_w{k}.npz").read_bytes()).hexdigest() for k in range(n_workers)}
    cells = np.concatenate([l["cells"] for l in logs])
    fits = np.concatenate([l["fits"] for l in logs])
    genomes = np.concatenate([l["genomes"] for l in logs])
    lie = np.concatenate([l["lie"] for l in logs])

    # instrument 1: exactness vs the order-independent serial reference
    ref = serial_reference(cells, fits, genomes)
    got = arch.dump()
    bad = [c for c in set(ref) | set(got) if ref.get(c) != (got[c][:2] if c in got else None)]
    lost_fit = sum(ref[c][0] - (got[c][0] if c in got else 0) for c in bad if c in ref)

    # instrument 2: audit, re-evaluate every elite in the world
    ag_cells = np.array(sorted(got), dtype=np.uint32)
    ag_g = np.frombuffer(b"".join(got[int(c)][1] for c in ag_cells), np.uint8).reshape(-1, GLEN)
    ag_f = np.array([got[int(c)][0] for c in ag_cells], np.int64)
    tf, tc = NKWorld().evaluate(ag_g)
    flagged = (tf.astype(np.int64) != ag_f) | (tc != ag_cells)
    lies = {(int(f), genomes[i].tobytes()) for i, f in zip(np.nonzero(lie)[0], fits[lie])}
    lie_present = np.array([(int(f), g.tobytes()) in lies for f, g in zip(ag_f, ag_g)], bool)

    t_ins = np.concatenate([l["t_insert"] for l in logs])
    t_smp = np.concatenate([l["t_sample"] for l in logs])
    arch.clear()
    return {
        "condition": name, "run": run, "archive": kind, "workers": n_workers, "liar": bool(liar),
        "gens": a.gens, "batch": a.batch, "offers": int(len(cells)), "raw_sha256": sha,
        # science-ish instrument readouts
        "ref_cells": len(ref), "archive_cells": len(got), "mismatched_cells": len(bad),
        "lost_fitness_sum": int(lost_fit), "audit_flagged": int(flagged.sum()),
        "lies_offered": int(lie.sum()), "lies_present_in_archive": int(lie_present.sum()),
        "lies_caught": int((flagged & lie_present).sum()), "audit_false_flags": int((flagged & ~lie_present).sum()),
        "coverage": round(len(got) / N_CELLS, 4), "qd_score_true": int(tf[~flagged].astype(np.int64).sum()),
        # engineering
        "wall_s": round(wall, 3), "offspring_per_s": round(len(cells) / wall, 1),
        "insert_ms_p50": _pct(t_ins, 50), "insert_ms_p99": _pct(t_ins, 99),
        "sample_ms_p50": _pct(t_smp, 50), "sample_ms_p99": _pct(t_smp, 99),
        "host_cpu_pct_mean": round(float(np.mean(cpu)), 1) if cpu else None,
        "host_cpu_pct_max": round(float(np.max(cpu)), 1) if cpu else None,
    }


def driver(a) -> None:
    HOT.mkdir(parents=True, exist_ok=True)
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    conds = [("serial1", "lua", 1, False), ("lua4", "lua", 4, False),
             ("racy4", "racy", 4, False), ("liar4", "lua", 4, True)]
    if a.only:
        conds = [c for c in conds if c[0] in a.only.split(",")]
    for rep, c in ((rep, c) for rep in range(a.reps) for c in conds):
        row = run_condition(*c, a, py)
        row["rep"], row["ts"] = rep, time.time()
        print(json.dumps(row), flush=True)
        with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["driver", "worker"])
    p.add_argument("--run"); p.add_argument("--kind", default="lua"); p.add_argument("--k", type=int, default=0)
    p.add_argument("--gens", type=int, default=300); p.add_argument("--batch", type=int, default=1024)
    p.add_argument("--liar", type=int, default=0); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--out", default=str(HOT)); p.add_argument("--only", default="")
    p.add_argument("--reps", type=int, default=1)
    a = p.parse_args()
    (driver if a.mode == "driver" else worker)(a)


if __name__ == "__main__":
    main()
