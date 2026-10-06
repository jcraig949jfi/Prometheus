"""PTE-C2B reducer: rows -> per-arm counts, arm verdicts, family search-barrier classification, stop flags.

usage: python reduce_c2b.py PLAN.json RUN_DIR OUT.json

Row exclusions (each reported; an excluded row never counts as a failure or a success):
  PLANT_FALSE        the plant reads FALSE on the row's held worlds          -> row excluded, flag
  START_COMPETENT    a BRK/STEP injected start reads TRUE on held worlds      -> row excluded, flag
                     (it was FALSE on its qualification worlds; TRUE on held means it was not reliably broken)
  OVERLAP            held/train overlap                                       -> row excluded, flag
  PREFIX_FAIL        B4X prefix gate not PASS                                 -> B4X row excluded, flag
Arm verdicts per family (n = rows counted; CP95 = exact Clopper-Pearson):
  BRK1 / BRK2 (count = BROKEN_LINEAGE_RECOVERY):
    LOCALLY_REPAIRABLE      >= 4 recoveries in >= 2 cells
    SPARSE_REPAIR_PATH      1-3 recoveries, or >= 4 concentrated in one cell
    LOCALLY_FLAT_SUPPORTED  0 recoveries
  B4X (count = NEW_AFTER_36: gen-36 champion not competent, a gen-72/108/144 champion competent):
    BUDGET_RESPONSIVE >= 4 in >= 2 cells; WEAK_BUDGET_RESPONSE 1-3 or one cell; NO_BUDGET_RESPONSE 0
  STEP (count = STEP_LINEAGE_SUCCESS):
    STEP_RESPONSIVE >= 4 in >= 2 cells; WEAK_STEP_RESPONSE 1-3 or one cell; NO_STEP_RESPONSE 0
Family classification (order s20). Responsive set R = {BRK1 if LOCALLY_REPAIRABLE, B4X if BUDGET_RESPONSIVE,
STEP if STEP_RESPONSIVE}:
  R = {}      -> LANDSCAPE_BARRIER (suffix _STRICT if BRK1, B4X and STEP all have count 0, else
                 _WITH_SPARSE_EXCEPTIONS)
  R = {B4X}   -> BUDGET_LIMITED
  R = {STEP}  -> STEPPING_STONE_LIMITED
  R = {BRK1}  -> LOCAL_BASIN_BARRIER
  otherwise   -> MIXED (R listed)
BACKGROUND_SUCCESS counts are reported per arm and never enter the lineage counts.
"""
import glob
import json
import os
import sys
from collections import defaultdict

from scipy.stats import beta


def cp95(k, n):
    if n == 0:
        return [0.0, 1.0]
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [lo, hi]


def ladder(k, cells_hit, top, mid, zero):
    if k == 0:
        return zero
    if k >= 4 and cells_hit >= 2:
        return top
    return mid


