"""C-R2-02: drawn cell small_program / nk_stub / decoder_rent / redis_lua / none (draw seed 1525295780674006649).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run.

  world     lane E's NKWorld (N=64, K=4, seed 20260914), descriptor = popcount halves, 33x33 cells.
  genome    small_program: 8 instructions x (op byte, arg byte) = 16 bytes, over a 64-bit register
            starting at 0. op = byte % 8, k = arg & 63, v = arg >> 6. Target-blind decoder:
              0 nop   1 set b[k]   2 flip b[k]   3 set b[k..k+7]   4 clear b[k..k+7]
              5 rotate: new[(i+k)%64] = b[i]   6 new[i] = b[i] xor b[(i+k)%64]
              7 flip every b[i] with (i-k) % (v+2) == 0
  pressure  decoder_rent: net fitness = NK(bits) - LAMBDA * (non-nop instructions), LAMBDA = 16384
            (half the mean per-locus NK value). Fixed before the run.
  substrate redis_lua: decode + NK evaluation + archive insert all run inside Redis (port 6392).
  control   bitset: 8-byte genome = the 64 bits, E1's mutation (p = 1/64 per bit), same Lua evaluator,
            no rent (no decoder). Program mutation: each byte replaced with p = 1/16.
  budget    300 gens x 128 offers, 8 run seeds per arm, equal offers.
  primary   median best net fitness (program, rent) >= median best raw NK fitness (bitset control)
  oracles   numpy reference == Lua on every offer of run seed 0 and on every final elite of every run
            (fit and cell exact). Cheats on 1024 random program genomes: skip_last (instruction 7 not
            executed) mismatches >= 50%; half_rent mismatches >= 90%; honest mismatches 0.

  python -m primordial.cohorts.c.r2_02_nk_program_rent [--gens 300] [--run-seeds 0-7] [--dev]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import redis

from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger
from primordial.qd.archive import LuaArchive
from primordial.qd.stubworld import GRID, N_CELLS, NKWorld, mutate as bit_mutate

EXP = "C-R2-02-nk-small-program-decoder-rent"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
LAMBDA, BATCH, N_INSTR = 16384, 128, 8
TABLE_KEY = "pm:c:r2-02:nk"
CELL_PROG = {"representation": "small_program", "world": "nk_stub", "pressure": "decoder_rent",
             "substrate": "redis_lua", "channel": "none"}
CELL_BITS = {"representation": "bitset", "world": "nk_stub", "pressure": "decoder_rent",
             "substrate": "redis_lua", "channel": "none"}

EVAL_LUA = r"""
local mode, gs, glen = tonumber(ARGV[1]), ARGV[2], tonumber(ARGV[3])
local lambda, cheat = tonumber(ARGV[4]), tonumber(ARGV[5])
local tb = redis.call('GET', KEYS[1])
local sbyte, floor = string.byte, math.floor
local fits, cells = {}, {}
for gi = 0, #gs / glen - 1 do
  local base = gi * glen
  local b = {}
  local active = 0
  if mode == 1 then
    for j = 0, 63 do
      local byte = sbyte(gs, base + floor(j / 8) + 1)
      b[j] = floor(byte / 2 ^ (7 - j % 8)) % 2
    end
  else
    for j = 0, 63 do b[j] = 0 end
    local last = 7
    if cheat == 1 then last = 6 end
    for s = 0, 7 do
      local op = sbyte(gs, base + 2 * s + 1) % 8
      local arg = sbyte(gs, base + 2 * s + 2)
      local k, v = arg % 64, floor(arg / 64)
      if op ~= 0 then active = active + 1 end
      if s <= last then
        if op == 1 then b[k] = 1
        elseif op == 2 then b[k] = 1 - b[k]
        elseif op == 3 then for t = 0, 7 do b[(k + t) % 64] = 1 end
        elseif op == 4 then for t = 0, 7 do b[(k + t) % 64] = 0 end
        elseif op == 5 then
          local nb = {}
          for i = 0, 63 do nb[(i + k) % 64] = b[i] end
          b = nb
        elseif op == 6 then
          local nb = {}
          for i = 0, 63 do nb[i] = (b[i] + b[(i + k) % 64]) % 2 end
          b = nb
        elseif op == 7 then
          for i = 0, 63 do if (i - k) % (v + 2) == 0 then b[i] = 1 - b[i] end end
        end
      end
    end
  end
  local f, d0, d1 = 0, 0, 0
  for j = 0, 63 do
    local idx = 0
    for t = 0, 4 do idx = idx + b[(j + t) % 64] * 2 ^ t end
    local o = (j * 32 + idx) * 2
    local lo, hi = sbyte(tb, o + 1, o + 2)
    f = f + lo + hi * 256
    if j < 32 then d0 = d0 + b[j] else d1 = d1 + b[j] end
  end
  local rent = lambda * active
  if cheat == 2 then rent = floor(lambda / 2) * active end
  fits[gi + 1] = struct.pack('<i4', f - rent)
  cells[gi + 1] = struct.pack('<I4', d0 * 33 + d1)
