"""Scope check for the common-mode finding: linear readout (S0 := IN) vs thresholded readout
(S0 := sign(IN)*256) at noise 64, code amplitude 1..64."""
from common import *
from prometheus.ananke import envs, assays, plants
from prometheus.ananke.physics import Physics
env = envs.EnvSpec(family="RELAY", d=1, delta=2, trials=12)
seeds = assays.world_seeds(0xC0FFEE, 64)
ph = Physics(topology="ring", n_sites=36, radius=1, dest_mode="all", lat_base=1, noise=64, payload_width=1, channels=1, prog_len=5)
for k in (2, 5, 8):
    lin = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1), ("SHR", "PAY0", "SENSE", k, 0), ("MOV", "S0", "IN0_0", 0, 0)])
    thr = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1), ("SHR", "PAY0", "SENSE", k, 0),
                               ("GT", "T0", "IN0_0", "ZERO", 0), ("GT", "T1", "ZERO", "IN0_0", 0), ("SUB", "S0", "T0", "T1", 0)])
    for name, G in (("linear", lin), ("threshold", thr)):
        r = assays.evaluate(ph, G[None][None], env, seeds, device="cpu", graph=False)
        print(f"amp {256>>k:3d} {name:9s}: acc {r.mean()[0]:.3f}  sens_act {r.sens_act[0]:+.3f}")
