"""W2-W minimal check resolving the P-1b vs P-2 contradiction on individual cells.
P-1b reads a recorded relay_flood failure as plant-dead physics; P-2 shows (3 A0 cells) that decay_shift>0
failures are a relay_flood write-on-change artefact. For every C1 RELAY NULL evolve cell with recorded
relay_flood acc <= .60, decay_shift > 0, and not P_PROVEN, score at the cell's own physics:
  (a) relay_refresh (P-2's 15-line plant) and (b) relay_flood with decay_shift := 0 (attribution control),
on campaign.plant_viability's 32 seeds (the recorded plant's worlds), eager CPU, prog_len max(L,16).
Known-answer: relay_flood at the cell's own physics must reproduce the recorded plant acc (prog_len max(L,12))."""
import json, os, sys, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "H-PLANT")); sys.path.insert(0, str(HERE.parent / "P-1"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import hp_common as hc
from prometheus.ananke import assays, envs, plants
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
import importlib.util
spec = importlib.util.spec_from_file_location("dp", str(HERE.parent / "P-1/decay_plant.py"))
src = open(HERE.parent / "P-1/decay_plant.py").read().split("N_PER =")[0]   # import relay_refresh only
ns = {}; exec(compile(src, "decay_plant_head", "exec"), ns)
relay_refresh = ns["relay_refresh"]

P = json.load(open(HERE / "out/placement.json"))
todo = [o["cell"] for o in P if o["family"] == "RELAY" and o["p2_decay_artefact"] and o["final_class"] != "P_PROVEN"]
print("cells", len(todo), flush=True)
out = []; t0 = time.process_time()
for c in todo:
    r = hc.row(c)
    ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
    p12 = ph0.replace(prog_len=max(ph0.prog_len, 12))
    ka = hc.evaluate(p12, plants.plant("relay_flood", p12), env, seeds)["acc"]
    p16 = ph0.replace(prog_len=max(ph0.prog_len, 16)).validate()
    rf = hc.evaluate(p16, hc.bc(p16, relay_refresh(p16)), env, seeds)
    pd0 = p12.replace(decay_shift=0).validate()
    f0 = hc.evaluate(pd0, plants.plant("relay_flood", pd0), env, seeds)
    o = {"cell": c, "prog_len": ph0.prog_len, "decay_shift": ph0.decay_shift, "recorded_flood": r["result"]["plant"]["acc"],
         "ka_flood": ka, "ka_exact": abs(ka - r["result"]["plant"]["acc"]) < 1e-9,
         "refresh": rf["acc"], "refresh_lo99": rf["lo99"], "refresh_in_space": ph0.prog_len >= 15,
         "flood_decay0": f0["acc"], "flood_decay0_lo99": f0["lo99"]}
    out.append(o); print(o, flush=True)
json.dump({"rows": out, "cpu_s": time.process_time() - t0}, open(HERE / "out/refresh_check.json", "w"), indent=1)
print("cpu_s", time.process_time() - t0)
