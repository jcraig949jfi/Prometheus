"""Champion truth tables. python run_champ.py <cell> main <trials...>   (half cube, offsets 1..15)
                       python run_champ.py <cell> verify <trial>        (FULL cube incl. w, offsets -1..15)
                       python run_champ.py <cell> check                 (C1 bit-identity vs lens_swap)"""
import json, sys, time
import numpy as np, torch
import common
from prometheus.ananke import assays
import tt
torch.set_num_threads(2)
name, mode = sys.argv[1], sys.argv[2]
ph, env, g, row = common.load(name)
SEEDS = assays.world_seeds(common.SEED_NS, 256)
OUT = common.HERE / "out"


def comps_for(verify):
    c = tt.coarse_components(ph, include_inert=verify)
    if not verify and name == "369f5a5b":
        c.pop("w", None)          # PLAN s1: inert (dest 'all'); kept in the verify slice
    return c


if mode == "check":
    r = {"cell": row["cell_id"], "C1": tt.check_vs_lens(ph, g, env, SEEDS[:32], 5, 6)}
    print(r, flush=True)
    json.dump(r, open(OUT / f"C1_{name}.json", "w"))
elif mode == "main":
    comps = comps_for(False)
    names = list(comps)
    half = [z for z in tt.all_subsets(len(names)) if z[0] == 0]
    offs = list(range(1, 16))
    for k in map(int, sys.argv[3:]):
        t = time.time()
        res, ep = tt.run_table(ph, g, env, SEEDS, k, offs, comps, half)
        np.savez_compressed(OUT / f"tt_{name}_main_k{k}.npz", names=np.array(names), subs=np.array(half),
                            y=ep.y[:, k], offsets=np.array(offs), **{f"o{o}": res[o] for o in offs})
        print(name, "trial", k, round(time.time() - t), "s", flush=True)
elif mode == "verify":
    comps = comps_for(True)
    names = list(comps)
    subs = tt.all_subsets(len(names))
    offs = [-1, 1, 5, 10, 14]          # deviation D2 (budget): verify slice offsets
    k = int(sys.argv[3])
    t = time.time()
    res, ep = tt.run_table(ph, g, env, SEEDS, k, offs, comps, subs, chunk=64)
    np.savez_compressed(OUT / f"tt_{name}_verify_k{k}.npz", names=np.array(names), subs=np.array(subs),
                        y=ep.y[:, k], offsets=np.array(offs), **{f"o{o}": res[o] for o in offs})
    print(name, "verify trial", k, round(time.time() - t), "s", flush=True)
