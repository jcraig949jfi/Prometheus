"""Learner-engineering scan on DEV seeds for the positive control only
(PREREG_E1 s8). python -m ensorain.e1.round_scan <tag> <json list of TT_LATENT cfgs> [cap]"""
import json, sys, collections
import numpy as np
from .arms import run_jobs


def main():
    tag, cfgs = sys.argv[1], json.loads(sys.argv[2])
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 192
    jobs = [dict(arm="TT_LATENT", cap=cap, lam=0.0, inst_seed=i, org_seed=0, cfg=c, ci=ci, econ={"energy0": 1e9})
            for ci, c in enumerate(cfgs) for i in range(100, 106)]
    rows = run_jobs(jobs, f"ensorain/runs/e1_dev_{tag}.jsonl")
    agg = collections.defaultdict(list)
    for r in rows:
        agg[r["ci"]].append(r)
    for ci in sorted(agg):
        v = agg[ci]
        print(cfgs[ci], "r2ho", round(float(np.median([r["r2_ho"] for r in v])), 3),
              "r2seen", round(float(np.median([r["r2_seen"] for r in v])), 3),
              "L2", round(float(np.mean([r["ok_L2"] / max(r["n_L2"], 1) for r in v])), 3),
              "comp$", round(float(np.mean([r["comp_energy"] for r in v])), 1))


if __name__ == "__main__":
    main()
