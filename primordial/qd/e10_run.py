"""E10: linear closed-loop brain vs open-loop sequences, both trained on 128 seeds.

  python -m primordial.qd.e10_run [--worlds 4,1,3] [--run-seeds 0-3] [--scale 1.0] [--tag full]

Posted on the bus before the run (E10-linear-closed-vs-open-128-seeds):
  closed  lane C linear genome + lane E codebook (E7.G7), lane B B6b FusedRollout(family="linear"),
          800 x 128 = 102,400 genomes on train seeds 9100..9227
  open    E4b QD on NbEncounter (E8.open_condition), 400 x 256 = 102,400 genomes, same seeds
  test    top-16 by train fitness on E6's 64 held-out seeds, per-seed mean
  PRIMARY linear held-out > open held-out, one-sided Mann-Whitney U p<0.05 over 4 run seeds, >=2/3 worlds
  ORACLES run seed 0, E7 numpy code on 8 held-out seeds: world 0/16, skip_lin >=14/16;
          brain 0 mismatched clear rows, cheat >=14/16
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd import e8_run as E8
from primordial.qd import e9_run as E9
from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "E10-linear-closed-vs-open-128-seeds"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = E7.HOT.parent / EXP
TRAIN = E8.seeds_n(128)
HELD64, HELD8, TOP = E7.HELD64, E7.HELD8, E7.TOP
FAM = "linear"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="4,1,3"); p.add_argument("--run-seeds", default="0-3")
    p.add_argument("--scale", type=float, default=1.0); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--tag", default="full"); p.add_argument("--skip-oracles", action="store_true")
    a = p.parse_args()
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    cg, cb = max(1, int(800 * a.scale)), 128
    og, ob = max(1, int(400 * a.scale)), 256
    for gs in [int(x) for x in a.worlds.split(",")]:
        for rs in E9.parse_seeds(a.run_seeds):
            t0 = time.perf_counter()
            g7 = E7.G7(gs, FAM)
            arch = LuaArchive(r, f"e10-c-{gs}-{rs}", g7.glen, UNSEEDED)
            arch.clear()
            rng = np.random.Generator(np.random.PCG64([1010, rs, gs]))
            fr = FusedRollout(g7.spec, cb, TRAIN, family=FAM)
            tc = time.perf_counter()
            for _ in range(cg):
                par = arch.sample(cb)
                g = g7.init(rng, cb) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
                fit, cells = fr.run(g)[:2]
                arch.insert(cells, fit, g7.pack(g), np.zeros((cb, 2), np.uint32))
            closed_wall = time.perf_counter() - tc
            el = arch.dump()
            craw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]),
                                 np.uint8).reshape(-1, g7.glen)
            ccells = len(el)
            arch.clear()
            spec = E4.Spec(gs)
            oraw, ocells, owall = E8.open_condition(spec, r, f"e10-o-{gs}-{rs}", TRAIN, og, ob, rs + 10)
            row = {"exp_id": EXP, "tag": a.tag, "gen_seed": gs, "run_seed": rs, "train_seeds": len(TRAIN),
                   "closed_family": FAM, "closed_genomes": cg * cb, "open_genomes": og * ob,
                   "closed_cells": ccells, "open_cells": ocells,
                   "closed_qd_wall_s": round(closed_wall, 1), "open_qd_wall_s": round(owall, 1),
                   "closed_train": E9.fused_score(g7, FAM, craw, TRAIN),
                   "closed_held64": E9.fused_score(g7, FAM, craw, HELD64),
                   "open_train": E8.open_score(spec, oraw, TRAIN), "open_held64": E8.open_score(spec, oraw, HELD64)}
            E4.SEEDS = np.arange(9100, 9108, dtype=np.int64)
            if rs == 0 and not a.skip_oracles:
                top = g7.unpack(craw)
                row["world_oracle_honest"] = E7.world_oracle(g7, top, HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(g7, top, HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(g7, top, HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(g7, top, HELD8, cheat=True)
            np.savez(HOT / f"{a.tag}_w{gs}_r{rs}_top.npz", closed=craw, open=oraw)
            row["wall_s"], row["ts"] = round(time.perf_counter() - t0, 1), time.time()
            print(json.dumps(row), flush=True)
            with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
