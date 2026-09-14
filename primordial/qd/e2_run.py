"""E2: meaningful branch points per CPU-hour, from EVENT-LEVEL lineage.

  python -m primordial.qd.e2_run [--gens 300] [--batch 1024] [--port 6394]

Branch point (v0, posted on the bus before the run):
  a win that OPENS an empty cell, with a real descent edge (parent is an
  earlier elite, hamming(child, parent) <= H), whose strict descendant still
  holds a cell k generations later, and whose best surviving descendant (by
  train fitness) scores z >= Z on a held-out NK world (25% of table redrawn).

Every win is XADDed by the same Lua call that performs it (stream
pm:qd:<run>:wins: c, f, g, p, n), so lineage is read from events, not from the
final archive (E1: an end-state check on a converging search went blind).

Conditions: honest (mutate sampled elites) and filler (CHEAT: random genomes
that claim sampled elites as parents). Controls on the transfer half: every
condition is re-scored on a fully redrawn (uncorrelated) world.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
from collections import defaultdict

import numpy as np
import redis

from primordial.qd.archive import SAMPLE_LUA, UNSEEDED, LuaArchive, reduce_batch
from primordial.qd.stubworld import GLEN, N_CELLS, NKWorld, mutate, random_genomes

EXP = "E2-branch-points"
ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "E" / f"{EXP}.jsonl"
H_MAX, K_PRIMARY, Z_PRIMARY = 8, 50, 2.0

LINEAGE_LUA = r"""
local zkey, skey, pre, glen = KEYS[1], KEYS[2], ARGV[1], tonumber(ARGV[2])
local cells, fits, gs, meta, ps = ARGV[3], ARGV[4], ARGV[5], ARGV[6], ARGV[7]
local function gless(a, b)
  for p = 1, glen, 4 do
    local x = struct.unpack('>I4', a, p)
    local y = struct.unpack('>I4', b, p)
    if x ~= y then return x < y end
  end
  return false
end
local wins = 0
for i = 0, #cells / 4 - 1 do
  local c = struct.unpack('<I4', cells, 4 * i + 1)
  local f = struct.unpack('<i4', fits, 4 * i + 1)
  local g = string.sub(gs, glen * i + 1, glen * (i + 1))
  local k = pre .. c
  local old = redis.call('HMGET', k, 'f', 'g')
  local better
  if not old[1] then better = true
  else
    local of = tonumber(old[1])
    better = (f > of) or (f == of and gless(g, old[2]))
  end
  if better then
    local gen = struct.unpack('<I4', meta, 8 * i + 1)
    redis.call('HSET', k, 'f', f, 'g', g, 'm', string.sub(meta, 8 * i + 1, 8 * (i + 1)))
    redis.call('ZADD', zkey, f, c)
    redis.call('XADD', skey, '*', 'c', c, 'f', f, 'g', g, 'p', string.sub(ps, glen * i + 1, glen * (i + 1)), 'n', gen)
    wins = wins + 1
  end
