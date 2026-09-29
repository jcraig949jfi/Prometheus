"""W-B probe harness: copy of lens.run with a pre-first-tick hook and an
every-tick hook. Between-tick only; physics untouched."""
from __future__ import annotations
import pathlib, sys
REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
import numpy as np
import torch
from prometheus.ananke import assays, envs, lens
from prometheus.ananke.engine import Controls, World

SEEDS = assays.world_seeds(0x5E5, 64)
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def run(ph, genome, env, seeds=SEEDS, pre=None, hooks=None, every=None, ctrl=None,
        record_r=False, device=DEV):
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device=device, ctrl=ctrl or Controls(), schedule=ep.schedule)
    if pre:
        pre(w)
    hooks = hooks or {}
    rs = []
    for t in range(env.T()):
        w.step()
        if t in hooks:
            for fn in (hooks[t] if isinstance(hooks[t], list) else [hooks[t]]):
                fn(w)
        if every:
            every(w, t)
        if record_r:
            rs.append(w.r.to(torch.int8).cpu().numpy())
    tr = w.trace.cpu().numpy()
    out = lens.Trace(ep, tr, envs.per_trial(ep, tr), {}, {k: v.cpu().numpy() for k, v in w.stats.items()})
    out.r = np.stack(rs) if record_r else None      # [T, B, N] after each tick
    out.world = w
    return out


def acc(tr, trials=None):
    trials = range(tr.ep.scored.shape[1]) if trials is None else trials
    return lens.trial_acc(tr, trials)


def paired(arm, normal):
    d = arm - normal
    m, lo, hi = lens.ci(d)
    verdict = "HURTS" if hi < 0 else ("EQUIV" if lo > -0.05 else "UNRESOLVED")
    return {"arm": lens.ci(arm), "d": [m, lo, hi], "v": verdict}


def freeze(w):
    w.ctrl.freeze_rule = True


def set_r(val):
    def f(w):
        v = torch.as_tensor(val, device=w.dev)
        w.r.copy_(v.expand_as(w.r).to(w.r.dtype) if v.dim() < 2 else v.to(w.r.dtype))
    return f


def pin(mask, val):
    """after every tick: r[mask] := val[mask] (per-site SETRULE ignored)."""
    def f(w, t=None):
        m = torch.as_tensor(mask, device=w.dev)
        v = torch.as_tensor(val, device=w.dev).to(w.r.dtype).expand_as(w.r)
        w.r.copy_(torch.where(m, v, w.r))
    return f


def census(r, Pd):
    """r [T,B,N]."""
    T, B, N = r.shape
    p = np.arange(B) ^ 1
    diff = (r != r[:, p]).sum()
    ch = (r[1:] != r[:-1])
    after = r[2 * Pd - 1:]
    vals, cnt = np.unique(after, return_counts=True)
    modal = int(vals[cnt.argmax()])
    unsettled = (r != modal).mean((1, 2))
    settle = int(np.argmax(unsettled == 0)) if (unsettled == 0).any() else -1
    return {"partner_diff_site_ticks": int(diff),
            "changes_after_trial0": int(ch[Pd - 1:].sum()),
            "changes_after_trial1": int(ch[2 * Pd - 1:].sum()),
            "modal_rule_after_trial1": modal,
            "modal_share_after_trial1": float(cnt.max() / cnt.sum()),
            "hist_after_trial1": {int(a): int(b) for a, b in zip(vals, cnt)},
            "share_not_modal_by_tick_first12": [round(float(x), 4) for x in unsettled[:12]],
            "first_tick_all_modal": settle}
