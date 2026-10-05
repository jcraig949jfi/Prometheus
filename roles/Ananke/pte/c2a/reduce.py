"""PTE-C2A reducer: rows -> cell verdicts, landscape form, family verdicts, positive control, stop flags.

usage: python reduce.py PLAN.json RUN_DIR OUT.json

Unit = the search seed. A search succeeds iff its champion's competence-class ruler is TRUE (reading3, 2.605 SE).
Censoring: every contrast uses only seed indices completed in BOTH arms (balanced); counts report n.

Cell verdict (C2 draft s6.4; operator order s9), evaluated in this order:
  stop flags (plant FALSE on its own held worlds, ceiling violation, held/train overlap) -> SUSPENDED
  U-LOCATED        any PSEED champion FALSE (plant lost), regardless of k_BASE (k_BASE reported)
  SEARCH-SUCCEEDS  k_BASE >= 6
  S-PARTIAL        2 <= k_BASE <= 5
  S-LOCATED        k_BASE <= 1, n_BASE >= 10, PSEED TRUE in every completed PSEED seed (>= 4)
  UNRESOLVED       anything else (incl. an INDETERMINATE PSEED, or censoring below the n floors)
Landscape form (S-LOCATED / S-PARTIAL cells, pooled over the family's such cells):
  RESPONSIVE      W0 or M32 raises success vs BASE (one-sided Fisher on pooled balanced counts, BH q .05 over
                  the family's two contrasts), or KSEED recovery > 0 at k >= 2 (a climbable basin)
  NEEDLE-LIKE     no arm responds (each upper 95% Newcombe bound on the success difference < .25),
                  KSEED k=1 recovery > 0 and k=2 = k=4 = 0
  LOCALLY_FLAT    no arm responds (bounded as above) and KSEED k=1 recovery = 0
  UNRESOLVED      anything else (an arm neither significant nor bounded below .25 = underpowered)
Family verdict (4 cells): SEARCH_LIMIT_SUPPORTED >= 3 S-LOCATED; SEARCH_LIMIT_NOT_SUPPORTED >= 3 in
  {SEARCH-SUCCEEDS, U-LOCATED}; else MIXED. Fewer than 4 interpretable cells: CELL_LEVEL_ONLY.
Positive control: SEARCH_HARNESS_FAILED iff k_BASE(control) <= 2 of 8 or a control PSEED is lost.
"""
import glob
import json
import math
import os
import sys
from collections import defaultdict

from scipy import stats


def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def newcombe_upper(k1, n1, k0, n0):
    """Upper 95% bound of p1 - p0 (Newcombe hybrid score)."""
    l1, u1 = wilson(k1, n1); l0, u0 = wilson(k0, n0)
    p1, p0 = k1 / n1, k0 / n0
    return p1 - p0 + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)


def bh(pv, q=0.05):
    idx = sorted(range(len(pv)), key=lambda i: pv[i])
    m = len(pv); rej = [False] * m; kmax = -1
    for r, i in enumerate(idx, 1):
        if pv[i] <= q * r / m:
            kmax = r
    for r, i in enumerate(idx, 1):
        rej[i] = r <= kmax
    return rej


