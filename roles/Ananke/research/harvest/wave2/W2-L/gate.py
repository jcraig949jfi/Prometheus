"""Known-answer gate: P-FLIP at d9cc cell 6f82f9c7, 32 pairs (row held seeds), plus timing."""
from w2l_common import *
ck = Clock()
r = hc.row("6f82f9c7d51bcef1")
ph, env = cell(r)
assert ph.digest().startswith("d9cc")
s = held_seeds(r)
out = {"plant": hc.evaluate(ph, hp_plants.p_flip(ph), env, s)}
t1 = ck.done()
out["relay_flood"] = comm_delta(ph, plants.plant("relay_flood", ph), env, s)
out["compute"] = ck.done(); out["t_plant"] = t1
for k in ("plant", "relay_flood"):
    print(k, {kk: round(v, 4) for kk, v in out[k].items() if isinstance(v, float)})
print(out["compute"], t1)
save("gate.json", out)
