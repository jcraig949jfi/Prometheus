"""A4b: exact write provenance for 311c465f: S0 is written only by rule 1
(S0 := SENSE xor ENERGY). Last awake tick with r==1 at the readout site
before each readout, classified by the SENSE on that tick."""
from w2e_common import *
import importlib.util
spec = importlib.util.spec_from_file_location("a4", str(HERE / "a4_311c465f.py"))
r = row("311c465f", "evolve"); ph, env = spec_of(r); g = genome_of(r)
Pd = env.period()
S = seeds(H_int(NS, 0xA4), 128)[:64]
def none_fn(ep):
    sv = ep.schedule.sense_val
    for k in range(env.trials):
        t0 = k * Pd; sv[t0 + env.cue_len:t0 + env.cue_len + env.gap].zero_()
def prov(fn):
    M = len(S)
    ep = envs.build(ph, env, S)
    if fn: fn(ep)
    ws = [S[m - m % 2] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    ro = ep.schedule.read_idx[:, 0]
    sv = ep.schedule.sense_val[:, :, 0].numpy()
    lw = np.full(M, "none", dtype=object)
    lab = np.full((M, env.trials), "", dtype=object)
    for t in range(env.T()):
        rb = w.r[torch.arange(M), ro].numpy().copy()
        w.step()
        if t % ph.update_period == 0:
            for b in np.flatnonzero(rb == 1):
                s = sv[t, b]
                kind = "cue" if abs(s) == env.amp else ("distr" if s != 0 else "silent")
                lw[b] = f"{kind}@{t % Pd}"
        for k in range(env.trials):
            if t == ep.ro_tick[0, k]:
                lab[:, k] = lw
    pt = envs.per_trial(ep, w.trace.cpu().numpy())
    vals = np.unique(lab.ravel())
    return {v: {"n": int((lab == v).sum()), "acc": round(float(pt[lab == v].mean()), 3)} for v in vals}
out = {"normal": prov(None), "no_distractors": prov(none_fn)}
save("a4b_311c_writes.json", out); print(json.dumps(out, indent=1))
