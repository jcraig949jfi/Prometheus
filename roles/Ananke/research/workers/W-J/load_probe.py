"""Descriptive: arrival load K per receiver-tick in the base physics, under
each champion's own operator (how often is K > cap = 2?). 1 thread."""
import sys, pathlib, json, numpy as np, torch
torch.set_num_threads(1)
from prometheus.ananke import c1b_run, lens, assays
from prometheus.ananke.rng import H_int
out = {}
for cid in sys.argv[1:]:
    ph, env, g, row = c1b_run.load(cid)
    seeds = assays.world_seeds(H_int(0x5EF, 0x10AD), 16)
    def rec(w, t):
        slot = (w.t) % w.LM
        K = w.Mcnt[slot].sum(-1)                  # arrivals about to be delivered next tick
        a = w.read_idx[:, 0]
        return (K.float().mean().item(), (K > 2).float().mean().item(),
                K[torch.arange(w.B), a].float().mean().item(), (K[torch.arange(w.B), a] > 2).float().mean().item())
    tr = lens.run(ph, g, env, seeds, recorders={"k": rec}, device="cpu")
    k = np.array(tr.rec["k"])
    out[cid] = {"collision": ph.collision, "mean_K_all": float(k[:, 0].mean()), "P(K>2)_all": float(k[:, 1].mean()),
                "mean_K_actuator": float(k[:, 2].mean()), "P(K>2)_actuator": float(k[:, 3].mean())}
    print(cid, out[cid], flush=True)
pathlib.Path("roles/Ananke/research/workers/W-J/out/load_probe.json").write_text(json.dumps(out, indent=1))