end
return {table.concat(fits), table.concat(cells)}
"""


def decode_ref(g: np.ndarray, cheat: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Reference program decoder: uint8 [B, 16] -> (bits uint8 [B, 64], active int64 [B])."""
    out = np.zeros((len(g), 64), np.uint8)
    active = np.zeros(len(g), np.int64)
    idx = np.arange(64)
    for n, row in enumerate(g):
        b = np.zeros(64, np.uint8)
        for s in range(N_INSTR):
            op, arg = int(row[2 * s]) % 8, int(row[2 * s + 1])
            k, v = arg & 63, arg >> 6
            active[n] += op != 0
            if cheat == 1 and s == 7:
                continue
            if op == 1:
                b[k] = 1
            elif op == 2:
                b[k] ^= 1
            elif op == 3:
                b[(k + np.arange(8)) % 64] = 1
            elif op == 4:
                b[(k + np.arange(8)) % 64] = 0
            elif op == 5:
                nb = np.empty_like(b); nb[(idx + k) % 64] = b; b = nb
            elif op == 6:
                b = b ^ b[(idx + k) % 64]
            elif op == 7:
                b = b ^ (((idx - k) % (v + 2)) == 0).astype(np.uint8)
        out[n] = b
    return out, active


def eval_ref(world: NKWorld, g: np.ndarray, mode: int, cheat: int = 0) -> tuple[np.ndarray, np.ndarray]:
    if mode == 1:
        return world.evaluate(g)
    bits, active = decode_ref(g, cheat)
    fit, cell = world.evaluate(np.packbits(bits, axis=1))
    lam = LAMBDA // 2 if cheat == 2 else LAMBDA
    return (fit.astype(np.int64) - lam * active).astype(np.int32), cell


class LuaEval:
    def __init__(self, r: redis.Redis, world: NKWorld):
        self.r = r
        r.set(TABLE_KEY, world.table.astype("<u2").tobytes())
        self.script = r.register_script(EVAL_LUA)

    def __call__(self, g: np.ndarray, mode: int, cheat: int = 0) -> tuple[np.ndarray, np.ndarray]:
        f, c = self.script(keys=[TABLE_KEY], args=[mode, g.tobytes(), g.shape[1], LAMBDA, cheat])
        return np.frombuffer(f, "<i4").astype(np.int32), np.frombuffer(c, "<u4").astype(np.uint32)


