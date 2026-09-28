"""W-L carrier identification (PLAN s5): mirror-pair swaps before cue k,
scored on trial k only, pooled over k in {4, 6, 8}; resets for necessity."""
from __future__ import annotations
import json, sys
import numpy as np, torch
import nback as nb
from prometheus.ananke import lens
from prometheus.ananke.engine import Controls

KS = (4, 6, 8)
NAMES = ("S", "Kp", "w", "inbox", "channel_all", "pay0", "pay1", "site_all")
RESETS = {"S": ("S",), "Kp": ("Kp",), "w": ("w",), "inbox": ("inbox",)}


def pooled(tr_list):
    """pair means of trial-k accuracy pooled over the runs (one k per run)."""
    return np.mean(np.stack([lens.trial_acc(tr, [k]) for tr, k in tr_list]), 0)


def table(ph, g, n, seeds, device="cpu", back=0, names=NAMES, resets=True):
    env = nb.spec(n)
    ep = nb.build_nback(ph, env, seeds)
    Pd = env.period()
    base = lens.run(ph, g, env, seeds, ep=ep, device=device)
    nrm = pooled([(base, k) for k in KS])
    out = {"normal": lens.ci(nrm), "n": n, "back": back}
    cs = lens.carriers(ph)
    for x in names:
        kind, fn = cs[x]
        runs = []
        ident = True
        for k in KS:
            t = (k - back) * Pd - 1
            tr = lens.run(ph, g, env, seeds, ep=ep, hooks={t: fn}, device=device)
            ident &= bool(np.array_equal(tr.trace, base.trace))
            runs.append((tr, k))
        p = pooled(runs)
        out[x] = {"acc": lens.ci(p), "verdict": lens.swap_verdict(nrm, p), "arm_identical": ident}
    if resets:
        for x, parts in list(RESETS.items()) + [("flush", None)]:
            runs = []
            for k in KS:
                t = (k - back) * Pd - 1
                ctrl = (Controls(flush_inflight_at=(t,)) if parts is None
                        else Controls(reset_state_at=(t,), reset_parts=parts))
                runs.append((lens.run(ph, g, env, seeds, ep=ep, ctrl=ctrl, device=device), k))
            p = pooled(runs)
            out["reset_" + x] = {"acc": lens.ci(p)}
    return out


if __name__ == "__main__":
    torch.set_num_threads(2)
    nb.install()
    ph = nb.m2()[0]
    seeds = nb.seeds(nb.NS, 0xCA, M=64)
    res = {}
    for name, n in (("P1S", 1), ("P1K", 1), ("P2S", 2)):
        g = nb.body(name, ph)[0]
        res[name] = table(ph, g, n, seeds)
        print(name, json.dumps({k: (v if not isinstance(v, dict) else [v.get("verdict"), round(v["acc"][0], 3)]) for k, v in res[name].items()}))
    (nb.HERE / "out" / "carriers_plants.json").write_text(json.dumps(res, indent=1))
