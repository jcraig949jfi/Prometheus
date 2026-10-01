"""Distinguishing test (OVERRIDE, diagnostic only): does the 12-line SBF plant work at the L8/C1 rows once the
genome is given prog_len 12 and channels 2? If yes, the binding constraint at those rows is the sampled genome
(length + channel count), not the physics."""
from v_common import *
import sbf
ck = Clock()
seeds = assays.world_seeds(V_DEV, 16)
vs = [(100, 1), (100, 2), (100, 3), (125, 4)]
res = {}
for c8 in ["48256f59", "1974a9cf", "333d6b2b"]:
    ph0, env = row_phys(c8)
    ph = ph0.replace(prog_len=12, channels=2)
    acc, st = veval(ph, np.stack([asm(ph, sbf.sbf(*v)) for v in vs]), env, seeds)
    res[c8] = [(v, summarize(acc[i]), int(st["collided"][i])) for i, v in enumerate(vs)]
    for r in res[c8]:
        print(c8, r)
save("sbf_l8_override_dev.json", {"res": res, "override": {"prog_len": 12, "channels": 2}, "cpu_s": ck.cpu()})
print(ck.cpu())
