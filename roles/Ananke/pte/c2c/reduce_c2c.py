"""C2BX + PTE-C2C reducer. usage: python reduce_c2c.py PLAN.json RUN_DIR OUT.json

Exclusions (flagged; never counted as success or failure): PLANT_FALSE (plant FALSE on the row's held worlds),
START_COMPETENT (a C2C STEP stone TRUE on held worlds), OVERLAP (held/train), PREFIX_FAIL (C2BX gate).

C2BX (measurement; per cell, pooled, and leave-RELAY-0019-out):
  cumulative success at 4x/8x/16x = any checkpoint champion competent at gen <= 144 / 288 / 576 (checkpoints every
  36 generations); first competent generation; persistence after first competence; final champion status at each
  budget. Late tail: NEW = competent by 576 and not by 144.
    TAIL_CONTINUES >= 4 NEW in >= 2 cells; TAIL_SPARSE 1-3 NEW or all in one cell; TAIL_STOPS 0 NEW.
  Arrivals reported separately for (144, 288] and (288, 576].
C2C (FLIP; counts per arm; STEP arms count STEP_LINEAGE_SUCCESS, BASE arms count any competent champion; background
successes in STEP arms reported separately):
  a = OP0_BASE, b = OPB_BASE, c = OP0_STEP, d = OPB_STEP.
  Material(x vs y), on the (cell, idx) pairs present in both arms: x >= 4, x's successes in >= 2 cells, and x - y >= 4.
  Classification, in order:
    Mc and Md|b              -> BASIN_PATH_ACCESSIBILITY_BARRIER (suffix _WITH_OPERATOR_EFFECT if Mb)
    Mb and not (Mc or Md|b)  -> OPERATOR_GRANULARITY_BARRIER
    Md|a and not Mb, not Mc  -> COMPOUND_SEARCH_GEOMETRY_BARRIER (interaction)
    none of Mb, Mc, Md|b, Md|a -> NEITHER_IMPROVES (suffix _WITH_SPARSE_EXCEPTIONS if any arm has a success)
    otherwise                -> MIXED (flags listed)
  where Mb = Material(b vs a), Mc = Material(c vs a), Md|b = Material(d vs b), Md|a = Material(d vs a).
  One-sided Fisher p and exact CP95 are reported beside every count; they do not enter the rule.
"""
import glob
import json
import os
import sys
from collections import defaultdict

from scipy.stats import beta, fisher_exact


