"""X-ERROR-THRESHOLD (EXPLORE, DOSE child of X-SELFLOC-SEEDED). Declared before running.

Observation that caused it: the seeded copier failed in 8 of 23 cells, 6 of them at the
HIGH mutation rate and 6 with STRUCTURAL (indel) mutation. Search needs in-place mutation;
a 6-byte copier is destroyed by it. Is there an error threshold for MAINTENANCE?

Single coordinate (DOSE): the in-place per-epoch mutation rate is the cell's own rate x m,
m in {0, 0.25, 0.5, 1, 2}. Birth mutation is unchanged (the cell's rate). Everything else
as X-SELFLOC-SEEDED's SEED_LOC arm (implant + free self-location), 23 cells, shared seed
9_730_000 + i per cell across doses.

Readouts per run: max_causal_replication_depth; replication_events.
Classification:
  THRESHOLD   the share of cells reaching depth >= 3 falls monotonically (non-increasing)
              from the best dose to m = 2 AND is at least 0.25 higher at the best dose
              than at m = 2
  NO_DOSE_EFFECT  the depth >= 3 share varies by < 0.10 across doses
  OTHER       otherwise (reported with the curve)
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
DOSES = (0.0, 0.25, 0.5, 1.0, 2.0)


def job(args):
    i, cell, m = args
    import world
    import z8
    motif, _ = z8.asm("ALLOC\nLDIR\nBIRTH\nHALT")

    class Dosed(world.Runner):
        def step(self):
            if m > 0:
                base = self.mut_rate
                self.mut_rate = base * m
                try:
                    for o in self.orgs:
                        if o.alive:
                            g = self._mutate(self._genome(o))
                            self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                            self.mem[o.slot:o.slot + len(g)] = g
                            o.length = len(g)
                finally:
                    self.mut_rate = base
            return super().step()

        def _execute(self, o):
            r = list(o.regs) if o.regs is not None else [0] * 8
            r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF
            r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF
            o.regs = r
            return super()._execute(o)

    s = Dosed(cell, 9_730_000 + i, tier="M", implant="ACTUAL_GENOME", implant_bytes=motif).run()
    return {"i": i, "m": m, "max_causal_depth": s["max_causal_replication_depth"],
            "replication_events": s["replication_events"]}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cells = json.loads((PARENT / "CELLS.json").read_text())
    idx = [i for i, c in enumerate(cells) if c["physics"] in FREE and c["cell"]["copy_primitive"] == "BLOCK"]
    todo = [(i, cells[i]["cell"], m) for i in idx for m in DOSES]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    n = len(idx)
    curve = {str(m): {"depth_ge3_share": round(sum(r["max_causal_depth"] >= 3 for r in res if r["m"] == m) / n, 3),
                      "depth_ge1_share": round(sum(r["max_causal_depth"] >= 1 for r in res if r["m"] == m) / n, 3),
                      "max_depth": max(r["max_causal_depth"] for r in res if r["m"] == m)} for m in DOSES}
    s3 = [curve[str(m)]["depth_ge3_share"] for m in DOSES]
    best = max(range(len(DOSES)), key=lambda k: s3[k])
    mono = all(s3[k] >= s3[k + 1] for k in range(best, len(DOSES) - 1))
    cls = ("THRESHOLD" if mono and s3[best] - s3[-1] >= 0.25 else
           "NO_DOSE_EFFECT" if max(s3) - min(s3) < 0.10 else "OTHER")
    out = {"classification": cls, "cells": n, "curve": curve, "best_dose": DOSES[best]}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
