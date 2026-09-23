"""TT_TUNED grid on dev seeds (0-999), observed order, in-life harvest.
Writes ensorain/e0/tt_tuned.json (the frozen TT_TUNED constants)."""
import json, itertools, collections
import numpy as np
from .arms import run_jobs

ECON = dict(theta=0.0, energy0=100, metabolism=0.8, horizon=12000)


def main():
    grid = []
    for lr, init, mode in [(0.1, 0.5, "joint"), (0.3, 0.8, "joint"), (0.3, 0.5, "joint"), (0.05, 0.8, "sgd"), (0.1, 0.8, "sgd")]:
        for buf, rep in [(0.0, 0), (0.5, 2)]:
            for eps in (0.1, 0.3):
                grid.append(dict(lr=lr, init_scale=init, mode=mode, buf_frac=buf, replay=rep, epsilon=eps))
    jobs = []
    for gi, g in enumerate(grid):
        for cap in (96, 168):
            for i in range(20, 26):
                jobs.append(dict(arm="TT_TUNED", cap=cap, lam=0.0, class_seed=0, inst_seed=i, org_seed=0, econ=ECON, tuned=g, gi=gi))
    rows = run_jobs(jobs, "ensorain/runs/dev_tune.jsonl")
    agg = collections.defaultdict(list)
    for r in rows:
        agg[r["gi"]].append(r["harvest"] if r["status"] == "OK" else 0.0)
    ranked = sorted(agg, key=lambda k: -np.mean(agg[k]))
    for k in ranked:
        print(k, grid[k], round(float(np.mean(agg[k])), 1))
    best = grid[ranked[0]]
    with open("ensorain/e0/tt_tuned.json", "w") as f:
        json.dump(best, f, indent=1)
    print("FROZEN", best)


if __name__ == "__main__":
    main()
