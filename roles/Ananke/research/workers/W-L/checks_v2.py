"""T1 v2 / T3-engine recheck (deviation logged in LOG.md Attempt 2).
T1 v2: pooled-over-trials agreement per lag in [.47,.53] (except j==n: ==1),
and distractor agreement CONDITIONAL on a nonzero distractor sum in [.47,.53];
fresh 4096-world sample (key 0x8). T3e: LAG0 / P1S on n=2 and LAG0 on n=1 with
512 fresh worlds (key 0x12): CI contains .5 and hi99 < .60."""
import json
import numpy as np, torch
import nback as nb
from prometheus.ananke import assays
torch.set_num_threads(2)
nb.install()
PH = nb.m2()[0]
out = {}
for n in (0, 1, 2):
    env = nb.spec(n)
    ep = nb.build_nback(PH, env, nb.seeds(nb.NS, 0x8, n, M=4096))
    y, c, sc = ep.y, ep.meta["cues"], ep.scored[0]
    sv = ep.schedule.sense_val.numpy()[..., 0]
    Pd = env.period()
    lag = {}
    ok = True
    for j in range(env.trials):
        a = [(y[:, k] == c[:, k - j]) for k in range(env.trials) if sc[k] and k >= j]
        if a:
            v = float(np.mean(a)); lag[j] = v
            ok &= (v == 1.0) if j == n else (.47 <= v <= .53)
    dd = []
    for k in range(env.trials):
        if sc[k]:
            t0 = k * Pd
            ds = np.sign(sv[t0 + env.cue_len:t0 + env.cue_len + env.gap].sum(0))
            nz = ds != 0
            dd.append((y[nz, k] == ds[nz]))
    dv = float(np.mean(np.concatenate(dd)))
    ok &= .47 <= dv <= .53
    out[f"T1v2_n{n}"] = {"pass": bool(ok), "lag_agree": lag, "distractor_nonzero_agree": dv}
    print(n, out[f"T1v2_n{n}"]["pass"], dv, {j: round(v, 4) for j, v in lag.items()})
for n, name in ((1, "LAG0"), (2, "LAG0"), (2, "P1S")):
    g, _ = nb.body(name, PH)
    r = assays.evaluate(PH, g[None], nb.spec(n), nb.seeds(nb.NS, 0x12, n, M=512), device="cpu")
    m, lo, hi = assays.pair_ci(r.pair_acc()[0])
    d = {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "pass": bool(lo <= .5 <= hi and hi < .6)}
    out[f"T3e_{name}_n{n}"] = d
    print(name, n, d)
(nb.HERE / "out" / "checks_v2.json").write_text(json.dumps(out, indent=1))
