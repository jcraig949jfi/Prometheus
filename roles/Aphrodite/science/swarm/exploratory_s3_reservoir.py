"""EXPLORATORY, POST-HOC (not preregistered; decided after reading S3's persistence rows).

The preregistered persistence arm drove exploiters to fixation (x = 1.000
in every run) with one-way mutation, so no honest variant existed after
the fix and neither model nor simulation could ever purge the exploit,
whatever its cost. Question: does an HONEST RESERVOIR restore purging on
the schedule the extended model predicts?

RESERVOIR at rate r: after selection and mutation, each exploiter returns
to an honest variant w.p. r. At this level of abstraction back-mutation
and re-seeding from an archive of honest ancestors (DGM-style) are the
same operation, so they are one arm.
Model (extended recursion): x_s = x(1-c)/(1-cx); x' = (1 - r)(x_s + mu(1 - x_s)).
NONE (r = 0) repeats the preregistered arm for reference.
"""
from __future__ import annotations

import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sims  # noqa: E402

MU, M, PRE, POST, RUNS = 0.005, 200, 200, 300, 100
COSTS, RATES = (0.02, 0.1), (0.005, 0.02)


def model_half(x0, c, mech, r):
    x = x0
    for gen in range(1, POST + 1):
        xs = x * (1 - c) / (1 - c * x)
        x = (1 - r) * (xs + MU * (1 - xs))
        if x <= x0 / 2:
            return gen, x
    return None, x


def run(args):
    mech, c, r = args
    rng = random.Random(7919 * int(round(c * 1000)) + 104729 * int(round(r * 1000)) + 13)
    out = []
    for _ in range(RUNS):
        e = 0
        for _ in range(PRE):
            e = sims.s3_generation(M, e, 0.5, 0.0, MU, 0.0, rng)
        x0 = e / M
        half = None
        for gen in range(1, POST + 1):
            e = sims.s3_generation(M, e, 0.0, 0.0, MU, c, rng)
            if r and e:
                e -= rng.binomialvariate(e, r)
            if half is None and e / M <= x0 / 2:
                half = gen
        out.append({"x_at_fix": x0, "x_end": e / M, "half_gen": half})
    return {"mech": mech, "c": c, "r": r, "runs": out}


if __name__ == "__main__":
    jobs = [("NONE", c, 0.0) for c in COSTS] + [("RESERVOIR", c, r) for c in COSTS for r in RATES]
    with Pool(7) as p:
        res = p.map(run, jobs)
    L = HERE / "ledgers"
    with open(L / "x_s3_reservoir.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for r in res:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    import statistics as st
    for r in res:
        x0 = st.fmean(x["x_at_fix"] for x in r["runs"])
        mh, _ = model_half(x0, r["c"], r["mech"], r["r"])
        halves = [x["half_gen"] for x in r["runs"] if x["half_gen"] is not None]
        print(r["mech"], "c", r["c"], "r", r["r"], "x0 %.3f" % x0, "model_half", mh,
              "sim_halved %d/%d" % (len(halves), RUNS), "sim_median_half", st.median(halves) if halves else None,
              "end_mean %.3f" % st.fmean(x["x_end"] for x in r["runs"]))
