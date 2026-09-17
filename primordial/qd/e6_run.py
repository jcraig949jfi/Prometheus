"""E6: do evolved elites generalise to held-out episode seeds? Open-loop vs closed-loop.

  python -m primordial.qd.e6_run [--worlds 1,2,3,4,5] [--scale 1.0] [--tag full]

Posted on the bus before the run (with the eligibility pre-check):
  both conditions 25,600 genomes on the 8 train seeds (E4.SEEDS): open-loop = E4b QD
  (NbEncounter, 100x256), closed-loop = E5 TT-brain QD (200x128). Top-16 elites by
  train fitness are scored on 64 HELD-OUT seeds (per-seed mean).
  SCIENCE  closed held-out mean > open held-out mean in >=2/3 eligible worlds (1, 3, 4).
  LEAK     open-loop QD trained on HELD8 (8 of the held-out seeds) must beat honest
           open-loop on HELD8 in 3/3 eligible worlds, else INDETERMINATE.
  ORACLE   on HELD8: honest open and closed top-16 0 failing; closed in skip_lin >=14/16.
Seed sets are swapped by rebinding SEEDS in e4_run and e5_run (functions read the module
global at call time).
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
from primordial.qd.archive import UNSEEDED, LuaArchive

EXP = "E6-heldout-seed-generalisation"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = E5.HOT.parent / EXP
TRAIN = E4.SEEDS.copy()
HELD64 = np.arange(30000, 30064, dtype=np.int64)
HELD8 = HELD64[:8]
ELIGIBLE = (1, 3, 4)
TOP = 16


def use(seeds: np.ndarray) -> None:
    E4.SEEDS = seeds
    E5.SEEDS = seeds


def top_genomes(arch: LuaArchive, n: int = TOP) -> np.ndarray:
    el = arch.dump()
    best = sorted(el.values(), key=lambda v: (-v[0], v[1]))[:n]
    return np.frombuffer(b"".join(v[1] for v in best), np.uint8).reshape(-1, arch.glen)


def closed_qd(bs, r, run, gens, batch, seed) -> LuaArchive:
    arch = LuaArchive(r, run, bs.glen, UNSEEDED)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([seed, bs.gen_seed]))
    for _ in range(gens):
        par = arch.sample(batch)
        g = E5.init_brains(rng, bs, batch) if len(par) == 0 else E5.mutate_brains(rng, bs, bs.unpack(par))
        fit, cells, _, _ = E5.rollout(bs, g)
        arch.insert(cells, fit, bs.pack(g), np.zeros((batch, 2), np.uint32))
    return arch


def open_score(spec, raw, seeds):
    use(seeds)
    return float(E4.evaluate(spec, spec.unpack(raw))[0].mean() / len(seeds))


def closed_score(bs, raw, seeds):
    use(seeds)
    return float(E5.rollout(bs, bs.unpack(raw))[0].mean() / len(seeds))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="1,2,3,4,5"); p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--port", type=int, default=6394); p.add_argument("--tag", default="full")
    p.add_argument("--train-seeds", type=int, default=8, help="train on seeds 9100..9100+N-1 (E6: 8)")
    p.add_argument("--exp", default=EXP, help="exp_id; rows go to ledger/rows/E/<exp>.jsonl")
    a = p.parse_args()
    global TRAIN, ROWS
    TRAIN = np.arange(9100, 9100 + a.train_seeds, dtype=np.int64)
    ROWS = E4.ROWS.with_name(f"{a.exp}.jsonl")
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    og, ob = max(1, int(100 * a.scale)), 256
    cg, cb = max(1, int(200 * a.scale)), 128
    for gs in [int(x) for x in a.worlds.split(",")]:
        t0 = time.perf_counter()
        spec, bs = E4.Spec(gs), E5.BrainSpec(gs)
        use(TRAIN)
        oarch, _ = E4B.qd(spec, r, f"e6-open-{gs}", E4B.nb_evaluate, "", og, ob, 600)
        otop = top_genomes(oarch); oarch.clear()
        use(TRAIN)
        carch = closed_qd(bs, r, f"e6-closed-{gs}", cg, cb, 601)
        ctop = top_genomes(carch); carch.clear()
        use(HELD8)
        larch, _ = E4B.qd(spec, r, f"e6-leak-{gs}", E4B.nb_evaluate, "", og, ob, 602)
        ltop = top_genomes(larch); larch.clear()
        row = {
            "exp_id": a.exp, "tag": a.tag, "gen_seed": gs, "eligible": gs in ELIGIBLE, "T": spec.T,
            "train_seeds": len(TRAIN),
            "open_genomes": og * ob, "closed_genomes": cg * cb, "top": TOP,
            "open_train": open_score(spec, otop, TRAIN), "closed_train": closed_score(bs, ctop, TRAIN),
            "open_held64": open_score(spec, otop, HELD64), "closed_held64": closed_score(bs, ctop, HELD64),
            "open_held8": open_score(spec, otop, HELD8), "leak_open_held8": open_score(spec, ltop, HELD8),
        }
        row["closed_beats_open_held"] = row["closed_held64"] > row["open_held64"]
        row["leak_beats_honest_held8"] = row["leak_open_held8"] > row["open_held8"]
        use(HELD8)
        row["oracle_open_held8"] = E4.oracle(spec, spec.unpack(otop), "")
        row["oracle_closed_held8"] = E5.world_oracle(bs, bs.unpack(ctop))
        row["oracle_closed_skip_lin_held8"] = E5.world_oracle(bs, bs.unpack(ctop), "skip_lin")
        use(TRAIN)
        np.savez(HOT / f"{a.tag}_w{gs}_top.npz", open=otop, closed=ctop, leak=ltop)
        row["wall_s"], row["ts"] = round(time.perf_counter() - t0, 1), time.time()
        print(json.dumps(row), flush=True)
        with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
