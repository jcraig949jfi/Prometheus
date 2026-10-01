"""economy 'high' = income 4/tick, c_op 1 per non-NOP op, c_mem 1 per nonzero S, c_emit 4 per copy,
e_max 100 (campaign.ECONOMY). Energy never gates OPS, only emission (engine.py:386-393). relay_flood has
12 non-NOP instructions, so an awake site loses >= 8/tick, hits E=0 within ~13 ticks and can never
afford an emission again. Prediction: under 'high' relay_flood emits only in the first ~13 ticks, so
plant accuracy ~ (first trial(s) + 0.5*rest). Check the A0 rows too."""
from common import *
import gzip, json, collections, numpy as np
from prometheus.ananke import envs, assays, plants
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from prometheus.ananke.campaign import ECONOMY
for eco in ("off", "low", "high"):
    for per in (1, 2):
        ph = Physics(topology="ring", n_sites=36, radius=1, dest_mode="all", prog_len=12, update_period=per, **ECONOMY[eco])
        env = envs.EnvSpec(family="RELAY", d=1, delta=4, trials=12)
        seeds = assays.world_seeds(5, 16)
        G = plants.plant("relay_flood", ph)
        ep = envs.build(ph, env, seeds)
        w = World(ph, np.repeat(G[None], 16, 0), [seeds[m - m % 2] for m in range(16)], device="cpu", schedule=ep.schedule)
        last_emit = -1
        for t in range(env.T()):
            w.step()
            if bool(w.last_emit.any()): last_emit = t
        acc = envs.score(ep, w.trace.numpy()).mean()
        print(f"economy {eco:4s} period {per}: plant acc {acc:.3f}  last tick with any emission {last_emit:3d} of {env.T()}  mean E end {float(w.E.float().mean()):.1f}")
ROOT2 = ROOT
R = [json.loads(l) for l in gzip.open(ROOT2/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
c = collections.defaultdict(list)
for r in R:
    if r["wave"] == "A0" and r["env"]["family"] == "RELAY":
        c[r["levels"]["economy"]].append(r["result"]["plant"]["acc"])
for k, v in c.items():
    v = np.array(v); print(f"A0 RELAY economy {k:4s}: n {len(v)}  plant acc max {v.max():.3f}  frac >= .75: {np.mean(v >= .75):.3f}")
