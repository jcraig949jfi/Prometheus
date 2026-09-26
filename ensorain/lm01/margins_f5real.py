"""Dev re-run of the margin sweep for F5 ONLY under the repaired rung scale "real_cells" (operator ruling 2026-09-26 item
3). Same margin seeds and frozen arms as lm01_margins_v1. Rows go to dev/margins_f5real/. It changes no rule; the
all_cells rows stay as the record of the old interpretation."""
import json
import os
import sys
import time
from multiprocessing import Pool

from .margins import job, jobs_from_frozen, HERE, LOG, SEEDS

OUTDIR = os.path.join(HERE, "dev", "margins_f5real")


def main(workers=8):
    from .learn_probe import _init
    J = [dict(j, scale="real_cells") for j in jobs_from_frozen() if j["family"] == "F5_nuisance"]
    J.sort(key=lambda j: {"L3": 0, "L2": 1, "L1": 2}[j["level"]])
    os.makedirs(OUTDIR, exist_ok=True)
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="start", sweep="lm01_margins_f5real_v1", t=t(), workers=workers,
                                 priority="BELOW_NORMAL", seeds=f"{SEEDS.start}-{SEEDS.stop - 1}", n_jobs=len(J))) + "\n")
    t0, n_stop = time.time(), 0
    with Pool(workers, initializer=_init) as p:
        for r in p.imap_unordered(job, J, chunksize=1):
            n_stop += r["status"] == "STOP_RAM"
            with open(os.path.join(OUTDIR, f"{r['family']}__{r['level']}__{r['gen']}.jsonl"), "a") as fh:
                fh.write(json.dumps(r) + "\n")
    with open(LOG, "a") as fh:
        fh.write(json.dumps(dict(event="end", sweep="lm01_margins_f5real_v1", t=t(), workers=workers, n_jobs=len(J),
                                 n_stop_ram=n_stop, wall_s=round(time.time() - t0, 1))) + "\n")


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 8))
