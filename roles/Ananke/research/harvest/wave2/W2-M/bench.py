import w2m_common as c, w2m_plants as wp, time
from prometheus.ananke import envs, assays
from prometheus.ananke.physics import Physics
ph = Physics(topology="ring", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, update_mode="sync", update_period=1, decay_shift=0, noise=0, state_dim=3,
             payload_width=3, channels=1, prog_len=16).validate()
env = envs.EnvSpec(family="MAJ", d=3, delta=8, trials=12)
seeds = assays.world_seeds(0x57324D, 64)
t = time.process_time(); w = time.time()
r = c.hc.evaluate(ph, wp.int_1(ph)[None][0], env, seeds) if False else c.hc.evaluate(ph, wp.int_1(ph), env, seeds)
print(r["acc"], r["lo99"], time.process_time() - t, time.time() - w)
