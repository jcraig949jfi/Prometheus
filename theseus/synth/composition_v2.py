"""THESEUS-30b: composition detector v2 (trace-based inertness) on the committed arms.

Prereg: roles/Theseus/prereg/2026-10-08_composition_v2/PREREG.md.

A part P (a contiguous rule block) is INERT iff its state trajectory is bitwise identical
to EMPTY's (same genome, one no-op rule) at IC seeds 0 and 1 (T = 128). A genome is a
COMPOSITION iff it is not inert as a whole and some split point s gives A = rules[:s]
and B = rules[s:] both inert. Unlike the 23b detector, no fingerprint is used, so
structural interventions cannot make an inert part look active (THESEUS-30a).

The run includes its own validity gate: the 160 THESEUS-30a control genomes
(planted / neg_active / neg_recall / neg_inert) are re-scored first.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import composition as cp  # noqa: E402
from . import substrate as sb  # noqa: E402

SEEDS = (0, 1)


def _traces(g):
    return [sb.run(g, seed=s)[0] for s in SEEDS]


def _same(ta, tb):
    return all(np.array_equal(a, b) for a, b in zip(ta, tb))


def job(g):
    t0 = time.process_time()
    rules = g["rules"]
    te = _traces(cp._with_rules(g, []))
    whole_inert = _same(_traces(g), te)
    inert_prefix = []
    inert_suffix = []
    for s in range(1, len(rules)):
        inert_prefix.append(_same(_traces(cp._with_rules(g, rules[:s])), te))
        inert_suffix.append(_same(_traces(cp._with_rules(g, rules[s:])), te))
    splits = [s + 1 for s in range(len(rules) - 1) if inert_prefix[s] and inert_suffix[s]]
    return {"n_rules": len(rules), "whole_inert": whole_inert, "composition": (not whole_inert) and bool(splits),
            "composition_splits": splits, "n_inert_prefix": int(sum(inert_prefix)),
            "n_inert_suffix": int(sum(inert_suffix)),
            "inert_rules": [i for i, r in enumerate(rules) if _same(_traces(cp._with_rules(g, [r])), te)],
            "cpu_s": time.process_time() - t0}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n", type=int, default=120)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    ctl = [json.loads(l) for l in open("theseus/runs/comp_control_2026-10-08/ROWS.jsonl", encoding="utf-8")]
    arms = cp.load_arms(np.random.default_rng(20261008), a.n)  # identical sample to 23b
    jobs = [("CTL:" + r["class"], r["id"], r["genome"]) for r in ctl] + \
           [(arm, r["id"], r["genome"]) for arm in cp.ARMS for r in arms[arm]]
    t0 = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(job, [g for _, _, g in jobs])
    rows = [{"arm": arm, "id": i, **x} for (arm, i, _), x in zip(jobs, res)]
    summ = {"wall_s": round(time.time() - t0, 1), "cpu_s": round(sum(x["cpu_s"] for x in res), 1), "groups": {}}
    for grp in sorted({r["arm"] for r in rows}):
        rs = [r for r in rows if r["arm"] == grp]
        summ["groups"][grp] = {"n": len(rs), "compositions": sum(r["composition"] for r in rs),
                               "whole_inert": sum(r["whole_inert"] for r in rs),
                               "with_any_inert_rule": sum(bool(r["inert_rules"]) for r in rs),
                               "median_inert_rules": float(np.median([len(r["inert_rules"]) for r in rs]))}
    with open(f"{out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
