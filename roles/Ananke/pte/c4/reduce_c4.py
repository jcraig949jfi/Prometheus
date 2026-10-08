"""PTE-C4 reducer (frozen rules; PREREG_PTE_C4.md). usage: python reduce_c4.py PLAN_T.json RUN_DIR OUT.json

Per task (GATE, FLIP) and arm (A, B, C): k = competent champions (task ruler TRUE on held), n, CP95, cells hit.
Material(x vs y) on (cell, idx) present in both: x >= 4, x's successes in >= 2 cells, x - y >= 4.
Labels per task:
  DUPLICATION_HELPS            Material(B vs A)
  REUSE_IMPROVES_COMPOSITION   Material(C vs B)    (paired: same gen-0 populations, only library insertion differs)
  COMPOSITION_REACHED          the task is competent in >= 4 searches of some arm across >= 2 cells
  SPARSE_EXCEPTION             1-3 competent searches in an arm, or all in one cell
  NO_COMPOSITION               0 competent searches in every arm
Reuse diagnostics (arm C):
  MODULE_PRESENT   fraction of champions carrying >= 1 library-tagged line; and of those, >= 1 LIVE library line
  MODULE_CAUSAL    among competent arm-C champions with library lines: ablating all library lines turns competence off
                   (status != TRUE) -> causal; reported as k/n
  MODULE_INTEGRITY library-tagged slots still holding an unmodified module instruction vs modified
  DESCRIPTION_LENGTH live-line count of competent champions per arm (median)
Exclusions (flagged): OVERLAP.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy.stats import beta


def cp95(k, n):
    if n == 0:
        return [0.0, 1.0]
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def main(plan_p, run_dir, out_p):
    rows = [json.loads(l) for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")) for l in open(p) if l.strip()]
    flags = [["OVERLAP", r["job_id"]] for r in rows if r["held_train_overlap"]]
    rows = [r for r in rows if not r["held_train_overlap"]]
    res = {"n_rows": len(rows), "flags": flags, "tasks": {}}
    for task in sorted({r["task"] for r in rows}):
        T = {}
        by = {(r["cell_id"], r["idx"], r["arm"]): r for r in rows if r["task"] == task}
        for arm in ("A", "B", "C"):
            rr = [r for r in rows if r["task"] == task and r.get("arm") == arm]
            k = sum(r["success"] for r in rr)
            d = {"n": len(rr), "k": k, "CP95": cp95(k, len(rr)),
                 "cells_hit": sorted({r["cell_id"] for r in rr if r["success"]}),
                 "median_live_lines_competent": float(np.median([len(r["live_lines"]) for r in rr if r["success"] and "live_lines" in r] or [np.nan]))}
            if arm == "C":
                withlib = [r for r in rr if r["lib_lines"] > 0]
                d["module_present"] = [len(withlib), len(rr)]
                d["module_live"] = [sum(1 for r in withlib if r.get("live_lib_lines")), len(withlib)]
                comp = [r for r in withlib if r["success"]]
                d["module_causal"] = [sum(1 for r in comp if r.get("lib_ablation", {}).get("status") != "TRUE"), len(comp)]
                tot = sum(v["n"] for r in withlib for v in r.get("module_integrity", {}).values())
                un = sum(v["unmodified"] for r in withlib for v in r.get("module_integrity", {}).values())
                d["module_integrity"] = {"slots": tot, "unmodified": un}
            T[arm] = d

        def material(x, y):
            keys = sorted({(c, i) for (c, i, a) in by if a == x} & {(c, i) for (c, i, a) in by if a == y})
            kx = [k for k in keys if by[(k[0], k[1], x)]["success"]]
            ky = [k for k in keys if by[(k[0], k[1], y)]["success"]]
            return {"x": x, "y": y, "n_pairs": len(keys), "kx": len(kx), "ky": len(ky),
                    "material": len(kx) >= 4 and len({k[0] for k in kx}) >= 2 and len(kx) - len(ky) >= 4}
        mBA, mCB = material("B", "A"), material("C", "B")
        labels = []
        if mBA["material"]:
            labels.append("DUPLICATION_HELPS")
        if mCB["material"]:
            labels.append("REUSE_IMPROVES_COMPOSITION")
        best = max(T.values(), key=lambda v: v["k"])
        if best["k"] >= 4 and len(best["cells_hit"]) >= 2:
            labels.append("COMPOSITION_REACHED")
        elif any(v["k"] for v in T.values()):
            labels.append("SPARSE_EXCEPTION")
        else:
            labels.append("NO_COMPOSITION")
        res["tasks"][task] = {"arms": T, "contrasts": {"B_vs_A": mBA, "C_vs_B": mCB}, "labels": labels}
    json.dump(res, open(out_p, "w"), indent=1, default=str)
    print(json.dumps({t: {"labels": v["labels"], **{a: f'{x["k"]}/{x["n"]}' for a, x in v["arms"].items()},
                          "C_reuse": {k: v["arms"]["C"].get(k) for k in ("module_present", "module_live", "module_causal")}}
                      for t, v in res["tasks"].items()}, indent=1))
    print("flags", flags)


if __name__ == "__main__":
    main(*sys.argv[1:4])
