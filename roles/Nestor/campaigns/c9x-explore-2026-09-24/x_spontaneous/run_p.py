"""X-SPONTANEOUS (EXPLORE, INITIAL_CONDITION child; parents C-SELFLOC and C-ENERGY).
Declared before running.

Question: with every barrier this campaign has CONFIRMED removed - in-place search, free
self-location, conserved energy inheritance at birth - does evidence-backed heredity arise
SPONTANEOUSLY from a fully random population (no implant) in the FREE non-pair physics?

Cells: every FREE-physics BLOCK cell used by X-NONPAIR-SEARCH or C-SELFLOC, except the
localized structural failures (MINIMAL_CRITERION gate; CONSTRUCTIVE on GRAPH = no free
local slot). One arm (PERMISSIVE), seed 9_900_500 + j, tier M, random start.
Readouts: births, faithful births (fid >= 0.90), replication_events, max causal depth, best
birth fidelity.
Classification: SIGNAL if any run has causal depth >= 2; WEAK_SIGNAL if any faithful
birth or replication event; CLEAN_NULL otherwise (then the remaining barrier is
DISCOVERY of the ALLOC -> copy -> BIRTH chain, and the next child measures its
assembly rate).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
C9 = ROOT.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))


def job(args):
    j, cell = args
    import world

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

    r = Permissive(cell, 9_900_500 + j, tier="M")
    s = r.run()
    fids = [e["fidelity"] for e in r.lineage if e["kind"] == "birth" and e["fidelity"] is not None]
    return {"j": j, "births": s["births_endogenous"], "faithful": sum(f >= 0.9 for f in fids),
            "best_fid": max(fids, default=None), "replication_events": s["replication_events"],
            "max_causal_depth": s["max_causal_replication_depth"], "alloc_calls": s["alloc_calls"]}


def main():
    cells = []
    for f in (ROOT / "x_nonpair_search" / "CELLS.json", ROOT / "c_selfloc_confirm" / "CELLS.json"):
        for c in json.loads(f.read_text()):
            cc = c["cell"]
            if c["physics"] == "OVERWRITE" or cc["copy_primitive"] != "BLOCK":
                continue
            if cc["pressure"] == "MINIMAL_CRITERION" or (cc["reproduction"] == "CONSTRUCTIVE" and cc["world"] == "GRAPH"):
                continue
            cells.append(cc)
    with mp.Pool(6) as pool:
        res = pool.map(job, list(enumerate(cells)))
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    d2 = sum(r["max_causal_depth"] >= 2 for r in res)
    anyrep = sum(1 for r in res if r["faithful"] or r["replication_events"])
    cls = "SIGNAL" if d2 else ("WEAK_SIGNAL" if anyrep else "CLEAN_NULL")
    out = {"classification": cls, "cells": len(cells), "cells_depth_ge2": d2, "cells_any_faithful_or_repl": anyrep,
           "births": sum(r["births"] for r in res), "cells_with_births": sum(1 for r in res if r["births"]),
           "best_fid": max((r["best_fid"] or 0) for r in res),
           "alloc_calls": sum(r["alloc_calls"] for r in res)}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
