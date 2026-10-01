"""Diagnostic (8 worlds): why INT_1 < INT_CO at fded1681 (ring64 r3, sample fanout 8, lat 4+dist, sync p2)."""
import numpy as np, w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
r = [x for x in c.maj_rows() if x["cell_id"].startswith("fded1681")][0]
ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); seeds = c.held_seeds(r)[:8]
print({k: r["physics"][k] for k in ("dup", "noise", "decay_shift", "cap", "collision", "update_mode", "update_period")})
for name, g, php in (("INT_CO", wp.int_co(ph), ph), ("INT_1", *wp.member(ph, lanes=1)[1::-1][::-1][:1], ph)):
    pass
for name in ("INT_CO", "INT_1"):
    php, g = (ph, wp.int_co(ph)) if name == "INT_CO" else wp.member(ph, lanes=1)[:2]
    ep = envs.build(php, env, seeds); ws = [seeds[m - m % 2] for m in range(8)]
    w = World(php, np.repeat(g[None], 8, 0), ws, device="cpu", schedule=ep.schedule)
    a = ep.schedule.read_idx[:, 0]
    S1t, cnt = [], []
    for t in range(env.T()):
        w.step(); S1t.append(w.S[0, a[0], :2].tolist()); cnt.append(int(w.Acc_cnt[0, a[0]].sum()))
    tr = w.trace.numpy()[:, 0, 0]
    print(name, "acc", envs.score(ep, w.trace.numpy())[:8].round(3))
    print(" world0 S0 trace t=0..44:", tr[:45].tolist())
    print(" world0 S1:", [x[1] for x in S1t[:45]])
    print(" ro ticks:", ep.ro_tick[0][:4].tolist(), "y:", ep.y[0][:4].tolist())
print("--- emission / arrival detail, world 0, t=20..31")
for name in ("INT_CO", "INT_1"):
    php, g = (ph, wp.int_co(ph)) if name == "INT_CO" else wp.member(ph, lanes=1)[:2]
    ep = envs.build(php, env, seeds); ws = [seeds[m - m % 2] for m in range(8)]
    w = World(php, np.repeat(g[None], 8, 0), ws, device="cpu", schedule=ep.schedule)
    a = int(ep.schedule.read_idx[0, 0]); si = ep.schedule.sense_idx[0].tolist()
    for t in range(32):
        cnt_before = int(w.Mcnt[:, 0, a].sum())
        w.step()
        if 20 <= t <= 31:
            em = [int(x) for x in np.flatnonzero(w.last_emit[0].numpy())]
            print(name, t, "emitters", em[:10], "sensors", si, "inflight->a", cnt_before, "S0a", int(w.S[0, a, 0]))
