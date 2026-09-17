"""E4b: QD in lane B's Encounter with an archive-level positive control and an exploit audit.

  python -m primordial.qd.e4b_run [--worlds 1,2,3,4,5] [--gens 100] [--batch 256] [--seeds 3] [--tag full]

Posted on the bus before the run (E4b-qd-encounter-archive-positive):
 (1) QD coverage AND qd_score > an archive filled with the same number of random genomes,
     median over run seeds, in >=4/5 worlds each.
 (2) exploit audit: share of 32 sampled elites with unpaid>0 ticks vs 32 random genomes
     (B's finding: an unaffordable action is free and still writes).
 (3) wforge oracle (hash + charge) on 32 sampled elites, run seed 0: honest 0/32 failing;
     skip_lin QD >=30/32 failing; fix_unaffordable QD detection reported.
Search eval: B's NbEncounter (honest, skip_lin); B's NpEncounter for fix_unaffordable (numba
form has no such cheat), the oracle and the unpaid counts. Genome/fitness/descriptor as E4.
Sampled elites are kept under pm-data/E so a late warning can still be audited.
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.qd import e4_run as E4
from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b1.nb_world import NbEncounter
from primordial.soup.b1.np_world import NpEncounter

EXP = "E4b-qd-encounter-archive-positive"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = __import__("pathlib").Path("C:/Users/jcrai/lab/pm-data/E") / EXP


def nb_evaluate(spec: E4.Spec, G: np.ndarray, cheat: str = "") -> np.ndarray:
    P, k = len(G), len(E4.SEEDS)
    w = NbEncounter(spec.mech, spec.wid, cheat=cheat)
    w.prepare(np.tile(E4.SEEDS, P), log=True)
    acts = np.ascontiguousarray(np.repeat(G, k, axis=0).transpose(1, 0, 2, 3)).astype(np.int32)
    w.run(acts)
    last = w.done_tick - 1
    ep = np.clip(w.log_charge[last, np.arange(P * k)], 0, None)
    return ep.sum(1).reshape(P, k).sum(1).astype(np.int32)


def np_evaluate(spec, G, cheat=""):
    return E4.evaluate(spec, G, cheat)[0]


def unpaid(spec: E4.Spec, G: np.ndarray) -> np.ndarray:
    """Ticks with an unaffordable action, summed over the 8 seeds, per genome (honest world)."""
    P, k = len(G), len(E4.SEEDS)
    _, _, w = E4.evaluate(spec, G)
    return w.unpaid.reshape(P, k).sum(1)


def qd(spec, r, run, evalf, cheat, gens, batch, seed):
    arch = LuaArchive(r, run, spec.glen, UNSEEDED)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([seed, spec.gen_seed]))
    t_eval, t0 = 0.0, time.perf_counter()
    for _ in range(gens):
        parents = arch.sample(batch)
        kids = E4.init_genomes(rng, spec, batch) if len(parents) == 0 else E4.mutate(rng, spec, spec.unpack(parents))
        s = time.perf_counter()
        fit = evalf(spec, kids, cheat)
        t_eval += time.perf_counter() - s
        arch.insert(E4.descriptor(kids), fit, spec.pack(kids), np.zeros((batch, 2), np.uint32))
    el = arch.dump()
    return arch, {"cells": len(el), "qd_score": int(sum(v[0] for v in el.values())),
                  "best": int(max(v[0] for v in el.values())), "wall_s": round(time.perf_counter() - t0, 2),
                  "episode_steps_per_s_eval": round(gens * batch * len(E4.SEEDS) * spec.T / t_eval, 1)}


def random_archive(spec, r, run, gens, batch, seed):
    arch = LuaArchive(r, run, spec.glen, UNSEEDED)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([seed + 1, spec.gen_seed]))
    for _ in range(gens):
        kids = E4.init_genomes(rng, spec, batch)
        arch.insert(E4.descriptor(kids), nb_evaluate(spec, kids), spec.pack(kids), np.zeros((batch, 2), np.uint32))
    el = arch.dump()
    return arch, {"cells": len(el), "qd_score": int(sum(v[0] for v in el.values())),
                  "best": int(max(v[0] for v in el.values()))}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="1,2,3,4,5"); p.add_argument("--gens", type=int, default=100)
    p.add_argument("--batch", type=int, default=256); p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--port", type=int, default=6394); p.add_argument("--tag", default="full")
    a = p.parse_args()
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    for gs in [int(x) for x in a.worlds.split(",")]:
        spec = E4.Spec(gs)
        base = {"exp_id": EXP, "tag": a.tag, "gen_seed": gs, "world_id": spec.wid, "T": spec.T, "S": spec.S,
                "W": spec.W, "lin_ops": len(spec.mech.lin_ops), "gens": a.gens, "batch": a.batch}
        # nb vs np fitness agreement on a fixed batch (the search evaluator must be the same world)
        chk = E4.init_genomes(np.random.Generator(np.random.PCG64(gs)), spec, 64)
        nb_np_equal = bool(np.array_equal(nb_evaluate(spec, chk), np_evaluate(spec, chk)))
        for s in range(a.seeds):
            row = {**base, "run_seed": s, "nb_np_fitness_equal": nb_np_equal}
            arch, row["qd"] = qd(spec, r, f"e4b-q-{gs}-{s}", nb_evaluate, "", a.gens, a.batch, 100 + s)
            rarch, row["random_archive"] = random_archive(spec, r, f"e4b-r-{gs}-{s}", a.gens, a.batch, 100 + s)
            if s == 0:
                el = E4.sample_elites(arch, spec, 5)
                rnd = E4.init_genomes(np.random.Generator(np.random.PCG64([9, gs])), spec, len(el))
                u_el, u_rnd = unpaid(spec, el), unpaid(spec, rnd)
                row["unpaid_elites_share"] = round(float((u_el > 0).mean()), 4)
                row["unpaid_random_share"] = round(float((u_rnd > 0).mean()), 4)
                row["unpaid_elites_mean"] = round(float(u_el.mean()), 2)
                row["unpaid_random_mean"] = round(float(u_rnd.mean()), 2)
                row["oracle_honest"] = E4.oracle(spec, el, "")
                carch, row["qd_skip_lin"] = qd(spec, r, f"e4b-c-{gs}", nb_evaluate, "skip_lin", a.gens, a.batch, 100)
                row["oracle_skip_lin"] = E4.oracle(spec, E4.sample_elites(carch, spec, 5), "skip_lin")
                carch.clear()
                farch, row["qd_fix_unaffordable"] = qd(spec, r, f"e4b-f-{gs}", np_evaluate, "fix_unaffordable",
                                                      a.gens, a.batch, 100)
                fel = E4.sample_elites(farch, spec, 5)
                row["oracle_fix_unaffordable"] = E4.oracle(spec, fel, "fix_unaffordable")
                row["fix_unaffordable_elites_with_unpaid"] = int((unpaid(spec, fel) > 0).sum())
                farch.clear()
                np.savez(HOT / f"{a.tag}_w{gs}_elites.npz", honest=el, fix_unaffordable=fel, random=rnd)
            arch.clear(); rarch.clear()
            row["ts"] = time.time()
            print(json.dumps(row), flush=True)
            with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
