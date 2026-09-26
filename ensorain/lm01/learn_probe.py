"""DEV learnability probe (#636 design question; gate rules #635/#636). DEV seeds only, envelope v2.

For every family x level and each (life_mult, noise) inside the SAME generator, does SOME arm (max over all arms)
beat N1 on the headline test set? The probe records which arm did it, so a family choice cannot silently favour one arm.
N1 = the better of two constants: the mean of all training values, and the mean of the last quarter.
Headline sets: never_seen (F1-F3), fresh_field (F4), ood_never_seen (F5).
Writes ensorain/lm01/dev/learnability.json. Logs start/end to DEV_SWEEP_LOG.jsonl."""
import json
import os
import sys
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "dev", "learnability.json")
LOG = os.path.join(HERE, "DEV_SWEEP_LOG.jsonl")
HEADLINE = {"F1_episodic": "never_seen", "F2_latent": "never_seen", "F3_switch": "never_seen",
            "F4_transfer": "fresh_field", "F5_nuisance": "ood_never_seen"}
LIFE, NOISES = (1.0, 2.0, 4.0), (0.1, 0.03)
SEEDS = range(9_200_000, 9_200_008)
WORKERS = 4


def _init():
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)


def job(a):
    import psutil
    if psutil.virtual_memory().available < 6 * 2 ** 30:
        return dict(a, status="STOP_RAM")
    from ensorain.wtp3.world3 import AC
    from .families import make_world
    from .smoke import arms_for
    fam, lv, sd, lm, nz = a["family"], a["level"], a["seed"], a["life_mult"], a["noise"]
    w = make_world(fam, lv, sd, life_mult=lm, noise=nz)
    T, truth = w["tests"][HEADLINE[fam]]
    ys = np.concatenate([y for _, y, _ in w["train"]])
    n1 = max(AC(np.full(len(T), ys.mean()), truth, 1.0), AC(np.full(len(T), ys[-len(ys) // 4:].mean()), truth, 1.0))
    acs = {}
    for arm in arms_for(w["dims"]):
        for A, y, _ in w["train"]:
            for i in range(0, len(y), 50):
                arm.observe(A[i:i + 50], y[i:i + 50])
        acs[arm.name.split("-rand")[0] if arm.name.startswith("M-rand") else arm.name] = AC(arm.predict(T), truth, 1.0)
    best = max(acs, key=acs.get)
    return dict(a, status="OK", gen=w["gen"], rank=w["rank"], coverage=w["coverage"], n_unseen=w["n_unseen"], n_test=int(len(T)), N1=n1, AC=acs, best_arm=best,
                best_minus_N1=acs[best] - n1)


def _log(ev, **kw):
    with open(LOG, "a") as f:
        f.write(json.dumps(dict(event=ev, sweep="lm01_learnability_probe_v1", t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                workers=WORKERS, priority="BELOW_NORMAL", seeds=f"{SEEDS.start}-{SEEDS.stop - 1}", **kw)) + "\n")


def main():
    from .families import FAMILIES, LEVELS
    jobs = [dict(family=f, level=l, seed=s, life_mult=lm, noise=nz)
            for f in FAMILIES for l in LEVELS for lm in LIFE for nz in NOISES for s in SEEDS]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    _log("start", n_jobs=len(jobs))
    t0 = time.time()
    with Pool(WORKERS, initializer=_init) as p:
        rows = p.map(job, jobs, chunksize=4)
    stops = sum(r["status"] != "OK" for r in rows)
    with open(OUT, "w") as f:
        json.dump(dict(sweep="lm01_learnability_probe_v1", seeds=[SEEDS.start, SEEDS.stop - 1], life=LIFE, noise=NOISES,
                       headline=HEADLINE, rows=rows), f)
    _log("end", n_jobs=len(jobs), n_stop=stops, wall_s=round(time.time() - t0, 1))
    print("done", len(rows), "stops", stops, "wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    sys.exit(main())
