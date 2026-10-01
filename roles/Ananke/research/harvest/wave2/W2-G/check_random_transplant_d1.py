"""W2-G distinguishing check for C1's 'topology-bound' reading.
C1 D-wave moved each RELAY law to a random graph KEEPING env d=3, which (on a BFS-distance graph)
forces a 3-hop task (check_random_transplant_hops.py: 128/128 placements). If the collapse to .500
is a hop-count effect rather than a lattice-geometry effect, the same law on the same random graph
at d=1 (one hop) should stay above chance. Evaluates each frozen champion (row result.champion) with
assays.evaluate on 64 fresh worlds (32 mirror pairs, W2-G namespace) in 3 conditions. CPU, 2 threads.
Not a search. Exploratory, post hoc."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
import gzip, json, pathlib, sys, time, dataclasses
ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import torch
torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
from prometheus.ananke import envs, assays
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
t0 = time.time(); c0 = time.process_time()
R = {json.loads(l)["cell_id"][:8]: json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")}
seeds = assays.world_seeds(H_int(0x57324747, 1), 64)   # "W2GG"
out = {}
for cid in ("bbef66a1", "31cd2a8a", "62a7fff9", "c16d5231"):
    r = R[cid]
    ph = Physics(**r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    g = g.reshape(1, ph.rules, ph.prog_len, 5)
    rnd = ph.replace(topology="random", k_random=max(3, ph.table_width())).validate()
    conds = {"native_d%d" % env.d: (ph, env),
             "random_d%d (C1 transplant)" % env.d: (rnd, env),
             "random_d1": (rnd, dataclasses.replace(env, d=1)),
             "native_d1": (ph, dataclasses.replace(env, d=1))}
    res = {}
    for name, (p2, e2) in conds.items():
        er = assays.evaluate(p2, g, e2, seeds, device="cpu", graph=False)
        pairs = er.acc.reshape(er.acc.shape[0], -1, 2).mean(-1)[0] if er.acc.ndim == 2 else None
        m = float(er.mean()[0])
        lo, hi = (None, None)
        if pairs is not None:
            _, lo, hi = assays.pair_ci(pairs)
            lo, hi = float(lo), float(hi)
        res[name] = {"acc": round(m, 3), "lo99": None if lo is None else round(lo, 3), "hi99": None if hi is None else round(hi, 3)}
    out[cid] = {"recorded_held": round(r["result"]["held"]["acc"], 3), **res}
    print(cid, out[cid], flush=True)
out["_compute"] = {"wall_s": round(time.time() - t0, 1), "cpu_s": round(time.process_time() - c0, 1), "threads": 2}
(pathlib.Path(__file__).parent / "random_transplant_d1.json").write_text(json.dumps(out, indent=1))
print(out["_compute"])
