"""B1 concurrent producers: P client processes, each driving its own key namespace on
the ONE private Redis (single-threaded Lua), started on a barrier, run for a fixed
window. Aggregate steps/s shows where the server, not the client, is the ceiling.

Only the server-side forms (lua1, luak) are swept: np/nb producers scale with client
cores, which the lane budget (<= 3 sustained) forbids measuring at P=16.

usage: python -m primordial.soup.b1.bench_producers --forms luak,lua1 --world 3 \
         --envs 256,4096 --producers 1,2,4,8,16 --window 4 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import time

import numpy as np


def _worker(i, form, world, n, window, barrier, q):
    """Always answers on q: (i, steps, calls, wall, error-or-None). A worker that dies
    silently would hang the parent on q.get (observed at luak n=4096 P=16)."""
    t0 = time.perf_counter()
    try:
        _work(i, form, world, n, window, barrier, q)
    except Exception as e:  # noqa: BLE001 -- the failure IS the measurement
        try:
            barrier.abort()
        except Exception:
            pass
        q.put((i, 0, 0, time.perf_counter() - t0, f"{type(e).__name__}: {e}"[:200]))


def _work(i, form, world, n, window, barrier, q):
    from .bench import episode_lengths
    from .common import action_tensor, episode_seeds, make_world
    from .lua_world import LuaEncounter
    mech, wid = make_world(world)
    seeds = episode_seeds(n, base=900_000 + 1000 * i)
    acts = action_tensor(mech, n, seed=77 + i)
    lens = episode_lengths(mech, wid, seeds, acts)
    w = LuaEncounter(mech, wid, ns=f"b1p{i}")
    k = 1 if form == "lua1" else mech.horizon
    barrier.wait()
    t0 = time.perf_counter()
    steps = calls = 0
    while time.perf_counter() - t0 < window:
        w.prepare(seeds)                      # episode reset inside the window: producers pay it
        t = 0
        while t < mech.horizon and time.perf_counter() - t0 < window:
            kk = min(k, mech.horizon - t)
            w.run(acts[t:t + kk], k=kk, ticks=kk)
            t += kk
            calls += 1
        steps += int(np.minimum(lens, t).sum())
    q.put((i, steps, calls, time.perf_counter() - t0, None))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", default="luak,lua1")
    ap.add_argument("--world", type=int, default=3)
    ap.add_argument("--envs", default="256,4096")
    ap.add_argument("--producers", default="1,2,4,8,16")
    ap.add_argument("--window", type=float, default=4.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    ctx = mp.get_context("spawn")
    with open(a.out, "a", encoding="utf-8", newline="\n") as fh:
        for form in a.forms.split(","):
            for n in (int(x) for x in a.envs.split(",")):
                for P in (int(x) for x in a.producers.split(",")):
                    barrier, q = ctx.Barrier(P), ctx.Queue()
                    procs = [ctx.Process(target=_worker, args=(i, form, a.world, n, a.window, barrier, q))
                             for i in range(P)]
                    for p in procs:
                        p.start()
                    got = [q.get() for _ in range(P)]
                    for p in procs:
                        p.join()
                    steps = sum(g[1] for g in got)
                    wall = max(g[3] for g in got)
                    errors = [f"p{g[0]}: {g[4]}" for g in got if g[4]]
                    row = {"form": form, "world_seed": a.world, "n_envs": n, "producers": P,
                           "status": "FAIL" if errors else "OK", "errors": errors,
                           "window_s": a.window, "steps": steps, "calls": sum(g[2] for g in got),
                           "wall_s": wall, "agg_steps_per_s": steps / wall,
                           "per_producer_steps_per_s": steps / wall / P}
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
                    fh.flush()
                    print(f"{form} n={n} P={P} agg={row['agg_steps_per_s']:,.0f} "
                          f"per={row['per_producer_steps_per_s']:,.0f}", flush=True)


if __name__ == "__main__":
    main()
