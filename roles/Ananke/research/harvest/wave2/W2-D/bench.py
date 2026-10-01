from w2d_common import *
r, ph, env, sp = flip_cell()
ck = Clock()
g = np.random.default_rng(0)
pop = search.random_genomes(g, 96, ph)
pop[0] = hp_plants.p_flip(ph)
seeds = assays.world_seeds(123, 8)
res = assays.evaluate(ph, pop, env, seeds, device="cpu")
print("96x8 eval", ck.done(), res.mean()[:3], res.sens_act[:3], res.sens_any[:3])
