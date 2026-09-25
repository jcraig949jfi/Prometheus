"""Dev-seed one-at-a-time sensitivity from the competent point (sets the
Round-3 local ranges; PREREG_D3 records the criterion)."""
import collections
import json
import numpy as np
from .core import run
from .round2 import COMPETENT

LEVELS = dict(lam=[7.5, 15, 60, 120], sweeps=[3, 5, 15, 20], scratch=[32, 64, 256, 512], cap=[128, 256, 384],
              replay_frac=[0.05, 0.15, 0.3], dream_ratio=[0.1, 0.3, 1.0], surprise_alpha=[0.1, 0.3, 1.0],
              disturb=[0.01, 0.03, 0.1], forget=[0.01, 0.03, 0.1], err_frac=[0.05, 0.1, 0.2],
              p_restruct=[0.1, 0.3, 1.0], drift=[0.1, 0.3, 0.6], noise=[0.05, 0.2, 0.3], kappa_mult=[0.25, 4.0],
              start=["random"])

if __name__ == "__main__":
    jobs, life = [], 0
    for k, vals in [("base", [None])] + list(LEVELS.items()):
        for v in vals:
            for i in range(8):
                d = dict(COMPETENT)
                if k != "base":
                    d[k] = v
                jobs.append(dict(life=life, inst=2500 + i, seed=950000 + life, dials=d, knob=k, val=v))
                life += 1
    out = "ensorain/runs/d3_sensitivity.jsonl"
    open(out, "w").close()
    run(jobs, out)
    rows = [json.loads(l) for l in open(out)]
    agg = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "OK":
            agg[(r["knob"], str(r["val"]))].append(r["r2_ho"])
    for k, v in agg.items():
        a = np.array(v)
        print(f"{k[0]:15s} {k[1]:8s} median R2 {np.median(a):7.2f}  learned {np.mean(a >= .5):.2f}  diverged {np.mean(a <= -1):.2f}")
