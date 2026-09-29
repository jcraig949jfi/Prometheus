"""W-L preregistered search arm (PLAN s2, s4).
python run_search.py --n 1 --seed 0 [--device cuda] [--pilot]
Pilot (CPU, labelled, never read against the criterion): pop 24, gens 8, M 8."""
from __future__ import annotations
import argparse, dataclasses, json, time
import numpy as np, torch
import nback as nb
from prometheus.ananke import assays, search
from prometheus.ananke.engine import Controls
from prometheus.ananke.rng import H_int

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, required=True)
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--device", default="cuda")
ap.add_argument("--pilot", action="store_true")
a = ap.parse_args()
torch.set_num_threads(2)
nb.install()
ph, _, _, row = nb.m2()
sp = search.SearchSpec(**row["search"])
if a.pilot:
    sp = dataclasses.replace(sp, pop=24, gens=8)
env = nb.spec(a.n)
sseed = H_int(nb.NS, a.n, a.seed)
tag = f"{'PILOT_' if a.pilot else ''}n{a.n}_s{a.seed}"
t0 = time.time()
def log(c):
    print(tag, json.dumps(c), f"{time.time()-t0:.0f}s", flush=True)
res = search.evolve(ph, env, sseed, sp, device=a.device, log=log)
champ = np.asarray(res["champion"], dtype=np.int64)
# held-out (0x5F3) evaluation + no-memory baselines on the same worlds
hs = nb.seeds(nb.NS_HELD, a.n, a.seed, M=64)
def pa(g, ctrl=None):
    return assays.evaluate(ph, g[None], env, hs, ctrl=ctrl, device=a.device).pair_acc()[0]
pc = pa(champ)
bl = {"NULL": pa(nb.body("NULL", ph)[0]), "LAG0": pa(nb.body("LAG0", ph)[0])}
if a.n == 2:
    bl["P1S_lag1"] = pa(nb.body("P1S", ph)[0])
bname = max(bl, key=lambda k: bl[k].mean())
m, lo, hi = assays.pair_ci(pc)
dm, dlo, dhi = assays.pair_ci(pc - bl[bname])
zc = pa(champ, Controls(zero_comm=True))
ok = bool(lo > .60 and dlo > 0)
out = {"tag": tag, "n": a.n, "seed": a.seed, "search_seed": sseed, "spec": sp.to_dict(),
       "pilot": a.pilot, "evolve": res,
       "held_5F3": {"acc": float(m), "lo99": float(lo), "hi99": float(hi),
                    "baseline": bname, "baselines": {k: float(v.mean()) for k, v in bl.items()},
                    "diff": float(dm), "diff_lo99": float(dlo), "diff_hi99": float(dhi),
                    "zero_comm": float(zc.mean()), "SUCCESS": ok},
       "wall_s": time.time() - t0}
(nb.HERE / "out").mkdir(exist_ok=True)
(nb.HERE / "out" / f"search_{tag}.json").write_text(json.dumps(out, indent=1))
print(tag, "HELD", json.dumps(out["held_5F3"]), f"wall {out['wall_s']:.0f}s", flush=True)