end
return wins
"""


class LineageArchive(LuaArchive):
    def __init__(self, r, run, glen, sampler_seed):
        super().__init__(r, run, glen, sampler_seed)
        self.skey = f"pm:qd:{run}:wins"
        self._lin = r.register_script(LINEAGE_LUA)

    def insert_lineage(self, cells, fits, genomes, parents, gen: int) -> int:
        meta = np.stack([np.full(len(cells), gen, np.uint32), np.arange(len(cells), dtype=np.uint32)], axis=1)
        c, f, g, m = reduce_batch(cells, fits, genomes, meta)
        return int(self._lin(keys=[self.zkey, self.skey], args=[
            self.pre, self.glen, c.astype("<u4").tobytes(), f.astype("<i4").tobytes(), g.tobytes(),
            m.astype("<u4").tobytes(), parents[m[:, 1]].tobytes()]))


def perturbed_world(frac: float, seed: int) -> NKWorld:
    w = NKWorld()
    rng = np.random.Generator(np.random.PCG64(seed))
    mask = rng.random(w.table.shape) < frac
    w.table = np.where(mask, rng.integers(0, 1 << 16, size=w.table.shape, dtype=np.int64), w.table)
    return w


def redis_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def evolve(r, run, mode, gens, batch, seed) -> dict:
    arch = LineageArchive(r, run, GLEN, UNSEEDED)
    arch.clear()
    world, rng = NKWorld(), np.random.Generator(np.random.PCG64(seed))
    c0, rc0, t0 = time.process_time(), redis_cpu(r), time.perf_counter()
    wins = 0
    for gen in range(gens):
        parents = arch.sample(batch)
        if len(parents) == 0:
            kids, parents = random_genomes(rng, batch), np.zeros((batch, GLEN), np.uint8)
        elif mode in ("honest", "fakefit"):
            kids = mutate(rng, parents)
        else:  # filler: random genomes, falsely attributed to the sampled elites
            kids = random_genomes(rng, batch)
        fits, cells = world.evaluate(kids)
        if mode == "fakefit":  # CHEAT: real descent, fitness shuffled across the batch (no information)
            fits = rng.permutation(fits)
        wins += arch.insert_lineage(cells, fits, kids, parents, gen)
    return {"cpu_worker_s": time.process_time() - c0, "cpu_redis_s": redis_cpu(r) - rc0,
            "wall_s": time.perf_counter() - t0, "wins": wins, "arch": arch}


def read_events(r, skey):
    recs, last = [], "-"
    while True:
        chunk = r.xrange(skey, min=last, count=10000)
        if last != "-":
            chunk = chunk[1:]
        if not chunk:
            break
        for _, f in chunk:
            recs.append((int(f[b"c"]), int(f[b"f"]), f[b"g"], f[b"p"], int(f[b"n"])))
        last = chunk[-1][0]
    return recs


def popcount_genomes(rng, d0: int, d1: int, m: int) -> np.ndarray:
    """m uniform genomes with exactly d0 ones in bits 0..31 and d1 in bits 32..63 (one descriptor cell)."""
    def half(d):
        ranks = np.argsort(np.argsort(rng.random((m, 32)), axis=1), axis=1)
        return (ranks < d).astype(np.uint8)
    return np.packbits(np.concatenate([half(d0), half(d1)], axis=1), axis=1)


_CELL_STATS: dict = {}


def cell_stats(world: NKWorld, cells: np.ndarray, m: int = 2000) -> tuple[np.ndarray, np.ndarray]:
    """Per-cell random baseline (mean, std) of `world` fitness; cached per (world, cell). std 0 -> z undefined."""
    from primordial.qd.stubworld import GRID
    mu, sd = np.empty(len(cells)), np.empty(len(cells))
    for j, c in enumerate(cells):
        key = (id(world), int(c))
        if key not in _CELL_STATS:
            rng = np.random.Generator(np.random.PCG64([7, int(c)]))
            f = world.evaluate(popcount_genomes(rng, int(c) // GRID, int(c) % GRID, m))[0].astype(np.float64)
            _CELL_STATS[key] = (f.mean(), f.std())
        mu[j], sd[j] = _CELL_STATS[key]
    return mu, sd


def branch_points(recs, gens, k, z_min, worlds: dict, z_mode: str = "global", return_z: bool = False) -> dict:
    n = len(recs)
    cell = np.array([x[0] for x in recs]); fit = np.array([x[1] for x in recs], np.int64)
    G = np.frombuffer(b"".join(x[2] for x in recs), np.uint8).reshape(n, GLEN)
    P = np.frombuffer(b"".join(x[3] for x in recs), np.uint8).reshape(n, GLEN)
    gen = np.array([x[4] for x in recs])
    ham = np.unpackbits(G ^ P, axis=1).sum(axis=1)

    first_win, parent, opens, seen = {}, np.full(n, -1), np.zeros(n, bool), set()
    for i in range(n):
        g = recs[i][2]
        if gen[i] > 0:
            parent[i] = first_win.get(recs[i][3], -1)
        first_win.setdefault(g, i)
        opens[i] = cell[i] not in seen
        seen.add(cell[i])
    edge = (parent >= 0) & (ham <= H_MAX)
    children = defaultdict(list)
    for i in np.nonzero(edge)[0]:  # parents always precede children in the stream
        children[parent[i]].append(i)

    def descendants(f):  # strict descendants along real edges
        out, stack = set(), list(children.get(f, ()))
        while stack:
            x = stack.pop()
            out.add(x)
            stack.extend(children.get(x, ()))
        return out

    founders = [i for i in range(n) if opens[i] and edge[i] and gen[i] + k <= gens - 1]
    need = defaultdict(list)
    for f in founders:
        need[gen[f] + k].append(f)
    occ, ptr, best = {}, 0, {}
    for t in range(gens):
        while ptr < n and gen[ptr] <= t:
            occ[cell[ptr]] = ptr
            ptr += 1
        if t in need:
            holders = set(occ.values())
            for f in need[t]:
                alive = descendants(f) & holders
                if alive:
                    best[f] = max(alive, key=lambda o: fit[o])
    surv = sorted(best)
    out = {"k": k, "z_min": z_min, "events": n, "real_edges": int(edge.sum()), "edge_rate": round(float(edge[gen > 0].mean()), 4) if (gen > 0).any() else None,
           "cells_opened_after_gen0": int((opens & (gen > 0)).sum()), "founders_eligible": len(founders),
           "founders_surviving": len(surv)}
    rng = np.random.Generator(np.random.PCG64(7))
    ref = random_genomes(rng, 100_000)
    for name, w in worlds.items():
        rf = w.evaluate(ref)[0].astype(np.float64)
        if surv:
            wf, wc = w.evaluate(G[[best[f] for f in surv]])
            if z_mode == "cell":
                mu, sd = cell_stats(w, wc)
                z = np.divide(wf - mu, sd, out=np.full(len(wf), np.nan), where=sd > 0)
            else:
                z = (wf - rf.mean()) / rf.std()
            bp = int((z >= z_min).sum())
        else:
            z, bp = np.empty(0), 0
        if return_z:
            out[f"z_{name}"] = z.tolist()
        out[f"bp_{name}"] = bp
        out[f"transfer_rate_{name}"] = round(bp / len(surv), 4) if surv else None
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=300); p.add_argument("--batch", type=int, default=1024)
    p.add_argument("--port", type=int, default=6394); p.add_argument("--reps", type=int, default=1)
    p.add_argument("--tag", default="full")
    a = p.parse_args()
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    worlds = {"held25": perturbed_world(0.25, 11), "null100": perturbed_world(1.0, 12), "train": NKWorld()}
    for rep in range(a.reps):
        for mode in ("honest", "filler"):
            run = f"e2{mode}-{int(time.time() * 1000) % 10**9}"
            ev = evolve(r, run, mode, a.gens, a.batch, seed=1000 + rep)
            recs = read_events(r, ev["arch"].skey)
            cpu_h = (ev["cpu_worker_s"] + ev["cpu_redis_s"]) / 3600
            for k in (10, K_PRIMARY, 100):
                bp = branch_points(recs, a.gens, k, Z_PRIMARY, worlds)
                row = {"exp_id": EXP, "tag": a.tag, "rep": rep, "mode": mode, "run": run, "gens": a.gens,
                       "batch": a.batch, "h_max": H_MAX, "primary": k == K_PRIMARY, "wins": ev["wins"],
                       "coverage": round(len(ev["arch"].dump()) / N_CELLS, 4),
                       "cpu_worker_s": round(ev["cpu_worker_s"], 2), "cpu_redis_s": round(ev["cpu_redis_s"], 2),
                       "wall_s": round(ev["wall_s"], 2), **bp,
                       "bp_held25_per_cpu_h": round(bp["bp_held25"] / cpu_h, 1), "ts": time.time()}
                print(json.dumps(row), flush=True)
                with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
            ev["arch"].clear()


if __name__ == "__main__":
    main()
