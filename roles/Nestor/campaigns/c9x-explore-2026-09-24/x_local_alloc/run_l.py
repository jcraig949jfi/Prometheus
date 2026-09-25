"""X-LOCAL-ALLOC (EXPLORE, MEASUREMENT localization; child of X-ERROR-THRESHOLD).
Declared before running.

Observation: 6 cells never replicate the seeded copier at any in-place dose (depth 0 at
m = 0..2): one MINIMAL_CRITERION cell (ALLOC is gated on competence >= 0.35 there, and a
random population has none), five GRID/GRAPH cells. Where does the copier's chain stop?

Re-run those 6 cells exactly as X-ERROR-THRESHOLD's m = 1 arm (same seed 9_730_000 + i), with
the copier organism instrumented: ALLOC attempts, ALLOC failures and the reason (competence
gate / no free local slot / other), accepted births, and whether the copier was still
alive at the end. Classification per cell: GATE (competence gate refused), LOCAL_FULL (no
free neighbour slot), DIED (copier died before replicating), OTHER.
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
ALWAYS_ZERO = (16, 17, 24, 28, 31, 33)


def job(i):
    import world
    import z8
    motif, _ = z8.asm("ALLOC\nLDIR\nBIRTH\nHALT")
    cell = json.loads((ROOT / "x_nonpair_search" / "CELLS.json").read_text())[i]["cell"]
    tel = {"alloc_attempts": 0, "gate_refused": 0, "local_full": 0, "alloc_ok": 0,
           "births": 0, "died_epoch": None, "death_cause": None}

    class R(world.Runner):
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

        def _on_alloc(self, o, ctx, want):
            if o.anc != 0:
                return super()._on_alloc(o, ctx, want)
            tel["alloc_attempts"] += 1
            gated = (self.cell["pressure"] == "MINIMAL_CRITERION" and self.d["has_task"] and o.comp < 0.35)
            local = self._alloc_allowed_slots(o)
            full = local is not None and not any(s in self.free_slots for s in local)
            got = super()._on_alloc(o, ctx, want)
            if got is None:
                if gated:
                    tel["gate_refused"] += 1
                elif full:
                    tel["local_full"] += 1
            else:
                tel["alloc_ok"] += 1
            return got

        def _on_birth(self, o, ctx, dst, cnt, partial):
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if ok and o.anc == 0:
                tel["births"] += 1
            return ok

        def _kill(self, o, why="reaped"):
            if o.alive and o.anc == 0 and o.oid == 0 and tel["died_epoch"] is None:
                tel["died_epoch"], tel["death_cause"] = self.epoch, why
            return super()._kill(o, why)

    s = R(cell, 9_730_000 + i, tier="M", implant="ACTUAL_GENOME", implant_bytes=motif).run()
    if tel["gate_refused"] and not tel["alloc_ok"]:
        cls = "GATE"
    elif tel["local_full"] and not tel["alloc_ok"]:
        cls = "LOCAL_FULL"
    elif tel["died_epoch"] is not None and tel["died_epoch"] < 5 and not tel["births"]:
        cls = "DIED"
    else:
        cls = "OTHER"
    return {"i": i, "world": cell["world"], "pressure": cell["pressure"],
            "reproduction": cell["reproduction"], "classification": cls, **tel,
            "max_causal_depth": s["max_causal_replication_depth"]}


def main():
    with mp.Pool(6) as pool:
        res = pool.map(job, ALWAYS_ZERO)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    for r in res:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
