"""Mechanism check for the 4222a5f7 SBF plant: replace each line by NOP in turn (DEV worlds, strict genome)."""
from v_common import *
import sbf
ck = Clock()
ph, env = row_phys("4222a5f7")
base = sbf.sbf(100, 3)
seeds = assays.world_seeds(V_DEV, 16)
G = [asm(ph, base)]
for i in range(len(base)):
    L = list(base); L[i] = ("NOP", 0, 0, 0, 0); G.append(asm(ph, L))
acc, st = veval(ph, np.stack(G), env, seeds)
names = ["full"] + [f"-{i}:{base[i][0]} {base[i][1]}" for i in range(len(base))]
res = {n: summarize(acc[k]) | {"collided": int(st["collided"][k])} for k, n in enumerate(names)}
for n, s in res.items():
    print(n, s["acc"], s["lo99"], s["collided"])
save("sbf_ablate_dev.json", {"res": res, "cpu_s": ck.cpu()})
