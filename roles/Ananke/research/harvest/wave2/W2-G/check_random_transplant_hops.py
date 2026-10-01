"""W2-G check: in C1's D-wave 'topology->random' transplant the env (d) is kept, so on the
random graph the actuator is placed at BFS distance d (envs.dist_matrix). Measure the forward
hop count sensor->actuator for the 4 RELAY D cells before/after the transplant. CPU, 2 threads."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
import gzip, json, pathlib, collections, sys
ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import torch
torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
from prometheus.ananke import envs, topology
from prometheus.ananke.physics import Physics
R = {json.loads(l)["cell_id"][:8]: json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")}
out = {}
for cid in ("bbef66a1", "31cd2a8a", "62a7fff9", "c16d5231"):
    r = R[cid]
    ph = Physics(**r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    res = {}
    for tag, p2 in (("native", ph), ("topology->random", ph.replace(topology="random", k_random=max(3, ph.table_width())).validate())):
        seeds = list(range(1000, 1128))
        ep = envs.build(p2, env, seeds)
        s = ep.schedule.sense_idx[:, 0].numpy(); a = ep.schedule.read_idx[:, 0].numpy()
        h = [int(topology.graph_distances(p2, int(si))[int(ai)]) for si, ai in zip(s, a)]
        res[tag] = dict(sorted(collections.Counter(h).items()))
    out[cid] = {"d": env.d, "topology": ph.topology, "radius": ph.radius, "hops_sensor_to_actuator": res}
print(json.dumps(out, indent=1))
(pathlib.Path(__file__).parent / "random_transplant_hops.json").write_text(json.dumps(out, indent=1))
