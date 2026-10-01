"""D-wave 'topology->random' transplant for MAJ champions: frozen (reversed MAJ placement) vs forward."""
from common import *
import gzip, json, numpy as np
from prometheus.ananke import envs, assays, campaign
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
real = envs.dist_matrix
for r in R:
    if r["kind"] != "adjudicate" or r["env"]["family"] != "MAJ": continue
    tp = r["result"]["transplants"].get("topology->random")
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); champ = np.asarray(r["extra"]["genome"])
    if tp is None or tp.get("status") != "RAN":
        print(r["cell_id"][:8], ph.topology, "topology->random:", tp); continue
    p2 = ph.replace(topology="random", k_random=max(3, ph.table_width())).validate()
    hseeds = assays.world_seeds(H_int(r["search_seed"], 0x7A7A), 32)
    a0 = assays.evaluate(p2, champ[None], env, hseeds, device="cpu", graph=False).mean()[0]
    envs._DIST_CACHE.clear(); envs.dist_matrix = lambda q: real(q).T.copy()
    try:
        a1 = assays.evaluate(p2, champ[None], env, hseeds, device="cpu", graph=False).mean()[0]
    finally:
        envs.dist_matrix = real; envs._DIST_CACHE.clear()
    print(r["cell_id"][:8], r["extra"]["source_cell"][:8], ph.topology, "d", env.d, "normal", round(r["result"]["controls"]["normal"]["acc"], 3),
          "| topology->random recorded", round(tp["acc"], 3), "rerun", round(a0, 3), "forward placement", round(a1, 3), flush=True)
