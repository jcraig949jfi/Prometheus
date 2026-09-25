"""C-R6-AP-02 (ANTI_PRIOR, cell assigned by code): bitset / nk_stub / obs_delay / redis_lua / none
(anti_prior.assign exp_id C-R6-AP-02, round 6).

The experimenter received only the cell; the prior and the arm are unread. nk_stub is not a screened graphworld world:
landscape rows only, no clause A claim. The definitions below are fixed before any run.

  world     lane E's NKWorld (N=64, K=4, seed 20260914; E1 / C-R2-02), one landscape. Fitness = NK(bits).
  brain     bitset: the 8-byte genome is the 64 bits (E1). A bitset reads no observation, so the only observation in
            this cell is the one the SEARCH makes: an offer's fitness entering the archive that parents are drawn from.
  pressure  obs_delay on that observation, in generations. d = 2 = the only non-zero obs_delay the world generator
            emits (SerendipityFoundry wforge world.py INTERFACE_MUTATE: obs_delay = 0 if obs_delay else 2); taken, not
            tuned. At the start of generation t every pending batch evaluated at generation <= t - 1 - d is inserted,
            then parents are sampled. d = 0 is ordinary MAP-Elites (batch t - 1 visible at t). Pending batches are
            flushed after the last generation, so both arms end with every offer inserted (equal offers).
  substrate redis_lua: NK evaluation (table in Redis, bit decode + neighbourhood index + sum in Lua) and the archive
            (E's LuaArchive, atomic insert, seeded sampler) run inside Redis :6392.
  arms      cell (d = 2) vs control (d = 0), same GA and sampler streams. Mutation E1 (p = 1/64 per bit); an empty
            sample (the archive has nothing visible yet) draws 128 uniform genomes.
  budget    GENS x 128 offers per run (GENS fixed below from a no-rows timing check, disclosed).
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 6201]); sampler [family + 1, run_seed, arm, 6201].
  reader    top1_train: the archive elite with the highest NK fitness (ties: smaller genome bytes); value = its NK
            fitness (the landscape is both the selection and the score; a bitset cannot transfer, C-R2-09).
  primary   median over the 32 runs of top1 NK (cell) >= median (control) - 0.5 * IQR (control).
  oracles   family 4200 run seed 0, each arm:
            world    numpy NKWorld.evaluate == Lua (fitness and cell) on every offer of the run; in EVERY run, every final
                     elite's archive fitness and cell == numpy recount of the STORED genome bytes (exact). Cheat: the Lua
                     evaluator with a K=3 window mismatches >= 90% of that run's final elites.
            replay   a client-side serial replay (python dict archive, the same total order, the same PCG64 streams, the
                     sampler's sorted-cell index rule, the same insertion schedule) reproduces the per-generation parent
                     hashes (0 mismatched generations) and the final archive (0 mismatched cells).
            delay    cell arm only: the same replay with d = 0 (cheat no_delay) mismatches the recorded parent hashes in
                     >= 1 generation. A delay that is not applied cannot pass both replay and delay.

  worker:  job = primordial.cohorts.c.r6_ap02_bitset_nk_obs_delay_lua:job
  dev:     python -m primordial.cohorts.c.r6_ap02_bitset_nk_obs_delay_lua dev   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from primordial.qd.stubworld import GRID, N_CELLS, NKWorld, mutate as bit_mutate

EXP = "C-R6-AP-02-bitset-nk-obs-delay-lua"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "bitset", "world": "nk_stub", "pressure": "obs_delay", "substrate": "redis_lua",
        "channel": "none"}
CELL_CTRL = dict(CELL, pressure="obs_delay_0_control")
DELAY = 2
BATCH, GLEN = 128, 8
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
GENS = 800      # no-rows dev check (20 gens): 0.0056 wall-s / gen (Lua CPU is server-side). Rule: largest of
                # {100, 200, 300, 400, 800} whose projection (64 runs) stays <= 1200 wall-s; 800 projects 287 s
PORT = 6392
TABLE_KEY = "pm:c:r6-ap02:nk"

EVAL_LUA = r"""
local gs, win = ARGV[1], tonumber(ARGV[2])
local tb = redis.call('GET', KEYS[1])
local sbyte, floor = string.byte, math.floor
local fits, cells = {}, {}
for gi = 0, #gs / 8 - 1 do
  local b = {}
  for j = 0, 63 do
    local byte = sbyte(gs, gi * 8 + floor(j / 8) + 1)
    b[j] = floor(byte / 2 ^ (7 - j % 8)) % 2
  end
  local f, d0, d1 = 0, 0, 0
  for j = 0, 63 do
    local idx = 0
    for t = 0, win - 1 do idx = idx + b[(j + t) % 64] * 2 ^ t end
    local o = (j * 32 + idx) * 2
    local lo, hi = sbyte(tb, o + 1, o + 2)
    f = f + lo + hi * 256
    if j < 32 then d0 = d0 + b[j] else d1 = d1 + b[j] end
  end
  fits[gi + 1] = struct.pack('<i4', f)
  cells[gi + 1] = struct.pack('<I4', d0 * 33 + d1)
