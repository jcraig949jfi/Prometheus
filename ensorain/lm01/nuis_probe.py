"""DEV probe: F5 learnability vs nuisance reliability nuis_p (a proposed family change, pending a steward ruling).
Envelope v2, dev seeds 9_210_000-9_210_007. Writes dev/nuis_probe.json; logs to DEV_SWEEP_LOG.jsonl."""
import json
import os
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np

from .learn_probe import _init, HERE, LOG

OUT = os.path.join(HERE, "dev", "nuis_probe.json")
SEEDS = range(9_210_000, 9_210_008)


def job(a):
    from ensorain.wtp3.world3 import AC
    from .families import make_world
    from .smoke import arms_for
    w = make_world("F5_nuisance", a["level"], a["seed"], life_mult=a["life_mult"], nuis_p=a["nuis_p"])
    T, truth = w["tests"]["ood_never_seen"]
    ys = np.concatenate([y for _, y, _ in w["train"]])
    n1 = max(AC(np.full(len(T), ys.mean()), truth, 1.0), AC(np.full(len(T), ys[-len(ys) // 4:].mean()), truth, 1.0))
    acs = {}
    for arm in arms_for(w["dims"]):
        for A, y, _ in w["train"]:
            for i in range(0, len(y), 50):
                arm.observe(A[i:i + 50], y[i:i + 50])
        acs[arm.name if not arm.name.startswith("M-") else "M"] = AC(arm.predict(T), truth, 1.0)
    return dict(a, N1=n1, AC=acs)


if __name__ == "__main__":
    jobs = [dict(level=l, seed=s, life_mult=lm, nuis_p=p) for l in ("L1", "L2", "L3") for lm in (1.0, 4.0)
            for p in (1.0, 0.75, 0.5, 0.25) for s in SEEDS]
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG, "a") as f:
        f.write(json.dumps(dict(event="start", sweep="lm01_nuis_probe_v1", t=t(), workers=4, priority="BELOW_NORMAL",
                                seeds=f"{SEEDS.start}-{SEEDS.stop - 1}", n_jobs=len(jobs))) + "\n")
    t0 = time.time()
    with Pool(4, initializer=_init) as p:
        rows = p.map(job, jobs, chunksize=4)
    with open(OUT, "w") as f:
        json.dump(dict(sweep="lm01_nuis_probe_v1", rows=rows), f)
    with open(LOG, "a") as f:
        f.write(json.dumps(dict(event="end", sweep="lm01_nuis_probe_v1", t=t(), workers=4, n_jobs=len(jobs),
                                wall_s=round(time.time() - t0, 1))) + "\n")
    import collections
    g = collections.defaultdict(list)
    for r in rows:
        g[(r["level"], r["life_mult"], r["nuis_p"])].append(r)
    for k in sorted(g):
        rs = g[k]
        best = np.array([max(r["AC"].values()) - r["N1"] for r in rs])
        med = {a: round(float(np.median([r["AC"][a] - r["N1"] for r in rs])), 2) for a in rs[0]["AC"]}
        print(k, "best-N1 med", round(float(np.median(best)), 2), "frac>.1", round(float((best > .1).mean()), 2), med)
