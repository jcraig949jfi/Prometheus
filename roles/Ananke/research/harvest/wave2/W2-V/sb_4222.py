"""SB family at 4222a5f7 STRICT (row genome: prog_len 12, D8, P1, C4, rules 4 broadcast). DEV worlds."""
from v_common import *
from sb_grid import sb

ck = Clock()
seeds = assays.world_seeds(V_DEV, 16)
c8 = "4222a5f7"
ph, env = row_phys(c8)
variants = [(g, ci, cs) for g in (1, 2) for (ci, cs) in ((25, 0), (50, 0), (100, 0), (100, 1), (100, 2), (125, 3), (125, 4))]
G = np.stack([asm(ph, sb(*v)) for v in variants])
acc, st = veval(ph, G, env, seeds)
res = [(v, summarize(a), int(st["collided"][i]), int(st["emitters"][i])) for i, (v, a) in enumerate(zip(variants, acc))]
for r in res:
    print(r)
save("sb_4222_dev.json", {"res": res, "cpu_s": ck.cpu(), "strict": True})
print(ck.cpu())
