import sys; pass
import af_common as c, time, json
from prometheus.ananke import envs, plants
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke import assays
src = open(c.HERE.parent / "P-1/decay_plant.py").read().split("N_PER =")[0]; ns = {}; exec(compile(src, "dp", "exec"), ns)
rr = ns["relay_refresh"]
for cid in ["dca299c515ff80d1", "7f149dc0"]:
    r = [x for x in c.hc.rows() if x["cell_id"].startswith(cid)][0]
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
    p16 = ph.replace(prog_len=max(ph.prog_len, 16)).validate()
    g = c.hc.bc(p16, rr(p16))
    for k in (1, 4):
        t0 = time.process_time(); out = c.batch_eval(p16, env, [(g, seeds, False)] * k); print(cid, k, round(time.process_time() - t0, 2), out[0]["acc"], env.T(), ph.n_sites)
