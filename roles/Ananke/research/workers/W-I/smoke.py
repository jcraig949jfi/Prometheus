import sys, time, pathlib, json
REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np, torch
from prometheus.ananke import assays, c1b_run
import traj
seeds = assays.world_seeds(0x5EE, 64)
for cid in sys.argv[1:]:
    ph, env, g, row = c1b_run.load(cid)
    t = time.time(); ok = traj.selfcheck(ph, g, env, seeds); print(cid, "selfcheck", ok, round(time.time()-t,1), flush=True)
    arms = [("normal", None, 0)] + [(f"a{j}", traj.SITE, j % 10) for j in range(47)]
    torch.cuda.synchronize(); t = time.time()
    traj.run_arms(ph, g, env, seeds, arms, chunk=48); torch.cuda.synchronize()
    print(cid, "48-arm chunk s", round(time.time()-t,1), "maxmem MB", torch.cuda.max_memory_allocated()//2**20, flush=True)
    t = time.time(); tp = traj.twin_profile(ph, g, env, 0x5EE ^ 0x7);  print("twin s", round(time.time()-t,1))
