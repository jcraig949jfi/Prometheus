"""PTE-C3R reducer (frozen rules; PREREG_PTE_C3R.md s5). usage: python reduce_c3r.py RUN_DIR [RUN_DIR2 ...] OUT.json

Rows from stage 1 (gen 36) and stage 2 (gens 72/108/144) are merged per trajectory (cell, rep, idx).
Competent = the frozen FLIP ruler TRUE on the search's held worlds for a checkpoint champion.
Exclusions (flagged, never counted): PLANT_FALSE (rep plant FALSE on the held worlds), OVERLAP (held/train,
held/monitor).
Per arm and budget b in {36 (1x), 144 (4x)}: k_b = searches with a competent checkpoint at a generation <= b, over the
searches that reached b. Discovery curve at 36/72/108/144.
Partial function: champion held B at each checkpoint; per cell the median over searches.
Material(x vs y, b) on (cell, idx) present at budget b in both arms: x >= 4, x's successes in >= 2 cells, x - y >= 4.
Labels, evaluated at the largest budget where both compared arms have >= 16 searches (4x if available, else 1x):
  CAPACITY_OPENS          Material(R1 vs R0)
  PERSISTENT_STATE_OPENS  Material(R2 vs R0) or Material(R5 vs R1)
  DUPLICATION_OPENS       Material(R3 vs R1) or Material(R4 vs R5)      (paired: same gen-0 populations)
  COMBINATION_REQUIRED    Material(R4 vs R0) and none of the single-factor contrasts above is material
  REPRESENTATION_OPENS    issued together with any of the above (umbrella)
  SPARSE_EXCEPTION        no material contrast, but >= 1 competent search in some non-R0 arm
  NO_REPRESENTATION_EFFECT no competent search in any non-R0 arm
  MIXED                   material contrasts that do not fit one pattern are listed as such
Kill criterion (order s5): MINIMAL_REPRESENTATION_ROUTE_FAILED if R3 and R4 each have <= 1 competent of their 4x
searches (n >= 24 each) AND no replicated upward partial-function shift: no arm among R1-R5 whose per-cell median
champion held B at 4x exceeds R0's by >= .05 in >= 2 cells.
"""
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np
from scipy.stats import beta


