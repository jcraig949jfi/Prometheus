"""PREREG s2: 'XOR single-input = 0.500 exactly'. Mirror twins negate x1 only (envs.py:201), so a reader of
x2 alone is exactly .500 per pair, but a reader of x1 alone is .500 only in expectation.
Check: S0 := SENSE at each sensor with sensor == actuator (leak env), and a one-hop relay from sensor k."""
from common import *
import numpy as np
from prometheus.ananke import envs, assays, plants
from prometheus.ananke.physics import Physics
ph = Physics(topology="global", n_sites=16, dest_mode="sample", fanout=15, prog_len=3, payload_width=1, channels=1)
G = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1), ("MOV", "PAY0", "SENSE", 0, 0), ("MOV", "S0", "IN0_0", 0, 0)])
env = envs.EnvSpec(family="XOR", d=1, delta=1, trials=12, cue_len=1)
seeds = assays.world_seeds(99, 64)
ep = envs.build(ph, env, seeds)
for keep in (0, 1):
    sv = ep.schedule.sense_val.clone(); sv[:, :, 1 - keep] = 0          # only sensor `keep` speaks
    import dataclasses
    from prometheus.ananke.engine import World, Schedule
    sch = Schedule(ep.schedule.sense_idx, sv, ep.schedule.read_idx)
    ws = [seeds[m - m % 2] for m in range(64)]
    w = World(ph, np.repeat(G[None, None], 64, 0), ws, device="cpu", schedule=sch)
    w.run(env.T(), graph=False)
    pair = envs.score(ep, w.trace.numpy()).reshape(32, 2).mean(1)
    print(f"only x{keep+1} transmitted (fanout 15 of 15 others -> actuator always hears it): mean {pair.mean():.4f}, "
          f"pairs exactly .5: {np.mean(pair == 0.5):.2f}, min/max pair {pair.min():.3f}/{pair.max():.3f}")