def main(plan_p, run_dir, out_p):
    plan = json.load(open(plan_p))
    rows = []
    for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")):
        rows += [json.loads(l) for l in open(p) if l.strip()]
    by = defaultdict(dict)                      # cell -> (arm, idx) -> row
    for r in rows:
        by[r["cell_id"]][(r["arm"], r["idx"])] = r
    cells = {c["cell_id"]: c for c in plan["cells"]}
    res = {"n_rows": len(rows), "cells": {}, "families": {}, "control": None, "stop_flags": []}
    for cid, c in cells.items():
        R = by.get(cid, {})
        st = lambda arm: {i: R[(arm, i)]["competence"]["status"] for (a, i) in R if a == arm}
        arms = {a: st(a) for a in c["arms"]}
        flags = []
        for r in R.values():
            if r["plant_held"]["status"] == "FALSE":
                flags.append(("PLANT_FAILURE", r["job_id"]))
            if r["namespaces"]["held_train_overlap"]:
                flags.append(("HELD_TRAIN_OVERLAP", r["job_id"]))
            if c.get("ceiling") is not None and r["champ_acc"] > c["ceiling"] + 0.05:
                flags.append(("CEILING_VIOLATION?", r["job_id"], r["champ_acc"], c["ceiling"]))
        b = arms.get("BASE", {})
        kB, nB = sum(v == "TRUE" for v in b.values()), len(b)
        ps = arms.get("PSEED", {})
        cell = {"role": c["role"], "k_BASE": kB, "n_BASE": nB, "BASE_CP95": wilson(kB, nB),
                "PSEED": ps, "flags": flags,
                "arms": {a: {"k": sum(v == "TRUE" for v in d.values()), "n": len(d),
                             "indeterminate": sum(v == "INDETERMINATE" for v in d.values())} for a, d in arms.items()}}
        if c["role"] == "RELAY-1h":
            failed = kB <= 2 or any(v == "FALSE" for v in ps.values())
            cell["verdict"] = "SEARCH_HARNESS_FAILED" if failed else "CONTROL_ALIVE"
            res["control"] = cell
            res["cells"][cid] = cell
            continue
        if flags:
            cell["verdict"] = "SUSPENDED"
        elif any(v == "FALSE" for v in ps.values()):
            cell["verdict"] = "U-LOCATED"
        elif kB >= 6:
            cell["verdict"] = "SEARCH-SUCCEEDS"
        elif 2 <= kB <= 5:
            cell["verdict"] = "S-PARTIAL"
        elif kB <= 1 and nB >= 10 and len(ps) >= 4 and all(v == "TRUE" for v in ps.values()):
            cell["verdict"] = "S-LOCATED"
        else:
            cell["verdict"] = "UNRESOLVED"
        # balanced contrasts (indices completed in both arms)
        con = {}
        for arm in ("W0", "M32"):
            d = arms.get(arm, {})
            ii = sorted(set(d) & set(b))
            con[arm] = {"idx": ii, "k_arm": sum(d[i] == "TRUE" for i in ii), "k_base": sum(b[i] == "TRUE" for i in ii),
                        "n": len(ii)}
        cell["contrasts"] = con
        cell["kseed"] = {a: cell["arms"].get(a) for a in ("KSEED-1", "KSEED-2", "KSEED-4")}
        res["cells"][cid] = cell
    # family level
    for fam_role in ("RELAY-mh", "FLIP"):
        fc = {k: v for k, v in res["cells"].items() if v["role"] == fam_role}
        if not fc:
            continue
        verdicts = [v["verdict"] for v in fc.values()]
        interp = [x for x in verdicts if x not in ("SUSPENDED",)]
        if len(fc) < 4 or len(interp) < 4:
            fv = "CELL_LEVEL_ONLY"
        elif sum(x == "S-LOCATED" for x in verdicts) >= 3:
            fv = "SEARCH_LIMIT_SUPPORTED"
        elif sum(x in ("SEARCH-SUCCEEDS", "U-LOCATED") for x in verdicts) >= 3:
            fv = "SEARCH_LIMIT_NOT_SUPPORTED"
        else:
            fv = "MIXED"
        S = {k: v for k, v in fc.items() if v["verdict"] in ("S-LOCATED", "S-PARTIAL")}
        land = None
        if S:
            pooled, pv, keys = {}, [], []
            for arm in ("W0", "M32"):
                ka = sum(v["contrasts"][arm]["k_arm"] for v in S.values())
                kb = sum(v["contrasts"][arm]["k_base"] for v in S.values())
                n = sum(v["contrasts"][arm]["n"] for v in S.values())
                p = stats.fisher_exact([[ka, n - ka], [kb, n - kb]], alternative="greater")[1] if n else 1.0
                ub = newcombe_upper(ka, n, kb, n) if n else 1.0
                pooled[arm] = {"k_arm": ka, "k_base": kb, "n": n, "p_one_sided": p, "upper95_diff": ub}
                pv.append(p); keys.append(arm)
            rej = bh(pv)
            for arm, r_ in zip(keys, rej):
                pooled[arm]["bh_reject"] = r_
            ks = {}
            for a in ("KSEED-1", "KSEED-2", "KSEED-4"):
                k_ = sum((v["arms"].get(a) or {}).get("k", 0) for v in S.values())
                n_ = sum((v["arms"].get(a) or {}).get("n", 0) for v in S.values())
                ks[a] = {"k": k_, "n": n_, "rate": k_ / n_ if n_ else None, "CP95": wilson(k_, n_)}
            bounded = all(pooled[a]["upper95_diff"] < 0.25 for a in pooled)
            k1, k2, k4 = (ks[a]["k"] for a in ("KSEED-1", "KSEED-2", "KSEED-4"))
            if any(rej) or (k2 + k4) > 0:
                form = "RESPONSIVE"
            elif bounded and k1 == 0 and ks["KSEED-1"]["n"] > 0:
                form = "LOCALLY_FLAT"
            elif bounded and k1 > 0 and k2 == 0 and k4 == 0:
                form = "NEEDLE-LIKE"
            else:
                form = "UNRESOLVED"
            land = {"cells": list(S), "pooled": pooled, "kseed": ks, "arms_bounded_below_.25": bounded, "form": form}
        res["families"][fam_role] = {"cells": {k: v["verdict"] for k, v in fc.items()}, "verdict": fv,
                                     "BASE_pooled": [sum(v["k_BASE"] for v in fc.values()),
                                                     sum(v["n_BASE"] for v in fc.values())],
                                     "landscape": land}
    for cid, v in res["cells"].items():
        for f in v["flags"]:
            res["stop_flags"].append([cid] + list(f))
    json.dump(res, open(out_p, "w"), indent=1, default=str)
    print(json.dumps({"control": res["control"] and res["control"]["verdict"],
                      "families": {k: v["verdict"] for k, v in res["families"].items()},
                      "cells": {k: (v["verdict"], v["k_BASE"], v["n_BASE"]) for k, v in res["cells"].items()},
                      "stop_flags": len(res["stop_flags"])}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
