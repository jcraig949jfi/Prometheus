"""THESEUS-31c evaluation: task J of DEEP+VERY_DEEP children, compared between two runs.

J = task_system.task_J at V 4, k 4, 400/400 episodes, seed 0 (the 31a setting), for up to
100 viable D children per run (seed 20261008). One-sided Mann-Whitney, first run > second.
"""
import argparse
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import task_system as ts  # noqa: E402


def _j(g):
    return ts.task_J(g, V=4, k=4, seed=0)["J"]


def sample(tag, n=100):
    rows = []
    for l in open(f"theseus/entities/{tag}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("viable") and e.get("kind") == "mechanism" and e.get("lane") in ("DEEP", "VERY_DEEP"):
            rows.append((e["id"], e["executableRepresentation"]))
    rng = np.random.default_rng(20261008)
    idx = sorted(rng.choice(len(rows), size=min(n, len(rows)), replace=False))
    return [rows[i] for i in idx]


def main(argv=None):
    from scipy.stats import mannwhitneyu
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    res = {}
    with Pool(a.workers) as pool:
        for t in (a.a, a.b):
            s = sample(t)
            js = pool.map(_j, [g for _, g in s])
            res[t] = {"ids": [i for i, _ in s], "J": js}
    ja, jb = np.array(res[a.a]["J"]), np.array(res[a.b]["J"])
    summ = {a.a: {"n": len(ja), "mean_J": float(ja.mean()), "median_J": float(np.median(ja))},
            a.b: {"n": len(jb), "mean_J": float(jb.mean()), "median_J": float(np.median(jb))},
            "mannwhitney_a_gt_b_p": float(mannwhitneyu(ja, jb, alternative="greater").pvalue)}
    json.dump({"summary": summ, "rows": res}, open(f"{out}/RESULT.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