def main(plan_p, run_dir, out_p):
    plan = json.load(open(plan_p))
    rows = []
    for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")):
        rows += [json.loads(l) for l in open(p) if l.strip()]
    flags, kept = [], []
    for r in rows:
        bad = None
        if r["held_eval"]["plant"]["status"] == "FALSE":
            bad = "PLANT_FALSE"
        elif "injected" in r["held_eval"] and r["held_eval"]["injected"]["status"] == "TRUE":
            bad = "START_COMPETENT"
        elif r["held_train_overlap"]:
            bad = "OVERLAP"
        elif r["arm"] == "B4X" and r.get("prefix_gate", {}).get("status") != "PASS":
            bad = "PREFIX_FAIL"
        if bad:
            flags.append([bad, r["job_id"]])
        else:
            kept.append(r)
    fam_of = {c["cell_id"]: c["role"] for c in plan["cells"]}
    res = {"n_rows": len(rows), "n_counted": len(kept), "flags": flags, "families": {}, "cells": {}}
    by = defaultdict(list)
    for r in kept:
        by[(fam_of[r["cell_id"]], r["arm"])].append(r)
    for cid in fam_of:
        cr = [r for r in kept if r["cell_id"] == cid]
        res["cells"][cid] = {arm: {"n": sum(r["arm"] == arm for r in cr),
                                   "lineage": sum(r["arm"] == arm and r["attribution"] in ("BROKEN_LINEAGE_RECOVERY", "STEP_LINEAGE_SUCCESS") for r in cr),
                                   "background": sum(r["arm"] == arm and r["attribution"] == "BACKGROUND_SUCCESS" for r in cr),
                                   "new_after_36": sum(r["arm"] == arm and bool(r.get("new_after_36")) for r in cr)}
                             for arm in ("BRK1", "BRK2", "B4X", "STEP")}
    for fam in ("RELAY-mh", "FLIP"):
        F = {}
        for arm in ("BRK1", "BRK2", "STEP", "B4X"):
            rr = by[(fam, arm)]
            if arm == "B4X":
                hit = [r for r in rr if r.get("new_after_36")]
            else:
                want = "BROKEN_LINEAGE_RECOVERY" if arm.startswith("BRK") else "STEP_LINEAGE_SUCCESS"
                hit = [r for r in rr if r["attribution"] == want]
            k, n = len(hit), len(rr)
            cells_hit = len({r["cell_id"] for r in hit})
            if arm.startswith("BRK"):
                v = ladder(k, cells_hit, "LOCALLY_REPAIRABLE", "SPARSE_REPAIR_PATH", "LOCALLY_FLAT_SUPPORTED")
            elif arm == "B4X":
                v = ladder(k, cells_hit, "BUDGET_RESPONSIVE", "WEAK_BUDGET_RESPONSE", "NO_BUDGET_RESPONSE")
            else:
                v = ladder(k, cells_hit, "STEP_RESPONSIVE", "WEAK_STEP_RESPONSE", "NO_STEP_RESPONSE")
            F[arm] = {"k": k, "n": n, "CP95": cp95(k, n), "cells_hit": cells_hit, "verdict": v,
                      "background_success": sum(r["attribution"] == "BACKGROUND_SUCCESS" for r in rr),
                      "final_success_any": sum(r["success"] for r in rr)}
            if arm == "B4X":
                F[arm]["first_competent_gen"] = [r.get("first_competent_gen") for r in rr if r.get("first_competent_gen")]
                F[arm]["competent_at_36"] = sum(r["checkpoint_status"]["36"] == "TRUE" if isinstance(r["checkpoint_status"], dict) and "36" in r["checkpoint_status"] else r["checkpoint_status"].get(36) == "TRUE" for r in rr)
                F[arm]["persistent_after_first"] = sum(
                    1 for r in rr if r.get("first_competent_gen") and all(
                        (r["checkpoint_status"].get(str(g)) or r["checkpoint_status"].get(g)) == "TRUE"
                        for g in (36, 72, 108, 144) if g >= r["first_competent_gen"]))
        Rset = sorted(a for a, tag in (("BRK1", "LOCALLY_REPAIRABLE"), ("B4X", "BUDGET_RESPONSIVE"), ("STEP", "STEP_RESPONSIVE"))
                      if F[a]["verdict"] == tag)
        if not Rset:
            strict = F["BRK1"]["k"] == 0 and F["B4X"]["k"] == 0 and F["STEP"]["k"] == 0
            cls = "LANDSCAPE_BARRIER" + ("_STRICT" if strict else "_WITH_SPARSE_EXCEPTIONS")
        elif Rset == ["B4X"]:
            cls = "BUDGET_LIMITED"
        elif Rset == ["STEP"]:
            cls = "STEPPING_STONE_LIMITED"
        elif Rset == ["BRK1"]:
            cls = "LOCAL_BASIN_BARRIER"
        else:
            cls = "MIXED:" + "+".join(Rset)
        res["families"][fam] = {"arms": F, "responsive": Rset, "classification": cls}
    json.dump(res, open(out_p, "w"), indent=1, default=str)
    print(json.dumps({f: {"class": v["classification"],
                          **{a: f'{x["k"]}/{x["n"]} {x["verdict"]} bg={x["background_success"]}' for a, x in v["arms"].items()}}
                      for f, v in res["families"].items()}, indent=1))
    print("flags", flags)


if __name__ == "__main__":
    main(*sys.argv[1:4])