def run_arm(r, ev, world, mode, rs, gens, audit_all) -> dict:
    glen = 16 if mode == 0 else 8
    arch = LuaArchive(r, f"c-r2-02-m{mode}-r{rs}", glen)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([2, rs, mode]))
    t0, t_eval, audit_offers, audit_bad = time.perf_counter(), 0.0, 0, 0
    for _ in range(gens):
        par = arch.sample(BATCH)
        if len(par) == 0:
            g = rng.integers(0, 256, (BATCH, glen), dtype=np.uint8)
        elif mode == 1:
            g = bit_mutate(rng, par)
        else:
            m = rng.random(par.shape) < 1.0 / glen
            g = np.where(m, rng.integers(0, 256, par.shape, dtype=np.uint8), par)
        s = time.perf_counter()
        fit, cell = ev(g, mode)
        t_eval += time.perf_counter() - s
        if audit_all:
            rf, rc = eval_ref(world, g, mode)
            audit_offers += len(g)
            audit_bad += int(((rf != fit) | (rc != cell)).sum())
        arch.insert(cell, fit, g, np.zeros((len(g), 2), np.uint32))
    el = arch.dump()
    arch.clear()
    cells = np.array(sorted(el), np.uint32)
    ef = np.array([el[int(c)][0] for c in cells], np.int64)
    eg = np.frombuffer(b"".join(el[int(c)][1] for c in cells), np.uint8).reshape(-1, glen)
    rf, rc = eval_ref(world, eg, mode)
    elite_bad = int(((rf.astype(np.int64) != ef) | (rc != cells)).sum())
    best = int(np.argmax(ef))
    raw_best = world.evaluate(eg[best:best + 1] if mode == 1 else np.packbits(decode_ref(eg[best:best + 1])[0], axis=1))[0]
    return {"kind": "run", "arm": "small_program" if mode == 0 else "bitset", "cell": CELL_PROG if mode == 0 else CELL_BITS,
            "run_seed": rs, "gens": gens, "offers": gens * BATCH, "genome_bytes": glen,
            "best_net": int(ef[best]), "best_raw_nk": int(raw_best[0]),
            "best_active": int(decode_ref(eg[best:best + 1])[1][0]) if mode == 0 else 0,
            "qd_score": int(ef.sum()), "archive_cells": len(el), "coverage": round(len(el) / N_CELLS, 4),
            "elites_audited": len(el), "elites_mismatched": elite_bad,
            "offers_audited": audit_offers, "offers_mismatched": audit_bad,
            "lua_eval_s": round(t_eval, 3), "wall_s": round(time.perf_counter() - t0, 2)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=300)
    p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--port", type=int, default=6392)
    p.add_argument("--dev", action="store_true", help="smoke: rows status dev, no QD ledger rows")
    a = p.parse_args()
    lo, hi = (int(x) for x in a.run_seeds.split("-"))
    r = redis.Redis(host="127.0.0.1", port=a.port)
    world = NKWorld()
    ev = LuaEval(r, world)
    decoder_bytes = len(EVAL_LUA.encode())
    rows_path = ROWS.with_name(f"{EXP}.dev.jsonl") if a.dev else ROWS
    with RowWriter(rows_path, EXP, commit_every_s=120) as w:
        crng = np.random.Generator(np.random.PCG64(777))
        cg = crng.integers(0, 256, (1024, 16), dtype=np.uint8)
        ctl = {}
        for name, cheat in (("honest", 0), ("skip_last", 1), ("half_rent", 2)):
            lf, lc = ev(cg, 0, cheat)
            rf, rc = eval_ref(world, cg, 0)
            share = float(((lf != rf) | (lc != rc)).mean())
            ctl[name] = share
            w.write({"kind": "cheat_control", "control": name, "genomes": 1024, "mismatch_share": round(share, 4),
                     "status": "dev" if a.dev else ("control" if cheat == 0 else "cheat")})
        cheats_ok = ctl["honest"] == 0.0 and ctl["skip_last"] >= 0.5 and ctl["half_rent"] >= 0.9
        runs = {0: [], 1: []}
        for rs in range(lo, hi + 1):
            for mode in (0, 1):
                row = run_arm(r, ev, world, mode, rs, a.gens, audit_all=(rs == lo))
                row["status"] = "dev" if a.dev else ("record" if mode == 0 else "control")
                runs[mode].append(row)
                print(json.dumps(row), flush=True)
                w.write(row)
        oracle_clean = cheats_ok and all(x["elites_mismatched"] == 0 and x["offers_mismatched"] == 0
                                         for m in runs.values() for x in m)
        med_prog = float(np.median([x["best_net"] for x in runs[0]]))
        med_bits = float(np.median([x["best_raw_nk"] for x in runs[1]]))
        summary = {"kind": "summary", "cell": CELL_PROG, "n_runs": len(runs[0]), "cheat_controls": ctl,
                   "oracle_clean": oracle_clean, "median_best_net_program": med_prog,
                   "median_best_raw_bitset": med_bits,
                   "median_qd_score_program": float(np.median([x["qd_score"] for x in runs[0]])),
                   "median_qd_score_bitset": float(np.median([x["qd_score"] for x in runs[1]])),
                   "median_coverage_program": float(np.median([x["coverage"] for x in runs[0]])),
                   "median_coverage_bitset": float(np.median([x["coverage"] for x in runs[1]])),
                   "median_best_active_program": float(np.median([x["best_active"] for x in runs[0]])),
                   "decoder_bytes_lua_source": decoder_bytes,
                   "primary": ("INDETERMINATE" if not oracle_clean else
                               ("PASS" if len(runs[0]) >= 8 and med_prog >= med_bits else "FAIL")),
                   "status": "dev" if a.dev else ("record" if oracle_clean else "cheat")}
        print(json.dumps(summary), flush=True)
        w.write(summary)
    r.delete(TABLE_KEY)
    if a.dev:
        return
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        for mode, cell, mech, status in ((0, CELL_PROG, "nk_small_program_8instr_rent16384", summary["status"]),
                                         (1, CELL_BITS, "nk_bitset_control_no_rent", "control")):
            xs = runs[mode]
            q.write({"cell": cell, "mechanism": mech,
                     "fitness": {"held64_median": None, "best_net_median": float(np.median([x["best_net"] for x in xs])),
                                 "qd_score_median": float(np.median([x["qd_score"] for x in xs])),
                                 "coverage_median": float(np.median([x["coverage"] for x in xs])), "n_runs": len(xs)},
                     "footprint": {"genome_bytes": 16 if mode == 0 else 8,
                                   "decoder_bytes": decoder_bytes if mode == 0 else 0},
                     "oracle": "clean (numpy reference == Lua on all offers of seed 0 and all elites; skip_last, "
                               "half_rent caught)" if oracle_clean else f"NOT clean: {json.dumps(ctl)}",
                     "baseline": False, "cohort": "C", "status": status,
                     "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


if __name__ == "__main__":
    main()
