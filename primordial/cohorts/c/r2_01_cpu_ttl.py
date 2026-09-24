"""C-R2-01: drawn cell tt_feat / w4 / cpu_ttl / numba_fused / none (draw seed 2847680424335095422).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run.

  pressure  cpu_ttl: E9's loop exactly (G7 tt_feat + codebook, LuaArchive, batch 128, E6's 8 train
            seeds, top-16 on E6's 64 held-out seeds), but training stops when the client process CPU
            time (time.process_time, all threads) spent in the loop reaches --ttl-cpu-s. Derivation of
            the default 1.0 s: E9 w4 tt_feat median wall 5.4 s/run, divided by 5. Fixed before the run.
            JIT warm-up rollout runs before the clock. Final held-out scoring and oracles are outside it.
  loophole  Redis server-side Lua CPU is NOT charged to the budget; the redis-server used_cpu delta is
            reported per run (port 6392 is lane C's), so the size of the loophole is visible.
  primary   held64_median over run seeds 0-7 >= 79.19 - 0.5 * 6.94 = 75.72 (E9 parity band)
  oracles   run seed 0, E7 numpy oracles on HELD8: world 0/16 failing, skip_lin >= 14/16;
            brain 0 mismatched clear rows, cheat (skip-odd) >= 14/16

  python -m primordial.cohorts.c.r2_01_cpu_ttl [--ttl-cpu-s 1.0] [--run-seeds 0-7]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import redis

from primordial.brain import genomes as gm
from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger
from primordial.qd import e7_run as E7
from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "C-R2-01-tt-feat-w4-cpu-ttl"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C") / EXP          # hot data never on F:
GS, FAM, BATCH = 4, "tt_feat", 128
CELL = {"representation": "tt_feat", "world": "w4", "pressure": "cpu_ttl", "substrate": "numba_fused",
        "channel": "none"}
BASE_MEDIAN, BASE_IQR = 79.19, 6.94


def server_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def score(g7, raw, seeds) -> float:
    fit = FusedRollout(g7.spec, len(raw), seeds, family=FAM).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ttl-cpu-s", type=float, default=1.0)
    p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--port", type=int, default=6392)
    p.add_argument("--max-gens", type=int, default=200)   # E9's budget is the ceiling; TTL should bind first
    a = p.parse_args()
    lo, hi = (int(x) for x in a.run_seeds.split("-"))
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    held = []
    with RowWriter(ROWS, EXP, commit_every_s=120) as w:
        for rs in range(lo, hi + 1):
            t0 = time.perf_counter()
            g7 = E7.G7(GS, FAM)
            arch = LuaArchive(r, f"c-r2-01-{rs}", g7.glen, UNSEEDED)
            arch.clear()
            rng = np.random.Generator(np.random.PCG64([990, rs, GS, list(gm.FAMILIES).index(FAM)]))  # E9's stream
            fr = FusedRollout(g7.spec, BATCH, E7.TRAIN, family=FAM)
            fr.run(g7.init(np.random.Generator(np.random.PCG64(12345)), BATCH))        # JIT warm-up, off the clock
            s_cpu0, c0, gens = server_cpu(r), time.process_time(), 0
            while gens < a.max_gens and time.process_time() - c0 < a.ttl_cpu_s:
                par = arch.sample(BATCH)
                g = g7.init(rng, BATCH) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
                fit, cells = fr.run(g)[:2]
                arch.insert(cells, fit, g7.pack(g), np.zeros((BATCH, 2), np.uint32))
                gens += 1
            client_cpu = time.process_time() - c0
            srv = server_cpu(r) - s_cpu0
            el = arch.dump()
            raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:E7.TOP]),
                                np.uint8).reshape(-1, g7.glen)
            arch.clear()
            np.save(HOT / f"w{GS}_{FAM}_r{rs}_top.npy", raw)
            row = {"kind": "run", "cell": CELL, "run_seed": rs, "ttl_cpu_s": a.ttl_cpu_s, "gens": gens,
                   "genomes": gens * BATCH, "cells": len(el), "client_cpu_s": round(client_cpu, 3),
                   "redis_server_cpu_s_uncharged": round(srv, 3), "param_bytes": g7.pb, "genome_bytes": g7.glen,
                   "train_per_seed": score(g7, raw, E7.TRAIN), "held64_per_seed": score(g7, raw, E7.HELD64),
                   "status": "record"}
            if rs == 0:
                top = g7.unpack(raw)
                row["world_oracle_honest"] = E7.world_oracle(g7, top, E7.HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(g7, top, E7.HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(g7, top, E7.HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(g7, top, E7.HELD8, cheat=True)
            row["wall_s"] = round(time.perf_counter() - t0, 2)
            held.append(row["held64_per_seed"])
            print(json.dumps(row), flush=True)
            w.write(row)
            if rs == 0:
                oracle = row
        q1, med, q3 = (float(x) for x in np.percentile(held, [25, 50, 75]))
        wo, ws, bo, bc = (oracle["world_oracle_honest"], oracle["world_oracle_skip_lin"],
                          oracle["brain_oracle_honest"], oracle["brain_oracle_cheat"])
        oracle_clean = (wo["elites_failing"] == 0 and ws["elites_failing"] >= 14 and bo["mismatched_rows"] == 0
                        and bo["clear_rows"] > 0 and bc["elites_mismatching"] >= 14)
        threshold = BASE_MEDIAN - 0.5 * BASE_IQR
        summary = {"kind": "summary", "cell": CELL, "n_runs": len(held), "held64_median": round(med, 3),
                   "iqr": round(q3 - q1, 3), "threshold": round(threshold, 3), "oracle_clean": oracle_clean,
                   "primary": "PASS" if (oracle_clean and len(held) >= 8 and med >= threshold) else
                              ("INDETERMINATE" if not oracle_clean else "FAIL"),
                   "clause_a_check_cpu_ttl": qd_ledger.check(qd_ledger.load(), "w4", "cpu_ttl", med, q3 - q1,
                                                             g7.glen, len(held), oracle_clean),
                   "status": "record" if oracle_clean else "cheat"}
        print(json.dumps(summary), flush=True)
        w.write(summary)
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        q.write({"cell": CELL, "mechanism": f"closed_loop_tt_feat_codebook_cpu_ttl_{a.ttl_cpu_s:g}s",
                 "fitness": {"held64_median": round(med, 3), "iqr": round(q3 - q1, 3), "n_runs": len(held)},
                 "footprint": {"genome_bytes": int(g7.glen)},
                 "oracle": "clean (E7 world/brain oracles, skip_lin + skip-odd cheats)" if oracle_clean
                           else f"NOT clean: {json.dumps([wo, ws, bo, bc])}",
                 "baseline": False, "cohort": "C", "status": summary["status"],
                 "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


if __name__ == "__main__":
    main()
