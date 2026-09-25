"""C-SELFLOC (CONFIRM). Frozen with PREREG.md; see there. Do not edit after commit.

    python run_c.py [workers]  -> RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parent.parent / "z80atlas-forensics-2026-09-23"
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
USED = HERE.parent / "x_nonpair_search" / "CELLS.json"
sys.path.insert(0, str(C9))
FREE = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE")


def cells():
    sel = json.loads((FOR / "REPLAY_SELECTION.json").read_text())
    runs = {json.loads(l)["run_id"]: json.loads(l) for l in open(FOR / "FROZEN_FUNNEL_RUNS.jsonl")}
    used = {c["source_run"] for c in json.loads(USED.read_text())}
    sys.path.insert(0, str(FOR))
    import forensic
    out = []
    for ph in FREE:
        fresh = [r for r in sel["by_physics"][ph]["run_ids"] if runs[r]["tier"] == "M"
                 and r not in used and runs[r]["copy_primitive"] == "BLOCK"][:12]
        for rid in fresh:
            cfg, _ = forensic.frozen_record(rid)
            out.append({"source_run": rid, "physics": ph, "cell": cfg["job"]["cell"]})
    return out


def job(args):
    k, cell, arm = args
    import world
    import z8
    motif, _ = z8.asm("ALLOC\nLDIR\nBIRTH\nHALT")

    class Search(world.Runner):
        def step(self):
            for o in self.orgs:
                if o.alive:
                    g = self._mutate(self._genome(o))
                    self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                    self.mem[o.slot:o.slot + len(g)] = g
                    o.length = len(g)
            return super().step()

    class SearchLoc(Search):
        def _execute(self, o):
            r = list(o.regs) if o.regs is not None else [0] * 8
            r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF
            r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF
            o.regs = r
            return super()._execute(o)

    R = SearchLoc if arm == "SEED_LOC" else Search
    s = R(cell, 9_800_000 + k, tier="M", implant="ACTUAL_GENOME", implant_bytes=motif).run()
    return {"k": k, "arm": arm, "max_causal_depth": s["max_causal_replication_depth"],
            "replication_events": s["replication_events"], "births": s["births_endogenous"]}


def fisher_one_sided(a, b, c, d):
    """P(X >= a) for the 2x2 [[a, b], [c, d]] with fixed margins (hypergeometric)."""
    n1, n2, k = a + b, c + d, a + c
    tot = math.comb(n1 + n2, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cs = cells()
    (HERE / "CELLS.json").write_text(json.dumps(cs, indent=1))
    todo = [(k, c["cell"], arm) for k, c in enumerate(cs) for arm in ("SEED_LOC", "SEED_ONLY")]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    L = [r for r in res if r["arm"] == "SEED_LOC"]
    O = [r for r in res if r["arm"] == "SEED_ONLY"]
    n = len(cs)
    l3, o3 = sum(r["max_causal_depth"] >= 3 for r in L), sum(r["max_causal_depth"] >= 3 for r in O)
    l1, o1 = sum(r["max_causal_depth"] >= 1 for r in L), sum(r["max_causal_depth"] >= 1 for r in O)
    p = fisher_one_sided(l1, n - l1, o1, n - o1)
    ok = l3 >= 4 and o3 == 0 and p < 0.01
    v = {"verdict": "CONFIRMED" if ok else "NOT_CONFIRMED", "cells": n,
         "SEED_LOC": {"depth_ge1": l1, "depth_ge3": l3, "depth_ge5": sum(r["max_causal_depth"] >= 5 for r in L),
                      "max_depth": max(r["max_causal_depth"] for r in L)},
         "SEED_ONLY": {"depth_ge1": o1, "depth_ge3": o3, "depth_ge5": sum(r["max_causal_depth"] >= 5 for r in O),
                       "max_depth": max(r["max_causal_depth"] for r in O)},
         "fisher_p_depth_ge1": p}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
