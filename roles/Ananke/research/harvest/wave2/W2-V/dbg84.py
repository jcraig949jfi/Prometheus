from v_common import *
import k16w
ph0, env = row_phys("84cf905d")
ph = ph0.replace(prog_len=18)
g = asm(ph, None, [k16w.bodyw("P", 12)] * 2 + [k16w.bodyw("Q", 12)] * 2)
seeds = assays.world_seeds(V_DEV, 2)
ws = [seeds[0], seeds[0]]
ep = envs.build(ph, env, seeds)
w = World(ph, np.repeat(g[None], 2, 0), ws, device="cpu", schedule=ep.schedule)
a = int(ep.schedule.read_idx[0, 0]); s = ep.schedule.sense_idx[0].tolist()
print("act", a, "sensors", s, "r0", w.r[0, a].item(), w.r[0, s].tolist())
M = envs.dist_matrix(ph); print("dist s1->a", M[s[0], a], "s2->a", M[s[1], a])
for t in range(env.T()):
    w.step()
    if t % 19 in (0, 2, 5, 10, 16, 17, 18):
        S = w.S[0]
        print(t, t % 19, "Kp0", w.Kp[0, a, 0].item(), "act S0..2", S[a, :3].tolist(), "nS1>0", int((S[:, 1] > 0).sum()), "nS2>0", int((S[:, 2] > 0).sum()),
              "E", w.E[0, a].item(), "y" if t % 19 == 16 else "", ep.y[0, t // 19] if t % 19 == 16 else "")
    if t > 80: break
