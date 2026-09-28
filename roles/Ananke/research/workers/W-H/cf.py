"""W-H Part 1 counterfactuals per PLAN ADDENDUM A. CPU, 2 threads."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np, torch
torch.set_num_threads(2)
from harness import run, acc, paired, AN
from prometheus.ananke import c1b_run, envs, lens

OUT = pathlib.Path(__file__).parent / "out"
B = 64


def setr(w, mask, val):
    m = torch.as_tensor(mask, device=w.dev)
    v = torch.as_tensor(val, device=w.dev).to(w.r.dtype)
    w.r.copy_(torch.where(m, v.expand_as(w.r), w.r))


def verdict_forbid(p):
    lo, hi = p["d"][1], p["d"][2]
    return "NECESSARY" if hi < 0 else ("NOT-NECESSARY" if lo > -0.05 else "UNRESOLVED")


def verdict_force(arm_ci, normal_ci):
    m, lo, hi = arm_ci
    if hi < 0.40:
        return "SUFFICIENT-FLIP"
    if lo >= normal_ci[1] - 0.05:
        return "NO-EFFECT"
    if lo <= 0.5 <= hi and hi < normal_ci[1]:
        return "SUFFICIENT-CHANCE"
    return "UNRESOLVED"


def go(cid):
    ph, env, g, row = c1b_run.load(cid)
    ep = envs.build(ph, env, AN)
    N, Pd, T = ph.n_sites, env.period(), env.T()
    a = ep.schedule.read_idx.numpy()[:, 0]
    s = ep.schedule.sense_idx.numpy()[:, 0]
    ro = np.zeros((B, N), bool); ro[np.arange(B), a] = True
    base = run(ph, g, env, ep=ep)
    nrm = acc(base)
    out = {"normal": lens.ci(nrm)}
    y = ep.y
    t0s = [k * Pd for k in range(env.trials)]
    if cid.startswith("b59e"):
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, ro, 0))
        p = paired(acc(tr), nrm); p["v"] = verdict_forbid(p); out["CF1_forbid_readout"] = p
        rng = np.random.default_rng(0x5ED)
        oth = np.zeros((B, N), bool)
        for b in range(0, B, 2):
            c = rng.choice(np.setdiff1d(np.arange(N), [a[b], s[b]]))
            oth[b, c] = oth[b + 1, c] = True
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, oth, 0))
        p = paired(acc(tr), nrm); p["v"] = verdict_forbid(p); out["CF1c_forbid_other_site"] = p
        neg = y == -1
        hooks = {}
        for k, t0 in enumerate(t0s):
            m = ro & neg[:, k][:, None]
            hooks[t0 + 5] = m
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, hooks[t], 1) if t in hooks else None)
        armc = lens.ci(acc(tr, mask=neg)); nc = lens.ci(acc(base, mask=neg))
        out["CF2_force_rule1_in_neg_trials"] = {"arm": armc, "normal_same_trials": nc, "v": verdict_force(armc, nc),
                                                "all_trials": lens.ci(acc(tr))}
    elif cid.startswith("311c"):
        ks = range(1, env.trials)
        fb = {t0s[k] + j for k in ks for j in (-1, 0)}
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, ro, 0) if t in fb else None)
        p = paired(acc(tr, ks), acc(base, ks)); p["v"] = verdict_forbid(p); out["CF1_forbid_rule1_at_cue"] = p
        fc = {t0s[k] + j for k in ks for j in (2, 3)}
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, ro, 1) if t in fc else None)
        armc = lens.ci(acc(tr, ks)); nc = lens.ci(acc(base, ks))
        out["CF2_force_rule1_in_gap"] = {"arm": armc, "normal_same_trials": nc, "v": verdict_force(armc, nc)}
        # extra diagnostic (not a decision arm): force at the cue phases (both), is the champion's write sufficient?
        fcc = {t0s[k] + j for k in ks for j in (-1, 0)}
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, ro, 1) if t in fcc else None)
        out["DIAG_force_rule1_at_cue"] = lens.ci(acc(tr, ks))
    elif cid.startswith("9564"):
        ts = 2 * Pd - 1
        allm = np.ones((B, N), bool)
        def forbid(mask):
            def f(w, t):
                if t >= ts:
                    setr(w, mask & (w.r == 2).cpu().numpy(), 0)
            return f
        later = range(2, env.trials)
        nl = acc(base, later)
        tr = run(ph, g, env, ep=ep, post=forbid(allm))
        p = paired(acc(tr, later), nl); p["v"] = verdict_forbid(p); out["CF1_forbid_rule2_all_sites"] = p
        tr = run(ph, g, env, ep=ep, post=forbid(ro))
        p = paired(acc(tr, later), nl); p["v"] = verdict_forbid(p); out["CF1r_forbid_rule2_readout"] = p
        neg = y == -1
        hooks = {t0s[k] + 3: np.repeat(neg[:, k][:, None], N, 1) for k in range(env.trials)}
        tr = run(ph, g, env, ep=ep, post=lambda w, t: setr(w, hooks[t], 2) if t in hooks else None)
        armc = lens.ci(acc(tr, mask=neg)); nc = lens.ci(acc(base, mask=neg))
        out["CF2_force_rule2_all_sites_neg_trials"] = {"arm": armc, "normal_same_trials": nc, "v": verdict_force(armc, nc),
                                                       "all_trials": lens.ci(acc(tr))}
    return out


if __name__ == "__main__":
    res = {}
    for c in sys.argv[1:]:
        res[c] = go(c)
        print(c[:8], json.dumps(res[c], default=float), flush=True)
    (OUT / "cf.json").write_text(json.dumps(res, indent=1, default=float))
