"""Timed measurement: is a numba port of the lineage loop needed? (C-013-T010; operator ruling s3 bullet 2.)

    python -m rso.reach.timing [--proposals N] [--out rso/reach/TIMING.json]

Development measurement on TOY settings only: short budgets, lineage indices outside the frozen set (TOY < 0),
and nothing about whether any lineage reaches the target is recorded or printed. It measures, per arm, wall seconds
per proposal of the pure-Python reference (run_ladder via arms.run_reach_lineage impl='py') against the cost of the
training evaluation alone, and the archive's cell count at the end of the toy budget (the X2/X3 parent draw is O(cells)
per proposal in the reference, so its cost grows with the archive).

Decision rule (written before the measurement): project the frozen design's WORST CASE (every lineage runs the full
budget) at the measured per-proposal cost of the Python reference, with the archive arms' overhead extrapolated
linearly in cells to the cell count implied by the measured growth. PORT if that projection exceeds 75% of the
demonstration's 4 CPU core-hour cap (the remainder is kept for certification, controls and the descriptor test);
otherwise do not port.
"""
import argparse
import json
import platform
import time
from datetime import datetime, timezone

import numpy as np

from rso.reach import arms

TOY = -100                  # development lineage (knock-out index LINEAGE0 - 100); the frozen set is lineage >= 0
CAP_CORE_H = 4.0
PORT_FRACTION = 0.75


def time_eval(n=5000):
    rng = np.random.default_rng(1)
    progs = [arms.mutate(arms.TARGET, 1, 1, 1, i) for i in range(64)]
    progs += [rng.integers(0, 64, size=(8, 4)).astype(np.int64) for _ in range(64)]
    arms.train_eval(progs[0])
    t = time.perf_counter()
    for i in range(n):
        arms.train_eval(progs[i % len(progs)])
    return (time.perf_counter() - t) / n


def time_arm(arm, d, proposals, impl="py"):
    t = time.perf_counter()
    r = arms.run_reach_lineage(arm, d, TOY, budget=proposals, impl=impl, geno_buckets=64)
    dt = time.perf_counter() - t
    n = r["evals"] if r["evals"] > 0 else proposals
    return dt / max(1, n), r["cells"], n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposals", type=int, default=6000)
    ap.add_argument("--out", default=None)
    ap.add_argument("--impl", default="py")
    ap.add_argument("--growth", action="store_true")
    a = ap.parse_args()
    t_eval = time_eval()
    rows = {}
    for arm in arms.ARMS:
        for d in (3, 8):
            spp, cells, n = time_arm(arm, d, a.proposals, a.impl)
            rows["%s d=%d" % (arm, d)] = dict(sec_per_proposal=spp, overhead_per_proposal=spp - t_eval,
                                              cells_at_end=cells, proposals_timed=n)
            print("%-14s d=%d  %.1f us/proposal (eval %.1f us)  cells %d" % (arm, d, spp * 1e6, t_eval * 1e6, cells))
    growth = {}
    if a.growth:
        for arm in ("X2", "X3"):
            for b in (5000, 20000, 40000):
                t = time.perf_counter()
                r = arms.run_reach_lineage(arm, 8, TOY + 1, budget=b, impl=a.impl)
                n = r["evals"] if r["evals"] > 0 else b
                growth["%s d=8 budget=%d" % (arm, b)] = dict(cells=r["cells"], distinct_genomes=r["distinct_genomes"],
                                                             sec_per_proposal=(time.perf_counter() - t) / max(1, n))
                print("growth %s budget %d: cells %d, %.1f us/proposal" % (arm, b, r["cells"],
                                                                          growth["%s d=8 budget=%d" % (arm, b)]["sec_per_proposal"] * 1e6))
    out = dict(growth=growth, what="C-013-T010 numba-port timing (toy settings; no outcome recorded)", impl=a.impl,
               host=platform.node(), python=platform.python_version(),
               written_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               eval_sec=t_eval, proposals_per_arm=a.proposals, rows=rows)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.write("\n")
    return out


if __name__ == "__main__":
    main()
