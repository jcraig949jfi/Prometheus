"""W2-X check of E-W13's extrapolation: P-2 tested relay_refresh at 3 A0 cells, but the SUPPORTED RELAY
decay_shift boundary was measured at two B-wave base cells (base 0: global, base 1: torus; both economy
'low'). Here: relay_flood vs relay_refresh (P-2's exact 15-line program) at the decay_shift=1 transect
cell of each base, with campaign.plant_viability's seeds (first 16 of the row's 32), prog_len 16 for both
(as P-2). Also each at decay 0 (same base, li 0). CPU, 2 threads."""
import os, sys, json, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
H = os.path.abspath("../../H-PLANT"); sys.path.insert(0, H); sys.path.insert(0, os.path.abspath("../P-1"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import hp_common as hc
from prometheus.ananke import assays, envs, plants
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
import importlib.util
spec = importlib.util.spec_from_file_location("dp_src", os.path.abspath("../P-1/decay_plant.py"))
src = open(os.path.abspath("../P-1/decay_plant.py")).read()
ns = {}; exec(src.split("N_PER =")[0].split("def relay_refresh")[0], ns)     # imports only
exec("def relay_refresh" + src.split("def relay_refresh")[1].split("N_PER =")[0], {**ns, "plants": plants}, ns)
relay_refresh = ns["relay_refresh"]
NW = int(sys.argv[1]) if len(sys.argv) > 1 else 16
cells = sys.argv[2].split(",") if len(sys.argv) > 2 else ["c0f8d6f5269b54dd", "d71f436e1d89cd42"]
out = []; t0 = time.time()
for cid in cells:
    r = hc.row(cid)
    ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)[:NW]
    p2 = ph0.replace(prog_len=max(ph0.prog_len, 16)).validate()
    a_f = hc.evaluate(p2, plants.plant("relay_flood", p2), env, seeds)
    a_r = hc.evaluate(p2, hc.bc(p2, relay_refresh(p2)), env, seeds)
    o = {"cell": cid, "decay": ph0.decay_shift, "topology": ph0.topology, "recorded_flood_32w_L12": r["result"]["plant"]["acc"],
         "flood": a_f["acc"], "flood_lo99": a_f["lo99"], "refresh": a_r["acc"], "refresh_lo99": a_r["lo99"], "wall_s": time.time() - t0}
    out.append(o); print(o, flush=True)
json.dump(out, open("check_ew13_boundary_bases.json", "w"), indent=1)