end
return {table.concat(fits), table.concat(cells)}
"""


class LuaEval:
    def __init__(self, r, world: NKWorld):
        r.set(TABLE_KEY, world.table.astype("<u2").tobytes())
        self.script = r.register_script(EVAL_LUA)

    def __call__(self, g: np.ndarray, window: int = 5):
        f, c = self.script(keys=[TABLE_KEY], args=[np.ascontiguousarray(g, np.uint8).tobytes(), window])
        return np.frombuffer(f, "<i4").astype(np.int64), np.frombuffer(c, "<u4").astype(np.uint32)


def _h(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


def run(r, ev, world, family, rs, arm_i, delay, gens, track=False):
    from primordial.qd.archive import LuaArchive
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, 6201]))
    arch = LuaArchive(r, f"c-r6-ap02-{family}-{rs}-{arm_i}", GLEN, sampler_seed=[family + 1, rs, arm_i, 6201])
    arch.clear()
    zeros = np.zeros((BATCH, 2), np.uint32)
    pending, hashes = [], []
    offers = offer_bad = 0
    for t in range(gens):
        while pending and pending[0][0] <= t - 1 - delay:
            _, c, f, g = pending.pop(0)
            arch.insert(c, f.astype(np.int32), g, zeros)
        par = arch.sample(BATCH)
        g = rng.integers(0, 256, (BATCH, GLEN), dtype=np.uint8) if len(par) == 0 else bit_mutate(rng, par)
        fit, cell = ev(g)
        if track:
            hashes.append(_h(par))
            rf, rc = world.evaluate(g)
            offers += len(g)
            offer_bad += int(((rf.astype(np.int64) != fit) | (rc != cell)).sum())
        pending.append((t, cell, fit, g))
    for _, c, f, g in pending:
        arch.insert(c, f.astype(np.int32), g, zeros)
    el = arch.dump()
    arch.clear()
    return el, hashes, offers, offer_bad


def replay(world, family, rs, arm_i, delay, gens):
    """Client-side serial reference of run(): -> (archive {cell: (f, genome bytes)}, parent hashes)."""
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, 6201]))
    srng = np.random.Generator(np.random.PCG64([family + 1, rs, arm_i, 6201]))
    arch: dict = {}
    pending, hashes = [], []

    def ins(cells, fits, gs):
        for c, f, g in zip(cells.tolist(), fits.tolist(), gs):
            gb = g.tobytes()
            old = arch.get(c)
            if old is None or f > old[0] or (f == old[0] and gb < old[1]):
                arch[c] = (f, gb)

    for t in range(gens):
        while pending and pending[0][0] <= t - 1 - delay:
            _, c, f, g = pending.pop(0)
            ins(c, f, g)
        u = srng.random(BATCH)
        cs = sorted(arch)
        if cs:
            j = np.minimum(np.floor(u * len(cs)).astype(np.int64), len(cs) - 1)
            par = np.frombuffer(b"".join(arch[cs[int(x)]][1] for x in j), np.uint8).reshape(-1, GLEN)
        else:
            par = np.empty((0, GLEN), np.uint8)
        hashes.append(_h(par))
        g = rng.integers(0, 256, (BATCH, GLEN), dtype=np.uint8) if len(par) == 0 else bit_mutate(rng, par)
        f, c = world.evaluate(g)
        pending.append((t, c.astype(np.uint32), f.astype(np.int64), g))
    for _, c, f, g in pending:
        ins(c, f, g)
    return arch, hashes


def summarize(el):
    order = sorted(el.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
    eg = np.frombuffer(b"".join(v[1] for _, v in order), np.uint8).reshape(-1, GLEN)
    ef = np.array([v[0] for _, v in order], np.int64)
    ec = np.array([c for c, _ in order], np.uint32)
    return eg, ef, ec


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    world = NKWorld()
    ev = LuaEval(r, world)
    arms = ((0, "cell", DELAY, CELL), (1, "control", 0, CELL_CTRL))
    todo = [(f, rs, ai) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for ai in (0, 1)]
    st = ctx.load_checkpoint() or {"next": 0, "best": {"cell": [], "control": []}, "clean": True, "ref": False}
    if not st["ref"]:
        rr = np.random.Generator(np.random.PCG64(5))
        rand = world.evaluate(rr.integers(0, 256, (4096, GLEN), dtype=np.uint8))[0]
        ctx.emit({"kind": "reference", "exp_id": exp_id, "gens": gens, "batch": BATCH, "delay": DELAY,
                  "delay_basis": "wforge world.py INTERFACE_MUTATE obs_delay in {0, 2}",
                  "random_nk_mean": float(rand.mean()), "random_nk_max_4096": int(rand.max()), "status": "control",
                  "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, ai = todo[st["next"]]
        _, arm, delay, cell = arms[ai]
        first = fam == FAMILIES[0] and rs == 0
        t0, c0 = time.perf_counter(), time.process_time()
        el, hashes, offers, offer_bad = run(r, ev, world, fam, rs, ai, delay, gens, track=first)
        eg, ef, ec = summarize(el)
        rf, rc = world.evaluate(eg)
        elite_bad = int(((rf.astype(np.int64) != ef) | (rc != ec)).sum())
        ok = elite_bad == 0 and offer_bad == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens, "delay": delay,
               "offers": gens * BATCH, "genome_bytes": GLEN, "reader": "top1_train", "top1_nk": int(ef[0]),
               "qd_score": int(ef.sum()), "archive_cells": len(el), "coverage": round(len(el) / N_CELLS, 4),
               "elites_audited": int(len(eg)), "elites_mismatched": elite_bad, "offers_audited": offers,
               "offers_mismatched": offer_bad, "status": "record" if arm == "cell" else "control"}
        if first:
            k3 = ev(eg, window=4)[0]
            rep_arch, rep_hash = replay(world, fam, rs, ai, delay, gens)
            rep_bad_cells = len(set(rep_arch) ^ set(el)) + sum(
                1 for c in set(rep_arch) & set(el) if rep_arch[c] != (el[c][0], el[c][1]))
            o = {"k3_window_share": round(float((k3 != ef).mean()), 4), "k3_elites": int(len(eg)),
                 "replay_mismatched_gens": int(sum(a != b for a, b in zip(rep_hash, hashes))) + abs(len(rep_hash) - len(hashes)),
                 "replay_mismatched_cells": int(rep_bad_cells)}
            o["ok"] = bool(ok and o["k3_window_share"] >= 0.9 and o["replay_mismatched_gens"] == 0
                           and o["replay_mismatched_cells"] == 0)
            if delay:
                _, nd_hash = replay(world, fam, rs, ai, 0, gens)
                o["no_delay_mismatched_gens"] = int(sum(a != b for a, b in zip(nd_hash, hashes)))
                o["ok"] = o["ok"] and o["no_delay_mismatched_gens"] >= 1
            row["oracles"] = o
            ok = o["ok"]
        st["clean"] = st["clean"] and ok
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["best"][arm].append(row["top1_nk"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    r.delete(TABLE_KEY)
    q = {a: [float(x) for x in np.percentile(st["best"][a], [25, 50, 75])] for a in st["best"]}
    bar = q["control"][1] - 0.5 * (q["control"][2] - q["control"][0])
    n = {a: len(st["best"][a]) for a in st["best"]}
    full = all(v == len(FAMILIES) * RUNS_PER_FAMILY for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if q["cell"][1] >= bar else "FAIL")
    paired = sum(1 for a, b in zip(st["best"]["cell"], st["best"]["control"]) if a < b)
    ctx.emit({"kind": "summary", "exp_id": exp_id, "cell": CELL, "runs_total": n["cell"],
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "top1_median_cell": q["cell"][1], "iqr_cell": q["cell"][2] - q["cell"][0],
              "top1_median_control": q["control"][1], "iqr_control": q["control"][2] - q["control"][0],
              "bar": bar, "paired_cell_below_control": paired, "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: nk_stub is not a screened graphworld world",
              "status": "record" if st["clean"] else "cheat", "ts": round(time.time(), 3)})


def dev(gens: int = 20) -> None:
    """No rows: Lua == numpy, replay exactness and no_delay eligibility on a short cell-arm run, wall per gen."""
    import redis
    r = redis.Redis(host="127.0.0.1", port=PORT)
    world = NKWorld()
    ev = LuaEval(r, world)
    t = time.perf_counter()
    el, hashes, offers, bad = run(r, ev, world, 4200, 0, 0, DELAY, gens, track=True)
    wall = time.perf_counter() - t
    rep_arch, rep_hash = replay(world, 4200, 0, 0, DELAY, gens)
    _, nd_hash = replay(world, 4200, 0, 0, 0, gens)
    eg, ef, _ = summarize(el)
    out = {"gens": gens, "wall_s_per_gen_with_audit": round(wall / gens, 4), "offers_mismatched": bad,
           "replay_mismatched_gens": sum(a != b for a, b in zip(rep_hash, hashes)),
           "replay_cells_equal": rep_arch == {c: (v[0], v[1]) for c, v in el.items()},
           "no_delay_mismatched_gens": sum(a != b for a, b in zip(nd_hash, hashes)),
           "k3_share": round(float((ev(eg, window=4)[0] != ef).mean()), 4), "top1": int(ef[0])}
    t = time.perf_counter()
    run(r, ev, world, 4200, 0, 1, 0, gens)
    out["wall_s_per_gen_no_audit"] = round((time.perf_counter() - t) / gens, 4)
    r.delete(TABLE_KEY)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 20) if sys.argv[1] == "dev" else None
