"""REACH01 R4 reducer: per-arm acquisition of COMBINE3, component necessity and copy structure, robustness, decision.

    python r4_reduce.py UNIT_DIR --rules RULES.json --component component_planted.json --out REDUCTION.json

NECESSITY (frozen definition, for up to MAXSOL found solutions per unit, in discovery order):
  component copies = offsets (dy, dx) in [-OFF, OFF]^2 at which >= 80% of the component's cells match exactly.
  For each solution: rung after inerting ALL copy cells, and after inerting each copy alone.
  necessary = inerting all copies drops the rung below 3.
POSITION ROBUSTNESS: fraction of 64 tile positions at which the solution keeps COMBINE3.
"""

import argparse
import glob
import json
import os
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "R3"))
import r4_accum as A  # noqa: E402

MAXSOL = 5


def copies(patch, comp):
    cells, states = comp
    out = []
    for dy in range(-A.OFF, A.OFF + 1):
        for dx in range(-A.OFF, A.OFF + 1):
            match, tot = 0, 0
            for (y, x), s in zip(cells, states):
                yy, xx = y + dy, x + dx
                if 0 <= yy < 16 and 0 <= xx < 16:
                    tot += 1
                    match += int(tuple(patch[:, yy, xx]) == tuple(s))
            if tot and match / len(cells) >= 0.8:
                out.append((dy, dx))
    return out


def inert(patch, comp, offs):
    q = patch.copy()
    for (dy, dx) in offs:
        for (y, x) in comp[0]:
            yy, xx = y + dy, x + dx
            if 0 <= yy < 16 and 0 <= xx < 16:
                q[:, yy, xx] = (9, 0, 0, 0, 0)
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--rules", required=True)
    ap.add_argument("--component", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.rules))
    comp, _cp = A.load_component(a.component)
    ev = A.Eval3("XOR", side=32)
    budget = None
    arms = {}
    for p in sorted(glob.glob(os.path.join(a.unit_dir, "*_s*.json"))):
        u = json.load(open(p))
        if u.get("schema") != "aether.reach01.r4.search.v1":
            continue
        budget = u["evals"]
        row = {"seed": u["seed"], "first": u["first_combine3_eval"], "found": u["combine3_distinct"],
               "max_rung": u["max_rung"], "max_progress": u["max_progress"], "solutions": []}
        if u.get("found_npz"):
            z = np.load(os.path.join(a.unit_dir, u["found_npz"]))
            for i in range(min(MAXSOL, len(z["patches"]))):
                sol = z["patches"][i]
                offs = copies(sol, comp)
                variants = [inert(sol, comp, offs)] + [inert(sol, comp, [o]) for o in offs]
                # robustness first (64 tile positions); then the ablations are evaluated at a position where the
                # solution itself is COMBINE3 (arbitration is coordinate-keyed), each variant alone at that position
                rob = ev.run_batch(np.stack([sol] * 64))
                good = [j for j in range(64) if sum(A.strict3(rob[j])) == 3]
                pos = good[0] if good else 0
                ref_rung = sum(A.strict3(rob[pos]))
                abl = []
                for v in variants:
                    Pv = np.zeros((pos + 1, 5, 16, 16), np.uint8)
                    Pv[:, 0] = 9
                    Pv[pos] = v
                    abl.append(sum(A.strict3(ev.run_batch(Pv)[pos])))
                row["solutions"].append({
                    "copies": offs, "eval_position": pos, "ref_rung_pos0": ref_rung, "rung_all_copies_inert": abl[0],
                    "rung_each_copy_inert": abl[1:],
                    "necessary": ref_rung == 3 and abl[0] < 3,
                    "position_frac_combine3": float(np.mean([sum(A.strict3(x)) == 3 for x in rob]))})
        arms.setdefault(u["arm"], []).append(row)
    summ = {}
    for arm, rows in arms.items():
        succ = [r for r in rows if r["first"] is not None]
        costs = [r["first"] if r["first"] is not None else budget + 1 for r in rows]
        sols = [s for r in rows for s in r["solutions"]]
        nec = [s["necessary"] for s in sols if s["ref_rung_pos0"] == 3]
        summ[arm] = {"seeds": len(rows), "success_seeds": len(succ), "median_cost": st.median(costs),
                     "solutions_checked": len(sols), "solutions_combine3_at_pos0": len(nec),
                     "necessity_frac": (sum(nec) / len(nec)) if nec else None,
                     "copies_hist": {str(k): sum(1 for s in sols if len(s["copies"]) == k) for k in range(5)},
                     "position_frac_median": st.median([s["position_frac_combine3"] for s in sols]) if sols else None,
                     "max_rung_median": st.median(r["max_rung"] for r in rows)}
    P_, U_, N_, S_ = (summ.get(k, {}) for k in "PUNS")
    trans = json.load(open(os.path.join(HERE, "transplant_task1.json")))
    trans_ok = sum(1 for k, v in trans.items() if k != "(0, 0)" and v >= R["transplant_frac_min"]) >= R["transplant_offsets_min"]

    def reuse(X):
        return (X.get("success_seeds", 0) >= R["seeds_min"] and N_.get("success_seeds", 0) <= R["control_seeds_max"]
                and S_.get("success_seeds", 0) <= R["control_seeds_max"]
                and (X.get("necessity_frac") or 0) >= R["necessity_frac_min"])
    if reuse(P_) and P_["median_cost"] <= R["cost_ratio_max"] * U_.get("median_cost", budget + 1):
        disp = "CUMULATIVE_ACQUISITION_ADVANTAGE"
    elif reuse(P_) or reuse(U_):
        disp = "COMPOSITION_REUSE_SUPPORTED"
    elif trans_ok:
        disp = "TRANSPLANT_SUPPORTED"
    else:
        disp = "REUSE_NOT_SUPPORTED"
    res = {"schema": "aether.reach01.r4.reduction.v1", "label": "ASSISTED CONTROL (planted component)",
           "arms": arms, "summary": summ, "transplant_task1": trans, "transplant_supported": trans_ok,
           "disposition": disp}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(summ, indent=1))
    print("DISPOSITION", disp, "(ASSISTED CONTROL)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
