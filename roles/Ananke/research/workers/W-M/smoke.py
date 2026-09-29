import sys, time, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE))
import torch; torch.set_num_threads(2)
from prometheus.ananke import assays, envs, plants
import lens_ins6 as L
SEEDS = assays.world_seeds(0x7E57, 32)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
t=time.time()
ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
g = plants.plant("hold_latch", ph)
print("selfcheck latch", L.selfcheck(ph, g, HOLD, SEEDS, 6, 4), round(time.time()-t,1))
for name, ph, g in [("latch", ph, g), ("echo", plants.c1b_echo_physics(), plants.echo_hold(plants.c1b_echo_physics())[None]),
                    ("null", ph, plants.plant("null", ph))]:
    t=time.time()
    r = L.mixture_scan(ph, g, HOLD, SEEDS, list(range(-1, 10)), "single", list(range(1, 12)), n_boot=200)
    print(name, r["normal"], round(time.time()-t,1))
    for o, c in r["offsets"].items():
        print(" ", o, c["class"], c["eligible"], {k: (round(c[k],2) if c[k] is not None else None) for k in ("fS","fC","fN","fX","ftie","identity","phi")})
