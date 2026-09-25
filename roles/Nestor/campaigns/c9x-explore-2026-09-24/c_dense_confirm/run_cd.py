"""C-DENSE (CONFIRM lane, fresh and frozen). Parent: X-DENSE-OPS-R (EXPLORE SIGNAL: with
search + free self-location + energy inheritance, adding 1-byte encodings of ALLOC/LDIR/
BIRTH gave evidence-backed spontaneous replication in 23/47 random-start cells (depth >= 2
in 5, max 6) against 0/47 with only the 2-byte encodings).

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, arms, endpoint, rule, allocation.

Claim under test: in the permissive FREE non-pair world, the discovery barrier to
spontaneous heredity is the encoding length of the world-op chain: 1-byte encodings yield
evidence-backed replication from random bytes, 2-byte encodings do not.

Fresh sample: tier-M FREE-physics BLOCK cells from the 1,255 predecessor random starts,
EXCLUDING every cell used by X-NONPAIR-SEARCH, C-SELFLOC, C-ENERGY, and the localized
structural failures (MINIMAL_CRITERION; CONSTRUCTIVE on GRAPH); the first 40 in ascending
sha256(run_id). Seeds 9_950_000 + k (never used). One job per worker process.
Arms (shared seed): PERMISSIVE (2-byte ops) and PERMISSIVE_DENSE (+ 1-byte encodings).
Primary endpoint: >= 1 evidence-backed replication event (replication_events > 0).
Rule: CONFIRMED iff DENSE has replication in >= 10 of 40 cells, PERMISSIVE in <= 1, and the
one-sided Fisher exact test gives p < 0.001. Secondary: cells with causal depth >= 2.

    python run_cd.py -> CELLS.json, RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CAMP = ROOT.parent
C9 = CAMP / "z80atlas-verify-2026-09-22"
FOR = CAMP / "z80atlas-forensics-2026-09-23"
sys.path.insert(0, str(C9))
sys.path.insert(0, str(ROOT / "x_dense_ops"))


def cells():
    runs = [json.loads(l) for l in open(FOR / "FROZEN_FUNNEL_RUNS.jsonl")]
    used = set()
    for f in (ROOT / "x_nonpair_search" / "CELLS.json", ROOT / "c_selfloc_confirm" / "CELLS.json",
              ROOT / "c_energy_confirm" / "CELLS.json"):
        used |= {c["source_run"] for c in json.loads(f.read_text())}
    sys.path.insert(0, str(FOR))
    import forensic
    cand = []
    for r in runs:
        if r["physics"] == "OVERWRITE" or r["tier"] != "M" or r["copy_primitive"] != "BLOCK" \
                or r["run_id"] in used:
            continue
        cc = forensic.frozen_record(r["run_id"])[0]["job"]["cell"]
        if cc["pressure"] == "MINIMAL_CRITERION" or (cc["reproduction"] == "CONSTRUCTIVE" and cc["world"] == "GRAPH"):
            continue
        cand.append({"source_run": r["run_id"], "physics": r["physics"], "cell": cc})
    cand.sort(key=lambda c: hashlib.sha256(c["source_run"].encode()).hexdigest())
    return cand[:40]


def job(args):
    k, cell, arm = args
    import world
    import z8 as z8_plain
    import run_d
    world.z8 = run_d.dense_z8() if arm == "PERMISSIVE_DENSE" else z8_plain

    class Permissive(world.Runner):
        def step(self):
            for o in self.orgs:
                if o.alive:
                    g = self._mutate(self._genome(o))
                    self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                    self.mem[o.slot:o.slot + len(g)] = g
                    o.length = len(g)
            return super().step()

        def _execute(self, o):
            r = list(o.regs) if o.regs is not None else [0] * 8
            r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF
            r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF
            o.regs = r
            return super()._execute(o)

        def _on_birth(self, o, ctx, dst, cnt, partial):
            n0 = len(self.orgs)
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if ok and len(self.orgs) > n0:
                child = self.orgs[-1]
                half = o.energy * 0.5
                o.energy -= half
                child.energy += half
            return ok

    s = Permissive(cell, 9_950_000 + k, tier="M").run()
    return {"k": k, "arm": arm, "replication_events": s["replication_events"],
            "max_causal_depth": s["max_causal_replication_depth"], "births": s["births_endogenous"]}


def main():
    import run_d
    ok, detail = run_d.selftest()
    if not ok:
        print("dense VM selftest FAILED", detail)
        return 1
    cs = cells()
    (HERE / "CELLS.json").write_text(json.dumps(cs, indent=1))
    todo = [(k, c["cell"], arm) for k, c in enumerate(cs) for arm in ("PERMISSIVE", "PERMISSIVE_DENSE")]
    with mp.Pool(6, maxtasksperchild=1) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    P = [r for r in res if r["arm"] == "PERMISSIVE"]
    D = [r for r in res if r["arm"] == "PERMISSIVE_DENSE"]
    n = len(cs)
    d1, p1 = sum(r["replication_events"] > 0 for r in D), sum(r["replication_events"] > 0 for r in P)
    k0 = d1 + p1
    p = sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(d1, min(n, k0) + 1)) / math.comb(2 * n, k0) if k0 else 1.0
    v = {"verdict": "CONFIRMED" if (d1 >= 10 and p1 <= 1 and p < 0.001) else "NOT_CONFIRMED",
         "cells": n, "DENSE_cells_replication": d1, "PERMISSIVE_cells_replication": p1,
         "fisher_p": p, "DENSE_depth_ge2": sum(r["max_causal_depth"] >= 2 for r in D),
         "PERMISSIVE_depth_ge2": sum(r["max_causal_depth"] >= 2 for r in P),
         "DENSE_max_depth": max(r["max_causal_depth"] for r in D)}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
