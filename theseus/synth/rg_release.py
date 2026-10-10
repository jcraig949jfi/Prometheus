"""THESEUS-51 S1: J at V8 k8 (sensor readout, task seed 0) for every selected-task solver of a run.

  python -m theseus.synth.rg_release --evaldir <dir> --run <run> --out <dir> [--workers 2]
"""
import argparse
import json
import os
from multiprocessing import Pool

from . import release_swap as rs
from . import sel_eval as se
from . import task_comp as tcm


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaldir", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    g = dict(se.sample(a.run))
    J = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/J_{a.run}.jsonl", encoding="utf-8")}
    items = [(i, g[i]) for i in sorted(J) if J[i] >= tcm.SOLVER]
    with Pool(a.workers) as pool:
        done = tcm._stage(pool, f"{a.out}/V8_{a.run}.jsonl", items, rs.J8)
    print(json.dumps({"run": a.run, "solvers": len(items), "release_ge_.6": sum(v >= 0.6 for v in done.values())}))


if __name__ == "__main__":
    main()
