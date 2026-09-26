"""D3 ruling (#648/#653): re-check P2 (F5 nuis_p .5) learnability at L2/L3 on the life-4x sets. Also runs F2 at the same
cells as a reference. Dev seeds 9_220_000-9_220_015, envelope v2 (4 workers, BELOW_NORMAL). Writes dev/p2_recheck.json."""
import json
import os
import time
from multiprocessing import Pool

import numpy as np

from .learn_probe import job, _init, HERE, LOG

OUT = os.path.join(HERE, "dev", "p2_recheck.json")
SEEDS = range(9_220_000, 9_220_016)

if __name__ == "__main__":
    jobs = [dict(family=f, level=l, seed=s, life_mult=4.0, noise=0.1) for f in ("F5_nuisance", "F2_latent")
            for l in ("L1", "L2", "L3") for s in SEEDS]
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG, "a") as f:
        f.write(json.dumps(dict(event="start", sweep="lm01_p2_recheck_v1", t=t(), workers=4, priority="BELOW_NORMAL",
                                seeds=f"{SEEDS.start}-{SEEDS.stop - 1}", n_jobs=len(jobs))) + "\n")
    t0 = time.time()
    with Pool(4, initializer=_init) as p:
        rows = p.map(job, jobs, chunksize=2)
    with open(OUT, "w") as f:
        json.dump(dict(sweep="lm01_p2_recheck_v1", nuis_p=0.5, life_mult=4.0, rows=rows), f)
    with open(LOG, "a") as f:
        f.write(json.dumps(dict(event="end", sweep="lm01_p2_recheck_v1", t=t(), workers=4, n_jobs=len(jobs),
                                wall_s=round(time.time() - t0, 1))) + "\n")
    for fam in ("F5_nuisance", "F2_latent"):
        for lv in ("L1", "L2", "L3"):
            rs = [r for r in rows if r["family"] == fam and r["level"] == lv and r["status"] == "OK"]
            b = np.array([r["best_minus_N1"] for r in rs])
            cnt = {}
            for r in rs:
                cnt[r["best_arm"]] = cnt.get(r["best_arm"], 0) + 1
            print(fam, lv, "n_unseen min/med", min(r["n_unseen"] for r in rs), int(np.median([r["n_unseen"] for r in rs])),
                  "| best-N1 med %.2f frac>.1 %.2f" % (np.median(b), (b > .1).mean()), "| best arms", cnt)
