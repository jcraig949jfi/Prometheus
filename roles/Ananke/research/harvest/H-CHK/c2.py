"""C2: PMAJ at champion loss .1 + fanout-8 sampling (PLAN_ADDENDUM X3)."""
import os, time, json
import numpy as np
import hchk as H
from prometheus.ananke import assays
wv = H.mod("wv_wv")
ph0, env, _ = H.champ()
php = H.c2_physics(ph0)
g = H.mod("wv_plants").genome(php, "PMAJ")
H.threads1()
t0 = time.time()
seeds = assays.world_seeds(0x650, 128)
OFFS = [2, 4, 6, 8, 12]
r = wv.run(php, g, env, seeds, OFFS, list(range(1, env.trials)), device=H.DEV)
np.savez_compressed(H.OUT / "c2_raw.npz", **{k: v for k, v in r.items() if k != "arms"})
out = H.wv_summary(r)
for t in out["strata"].values():
    print(H.wv_line(t), flush=True)
from prometheus.ananke import envs
ep = envs.build(php, env, seeds)
acc = float(np.nanmean(np.where(r["normal_s0"] == 0, .5, (np.sign(r["normal_s0"]) == r["y"]))[r["scored"]]))
rd = H.reading_c2(out)
print("READING", rd, "normal acc", acc, flush=True)
H.dump({"reading": rd, "normal_acc": acc, "summary": out, "physics": php.to_dict(), "wall_s": time.time() - t0,
        "pid": os.getpid()}, "c2.json")
