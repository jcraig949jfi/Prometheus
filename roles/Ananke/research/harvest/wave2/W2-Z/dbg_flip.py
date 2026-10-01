import sys; sys.path.insert(0,'.')
import wz_common as wz, plants_wz as pw
np = wz.np
c = sys.argv[1]; eoff = len(sys.argv) > 2 and sys.argv[2] == "eoff"
r = wz.row(c); ph0, env = wz.cell(r)
act = pw.flip_actuator(); relay = pw.relay_att(1) + pw.DISPATCH
ph = ph0.replace(prog_len=max(ph0.prog_len, len(act)), state_dim=max(3, ph0.state_dim), setrule=1, rules=max(2, ph0.rules)).validate()
if eoff: ph = wz.econ_off(ph)
g = pw.two_rule(ph, relay, act)
seeds = wz.held(r, 2)
ep = wz.envs.build(ph, env, seeds)
w = wz.World(ph, np.repeat(g[None], 2, 0), [seeds[0], seeds[0]], device="cpu", schedule=ep.schedule)
s = int(ep.schedule.sense_idx[0, 0]); a = int(ep.schedule.read_idx[0, 0])
print("sensor", s, "act", a, "Pd", env.period(), "delta", env.delta)
for t in range(env.period() * 5):
    w.step()
    print(t, "sv", ep.schedule.sense_val[t, 0].tolist(), "aw_a", int(w.last_awake[0, a]), "r_a", int(w.r[0, a]), "S_a", w.S[0, a, :3].tolist(), "E_s", int(w.E[0, s]), "E_a", int(w.E[0, a]),
          "emit", int(w.last_emit[0].sum()), "emit_s", int(w.last_emit[0, s]), "rules_hist", np.bincount(w.r[0].numpy(), minlength=ph.rules).tolist())
