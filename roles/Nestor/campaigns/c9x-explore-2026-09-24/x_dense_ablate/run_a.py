"""X-DENSE-ABLATE (EXPLORE, CAUSAL; child of X-DENSE-OPS-R). Declared before running.

With 1-byte world-op encodings, spontaneous evidence-backed replication appeared in the
permissive world (search + free self-location + energy inheritance). Which of the three
relieved barriers are still NECESSARY once the encoding is short? Each arm removes exactly
one (single-coordinate ablations), on the 47 X-DENSE-OPS cells, shared seed 9_960_000 + j:

  FULL        dense + search + self-location + inheritance   (reference)
  NO_LOC      dense + search + inheritance                   (self-location removed)
  NO_ENERGY   dense + search + self-location                 (inheritance removed)
  NO_SEARCH   dense + self-location + inheritance            (in-place mutation removed)

Readouts: cells with >= 1 evidence-backed replication event; cells with depth >= 2.
Classification per ablation, against FULL: NECESSARY if its replication-cell count falls to
<= 25% of FULL's; CONTRIBUTES if it falls to 25-75%; NOT_NECESSARY if >= 75%.
One job per worker process (the VM swap cannot leak).
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
sys.path.insert(0, str(ROOT / "x_dense_ops"))
ARMS = ("FULL", "NO_LOC", "NO_ENERGY", "NO_SEARCH")


def job(args):
    j, cell, arm = args
    import world
    import run_d
    world.z8 = run_d.dense_z8()
    search, loc, energy = arm != "NO_SEARCH", arm != "NO_LOC", arm != "NO_ENERGY"

    class W(world.Runner):
        def step(self):
            if search:
                for o in self.orgs:
                    if o.alive:
                        g = self._mutate(self._genome(o))
                        self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                        self.mem[o.slot:o.slot + len(g)] = g
                        o.length = len(g)
            return super().step()

        def _execute(self, o):
            if loc:
                r = list(o.regs) if o.regs is not None else [0] * 8
                r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF
                r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF
                o.regs = r
            return super()._execute(o)

        def _on_birth(self, o, ctx, dst, cnt, partial):
            n0 = len(self.orgs)
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if energy and ok and len(self.orgs) > n0:
                child = self.orgs[-1]
                half = o.energy * 0.5
                o.energy -= half
                child.energy += half
            return ok

    s = W(cell, 9_960_000 + j, tier="M").run()
    return {"j": j, "arm": arm, "replication_events": s["replication_events"],
            "max_causal_depth": s["max_causal_replication_depth"]}


def main():
    import run_d
    cells = run_d.cells()
    todo = [(j, c, arm) for j, c in enumerate(cells) for arm in ARMS]
    with mp.Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 6, maxtasksperchild=1) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    rep = {a: sum(1 for r in res if r["arm"] == a and r["replication_events"]) for a in ARMS}
    d2 = {a: sum(1 for r in res if r["arm"] == a and r["max_causal_depth"] >= 2) for a in ARMS}
    full = rep["FULL"] or 1
    cls = {a: ("NECESSARY" if rep[a] <= 0.25 * full else "CONTRIBUTES" if rep[a] < 0.75 * full else "NOT_NECESSARY")
           for a in ARMS if a != "FULL"}
    out = {"cells": len(cells), "cells_with_replication": rep, "cells_depth_ge2": d2, "classification": cls}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
