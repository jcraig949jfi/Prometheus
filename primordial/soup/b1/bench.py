"""B1 steps/s surface: every form x n_envs x world, open-loop (the action tensor is an
input, generated untimed). Timed region = state transition + economy only; setup
(xorshift stream seeding via sha256, state upload) is reported separately as prep_s.

steps = sum over envs of min(episode length, ticks run): the work the reference does.
Forms that keep stepping absorbed envs (np, lua) are charged for it in wall time.

usage: python -m primordial.soup.b1.bench --forms ref,np,nb,lua1,luak --worlds 0,3 \
         --envs 1,16,256,4096,65536 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from .common import action_tensor, episode_seeds, make_world, reference

BUDGET_S = float(os.environ.get("B1_BUDGET_S", "2.0"))


def host_cpu() -> float | None:
    try:
        import psutil
        return psutil.cpu_percent(interval=0.2)
    except Exception:
        return None


def episode_lengths(mech, wid, seeds, acts) -> np.ndarray:
    from .nb_world import NbEncounter
    w = NbEncounter(mech, wid)
    w.prepare(seeds)
    w.run(acts)
    return w.done_tick.copy()


def bench_ref(mech, wid, seeds, acts, lens):
    n = min(len(seeds), 64)
    t0 = time.perf_counter()
    for e in range(n):
        reference(mech, wid, int(seeds[e]), acts[:, e])
    wall = time.perf_counter() - t0
    return {"ticks": mech.horizon, "steps": int(lens[:n].sum()), "wall_s": wall, "prep_s": 0.0,
            "envs_run": n}


def bench_np(mech, wid, seeds, acts, lens):
    from .np_world import NpEncounter
    w = NpEncounter(mech, wid, record=None, with_obs=False)
    p0 = time.perf_counter()
    w.reset(seeds)
    prep = time.perf_counter() - p0
    t0 = time.perf_counter()
    t = 0
    while t < mech.horizon and (t == 0 or time.perf_counter() - t0 < BUDGET_S):
        w.step(acts[t])
        t += 1
    wall = time.perf_counter() - t0
    return {"ticks": t, "steps": int(np.minimum(lens, t).sum()), "wall_s": wall, "prep_s": prep}


def bench_nb(mech, wid, seeds, acts, lens):
    from .nb_world import NbEncounter
    w = NbEncounter(mech, wid)
    p0 = time.perf_counter()
    w.prepare(seeds)
    prep = time.perf_counter() - p0
    w.run(acts[:, :1])  # jit warm (cache=True); shapes identical except n
    w.prepare(seeds)
    t0 = time.perf_counter()
    w.run(acts)
    wall = time.perf_counter() - t0
    return {"ticks": mech.horizon, "steps": int(lens.sum()), "wall_s": wall, "prep_s": prep,
            "numba_threads": int(os.environ.get("NUMBA_NUM_THREADS", "0") or 0)}


def _bench_lua(k):
    def f(mech, wid, seeds, acts, lens):
        from .lua_world import LuaEncounter
        w = LuaEncounter(mech, wid, ns=f"b1bench{k}")
        p0 = time.perf_counter()
        w.prepare(seeds)
        prep = time.perf_counter() - p0
        kk = k or mech.horizon
        t0 = time.perf_counter()
        t = 0
        while t < mech.horizon and (t == 0 or time.perf_counter() - t0 < BUDGET_S):
            step = min(kk, mech.horizon - t)
            w.run(acts[t:t + step], k=step, ticks=step)
            t += step
        wall = time.perf_counter() - t0
        return {"ticks": t, "steps": int(np.minimum(lens, t).sum()), "wall_s": wall, "prep_s": prep,
                "k_per_call": kk}
    return f


def bench_fk(mech, wid, seeds, acts, lens):
    from .falkor_world import FalkorEncounter
    w = FalkorEncounter(mech, wid, graph="b1bench")
    p0 = time.perf_counter()
    w.prepare(seeds)
    prep = time.perf_counter() - p0
    t0 = time.perf_counter()
    t = 0
    while t < mech.horizon and (t == 0 or time.perf_counter() - t0 < BUDGET_S):
        w.run(acts, ticks=1)
        t += 1
    wall = time.perf_counter() - t0
    return {"ticks": t, "steps": int(np.minimum(lens, t).sum()), "wall_s": wall, "prep_s": prep}


FORMS = {"ref": bench_ref, "np": bench_np, "nb": bench_nb, "lua1": _bench_lua(1), "luak": _bench_lua(0),
         "fk": bench_fk}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", default="ref,np,nb,lua1,luak")
    ap.add_argument("--worlds", default="0,3")
    ap.add_argument("--envs", default="1,16,256,4096")
    ap.add_argument("--skip", default="", help="form:max_envs caps, e.g. lua1:4096,ref:64")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    caps = dict((kv.split(":")[0], int(kv.split(":")[1])) for kv in a.skip.split(",") if kv)
    with open(a.out, "a", encoding="utf-8", newline="\n") as fh:
        for g in (int(x) for x in a.worlds.split(",")):
            mech, wid = make_world(g)
            for n in (int(x) for x in a.envs.split(",")):
                seeds = episode_seeds(n, base=500_000 + g)
                acts = action_tensor(mech, n, seed=1000 + g)
                lens = episode_lengths(mech, wid, seeds, acts)
                for form in a.forms.split(","):
                    if form in caps and n > caps[form]:
                        continue
                    cpu = host_cpu()
                    res = FORMS[form](mech, wid, seeds, acts, lens)
                    row = {"form": form, "world_seed": g, "world_id": wid, "n_envs": n,
                           "n_regs": mech.n_regs, "n_slots": mech.n_slots, "horizon": mech.horizon,
                           "stoch": mech.stoch_rate, "delay": mech.delay, "lin_ops": len(mech.lin_ops),
                           "host_cpu_pct_before": cpu, **res,
                           "steps_per_s": res["steps"] / res["wall_s"] if res["wall_s"] > 0 else None}
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
                    fh.flush()
                    print(f"{form:5s} w{g} n={n:6d} ticks={res['ticks']:4d} "
                          f"steps/s={row['steps_per_s']:,.0f} prep={res['prep_s']:.2f}s cpu={cpu}")


if __name__ == "__main__":
    main()
