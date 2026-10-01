"""Test (b): plant-seeded copy of search.evolve (W2-D t_b_seeded.py, itself a verbatim copy of search.evolve with
gen-0 index 0 overwritten by the plant), adapted to a cell-prefix argument and a third seed. Eager CPU.
usage: python t_b_seeded.py 8743|f29c A|B|C GENS
  A = C1's own search_seed (other 95 genomes = C1's own gen-0 population); B = H(seed,0x5732) (W2-D's B);
  C = H(seed,0x5733)."""
import dataclasses
from ak_common import *
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS, random_genomes, mutate, crossover
p, which, gens = sys.argv[1], sys.argv[2], int(sys.argv[3])
r, ph, env, sp0 = cell(p)
sp = dataclasses.replace(sp0, gens=gens)
search_seed = {"A": r["search_seed"], "B": H_int(r["search_seed"], 0x5732), "C": H_int(r["search_seed"], 0x5733)}[which]
pl = plant(p, ph)
NW, NR = ph.n_write(), ph.n_read()
def reduced(x):
    return np.stack([x[..., 0] % 16, x[..., 1] % NW, x[..., 2] % NR, x[..., 3] % NR, x[..., 3] & 15, x[..., 4]], -1)
def ldiff(x):
    return int((reduced(x) != reduced(pl)).any(-1).sum())
ck = Clock()
g = np.random.default_rng(search_seed)
pop = random_genomes(g, sp.pop, ph)
pop[0] = pl
curve = []
for gen in range(sp.gens):
    seeds = assays.world_seeds(H_int(search_seed, TRAIN_NS, gen), sp.M)
    res = ev(ph, pop, env, seeds)
    acc = res.mean()
    f = acc + sp.w_contrast * np.maximum(res.sens_act, 0) + sp.w_any * res.sens_any
    order = np.argsort(-f, kind="stable")
    is_plant = np.array([np.array_equal(q, pl) for q in pop])
    lines = np.array([ldiff(q) for q in pop])
    rank = [int(np.where(order == i)[0][0]) for i in np.flatnonzero(is_plant)]
    nonplant_f = np.sort(f[~is_plant])[::-1]
    rec = {"gen": gen, "best_fit": float(f[order[0]]), "best_acc": float(acc[order[0]]), "best_lines_diff": int(lines[order[0]]),
           "max_acc": float(acc.max()), "mean_acc": float(acc.mean()),
           "n_exact_plant": int(is_plant.sum()), "n_reduced_equal": int((lines == 0).sum()), "n_lines_diff_le2": int((lines <= 2).sum()),
           "plant_ranks": rank, "plant_acc": [float(acc[i]) for i in np.flatnonzero(is_plant)][:3],
           "plant_fit": [float(f[i]) for i in np.flatnonzero(is_plant)][:3],
           "n_acc_ge_.70": int((acc >= .70).sum()), "n_acc_.60_.70": int(((acc >= .6) & (acc < .7)).sum()),
           "nonplant_fit_top4": nonplant_f[:4].round(4).tolist(),
           "max_acc_nonplant": float(acc[~is_plant].max()) if (~is_plant).any() else None,
           "wall_s": round(time.time() - ck.w0, 1), "cpu_s": round(time.process_time() - ck.t0, 1)}
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
rf = assays.evaluate(ph, pop, env, fseeds, device="cpu", graph=False)
ci = int(np.argmax(rf.mean()))
champ = pop[ci]
hseeds = assays.world_seeds(H_int(search_seed, HELD_NS), sp.M_held)
rh = ev(ph, champ[None], env, hseeds)
rz = ev(ph, champ[None], env, hseeds, ctrl=Controls(zero_comm=True))
m, lo, hi = assays.pair_ci(rh.pair_acc()[0])
dm, dlo, dhi = assays.pair_ci(rh.pair_acc()[0] - rz.pair_acc()[0])
fin = rf.mean(); isp = np.array([np.array_equal(q, pl) for q in pop])
out = {"cell": r["cell_id"], "run": which, "search_seed": search_seed, "search": sp.to_dict(), "gens_truncated_from": sp0.gens,
       "curve": curve, "final_pop_acc": fin, "final_n_ge_.70": int((fin >= .7).sum()),
       "final_plant_acc": [float(fin[i]) for i in np.flatnonzero(isp)], "final_n_exact_plant": int(isp.sum()),
       "champ_is_plant": bool(np.array_equal(champ, pl)), "champ_train_final": float(fin[ci]),
       "champ_lines_diff_from_plant": ldiff(champ),
       "held": {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "zero_comm": float(rz.pair_acc()[0].mean()),
                "comm_delta_lo99": float(dlo)},
       "retained": bool(lo > 0.55 and (np.array_equal(champ, pl) or ldiff(champ) <= 4)),
       "compute": ck.done()}
print({k: v for k, v in out.items() if k not in ("curve", "final_pop_acc")})
save(f"t_b_seeded_{p}_{which}.json", out)
