"""H-SCI small check: in MAJ champions, does the readout follow ONE sensor or
the majority? Normal run only (no intervention), CPU, 2 threads.
Per scored (world, trial): sign(S0 at readout) vs each sensor's flipped cue
sign and vs the 5-sensor majority. Ties (S0 == 0) excluded from agreement."""
import os, sys, json
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
import numpy as np, torch
torch.set_num_threads(2)
sys.path.insert(0, os.getcwd())
from prometheus.ananke import assays, c1b_run, envs, lens

out = {}
for cell in sys.argv[1:]:
    ph, env, g, _ = c1b_run.load(cell)
    seeds = assays.world_seeds(0x5C1, 128)
    tr = lens.run(ph, g, env, seeds, device="cpu")
    ep = tr.ep
    B, K = ep.y.shape
    Pd = env.period()
    sv = ep.schedule.sense_val.numpy()           # [T, B, 5]
    s0 = tr.trace[ep.ro_tick, np.arange(B)[:, None], 0]   # [B, K]
    cue = np.stack([np.sign(sv[k * Pd, :, :]) for k in range(K)], 1)  # [B, K, 5]
    maj = np.sign(cue.sum(-1))
    dec = s0 != 0
    res = {"acc": float(tr.per_trial.mean()), "tie_frac": float(1 - dec.mean())}
    a = np.sign(s0)
    for j in range(cue.shape[-1]):
        res[f"agree_s{j}"] = float((a[dec] == cue[..., j][dec]).mean())
    res["agree_maj"] = float((a[dec] == maj[dec]).mean())
    res["agree_y"] = float((a[dec] == ep.y[dec]).mean())
    # ceiling references
    res["maj_vs_y"] = float((maj == ep.y).mean())
    out[cell] = res
    print(cell, json.dumps(res))
json.dump(out, open("roles/Ananke/research/harvest/H-SCI/sensor_agreement.json", "w"), indent=1)
