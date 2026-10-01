"""Known-answer gate + test (c) at one MAJ cell (W2-D t_c_fitness.py adapted to the cell prefix argument).
Gate: recorded champion reproduces held acc and champ_train_final exactly on CPU (C1 seed namespaces).
(c): C1 shaped fitness f = acc + w_contrast*max(sens_act,0) + w_any*sens_any of plant vs champion on
train gen 0, train last gen, final and held worlds.  usage: python t_c_fitness.py 8743|f29c"""
from ak_common import *
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS
p = sys.argv[1]
r, ph, env, sp = cell(p)
ck = Clock()
S = r["search_seed"]
champ = np.asarray(r["result"]["champion"])
pl = plant(p, ph)
pop = np.stack([pl, champ])
sets = {"held": assays.world_seeds(H_int(S, HELD_NS), sp.M_held),
        "final": assays.world_seeds(H_int(S, FINAL_NS), sp.M_final)}
for gen in (0, sp.gens - 1):
    sets[f"train_g{gen}"] = assays.world_seeds(H_int(S, TRAIN_NS, gen), sp.M)
out = {"cell": r["cell_id"], "search": sp.to_dict(), "sets": {}}
for name, seeds in sets.items():
    res = ev(ph, pop, env, seeds)
    acc = res.mean()
    f = acc + sp.w_contrast * np.maximum(res.sens_act, 0) + sp.w_any * res.sens_any
    pa = res.pair_acc(); cis = [assays.pair_ci(pa[i]) for i in range(2)]
    d = assays.pair_ci(pa[0] - pa[1])
    out["sets"][name] = {"acc": acc, "sens_act": res.sens_act, "sens_any": res.sens_any, "fit": f,
                         "ci99": [[float(c[1]), float(c[2])] for c in cis], "plant_minus_champ": [float(x) for x in d]}
    print(name, "acc", acc.round(4), "contrast", res.sens_act.round(3), "any", res.sens_any.round(3), "fit", f.round(4),
          "p-c", np.round(d, 3), flush=True)
out["gate"] = {"held_recorded": r["result"]["held"]["acc"], "held_cpu": float(out["sets"]["held"]["acc"][1]),
               "final_recorded": r["result"]["champ_train_final"], "final_cpu": float(out["sets"]["final"]["acc"][1])}
out["gate"]["pass"] = (abs(out["gate"]["held_recorded"] - out["gate"]["held_cpu"]) < 1e-9 and
                       abs(out["gate"]["final_recorded"] - out["gate"]["final_cpu"]) < 1e-9)
out["compute"] = ck.done()
print(out["gate"], out["compute"])
save(f"t_c_fitness_{p}.json", out)
