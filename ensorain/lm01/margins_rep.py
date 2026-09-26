"""D10(b) HEADLINE REPLICATE sweep (#715 proposal; accepted by Aporia #717, pending Cyclops/operator). Dev margin seeds
9_500_000-015, the same worlds as lm01_margins_v1.

Per world: the RANDOM reservoir rungs (rank 3) and converged L-R, run with learner/eviction seed 1 and scored on a
bootstrap resample of the same headline test cells. Paired with replicate a (seed 0, the full test set) from
lm01_margins_v1, this gives the headline curve's OWN replicate noise. It changes no rule. Rows go to
dev/margins_rep/<stratum>.jsonl; start/end are logged."""
import json
import os
import sys
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np

from .margins import SEEDS, RANK, _feed, _ac_cells, _AC, _rungs, _iters, jobs_from_frozen, HERE, LOG

OUTDIR = os.path.join(HERE, "dev", "margins_rep")


def job(a):
    import psutil
    if psutil.virtual_memory().available < 6 * 2 ** 30:
        return dict(a, status="STOP_RAM")
    from .arms import BufferALS, LosslessR
    from .families import make_world
    from .select_arms import HEADLINE_SEL
    t0 = time.time()
    f, l, g, sd = a["family"], a["level"], a["gen"], a["seed"]
    w = make_world(f, l, sd, gen=g)
    T, truth = w["tests"][HEADLINE_SEL[f]]
    out = {k: a[k] for k in ("family", "level", "gen", "seed")}
    if len(T) < 8:
        return dict(out, status="TOO_FEW_TEST")
    boot = np.random.default_rng(sd + 991).integers(0, len(T), len(T))
    n = sum(len(s[1]) for s in w["train"])
    lad = {}
    for rung, B in _rungs(w["dims"], n).items():
        arm = _feed(BufferALS(w["dims"], RANK, max(1, B), evict="random", seed=1), w["train"])
        lad[f"random|{rung}"] = dict(B=int(B), AC_b=_AC(_ac_cells(arm.predict(T[boot]), truth[boot])), iters=_iters(arm))
    lr = _feed(LosslessR(w["dims"], rank=RANK, seed=1), w["train"])
    lad["L-R|full"] = dict(B=n, AC_b=_AC(_ac_cells(lr.predict(T[boot]), truth[boot])), iters=_iters(lr))
    return dict(out, status="OK", ladder_b=lad, wall=time.time() - t0)


def main(workers=8):
    from .learn_probe import _init
    J = [{k: j[k] for k in ("family", "level", "gen", "seed")} for j in jobs_from_frozen()]
    J.sort(key=lambda j: {"L3": 0, "L2": 1, "L1": 2}[j["level"]])
    os.makedirs(OUTDIR, exist_ok=True)
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="start", sweep="lm01_margins_rep_v1", t=t(), workers=workers,
                                 priority="BELOW_NORMAL", seeds=f"{SEEDS.start}-{SEEDS.stop - 1}", n_jobs=len(J))) + "\n")
    t0, n_stop = time.time(), 0
    with Pool(workers, initializer=_init) as p:
        for r in p.imap_unordered(job, J, chunksize=1):
            n_stop += r["status"] == "STOP_RAM"
            with open(os.path.join(OUTDIR, f"{r['family']}__{r['level']}__{r['gen']}.jsonl"), "a") as fh:
                fh.write(json.dumps(r) + "\n")
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="end", sweep="lm01_margins_rep_v1", t=t(), workers=workers, n_jobs=len(J),
                                 n_stop_ram=n_stop, wall_s=round(time.time() - t0, 1))) + "\n")
    print("done", len(J), "stop_ram", n_stop)


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 8))
