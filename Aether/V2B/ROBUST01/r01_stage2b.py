"""ROBUST01 stage 2b: pick the GENUINE reuse component from stage 1 by a frozen rule, then write its plans.

    python r01_stage2b.py --s1 REDUCTION_S1.json --fold-dir S1_SEARCH_DIR --outdir S2B_DIR [--backend gpu]

Candidates: stage 1 arm-C certified candidates that are AUTONOMOUS and have zero energy-field contest events; the
COMPOSE ones first, then the COMBINE-only ones; within each group by (seed, found_at_eval). For each in turn:
  1. component = Na U Nb with the patch's exact cell states;
  2. SUFFICIENT: the component alone (rest of the patch inert) is COMBINE at G1;
  3. KNOWN ANSWER on R4c's task (G1 + input C at (12, 1)): the component alone is strictly dependent on a and b and
     not on c, with in2 = (0x55, 0xAA) (R4c's alphabet), else with (0x33, 0xCC) (R4's alphabet).
The first candidate passing 2 and 3 is the component. None -> STAGE2B_NOT_TESTABLE.json and no plan.
Plans: R4c's 32 units (arms N S U P x seeds 0-7, 20 x 1024) through r01_run.py, and one r4_reduce unit with this
component's own transplant table.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402

ALPHABETS = ((0x55, 0xAA), (0x33, 0xCC))
INC = (12, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s1", required=True)
    ap.add_argument("--fold-dir", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--backend", default="gpu")
    a = ap.parse_args()
    FP.install()
    import r01_lib as L
    import r3_frontier as F
    import r4_accum as A
    F.set_geom("G1")
    os.makedirs(a.outdir, exist_ok=True)
    s1 = json.load(open(a.s1))
    pool = [c for c in s1["candidates"] if c["arm"] == "C" and c["AUTONOMOUS"] and c["energy_multi"] == 0]
    pool.sort(key=lambda c: (not c["COMPOSE"], c["seed"], c["found_at_eval"]))
    log, chosen = [], None
    for c in pool:
        z = np.load(os.path.join(a.fold_dir, "G1_C_s%d_combine.npz" % c["seed"]))
        patch = z["patches"][[str(h) for h in z["hashes"]].index(c["hash"])]
        cells = sorted({tuple(x) for x in c["Na"]} | {tuple(x) for x in c["Nb"]})
        states = [tuple(int(v) for v in patch[:, y, x]) for (y, x) in cells]
        alone = L.place(cells, states)
        entry = {"seed": c["seed"], "hash": c["hash"], "COMPOSE": c["COMPOSE"], "cells": len(cells),
                 "sufficient": L.rung(L.table(alone, a.backend)) == 2, "in2": None}
        if entry["sufficient"]:
            A.INC = INC
            for in2 in ALPHABETS:
                A.IN2 = in2
                out8 = A.Eval3("XOR", side=32, backend=a.backend).run_batch(np.stack([alone]))[0]
                if A.strict3(out8) == [True, True, False]:
                    entry["in2"] = list(in2)
                    break
        log.append(entry)
        if entry["sufficient"] and entry["in2"]:
            chosen = (c, patch, cells, states, entry["in2"])
            break
    if chosen is None:
        json.dump({"schema": "aether.robust01.s2b.v1", "disposition": "REUSE_NOT_TESTABLE", "pool": len(pool),
                   "log": log}, open(os.path.join(a.outdir, "STAGE2B_NOT_TESTABLE.json"), "w"), indent=1)
        print("REUSE_NOT_TESTABLE", len(pool))
        return 0
    c, patch, cells, states, in2 = chosen
    comp_path = os.path.join(a.outdir, "component_s2b.json").replace(os.sep, "/")
    json.dump({"source": "ROBUST01 stage 1 G1_C_s%d (fold law; certificate-guided search; AUTONOMOUS%s)"
                         % (c["seed"], ", COMPOSE" if c["COMPOSE"] else ""),
               "geom": "G1", "hash": c["hash"], "cells": [list(x) for x in cells], "states": [list(s) for s in states],
               "patch": patch.tolist(), "certificate": c, "in2": in2, "selection_log": log},
              open(comp_path, "w"), indent=1)
    tr_path = os.path.join(a.outdir, "transplant_task1_s2b.json").replace(os.sep, "/")
    json.dump(L.transplant(cells, states, a.backend), open(tr_path, "w"), indent=1)
    in2s = "0x%02X,0x%02X" % tuple(in2)
    search_dir = os.path.join(a.outdir, "search").replace(os.sep, "/")
    plan = []
    for s in range(8):
        for arm in "NSUP":
            plan.append({"id": "S2B_%s_s%d" % (arm, s),
                         "argv": ["../ROBUST01/r01_run.py", "{out}", "R4/r4_accum.py", "--arm", arm, "--seed", str(s),
                                  "--component", comp_path, "--batches", "20", "--geom", "G1", "--inc", "12,1",
                                  "--in2", in2s, "--out", "{out}"],
                         "out": "%s/%s_s%d.json" % (search_dir, arm, s)})
    json.dump(plan, open(os.path.join(a.outdir, "plan_s2b_search.json"), "w"), indent=1)
    red = [{"id": "S2B_reduce",
            "argv": ["../ROBUST01/r01_run.py", "{out}", "R4/r4_reduce.py", search_dir,
                     "--rules", os.path.join(FP.REACH01, "R4", "RULES.json").replace(os.sep, "/"),
                     "--component", comp_path, "--geom", "G1", "--inc", "12,1", "--in2", in2s,
                     "--transplant", tr_path, "--out", "{out}"],
            "out": os.path.join(a.outdir, "REDUCTION_S2B.json").replace(os.sep, "/")}]
    json.dump(red, open(os.path.join(a.outdir, "plan_s2b_reduce.json"), "w"), indent=1)
    print("component", comp_path, "cells", len(cells), "in2", in2s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
