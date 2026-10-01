"""W-V POST HOC (labelled, not in PLAN): 4781b0a1 normal run, ns 0x650 M 128. Per offset o (trials 1..11):
fraction of mirror pairs whose (a) readout S1, (b) readout S (any), (c) readout Kp, (d) readout inbox, (e) sensor j
S1, differ between partners; and (f) per sensor, mirror-different in-flight traffic to the readout.
Also: when (relative to t0) the readout's final-window arrivals were emitted. python posthoc_state.py"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import torch

import wv
from prometheus.ananke import assays, envs

ph, env, g, _ = wv.load("4781b0a1")
M = 128
seeds = assays.world_seeds(0x650, M)
ep = envs.build(ph, env, seeds)
w = wv.TagWorld(ph, np.repeat(g[None], M, 0), [seeds[m - (m % 2)] for m in range(M)], device="cpu",
                schedule=ep.schedule)
Pd = env.period()
bi = torch.arange(M)
ro = w.ro
sidx = w.sch_idx
acc = {}
for t in range(env.T()):
    w.step()
    k, o = divmod(t, Pd)
    if not (1 <= k <= 11) or o > 16:
        continue
    A, B = slice(0, None, 2), slice(1, None, 2)
    r = {}
    S1 = w.S[bi, ro, 1]
    r["ro_S1"] = (S1[A] != S1[B]).float().mean().item()
    Sa = w.S[bi, ro]
    r["ro_S"] = (Sa[A] != Sa[B]).any(-1).float().mean().item()
    Kp = w.Kp[bi, ro]
    r["ro_Kp"] = (Kp[A] != Kp[B]).any(-1).float().mean().item()
    ib = w.Acc_sum[bi, ro].flatten(1)
    r["ro_inbox"] = (ib[A] != ib[B]).any(-1).float().mean().item()
    for j in range(5):
        s1 = w.S[bi, sidx[:, j], 1]
        r[f"sens{j}_S1"] = (s1[A] != s1[B]).float().mean().item()
    T = w.Tsum.sum((-1, -2))
    d = (T[:, A] != T[:, B]).any(0).float().mean(0)
    for j in range(6):
        r[f"fl{j}"] = d[j].item()
    acc.setdefault(o, []).append(r)
out = {o: {kk: round(float(np.mean([x[kk] for x in v])), 3) for kk in v[0]} for o, v in sorted(acc.items())}
for o, v in out.items():
    print(o, v, flush=True)
(HERE / "out" / "posthoc_state.json").write_text(json.dumps(out, indent=1))
