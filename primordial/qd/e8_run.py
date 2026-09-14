"""E8: does closed-loop overfit close with many train seeds? (lane B's B6 fused rollout)

  python -m primordial.qd.e8_run [--worlds 4,1,3] [--ns 8,32,128] [--run-seeds 0,1] [--scale 1.0] [--tag full]

Posted on the bus before the run (E8-fused-closed-loop-seed-scaling):
  closed  E5 tt_digits genome (BrainSpec) evaluated by primordial.soup.b6.fused.FusedRollout
          (exact == E5 numpy rollout per B6 and lane C's C6 audit), 800 x 128 = 102,400 genomes
  open    E4b QD on NbEncounter, 400 x 256 = 102,400 genomes
  seeds   train N in {8, 32, 128} = 9100..9100+N-1; held-out = E6's 64 seeds 30000..30063
  test    top-16 by train fitness, held-out mean per seed
  PRIMARY closed median(N=128) - median(N=8) > max(run range at 128, run range at 8) in >=2/3 worlds
  ORACLES on every closed condition's top-16, 8 held-out seeds, E5 numpy code:
          world 0/16 failing, skip_lin >=14/16; brain 0 mismatched clear rows, skip-odd >=14/16
B, C and E5 code are read-only here.
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.qd import e4_run as E4
from primordial.qd import e4b_run as E4B
from primordial.qd import e5_run as E5
from primordial.qd import e6_run as E6
from primordial.qd.archive import LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "E8-fused-closed-loop-seed-scaling"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = E5.HOT.parent / EXP
HELD64, HELD8 = E6.HELD64, E6.HELD8
TOP = 16


def seeds_n(n: int) -> np.ndarray:
    return np.arange(9100, 9100 + n, dtype=np.int64)


def top_raw(arch: LuaArchive, n: int = TOP) -> np.ndarray:
    el = arch.dump()
    best = sorted(el.values(), key=lambda v: (-v[0], v[1]))[:n]
    return np.frombuffer(b"".join(v[1] for v in best), np.uint8).reshape(-1, arch.glen)


def closed_condition(bs, r, run, seeds, gens, batch, rs):
    arch = LuaArchive(r, run, bs.glen)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([880, rs, bs.gen_seed, len(seeds)]))
    fr = FusedRollout(bs, batch, seeds)
    t0 = time.perf_counter()
    for _ in range(gens):
        par = arch.sample(batch)
        g = E5.init_brains(rng, bs, batch) if len(par) == 0 else E5.mutate_brains(rng, bs, bs.unpack(par))
        fit, cells, _, _, _ = fr.run(g)
        arch.insert(cells, fit, bs.pack(g), np.zeros((batch, 2), np.uint32))
    raw = top_raw(arch)
    cells_n = len(arch.dump())
    arch.clear()
    return raw, cells_n, time.perf_counter() - t0


def closed_score(bs, raw, seeds) -> float:
    g = bs.unpack(raw)
    fit = FusedRollout(bs, len(raw), seeds).run(g)[0]
    return float(fit.mean() / len(seeds))


def open_condition(spec, r, run, seeds, gens, batch, rs):
    E4.SEEDS = seeds
    arch, st = E4B.qd(spec, r, run, E4B.nb_evaluate, "", gens, batch, 890 + 10 * rs)
    raw = top_raw(arch)
    arch.clear()
    return raw, st["cells"], st["wall_s"]


def open_score(spec, raw, seeds) -> float:
    E4.SEEDS = seeds
    return float(E4.evaluate(spec, spec.unpack(raw))[0].mean() / len(seeds))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="4,1,3"); p.add_argument("--ns", default="8,32,128")
    p.add_argument("--run-seeds", default="0,1"); p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--port", type=int, default=6394); p.add_argument("--tag", default="full")
    p.add_argument("--skip-oracles", action="store_true", help="smoke only")
    a = p.parse_args()
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    cg, cb = max(1, int(800 * a.scale)), 128
    og, ob = max(1, int(400 * a.scale)), 256
    for gs in [int(x) for x in a.worlds.split(",")]:
        bs, spec = E5.BrainSpec(gs), E4.Spec(gs)
        for n in [int(x) for x in a.ns.split(",")]:
            tr = seeds_n(n)
            for rs in [int(x) for x in a.run_seeds.split(",")]:
                t0 = time.perf_counter()
                craw, ccells, cwall = closed_condition(bs, r, f"e8-c-{gs}-{n}-{rs}", tr, cg, cb, rs)
                oraw, ocells, owall = open_condition(spec, r, f"e8-o-{gs}-{n}-{rs}", tr, og, ob, rs)
                row = {"exp_id": EXP, "tag": a.tag, "gen_seed": gs, "train_seeds": n, "run_seed": rs,
                       "closed_genomes": cg * cb, "open_genomes": og * ob,
                       "closed_cells": ccells, "open_cells": ocells,
                       "closed_qd_wall_s": round(cwall, 1), "open_qd_wall_s": round(owall, 1),
                       "closed_train": closed_score(bs, craw, tr), "closed_held64": closed_score(bs, craw, HELD64),
                       "open_train": open_score(spec, oraw, tr), "open_held64": open_score(spec, oraw, HELD64)}
                if not a.skip_oracles:
                    E5.SEEDS = HELD8
                    elites = bs.unpack(craw)
                    row["world_oracle_honest"] = E5.world_oracle(bs, elites)
                    row["world_oracle_skip_lin"] = E5.world_oracle(bs, elites, "skip_lin")
                    row["brain_oracle_honest"] = E5.brain_oracle(bs, elites)
                    row["brain_oracle_skip_odd"] = E5.brain_oracle(bs, elites, skip_odd=True)
                E4.SEEDS = np.arange(9100, 9108, dtype=np.int64)
                E5.SEEDS = E4.SEEDS
                np.savez(HOT / f"{a.tag}_w{gs}_n{n}_r{rs}_top.npz", closed=craw, open=oraw)
                row["wall_s"], row["ts"] = round(time.perf_counter() - t0, 1), time.time()
                print(json.dumps(row), flush=True)
                with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                    fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
