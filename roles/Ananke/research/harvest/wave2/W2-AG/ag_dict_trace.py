"""W2-AG: why is 4781b0a1 EXACTLY .500 (zero variance) under W2-M's DICT ablation, when its plant scores .651
on the same worlds? Normal vs DICT on 16 of the row's own held worlds; record actuator readouts and stats."""
import os, sys, json, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ.setdefault("OMP_NUM_THREADS", "2")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "H-PLANT"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
from hp_common import row
from prometheus.ananke import assays, envs, search
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
t0 = time.process_time()
r = [x for x in __import__("hp_common").rows() if x["cell_id"].startswith("4781b0a1") and x["kind"] == "evolve"][0]
ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); g0 = np.asarray(r["result"]["champion"])
seeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), 64)[:16]
out = {"physics": {k: r["physics"][k] for k in ("topology", "n_sites", "radius", "update_mode", "update_period", "lat_base", "lat_hop", "loss", "dest_mode", "fanout", "wimm")}}
for mode in ("normal", "DICT"):
    M = len(seeds); ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    if mode == "DICT":
        ep.schedule.sense_val[:, :, 1:] = 0
    w = World(ph, np.repeat(g0[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy(); acc = envs.score(ep, tr)
    sv = ep.schedule.sense_val.cpu().numpy() if hasattr(ep.schedule.sense_val, "cpu") else np.asarray(ep.schedule.sense_val)
    out[mode] = {"acc_per_world": [round(float(a), 3) for a in acc],
                 "stats": {k: [int(x) for x in v.cpu().numpy().ravel()[:16]] for k, v in w.stats.items()},
                 "trace_shape": list(tr.shape), "trace_w0": tr[0].ravel()[:240].tolist(), "trace_w1": tr[1].ravel()[:240].tolist(),
                 "sense_nonzero_per_sensor_w0": [int((sv[:, 0, k] != 0).sum()) for k in range(sv.shape[2])]}
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "dict_trace_4781.json"), "w"), indent=1)
print(json.dumps(out["physics"])); 
for mode in ("normal", "DICT"):
    print(mode, out[mode]["acc_per_world"]); print(" stats", {k: v[:4] for k, v in out[mode]["stats"].items()})
    print(" sense nz", out[mode]["sense_nonzero_per_sensor_w0"], "trace shape", out[mode]["trace_shape"])
    print(" w0 trace", out[mode]["trace_w0"][:60])
print("cpu_s", out["cpu_s"])
