#!/usr/bin/env python3
"""POST-HOC (not preregistered) confirmation. Written after results.json showed the
pilot-selected MOD delta (1e-3) freezes early while 3e-4 reached the ground state.
Fresh instances (seeds 6..10), delta fixed from the main-run grid: MOD 3e-4, SK 1e-4.
Same code paths and analysis as toy.py main. Output: posthoc.json."""
import json, os, time
from multiprocessing import Pool
import toy

toy.SEEDS = (6, 7, 8, 9, 10)
pil = {"MOD": {"primary_delta": 3e-4}, "SK": {"primary_delta": 1e-4}}
toy.DELTAS = (1e-4, 3e-4)   # NI grid limited to the two slow rates
if __name__ == "__main__":
    t0 = time.time()
    jobs = []
    for f in toy.FAMILIES:
        dp = pil[f]["primary_delta"]
        for sd in toy.SEEDS:
            for d in toy.DELTAS:
                jobs.append({"fam": f, "seed": sd, "cond": "NI", "delta": d, "record": d == dp})
            jobs.append({"fam": f, "seed": sd, "cond": "noyield", "delta": 0.0})
            for c in ("anti", "perm", "noreset", "nodiss"):
                jobs.append({"fam": f, "seed": sd, "cond": c, "delta": dp})
            jobs.append({"fam": f, "seed": sd, "cond": "fast", "delta": toy.DELTA_FAST})
    with Pool(4) as p:
        out = p.map(toy.run_job, jobs, chunksize=1)
    recs = {(r["fam"], r["seed"]): r.pop("record") for r in out if "record" in r}
    jobs2 = []
    for f in toy.FAMILIES:
        for i, sd in enumerate(toy.SEEDS):
            other = toy.SEEDS[(i + 1) % len(toy.SEEDS)]
            jobs2.append({"fam": f, "seed": sd, "cond": "shuf_oth", "delta": pil[f]["primary_delta"],
                          "foreign": recs[(f, other)]})
    with Pool(4) as p:
        out += p.map(toy.run_job, jobs2, chunksize=1)
    print("wall %.0fs" % (time.time() - t0))
    here = os.path.dirname(os.path.abspath(__file__))
    toy.analyse(out, pil)
    os.replace(os.path.join(here, "results.json"), os.path.join(here, "posthoc.json"))
