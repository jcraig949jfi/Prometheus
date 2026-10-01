import numpy as np, w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
r = [x for x in c.maj_rows() if x["cell_id"].startswith("fded1681")][0]
ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); seeds = c.held_seeds(r)[:8]
php, g, ok, n = wp.member(ph, lanes=1)
print(php.prog_len, php.rules, php.mut_site, php.setrule, php.wimm, php.plastic_route)
print("\n".join(c.hc.decompile(php, g[0])))
print(g[0])
ep = envs.build(php, env, seeds)
print("sense vals t=22 world0:", ep.schedule.sense_val[22, 0].tolist(), ep.schedule.sense_val[6,0].tolist())
