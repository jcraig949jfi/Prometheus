"""campaign.flip_state_transplant (PREREG s9 FLIP adapted-state transplant): donor and recipient are built
from the SAME seeds, genome and schedule, so after T_half they are bit-identical and
assays.transplant_state raises RuntimeError('NOT_APPLICABLE: transplant changed nothing').
Prediction: the branch can never return data; a FLIP adjudication cell would FAIL (counted toward PARK)."""
from common import *
import numpy as np
from prometheus.ananke import campaign, envs, search, plants
from prometheus.ananke.physics import Physics
ph = Physics(topology="ring", n_sites=24, radius=1, dest_mode="all", prog_len=12, wimm=1, plastic_route=1)
env = envs.EnvSpec(family="FLIP", d=1, delta=4, trials=16, block=4)
spec = {"search_seed": 12345, "search": search.SearchSpec().to_dict()}
for name, G in (("relay_flood", plants.plant("relay_flood", ph)),
                ("random", search.random_genomes(np.random.default_rng(0), 1, ph)[0])):
    try:
        out = campaign.flip_state_transplant(ph, G, env, spec, "cpu")
        print(name, "RETURNED", out)
    except Exception as e:
        print(name, "RAISED", type(e).__name__, e)
