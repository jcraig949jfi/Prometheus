"""X-NONPAIR-SEARCH runner (EXPLORE). See PREREG.md. Imports the frozen Cycle-9 substrate
read-only; the only treatment is per-epoch in-place mutation (subclass).

    python run_x.py [workers]   -> results/<cell_index>_<arm>.json, then SUMMARY.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
FOR = HERE.parent.parent / "z80atlas-forensics-2026-09-23"
sys.path.insert(0, str(C9))
OUT = HERE / "results"
PHYSICS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE", "OVERWRITE")
KEYS = ("births_endogenous", "replication_events", "births_similar_no_write",
        "max_causal_replication_depth", "alloc_calls", "pop_final", "extinct", "uniq_final")


def cells():
    sel = json.loads((FOR / "REPLAY_SELECTION.json").read_text())
    runs = {json.loads(l)["run_id"]: json.loads(l) for l in open(FOR / "FROZEN_FUNNEL_RUNS.jsonl")}
    sys.path.insert(0, str(FOR))
    import forensic
    out = []
    for phys in PHYSICS:
        picked = [r for r in sel["by_physics"][phys]["run_ids"] if runs[r]["tier"] == "M"][:12]
        for rid in picked:
            cfg, _ = forensic.frozen_record(rid)
            out.append({"source_run": rid, "physics": phys, "cell": cfg["job"]["cell"]})
    return out


def job(args):
    i, c, arm = args
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

    cls = InPlace if arm == "INPLACE" else world.Runner
    r = cls(c["cell"], 9_700_000 + i, tier="M")
    s = r.run()
    rec = {"i": i, "arm": arm, "source_run": c["source_run"], "physics": c["physics"],
           **{k: s.get(k) for k in KEYS}}
    (OUT / ("%03d_%s.json" % (i, arm))).write_text(json.dumps(rec))
    return i, arm


def summarize():
    rows = [json.loads(p.read_text()) for p in sorted(OUT.glob("*.json"))]
    by = {}
    for ph in PHYSICS:
        d = {}
        for arm in ("CONTROL", "INPLACE"):
            R = [r for r in rows if r["physics"] == ph and r["arm"] == arm]
            d[arm] = {"runs": len(R),
                      "cells_with_births": sum(1 for r in R if r["births_endogenous"]),
                      "births": sum(r["births_endogenous"] for r in R),
                      "cells_with_faithful_births": sum(1 for r in R if r["replication_events"] + r["births_similar_no_write"]),
                      "cells_with_replication": sum(1 for r in R if r["replication_events"]),
                      "replication_events": sum(r["replication_events"] for r in R),
                      "max_causal_depth": max((r["max_causal_replication_depth"] or 0 for r in R), default=0)}
        by[ph] = d
    ctrl = {r["i"]: r for r in rows if r["arm"] == "CONTROL"}
    inp = {r["i"]: r for r in rows if r["arm"] == "INPLACE"}
    new_rep = sum(1 for i in inp if inp[i]["replication_events"] and not (ctrl.get(i) or {}).get("replication_events"))
    birth_gain = (sum(1 for r in inp.values() if r["births_endogenous"])
                  - sum(1 for r in ctrl.values() if r["births_endogenous"]))
    new_faithful = sum(1 for i in inp if (inp[i]["replication_events"] + inp[i]["births_similar_no_write"])
                       and not ((ctrl.get(i) or {}).get("replication_events", 0) + (ctrl.get(i) or {}).get("births_similar_no_write", 0)))
    cls = ("SIGNAL" if new_rep >= 3 else
           "WEAK_SIGNAL" if birth_gain >= 5 or new_faithful > 0 else "CLEAN_NULL")
    out = {"classification": cls, "cells_new_replication": new_rep, "birth_cell_gain": birth_gain,
           "cells_new_faithful_birth": new_faithful, "by_physics": by, "n_rows": len(rows)}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    OUT.mkdir(exist_ok=True)
    cs = cells()
    (HERE / "CELLS.json").write_text(json.dumps(cs, indent=1))
    todo = [(i, c, arm) for i, c in enumerate(cs) for arm in ("CONTROL", "INPLACE")
            if not (OUT / ("%03d_%s.json" % (i, arm))).exists()]
    print("todo", len(todo), flush=True)
    with mp.Pool(workers) as pool:
        for n, (i, arm) in enumerate(pool.imap_unordered(job, todo), 1):
            print("%d/%d %d %s" % (n, len(todo), i, arm), flush=True)
    summarize()


if __name__ == "__main__":
    main()
