"""Test (b): plant-seeded copy of search.evolve at 6f82f9c7. See PLAN_b_seeded.md. usage: python t_b_seeded.py A|B"""
import sys, dataclasses
from w2d_common import *
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS, random_genomes, mutate, crossover
from prometheus.ananke.engine import Controls
which = sys.argv[1]
r, ph, env, sp0 = flip_cell()
sp = dataclasses.replace(sp0, gens=int(sys.argv[2]) if len(sys.argv) > 2 else 4)
search_seed = r["search_seed"] if which == "A" else H_int(r["search_seed"], 0x5732)
plant = hp_plants.p_flip(ph)
ck = Clock()
g = np.random.default_rng(search_seed)
pop = random_genomes(g, sp.pop, ph)
pop[0] = plant
curve = []
for gen in range(sp.gens):
    seeds = assays.world_seeds(H_int(search_seed, TRAIN_NS, gen), sp.M)
    res = assays.evaluate(ph, pop, env, seeds, device="cpu")
    acc = res.mean()
    f = acc + sp.w_contrast * np.maximum(res.sens_act, 0) + sp.w_any * res.sens_any
    order = np.argsort(-f, kind="stable")
    is_plant = np.array([np.array_equal(p, plant) for p in pop])
    rank = [int(np.where(order == i)[0][0]) for i in np.flatnonzero(is_plant)]
    nonplant_f = np.sort(f[~is_plant])[::-1]
    rec = {"gen": gen, "best_fit": float(f[order[0]]), "best_acc": float(acc[order[0]]), "max_acc": float(acc.max()),
           "mean_acc": float(acc.mean()), "n_exact_plant": int(is_plant.sum()), "plant_ranks": rank,
           "plant_acc": [float(acc[i]) for i in np.flatnonzero(is_plant)][:3],
           "n_acc_ge_.90": int((acc >= .90).sum()), "n_acc_.60_.90": int(((acc >= .6) & (acc < .9)).sum()),
           "nonplant_fit_top4": nonplant_f[:4].round(4).tolist(),
           "max_acc_nonplant": float(acc[~is_plant].max()) if (~is_plant).any() else None,
           "wall_s": round(time.time() - ck.w0, 1)}
    curve.append(rec); print(rec, flush=True)
    if gen == sp.gens - 1:
        break
    k = max(2, int(sp.pop * sp.trunc))
    parents = pop[order[:k]]
    nxt = [pop[order[i]] for i in range(sp.elite)]
    while len(nxt) < sp.pop:
        a = parents[g.integers(k)]
        if g.random() < sp.p_cross:
            a = crossover(g, a, parents[g.integers(k)])
        nxt.append(mutate(g, a, sp))
    pop = np.stack(nxt)
fseeds = assays.world_seeds(H_int(search_seed, FINAL_NS), sp.M_final)
rf = assays.evaluate(ph, pop, env, fseeds, device="cpu")
ci = int(np.argmax(rf.mean()))
champ = pop[ci]
hseeds = assays.world_seeds(H_int(search_seed, HELD_NS), sp.M_held)
rh = assays.evaluate(ph, champ[None], env, hseeds, device="cpu")
rz = assays.evaluate(ph, champ[None], env, hseeds, ctrl=Controls(zero_comm=True), device="cpu")
m, lo, hi = assays.pair_ci(rh.pair_acc()[0])
out = {"run": which, "search_seed": search_seed, "search": sp.to_dict(), "curve": curve,
       "final_pop_acc": rf.mean(), "final_n_ge_.90": int((rf.mean() >= .9).sum()),
       "champ_is_plant": bool(np.array_equal(champ, plant)), "champ_train_final": float(rf.mean()[ci]),
       "champ_lines_diff_from_plant": int((champ != plant).any(-1).sum()),
       "held": {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "zero_comm": float(rz.mean()[0])},
       "compute": ck.done()}
print({k: v for k, v in out.items() if k not in ("curve", "final_pop_acc")})
save(f"t_b_seeded_{which}.json", out)
