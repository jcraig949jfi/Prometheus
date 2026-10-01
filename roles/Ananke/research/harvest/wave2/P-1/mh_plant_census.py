"""P-1b: relay_flood plant viability (C1's own campaign.plant_viability) at every C1 RELAY evolve row
whose env demands >= 2 hops and is light-cone reachable (H-PLANT lc bound >= .95). CPU, 2 threads."""
import json, math, os, sys, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, "../../H-PLANT")
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import hp_common as hc
from prometheus.ananke import assays, envs, plants
from prometheus.ananke.rng import H_int
from prometheus.ananke.physics import Physics
lc = {o["cell"]: o["bound"] for o in json.load(open("../../H-PLANT/out/lc_census.json"))["rows"]}
def hops(r):
    ph = r["physics"]; d = r["env"]["d"]; t = ph["topology"]
    if t == "global": return 1
    if t in ("ring", "torus"): return math.ceil(d / ph["radius"])
    return d
out = []; t0 = time.time()
for r in hc.rows():
    if r["env"]["family"] != "RELAY" or r["kind"] != "evolve" or hops(r) < 2: continue
    b = lc.get(r["cell_id"])
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    p2 = ph.replace(prog_len=max(ph.prog_len, 12))
    g = plants.plant("relay_flood", p2)
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)   # campaign.plant_viability's seeds
    pv = hc.evaluate(p2, g, env, seeds)                                  # eager CPU (assays.evaluate graph=True is slow on CPU)
    held = r["result"].get("held") or {}
    o = {"cell": r["cell_id"], "wave": r["wave"], "topology": ph.topology, "radius": ph.radius, "d": env.d,
         "delta": env.delta, "hops": hops(r), "lc_bound": b, "plant_acc": pv["acc"],
         "plant_lo99": pv.get("lo99"), "held_acc": held.get("acc"), "held_lo99": held.get("lo99"),
         "max_train_acc": max(c["max_acc"] for c in r["result"]["curve"])}
    out.append(o); print(o, flush=True)
json.dump({"rows": out, "cpu_s": time.time() - t0}, open("mh_plant_census.json", "w"), indent=1)
print("cpu_s", time.time() - t0)
