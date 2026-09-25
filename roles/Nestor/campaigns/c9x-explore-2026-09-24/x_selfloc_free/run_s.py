"""X-SELFLOC-FREE (EXPLORE, BARRIER child of X-NONPAIR-FIDELITY). Declared before running.

Observation that caused it: with in-place search, FREE-physics organisms reach declared
births, but all 231 births carry none of the parent's bytes (fidelity < 0.06). Copying the
parent requires locating oneself, then a copy primitive, then BIRTH; S1-A found
self-location executed by ~0.05% of organisms.

Question: is SELF-LOCATION the barrier between declared births and faithful copies?
Single coordinate (BARRIER): at the start of every slice HL := own base, BC := own length
are placed in the registers (the organism may overwrite them). Nothing else is provided:
ALLOC, the copy (LDIR, needing DE from ALLOC) and BIRTH must still be found by search.

Cells: every FREE-physics cell (ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL, CONSTRUCTIVE) with
copy_primitive BLOCK among X-NONPAIR-SEARCH's 36 FREE cells. Arms, shared seed 9_710_000+i:
  SEARCH       in-place mutation each epoch (the parent's INPLACE treatment)
  SEARCH_LOC   the same, plus free self-location
Readouts: births, faithful births (fid >= 0.90), replication_events, max causal depth.
Classification: SIGNAL if SEARCH_LOC shows replication_events in >= 3 cells where SEARCH
shows none; WEAK_SIGNAL if any faithful birth appears in SEARCH_LOC only, or the best
birth fidelity rises above 0.5 in >= 3 cells; CLEAN_NULL otherwise.
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
            r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF          # H, L = own base
            r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF      # B, C = own length
            o.regs = r
            return super()._execute(o)

    R = SearchLoc if arm == "SEARCH_LOC" else Search
    r = R(cell, 9_710_000 + i, tier="M")
    s = r.run()
    fids = [e["fidelity"] for e in r.lineage if e["kind"] == "birth" and e["fidelity"] is not None]
    return {"i": i, "arm": arm, "births": s["births_endogenous"],
            "faithful": sum(1 for f in fids if f >= 0.9), "best_fid": max(fids, default=None),
            "replication_events": s["replication_events"],
            "max_causal_depth": s["max_causal_replication_depth"]}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cells = json.loads((PARENT / "CELLS.json").read_text())
    todo = [(i, c["cell"], arm) for i, c in enumerate(cells)
            if c["physics"] in FREE and c["cell"]["copy_primitive"] == "BLOCK"
            for arm in ("SEARCH", "SEARCH_LOC")]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    S = {r["i"]: r for r in res if r["arm"] == "SEARCH"}
    L = {r["i"]: r for r in res if r["arm"] == "SEARCH_LOC"}
    new_rep = sum(1 for i in L if L[i]["replication_events"] and not S[i]["replication_events"])
    new_faith = sum(1 for i in L if L[i]["faithful"] and not S[i]["faithful"])
    fid_up = sum(1 for i in L if (L[i]["best_fid"] or 0) > 0.5 and (S[i]["best_fid"] or 0) <= 0.5)
    cls = "SIGNAL" if new_rep >= 3 else ("WEAK_SIGNAL" if new_faith or fid_up >= 3 else "CLEAN_NULL")
    out = {"classification": cls, "cells": len(L), "cells_new_replication": new_rep,
           "cells_new_faithful": new_faith, "cells_best_fid_above_half": fid_up,
           "births": {a: sum(r["births"] for r in res if r["arm"] == a) for a in ("SEARCH", "SEARCH_LOC")},
           "cells_with_births": {a: sum(1 for r in res if r["arm"] == a and r["births"]) for a in ("SEARCH", "SEARCH_LOC")},
           "max_causal_depth": {a: max(r["max_causal_depth"] for r in res if r["arm"] == a) for a in ("SEARCH", "SEARCH_LOC")},
           "best_fid": {a: max((r["best_fid"] or 0) for r in res if r["arm"] == a) for a in ("SEARCH", "SEARCH_LOC")}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
