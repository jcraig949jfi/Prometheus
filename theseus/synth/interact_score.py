"""THESEUS-47: arm x redundancy interaction on generalisation, fresh seed.

Prereg: roles/Theseus/prereg/2026-10-09_interaction/PREREG.md.

Step 1 (scoring): every selected-task solver (J >= .6, from the task_comp law eval) of the
--law and --nolaw runs is scored with generalise.job (J at V4 k4..20, V8 k8); checkpointed.
Step 2 (test): REDUNDANT = n_essential 0 vs ONE-POINT >= 1. Per arm, RD (redundant - one-point)
in the share solving V8 k8 (primary) and V4 k20 (secondary), Wald SE; interaction
z = (RD_law - RD_nolaw) / sqrt(se_law^2 + se_nolaw^2), one-sided.

  python -m theseus.synth.interact_score --tag <tag> --evaldir <dir> --law <run> --nolaw <run>
"""

import argparse
import json
import math
import os
from multiprocessing import Pool

from scipy.stats import fisher_exact, norm

from . import generalise as ge
from . import sel_eval as se
from . import task_comp as tcm


def rd(rows, pred):
    R = [r for r in rows if r["n_essential"] == 0]
    O = [r for r in rows if r["n_essential"] >= 1]
    a, n1, c, n2 = sum(pred(r) for r in R), len(R), sum(pred(r) for r in O), len(O)
    p1, p2 = a / n1, c / n2
    se_ = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return {"redundant": [a, n1], "one_point": [c, n2], "rd": p1 - p2, "se": se_,
            "fisher_one_sided_p": float(fisher_exact([[a, n1 - a], [c, n2 - c]], alternative="greater").pvalue)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--evaldir", required=True)
    ap.add_argument("--law", required=True)
    ap.add_argument("--nolaw", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    items, meta = [], {}
    for arm, run in (("law", a.law), ("nolaw", a.nolaw)):
        g = dict(se.sample(run))
        J = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/J_{run}.jsonl", encoding="utf-8")}
        KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/KO_{run}.jsonl", encoding="utf-8")}
        for i in sorted(J):
            if J[i] >= tcm.SOLVER:
                k = f"{run}:{i}"
                meta[k] = {"arm": arm, "run": run, "id": i, "J_sel": J[i], "n_essential": KO[i]["n_essential"]}
                items.append((k, g[i]))
    with Pool(a.workers) as pool:
        done = tcm._stage(pool, f"{out}/ROWS.jsonl", items, ge.job)
    rows = [{**meta[k], **done[k]} for k, _ in items]
    res = {}
    for name, pred in (("V8k8", lambda r: r["J_V8k8"] >= 0.6), ("V4k20", lambda r: r["J_delay"][4] >= 0.6)):
        L = rd([r for r in rows if r["arm"] == "law"], pred)
        N = rd([r for r in rows if r["arm"] == "nolaw"], pred)
        z = (L["rd"] - N["rd"]) / math.sqrt(L["se"] ** 2 + N["se"] ** 2)
        res[name] = {"law": L, "nolaw": N, "interaction_z": z, "interaction_p_one_sided": float(norm.sf(z))}
    arm_tabs = {}
    for name, pred in (("V8k8", lambda r: r["J_V8k8"] >= 0.6), ("V4k20", lambda r: r["J_delay"][4] >= 0.6)):
        L = [r for r in rows if r["arm"] == "law"]
        N = [r for r in rows if r["arm"] == "nolaw"]
        a1, c1 = sum(pred(r) for r in L), sum(pred(r) for r in N)
        arm_tabs[name] = {"law": [a1, len(L)], "nolaw": [c1, len(N)],
                          "fisher_one_sided_p": float(fisher_exact([[a1, len(L) - a1], [c1, len(N) - c1]], alternative="greater").pvalue)}
    summ = {"n": len(rows), "interaction": res, "arm_contrast": arm_tabs}
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    with open(f"{out}/TABLE.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
