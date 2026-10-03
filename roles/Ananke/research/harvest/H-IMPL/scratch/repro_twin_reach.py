"""H-IMPL repro: twin_assay perturbs EVERY sensor column but measures reach from
sensor 0, so a program with NO communication reports distal reach on MAJ/XOR."""
import numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays, envs, plants
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics

ph = Physics(topology="torus", n_sites=100, radius=1, state_dim=2, payload_width=1, channels=1,
             prog_len=4, rules=1).validate()
g = plants.plant("sense_copy", ph)          # S0 := SENSE; never emits (O.emit stays 0)
seeds = assays.world_seeds(0xB0B, 16)
for fam in ("RELAY", "HOLD", "MAJ", "XOR"):
    env = envs.EnvSpec(family=fam, d=3, delta=8, gap=8, trials=12)
    tw = assays.twin_assay(ph, g[None], env, seeds, device="cpu")
    ev = assays.evaluate(ph, g[None], env, seeds, device="cpu", graph=False)
    zc = assays.evaluate(ph, g[None], env, seeds, ctrl=Controls(zero_comm=True), device="cpu", graph=False)
    print(f"{fam:5s} emit_rate={ev.tel['emit_rate'][0]:.3f} acc={ev.mean()[0]:.3f} zero_comm_acc={zc.mean()[0]:.3f} "
          f"twin reach={tw['reach'][0]:.2f} beyond_hop={tw['beyond_hop'][0]:.2f} readout_flipped={tw['readout_flipped'][0]:.2f}")
