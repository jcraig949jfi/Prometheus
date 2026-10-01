"""Known answer / soundness for the epidemic-cone bound: on synthetic RELAY physics where a persistent-burst
relay (B(k) with k >= delta, close to the optimal epidemic) is near the bound, the measured plant accuracy (64
worlds, engine) must not exceed EC_bound_upper beyond sampling error, and the bound should be reasonably tight.
Physics span global/sampled ring/torus, loss, async, jitter, dup, sync period 2."""
import af_common as c
import numpy as np
from prometheus.ananke import envs, assays
from prometheus.ananke.physics import Physics
import relay_variants as rv
from epicone import bound

ck = c.Clock(); rng = np.random.default_rng(7); out = []
seeds = assays.world_seeds(0xEC0, 64)
base = dict(payload_width=1, channels=1, state_dim=2, prog_len=16, decay_shift=0, lat_hop=0)
cases = {
    "glob64_f1_d6": (Physics(topology="global", n_sites=64, fanout=1, lat_base=1, **base), envs.EnvSpec(family="RELAY", d=1, delta=6)),
    "glob64_f1_d8_loss.3": (Physics(topology="global", n_sites=64, fanout=1, lat_base=1, loss=0.3, **base), envs.EnvSpec(family="RELAY", d=1, delta=8)),
    "glob100_f2_async.8_jit1": (Physics(topology="global", n_sites=100, fanout=2, lat_base=1, lat_jitter=1, update_mode="async", update_p=0.8, **base), envs.EnvSpec(family="RELAY", d=1, delta=8)),
    "ring64_r2_s1_d4_dl8": (Physics(topology="ring", n_sites=64, radius=2, fanout=1, lat_base=1, **base), envs.EnvSpec(family="RELAY", d=4, delta=8)),
    "torus100_r1_s2_loss.3_dup.1": (Physics(topology="torus", n_sites=100, radius=1, fanout=2, lat_base=1, loss=0.3, dup=0.1, **base), envs.EnvSpec(family="RELAY", d=3, delta=8)),
    "glob64_f1_sync2_d8": (Physics(topology="global", n_sites=64, fanout=1, lat_base=1, update_period=2, **base), envs.EnvSpec(family="RELAY", d=1, delta=8)),
}
for name, (ph, env) in cases.items():
    ph = ph.validate()
    jobs = []
    for k in (env.delta, 4):
        jobs.append((rv.genome(ph, rv.B(k))[1], seeds, False))
    jobs.append((rv.genome(ph, rv.R11())[1], seeds, False))
    res = c.batch_eval(ph.replace(prog_len=16, state_dim=2).validate(), env, jobs)
    b = bound(ph, env, seeds, rng)
    best = max(res, key=lambda e: e["acc"])
    rec = {"case": name, "EC": b["EC_bound"], "EC_upper": b["EC_bound_upper"], "B_delta": res[0]["acc"], "B4": res[1]["acc"],
           "R11": res[2]["acc"], "best_lo99": best["lo99"], "sound": bool(best["lo99"] <= b["EC_bound_upper"])}
    out.append(rec); print(rec, flush=True)
c.save("ka_epicone.json", {"rows": out, "compute": ck.done()}); print(ck.done())