def cp95(k, n):
    if n == 0:
        return [0.0, 1.0]
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def main(plan_p, run_dir, out_p):
    plan = json.load(open(plan_p))
    rows = []
    for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")):
        rows += [json.loads(l) for l in open(p) if l.strip()]
    flags, kept = [], []
    for r in rows:
        bad = None
        if r["held_train_overlap"]:
            bad = "OVERLAP"
        elif r["campaign"] == "C2BX":
            if r["plant_held"]["status"] == "FALSE":
                bad = "PLANT_FALSE"
            elif r["prefix_gate"]["status"] != "PASS":
                bad = "PREFIX_FAIL"
        else:
            if r["held_eval"]["plant"]["status"] == "FALSE":
                bad = "PLANT_FALSE"
            elif "injected" in r["held_eval"] and r["held_eval"]["injected"]["status"] == "TRUE":
                bad = "START_COMPETENT"
        (flags.append([bad, r["job_id"]]) if bad else kept.append(r))
    res = {"n_rows": len(rows), "n_counted": len(kept), "flags": flags}
    # ---------------- C2BX
    bx = [r for r in kept if r["campaign"] == "C2BX"]

    def curve(rs):
        out = {"n": len(rs)}
        sb = lambda r, b: bool(r["success_by"].get(b, False))      # a row only counts at budgets it reached
        for b in ("144", "288", "576"):
            rb = [r for r in rs if b in r["success_by"]]
            k = sum(sb(r, b) for r in rb)
            out[f"cum_{b}"] = [k, len(rb), cp95(k, len(rb))]
        new = [r for r in rs if sb(r, "576") and not sb(r, "144")]
        out["new_after_144"] = len(new)
        out["new_144_288"] = sum(1 for r in rs if sb(r, "288") and not sb(r, "144"))
        out["new_288_576"] = sum(1 for r in rs if sb(r, "576") and not sb(r, "288"))
        out["first_competent_gens"] = sorted(r["first_competent_gen"] for r in rs if r["first_competent_gen"])
        out["persistent_after_first"] = sum(1 for r in rs if r["first_competent_gen"] and all(
            r["checkpoint_status"][g] == "TRUE" for g in r["checkpoint_status"] if int(g) >= r["first_competent_gen"]))
        cells_new = {r["cell_id"] for r in new}
        out["tail"] = ("TAIL_STOPS" if not new else
                       ("TAIL_CONTINUES" if len(new) >= 4 and len(cells_new) >= 2 else "TAIL_SPARSE"))
        out["final_status_TRUE_at"] = {b: sum(r["final_status_at"].get(b) == "TRUE" for r in rs) for b in ("144", "288", "576")}
        return out
    res["C2BX"] = {"pooled": curve(bx),
                   "leave_0019_out": curve([r for r in bx if not r["cell_id"].startswith("RELAY-0019")]),
                   "per_cell": {cid: curve([r for r in bx if r["cell_id"] == cid]) for cid in sorted({r["cell_id"] for r in bx})}}
    # ---------------- C2C
    cc = [r for r in kept if r["campaign"] == "C2C"]
    arm = defaultdict(dict)
    for r in cc:
        arm[r["arm"]][(r["cell_id"], r["idx"])] = r

    def hit(r):
        if r["start"] == "STEP":
            return r["attribution"] == "STEP_LINEAGE_SUCCESS"
        return bool(r["success"])

    def material(x, y):
        keys = sorted(set(arm[x]) & set(arm[y]))
        kx = [k for k in keys if hit(arm[x][k])]; ky = [k for k in keys if hit(arm[y][k])]
        n = len(keys)
        p = fisher_exact([[len(kx), n - len(kx)], [len(ky), n - len(ky)]], alternative="greater")[1] if n else 1.0
        m = len(kx) >= 4 and len({k[0] for k in kx}) >= 2 and len(kx) - len(ky) >= 4
        return {"x": x, "y": y, "n_pairs": n, "kx": len(kx), "ky": len(ky), "cells_x": len({k[0] for k in kx}),
                "fisher_p_one_sided": p, "material": m}
    A = {a: {"n": len(arm[a]), "k": sum(hit(r) for r in arm[a].values()),
             "background": sum(r["attribution"] == "BACKGROUND_SUCCESS" for r in arm[a].values()) if a.endswith("STEP") else None,
             "per_cell": {cid: [sum(hit(r) for (c, _), r in arm[a].items() if c == cid), sum(1 for (c, _) in arm[a] if c == cid)]
                          for cid in sorted({c for c, _ in arm[a]})}}
         for a in ("OP0_BASE", "OPB_BASE", "OP0_STEP", "OPB_STEP")}
    for a in A:
        A[a]["CP95"] = cp95(A[a]["k"], A[a]["n"])
    Mb = material("OPB_BASE", "OP0_BASE"); Mc = material("OP0_STEP", "OP0_BASE")
    Mdb = material("OPB_STEP", "OPB_BASE"); Mda = material("OPB_STEP", "OP0_BASE")
    mb, mc, mdb, mda = Mb["material"], Mc["material"], Mdb["material"], Mda["material"]
    if mc and mdb:
        cls = "BASIN_PATH_ACCESSIBILITY_BARRIER" + ("_WITH_OPERATOR_EFFECT" if mb else "")
    elif mb and not (mc or mdb):
        cls = "OPERATOR_GRANULARITY_BARRIER"
    elif mda and not mb and not mc:
        cls = "COMPOUND_SEARCH_GEOMETRY_BARRIER"
    elif not (mb or mc or mdb or mda):
        anyhit = any(A[a]["k"] for a in A) or any((A[a]["background"] or 0) for a in A)
        cls = "NEITHER_IMPROVES" + ("_WITH_SPARSE_EXCEPTIONS" if anyhit else "")
    else:
        cls = "MIXED:" + ",".join(n for n, v in (("Mb", mb), ("Mc", mc), ("Md|b", mdb), ("Md|a", mda)) if v)
    res["C2C"] = {"arms": A, "contrasts": {"Mb": Mb, "Mc": Mc, "Md|b": Mdb, "Md|a": Mda}, "classification": cls}
    json.dump(res, open(out_p, "w"), indent=1, default=str)
    print(json.dumps({"C2BX_pooled": {k: v for k, v in res["C2BX"]["pooled"].items()},
                      "C2BX_leave_0019_out_tail": res["C2BX"]["leave_0019_out"]["tail"],
                      "C2C": {a: f'{v["k"]}/{v["n"]} bg={v["background"]}' for a, v in A.items()},
                      "C2C_class": cls}, indent=1, default=str))
    print("flags", flags)


if __name__ == "__main__":
    main(*sys.argv[1:4])
