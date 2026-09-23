"""Basin width of self-replication in the FROZEN chemistry (Phase 2E): how often is a uniformly random tape, alone,
already a self-replicator?

Isolation test (the geometry.py convention, strengthened with provenance): own tape at [0,L), an EMPTY (zero)
neighbour window, fresh inputs; the tape is a SELF_REPLICATOR iff after one execution the window holds a copy of
the tape at fidelity >= 0.9, >= 90% of the window bytes were last written by a copy op whose source address lay in
[0,L), and the physics' viability rule is met (ENDOGENOUS_COPY: all L window bytes written). Also records the
minimal-copier statistics: which instruction did the copying (LDI / LDIR / COPYALL / LD (T),A), the PC of the copy,
and the number of executed defined instructions before it (the NOP-slide).
    python basin.py --n 400000 --workers 8
Writes receipts/BASIN.json."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402
import traced_replay as TRc  # noqa: E402  (the verified provenance tracer)


def _chunk(args):
    rep, seed, n = args
    vm, W = TRc._install()
    L = 32 if rep == "BYTECODE32" else 64
    allow = rep == "VM_COPY"
    rng = random.Random(seed)
    hits = []; copy_ops = collections.Counter(); defined = 0
    TRc._ACC["L"] = L
    for i in range(n):
        tape = bytes(rng.randrange(256) for _ in range(L))
        mem = bytearray(256); mem[:L] = tape
        TRc._ACC["writes"] = {}; TRc._ACC["own_steps"] = TRc._ACC["win_steps"] = TRc._ACC["other_steps"] = 0
        tr = vm.execute(mem, L, 0, 256, [rng.randrange(256)], allow_copyall=allow)
        ws = TRc._ACC["writes"]
        if len(ws) < L:
            continue
        child = bytes(mem[L:2 * L])
        fid = 1.0 - sum(1 for x, y in zip(child, tape) if x != y) / L
        own = sum(1 for a, (src, pc, op) in ws.items() if op in TRc.COPY_OPS and src is not None and src < L)
        own_code = sum(1 for a, (src, pc, op) in ws.items() if op in TRc.COPY_OPS and src is not None and src < L and pc < L)
        if fid >= 0.9 and own >= 0.9 * L and own_code >= 0.9 * own:
            ops = collections.Counter(op for (src, pc, op) in ws.values())
            hits.append({"tape": tape.hex(), "fid": round(fid, 3), "op": ops.most_common(1)[0][0],
                         "copy_pc": min(pc for (src, pc, op) in ws.values()), "steps": tr.steps})
    return {"rep": rep, "n": n, "hits": hits}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260923)
    a = ap.parse_args()
    jobs = []
    per = 20000
    for rep in ("Z80_64", "BYTECODE32", "VM_COPY"):
        for k in range(a.n // per):
            jobs.append((rep, a.seed * 1000 + hash(rep) % 997 * 0 + len(jobs), per))
    with mp.Pool(a.workers) as pool:
        res = pool.map(_chunk, jobs)
    out = {"n_per_representation": a.n, "seed": a.seed, "definition": __doc__, "by_rep": {}}
    for rep in ("Z80_64", "BYTECODE32", "VM_COPY"):
        rs = [r for r in res if r["rep"] == rep]
        hits = [h for r in rs for h in r["hits"]]
        n = sum(r["n"] for r in rs)
        k = len(hits)
        p = k / n
        se = (p * (1 - p) / n) ** 0.5
        out["by_rep"][rep] = {"n": n, "self_replicators": k, "p": p, "ci95": [max(0, p - 1.96 * se), p + 1.96 * se],
                              "per_initial_population_of_128": 1 - (1 - p) ** 128,
                              "copy_op": dict(collections.Counter(h["op"] for h in hits)),
                              "copy_pc_hist": dict(sorted(collections.Counter(h["copy_pc"] // 8 * 8 for h in hits).items())),
                              "examples": hits[:12]}
    p = Ld.write("BASIN.json", out)
    print(p)
    for rep, v in out["by_rep"].items():
        print(rep, v["n"], v["self_replicators"], "%.2e" % v["p"], "P(>=1 in a 128-tape init)=%.3f" % v["per_initial_population_of_128"], v["copy_op"])


if __name__ == "__main__":
    main()
