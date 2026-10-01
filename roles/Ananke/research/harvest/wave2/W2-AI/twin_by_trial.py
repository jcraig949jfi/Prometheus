"""W2-AI: recorded twin assay (trial 2, hseeds[:16]) reproduced on CPU, then repeated for every trial, to see whether
REACH_BEYOND_HOP=False (beyond_hop < .5) coexists with certified forwarding. CPU eager, 2 threads."""
import os, sys, json, gzip, pathlib, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
ROOT = pathlib.Path(__file__).resolve().parents[6]; sys.path.insert(0, str(ROOT))
import numpy as np, torch
torch.set_num_threads(2); assert not torch.cuda.is_available()
from prometheus.ananke import assays, envs, search
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
R = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l)
    if r["cell_id"] in ("925caa3a48964717", "882525a9d4a3d073"):
        R[r["cell_id"]] = r
out = {}
c0 = time.process_time()
for cid, r in R.items():
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); sp = search.SearchSpec(**r["search"])
    g = np.asarray(r["result"]["champion"])
    hs = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)[:16]
    per = {}
    for tr in range(env.trials):
        tw = assays.twin_assay(ph, g[None], env, hs, trial=tr, device="cpu")
        per[tr] = {k: float(v[0]) for k, v in tw.items()}
    rec = r["result"]["twin"]
    ka = all(abs(per[2][k] - rec[k]) < 1e-9 for k in rec)
    out[cid] = {"recorded_twin": rec, "trial2_repro_exact": ka,
                "beyond_hop_by_trial": [per[t]["beyond_hop"] for t in range(env.trials)],
                "readout_flipped_by_trial": [per[t]["readout_flipped"] for t in range(env.trials)],
                "reach_by_trial": [per[t]["reach"] for t in range(env.trials)]}
    print(cid, json.dumps(out[cid]), flush=True)
out["cpu_s"] = round(time.process_time() - c0, 1)
(pathlib.Path(__file__).parent / "out_twin_by_trial.json").write_text(json.dumps(out, indent=1))
print(out["cpu_s"])
