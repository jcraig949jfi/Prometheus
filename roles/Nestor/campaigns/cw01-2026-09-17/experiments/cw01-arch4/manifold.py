"""The temporal-response manifold as data: P-F02's census programs (regenerated deterministically), its
cluster centroids, nearest-centroid assignment, representatives per geometry, and the raw curve set.
Shape ids follow P-F02's RESULT.json clusters: 0 start_anchored, 1 schedule, 2 ask_time (small), 3 immune,
4 periodic, 5 ask_time. Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "P-D01"))
sys.path.insert(0, str(HERE / "P-F02"))
import common as CM            # noqa: E402
from run_PD01 import c408_tops   # noqa: E402
from run_PF02 import curve, KEYS, POS, DOSES, worlds   # noqa: E402,F401
A = CM.A
SHAPE = {0: "start_anchored", 1: "schedule", 2: "ask_time", 3: "immune", 4: "periodic", 5: "ask_time"}
WORLDS3 = ("W0", "W2_K2", "W1_d4")
_C = {}


def census_programs():
    """P-F02's program list, regenerated (same walks, same tops)."""
    if "progs" in _C:
        return _C["progs"]
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, lineage="parent:" + p["stratum"]) for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        for d in (4, 8, 16):
            if d in wk["archived"]:
                programs.append({"organism_id": "%s/w1d%d" % (p["organism_id"], d), "lineage": "walker%d:%s" % (d, p["stratum"]), "manifest": wk["archived"][d], "env": p["env"]})
    programs += [dict(p, lineage="c408") for p in c408_tops()]
    tops = json.loads((HERE / "P-F03" / "tops.json").read_text(encoding="utf-8"))
    for x in tops:
        for i, t in enumerate(x["tops"][:16]):
            programs.append({"organism_id": "pf03-%s-%s-%d-%s-%d" % (x["env"], x["mode"], x["seed"], x["stage"], i), "lineage": "pf03:%s:%s:%s" % (x["env"], x["mode"], x["stage"]), "manifest": t["m"], "env": x["env"]})
    _C["progs"] = programs
    return programs


def centroids():
    if "cent" not in _C:
        r = json.loads((HERE / "P-F02" / "RESULT.json").read_text(encoding="utf-8"))
        _C["cent"] = {c["id"]: [c["centroid"][k] for k in KEYS] for c in r["clusters"]}
    return _C["cent"]


def rows():
    if "rows" not in _C:
        _C["rows"] = {r["pid"]: r for r in json.loads((HERE / "P-F02" / "rows.json").read_text(encoding="utf-8"))}
    return _C["rows"]


def dist(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.mean(np.abs(a[ok] - b[ok]))) if ok.any() else float("nan")


def nearest(v, cents=None):
    cents = cents or centroids()
    ds = {k: dist(v, c) for k, c in cents.items()}
    k = min(ds, key=ds.get)
    return k, ds[k]


def representatives(cluster, n=8, exclude_prefix="pf03"):
    """The n census programs nearest a cluster's centroid (complete vectors; census members only)."""
    cent = centroids()[cluster]
    cand = []
    for pid, r in rows().items():
        if pid.startswith(exclude_prefix) or not all(x == x for x in r["vector"]):
            continue
        k, d = nearest(r["vector"])
        if k == cluster:
            cand.append((d, pid))
    cand.sort()
    byid = {p["organism_id"]: p for p in census_programs()}
    return [dict(byid[pid], cluster=cluster, shape=SHAPE[cluster], d_centroid=d) for d, pid in cand[:n] if pid in byid]


def rewards3(m):
    return {w: A.evaluate(m, A.episodes(w), rng_seed=0, reward_mode="per_ask")["reward_per_ask"] for w in WORLDS3}


def distinctive(v, thr=0.5):
    return {i for i, x in enumerate(v) if x == x and x >= thr}
