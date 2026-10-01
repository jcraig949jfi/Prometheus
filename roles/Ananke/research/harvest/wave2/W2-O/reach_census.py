"""W2-O population extension (no engine runs): actuator reachability on the HELD worlds of EVERY recorded C1
evolve cell in XOR/FLIP/RELAY/MAJ. A world is IMPOSSIBLE when the information the task needs has no
directed transport path to the actuator:
  RELAY/FLIP: sensor -> actuator unreachable;   XOR: either sensor unreachable;   MAJ: no sensor reaches.
MAJ also reports PARTIAL worlds (some but not all sensors reach). Symmetric topologies (torus/ring/global)
are connected, so only random/smallworld can have impossible worlds; they are all scanned anyway."""
import os, sys, json, gzip, pathlib, collections, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "1"
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
import numpy as np
import torch
assert not torch.cuda.is_available()
torch.set_num_threads(1)
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import HELD_NS

t0 = time.process_time()
R = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
ev = [r for r in R if r["kind"] == "evolve" and r["env"]["family"] in ("XOR", "FLIP", "RELAY", "MAJ")]
_M = {}


def tdist(ph):
    key = ph.digest()
    if key not in _M:
        N = ph.n_sites
        nbr, _ = topology.build(ph)
        if nbr is None:
            M = np.ones((N, N), dtype=np.int64)
            np.fill_diagonal(M, 0)
        else:
            M = np.stack([topology.graph_distances(ph, s) for s in range(N)])
        _M[key] = M
    return _M[key]


rows = []
for r in ev:
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = r["search"]
    seeds = assays.world_seeds(H_int(r["search_seed"], HELD_NS), sp["M_held"])
    ep = envs.build(ph, env, seeds)
    M = tdist(ph)
    s = ep.schedule.sense_idx.numpy()
    a = ep.schedule.read_idx.numpy()[:, 0]
    fam = env.family
    cols = s[:, :1] if fam in ("RELAY", "FLIP") else s
    reach = M[cols, a[:, None]] >= 0
    if fam == "MAJ":
        imp = ~reach.any(1)
    else:
        imp = ~reach.all(1)
    part = int(((~reach).any(1) & reach.any(1)).sum()) if fam == "MAJ" else 0
    rows.append({"cell": r["cell_id"], "family": fam, "topology": ph.topology, "wave": r["wave"],
                 "signal": bool(r["labels"].get("SIGNAL")), "held": r["result"]["held"]["acc"],
                 "impossible": int(imp.sum()), "partial": part, "M": len(seeds),
                 "no_in_edge_actuator": int(sum(1 for x in a if not (M[:, x] > 0).any()))})
summ = {}
for fam in ("XOR", "FLIP", "RELAY", "MAJ"):
    for sig in (False, True):
        rr = [x for x in rows if x["family"] == fam and x["signal"] == sig]
        if not rr:
            continue
        k = f"{fam}|{'SIGNAL' if sig else 'NULL'}"
        W = sum(x["M"] for x in rr)
        summ[k] = {"cells": len(rr), "cells_with_impossible": sum(x["impossible"] > 0 for x in rr),
                   "impossible_worlds": sum(x["impossible"] for x in rr), "worlds": W,
                   "impossible_frac": round(sum(x["impossible"] for x in rr) / W, 4),
                   "max_impossible_in_cell": max(x["impossible"] for x in rr),
                   "partial_worlds": sum(x["partial"] for x in rr),
                   "by_topology": {t: [sum(1 for x in rr if x["topology"] == t),
                                       sum(x["impossible"] for x in rr if x["topology"] == t)]
                                   for t in sorted({x["topology"] for x in rr})}}
out = {"summary": summ, "rows": rows, "cpu_s": round(time.process_time() - t0, 1)}
(HERE / "out/reach_census.json").write_text(json.dumps(out, indent=1))
print(json.dumps(summ, indent=1), out["cpu_s"])
