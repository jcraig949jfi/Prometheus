"""PTE-C4 s8 diagnostic reducer (PREREG_PTE_C4 s7, frozen rule). usage: python reduce_c4d.py RUN_DIR OUT.json
Arm D (GATE, designed two-half library): k competent searches (RELAY-mh TRUE on held), cells hit.
  REPRESENTABLE_BUT_UNSEARCHABLE     k >= 4 across >= 2 cells
  REPRESENTATION_STILL_INADEQUATE    k <= 1
  INCONCLUSIVE_SPARSE                otherwise
Reported with it: per search, whether BOTH halves are present and live in the champion, and whether ablating all library
lines turns competence off (the halves are causal); the paired arm-C GATE outcome is reported by reduce_c4.
Exclusions (flagged): OVERLAP."""
import glob
import json
import os
import sys

from scipy.stats import beta


def cp95(k, n):
    if n == 0:
        return [0.0, 1.0]
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def main(run_dir, out_p):
    rows = [json.loads(l) for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")) for l in open(p) if l.strip()]
    flags = [["OVERLAP", r["job_id"]] for r in rows if r["held_train_overlap"]]
    rows = [r for r in rows if not r["held_train_overlap"] and r.get("arm") == "D"]
    k = sum(r["success"] for r in rows); cells = sorted({r["cell_id"] for r in rows if r["success"]})
    if k >= 4 and len(cells) >= 2:
        verdict = "REPRESENTABLE_BUT_UNSEARCHABLE"
    elif k <= 1:
        verdict = "REPRESENTATION_STILL_INADEQUATE"
    else:
        verdict = "INCONCLUSIVE_SPARSE"
    per = [{"job_id": r["job_id"], "success": r["success"], "lib_modules": r["lib_modules"],
            "both_halves_present": set(r["lib_modules"]) >= {1, 2},
            "live_lib_lines": r.get("live_lib_lines"), "lib_ablation": (r.get("lib_ablation") or {}).get("status")}
           for r in rows]
    res = {"n": len(rows), "k": k, "CP95": cp95(k, len(rows)), "cells_hit": cells, "verdict": verdict, "flags": flags,
           "both_halves_present": sum(p["both_halves_present"] for p in per), "per_search": per}
    json.dump(res, open(out_p, "w"), indent=1)
    print(json.dumps({x: res[x] for x in ("n", "k", "CP95", "cells_hit", "verdict", "both_halves_present", "flags")}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
