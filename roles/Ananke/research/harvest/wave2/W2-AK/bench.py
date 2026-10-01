"""Timing probe + cell description: one 96x8 generation-sized evaluation per cell."""
from ak_common import *
out = {}
for p in CELLS:
    r, ph, env, sp = cell(p)
    print(p, r["cell_id"], r["wave"], r["labels"], "\n search", sp.to_dict(), "\n env", r["env"], "\n levels", r.get("levels"))
    print(" phys", {k: v for k, v in ph.to_dict().items()})
    g = np.random.default_rng(1); pop = search.random_genomes(g, sp.pop, ph)
    ck = Clock(); res = ev(ph, pop, env, assays.world_seeds(123, sp.M)); c = ck.done()
    print(" gen-eval", c, "T", env.T(), "maxacc", res.mean().max()); out[p] = c
save("bench.json", out)
