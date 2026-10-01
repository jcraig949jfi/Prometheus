"""Size of the MAJ reversed-placement artefact on directed graphs.
(1) per world: actuator in-degree 0 (no packet can ever arrive) and sensors unreachable;
(2) plant viability (relay_flood, prog_len max(L,12), 32 worlds, as campaign.plant_viability) with the
    frozen placement vs a FORWARD placement (same RNG draws, M transposed so sensors sit at transport
    distance d), on the MAJ topology-transect cells and the 4781b0a1 topology->random transplant."""
from common import *
import gzip, json, collections, numpy as np
from prometheus.ananke import envs, assays, plants, campaign
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]

def plant_acc(ph, env, seed, forward=False):
    p2 = ph.replace(prog_len=max(ph.prog_len, 12))
    g = plants.plant("relay_flood", p2)[None]
    seeds = assays.world_seeds(H_int(seed, 0x9147), 32)
    real = envs.dist_matrix
    if forward:
        envs._DIST_CACHE.clear()
        envs.dist_matrix = lambda ph_: real(ph_).T.copy()     # MAJ uses M[a] -> becomes column a = M[:, a]
    try:
        acc = assays.evaluate(p2, g, env, seeds, device="cpu", graph=False).mean()[0]
    finally:
        envs.dist_matrix = real; envs._DIST_CACHE.clear()
    return acc

# (1) unreachable actuators
c = collections.Counter()
for r in R:
    if r["wave"] == "A0" and r["env"]["family"] == "MAJ" and r["physics"]["topology"] == "random":
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        M = envs.dist_matrix(ph)
        ep = envs.build(ph, env, assays.world_seeds(H_int(r["search_seed"], 0x9147), 32))
        for b in range(0, 32, 2):
            a = int(ep.schedule.read_idx[b, 0]); s = ep.schedule.sense_idx[b].numpy()
            f = M[s, a]
            c["worlds"] += 1; c["indeg0"] += int((M[:, a] >= 10**6).sum() == len(M) - 1)
            c["all_unreach"] += int((f >= 10**6).all()); c["fwd_eq_d"] += int((f == env.d).sum()); c["sensors"] += len(s)
print("A0 MAJ random-topology plant worlds:", dict(c))
# (2) plant viability frozen vs forward placement on transect cells
rows = [r for r in R if r["wave"] in ("B", "B2") and r["env"]["family"] == "MAJ"
        and (r.get("extra") or {}).get("transect") == "topology" and r["physics"]["topology"] in ("random", "smallworld")]
done = set()
for r in rows:
    key = (r["wave"], r["extra"]["track"], r["extra"]["base"], r["physics"]["topology"], r["extra"]["rep"])
    if key in done or r["kind"] != "census": continue
    done.add(key)
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    a0 = plant_acc(ph, env, r["search_seed"]); a1 = plant_acc(ph, env, r["search_seed"], forward=True)
    print(key, "d", env.d, "recorded plant", round(r["result"]["plant"]["acc"], 3), "rerun frozen", round(a0, 3), "forward placement", round(a1, 3), flush=True)
