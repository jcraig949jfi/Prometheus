import overlay, json, time, numpy as np
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import HELD_NS
from prometheus.ananke.audit import ceilings as CL
from prometheus.ananke.audit.tests import _data as D
t0 = time.process_time()
def cell(c):
    r = D.by_id()[c]; return r, Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
w2p = D.load_json("roles/Ananke/research/harvest/wave2/W2-P/out/task2_timing.json")["rows"]
asy = [o for o in w2p if o["update_mode"] == "async"]
pick = [o for o in asy if o["family"] == "MAJ"][:3] + [o for o in asy if o["family"] == "RELAY"][:3]
for o in pick:
    r, ph, env = cell(o["cell"])
    s = assays.world_seeds(H_int(0x57325050, int(o["cell"][:8], 16)), 128)
    t = time.process_time(); j = CL.joint(ph, env, s)
    print("W2P", o["cell"][:8], o["family"], [round(abs(j[k]-o["ceil_"+k]), 15) for k in ("lc","cue","joint")], o["ceil_joint"], round(time.process_time()-t,2))
w2u = D.load_json("roles/Ananke/research/harvest/wave2/W2-U/out/task1_xor_flip.json")["rows"]
asy = [o for o in w2u if o["update_mode"] == "async" and o["ceil"]["joint"] < 0.999]
pick = [o for o in asy if o["family"] == "FLIP"][:3] + [o for o in asy if o["family"] == "XOR"][:3]
for o in pick:
    r, ph, env = cell(o["cell"])
    s = assays.world_seeds(H_int(0x57325555, int(o["cell"][:8], 16)), 128)
    t = time.process_time(); j = CL.joint(ph, env, s)
    print("W2U", o["cell"][:8], o["family"], {k: abs(j[k]-v) for k, v in o["ceil"].items() if k != "n_trials"}, o["ceil"]["joint"], round(time.process_time()-t,2))
sig = D.load_json("roles/Ananke/research/harvest/wave2/W2-T/out/lcwake_sig_b0of1.json")["rows"]
sig = sorted(sig, key=lambda x: x["held_exact"]["bound"] - x["held_acc"])[:8]
for o in sig:
    r, ph, env = cell(o["cell"])
    hs = assays.world_seeds(H_int(r["search_seed"], HELD_NS), r["search"]["M_held"])
    t = time.process_time(); e = CL.lightcone(ph, env, hs, wake="exact"); op = CL.lightcone(ph, env, hs)
    print("W2T", o["cell"][:8], o["family"], o["update_mode"], o["held_acc"], o["held_exact"]["bound"], e["bound"], abs(e["bound"]-o["held_exact"]["bound"]), abs(op["bound"]-o["held_opt"]["bound"]), round(time.process_time()-t,2))
ep = D.load_json("roles/Ananke/research/harvest/wave2/W2-S/out/epidemic_bound.json")
bad = 0
for o in ep:
    r, ph, env = cell(o["cell"])
    b = CL.epidemic(ph, env); bad += round(b["bound"], 4) != o["acc_bound"] or round(b["q_max"], 4) != o["q_max"]
print("epidemic", len(ep), "bad", bad)
print("cpu", time.process_time() - t0)
