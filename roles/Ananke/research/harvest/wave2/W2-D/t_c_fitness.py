"""Test (c) + known-answer gate: C1 objective on P-FLIP plant vs C1 champion at 6f82f9c7.
Gate: champion must reproduce recorded held acc and champ_train_final exactly on CPU."""
from w2d_common import *
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS
r, ph, env, sp = flip_cell()
ck = Clock()
S = r["search_seed"]
champ = np.asarray(r["result"]["champion"])
plant = hp_plants.p_flip(ph)
pop = np.stack([plant, champ])
sets = {"held": assays.world_seeds(H_int(S, HELD_NS), sp.M_held),
        "final": assays.world_seeds(H_int(S, FINAL_NS), sp.M_final)}
for gen in (0, 35):
    sets[f"train_g{gen}"] = assays.world_seeds(H_int(S, TRAIN_NS, gen), sp.M)
out = {"cell": FLIP_CELL, "search": sp.to_dict(), "sets": {}}
for name, seeds in sets.items():
    res = assays.evaluate(ph, pop, env, seeds, device="cpu")
    acc = res.mean()
    f = acc + sp.w_contrast * np.maximum(res.sens_act, 0) + sp.w_any * res.sens_any
    pa = res.pair_acc()
    cis = [assays.pair_ci(pa[i]) for i in range(2)]
    out["sets"][name] = {"acc": acc, "sens_act": res.sens_act, "sens_any": res.sens_any, "fit": f,
                         "ci99": [[float(c[1]), float(c[2])] for c in cis], "per_world": res.acc}
    print(name, "acc", acc.round(4), "contrast", res.sens_act.round(3), "any", res.sens_any.round(3), "fit", f.round(4))
out["gate"] = {"held_recorded": r["result"]["held"]["acc"], "held_cpu": float(out["sets"]["held"]["acc"][1]),
               "final_recorded": r["result"]["champ_train_final"], "final_cpu": float(out["sets"]["final"]["acc"][1])}
out["gate"]["pass"] = (abs(out["gate"]["held_recorded"]-out["gate"]["held_cpu"]) < 1e-9 and
                       abs(out["gate"]["final_recorded"]-out["gate"]["final_cpu"]) < 1e-9)
out["compute"] = ck.done()
print(out["gate"], out["compute"])
save("t_c_fitness.json", out)
