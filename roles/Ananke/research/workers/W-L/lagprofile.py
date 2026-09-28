"""POST-HOC (not preregistered): lag-agreement profile. For each champion,
P(sign S0 at readout k == c_{k-j}) for j = 0..4 (zero answers count .5),
pooled over trials k >= 4, on 256 fresh worlds (0x5F3 key 0x1A6). A selective
n-back store peaks at j = n only; an integrator agrees with every past cue."""
import json, glob
import numpy as np, torch
import nback as nb
from prometheus.ananke import lens, plants
torch.set_num_threads(2)
nb.install()
ph = nb.m2()[0]
seeds = nb.seeds(nb.NS_HELD, 0x1A6, M=256)
def integ(ph):
    b = plants.assemble(ph, [("ADD", "S0", "S0", "SENSE", 0)])   # W-G C-EFF idiom
    return b[None]
items = [(f"search_{t}", t) for t in ["n0_s0","n0_s1","n1_s0","n1_s1","n1_s2","n1_s3","n2_s0","n2_s1","n2_s2","n2_s3"]]
res = {}
def prof(g, n):
    env = nb.spec(n)
    ep = nb.build_nback(ph, env, seeds)
    tr = lens.run(ph, g, env, seeds, ep=ep, device="cuda")
    s0 = tr.trace[ep.ro_tick, np.arange(len(seeds))[:, None], 0]      # [B, trials]
    c = ep.meta["cues"]
    out = {}
    for j in range(5):
        ks = [k for k in range(4, env.trials)]
        a = np.where(s0[:, ks] == 0, .5, (np.sign(s0[:, ks]) == c[:, [k - j for k in ks]]).astype(float))
        out[j] = round(float(a.mean()), 3)
    return out
for name, n in (("PLANT_P1S", 1), ("PLANT_P2S", 2), ("PLANT_LAG0", 0), ("PLANT_INTEGRATOR", 1)):
    g = integ(ph) if name == "PLANT_INTEGRATOR" else nb.body(name[6:], ph)[0]
    res[name] = prof(g, n); print(name, res[name], flush=True)
for f, t in items:
    d = json.load(open(nb.HERE / "out" / f"{f}.json"))
    res[t] = {"SUCCESS": d["held_5F3"]["SUCCESS"], "lags": prof(np.asarray(d["evolve"]["champion"], dtype=np.int64), d["n"])}
    print(t, res[t], flush=True)
(nb.HERE / "out" / "lagprofile.json").write_text(json.dumps(res, indent=1))
