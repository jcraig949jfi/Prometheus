"""Is LC2 a bound? Compare plant accuracy with LC2 computed on the SAME DEV worlds (positions), many reps.
usage: python check_bound_vs_plant.py cell8 [cell8...]  (uses the best screen2 variant of each row)."""
import sys
import numpy as np
from wj_common import *
import lc2
import plants_wj as pw
from screen2 import build
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics

scr = json.load(open(OUT / "screen2.json"))["rows"]
out = {}
for c8 in sys.argv[1:]:
    r = [x for x in xor_evolve() if x["cell_id"].startswith(c8)][0]
    best = max([s for s in scr if s["cell"] == r["cell_id"]], key=lambda s: s["acc"])
    ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(WJ_DEV, 16)
    ep = envs.build(ph0, env, seeds)
    sidx = ep.schedule.sense_idx.numpy(); ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph0)
    rng = np.random.default_rng(5)
    modes = ["all" if (ph0.dest_mode == "all" and ph0.topology != "global") else "sample"]
    f = {m: [] for m in modes}
    for m in modes:
        for b in range(0, 16, 2):
            fb = []
            for k in range(env.trials):
                for _ in range(16):
                    i1, i2 = lc2.reach_trial(ph0, env, sidx[b][:2], int(ridx[b]), k * env.period(), rng, nbr, dist, m)
                    fb.append(i1 and i2)
            f[m].append(float(np.mean(fb)))
    lines, ev, f2 = build(ph0, env, best["fam"], best["opts"])
    ph, ov = pw.fit(ph0, lines, ev, f2, strict=False)
    e = hc.evaluate(ph, pw.genome(ph, lines), env, seeds)
    pairs = np.array(e["pairs"])
    out[c8] = {"variant": best["fam"] + str(best["opts"]), "plant_pairs": pairs.tolist(),
               "lc2_ub_pairs": {m: [0.5 + x / 2 for x in v] for m, v in f.items()},
               "plant_mean": float(pairs.mean()), "lc2_mean": {m: 0.5 + float(np.mean(v)) / 2 for m, v in f.items()},
               "route_writes": e["stats"]["route_writes"]}
    print(c8, out[c8]["variant"], "plant", np.round(pairs, 3), "ub", {m: np.round(0.5 + np.array(v) / 2, 3) for m, v in f.items()},
          "route_writes", e["stats"]["route_writes"])
save("check_bound_vs_plant.json", out)
