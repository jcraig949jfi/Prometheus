"""W-B Part 1: SETRULE probes on the two M3 specimens (PLAN.md X1-X8)."""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
import torch
from probe import (REPO, SEEDS, run, acc, paired, freeze, set_r, pin, census)
from prometheus.ananke import c1b, c1b_run, lens

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)


def pair_mask(B, N, frac, seed, exclude):
    """same mask for both mirror partners; never includes excluded sites."""
    g = np.random.default_rng(seed)
    m = np.zeros((B, N), bool)
    for p in range(B // 2):
        cand = np.flatnonzero(~exclude[2 * p])
        k = int(round(frac * len(cand)))
        pick = g.choice(cand, k, replace=False)
        m[2 * p, pick] = m[2 * p + 1, pick] = True
    return m


def spike(cid):
    t_start = time.time()
    ph, env, g, _ = c1b_run.load(cid)
    Pd, R = env.period(), ph.rules
    tk = c1b.ticks(env)
    out = {}
    base = run(ph, g, env, record_r=True)
    nrm = acc(base)
    B, N = base.r.shape[1:]
    ro = np.zeros((B, N), bool)
    ridx = base.ep.schedule.read_idx.cpu().numpy()
    for b in range(B):
        ro[b, ridx[b]] = True
    r0 = base.world.r0.cpu().numpy()
    out["normal"] = lens.ci(nrm)
    out["X1_census"] = census(base.r, Pd)
    out["X1_readout_sites_per_world"] = int(ro[0].sum())
    # X2 uniform init + freeze; X3 init 0 with SETRULE on; X4 control
    for k in range(R):
        tr = run(ph, g, env, pre=lambda w, k=k: (set_r(k)(w), freeze(w)))
        out[f"X2_uniform{k}_frozen"] = paired(acc(tr), nrm)
    tr = run(ph, g, env, pre=set_r(0), record_r=True)
    out["X3_init0_setrule_on"] = paired(acc(tr), nrm)
    out["X3_trial0"] = {"normal": float(acc(base, [0]).mean()), "init0": float(acc(tr, [0]).mean())}
    out["X3_census"] = census(tr.r, Pd)
    out["X3_trace_identical_after_trial0"] = bool((tr.trace[Pd:] == base.trace[Pd:]).all())
    tr = run(ph, g, env, pre=freeze)
    out["X4_random_init_frozen"] = paired(acc(tr), nrm)
    # natural experiment inside X4: readout site starting at rule 0 vs not
    ro_rule = np.array([r0[b, ridx[b][0]] for b in range(B)])
    per_world = np.nanmean(np.where(tr.ep.scored, tr.per_trial, np.nan), 1)
    out["X4_by_readout_r0"] = {int(k): [float(per_world[ro_rule == k].mean()) if (ro_rule == k).any() else None,
                                        int((ro_rule == k).sum())] for k in range(R)}
    # X5 per-site
    everyt = lambda f: (lambda w, t: f(w))
    tr = run(ph, g, env, every=everyt(pin(ro, r0)), pre=pin(ro, r0))
    out["X5a_readout_pinned_r0"] = paired(acc(tr), nrm)
    out["X5a_readout_r0_zero_frac"] = float((ro_rule == 0).mean())
    tr = run(ph, g, env, every=everyt(pin(~ro, r0)), pre=pin(~ro, r0))
    out["X5b_others_pinned_r0"] = paired(acc(tr), nrm)
    rng = np.random.default_rng(0x5E5)
    junk = np.repeat(rng.integers(1, R, size=(B // 2, N)), 2, axis=0)
    for f in (0.05, 0.1, 0.25, 0.5, 1.0):
        m = pair_mask(B, N, f, 11, ro)
        tr = run(ph, g, env, pre=lambda w, m=m: (set_r(0)(w), pin(m, junk)(w)), every=everyt(pin(m, junk)))
        out[f"X5c_junk_frac{f}"] = paired(acc(tr), nrm)
    for k in range(1, R):
        m = pair_mask(B, N, 0.25, 11, ro)
        tr = run(ph, g, env, pre=lambda w, m=m, k=k: (set_r(0)(w), pin(m, k)(w)), every=everyt(pin(m, k)))
        out[f"X5d_junk25_rule{k}"] = paired(acc(tr), nrm)
    # X6 repair after a mid-run randomization at trial 4 mid
    tm = tk["mid"][4]
    rnd = np.repeat(rng.integers(0, R, size=(B // 2, N)), 2, axis=0)
    later = range(5, env.trials)
    nl = acc(base, later)
    tr = run(ph, g, env, hooks={tm: set_r(rnd)}, record_r=True)
    out["X6_randomize_mid_t4_setrule_on"] = paired(acc(tr, later), nl)
    out["X6_trial4"] = {"normal": float(acc(base, [4]).mean()), "rand_on": float(acc(tr, [4]).mean())}
    uns = (tr.r[tm:] != 0).mean((1, 2))
    out["X6_share_not0_ticks_after"] = [round(float(x), 4) for x in uns[:8]]
    tr = run(ph, g, env, hooks={tm: [set_r(rnd), freeze]})
    out["X6_randomize_mid_t4_then_frozen"] = paired(acc(tr, later), nl)
    # X7 exact reduction to a rules=1 law
    ph1 = ph.replace(rules=1)
    t1 = run(ph1, g[:1].copy(), env)
    t0f = run(ph, g, env, pre=lambda w: (set_r(0)(w), freeze(w)))
    out["X7_rules1_vs_r0frozen_bit_identical"] = bool((t1.trace == t0f.trace).all())
    out["X7_rules1_vs_normal"] = paired(acc(t1), nrm)
    # X8 neighbouring physics
    for name, kw in (("update_p1.0", dict(update_p=1.0)), ("loss0.15", dict(loss=0.15)),
                     ("lat_base3", dict(lat_base=3))):
        p2 = ph.replace(**kw)
        bn = run(p2, g, env)
        tz = run(p2, g, env, pre=lambda w: (set_r(0)(w), freeze(w)))
        tf = run(p2, g, env, pre=freeze)
        out[f"X8_{name}"] = {"normal": lens.ci(acc(bn)), "r0_frozen": paired(acc(tz), acc(bn)),
                            "random_frozen": paired(acc(tf), acc(bn))}
    out["_wall_s"] = time.time() - t_start
    return out


if __name__ == "__main__":
    ids = sys.argv[1:] or list(c1b.SPECIMENS["M3"])
    res = {}
    for cid in ids:
        res[cid[:8]] = spike(cid)
        print(json.dumps(res[cid[:8]], default=float)[:4000], flush=True)
    (OUT / "m3.json").write_text(json.dumps(res, indent=1, default=float))
