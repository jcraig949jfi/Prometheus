"""W2-X check of H6 v3/v4 'forwarding never discovered' / 'categorical one-hop wall': the two C1 multi-hop
RELAY SIGNAL rows (925caa3a ring r3 d5 = 2 hops; 882525a9 smallworld d3) re-scored on 128 FRESH worlds
(namespace 0x5A5A, 64 mirror pairs), at their own condition and with zero_comm. If accuracy replicates above
chance on fresh worlds, information crossed >= 2 hops, i.e. some forwarding exists. CPU, 2 threads."""
import os, sys, json
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
sys.path.insert(0, os.path.abspath("../../H-PLANT"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
import hp_common as hc
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
from prometheus.ananke.engine import Controls
from prometheus.ananke.rng import H_int
out = []
for cid in ["925caa3a48964717", "882525a9d4a3d073"]:
    r = hc.row(cid)
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int32)
    seeds = assays.world_seeds(H_int(0x5A5A, int(cid[:8], 16)), 128)
    a = hc.evaluate(ph, g, env, seeds)
    z = hc.evaluate(ph, g, env, seeds, ctrl=Controls(zero_comm=True))
    M = envs.dist_matrix(ph)
    o = {"cell": cid, "topology": ph.topology, "radius": ph.radius, "d": env.d, "recorded_held": r["result"]["held"]["acc"],
         "fresh_acc": a["acc"], "fresh_lo99": a["lo99"], "zero_comm_acc": z["acc"]}
    out.append(o); print(o, flush=True)
json.dump(out, open("check_multihop_forwarding.json", "w"), indent=1)
