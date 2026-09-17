"""B5: where does lane E's closed-loop rollout time go? (measure before building)

An exact copy of primordial/qd/e5_run.rollout's per-tick loop (E code imported read-only)
with a timer around each part:
  brain   E's population-batched numpy forward (digits + einsum per digit + argmax)
  act     codebook gather g[3][genv, idx] -> int32 actions
  books   E's descriptor counters (live mask, abstain / magnitude sums)
  world   lane B NpEncounter.step with_obs=True (transition + economy + observation)
Setup (reset: sha256 stream seeding) is timed separately and excluded from the split.

Control: brain + act + books + world must equal the loop wall within 5%, and the copy's
fitness must equal E's own rollout fitness for the same brains (the copy is the same loop).

usage: python -m primordial.soup.b5.split --worlds 1,2,3,4,5 --P 128 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np

from primordial.qd import e5_run as E5
from primordial.soup.b1.np_world import NpEncounter


def make_forward(kind: str, bs):
    """numpy: E5's own forward. fast: lane C's C5 configuration, exactly as c5_rollout.py builds it
    (gm.TTDigits(bs.D, E5.A).forward_fast(g[:3], obs, gidx, parallel=True)), imported read-only."""
    if kind == "numpy":
        return lambda g, obs, gidx: E5.forward(g, obs, gidx, False)
    if kind == "fast":
        from primordial.brain import genomes as gm
        fam = gm.TTDigits(bs.D, E5.A)
        return lambda g, obs, gidx: fam.forward_fast(g[:3], obs, gidx, cheat=False, parallel=True)
    raise ValueError(kind)


def timed_rollout(bs, g, fwd=None):
    fwd = fwd or make_forward("numpy", bs)
    P, k, S, D = len(g[0]), len(E5.SEEDS), bs.S, bs.D
    n = P * k
    t = {"brain": 0.0, "act": 0.0, "books": 0.0, "world": 0.0}
    s0 = time.perf_counter()
    w = NpEncounter(bs.mech, bs.wid, record=None, cheat="", with_obs=True)
    obs = w.reset(np.tile(E5.SEEDS, P))
    setup = time.perf_counter() - s0
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S)
    abst = np.zeros(n); mag = np.zeros(n); cnt = np.zeros(n)
    ticks = 0
    loop0 = time.perf_counter()
    for _ in range(bs.T):
        a0 = time.perf_counter()
        idx = fwd(g, obs.reshape(n * S, D), grow).reshape(n, S)
        a1 = time.perf_counter()
        a = g[3][genv[:, None], idx].astype(np.int32)
        a2 = time.perf_counter()
        live = w.alive & ~w.done[:, None]
        x = (a % 8).sum(-1)
        abst += ((x == 0) & live).sum(1); mag += (x * live).sum(1); cnt += live.sum(1)
        a3 = time.perf_counter()
        obs, _, done = w.step(a)
        a4 = time.perf_counter()
        t["brain"] += a1 - a0; t["act"] += a2 - a1; t["books"] += a3 - a2; t["world"] += a4 - a3
        ticks += 1
        if done.all():
            break
    loop = time.perf_counter() - loop0
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int32)
    return t, loop, setup, ticks, n, fit


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,2,3,4,5")
    ap.add_argument("--P", type=int, default=128)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--forward", default="numpy", choices=("numpy", "fast"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for gs in (int(x) for x in a.worlds.split(",")):
        bs = E5.BrainSpec(gs)
        g = E5.init_brains(np.random.default_rng(1000 + gs), bs, a.P)
        E5.rollout(bs, g)                                           # warm numpy / caches
        ref_fit = E5.rollout(bs, g)[0]                              # E5's own rollout, numpy forward
        fwd = make_forward(a.forward, bs)
        timed_rollout(bs, g, fwd)                                   # compile numba (fast) outside timing
        reps = []
        for _ in range(a.reps):
            t, loop, setup, ticks, n, fit = timed_rollout(bs, g, fwd)
            reps.append((t, loop, setup, ticks, n, fit))
        # median rep by loop wall
        t, loop, setup, ticks, n, fit = sorted(reps, key=lambda r: r[1])[len(reps) // 2]
        parts = sum(t.values())
        row = {"forward": a.forward, "world_seed": gs, "world_id": bs.wid, "P": a.P, "envs": n, "S": bs.S,
               "D": bs.D, "d_cores": bs.d,
               "W": bs.W, "T": bs.T, "ticks_run": ticks, "corrupt": bs.mech.corrupt_rate,
               "obs_delay": bs.mech.obs_delay, "loop_wall_s": loop, "setup_s": setup,
               "parts_s": t, "share": {k2: v / loop for k2, v in t.items()},
               "parts_over_loop": parts / loop,
               "episode_steps_per_s": n * ticks / loop,
               "fitness_equals_e5_rollout": bool(np.array_equal(fit, ref_fit))}
        row["glue_share"] = row["share"]["world"] + row["share"]["act"] + row["share"]["books"]
        rows.append(row)
        print(f"w{gs} envs={n} T={ticks} D={bs.D} d={bs.d} loop={loop:.2f}s "
              f"shares={ {k2: round(v, 3) for k2, v in row['share'].items()} } "
              f"parts/loop={row['parts_over_loop']:.3f} steps/s={row['episode_steps_per_s']:,.0f} "
              f"fit_eq={row['fitness_equals_e5_rollout']}", flush=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    # B5 (numpy forward) judged the world share alone; B5b (fast forward) judges world + act + books
    key = "glue_share" if a.forward == "fast" else None
    share = (lambda r: r["glue_share"]) if key else (lambda r: r["share"]["world"])
    ge50 = sum(share(r) >= 0.5 for r in rows)
    lt30 = sum(share(r) < 0.3 for r in rows)
    print(json.dumps({"forward": a.forward, "worlds": len(rows),
                      "judged": "world+act+books" if key else "world",
                      "share_ge_50pct": ge50, "share_lt_30pct": lt30,
                      "decision": ("build closed-loop numba kernel" if ge50 >= 3 else
                                   "do NOT build" if lt30 >= 3 else "ambiguous: neither rule met"),
                      "controls_ok": all(abs(r["parts_over_loop"] - 1) <= 0.05 and r["fitness_equals_e5_rollout"]
                                         for r in rows)}, indent=1))


if __name__ == "__main__":
    main()
