"""THESEUS-43: do the 36/37 contrasts hold on a HELD-OUT harder variant of the task?

Prereg: roles/Theseus/prereg/2026-10-09_transfer_hard/PREREG.md.

Variant: cue recall V 8, k 16, sensor-only readout (task seed 0, 400/400 episodes); selection
in every run used V 4, k 8. Same 100-child samples as task_comp (sel_eval.sample). Gate rows
(task_comp.controls) re-scored at the variant. Checkpointed J_<run>.jsonl per run.

  python -m theseus.synth.transfer_eval --tag <tag> --runs r1,r2,... [--workers 4]
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

V, K = 8, 16


def J(g):
    return ts.task_J(g, V=V, k=K, seed=0, readout="ch0")["J"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    ctl = tcm.controls()
    with Pool(a.workers) as pool:
        cj = dict(zip(ctl, pool.map(J, list(ctl.values()))))
        json.dump(cj, open(f"{out}/CONTROLS_RUN.json", "w"), indent=1)
        res = {}
        for r in a.runs.split(","):
            s = dict(se.sample(r))
            js = tcm._stage(pool, f"{out}/J_{r}.jsonl", list(s.items()), J)
            res[r] = {"n": len(js), "solvers": sum(v >= tcm.SOLVER for v in js.values()),
                      "mean_J": sum(js.values()) / len(js)}
    json.dump({"V": V, "k": K, "controls": cj, "runs": res}, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
