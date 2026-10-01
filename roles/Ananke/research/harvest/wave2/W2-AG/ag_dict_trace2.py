"""W2-AG: actuator readout time series for 4781b0a1, normal vs DICT, worlds 0/1 (one mirror pair)."""
import os, sys, json, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "H-PLANT"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
import hp_common
from prometheus.ananke import assays, envs, search
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
t0 = time.process_time()
r = [x for x in hp_common.rows() if x["cell_id"].startswith("4781b0a1") and x["kind"] == "evolve"][0]
ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); g0 = np.asarray(r["result"]["champion"])
seeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), 64)[:4]
res = {}
for mode in ("normal", "DICT"):
    M = len(seeds); ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    if mode == "DICT":
        ep.schedule.sense_val[:, :, 1:] = 0
    w = World(ph, np.repeat(g0[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()[:, :, 0]
    res[mode] = {"nz_ticks_w0": [(int(t), int(tr[t, 0])) for t in range(tr.shape[0]) if tr[t, 0] != -3][:40],
                 "nz_ticks_w1": [(int(t), int(tr[t, 1])) for t in range(tr.shape[0]) if tr[t, 1] != -3][:40],
                 "n_nz": [int((tr[:, m] != -3).sum()) for m in range(M)]}
    sv = np.asarray(ep.schedule.sense_val)
    res[mode]["cue_ticks_w0_sensor0"] = [(int(t), int(sv[t, 0, 0])) for t in range(sv.shape[0]) if sv[t, 0, 0] != 0][:12]
res["schedule_attrs"] = [a for a in dir(ep.schedule) if not a.startswith("_")]
res["ro_ticks"] = np.asarray(ep.ro_tick).ravel()[:24].tolist() if hasattr(ep, "ro_tick") else None
res["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(res, open(os.path.join(os.path.dirname(__file__), "dict_trace2_4781.json"), "w"), indent=1)
print(json.dumps(res, indent=0)[:4000])
