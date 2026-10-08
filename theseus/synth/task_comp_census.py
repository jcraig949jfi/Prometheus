"""THESEUS-36b: census of the composition-necessary task on UNSELECTED arms (no task selection).

Prereg: roles/Theseus/prereg/2026-10-08_composition_task_census/PREREG.md.
Arms of a full run (D, R, P, B, C via task_replicate.load, 100 viable each, seed 20261008);
J = task_comp.J (V 4, k 8, sensor-only readout); SOLVER = J >= .6. Checkpointed.
"""
import argparse
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import task_comp as tcp  # noqa: E402
from . import task_replicate as tr  # noqa: E402


def main(argv=None):
    from scipy.stats import fisher_exact
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    jobs = tr.load(a.ref, np.random.default_rng(20261008), 100)
    grp = {i: g for g, i, _ in jobs}
    with Pool(a.workers) as pool:
        js = tcp._stage(pool, f"{out}/J.jsonl", [(i, g) for _, i, g in jobs], tcp.J)
    summ = {"ref": a.ref, "arms": {}}
    for arm in tr.ARMS:
        v = [js[i] for i in js if grp[i] == arm]
        summ["arms"][arm] = {"n": len(v), "solvers": sum(x >= tcp.SOLVER for x in v), "mean_J": float(np.mean(v))}
    A = summ["arms"]
    d = (A["D"]["solvers"], A["D"]["n"])
    one = (sum(A[k]["solvers"] for k in "PBC"), sum(A[k]["n"] for k in "PBC"))
    r = (A["R"]["solvers"], A["R"]["n"])
    f = lambda x, y: float(fisher_exact([[x[0], x[1] - x[0]], [y[0], y[1] - y[0]]], alternative="greater").pvalue)
    summ["D_gt_oneshot_p"], summ["D_gt_R_p"] = f(d, one), f(d, r)
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
