"""X-SELFLOC-SEEDED (EXPLORE, INITIAL_CONDITION child of X-SELFLOC-FREE). Declared before running.

Observation that caused it: free self-location doubled births but produced no faithful
copy (CLEAN_NULL). Charter: localize the failure. With HL/BC provided, the six-byte chain
ALLOC ; LDIR ; BIRTH (ED30 EDB0 ED31) is a complete replicator in FREE physics, so either
(a) the physics does NOT support it (something blocks the copy or its propagation), or
(b) it does, and search simply never assembles the chain.

Design: the 23 cells of X-SELFLOC-FREE; ONE organism implanted with
  ALLOC ; LDIR ; BIRTH ; HALT   (padded with random bytes by the world)
into the otherwise random population. Arms, shared seed 9_720_000 + i:
  SEED_LOC   in-place search + free self-location (HL/BC) + the implant
  SEED_ONLY  in-place search + the implant, NO free self-location (negative control:
             without HL/BC the chain copies from address 0, not from itself)
Readouts: replication_events, max_causal_replication_depth, faithful births.
Classification (localization, not discovery):
  PHYSICS_SUPPORTS  SEED_LOC reaches causal depth >= 3 in >= 5 cells and SEED_ONLY in <= 1
                    -> the barrier is discovery by search (combinatorial), not the physics
  PHYSICS_BLOCKS    SEED_LOC reaches depth >= 1 in <= 2 cells
                    -> something in the physics stops the implanted copier
  MIXED             otherwise
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PARENT = HERE.parent / "x_nonpair_search"
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
FREE = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE")


def job(args):
    i, cell, arm = args
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
    r = R(cell, 9_720_000 + i, tier="M", implant="ACTUAL_GENOME", implant_bytes=motif)
    s = r.run()
    fids = [e["fidelity"] for e in r.lineage if e["kind"] == "birth" and e["fidelity"] is not None]
    return {"i": i, "arm": arm, "births": s["births_endogenous"],
            "faithful": sum(1 for f in fids if f >= 0.9),
            "replication_events": s["replication_events"],
            "max_causal_depth": s["max_causal_replication_depth"],
            "pop_final": s["pop_final"]}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cells = json.loads((PARENT / "CELLS.json").read_text())
    todo = [(i, c["cell"], arm) for i, c in enumerate(cells)
            if c["physics"] in FREE and c["cell"]["copy_primitive"] == "BLOCK"
            for arm in ("SEED_LOC", "SEED_ONLY")]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    L = [r for r in res if r["arm"] == "SEED_LOC"]
    O = [r for r in res if r["arm"] == "SEED_ONLY"]
    l3 = sum(1 for r in L if r["max_causal_depth"] >= 3)
    o3 = sum(1 for r in O if r["max_causal_depth"] >= 3)
    l1 = sum(1 for r in L if r["max_causal_depth"] >= 1)
    cls = ("PHYSICS_SUPPORTS" if l3 >= 5 and o3 <= 1 else
           "PHYSICS_BLOCKS" if l1 <= 2 else "MIXED")
    out = {"classification": cls, "cells": len(L),
           "SEED_LOC": {"depth_ge1": l1, "depth_ge3": l3,
                        "max_depth": max(r["max_causal_depth"] for r in L),
                        "replication_events": sum(r["replication_events"] for r in L),
                        "faithful": sum(r["faithful"] for r in L)},
           "SEED_ONLY": {"depth_ge1": sum(1 for r in O if r["max_causal_depth"] >= 1), "depth_ge3": o3,
                         "max_depth": max(r["max_causal_depth"] for r in O),
                         "replication_events": sum(r["replication_events"] for r in O),
                         "faithful": sum(r["faithful"] for r in O)}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
