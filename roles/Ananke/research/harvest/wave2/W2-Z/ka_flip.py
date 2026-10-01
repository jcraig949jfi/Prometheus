"""Known-answer gate for the two-rule FLIP plant at clean physics, plus single-world trace."""
import sys; sys.path.insert(0, '.')
import wz_common as wz, plants_wz as pw
np = wz.np
Physics = wz.Physics
s = int(sys.argv[1]) if len(sys.argv) > 1 else 1
econ = len(sys.argv) > 2 and sys.argv[2] == "econ"
trace = "t" in sys.argv
ph = Physics(topology="ring", n_sites=64, radius=1, dest_mode="all", lat_base=1, update_mode="sync", update_period=1,
             state_dim=4, payload_width=1, channels=1, prog_len=28, rules=2, setrule=1)
if econ:
    ph = ph.replace(e_income=4, e_max=100, c_emit=4, c_op=1, c_mem=1)
for a in sys.argv:
    if a.startswith("P="): ph = ph.replace(update_period=int(a[2:]))
    if a.startswith("p="): ph = ph.replace(update_mode="async", update_p=float(a[2:]))
env = wz.envs.EnvSpec(family="FLIP", d=3, delta=16, trials=16, block=4)
relay = pw.relay_att(s) + pw.DISPATCH
act = pw.flip_actuator_v2() if "v2" in sys.argv else pw.flip_actuator()
g = pw.two_rule(ph, relay, act)
seeds = wz.assays.world_seeds(0x575A4B41, 32)
o = wz.ws.flip_eval(ph, g, env, seeds)
print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items() if k in ("acc", "lo99", "chg", "same", "bal", "bal_lo99", "ro_zero_frac")})
if trace:
    ep = wz.envs.build(ph, env, seeds[:2])
    w = wz.World(ph, np.repeat(g[None], 2, 0), [seeds[0], seeds[0]], device="cpu", schedule=ep.schedule)
    sidx = int(ep.schedule.sense_idx[0, 0]); a = int(ep.schedule.read_idx[0, 0])
    print("sensor", sidx, "act", a)
    for t in range(env.period() * 4):
        insum = int(w.Acc_sum[0, a, 0, 0])
        w.step()
        print(t, ep.schedule.sense_val[t, 0].tolist(), "IN_a(pre)", insum, "r_a", int(w.r[0, a]), "S_a", w.S[0, a, :3].tolist(), "nemit", int(w.last_emit[0].sum()))
