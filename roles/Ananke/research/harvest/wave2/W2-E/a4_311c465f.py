"""A4: 311c465f (HOLD torus, R=2, decay 3) needs its distractors. Schedule
variants + write-provenance trace at the readout site."""
from w2e_common import *
import dataclasses
ck = Clock()
r = row("311c465f", "evolve"); ph, env = spec_of(r); g = genome_of(r)
S = seeds(H_int(NS, 0xA4), 128)
Pd = env.period()

def mk(mode, amp=None):
    def f(ep):
        sv = ep.schedule.sense_val
        T = sv.shape[0]
        for k in range(env.trials):
            t0 = k * Pd
            a, b = t0 + env.cue_len, t0 + env.cue_len + env.gap
            seg = sv[a:b]
            if mode == "none":
                seg.zero_()
            elif mode == "amp":
                seg.copy_(torch.sign(seg) * amp)
            elif mode == "const":       # constant sign within world (mirror keeps sign flip)
                lead_sign = torch.sign(sv[t0:t0 + 1])   # sign of cue: use +|amp| * mirror sign
                # mirror sign: world b odd negated; recover from parity of b
                ms = torch.tensor([1 if b_ % 2 == 0 else -1 for b_ in range(seg.shape[1])], dtype=seg.dtype)
                seg.copy_(ms[None, :, None] * env.amp_dist * (seg != 0).to(seg.dtype))
            elif mode in ("awake_only_removed", "asleep_only_removed"):
                for t in range(a, b):
                    awake = (t % ph.update_period == 0)
                    if (mode == "awake_only_removed") == awake:
                        sv[t].zero_()
    return f

variants = {"normal": None, "no_distractors": mk("none"), "amp63_odd": mk("amp", 63),
            "amp65_odd": mk("amp", 65), "amp32": mk("amp", 32), "amp128": mk("amp", 128), "amp2": mk("amp", 2),
            "const_sign_64": mk("const"), "distr_removed_awake_ticks": mk("awake_only_removed"),
            "distr_removed_asleep_ticks": mk("asleep_only_removed")}
out = {"decompiled": {gi: decompile(ph, g[gi]) for gi in range(ph.rules)}, "variants": {}}
for name, fn in variants.items():
    acc, tr, ep, w = run(ph, g, env, S, sched_fn=fn)
    out["variants"][name] = ci(pairs(acc))
    print(name, out["variants"][name], flush=True)

# write provenance at the readout site (normal and no-distractor), 64 worlds
def provenance(fn):
    M = 64; SS = S[:M]
    ep = envs.build(ph, env, SS)
    if fn: fn(ep)
    ws = [SS[m - m % 2] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    ro = ep.schedule.read_idx[:, 0]
    last_write_kind = np.full((M, env.trials), "", dtype=object)
    lw = np.full(M, "init", dtype=object)
    prev = w.S[torch.arange(M), ro, 0].clone()
    sv = ep.schedule.sense_val[:, :, 0].numpy()
    rhist = []
    counts = {}
    for t in range(env.T()):
        r_before = w.r[torch.arange(M), ro].clone()
        w.step()
        cur = w.S[torch.arange(M), ro, 0]
        awake = (t % ph.update_period == 0)
        changed = (cur != prev).numpy() if awake else np.zeros(M, bool)
        for b in np.flatnonzero(changed):
            s = sv[t, b]
            k = t % Pd
            kind = ("cue" if abs(s) == env.amp else "distr" if s != 0 else "silent")
            lw[b] = f"{kind}@{k}"
        prev = cur.clone()
        rhist.append(r_before.numpy())
        for k in range(env.trials):
            if t == ep.ro_tick[0, k]:
                for b in range(M):
                    last_write_kind[b, k] = lw[b]
    vals, cnt = np.unique(last_write_kind.ravel(), return_counts=True)
    acc_by = {}
    pt = envs.per_trial(ep, w.trace.cpu().numpy())
    for v in vals:
        acc_by[v] = {"n": int((last_write_kind == v).sum()), "acc": float(pt[last_write_kind == v].mean())}
    rh = np.array(rhist)  # [T, M]
    phase_r1 = {int(k): float((rh[np.arange(env.T()) % Pd == k] == 1).mean()) for k in range(Pd)}
    return {"last_write_at_readout": acc_by, "P(r=1 at readout site) by in-trial tick": phase_r1}
out["provenance_normal"] = provenance(None)
out["provenance_no_distr"] = provenance(variants["no_distractors"])
out["provenance_amp63"] = provenance(variants["amp63_odd"])
out["clock"] = ck.done(); save("a4_311c465f.json", out); print(json.dumps(out, indent=1))
