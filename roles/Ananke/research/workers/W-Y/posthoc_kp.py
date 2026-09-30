"""POST HOC (labelled; after the champion result). Normal run of 4781b0a1, M 128, ns 0x670: which Kp slots are
ever nonzero, anywhere (all sites) and at the readout, over the whole episode? -> out/posthoc_kp.json"""
import json
import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import wy  # noqa: E402
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402

ph, env, g, _ = wy.load("4781b0a1")
M = 128
seeds = assays.world_seeds(0x670, M)
ep = envs.build(ph, env, seeds)
ws1 = [seeds[m - (m % 2)] for m in range(M)]
w = World(ph, np.repeat(g[None], M, 0), ws1, device="cpu", ctrl=Controls(), schedule=ep.schedule)
ro = torch.as_tensor(ep.schedule.read_idx[:, 0], dtype=torch.int64)
ar = torch.arange(M)
L = ph.prog_len
nz_any = np.zeros(L)
nz_ro = np.zeros(L)
diff_ro = np.zeros(L)
T = env.T()
for t in range(T):
    w.step()
    kp = w.Kp
    nz_any += (kp != 0).any(1).float().mean(0).numpy()
    k = kp[ar, ro]
    nz_ro += (k != 0).float().mean(0).numpy()
    diff_ro += (k[0::2] != k[1::2]).float().mean(0).numpy()
res = {"frac_worlds_any_site_nonzero_mean_over_ticks": (nz_any / T).round(4).tolist(),
       "frac_readout_nonzero_mean_over_ticks": (nz_ro / T).round(4).tolist(),
       "frac_pairs_readout_mirror_diff_mean_over_ticks": (diff_ro / T).round(4).tolist(), "T": T}
(HERE / "out" / "posthoc_kp.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
