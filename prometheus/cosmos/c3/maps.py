"""Certification maps over the visible families (S1_PREREG_LAW s3). One row per world:
family, native params, k, certificate (v3), generic coordinates.

  python -m prometheus.cosmos.c3.maps <out_dir> [n_per_family] [workers]
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.geometry import coordinates
from prometheus.cosmos.c3.substrates import RNN, Graph, Hybrid, Stig
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.hashing import code_identity, h

LATTICE = {
    "rnn": {"rho": [0, .3, .6, .8, .9, .95, 1.0, 1.1], "a": [.2, .5, 1], "sigma": [.01, .1, .3, 1]},
    "graph": {"K": [1, 2, 3, 4, 6], "b": [-1, -.5, 0, .5], "p": [0, .01, .03, .1]},
    "stig": {"delta": [.02, .1, .3, .6], "D": [0, .1, .3], "v": [0, 1, 2], "j": [0, .1, .3]},
}
DELAYS = [2, 4, 8]
SEED = 20260924


def build(family: str, params: Dict[str, Any], k: int):
    t = Task(4, k)
    if family == "rnn":
        return RNN(t, params["rho"], params["a"], params["sigma"]), t
    if family == "graph":
        return Graph(t, int(params["K"]), params["b"], params["p"]), t
    if family == "stig":
        return Stig(t, params["delta"], params["D"], int(params["v"]), params["j"]), t
    if family == "hybrid":
        return Hybrid(t, params["internal"], params["external"]), t
    raise ValueError(family)


def world_row(job: Dict[str, Any]) -> Dict[str, Any]:
    fam, params, k = job["family"], job["params"], job["k"]
    sysm, task = build(fam, params, k)
    wid = h({"family": fam, "params": params, "k": k})
    seed = int(wid[:8], 16)
    t0 = time.time()
    cert = certify(sysm, task, seed=seed)
    coords = coordinates(sysm, task, seed=seed + 1)
    return {"world_id": wid, "family": fam, "params": params, "k": k, "class": cert["class"],
            "P1": cert["P1"], "P2": cert["P2"], "coords": coords, "s": round(time.time() - t0, 1)}


def sample_jobs(n_per_family: int, seed: int = SEED) -> List[Dict[str, Any]]:
    rng = np.random.default_rng(seed)
    jobs = []
    for fam, lat in LATTICE.items():
        seen = set()
        while sum(1 for j in jobs if j["family"] == fam) < n_per_family:
            p = {k2: (v[rng.integers(len(v))]) for k2, v in lat.items()}
            p = {k2: (float(x) if isinstance(x, float) else int(x)) for k2, x in p.items()}
            k = int(DELAYS[rng.integers(len(DELAYS))])
            key = json.dumps([p, k], sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            jobs.append({"family": fam, "params": p, "k": k})
    return jobs


def hybrid_jobs() -> List[Dict[str, Any]]:
    return [{"family": "hybrid", "params": {"internal": i, "external": e}, "k": k}
            for i in (True, False) for e in (True, False) for k in DELAYS]


def run(jobs, workers: int) -> List[Dict[str, Any]]:
    if workers <= 1:
        return [world_row(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(world_row, jobs))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    out.mkdir(parents=True, exist_ok=True)
    rows = run(sample_jobs(n), w)
    hyb = run(hybrid_jobs(), w)
    res = {"identity": code_identity(), "n_per_family": n, "rows": rows, "hybrid": hyb}
    (out / "MAPS.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    from collections import Counter
    for fam in LATTICE:
        print(fam, dict(Counter(r["class"] for r in rows if r["family"] == fam)))
    print("hybrid", [(r["params"], r["k"], r["class"]) for r in hyb])
