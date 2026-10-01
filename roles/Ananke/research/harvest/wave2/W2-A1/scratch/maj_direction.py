"""envs.build MAJ places sensors with _pick_at(g, M[a], d): M[a] = BFS hops FROM the actuator over the
DIRECTED out-edge table (topology.graph_distances). Packets travel sensor -> actuator, i.e. M[s][a].
On directed graphs (random; rewired smallworld edges) the two differ. Measure the forward (transport)
hop count of MAJ sensors vs the nominal d, for every MAJ physics in the C1 rows on random/smallworld."""
from common import *
import gzip, json, collections, numpy as np
from prometheus.ananke import envs, assays
from prometheus.ananke.physics import Physics
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
seen = {}
for r in R:
    if r["env"]["family"] == "MAJ" and r["physics"]["topology"] in ("random", "smallworld"):
        key = json.dumps([r["physics"], r["env"]], sort_keys=True)
        seen.setdefault(key, []).append(r)
stats = collections.defaultdict(list); sig_rows = []
for key, rs in seen.items():
    ph = Physics.from_dict(rs[0]["physics"]); env = envs.EnvSpec(**rs[0]["env"])
    M = envs.dist_matrix(ph)
    ep = envs.build(ph, env, assays.world_seeds(1, 32))
    a = ep.schedule.read_idx[:, 0].numpy(); s = ep.schedule.sense_idx.numpy()
    fwd = np.array([[M[s[b, j], a[b]] for j in range(s.shape[1])] for b in range(0, 32, 2)])
    rev = np.array([[M[a[b], s[b, j]] for j in range(s.shape[1])] for b in range(0, 32, 2)])
    stats[(ph.topology, env.d)].append((rev.mean(), fwd.mean(), (fwd == rev).mean(), (fwd <= 1).mean()))
    for r in rs:
        if r["kind"] == "evolve" and r["result"]["held"]["lo99"] > .55:
            sig_rows.append((r["cell_id"][:8], ph.topology, env.d, round(fwd.mean(), 2), round(r["result"]["held"]["acc"], 3)))
for k in sorted(stats):
    v = np.array(stats[k])
    print(f"{k}: physics cells {len(v)}  nominal(rev) mean {v[:,0].mean():.2f}  forward mean {v[:,1].mean():.2f}  "
          f"frac sensors fwd==rev {v[:,2].mean():.2f}  frac fwd<=1 hop {v[:,3].mean():.2f}")
print("MAJ SIGNAL rows on directed graphs (cell, topo, d, mean forward hops of sensors, held):", sig_rows)
