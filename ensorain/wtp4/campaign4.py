"""WTP-04 Habitable Islands runner (PREREG_WTP04 s6). Jobs = family x grid point x seed.
Envelope (ubu006): <= 3 workers, nice 10, stop (no new jobs) when available RAM < 3 GB.
Rows stream to ensorain/runs/wtp04/<name>.jsonl (append; a restart skips finished keys)."""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import psutil

from .axes import grid
from .families import families
from .habit import unit

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp04")
MIN_FREE_GB = 3.0


def jobs(seeds, fams=None, axes=None):
    F = [f for f in families() if fams is None or f["fid"] in fams]
    G = [p for p in grid() if axes is None or p[0] in axes or p[0] == "native"]
    return [(f["fid"], ax, lab, s) for f in F for (ax, lab, _) in G for s in seeds]


def _job(a):
    fid, ax, lab, seed = a
    os.nice(10) if os.getpid() != os.getppid() and os.nice(0) < 10 else None
    f = next(x for x in families() if x["fid"] == fid)
    tf = next(t for (x, l, t) in grid() if x == ax and l == lab)
    u = unit(tf(f["g"]), seed)
    return dict(fid=fid, axis=ax, level=lab, **u)


def run(name, seeds, workers=3, fams=None, axes=None):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{name}.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done.add((r["fid"], r["axis"], r["level"], r["seed"]))
    todo = [j for j in jobs(seeds, fams, axes) if j not in done]
    print(f"{name}: {len(todo)} jobs ({len(done)} already done), {workers} workers", flush=True)
    t0 = time.time()
    with mp.get_context("spawn").Pool(workers, maxtasksperchild=20) as pool, open(path, "a") as fh:
        it = iter(todo)
        pending = []
        n = 0
        while True:
            while len(pending) < workers * 2:
                if psutil.virtual_memory().available / 2 ** 30 < MIN_FREE_GB:
                    break
                j = next(it, None)
                if j is None:
                    break
                pending.append(pool.apply_async(_job, (j,)))
            if not pending:
                break
            r = pending.pop(0).get()
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            n += 1
            if n % 20 == 0:
                print(f"  {n}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
    print(f"{name}: done {n} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--seeds", required=True, help="comma list")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--fams")
    ap.add_argument("--axes")
    a = ap.parse_args()
    run(a.name, [int(s) for s in a.seeds.split(",")], a.workers,
        a.fams.split(",") if a.fams else None, a.axes.split(",") if a.axes else None)
    sys.exit(0)
