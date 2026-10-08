"""Run the substitution attacks (roles/Cosmos/c3/S1_PREREG_SUBSTITUTION.md) and score the unchanged law.

  python -m prometheus.cosmos.c3.subst_run <out_dir> [workers]
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.geometry import coordinates
from prometheus.cosmos.c3.substitution import LATTICE, build
from prometheus.cosmos.hashing import code_identity, h

LAW_THRESHOLD = 0.0304          # preliminary law, S1_RESULT.md (NOT refitted)
DELAYS = [2, 4, 8]


def row(job):
    s, t = build(job["family"], job["params"], job["k"])
    seed = int(h(job)[:8], 16)
    t0 = time.time()
    c = certify(s, t, seed=seed)
    co = coordinates(s, t, seed=seed + 1)
    return {**job, "class": c["class"], "P1": c["P1"], "P2": c["P2"], "coords": co, "s": round(time.time() - t0, 1)}


def jobs(seed=20260927, n=24):
    rng = np.random.default_rng(seed)
    out = []
    for fam, lat in LATTICE.items():
        seen = set()
        while sum(1 for j in out if j["family"] == fam) < n:
            p = {k: v[rng.integers(len(v))] for k, v in lat.items()}
            p = {k: (float(x) if isinstance(x, float) else int(x)) for k, x in p.items()}
            k = int(DELAYS[rng.integers(3)])
            key = json.dumps([p, k], sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            out.append({"family": fam, "params": p, "k": k})
    return out


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    with ProcessPoolExecutor(max_workers=w) as ex:
        rows = list(ex.map(row, jobs()))
    summary = {}
    for fam in LATTICE:
        R = [r for r in rows if r["family"] == fam and r["class"] in ("NONE", "PASSIVE", "FUNCTIONAL")]
        pred = [r["coords"]["sR"] > LAW_THRESHOLD for r in R]
        truth = [r["class"] == "FUNCTIONAL" for r in R]
        misses = [r for r, p, y in zip(R, pred, truth) if p != y]
        summary[fam] = {"classes": dict(Counter(r["class"] for r in rows if r["family"] == fam)),
                        "n_scored": len(R), "agreement": float(np.mean([p == y for p, y in zip(pred, truth)])) if R else None,
                        "misses": [{"params": m["params"], "k": m["k"], "class": m["class"], "sR": m["coords"]["sR"],
                                    "sF": m["coords"]["sF"], "rR": m["coords"]["rR"], "effect": m["P2"]["effect"]} for m in misses]}
    res = {"identity": code_identity(), "law_threshold": LAW_THRESHOLD, "summary": summary, "rows": rows}
    (out / "SUBST.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    for fam, v in summary.items():
        print(fam, v["classes"], "agreement %.3f of %d" % (v["agreement"] or 0, v["n_scored"]))
        for m in v["misses"]:
            print("   MISS", m)
