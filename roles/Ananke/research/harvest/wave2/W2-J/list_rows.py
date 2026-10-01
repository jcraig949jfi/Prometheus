import collections
from wj_common import *
L = lc()
ev = xor_evolve()
keys = ["topology", "n_sites", "radius", "k_random", "rewire", "update_mode", "update_period", "update_p", "loss", "loss_per_hop",
        "cap", "collision", "decay_shift", "noise", "dest_mode", "fanout", "lat_base", "lat_hop", "lat_jitter", "dup",
        "prog_len", "state_dim", "payload_width", "channels", "rules", "mut_site", "e_income", "e_max", "c_emit", "c_op", "c_mem", "plastic_route", "setrule", "wimm"]
out = []
for r in ev:
    p = r["physics"]
    h = held(r)
    out.append({"cell": r["cell_id"], "wave": r["wave"], "env": {k: r["env"][k] for k in ("d", "delta", "trials", "cue_len", "iti")},
                "phys": {k: p[k] for k in keys}, "bound": L[r["cell_id"]]["bound"], "held_acc": h.get("acc"), "held_lo99": h.get("lo99")})
save("rows83.json", out)
un = [o for o in out if o["bound"] >= 0.6]
print(len(out), len(un))
for k in keys:
    c = collections.Counter(str(o["phys"][k]) for o in un)
    print(k, dict(c))
print(collections.Counter((o["env"]["d"], o["env"]["delta"]) for o in un))
print(collections.Counter(o["wave"] for o in un))
print("held keys", list(held(ev[0]).keys()))
