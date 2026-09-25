"""X-NEARMISS (EXPLORE, MEASUREMENT; child of X-SPONTANEOUS, CLEAN_NULL). Declared before running.

Observation: in the permissive random-start worlds no birth reached fidelity 0.90, but the
best reached 0.688 (the unrelieved search arm never exceeded 0.24). Mining the negative
examples nearest success: what were those parents executing?

Re-run (same seed, same subclass - deterministic) every X-SPONTANEOUS cell whose best birth
fidelity exceeded 0.40, and for each birth with fidelity > 0.40 record the parent genome's
disassembly, which world ops it contains (ALLOC / LDIR / LDDR / BIRTH / SPLIT) and in what
order, the child length, and the parent-placed share (bytes differing from the slot's
pre-image, measured directly this time rather than through the ambiguous `span`).
Readout (descriptive): the motif classes of near-miss parents and where the copy fell short.
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
sys.path.insert(0, str(ROOT / "x_spontaneous"))


def job(args):
    j, cell = args
    import world
    import z8
    import run_p
    base = run_p.job.__code__  # noqa: F841 (documentation: same subclass logic below)
    rec = []

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
            p = self.pending.get(o.oid)
            pre = bytes(p[2]) if p else b""
            slot = p[0] if p else None
            parent = self._genome(o)
            n0 = len(self.orgs)
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if ok and len(self.orgs) > n0:
                child = self.orgs[-1]
                half = o.energy * 0.5
                o.energy -= half
                child.energy += half
                e = self.lineage[-1]
                if e["fidelity"] is not None and e["fidelity"] > 0.40:
                    cg = self._genome(child)
                    placed = sum(1 for k in range(min(len(cg), len(pre))) if cg[k] != pre[k]) / max(1, len(cg))
                    ops = [t for _a, t in z8.dis(parent) if t in ("ALLOC", "LDIR", "LDDR", "BIRTH", "SPLIT", "SELF", "GETPC")]
                    rec.append({"epoch": self.epoch, "fid": e["fidelity"], "partial": partial,
                                "child_len": len(cg), "parent_len": len(parent),
                                "placed_share": round(placed, 3), "world_ops_in_order": ops,
                                "parent_hex": parent.hex()})
            return ok

    Permissive(cell, 9_900_500 + j, tier="M").run()
    return j, rec


def main():
    res = json.loads((ROOT / "x_spontaneous" / "RESULTS.json").read_text())
    cells = []
    for f in (ROOT / "x_nonpair_search" / "CELLS.json", ROOT / "c_selfloc_confirm" / "CELLS.json"):
        for c in json.loads(f.read_text()):
            cc = c["cell"]
            if c["physics"] == "OVERWRITE" or cc["copy_primitive"] != "BLOCK":
                continue
            if cc["pressure"] == "MINIMAL_CRITERION" or (cc["reproduction"] == "CONSTRUCTIVE" and cc["world"] == "GRAPH"):
                continue
            cells.append(cc)
    todo = [(r["j"], cells[r["j"]]) for r in res if (r["best_fid"] or 0) > 0.40]
    with mp.Pool(6) as pool:
        out = pool.map(job, todo)
    allrec = [dict(r, j=j, reproduction=cells[j]["reproduction"]) for j, recs in out for r in recs]
    (HERE / "NEARMISS.json").write_text(json.dumps(allrec, indent=1))
    from collections import Counter
    motif = Counter(" ".join(r["world_ops_in_order"]) for r in allrec)
    print("near-miss births:", len(allrec), "cells:", len(todo))
    print("partial (SPLIT) share:", sum(r["partial"] for r in allrec), "of", len(allrec))
    print("placed_share median:", sorted(r["placed_share"] for r in allrec)[len(allrec) // 2] if allrec else None)
    for m, n in motif.most_common(10):
        print("%4d  %s" % (n, m))


if __name__ == "__main__":
    main()
