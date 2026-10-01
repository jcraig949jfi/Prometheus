"""Mirror twins share EVERY physics draw, including additive payload NOISE (engine.py:515-518 keys
the noise hash on ws,t,n only). A linear mechanism's twin difference S0_lead - S0_twin therefore
cancels the noise exactly, so the selection bonus sens_act (assays.py:83, search.py:94) is blind to
noise while accuracy is not. Toy: sensor emits PAY0 = SENSE >> k (k sets the code amplitude),
every site re-emits, actuator S0 := IN0_0."""
from common import *
import numpy as np
from prometheus.ananke import envs, assays, plants
from prometheus.ananke.physics import Physics

def genome(ph, k):
    return plants.assemble(ph, [
        ("CONST", "EMIT", 0, 0, 1),
        ("SHR", "PAY0", "SENSE", k, 0),     # bf = b field = k -> shift k
        ("MOV", "S0", "IN0_0", 0, 0),
    ])[None][None]

env = envs.EnvSpec(family="RELAY", d=1, delta=2, trials=12)
seeds = assays.world_seeds(0xC0FFEE, 64)
print("noise  shift  amp   acc     sens_act  fitness_bonus(.10*max(sens_act,0))")
for noise in (0, 16, 64):
    ph = Physics(topology="ring", n_sites=36, radius=1, dest_mode="all", lat_base=1, noise=noise,
                 payload_width=1, channels=1, prog_len=3)
    for k in (2, 5, 8):
        G = genome(ph, k)
        r = assays.evaluate(ph, G, env, seeds, device="cpu", graph=False)
        print(f"{noise:5d}  {k:5d}  {256>>k:4d}  {r.mean()[0]:.3f}   {r.sens_act[0]:+.3f}    {0.10*max(r.sens_act[0],0):.3f}")
