"""X-PAIR-NORECOMB (EXPLORE, CAUSAL; child of X-H2-NORECOMB). Declared before running.

The recombination splice both MANUFACTURED the predecessor's pair-tape "replicators" (Z80A-D05:
88% of the 1,031) and DESTROYS genuine copies (X-H2-TERMINATION / X-H2-NORECOMB). Does it also
suppress SPONTANEOUS pair-tape heredity - from random bytes, with no implant?

Cells: the RECOMBINATION-axis cells among the 57 P-11 survivors whose cell is valid under the
Cycle-9 grammar, first 24 by ascending sha256(run_id). Random start, tier M, fresh seeds
9_988_000 + j, shared by both arms. One job per worker process.
Arms: BASE (cell as frozen, splice on) and NO_RECOMB (atlas_axis NONE).
Readouts: p11_events (causal copies arising spontaneously), max_causal_replication_depth.
Classification: SIGNAL if NO_RECOMB reaches depth >= 3 in >= 4 more cells than BASE; CLEAN_NULL
if the depth >= 2 counts differ by <= 1; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parent.parent
C9 = CAMP / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))


def cells():
    import grammar as G
    rows = [json.loads(l) for l in open(CAMP / "z80atlas-forensics-2026-09-23" / "P11_REASSAY.jsonl")]
    cand = [r for r in rows if r.get("n_p11_events") and r["cell"]["atlas_axis"] == "RECOMBINATION"
            and G.is_valid(r["cell"])]
    cand.sort(key=lambda r: hashlib.sha256(r["run_id"].encode()).hexdigest())
    return [{"source_run": r["run_id"], "cell": r["cell"]} for r in cand[:24]]


def job(args):
    j, cell, arm = args
    import world
    c = dict(cell, atlas_axis="NONE") if arm == "NO_RECOMB" else dict(cell)
    s = world.Runner(c, 9_988_000 + j, tier="M").run()
    return {"j": j, "arm": arm, "p11_events": s["p11_events"], "pred_events": s["replication_events"],
            "depth": s["max_causal_replication_depth"]}


def main():
    cs = cells()
    (HERE / "CELLS.json").write_text(json.dumps(cs, indent=1))
    todo = [(j, c["cell"], a) for j, c in enumerate(cs) for a in ("BASE", "NO_RECOMB")]
    with mp.Pool(6, maxtasksperchild=1) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    B = {r["j"]: r for r in res if r["arm"] == "BASE"}
    N = {r["j"]: r for r in res if r["arm"] == "NO_RECOMB"}
    d3 = {a: sum(1 for r in X.values() if r["depth"] >= 3) for a, X in (("BASE", B), ("NO_RECOMB", N))}
    d2 = {a: sum(1 for r in X.values() if r["depth"] >= 2) for a, X in (("BASE", B), ("NO_RECOMB", N))}
    cls = ("SIGNAL" if d3["NO_RECOMB"] - d3["BASE"] >= 4 else
           "CLEAN_NULL" if abs(d2["NO_RECOMB"] - d2["BASE"]) <= 1 else "WEAK_SIGNAL")
    out = {"classification": cls, "cells": len(cs), "depth_ge2": d2, "depth_ge3": d3,
           "p11_events": {a: sum(r["p11_events"] for r in X.values()) for a, X in (("BASE", B), ("NO_RECOMB", N))},
           "pred_events": {a: sum(r["pred_events"] for r in X.values()) for a, X in (("BASE", B), ("NO_RECOMB", N))},
           "max_depth": {a: max(r["depth"] for r in X.values()) for a, X in (("BASE", B), ("NO_RECOMB", N))}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