def cp95(k, n):
    if n == 0:
        return [0.0, 1.0]
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def main(args):
    out_p = args[-1]; dirs = args[:-1]
    rows = []
    for d in dirs:
        for p in glob.glob(os.path.join(d, "rows_w*.jsonl")):
            rows += [json.loads(l) for l in open(p) if l.strip()]
    traj = defaultdict(dict)
    flags = []
    for r in rows:
        if r["held_train_overlap"] or r["held_monitor_overlap"]:
            flags.append(["OVERLAP", r["job_id"]]); continue
        if r["plant_held"]["status"] == "FALSE":
            flags.append(["PLANT_FALSE", r["job_id"]]); continue
        t = traj[(r["cell_id"], r["rep"], r["idx"])]
        for g, s in r["checkpoint_status"].items():
            t[int(g)] = {"status": s, "B": r["checkpoints"][g]["competence"].get("B", {}).get("mean")}
    reps = sorted({k[1] for k in traj})

    def reached(t, b):
        return b in t

    def success_by(t, b):
        return any(v["status"] == "TRUE" for g, v in t.items() if g <= b)
    res = {"n_rows": len(rows), "flags": flags, "arms": {}}
    for rep in reps:
        T = {k: v for k, v in traj.items() if k[1] == rep}
        a = {}
        for b in (36, 72, 108, 144):
            tt = [v for v in T.values() if reached(v, b)]
            k = sum(success_by(v, b) for v in tt)
            cells = sorted({c for (c, _, _), v in T.items() if reached(v, b) and success_by(v, b)})
            medB = {}
            for c in sorted({c for (c, _, _) in T}):
                bs = [v[b]["B"] for (cc, _, _), v in T.items() if cc == c and reached(v, b) and v[b]["B"] is not None]
                if bs:
                    medB[c] = float(np.median(bs))
            a[str(b)] = {"n": len(tt), "k": k, "CP95": cp95(k, len(tt)), "cells_hit": cells, "median_champ_B": medB}
        res["arms"][rep] = a

    def material(x, y, b):
        keys = sorted({(c, i) for (c, r, i) in traj if r == x and reached(traj[(c, r, i)], b)} &
                      {(c, i) for (c, r, i) in traj if r == y and reached(traj[(c, r, i)], b)})
        kx = [k for k in keys if success_by(traj[(k[0], x, k[1])], b)]
        ky = [k for k in keys if success_by(traj[(k[0], y, k[1])], b)]
        return {"x": x, "y": y, "budget": b, "n_pairs": len(keys), "kx": len(kx), "ky": len(ky),
                "cells_x": len({k[0] for k in kx}),
                "material": len(kx) >= 4 and len({k[0] for k in kx}) >= 2 and len(kx) - len(ky) >= 4}

    def budget_for(x, y):
        for b in (144, 36):
            if res["arms"].get(x, {}).get(str(b), {}).get("n", 0) >= 16 and res["arms"].get(y, {}).get(str(b), {}).get("n", 0) >= 16:
                return b
        return None
    contrasts = {}
    for name, (x, y) in {"cap": ("R1", "R0"), "pers": ("R2", "R0"), "pers_cap": ("R5", "R1"), "dup": ("R3", "R1"),
                         "dup_pers": ("R4", "R5"), "comb": ("R4", "R0")}.items():
        b = budget_for(x, y)
        contrasts[name] = material(x, y, b) if b else None
    m = {k: bool(v and v["material"]) for k, v in contrasts.items()}
    labels = []
    if m["cap"]:
        labels.append("CAPACITY_OPENS")
    if m["pers"] or m["pers_cap"]:
        labels.append("PERSISTENT_STATE_OPENS")
    if m["dup"] or m["dup_pers"]:
        labels.append("DUPLICATION_OPENS")
    if m["comb"] and not (m["cap"] or m["pers"] or m["pers_cap"] or m["dup"] or m["dup_pers"]):
        labels.append("COMBINATION_REQUIRED")
    if labels:
        labels.insert(0, "REPRESENTATION_OPENS")
        if len(labels) > 2:
            labels.append("MIXED")
    else:
        anyk = any(res["arms"][r][str(b)]["k"] for r in reps if r != "R0" for b in (36, 144) if str(b) in res["arms"][r])
        labels.append("SPARSE_EXCEPTION" if anyk else "NO_REPRESENTATION_EFFECT")
    # kill criterion
    k4 = {r: res["arms"].get(r, {}).get("144", {}) for r in ("R3", "R4")}
    shift = {}
    r0 = res["arms"].get("R0", {}).get("144", {}).get("median_champ_B", {})
    for r in ("R1", "R2", "R3", "R4", "R5"):
        mb = res["arms"].get(r, {}).get("144", {}).get("median_champ_B", {})
        shift[r] = {c: mb[c] - r0[c] for c in mb if c in r0}
    replicated_shift = any(sum(v >= .05 for v in s.values()) >= 2 for s in shift.values())
    kill = all(v.get("n", 0) >= 24 and v.get("k", 99) <= 1 for v in k4.values()) and not replicated_shift
    res.update(contrasts=contrasts, labels=labels, partial_B_shift_vs_R0_4x=shift, replicated_upward_shift=replicated_shift,
               kill_criterion={"MINIMAL_REPRESENTATION_ROUTE_FAILED": kill, "R3_4x": k4["R3"], "R4_4x": k4["R4"]})
    json.dump(res, open(out_p, "w"), indent=1, default=str)
    print(json.dumps({"labels": labels, "kill": kill,
                      "arms": {r: {b: f'{v[b]["k"]}/{v[b]["n"]}' for b in v} for r, v in res["arms"].items()},
                      "contrasts": {k: v and (v["kx"], v["ky"], v["n_pairs"], v["budget"], v["material"]) for k, v in contrasts.items()}},
                     indent=1))
    print("flags", flags)


if __name__ == "__main__":
    main(sys.argv[1:])
