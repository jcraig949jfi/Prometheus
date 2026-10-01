"""A10: anatomy of distractor dependence in 2c300c47 and 0c18ce5e (HOLD global, ~1.0
with distractors, ~.5 without). Variants: one silent awake gap tick (first/last),
amplitude sweep, constant sign; trace of the actuator's Kp and S0 sign over a trial."""
from w2e_common import *
ck = Clock()
def variant(env, ph, kind, val=None):
    Pd = env.period()
    def f(ep):
        sv = ep.schedule.sense_val
        for k in range(env.trials):
            t0 = k * Pd; a, b = t0 + env.cue_len, t0 + env.cue_len + env.gap
            aw = [t for t in range(a, b) if t % ph.update_period == 0] if ph.update_mode == "sync" else list(range(a, b))
            if kind == "silent_last" and aw: sv[aw[-1]].zero_()
            elif kind == "silent_first" and aw: sv[aw[0]].zero_()
            elif kind == "amp": seg = sv[a:b]; seg.copy_(torch.sign(seg) * val)
            elif kind == "const":
                seg = sv[a:b]; ms = torch.tensor([1 if i % 2 == 0 else -1 for i in range(seg.shape[1])], dtype=seg.dtype)
                seg.copy_(ms[None, :, None] * env.amp_dist * (seg != 0).to(seg.dtype))
            elif kind == "silent_iti_to_distr":   # fill iti/readout ticks with distractors too
                pass
    return f
out = {}
for cid in ["2c300c47", "0c18ce5e"]:
    r = row(cid, "evolve"); ph, env = spec_of(r); g = genome_of(r)
    S = seeds(H_int(NS, 0xA10, int(cid, 16) & 0xFFFF), 64)
    res = {}
    for name, fn in [("normal", None), ("silent_first_awake_gap_tick", variant(env, ph, "silent_first")),
                     ("silent_last_awake_gap_tick", variant(env, ph, "silent_last")), ("const_sign", variant(env, ph, "const"))] + \
                    [(f"amp{a}", variant(env, ph, "amp", a)) for a in (0, 16, 32, 48, 63, 65, 96, 128, 200)]:
        a, *_ = run(ph, g, env, S, sched_fn=fn); res[name] = round(ci(pairs(a))[0], 3)
    out[cid] = res; print(cid, res, flush=True)
out["clock"] = ck.done(); save("a10_distr_dep.json", out)
