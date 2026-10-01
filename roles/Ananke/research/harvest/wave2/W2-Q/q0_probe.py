"""Q0: timing probe + bit-exact equivalence of batched vs standalone (hp_common.evaluate semantics)."""
from q_common import *
ck = Clock()
r = row("2c300c47"); ph, env = spec_of(r); g = genome_of(r)
S = seeds(H_int(NS, 0x00, 1), 32)
t = time.process_time()
ep = envs.build(ph, env, S); w = World(ph, np.repeat(g[None], 32, 0), mirrored(S), device="cpu", schedule=ep.schedule)
w.run(env.T(), graph=False); a_solo = envs.score(ep, w.trace.numpy()); t1 = time.process_time() - t
t = time.process_time()
res, _ = run_batched(ph, g, env, S, [("N", None)] * 5); t5 = time.process_time() - t
print("solo32 cpu", round(t1, 2), "batched5x32 cpu", round(t5, 2), "T", env.T(), "N", ph.n_sites)
print("bit-exact", all(np.array_equal(res["N"][0], a_solo) for _ in [0]), a_solo.mean())
print(ck.done())
