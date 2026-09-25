"""X-ENERGY-INHERIT (EXPLORE, ECOLOGY child of X-ERROR-THRESHOLD). Declared before running.

Observation that caused it: the seeded copier's failure is a per-CELL property, stable
across in-place doses (NO_DOSE_EFFECT). Seven cells sit at causal depth exactly 1 at every
dose: the copier replicates once, its children never do. All seven run an energy-economy
pressure (COMPETITION, RESOURCE_GATED, METABOLIC), under which a slice is capped at the
organism's energy - and an endogenous newborn starts with energy 0 (world._on_birth never
sets it), so it cannot afford the ~70 instructions its own copy needs.

Single coordinate (ECOLOGY): at every accepted endogenous birth the parent transfers half
its energy to the child (energy is conserved; nothing is created). Everything else as the
SEED_LOC arm (implant + free self-location + in-place search at the cell's rate).

Cells: every energy-pressure cell (COMPETITION, RESOURCE_GATED, METABOLIC) among the FREE
BLOCK cells of X-NONPAIR-SEARCH and C-SELFLOC (EXPLORE may reuse cells). Arms, shared seed
9_740_000 + j: BASE (as SEED_LOC) and INHERIT.
Readouts: max_causal_replication_depth (depth >= 2 is the key: a child replicated).
Classification: SIGNAL if INHERIT reaches depth >= 2 in >= 3 more cells than BASE;
CLEAN_NULL if the difference is <= 1; WEAK_SIGNAL otherwise.
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
ENERGY = ("COMPETITION", "RESOURCE_GATED", "METABOLIC")


def job(args):
    j, cell, arm = args
    import world
    import z8
    motif, _ = z8.asm("ALLOC\nLDIR\nBIRTH\nHALT")

    class Base(world.Runner):
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

    class Inherit(Base):
        def _on_birth(self, o, ctx, dst, cnt, partial):
            n0 = len(self.orgs)
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if ok and len(self.orgs) > n0:
                child = self.orgs[-1]
                half = o.energy * 0.5
                o.energy -= half
                child.energy += half
            return ok

    R = Inherit if arm == "INHERIT" else Base
    s = R(cell, 9_740_000 + j, tier="M", implant="ACTUAL_GENOME", implant_bytes=motif).run()
    return {"j": j, "arm": arm, "pressure": cell["pressure"],
            "max_causal_depth": s["max_causal_replication_depth"],
            "replication_events": s["replication_events"]}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    pool_cells = []
    for f in (ROOT / "x_nonpair_search" / "CELLS.json", ROOT / "c_selfloc_confirm" / "CELLS.json"):
        for c in json.loads(f.read_text()):
            cc = c["cell"]
            if c["physics"] in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE") \
                    and cc["copy_primitive"] == "BLOCK" and cc["pressure"] in ENERGY:
                pool_cells.append(cc)
    todo = [(j, c, arm) for j, c in enumerate(pool_cells) for arm in ("BASE", "INHERIT")]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    B = [r for r in res if r["arm"] == "BASE"]
    I = [r for r in res if r["arm"] == "INHERIT"]
    b2, i2 = sum(r["max_causal_depth"] >= 2 for r in B), sum(r["max_causal_depth"] >= 2 for r in I)
    d = i2 - b2
    cls = "SIGNAL" if d >= 3 else ("CLEAN_NULL" if d <= 1 else "WEAK_SIGNAL")
    out = {"classification": cls, "cells": len(pool_cells),
           "BASE": {"depth_ge2": b2, "depth_ge5": sum(r["max_causal_depth"] >= 5 for r in B),
                    "max_depth": max(r["max_causal_depth"] for r in B)},
           "INHERIT": {"depth_ge2": i2, "depth_ge5": sum(r["max_causal_depth"] >= 5 for r in I),
                       "max_depth": max(r["max_causal_depth"] for r in I)}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
