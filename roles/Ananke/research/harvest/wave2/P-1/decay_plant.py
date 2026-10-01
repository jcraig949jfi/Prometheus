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
# MATCHED COUNTERFACTUAL: A0 RELAY rows with decay_shift == 0 where relay_flood is viable (recorded acc > .7);
# set decay_shift to 1, 3, 6 and compare relay_flood vs relay_refresh on identical worlds.
rng = np.random.default_rng(7)
pool = [r for r in hc.rows() if r["wave"] == "A0" and r["env"]["family"] == "RELAY" and r["result"].get("plant")
        and r["physics"]["decay_shift"] == 0 and r["result"]["plant"]["acc"] > 0.7]
rows = [pool[i] for i in rng.choice(len(pool), size=N_PER, replace=False)]
out = []; t0 = time.time()
for r in rows:
    ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 16)
    for dk in [1]:
        p2 = ph0.replace(prog_len=max(ph0.prog_len, 16), decay_shift=dk).validate()
        a_f = hc.evaluate(p2, plants.plant("relay_flood", p2), env, seeds)
        a_r = hc.evaluate(p2, hc.bc(p2, relay_refresh(p2)), env, seeds)
        o = {"cell": r["cell_id"], "decay": dk, "recorded_flood_d0": r["result"]["plant"]["acc"],
             "flood": a_f["acc"], "flood_lo99": a_f["lo99"], "refresh": a_r["acc"], "refresh_lo99": a_r["lo99"],
             "topology": ph0.topology, "update_mode": ph0.update_mode, "update_period": ph0.update_period}
        out.append(o); print(o, flush=True)
json.dump({"design": "matched counterfactual decay_shift on viable decay-0 A0 RELAY rows", "rows": out,
           "wall_s": time.time() - t0}, open("decay_plant_d1.json", "w"), indent=1)
