"""A5: engine-measured echo kernel from single-cue twins (base physics)."""
import json
import numpy as np
import torch
import conditions as C
from prometheus.ananke import assays, envs
from prometheus.ananke.engine import Schedule, World

torch.set_num_threads(2)
K_TRIAL = 5
CPRIME = {"4ab2ba01": 1, "fresh1": 0, "fresh2": 1, "fresh3": 1}


def measure(ph, env, g, cp, M=64):
    seeds = assays.world_seeds(0x5E4A, M)
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.clone()
    Pd = env.period()
    tk0 = K_TRIAL * Pd
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
    si, ri = ep.schedule.sense_idx.clone(), ep.schedule.read_idx.clone()
    for b in range(1, M, 2):
        si[b], ri[b] = si[b - 1], ri[b - 1]
    ws = [seeds[m - (m % 2)] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws, device="cpu", schedule=Schedule(si, sv, ri))
    a = w.read_idx[:, 0]
    bi = torch.arange(M)
    P = ph.update_period
    te = next(t for t in range(tk0, tk0 + env.cue_len) if t % P == 0)
    cue_sign = np.sign(sv[te, 0::2, 0].numpy())
    K = {}
    for t in range(env.T()):
        d = w.Msum[t % w.LM][bi, a, 0, cp].numpy().astype(float)
        diff = (d[0::2] - d[1::2]) * cue_sign
        if t > te and np.any(diff):
            W = -(-t // P) * P
            K[W - te] = K.get(W - te, 0.0) + float(diff.sum()) / len(cue_sign)
        w.step()
    return te, K


if __name__ == "__main__":
    ph, env, G = C.base()
    out = {}
    for name, g in G.items():
        te, K = measure(ph, env, g, CPRIME[name])
        pos = {k: v for k, v in K.items() if k <= 20}
        tot = sum(abs(v) for v in pos.values())
        out[name] = {"cue_wake": te, "kernel_raw": K,
                     "kernel_norm": {k: round(abs(v) / tot, 3) for k, v in sorted(pos.items())}}
        print(name, out[name]["kernel_norm"], flush=True)
    (C.HERE / "out/kernel_engine.json").write_text(json.dumps(out, indent=1))
