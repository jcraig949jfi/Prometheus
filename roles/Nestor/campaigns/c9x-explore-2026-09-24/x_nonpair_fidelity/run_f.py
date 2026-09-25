"""X-NONPAIR-FIDELITY (EXPLORE, MEASUREMENT child of X-NONPAIR-SEARCH).

Question (declared before running): the in-place-mutation arm unlocked births in the FREE
physics but none reached fidelity >= 0.90. Is the gap NO COPYING (the parent placed few of
the child's bytes; fidelity near the chance level) or IMPERFECT COPYING (the parent wrote
most of the child, fidelity high but below 0.90)?

Method: re-run, deterministically (same cell, same seed 9_700_000 + i, same subclass), every
INPLACE run in which X-NONPAIR-SEARCH recorded a birth, and read each birth edge from the
in-memory lineage: fidelity of child to parent, and the parent-placed share (`span` /
child length). Re-running must reproduce the parent's births count exactly (checked).

Readout: per physics, the distribution of fidelity and placed share across births;
counts of births with placed share >= 0.5 (copying happened) and fidelity bands.
Classification: IMPERFECT_COPYING if >= 25% of births have placed share >= 0.5 and median
fidelity among those >= 0.5; NO_COPYING if < 10% have placed share >= 0.5; else MIXED.

    python run_f.py [workers]
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
PARENT = HERE.parent / "x_nonpair_search"
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))


def job(args):
    i, cell, expect_births = args
    import world

    class InPlace(world.Runner):
        def step(self):
            for o in self.orgs:
                if o.alive:
                    g = self._mutate(self._genome(o))
                    self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                    self.mem[o.slot:o.slot + len(g)] = g
                    o.length = len(g)
            return super().step()

    r = InPlace(cell, 9_700_000 + i, tier="M")
    s = r.run()
    births = [{"fid": e["fidelity"], "span": e["span"], "epoch": e["epoch"]}
              for e in r.lineage if e["kind"] == "birth"]
    return {"i": i, "births_endogenous": s["births_endogenous"], "expected": expect_births,
            "reproduced": s["births_endogenous"] == expect_births, "births": births,
            "L": r.L}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cells = json.loads((PARENT / "CELLS.json").read_text())
    todo = []
    for p in sorted((PARENT / "results").glob("*_INPLACE.json")):
        rec = json.loads(p.read_text())
        if rec["births_endogenous"] and rec["physics"] != "OVERWRITE":
            todo.append((rec["i"], cells[rec["i"]]["cell"], rec["births_endogenous"]))
    ow = [json.loads(p.read_text()) for p in sorted((PARENT / "results").glob("*_INPLACE.json"))]
    todo += [(r["i"], cells[r["i"]]["cell"], r["births_endogenous"]) for r in ow
             if r["births_endogenous"] and r["physics"] == "OVERWRITE"]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    by = {}
    for r in res:
        ph = cells[r["i"]]["physics"]
        d = by.setdefault(ph, {"runs": 0, "reproduced": 0, "births": []})
        d["runs"] += 1
        d["reproduced"] += r["reproduced"]
        for b in r["births"]:
            share = (b["span"] or 0) / r["L"]
            d["births"].append((b["fid"], min(share, 1.0)))
    out = {}
    for ph, d in by.items():
        B = d["births"]
        placed = [f for f, s in B if s >= 0.5]
        frac = len(placed) / len(B) if B else 0.0
        med = statistics.median(placed) if placed else None
        cls = ("IMPERFECT_COPYING" if frac >= 0.25 and (med or 0) >= 0.5 else
               "NO_COPYING" if frac < 0.10 else "MIXED")
        out[ph] = {"runs": d["runs"], "reproduced": d["reproduced"], "births": len(B),
                   "share_placed_ge_half": round(frac, 3),
                   "median_fid_placed": med, "max_fid": max((f for f, _ in B), default=None),
                   "fid_bands": {"<0.25": sum(f < 0.25 for f, _ in B),
                                 "0.25-0.5": sum(0.25 <= f < 0.5 for f, _ in B),
                                 "0.5-0.75": sum(0.5 <= f < 0.75 for f, _ in B),
                                 "0.75-0.9": sum(0.75 <= f < 0.9 for f, _ in B),
                                 ">=0.9": sum(f >= 0.9 for f, _ in B)},
                   "classification": cls}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
