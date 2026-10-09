"""THESEUS-45: why do law-built solvers generalise? Delay vs alphabet, and the essential law.

Prereg: roles/Theseus/prereg/2026-10-09_generalise/PREREG.md.

Population: every selected-task solver (J >= .6 at V4 k8, from the 40/38 eval rows) of the
task0 and no-law runs of seeds 1-3. Per solver, sensor-only readout, task seed 0:
  J at V 4, k in DELAYS     (delay axis, alphabet fixed)
  J at V 8, k 8             (alphabet axis, delay fixed)
Checkpointed ROWS.jsonl.

  python -m theseus.synth.generalise --tag generalise_2026-10-09 [--workers 2]
"""

import argparse
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

from . import sel_eval as se  # noqa: E402
from . import task_comp as tcm  # noqa: E402
from . import task_system as ts  # noqa: E402

DELAYS = [4, 8, 12, 16, 20]
EVALS = [  # (stratum, arm, run, evaldir holding the selected-task J and KO rows)
    (1, "law", "v0_2t0_2026-10-08", "theseus/runs/comp_task_law_2026-10-08"),
    (1, "nolaw", "v0_2t0nl_2026-10-08", "theseus/runs/comp_task_law_2026-10-08"),
    (2, "law", "v0_2t0_s2_2026-10-08", "theseus/runs/comp_task_s2_law_2026-10-08"),
    (2, "nolaw", "v0_2t0nl_s2_2026-10-08", "theseus/runs/comp_task_s2_law_2026-10-08"),
    (3, "law", "v0_2t0_s3_2026-10-09", "theseus/runs/comp_task_s3_law_2026-10-09"),
    (3, "nolaw", "v0_2t0nl_s3_2026-10-09", "theseus/runs/comp_task_s3_law_2026-10-09"),
]


def job(g):
    return {"J_delay": [ts.task_J(g, V=4, k=k, seed=0, readout="ch0")["J"] for k in DELAYS],
            "J_V8k8": ts.task_J(g, V=8, k=8, seed=0, readout="ch0")["J"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    items, meta = [], {}
    for st, arm, run, d in EVALS:
        g = dict(se.sample(run))
        J = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{d}/J_{run}.jsonl", encoding="utf-8")}
        KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{d}/KO_{run}.jsonl", encoding="utf-8")}
        for i in sorted(J):
            if J[i] >= tcm.SOLVER:
                key = f"{run}:{i}"
                rules = g[i]["rules"]
                ess = KO[i]["essential"]
                law_ess = [x for x in ess if "law:" in str(rules[x].get("prov"))]
                meta[key] = {"stratum": st, "arm": arm, "run": run, "id": i, "J_sel": J[i],
                             "n_essential": len(ess), "law_essential": bool(law_ess),
                             "law_src_distinct": [len(set(rules[x]["src"])) for x in law_ess]}
                items.append((key, g[i]))
    with Pool(a.workers) as pool:
        done = tcm._stage(pool, f"{out}/ROWS.jsonl", items, job)
    rows = [{**meta[k], **done[k]} for k, _ in items]
    with open(f"{out}/TABLE.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(json.dumps({"n": len(rows), "by_arm": {a_: sum(r["arm"] == a_ for r in rows) for a_ in ("law", "nolaw")}}))


if __name__ == "__main__":
    main()
