"""A4c: distractor-magnitude tongue for 311c465f (even and odd amplitudes,
plus +-jitter around 64)."""
from w2e_common import *
ck = Clock()
r = row("311c465f", "evolve"); ph, env = spec_of(r); g = genome_of(r)
Pd = env.period(); S = seeds(H_int(NS, 0xA4C), 128)
def amp_fn(a, jit=0):
    def f(ep):
        sv = ep.schedule.sense_val
        rg = np.random.default_rng(5)
        for k in range(env.trials):
            t0 = k * Pd; seg = sv[t0 + env.cue_len:t0 + env.cue_len + env.gap]
            if jit:
                # jitter shared by mirror partners (pairs b, b+1)
                J = rg.integers(-jit, jit + 1, size=(seg.shape[0], seg.shape[1] // 2))
                J = np.repeat(J, 2, axis=1)
                mag = torch.as_tensor(a + 2 * J, dtype=seg.dtype)[..., None]
            else:
                mag = a
            seg.copy_(torch.sign(seg) * mag)
    return f
out = {}
for a in list(range(40, 100, 4)) + [62, 63, 65, 66, 192]:
    acc, *_ = run(ph, g, env, S, sched_fn=amp_fn(a)); out[f"amp{a}"] = round(ci(pairs(acc))[0], 3)
for j in (1, 2, 4):
    acc, *_ = run(ph, g, env, S, sched_fn=amp_fn(64, j)); out[f"amp64_jitter+-{2*j}"] = ci(pairs(acc))
out["clock"] = ck.done(); save("a4c_311c_sweep.json", out); print(json.dumps(out))
