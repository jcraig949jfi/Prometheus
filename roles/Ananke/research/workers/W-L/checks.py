"""W-L task-validity checks T1-T4 and plant solvability / baselines (PLAN s3a, s3b).
CPU, 2 threads. Writes out/checks.json."""
from __future__ import annotations

import itertools
import json

import numpy as np
import torch

import nback as nb
from prometheus.ananke import assays

torch.set_num_threads(2)
nb.install()
PH, ENV0, _, _ = nb.m2()
out = {"physics": PH.to_dict(), "env": ENV0.to_dict()}


def task_checks(n):
    env = nb.spec(n)
    s = nb.seeds(nb.NS, 0x7, n, M=4096)
    ep = nb.build_nback(PH, env, s)
    y, c, sc = ep.y, ep.meta["cues"], ep.scored
    sv = ep.schedule.sense_val.numpy()[..., 0]           # [T, B]
    Pd = env.period()
    res = {"n": n}
    # T1
    agree = {}
    ok1 = True
    for j in range(0, env.trials):
        vals = []
        for k in range(env.trials):
            if sc[0, k] and k - j >= 0:
                vals.append((y[:, k] == c[:, k - j]).mean())
        if vals:
            v = float(np.mean(vals)), float(np.min(vals)), float(np.max(vals))
            agree[j] = v
            if j == n:
                ok1 &= v[1] == 1.0
            else:
                ok1 &= (.47 <= v[1]) and (v[2] <= .53)
    dsum = []
    for k in range(env.trials):
        if sc[0, k]:
            t0 = k * Pd
            ds = np.sign(sv[t0 + env.cue_len:t0 + env.cue_len + env.gap].sum(0))
            dsum.append((y[:, k] == ds).mean())
    ok1 &= (.47 <= min(dsum)) and (max(dsum) <= .53)
    res["T1"] = {"pass": bool(ok1), "agree_by_lag(mean,min,max)": agree,
                 "distractor_agree_min_max": [float(min(dsum)), float(max(dsum))]}
    # T2
    ok2 = bool((y[1::2] == -y[0::2]).all() and (sv[:, 1::2] == -sv[:, 0::2]).all())
    res["T2"] = {"pass": ok2}
    # T3 host-side exhaustive: boolean functions of the other lags in {0..2}
    lags = [j for j in range(3) if j != n]
    best = 0.0
    ks = [k for k in range(env.trials) if sc[0, k] and k >= 2]
    X = np.stack([np.stack([c[:, k - j] for j in lags], -1) for k in ks], 1)   # [B, K, nl]
    Y = np.stack([y[:, k] for k in ks], 1)
    idx = ((X > 0).astype(int) * (2 ** np.arange(len(lags)))).sum(-1)
    for tab in itertools.product([-1, 1], repeat=2 ** len(lags)):
        pred = np.array(tab)[idx]
        best = max(best, float((pred == Y).mean()))
    res["T3_host"] = {"pass": best <= .53, "max_acc_over_%d_functions" % 2 ** 2 ** len(lags): best}
    # T4: the lag-n cue value never reappears in the schedule after its own cue
    ok4 = True
    for k in range(n, env.trials):
        tA = (k - n) * Pd + env.cue_len                    # after cue k-n
        seg = sv[tA:(k * Pd + env.cue_len + env.gap + 1)]
        big = np.abs(seg) >= 256
        # any cue-amplitude sample after cue k-n belongs to cues k-n+1..k, which are independent
        ok4 &= bool(big.sum(0).max() <= 2 * n)
    res["T4"] = {"pass": ok4}
    return res


def plant_eval(name, n, ns):
    g, nl = nb.body(name, PH)
    env = nb.spec(n)
    s = nb.seeds(ns, n, 0x11, M=64)
    r = assays.evaluate(PH, g[None], env, s, device="cpu")
    pa = r.pair_acc()[0]
    m, lo, hi = assays.pair_ci(pa)
    return {"plant": name, "lines": nl, "n": n, "acc": float(m), "lo99": float(lo), "hi99": float(hi)}, pa


if __name__ == "__main__":
    out["tasks"] = [task_checks(n) for n in (0, 1, 2)]
    for t in out["tasks"]:
        print(t["n"], {k: v["pass"] for k, v in t.items() if isinstance(v, dict) and "pass" in v})
    pl = []
    for n, names in ((0, ["LAG0", "NULL"]), (1, ["P1S", "P1K", "LAG0", "NULL"]),
                     (2, ["P2S", "P1S", "LAG0", "NULL"])):
        for name in names:
            for ns, lab in ((nb.NS, "analysis"), (nb.NS_HELD, "held")):
                d, _ = plant_eval(name, n, ns)
                d["ns"] = lab
                pl.append(d)
                print(d)
    out["plants"] = pl
    (nb.HERE / "out").mkdir(exist_ok=True)
    (nb.HERE / "out" / "checks.json").write_text(json.dumps(out, indent=1, default=str))
