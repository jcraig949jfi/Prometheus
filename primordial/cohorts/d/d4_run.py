"""D4 (ANOM-1789417965533-0): same seed, identical fitness landscape, different QD best.

LuaArchive.sample draws parents with server-side ZRANDMEMBER, which no client seed controls. This reruns
E4's QD loop (genomes, mutation, descriptor, fitness imported read-only from primordial.qd.e4_run) with
  LUA  the library archive, twice at the same seed
  DET  the same archive with a seeded client-side sampler (copy-on-write subclass, lane D)
and compares final-archive hashes. Predicate on the bus ("D4-qd-sampler-nondeterminism HYPOTHESIS").

usage: python -m primordial.cohorts.d.d4_run [--worlds 1,2,3,4,5] [--gens 100]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

import numpy as np
import redis

from primordial.fabric.rows import RowWriter
from primordial.qd import e4_run as E4
from primordial.qd.archive import LuaArchive

EXP = "D4-qd-sampler-nondeterminism"
ROOT = pathlib.Path(__file__).resolve().parents[2]
PORT, BATCH, SEED = 6393, 256, 41


class DetArchive(LuaArchive):
    """LuaArchive whose parent sample is drawn by a client PCG64 over the cells in ascending order
    (with replacement, like ZRANDMEMBER with a negative count)."""

    def __init__(self, r, run, glen, sampler_seed):
        super().__init__(r, run, glen)
        self.srng = np.random.Generator(np.random.PCG64(sampler_seed))

    def sample(self, n: int) -> np.ndarray:
        cells = sorted(int(c) for c in self.r.zrange(self.zkey, 0, -1))
        if not cells:
            return np.empty((0, self.glen), np.uint8)
        pick = self.srng.integers(0, len(cells), n)
        p = self.r.pipeline(transaction=False)
        for i in pick:
            p.hget(self.pre + str(cells[i]), "g")
        return np.frombuffer(b"".join(p.execute()), np.uint8).reshape(-1, self.glen)


def qd(spec, arch, cheat, gens):
    """E4.qd's loop with the archive injected; also hashes the parent stream."""
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([SEED, spec.gen_seed]))
    sh = hashlib.sha256()
    best = 0
    t0 = time.perf_counter()
    for _ in range(gens):
        parents = arch.sample(BATCH)
        sh.update(parents.tobytes())
        kids = E4.init_genomes(rng, spec, BATCH) if len(parents) == 0 else E4.mutate(rng, spec, spec.unpack(parents))
        fit, _, _ = E4.evaluate(spec, kids, cheat)
        best = max(best, int(fit.max()))
        arch.insert(E4.descriptor(kids), fit, spec.pack(kids), np.zeros((BATCH, 2), np.uint32))
    el = arch.dump()
    ah = hashlib.sha256()
    for c in sorted(el):
        ah.update(int(c).to_bytes(4, "little") + int(el[c][0]).to_bytes(8, "little", signed=True) + el[c][1])
    arch.clear()
    return {"best": best, "cells": len(el), "qd_score": int(sum(v[0] for v in el.values())),
            "archive_sha": ah.hexdigest()[:16], "parent_stream_sha": sh.hexdigest()[:16],
            "wall_s": round(time.perf_counter() - t0, 2)}


ARMS = (("lua_honest_a", "lua", "", None), ("lua_honest_b", "lua", "", None),
        ("det_honest_s0_a", "det", "", 0), ("det_honest_s0_b", "det", "", 0),
        ("det_honest_s1", "det", "", 1), ("det_skip_lin_s0", "det", "skip_lin", 0))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,2,3,4,5"); ap.add_argument("--gens", type=int, default=100)
    a = ap.parse_args(argv)
    status = "record" if a.gens == 100 else "dev"
    tag = EXP if a.gens == 100 else f"{EXP}-dev"
    r = redis.Redis(host="127.0.0.1", port=PORT)
    res = {}
    with RowWriter(ROOT / "ledger" / "rows" / "D" / f"{tag}.jsonl", tag, commit_every_s=120) as w:
        for gs in [int(x) for x in a.worlds.split(",")]:
            spec = E4.Spec(gs)
            for name, kind, cheat, sseed in ARMS:
                run = f"d4-{gs}-{name}"
                arch = LuaArchive(r, run, spec.glen) if kind == "lua" else DetArchive(r, run, spec.glen, [sseed, gs])
                out = qd(spec, arch, cheat, a.gens)
                res[(gs, name)] = out
                row = {"status": "cheat" if cheat else ("control" if name == "det_honest_s1" else status),
                       "kind": "qd_run", "gen_seed": gs, "arm": name, "archive": kind, "cheat": cheat,
                       "sampler_seed": sseed, "qd_seed": SEED, "gens": a.gens, "batch": BATCH, **out}
                w.write(row)
                print(json.dumps(row), flush=True)
        worlds = sorted({g for g, _ in res})
        eq = lambda g, x, y: res[(g, x)]["archive_sha"] == res[(g, y)]["archive_sha"]
        checks = {
            "H1_lua_repeat_differs_ge4of5": sum(not eq(g, "lua_honest_a", "lua_honest_b") for g in worlds) >= 4,
            "H2_det_repeat_identical_all": all(eq(g, "det_honest_s0_a", "det_honest_s0_b") for g in worlds),
            "H3_det_skip_lin_eq_honest_iff_w124": all(eq(g, "det_honest_s0_a", "det_skip_lin_s0") == (g in (1, 2, 4))
                                                      for g in worlds),
            "C_sampler_seed_changes_archive_ge4of5": sum(not eq(g, "det_honest_s0_a", "det_honest_s1")
                                                         for g in worlds) >= 4,
        }
        summary = {"exp": tag, "checks": checks, "worlds": worlds,
                   "table": {f"w{g}": {n: [res[(g, n)]["best"], res[(g, n)]["cells"], res[(g, n)]["archive_sha"]]
                                       for n, *_ in ARMS} for g in worlds}}
        w.write({"status": status, "kind": "summary", **summary})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
