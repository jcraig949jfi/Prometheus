"""P-2: is C1's decay_shift>0 RELAY 'physics-dead' map a relay_flood artifact?
relay_refresh = 3 lines that re-normalise S0 to sign(S0)*256 at every awake tick, then relay_flood unchanged.
Scored with campaign.plant_viability's seeds (H_int(search_seed,0x9147), 32 worlds), eager CPU, prog_len>=16."""
import json, os, sys, time, collections
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, "../../H-PLANT")
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
import hp_common as hc
from prometheus.ananke import assays, envs, plants
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int

def relay_refresh(ph):
    return plants.assemble(ph, [
        ("GT", "T2", "S0", "ZERO", 0), ("GT", "T3", "ZERO", "S0", 0), ("SUB", "S0", "T2", "T3", 0),
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("GT", "T2", "T0", "ZERO", 0), ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0), ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0), ("MULQ", "EMIT", "T2", "T3", 0), ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0), ("ADD", "S0", "S0", "T3", 0)])

N_PER = int(sys.argv[1]) if len(sys.argv) > 1 else 6
rng = np.random.default_rng(7)
pool = collections.defaultdict(list)
for r in hc.rows():
    if r["wave"] != "A0" or r["env"]["family"] != "RELAY": continue
    p = r["result"].get("plant"); ph = r["physics"]
    if not p: continue
    if ph["decay_shift"] > 0 and p["acc"] <= 0.6: pool[ph["decay_shift"]].append(r)
    if ph["decay_shift"] == 0 and p["acc"] > 0.6: pool["ctl0"].append(r)   # known-answer: viable rows
out = []; t0 = time.time()
for k in [1, 3, 6, "ctl0"]:
    rows = [pool[k][i] for i in rng.choice(len(pool[k]), size=min(N_PER, len(pool[k])), replace=False)]
    for r in rows:
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        p2 = ph.replace(prog_len=max(ph.prog_len, 16)).validate()
        seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
        a_flood = hc.evaluate(p2, plants.plant("relay_flood", p2), env, seeds)["acc"]
        ev = hc.evaluate(p2, hc.bc(p2, relay_refresh(p2)), env, seeds)
        o = {"cell": r["cell_id"], "decay": k, "recorded_flood": r["result"]["plant"]["acc"], "flood_L16": a_flood,
             "refresh": ev["acc"], "refresh_lo99": ev["lo99"], "topology": ph.topology, "update_mode": ph.update_mode}
        out.append(o); print(o, flush=True)
json.dump({"rows": out, "wall_s": time.time() - t0}, open("decay_plant.json", "w"), indent=1)
