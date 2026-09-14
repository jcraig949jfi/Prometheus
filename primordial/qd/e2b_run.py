"""E2b: branch points with a per-cell random baseline and a 20-world null distribution.

  python -m primordial.qd.e2b_run [--gens 300] [--batch 1024] [--reps 3] [--tag full]

Bar (posted on the bus before the run, after a 5-rep attainable-range pre-check):
  honest   held25 transfer rate > MAX over 20 fully redrawn null worlds, 3/3 reps, >=50 BPs each
  fakefit  CHEAT (real descent, fitness shuffled within each batch): must NOT beat the null max in >=2/3 reps
  filler   structural control (false parents fail the descent check)
Branch point definition unchanged from E2 (k=50, z>=2, hamming<=8), z now per cell.
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.qd import e2_run as E

EXP = "E2b-branch-points-cell-baseline"
ROWS = E.ROWS.with_name(f"{EXP}.jsonl")
N_NULL = 20


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=300); p.add_argument("--batch", type=int, default=1024)
    p.add_argument("--reps", type=int, default=3); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--tag", default="full")
    a = p.parse_args()
    r = redis.Redis(port=a.port)
    worlds = {"held25": E.perturbed_world(0.25, 11)}
    worlds.update({f"null{i}": E.perturbed_world(1.0, 100 + i) for i in range(N_NULL)})
    for rep in range(a.reps):
        for mode in ("honest", "fakefit", "filler"):
            run = f"e2b{mode}-{int(time.time() * 1000) % 10**9}"
            ev = E.evolve(r, run, mode, a.gens, a.batch, seed=3000 + rep)
            recs = E.read_events(r, ev["arch"].skey)
            bp = E.branch_points(recs, a.gens, E.K_PRIMARY, E.Z_PRIMARY, worlds, z_mode="cell")
            nulls = [bp[f"transfer_rate_null{i}"] for i in range(N_NULL)]
            null_bps = [bp[f"bp_null{i}"] for i in range(N_NULL)]
            rate25 = bp["transfer_rate_held25"]
            cpu_h = (ev["cpu_worker_s"] + ev["cpu_redis_s"]) / 3600
            row = {
                "exp_id": EXP, "tag": a.tag, "rep": rep, "mode": mode, "run": run, "gens": a.gens, "batch": a.batch,
                "k": E.K_PRIMARY, "z_min": E.Z_PRIMARY, "h_max": E.H_MAX, "z_mode": "cell", "wins": ev["wins"],
                "events": bp["events"], "real_edges": bp["real_edges"], "founders_eligible": bp["founders_eligible"],
                "founders_surviving": bp["founders_surviving"], "bp_held25": bp["bp_held25"],
                "transfer_rate_held25": rate25, "null_rates": nulls,
                "null_rate_max": max(nulls) if rate25 is not None else None,
                "null_rate_mean": round(float(np.mean(nulls)), 4) if rate25 is not None else None,
                "beats_all_nulls": (rate25 > max(nulls)) if rate25 is not None else False,
                "bp_excess_over_null_mean": round(bp["bp_held25"] - float(np.mean(null_bps)), 1),
                "cpu_worker_s": round(ev["cpu_worker_s"], 2), "cpu_redis_s": round(ev["cpu_redis_s"], 2),
                "wall_s": round(ev["wall_s"], 2),
                "bp_held25_per_cpu_h": round(bp["bp_held25"] / cpu_h, 1),
                "bp_excess_per_cpu_h": round((bp["bp_held25"] - float(np.mean(null_bps))) / cpu_h, 1),
                "ts": time.time(),
            }
            print(json.dumps({k: v for k, v in row.items() if k != "null_rates"}), flush=True)
            with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
            ev["arch"].clear()


if __name__ == "__main__":
    main()
