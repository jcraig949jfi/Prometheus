"""Independent-path check: the 4222a5f7 SBF plant through H-PLANT hc.evaluate (c1b semantics) and through
prometheus.ananke.assays.evaluate (the C1 search's own evaluator, CPU eager), same W2VS worlds."""
from v_common import *
import sbf
ck = Clock()
ph, env = row_phys("4222a5f7")
g = asm(ph, sbf.sbf(100, 3))
seeds = assays.world_seeds(V_NS, 64)
r1 = hc.evaluate(ph, g, env, seeds); r1.pop("pairs")
r2 = assays.evaluate(ph, g[None], env, seeds, device="cpu", graph=False)
s2 = summarize(r2.acc[0])
# genome-space check: every field reachable by C1's random_genomes (fields 0..255, imm in [-128,127])
ok = bool((g[..., :4] >= 0).all() and (g[..., :4] < 256).all() and (g[..., 4] >= -128).all() and (g[..., 4] < 128).all())
out = {"hc_evaluate": r1, "assays_evaluate": s2, "sens_act": float(r2.sens_act[0]), "genome_in_C1_space": ok,
       "genome_shape": list(g.shape), "row_prog_len": ph.prog_len, "cpu_s": ck.cpu()}
print(out)
save("xcheck_4222.json", out)
