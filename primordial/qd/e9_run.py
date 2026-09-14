"""E9: is E7b's family ranking real? 8 run seeds per family on lane B's B6b fused rollout.

  python -m primordial.qd.e9_run [--worlds 4,1,3] [--fams linear,tt_feat,tt_digits] [--run-seeds 0-7]
                                 [--gens 200] [--batch 128] [--tag full]

Posted on the bus before the run (E9-family-ranking-fused-8-seeds):
  genome  E7's G7 (lane C C4 family params + lane E codebook), read-only reuse of e7_run
  eval    primordial.soup.b6.fused.FusedRollout(spec, P, seeds, family=...).run((params, codebook))
          (exact == E7.rollout per B6b and lane C's C6b audit)
  setup   E7 exactly: 200 x 128 genomes, E6's 8 train seeds, top-16 on E6's 64 held-out seeds
  PRIMARY linear beats the runner-up family (next-highest median) by one-sided Mann-Whitney U,
          p < 0.05, in >=2/3 worlds
  ORACLES run seed 0 of each family x world, E7 numpy oracles on 8 held-out seeds:
          world 0/16 failing, skip_lin >=14/16; brain 0 mismatched clear rows, cheat >=14/16
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.brain import genomes as gm
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "E9-family-ranking-fused-8-seeds"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = E7.HOT.parent / EXP
TRAIN, HELD64, HELD8, TOP = E7.TRAIN, E7.HELD64, E7.HELD8, E7.TOP


def parse_seeds(s: str) -> list[int]:
    if "-" in s:
        lo, hi = s.split("-")
        return list(range(int(lo), int(hi) + 1))
    return [int(x) for x in s.split(",")]


def fused_score(g7, fam, raw, seeds) -> float:
    fit = FusedRollout(g7.spec, len(raw), seeds, family=fam).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="4,1,3"); p.add_argument("--fams", default="linear,tt_feat,tt_digits")
    p.add_argument("--run-seeds", default="0-7"); p.add_argument("--gens", type=int, default=200)
    p.add_argument("--batch", type=int, default=128); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--tag", default="full"); p.add_argument("--skip-oracles", action="store_true")
    a = p.parse_args()
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(port=a.port)
    for gs in [int(x) for x in a.worlds.split(",")]:
        for fam in a.fams.split(","):
            for rs in parse_seeds(a.run_seeds):
                t0 = time.perf_counter()
                g7 = E7.G7(gs, fam)
                arch = LuaArchive(r, f"e9-{gs}-{fam}-{rs}", g7.glen)
                arch.clear()
                rng = np.random.Generator(np.random.PCG64([990, rs, gs, list(gm.FAMILIES).index(fam)]))
                fr = FusedRollout(g7.spec, a.batch, TRAIN, family=fam)
                t_eval = 0.0
                for _ in range(a.gens):
                    par = arch.sample(a.batch)
                    g = g7.init(rng, a.batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
                    s = time.perf_counter()
                    fit, cells = fr.run(g)[:2]
                    t_eval += time.perf_counter() - s
                    arch.insert(cells, fit, g7.pack(g), np.zeros((a.batch, 2), np.uint32))
                el = arch.dump()
                raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]),
                                    np.uint8).reshape(-1, g7.glen)
                arch.clear()
                np.save(HOT / f"{a.tag}_w{gs}_{fam}_r{rs}_top.npy", raw)
                row = {"exp_id": EXP, "tag": a.tag, "gen_seed": gs, "family": fam, "run_seed": rs,
                       "param_bytes": g7.pb, "genomes": a.gens * a.batch, "cells": len(el),
                       "fused_eval_s": round(t_eval, 2),
                       "train_per_seed": fused_score(g7, fam, raw, TRAIN),
                       "held64_per_seed": fused_score(g7, fam, raw, HELD64)}
                if rs == 0 and not a.skip_oracles:
                    top = g7.unpack(raw)
                    row["world_oracle_honest"] = E7.world_oracle(g7, top, HELD8)
                    row["world_oracle_skip_lin"] = E7.world_oracle(g7, top, HELD8, "skip_lin")
                    row["brain_oracle_honest"] = E7.brain_oracle(g7, top, HELD8)
                    row["brain_oracle_cheat"] = E7.brain_oracle(g7, top, HELD8, cheat=True)
                row["wall_s"], row["ts"] = round(time.perf_counter() - t0, 1), time.time()
                print(json.dumps(row), flush=True)
                with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                    fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
